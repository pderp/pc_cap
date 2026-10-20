"""Phase 0 figures (CPU): frontier curves, failure atlas, oracle rescue, in-context comparison, locality corrigendum,
composition ceiling. PNG + SVG under assets/post_conference/phase0/figures/."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from aw.post_conference.common import DATASETS, FIGURES, NULL_THRESHOLD, TABLES, Status, ensure_dirs, mpl

DS = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
COL = {"bp": "#1f77b4", "epc": "#d62728", "frozen": "#444444", "knn": "#7f7f7f", "lex": "#2ca02c", "oracle": "#9467bd"}
LAB = {"bp": "BP-CAP", "epc": "PC-CAP"}


def save(fig, name):
    fig.savefig(FIGURES / f"{name}.png", dpi=150, bbox_inches="tight")
    fig.savefig(FIGURES / f"{name}.svg", bbox_inches="tight")
    import matplotlib.pyplot as plt

    plt.close(fig)
    return name


def frontier(plt, fr, icf, ics):
    """Paraphrase success vs false-fire rate on constructed near-miss neighbours (left) and paraphrase mean NLL vs
    fire rate on item-locality prompts (right), one row per dataset; threshold sweeps for the six readers, the
    in-context retrievers' threshold sweeps, frozen and the in-context oracle."""
    fig, axes = plt.subplots(3, 2, figsize=(12, 12))
    for i, ds in enumerate(DATASETS):
        for j, (xcol, ycol, xl, yl) in enumerate((("near_miss_neighbour_fire_rate", "paraphrase_exact", "false-fire rate on near-miss neighbours", "paraphrase exact match"),
                                                  ("locality_item_fire_rate", "paraphrase_mean_nll", "fire rate on item-locality prompts", "paraphrase mean NLL (nats/token)"))):
            ax = axes[i, j]
            for model, x in fr[fr.dataset == ds].groupby("model"):
                x = x.sort_values("tau")
                rule = model.split("_")[0]
                ax.plot(x[xcol], x[ycol], "-", color=COL[rule], alpha=0.8, lw=1.2, label=LAB[rule] if model.endswith("s0") else None)
                r = x[np.isclose(x.tau, NULL_THRESHOLD)]
                ax.plot(r[xcol], r[ycol], "o", color=COL[rule], ms=6)
            for arm in ("knn", "lex"):
                x = icf[(icf.dataset == ds) & (icf.arm == arm)].sort_values("theta")
                if len(x):
                    ax.plot(x[xcol], x[ycol], "--", color=COL[arm], lw=1.2, label=f"in-context {arm} (threshold sweep)")
            s = ics[(ics.dataset == ds) & (ics.family == "paraphrase")]
            fz = s[s.arm == "frozen"]
            orc = s[s.arm == "in-context oracle"]
            if len(fz):
                ax.plot([0], [fz.exact.iloc[0] if j == 0 else fz.mean_nll.iloc[0]], "s", color=COL["frozen"], ms=8, label="frozen GPT-2")
            if len(orc):
                ax.plot([0], [orc.exact_prefix.iloc[0] if j == 0 else orc.mean_nll.iloc[0]], "^", color=COL["oracle"], ms=8, label="in-context oracle (own fact)")
            ax.set_xlabel(xl)
            ax.set_ylabel(yl)
            ax.set_title(f"{DS[ds]}")
            ax.grid(alpha=0.3)
            if i == 0 and j == 0:
                ax.legend(fontsize=8, loc="lower right")
    fig.suptitle("Gate frontier: null-threshold sweep of the six readers (dots = registered threshold 0.5) versus in-context retrieval; lowering the threshold costs nothing on the GPU, raising it was replayed", fontsize=10)
    fig.tight_layout()
    return save(fig, "frontier")


def frontier_cvar(plt, fr):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for i, ds in enumerate(DATASETS):
        ax = axes[i]
        for model, x in fr[fr.dataset == ds].groupby("model"):
            x = x.sort_values("tau")
            rule = model.split("_")[0]
            ax.plot(x.tau, x.paraphrase_cvar95, "-", color=COL[rule], alpha=0.8, label=LAB[rule] if model.endswith("s0") else None)
            ax.plot(x.tau, x.paraphrase_mean_nll, ":", color=COL[rule], alpha=0.8)
        ax.axvline(NULL_THRESHOLD, color="k", lw=0.8, ls="--")
        ax.set_title(f"{DS[ds]}: paraphrase CVaR95 (solid) and mean (dotted) vs null threshold")
        ax.set_xlabel("null threshold τ (fire when null mass < τ)")
        ax.set_ylabel("nats/token")
        ax.grid(alpha=0.3)
        if i == 0:
            ax.legend(fontsize=8)
    fig.tight_layout()
    return save(fig, "frontier_threshold_sweep")


