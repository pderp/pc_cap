"""Render two HT-17 figures from an analysis JSON; no fitting or source reads."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

LABEL = {"R1_learned_ff": "learned v5", "v0_stable": "stable v0",
         "R1_nonlearned": "random reader", "v5": "original v5", "capoff": "cap off",
         "mixture:0.367879": "one-nat mixture", "bp": "BP reader", "epc": "ePC reader"}
COLORS = dict(zip(LABEL, plt.get_cmap("tab10").colors, strict=False))


def save(fig, folder, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(folder / f"{name}.{ext}", dpi=180, bbox_inches="tight")
    plt.close(fig)


def frequency_severity(report, output):
    fig, axes = plt.subplots(3, 2, figsize=(12, 11), squeeze=False)
    phases = ("stage4", "AW-B", "PC-reader")
    for i, phase in enumerate(phases):
        for j, ds in enumerate(("zsre", "counterfact")):
            ax, zero = axes[i, j], []
            for g in report["groups"]:
                cond = g["condition"]
                if g["phase"] != phase or g["dataset"] != ds or cond not in LABEL:
                    continue
                row = g["thresholds"]["0.01"]
                x, y = row["frequency"], row["conditional_mean_loss"]
                label = f"{LABEL[cond]} (n={g['cells']} cells)"
                if not x or y is None:
                    zero.append(label + ": no Δ > 0.01")
                    continue
                color = COLORS[cond]
                lo, hi = row["frequency_interval"]
                ax.hlines(y, lo, hi, color=color, linewidth=1.3)
                if row["conditional_mean_interval"] is not None:
                    lo, hi = row["conditional_mean_interval"]
                    ax.vlines(x, lo, hi, color=color, linewidth=1.3)
                ax.scatter([x], [y], color=color, label=label, s=45, zorder=3)
            if zero:
                ax.text(.02, .97, "\n".join(zero), transform=ax.transAxes, va="top", fontsize=8)
            ax.set_xscale("log")
            low, high = ax.get_xlim()
            ax.xaxis.set_major_locator(FixedLocator(np.geomspace(low, high, 4)))
            ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{100 * value:.3g}%"))
            ax.xaxis.set_minor_locator(NullLocator())
            ax.set_title(f"{phase} · {ds}")
            ax.set_xlabel("Harmful-change frequency: P(ΔNLL > 0.01 nat)")
            ax.set_ylabel("Mean ΔNLL given ΔNLL > 0.01 (nats)")
            ax.grid(alpha=.2, which="both")
            if ax.get_legend_handles_labels()[0]:
                ax.legend(fontsize=8, loc="best")
    pending = len(report["pending_reader_cells"])
    fig.suptitle("How often harmful changes occur, and how severe they are\n"
                 "95% joint-window bootstrap intervals; fixed observed cells", fontsize=14)
    fig.text(.5, .006, f"Own cap-off reference · 245,237 repeated positions per cell · "
             f"{pending} ePC evaluations pending\n"
             "Window independence is unverified; intervals do not cover realization/seed uncertainty. "
             "Studies differ in edit count (Stage-4: 1,000; others: 300).",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .045, 1, .94))
    save(fig, output, "frequency_severity")


def sf(y, shape, scale):
    if shape == 0:
        return np.exp(-y / scale)
    base = 1 + shape * y / scale
    answer = np.zeros_like(y)
    valid = base > 0
    answer[valid] = np.exp(-np.log(base[valid]) / shape)
    return answer


def survival(report, output):
    fig, axes = plt.subplots(3, 2, figsize=(12, 11), squeeze=False)
    for i, condition in enumerate(("R1_learned_ff", "v0_stable", "R1_nonlearned")):
        for j, dataset in enumerate(("zsre", "counterfact")):
            ax = axes[i, j]
            candidates = [c for c in report["cells"] if c["phase"] == "stage4"
                          and c["condition"] == condition and c["dataset"] == dataset
                          and c["realization"] == 0 and c["order"] == 100]
            ax.set_title(f"{LABEL[condition]} · {dataset}")
            ax.set_xlabel("ΔNLL (nats)")
            ax.set_ylabel("P(ΔNLL > x), all positions")
            if not candidates:
                ax.text(.1, .5, "Cell absent from this snapshot", transform=ax.transAxes)
                continue
            c = candidates[0]
            first = c["statistics"]["thresholds"]["0.01"]
            if first["count"] == 0:
                ax.text(.1, .5, "No observed ΔNLL > 0.01 nat\nNo tail fitted", transform=ax.transAxes)
                ax.set_axis_off()
                continue
            x, p = np.asarray(first["survival"]["grid"]), np.asarray(first["survival"]["empirical"])
            ax.loglog(x, np.where(p > 0, p, np.nan), color="black", linewidth=2,
                      label="empirical (sampled grid)")
            notes = []
            for u, row in c["statistics"]["thresholds"].items():
                fit = row["fit"]
                if fit["status"] != "eligible":
                    notes.append(f"u={u}: {fit['status']}")
                    continue
                x = np.geomspace(float(u), c["statistics"]["maximum"], 200)
                p = row["fraction"] * sf(x - float(u), fit["shape"], fit["scale"])
                ax.loglog(x, np.where(p > 0, p, np.nan), linewidth=1.2,
                          label=f"GPD u={u}, shape={fit['shape']:.2f}")
            if "exponential" in first:
                x = np.geomspace(.01, c["statistics"]["maximum"], 200)
                p = first["fraction"] * sf(x - .01, 0, first["exponential"]["scale"])
                ax.loglog(x, p, "--", color="gray", label="exponential u=0.01")
            if notes:
                ax.text(.02, .03, "\n".join(notes), transform=ax.transAxes, fontsize=7)
            ax.set_ylim(1 / c["statistics"]["positions"] / 2, first["fraction"] * 2)
            ax.grid(alpha=.2, which="both")
            ax.legend(fontsize=7, loc="best")
    fig.suptitle("Finite-range survival and threshold sensitivity\n"
                 "Fixed illustration: realization 0, order 100; all cells retained in tables", fontsize=14)
    fig.text(.5, .01, "Curves are fitted conditional excess models × observed exceedance probability. "
             "Invalid/sparse fits omitted explicitly; zero survival is not floored.\n"
             "Curves do not identify an asymptotic law or complexity class; see held-out-window scores "
             "and realization/order variation in the report.", ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .05, 1, .94))
    save(fig, output, "survival_thresholds")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    report = json.loads(args.report.read_text())
    args.out.mkdir(parents=True, exist_ok=False)
    frequency_severity(report, args.out)
    survival(report, args.out)


if __name__ == "__main__":
    main()
