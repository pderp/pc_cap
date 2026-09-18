"""Render existing audited development summaries; no models, JAX or new assays."""

import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT.parent / "assets/cache/matplotlib-ht9"))
FRAMING = "Preliminary hints; not coupled free energy, a coupled Markov blanket, or a test of the one-κ conjecture."


def read(path):
    raw = path.read_bytes()
    return json.loads(raw), dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest())


def figure_data():
    review, rb = read(ROOT / "logs/r1_round22/ht3e-independent-review-v2.json")
    full, fb = read(ROOT / "logs/r1_round35/ht6-final/report.json")
    arms = ["ordinary", "kappa02", "kappa05", "clip2"]
    pilot = []
    for arm in arms:
        for seed in range(3):
            rows = [r for r in review["pilot"]["rows"] if r["arm"] == arm and r["seed"] == seed]
            if len(rows) != 3 or {r["dataset"] for r in rows} != {"zsre", "counterfact", "mquake"}:
                raise ValueError("complete three-dataset seed required")
            pilot.append(dict(arm=arm, seed=seed,
                              ret_gs=math.fsum(r["ret_gs"] for r in rows) / 3,
                              es95=math.fsum(r["es95"] for r in rows) / 3))
    stress = []
    for dataset, row in review["stress"].items():
        for schedule, values in row["schedules"].items():
            for step, point in sorted(values["points"].items(), key=lambda kv: int(kv[0])):
                stress.append(dict(dataset=dataset, schedule=schedule, edit=int(step),
                                   mean_positive=point["mean_positive"], exact=point["exact"],
                                   max_positive=point["max_positive"]))
    if full["completed"] != full["expected"] or full["completed"] != 4:
        raise ValueError("final four-cell HT-6 report required")
    concentration = []
    for row in full["cells"].values():
        metrics = row["full"]["references"]["original"]
        concentration.append(dict(
            cell=row["cell"], n=row["concentration"]["full"]["positions"],
            kl=row["cap_fidelity_benchmark"]["references"]["original"]["mean_kl_nats"],
            loss=metrics["loss"],
            half_kl_count=row["concentration"]["full"]["references"]["original"]["kl_positions"]["minimum_count_for_half_mass"],
        ))
    return dict(sources=[rb, fb], pilot=pilot, stress=stress, full=concentration,
                retention_floor=review["pilot"]["comparisons"]["kappa02"]["retention_floor"],
                framing=FRAMING, scope="development", model_calls=0)


