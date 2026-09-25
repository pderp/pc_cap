"""Corrected S5 replication, isolated from the frozen R1 tree (PC-1).

Use ``python -m aw.pc_v0 --help``. ``plan`` is CPU/read-only metadata work.
``profile``, ``diagnose`` and ``run`` require --execute and a released GPU lease.
Profile/diagnose use development items; only run opens the exposed S5 populations.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import hashlib
import json
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.bases.epc import EPCBase
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, SiteId, Write
from pccap.data.selection import stream_items
from pccap.harness.ledger import Ledger
from pccap.harness.runs import Evaluator, run_stream
from pccap.metrics.editing import exact_match_aliases
from pccap.routers import make_router

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
ARCHIVE_SHA = "84126123f48c83e9270d6995335e86562e733efab7926ffa3178daadc5305a1f"
WEIGHTS_SHA = "ea4c561d3963ffd89f866337ef5e789a4ef15b7558b4c717594dbef88cd26f51"
OUTPUT = ROOT / "results/additional_work/PC-v0"
CUTOFF = datetime(2026, 10, 9, 17, tzinfo=ZoneInfo("America/New_York")).timestamp()
ARMS = {"SE-A": "adjoint", "SE-E": "error"}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def dump(path, obj):
    with Path(path).open("x") as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write("\n")


def archive():
    if sha(ARCHIVE) != ARCHIVE_SHA:
        raise ValueError("archived S5 settings changed")
    return json.loads(ARCHIVE.read_text())


def design(orders=1):
    if orders not in (1, 5):
        raise ValueError("choose the 12- or 60-cell scope before inspecting outcomes")
    f = archive()
    return [{"dataset": ds, "realization": r, "order": order, "arm": arm,
             "items": f["stream_lengths"][ds]}
            for ds in ("zsre", "counterfact") for r in f["realizations"]
            for order in f["order_seeds"][:orders] for arm in ARMS]


def build_cap(base, dataset, arm, seed, frozen=None):
    f = archive() if frozen is None else frozen
    if arm not in ARMS:
        raise ValueError("expected SE-A or SE-E")
    cal = f["calibration"]["EPC"]
    return Cap(base, CapConfig(
        arm="C1", read="h", d=base.d, seed=seed, credit=ARMS[arm], credit_iters=8,
        radii={int(k): float(v) for k, v in cal["radii"][dataset].items()},
        bank_scales={int(k): float(v) for k, v in cal["b_m"].items()},
    ), base.ledger)


def budget(frozen=None):
    f = archive() if frozen is None else frozen
    return Budget(**{k: f[k] for k in ("A", "epsilon", "R", "tau_edit")})


class SupplementalEvaluator(Evaluator):
    """Original metrics unchanged; score the SAME generations a second way."""

    def __init__(self, *args, secondary_path=None, **kw):
        self.secondary_path, self.last_items = secondary_path, []
        super().__init__(*args, **kw)

    def _decode_many(self, *args, **kw):
        self.last_decodes = super()._decode_many(*args, **kw)
        return self.last_decodes

    def items(self, learner, items):
        rows = super().items(learner, items)
        decs = iter(self.last_decodes)
        for item, row in zip(items, rows):
            own = next(decs)
            paras = [next(decs) for _ in item.paraphrases]
            row["bounded_es"] = exact_match_aliases(own.text, item.aliases, truncated=False)["value"]
            row["bounded_gs"] = (float(np.mean([
                exact_match_aliases(x.text, item.aliases, truncated=False)["value"] for x in paras
            ])) if paras else None)
            row["truncated"] = own.truncated
            row["paraphrases_truncated"] = sum(x.truncated for x in paras)
        self.last_items = rows
        if self.secondary_path is not None:
            with Path(self.secondary_path).open("a") as f:
                f.write(json.dumps({"item_ids": [x.item_id for x in items], "rows": rows}, allow_nan=False) + "\n")
        return rows


def credit_diagnostics(base, ids, target, writes, horizons=(1, 8, 32)):
    """Fixed-prefix diagnostic; no changes to weights, memory or solver settings."""
    before = base.checksum(recompute=True)
    exact = base.adjoint(ids, int(target), writes, phase="learning")
    rows = []
    for k in horizons:
        er = base.infer_errors(ids, int(target), iters=k, writes=writes, phase="learning")
        sites = []
        for s, e in er.site_errors.items():
            a, e = -np.asarray(exact[s], np.float64), np.asarray(e, np.float64)
            an, en = float(np.linalg.norm(a)), float(np.linalg.norm(e))
            sites.append({"bank": s.bank, "cosine_to_negative_adjoint": float(a @ e / (an * en)) if an * en else None,
                          "error_norm": en, "adjoint_norm": an, "norm_ratio": en / an if an else None,
                          "one_step_max_abs_error": float(np.max(np.abs(e - base.error_lr * a))) if k == 1 else None})
        rows.append({"iters": k, "energies": er.energies, "gradient_norm_0": er.grad_norm_0,
                     "gradient_norm_k": er.grad_norm_k, "r_k": er.r_k, "sites": sites, "cost": er.cost.as_dict()})
    if before != base.checksum(recompute=True):
        raise RuntimeError("diagnostic changed base weights")
    return rows


def source_identities():
    files = [Path(__file__), ARCHIVE, ROOT / "requirements.lock"]
    files += [ROOT / x for x in (
        "src/pccap/bases/epc.py", "src/pccap/bases/bp.py", "src/pccap/bases/gpt2_jax.py",
        "src/pccap/pc/epc_inference.py", "src/pccap/pc/nodes.py", "src/pccap/cap/learn.py",
        "src/pccap/cap/cap.py", "src/pccap/harness/runs.py", "src/pccap/data/decode.py",
        "src/pccap/data/selection.py", "src/pccap/metrics/editing.py")]
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


@contextmanager
def wall_limit(seconds):
    """Stop/failure stays a partial run; existing item guards protect in-flight state."""
    def expired(_signum, _frame):
        raise TimeoutError("PC-v0 wall-time allowance exhausted")
    old = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def _new_output(path):
    path = Path(path).resolve()
    if not path.is_relative_to(OUTPUT) or path == OUTPUT:
        raise ValueError(f"new run directory must be below {OUTPUT}")
    # The inherited runner writes large snapshots here, outside the repository.
    snapshot = Path(pccap.ASSETS_ROOT) / "runs" / path.relative_to(ROOT / "results")
    if path.exists() or snapshot.exists():
        raise FileExistsError("run or corresponding snapshot directory already exists")
    path.mkdir(parents=True)
    return path


def load_inputs(dataset, realization, order, population, n):
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.harness.stage_s4 import _items_from

    f = archive()
    if population == "development":
        items, unrelated = load_dev_items(dataset, n, seed=21)
        if len(items) != n:
            raise ValueError("insufficient development items")
        return items, unrelated[:200], 0, 0, {"population": "development", "selection_seed": 21,
                                               "manifest_sha256": sha(ROOT / f"manifests/dev/{dataset}_dev.json")}
    from pccap.data.confirm import load

    if realization not in f["realizations"] or order not in f["order_seeds"]:
        raise ValueError("unknown historical coordinate")
    if n != f["stream_lengths"][dataset]:
        raise ValueError("replication must retain the complete historical stream length")
    path = ROOT / f["confirm_dir"] / f"{dataset}_r{realization}.json"
    man = load(path, frozen=ARCHIVE)
    seeds = man["named_seeds"][str(order)]
    items = _items_from(stream_items(man, order, n))
    _, unrelated = load_dev_items(dataset, 1, seed=int(seeds["seed_router"]))
    return items, unrelated[:200], int(seeds["seed_cap_init"]), int(seeds["seed_router"]), {
        "population": "exposed historical S5; supplemental defect-correction replication",
        "manifest": str(path), "manifest_sha256": sha(path), "named_seeds": seeds}


def run_cell(args):
    import jax

    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.stage_s3 import drift_sample

    if not args.execute:
        raise ValueError("model execution requires --execute after GPU release")
    allowance = min(args.wall_seconds, CUTOFF - time.time())
    if allowance <= 0:
        raise ValueError("experimental cutoff or wall allowance reached")
    out = _new_output(args.output)
    started = time.monotonic()
    ledger = Ledger()
    outcome = {"status": "failed", "dataset": args.dataset, "arm": args.arm}
    try:
        with wall_limit(allowance), gpu_lease("PC-1", stage="additional_work", projected_seconds=allowance, exclusive=True) as lease:
            if lease.other_cuda_processes():
                raise RuntimeError("GPU is occupied; release is required before PC execution")
            if not any(d.platform == "gpu" for d in jax.devices()):
                raise RuntimeError("real-base execution requires JAX CUDA; use CPU only for tiny tests")
            f = archive()
            weights = Path(f["base_checkpoints"]["epc"]["path"])
            if sha(weights) != WEIGHTS_SHA or f["base_checkpoints"]["epc"]["sha256"] != WEIGHTS_SHA:
                raise ValueError("regenerated ePC weights mismatch")
            tok = GPT2Tokenizer()
            if sha(g.DEFAULT_SNAPSHOT / "tokenizer.json") != f["tokenizer_rev"]["tokenizer_json_sha256"]:
                raise ValueError("S5 tokenizer identity mismatch")
            base = EPCBase.from_npz(weights, ledger=ledger, error_lr=0.1)
            before = base.checksum(recompute=True)
            items, unrelated, cap_seed, router_seed, population = load_inputs(
                args.dataset, args.realization, args.order, args.population, args.items)
            drift_manifest = json.loads((ROOT / "manifests/dev/lm_sets.json").read_text())
            drift_binding = drift_manifest["files"]["drift_tokens"]
            if sha(drift_binding["path"]) != drift_binding["sha256"]:
                raise ValueError("drift source mismatch")
            cap = build_cap(base, args.dataset, args.arm, cap_seed, f)
            config = {**vars(args), **population, "weights_sha256": WEIGHTS_SHA,
                      "sources": source_identities(), "initial_state": cap.state_hash(),
                      "item_ids": [x.item_id for x in items], "error_lr": 0.1, "credit_iters": 8,
                      "scoring": "unchanged S5 primary; bounded text secondary", "drift": drift_binding,
                      "locality_prompts_sha256": hashlib.sha256(json.dumps(unrelated).encode()).hexdigest(),
                      "base_hash_before": before, "determinism": pccap.determinism_report()}
            dump(out / "config.json", config)
            if args.diagnostic:
                run_diagnostic(base, cap, items, out, f)
                outcome["status"] = "complete"
            else:
                ev = SupplementalEvaluator(base, tok, unrelated, drift_sample(4096), secondary_path=out / "secondary.jsonl")
                result = run_stream(cap, items, make_router("C1"), budget(f), ev, out, ledger,
                                    checkpoints=tuple(f["checkpoints"]), seed=router_seed, arm=args.arm,
                                    resource_stop_seconds=f["resource_rules"]["run_allowance_seconds"])
                vals = ev.last_items
                gs = [x["bounded_gs"] for x in vals if x["bounded_gs"] is not None]
                immediate = [json.loads(s) for s in (out / "items.jsonl").read_text().splitlines()]
                dump(out / "secondary-summary.json", {
                    "bounded_es_immediate": float(np.mean([x["bounded_es"] for x in immediate])) if immediate else None,
                    "bounded_ret_es_end": float(np.mean([x["bounded_es"] for x in vals])) if vals else None,
                    "bounded_ret_gs_end": float(np.mean(gs)) if gs else None,
                    "bounded_ls_end": result["metrics"]["ls_complete_answer_end"]["value"],
                    "locality_note": "legacy S5 LS already uses exact bounded decoded-text equality",
                    "items_completed": result["items_completed"], "items_planned": result["items_planned"]})
                outcome.update(status=result["status"], items_completed=result["items_completed"], items_planned=len(items))
            after = base.checksum(recompute=True)
            outcome.update(base_hash_before=before, base_hash_after=after)
            if before != after:
                raise RuntimeError("base weights changed")
    except BaseException as exc:
        outcome.update(status="wall_stop" if isinstance(exc, TimeoutError) else "failed", error=repr(exc))
        raise
    finally:
        outcome["elapsed_process_seconds"] = time.monotonic() - started
        outcome["ledger"] = ledger.totals()
        dump(out / "finish.json", outcome)
        ledger.write(out)
    return outcome


def run_diagnostic(base, cap, items, out, frozen):
    """First three support prefixes of each of three fixed development items."""
    rows = []
    for item in items[:3]:
        cap.update_item(item, make_router("C1"), budget(frozen))
        ids = np.asarray(item.prompt_ids, np.int32)
        for target in np.asarray(item.answer_ids, np.int32)[:3]:
            ep = cap.edited_forward(ids, phase="learning")
            writes = [Write(SiteId(m, g.BANK_BLOCK[m], len(ids) - 1), ep.writes[m]) for m in (1, 2, 3)]
            for label, ws in (("zero", []), ("acquired", writes)):
                row = {"item_id": item.item_id, "prefix_ids": ids.tolist(), "target": int(target),
                       "writes": label, "write_norms": [float(np.linalg.norm(w.vector)) for w in ws],
                       "diagnostics": credit_diagnostics(base, ids, int(target), ws)}
                rows.append(row)
            ids = np.concatenate([ids, np.int32([target])])
    dump(out / "diagnostics.json", {"sample": "first 3 prefixes of first 3 fixed seed-21 dev items; no outcome selection", "rows": rows})


def run_group(args):
    if not args.execute:
        raise ValueError("GPU work requires --execute after release")
    out = _new_output(args.output)
    development = args.command in ("profile", "diagnose")
    cells = ([{"dataset": d, "realization": 0, "order": 100, "arm": a,
               "items": 3 if args.command == "diagnose" else args.items}
              for d in ("zsre", "counterfact") for a in (("SE-A",) if args.command == "diagnose" else ARMS)]
             if development else design(args.orders))
    dump(out / "plan.json", {"population": "development" if development else "exposed S5", "cells": cells,
                             "replication_design": design(args.orders),
                             "wall_seconds": args.wall_seconds, "sources": source_identities()})
    start = time.monotonic()
    completed = []
    try:
        for c in cells:
            remaining = min(args.wall_seconds - (time.monotonic() - start), CUTOFF - time.time())
            if remaining <= 0:
                break
            dest = out / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
            cmd = [sys.executable, "-m", "aw.pc_v0", "cell", "--execute", "--output", str(dest),
                   "--population", "development" if development else "replication", "--wall-seconds", str(remaining)]
            for k, v in c.items():
                cmd += ["--" + k, str(v)]
            if args.command == "diagnose":
                cmd += ["--diagnostic"]
            with (out / f"{dest.name}.log").open("x") as log:
                p = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, check=False)
            finish = dest / "finish.json"
            completed.append({"cell": c, "exit_code": p.returncode, "finish": json.loads(finish.read_text()) if finish.exists() else None})
            if p.returncode or not completed[-1]["finish"] or completed[-1]["finish"]["status"] != "complete":
                break
    finally:
        dump(out / "summary.json", {"planned": len(cells), "finished": completed,
                                    "elapsed_process_seconds": time.monotonic() - start,
                                    "profile_note": "Development costs include fresh-process compilation and endpoint evaluation; not a measured full-stream cost."})
    return {"planned": len(cells), "finished": len(completed), "complete": len(completed) == len(cells) and all(x["finish"] and x["finish"]["status"] == "complete" for x in completed)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("plan", "profile", "diagnose", "run", "cell"))
    p.add_argument("--orders", type=int, choices=(1, 5), default=1)
    p.add_argument("--output", type=str)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--wall-seconds", type=float, default=86400)
    p.add_argument("--items", type=int, default=10)
    p.add_argument("--dataset", choices=("zsre", "counterfact"))
    p.add_argument("--arm", choices=tuple(ARMS), default="SE-A")
    p.add_argument("--realization", type=int, default=0)
    p.add_argument("--order", type=int, default=100)
    p.add_argument("--population", choices=("development", "replication"), default="development")
    p.add_argument("--diagnostic", action="store_true")
    a = p.parse_args()
    if not np.isfinite(a.wall_seconds) or a.wall_seconds <= 0 or a.items < 1:
        p.error("positive finite wall allowance and item count required")
    if a.command == "plan":
        result = {"cells": design(a.orders), "source": str(ARCHIVE), "model_execution": False}
    else:
        if not a.output or not a.execute:
            p.error("a new --output directory and --execute are required after GPU release")
        if a.command == "cell" and (not a.dataset or a.diagnostic and a.population != "development"):
            p.error("cell needs a dataset; diagnostics are development-only")
        result = run_cell(a) if a.command == "cell" else run_group(a)
    print(json.dumps(result, allow_nan=False))
    if result.get("complete") is False:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
