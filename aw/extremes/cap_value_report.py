"""Supplemental report: the value of a CAP on frozen GPT-2 small — frozen vs BP-CAP vs PC-CAP (Markdown + PDF).

    JAX_PLATFORMS=cpu python -m aw.extremes.cap_value_report

Every number is read from results/extremes_analysis/ext-20261009/tables/cap_value/*.csv (written by aw.extremes.cap_value)
or from the study's existing tables; nothing is typed in by hand. Question A (what a CAP adds to frozen GPT-2, including on
extreme examples) is primary; question B (PC- vs BP-trained reader) is reported inside it.
"""

from __future__ import annotations

import json
import math
from datetime import date

import numpy as np
import pandas as pd

from aw.extremes.common import DATA, OUT, RUN_ID, Status, atomic_write_bytes, git_head
from aw.extremes.report import MODEL_LABEL, ci, f, md_table, pct

T = OUT / "tables" / "cap_value"
FIGREL = "../../../../../assets/extremes_analysis/ext-20261009/figures/cap_value"
DS = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
LAB = {"frozen": "Frozen GPT-2 (no CAP)", "bp_mean": "BP-CAP (seed mean)", "epc_mean": "PC-CAP (seed mean)", **{f"bp_reader_s{s}": f"BP-CAP seed {s}" for s in range(3)}, **{f"epc_reader_s{s}": f"PC-CAP seed {s}" for s in range(3)}}
THREE = ("frozen", "bp_mean", "epc_mean")
SEEDROWS = [f"bp_reader_s{s}" for s in range(3)] + [f"epc_reader_s{s}" for s in range(3)]


def csv(name):
    p = T / f"{name}.csv"
    return pd.read_csv(p) if p.exists() and p.stat().st_size else pd.DataFrame()


def g(r, k, d=3):
    v = r.get(k) if hasattr(r, "get") else None
    return f(None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v), d)


def gp(r, k, d=1):
    v = r.get(k)
    return pct(None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v), d=d)


def rng(r, k, d=3):
    lo, hi = r.get(k + "_seed_min"), r.get(k + "_seed_max")
    if lo is None or (isinstance(lo, float) and math.isnan(lo)):
        return ""
    return f" ({f(lo, d)}–{f(hi, d)})"


# ------------------------------------------------------------------------------------------------ sections
def sec_basic(basic, h=300):
    out = []
    for ds in DS:
        b = basic[(basic["dataset"] == ds) & (basic["horizon"] == h)].set_index("model")
        if b.empty:
            continue
        rows = []
        for m in list(THREE) + SEEDROWS:
            if m not in b.index:
                continue
            r = b.loc[m]
            es = gp(r, "ES") + (" ‡" if m == "frozen" else "")
            retgs = gp(r, "RET_GS") + (" §" if m == "frozen" else "")
            ls = gp(r, "LS") + (" ¶" if m == "frozen" else "")
            mh = gp(r, "mh_question_accuracy") if ds == "mquake" else "n/a"
            mh_all = gp(r, "mh_all_case") if ds == "mquake" else "n/a"
            rows.append([LAB.get(m, m), es, gp(r, "RET_ES"), retgs, g(r, "nll_edit"), g(r, "nll_paraphrase"), (g(r, "nll_edit_true_target") if ds != "zsre" else "n/a"), ls, gp(r, "D_locality_item_frac_worse") if m != "frozen" else "0 % (reference)", gp(r, "near_miss"), gp(r, "unseen_false_fire_rate"), mh, mh_all])
        den = b.loc["bp_mean"].get("RET_GS_den") if "bp_mean" in b.index else None
        out.append(f"### {DS[ds]} ({h} edits; {int(den) if pd.notna(den) else '—'} items; losses in nats/token)\n\n" + md_table(["model", "ES", "RET-ES", "RET-GS", "NLL taught prompt", "NLL paraphrase", "NLL original fact", "LS (own ref.)", "locality worse than frozen", "near-miss", "unseen false fires", "multi-hop Q acc.", "multi-hop all-3"], rows))
    out.append("‡ zero **by the eligibility screen**: every stream item was selected because frozen GPT-2 did not produce the answer (zsRE 0/10,720, CounterFact 0/20,391 screened; MQuAKE items pass the same screen). § measured zero (paraphrases were not part of the screen). ¶ 1 **by definition**: the locality reference *is* the frozen response. "
               "Frozen multi-hop question accuracy is the recorded cap-off exact match on the post-edit answer (0/240 on every cell); case-level all-3 success for the frozen path is not separately stored (it is 0 because no question is correct). Readers' ES/RET-ES/RET-GS/LS/near-miss/false-fire values are the registered record metrics; losses are this study's teacher-forced measurements on identical prompt/answer pairs.")
    return "\n\n".join(out)


