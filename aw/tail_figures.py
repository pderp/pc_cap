"""HT-13: distributional harm figures from the saved full-validation vectors (read-only on results, CPU).

For every completed Stage-4 cell with a ``full-validation-*.npz`` (layout: loss_cap, loss_capoff, loss_original,
kl_capoff_to_cap, kl_original_to_cap per window position), pool the signed per-token loss change
``d = loss_cap - loss_capoff`` by condition × dataset and report the tail: survival P(d > x), exceedance at fixed
thresholds, maximum, ES99 of the positive part, and half-mass concentration (the smallest number of positions carrying
half of the total positive harm). Figures: survival curves (log–log) per dataset, and rarity-versus-severity
(fraction of positions with d > 0.01 nats against the maximum), one point per condition × dataset.

Usage (from the repo root, CPU):
    JAX_PLATFORMS=cpu ../venv/bin/python -m aw.tail_figures --out /home/derp/cap/assets/presentation-materials/figures/tails
"""
from __future__ import annotations

import argparse
import glob
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CELL_RE = re.compile(r"stage4_sealed_cells/([A-Za-z0-9_]+)-(zsre|counterfact|mquake)-(\d)-(\d+)-")
THRESHOLDS = (0.01, 0.1, 1.0, 2.0, 5.0)
LABEL = {
    "R1_learned_ff": "learned reader (v5)", "R1_nonlearned": "random reader", "v0_stable": "stable v0 cap",
    "v0_live_C1": "live v0 cap C1", "v0_live_C2": "live v0 cap C2", "matched_update": "matched update",
    "S1_LM": "continued base (LM) + stable cap", "S1_literal": "continued base (literal) + stable cap",
}


def collect(pattern: str) -> dict[tuple[str, str], list[np.ndarray]]:
    pooled: dict[tuple[str, str], list[np.ndarray]] = defaultdict(list)
    for f in sorted(glob.glob(pattern)):
        m = CELL_RE.search(f)
        if not m:
            continue
        cond, ds, _, _ = m.groups()
        v = np.load(f)["values"]
        pooled[(cond, ds)].append((v[:, :, 0] - v[:, :, 1]).ravel())
    return pooled


def statistics(d: np.ndarray) -> dict:
    pos = np.maximum(d, 0.0)
    s = np.sort(pos)[::-1]
    cs = np.cumsum(s)
    half = int(np.searchsorted(cs, 0.5 * cs[-1]) + 1) if cs[-1] > 0 else 0
    return {
        "positions": int(d.size),
        "changed_fraction": float((np.abs(d) > 1e-9).mean()),
        "mean_signed": float(d.mean()),
        "exceedance": {str(t): float((d > t).mean()) for t in THRESHOLDS},
        "max": float(d.max()),
        "es99_positive": float(np.quantile(pos, 0.99)),
        "half_mass_positions": half,
        "half_mass_fraction": float(half / d.size) if d.size else None,
    }


def survival(d: np.ndarray, grid: np.ndarray) -> np.ndarray:
    ds = np.sort(d)
    return 1.0 - np.searchsorted(ds, grid, side="right") / ds.size


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default=str(ROOT / "results/R1/stage4_sealed_cells/*/attempt-0000/full-validation-*.npz"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    pooled = collect(args.pattern)
    grid = np.logspace(-3, np.log10(60), 200)
    table = {}
    curves = {}
    for key, parts in sorted(pooled.items()):
        d = np.concatenate(parts)
        table[f"{key[0]}|{key[1]}"] = dict(condition=key[0], dataset=key[1], cells=len(parts), **statistics(d))
        curves[key] = survival(d, grid)
    (out / "tails.json").write_text(json.dumps(dict(thresholds=THRESHOLDS, grid=grid.tolist(), table=table), indent=1))

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # survival curves, one panel per dataset
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    for ax, ds in zip(axes, ("zsre", "counterfact", "mquake")):
        for key, c in sorted(curves.items()):
            if key[1] != ds or not np.any(c > 0):
                continue
            ax.loglog(grid, np.maximum(c, 1e-9), label=LABEL.get(key[0], key[0]), lw=1.4)
        ax.set_title(ds)
        ax.set_xlabel("token loss increase x (nats)")
        ax.set_ylim(1e-7, 1e-1)
        ax.grid(True, which="both", alpha=0.25)
        ax.legend(fontsize=6.5, loc="lower left")
    axes[0].set_ylabel("P(loss increase > x) over all validation positions")
    fig.suptitle("Ordinary-text harm is rare and heavy-tailed: survival of the per-token loss increase, all completed cells pooled")
    fig.tight_layout()
    fig.savefig(out / "survival_by_dataset.png", dpi=160)
    plt.close(fig)

    # rarity versus severity
    fig, ax = plt.subplots(figsize=(7.5, 5.0))
    markers = {"zsre": "o", "counterfact": "s", "mquake": "^"}
    conditions = sorted({r["condition"] for r in table.values()})
    colours = {c: plt.cm.tab10(i % 10) for i, c in enumerate(conditions)}
    seen_cond, seen_ds = set(), set()
    for k, row in table.items():
        x = row["exceedance"]["0.01"]
        if x <= 0:
            continue
        c, ds = row["condition"], row["dataset"]
        ax.scatter(x, row["max"], marker=markers[ds], s=70, color=colours[c], edgecolor="black", linewidth=0.5,
                   label=LABEL.get(c, c) if c not in seen_cond else None)
        seen_cond.add(c)
        seen_ds.add(ds)
    for ds in sorted(seen_ds):  # marker legend entries (shape = dataset)
        ax.scatter([], [], marker=markers[ds], color="white", edgecolor="black", s=70, label=f"dataset: {ds}")
    ax.legend(fontsize=6.5, loc="upper right", ncol=1, framealpha=0.9)
    ax.set_xscale("log")
    ax.set_xlabel("fraction of positions with loss increase > 0.01 nats (rarity)")
    ax.set_ylabel("maximum token loss increase (nats) (severity)")
    ax.set_title("Rarity versus severity of unintended harm, by condition")
    ax.grid(True, which="both", alpha=0.25)
    fig.tight_layout()
    fig.savefig(out / "rarity_vs_severity.png", dpi=160)
    plt.close(fig)

    # markdown table
    lines = ["| condition | dataset | cells | changed positions | P(>0.01) | P(>1) | P(>5) | max (nats) | ES99+ | half-mass positions |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for k, r in table.items():
        e = r["exceedance"]
        lines.append(f'| {LABEL.get(r["condition"], r["condition"])} | {r["dataset"]} | {r["cells"]} | {100*r["changed_fraction"]:.3f} % | '
                     f'{100*e["0.01"]:.4f} % | {100*e["1.0"]:.4f} % | {100*e["5.0"]:.4f} % | {r["max"]:.2f} | {r["es99_positive"]:.3f} | '
                     f'{r["half_mass_positions"]} of {r["positions"]} |')
    (out / "table.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: dict(cells=v["cells"], max=round(v["max"], 2), p001=v["exceedance"]["0.01"], half=v["half_mass_positions"]) for k, v in table.items()}, indent=0))


if __name__ == "__main__":
    main()
