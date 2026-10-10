"""Figures for the CAP-value supplement (three models in every panel: frozen GPT-2, BP-CAP, PC-CAP).

    JAX_PLATFORMS=cpu MPLCONFIGDIR=/tmp/ext-mpl python -m aw.extremes.cap_value_figures

Detailed figures -> assets/extremes_analysis/ext-20261009/figures/cap_value/*.png|svg
Slide package   -> assets/extremes_analysis/ext-20261009/figures/cap_value/slides/slide{1..5}_*.png|svg (16:9)
captions.json next to the figures. The frozen model is never dropped from a panel because its numbers are far worse.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from aw.extremes.common import DATA, MPL_SITE, OUT, Status, atomic_json

sys.path.append(str(MPL_SITE))
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

T = OUT / "tables" / "cap_value"
FIG = DATA / "figures" / "cap_value"
SL = FIG / "slides"
COL = {"frozen": "#444444", "bp_mean": "#1f77b4", "epc_mean": "#d62728", "bp": "#1f77b4", "epc": "#d62728"}
LABEL = {"frozen": "Frozen GPT-2 (no CAP)", "bp_mean": "BP-CAP", "epc_mean": "PC-CAP"}
DS_LABEL = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
THREE = ("frozen", "bp_mean", "epc_mean")
CAPTIONS = {}


def csv(name):
    p = T / f"{name}.csv"
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def save(fig, name, caption, slide=False):
    d = SL if slide else FIG
    d.mkdir(parents=True, exist_ok=True)
    fig.savefig(d / f"{name}.png", dpi=170, bbox_inches="tight")
    fig.savefig(d / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    CAPTIONS[("slides/" if slide else "") + name] = caption


def seeds_of(df, rule, h=300):
    return df[df["model"].isin([f"{rule}_reader_s{s}" for s in range(3)])]


# ------------------------------------------------------------------------------------------------ panel helpers
def panel_losses(ax, own, ds, fams=("edit", "paraphrase"), h=300, title=True, fontsize=9):
    """Grouped bars: mean per-token loss of the three models (CI whiskers), per-seed dots."""
    z = own[(own["dataset"] == ds) & (own["horizon"] == h)]
    width = 0.26
    xs = np.arange(len(fams))
    for i, m in enumerate(THREE):
        vals, lo, hi = [], [], []
        for fam in fams:
            r = z[(z["family"] == fam) & (z["model"] == m)]
            vals.append(float(r["mean"].iloc[0]) if len(r) else np.nan); lo.append(float(r["mean_ci_low"].iloc[0]) if len(r) else np.nan); hi.append(float(r["mean_ci_high"].iloc[0]) if len(r) else np.nan)
        vals, lo, hi = map(np.asarray, (vals, lo, hi))
        ax.bar(xs + (i - 1) * width, vals, width, color=COL[m], label=LABEL[m], yerr=[vals - lo, hi - vals], capsize=3, error_kw=dict(lw=0.8))
        if m != "frozen":
            rule = m[:-5]
            for fi, fam in enumerate(fams):
                pts = z[(z["family"] == fam) & z["model"].isin([f"{rule}_reader_s{s}" for s in range(3)])]["mean"]
                ax.plot(np.full(len(pts), xs[fi] + (i - 1) * width), pts, "o", color="white", mec="k", ms=3.5, mew=0.6, zorder=5)
    ax.set_xticks(xs); ax.set_xticklabels([{"edit": "taught prompt", "paraphrase": "paraphrase", "unseen": "un-taught prompt", "locality_item": "locality prompt"}.get(f, f) for f in fams], fontsize=fontsize)
    ax.set_ylabel("per-token NLL of the target (nats)", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    if title:
        n = {fam: int(z[(z["family"] == fam) & (z["model"] == "frozen")]["n"].iloc[0]) for fam in fams if len(z[(z["family"] == fam) & (z["model"] == "frozen")])}
        ax.set_title(f"{DS_LABEL[ds]} ({h} edits; n = " + ", ".join(f"{k} {v}" for k, v in n.items()) + ")", fontsize=fontsize + 1)


def panel_success(ax, basic, ds, metrics=("RET_ES", "RET_GS"), h=300, fontsize=9, title=True):
    z = basic[(basic["dataset"] == ds) & (basic["horizon"] == h)].set_index("model")
    width = 0.26
    xs = np.arange(len(metrics))
    for i, m in enumerate(THREE):
        vals = np.array([float(z.loc[m][k]) if (m in z.index and pd.notna(z.loc[m].get(k))) else np.nan for k in metrics]) * 100
        bars = ax.bar(xs + (i - 1) * width, vals, width, color=COL[m], label=LABEL[m])
        if m == "frozen":
            for b, k in zip(bars, metrics):
                flag = str(z.loc["frozen"].get(k + "_flag", "")) if "frozen" in z.index else ""
                ax.annotate("0 %\n(by screen)" if "screen" in flag else "0 %\n(measured)", (b.get_x() + b.get_width() / 2, 1), ha="center", va="bottom", fontsize=fontsize - 2, color="#333333")
        else:
            rule = m[:-5]
            for ki, k in enumerate(metrics):
                pts = [float(z.loc[f"{rule}_reader_s{s}"][k]) * 100 for s in range(3) if f"{rule}_reader_s{s}" in z.index and pd.notna(z.loc[f"{rule}_reader_s{s}"].get(k))]
                ax.plot(np.full(len(pts), xs[ki] + (i - 1) * width), pts, "o", color="white", mec="k", ms=3.5, mew=0.6, zorder=5)
    ax.set_ylim(0, 105); ax.set_xticks(xs); ax.set_xticklabels([{"RET_ES": "taught prompt\n(RET-ES)", "RET_GS": "paraphrase\n(RET-GS)", "ES": "immediate\n(ES)", "mh_question_accuracy": "multi-hop\nquestions"}.get(k, k) for k in metrics], fontsize=fontsize)
    ax.set_ylabel("exact-match success (%)", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    if title:
        den = z.loc["bp_mean"].get("RET_GS_den") if "bp_mean" in z.index else None
        ax.set_title(f"{DS_LABEL[ds]} ({h} edits; {int(den) if pd.notna(den) else '—'} items)", fontsize=fontsize + 1)


def panel_hard(ax, hard, ds, fam="paraphrase", h=300, fontsize=9, title=True):
    z = hard[(hard["dataset"] == ds) & (hard["family"] == fam) & (hard["horizon"] == h)]
    sets = ("hard5", "hard1")
    width = 0.26
    xs = np.arange(len(sets))
    for i, m in enumerate(THREE):
        vals, lo, hi = [], [], []
        for st in sets:
            r = z[(z["set"] == st) & (z["model"] == m)]
            vals.append(float(r["mean_loss"].iloc[0]) if len(r) else np.nan); lo.append(float(r["mean_loss_ci_low"].iloc[0]) if len(r) else np.nan); hi.append(float(r["mean_loss_ci_high"].iloc[0]) if len(r) else np.nan)
        vals, lo, hi = map(np.asarray, (vals, lo, hi))
        ax.bar(xs + (i - 1) * width, vals, width, color=COL[m], label=LABEL[m], yerr=[vals - lo, hi - vals], capsize=3, error_kw=dict(lw=0.8))
        if m != "frozen":
            for si, st in enumerate(sets):
                pts = z[(z["set"] == st) & z["model"].isin([f"{m[:-5]}_reader_s{s}" for s in range(3)])]["mean_loss"]
                ax.plot(np.full(len(pts), xs[si] + (i - 1) * width), pts, "o", color="white", mec="k", ms=3.5, mew=0.6, zorder=5)
    ks = {st: int(z[(z["set"] == st) & (z["model"] == "frozen")]["k"].iloc[0]) for st in sets if len(z[(z["set"] == st) & (z["model"] == "frozen")])}
    ax.set_xticks(xs); ax.set_xticklabels([f"frozen-hardest 5 %\n(k = {ks.get('hard5', '—')})", f"frozen-hardest 1 %\n(k = {ks.get('hard1', '—')})"], fontsize=fontsize)
    ax.set_ylabel("mean per-token NLL on the fixed set (nats)", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    if title:
        ax.set_title(f"{DS_LABEL[ds]} {fam} prompts ({h} edits)", fontsize=fontsize + 1)


def panel_own(ax, own, ds, fam="paraphrase", h=300, fontsize=9, title=True):
    z = own[(own["dataset"] == ds) & (own["family"] == fam) & (own["horizon"] == h)]
    stats = (("cvar95", "own worst 5 %\n(CVaR95)"), ("cvar99", "own worst 1 %\n(CVaR99)"))
    width = 0.26
    xs = np.arange(len(stats))
    for i, m in enumerate(THREE):
        r = z[z["model"] == m]
        if r.empty:
            continue
        vals = np.array([float(r[s].iloc[0]) for s, _ in stats]); lo = np.array([float(r[s + "_ci_low"].iloc[0]) for s, _ in stats]); hi = np.array([float(r[s + "_ci_high"].iloc[0]) for s, _ in stats])
        ax.bar(xs + (i - 1) * width, vals, width, color=COL[m], label=LABEL[m], yerr=[vals - lo, hi - vals], capsize=3, error_kw=dict(lw=0.8))
        if m != "frozen":
            for si, (s, _) in enumerate(stats):
                pts = z[z["model"].isin([f"{m[:-5]}_reader_s{k}" for k in range(3)])][s]
                ax.plot(np.full(len(pts), xs[si] + (i - 1) * width), pts, "o", color="white", mec="k", ms=3.5, mew=0.6, zorder=5)
    ax.set_xticks(xs); ax.set_xticklabels([t for _, t in stats], fontsize=fontsize); ax.set_ylabel("mean of each model's own worst cases (nats/token)", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    if title:
        n = int(z[z["model"] == "frozen"]["n"].iloc[0]) if len(z[z["model"] == "frozen"]) else 0
        ax.set_title(f"{DS_LABEL[ds]} {fam} prompts ({h} edits; n = {n})", fontsize=fontsize + 1)


def panel_deciles(ax, dec, ds, fam="paraphrase", h=300, fontsize=9, title=True, ymax=None):
    z = dec[(dec["dataset"] == ds) & (dec["family"] == fam) & (dec["horizon"] == h)]
    for m in THREE:
        r = z[z["model"] == m].sort_values("decile")
        if r.empty:
            continue
        ax.plot(r["decile"], r["mean_loss"], "-o", color=COL[m], label=LABEL[m], ms=4)
        ax.fill_between(r["decile"], r["ci_low"], r["ci_high"], color=COL[m], alpha=0.18, lw=0)
    for rule in ("bp", "epc"):
        for s in range(3):
            r = z[z["model"] == f"{rule}_reader_s{s}"].sort_values("decile")
            if len(r):
                ax.plot(r["decile"], r["mean_loss"], "-", color=COL[rule], alpha=0.35, lw=0.7)
    ax.set_xticks(range(1, 11)); ax.set_xlabel("frozen-difficulty decile (1 = easiest for frozen GPT-2)", fontsize=fontsize); ax.set_ylabel("mean per-token NLL (nats)", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    if ymax is not None:
        ax.set_ylim(-0.3, ymax)
    if title:
        n = int(z[z["model"] == "frozen"]["n"].sum()) if len(z) else 0
        ax.set_title(f"{DS_LABEL[ds]} {fam} prompts ({h} edits; n = {n})", fontsize=fontsize + 1)


def panel_survival(ax, curves, tails, ds, fontsize=9, title=True):
    z = curves[curves["dataset"] == ds]
    if z.empty:
        return
    for _, r in z.iterrows():
        g = np.asarray(json.loads(r["grid"])); sv = np.asarray(json.loads(r["survival"]))
        m = r["model"]
        if m == "frozen":
            ax.loglog(g, np.maximum(sv, 1e-6), color=COL["frozen"], lw=2.2, label=f"frozen (n = {int(r['n_tokens']):,} tokens)")
        elif m.endswith("_pooled_seeds"):
            continue
        else:
            rule = "bp" if m.startswith("bp") else "epc"
            ax.loglog(g, np.maximum(sv, 1e-6), color=COL[rule], lw=0.9, alpha=0.8, label=(LABEL[rule + "_mean"] + " (3 seeds)") if m.endswith("s0") else None)
    tz = tails[(tails["dataset"] == ds) & (tails["model"] == "frozen")]
    for _, r in tz.iterrows():
        if r["threshold_name"].startswith("frozen P95") or r["threshold_name"] in ("8 nats",):
            ax.axvline(r["threshold"], color="gray", ls=":", lw=0.8)
            ax.annotate(r["threshold_name"], (r["threshold"], 0.6), fontsize=fontsize - 2, rotation=90, va="top", ha="right", color="gray")
    ax.set_xlabel("per-token target NLL threshold u (nats)", fontsize=fontsize); ax.set_ylabel("fraction of target tokens with NLL > u", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    ax.set_ylim(1e-4, 1.05)
    if title:
        ax.set_title(f"{DS_LABEL[ds]}: token-loss survival (300 edits)", fontsize=fontsize + 1)


def panel_collateral(ax, coll, ds, h=300, fontsize=9, title=True):
    fams = ("locality_item", "locality", "near_miss_neighbour", "unseen")
    labels = {"locality_item": "item\nlocality", "locality": "sealed\nlocality (50)", "near_miss_neighbour": "near-miss\nneighbour", "unseen": "un-taught\nprompt"}
    z = coll[(coll["dataset"] == ds) & (coll["horizon"] == h)]
    xs = np.arange(len(fams)); width = 0.38
    for i, m in enumerate(("bp_mean", "epc_mean")):
        worse, wlo, whi, better, sev = [], [], [], [], []
        for fam in fams:
            r = z[(z["family"] == fam) & (z["model"] == m)]
            worse.append(100 * float(r["frac_worse"].iloc[0]) if len(r) else np.nan); wlo.append(100 * float(r["frac_worse_ci_low"].iloc[0]) if len(r) else np.nan); whi.append(100 * float(r["frac_worse_ci_high"].iloc[0]) if len(r) else np.nan)
            better.append(100 * float(r["frac_better"].iloc[0]) if len(r) else np.nan)
            sev.append(int(z[(z["family"] == fam) & z["model"].isin([f"{m[:-5]}_reader_s{s}" for s in range(3)])]["n_D_gt_2"].sum()) if len(r) else 0)
        worse, wlo, whi, better = map(np.asarray, (worse, wlo, whi, better))
        ax.bar(xs + (i - 0.5) * width, worse, width, color=COL[m], label=f"{LABEL[m]}: worse than frozen", yerr=[worse - wlo, whi - worse], capsize=3, error_kw=dict(lw=0.8))
        ax.bar(xs + (i - 0.5) * width, -better, width, color=COL[m], alpha=0.45, label=f"{LABEL[m]}: better than frozen")
        for xi, (w, hi_, s) in enumerate(zip(worse, whi, sev)):
            if s > 0:
                ax.annotate(f"{s} > 2 nats", (xs[xi] + (i - 0.5) * width, (hi_ if np.isfinite(hi_) else 0) + 0.3), xytext=(0, 9 * i), textcoords="offset points", ha="center", va="bottom", fontsize=fontsize - 3, color=COL[m])
    ax.axhline(0, color="k", lw=0.6)
    ax.set_xticks(xs); ax.set_xticklabels([labels[f] for f in fams], fontsize=fontsize - 2); ax.set_ylabel("% of probes changed vs frozen\n(+ worse / − better)", fontsize=fontsize - 1); ax.tick_params(labelsize=fontsize - 1)
    ax.margins(y=0.25)
    if title:
        ax.set_title(f"{DS_LABEL[ds]}: change vs frozen ({h} edits)", fontsize=fontsize + 1)


def panel_mquake(ax, basic, fontsize=9):
    z = basic[(basic["dataset"] == "mquake") & (basic["horizon"] == 300)].set_index("model")
    keys = ("RET_GS", "mh_question_accuracy", "mh_all_case")
    names = ("single-hop paraphrase\n(RET-GS, 300 items)", "multi-hop question\naccuracy (240)", "all 3 multi-hop\nquestions (80 cases)")
    xs = np.arange(len(keys)); width = 0.26
    for i, m in enumerate(THREE):
        vals = []
        for k in keys:
            v = z.loc[m].get(k) if m in z.index else np.nan
            vals.append(100 * float(v) if pd.notna(v) else np.nan)
        vals = np.asarray(vals)
        bars = ax.bar(xs + (i - 1) * width, np.nan_to_num(vals), width, color=COL[m], label=LABEL[m])
        for b, v, k in zip(bars, vals, keys):
            if not np.isfinite(v):
                ax.annotate("not\nrecorded", (b.get_x() + b.get_width() / 2, 1), ha="center", va="bottom", fontsize=fontsize - 3, color="#333333")
            elif v < 3:
                ax.annotate(f"{v:.1f} %", (b.get_x() + b.get_width() / 2, 1), ha="center", va="bottom", fontsize=fontsize - 2, color="#333333")
        if m != "frozen":
            for ki, k in enumerate(keys):
                pts = [100 * float(z.loc[f"{m[:-5]}_reader_s{s}"][k]) for s in range(3) if f"{m[:-5]}_reader_s{s}" in z.index and pd.notna(z.loc[f"{m[:-5]}_reader_s{s}"].get(k))]
                ax.plot(np.full(len(pts), xs[ki] + (i - 1) * width), pts, "o", color="white", mec="k", ms=3.5, mew=0.6, zorder=5)
    ax.set_ylim(0, 105); ax.set_xticks(xs); ax.set_xticklabels(names, fontsize=fontsize - 1); ax.set_ylabel("%", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    ax.set_title("MQuAKE, 300 edits: single-hop retention vs multi-hop composition", fontsize=fontsize + 1)


def panel_pc_vs_bp(ax, gains, fontsize=9):
    """Seed-mean paired contrast ePC − BP (positive favours PC) with the two caps' gains over frozen for scale."""
    rows = []
    for ds in ("zsre", "counterfact", "mquake"):
        for fam in ("edit", "paraphrase"):
            z = gains[(gains["dataset"] == ds) & (gains["family"] == fam) & (gains["target"] == "new") & (gains["horizon"] == 300) & (gains["seed"].astype(str) == "mean")]
            if z.empty:
                continue
            d = {g: (float(r["mean"]), json.loads(r["mean_ci"]) if isinstance(r["mean_ci"], str) else r["mean_ci"]) for g, r in zip(z["gain"], z.to_dict("records"))}
            rows.append((f"{DS_LABEL[ds]}\n{fam}", d))
    xs = np.arange(len(rows)); width = 0.26
    for i, (g, color, lab) in enumerate((("G_BP", COL["bp"], "BP-CAP gain over frozen"), ("G_PC", COL["epc"], "PC-CAP gain over frozen"), ("G_PCvsBP", "#777777", "PC-CAP − BP-CAP (positive favours PC)"))):
        v = np.array([d[g][0] if g in d else np.nan for _, d in rows]); lo = np.array([d[g][1][0] if g in d else np.nan for _, d in rows]); hi = np.array([d[g][1][1] if g in d else np.nan for _, d in rows])
        ax.bar(xs + (i - 1) * width, v, width, color=color, label=lab, yerr=[v - lo, hi - v], capsize=3, error_kw=dict(lw=0.8))
    ax.axhline(0, color="k", lw=0.6); ax.set_xticks(xs); ax.set_xticklabels([r[0] for r in rows], fontsize=fontsize - 1); ax.set_ylabel("per-token NLL reduction (nats), seed mean", fontsize=fontsize); ax.tick_params(labelsize=fontsize)
    ax.set_title("Question B inside question A: PC vs BP is a small contrast within a large CAP gain (300 edits; 2,000 item-bootstrap draws)", fontsize=fontsize)


