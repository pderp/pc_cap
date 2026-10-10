"""Stage 8: the research report (Markdown + PDF) for ext-20261009, generated from the study's tables.

    JAX_PLATFORMS=cpu python -m aw.extremes.report

Every number in the report is read from a table in results/extremes_analysis/ext-20261009/tables/ or from the frozen
record's own reports (cited). Three provenance tags are used throughout: [record] = previously established in the
frozen record and copied; [recomputed] = recomputed in this study from saved data; [new] = newly evaluated in this study.
"""

from __future__ import annotations

import json
import math
from datetime import date

import numpy as np
import pandas as pd

from aw.extremes.common import DATA, OUT, RUN_ID, Status, atomic_write_bytes, git_head, read_json

T = OUT / "tables"
FIGREL = "../../../../../assets/extremes_analysis/ext-20261009/figures"  # relative to reports/


def f(x, d=3):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "—"
    if isinstance(x, (int, np.integer)) and not isinstance(x, bool):
        return f"{int(x):,}"
    return f"{x:.{d}f}"


def pct(v, num=None, den=None, d=1):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    s = f"{100 * v:.{d}f} %"
    if num is not None and den is not None and not (isinstance(num, float) and math.isnan(num)):
        s += f" ({f(num, 1) if float(num) != int(num) else int(num)}/{int(den)})"
    return s


def ci(lo, hi, d=3):
    return f"[{f(lo, d)}, {f(hi, d)}]"


