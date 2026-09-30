"""PC-15: paired reader training on the selected v5 recipe; local JAX only.

plan is metadata-only. profile/train/evaluate require explicit execution and the
exclusive GPU lease. Evaluation always reacquires with the adjoint rule.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import dataclasses
import json
import math
import pickle
import resource
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import jax
import jax.numpy as jnp
import numpy as np

from aw.interface import ALL, prune_reader
from aw.pc_v0 import CUTOFF, blocking_cuda_processes, dump, sha, wall_limit
from aw.pc_v1_run import bound_recipe, checked
from pccap.bases.bp import BPBase
from pccap.bases.epc import EPCBase
from pccap.harness.ledger import Ledger
from pccap.revision_v1.controller import ControllerConfig, init_controller
from pccap.revision_v1.epc_train import EPCTrainer, EPCWriteGradients
from pccap.revision_v1.observations import ObservationEncoder
from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
from pccap.revision_v1.stream_train import (
    add_text_nulls,
    bank_identity,
    build_bank,
    build_text_bank,
    merge_banks,
    stream_episode_mixed,
    verify_bank,
)
from pccap.revision_v1.train import LossConfig, retrieval_loss
from pccap.revision_v1.train_fast import FastTrainer

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(pccap.ASSETS_ROOT)
OUTPUT = ROOT / "results/additional_work/PC-reader"
SUMMARY = ROOT / "results/R1/pilot/r1_50_stream_sel6_text_s2/summary.json"
CACHE = ASSETS / "runs/pc_cap/additional_work/reader-training-cache"
NO_NEW_FITS = datetime(2026, 10, 6, tzinfo=ZoneInfo("America/New_York")).timestamp()
AVERAGE_STEPS = (150, 200, 250, 300)
RULES = ("bp", "epc")
SEEDS = (0, 1, 2)


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def recipe():
    original, construction_binding = bound_recipe("zsre")
    summary = json.loads(SUMMARY.read_bytes())
    args = summary["args"]
    required = dict(
        pool_items=1000,
        held_out=100,
        steps=300,
        batch=2,
        n_memory=64,
        n_query_records=8,
        n_out=8,
        save_every=50,
        kappa=0.0,
        clip_surprisal=None,
        out_para_nulls=True,
        out_para_prob=1.0,
        lr=0.001,
        weight_decay=0.01,
        dev_every=50,
        no_query_null=False,
        lex_idf=False,
        text_nulls=8,
        text_windows=512,
    )
    if any(args[k] != v for k, v in required.items()):
        raise ValueError("selected v5 training recipe changed")
    if original["construction"]["weights"]["checkpoint"] != "avg150-300":
        raise ValueError("selected checkpoint policy differs")
    pools = [binding(ROOT / name) for name in args["pool"].split(",")]
    return dict(
        schema="supplemental-reader-training-v1",
        original_summary=binding(SUMMARY),
        source_recipe=construction_binding,
        pools=pools,
        stop_tokens=binding(ROOT / args["stop_tokens"]),
        training=required,
        calibration=original["construction"]["calibration"],
        base=original["construction"]["base"],
        seeds=list(SEEDS),
        checkpoint_steps=list(AVERAGE_STEPS),
        checkpoint_policy="unweighted tensor mean at 150/200/250/300; no outcome selection",
        error_credit=dict(
            iterations=8, error_lr=0.1, source="pccap.revision_v1.epc_train.EPCTrainer"
        ),
        loss=dataclasses.asdict(LossConfig()),
        text_range=[0, 50001920],
        text_seed="training_seed + 7",
        acquisition="adjoint in every evaluation arm; newly empty memory",
    )


def source_hashes():
    files = [Path(__file__), ROOT / "aw/interface.py", ROOT / "requirements.lock"]
    files += sorted((ROOT / "src/pccap/revision_v1").glob("*.py"))
    files += sorted((ROOT / "src/pccap/pc").glob("*.py"))
    files += [ROOT / ("src/pccap/bases/" + name) for name in ("bp.py", "epc.py", "gpt2_jax.py")]
    return {str(p): sha(p) for p in files}


def plan():
    return dict(
        recipe=recipe(),
        sources_sha256=source_hashes(),
        model_execution=False,
        trainings=[dict(rule=rule, seed=seed, read_taps=ALL) for rule in RULES for seed in SEEDS],
        evaluations=[
            dict(
                rule=rule,
                seed=seed,
                dataset=ds,
                realization=0,
                order=100,
                items=300,
                acquisition="adjoint",
                checkpoints=[100, 300],
            )
            for rule in RULES
            for seed in SEEDS
            for ds in ("zsre", "counterfact")
        ],
        population="post hoc/exposed realization-0 streams; training seeds are not subject realizations",
        profile_required=True,
        gpu_dispatch="Capstan",
        experimental_cutoff=CUTOFF,
        new_fit_cutoff=NO_NEW_FITS,
    )


def configs(spec, read_taps=ALL):
    if read_taps not in (ALL, (2, 3)):
        raise ValueError("only the declared full and upper read sets are admitted")
    stop = checked(spec["stop_tokens"])
    rc = ReaderConfig(stop_tokens=tuple(int(t) for t in stop["tokens"]), taps=read_taps)
    cc = ControllerConfig(
        A=0.3, bank_scales=tuple(spec["calibration"]["bank_scales"][str(k)] for k in ALL)
    )
    return rc, cc


def initial_theta(seed, rc, cc):
    k1, k2 = jax.random.split(jax.random.PRNGKey(seed))
    full = dataclasses.replace(rc, taps=ALL)
    theta = dict(reader=init_reader(k1, full), controller=init_controller(k2, cc))
    return prune_reader(theta, rc.taps)


def project_episode(feats, taps):
    """Slice cached full-tap observations everywhere; preserve tokens/targets/order."""
    if taps == ALL:
        return feats
    idx = [ALL.index(m) for m in taps]

    def sliced(value):
        return None if value is None else np.asarray(value)[idx]

    supports = [
        dataclasses.replace(
            s,
            last=sliced(s.last),
            span=sliced(s.span),
            code_last=sliced(s.code_last),
            code_span=sliced(s.code_span),
        )
        for s in feats.supports
    ]
    queries = [
        dataclasses.replace(
            q,
            last=sliced(q.last),
            span=sliced(q.span),
            prefixes=[
                dataclasses.replace(p, last=sliced(p.last), span=sliced(p.span)) for p in q.prefixes
            ],
        )
        for q in feats.queries
    ]
    return dataclasses.replace(feats, supports=supports, queries=queries)


def trainer(rule, base, rc, cc, args):
    kw = dict(lc=LossConfig(), lr=args["lr"], clip=1.0, weight_decay=args["weight_decay"])
    if rule == "bp":
        return FastTrainer(rc, cc, base.params, base.cfg, ledger=base.ledger, **kw)
    if rule == "epc":
        return EPCTrainer(rc, cc, EPCWriteGradients(base, iters=8), **kw)
    raise ValueError("rule must be bp or epc")


def memory_guard(min_mb=4096):
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            available = int(line.split()[1]) / 1024
            if available < min_mb:
                raise MemoryError(f"MemAvailable {available:.0f} MiB below {min_mb} MiB")
            return available
    raise RuntimeError("MemAvailable unavailable")


def device_memory():
    """Backend-reported allocator statistics; unavailable is not zero."""
    return [{"device": str(d), "statistics": d.memory_stats()} for d in jax.devices()]


def save_theta(path, theta):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        **{
            jax.tree_util.keystr(k): np.asarray(v)
            for k, v in jax.tree_util.tree_flatten_with_path(theta)[0]
        },
    )
    return dict(**binding(path), params_sha256=params_hash(theta))


def load_theta(record, template):
    if sha(record["path"]) != record["sha256"]:
        raise ValueError("reader artifact changed")
    leaves, tree = jax.tree_util.tree_flatten_with_path(template)
    with np.load(record["path"], allow_pickle=False) as saved:
        keys = [jax.tree_util.keystr(k) for k, _ in leaves]
        if set(saved.files) != set(keys):
            raise ValueError("checkpoint parameter topology differs")
        values = [saved[k].copy() for k in keys]
    if any(v.shape != ref.shape or not np.isfinite(v).all() for v, (_, ref) in zip(values, leaves)):
        raise ValueError("checkpoint dimensions/nonfinite values")
    theta = jax.tree_util.tree_unflatten(tree, [jnp.asarray(v) for v in values])
    if params_hash(theta) != record["params_sha256"]:
        raise ValueError("reader parameter hash differs")
    return theta


def average_thetas(values):
    if len(values) != 4:
        raise ValueError("all four fixed checkpoints required; no missing-step substitution")
    return jax.tree_util.tree_map(
        lambda *xs: jnp.asarray(np.mean(np.stack(xs), axis=0), jnp.float32), *values
    )


def data(base, spec, seed):
    """Reuse qualified original full-tap banks without modifying them."""
    rc, _ = configs(spec)
    enc = ObservationEncoder(base, taps=ALL)
    banks, records, train_ix, dev_ix = [], [], [], []
    for pool in spec["pools"]:
        memory_guard()
        rows = checked(pool)["items"][:1000]
        expected = bank_identity(rows, enc.base_hash, enc.encoder_version, ALL, 2, 2, np.float16)
        old = ASSETS / "runs/pc_cap/R1/banks" / (Path(pool["path"]).stem + "_1000.pkl")
        fresh = CACHE / (Path(pool["path"]).stem + "_1000.pkl")
        path = old if old.exists() else fresh
        reused = path.exists()
        if reused:
            bank = pickle.loads(path.read_bytes())
            verify_bank(bank, expected)
        else:
            bank = build_bank(base, enc, rows, rc, progress=100)
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as f:
                pickle.dump(bank, f)
        # The MQuAKE v3 pool holds 500 items (its original bank file keeps the `_1000` name); compare with the rows
        # actually loaded, not a fixed 1,000 (Capstan, 2026-09-30 01:10, first dispatch; Capex to review).
        if len(bank.items) != len(rows) or [v.item_id for v in bank.items] != [
            v["item_id"] for v in rows
        ]:
            raise ValueError("bank item coverage/order differs")
        if any(
            not np.array_equal(it.prompt_ids, row["prompt_ids"])
            or not np.array_equal(it.answer_ids, row["answer_ids"])
            for it, row in zip(bank.items, rows)
        ):
            raise ValueError("cached bank tokens differ from its bound pool")
        offset = sum(len(b.items) for b in banks)
        n = len(bank.items)
        split = (n * 9) // 10  # last tenth of each pool held out, as 900 / 1,000 was for the 1,000-item pools
        train_ix.append(list(range(offset, offset + split)))
        dev_ix.append(list(range(offset + split, offset + n)))
        banks.append(bank)
        records.append(
            dict(
                **binding(path),
                reused=reused,
                identity=expected,
                content_sha256=bank.content_hash(),
            )
        )
    from pccap.distill.data import load_shard

    shard_path = ASSETS / "data/raw/openwebtext/openwebtext.bin"
    text_path = CACHE / f"text-seed{seed}-full.pkl"
    text_identity = dict(
        base=enc.base_hash,
        seed=seed + 7,
        range=spec["text_range"],
        windows=512,
        source=binding(shard_path),
        builder=sha(ROOT / "src/pccap/revision_v1/stream_train.py"),
    )
    memory_guard()
    if text_path.exists():
        saved = pickle.loads(text_path.read_bytes())
        if saved["identity"] != text_identity:
            raise ValueError("text bank identity differs")
        text_bank = saved["bank"]
        reused = True
    else:
        text_bank = build_text_bank(
            base, enc, load_shard(shard_path)[:50001920], rc, n_windows=512, seed=seed + 7
        )
        text_path.parent.mkdir(parents=True, exist_ok=True)
        with text_path.open("xb") as f:
            pickle.dump(dict(identity=text_identity, bank=text_bank), f)
        reused = False
    if len(text_bank) != 1536:
        raise ValueError("complete 512-window/three-prefix text bank required")
    records.append(dict(**binding(text_path), reused=reused, identity=text_identity))
    return merge_banks(banks), train_ix, dev_ix, text_bank, records


def episodes(bank, indices, text_bank, rng, *, training, batch, taps=ALL):
    result = [
        stream_episode_mixed(
            indices,
            bank,
            rng,
            n_memory=64,
            n_query_records=8,
            n_out=8,
            out_paraphrase_nulls=training,
            out_paraphrase_null_prob=1.0,
            episode_id="" if training else f"dev-{i}",
        )
        for i in range(batch)
    ]
    # Preserve the original script's RNG order: sample the whole episode batch,
    # then append text nulls to each episode, including all six development episodes.
    return [project_episode(add_text_nulls(ep, text_bank, rng, 8), taps) for ep in result]


def episode_identity(batch):
    from pccap.revision_v1.analysis import digest

    return digest(
        [
            dict(
                supports=[s.record_id for s in e.supports],
                queries=[
                    dict(
                        id=q.query_id,
                        role=q.role,
                        target=q.target_record,
                        prefixes=[
                            dict(ids=p.ids[: p.n].tolist(), target=p.target) for p in q.prefixes
                        ],
                    )
                    for q in e.queries
                ],
            )
            for e in batch
        ]
    )


def train_loop(
    base, rc, cc, rule, seed, spec, get_batch, dev, out, resources, *, steps=300, guard=memory_guard
):
    """Same engine for the tiny test and owner runs; no outcome-selected checkpoint."""
    args = spec["training"]
    theta = initial_theta(seed, rc, cc)
    initial_hash, base_hash = params_hash(theta), base.checksum(recompute=True)
    tr = trainer(rule, base, rc, cc, args)
    state = tr.init(theta)
    candidates, trajectory, costs = [], [], []
    started = time.monotonic()
    for step in range(1, steps + 1):
        guard()
        if step > 1 and (step - 1) % 50 == 0:
            jax.clear_caches()
        batch = get_batch()
        identity = episode_identity(batch)
        t0 = time.monotonic()
        theta, state, metrics = tr.outer_step(theta, state, batch)
        if any(not math.isfinite(float(v)) for v in metrics.values()) or any(
            not bool(jnp.isfinite(v).all()) for v in jax.tree_util.tree_leaves(theta)
        ):
            raise FloatingPointError("nonfinite training output; no final reader admitted")
        elapsed = time.monotonic() - t0
        costs.append(elapsed)
        row = dict(step=step, episode_sha256=identity, metrics=metrics, update_seconds=elapsed)
        if step % 50 == 0 or step == steps:
            # One common exact retrieval diagnostic. EPC's settled CE is labelled
            # separately and is never compared as though it were feedforward CE.
            row["dev_retrieval"] = float(
                np.mean([float(retrieval_loss(theta, rc, e, True)) for e in dev])
            )
            row["checkpoint"] = save_theta(resources / f"theta_step{step}.npz", theta)
        with (out / "metrics.jsonl").open("a") as f:
            f.write(json.dumps(row, allow_nan=False) + "\n")
        trajectory.append(identity)
        if step in AVERAGE_STEPS:
            candidates.append(jax.tree_util.tree_map(lambda v: np.asarray(v).copy(), theta))
    selected = average_thetas(candidates) if steps == 300 else theta
    artifact = save_theta(
        resources / ("theta_avg150-300.npz" if steps == 300 else "profile_theta.npz"), selected
    )
    if base.checksum(recompute=True) != base_hash:
        raise RuntimeError("training modified the frozen base")
    return dict(
        status="complete",
        rule=rule,
        seed=seed,
        read_taps=list(rc.taps),
        steps=steps,
        profile_only=steps != 300,
        reader=artifact,
        initial_reader_sha256=initial_hash,
        base_sha256=base_hash,
        trajectory=trajectory,
        update_seconds=costs,
        training_seconds=time.monotonic() - started,
        selected_steps=list(AVERAGE_STEPS) if steps == 300 else [steps],
        reader_config=dataclasses.asdict(rc),
        controller_config=dataclasses.asdict(cc),
        parameter_count=sum(int(v.size) for v in jax.tree_util.tree_leaves(selected)),
        reusable_parameter_bytes=sum(int(v.nbytes) for v in jax.tree_util.tree_leaves(selected)),
        metric_note="EPC answer is settled CE; BP answer is feedforward CE; dev retrieval uses one common exact diagnostic",
        peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        device_memory=device_memory(),
    )


def validate_profile(path, rule, taps, spec):
    if not path:
        raise ValueError("matching complete ten-step development profile required")
    profile = json.loads((Path(path) / "report.json").read_bytes())
    cost = json.loads((Path(path) / "cost.json").read_bytes())
    if (
        profile.get("status") != "complete"
        or cost.get("status") != "complete"
        or not profile["profile_only"]
        or profile["rule"] != rule
        or profile["read_taps"] != list(taps)
        or profile["steps"] != 10
        or profile["recipe"] != spec
        or profile["sources_sha256"] != source_hashes()
    ):
        raise ValueError("matching complete ten-step development profile required")
    return profile


def remaining_allowance(output_root, requested):
    """AW-L's 48-hour ceiling includes profiling and failed attempts, once each."""
    allowance = min(requested, CUTOFF - time.time())
    if output_root == ROOT / "results/additional_work/AW-L":
        files = list(output_root.rglob("cost.json"))
        # Top-level process receipt includes its stream/harm components.
        files = [
            p
            for p in files
            if not any(
                (q / "cost.json").exists()
                for q in p.parent.parents
                if q != output_root and q.is_relative_to(output_root)
            )
        ]
        charged = sum(json.loads(p.read_bytes())["elapsed_process_seconds"] for p in files)
        allowance = min(allowance, 48 * 3600 - charged)
    if not math.isfinite(allowance) or allowance <= 0:
        raise ValueError("no positive allowance remains before ceiling/cutoff")
    return allowance