# ------------------------------------------------------------------------------------------------ detailed figures
def detailed(basic, own, hard, dec, tails, curves, coll, gains):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, ds in zip(axes, DS_LABEL):
        panel_losses(ax, own, ds)
    axes[0].legend(fontsize=8)
    save(fig, "adaptation_losses", "Ordinary adaptation: mean teacher-forced per-token NLL of the taught answer on the taught prompt and on its paraphrases for frozen GPT-2 (no CAP), BP-CAP and PC-CAP (seed means; white dots = the three training seeds) at the 300-edit memory; 95 % item-bootstrap intervals (2,000 draws). Shared y-axis.")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for ax, ds in zip(axes, DS_LABEL):
        panel_success(ax, basic, ds)
    axes[0].legend(fontsize=8, loc="center left")
    save(fig, "adaptation_success", "Ordinary adaptation: exact-match success on the taught prompt (RET-ES) and on paraphrases (RET-GS) at 300 edits. Frozen GPT-2 is 0 % by construction on taught prompts (the eligibility screen kept only items the base did not answer) and a measured 0 % on paraphrases; the frozen bars are kept at zero and labelled rather than omitted.")
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5), sharey="row")
    for j, ds in enumerate(DS_LABEL):
        panel_hard(axes[0, j], hard, ds, "paraphrase"); panel_hard(axes[1, j], hard, ds, "edit")
    axes[0, 0].legend(fontsize=8)
    save(fig, "frozen_hardest", "Comparison B: the same frozen-defined hardest 5 % and 1 % of paraphrase (top) and taught (bottom) prompts, scored by all three models; bars = mean per-token NLL on the fixed set, whiskers = 95 % bootstrap over the items in the set, dots = seeds. Shared y-axis per row.")
    fig, axes = plt.subplots(2, 3, figsize=(14, 7.5), sharey="row")
    for j, ds in enumerate(DS_LABEL):
        panel_own(axes[0, j], own, ds, "paraphrase"); panel_own(axes[1, j], own, ds, "edit")
    axes[0, 0].legend(fontsize=8)
    save(fig, "own_worst", "Comparison A: each model's own worst 5 % (CVaR95) and worst 1 % (CVaR99) of per-token NLL on paraphrase (top) and taught (bottom) prompts at 300 edits; 95 % item-bootstrap intervals; dots = seeds. The sets differ between models by construction.")
    ymax = {}
    for fam in ("paraphrase", "edit", "unseen", "locality_item"):
        z = dec[(dec["family"] == fam) & (dec["horizon"] == 300)]
        ymax[fam] = float(z["ci_high"].max()) * 1.05 if len(z) else None
    for fam in ("paraphrase", "edit", "unseen", "locality_item"):
        fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
        for ax, ds in zip(axes, DS_LABEL):
            panel_deciles(ax, dec, ds, fam, ymax=ymax[fam])
        axes[0].legend(fontsize=8)
        save(fig, f"deciles_{fam}", f"Actual per-token NLL (not gains) of frozen GPT-2, BP-CAP and PC-CAP across frozen-difficulty deciles of {fam} prompts at 300 edits; deciles are fixed by the frozen loss; bands = 95 % item-group bootstrap (500 draws) of the seed-mean; thin lines = individual seeds. Comparable y-axes across datasets.")
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    for ax, ds in zip(axes, DS_LABEL):
        panel_survival(ax, curves, tails, ds)
    axes[0].legend(fontsize=7)
    save(fig, "token_survival", "Tail comparison at common absolute thresholds: survival functions of the token-level target NLL (terminator excluded) pooled over edit/paraphrase/unseen (new target) and locality/near-miss (true target) probes at 300 edits, frozen GPT-2 vs each seed of BP-CAP and PC-CAP. Dotted lines mark the frozen P95 and 8 nats. Curves are descriptive; shapes are fitted only where exceedances ≥ 100 (table).")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    for ax, ds in zip(axes, DS_LABEL):
        panel_collateral(ax, coll, ds)
    axes[0].legend(fontsize=7, loc="lower left")
    save(fig, "collateral_vs_frozen", "Collateral change vs frozen GPT-2 on prompts the cap should leave alone: percentage of probes with per-token NLL worse (+) or better (−) than frozen by more than 1e-3 nats, with 95 % bootstrap intervals (seed means), and the number of severe deteriorations above 2 nats/token summed over the three seeds. Unchanged probes are bit-identical to frozen.")
    fig, ax = plt.subplots(figsize=(8, 4.2))
    panel_mquake(ax, basic); ax.legend(fontsize=8)
    save(fig, "mquake_multihop", "MQuAKE at 300 edits: single-hop paraphrase retention versus the registered multi-hop composition endpoint (80 cases × 3 questions) for frozen GPT-2 (cap-off exact match: 0 of 240), BP-CAP and PC-CAP. Neither cap composes edited facts; case-level any/all success for the frozen path is not separately recorded.")
    fig, ax = plt.subplots(figsize=(12, 4.2))
    panel_pc_vs_bp(ax, gains); ax.legend(fontsize=8)
    save(fig, "pc_vs_bp_within_gain", "Question B inside question A: seed-mean per-token NLL reduction over frozen for BP-CAP and PC-CAP, and their paired contrast (PC − BP; positive favours PC), by dataset and prompt family at 300 edits; 95 % item-bootstrap intervals (2,000 draws).")