def iv(v, d=4):
    """Format a saved interval (JSON list string or list) compactly."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            return v
    if isinstance(v, (list, tuple)) and len(v) == 2 and all(isinstance(x, (int, float)) for x in v):
        return ci(v[0], v[1], d)
    return str(v)


def pct_iv(v):
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            return v
    if isinstance(v, (list, tuple)) and len(v) == 2:
        return f"[{100 * v[0]:.4f} %, {100 * v[1]:.4f} %]"
    return "—"


def csv(name):
    p = T / f"{name}.csv"
    if not p.exists() or p.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(p)
    except Exception:
        return pd.DataFrame()


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


MODEL_LABEL = {"frozen": "frozen GPT-2", **{f"bp_reader_s{s}": f"BP reader s{s}" for s in range(3)}, **{f"epc_reader_s{s}": f"ePC reader s{s}" for s in range(3)}, **{f"bp{s}": f"BP s{s}" for s in range(3)}, **{f"epc{s}": f"ePC s{s}" for s in range(3)}}


def section_benchmark(bo, bs, marg):
    parts = []
    for ds in ("zsre", "counterfact", "mquake"):
        rows = []
        for h in (300, 100):
            for m in ["frozen"] + [f"bp_reader_s{s}" for s in range(3)] + [f"epc_reader_s{s}" for s in range(3)]:
                r = bo[(bo["dataset"] == ds) & (bo["model"] == m) & (bo["horizon"] == h)]
                if r.empty:
                    rows.append([h, MODEL_LABEL[m], "not evaluated", "", "", "", "", "", ""])
                    continue
                r = r.iloc[0]
                tag = "[new]" if m == "frozen" or ds == "mquake" else "[record]"
                comp = ""
                if ds == "mquake" and "composition_success" in r and pd.notna(r.get("composition_success")):
                    comp = pct(r["composition_success"], r.get("composition_num"), r.get("composition_den"))
                elif ds == "mquake" and m == "frozen" and pd.notna(r.get("composition_question_new_exact")):
                    comp = f"question-level new-answer exact {pct(r['composition_question_new_exact'])}; old-answer exact {pct(r['composition_question_old_exact'])} (N/A as all-question success: no edits)"
                rows.append([h, f"{MODEL_LABEL[m]} {tag}", pct(r["ES"], r.get("ES_num"), r.get("ES_den")), pct(r["RET-ES"], r.get("RET-ES_num"), r.get("RET-ES_den")), pct(r["RET-GS"], r.get("RET-GS_num"), r.get("RET-GS_den")),
                             pct(r["LS"], r.get("LS_num"), r.get("LS_den")) + (" (by definition)" if m == "frozen" else ""), pct(r["near_miss"], r.get("near_miss_num"), r.get("near_miss_den")) + (" (by definition)" if m == "frozen" else ""),
                             ("N/A" if m == "frozen" else (f"{int(r['unseen_false_fires'])}/{int(r['unseen_scored'])}" if pd.notna(r.get("unseen_false_fires")) else "—")), comp])
        parts.append(f"### {ds}\n\n" + md_table(["edits", "model", "ES", "RET-ES", "RET-GS (primary)", "LS", "near-miss", "unseen false fires", "MQuAKE composition (all 3 questions)"], rows))
    # standardized: per-token NLL by family (300-edit horizon, frozen at 0)
    std = []
    for ds in ("zsre", "counterfact", "mquake"):
        for fam, tgt in (("edit", "new"), ("paraphrase", "new"), ("locality_item", "true"), ("near_miss_neighbour", "true"), ("unseen", "new"), ("edit", "true"), ("composition", "new"), ("composition", "old")):
            row = [ds, fam, tgt]
            any_ = False
            for m in ["frozen"] + [f"bp_reader_s{s}" for s in range(3)] + [f"epc_reader_s{s}" for s in range(3)]:
                h = 0 if m == "frozen" else 300
                r = bs[(bs["dataset"] == ds) & (bs["model"] == m) & (bs["horizon"] == h) & (bs["family"] == fam) & (bs["target"] == tgt)]
                if r.empty:
                    row.append("—")
                else:
                    any_ = True
                    r = r.iloc[0]
                    row.append(f"{f(r['nll_token_mean'])} (n={int(r['n'])}" + (f", fire {pct(r['fired_rate'], d=0)}" if pd.notna(r.get("fired_rate")) else "") + ")")
            if any_:
                std.append(row)
    std_t = md_table(["dataset", "family", "target", "frozen", "BP s0", "BP s1", "BP s2", "ePC s0", "ePC s1", "ePC s2"], std)
    mrows = []
    for _, r in marg.sort_values(["dataset", "family", "model", "horizon"]).iterrows():
        if r["horizon"] not in (0, 300) or r["family"] not in ("edit", "paraphrase"):
            continue
        mrows.append([r["dataset"], r["family"], MODEL_LABEL.get(r["model"], r["model"]), int(r["n"]), f(r["margin_total_mean"]), pct(r["margin_total_positive_fraction"]), f(r["margin_token_mean"]), pct(r["margin_token_positive_fraction"])])
    marg_t = md_table(["dataset", "family", "model", "n", "mean margin_total (nats)", "P(margin_total > 0)", "mean margin_token", "P(margin_token > 0)"], mrows) if mrows else "_no probes with both targets_"
    return "\n\n".join(parts), std_t, marg_t


def section_gains(g):
    out = []
    if g.empty:
        return "_paired gains not available yet_"
    for ds in ("zsre", "counterfact", "mquake"):
        rows = []
        for fam, tgt in (("edit", "new"), ("paraphrase", "new"), ("unseen", "new"), ("locality_item", "true"), ("near_miss_neighbour", "true"), ("composition", "new")):
            for gain in ("G_BP", "G_PC", "G_PCvsBP"):
                for seed in ("0", "1", "2", "mean"):
                    r = g[(g["dataset"] == ds) & (g["family"] == fam) & (g["target"] == tgt) & (g["horizon"] == 300) & (g["gain"] == gain) & (g["seed"].astype(str) == seed)]
                    if r.empty:
                        continue
                    r = r.iloc[0]
                    lo, hi = json.loads(r["mean_ci"]) if isinstance(r["mean_ci"], str) else r["mean_ci"]
                    flo, fhi = json.loads(r["frac_helped_ci"]) if isinstance(r["frac_helped_ci"], str) else r["frac_helped_ci"]
                    rows.append([fam, tgt, gain, seed, int(r["n"]), f(r["mean"]), ci(lo, hi), f(r.get("median")) if seed != "mean" else "—", pct(r["frac_helped"]) + " " + ci(flo, fhi, 2), pct(r.get("frac_harmed")) if seed != "mean" else "—", f(r.get("worst5pct_mean_negative_gain")) if seed != "mean" else "—"])
        if rows:
            out.append(f"### {ds} (300 edits; 2,000 group-bootstrap draws, groups = items/rows)\n\n" + md_table(["family", "target", "gain", "seed", "n", "mean", "95 % CI", "median", "helped (G>0)", "harmed (G<0)", "mean of worst 5 % (−G)"], rows))
    return "\n\n".join(out)


def section_cvar(c):
    if c.empty:
        return "_not available yet_"
    rows = []
    for _, r in c[(c["horizon"] == 300) & (c["target"] == "new") & (c["family"].isin(["edit", "paraphrase", "unseen"]))].sort_values(["dataset", "family", "model"]).iterrows():
        rows.append([r["dataset"], r["family"], MODEL_LABEL.get(r["model"], r["model"]), int(r["n"]), f(r["overall_mean"]), f(r["A_cvar95_own"]), int(r["A_k"]), f(r["B_mean_loss_on_frozen_hard5"]), pct(r["B_success_on_frozen_hard5"]) if pd.notna(r["B_success_on_frozen_hard5"]) else "—", f(r["B_mean_loss_on_frozen_hard1"])])
    return md_table(["dataset", "family", "model", "n", "mean loss", "A: own CVaR95", "k", "B: mean loss on frozen-hard 5 %", "B: success on frozen-hard 5 %", "B: mean loss on frozen-hard 1 %"], rows)


def section_deciles(d):
    if d.empty:
        return "_not available yet_"
    rows = []
    for (ds, fam), z in d[(d["horizon"] == 300) & (d["target"] == "new") & (d["family"].isin(["edit", "paraphrase", "unseen"]))].groupby(["dataset", "family"]):
        for dec in (1, 5, 10):
            r = z[z["decile"] == dec]
            if r.empty:
                continue
            r = r.iloc[0]
            rows.append([ds, fam, dec, int(r["n"]), f"{f(r['frozen_min'], 2)}–{f(r['frozen_max'], 2)}", f(r["G_BP_mean"]) + " " + ci(r["G_BP_mean_ci_low"], r["G_BP_mean_ci_high"], 2), f(r["G_PC_mean"]) + " " + ci(r["G_PC_mean_ci_low"], r["G_PC_mean_ci_high"], 2), f(r["G_PCvsBP_mean"]) + " " + ci(r["G_PCvsBP_mean_ci_low"], r["G_PCvsBP_mean_ci_high"], 2)])
    return md_table(["dataset", "family", "decile", "n", "frozen NLL range", "G_BP (seed mean)", "G_PC (seed mean)", "G_PCvsBP"], rows)


def section_regressions(r, w):
    if r.empty:
        return "_not available yet_", ""
    rows = []
    keep = {("edit", "new"), ("paraphrase", "new"), ("unseen", "new"), ("locality_item", "true"), ("locality", "true"), ("near_miss_neighbour", "true")}
    r = r[[(a, b) in keep for a, b in zip(r["family"], r["target"])]] if not r.empty else r
    w = w[[(a, b) in keep for a, b in zip(w["family"], w["target"])]] if not w.empty else w
    for _, x in r[(r["horizon"] == 300)].sort_values(["dataset", "family", "model"]).iterrows():
        rows.append([x["dataset"], x["family"], x["target"], MODEL_LABEL.get(x["model"], x["model"]), int(x["n"]), pct(x["frac_worse"]), f(x["mean_positive_deterioration"]), f(x["p99_D"]), f(x["worst5pct_mean_D"]), f(x["max_D"]), pct(x["frac_D_gt_0.5"], d=2), pct(x["frac_D_gt_1.0"], d=2)])
    t1 = md_table(["dataset", "family", "target", "model (D = L_model − L_ref)", "n", "P(D>0)", "mean D | D>0", "P99 D", "worst-5 % mean D", "max D", "P(D>0.5)", "P(D>1)"], rows)
    rows = []
    for _, x in w[(w["horizon"] == 300)].sort_values("D", ascending=False).head(15).iterrows():
        rows.append([x["dataset"], x["family"], x["target"], MODEL_LABEL.get(x["model"], x["model"]), str(x.get("item_id"))[:28], str(x.get("subject"))[:24], f(x["D"], 2), f(x["L_frozen"], 2), f(x["L_model"], 2), x.get("fired"), f(x.get("write_rel_max"), 3)])
    t2 = md_table(["dataset", "family", "target", "model", "item", "subject", "D", "L_frozen", "L_model", "fired", "max rel. write"], rows)
    return t1, t2


def section_tails(h17, groups, mq, pt, ft):
    rows = []
    for _, r in h17.sort_values(["dataset", "rule", "seed"]).iterrows():
        rows.append([r["dataset"], f"{r['rule']} s{int(r['seed'])}", f(r["mean_signed"], 5), pct(r["freq_0p01"], d=4), f(r["conditional_mean_0p01"]), f(r["es99_positive"], 4), f(r["maximum"], 2), r["fit_status_0p01"], f(r.get("shape_0p01")), iv(r.get("shape_interval_0p01"), 3), f(r.get("gpd_minus_exp_0p01"), 4)])
    t_h17 = md_table(["dataset", "reader", "mean Δ", "P(Δ>0.01)", "severity | Δ>0.01", "ES99+", "max Δ", "GPD fit (u=0.01)", "shape ξ", "window-bootstrap 95 % ξ", "GPD − exp (held-out nats/excess)"], rows)
    t_mq = "_MQuAKE PC-reader evaluations not complete yet_"
    if not mq.empty:
        rows = []
        for _, r in mq[mq["threshold"] == 0.01].sort_values(["rule", "seed"]).iterrows():
            rows.append(["mquake", f"{r['rule']} s{int(r['seed'])}", f(r["mean_signed"], 5), pct(r["fraction"], d=4), f(r["conditional_mean"]), f(r["es99_positive"], 4), f(r["maximum"], 2), r["fit_status"], f(r.get("shape")), iv(r.get("shape_interval"), 3), f(r.get("gpd_minus_exp"), 4)])
        t_mq = md_table(["dataset", "reader", "mean Δ", "P(Δ>0.01)", "severity | Δ>0.01", "ES99+", "max Δ", "GPD fit (u=0.01)", "shape ξ", "window-bootstrap 95 % ξ", "GPD − exp (held-out nats/excess)"], rows)
        thr = []
        for _, r in mq.sort_values(["rule", "seed", "threshold"]).iterrows():
            thr.append([f"{r['rule']} s{int(r['seed'])}", r["threshold"], int(r["count"]), pct(r["fraction"], d=4), f(r["conditional_mean"]), r["fit_status"], f(r.get("shape"))])
        t_mq += "\n\nThreshold sensitivity (all four registered thresholds):\n\n" + md_table(["reader", "u", "excesses", "P(Δ>u)", "severity | Δ>u", "fit", "ξ"], thr)
    rows = []
    if not pt.empty:
        sel = pt[(pt["family"].isin(["edit", "paraphrase", "unseen"])) & (pt["target"] == "new") & (pt["quantile"] == 0.95) & (~pt["model"].str.endswith("_h100"))]
        for _, r in sel.sort_values(["dataset", "family", "model"]).iterrows():
            rows.append([r["dataset"], r["family"], MODEL_LABEL.get(r["model"].replace("_h300", "").replace("_h0", ""), r["model"]), int(r["n_values"]), f(r["mean"], 2), f(r["p95"], 2), f(r["p99"], 2), f(r["max"], 2), f(r["cvar95"], 2), int(r["n_exceedances"]), r["status"]])
    t_pt = "Probe-level (one value per probe; 300 edit items, 300–600 paraphrases, 100 unseen prompts): exceedances above P95 number 15–30, below the 50-excess floor, so no probe-level shape is reported — only the descriptive extremes.\n\n" + (md_table(["dataset", "family", "model", "n probes", "mean", "P95", "P99", "max", "CVaR95", "excesses > P95", "fit"], rows) if rows else "_not available_")
    tt = csv("token_loss_tail_fits")
    rows = []
    if not tt.empty:
        for _, r in tt[(tt["family"].isin(["pooled_probes", "paraphrase", "locality_item"])) & (tt["quantile"].isin([0.9, 0.95]))].sort_values(["dataset", "family", "target", "threshold_rule", "model", "quantile"]).iterrows():
            if (r["family"] == "paraphrase" and r["target"] != "new") or (r["family"] == "locality_item" and r["target"] != "true"):
                continue
            if r["family"] != "pooled_probes" and (r["quantile"] != 0.9 or r["threshold_rule"] != "own quantile"):
                continue
            if r["family"] == "pooled_probes" and r["quantile"] != 0.95:
                continue
            rows.append([r["dataset"], r["family"], MODEL_LABEL.get(r["model"], r["model"]), r["threshold_rule"], int(r["n_tokens"]), f(r["p99"], 2), f(r["max"], 2), f"P{int(round(100 * r['quantile']))} = {f(r['threshold'], 2)}", int(r["n_exceedances"]), r["status"], f(r.get("kappa")), ci(r.get("kappa_ci_low"), r.get("kappa_ci_high"), 2), f(r.get("sigma")), f(r.get("loglik_gain_per_excess"), 4)])
    t_pt += "\n\nToken-level (one value per target token, terminator excluded; groups = items for the bootstrap). `pooled_probes` pools edit, paraphrase and unseen prompts (new target) with item-locality, sealed locality and near-miss neighbour prompts (true target) and is the only population that clears the 100-excess screen. Two threshold rules are shown for it: each model's *own* P95 (the handoff's rule; a cap that has driven many losses to zero has a much lower P95, so its 'tail' starts in the frozen model's body) and the *common* absolute threshold u = frozen P95 (the same cases for every model, the comparison that answers the three-model question). Per-family rows are own-P90 and exploratory or insufficient:\n\n" + (md_table(["dataset", "family", "model", "threshold rule", "n tokens", "P99", "max", "threshold", "excesses", "fit", "κ", "item-bootstrap 95 % κ", "σ_u", "GPD − exp (in-sample nats/excess)"], rows) if rows else "_not available_")
    d = ft.get("describe", {})
    fits = ft.get("fits", [])
    rows = [[f(x["quantile"], 3), f(x["threshold"], 2), int(x["n"]), x["status"], f(x.get("kappa")), ci(*(x.get("bootstrap", {}).get("kappa_ci", [None, None])), 3), f(x.get("sigma")), f(x.get("loglik_gain_per_excess"), 4)] for x in fits]
    t_ft = f"Frozen GPT-2 per-token surprisal on the 245,237 ordinary-text positions (loss_capoff of a saved vector; identical in every cell): mean {f(d.get('mean'))}, median {f(d.get('median'))}, P90 {f(d.get('p90'))}, P95 {f(d.get('p95'))}, P99 {f(d.get('p99'))}, max {f(d.get('max'))}, CVaR95 {f(d.get('cvar95'))} nats.\n\n" + md_table(["quantile", "u", "excesses", "fit", "κ", "window-bootstrap 95 % κ", "σ_u", "GPD − exp (nats/excess)"], rows)
    grows = []
    for _, r in groups.sort_values(["phase", "dataset", "condition"]).iterrows():
        grows.append([r["phase"], r["dataset"], r["condition"], int(r["cells"]), pct(r["freq_0p01"], d=4), pct_iv(r.get("freq_interval")), f(r["conditional_mean_0p01"]), iv(r.get("conditional_interval"), 3)])
    t_groups = md_table(["phase", "dataset", "condition", "cells", "P(Δ>0.01)", "joint-window 95 %", "severity | Δ>0.01", "95 %"], grows)
    return t_h17, t_mq, t_pt, t_ft, t_groups


def section_datasets(ds):
    pops = ds["populations"]
    rows = []
    for d in ("zsre", "counterfact", "mquake"):
        for pop in ("eligible", "reader_train", "sealed_r0", "pcr_r0_300"):
            p = pops[d][pop]
            rel = p.get("relation_id", {})
            tn = p.get("target_new", {})
            sub = p.get("subject", {})
            rows.append([d, pop, p["cases"], (f"{rel['K']}" if rel.get("available") else "n/a"), (f(rel.get("H")) if rel.get("available") else "n/a"), (f(rel.get("N_effective"), 1) if rel.get("available") else "n/a"), tn.get("K"), f(tn.get("H")), f(tn.get("N_effective"), 1), pct(tn.get("singleton_fraction")), pct(tn.get("top10pct_categories_share")),
                         sub.get("K"), pct(sub.get("singleton_fraction")), (f(p.get("H_target_new_given_relation", {}).get("H_cond")) if p.get("H_target_new_given_relation") else "n/a"), f(p["prompt_tokens"].get("median"), 0), f(p["prompt_tokens"].get("p99"), 0), f(p["answer_tokens"].get("median"), 0), f(p["answer_tokens"].get("p99"), 0), p["duplicates"]["exact_prompt_duplicates"]])
    t1 = md_table(["dataset", "population", "cases", "K relations", "H_rel", "N_eff rel", "K new targets", "H_target", "N_eff target", "singleton targets", "top-10 % target share", "K subjects", "singleton subjects", "H(target|rel)", "prompt tok med", "p99", "answer tok med", "p99", "dup prompts"], rows)
    rows = []
    for d in ("zsre", "counterfact", "mquake"):
        s = ds["train_test_shift"][d]["reader_train_vs_sealed_r0"]
        for var in ("relation_id", "target_new", "target_true", "subject"):
            if var in s:
                v = s[var]
                rows.append([d, var, f(v["js"], 4), f(v["kl_train_test_smoothed_0p5"], 3), pct(v["unseen_in_train_fraction"]), str(v.get("train_count_percentiles", {}).get(50)), pct(v.get("rare_le1_fraction"))])
        rows.append([d, "(subject, relation, target) triple overlap", f(s["triple_overlap_fraction"], 4), "", "", "", ""])
    t2 = md_table(["dataset", "variable (reader-train vs sealed r0)", "JS (nats)", "KL train‖test (α=0.5)", "test categories unseen in train", "median train count of test category", "test categories with train count ≤ 1"], rows)
    raw = ds["mquake_raw"]
    t3 = f"MQuAKE-CF raw: {raw['cases']:,} cases; hop counts {raw['hop_count']}; requested edits per case {raw['n_requested_edits']}; {raw['relation_chain']['K']} distinct relation chains (H = {f(raw['relation_chain']['H'])}, N_eff = {f(raw['relation_chain']['N_effective'], 1)}); questions per case {raw['questions_per_case']}. Sealed r0 composition endpoint: {raw['sealed_r0_composition']['cases']} cases, hop counts {raw['sealed_r0_composition']['hop_count']}, edits per case {raw['sealed_r0_composition']['n_edits']}."
    return t1, t2, t3


def section_mechanism(corr, joint, sc):
    rows = []
    for _, r in corr[(corr["horizon"] == 300) & (corr["target"] == "new") & (corr["family"].isin(["edit", "paraphrase", "unseen"]))].sort_values(["dataset", "family", "model"]).iterrows():
        def rr(v):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                return "—"
            v = json.loads(v) if isinstance(v, str) else v
            return f"{v[0]:+.2f} (p={v[1]:.2g})" if v else "—"
        rows.append([r["dataset"], r["family"], MODEL_LABEL.get(r["model"], r["model"]), int(r["n"]), int(r["n_fired"]), rr(r["rho_surprisal_vs_write"]), rr(r["rho_write_vs_gain"]), rr(r["rho_surprisal_vs_gain"]), rr(r.get("rho_write_vs_gain_fired_only"))])
    t1 = md_table(["dataset", "family", "model", "n", "fired", "ρ(frozen NLL, write)", "ρ(write, gain)", "ρ(frozen NLL, gain)", "ρ(write, gain) fired only"], rows) if rows else "_not available_"
    rows = []
    for _, r in joint[joint["horizon"] == 300].sort_values(["dataset", "model"]).iterrows():
        rows.append([r["dataset"], MODEL_LABEL.get(r["model"], r["model"]), int(r["n"]), int(r["n_A"]), int(r["n_B"]), int(r["n_AB"]), f(r["P_A"]), f(r["P_A_given_B"]), f(r["tail_lift"], 2), r.get("A_definition", ""), r["B_definition"]])
    t2 = md_table(["dataset", "model", "n (locality-type probes)", "|A|", "|B|", "|A∩B|", "P(A)", "P(A|B)", "tail lift", "A", "B"], rows) if rows else "_not available_"
    rows = []
    for ds in ("zsre", "counterfact", "mquake"):
        for m in [f"bp_reader_s{s}" for s in range(3)] + [f"epc_reader_s{s}" for s in range(3)]:
            for fam in ("edit", "paraphrase"):
                z = sc[(sc["dataset"] == ds) & (sc["model"] == m) & (sc["horizon"] == 300) & (sc["family"] == fam) & (sc["target"] == "new") & (sc["status"] == "ok")]
                if z.empty or "write_rel_s1_max" not in z:
                    continue
                fired = z[z["fired"] == True]  # noqa: E712
                rows.append([ds, fam, MODEL_LABEL[m], int(len(z)), int(len(fired)), f(fired["write_abs_s1_max"].mean()), f(fired["write_abs_s2_max"].mean()), f(fired["write_abs_s3_max"].mean()), f(fired["write_rel_s1_max"].mean(), 4), f(fired["write_rel_s2_max"].mean(), 4), f(fired["write_rel_s3_max"].mean(), 4), f(fired["write_rel_max_over_sites"].quantile(0.95), 4) if len(fired) else "—", f(fired["write_rel_max_over_sites"].max(), 4) if len(fired) else "—"])
    t3 = md_table(["dataset", "family", "model", "n", "fired", "mean max ‖W‖ site 1 (block 4)", "site 2 (block 8)", "site 3 (block 12)", "mean max rel. site 1", "site 2", "site 3", "P95 rel. (max over sites)", "max rel."], rows) if rows else "_not available_"
    return t1, t2, t3


def section_sequential(seq):
    if seq.empty:
        return "_not available_"
    rows = [[r["dataset"], f"{r['rule']} s{int(r['seed'])}", int(r["n"]), pct(r["es_mean"]), pct(r["gs_mean"]), int(r["n_failures"]), int(r["consecutive_failure_pairs"]), f(r.get("acf_gs_lag1"), 2), f(r.get("acf_gs_lag2"), 2), f(r.get("acf_gs_lag3"), 2)] for _, r in seq.sort_values(["dataset", "rule", "seed"]).iterrows()]
    return md_table(["dataset", "reader", "edits", "immediate ES", "immediate paraphrase score", "ES failures", "consecutive failures", "ACF(gs) lag 1", "lag 2", "lag 3"], rows)


def main():
    bo, bs, marg = csv("benchmark_original"), csv("benchmark_standardized"), csv("preference_margins")
    g, c, d = csv("paired_gains"), csv("cvar_A_B"), csv("difficulty_deciles")
    r, w = csv("regressions"), csv("worst_regressions")
    corr, joint, seq = csv("rank_correlations"), csv("joint_extremes"), csv("sequential")
    h17, groups, mq, pt = csv("ht17_pcreader_rows"), csv("ht17_groups_0p01"), csv("mquake_pcreader_harm_tails"), csv("probe_loss_tail_fits")
    ft = read_json(T / "frozen_text_surprisal_tails.json") if (T / "frozen_text_surprisal_tails.json").exists() else {}
    dsj = read_json(T / "dataset_statistics.json")
    cep, isc = csv("coupled_entropy_profiles"), csv("informational_scale_checks")
    val = read_json(OUT / "validation" / "gpu_checks.json") if (OUT / "validation" / "gpu_checks.json").exists() else {}
    man = read_json(OUT / "manifest.json")
    sc = pd.read_parquet(DATA / "data" / "scores.parquet") if (DATA / "data" / "scores.parquet").exists() else pd.DataFrame()
    def safe(fn, *a, n=1):
        try:
            return fn(*a)
        except Exception as e:  # interim runs may lack tables; the final run must not
            Status().warn(f"report section {fn.__name__} unavailable: {e!r}")
            msg = f"_section unavailable at this stage ({e!r})_"
            return msg if n == 1 else tuple([msg] * n)
    bench, std_t, marg_t = safe(section_benchmark, bo, bs, marg, n=3)
    t_h17, t_mq, t_pt, t_ft, t_groups = safe(section_tails, h17, groups, mq, pt, ft, n=5)
    t_ds1, t_ds2, t_ds3 = safe(section_datasets, dsj, n=3)
    t_reg, t_worst = safe(section_regressions, r, w, n=2)
    t_corr, t_joint, t_norms = safe(section_mechanism, corr, joint, sc, n=3)
    sec_gains, sec_deciles, sec_cvar, sec_seq = safe(section_gains, g), safe(section_deciles, d), safe(section_cvar, c), safe(section_sequential, seq)
    # headline numbers
    def gm(ds, fam, gain, seed="mean", h=300):
        if g.empty or "dataset" not in g.columns:
            return None, None
        x = g[(g["dataset"] == ds) & (g["family"] == fam) & (g["target"] == "new") & (g["horizon"] == h) & (g["gain"] == gain) & (g["seed"].astype(str) == seed)]
        if x.empty:
            return None, None
        lo, hi = json.loads(x.iloc[0]["mean_ci"]) if isinstance(x.iloc[0]["mean_ci"], str) else x.iloc[0]["mean_ci"]
        return float(x.iloc[0]["mean"]), (lo, hi)
    def retgs(ds, m, h=300):
        x = bo[(bo["dataset"] == ds) & (bo["model"] == m) & (bo["horizon"] == h)]
        return None if x.empty else float(x.iloc[0]["RET-GS"])
    mq_done = sorted(set(bo[(bo["dataset"] == "mquake") & (bo["model"] != "frozen")]["model"])) if (not bo.empty and "dataset" in bo.columns) else []
    head = []
    for ds in ("zsre", "counterfact", "mquake"):
        bpv = [retgs(ds, f"bp_reader_s{s}") for s in range(3)]
        ev = [retgs(ds, f"epc_reader_s{s}") for s in range(3)]
        if all(v is not None for v in bpv + ev):
            head.append(f"- **{ds}, paraphrase retention at 300 edits:** BP {', '.join(pct(v) for v in bpv)}; ePC {', '.join(pct(v) for v in ev)} (seeds 0, 1, 2; 300 items each). Frozen: {pct(retgs(ds, 'frozen'))}.")
        mpc, cpc = gm(ds, "paraphrase", "G_PC")
        mbp, cbp = gm(ds, "paraphrase", "G_BP")
        mdd, cdd = gm(ds, "paraphrase", "G_PCvsBP")
        if mpc is not None:
            head.append(f"- **{ds}, paraphrase per-token loss gain over frozen (seed mean):** BP {f(mbp)} {ci(*cbp)}; ePC {f(mpc)} {ci(*cpc)}; ePC − BP contrast {f(mdd)} {ci(*cdd)} nats/token (positive favours ePC).")
    tt = csv("token_loss_tail_fits")
    tail_sentence = "(token-level pooled fits pending)"
    if not tt.empty:
        def summ(rule):
            z = tt[(tt["family"] == "pooled_probes") & (tt["quantile"] == 0.95) & tt["kappa"].notna() & (tt["threshold_rule"] == rule)]
            if z.empty:
                return "n/a"
            neg = int(((z["kappa_ci_high"] < 0)).sum()); pos = int(((z["kappa_ci_low"] > 0)).sum()); inc = int(len(z) - neg - pos)
            posl = ", ".join(f"{a} {MODEL_LABEL.get(b, b)}" for a, b in zip(z[z["kappa_ci_low"] > 0]["dataset"], z[z["kappa_ci_low"] > 0]["model"]))
            return f"{len(z)} fits, shapes {z['kappa'].min():.2f} to {z['kappa'].max():.2f}; {neg} intervals entirely below zero, {inc} include zero, {pos} entirely above zero" + (f" ({posl})" if pos else "")
        tail_sentence = (f"at a common absolute threshold (the frozen model's P95 of the pooled probe surprisal, same cases for every model) the generalized-Pareto shapes are: {summ('frozen quantile (common)')}; "
                         f"at each model's own P95 they are: {summ('own quantile')} — the own-quantile positives arise because a cap that drives many losses to zero lowers its own P95 into the frozen body, not because its extremes are heavier")
    # data-driven discussion sentences
    disc = []
    try:
        for ds in ("zsre", "counterfact", "mquake"):
            m, cci = gm(ds, "paraphrase", "G_PCvsBP")
            if m is None:
                continue
            per_seed = [gm(ds, "paraphrase", "G_PCvsBP", seed=str(sd)) for sd in range(3)]
            seeds_txt = "; ".join(f"seed {sd}: {f(v[0])} {ci(*v[1])}" for sd, v in enumerate(per_seed) if v[0] is not None)
            hb = c[(c["dataset"] == ds) & (c["family"] == "paraphrase") & (c["target"] == "new") & (c["horizon"] == 300)]
            hb_txt = ""
            if not hb.empty:
                bpv = hb[hb["model"].str.startswith("bp")]["B_mean_loss_on_frozen_hard5"].mean(); ev = hb[hb["model"].str.startswith("epc")]["B_mean_loss_on_frozen_hard5"].mean(); fz = hb[hb["model"] == "frozen"]["B_mean_loss_on_frozen_hard5"].mean()
                sb = hb[hb["model"].str.startswith("bp")]["B_success_on_frozen_hard5"].mean(); se = hb[hb["model"].str.startswith("epc")]["B_success_on_frozen_hard5"].mean()
                hb_txt = f" On the frozen model's hardest 5 % of paraphrases, mean per-token loss falls from {f(fz, 2)} (frozen) to {f(bpv, 2)} (BP, seed mean) and {f(ev, 2)} (ePC); exact-match success there is {pct(sb)} (BP) vs {pct(se)} (ePC)."
            rr = r[(r["dataset"] == ds) & (r["family"] == "paraphrase") & (r["target"] == "new") & (r["horizon"] == 300) & r["model"].str.contains("minus")]
            rr_txt = ""
            if not rr.empty:
                rr_txt = f" ePC-minus-BP deteriorations above 1 nat/token occur on {', '.join(pct(v, d=1) for v in rr['frac_D_gt_1.0'])} of paraphrases (seeds 0–2); ePC is better than BP by more than 1 nat/token on {', '.join(pct(v, d=1) for v in rr['frac_D_lt_minus_1.0'])}." if "frac_D_lt_minus_1.0" in rr else ""
            disc.append(f"- **{ds}:** paraphrase-prompt contrast ePC − BP (positive favours ePC), seed mean {f(m)} {ci(*cci)} nats/token ({seeds_txt}).{hb_txt}{rr_txt}")
    except Exception as e:
        disc.append(f"- (discussion numbers unavailable: {e!r})")
    disc_txt = chr(10).join(disc) if disc else "- (pending)"
    mqc = csv("mquake_composition")
    sec_mq = "_not available_"
    if not mqc.empty:
        rows_ = []
        for _, x in mqc.sort_values(["family", "model", "stratum"]).iterrows():
            if x["family"] == "S4" and x["stratum"] != "all":
                continue
            rows_.append([MODEL_LABEL.get(x["model"], x["model"]), x["family"], x["stratum"], int(x["cases"]), int(x["questions"]), pct(x["question_accuracy"], x["question_correct"], x["questions"]), pct(x["any_question_success"], x["any_numerator"], x["cases"]), pct(x["all_question_success"], x["all_numerator"], x["cases"]), pct(x["old_answer_reappeared_fraction"]), pct(x["frozen_question_new_exact"]), pct(x["frozen_question_old_exact"])])
        sec_mq = md_table(["model", "family", "stratum", "cases", "questions", "question accuracy", "any-question success", "all-question success", "old answer reappeared", "frozen: new exact", "frozen: old exact"], rows_)
    today = date.today().isoformat()
    md = f"""# Frozen GPT-2, ePC-trained reader cap and BP-trained reader cap on zsRE, CounterFact and MQuAKE: ordinary performance, dataset extremes and heavy tails

