"""Grammar per-sequence accelerator cost on the GPU (S4-02 input): a 128-item run per arm through the shared
harness (grammar_context + run_stream, dev-mode seeds), reporting ledger accel seconds per sequence (learning +
immediate evaluation) and the rescoring cost, so the projection's grammar term (``--grammar-learn-s``) is measured
rather than assumed.   python scripts/grammar_timing.py [--n 128] → results/S2/grammar_timing.json"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=128, help="items per run (16 per task x 8 tasks by default)")
    ap.add_argument("--arms", default="C1,C2,CR,C0")
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.contracts import Budget
    from pccap.fixtures.grammar_eval import grammar_context
    from pccap.harness.arms import make_learner, router_for
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream

    frozen = json.loads((ROOT / "manifests" / "frozen.draft.json").read_text())
    out = {"n_items": args.n, "backend": None, "arms": {}, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with gpu_lease("S2:grammar_timing", stage="S2", projected_seconds=600.0):
        import jax

        out["backend"] = jax.default_backend()
        for arm in args.arms.split(","):
            ledger = Ledger()
            gc = grammar_context(0, 0, args.n // 8, ledger=ledger)
            base = gc["base"]
            budget = Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]), R=int(frozen["R"]), tau_edit=float(frozen["tau_edit"]))
            cal = (frozen.get("calibration") or {}).get("GRAM")
            radii = {int(m): float(v) for m, v in cal["radii"]["grammar"].items()} if cal else gc["radii"]
            b_m = {int(m): float(v) for m, v in cal["b_m"].items()} if cal else gc["b_m"]
            learner = make_learner(arm, base, ledger, radii=radii, bank_scales=b_m, read=frozen["radii"]["read"], seed=7)
            router = router_for(arm, cr_distribution=(frozen.get("cr_distribution") or {}).get("grammar"), cr_label="cr_profile_uniform")
            ev = Evaluator(base, gc["tok"], gc["unrelated"], gc["drift"], drift_positions=len(gc["drift"]), drift_window=gc["drift_window"], max_new=1)
            rd = ROOT / "results" / "S2" / "grammar_timing" / arm
            t0 = time.time()
            m = run_stream(learner, gc["items"], router, budget, ev, rd, ledger, checkpoints=(args.n // 2,), seed=8, arm=arm)
            wall = time.time() - t0
            rows = [json.loads(line) for line in (rd / "items.jsonl").read_text().splitlines() if line.strip()]
            upd = sum(r["ledger_delta"]["update"]["total"] for r in rows)
            ev_s = sum(r["ledger_delta"]["immediate_eval"]["total"] for r in rows)
            ck = json.loads((rd / "checkpoints.json").read_text())
            resc = sum(c["rescoring_accel_seconds"]["total"] for c in ck)
            out["arms"][arm] = {"items": len(rows), "update_s_per_item": upd / len(rows), "immediate_eval_s_per_item": ev_s / len(rows),
                                "learn_plus_eval_s_per_item": (upd + ev_s) / len(rows), "rescoring_s_total": resc, "rescoring_s_per_item_rescored": resc / sum(c["items"] for c in ck),
                                "ledger_total_s": ledger.totals()["total"]["accel_seconds"], "wall_s": wall, "es_immediate": m["metrics"]["es_immediate"]["value"]}
            print(arm, json.dumps({k: round(v, 4) if isinstance(v, float) else v for k, v in out["arms"][arm].items()}))
    out["max_learn_plus_eval_s_per_item"] = max(v["learn_plus_eval_s_per_item"] for v in out["arms"].values())
    (ROOT / "results" / "S2" / "grammar_timing.json").write_text(json.dumps(out, indent=1))
    print("max learn+eval s/item", out["max_learn_plus_eval_s_per_item"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
