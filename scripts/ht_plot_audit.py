"""Plot the saved historical drift distribution; no model execution."""

import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/home/derp/cap/assets/matplotlib-ht-round15")
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "logs/heavy_tail/audit-20260915-round15"
    audit = json.loads((folder / "audit.json").read_text())
    selected = next(
        s
        for s in audit["series"]
        if s["metric"] == "preservation_nll_minus_original"
        and "development_profile-" in s["source"]
    )
    path = ROOT / selected["source"]
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != selected["source_sha256"]:
        raise ValueError("audited source changed")
    rows = json.loads(raw)["endpoints"]["drift"]["rows"]
    delta = np.asarray([r["cap"] - r["original"] for r in rows], dtype=float)
    positive = np.maximum(delta, 0)
    stats = selected["statistics"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
    nonzero = np.sort(positive[positive > 0])
    surv = np.arange(len(nonzero), 0, -1) / len(positive)
    axes[0].step(nonzero, surv, where="pre", color="#185d88")
    axes[0].set(
        xscale="log",
        yscale="log",
        xlabel="Positive NLL harm (nats)",
        ylabel="Fraction of all positions at or above threshold",
    )
    axes[0].set_title("Empirical tail; no fitted power law")
    names = ["Mean signed", "p95 positive", "ES95 positive", "Maximum"]
    values = [
        stats["mean_signed"],
        stats["p95_positive"],
        stats["ES95_positive"],
        stats["maximum_positive"],
    ]
    axes[1].bar(names, values, color=["#185d88", "#448c90", "#d99a36", "#b84035"])
    axes[1].set(yscale="log", ylabel="NLL harm (nats)")
    axes[1].set_title("One large event is hidden by central summaries")
    axes[1].tick_params(axis="x", rotation=15)
    fig.suptitle(
        "Historical v4 development reader: 300 zsRE edits, 128 windows, 16,256 positions",
        fontsize=11,
    )
    fig.supxlabel(
        "Exact zero positive harm: 10,142 / 16,256; one position exceeds 0.01 nat; max at w125:p26.",
        fontsize=9,
    )
    for suffix in ("pdf", "svg"):
        target = folder / f"mean_vs_tail.{suffix}"
        with target.open("xb") as stream:
            fig.savefig(stream, format=suffix)
    plt.close(fig)


if __name__ == "__main__":
    main()