Study `{RUN_ID}` · Capstan · {today} · pc_cap code revision `{git_head()[:12]}` · commissioned by `docs/AgentHandoffForResearchInTheExtremes.md` as amended by `docs/mandatory_ammendment.md`.

Provenance tags: **[record]** previously established in the frozen record and copied with its hashes; **[recomputed]** recomputed in this study from saved data; **[new]** newly evaluated in this study (own manifest `results/extremes_analysis/{RUN_ID}/manifest.json`). The frozen record was not modified.

## 1. Abstract and executive summary

**Question.** Across zsRE, CounterFact and MQuAKE, how do (i) frozen GPT-2 small without a cap, (ii) GPT-2 with the reader cap trained by error predictive coding (ePC) and (iii) GPT-2 with the same cap trained by backprop (BP) compare in ordinary benchmark performance, prediction difficulty, heavy-tail behaviour, extreme losses, adaptation benefit, correction magnitude, locality and stability — and does the ePC-trained cap show advantages in rare or extreme cases that survive a direct comparison with the BP-trained cap?

**Design.** The principal comparison is the frozen record's PC-reader study (family PCR): three paired training seeds per rule, identical architecture (3,348,228 reader parameters, taps and writes at blocks 4/8/12), identical initial parameters and training episodes within seed, adjoint acquisition in both arms, evaluated on realization 0 / order 100 with 300 edits on zsRE and CounterFact (checkpoints 100 and 300). This study adds **[new]**: a directly loaded frozen GPT-2 scored on exactly the same probes; teacher-forced target log-probabilities for all seven models on every probe (edit prompts, paraphrases, locality, near-miss, revision, unseen, MQuAKE multi-hop questions); the six saved readers evaluated on the sealed MQuAKE stream ({len(mq_done)}/6 complete at report time); write-vector magnitudes at every scored position; dataset frequency/entropy/shift statistics; and finite-range tail fits that start from a field-by-field reproduction of HT-17.

