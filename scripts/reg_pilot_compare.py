"""REG-01: compare the JAX pilot's per-step trajectory with the sibling's logged production run
(read-only reference `results/distillation/50m-tokens/metrics.csv`, commit 298fc719…) over the same
steps (same data, same weights, same protocol). Writes results/REG/pilot_compare.json.

    python scripts/reg_pilot_compare.py --run pilot-100
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SIBLING = Path("/home/derp/cap/llm-by-neural-predictive-coding/results/distillation/50m-tokens/metrics.csv")


def load(path: Path, n: int) -> dict[str, np.ndarray]:
    rows = [r for r in csv.DictReader(path.open()) if int(r["step"]) < n]
    cols = ("bp_loss", "pc_loss", "inner_energy_end", "tracking_residual", "pc_grad_norm", "inner_grad_norm_last", "T")
    return {c: np.array([float(r[c]) for r in rows]) for c in cols} | {"n": len(rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="pilot-100")
    ap.add_argument("--steps", type=int, default=100)
    args = ap.parse_args()
    ours = load(ROOT / "results" / "REG" / args.run / "metrics.csv", args.steps)
    ref = load(SIBLING, args.steps)
    n = min(ours["n"], ref["n"])
    out = {"run": args.run, "steps_compared": n, "per_metric": {}}
    for c in ("bp_loss", "pc_loss", "inner_energy_end", "tracking_residual", "pc_grad_norm", "inner_grad_norm_last"):
        a, b = ours[c][:n], ref[c][:n]
        sl = slice(2, n)  # steps 0-1 are at the round-off floor (student == teacher), excluded from ratios
        ratio = a[sl] / np.where(b[sl] == 0, np.nan, b[sl])
        out["per_metric"][c] = {
            "pearson_r": float(np.corrcoef(a[sl], b[sl])[0, 1]) if n > 3 else None,
            "median_ratio_ours_over_sibling": float(np.nanmedian(ratio)),
            "iqr_ratio": [float(np.nanpercentile(ratio, 25)), float(np.nanpercentile(ratio, 75))],
            "max_abs_rel_diff": float(np.nanmax(np.abs(ratio - 1))),
            "ours_first5": a[:5].tolist(), "sibling_first5": b[:5].tolist(),
            "ours_mean": float(a[sl].mean()), "sibling_mean": float(b[sl].mean()),
        }
    out["T_identical"] = bool(np.array_equal(ours["T"][:n], ref["T"][:n]))
    p = ROOT / "results" / "REG" / "pilot_compare.json"
    p.write_text(json.dumps(out, indent=1))
    for c, v in out["per_metric"].items():
        print(f"{c:22s} r={v['pearson_r']:.4f} median ratio={v['median_ratio_ours_over_sibling']:.4f} IQR={v['iqr_ratio'][0]:.3f}-{v['iqr_ratio'][1]:.3f} max|rel|={v['max_abs_rel_diff']:.3f}")
    print("wrote", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
