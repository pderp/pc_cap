"""Render the six bound Stage-4 report figures; no statistics are re-estimated."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from scripts import r1_63l_full_validation_contract as full

DATASETS = ("zsre", "counterfact", "mquake")
COLORS = ("#1864ab", "#d9480f", "#2b8a3e")


def render(data_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    path = Path(data_path).resolve()
    binding = full.ref(path)
    data = json.loads(path.read_text())
    for source, sha in data["source_bindings_sha256"].items():
        if full.sha(source) != sha:
            raise ValueError("report source changed: " + source)
    if (
        data["watch"]["journal"]
        and full.ref(data["watch"]["journal"]["path"]) != data["watch"]["journal"]
    ):
        raise ValueError("watch snapshot changed")
    out = path.parent / "figures"
    out.mkdir(exist_ok=False)
    tables = data["tables"]
    exports = []
    banner = (
        "SYNTHETIC SOFTWARE REHEARSAL — NOT RESEARCH RESULTS"
        if data["synthetic"]
        else "Receipt-bound analysis snapshot"
    )
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})

    def save(fig, name, title, note):
        fig.suptitle(banner + "\n" + title, fontsize=12)
        fig.text(0.02, 0.015, note, fontsize=8, va="bottom")
        fig.tight_layout(rect=(0, 0.075, 1, 0.94))
        for extension in ("png", "pdf", "svg"):
            destination = out / (name + "." + extension)
            fig.savefig(destination, dpi=150)
            exports.append(full.ref(destination))
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    rows = tables["blocks"]
    x = np.arange(len(rows))
    ax.bar(x - 0.18, [r["planned"] for r in rows], 0.36, label="planned")
    ax.bar(x + 0.18, [r["artifact_complete"] for r in rows], 0.36, label="artifact complete")
    ax.set(
        xticks=x,
        xticklabels=[r["block_number"] for r in rows],
        xlabel="Registered block",
        ylabel="Cells",
    )
    ax.legend()
    save(
        fig,
        "disposition",
        "Registered block inventory",
        "Artifact completion is separate from scientific admission, endpoint coverage and benchmark labels. See cell inventory.",
    )

    fig, axes = plt.subplots(3, 3, figsize=(17, 11), squeeze=False)
    for di, ds in enumerate(DATASETS):
        for mi, metric in enumerate(("RET-GS", "ES", "LS")):
            ax = axes[di, mi]
            rows = [r for r in tables["primary"] if r["dataset"] == ds and r["metric"] == metric]
            for y, row in enumerate(rows):
                interval = row["adjusted_interval"]
                if row["estimate"] is None or interval["lower"] is None:
                    ax.text(
                        0.02, y, "unavailable", transform=ax.get_yaxis_transform(), color="#666666"
                    )
                else:
                    ax.plot([interval["lower"], interval["upper"]], [y, y], color=COLORS[di], lw=3)
                    ax.scatter([row["estimate"]], [y], color=COLORS[di], s=18)
            ax.axvline(0, color="gray", lw=0.7)
            ax.set(
                yticks=range(len(rows)),
                yticklabels=[r["contrast"] for r in rows],
                title=f"{ds}: {metric}",
                xlabel="Treatment − control at 1,000 edits",
            )
            ax.set_ylim(len(rows) - 0.5, -0.5)
    save(
        fig,
        "primary-intervals",
        "All 63 registered adjusted intervals, including unavailable slots",
        "Registered family remains 63. With three realization clusters, these are preliminary decision summaries; demonstrated familywise coverage is not claimed. Effects, order dispersion and assumption-labelled secondary t sensitivity (D.5): primary.csv.",
    )

    fig, axes = plt.subplots(3, 4, figsize=(15, 10), squeeze=False)
    conditions = sorted({r["condition"] for r in tables["trajectories"]})
    palette = dict(zip(conditions, plt.get_cmap("tab10").colors, strict=False))
    for di, ds in enumerate(DATASETS):
        for mi, metric in enumerate(("ES", "RET-ES", "RET-GS", "LS")):
            ax = axes[di, mi]
            grouped = defaultdict(list)
            for row in tables["trajectories"]:
                if (
                    row["dataset"] == ds
                    and row["metric"] == metric
                    and row["status"] == "complete"
                    and row["value"] is not None
                ):
                    grouped[(row["condition"], row["checkpoint"])].append(row["value"])
            for condition in conditions:
                steps = sorted(k[1] for k in grouped if k[0] == condition)
                if steps:
                    ax.plot(
                        steps,
                        [
                            sum(grouped[(condition, n)]) / len(grouped[(condition, n)])
                            for n in steps
                        ],
                        marker="o",
                        markersize=3,
                        color=palette[condition],
                        label=condition,
                    )
            ax.set(
                title=f"{ds}: {metric}",
                xlabel="Attempted edits",
                ylabel="Descriptive mean",
                ylim=(-0.03, 1.03),
            )
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.023), ncol=5, fontsize=7)
    save(
        fig,
        "checkpoint-trajectories",
        "Observed checkpoint trajectories; both registered cadences",
        "Means of available cell values; no uncertainty or independence claim. See CSV for denominators, order/realization identity and missingness.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    for ax, reference in zip(axes, ("capoff", "original"), strict=True):
        for ds, color in zip(DATASETS, COLORS, strict=True):
            rows = [
                r
                for r in tables["fidelity"]
                if r["dataset"] == ds
                and r["reference"] == reference
                and r["mean_kl_nats"] is not None
            ]
            ax.scatter(
                [r["mean_kl_nats"] for r in rows],
                [r["mean_signed_nll_increase_nats"] for r in rows],
                s=18,
                alpha=0.45,
                color=color,
                label=f"{ds} (n={len(rows)})",
            )
        ax.axvline(0.001, color="gray", linestyle="--")
        ax.axhline(0.01, color="gray", linestyle=":")
        ax.set(
            title=reference,
            xlabel="Mean KL(reference || cap), nats",
            ylabel="Mean signed NLL increase, nats",
        )
        ax.legend(fontsize=8)
    save(
        fig,
        "cap-fidelity",
        "Full-validation cap-fidelity labels (DEC-064)",
        "Each point is one cell/reference; overplotting is possible. Missing values omitted, never plotted as zero. Threshold breaches do not veto admission.",
    )

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), squeeze=False)
    names = ("mean_signed", "ES95_positive", "ES99_positive", "maximum_positive")
    for ri, reference in enumerate(("capoff", "original")):
        for mi, metric in enumerate(("loss", "kl")):
            ax = axes[ri, mi]
            for di, (ds, color) in enumerate(zip(DATASETS, COLORS, strict=True)):
                rows = [
                    r
                    for r in tables["tails"]
                    if r["population"] == "full_validation"
                    and r["reference"] == reference
                    and r["metric"] == metric
                    and r["dataset"] == ds
                    and r["status"] == "complete"
                ]
                for ni, name in enumerate(names):
                    ys = [r[name] for r in rows if r[name] is not None]
                    ax.scatter(
                        [ni + (di - 1) * 0.16] * len(ys),
                        ys,
                        alpha=0.3,
                        s=10,
                        color=color,
                        label=ds if ni == 0 else None,
                    )
            ax.set(
                xticks=range(4),
                xticklabels=("mean signed", "ES95+", "ES99+", "max+"),
                title=f"{reference}: {metric}",
                ylabel="Nats (symlog)",
            )
            ax.set_yscale("symlog", linthresh=0.001)
            ax.legend(fontsize=8)
    save(
        fig,
        "full-validation-tails",
        "Full-validation cell tails; sample-based estimates remain separate",
        "Points are per-cell summaries, not pooled token distributions or independent replicates. Overplotting possible; exact counts/exceedances in tails.csv.",
    )

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    observations = tables.get("watch_observations", [])
    for ax, reference in zip(axes, ("capoff", "original"), strict=True):
        for owned, marker, label in (
            (True, "o", "this exact matrix"),
            (False, "x", "other journal scope"),
        ):
            xs, ys = [], []
            for i, row in enumerate(observations):
                if row["in_this_matrix"] == owned:
                    xs.append(i + 1)
                    ys.append(row["metrics"][reference]["mean_kl"])
            ax.scatter(xs, ys, marker=marker, s=12, label=label)
        ax.axhline(0.001, color="gray", linestyle="--")
        ax.set(
            title=reference,
            xlabel="Journal observation index (not elapsed time)",
            ylabel="Mean KL, nats",
        )
        if observations:
            ax.legend(fontsize=8)
        else:
            ax.text(
                0.5,
                0.5,
                "Watch unavailable / no supplied observations",
                ha="center",
                transform=ax.transAxes,
            )
    save(
        fig,
        "watch-sequence",
        "Fidelity-watch observation sequence",
        "Read-only snapshot; no alert delivery or acknowledgement. Entries/creep rules and global-versus-matrix membership: watch CSVs.",
    )
    if full.ref(path) != binding:
        raise ValueError("report data changed during plotting")
    manifest = dict(
        task="R1-D14",
        synthetic=data["synthetic"],
        report_data=binding,
        producer=full.ref(__file__),
        exports=exports,
        figures=len(data["figures"]),
        figure_sources=data["figures"],
    )
    with (out / "manifest.json").open("x") as f:
        json.dump(manifest, f, indent=2)
    return dict(figures=6, exports=len(exports), manifest=full.ref(out / "manifest.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    print(json.dumps(render(parser.parse_args().data), indent=2))
