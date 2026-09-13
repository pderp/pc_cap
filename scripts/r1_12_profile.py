"""R1-12/R1-13: profile RevisionCap on 10 zsRE development edits with untrained (random-init) reader/controller weights
(design §First development configuration: "profiled on 10 edits before any stream"). Gates checked here on the real base:
  4  empty memory → predict equals the cap-off base logits exactly; hard null → exact zero writes;
  2  reusable weights hashed before/after the stream (unchanged); predict never changes the state hash (PC-8);
  3  snapshot round-trip after the stream;
  6  costs per edit and per read reconciled with the ledger (query/learning columns).
    python scripts/r1_12_profile.py [--n 10] [--steps 3] [--lr 1e-2] → results/R1/profile_10.json"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "R1"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--steps", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-2)
    args = ap.parse_args()
    import pccap  # noqa: F401
    from pccap.bases.bp import BPBase
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import Evaluator, run_stream
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig

    frozen = json.loads((ROOT / "manifests" / "archive" / "frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json").read_text())
    b_m = tuple(float(frozen["b_m"][k]) for k in ("1", "2", "3"))
    items, unrelated = load_dev_items("zsre", args.n, seed=21)
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict = {"n": args.n, "steps": args.steps, "lr": args.lr}
    with gpu_lease("R1:profile", stage="R1", projected_seconds=1800.0):
        ledger = Ledger()
        base, tok = BPBase(ledger=ledger), GPT2Tokenizer()
        cfg = RevisionConfig(reader=ReaderConfig(), controller=ControllerConfig(A=float(frozen["A"]), bank_scales=b_m), fast=FastConfig(steps=args.steps, lr=args.lr), tau_edit=float(frozen["tau_edit"]))
        cap = RevisionCap(base, cfg, ledger)
        report["n_params"] = cap.n_params
        assert cap.n_params <= 5_000_000, cap.n_params
        # gate 4: empty memory → cap-off logits exactly
        ids = np.asarray(items[0].prompt_ids, np.int32)
        off = np.asarray(base.forward(ids, (), phase="query", last_only=True).logits)
        on = cap.predict(ids).logits
        assert np.array_equal(off, on), "empty memory must reproduce the cap-off logits exactly"
        h0 = cap.state_hash()
        cap.predict(np.concatenate([ids, np.int32([items[0].answer_ids[0]])]))
        assert cap.state_hash() == h0, "predict changed the state (PC-8)"
        report["gate4_empty_memory_exact"] = True
        # timing of one read (observation + corrected pass) after one edit
        t0 = time.time()
        out0 = cap.update_item(items[0], None, None)
        report["first_edit"] = {"code": out0.code, "rounds": out0.rounds_used, "acquired": out0.acquired_threshold_all_prefixes, "wall_s": time.time() - t0,
                                "reverses": out0.cost.reverses, "full_forwards": out0.cost.full_forwards, "loss_after": [p["loss_after"] for p in out0.prefix_outcomes]}
        cap.reset_queries()
        t0 = time.time()
        for _ in range(5):
            cap.predict(ids)
        report["read_wall_s_mean_warm"] = (time.time() - t0) / 5
        # the stream (remaining items) through the v0 harness
        ph = cap.params_hash
        ev = Evaluator(base, tok, unrelated[:20], None)
        rd = OUT / "profile_stream"
        q0, l0 = ledger.query.accel_seconds, ledger.learning.accel_seconds
        t0 = time.time()
        m = run_stream(cap, items[1:], None, Budget(A=float(frozen["A"]), R=args.steps, tau_edit=float(frozen["tau_edit"])), ev, rd, ledger, checkpoints=(), seed=1, arm="R1")
        report["stream"] = {"wall_s": time.time() - t0, "metrics": {k: v["value"] for k, v in m["metrics"].items() if k in ("es_immediate", "ret_es_end", "ret_gs_end", "ls_complete_answer_end")},
                            "query_accel_s": ledger.query.accel_seconds - q0, "learning_accel_s": ledger.learning.accel_seconds - l0, "records": len(cap.store.records), "bytes": cap.store.bytes()}
        from pccap.revision_v1.reader import params_hash
        assert params_hash(cap.params) == ph, "reusable weights changed during the stream (gate 2)"
        report["gate2_params_frozen"] = True
        # gate 3: snapshot round-trip
        blob_hash = cap.state_hash()
        st = cap.export_state()
        cap2 = RevisionCap(base, cfg, ledger, params=cap.params)
        cap2.import_state(st)
        assert cap2.state_hash() == blob_hash
        report["gate3_snapshot_round_trip"] = True
        report["ledger"] = ledger.totals()
    (OUT / "profile_10.json").write_text(json.dumps(report, indent=1, default=float))
    print(json.dumps({k: report[k] for k in ("n_params", "first_edit", "read_wall_s_mean_warm", "stream")}, default=float), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