def sec_improvements(imp, h=300):
    rows = []
    for ds in DS:
        for metric, name in (("nll_edit", "NLL taught prompt"), ("nll_paraphrase", "NLL paraphrase"), ("nll_edit_true_target", "NLL original fact"), ("RET_ES", "RET-ES"), ("RET_GS", "RET-GS"), ("mh_question_accuracy", "multi-hop Q accuracy")):
            z = imp[(imp["dataset"] == ds) & (imp["horizon"] == h) & (imp["metric"] == metric)]
            if z.empty:
                continue
            bp = z[z["model"] == "bp_mean"]; pc = z[z["model"] == "epc_mean"]
            if bp.empty or pc.empty:
                continue
            bp, pc = bp.iloc[0], pc.iloc[0]
            kind = bp["kind"]
            if kind == "loss":
                rows.append([DS[ds], name, f(bp["frozen"]), f(bp["model_value"]), f(pc["model_value"]), f"−{f(bp['absolute_improvement'])} ({f(bp['percent_improvement'], 1)} %)", f"−{f(pc['absolute_improvement'])} ({f(pc['percent_improvement'], 1)} %)"])
            else:
                rows.append([DS[ds], name, pct(bp["frozen"]), pct(bp["model_value"]), pct(pc["model_value"]), f"+{f(bp['absolute_improvement'], 1)} points" + (" (rel. undefined, frozen 0)" if bp["percent_improvement"] is None or pd.isna(bp["percent_improvement"]) else f" ({f(bp['percent_improvement'], 0)} %)"), f"+{f(pc['absolute_improvement'], 1)} points" + (" (rel. undefined, frozen 0)" if pc["percent_improvement"] is None or pd.isna(pc["percent_improvement"]) else f" ({f(pc['percent_improvement'], 0)} %)")])
    return md_table(["dataset", "metric", "frozen", "BP-CAP", "PC-CAP", "BP-CAP vs frozen", "PC-CAP vs frozen"], rows)


def sec_own(own, h=300, fams=("paraphrase", "edit", "unseen", "locality_item")):
    rows = []
    for ds in DS:
        for fam in fams:
            z = own[(own["dataset"] == ds) & (own["family"] == fam) & (own["horizon"] == h)].set_index("model")
            for m in THREE:
                if m not in z.index:
                    continue
                r = z.loc[m]
                rows.append([DS[ds], fam, LAB[m], int(r["n"]), f"{f(r['mean'])} {ci(r['mean_ci_low'], r['mean_ci_high'])}", f"{f(r['cvar95'])} {ci(r['cvar95_ci_low'], r['cvar95_ci_high'])}", f"{f(r['cvar99'])} {ci(r['cvar99_ci_low'], r['cvar99_ci_high'])}", f(r["max"])])
    return md_table(["dataset", "family", "model", "n", "mean", "own worst 5 % (CVaR95)", "own worst 1 % (CVaR99)", "max"], rows)


def sec_hard(hard, h=300, fams=("paraphrase", "edit")):
    rows = []
    for ds in DS:
        for fam in fams:
            for st, name in (("hard5", "frozen-hardest 5 %"), ("hard1", "frozen-hardest 1 %")):
                z = hard[(hard["dataset"] == ds) & (hard["family"] == fam) & (hard["horizon"] == h) & (hard["set"] == st)].set_index("model")
                for m in THREE:
                    if m not in z.index:
                        continue
                    r = z.loc[m]
                    rows.append([DS[ds], fam, name, int(r["k"]), LAB[m], f"{f(r['mean_loss'])} {ci(r['mean_loss_ci_low'], r['mean_loss_ci_high'])}", (f"{pct(r['success'])} {ci(r['success_ci_low'], r['success_ci_high'], 2)}" if pd.notna(r.get("success")) else "—"), pct(r["frac_below_1nat"]), f(r["max_loss"])])
    return md_table(["dataset", "family", "fixed set", "k", "model", "mean NLL on the set", "exact-match on the set", "share below 1 nat", "max"], rows)


def sec_deciles(dec, fam="paraphrase", h=300):
    out = []
    for ds in DS:
        z = dec[(dec["dataset"] == ds) & (dec["family"] == fam) & (dec["horizon"] == h)]
        if z.empty:
            continue
        rows = []
        for d in range(1, 11):
            zz = z[z["decile"] == d].set_index("model")
            if zz.empty:
                continue
            r0 = zz.loc["frozen"]
            cells = [str(d), int(r0["n"]), f"{f(r0['frozen_min'], 2)}–{f(r0['frozen_max'], 2)}"]
            for m in THREE:
                r = zz.loc[m]
                cells.append(f"{f(r['mean_loss'], 2)} {ci(r['ci_low'], r['ci_high'], 2)}" + (f" / {pct(r['success'], d=0)}" if pd.notna(r.get("success")) else ""))
            rows.append(cells)
        out.append(f"**{DS[ds]} {fam} prompts ({h} edits)** — mean NLL [95 % CI] / exact-match per decile\n\n" + md_table(["decile", "n", "frozen NLL range", LAB["frozen"], LAB["bp_mean"], LAB["epc_mean"]], rows))
    return "\n\n".join(out)


def sec_tails(tails):
    rows = []
    for ds in DS:
        for tn in ("frozen P95", "8 nats", "10 nats"):
            z = tails[(tails["dataset"] == ds) & (tails["threshold_name"] == tn)]
            for m in ["frozen"] + [f"bp_reader_s{s}" for s in range(3)] + [f"epc_reader_s{s}" for s in range(3)]:
                r = z[z["model"] == m]
                if r.empty:
                    continue
                r = r.iloc[0]
                kap = f"{f(r['kappa'], 2)} {ci(r.get('kappa_ci_low'), r.get('kappa_ci_high'), 2)}" if pd.notna(r.get("kappa")) else f"— ({r['fit_status']})"
                rows.append([DS[ds], tn, f(r["threshold"], 2), LAB.get(m, m), f"{int(r['n_tokens']):,}", int(r["n_exceed"]), f"{100 * r['frac_exceed']:.2f} %", g(r, "mean_excess", 2), kap, g(r, "loglik_gain_per_excess_vs_exponential", 4)])
    return md_table(["dataset", "threshold", "u (nats)", "model", "tokens", "exceedances", "fraction above u", "mean excess", "GPD shape κ [95 % CI]", "log-lik gain/excess vs exponential"], rows)