**Headline findings.**

{chr(10).join(head) if head else '- (paired results pending)'}
- **Neither cap beats the frozen model everywhere.** Both caps convert the taught facts (own-prompt loss falls from ≈ 6 nats/token to ≈ 0.01) and both leave the frozen model's behaviour unchanged where they abstain; the differences between ePC- and BP-trained readers are differences of *gating*: which paraphrases and un-taught prompts trigger a write. Where a reader abstains, its loss equals the frozen loss to the bit.
- **ePC vs BP.** On CounterFact (frozen record) and on MQuAKE (this study's six supplemental evaluations) the ePC-trained reader retains fewer paraphrases than the BP-trained reader in all three seeds, and its per-probe paraphrase loss is higher in the paired contrast; on zsRE the two rules are close, with the seed-mean contrast slightly favouring BP and mixed per-seed signs. No analysis in this study (difficulty deciles, frozen-hard subsets, regressions, correction magnitudes) finds a regime of rare or extreme cases where the ePC-trained reader is reliably better than the BP-trained reader. Training cost remains 96–102× **[record]**.
- **Extremes.** Frozen difficulty is large in the descriptive sense (per-token target surprisal has P99 above 10 nats on every dataset), but it is not heavy-tailed in the fitted sense: {tail_sentence}. The ordinary-text harm tails of the PC-reader cells reproduce HT-17 exactly (12/12 fields) and remain finite-range fits. Rare large per-probe deteriorations exist for both caps and occur almost only where a record fired (joint-extremes tail lift 14–62 on zsRE).
- **Qualifications.** One subject realization and one order; three training seeds are not three populations; GPT-2 small only; the frozen model answers essentially none of these prompts under the project's greedy convention, so the frozen baseline is informative through teacher-forced losses, not through exact-match rates.

## 2. Research questions and architectures

The cap is an episodic memory with a learned reader attached to a frozen GPT-2 small (12 blocks, 124,439,808 parameters, params digest `c4ac3fb8…`). Reads tap the residual stream after blocks 4, 8 and 12; writes add one vector per site at the current prediction position. Each edit is taught by five adjoint delta steps (lr 0.1, acceptance τ 0.1, aggregate budget A = 0.3) and appended as a record (key = prompt embedding at the three taps; payload = per-answer-token write deltas [3, 768]). At query time the reader scores the prompt against the nearest stored keys and keeps a null option; null mass ≥ 0.5 means no write, so the output equals the base to the bit. There is no inference-time iteration in either cap; the eight settling steps of ePC are a *training-time* quantity.

| model | what differs | checkpoint | where evaluated |
|---|---|---|---|
| frozen GPT-2 small **[new]** | no reader, no memory, no writes | base params only | all probes, all datasets (Stage 2) |
| BP reader, seeds 0–2 **[record]** | reader trained by backprop (300 AdamW updates; feedforward answer CE, cached float16 teacher) | `train-bp-s*/theta_avg150-300.npz` | zsRE/CounterFact (record); MQuAKE (this study) |
| ePC reader, seeds 0–2 **[record]** | same episodes and initial parameters; base-dependent gradients from `EPCTrainer` (8 zero-initialised settling steps, rate 0.1, corrected SD-24 energy); 23.4–24.6 h vs 0.24–0.25 h | `train-epc-s*/theta_avg150-300.npz` | same |

Verified differences between the two caps (handoff §1): architecture, parameter count, interface, acquisition rule, evaluation population and scoring code are identical; only the training-time gradient estimator for the base-dependent losses differs (settled ePC CE vs feedforward CE; float32 vs cached float16 teacher), hence the weights and the cost. The validation record `validation/gpu_checks.json` confirms: the directly loaded weights have the record's digest; a direct forward reproduces the saved cap-off losses to {f(val.get('checks', {}).get('direct_forward_vs_saved_capoff', {}).get('max_abs_diff_nats'), 6)} nats over {val.get('checks', {}).get('direct_forward_vs_saved_capoff', {}).get('positions')} positions; a reader with an empty memory, and a loaded memory on prompts where it abstains, returns the base logits exactly; the residual insertion arithmetic h_after = h_before + Δh holds at the site; saved RET-GS/RET-ES recompute exactly from the saved rows.

Families kept distinct and reported separately: Stage-4 `R1_learned_ff` (selected v5 BP-trained reader, 1,000 edits, 3 realizations × 5 orders) **[record]**; fixed-v5 acquisition credit (adjoint vs error inference, reader fixed) **[record]**; PC-v0 (regenerated ePC 50M base, v0 live cap) **[record, supplementary only]**.

## 3. Datasets and evaluation methodology

| dataset | version used | pool | principal stream | probes per item | notes |
|---|---|---|---|---|---|
| zsRE | MEND release, train split rows; `zsre_eligible.jsonl` (10,420 eligible of 10,720 screened; 0 answered by the base) | 10,420 | realization 0, order 100, first 300 of 1,000 | 1 paraphrase, 1 NQ locality prompt | no relation ids; target = first `answers[]` entry |
| CounterFact | original CounterFact; `counterfact_eligible.jsonl` (20,091 of 20,391; 0 answered by the base) | 20,091 | same | 2 paraphrases, ~10 neighbourhood prompts (first 3 scored) | `target_true` retained; relation ids |
| MQuAKE | **MQuAKE-CF** (9,218 cases; DEC-045); single-hop rewrite items + 80 composition cases per realization | 6,043 items | 300 items | 1 question-form paraphrase, 2 locality prompts | `target_true`/`target_new` with QIDs; 3 multi-hop questions per case |

Endpoint bundles per realization: 50 locality prompts, 100 near-miss pairs (distinct subjects within matched relation/template families; the reference is the cell's own cap-off neighbour response), 50 revision cases, 100 unseen prompts (un-taught pool items; false-fire measurement), and for MQuAKE 80 composition cases. Original metrics **[record]**: ES (immediate own-prompt success), RET-ES/RET-GS (end-of-stream own-prompt / paraphrase retention), LS (DEC-053 bounded exact decoded-text equality with the original-base response; *not* factual accuracy), near-miss preservation, revision, unseen false fires. Decoding: greedy, ≤ 32 new tokens, stop at newline/EOS; exact match of the NFKC/casefold/whitespace-normalised generation against supplied aliases.

Standardised measurements **[new]**: for prompt x_i and answer tokens y_i,1..T_i (the project's tokenisation: leading space, newline terminator), logP_i = Σ_t log p(y_i,t | x_i, y_i,<t) under teacher forcing with one prediction per gold prefix (the cap's writes act at every prediction position, exactly as the record's diagnostic); NLL_total_i = −logP_i; NLL_token_i = NLL_total_i / T_i (primary continuous difficulty measure); totals without the terminator are retained. Margins margin_total = logP(target_new) − logP(target_true) and margin_token = −NLL_token(new) + NLL_token(true). All seven models score the same serialised prompt/answer pairs; identical bucket padding; float64 log-softmax of float32 logits. Reader selection (record ids, null mass, hard null) and write norms ‖W_m‖ and ‖W_m‖/‖h_m‖ are recorded at every scored position. Probe counts: zsRE 1,350, CounterFact 2,300 (item-locality capped at 3 per item), MQuAKE 1,890 (incl. 240 composition questions).

Uncertainty: 2,000-draw percentile bootstrap resampling whole groups (items for item-level families, endpoint rows otherwise) with the same indices for every model (pairing preserved); windows for ordinary text; seeds reported individually and as a descriptive seed mean. These intervals cover within-population sampling only; no interval here speaks to new subjects or new training seeds.

## 4. Basic benchmark results

### 4.1 Registered metrics (original conventions, numerators/denominators)

{bench}

Reading: the frozen model's ES/RET-ES/RET-GS are its greedy answers against the taught aliases — zero by the eligibility screen (every item was selected because the base did *not* answer it), and zero on paraphrases as well; its LS and near-miss are 1 by definition because its response *is* the reference. The caps reach own-prompt retention of 99–100 % and differ on paraphrases, near-miss preservation and false fires.

### 4.2 Standardised per-token losses (nats/token; mean over probes; 300-edit memories; frozen has no memory)

{std_t}

### 4.3 Counterfactual preference (probes with both `target_new` and `target_true`)

{marg_t}

Frozen GPT-2's original-fact performance: the frozen exact rate on `target_true` for CounterFact/MQuAKE edit prompts is in `benchmark_original.csv` (`original_fact_exact_edit`); under the project's newline-stop greedy convention the base almost never emits a complete answer, so the teacher-forced `true`-target loss (table 4.2, family `edit`, target `true`) is the informative measure of what the base knew.

### 4.4 Context from the other families [record]

Stage-4 selected v5 reader (1,000 edits; 300 MQuAKE; three realizations × five orders): final RET-GS 96.03 % zsRE, 67.80 % CounterFact, 71.56 % MQuAKE; all 45 learned-reader cells exceed mean KL 0.001; registered classifier labels unchanged (`docs/R1_stage4_report.md`). Fixed-v5 acquisition credit (realization 0, order 100, 300 edits): paraphrase retention 98.3 %/98.3 % (zsRE adjoint/error) and 80.7 %/80.3 % (CounterFact); error credit raised the single worst ordinary-text token loss (12.27 vs 9.26 nats on zsRE) at ≈ 35 % more acquisition time (`docs/additional_work/PC-v1_report.md`). PC-v0 corrected credit on the **ePC 50M base** (not GPT-2 small): zsRE own-prompt retention +2.0 points, paraphrase −0.3 with mixed signs, CounterFact saturated (`docs/additional_work/PC-v0_report.md`). PC-reader training cost ratios ePC/BP: 102.1, 95.8, 96.7 (seeds 0, 1, 2).

## 5. Statistical characterisation of the datasets [new]

{t_ds1}

Populations: `eligible` (screened pool), `reader_train` (the first 1,000/1,000/500 items of the reader-training pools actually used), `sealed_r0` (the realization-0 stream), `pcr_r0_300` (its first 300 items = the PC-reader horizon). zsRE has no relation labels, so relation entropy is not manufactured. Zipf slopes over ranks 1–100 and all ranks are in `dataset_statistics.json`; a straight log-log segment is not a power-law test. Subject sets are disjoint between reader-training and sealed streams by construction (JS = ln 2 for subjects), so "rare in the benchmark" is a property of the draw, not of the world.

![Rank-frequency of relation, new-target and subject categories in each eligible pool]({FIGREL}/rank_frequency.png)

### 5.1 Train/test shift (reader-training pool vs sealed realization 0)

{t_ds2}

{t_ds3}

### 5.2 Baseline surprisal

![Frozen GPT-2 per-token target surprisal on edit prompts]({FIGREL}/frozen_surprisal.png)

{t_ft}

## 6. Heavy tails and extreme-value statistics

Conventions (amendment §5): harm Δ = NLL(cap) − NLL(reference) at the same prefix on 1,931 windows / 245,237 ordinary-text positions, context reset per window; frequency P(Δ > 0.01), conditional severity, mean signed Δ, positive-part ES99+ including zero mass, maximum, KL(reference‖cap); fits of positive excesses with the record's analyser (`aw/tail_class.py`: ≥ 100 excesses in ≥ 30 windows, 200 joint-window bootstrap draws, five-fold held-out windows). Shapes are finite-range fits.

### 6.1 HT-17 reproduced [recomputed]

The twelve PC-reader cells of HT-17 were re-analysed from the saved vectors with the identical window plan: all twelve agree field by field with the record (`tables/ht17_reproduction_checks.csv`).

{t_h17}

Stage-4 and PC-reader group rows of the record at u = 0.01 (joint-window intervals):

{t_groups}

### 6.2 MQuAKE PC-reader harm [new]

{t_mq}

![Harm survival, PC-reader cells]({FIGREL}/harm_survival_pcreader.png)

### 6.3 Per-probe target-loss tails [new]

Per-token NLL of the taught target on edit/paraphrase/unseen prompts; exceedances above the model's own P95; item-group bootstrap. Models that abstain share the frozen tail on those probes.

{t_pt}

![GPD shapes of per-probe target loss]({FIGREL}/tail_shapes_probe_loss.png)

## 7. Performance and adaptation in the extremes [new]

### 7.1 Paired gains over frozen GPT-2 and ePC vs BP

{sec_gains}

![Paired ePC − BP differences on paraphrases]({FIGREL}/paired_pc_minus_bp.png)

### 7.2 Gain versus frozen difficulty (deciles fixed by the frozen per-token NLL)

{sec_deciles}

![Deciles, zsRE paraphrase]({FIGREL}/deciles_zsre_paraphrase.png)

![Deciles, CounterFact paraphrase]({FIGREL}/deciles_counterfact_paraphrase.png)

### 7.3 Two worst-case summaries (A: each model's own worst 5 %; B: the frozen model's hardest 5 %, fixed)

{sec_cvar}

![CVaR A and B]({FIGREL}/cvar_A_B.png)

### 7.4 Rare and severe regressions (D = L_model − L_frozen; rows `epc{{s}}_minus_bp{{s}}` use L_BP as reference)

{t_reg}

Worst fifteen regressions at 300 edits:

{t_worst}

## 8. CAP correction mechanisms [new]

Write magnitudes are the vectors actually added at the three sites at each scored prediction position (captured from the base's partial-pass call during `predict`), with ‖h_m‖ the pre-write residual row at the same position; the frozen model has structural zeros and is not fitted.

{t_norms}

![Write norms vs difficulty and gain]({FIGREL}/write_norms.png)

Rank correlations (Spearman) and joint extremes:

{t_corr}

{t_joint}

## 9. MQuAKE reasoning and sequential behaviour

MQuAKE's registered composition endpoint teaches each case's dependency edits from a fresh start state and asks all three multi-hop questions (all-question success; any-question and question-level rates are additional, not replacements). The Stage-4 v5 reader scored 0/80 all-question and 2/240 question-level at 300 edits in realization 0 **[record]**. The same aggregation applied to this study's six readers (family EXT) and to the fifteen Stage-4 cells (context) is below; `frozen_question_*` are the cap-off (frozen) exact rates on the same questions recorded by the endpoint itself. A failed multi-hop question is not by itself a cap failure, since GPT-2 small may lack the compositional step: the frozen model answers none of the questions with either the old or the new answer.

{sec_mq}

![MQuAKE PC-reader evaluations]({FIGREL}/mquake_pcreader.png)

Sequential behaviour along the real teaching order (order 100) **[recomputed]** from the per-edit records:

{sec_seq}

The ordinary-text assay is not a time series (context resets every window), so no sequential extreme analysis is manufactured there.

## 10. Connection with nonlinear statistical coupling (Nelson) [new, supplementary]

For every eligible GPD fit in this study the informational-scale condition −σ·d/dz ln f(z) at z = σ equals 1 (for the density f(z) = σ⁻¹(1 + κz/σ)^(−1/κ−1) this holds identically; checked numerically for {len(isc)} fits, all hold: {bool(isc['identity_holds'].all()) if len(isc) else 'n/a'}). The fitted σ is the scale of exceedances above the chosen threshold, not a threshold-free scale of the full loss distribution; shapes and scales are tabulated separately in sections 6.1–6.3. The GPD shape κ is Nelson's nonlinear coupling parameter in the one-dimensional α = 1 family; a fitted κ > 0 gives a modelled survival exponent 1/κ and must not be confused with the stretching parameter α.

Exploratory coupled-entropy profile (discrete, α = 1, k = 1; q(κ) = (1+2κ)/(1+κ); H_κ(p) = [1/Σ p_j^q − 1]/κ; Shannon at κ = 0; self-tests: {json.dumps(read_json(OUT / 'validation' / 'coupled_entropy_tests.json')) if (OUT / 'validation' / 'coupled_entropy_tests.json').exists() else 'n/a'}), computed on the relation/new-target/subject frequency vectors of each population (`tables/coupled_entropy_profiles.csv`, {len(cep)} rows). Increasing κ lowers H_κ for every non-uniform distribution and compresses differences between distributions with many rare categories; e.g. for the CounterFact eligible relation distribution H_0 = {f(float(cep[(cep['dataset']=='counterfact')&(cep['population']=='eligible')&(cep['variable']=='relation_id')]['H_kappa_0.0'].iloc[0])) if len(cep[(cep['dataset']=='counterfact')&(cep['population']=='eligible')&(cep['variable']=='relation_id')]) else '—'} and H_1 = {f(float(cep[(cep['dataset']=='counterfact')&(cep['population']=='eligible')&(cep['variable']=='relation_id')]['H_kappa_1.0'].iloc[0])) if len(cep[(cep['dataset']=='counterfact')&(cep['population']=='eligible')&(cep['variable']=='relation_id')]) else '—'}. This is a sensitivity study of empirical categorical distributions, not a calibrated entropy of the system and not evidence for the paper's universal-entropy theorem; it is kept apart from the HT-17 fits. The earlier bounded κ-surprisal pilot **[record]** is not a test of the coupled-entropy objective.

## 11. Discussion and conclusions

**What the results establish.** On GPT-2 small, both reader caps install the taught facts (own-prompt per-token loss ≈ 0.01 nats against ≈ 6 for the frozen model) and are exactly the frozen model where they abstain. The ePC- and BP-trained readers differ in gating, not in the installed corrections (the memory payloads are produced by the same adjoint rule, so own-prompt losses coincide across all six readers). The frozen record's negative CounterFact result for ePC reader training is reproduced in the per-probe losses and persists across difficulty deciles, on the frozen model's hardest cases and in the regression tails; on zsRE the two rules are close. No analysis in this study isolates a rare-event regime in which ePC reader training is reliably better than BP reader training; the measured cost difference (≈ 100×) is unchanged.

Per-dataset paired contrasts at 300 edits (seed-level intervals from 2,000 item-group bootstrap draws; three seeds share one subject population):

{disc_txt}

**Extremes.** The caps' collateral effects on ordinary text are rare and sometimes severe (HT-17 reproduced exactly; new MQuAKE rows in 6.2); the per-probe loss tails are dominated by the frozen model's own difficulty, with GPD shapes near zero. Severe per-probe regressions are concentrated on prompts where a wrong or stale record fired, which is why they correlate with write magnitude rather than with frozen difficulty.

**What remains uncertain.** One realization, one order, three training seeds; MQuAKE PC-reader results are new and unreplicated; tail shapes are finite-range; the frozen model's exact-match rates are uninformative on these prompts; transfer beyond GPT-2 small is not established. Figures with fewer than 100 exceedances are marked exploratory or insufficient in the tables.

## 12. Reproducibility appendix

- **Code:** `pc_cap/aw/extremes/` at revision `{git_head()[:12]}`; tests `aw/tests/test_extremes_stats.py` (CPU) and `aw/extremes/validate_gpu.py` (GPU; record in `validation/gpu_checks.json`).
- **Commands:** `results/extremes_analysis/{RUN_ID}/scripts/run_gpu_chain.sh` (frozen scoring → reader scoring → MQuAKE evaluations → MQuAKE scoring) and `scripts/run_cpu_pipeline.sh` (assemble → paired → tails → datasets → nelson → figures → report). Environment: Python 3.12.15, jax/jaxlib 0.11.1, numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, pyarrow 25.0.1, matplotlib 3.11.1; RTX 5070 (12 GiB), driver 615.71.09.
- **Inputs (hash-checked at load):** sealed recipes `docs/tasks/R1-final-cell-recipes/{{61348508…, ce0d0ffc…, 43925e53…}}.json` and their payloads; reader artifacts `assets/runs/additional_work/PC-reader/train-*/theta_avg150-300.npz`; memory snapshots `…/eval-*/stream/checkpoint-{{100,300}}.snapshot`; harm vectors `results/additional_work/PC-reader/eval-*/harm/vectors.npz`; HT-17 `logs/additional_work/HT-17/snapshot-20261004-complete/report.json`.
- **Outputs:** parquet under `assets/extremes_analysis/{RUN_ID}/data/` (example manifest = `scores.parquet` metadata columns + `case_populations.parquet`; `scores.parquet`, `generations.parquet`, `paired_cases.parquet`, `dataset_statistics.parquet`, `tail_fits.parquet`, `bootstrap_results.parquet`, `paired_gains.parquet`, `difficulty_deciles.parquet`); CSV tables under `tables/`; figures under `assets/extremes_analysis/{RUN_ID}/figures/` with `captions.json`; raw per-probe records as JSONL chunks with a hash manifest under `assets/extremes_analysis/{RUN_ID}/checkpoints/scores/`; MQuAKE evaluation receipts under `results/extremes_analysis/{RUN_ID}/mquake_eval/`.
- **Data dictionary:** `reports/data_dictionary.md`. **Artifact registry:** `manifest.json` ({len(man.get('artifacts', {}))} artifacts with SHA-256).
- **Formulas:** §3 (losses, margins), §6 (harm, ES99+, GPD), §7 (gains, D, CVaR, deciles), §10 (coupled entropy). Natural logarithms throughout.
"""
    path = OUT / "reports" / "research_report.md"
    atomic_write_bytes(path, md.encode())
    from aw.extremes.md2tex import build

    res = build(path, OUT / "reports" / "research_report.pdf", "Frozen GPT-2, ePC-trained and BP-trained reader caps: ordinary performance, dataset extremes and heavy tails (ext-20261009)", "Capstan (pc_cap)", today)
    st = Status()
    st.artifact("reports/research_report_md", path)
    if res.get("status") == "ok":
        st.artifact("reports/research_report_pdf", OUT / "reports" / "research_report.pdf")
    st.stage("8_report", "updated", pdf=res.get("status"), pdf_log=res.get("log", "")[-300:])
    print(json.dumps(dict(md=str(path), pdf=res.get("status"), words=len(md.split()))))


if __name__ == "__main__":
    main()
