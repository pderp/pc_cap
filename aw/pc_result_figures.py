"""Standalone publication figures from completed PC reports; no JAX/model imports."""

from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / "assets/presentation-materials/figures"
COLORS = {"SE-A": "#226b95", "SE-E": "#b65330"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def export(fig, folder, name, inputs):
    folder.mkdir(parents=True, exist_ok=True)
    records = []
    for ext in ("png", "pdf", "svg"):
        path = folder / (name + "." + ext)
        fig.savefig(path, dpi=180, bbox_inches="tight")
        records.append(dict(path=str(path), sha256=sha(path)))
    plt.close(fig)
    (folder / (name + "-manifest.json")).write_text(
        json.dumps(
            dict(
                inputs={str(p): sha(p) for p in inputs},
                generator={str(Path(__file__).resolve()): sha(__file__)},
                exports=records,
            ),
            indent=2,
        )
        + "\n"
    )


def main():
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    for version in (0, 1):
        folder = (
            ROOT
            / f"logs/additional_work/PC-v{version}"
            / ("report-60-20260927" if version == 0 else "report-4-20260927")
        )
        rp, hp = folder / "report.json", folder / "harm/report.json"
        report, harm = (json.loads(p.read_text()) for p in (rp, hp))
        out = BASE / f"pc_v{version}" / "completed-20260928"
        fig, axes = plt.subplots(1, 3, figsize=(13, 4.4))
        if version == 0:
            for r, marker in enumerate(("o", "s", "^")):
                y = [
                    next(
                        a
                        for a in report["aggregates"]
                        if a["dataset"] == "zsre" and a["metric"] == m
                    )["realizations"][r]
                    for m in ("ES", "RET-ES", "RET-GS", "LS")
                ]
                axes[0].scatter(
                    np.arange(4) + (r - 1) * 0.14,
                    np.asarray(y) * 100,
                    marker=marker,
                    label=f"realization {r}",
                )
            axes[0].axhline(0, color="gray", linewidth=0.7)
            axes[0].set(
                xticks=range(4),
                xticklabels=["ES", "RET-ES", "RET-GS", "LS"],
                ylabel="SE-E − SE-A (percentage points)",
                title="zsRE: five-order means",
            )
            axes[0].legend(fontsize=8)
        else:
            for i, arm in enumerate(("SE-A", "SE-E")):
                y = [
                    next(c for c in report["cells"] if c["dataset"] == ds and c["arm"] == arm)[
                        "checkpoints"
                    ]["300"]["RET-GS"]["value"]
                    for ds in ("zsre", "counterfact")
                ]
                axes[0].bar(
                    np.arange(2) + (i - 0.5) * 0.3, y, width=0.28, label=arm, color=COLORS[arm]
                )
            axes[0].set(
                xticks=range(2),
                xticklabels=["zsRE", "CounterFact"],
                ylim=(0, 1.05),
                ylabel="Paraphrase retention (fraction)",
                title="300 edits; one realization/order",
            )
            axes[0].legend()
        for i, arm in enumerate(("SE-A", "SE-E")):
            s = [
                c["readout"]["summary"]["original"]["loss"]
                for c in harm["cells"]
                if c["dataset"] == "zsre" and c["arm"] == arm
            ]
            values = [
                statistics.mean(x[k] for x in s)
                for k in ("mean_signed", "es99_positive", "maximum_signed")
            ]
            axes[1].scatter(
                np.arange(3) + (i - 0.5) * 0.14, values, s=45, color=COLORS[arm], label=arm
            )
            for x, y in zip(np.arange(3) + (i - 0.5) * 0.14, values):
                axes[1].annotate(
                    f"{y:.3g}",
                    (x, y),
                    xytext=(0, 7 if i == 0 else -14),
                    textcoords="offset points",
                    ha="center",
                    fontsize=8,
                )
            cells = [c for c in report["cells"] if c["arm"] == arm]
            times = [
                statistics.mean(
                    c["finish"]["elapsed_process_seconds"] for c in cells if c["dataset"] == ds
                )
                for ds in ("zsre", "counterfact")
            ]
            axes[2].bar(
                np.arange(2) + (i - 0.5) * 0.3, times, width=0.28, label=arm, color=COLORS[arm]
            )
        axes[1].set(
            yscale="log",
            xticks=range(3),
            xticklabels=["Mean ΔNLL", "ES99+", "Mean max" if version == 0 else "Maximum"],
            ylabel="zsRE loss increase (nats; log axis)",
            title=f"{harm['selection']['positions']:,} positions / cell",
        )
        axes[1].legend()
        axes[1].margins(y=0.22)
        axes[2].set(
            xticks=range(2),
            xticklabels=["zsRE", "CounterFact"],
            ylabel="Mean seconds / cell",
            title="Whole-process cost" if version == 0 else "Stream-engine cost",
        )
        axes[2].legend()
        fig.suptitle(
            "Corrected PC credit vs adjoint — "
            + ("v0 cap, 60 cells" if version == 0 else "fixed-v5 reader, four cells"),
            fontsize=14,
        )
        note = "Exposed supplemental data. " + (
            "Three realizations; orders averaged within realization. CounterFact primary ES/RET-ES/LS=1, RET-GS=0."
            if version == 0
            else "No equivalence inference from one realization. Reader remains BP-trained. Whole-process costs are in the report."
        )
        fig.text(0.5, 0.01, note, ha="center", fontsize=9)
        fig.tight_layout(rect=(0, 0.05, 1, 0.94))
        export(fig, out, "efficacy-harm-cost", [rp, hp])


if __name__ == "__main__":
    main()
