"""Render precomputed empirical curves in the existing plotting environment; no JAX."""

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT.parent / "assets/cache/matplotlib-ht6"))


def render(source, output):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    value = json.loads(source.read_text())
    targets = [output / ("tail-survival." + suffix) for suffix in ("png", "pdf")]
    if any(p.exists() for p in targets):
        raise FileExistsError("new plot outputs required")
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for ax, panel in zip(axes.flat, value["panels"], strict=True):
        ax.set_title(panel["title"], fontsize=10)
        if not panel["series"]:
            ax.text(
                0.5, 0.5, "Measurement pending", ha="center", va="center", transform=ax.transAxes
            )
            ax.set_axis_off()
            continue
        ax.set_yscale("log")
        ax.set_ylim(0.5 / max(s["n"] for s in panel["series"]), 1.05)
        positive = False
        for series in panel["series"]:
            label = f"{series['name']} (N={series['n']:,})"
            if not any(y > 0 for y in series["y"]):
                ax.plot([], [], label=label + "; no positive harm")
                continue
            positive = True
            ax.step(
                series["x"],
                series["y"],
                where="post",
                label=label,
            )
        ax.set_xlim(left=0)
        if not positive:
            ax.set_xlim(0, 1)
            ax.text(
                0.5,
                0.5,
                "No positive NLL harm observed\nSurvival = 0 for every x ≥ 0",
                ha="center",
                va="center",
                transform=ax.transAxes,
            )
        ax.set_xlabel("Positive NLL increase (nats)")
        ax.set_ylabel("Fraction strictly above x")
        ax.grid(alpha=0.2)
        ax.legend(fontsize=8)
    fig.suptitle(
        f"Development ordinary-text tails — {value['completed']}/4 cells; no power-law fit"
    )
    for target in targets:
        fig.savefig(target, dpi=160)
    plt.close(fig)
    with (output / "plot-environment.json").open("x") as f:
        json.dump(
            dict(
                python=sys.executable,
                matplotlib=matplotlib.__version__,
                input=str(source),
                model_calls=0,
            ),
            f,
            indent=2,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        parser.error("repository log directory required")
    render(args.input, args.output)