def execute_training(args, *, read_taps=ALL, output_root=OUTPUT):
    if not args.execute:
        raise ValueError("GPU training requires --execute; plan is the CPU-only command")
    if args.rule not in RULES or args.seed not in SEEDS:
        raise ValueError("declared rule and seed required")
    if time.time() >= NO_NEW_FITS:
        raise ValueError("October 6 new-fit cutoff reached")
    spec = recipe()
    source_snapshot = source_hashes()
    profile = args.command == "profile"
    previous = None if profile else validate_profile(args.profile, args.rule, read_taps, spec)
    out = Path(args.output).resolve()
    if not out.is_relative_to(output_root) or out == output_root or out.exists():
        raise ValueError("new result directory under " + str(output_root) + " required")
    resources = ASSETS / "runs" / out.relative_to(ROOT / "results")
    if resources.exists():
        raise FileExistsError(resources)
    allowance = remaining_allowance(output_root, args.wall_seconds)
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    cost = dict(
        status="failed",
        scope="reader training including construction/cache; no acquisition or harm",
    )
    started = time.monotonic()
    ledger = Ledger()
    try:
        from pccap.harness.lease import gpu_lease

        with (
            gpu_lease(
                "PC-15" if output_root == OUTPUT else "AW-L5",
                stage="additional_work",
                projected_seconds=allowance,
                exclusive=True,
            ) as lease,
            wall_limit(allowance),
        ):
            others = lease.other_cuda_processes()
            if (
                any("error" in r for r in others)
                or blocking_cuda_processes(others)
                or not any(d.platform == "gpu" for d in jax.devices())
            ):
                raise RuntimeError("owner needs a released CUDA device")
            memory_guard()
            for name, value in spec["base"]["files"].items():
                if sha(Path(spec["base"]["path"]) / name) != value:
                    raise ValueError("base snapshot identity differs")
            base = (EPCBase if args.rule == "epc" else BPBase)(
                snapshot=spec["base"]["path"], ledger=ledger
            )
            rc, cc = configs(spec, read_taps)
            t0 = time.monotonic()
            bank, train_ix, dev_ix, text_bank, caches = data(base, spec, args.seed)
            cache_seconds = time.monotonic() - t0
            rng, dev_rng = np.random.default_rng(args.seed), np.random.default_rng(args.seed + 1000)
            dev = episodes(
                bank, dev_ix, text_bank, dev_rng, training=False, batch=6, taps=read_taps
            )
            report = train_loop(
                base,
                rc,
                cc,
                args.rule,
                args.seed,
                spec,
                lambda: episodes(
                    bank, train_ix, text_bank, rng, training=True, batch=2, taps=read_taps
                ),
                dev,
                out,
                resources,
                steps=10 if profile else 300,
            )
            if source_hashes() != source_snapshot or recipe() != spec:
                raise ValueError("training sources or recipe changed during execution")
            report.update(
                recipe=spec,
                sources_sha256=source_snapshot,
                caches=caches,
                cache_seconds=cache_seconds,
                dev_episode_sha256=episode_identity(dev),
                profile=None if previous is None else binding(Path(args.profile) / "report.json"),
                projected_update_seconds_300=sum(report["update_seconds"]) * 300 / report["steps"],
                projection_note="linear update-only extrapolation; separately add cache/dev/evaluation/full harm and retries",
            )
            dump(out / "report.json", report)
            cost["status"] = "complete"
    except BaseException as exc:
        cost["error"] = repr(exc)
        raise
    finally:
        cost.update(
            elapsed_process_seconds=time.monotonic() - started,
            ledger=ledger.totals(),
            peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        )
        dump(out / "cost.json", cost)
    return report


def parser():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("command", choices=("plan", "profile", "train", "evaluate"))
    p.add_argument("--rule", choices=RULES, default="bp")
    p.add_argument("--seed", type=int, choices=SEEDS, default=0)
    p.add_argument("--output")
    p.add_argument("--profile", help="completed matching ten-step training profile directory")
    p.add_argument("--training", help="completed training directory for evaluation")
    p.add_argument("--dataset", choices=("zsre", "counterfact"), default="zsre")
    p.add_argument(
        "--development", action="store_true", help="ten-item development evaluation profile"
    )
    p.add_argument(
        "--evaluation-profile", help="matching development evaluation receipt for 300-item run"
    )
    p.add_argument("--wall-seconds", type=float, default=14400)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--execute", action="store_true")
    return p


def main():
    args = parser().parse_args()
    if args.command == "plan":
        print(json.dumps(plan(), indent=2))
    elif args.command == "evaluate":
        from aw.trained_reader_eval import execute_evaluation

        execute_evaluation(args)
    else:
        execute_training(args)


if __name__ == "__main__":
    main()
