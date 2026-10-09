"""Stage 6 (CPU): the three models in the extremes — paired gains, difficulty deciles, CVaR A/B, regressions, locality,
correction magnitudes, joint extremes, rank correlations, sequential behaviour; grouped bootstrap intervals.

    JAX_PLATFORMS=cpu python -m aw.extremes.paired

Observation units and groups: item-level families (edit, paraphrase, locality_item) are grouped by item_id; endpoint
families by their own row id; bootstrap resamples groups (2,000 draws, seed 20261009) and the same indices are used for
every model, so pairing is preserved. Training seeds are reported one by one and as a seed-mean; three seeds on one
subject population are not three populations, and the intervals say nothing about new subjects.
Losses are per-token NLL (nats) of the stated target; gains G = L_frozen - L_model (positive favours the model);
deteriorations D = L_model - L_frozen. "PC" = ePC-trained reader, "BP" = BP-trained reader (same seed).
"""

from __future__ import annotations

import json
import math

import numpy as np
import pandas as pd
from scipy import stats as sps

from aw.extremes import stats as S
from aw.extremes.common import DATA, OUT, Status, atomic_csv, atomic_json, atomic_parquet

SEEDS = (0, 1, 2)
FAMILIES_ITEM = ("edit", "paraphrase", "locality_item")
DRAWS = 2000
SEED = 20261009


def cols(h):
    return dict(frozen="L_frozen_h0", **{f"bp{s}": f"L_bp_reader_s{s}_h{h}" for s in SEEDS}, **{f"epc{s}": f"L_epc_reader_s{s}_h{h}" for s in SEEDS})


def group_key(df):
    return np.where(df["family"].isin(FAMILIES_ITEM), df["item_id"].astype(str), df["probe_id"].astype(str))


def paired_block(x: pd.DataFrame, h: int):
    """Per (dataset, family, target) and seed: paired gains and bootstrap CIs."""
    c = cols(h)
    need = [c["frozen"]] + [c[f"bp{s}"] for s in SEEDS] + [c[f"epc{s}"] for s in SEEDS]
    if any(n not in x.columns for n in need):
        return []
    y = x.dropna(subset=need)
    if len(y) < 10:
        return []
    groups = group_key(y)
    F = y[c["frozen"]].to_numpy(float)
    out = []
    for s in SEEDS:
        B, P = y[c[f"bp{s}"]].to_numpy(float), y[c[f"epc{s}"]].to_numpy(float)
        for name, g in (("G_PC", F - P), ("G_BP", F - B), ("G_PCvsBP", B - P)):
            def stat(idx, g=g):
                v = g[idx]
                return np.array([v.mean(), np.median(v), (v > 0).mean(), (v < 0).mean(), np.percentile(v, 5), np.percentile(v, 95), S.cvar(-v, 0.95)["value"]])
            bs = S.grouped_bootstrap(stat, groups, draws=DRAWS, seed=SEED)
            pt = bs["point"]
            out.append(dict(horizon=h, seed=s, gain=name, n=int(len(y)), n_groups=bs["n_groups"], mean=pt[0], median=pt[1], frac_helped=pt[2], frac_harmed=pt[3], p5=pt[4], p95=pt[5], worst5pct_mean_negative_gain=-pt[6], sd=float(g.std(ddof=1)),
                            mean_ci=[bs["ci_low"][0], bs["ci_high"][0]], median_ci=[bs["ci_low"][1], bs["ci_high"][1]], frac_helped_ci=[bs["ci_low"][2], bs["ci_high"][2]], frac_harmed_ci=[bs["ci_low"][3], bs["ci_high"][3]]))
    # seed-mean of the three paired contrasts (descriptive)
    Bm = np.mean([y[c[f"bp{s}"]].to_numpy(float) for s in SEEDS], axis=0)
    Pm = np.mean([y[c[f"epc{s}"]].to_numpy(float) for s in SEEDS], axis=0)
    for name, g in (("G_PC", F - Pm), ("G_BP", F - Bm), ("G_PCvsBP", Bm - Pm)):
        bs = S.grouped_bootstrap(lambda idx, g=g: np.array([g[idx].mean(), (g[idx] > 0).mean()]), groups, draws=DRAWS, seed=SEED)
        out.append(dict(horizon=h, seed="mean", gain=name, n=int(len(y)), n_groups=bs["n_groups"], mean=bs["point"][0], frac_helped=bs["point"][1], mean_ci=[bs["ci_low"][0], bs["ci_high"][0]], frac_helped_ci=[bs["ci_low"][1], bs["ci_high"][1]]))
    return out


