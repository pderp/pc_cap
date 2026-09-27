"""A readable slide-5 view of existing triplet retention; no new analysis."""

from __future__ import annotations

import argparse
import json
import site
import statistics
from pathlib import Path

from aw.pc_v0_report import ROOT, sha


def render(output):
    site.addsitedir(
        str(ROOT.parent / "assets/envs/status-paper-20260911/lib/python3.12/site-packages")
    )
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out = Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = ROOT / "logs/R1/reports/triplet/summary.json"
    rows = json.loads(source.read_bytes())["groups"]
    lookup = {(r["dataset"], r["condition"], r["realization"]): r for r in rows}
    plotted = []
    with plt.rc_context({"font.size": 16, "axes.spines.top": False, "axes.spines.right": False}):
        fig, axes = plt.subplots(1, 3, figsize=(14, 4.4), sharey=True)
        for ax, ds, title in zip(
            axes,
            ("zsre", "counterfact", "mquake"),
            ("zsRE · 1,000 edits", "CounterFact · 1,000 edits", "MQuAKE · 300 edits"),
            strict=True,
        ):
            for condition, label, color, marker in (
                ("R1_learned_ff", "Learned reader", "#2369a7", "o"),
                ("R1_nonlearned", "Random reader", "#cb6928", "s"),
                ("v0_stable", "Stable cap", "#4b8a58", "^"),
            ):
                values = [lookup[ds, condition, r]["primary"]["RET-GS"] for r in range(3)]
                if any(
                    len(v) != 5 or not all(np.isfinite(x) and 0 <= x <= 1 for x in v)
                    for v in values
                ):
                    raise ValueError("five finite order fractions per realization required")
                avg = np.array([statistics.mean(v) for v in values])
                low, high = np.array([min(v) for v in values]), np.array([max(v) for v in values])
                ax.errorbar(
                    range(3),
                    avg,
                    yerr=[avg - low, high - avg],
                    color=color,
                    marker=marker,
                    markersize=7,
                    linewidth=2,
                    capsize=4,
                    label=label,
                )
                plotted.append(
                    dict(
                        dataset=ds,
                        condition=condition,
                        realization_means=avg.tolist(),
                        order_values=values,
                        mean_over_cells=statistics.mean(avg),
                    )
                )
            ax.set(
                title=title,
                xlabel="Realization",
                xticks=[0, 1, 2],
                ylim=(-0.035, 1.035),
                xlim=(-0.15, 2.15),
            )
            ax.grid(axis="y", alpha=0.2)
        axes[0].set_ylabel("Paraphrase retention")
        handles, labels = axes[0].get_legend_handles_labels()
        fig.legend(
            handles, labels, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.01), frameon=False
        )
        fig.text(
            0.5,
            0.025,
            "Points average five dependent orders; whiskers show order range, not confidence intervals.",
            ha="center",
            fontsize=12,
        )
        fig.tight_layout(rect=(0, 0.075, 1, 0.88))
        exports = []
        for extension in ("png", "svg", "pdf"):
            path = out / f"paraphrase-retention.{extension}"
            fig.savefig(path, dpi=160)
            exports.append(dict(path=str(path), sha256=sha(path)))
        plt.close(fig)
    manifest = dict(
        source=dict(path=str(source), sha256=sha(source)),
        producer=dict(path=str(Path(__file__).resolve()), sha256=sha(__file__)),
        exports=exports,
        plotted=plotted,
        scope="existing 135-cell triplet; no new inference",
    )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    render(parser.parse_args().output)
