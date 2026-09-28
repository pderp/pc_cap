"""PC-7: paired fixed-v5 credit experiment, isolated from the registered R1 run.

plan reads recipe metadata only. profile/cell/run require --execute and a GPU
lease. The exposed R1 streams are reused, not relabeled as fresh confirmation.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from aw.pc_v0 import ARMS, CUTOFF, blocking_cuda_processes, dump, sha, wall_limit
from aw.pc_v1_acquire import PCRevisionCap
from aw.pc_v1_readout import query_view
from pccap.harness.snapshot import restore, save
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.analysis_stage4 import endpoint_summary
from pccap.revision_v1.endpoints import EndpointResourceFailure
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.revision_v1.stage4_assays import CellAssays

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "results/additional_work/PC-v1"
POPULATION = "post hoc / exposed R1 realization-0 streams, first 300 edits in order 100"
RECIPES = {
    "zsre": (
        "docs/tasks/R1-final-cell-recipes/61348508e40d54351613ab14.json",
        "a14686a8bd0651e8e06b6bbf64b90420f175b7f77991dc5c885cd106ac340b35",
    ),
    "counterfact": (
        "docs/tasks/R1-final-cell-recipes/ce0d0ffc2a58a60e27c460d9.json",
        "e3b541c4e5b2a5087ab6f1c8191d2caab5cadae0955d83b33d47e111cd3cba31",
    ),
}
DEVELOPMENT = {
    "zsre": (
        "docs/tasks/R1-post63l-active/R1-64f/R1-64f-zsre-R1_learned_ff.recipe.json",
        "3101eb264ddff145a430e974daee1e71acfcf10e8dfb9155e3916b2bc82e1d66",
    ),
    "counterfact": (
        "docs/tasks/R1-64-counterfact-v5.recipe.json",
        "13340760cfa3aecc31dd4cc42e27e8bdce79916780b45bdc63c9bcbec7c09394",
    ),
}


def checked(binding):
    p = Path(binding["path"])
    if sha(p) != binding["sha256"]:
        raise ValueError(f"input identity differs: {p}")
    return json.loads(p.read_bytes())


def bound_recipe(dataset, *, development=False):
    name, identity = (DEVELOPMENT if development else RECIPES)[dataset]
    binding = dict(path=str(ROOT / name), sha256=identity)
    return checked(binding), binding


def sources():
    files = [Path(__file__), ROOT / "requirements.lock"]
    files += [
        ROOT / name
        for name in (
            "aw/pc_v0.py",
            "aw/pc_v1_acquire.py",
            "aw/pc_v1_readout.py",
            "scripts/r1_61_cell_driver.py",
            "scripts/r1_49g_secondary.py",
            "scripts/r1_75_analysis_stage4_v1.py",
            "scripts/r1_49g_inference.py",
            "src/pccap/bases/epc.py",
            "src/pccap/bases/bp.py",
            "src/pccap/bases/gpt2_jax.py",
            "src/pccap/pc/epc_inference.py",
            "src/pccap/pc/nodes.py",
            "src/pccap/contracts.py",
            "src/pccap/data/decode.py",
            "src/pccap/data/tokenize.py",
            "src/pccap/harness/ledger.py",
            "src/pccap/harness/lease.py",
            "src/pccap/harness/snapshot.py",
        )
    ]
    files += sorted((ROOT / "src/pccap/revision_v1").glob("*.py"))
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


def design(development=False):
    return [
        dict(dataset=d, realization=0, order=100, arm=a, items=10 if development else 300)
        for d in RECIPES
        for a in ARMS
    ]


def plan(development=False):
    recipes = {}
    for ds in RECIPES:
        m, binding = bound_recipe(ds)
        dev, db = bound_recipe(ds, development=True)
        if m["cell"] != dict(condition="R1_learned_ff", dataset=ds, realization=0, order=100):
            raise ValueError("wrong registered source coordinate")
        recipes[ds] = dict(
            construction_recipe=binding,
            payload_recipe=db if development else binding,
            payload=(dev if development else m)["payload"],
            construction=m["construction"],
            tokenizer_sha256=m["tokenizer_sha256"],
        )
    return dict(
        schema_version=1,
        population="development" if development else POPULATION,
        cells=design(development),
        checkpoints=[10] if development else [100, 300],
        recipes=recipes,
        sources=sources(),
        model_execution=False,
        payload_opened=False,
        credit=dict(arms=ARMS, iters=8, error_lr=0.1, energy="SD-24 corrected"),
        endpoint_policy="R1 installed scoring; near-miss/revision at both 100 and 300 as supplemental cadence",
        excluded_assays="unseen/composition and ordinary-text harm are not run here; harm is separately costed",
        per_cell_wall_ceiling_seconds=7200,
    )


def load_payload(spec, n):
    payload = checked(spec["payload"])
    if len(payload["items"]) < n:
        raise ValueError("insufficient planned stream")
    items = payload["items"][:n]  # prefix of the original ordered payload; no selection by outcome
    if len({r["item_id"] for r in items}) != n or len({r["fact_id"] for r in items}) != n:
        raise ValueError("repeated stream item/fact")
    endpoints = {k: payload["endpoints"][k] for k in ("locality", "near_miss", "revision")}
    for kind, target in (("locality", 50), ("near_miss", 100), ("revision", 50)):
        definition = endpoints[kind]
        ids = definition["expected_ids"]
        if (
            len(ids) != target
            or len(ids) != len(set(ids))
            or [r["item_id"] for r in definition["rows"]] != ids
        ):
            raise ValueError("incomplete or reordered endpoint inventory: " + kind)
    return items, endpoints


def construct(spec, arm):
    import jax
    from scripts.r1_61_cell_driver import construct_owner_adapter

    from pccap.bases.epc import EPCBase

    recipe = checked(spec["construction_recipe"])
    original, tokenizer = construct_owner_adapter(recipe)
    if original.identity() != recipe["adapter_identity"]:
        raise ValueError("registered adapter identity differs")
    original_hash = original.base.checksum(recompute=True)
    base = EPCBase(
        params_np=jax.tree_util.tree_map(np.asarray, original.base.params),
        cfg=original.base.cfg,
        ledger=original.ledger,
        error_lr=0.1,
    )
    if base.checksum(recompute=True) != original_hash:
        raise ValueError("EPC interface changed original BP weights")
    cap = PCRevisionCap(
        base,
        original.learner.cfg,
        base.ledger,
        params=original.learner.params,
        acquisition_credit=ARMS[arm],
        credit_iters=8,
    )
    if cap.store.records or params_hash(cap.params) != original.learner.params_hash:
        raise ValueError("fresh memory and identical selected reader required")
    if query_view(cap).state_hash() != original.state_hash():
        raise ValueError("credit arm changes initial inference state")
    return CellAdapter(cap, "R1_learned_ff", budget=original.budget), tokenizer


def snapshot(cap, path):
    state = cap.export_state()
    file_hash = save(state, path)
    if (
        restore(Path(path).read_bytes(), expected_hash=state.content_hash()).content_hash()
        != cap.state_hash()
    ):
        raise ValueError("snapshot roundtrip failed")
    return dict(
        path=str(Path(path).resolve()),
        sha256=file_hash,
        state_sha256=cap.state_hash(),
        base_sha256=cap.base.checksum(recompute=True),
        reader_sha256=params_hash(cap.params),
        credit=cap.acquisition_credit,
        iters=cap.credit_iters,
    )


def metrics(cp, ids, endpoints):
    from scripts.r1_49g_secondary import _semantic

    # Use installed denominator/scoring functions, including unavailable != zero.
    rows = cp["endpoints"]["revision"]["rows"]
    revisions = [dict(r, semantic=_semantic(r) if r["status"] == "ok" else None) for r in rows]
    return {
        "ES": endpoint_summary(cp["history"], ids, "es"),
        "RET-ES": endpoint_summary(cp["retention"]["rows"], ids, "es"),
        "RET-GS": endpoint_summary(cp["retention"]["rows"], ids, "gs"),
        "LS": endpoint_summary(
            cp["locality"]["rows"], endpoints["locality"]["expected_ids"], "preserved"
        ),
        "near_miss": endpoint_summary(
            cp["endpoints"]["near_miss"]["rows"],
            endpoints["near_miss"]["expected_ids"],
            "preserved",
        ),
        "revision": endpoint_summary(revisions, endpoints["revision"]["expected_ids"], "semantic"),
        "revision_latest_answer": endpoint_summary(
            rows, endpoints["revision"]["expected_ids"], "latest_answer_success"
        ),
    }


def execute_stream(
    adapter, tokenizer, items, endpoints, checkpoints, output, resources, config, *, max_new=32
):
    """Shared production/tiny-fixture engine. Caller owns lease and deadline."""
    out, resources = Path(output), Path(resources)
    if out.exists() or resources.exists():
        raise FileExistsError("new result and snapshot directories required")
    if (
        not checkpoints
        or sorted(set(checkpoints)) != list(checkpoints)
        or checkpoints[-1] != len(items)
        or checkpoints[0] < 1
    ):
        raise ValueError("increasing checkpoints must end at the full selected stream")
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    started = time.monotonic()
    ledger, cap = adapter.ledger, adapter.learner
    base_hash, reader_hash = cap.base.checksum(recompute=True), params_hash(cap.params)
    initial = cap.state_hash()
    assays = CellAssays(adapter, tokenizer, max_new=max_new)
    history, completed = [], []
    finish = dict(
        status="failed",
        items_completed=0,
        items_planned=len(items),
        checkpoints_completed=completed,
        base_hash_before=base_hash,
        reader_hash_before=reader_hash,
        cost_policy="shared ledger totals and returned costs separate; never summed together",
    )
    configuration = dict(
        config,
        item_ids=[x.item_id for x in items],
        endpoints_sha256=digest(endpoints),
        initial_state=initial,
        initial_inference_state=query_view(cap).state_hash(),
        base_sha256=base_hash,
        reader_sha256=reader_hash,
        max_new=max_new,
        semantic_config=json.loads(cap.semantic_config()),
        checkpoints=list(checkpoints),
        determinism=pccap.determinism_report(),
    )
    dump(out / "config.json", configuration)

    def phase(label, operation, *, learning=False):
        before = adapter.state_hash()
        ledger_before, t0 = ledger.totals(), time.monotonic()
        assays.events.clear()
        status = "failed"
        try:
            value = operation()
            if not learning and adapter.state_hash() != before:
                raise RuntimeError("assay failed to preserve stream memory")
            status = "complete"
            return value
        finally:
            adapter.reset_queries()
            entry = dict(
                phase=label,
                status=status,
                elapsed_process_seconds=time.monotonic() - t0,
                state_before=before,
                state_after=adapter.state_hash(),
                ledger_before=ledger_before,
                ledger_after=ledger.totals(),
                returned_events=assays.events,
            )
            with (out / "phases.jsonl").open("a") as f:
                f.write(json.dumps(entry, allow_nan=False) + "\n")

    def update(item):
        result = adapter.update_item(item)
        assays.events.append(
            dict(
                phase="learning",
                item_id=item.item_id,
                code=result.code,
                returned_cost=result.cost.as_dict(),
            )
        )
        if result.code == "resource_stop" or any(
            str(c).startswith("resource_failure:") for c in result.codes
        ):
            raise EndpointResourceFailure(";".join(result.codes))
        return dict(
            code=result.code, original_code=adapter.last_original_outcome, codes=list(result.codes)
        )

    try:
        if cap.store.records:
            raise ValueError("each paired cell must begin with fresh memory")
        for n, item in enumerate(items, 1):
            outcome = phase(f"edit:{n}", lambda item=item: update(item), learning=True)
            row = phase(f"immediate:{n}", lambda item=item: assays.item(item))
            history.append(dict(row, outcome=outcome, index=n))
            finish["items_completed"] = n
            with (out / "items.jsonl").open("a") as f:
                f.write(json.dumps(history[-1], allow_nan=False) + "\n")
            if n not in checkpoints:
                continue
            cp = dict(checkpoint=n, history=list(history), endpoints={})
            cp["retention"] = phase(f"retention:{n}", lambda n=n: assays.retention(items[:n]))
            cp["locality"] = phase(f"locality:{n}", lambda: assays.locality(endpoints["locality"]))
            for kind in ("near_miss", "revision"):
                cp["endpoints"][kind] = phase(
                    f"{kind}:{n}",
                    lambda kind=kind, n=n: assays.challenges(kind, endpoints[kind], items[:n]),
                )
                if any(
                    r.get("status") == "resource_failure" for r in cp["endpoints"][kind]["rows"]
                ):
                    raise EndpointResourceFailure("resource failure in " + kind)
            cp["metrics"] = metrics(cp, [it.item_id for it in items[:n]], endpoints)
            if (
                cap.base.checksum(recompute=True) != base_hash
                or params_hash(cap.params) != reader_hash
            ):
                raise RuntimeError("immutable base or reader changed")
            cp["snapshot"] = snapshot(cap, resources / f"checkpoint-{n}.snapshot")
            cp["state_sha256"] = cp["snapshot"]["state_sha256"]
            dump(out / f"checkpoint-{n}.json", cp)
            completed.append(n)
        finish["status"] = "complete"
    except BaseException as exc:
        finish.update(
            status="wall_stop" if isinstance(exc, TimeoutError) else "failed", error=repr(exc)
        )
        raise
    finally:
        finish.update(
            elapsed_process_seconds=time.monotonic() - started,
            ledger=ledger.totals(),
            state_sha256=cap.state_hash(),
            base_hash_after=cap.base.checksum(recompute=True),
            reader_hash_after=params_hash(cap.params),
            config_sha256=sha(out / "config.json"),
        )
        dump(out / "finish.json", finish)
        ledger.write(out)
    return finish


def new_path(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OUTPUT) or path == OUTPUT or path.exists():
        raise ValueError("new output must be below " + str(OUTPUT))
    resources = Path(pccap.ASSETS_ROOT) / "runs" / path.relative_to(ROOT / "results")
    if resources.exists():
        raise FileExistsError("snapshot directory exists")
    return path, resources


def validate_profile(path):
    path = Path(path).resolve()
    p = json.loads((path / "plan.json").read_bytes())
    if p != plan(True):
        raise ValueError("completed development profile must match the current design and code")
    refs = {str(path / "plan.json"): sha(path / "plan.json")}
    for c in design(True):
        folder = path / cell_name(c)
        f = json.loads((folder / "finish.json").read_bytes())
        cfg = json.loads((folder / "config.json").read_bytes())
        if (
            f["status"] != "complete"
            or f["items_completed"] != 10
            or f["checkpoints_completed"] != [10]
            or f["config_sha256"] != sha(folder / "config.json")
        ):
            raise ValueError("incomplete development profile")
        if cfg["cell"] != c or cfg["population"] != "development" or cfg["sources"] != p["sources"]:
            raise ValueError("wrong profile coordinate/population/source")
        refs[str(folder / "finish.json")] = sha(folder / "finish.json")
        refs[str(folder / "config.json")] = sha(folder / "config.json")
    return refs


def cell_name(c):
    return f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"


def run_cell(args):
    import jax

    from pccap.harness.lease import gpu_lease

    if not args.execute:
        raise ValueError("real execution requires --execute")
    development = args.population == "development"
    p = plan(development)
    c = next(x for x in p["cells"] if x["dataset"] == args.dataset and x["arm"] == args.arm)
    profile = None if development else validate_profile(args.profile)
    out, resources = new_path(args.output)
    allowance = min(args.wall_seconds, 7200, CUTOFF - time.time())
    if allowance <= 0:
        raise ValueError("deadline/allowance exhausted")
    started = time.monotonic()
    context = {}
    try:
        with (
            wall_limit(allowance),
            gpu_lease(
                "PC-7", stage="additional_work", projected_seconds=allowance, exclusive=True
            ) as lease,
        ):
            others = lease.other_cuda_processes()
            if any("error" in row for row in others):
                raise RuntimeError("CUDA occupancy query failed")
            blocked = blocking_cuda_processes(others)  # owner-approved policy, imported unchanged
            if blocked:
                raise RuntimeError("GPU occupied by project compute")
            context["other_cuda_processes"] = others
            if not any(d.platform == "gpu" for d in jax.devices()):
                raise RuntimeError(
                    "real-base execution requires CUDA; use tiny CPU fixtures for tests"
                )
            spec = p["recipes"][c["dataset"]]
            rows, endpoints = load_payload(spec, c["items"])
            adapter, tok = construct(spec, c["arm"])
            items = [as_edit(r, tok) for r in rows]
            cfg = dict(
                cell=c,
                population=p["population"],
                sources=p["sources"],
                inputs=spec,
                profile_sources=profile,
                context=context,
            )
            result = execute_stream(
                adapter, tok, items, endpoints, p["checkpoints"], out, resources, cfg
            )
    except BaseException as exc:
        # Failures before the stream engine still receive a durable finish.
        if not (out / "finish.json").exists():
            out.mkdir(parents=True, exist_ok=True)
            dump(
                out / "finish.json",
                dict(
                    status="failed",
                    error=repr(exc),
                    items_completed=0,
                    cell=c,
                    population=p["population"],
                    context=context,
                ),
            )
        raise
    finally:
        out.mkdir(parents=True, exist_ok=True)
        dump(
            out / "process.json",
            dict(
                elapsed_process_seconds=time.monotonic() - started,
                scope="includes lease wait, model construction and stream; not additive to finish time",
                wall_allowance_seconds=allowance,
            ),
        )
    return result


def run_group(args):
    if not args.execute:
        raise ValueError("real execution requires --execute")
    development = args.command == "profile"
    p = plan(development)
    if not development:
        validate_profile(args.profile)
    out, _ = new_path(args.output)
    out.mkdir(parents=True)
    dump(out / "plan.json", p)
    start, finished = time.monotonic(), []
    try:
        for c in p["cells"]:
            remaining = min(
                args.wall_seconds - (time.monotonic() - start), CUTOFF - time.time(), 7200
            )
            if remaining <= 0:
                break
            dest = out / cell_name(c)
            cmd = [
                sys.executable,
                "-m",
                "aw.pc_v1_run",
                "cell",
                "--execute",
                "--output",
                str(dest),
                "--dataset",
                c["dataset"],
                "--arm",
                c["arm"],
                "--wall-seconds",
                str(remaining),
                "--population",
                "development" if development else "replication",
            ]
            if not development:
                cmd += ["--profile", str(Path(args.profile).resolve())]
            with (out / (dest.name + ".log")).open("x") as log:
                process = subprocess.run(
                    cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False
                )
            path = dest / "finish.json"
            f = json.loads(path.read_bytes()) if path.exists() else None
            finished.append(dict(cell=c, exit_code=process.returncode, finish=f))
            if process.returncode or not f or f["status"] != "complete":
                break
    finally:
        summary = dict(
            planned=4,
            finished=finished,
            elapsed_process_seconds=time.monotonic() - start,
            complete=len(finished) == 4
            and all(r["finish"] and r["finish"]["status"] == "complete" for r in finished),
        )
        dump(out / "summary.json", summary)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command", choices=("plan", "profile", "run", "cell"))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--output")
    ap.add_argument("--profile", help="completed four-cell development profile directory")
    ap.add_argument("--wall-seconds", type=float, default=28800)
    ap.add_argument("--dataset", choices=tuple(RECIPES))
    ap.add_argument("--arm", choices=tuple(ARMS))
    ap.add_argument("--population", choices=("development", "replication"), default="development")
    args = ap.parse_args()
    if not np.isfinite(args.wall_seconds) or not 0 < args.wall_seconds <= 28800:
        ap.error("positive allowance <= 28,800 seconds required; each cell <= 7,200")
    if args.command == "plan":
        result = plan(args.population == "development")
    else:
        if not args.output or not args.execute:
            ap.error("--execute and a new --output are required")
        if args.command == "cell" and (not args.dataset or not args.arm):
            ap.error("cell requires --dataset and --arm")
        if (
            args.command == "run" or args.command == "cell" and args.population == "replication"
        ) and not args.profile:
            ap.error("replication requires the completed --profile")
        result = run_cell(args) if args.command == "cell" else run_group(args)
    print(json.dumps(result, allow_nan=False))
    if result.get("complete") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