def cvar_blocks(x: pd.DataFrame, h: int):
    """A: each model's own worst 5 %; B: the frozen model's worst-5 % cases, fixed, scored by every model."""
    c = cols(h)
    need = list(c.values())
    if any(n not in x.columns for n in need):
        return []
    y = x.dropna(subset=need)
    if len(y) < 20:
        return []
    F = y[c["frozen"]].to_numpy(float)
    k = max(1, math.ceil(0.05 * len(y)))
    hard = np.argsort(F)[::-1][:k]
    k1 = max(1, math.ceil(0.01 * len(y)))
    hard1 = np.argsort(F)[::-1][:k1]
    out = []
    for name, col in c.items():
        v = y[col].to_numpy(float)
        ex = y.get("X_" + col[2:], pd.Series([np.nan] * len(y))).to_numpy(float) if ("X_" + col[2:]) in y.columns else np.full(len(y), np.nan)
        out.append(dict(horizon=h, model=name, n=int(len(y)), A_cvar95_own=S.cvar(v, 0.95)["value"], A_k=k, B_mean_loss_on_frozen_hard5=float(v[hard].mean()), B_success_on_frozen_hard5=(float(np.nanmean(ex[hard])) if np.isfinite(ex[hard]).any() else None),
                        B_mean_loss_on_frozen_hard1=float(v[hard1].mean()), B_k1=k1, overall_mean=float(v.mean()), overall_success=(float(np.nanmean(ex)) if np.isfinite(ex).any() else None)))
    return out