def atlas(plt, summ):
    cats = [c for c in summ.category.unique() if "fired" in c or "abstained" in c]
    order = ["correct record fired, success", "correct record fired, failed (payload)", "wrong record fired", "abstained by null threshold, correct record retrieved", "abstained by rare-token veto, correct record retrieved", "abstained, correct record not retrieved", "abstained, no candidates"]
    order = [c for c in order if c in cats]
    colors = ["#2ca02c", "#ff7f0e", "#d62728", "#1f77b4", "#17becf", "#9467bd", "#7f7f7f"]
    fig, ax = plt.subplots(figsize=(11, 4.5))
    x = summ[(summ.family == "paraphrase") & (summ.model.isin(["bp_mean", "epc_mean"]))]
    labels, bottoms = [], []
    pos = 0
    ticks = []
    for ds in DATASETS:
        for rule in ("bp", "epc"):
            y = x[(x.dataset == ds) & (x.rule == rule)].set_index("category").share_seed_mean
            b = 0
            for c, col in zip(order, colors):
                v = float(y.get(c, 0.0))
                ax.bar(pos, v, bottom=b, color=col, width=0.8, label=c if pos == 0 else None)
                b += v
            ticks.append((pos, f"{DS[ds]}\n{LAB[rule]}"))
            pos += 1
        pos += 0.6
    ax.set_xticks([t for t, _ in ticks])
    ax.set_xticklabels([l for _, l in ticks], fontsize=8)
    ax.set_ylabel("share of paraphrase probes (seed mean)")
    ax.set_title("Failure atlas on paraphrases at 300 edits: what the reader did")
    ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.tight_layout()
    return save(fig, "failure_atlas")


def oracle(plt, orc, ics):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4), sharey=True)
    for i, ds in enumerate(DATASETS):
        ax = axes[i]
        x = orc[orc.dataset == ds]
        pos = 0
        ticks = []
        for rule in ("bp", "epc"):
            y = x[x.rule == rule]
            ax.bar(pos, y.success_registered.mean(), color=COL[rule], alpha=0.5, width=0.8, yerr=[[y.success_registered.mean() - y.success_registered.min()], [y.success_registered.max() - y.success_registered.mean()]], capsize=3)
            ax.bar(pos + 1, y.success_oracle.mean(), color=COL[rule], width=0.8, yerr=[[y.success_oracle.mean() - y.success_oracle.min()], [y.success_oracle.max() - y.success_oracle.mean()]], capsize=3)
            ticks += [(pos, f"{LAB[rule]}\nregistered gate"), (pos + 1, f"{LAB[rule]}\noracle record")]
            pos += 2.5
        s = ics[(ics.dataset == ds) & (ics.family == "paraphrase")]
        for arm, col in (("in-context oracle", COL["oracle"]), ("in-context knn", COL["knn"]), ("in-context lex", COL["lex"])):
            v = s[s.arm == arm]
            if len(v):
                ax.bar(pos, v.exact_prefix.iloc[0], color=col, width=0.8)
                ticks.append((pos, arm.replace("in-context ", "in-context\n")))
                pos += 1
        ax.set_xticks([t for t, _ in ticks])
        ax.set_xticklabels([l for _, l in ticks], fontsize=7)
        ax.set_title(f"{DS[ds]}: paraphrase success")
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("paraphrase exact match (seed min/mean/max)")
    fig.suptitle("Oracle selection (item's own record forced) versus the registered gate, beside the in-context arms (prefix exact match)", fontsize=10)
    fig.tight_layout()
    return save(fig, "oracle_rescue")


def incontext(plt, ics):
    fams = [("edit", "taught prompt"), ("paraphrase", "paraphrase"), ("locality_item", "item-locality (true answer)"), ("near_miss_neighbour", "near-miss neighbour (true)"), ("unseen", "unseen (new)")]
    arms = ["frozen", "in-context oracle", "in-context knn", "in-context lex", "BP-CAP seed mean", "PC-CAP seed mean"]
    cols = [COL["frozen"], COL["oracle"], COL["knn"], COL["lex"], COL["bp"], COL["epc"]]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for i, ds in enumerate(DATASETS):
        for j, metric in enumerate(("mean_nll", "frac_worse_1nat")):
            ax = axes[j, i]
            w = 0.13
            for k, (arm, col) in enumerate(zip(arms, cols)):
                vals = []
                for fam, _ in fams:
                    v = ics[(ics.dataset == ds) & (ics.family == fam) & (ics.arm == arm)]
                    vals.append(float(v[metric].iloc[0]) if len(v) else np.nan)
                ax.bar(np.arange(len(fams)) + (k - 2.5) * w, vals, width=w, color=col, label=arm if (i == 0 and j == 0) else None)
            ax.set_xticks(np.arange(len(fams)))
            ax.set_xticklabels([l for _, l in fams], fontsize=7, rotation=15)
            ax.set_title(f"{DS[ds]}: " + ("mean NLL (nats/token)" if metric == "mean_nll" else "fraction worse than frozen by > 1 nat"))
            ax.grid(axis="y", alpha=0.3)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle("Equal-information baselines: frozen GPT-2 with a retrieved taught fact in context, beside the caps (300 edits)", fontsize=10)
    fig.tight_layout()
    return save(fig, "incontext_vs_cap")


