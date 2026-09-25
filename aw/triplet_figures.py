"""Presentation of the completed triplet; reads already computed statistics only."""

from __future__ import annotations

import hashlib
import json
import shutil
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/R1/reports/triplet"
EXPORT = ROOT.parent / "assets/presentation-materials/figures/triplet"


def binding(path):
    path = Path(path)
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    summary = json.loads((OUT / "summary.json").read_bytes())
    analysis = json.loads((OUT / "analysis.json").read_bytes())
    rows = summary["groups"]
    lookup = {(r["dataset"], r["condition"], r["realization"]): r for r in rows}
    datasets = ("zsre", "counterfact", "mquake")
    conditions = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
    labels = ("Learned v5", "Random reader", "Stable v0")
    colors = ("#2369a7", "#cb6928", "#4b8a58")
    target = OUT / "slide-figures"
    target.mkdir(exist_ok=False)
    EXPORT.mkdir(parents=True, exist_ok=True)
    exports = []
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(3, 3, figsize=(13, 9.5), sharex=True, sharey=True)
    for i, dataset in enumerate(datasets):
        for j, metric in enumerate(("RET-GS", "RET-ES", "LS")):
            ax = axes[i, j]
            for condition, label, color in zip(conditions, labels, colors, strict=True):
                vals = [lookup[dataset, condition, r]["primary"][metric] for r in range(3)]
                means = np.array([statistics.mean(v) for v in vals])
                low, high = np.array([min(v) for v in vals]), np.array([max(v) for v in vals])
                ax.errorbar(range(3), means, yerr=[means - low, high - means], color=color,
                            marker="o", linewidth=1.7, capsize=4, label=label)
            n = 300 if dataset == "mquake" else 1000
            ax.set(title=f"{dataset} · {n} edits · {metric}", xticks=[0, 1, 2], ylim=(-.04, 1.07))
            if i == 2:
                ax.set_xlabel("Realization")
            if j == 0:
                ax.set_ylabel("Correct / preserved fraction")
    handles, legend_labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, ncol=3, loc="upper center", bbox_to_anchor=(.5, .94))
    fig.suptitle("Primary triplet across all three realizations", fontsize=17, y=.99)
    fig.text(.03, .015, "Points: means of five orders within each realization; whiskers: order range, not confidence intervals.\n"
             "RET-GS: paraphrase retention; RET-ES: own-prompt retention; LS: locality. MQuAKE at 300 is descriptive.", fontsize=10)
    fig.tight_layout(rect=(0, .065, 1, .90))
    for ext in ("png", "pdf", "svg"):
        path = target / f"behavior-by-realization.{ext}"
        fig.savefig(path, dpi=160)
        with path.open("rb") as src, (EXPORT / path.name).open("xb") as dst:
            shutil.copyfileobj(src, dst)
        exports.append({"source": binding(path), "presentation_copy": binding(EXPORT / path.name)})
    plt.close(fig)
    for name in ("primary-intervals", "cap-fidelity", "full-validation-tails"):
        for ext in ("png", "pdf", "svg"):
            path = OUT / f"appendix/figures/{name}.{ext}"
            with path.open("rb") as src, (EXPORT / path.name).open("xb") as dst:
                shutil.copyfileobj(src, dst)
            exports.append({"source": binding(path), "presentation_copy": binding(EXPORT / path.name)})
    learned = {d: [lookup[d, "R1_learned_ff", r] for r in range(3)] for d in datasets}
    means = {d: statistics.mean(statistics.mean(r["primary"]["RET-GS"]) for r in learned[d]) for d in datasets}
    maximum = max(v for rs in learned.values() for r in rs for v in r["fidelity"]["original"]["max_positive_nll"])
    findings = (f"The learned reader's mean final paraphrase retention across the three realizations is "
                f"**{means['zsre']:.4f} on zsRE**, **{means['counterfact']:.4f} on CounterFact**, and "
                f"**{means['mquake']:.4f} on MQuAKE** (the latter at 300 edits). The retention advantage recurs across "
                "the three tested populations. Three of the four available registered contrasts receive a preliminary "
                "positive label; learned versus stable v0 on CounterFact is **inconclusive**, because locality falls "
                "to 48/50 in realization 2 despite the large retention gain. These labels do not establish population-level superiority.\n\n"
                f"All **45 learned-reader cells fail the mean-KL benchmark**. The largest observed positive token-NLL "
                f"change among them is **{maximum:.3f} nats**. zsRE near-miss preservation is 86/100, 92/100 and 87/100 "
                "in realizations 0, 1 and 2, respectively, while its 50-prompt locality score remains perfect. Useful "
                "retention therefore coexists with specificity failures and concentrated ordinary-text harm.\n\n"
                "![Behavior across realizations](../logs/R1/reports/triplet/slide-figures/behavior-by-realization.png)\n\n")
    # This is a separate presentation pass; the inference producer stays unchanged.
    doc = ROOT / "docs/R1_stage4_report_triplet.md"
    text = doc.read_text()
    marker = "## Final behavior by realization"
    if text.count(marker) != 1 or "All **45 learned-reader cells" in text:
        raise ValueError("expected unadorned native-summary publication")
    text = text.replace(marker, findings + marker)
    for contrast in analysis["contrasts"]:
        for value in contrast["metrics"].values():
            interval = value["adjusted_interval"]
            if interval:
                text = text.replace(str(interval), f"[{interval['lower']:.5f}, {interval['upper']:.5f}]")
    doc.write_text(text)
    with (target / "manifest.json").open("x") as f:
        json.dump({"sources": [binding(OUT / "summary.json"), binding(OUT / "analysis.json"), binding(__file__)],
                   "exports": exports, "readable_report": binding(doc)}, f, indent=2)
        f.write("\n")
    print(json.dumps({"presentation_exports": len(exports), "groups": len(rows)}))


if __name__ == "__main__":
    main()