def decile_blocks(x: pd.DataFrame, h: int):
    c = cols(h)
    need = list(c.values())
    if any(n not in x.columns for n in need):
        return []
    y = x.dropna(subset=need).copy()
    if len(y) < 50:
        return []
    F = y[c["frozen"]].to_numpy(float)
    order = np.lexsort((y["probe_id"].to_numpy(), F))  # deterministic ties by probe id
    rank = np.empty(len(y), int)
    rank[order] = np.arange(len(y))
    y["decile"] = (rank * 10 // len(y)) + 1
    out = []
    for dec, z in y.groupby("decile"):
        Fz = z[c["frozen"]].to_numpy(float)
        row = dict(horizon=h, decile=int(dec), n=int(len(z)), frozen_mean=float(Fz.mean()), frozen_min=float(Fz.min()), frozen_max=float(Fz.max()))
        for s in SEEDS:
            B, P = z[c[f"bp{s}"]].to_numpy(float), z[c[f"epc{s}"]].to_numpy(float)
            row[f"G_PC_s{s}"] = float((Fz - P).mean()); row[f"G_BP_s{s}"] = float((Fz - B).mean()); row[f"G_PCvsBP_s{s}"] = float((B - P).mean())
        Bm = np.mean([z[c[f"bp{s}"]].to_numpy(float) for s in SEEDS], axis=0); Pm = np.mean([z[c[f"epc{s}"]].to_numpy(float) for s in SEEDS], axis=0)
        groups = group_key(z)
        for name, g in (("G_PC", Fz - Pm), ("G_BP", Fz - Bm), ("G_PCvsBP", Bm - Pm)):
            bs = S.grouped_bootstrap(lambda idx, g=g: np.array([g[idx].mean(), np.median(g[idx])]), groups, draws=500, seed=SEED)
            row[f"{name}_mean"] = bs["point"][0]; row[f"{name}_mean_ci_low"] = bs["ci_low"][0]; row[f"{name}_mean_ci_high"] = bs["ci_high"][0]; row[f"{name}_median"] = bs["point"][1]
        for name, col in c.items():
            xc = "X_" + col[2:]
            if xc in z.columns and z[xc].notna().any():
                row[f"success_{name}"] = float(z[xc].mean())
        out.append(row)
    return out


def regression_blocks(x: pd.DataFrame, h: int, thresholds=(0.5, 1.0, 2.0)):
    c = cols(h)
    need = list(c.values())
    if any(n not in x.columns for n in need):
        return [], []
    y = x.dropna(subset=need)
    F = y[c["frozen"]].to_numpy(float)
    rows, worst = [], []
    for name, col in c.items():
        if name == "frozen":
            continue
        D = y[col].to_numpy(float) - F
        pos = D[D > 0]
        row = dict(horizon=h, model=name, n=int(len(y)), frac_worse=float((D > 0).mean()), mean_positive_deterioration=(float(pos.mean()) if pos.size else None), p95_D=float(np.percentile(D, 95)), p99_D=float(np.percentile(D, 99)),
                   worst5pct_mean_D=S.cvar(D, 0.95)["value"], max_D=float(D.max()))
        for t in thresholds:
            row[f"frac_D_gt_{t}"] = float((D > t).mean()); row[f"n_D_gt_{t}"] = int((D > t).sum())
        rows.append(row)
        top = np.argsort(D)[::-1][:5]
        for i in top:
            r = y.iloc[i]
            worst.append(dict(horizon=h, model=name, probe_id=r["probe_id"], family=r["family"], target=r["target"], item_id=r.get("item_id"), subject=r.get("subject"), relation_id=r.get("relation_id"), D=float(D[i]), L_frozen=float(F[i]), L_model=float(y[col].iloc[i]),
                              fired=r.get("F_" + col[2:]), write_rel_max=r.get("W_" + col[2:])))
    # PC substantially worse than BP and vice versa (same seed)
    for s in SEEDS:
        D = y[c[f"epc{s}"]].to_numpy(float) - y[c[f"bp{s}"]].to_numpy(float)
        rows.append(dict(horizon=h, model=f"epc{s}_minus_bp{s}", n=int(len(y)), frac_worse=float((D > 0).mean()), mean_positive_deterioration=(float(D[D > 0].mean()) if (D > 0).any() else None), p95_D=float(np.percentile(D, 95)), p99_D=float(np.percentile(D, 99)),
                         worst5pct_mean_D=S.cvar(D, 0.95)["value"], max_D=float(D.max()), **{f"frac_D_gt_{t}": float((D > t).mean()) for t in thresholds}, **{f"frac_D_lt_minus_{t}": float((D < -t).mean()) for t in thresholds}))
    return rows, worst


def correlation_blocks(x: pd.DataFrame, h: int):
    """Spearman correlations between frozen surprisal, write magnitude, gain and locality deterioration (per seed/model)."""
    c = cols(h)
    out = []
    for name, col in c.items():
        if name == "frozen":
            continue
        w = "W_" + col[2:]
        if w not in x.columns or c["frozen"] not in x.columns:
            continue
        y = x.dropna(subset=[col, c["frozen"], w])
        if len(y) < 30:
            continue
        F, L, W = y[c["frozen"]].to_numpy(float), y[col].to_numpy(float), y[w].to_numpy(float)
        G = F - L
        fired = W > 0
        def rho(a, b):
            if len(a) < 10 or np.all(a == a[0]) or np.all(b == b[0]):
                return None
            r = sps.spearmanr(a, b)
            return [float(r.statistic), float(r.pvalue)]
        out.append(dict(horizon=h, model=name, n=int(len(y)), n_fired=int(fired.sum()),
                        rho_surprisal_vs_write=rho(F, W), rho_write_vs_gain=rho(W, G), rho_surprisal_vs_gain=rho(F, G),
                        rho_write_vs_gain_fired_only=rho(W[fired], G[fired]) if fired.sum() >= 10 else None, rho_surprisal_vs_deterioration_fired=rho(F[fired], -G[fired]) if fired.sum() >= 10 else None))
    return out


def joint_extremes(x: pd.DataFrame, h: int):
    """A: locality deterioration in its worst 10 %; B: relative write magnitude in its top 10 % (locality families only)."""
    c = cols(h)
    out = []
    loc = x[x["family"].isin(["locality_item", "locality", "near_miss_neighbour", "unseen"])]
    for name, col in c.items():
        if name == "frozen":
            continue
        w = "W_" + col[2:]
        if w not in loc.columns:
            continue
        y = loc.dropna(subset=[col, c["frozen"], w])
        if len(y) < 50:
            continue
        D = y[col].to_numpy(float) - y[c["frozen"]].to_numpy(float)
        W = y[w].to_numpy(float)
        A = D >= np.quantile(D, 0.9)
        B = W >= np.quantile(W, 0.9) if (W > 0).mean() >= 0.1 else (W > 0)
        pA, pAB = A.mean(), (A & B).sum() / max(1, B.sum())
        out.append(dict(horizon=h, model=name, n=int(len(y)), n_A=int(A.sum()), n_B=int(B.sum()), n_AB=int((A & B).sum()), P_A=float(pA), P_A_given_B=float(pAB), tail_lift=(float(pAB / pA) if pA > 0 else None), B_definition=("top 10 % relative write" if (W > 0).mean() >= 0.1 else "any nonzero write (fewer than 10 % fire)")))
    return out


def sequential(dataset: str):
    """Real teaching order from the frozen-record items.jsonl: immediate-success runs and lag-1..5 autocorrelation of per-edit acquisition outcome."""
    from aw.extremes.models import eval_dir

    rows = []
    for rule in ("bp", "epc"):
        for s in SEEDS:
            f = eval_dir(rule, s, dataset) / "stream" / "items.jsonl"
            if not f.exists():
                continue
            es = np.array([json.loads(l)["es"] for l in open(f)], float)
            gs = np.array([json.loads(l).get("gs") or 0.0 for l in open(f)], float)
            def acf(v, lag):
                if v.std() == 0 or len(v) <= lag + 2:
                    return None
                return float(np.corrcoef(v[:-lag], v[lag:])[0, 1])
            fail = es < 1
            runs = int(((fail[1:]) & (fail[:-1])).sum())
            rows.append(dict(dataset=dataset, rule=rule, seed=s, n=int(len(es)), es_mean=float(es.mean()), gs_mean=float(gs.mean()), n_failures=int(fail.sum()), consecutive_failure_pairs=runs,
                             **{f"acf_gs_lag{l}": acf(gs, l) for l in range(1, 6)}, order_note="payload stream order = teaching order (order 100)"))
    return rows


def main():
    pc = pd.read_parquet(DATA / "data" / "paired_cases.parquet")
    gains, cvars, deciles, regs, worst, corr, joint = [], [], [], [], [], [], []
    for (ds, fam, tgt), x in pc.groupby(["dataset", "family", "target"]):
        for h in (300, 100):
            for r in paired_block(x, h):
                gains.append(dict(dataset=ds, family=fam, target=tgt, **r))
            for r in cvar_blocks(x, h):
                cvars.append(dict(dataset=ds, family=fam, target=tgt, **r))
            if fam in ("edit", "paraphrase", "locality_item", "unseen", "near_miss_neighbour"):
                for r in decile_blocks(x, h):
                    deciles.append(dict(dataset=ds, family=fam, target=tgt, **r))
            rr, ww = regression_blocks(x, h)
            regs += [dict(dataset=ds, family=fam, target=tgt, **r) for r in rr]
            worst += [dict(dataset=ds, family=fam, target=tgt, **r) for r in ww]
            corr += [dict(dataset=ds, family=fam, target=tgt, **r) for r in correlation_blocks(x, h)]
    for ds, x in pc.groupby("dataset"):
        for h in (300, 100):
            joint += [dict(dataset=ds, **r) for r in joint_extremes(x, h)]
    seq = [r for ds in ("zsre", "counterfact", "mquake") for r in sequential(ds)]
    for name, rows in (("paired_gains", gains), ("cvar_A_B", cvars), ("difficulty_deciles", deciles), ("regressions", regs), ("worst_regressions", worst), ("rank_correlations", corr), ("joint_extremes", joint), ("sequential", seq)):
        df = pd.DataFrame(rows)
        atomic_csv(OUT / "tables" / f"{name}.csv", df)
        if name in ("paired_gains", "difficulty_deciles"):
            atomic_parquet(DATA / "data" / f"{name}.parquet", df)
    atomic_parquet(DATA / "data" / "bootstrap_results.parquet", pd.DataFrame(gains))
    st = Status()
    st.stage("6_paired", "updated", gains=len(gains), cvar=len(cvars), deciles=len(deciles), regressions=len(regs), correlations=len(corr), joint=len(joint), sequential=len(seq))
    print(json.dumps(dict(gains=len(gains), cvar=len(cvars), deciles=len(deciles), regressions=len(regs), correlations=len(corr), joint=len(joint), sequential=len(seq))))


if __name__ == "__main__":
    main()