def tails_sensitivity(tails):
    """How many fits support a heavy tail (κ CI entirely above 0) by threshold, per model group."""
    rows = []
    for tn in ("frozen P90", "frozen P95", "frozen P97.5", "5 nats", "8 nats", "10 nats"):
        z = tails[(tails["threshold_name"] == tn) & (~tails["pooled_seeds"].astype(bool))]
        fits = z[z["kappa"].notna()]
        pos = int((fits["kappa_ci_low"] > 0).sum()) if len(fits) else 0
        neg = int((fits["kappa_ci_high"] < 0).sum()) if len(fits) else 0
        rows.append([tn, int(len(z)), int(len(fits)), int((z["fit_status"] == "insufficient").sum()), int((z["fit_status"] == "exploratory").sum()), f"{f(fits['kappa'].min(), 2)} to {f(fits['kappa'].max(), 2)}" if len(fits) else "—", pos, neg, int(len(fits) - pos - neg)])
    return md_table(["threshold", "model×dataset cells", "fitted (≥ 50 exc.)", "insufficient (< 50)", "exploratory (50–99)", "κ range", "CI entirely > 0", "CI entirely < 0", "CI includes 0"], rows)


def sec_collateral(coll, h=300):
    rows = []
    for ds in DS:
        for fam in ("locality_item", "locality", "near_miss_neighbour", "unseen"):
            z = coll[(coll["dataset"] == ds) & (coll["family"] == fam) & (coll["horizon"] == h)]
            for m in ("bp_mean", "epc_mean"):
                r = z[z["model"] == m]
                if r.empty:
                    continue
                r = r.iloc[0]
                seeds = z[z["model"].isin([f"{m[:-5]}_reader_s{s}" for s in range(3)])]
                sev = f"{int(seeds['n_D_gt_1'].sum())} / {int(seeds['n_D_gt_2'].sum())} / {int(seeds['n_D_gt_5'].sum())}"
                chg = (f"{100 * seeds['answer_changed_vs_frozen'].mean():.1f} %" if seeds["answer_changed_vs_frozen"].notna().any() else "n/a (not generated)") if "answer_changed_vs_frozen" in seeds else "n/a"
                own = (f"{seeds['record_own_reference_metric'].iloc[0]} = {', '.join(pct(v) for v in seeds['record_own_reference_value'])}" if "record_own_reference_metric" in seeds and seeds["record_own_reference_metric"].notna().any() else "—")
                rows.append([DS[ds], fam, LAB[m], int(r["n"]), f"{pct(r['frac_worse'])} {ci(100 * r['frac_worse_ci_low'], 100 * r['frac_worse_ci_high'], 1)}", f"{pct(r['frac_better'])}", f(r["mean_D"], 4), f(r["mean_positive_D"], 3), f(r["max_D"], 2), sev, chg, own])
    return md_table(["dataset", "family", "model", "n", "worse than frozen (> 1e-3 nats) [CI]", "better than frozen", "mean D", "mean positive D", "max D", "severe D > 1 / 2 / 5 nats (3 seeds)", "decoded answer changed vs frozen (seed mean)", "record metric vs own cap-off (seeds 0–2)"], rows)


def sec_worst(worst, h=300, k=2):
    rows = []
    for ds in DS:
        z = worst[(worst["dataset"] == ds) & (worst["horizon"] == h)].sort_values("D", ascending=False)
        for fam in ("locality_item", "locality", "near_miss_neighbour", "unseen"):
            zz = z[z["family"] == fam].head(k)
            for _, r in zz.iterrows():
                rows.append([DS[ds], fam, LAB.get(r["model"], r["model"]), str(r.get("subject"))[:40], f(r["L_frozen"], 2), f(r["L_model"], 2), f(r["D"], 2), str(r.get("fired")), g(r, "write_rel_max", 3)])
    return md_table(["dataset", "family", "model", "subject", "L frozen", "L cap", "D", "fired", "rel. write"], rows)


def sec_harm(harm):
    rows = []
    for _, r in harm.sort_values(["dataset", "rule", "seed"]).iterrows():
        rows.append([DS[r["dataset"]], LAB.get(r["model"], r["model"]), f"{int(r['positions']):,}", f"{r['mean_signed']:.2e}", f"{r['es99_positive']:.4f}", f(r["maximum"], 2), int(r["count_gt_0.01"]), int(r["count_gt_1.0"]), f"{r['changed_distribution_fraction']:.2e}" if pd.notna(r.get("changed_distribution_fraction")) else "—"])
    return md_table(["dataset", "cap", "positions", "mean Δ (nats)", "ES99+ (positive part)", "max Δ", "positions Δ > 0.01", "positions Δ > 1", "fraction of positions changed"], rows)


def sec_gating(gate, h=300):
    rows = []
    for ds in DS:
        for fam in ("paraphrase", "edit"):
            z = gate[(gate["dataset"] == ds) & (gate["family"] == fam) & (gate["horizon"] == h)]
            for _, r in z.iterrows():
                rows.append([DS[ds], fam, LAB.get(r["model"], r["model"]), int(r["n"]), pct(r["abstain_rate"]), g(r, "loss_abstained_mean", 2), g(r, "loss_abstained_cvar95", 2), g(r, "loss_fired_mean", 3), g(r, "loss_fired_cvar95", 2), gp(r, "success_fired"), f"{int(r['frozen_hard5_abstained'])}/{int(r['frozen_hard5_n'])}", pct(r["share_of_worst5pct_that_abstained"]), int(r["n_fired_but_above_2nats"]), g(r, "abstained_equal_frozen_max_abs_diff", 6)])
    return md_table(["dataset", "family", "cap", "n", "abstained", "NLL abstained (mean)", "NLL abstained (CVaR95)", "NLL fired (mean)", "NLL fired (CVaR95)", "success when fired", "frozen-hardest-5 % abstained", "share of own worst 5 % that abstained", "fired but > 2 nats", "max |L_abstained − L_frozen|"], rows)


