"""AW-B4 survival curves from verified vectors; calibration and evaluation separate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "logs/additional_work/AW-B/report-20260929/calibration-review.json"
OUTPUT = ROOT.parent / "assets/presentation-materials/figures/aw_b"


def survival(values):
    """Right-continuous P(X>x); all positions, including nonpositive, in N."""
    a = np.sort(np.asarray(values, dtype=float).ravel())
    if len(a) == 0 or not np.isfinite(a).all():
        raise ValueError("finite nonempty loss array required")
    x = np.unique(np.r_[0.0, a[a > 0]])
    y = (len(a) - np.searchsorted(a, x, side="right")) / len(a)
    return x, y


def draw(report_path=REPORT, output=OUTPUT):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from aw.pc_result_figures import export, sha

    path = Path(report_path)
    report = json.loads(path.read_bytes())
    if report["schema"] != "aw-b-report-v1":
        raise ValueError("verified AW-B report required")
    for p, h in report["sources_sha256"].items():
        if sha(p) != h:
            raise ValueError("changed source: " + p)
    final = report["status"] == "complete"
    source = report["evaluation"] if final else report["calibration"]
    selection = report["selection"]
    mixture = selection["chosen"]["bound"]["key"]
    if not mixture.startswith("mixture:"):
        raise ValueError("figure requires the selected mixture")
    inputs = [path, Path(__file__).resolve()]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, ds in zip(axes, ("zsre", "counterfact")):
        rows = [
            row for name, row in source["cells"].items() if name == ds or name.startswith(ds + "-")
        ]
        for key, color, label in (
            ("v5", "#9e492f", "Unwrapped v5"),
            (mixture, "#246b8d", "Mixture, ρ = exp(−1)"),
        ):
            distributions = []
            for row in rows:
                binding = row["harm"][key]["vectors"]
                p = Path(binding["path"])
                if sha(p) != binding["sha256"]:
                    raise ValueError("changed vector")
                with np.load(p, allow_pickle=False) as f:
                    v = f["values"]
                    values = (v[:, :, 0] - v[:, :, 2]).ravel()
                inputs.append(p)
                distributions.append(values)
                x, y = survival(values)
                ax.step(
                    x,
                    y,
                    where="post",
                    color=color,
                    alpha=0.22 if final else 0.9,
                    linewidth=1.3,
                    label=label if len(rows) == 1 else None,
                )
            if final:
                # Equal position counts: pooled curve equals mean of order-specific survival curves.
                x, y = survival(np.concatenate(distributions))
                ax.step(x, y, where="post", color=color, linewidth=2, label=label + " (order mean)")
        ax.axvline(1, color="#565656", linestyle="--", linewidth=1, label="1-nat ceiling")
        ax.set(
            title=ds,
            xlabel="Positive loss increase vs base (nats)",
            yscale="log",
            ylim=(0.5 / (245237 * len(rows)), 1.2),
            xlim=(0, None),
        )
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("P(ΔNLL > x), all 245,237 positions per memory")
    fig.suptitle(
        "Bounding rare prediction loss at a fixed prefix\n"
        + (
            "Exposed realization-0 evaluation, five orders"
            if final
            else "Development calibration only — evaluation pending"
        ),
        fontsize=13,
    )
    fig.text(
        0.5,
        0.012,
        "Cap-off has zero positive loss increase. Curves include zero / beneficial positions in the denominator.\nPer-token bound against the same base, not a total-loss or generated-text guarantee. No independent-token uncertainty.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.1, 1, 0.88))
    export(fig, Path(output), "evaluation-survival" if final else "calibration-survival", inputs)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", default=str(REPORT))
    p.add_argument("--output", default=str(OUTPUT))
    a = p.parse_args()
    draw(a.report, a.output)