def locality(plt, lc):
    fig, ax = plt.subplots(figsize=(8, 4))
    x = lc[lc.dataset == "mquake"].sort_values("model")
    pos = np.arange(len(x))
    ax.bar(pos - 0.2, x.taught_severe, width=0.4, color="#9467bd", label="severe deteriorations on locality prompts that are taught items (cap applied its own record)")
    ax.bar(pos + 0.2, x.other_severe, width=0.4, color="#d62728", label="severe deteriorations on genuinely unrelated locality prompts")
    ax.set_xticks(pos)
    ax.set_xticklabels(x.label, rotation=20, fontsize=8)
    ax.set_ylabel("count of D > 2 nats/token (600 prompts)")
    ax.set_title("MQuAKE item-locality corrigendum: 40 of 600 locality prompts are themselves taught stream items")
    ax.legend(fontsize=7)
    fig.tight_layout()
    return save(fig, "locality_corrigendum")


def composition(plt, cr, cf):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4))
    ax = axes[0]
    x = cr[cr.target == "new"].sort_values("model")
    pos = np.arange(len(x))
    ax.bar(pos - 0.3, x.dependency_retrieved_rate, width=0.3, color="#1f77b4", label="dependency record among retrieved candidates")
    ax.bar(pos, x.fired_rate, width=0.3, color="#ff7f0e", label="gate fired")
    ax.bar(pos + 0.3, x.exact_rate, width=0.3, color="#2ca02c", label="new answer exact")
    ax.set_xticks(pos)
    ax.set_xticklabels(x.label, rotation=20, fontsize=8)
    ax.set_title("Multi-hop questions (240): retrieval, firing, success")
    ax.legend(fontsize=7)
    ax.grid(axis="y", alpha=0.3)
    ax = axes[1]
    rows = cf[cf.kind.isin(["single_hop_cloze (unedited hop)", "single_hop_question (unedited hop)", "single_hop_cloze (edited hop)", "multihop_in_context"]) & (cf.target == "new")]
    labels = {"single_hop_cloze (unedited hop)": "frozen: unedited hop\n(cloze)", "single_hop_question (unedited hop)": "frozen: unedited hop\n(question)", "single_hop_cloze (edited hop)": "frozen: edited hop\n(cloze, new answer)", "multihop_in_context": "frozen + taught fact\nin context: multi-hop"}
    ax.bar(np.arange(len(rows)), rows.exact.astype(float), color=["#444444", "#444444", "#888888", "#9467bd"][: len(rows)])
    ax.set_xticks(np.arange(len(rows)))
    ax.set_xticklabels([labels.get(k, k) for k in rows.kind], fontsize=7)
    ax.set_ylabel("exact match")
    ax.set_title("Frozen GPT-2 small: does it know the other hop?")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    return save(fig, "composition")


def main():
    ensure_dirs()
    plt = mpl()
    made = []
    fr = pd.read_csv(TABLES / "frontier.csv")
    icf = pd.read_csv(TABLES / "incontext_frontier.csv")
    ics = pd.read_csv(TABLES / "incontext_summary.csv")
    made.append(frontier(plt, fr, icf, ics))
    made.append(frontier_cvar(plt, fr))
    made.append(atlas(plt, pd.read_csv(TABLES / "failure_atlas_summary.csv")))
    made.append(oracle(plt, pd.read_csv(TABLES / "oracle_rescue.csv"), ics))
    made.append(incontext(plt, ics))
    made.append(locality(plt, pd.read_csv(TABLES / "locality_contamination.csv")))
    made.append(composition(plt, pd.read_csv(TABLES / "composition_retrieval.csv"), pd.read_csv(TABLES / "composition_frozen_ceiling.csv")))
    st = Status()
    for m in made:
        st.artifact(f"figures/{m}", FIGURES / f"{m}.png")
    st.stage("figures", "complete", figures=made)
    print(json.dumps(made))


if __name__ == "__main__":
    main()