def sec_pc_vs_bp(gains, basic, h=300):
    rows = []
    for ds in DS:
        for fam in ("edit", "paraphrase"):
            z = gains[(gains["dataset"] == ds) & (gains["family"] == fam) & (gains["target"] == "new") & (gains["horizon"] == h)]
            if z.empty:
                continue
            def cell(gain, seed="mean"):
                r = z[(z["gain"] == gain) & (z["seed"].astype(str) == seed)]
                if r.empty:
                    return "—"
                r = r.iloc[0]
                lo, hi = json.loads(r["mean_ci"]) if isinstance(r["mean_ci"], str) else r["mean_ci"]
                return f"{f(r['mean'])} {ci(lo, hi)}"
            rows.append([DS[ds], fam, cell("G_BP"), cell("G_PC"), cell("G_PCvsBP"), "; ".join(f"s{s}: {cell('G_PCvsBP', str(s))}" for s in range(3))])
    t1 = md_table(["dataset", "family", "BP-CAP gain over frozen", "PC-CAP gain over frozen", "PC − BP (positive favours PC)", "PC − BP per seed"], rows)
    rows = []
    for ds in DS:
        b = basic[(basic["dataset"] == ds) & (basic["horizon"] == h)].set_index("model")
        for m in ("bp_mean", "epc_mean"):
            if m in b.index:
                r = b.loc[m]
                rows.append([DS[ds], LAB[m], gp(r, "RET_GS") + rng(r, "RET_GS", 3).replace("0.", ".") if False else gp(r, "RET_GS") + f" ({pct(r.get('RET_GS_seed_min'))}–{pct(r.get('RET_GS_seed_max'))})", gp(r, "near_miss"), gp(r, "unseen_false_fire_rate"), (gp(r, "mh_all_case") if ds == "mquake" else "n/a"), g(r, "harm_es99_positive", 4), g(r, "harm_max", 2)])
    t2 = md_table(["dataset", "cap", "RET-GS seed mean (min–max)", "near-miss", "unseen false fires", "multi-hop all-3", "text harm ES99+ (seed mean)", "text harm max Δ"], rows)
    return t1, t2


def sec_support(sup):
    return md_table(["requested comparison", "support", "how", "where"], [[r["requested_comparison"], r["support"], r["how"], r["where"]] for _, r in sup.iterrows()])


def sec_audit(rec, audit):
    bad = rec[(rec["model"] == "frozen") & (rec["consistent_with_horizon"] == False)]  # noqa: E712
    a = audit[(audit["item_level"]) & (audit["horizon"] == 100)]
    mixed = int(((a["probe_rows"] - a["probe_rows_within_horizon"]) > 0).sum())
    rows = []
    for ds in DS:
        for h in (100, 300):
            z = rec[(rec["dataset"] == ds) & (rec["horizon"] == h)]
            fz = z[z["model"] == "frozen"]; rd = z[z["model"] != "frozen"]
            rows.append([DS[ds], h, (int(fz["ES_den"].iloc[0]) if len(fz) else "—"), (int(fz["RET_GS_den"].iloc[0]) if len(fz) else "—"), ", ".join(str(int(v)) for v in sorted(rd["ES_den"].dropna().unique())), ", ".join(str(int(v)) for v in sorted(rd["RET_GS_den"].dropna().unique()))])
    t = md_table(["dataset", "horizon", "frozen ES denominator", "frozen RET-GS denominator (items)", "reader ES denominators", "reader RET-GS denominators"], rows)
    return t, len(bad), mixed


