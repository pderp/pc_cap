"""Supplemental analysis for ext-20261009: the value of adding a CAP to frozen GPT-2 small (question A) and, within that
benefit, PC- versus BP-trained readers (question B). CPU only; no new evaluations.

    JAX_PLATFORMS=cpu python -m aw.extremes.cap_value

Three models appear in every comparison: frozen GPT-2 small (no cap), BP-CAP (BP-trained reader) and PC-CAP (ePC-trained
reader). The caps have three paired training seeds each; "seed mean" is the per-probe mean of the three seeds' losses (or
success indicators), and per-seed rows are kept. Losses are teacher-forced per-token NLL (nats/token) of the stated target;
the principal horizon is the 300-edit memory. Item-level families at the 100-edit horizon cover the first 100 stream items
only (denominator audit, 2026-10-10). Uncertainty: percentile bootstrap resampling whole groups (items, or endpoint rows),
same indices for every model.

Outputs: results/extremes_analysis/ext-20261009/tables/cap_value/*.csv and assets/.../data/cap_value/*.parquet.
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd

from aw.extremes import stats as S
from aw.extremes.common import DATA, OUT, Status, atomic_csv, atomic_json, atomic_parquet, read_json
from aw.extremes.models import eval_dir
from aw.extremes.paired import DRAWS, FAMILIES_ITEM, NOISE, SEED, SEEDS, at_horizon, group_key

T = OUT / "tables" / "cap_value"
DD = DATA / "data" / "cap_value"
DATASETS = ("zsre", "counterfact", "mquake")
RULES = {"bp": "BP-CAP", "epc": "PC-CAP"}
# the one target per family that the cap is supposed to help (new) or leave alone (true)
FAMILY_TARGET = {"edit": "new", "paraphrase": "new", "unseen": "new", "near_miss_edit": "new", "locality_item": "true", "locality": "true", "near_miss_neighbour": "true"}
ADAPT_FAMILIES = ("edit", "paraphrase")           # question A: what the cap should improve
COLLATERAL_FAMILIES = ("locality_item", "locality", "near_miss_neighbour", "unseen")  # what the cap should leave unchanged
SEVERE = (1.0, 2.0, 5.0)                           # nats/token deterioration thresholds for "severe events"
ABS_THRESHOLDS = (5.0, 8.0, 10.0)                  # common absolute token-loss thresholds (nats) for the tail comparison


def lcol(model, h):
    return "L_frozen_h0" if model == "frozen" else f"L_{model}_h{h}"


def model_columns(h):
    """Column names of per-probe losses: frozen, each seed of each rule."""
    d = {"frozen": lcol("frozen", h)}
    for rule in RULES:
        for s in SEEDS:
            d[f"{rule}_reader_s{s}"] = lcol(f"{rule}_reader_s{s}", h)
    return d


def add_seed_means(y: pd.DataFrame, h: int) -> pd.DataFrame:
    """Append per-probe seed-mean loss / success / fired columns for each rule (BP-CAP, PC-CAP)."""
    y = y.copy()
    for rule in RULES:
        Ls = [f"L_{rule}_reader_s{s}_h{h}" for s in SEEDS]
        Xs = [f"X_{rule}_reader_s{s}_h{h}" for s in SEEDS]
        Fs = [f"F_{rule}_reader_s{s}_h{h}" for s in SEEDS]
        y[f"L_{rule}_mean_h{h}"] = y[Ls].astype(float).mean(axis=1)
        if all(c in y.columns for c in Xs):
            y[f"X_{rule}_mean_h{h}"] = y[Xs].astype(float).mean(axis=1)
        if all(c in y.columns for c in Fs):
            y[f"F_{rule}_mean_h{h}"] = y[Fs].astype(float).mean(axis=1)
    return y


def display_models(h):
    """(key, label, loss column, success column, fired column) for the three models plus per-seed rows."""
    out = [("frozen", "Frozen GPT-2 (no cap)", "L_frozen_h0", "X_frozen_h0", None)]
    for rule, lab in RULES.items():
        out.append((f"{rule}_mean", f"{lab} (seed mean)", f"L_{rule}_mean_h{h}", f"X_{rule}_mean_h{h}", f"F_{rule}_mean_h{h}"))
    for rule, lab in RULES.items():
        for s in SEEDS:
            out.append((f"{rule}_reader_s{s}", f"{lab} seed {s}", f"L_{rule}_reader_s{s}_h{h}", f"X_{rule}_reader_s{s}_h{h}", f"F_{rule}_reader_s{s}_h{h}"))
    return out


def ready(x: pd.DataFrame, h: int):
    need = list(model_columns(h).values())
    if any(c not in x.columns for c in need):
        return None
    y = x.dropna(subset=need)
    return add_seed_means(y, h) if len(y) else None


# ------------------------------------------------------------------------------------------------ 1. denominator audit
def denominator_audit(scores: pd.DataFrame, gens: pd.DataFrame, bo: pd.DataFrame):
    rows = []
    ok = scores[scores["status"] == "ok"]
    for (ds, model, h), x in ok.groupby(["dataset", "model", "horizon"]):
        for fam, z in x.groupby("family"):
            items = z["item_id"].nunique()
            within = int((z["stream_index"] <= h).sum()) if (fam in FAMILIES_ITEM and h) else None
            rows.append(dict(dataset=ds, model=model, horizon=int(h), family=fam, probe_rows=int(len(z)), probes=int(z["probe_id"].nunique()), items=int(items), targets=",".join(sorted(z["target"].unique())),
                             probe_rows_within_horizon=within, item_level=(fam in FAMILIES_ITEM)))
    audit = pd.DataFrame(rows)
    # record denominators and the frozen rows as written in benchmark_original.csv (after the fix in assemble.py)
    rec = []
    for _, r in bo.iterrows():
        rec.append(dict(dataset=r["dataset"], model=r["model"], horizon=int(r["horizon"]), ES_den=r.get("ES_den"), RET_ES_den=r.get("RET-ES_den"), RET_GS_den=r.get("RET-GS_den"), LS_den=r.get("LS_den"), near_miss_den=r.get("near_miss_den"),
                        consistent_with_horizon=(bool(r.get("ES_den") == r["horizon"]) if pd.notna(r.get("ES_den")) else None)))
    return audit, pd.DataFrame(rec)


# ------------------------------------------------------------------------------------------- 2. basic performance table
def _record_metric(bo, ds, model, h, key):
    x = bo[(bo["dataset"] == ds) & (bo["model"] == model) & (bo["horizon"] == h)]
    if x.empty or key not in x.columns:
        return None, None, None
    r = x.iloc[0]
    return r[key], r.get(key + "_num"), r.get(key + "_den")


def basic_performance(pc: pd.DataFrame, gens: pd.DataFrame, bo: pd.DataFrame, mqc: pd.DataFrame, harm: pd.DataFrame):
    rows = []
    for ds in DATASETS:
        pcd = pc[pc["dataset"] == ds]
        for h in (300, 100):
            # per-probe losses for the adaptation and collateral families
            blocks = {}
            for fam in ("edit", "paraphrase", "locality_item", "locality", "near_miss_neighbour", "unseen"):
                tgt = FAMILY_TARGET[fam]
                x = at_horizon(pcd[(pcd["family"] == fam) & (pcd["target"] == tgt)], h)
                blocks[fam] = ready(x, h)
            true_block = None
            if ds in ("counterfact", "mquake"):
                true_block = ready(at_horizon(pcd[(pcd["family"] == "edit") & (pcd["target"] == "true")], h), h)
            for key, label, Lc, Xc, Fc in display_models(h):
                row = dict(dataset=ds, horizon=h, model=key, label=label)
                if key == "frozen":
                    g = gens[(gens["model"] == "frozen") & (gens["dataset"] == ds) & (gens["stream_index"].fillna(0) <= h)]
                    e = g[g["family"] == "edit"]["exact_new"]; p = g[g["family"] == "paraphrase"].groupby("item_id")["exact_new"].mean()
                    row.update(ES=float(e.mean()), ES_num=int(e.sum()), ES_den=int(len(e)), ES_flag="zero by eligibility screen (base did not answer any pool item)",
                               RET_ES=float(e.mean()), RET_ES_num=int(e.sum()), RET_ES_den=int(len(e)), RET_ES_flag="zero by eligibility screen",
                               RET_GS=float(p.mean()), RET_GS_num=float(p.sum()), RET_GS_den=int(len(p)), RET_GS_flag="measured zero (paraphrases were not screened; consistent with the screen)",
                               LS=1.0, LS_num=50, LS_den=50, LS_flag="1 by definition: the frozen response is the locality reference",
                               near_miss=1.0, near_miss_den=100, near_miss_flag="1 by definition", unseen_false_fire_rate=0.0, unseen_flag="no reader: cannot fire")
                    if ds == "mquake" and not mqc.empty:
                        z = mqc[(mqc["family"] == "EXT") & (mqc["stratum"] == "all")]
                        row.update(mh_question_accuracy=float(z["frozen_question_new_exact"].mean()), mh_any_case=None, mh_all_case=None, mh_questions=int(z["questions"].iloc[0]) if len(z) else None, mh_cases=int(z["cases"].iloc[0]) if len(z) else None,
                                   mh_flag="measured: cap-off (= frozen) exact match on the post-edit multi-hop answer, 240 questions; case-level any/all not separately recorded for the frozen path")
                elif key.endswith("_mean"):
                    rule = key[:-5]
                    def seedmean(metric):
                        vals = [_record_metric(bo, ds, f"{rule}_reader_s{s}", h, metric)[0] for s in SEEDS]
                        vals = [float(v) for v in vals if v is not None and not (isinstance(v, float) and math.isnan(v))]
                        return (float(np.mean(vals)), float(min(vals)), float(max(vals)), len(vals)) if vals else (None, None, None, 0)
                    for metric, name in (("ES", "ES"), ("RET-ES", "RET_ES"), ("RET-GS", "RET_GS"), ("LS", "LS"), ("near_miss", "near_miss"), ("unseen_false_fire_rate", "unseen_false_fire_rate")):
                        m, lo, hi, n = seedmean(metric)
                        row[name] = m; row[name + "_seed_min"] = lo; row[name + "_seed_max"] = hi
                    _, _, den = _record_metric(bo, ds, f"{rule}_reader_s0", h, "RET-GS"); row["RET_GS_den"] = den
                    _, _, den = _record_metric(bo, ds, f"{rule}_reader_s0", h, "ES"); row["ES_den"] = den; row["RET_ES_den"] = den
                    row["LS_den"] = 50; row["near_miss_den"] = 100
                    row["LS_flag"] = "record: decoded-text equality with the cap-off (= frozen) response on 50 locality prompts"
                    if ds == "mquake" and not mqc.empty and h == 300:
                        z = mqc[(mqc["family"] == "EXT") & (mqc["stratum"] == "all") & mqc["model"].str.startswith(rule)]
                        row.update(mh_question_accuracy=float(z["question_accuracy"].mean()), mh_any_case=float(z["any_question_success"].mean()), mh_all_case=float(z["all_question_success"].mean()), mh_questions=int(z["questions"].iloc[0]), mh_cases=int(z["cases"].iloc[0]),
                                   mh_flag="registered composition endpoint (80 cases x 3 questions), seed mean")
                else:
                    for metric, name in (("ES", "ES"), ("RET-ES", "RET_ES"), ("RET-GS", "RET_GS"), ("LS", "LS"), ("near_miss", "near_miss"), ("unseen_false_fire_rate", "unseen_false_fire_rate")):
                        v, num, den = _record_metric(bo, ds, key, h, metric)
                        row[name] = v; row[name + "_num"] = num; row[name + "_den"] = den
                    if ds == "mquake" and not mqc.empty and h == 300:
                        z = mqc[(mqc["family"] == "EXT") & (mqc["stratum"] == "all") & (mqc["model"] == key)]
                        if len(z):
                            row.update(mh_question_accuracy=float(z["question_accuracy"].iloc[0]), mh_any_case=float(z["any_question_success"].iloc[0]), mh_all_case=float(z["all_question_success"].iloc[0]), mh_questions=int(z["questions"].iloc[0]), mh_cases=int(z["cases"].iloc[0]))
                # teacher-forced losses (same probes for every model)
                for fam, blk in blocks.items():
                    if blk is None or Lc not in blk.columns:
                        continue
                    v = blk[Lc].to_numpy(float)
                    row[f"nll_{fam}"] = float(v.mean()); row[f"nll_{fam}_median"] = float(np.median(v)); row[f"nll_{fam}_n"] = int(len(v))
                    if Xc in blk.columns and blk[Xc].notna().any():
                        row[f"exact_{fam}"] = float(blk[Xc].astype(float).mean())
                    if key != "frozen":
                        D = v - blk["L_frozen_h0"].to_numpy(float)
                        row[f"D_{fam}_mean"] = float(D.mean()); row[f"D_{fam}_frac_worse"] = float((D > NOISE).mean()); row[f"D_{fam}_frac_better"] = float((D < -NOISE).mean()); row[f"D_{fam}_max"] = float(D.max())
                if true_block is not None and Lc in true_block.columns:
                    row["nll_edit_true_target"] = float(true_block[Lc].mean())
                # harm on unrelated text (record; reference = cap-off = frozen for these GPT-2 small readers)
                if key != "frozen" and not harm.empty and h == 300:
                    hz = harm[(harm["dataset"] == ds) & (harm["model"].isin([key] if not key.endswith("_mean") else [f"{key[:-5]}_reader_s{s}" for s in SEEDS]))]
                    if len(hz):
                        row.update(harm_mean_signed=float(hz["mean_signed"].mean()), harm_es99_positive=float(hz["es99_positive"].mean()), harm_max=float(hz["maximum"].max()), harm_frac_gt_0p01=float(hz["frac_gt_0.01"].mean()), harm_frac_gt_1=float(hz["frac_gt_1.0"].mean()), harm_positions=int(hz["positions"].iloc[0]))
                rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------------- 3. improvements
def improvements(basic: pd.DataFrame):
    rows = []
    for ds in DATASETS:
        for h in (300, 100):
            b = basic[(basic["dataset"] == ds) & (basic["horizon"] == h)].set_index("model")
            if "frozen" not in b.index:
                continue
            fz = b.loc["frozen"]
            for metric, kind in (("nll_edit", "loss"), ("nll_paraphrase", "loss"), ("nll_edit_true_target", "loss"), ("ES", "rate"), ("RET_ES", "rate"), ("RET_GS", "rate"), ("exact_paraphrase", "rate"), ("mh_question_accuracy", "rate"), ("nll_locality_item", "loss"), ("nll_unseen", "loss")):
                if metric not in b.columns or pd.isna(fz.get(metric)):
                    continue
                f0 = float(fz[metric])
                for rule, lab in RULES.items():
                    for key in [f"{rule}_mean"] + [f"{rule}_reader_s{s}" for s in SEEDS]:
                        if key not in b.index or pd.isna(b.loc[key].get(metric)):
                            continue
                        v = float(b.loc[key][metric])
                        if kind == "loss":
                            absd = f0 - v
                            pctd = (100.0 * absd / f0) if f0 > 0 else None
                            note = "loss reduction (nats/token); percentage of the frozen loss"
                        else:
                            absd = 100.0 * (v - f0)
                            pctd = (100.0 * (v - f0) / f0) if f0 > 0 else None
                            note = "percentage points; relative improvement undefined because the frozen rate is 0" if f0 == 0 else "percentage points; relative improvement vs frozen rate"
                        rows.append(dict(dataset=ds, horizon=h, metric=metric, kind=kind, model=key, label=b.loc[key]["label"], frozen=f0, model_value=v, absolute_improvement=absd, percent_improvement=pctd, note=note))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------- 4. extremes: own worst, frozen hardest
def _hard_sets(F: np.ndarray, probe_ids: np.ndarray):
    order = np.lexsort((probe_ids, -F))  # worst first, deterministic ties
    k5 = max(1, math.ceil(0.05 * len(F))); k1 = max(1, math.ceil(0.01 * len(F)))
    return order[:k5], order[:k1]


def extremes(pc: pd.DataFrame, h: int, draws: int = DRAWS):
    own, hard = [], []
    for ds in DATASETS:
        for fam in ("edit", "paraphrase", "unseen", "locality_item", "locality", "near_miss_neighbour"):
            tgt = FAMILY_TARGET[fam]
            x = at_horizon(pc[(pc["dataset"] == ds) & (pc["family"] == fam) & (pc["target"] == tgt)], h)
            y = ready(x, h)
            if y is None or len(y) < 20:
                continue
            groups = group_key(y)
            models = display_models(h)
            L = np.stack([y[c].to_numpy(float) for _, _, c, _, _ in models])  # [m, n]
            X = np.stack([(y[c].astype(float).to_numpy() if (c in y.columns and y[c].notna().any()) else np.full(len(y), np.nan)) for _, _, _, c, _ in models])
            # A: own worst 5 % / 1 % (CVaR95 / CVaR99), bootstrap over all groups
            def statA(idx):
                out = []
                for m in range(L.shape[0]):
                    v = L[m, idx]
                    out += [S.cvar(v, 0.95)["value"], S.cvar(v, 0.99)["value"], float(v.mean())]
                return np.array(out)
            bsA = S.grouped_bootstrap(statA, groups, draws=draws, seed=SEED)
            k5 = max(1, math.ceil(0.05 * len(y))); k1 = max(1, math.ceil(0.01 * len(y)))
            for m, (key, label, _, _, _) in enumerate(models):
                p = bsA["point"][3 * m: 3 * m + 3]; lo = bsA["ci_low"][3 * m: 3 * m + 3]; hi = bsA["ci_high"][3 * m: 3 * m + 3]
                own.append(dict(dataset=ds, family=fam, target=tgt, horizon=h, model=key, label=label, n=int(len(y)), n_groups=bsA["n_groups"], k5=k5, k1=k1,
                                mean=p[2], mean_ci_low=lo[2], mean_ci_high=hi[2], cvar95=p[0], cvar95_ci_low=lo[0], cvar95_ci_high=hi[0], cvar99=p[1], cvar99_ci_low=lo[1], cvar99_ci_high=hi[1],
                                p95=float(np.percentile(L[m], 95)), p99=float(np.percentile(L[m], 99)), max=float(L[m].max())))
            # B: the frozen model's hardest 5 % / 1 %, fixed; bootstrap within the fixed set (groups of the set)
            F = y["L_frozen_h0"].to_numpy(float)
            i5, i1 = _hard_sets(F, y["probe_id"].to_numpy())
            for tag, idx_set in (("hard5", i5), ("hard1", i1)):
                g_set = groups[idx_set]
                def statB(idx, idx_set=idx_set):
                    sel = idx_set[idx]
                    out = []
                    for m in range(L.shape[0]):
                        out += [float(L[m, sel].mean()), (float(np.nanmean(X[m, sel])) if np.isfinite(X[m, sel]).any() else np.nan)]
                    return np.array(out)
                bsB = S.grouped_bootstrap(statB, g_set, draws=draws, seed=SEED)
                for m, (key, label, _, _, _) in enumerate(models):
                    p = bsB["point"][2 * m: 2 * m + 2]; lo = bsB["ci_low"][2 * m: 2 * m + 2]; hi = bsB["ci_high"][2 * m: 2 * m + 2]
                    hard.append(dict(dataset=ds, family=fam, target=tgt, horizon=h, set=tag, model=key, label=label, n_total=int(len(y)), k=int(len(idx_set)), n_groups_in_set=bsB["n_groups"], frozen_threshold=float(F[idx_set].min()),
                                     mean_loss=p[0], mean_loss_ci_low=lo[0], mean_loss_ci_high=hi[0], success=(None if np.isnan(p[1]) else p[1]), success_ci_low=(None if np.isnan(lo[1]) else lo[1]), success_ci_high=(None if np.isnan(hi[1]) else hi[1]),
                                     max_loss=float(L[m, idx_set].max()), frac_below_1nat=float((L[m, idx_set] < 1.0).mean()), frac_still_above_frozen_median=float((L[m, idx_set] > np.median(F)).mean())))
    return pd.DataFrame(own), pd.DataFrame(hard)


# ------------------------------------------------------------------------------------------ 5. actual loss by decile
def deciles(pc: pd.DataFrame, h: int, draws: int = 500):
    rows = []
    for ds in DATASETS:
        for fam in ("edit", "paraphrase", "unseen", "locality_item"):
            tgt = FAMILY_TARGET[fam]
            y = ready(at_horizon(pc[(pc["dataset"] == ds) & (pc["family"] == fam) & (pc["target"] == tgt)], h), h)
            if y is None or len(y) < 50:
                continue
            F = y["L_frozen_h0"].to_numpy(float)
            order = np.lexsort((y["probe_id"].to_numpy(), F))
            rank = np.empty(len(y), int); rank[order] = np.arange(len(y))
            y = y.assign(decile=(rank * 10 // len(y)) + 1)
            models = display_models(h)
            for dec, z in y.groupby("decile"):
                groups = group_key(z)
                L = np.stack([z[c].to_numpy(float) for _, _, c, _, _ in models])
                bs = S.grouped_bootstrap(lambda idx: L[:, idx].mean(axis=1), groups, draws=draws, seed=SEED)
                for m, (key, label, _, Xc, _) in enumerate(models):
                    row = dict(dataset=ds, family=fam, target=tgt, horizon=h, decile=int(dec), n=int(len(z)), frozen_min=float(L[0].min()), frozen_max=float(L[0].max()), model=key, label=label,
                               mean_loss=float(bs["point"][m]), ci_low=float(bs["ci_low"][m]), ci_high=float(bs["ci_high"][m]), median_loss=float(np.median(L[m])))
                    if Xc in z.columns and z[Xc].notna().any():
                        row["success"] = float(z[Xc].astype(float).mean())
                    rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------- 6. tails at common thresholds
def token_tails(scores: pd.DataFrame, h: int = 300):
    """Token-level target surprisal (terminator excluded) pooled over the probe families; frozen vs each cap at the same
    absolute thresholds: the frozen P90/P95/P97.5 and fixed 5/8/10 nats. GPD fits only where >= 100 exceedances; the
    exponential special case is compared on the same sample. Per seed, and per rule with the three seeds pooled (flagged)."""
    ok = scores[(scores["status"] == "ok") & (scores["horizon"].isin([0, h]))]
    keep = [(f, t) in FAMILY_TARGET.items() for f, t in zip(ok["family"], ok["target"])]
    ok = ok[keep]
    ok = at_horizon(ok, h)
    rows, curves = [], []
    for ds in DATASETS:
        d = ok[ok["dataset"] == ds]
        series = {}
        for model, x in d.groupby("model"):
            vals, groups = [], []
            for pt, iid in zip(x["per_token_nll"], x["item_id"]):
                v = json.loads(pt)[:-1]
                vals += v; groups += [str(iid)] * len(v)
            series[model] = (np.asarray(vals, float), np.asarray(groups))
        for rule in RULES:
            parts = [series[f"{rule}_reader_s{s}"] for s in SEEDS if f"{rule}_reader_s{s}" in series]
            if len(parts) == 3:
                series[f"{rule}_pooled_seeds"] = (np.concatenate([p[0] for p in parts]), np.concatenate([p[1] for p in parts]))
        if "frozen" not in series:
            continue
        fz = series["frozen"][0]
        thresholds = [("frozen P90", float(np.quantile(fz, 0.90))), ("frozen P95", float(np.quantile(fz, 0.95))), ("frozen P97.5", float(np.quantile(fz, 0.975)))] + [(f"{u:g} nats", u) for u in ABS_THRESHOLDS]
        grid = np.geomspace(0.05, max(fz.max(), 1.0) * 1.05, 80)
        for model, (v, g) in series.items():
            curves.append(dict(dataset=ds, model=model, n_tokens=int(v.size), grid=json.dumps([float(t) for t in grid]), survival=json.dumps([float((v > t).mean()) for t in grid])))
            for name, u in thresholds:
                m = v > u
                z = v[m] - u
                fit = S.gpd_fit(z)
                row = dict(dataset=ds, horizon=h, model=model, pooled_seeds=model.endswith("_pooled_seeds"), threshold_name=name, threshold=u, n_tokens=int(v.size), n_items=int(len(np.unique(g))), n_exceed=int(m.sum()), frac_exceed=float(m.mean()),
                           mean_excess=(float(z.mean()) if z.size else None), p99_token_loss=float(np.percentile(v, 99)), max_token_loss=float(v.max()), fit_status=fit.get("status"), kappa=fit.get("kappa"), sigma=fit.get("sigma"),
                           loglik_gain_per_excess_vs_exponential=fit.get("loglik_gain_per_excess"))
                if fit.get("kappa") is not None:
                    b = S.gpd_bootstrap(z, g[m], draws=200, seed=3)
                    row["kappa_ci_low"], row["kappa_ci_high"] = b.get("kappa_ci", [None, None])
                    row["heavy_tail_supported"] = bool(row["kappa_ci_low"] is not None and row["kappa_ci_low"] > 0)
                rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(curves)


# ---------------------------------------------------------------------------------- 7. locality / collateral vs frozen
def harm_table():
    rows = []
    for ds in DATASETS:
        for rule in RULES:
            for s in SEEDS:
                p = eval_dir(rule, s, ds) / "harm" / "summary.json"
                if not p.exists():
                    continue
                j = read_json(p)
                summ = j["summary"]["capoff"]["loss"]
                rep = eval_dir(rule, s, ds) / "report.json"
                cdf = read_json(rep).get("changed_distribution_fraction") if rep.exists() else None
                rows.append(dict(dataset=ds, model=f"{rule}_reader_s{s}", rule=rule, seed=s, positions=summ["positions"], mean_signed=summ["mean_signed"], mean_positive=summ["mean_positive"], es99_positive=summ["es99_positive"], maximum=summ["maximum_signed"],
                                 **{f"count_gt_{k}": summ["exceedance"][k]["count"] for k in ("0.01", "0.1", "1.0")}, **{f"frac_gt_{k}": summ["exceedance"][k]["fraction"] for k in ("0.01", "0.1", "1.0")},
                                 changed_distribution_fraction=cdf, reference="cap-off = frozen GPT-2 (bit-identical when the reader abstains; direct forward reproduces saved cap-off losses to 5e-5 nats)", source=str(p)))
    return pd.DataFrame(rows)


def collateral(pc: pd.DataFrame, gens: pd.DataFrame, bo: pd.DataFrame, h: int):
    rows, worst = [], []
    fz_text = gens[gens["model"] == "frozen"].set_index(["dataset", "probe_id"])["text"]
    for ds in DATASETS:
        for fam in COLLATERAL_FAMILIES:
            tgt = FAMILY_TARGET[fam]
            y = ready(at_horizon(pc[(pc["dataset"] == ds) & (pc["family"] == fam) & (pc["target"] == tgt)], h), h)
            if y is None or len(y) < 10:
                continue
            F = y["L_frozen_h0"].to_numpy(float)
            groups = group_key(y)
            for key, label, Lc, Xc, Fc in display_models(h):
                if key == "frozen":
                    continue
                D = y[Lc].to_numpy(float) - F
                bs = S.grouped_bootstrap(lambda idx: np.array([D[idx].mean(), (D[idx] > NOISE).mean(), (D[idx] < -NOISE).mean()]), groups, draws=DRAWS, seed=SEED)
                row = dict(dataset=ds, family=fam, target=tgt, horizon=h, model=key, label=label, n=int(len(y)), reference="frozen GPT-2 (direct)",
                           mean_D=bs["point"][0], mean_D_ci_low=bs["ci_low"][0], mean_D_ci_high=bs["ci_high"][0], frac_worse=bs["point"][1], frac_worse_ci_low=bs["ci_low"][1], frac_worse_ci_high=bs["ci_high"][1],
                           frac_better=bs["point"][2], frac_better_ci_low=bs["ci_low"][2], frac_better_ci_high=bs["ci_high"][2], frac_unchanged=float((np.abs(D) <= NOISE).mean()),
                           mean_positive_D=(float(D[D > NOISE].mean()) if (D > NOISE).any() else 0.0), mean_negative_D=(float(D[D < -NOISE].mean()) if (D < -NOISE).any() else 0.0), p99_D=float(np.percentile(D, 99)), max_D=float(D.max()), min_D=float(D.min()), cvar95_D=S.cvar(D, 0.95)["value"],
                           **{f"n_D_gt_{t:g}": int((D > t).sum()) for t in SEVERE}, **{f"n_D_lt_minus_{t:g}": int((D < -t).sum()) for t in SEVERE})
                if Fc and Fc in y.columns:
                    row["fired_rate"] = float(y[Fc].astype(float).mean())
                # decoded-answer change vs frozen (generated families only)
                if fam in ("locality", "near_miss_neighbour", "unseen") and not key.endswith("_mean"):
                    g = gens[(gens["model"] == key) & (gens["dataset"] == ds) & (gens["horizon"] == h) & (gens["family"] == fam)]
                    if len(g):
                        ref = fz_text.reindex(list(zip(g["dataset"], g["probe_id"])))
                        row["answer_changed_vs_frozen"] = float((g["text"].to_numpy() != ref.to_numpy()).mean()); row["answers_compared"] = int(len(g))
                    # the record's own cap-off reference metric for the same family
                    rec_key = {"locality": "LS", "near_miss_neighbour": "near_miss", "unseen": "unseen_false_fire_rate"}[fam]
                    v, num, den = _record_metric(bo, ds, key, h, rec_key)
                    row["record_own_reference_metric"] = rec_key; row["record_own_reference_value"] = v
                rows.append(row)
                if not key.endswith("_mean"):
                    top = np.argsort(D)[::-1][:3]
                    for i in top:
                        if D[i] <= NOISE:
                            continue
                        r = y.iloc[i]
                        worst.append(dict(dataset=ds, family=fam, horizon=h, model=key, probe_id=r["probe_id"], item_id=r.get("item_id"), subject=r.get("subject"), D=float(D[i]), L_frozen=float(F[i]), L_model=float(y[Lc].iloc[i]), fired=r.get(Fc), write_rel_max=r.get("W_" + Lc[2:])))
    return pd.DataFrame(rows), pd.DataFrame(worst)


# ------------------------------------------------------------------------------------------ 8. gating failures
def gating(pc: pd.DataFrame, h: int):
    rows = []
    for ds in DATASETS:
        for fam in ADAPT_FAMILIES:
            y = ready(at_horizon(pc[(pc["dataset"] == ds) & (pc["family"] == fam) & (pc["target"] == "new")], h), h)
            if y is None:
                continue
            F = y["L_frozen_h0"].to_numpy(float)
            i5, _ = _hard_sets(F, y["probe_id"].to_numpy())
            hard = np.zeros(len(y), bool); hard[i5] = True
            for key, label, Lc, Xc, Fc in display_models(h):
                if key == "frozen" or key.endswith("_mean") or Fc not in y.columns:
                    continue
                L = y[Lc].to_numpy(float); fired = y[Fc].astype(bool).to_numpy()
                W = y.get("W_" + Lc[2:])
                ex = y[Xc].astype(float).to_numpy() if Xc in y.columns else np.full(len(y), np.nan)
                abst = ~fired
                rows.append(dict(dataset=ds, family=fam, horizon=h, model=key, label=label, n=int(len(y)), n_fired=int(fired.sum()), n_abstained=int(abst.sum()), abstain_rate=float(abst.mean()),
                                 loss_abstained_mean=(float(L[abst].mean()) if abst.any() else None), loss_abstained_cvar95=(S.cvar(L[abst], 0.95)["value"] if abst.any() else None), loss_abstained_max=(float(L[abst].max()) if abst.any() else None),
                                 loss_fired_mean=(float(L[fired].mean()) if fired.any() else None), loss_fired_cvar95=(S.cvar(L[fired], 0.95)["value"] if fired.any() else None), loss_fired_max=(float(L[fired].max()) if fired.any() else None),
                                 success_fired=(float(np.nanmean(ex[fired])) if fired.any() and np.isfinite(ex[fired]).any() else None), success_abstained=(float(np.nanmean(ex[abst])) if abst.any() and np.isfinite(ex[abst]).any() else None),
                                 abstained_equal_frozen_max_abs_diff=(float(np.abs(L[abst] - F[abst]).max()) if abst.any() else None),
                                 frozen_hard5_n=int(hard.sum()), frozen_hard5_abstained=int((hard & abst).sum()), frozen_hard5_abstain_rate=float((hard & abst).sum() / max(1, hard.sum())),
                                 cvar95_overall=S.cvar(L, 0.95)["value"], share_of_worst5pct_that_abstained=float(abst[np.argsort(L)[::-1][: max(1, math.ceil(0.05 * len(L)))]].mean()),
                                 n_fired_but_above_2nats=int((fired & (L > 2.0)).sum()), n_fired_but_failed=(int((fired & (ex == 0)).sum()) if np.isfinite(ex).any() else None)))
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------- 9. support matrix
def support_matrix(scores, gens, bo, mqc, harm):
    have_mq = not mqc.empty and (mqc["family"] == "EXT").any()
    have_harm = not harm.empty
    def models_present(ds, fam):
        x = scores[(scores["dataset"] == ds) & (scores["family"] == fam) & (scores["status"] == "ok")]
        return sorted(x["model"].unique())
    req = [
        ("Basic: ES / RET-ES / RET-GS, all three models, three datasets", "supported", "readers: record checkpoints (zsRE/CounterFact) and this study's MQuAKE evaluations; frozen: greedy generations on the same prompts (zero by screen / measured zero)", "benchmark_original.csv; cap_value/basic_performance.csv"),
        ("Basic: teacher-forced target NLL, all three models", "supported", "scores.parquet (same serialised prompt/answer pairs, same code path)", "cap_value/basic_performance.csv"),
        ("Basic: locality vs frozen (direct) and vs own cap-off reference", "supported", "direct: teacher-forced NLL and decoded answers on the same locality/near-miss/unseen prompts; own reference: record LS / near-miss / false-fire metrics; cap-off = frozen for these readers", "cap_value/collateral_vs_frozen.csv"),
        ("Basic: MQuAKE multi-hop accuracy, all three models", "supported" if have_mq else "missing", "readers: registered composition endpoint (80 cases); frozen: cap-off exact match on the same post-edit questions (case-level any/all not recorded for the frozen path; its question accuracy is 0)", "mquake_composition.csv"),
        ("Ordinary adaptation plots and absolute/percentage improvements", "supported", "losses: percentage of frozen loss; success rates: percentage points only (frozen rate 0 makes relative change undefined)", "cap_value/improvements.csv"),
        ("Extremes A: each model's own worst 5 % / 1 % (CVaR95 / CVaR99) with CIs", "supported", "item-group bootstrap, 2,000 draws", "cap_value/extremes_own_worst.csv"),
        ("Extremes B: frozen-defined hardest 5 % / 1 %, all three models, with CIs", "supported", "fixed sets; bootstrap within the set", "cap_value/extremes_frozen_hardest.csv"),
        ("Actual loss by frozen-difficulty decile, all three models, CIs, shared axes", "supported", "500 group-bootstrap draws per decile", "cap_value/deciles_actual_loss.csv; figures/cap_value/deciles_*.png"),
        ("Tail shapes at common absolute thresholds, with n, sensitivity, uncertainty", "supported (fits are finite-range; no power-law claim)", "token-level pooled probe surprisal; frozen P90/P95/P97.5 and 5/8/10 nats; GPD only with >= 100 exceedances", "cap_value/token_tails_common_thresholds.csv"),
        ("Locality / unrelated text / collateral: each cap vs frozen and vs own cap-off, incl. severe events", "supported", "probes: direct per-probe deteriorations D with counts above 1/2/5 nats; unrelated text: record harm summaries (245,237 positions per cell)", "cap_value/collateral_vs_frozen.csv; cap_value/harm_unrelated_text.csv"),
        ("Negative findings: MQuAKE multi-hop; residual extreme losses when gating fails", "supported", "composition endpoint; abstained paraphrases keep the frozen loss exactly", "cap_value/gating_failures.csv"),
        ("Frozen multi-hop any-/all-question case success", "partial", "only question-level cap-off exact match is recorded (0 of 240 on every cell); case-level any/all for the frozen path are therefore 0 as well but are not separately stored", "mquake_composition.csv (frozen_question_new_exact)"),
        ("Frozen-model exact match on paraphrases of CounterFact/MQuAKE 'true' facts", "supported (as loss)", "greedy newline-stop decoding almost never completes a true answer; the true-target NLL is reported instead", "benchmark_standardized.csv (edit/true)"),
        ("New realizations / orders / training seeds", "not available", "would need new GPU evaluations outside the frozen record; not run (amendment: no unnecessary reruns)", "—"),
    ]
    return pd.DataFrame([dict(requested_comparison=a, support=b, how=c, where=d) for a, b, c, d in req])


# -------------------------------------------------------------------------------------------------------- main
def main():
    scores = pd.read_parquet(DATA / "data" / "scores.parquet")
    gens = pd.read_parquet(DATA / "data" / "generations.parquet")
    pc = pd.read_parquet(DATA / "data" / "paired_cases.parquet")
    bo = pd.read_csv(OUT / "tables" / "benchmark_original.csv")
    mqc = pd.read_csv(OUT / "tables" / "mquake_composition.csv") if (OUT / "tables" / "mquake_composition.csv").exists() else pd.DataFrame()
    if "stream_index" not in gens.columns:
        meta = scores[["dataset", "probe_id", "stream_index"]].drop_duplicates()
        gens = gens.merge(meta, on=["dataset", "probe_id"], how="left")
    st = Status()
    harm = harm_table()
    audit, rec = denominator_audit(scores, gens, bo)
    basic = basic_performance(pc, gens, bo, mqc, harm)
    imp = improvements(basic)
    own300, hard300 = extremes(pc, 300)
    own100, hard100 = extremes(pc, 100, draws=500)
    dec = pd.concat([deciles(pc, 300), deciles(pc, 100, draws=200)], ignore_index=True)
    tails, curves = token_tails(scores, 300)
    coll300, worst300 = collateral(pc, gens, bo, 300)
    gate = pd.concat([gating(pc, 300), gating(pc, 100)], ignore_index=True)
    sup = support_matrix(scores, gens, bo, mqc, harm)
    # per-probe seed-mean case table for the figures / reuse
    cases = []
    for (ds, fam, tgt), x in pc.groupby(["dataset", "family", "target"]):
        if fam == "composition":
            continue
        y = ready(x, 300)
        if y is None:
            continue
        keep = ["dataset", "probe_id", "family", "target", "item_id", "stream_index", "subject", "L_frozen_h0", "X_frozen_h0", "L_bp_mean_h300", "L_epc_mean_h300"] + [c for c in y.columns if c.startswith(("X_bp_mean", "X_epc_mean", "F_bp_mean", "F_epc_mean"))] + [f"L_{r}_reader_s{s}_h300" for r in RULES for s in SEEDS]
        cases.append(y[[c for c in keep if c in y.columns]])
    cases = pd.concat(cases, ignore_index=True) if cases else pd.DataFrame()
    T.mkdir(parents=True, exist_ok=True); DD.mkdir(parents=True, exist_ok=True)
    tables = {"denominator_audit_probes": audit, "denominator_audit_record": rec, "basic_performance": basic, "improvements": imp, "extremes_own_worst": pd.concat([own300, own100], ignore_index=True), "extremes_frozen_hardest": pd.concat([hard300, hard100], ignore_index=True),
              "deciles_actual_loss": dec, "token_tails_common_thresholds": tails, "collateral_vs_frozen": coll300, "collateral_worst_cases": worst300, "harm_unrelated_text": harm, "gating_failures": gate, "support_matrix": sup}
    for name, df in tables.items():
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].map(lambda v: json.dumps(v) if isinstance(v, (list, dict)) else v)
        atomic_csv(T / f"{name}.csv", df)
        st.artifact(f"tables/cap_value/{name}", T / f"{name}.csv", rows=int(len(df)))
    atomic_parquet(DD / "survival_curves.parquet", curves)
    if len(cases):
        atomic_parquet(DD / "cases_seed_mean.parquet", cases)
        st.artifact("data/cap_value/cases_seed_mean", DD / "cases_seed_mean.parquet", rows=int(len(cases)))
    st.artifact("data/cap_value/survival_curves", DD / "survival_curves.parquet", rows=int(len(curves)))
    st.stage("9_cap_value", "updated", tables={k: int(len(v)) for k, v in tables.items()})
    print(json.dumps({k: int(len(v)) for k, v in tables.items()}))


if __name__ == "__main__":
    main()
