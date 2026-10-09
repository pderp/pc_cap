"""Figures for ext-20261009 (matplotlib from the status-paper environment, as the frozen reproduction guide does).

    JAX_PLATFORMS=cpu MPLCONFIGDIR=/tmp/ext-mpl python -m aw.extremes.figures

Every figure states dataset, sample size, evaluation type, models, units and uncertainty in its title or caption file.
Outputs PNG + SVG under assets/extremes_analysis/ext-20261009/figures/ and a captions.json next to them.
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

FIG = DATA / "figures"
COL = {"frozen": "#444444", "bp": "#1f77b4", "epc": "#d62728"}
CAPTIONS = {}


def save(fig, name, caption):
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / f"{name}.png", dpi=160, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)
    CAPTIONS[name] = caption


def fig_rank_frequency():
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, ds in zip(axes, ("zsre", "counterfact", "mquake")):
        for var, ls in (("relation_id", "-"), ("target_new", "--"), ("subject", ":")):
            p = DATA / "data" / "frequency" / f"{ds}_eligible_{var}.csv"
            if not p.exists():
                continue
            t = pd.read_csv(p)
            ax.loglog(t["rank"], t["count"], ls, label=f"{var} (K={len(t)})")
        ax.set_title(f"{ds}: eligible pool, independent cases")
        ax.set_xlabel("rank"); ax.set_ylabel("count"); ax.legend(fontsize=7)
    save(fig, "rank_frequency", "Rank-frequency (log-log) of relation, new-target and subject categories in each eligible pool (zsRE 10,420; CounterFact 20,091; MQuAKE 6,043 single-hop items). zsRE has no relation ids. Straight segments are not a power-law test.")


def fig_frozen_surprisal():
    pc = pd.read_parquet(DATA / "data" / "paired_cases.parquet")
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
    for ds in ("zsre", "counterfact", "mquake"):
        x = pc[(pc["dataset"] == ds) & (pc["family"] == "edit") & (pc["target"] == "new")]["L_frozen_h0"].dropna().to_numpy()
        if not len(x):
            continue
        xs = np.sort(x)
        axes[0].hist(x, bins=40, histtype="step", density=True, label=f"{ds} (n={len(x)})")
        axes[1].loglog(xs, 1 - np.arange(len(xs)) / len(xs), label=ds)
    axes[0].set_xlabel("frozen GPT-2 per-token NLL of the taught target (nats)"); axes[0].set_ylabel("density"); axes[0].legend(fontsize=8); axes[0].set_title("edit prompts, realization 0 (300 items each)")
    axes[1].set_xlabel("per-token NLL (nats)"); axes[1].set_ylabel("P(X > x)"); axes[1].set_title("empirical survival (CCDF)"); axes[1].legend(fontsize=8)
    save(fig, "frozen_surprisal", "Frozen GPT-2 small: teacher-forced per-token NLL of the taught (new) target on the 300 edit prompts of realization 0, per dataset; histogram and empirical CCDF. No cap, no adaptation.")


def fig_tail_shapes():
    p = OUT / "tables" / "token_loss_tail_fits.csv"
    if not p.exists():
        return
    t = pd.read_csv(p)
    t = t[(t["family"] == "pooled_probes") & (t["quantile"] == 0.95) & t["kappa"].notna()]
    if t.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 3.8))
    labels = []
    for i, (_, r) in enumerate(t.sort_values(["dataset", "model"]).iterrows()):
        lo, hi = r.get("kappa_ci_low"), r.get("kappa_ci_high")
        ax.errorbar(i, r["kappa"], yerr=[[r["kappa"] - lo] if pd.notna(lo) else [0], [hi - r["kappa"]] if pd.notna(hi) else [0]], fmt="o", color=COL["epc"] if "epc" in r["model"] else COL["bp"] if "bp" in r["model"] else COL["frozen"])
        labels.append(f"{r['dataset']} {r['family']}\n{r['model']}")
    ax.axhline(0, color="k", lw=0.5); ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=5, rotation=90); ax.set_ylabel("GPD shape kappa (P95 threshold)")
    ax.set_title("Token-level target-surprisal tails, pooled probe families: GPD shape with item-bootstrap 95 % CI")
    save(fig, "tail_shapes_probe_loss", "Generalized-Pareto shape fitted to exceedances of per-token target surprisal above its P95, pooled over all target tokens (terminator excluded) of the edit/paraphrase/unseen prompts (new target) and locality/near-miss prompts (true target) for each model at 300 edits (frozen: no memory); 200 item-group bootstrap draws. Finite-range fits, not asymptotic classes.")


def fig_deciles():
    p = OUT / "tables" / "difficulty_deciles.csv"
    if not p.exists():
        return
    t = pd.read_csv(p)
    for ds in t["dataset"].unique():
        for fam in ("edit", "paraphrase", "unseen"):
            z = t[(t["dataset"] == ds) & (t["family"] == fam) & (t["horizon"] == 300) & (t["target"] == "new")]
            if z.empty:
                continue
            fig, ax = plt.subplots(figsize=(7, 3.8))
            for name, color in (("G_BP", COL["bp"]), ("G_PC", COL["epc"])):
                ax.errorbar(z["decile"], z[f"{name}_mean"], yerr=[z[f"{name}_mean"] - z[f"{name}_mean_ci_low"], z[f"{name}_mean_ci_high"] - z[f"{name}_mean"]], fmt="-o", color=color, label=f"{name} (seed mean)")
            ax.plot(z["decile"], z["G_PCvsBP_mean"], "s--", color="gray", label="G_PCvsBP")
            ax.axhline(0, color="k", lw=0.5); ax.set_xlabel("frozen-difficulty decile (1 = easiest)"); ax.set_ylabel("gain = L_frozen - L_model (nats/token)")
            ax.set_title(f"{ds} {fam} (new target), 300 edits, n={int(z['n'].sum())}; 500 group-bootstrap draws"); ax.legend(fontsize=8)
            save(fig, f"deciles_{ds}_{fam}", f"Mean paired gain over frozen GPT-2 by frozen-difficulty decile on {ds} {fam} prompts (new target) at the 300-edit horizon; BP and ePC readers as seed means over three paired seeds; grey: ePC minus BP. Deciles are fixed by the frozen model's per-token NLL; 95 % intervals from 500 item-group bootstrap draws.")


def fig_cvar():
    p = OUT / "tables" / "cvar_A_B.csv"
    if not p.exists():
        return
    t = pd.read_csv(p)
    t = t[(t["horizon"] == 300) & (t["target"] == "new") & (t["family"].isin(["edit", "paraphrase", "unseen"]))]
    if t.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ax, col, title in ((axes[0], "A_cvar95_own", "A: each model's own CVaR95 of per-token loss"), (axes[1], "B_mean_loss_on_frozen_hard5", "B: mean loss on the frozen model's hardest 5 %")):
        piv = t.pivot_table(index=["dataset", "family"], columns="model", values=col)
        piv.plot.bar(ax=ax, width=0.85, color=[COL["frozen"] if m == "frozen" else COL["bp"] if m.startswith("bp") else COL["epc"] for m in piv.columns], legend=False)
        ax.set_title(title, fontsize=9); ax.set_ylabel("nats/token"); ax.tick_params(axis="x", labelsize=7)
    axes[0].legend(fontsize=6, ncol=2)
    save(fig, "cvar_A_B", "Two different worst-case summaries at 300 edits: (A) each model's own CVaR95 of per-token target loss; (B) every model's mean loss on the same fixed set, the 5 % of cases hardest for frozen GPT-2. Families: edit, paraphrase, unseen (new target).")


def fig_paired_differences():
    pc = pd.read_parquet(DATA / "data" / "paired_cases.parquet")
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, ds in zip(axes, ("zsre", "counterfact", "mquake")):
        z = pc[(pc["dataset"] == ds) & (pc["family"] == "paraphrase") & (pc["target"] == "new")]
        ok = True
        for s in range(3):
            a, b = f"L_bp_reader_s{s}_h300", f"L_epc_reader_s{s}_h300"
            if a not in z.columns or b not in z.columns:
                ok = False
                continue
            d = (z[b] - z[a]).dropna()
            ax.hist(d, bins=40, histtype="step", label=f"seed {s} (n={len(d)}, mean {d.mean():+.3f})")
        ax.axvline(0, color="k", lw=0.5); ax.set_xlabel("L_ePC - L_BP (nats/token), paraphrase prompts, 300 edits"); ax.set_title(ds); ax.legend(fontsize=7)
        if not ok:
            ax.text(0.5, 0.5, "not available", ha="center", transform=ax.transAxes)
    save(fig, "paired_pc_minus_bp", "Paired per-probe differences of per-token target loss, ePC-trained minus BP-trained reader of the same seed, on paraphrase prompts (new target) at the 300-edit horizon. Positive values favour BP.")


def fig_write_norms():
    sc = pd.read_parquet(DATA / "data" / "scores.parquet")
    z = sc[(sc["horizon"] == 300) & (sc["target"] == "new") & (sc["family"].isin(["edit", "paraphrase"])) & sc["write_rel_max_over_sites"].notna()]
    if z.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    for ds, marker in (("zsre", "o"), ("counterfact", "s"), ("mquake", "^")):
        for rule, color in (("bp", COL["bp"]), ("epc", COL["epc"])):
            y = z[(z["dataset"] == ds) & (z["model"].str.startswith(rule))]
            if y.empty:
                continue
            fr = y.merge(sc[(sc["model"] == "frozen") & (sc["target"] == "new")][["dataset", "probe_id", "nll_token"]].rename(columns={"nll_token": "L_frozen"}), on=["dataset", "probe_id"], how="left")
            axes[0].scatter(fr["L_frozen"], fr["write_rel_max_over_sites"], s=6, alpha=0.4, marker=marker, color=color, label=f"{ds} {rule}")
            axes[1].scatter(fr["write_rel_max_over_sites"], fr["L_frozen"] - fr["nll_token"], s=6, alpha=0.4, marker=marker, color=color)
    axes[0].set_xlabel("frozen per-token NLL (nats)"); axes[0].set_ylabel("max relative write norm over sites"); axes[0].set_yscale("symlog", linthresh=1e-3); axes[0].legend(fontsize=6, ncol=2); axes[0].set_title("correction magnitude vs baseline difficulty")
    axes[1].set_xlabel("max relative write norm over sites"); axes[1].set_ylabel("gain over frozen (nats/token)"); axes[1].set_xscale("symlog", linthresh=1e-3); axes[1].set_title("correction magnitude vs gain")
    save(fig, "write_norms", "Relative write magnitude (||W_m|| / ||h_m|| at the prediction position, maximum over the three sites and over the scored target positions) against frozen difficulty and against the paired gain; edit and paraphrase prompts, new target, 300 edits, all six readers. Zero means the reader abstained.")


def fig_mquake():
    p = OUT / "tables" / "benchmark_original.csv"
    if not p.exists():
        return
    t = pd.read_csv(p)
    z = t[(t["dataset"] == "mquake") & (t["horizon"] == 300) & t["composition_success"].notna()] if "composition_success" in t else pd.DataFrame()
    if z.empty:
        return
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(z["model"], z["RET-GS"], color=[COL["epc"] if "epc" in m else COL["bp"] for m in z["model"]], label="RET-GS (paraphrase retention)")
    ax.plot(z["model"], z["composition_success"], "kD", label="multi-hop all-question success (80 cases)")
    ax.set_ylim(0, 1); ax.tick_params(axis="x", rotation=45, labelsize=8); ax.legend(fontsize=8); ax.set_title("MQuAKE, 300 edits: new supplemental PC-reader evaluations (ext-20261009)")
    save(fig, "mquake_pcreader", "MQuAKE realization 0, order 100, 300 edits: paraphrase retention (RET-GS, 300 items) and the registered composition endpoint (all three multi-hop questions correct, 80 cases) for the six saved readers, evaluated in this study.")


def fig_harm_survival():
    """Ordinary-text harm survival for the twelve frozen-record PC-reader cells plus this study's MQuAKE cells."""
    from aw.extremes.models import eval_dir

    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    for ax, ds in zip(axes, ("zsre", "counterfact", "mquake")):
        for rule, color in (("bp", COL["bp"]), ("epc", COL["epc"])):
            for s in range(3):
                vec = eval_dir(rule, s, ds) / "harm" / "vectors.npz"
                if not vec.exists():
                    continue
                with np.load(vec, allow_pickle=False) as f:
                    d = (f["values"][:, :, 0] - f["values"][:, :, 1]).ravel()
                grid = np.geomspace(0.01, max(0.011, d.max()), 60)
                surv = [(d > x).mean() for x in grid]
                ax.loglog(grid, np.maximum(surv, 1e-7), color=color, alpha=0.7, label=f"{rule} s{s}")
        ax.set_title(f"{ds} (245,237 positions per cell)"); ax.set_xlabel("harm threshold (nats)"); ax.set_ylabel("fraction of positions above"); ax.legend(fontsize=6)
    save(fig, "harm_survival_pcreader", "Ordinary-text harm (loss with cap minus loss without, same prefix) survival curves for the BP- and ePC-trained readers at 300 edits: zsRE and CounterFact from the frozen record, MQuAKE from this study's supplemental evaluations. Zero survival omitted on the log axis; curves are not power-law tests.")


def main():
    for f in (fig_rank_frequency, fig_frozen_surprisal, fig_tail_shapes, fig_deciles, fig_cvar, fig_paired_differences, fig_write_norms, fig_mquake, fig_harm_survival):
        try:
            f()
        except Exception as e:  # keep going; record the failure
            CAPTIONS[f.__name__] = f"FAILED: {e!r}"
    atomic_json(FIG / "captions.json", CAPTIONS)
    Status().stage("8_figures", "updated", figures=sorted(k for k, v in CAPTIONS.items() if not str(v).startswith("FAILED")), failed=sorted(k for k, v in CAPTIONS.items() if str(v).startswith("FAILED")))
    print(json.dumps({k: (v[:40] if not v.startswith("FAILED") else v) for k, v in CAPTIONS.items()}))


if __name__ == "__main__":
    main()