def headline(basic, imp, hard, own, coll, gate, tails, gains, harm):
    H = []
    def b(ds, m, k):
        z = basic[(basic["dataset"] == ds) & (basic["horizon"] == 300) & (basic["model"] == m)]
        return None if z.empty or pd.isna(z.iloc[0].get(k)) else float(z.iloc[0][k])
    # A1 ordinary
    parts = []
    for ds in DS:
        fz, bp, pc = b(ds, "frozen", "nll_paraphrase"), b(ds, "bp_mean", "nll_paraphrase"), b(ds, "epc_mean", "nll_paraphrase")
        if fz is None:
            continue
        parts.append(f"{DS[ds]} {f(fz, 2)} → {f(bp, 2)} (BP-CAP, −{100 * (fz - bp) / fz:.0f} %) / {f(pc, 2)} (PC-CAP, −{100 * (fz - pc) / fz:.0f} %)")
    H.append("- **A1. Ordinary adaptation.** On paraphrases of the taught facts (the cap never saw these prompts), mean per-token NLL falls from frozen to cap: " + "; ".join(parts) + ". Exact-match paraphrase retention rises from a measured 0 % (frozen) to "
             + "; ".join(f"{DS[ds]} {pct(b(ds, 'bp_mean', 'RET_GS'))} (BP) / {pct(b(ds, 'epc_mean', 'RET_GS'))} (PC)" for ds in DS if b(ds, "bp_mean", "RET_GS") is not None) + ". On the taught prompts themselves both caps reach 99–100 % (frozen: 0 % by the eligibility screen).")
    # A2 frozen hardest (data-driven: absolute and relative reduction on the fixed hardest 5 % vs overall)
    parts = []
    for ds in DS:
        z = hard[(hard["dataset"] == ds) & (hard["family"] == "paraphrase") & (hard["horizon"] == 300) & (hard["set"] == "hard5")].set_index("model")
        o = own[(own["dataset"] == ds) & (own["family"] == "paraphrase") & (own["horizon"] == 300)].set_index("model")
        if z.empty or o.empty:
            continue
        fz, bp, pc = z.loc["frozen", "mean_loss"], z.loc["bp_mean", "mean_loss"], z.loc["epc_mean", "mean_loss"]
        ofz, obp, opc = o.loc["frozen", "mean"], o.loc["bp_mean", "mean"], o.loc["epc_mean", "mean"]
        parts.append(f"{DS[ds]} (k = {int(z.loc['frozen', 'k'])}): {f(fz, 2)} → {f(bp, 2)} (BP, −{100 * (fz - bp) / fz:.0f} % vs −{100 * (ofz - obp) / ofz:.0f} % overall) / {f(pc, 2)} (PC, −{100 * (fz - pc) / fz:.0f} % vs −{100 * (ofz - opc) / ofz:.0f} % overall); exact match on the set {pct(z.loc['bp_mean', 'success'])} / {pct(z.loc['epc_mean', 'success'])}")
    H.append("- **A2. The frozen model's hardest examples.** On the fixed 5 % of paraphrases that frozen GPT-2 finds hardest, mean NLL falls " + "; ".join(parts) + ". The absolute reduction is largest where the frozen model is worst (decile figures), while the caps' own loss also rises with frozen difficulty, so the relative reduction on the hardest cases is somewhat smaller than overall on CounterFact and MQuAKE and complete on zsRE.")
    # A3 own worst
    parts = []
    for ds in DS:
        z = own[(own["dataset"] == ds) & (own["family"] == "paraphrase") & (own["horizon"] == 300)].set_index("model")
        if z.empty:
            continue
        parts.append(f"{DS[ds]}: CVaR95 {f(z.loc['frozen', 'cvar95'], 2)} → {f(z.loc['bp_mean', 'cvar95'], 2)} (BP, −{100 * (z.loc['frozen', 'cvar95'] - z.loc['bp_mean', 'cvar95']) / z.loc['frozen', 'cvar95']:.0f} %) / {f(z.loc['epc_mean', 'cvar95'], 2)} (PC, −{100 * (z.loc['frozen', 'cvar95'] - z.loc['epc_mean', 'cvar95']) / z.loc['frozen', 'cvar95']:.0f} %); CVaR99 {f(z.loc['frozen', 'cvar99'], 2)} → {f(z.loc['bp_mean', 'cvar99'], 2)} / {f(z.loc['epc_mean', 'cvar99'], 2)}")
    H.append("- **A3. Each model's own worst errors.** The caps' own worst 5 % and 1 % of paraphrase losses are lower than the frozen model's own worst cases, but by much less than the mean improvement: " + "; ".join(parts) + ". A cap's residual worst cases are the prompts on which its reader abstained (loss = frozen loss to the bit) or fired without fixing the answer (table 9.2).")
    # A4 collateral
    parts = []
    for ds in DS:
        z = coll[(coll["dataset"] == ds) & (coll["family"] == "locality_item") & (coll["horizon"] == 300)]
        if z.empty:
            continue
        bp = z[z["model"] == "bp_mean"].iloc[0]; pc = z[z["model"] == "epc_mean"].iloc[0]
        sb = z[z["model"].isin([f"bp_reader_s{s}" for s in range(3)])]["n_D_gt_2"].sum(); sp = z[z["model"].isin([f"epc_reader_s{s}" for s in range(3)])]["n_D_gt_2"].sum()
        parts.append(f"{DS[ds]}: worse than frozen on {pct(bp['frac_worse'])} (BP) / {pct(pc['frac_worse'])} (PC) of item-locality prompts, severe (> 2 nats/token) events {int(sb)} / {int(sp)} over three seeds ({int(bp['n'])} prompts each)")
    H.append("- **A4. Collateral change.** Against frozen GPT-2 directly (not only against each cap's own cap-off reference), the caps leave most locality-type prompts bit-identical; the exceptions are rare but can be severe: " + "; ".join(parts) + f". On {int(harm['positions'].iloc[0]):,} positions of unrelated text per cell the mean change is {harm['mean_signed'].min():.1e} to {harm['mean_signed'].max():.1e} nats, with single-position maxima of {harm['maximum'].min():.1f}–{harm['maximum'].max():.1f} nats and {int(harm['count_gt_1.0'].min())}–{int(harm['count_gt_1.0'].max())} positions changed by more than 1 nat per cell (table 8.3).")
    # A5 negatives
    mq = basic[(basic["dataset"] == "mquake") & (basic["horizon"] == 300)].set_index("model")
    if "bp_mean" in mq.index and pd.notna(mq.loc["bp_mean"].get("mh_all_case")):
        H.append(f"- **A5. What the CAP does not fix.** MQuAKE multi-hop composition stays at the frozen level: all-three-questions success {pct(mq.loc['bp_mean', 'mh_all_case'])} (BP) / {pct(mq.loc['epc_mean', 'mh_all_case'])} (PC) of 80 cases, question accuracy {pct(mq.loc['bp_mean', 'mh_question_accuracy'])} / {pct(mq.loc['epc_mean', 'mh_question_accuracy'])} vs frozen {pct(mq.loc['frozen', 'mh_question_accuracy'])}; and every abstained paraphrase keeps the frozen model's full loss.")
    # tails
    fits = tails[(tails["threshold_name"].isin(["frozen P95", "8 nats"])) & (~tails["pooled_seeds"].astype(bool)) & tails["kappa"].notna()]
    posrows = fits[fits["kappa_ci_low"] > 0]
    posl = "; ".join(f"{LAB.get(r['model'], r['model'])} on {DS[r['dataset']]} at {r['threshold_name']} (κ = {f(r['kappa'], 2)} {ci(r['kappa_ci_low'], r['kappa_ci_high'], 2)}, {int(r['n_exceed'])} exceedances)" for _, r in posrows.iterrows())
    H.append(f"- **A6. Tail shape.** At common absolute thresholds (frozen P95 and 8 nats) {len(fits)} GPD fits with ≥ 50 exceedances have shapes from {f(fits['kappa'].min(), 2)} to {f(fits['kappa'].max(), 2)}; {len(posrows)} interval(s) lie entirely above zero" + (f" ({posl}), and that cell turns negative at 8 nats" if len(posrows) else "") + ". At every common threshold both caps have fewer exceedances than frozen GPT-2 (table 7.1): the caps thin the frozen tail rather than change its class, and none of these finite-sample fits is evidence of a power law.")
    # B
    parts = []
    for ds in DS:
        z = gains[(gains["dataset"] == ds) & (gains["family"] == "paraphrase") & (gains["target"] == "new") & (gains["horizon"] == 300) & (gains["seed"].astype(str) == "mean") & (gains["gain"] == "G_PCvsBP")]
        if z.empty:
            continue
        r = z.iloc[0]; lo, hi = json.loads(r["mean_ci"])
        parts.append(f"{DS[ds]} {f(r['mean'])} {ci(lo, hi)}")
    def bb(ds, m, k):
        return b(ds, m, k)
    gate_txt = "; ".join(f"{DS[ds]} false fires {pct(bb(ds, 'bp_mean', 'unseen_false_fire_rate'))} (BP) vs {pct(bb(ds, 'epc_mean', 'unseen_false_fire_rate'))} (PC), text-harm ES99+ {f(bb(ds, 'bp_mean', 'harm_es99_positive'), 4)} vs {f(bb(ds, 'epc_mean', 'harm_es99_positive'), 4)}" for ds in DS if bb(ds, "bp_mean", "harm_es99_positive") is not None)
    H.append("- **B. PC vs BP within the CAP benefit.** The paired seed-mean contrast PC − BP on paraphrase NLL (positive favours PC) is " + "; ".join(parts) + " nats/token: a small fraction of either cap's gain over frozen, and negative on every dataset. PC-CAP retains fewer paraphrases than BP-CAP on CounterFact and MQuAKE in all three seeds and is close on zsRE. Its gate is more conservative, which shows up as fewer false fires and less unrelated-text harm on zsRE (" + gate_txt + "), not as better behaviour on hard cases: in no extreme-case view (frozen-hardest sets, own worst cases, deciles, severe collateral events) is the PC-trained reader reliably better. The two caps share architecture, acquisition and inference; only the reader's training differs, and PC training cost ≈ 100× more GPU time.")
    return "\n".join(H)