# ------------------------------------------------------------------------------------------------ slide package
def slides(basic, own, hard, dec, tails, curves, coll, gains):
    fs = 10
    # slide 1: value of CAP in ordinary adaptation
    fig, axes = plt.subplots(2, 3, figsize=(13.33, 7.5), sharey="row")
    for j, ds in enumerate(DS_LABEL):
        panel_losses(axes[0, j], own, ds, fontsize=fs); panel_success(axes[1, j], basic, ds, fontsize=fs)
    axes[0, 0].legend(fontsize=fs - 1); fig.suptitle("A. Adding a CAP to frozen GPT-2 small: taught facts and their paraphrases (300 edits, realization 0)", fontsize=fs + 3)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "slide1_cap_value_ordinary", "Slide 1 — value of a CAP in ordinary adaptation: per-token loss (top) and exact-match success (bottom) for frozen GPT-2, BP-CAP and PC-CAP on taught prompts and paraphrases; three datasets; seed means with per-seed dots and 95 % intervals.", slide=True)
    # slide 2: frozen hardest examples
    fig, axes = plt.subplots(2, 3, figsize=(13.33, 7.5), sharey="row")
    ymax = float(dec[(dec["family"] == "paraphrase") & (dec["horizon"] == 300)]["ci_high"].max()) * 1.05
    for j, ds in enumerate(DS_LABEL):
        panel_hard(axes[0, j], hard, ds, "paraphrase", fontsize=fs); panel_deciles(axes[1, j], dec, ds, "paraphrase", fontsize=fs, ymax=ymax)
    axes[0, 0].legend(fontsize=fs - 1); fig.suptitle("A. CAP vs frozen GPT-2 on the frozen model's hardest paraphrases: fixed hardest 5 % / 1 % (top) and actual loss by frozen-difficulty decile (bottom)", fontsize=fs + 2)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "slide2_frozen_hardest", "Slide 2 — the same frozen-defined hardest examples scored by all three models, and the actual loss of each model across frozen-difficulty deciles (paraphrases, 300 edits).", slide=True)
    # slide 3: own worst errors + survival at common thresholds
    fig, axes = plt.subplots(2, 3, figsize=(13.33, 7.5))
    for j, ds in enumerate(DS_LABEL):
        panel_own(axes[0, j], own, ds, "paraphrase", fontsize=fs); panel_survival(axes[1, j], curves, tails, ds, fontsize=fs)
    for ax in axes[0, 1:]:
        ax.sharey(axes[0, 0])
    axes[0, 0].legend(fontsize=fs - 1); axes[1, 0].legend(fontsize=fs - 2)
    fig.suptitle("A. Each model's own worst errors (top) and the token-loss tail at common absolute thresholds (bottom), 300 edits", fontsize=fs + 3)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "slide3_own_worst_and_tails", "Slide 3 — each model's own worst 5 % / 1 % of paraphrase losses (CVaR, with intervals) and the survival of token-level target loss for frozen GPT-2 and each cap seed at common thresholds.", slide=True)
    # slide 4: locality / interference and limitations
    fig = plt.figure(figsize=(13.33, 7.5))
    gs = fig.add_gridspec(2, 3, height_ratios=(1.15, 1))
    for j, ds in enumerate(DS_LABEL):
        panel_collateral(fig.add_subplot(gs[0, j]), coll, ds, fontsize=fs)
    ax = fig.add_subplot(gs[1, 0:2]); panel_mquake(ax, basic, fontsize=fs); ax.legend(fontsize=fs - 2)
    ax = fig.add_subplot(gs[1, 2]); ax.axis("off")
    # residual extreme losses when gating fails (paraphrases)
    gate = csv("gating_failures")
    txt = ["Remaining limitations (300 edits):"]
    for ds in DS_LABEL:
        z = gate[(gate["dataset"] == ds) & (gate["family"] == "paraphrase") & (gate["horizon"] == 300)]
        if z.empty:
            continue
        for rule, lab in (("bp", "BP-CAP"), ("epc", "PC-CAP")):
            r = z[z["model"].str.startswith(rule)]
            txt.append(f"{DS_LABEL[ds]} {lab}: abstains on {100 * r['abstain_rate'].mean():.1f} % of paraphrases (seed mean);\n   those keep the frozen loss (mean {r['loss_abstained_mean'].mean():.1f} nats/token);\n   {int(r['frozen_hard5_abstained'].sum())}/{int(r['frozen_hard5_n'].sum())} frozen-hardest-5 % cases abstained (3 seeds)")
    txt.append("MQuAKE multi-hop composition: no cap answers\nall three questions of any case (0/80, every seed).")
    ax.text(0, 1, "\n".join(txt), va="top", ha="left", fontsize=fs - 2, family="monospace", transform=ax.transAxes)
    fig.suptitle("A. The locality / interference trade-off and what the CAP does not fix", fontsize=fs + 3)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "slide4_locality_and_limits", "Slide 4 — collateral change vs frozen GPT-2 on locality-type prompts (with severe events), MQuAKE multi-hop composition (a negative result for both caps) and the residual losses where the reader abstains.", slide=True)
    # slide 5: PC vs BP secondary
    fig, axes = plt.subplots(2, 1, figsize=(13.33, 7.5), height_ratios=(1.2, 1))
    panel_pc_vs_bp(axes[0], gains, fontsize=fs); axes[0].legend(fontsize=fs - 1)
    # RET-GS per seed, both rules, and frozen
    z = basic[basic["horizon"] == 300]
    xs = np.arange(3); width = 0.12
    for i, (m, lab) in enumerate((("frozen", "Frozen GPT-2"), *[(f"bp_reader_s{s}", f"BP-CAP s{s}") for s in range(3)], *[(f"epc_reader_s{s}", f"PC-CAP s{s}") for s in range(3)])):
        vals = [100 * float(z[(z["dataset"] == ds) & (z["model"] == m)]["RET_GS"].iloc[0]) for ds in DS_LABEL]
        axes[1].bar(xs + (i - 3) * width, vals, width, color=COL["frozen"] if m == "frozen" else COL["bp"] if m.startswith("bp") else COL["epc"], alpha=1.0 if m == "frozen" else 0.5 + 0.25 * int(m[-1]), label=lab)
    axes[1].set_xticks(xs); axes[1].set_xticklabels([DS_LABEL[d] for d in DS_LABEL], fontsize=fs); axes[1].set_ylabel("paraphrase retention RET-GS (%)", fontsize=fs); axes[1].set_ylim(0, 105); axes[1].legend(fontsize=fs - 3, ncol=7)
    axes[1].set_title("B. Paraphrase retention per training seed (frozen = 0 % measured)", fontsize=fs + 1)
    fig.suptitle("B. Given that a CAP helps, does PC training beat BP training? (secondary comparison)", fontsize=fs + 3)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    save(fig, "slide5_pc_vs_bp", "Slide 5 — PC vs BP as a secondary comparison within the CAP benefit: seed-mean gains over frozen and the paired PC − BP contrast with intervals (top); paraphrase retention per seed with the frozen baseline (bottom).", slide=True)


def main():
    basic, own, hard, dec, tails, coll = csv("basic_performance"), csv("extremes_own_worst"), csv("extremes_frozen_hardest"), csv("deciles_actual_loss"), csv("token_tails_common_thresholds"), csv("collateral_vs_frozen")
    curves = pd.read_parquet(DATA / "data" / "cap_value" / "survival_curves.parquet")
    gains = pd.read_csv(OUT / "tables" / "paired_gains.csv")
    for fn in (detailed, slides):
        try:
            fn(basic, own, hard, dec, tails, curves, coll, gains)
        except Exception as e:
            CAPTIONS[fn.__name__] = f"FAILED: {e!r}"
            raise
    atomic_json(FIG / "captions.json", CAPTIONS)
    Status().stage("9_cap_value_figures", "updated", figures=sorted(k for k, v in CAPTIONS.items() if not str(v).startswith("FAILED")))
    print(json.dumps(sorted(CAPTIONS)))


if __name__ == "__main__":
    main()
