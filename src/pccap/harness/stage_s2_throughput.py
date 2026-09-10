"""S2-06: throughput profile (PDF S2 "Throughput"; plan §6.8).

100 complete development edits per dataset under each available arm (cap arms C0/C1/C2/CR now;
B1/B3/B4 and ePC credit when they exist), each run including immediate ES/GS/LS evaluation,
memory search, a checkpoint save at 100 and the rescoring pass, under the **exclusive** GPU lease
(``nvidia-smi`` compute apps captured before/after). Warmup/compile is measured separately with a
2-item warmup stream before timing. Reported per arm and dataset: operation counts and
accelerator seconds per edit (learning and query columns), stratified by answer length, and
peak memory.

    python -m pccap.harness.stage_s2_throughput --n 100 --arms C0 C1 C2 CR
→ results/S2/throughput.json and per-run directories results/S2/throughput/<arm>/<dataset>/.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax

from pccap.bases.bp import BPBase
from pccap.contracts import Budget
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.arms import cr_distribution_for, make_learner, router_for
from pccap.harness.ledger import Ledger
from pccap.harness.runs import Evaluator, run_stream
from pccap.harness.stage_s2 import calibration, load_dev_items
from pccap.harness.stage_s3 import chosen_A, drift_sample

ROOT = Path(__file__).resolve().parents[3]
S2 = ROOT / "results" / "S2"


def profile_arm(arm: str, ds: str, n: int, tok: GPT2Tokenizer, out_dir: Path, drift_positions: int = 1024,
                locality_prompts: int = 100, cr_dist: bool = False, lora_lr: float = 1e-4) -> dict:
    b_m, radii = calibration(ds)
    A = chosen_A()
    cr_d, cr_label = cr_distribution_for(ds) if cr_dist else (None, "cr_profile_uniform")

    def router():
        return router_for(arm, cr_distribution=cr_d, cr_label=cr_label)
    items, unrelated = load_dev_items(ds, n + 2, seed=21)
    warm_items, items = items[:2], items[2 : n + 2]
    # warmup (compile) on a separate learner and ledger, reported separately
    wl = Ledger()
    wbase = BPBase(ledger=wl)
    wcap = make_learner(arm, wbase, wl, radii=radii, bank_scales=b_m, seed=0, lora_lr=lora_lr)
    t0 = time.perf_counter()
    wev = Evaluator(wbase, tok, unrelated[:5], None)
    run_stream(wcap, warm_items, router(), Budget(A=A), wev, out_dir / "warmup", wl, checkpoints=(), arm=arm)
    warmup_seconds = time.perf_counter() - t0
    # timed run
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    cap = make_learner(arm, base, ledger, radii=radii, bank_scales=b_m, seed=0, lora_lr=lora_lr)
    ev = Evaluator(base, tok, unrelated[:locality_prompts], drift_sample(drift_positions))
    eval_setup_seconds = ledger.totals()["query"]["accel_seconds"]
    t0 = time.perf_counter()
    m = run_stream(cap, items, router(), Budget(A=A), ev, out_dir, ledger, checkpoints=(100,), arm=arm)
    wall = time.perf_counter() - t0
    tot = ledger.totals()
    items_rows = [json.loads(line) for line in (out_dir / "items.jsonl").read_text().splitlines()]
    by_len: dict[str, dict] = {}
    for r in items_rows:
        k = str(r["answer_tokens"])
        d = by_len.setdefault(k, {"n": 0, "accel_seconds": 0.0, "full_forwards": 0, "partial_forwards": 0, "reverses": 0, "rounds": 0})
        d["n"] += 1
        for f in ("accel_seconds", "full_forwards", "partial_forwards", "reverses"):
            d[f] += r["cost"][f]
        d["rounds"] += r["rounds"]
    for d in by_len.values():
        d["accel_seconds_per_edit"] = d["accel_seconds"] / d["n"]
    learn_s = tot["learning"]["accel_seconds"]
    query_s = tot["query"]["accel_seconds"] - eval_setup_seconds
    stats = jax.devices()[0].memory_stats() or {}
    return {"arm": arm, "dataset": ds, "n_items": len(items), "A": A, "radii": radii, "b_m": b_m, "cr_label": cr_label if arm == "CR" else None, "lora_lr": lora_lr if arm in ("B1", "B3") else None,
            "warmup_seconds_wall": warmup_seconds, "eval_setup_query_seconds": eval_setup_seconds,
            "wall_seconds": wall, "learning_accel_seconds": learn_s, "query_accel_seconds": query_s,
            "learning_accel_seconds_per_edit": learn_s / len(items), "query_accel_seconds_per_edit": query_s / len(items),
            "wall_seconds_per_edit": wall / len(items), "ops_learning": {k: tot["learning"][k] for k in ("full_forwards", "partial_forwards", "reverses", "router_probes", "search_candidates", "prefix_microsteps")},
            "ops_query": {k: tot["query"][k] for k in ("full_forwards", "partial_forwards")},
            "by_answer_length": by_len, "peak_mib": (stats.get("peak_bytes_in_use") or 0) / 2**20,
            "metrics": {k: v["value"] for k, v in m["metrics"].items()}, "memory_occupied_bytes": m["metrics"]["memory_occupied_bytes"]["value"]}


def main(argv=None) -> int:
    from pccap.harness.lease import gpu_lease

    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--arms", nargs="*", default=["C0", "C1", "C2", "CR"])
    ap.add_argument("--datasets", nargs="*", default=["zsre", "counterfact"])
    ap.add_argument("--out", default=str(S2 / "throughput.json"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--cr-dist", action="store_true", help="CR uses manifests/cr_distribution.json (S3-05) instead of uniform")
    ap.add_argument("--lora-lr", type=float, default=1e-4, help="B1/B3 Adam learning rate (development screen {3e-5, 1e-4, 3e-4})")
    args = ap.parse_args(argv)
    out_path = Path(args.out)
    tok = GPT2Tokenizer()
    unavailable = {"B1": "S2-03 pending", "B3": "S2-04 pending", "B4": "S2-05 pending", "EPC_credit": "REG-03 pending", "grammar": "GRAM-02 pending"}
    for a in args.arms:
        unavailable.pop(a, None)
    out = {"n_per_run": args.n, "runs": {}, "unavailable": unavailable}
    with gpu_lease("S2-06", stage="S2", projected_seconds=3 * 3600, exclusive=True) as lease:
        for arm in args.arms:
            for ds in args.datasets:
                r = profile_arm(arm, ds, args.n, tok, S2 / ("throughput" + (f"_{args.tag}" if args.tag else "")) / arm / ds, cr_dist=args.cr_dist, lora_lr=args.lora_lr)
                out["runs"][f"{arm}/{ds}"] = r
                print(f"{arm} {ds}: learn {r['learning_accel_seconds_per_edit']:.3f} s/edit, query {r['query_accel_seconds_per_edit']:.3f} s/edit, "
                      f"wall {r['wall_seconds_per_edit']:.2f} s/edit, ES {r['metrics']['es_immediate']:.2f} RET-GS {r['metrics']['ret_gs_end']}", flush=True)
                out_path.write_text(json.dumps({**out, "lease": lease.report, "partial": True}, indent=1, default=float))
        out["lease"] = lease.report
        out["other_cuda_processes_before"] = lease.other_cuda_processes()
    out["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out_path.write_text(json.dumps(out, indent=1, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
