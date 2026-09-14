"""M5: choose the deployment locality rule per dataset on a DEVELOPMENT stream — the null threshold (and optionally the
cosine gate) that maximizes RET-GS subject to LS ≥ ls_min — from existing stream evaluations or by running a sweep.
Confirmatory streams are fresh draws; the chosen rule is fixed before the freeze and stated in the protocol.
    python scripts/r1_52_operating_point.py --theta <npz> --dataset zsre|counterfact [--thresholds 0.15,0.25,0.5,0.7,0.85,0.95] [--gates none,0.93] [--ls-min 0.99] [--no-query-null]
    → results/R1/operating_point_<dataset>_<tag>.json"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--dataset", required=True, choices=("zsre", "counterfact"))
    ap.add_argument("--thresholds", default="0.15,0.25,0.5,0.7,0.85,0.95,1.01")
    ap.add_argument("--gates", default="none,0.93")
    ap.add_argument("--ls-min", type=float, default=0.99)
    ap.add_argument("--no-query-null", action="store_true")
    ap.add_argument("--tag", default=None)
    ap.add_argument("--no-lease", action="store_true")
    args = ap.parse_args()
    import hashlib
    cfg_id = hashlib.sha256((Path(args.theta).read_bytes() if Path(args.theta).exists() else b"") + f"{args.dataset}|{args.no_query_null}".encode()).hexdigest()[:8]
    tag = (args.tag or Path(args.theta).parent.name) + f"_{cfg_id}"  # R50-08: the run identity binds the weights and configuration
    rows = []
    for th in args.thresholds.split(","):
        for gate in args.gates.split(","):
            run_tag = f"op_{tag}_null{th}_gate{gate}"
            summary = ROOT / "results" / "R1" / (f"stream_eval_{run_tag}.json" if args.dataset == "zsre" else f"stream_eval_{run_tag}@counterfact.json")
            if not summary.exists():
                cmd = [sys.executable, str(ROOT / "scripts" / "r1_13_stream_eval.py")] + (["--no-lease"] if args.no_lease else []) + ["--dataset", args.dataset, "--theta", args.theta, "--tag", run_tag,
                       "--delta-steps", "5", "--delta-lr", "0.1", "--null-threshold", th] + (["--min-score", gate] if gate != "none" else []) + (["--no-query-null"] if args.no_query_null else [])
                subprocess.run(cmd, check=True, capture_output=True)
            d = json.loads(summary.read_text())
            sm = d["stream"] if "stream" in d else d["stream_metrics"]
            rows.append({"null_threshold": float(th), "gate": None if gate == "none" else float(gate), "ES": sm["es_immediate"], "RET_ES": sm["ret_es_end"], "RET_GS": sm["ret_gs_end"], "LS": sm["ls_complete_answer_end"]})
    feasible = [r for r in rows if r["LS"] >= args.ls_min]
    best = max(feasible, key=lambda r: (r["RET_GS"], r["LS"])) if feasible else None
    out = {"dataset": args.dataset, "theta": args.theta, "ls_min": args.ls_min, "grid": {"thresholds": args.thresholds, "gates": args.gates}, "tie_break": "max RET-GS, then max LS", "rows": rows, "chosen": best,
           "caveat": "LS over 50 locality prompts moves in steps of 0.02; LS ≥ 0.99 means 50/50 observed, not 99 % population preservation (R50-08)",
           "rule": "maximize RET-GS subject to LS ≥ ls_min on the development stream; fixed before the freeze; confirmatory streams are fresh draws"}
    path = ROOT / "results" / "R1" / f"operating_point_{args.dataset}_{tag}.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps({"dataset": args.dataset, "chosen": best, "n_rows": len(rows)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
