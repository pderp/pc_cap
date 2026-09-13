"""S5-04 input: the substrate contrasts (SE-A vs SB, SE-E vs SE-A) through the frozen paired machinery.

``pccap.analysis.paired.analyze_paired`` analyses the frozen contrasts C2 vs C1 and C2 vs CR. The S5 contrasts are
computed with the SAME code and policy (paired-cluster bootstrap over realizations, orders kept together, the frozen
margins) by relabelling arms in the endpoint rows — treatment → "C2", comparator → "C1" — so no source under the frozen
tree changes. SB rows are the S4 C1 runs (reused, plan §6.11). The "C2-CR" slot is absent by construction, so the
combined classification reads "incomplete"; the contrast of interest is reported from its own checks.
    python scripts/s5_paired.py --dataset zsre  → results/S5/paired_<dataset>.json"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = "frozen-confirmatory-v2-84126123"
CONTRASTS = (("SE-A", "SB"), ("SE-E", "SE-A"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--draws", type=int, default=10_000)
    args = ap.parse_args()
    from pccap.analysis.paired import analyze_paired
    from pccap.analysis.s4_06 import collect_rows, expected_from_loader

    s4_rows, n4 = collect_rows(ROOT / "results" / "S4" / EXP, args.dataset, EXP)
    s5_rows, n5 = collect_rows(ROOT / "results" / "S5" / EXP, args.dataset, EXP)
    by_arm: dict[str, list] = {}
    for r in s4_rows:
        if r["arm"] == "C1":
            by_arm.setdefault("SB", []).append({**r, "arm": "SB"})
    for r in s5_rows:
        by_arm.setdefault(r["arm"], []).append(r)
    expected = expected_from_loader(args.dataset)
    out = {"dataset": args.dataset, "experiment_id": EXP, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "method": "frozen analyze_paired with arm relabelling (treatment→C2, comparator→C1); SB = the S4 C1 runs",
           "rows": {a: len(v) for a, v in by_arm.items()}, "notes": n4 + n5, "contrasts": {}}
    for treat, comp in CONTRASTS:
        if treat not in by_arm or comp not in by_arm:
            out["contrasts"][f"{treat}-{comp}"] = {"status": "unavailable", "missing": [a for a in (treat, comp) if a not in by_arm]}
            continue
        rows = [{**r, "arm": "C2"} for r in by_arm[treat]] + [{**r, "arm": "C1"} for r in by_arm[comp]]
        rep = analyze_paired(rows, expected_items=expected, stream_id=args.dataset, draws=args.draws)
        c = rep["contrasts"]["C2-C1"]
        out["contrasts"][f"{treat}-{comp}"] = {"treatment": treat, "comparator": comp, "status": c["status"], "classification_of_this_contrast": c["classification"],
                                               "checks": c["checks"], "measures": {k: {kk: vv for kk, vv in v.items() if kk != "paired_differences"} for k, v in c["measures"].items()},
                                               "missing": c.get("missing"), "margins": rep.get("margins")}
    (ROOT / "results" / "S5").mkdir(exist_ok=True)
    (ROOT / "results" / "S5" / f"paired_{args.dataset}.json").write_text(json.dumps(out, indent=1, default=float))
    for name, c in out["contrasts"].items():
        if c.get("status") == "unavailable":
            print(name, "unavailable", c["missing"])
            continue
        print(f"{name}: {c['classification_of_this_contrast']} checks {c['checks']}")
        for meas, m in c["measures"].items():
            e, iv = m.get("estimate", {}), m.get("interval", {})
            print(f"  {meas:8s} Δ={e.get('value'):+.4f} 97.5% [{iv.get('lower'):+.4f}, {iv.get('upper'):+.4f}] per-realization {[round(x, 4) for x in m.get('realization_means', [])]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