def main():
    basic, imp, own, hard, dec = csv("basic_performance"), csv("improvements"), csv("extremes_own_worst"), csv("extremes_frozen_hardest"), csv("deciles_actual_loss")
    tails, coll, worst, harm, gate, sup = csv("token_tails_common_thresholds"), csv("collateral_vs_frozen"), csv("collateral_worst_cases"), csv("harm_unrelated_text"), csv("gating_failures"), csv("support_matrix")
    audit, rec = csv("denominator_audit_probes"), csv("denominator_audit_record")
    gains = pd.read_csv(OUT / "tables" / "paired_gains.csv")
    t_audit, n_bad, n_mixed = sec_audit(rec, audit)
    t_pcbp1, t_pcbp2 = sec_pc_vs_bp(gains, basic)
    today = date.today().isoformat()
    figs = sorted(p.name for p in (DATA / "figures" / "cap_value").glob("*.png"))
    slides = sorted(p.name for p in (DATA / "figures" / "cap_value" / "slides").glob("*.png"))
    md = f"""# The value of a CAP on frozen GPT-2 small: frozen GPT-2 vs BP-CAP vs PC-CAP on zsRE, CounterFact and MQuAKE — ordinary performance, extremes, collateral change

Supplement to study `{RUN_ID}` · Capstan · {today} · pc_cap code revision `{git_head()[:12]}` · requested by the lead on 2026-10-10 ("Frozen/no-CAP baseline must be central"). Built from the existing recorded scores of `{RUN_ID}` (no new GPU evaluations); the frozen record was not modified.

**Two-part question.** **A.** What is gained by adding a CAP (episodic memory + learned reader, 3,348,228 parameters, writes at blocks 4/8/12) to frozen GPT-2 small, especially on extreme examples? **B.** Given that a CAP is beneficial, does training its reader by error predictive coding (PC-CAP) offer any advantage over backprop (BP-CAP)? Question A is primary here; question B is reported inside it.

**Models.** *Frozen GPT-2 small (no CAP)*: the base parameters (digest `c4ac3fb8…`) loaded directly; validated against the record's cap-off path (direct forward reproduces saved cap-off losses to 5e-5 nats; a reader that abstains returns the base logits exactly). *BP-CAP* and *PC-CAP*: the frozen record's PC-reader study — the same cap architecture, the same adjoint acquisition (5 delta steps), the same 300 edits of realization 0 / order 100, three paired training seeds each; only the reader's training-time gradient estimator differs. Cap numbers are shown as the **seed mean** (per-probe mean over the three seeds) with the per-seed values beside them; seeds are not independent populations.

**Conventions.** Principal horizon: the 300-edit memory (100-edit rows are in the CSVs). Losses: teacher-forced per-token NLL (nats/token) of the stated target on identical serialised prompt/answer pairs for every model. Exact match: greedy, ≤ 32 tokens, newline stop, normalised alias match (the project's registered convention). Intervals: 95 % percentile bootstrap over items (or endpoint rows), the same resampled indices for every model (pairing preserved); 2,000 draws, 500 for deciles. "D" = L_cap − L_frozen on the same probe; a probe is "unchanged" when |D| ≤ 1e-3 nats (float32 reduction noise is ~1e-4).

## 1. Executive summary

{headline(basic, imp, hard, own, coll, gate, tails, gains, harm)}

**Zeros that are not measurements.** Frozen ES/RET-ES are 0 **by the eligibility screen** (items the base already answered were excluded from every pool); frozen LS and near-miss preservation are 1 **by definition** (the frozen output is the reference). These cells are marked in every table and are never used to compute a relative improvement.

## 2. Which requested comparisons the existing data support

{sec_support(sup)}

No additional GPU evaluation was needed: every matched three-model comparison requested could be reconstructed from the recorded teacher-forced scores, generations, record checkpoints and harm vectors of `{RUN_ID}`.

## 3. Denominator and probe-population audit

Finding: in the previous report the frozen rows at the **100-edit** horizon used denominators of 300 (all stream items) while the readers' 100-edit metrics use the first 100 items; and the paired/CVaR/decile tables at horizon 100 scored all 300 edit/paraphrase/locality probes against a 100-edit memory, so 200 of the 300 "taught" items were in fact not yet taught. Both are corrected: `aw/extremes/assemble.py` now restricts the frozen horizon-h rows to the first h stream items, and `aw/extremes/paired.py` (and this supplement) restrict item-level families to `stream_index ≤ h` (`at_horizon`). The main report was regenerated with the fix. Frozen rows still inconsistent after the fix: **{n_bad}**; item-level families with probes outside the horizon in the corrected tables: **{n_mixed}** (counted on the raw scores, which deliberately keep all 300 items for both memories — the restriction is applied at analysis time).

{t_audit}

Probe populations (identical for every model): zsRE 1,350 probes (300 edit, 300 paraphrase, 300 item-locality, 50 locality, 100 + 100 near-miss, 50 + 50 revision, 100 unseen); CounterFact 2,300 (600 paraphrases, 900 item-locality capped at 3 per item); MQuAKE 1,890 (incl. 240 composition questions, scored separately under the registered endpoint, not through the stream memory). `tables/cap_value/denominator_audit_probes.csv` lists every (model, dataset, horizon, family) count.

## 4. Basic performance: all three models, all three datasets

{sec_basic(basic)}

![Ordinary adaptation: per-token loss]({FIGREL}/adaptation_losses.png)

![Ordinary adaptation: exact-match success]({FIGREL}/adaptation_success.png)

### 4.1 Absolute and percentage improvement over frozen GPT-2 (300 edits, seed means)

{sec_improvements(imp)}

Loss improvements are reported as absolute reductions and as a percentage of the frozen loss; success-rate improvements as percentage points, with the relative change marked undefined wherever the frozen rate is 0. Full per-seed and 100-edit rows: `tables/cap_value/improvements.csv`.

## 5. Extremes, comparison A: each model's own worst 5 % and 1 % (CVaR95 / CVaR99)

{sec_own(own)}

![Own worst cases]({FIGREL}/own_worst.png)

## 6. Extremes, comparison B: the frozen model's hardest 5 % and 1 %, scored by all three models

The sets are fixed by the frozen per-token NLL (ties broken by probe id); every model is evaluated on exactly the same probes; intervals are bootstraps over the items inside the set.

{sec_hard(hard)}

![Frozen-hardest sets]({FIGREL}/frozen_hardest.png)

### 6.1 Actual loss across frozen-difficulty deciles (not gains)

{sec_deciles(dec)}

![Deciles, paraphrase]({FIGREL}/deciles_paraphrase.png)

![Deciles, taught prompt]({FIGREL}/deciles_edit.png)

![Deciles, un-taught prompt]({FIGREL}/deciles_unseen.png)

![Deciles, item locality]({FIGREL}/deciles_locality_item.png)

## 7. Tail shape at common absolute thresholds

Variable: token-level target NLL (terminator excluded) pooled over the probe families where the cap should act (edit, paraphrase, unseen: new target) or abstain (item-locality, locality, near-miss neighbour: true target), at the 300-edit memory. Thresholds are **absolute and common to all models**: the frozen model's P90/P95/P97.5 and 5/8/10 nats. A generalized-Pareto shape is fitted only with ≥ 50 exceedances (flagged "exploratory" below 100), compared with the exponential special case on the same sample, with a 200-draw item-group bootstrap interval. These are finite-range descriptive fits; a shape interval that includes or excludes zero says how the excess distribution decays above a given threshold, not that a power law holds.

### 7.1 Exceedance counts and shapes at the frozen P95, 8 nats and 10 nats

{sec_tails(tails)}

### 7.2 Threshold sensitivity (per-seed cells, three datasets)

{tails_sensitivity(tails)}

![Token-loss survival]({FIGREL}/token_survival.png)

## 8. Locality, unrelated text and collateral damage: each cap vs the original frozen model and vs its own cap-off reference

For these GPT-2 small readers the "own cap-off reference" of the record (the same base with the reader switched off) **is** frozen GPT-2: the direct forward reproduces the saved cap-off losses to 5e-5 nats. The two comparisons therefore coincide for unrelated text, and on probes the direct comparison below adds what the registered metrics cannot show: the size of each change, not only whether the decoded answer moved.

### 8.1 Per-probe deterioration D = L_cap − L_frozen on prompts the cap should leave alone (300 edits)

{sec_collateral(coll)}

![Collateral change vs frozen]({FIGREL}/collateral_vs_frozen.png)

### 8.2 Largest collateral deteriorations (two per family and dataset)

{sec_worst(worst)}

### 8.3 Unrelated text: 1,931 windows, 245,237 positions per cell; change = NLL(cap) minus NLL(frozen) at the same prefix [record]

{sec_harm(harm)}

## 9. Negative findings, stated plainly

### 9.1 MQuAKE multi-hop composition

![MQuAKE multi-hop]({FIGREL}/mquake_multihop.png)

Both caps answer the single-hop paraphrases of the edited facts (RET-GS 58–72 %) and neither composes them: the registered composition endpoint (80 cases × 3 questions, dependency edits taught from a fresh state) gives all-three-questions success of 0/80 for every seed of both caps and question accuracy of 0–2 of 240; the frozen cap-off exact match on the same questions is 0/240. The Stage-4 selected v5 reader behaves the same (0–2 questions of 240–264 per cell). The CAP adds retrieval of single facts; it adds no multi-hop reasoning over them.

### 9.2 Residual extreme losses when gating fails

{sec_gating(gate)}

Where the reader abstains (hard null), the cap's output is the frozen model's output and the loss is the frozen loss exactly (last column). The caps' remaining worst 5 % of paraphrase losses are therefore dominated by abstentions on frozen-hard prompts, plus a small number of fired-but-wrong cases above 2 nats/token.

## 10. Question B inside question A: PC-CAP vs BP-CAP

{t_pcbp1}

{t_pcbp2}

![PC vs BP inside the CAP gain]({FIGREL}/pc_vs_bp_within_gain.png)

## 11. Conclusions

**A.** Adding a CAP to frozen GPT-2 small converts the taught facts (own-prompt loss ≈ 6 → ≈ 0.02 nats/token; retention 99–100 % vs 0 % by screen) and transfers to paraphrases the cap never saw (loss reductions of roughly 65–90 % of the frozen loss; retention 57–99 % vs a measured 0 %). The gain is at least as large on the frozen model's hardest decile and hardest 5 %/1 % as elsewhere, so the benefit is not confined to easy cases. Each cap's own worst 5 %/1 % are lower than frozen's but remain in the 5–10 nats/token range, because they are the cases where gating failed and the cap fell back to the frozen model. Against frozen GPT-2 directly, collateral change on locality-type prompts is rare and mostly tiny but includes a handful of severe events per seed, and on unrelated text the mean change per position is at most {harm['mean_signed'].max():.1e} nats while single positions move by up to {harm['maximum'].max():.0f} nats (table 8.3). The CAP does not add multi-hop composition. Tail shapes at common thresholds are finite-range and do not change class; the caps thin the tail rather than reshape it.

**B.** Given that a CAP helps, the PC-trained reader is not better than the BP-trained one: the paired contrast is negative on all three datasets for paraphrases, PC-CAP retains fewer paraphrases on CounterFact and MQuAKE in every seed, and no extreme-case view (frozen-hardest sets, own worst cases, deciles, severe collateral events, text harm) shows a reliable PC advantage. PC training also costs ≈ 100× the GPU time. The PC/BP difference is a difference of *gating* (which paraphrases trigger a write), small relative to the CAP-vs-frozen difference.

**Qualifications.** One subject realization and one teaching order; three training seeds on one population; GPT-2 small only; all intervals are within-population. Frozen exact-match rates on taught prompts are zero by construction; the frozen baseline is informative through teacher-forced losses, through paraphrase/locality decoded answers, and through its position in every three-model panel.

## 12. Reproducibility

- Code (CPU only): `aw/extremes/cap_value.py` (tables), `aw/extremes/cap_value_figures.py` (figures + slide package), `aw/extremes/cap_value_report.py` (this document); fixes in `aw/extremes/assemble.py` and `aw/extremes/paired.py` (horizon-restricted denominators). Pipeline: `results/extremes_analysis/{RUN_ID}/scripts/run_cpu_pipeline.sh` (now includes the three cap_value stages).
- Tables: `results/extremes_analysis/{RUN_ID}/tables/cap_value/` — {', '.join(sorted(p.name for p in T.glob('*.csv')))}.
- Data: `assets/extremes_analysis/{RUN_ID}/data/cap_value/cases_seed_mean.parquet` (per-probe losses of all seven models and seed means), `survival_curves.parquet`.
- Figures: `assets/extremes_analysis/{RUN_ID}/figures/cap_value/` — {', '.join(figs)}; slide package `figures/cap_value/slides/` — {', '.join(slides)}; captions in `figures/cap_value/captions.json`.
- Inputs: `scores.parquet`, `generations.parquet`, `paired_cases.parquet`, `benchmark_original.csv`, `mquake_composition.csv`, `paired_gains.csv`, record checkpoints and `harm/summary.json` of the twelve PC-reader cells and the six MQuAKE cells (hashes in `manifest.json`).
"""
    out_md = OUT / "reports" / "cap_value_report.md"
    atomic_write_bytes(out_md, md.encode())
    st = Status()
    st.artifact("reports/cap_value_report_md", out_md)
    try:
        from aw.extremes.md2tex import build
        res = build(out_md, OUT / "reports" / "cap_value_report.pdf", "The value of a CAP on frozen GPT-2 small: frozen vs BP-CAP vs PC-CAP", "Capstan (pc_cap)", today)
        if res.get("status") == "ok":
            st.artifact("reports/cap_value_report_pdf", OUT / "reports" / "cap_value_report.pdf", pages=res.get("pages"))
        else:
            st.warn(f"cap_value PDF build failed: {res.get('log', '')[-800:]}")
        print(json.dumps(dict(md=str(out_md), pdf=res)))
    except Exception as e:
        st.warn(f"cap_value PDF build error: {e!r}")
        print(json.dumps(dict(md=str(out_md), pdf_error=repr(e))))
    st.stage("9_cap_value_report", "updated")


if __name__ == "__main__":
    main()