def render(output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    data = figure_data()
    output = output.resolve()
    if not output.is_relative_to(ROOT / "logs"):
        raise ValueError("new directory under repository logs required")
    output.mkdir(parents=True, exist_ok=False)
    (output / "figure-data.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")

    def save(fig, name, footer):
        fig.text(0.5, 0.015, footer, ha="center", fontsize=9)
        fig.tight_layout(rect=(0, 0.10, 1, 0.95))
        for suffix in ("pdf", "svg", "png"):
            fig.savefig(output / f"{name}.{suffix}", dpi=180)
        plt.close(fig)

    colors = ["#34699a", "#cd6b25", "#7b4e9b", "#43856b"]
    arms = ["ordinary", "kappa02", "kappa05", "clip2"]
    names = ["Ordinary", "κ = 0.2", "κ = 0.5", "Clip 2"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.5))
    for ax, metric, label in zip(axes, ["ret_gs", "es95"],
                                ["Paraphrase retention (RET-GS)", "ES95 positive NLL harm (nats)"], strict=True):
        for x, arm, color in zip(range(4), arms, colors, strict=True):
            vals = [r[metric] for r in data["pilot"] if r["arm"] == arm]
            ax.scatter([x - .09, x, x + .09], vals, color=color, s=32)
            ax.plot([x-.2, x+.2], [math.fsum(vals)/3]*2, color=color, lw=3)
        ax.set_xticks(range(4), names)
        ax.set_ylabel(label)
        ax.grid(axis="y", alpha=.2)
    axes[0].axhline(data["retention_floor"], color="black", ls="--", lw=1, label="Predeclared floor")
    axes[0].legend(fontsize=9)
    fig.suptitle("Loss-level κ pilot: neither κ arm meets the retention + tail rule")
    save(fig, "kappa-tradeoff", "Points: three seed means across three datasets; bars: means, not confidence intervals.\n" + FRAMING)

    fig, axes = plt.subplots(1, 3, figsize=(12, 5))
    for ax, dataset in zip(axes, ["zsre", "counterfact", "mquake"], strict=True):
        for schedule, marker, style in [("shuffled", "o", "-"), ("clustered", "x", "--")]:
            rows = [r for r in data["stress"] if r["dataset"] == dataset and r["schedule"] == schedule]
            ax.plot([r["edit"] for r in rows], [r["mean_positive"] for r in rows],
                    marker=marker, ls=style, label=schedule)
        ax.axvline(60, color="gray", lw=1, ls=":")
        ax.set_title(dataset + " · exact old answers 20/20")
        ax.set_xlabel("Attempted edits (lines connect observations)")
        ax.set_ylabel("Mean positive ΔNLL vs edit 20 (nats)")
        ax.set_ylim(-.025, .38)
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    fig.suptitle("Old-fact probability harm persisted through the observation window")
    save(fig, "stress-trajectories", "Development: one seed, two tested schedules; overlapping curves are observed equality.\nCounterFact: 20 updates observed after first detected harm; MQuAKE: 40. Recovery beyond edit 100 is unknown.")

    fig, axes = plt.subplots(1, 2, figsize=(11, 5.8))
    for x, row in enumerate(data["full"]):
        label = row["cell"]["dataset"] + "\n" + ("primary v5" if row["cell"]["condition"] == "R1_learned_ff" else "v0 stable")
        axes[0].bar(x, row["kl"], color=colors[x])
        half = "undefined\n(total KL = 0)" if row["half_kl_count"] is None else str(row["half_kl_count"])
        axes[0].annotate("½ KL: " + half, (x, row["kl"]), xytext=(0, 16), textcoords="offset points", ha="center", fontsize=8)
        axes[1].scatter(x-.08, row["loss"]["ES95_positive"], color=colors[x], marker="o")
        axes[1].scatter(x+.08, row["loss"]["maximum_positive"], color=colors[x], marker="^")
        axes[0].set_xticks(range(len(data["full"])), [
            r["cell"]["dataset"] + "\n" + ("primary v5" if r["cell"]["condition"] == "R1_learned_ff" else "v0 stable") for r in data["full"]])
        axes[1].text(x, -.65, label, ha="center", fontsize=9, va="top")
    axes[0].axhline(.001, color="black", ls="--", label="Mean-KL benchmark 0.001")
    axes[0].set_ylabel("Mean KL(original base ‖ cap), nats")
    axes[0].set_ylim(0, max(r["kl"] for r in data["full"]) * 1.25)
    axes[0].legend(fontsize=8)
    axes[1].scatter([], [], color="black", marker="o", label="ES95 positive harm")
    axes[1].scatter([], [], color="black", marker="^", label="Maximum positive harm")
    axes[1].set_ylabel("Positive target-token NLL increase, nats")
    axes[1].set_xticks([])
    axes[1].set_ylim(-.5, 18)
    axes[1].legend(fontsize=8)
    fig.suptitle("Full validation: mean fidelity and rare harm answer different questions")
    save(fig, "full-fidelity-and-tail", "Development, 300 edits; 245,237 positions per cell, original-base reference.\n½ KL = positions carrying half the total KL; DEC-064 benchmarks are secondary, not admission vetoes.")
    (output / "rendering.json").write_text(json.dumps(dict(
        python=sys.executable, matplotlib=matplotlib.__version__,
        producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        sources=data["sources"], model_calls=0), indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    render(parser.parse_args().output)
