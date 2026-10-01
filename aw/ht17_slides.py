"""Presentation-sized HT-17 frequency/severity panels; reads saved summaries only."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = json.loads(args.report.read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.1))
    labels = {
        "R1_learned_ff": "Learned v5",
        "v0_stable": "Stable v0",
        "R1_nonlearned": "Random reader",
    }
    colors = dict(zip(labels, ("#276f95", "#b26226", "#727c3c"), strict=True))
    for ax, dataset in zip(axes, ("zsre", "counterfact"), strict=True):
        for group in report["groups"]:
            if (
                group["phase"] != "stage4"
                or group["dataset"] != dataset
                or group["condition"] not in labels
            ):
                continue
            row = group["thresholds"]["0.01"]
            x, y, cond = row["frequency"], row["conditional_mean_loss"], group["condition"]
            if not x or y is None:
                ax.text(
                    0.03,
                    0.95,
                    "Stable v0: no observed harmful changes;\nconditional severity undefined; RET-GS = 0",
                    transform=ax.transAxes,
                    va="top",
                    fontsize=10,
                )
                continue
            ax.hlines(y, *row["frequency_interval"], color=colors[cond])
            if row["conditional_mean_interval"] is not None:
                ax.vlines(x, *row["conditional_mean_interval"], color=colors[cond])
            ax.scatter(x, y, s=70, color=colors[cond], label=labels[cond], zorder=3)
        ax.set_title("zsRE" if dataset == "zsre" else "CounterFact", fontsize=14)
        ax.set_xscale("log")
        low, high = ax.get_xlim()
        ax.xaxis.set_major_locator(
            FixedLocator([math.exp(math.log(low) + i * math.log(high / low) / 3) for i in range(4)])
        )
        ax.xaxis.set_minor_locator(NullLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{100 * x:.3g}%"))
        ax.set_xlabel("Fraction of all positions with ΔNLL > 0.01 nat", fontsize=11)
        ax.set_ylabel("Mean ΔNLL among those positions (nats)", fontsize=11)
        ax.grid(alpha=0.2)
        ax.legend(loc="lower left" if dataset == "zsre" else "lower right", fontsize=10)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.text(
        0.5,
        0.025,
        "Own cap-off reference · 1,000 edits · 15 cells/dataset/condition · same 245,237 positions reused\n"
        "95% joint-window intervals conditional on observed cells; window independence unverified; no population coverage claim.",
        ha="center",
        fontsize=10,
    )
    paths = []
    for ext in ("png", "svg", "pdf"):
        path = args.out / f"frequency-severity-stage4.{ext}"
        fig.savefig(path, dpi=180, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)

    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    (args.out / "manifest.json").write_text(
        json.dumps(
            {
                "source": {"path": str(args.report.resolve()), "sha256": digest(args.report)},
                "generator_sha256": digest(Path(__file__)),
                "exports": {str(p.resolve()): digest(p) for p in paths},
                "selection": "All primary Stage-4 cells on both datasets, not outcome-selected",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
