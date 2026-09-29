"""PC-13 publication figure; standard plotting, no model/JAX execution."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

from aw.pc_result_figures import export, sha

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "logs/additional_work/PC-v0/controls-report-20260929/report.json"
OUTPUT = ROOT.parent / "assets/presentation-materials/figures/pc_v0/controls"


def draw(source=SOURCE, output=OUTPUT):
    source, output = Path(source), Path(output)
    r = json.loads(source.read_bytes())
    if r["status"] != "complete" or r["schema"] != "pc-depth-report-v1":
        raise ValueError("complete scientific depth report required")
    for path, h in r["sources_sha256"].items():
        if sha(path) != h:
            raise ValueError("figure source changed: " + path)
    depths = [1, 8, 32]
    x = np.arange(3)
    fig, axes = plt.subplots(1, 4, figsize=(14, 4.2))
    settings = [
        ("RET-ES", "Own-prompt retention", "Fraction", False),
        ("RET-GS", "Paraphrase retention", "Fraction", False),
        ("es99_positive", "Ordinary-text ES99+", "Nats", False),
        ("learning_seconds", "Learning cost", "Seconds / cell", True),
    ]
    for ax, (field, title, label, log) in zip(axes, settings):
        for arm, color, marker in (("SE-A", "#276787", "o"), ("SE-E", "#b64f2d", "s")):
            rows = [
                next(
                    c
                    for c in r["summary"]
                    if (c["dataset"], c["depth"], c["arm"]) == ("zsre", k, arm)
                )
                for k in depths
            ]
            values = [c["metrics"][field] if field.startswith("RET") else c[field] for c in rows]
            ax.plot(x, values, color=color, marker=marker, label=arm, linewidth=1.6)
            for at, value in zip(x, values):
                ax.annotate(
                    f"{value:.3f}" if not log else f"{value:.0f}",
                    (at, value),
                    xytext=(0, 8 if arm == "SE-E" else -15),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                    color=color,
                )
        ax.set(
            xticks=x, xticklabels=depths, xlabel="Error-settling steps", ylabel=label, title=title
        )
        if log:
            ax.set_yscale("log")
        ax.margins(y=0.35)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(loc="upper left", fontsize=8)
    fig.suptitle(
        "More settling: better taught-answer retention, higher cost and ES99+\nzsRE · same order 100 · three realization means",
        fontsize=13,
    )
    fig.text(
        0.5,
        0.01,
        "Exposed S5. 1,000 edits; harm on 4,064 fixed positions. One-step endpoint scores equal adjoint; harm differs slightly numerically.\nNo confidence interval or depth selection. CounterFact is saturated / at a paraphrase floor; full results in the report.",
        ha="center",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.10, 1, 0.88))
    export(fig, output, "depth-retention-harm-cost", [source, Path(__file__).resolve()])


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", default=str(SOURCE))
    p.add_argument("--output", default=str(OUTPUT))
    a = p.parse_args()
    draw(a.report, a.output)
