"""HT-1b: mean/tail and exact empirical survival for the bound round16 snapshot."""

import hashlib
import json
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "logs/heavy_tail/audit-v5-round16-supplement/audit.json"


def plot(output):
    report = json.loads(AUDIT.read_text())
    paths = {
        "v4 · zsRE": "R1_learned_ff-zsre-development-source-9084e84fc6dd00038904",
        "v5 · zsRE": "R1_learned_ff-zsre-development-source-d22ce6801209c6184480",
        "v5 · CounterFact": "R1_learned_ff-counterfact-development-source-bc285b69b70dff8514a4",
    }
    data = []
    references = []
    for label, cell in paths.items():
        source = f"results/R1/stage4_dev_cells/{cell}/attempt-0000/checkpoint-300.json"
        binding = next(s for s in report["source_inventory"] if s["path"] == source)
        raw = (ROOT / source).read_bytes()
        if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
            raise ValueError("audited source changed")
        drift = json.loads(raw)["endpoints"]["drift"]
        s = next(
            s
            for s in report["series"]
            if s["source"] == source
            and s["metric"] == "preservation_nll_minus_original"
            and s["address"] == "$.endpoints.drift.rows"
        )
        harm = np.array([r["cap"] - r["original"] for r in drift["rows"]])
        references.append(
            (
                drift["source_sha256"],
                [(r["item_id"], r["original"], r["capoff"]) for r in drift["rows"]],
            )
        )
        data.append((label, harm, s["statistics"]))
    shared = all(r == references[0] for r in references)
    if not shared:
        raise ValueError("common text/reference population required for this figure")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.9))
    colors = ["#778899", "#187f9f", "#b95627"]
    metrics = [
        ("mean_signed", "Mean signed"),
        ("ES95_positive", "Worst 5% mean"),
        ("maximum_positive", "Maximum"),
    ]
    x = np.arange(len(metrics))
    for i, (label, harm, s) in enumerate(data):
        axes[0].bar(
            x + (i - 1) * 0.24, [s[k] for k, _ in metrics], width=0.24, color=colors[i], label=label
        )
        positive = np.maximum(harm, 0.0)
        thresholds = np.unique(
            np.concatenate(([0.01], positive[positive > 0.01], [max(positive) + 0.2]))
        )
        survival = (
            len(positive) - np.searchsorted(np.sort(positive), thresholds, side="right")
        ) / len(positive)
        axes[1].step(
            thresholds, survival, where="post", color=colors[i], label=label, linewidth=1.8
        )
    axes[0].set_xticks(x, [v for _, v in metrics])
    axes[0].set_yscale("log")
    axes[0].set_ylabel("NLL increase (nats; logarithmic scale)")
    axes[0].set_title("Small averages coexist with large local errors")
    axes[0].legend(frameon=False, fontsize=9)
    axes[1].set_yscale("log")
    axes[1].set_ylim(0.5 / 16256, 100 / 16256)
    axes[1].set_xlim(0.01, 9)
    axes[1].set_xlabel("Positive NLL harm threshold x (nats)")
    axes[1].set_ylabel("Fraction of all positions with harm > x")
    axes[1].set_title("Empirical upper tail (no fitted distribution)")
    for ax in axes:
        ax.grid(axis="y", alpha=0.22)
        ax.set_axisbelow(True)
    fig.suptitle(
        "Development snapshot · 300 edits · 128 shared windows / 16,256 positions", fontsize=12
    )
    fig.text(
        0.05,
        0.025,
        "Original-base reference; dependent positions. v5 full/incremental duplicates counted once.\nDifferent readers/edit histories: descriptive comparisons, not isolated treatment effects.",
        fontsize=9,
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.94))
    output = output.resolve()
    if not output.is_relative_to(ROOT / "logs/heavy_tail"):
        raise ValueError("figure belongs under pc_cap/logs/heavy_tail")
    for suffix in (".pdf", ".svg", ".png"):
        target = output.with_suffix(suffix)
        with target.open("xb") as f:
            fig.savefig(f, format=suffix[1:], dpi=170, bbox_inches="tight")
    plt.close(fig)
    return {"shared_ordered_source_and_both_reference_nll": shared, "panels": len(data), "n": 16256}


if __name__ == "__main__":
    print(plot(ROOT / "logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5"))
