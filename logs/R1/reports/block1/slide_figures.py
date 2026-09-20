"""Export descriptive realization-0 figures, with no inferential error bars."""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATASETS = ("zsre", "counterfact", "mquake")
CONDITIONS = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
LABELS = ("Learned v5", "Random reader", "Stable v0")
COLORS = ("#2369a7", "#cb6928", "#4b8a58")


def ref(path):
    with Path(path).open("rb") as stream:
        return dict(path=str(Path(path).resolve()), sha256=hashlib.file_digest(stream, "sha256").hexdigest())


def main():
    replace = sys.argv[1:] == ["--replace"]
    if sys.argv[1:] and not replace:
        raise ValueError("only --replace is supported")
    summary_path = HERE / "summary.json"
    summary_ref = ref(summary_path)
    data = json.loads(summary_path.read_text())
    groups = {(r["dataset"], r["condition"]): r for r in data["groups"]}
    output = HERE / "slide-figures"
    destination = ROOT.parent / "assets/presentation-materials/figures/block1"
    output.mkdir(exist_ok=replace)
    destination.mkdir(parents=True, exist_ok=True)
    exports = []
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

    def save(fig, name, title, note):
        fig.suptitle(title + "\nBlock 1: one realization, five orders", fontsize=17)
        fig.text(0.02, 0.015, note, fontsize=10, va="bottom")
        fig.tight_layout(rect=(0, 0.095, 1, 0.91))
        for ext in ("png", "pdf", "svg"):
            path = output / (name + "." + ext)
            fig.savefig(path, dpi=160)
            target = destination / path.name
            with target.open("wb" if replace else "xb") as stream, path.open("rb") as source:
                shutil.copyfileobj(source, stream)
            exports.append(dict(source=ref(path), presentation_copy=ref(target)))
        plt.close(fig)

    fig, axes = plt.subplots(3, 3, figsize=(13.5, 9.5))
    for di, ds in enumerate(DATASETS):
        for mi, metric in enumerate(("RET-GS", "RET-ES", "LS")):
            ax = axes[di, mi]
            for i, cond in enumerate(CONDITIONS):
                s = groups[ds, cond]["primary"][metric]
                ax.scatter(i + np.linspace(-0.07, 0.07, 5), s["values"], s=22, color=COLORS[i])
                ax.plot([i - .22, i + .22], [s["mean"]] * 2, lw=2, color=COLORS[i])
            horizon = 300 if ds == "mquake" else 1000
            ax.set(title=f"{ds} · {horizon} edits · {metric}", ylim=(-.04, 1.07),
                   xticks=range(3), xticklabels=LABELS, ylabel="Fraction correct / preserved")
            ax.tick_params(axis="x", labelsize=9)
    save(fig, "final-behavior", "Paraphrase retention and preservation at the final checkpoint",
         "Dots: five orders of the same items; bars: their descriptive mean. No confidence intervals.\nRET-GS: paraphrase retention; RET-ES: original edit-prompt retention; LS: 50 locality prompts. MQuAKE is descriptive at 300.")

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5))
    for mi, metric in enumerate(("RET-GS", "ES", "LS")):
        ax = axes[mi]
        rows = [r for r in data["primary_realization0"] if r["metric"] == metric and r["complete"]]
        for y, row in enumerate(rows):
            color = COLORS[0] if row["dataset"] == "zsre" else COLORS[1]
            ax.plot([row["minimum"], row["maximum"]], [y, y], color=color, lw=3)
            ax.scatter(row["order_values"], [y] * 5, color=color, s=28, alpha=.65)
        ax.axvline(0, color="gray", lw=.8)
        ax.set(yticks=range(len(rows)), yticklabels=[r["dataset"] + " vs " + ("random" if r["contrast"].endswith("R1_nonlearned") else "stable") for r in rows],
               xlabel="Learned v5 minus control", title=metric)
        ax.invert_yaxis()
        ax.xaxis.set_major_locator(MaxNLocator(nbins=3))
        ax.tick_params(axis="x", labelsize=9)
    save(fig, "paired-order-effects", "Observed paired effects; intervals and classifiers remain unavailable",
         "Dots and line spans show the five paired order differences and their min–max range, NOT confidence intervals.\nOnly 12 of 63 registered metric slots have a realization-0 estimate here. MQuAKE-1000 is unavailable by design.")

    fig, axes = plt.subplots(1, 3, figsize=(14, 6.5))
    metrics = ("mean_signed_nll", "maximum_positive_nll", "half_kl_positions")
    titles = ("Mean signed\nloss increase", "Largest single-position\nloss increase", "Positions carrying\nhalf the KL")
    for ax, metric, title in zip(axes, metrics, titles, strict=True):
        vals = [groups[ds, "R1_learned_ff"]["fidelity"]["capoff"][metric]["mean"] for ds in DATASETS]
        ax.bar(range(3), vals, color=COLORS)
        for x, value in enumerate(vals):
            ax.text(x, value, f"{value:.5g}", ha="center", va="bottom")
        ax.set(title=title, xticks=range(3), xticklabels=DATASETS,
               ylabel="Positions (out of 245,237)" if metric == "half_kl_positions" else "Nats", ylim=(0, max(vals) * 1.2))
    save(fig, "concentrated-harm", "Small average changes coexist with concentrated large changes",
         "Learned v5; full validation, own-cap-off reference. The original-base reference is identical in these cells.\nAll five orders have identical final summaries within each dataset. This demonstrates concentration, not a power-law tail.")
    for name in ("cap-fidelity", "full-validation-tails", "checkpoint-trajectories"):
        for ext in ("png", "pdf", "svg"):
            path = HERE / "appendix/figures" / (name + "." + ext)
            target = destination / path.name
            with target.open("wb" if replace else "xb") as stream, path.open("rb") as source:
                shutil.copyfileobj(source, stream)
            exports.append(dict(source=ref(path), presentation_copy=ref(target)))
    if ref(summary_path) != summary_ref:
        raise ValueError("plot input changed")
    with (output / "manifest.json").open("w" if replace else "x") as stream:
        json.dump(dict(summary=summary_ref, analysis=ref(HERE / "analysis.json"), producer=ref(__file__), exports=exports,
                       interpretation="Descriptive within-realization order variation; no confidence interval or classifier."), stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(custom_figures=3, custom_exports=9, presentation_exports=len(exports))))


if __name__ == "__main__":
    main()
