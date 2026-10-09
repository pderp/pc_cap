"""Stage 5 (CPU): heavy tails — reproduce HT-17's summary for the matched conditions, then extend to new observables.

    JAX_PLATFORMS=cpu python -m aw.extremes.tails

Part A (reproduction): the HT-17 record (logs/additional_work/HT-17/snapshot-20261004-complete/report.json) is read and
its PC-reader rows (12 cells) and the Stage-4 primary groups are copied; the per-cell statistics of the 12 PC-reader
vectors are recomputed with the record's own analyzer (aw.tail_class.analyze with the identical window plan) and
compared field by field.
Part B (extension, labelled new): (1) ordinary-text harm statistics and finite-range GPD/exponential comparison for this
study's six MQuAKE PC-reader evaluations with the same analyzer; (2) frozen-model per-probe surprisal (per-token NLL of
the taught/true target) by dataset and family, with GPD fits at P90/P95/P97.5 and item-group bootstrap; (3) the same
for each reader's per-probe loss; (4) frozen ordinary-text per-token surprisal (loss_capoff) by window.
Shapes are finite-range fits; nothing here establishes an asymptotic class.
"""

from __future__ import annotations

import glob
import json

import numpy as np
import pandas as pd

from aw.extremes import stats as S
from aw.extremes.common import DATA, OUT, ROOT, Status, atomic_csv, atomic_json, atomic_parquet, read_json, sha
from aw.extremes.models import PCR, eval_dir

HT17 = ROOT / "logs/additional_work/HT-17/snapshot-20261004-complete/report.json"


def load_delta(path):
    with np.load(path, allow_pickle=False) as f:
        v = f["values"]
    return v[:, :, 0] - v[:, :, 1], v


def reproduce_ht17():
    from aw.tail_class import analyze, window_plan

    rep = read_json(HT17)
    weights, folds = window_plan(1931)
    rows, checks = [], []
    for c in rep["cells"]:
        if c["phase"] != "PC-reader":
            continue
        vec = c["vector"]
        path = vec["path"] if isinstance(vec, dict) else vec
        if isinstance(vec, dict) and sha(path) != vec["sha256"]:
            raise ValueError("HT-17 source vector changed: " + path)
        delta, _ = load_delta(path)
        mine, _ = analyze(delta, weights=weights, folds=folds, bootstrap_fits=False)
        rec = c["statistics"]
        t = rec["thresholds"]["0.01"]
        mt = mine["thresholds"]["0.01"]
        same = dict(mean_signed=abs(mine["mean_signed"] - rec["mean_signed"]) < 1e-12, es99=abs(mine["es99_positive"] - rec["es99_positive"]) < 1e-12, maximum=mine["maximum"] == rec["maximum"],
                    count_0p01=mt["count"] == t["count"], conditional=(mt["conditional_mean_loss"] is None and t["conditional_mean_loss"] is None) or abs((mt["conditional_mean_loss"] or 0) - (t["conditional_mean_loss"] or 0)) < 1e-9,
                    fit_status=mt["fit"].get("status") == t["fit"].get("status"), shape=(abs((mt["fit"].get("shape") or 0) - (t["fit"].get("shape") or 0)) < 1e-9) if "shape" in t["fit"] else True)
        checks.append(dict(id=c["id"], **same))
        rows.append(dict(phase="PC-reader", dataset=c["dataset"], rule=c["condition"], seed=c["seed"], positions=rec["positions"], mean_signed=rec["mean_signed"], es99_positive=rec["es99_positive"], maximum=rec["maximum"],
                         freq_0p01=t["fraction"], count_0p01=t["count"], conditional_mean_0p01=t["conditional_mean_loss"], freq_interval=t.get("frequency_interval"), fit_status_0p01=t["fit"].get("status"), shape_0p01=t["fit"].get("shape"),
                         scale_0p01=t["fit"].get("scale"), shape_interval_0p01=(t.get("shape_bootstrap") or {}).get("shape_interval"), gpd_minus_exp_0p01=(t.get("cross_validation") or {}).get("gpd_minus_exponential_per_excess"), gate=json.dumps(c.get("gate")), efficacy=json.dumps(c.get("efficacy"))))
    groups = [g for g in rep["groups"] if g["phase"] in ("stage4", "PC-reader")]
    grows = []
    for g in groups:
        t = g["thresholds"]["0.01"]
        grows.append(dict(phase=g["phase"], dataset=g["dataset"], condition=g["condition"], cells=g["cells"], freq_0p01=t["frequency"], freq_interval=t.get("frequency_interval"), conditional_mean_0p01=t["conditional_mean_loss"], conditional_interval=t.get("conditional_mean_interval")))
    return pd.DataFrame(rows), pd.DataFrame(checks), pd.DataFrame(grows), rep


def new_mquake_harm():
    from aw.tail_class import analyze, window_plan

    weights, folds = window_plan(1931)
    rows = []
    for rule in ("bp", "epc"):
        for seed in (0, 1, 2):
            d = eval_dir(rule, seed, "mquake")
            vec = d / "harm" / "vectors.npz"
            if not vec.exists() or not (d / "report.json").exists():
                continue
            delta, _ = load_delta(vec)
            a, _ = analyze(delta, weights=weights, folds=folds, bootstrap_fits=True)
            for u, t in a["thresholds"].items():
                rows.append(dict(family="EXT", dataset="mquake", rule=rule, seed=seed, threshold=float(u), positions=a["positions"], mean_signed=a["mean_signed"], es99_positive=a["es99_positive"], maximum=a["maximum"],
                                 count=t["count"], fraction=t["fraction"], conditional_mean=t["conditional_mean_loss"], freq_interval=t.get("frequency_interval"), conditional_interval=t.get("conditional_mean_interval"),
                                 fit_status=t["fit"].get("status"), shape=t["fit"].get("shape"), shape_interval=(t.get("shape_bootstrap") or {}).get("shape_interval"), scale=t["fit"].get("scale"), gpd_minus_exp=(t.get("cross_validation") or {}).get("gpd_minus_exponential_per_excess"), vector=str(vec), vector_sha256=sha(vec)))
    return pd.DataFrame(rows)


def probe_surprisal_tails(paired: pd.DataFrame):
    """GPD fits of per-token target NLL by (dataset, family, target, model column); groups = item_id for the bootstrap."""
    rows = []
    cols = [c for c in paired.columns if c.startswith("L_")]
    for (ds, fam, tgt), x in paired.groupby(["dataset", "family", "target"]):
        if fam == "composition":
            continue
        for col in cols:
            v = x[col].to_numpy(float)
            ok = np.isfinite(v)
            if ok.sum() < 100:
                continue
            groups = x["item_id"].to_numpy()[ok]
            d = S.describe(v[ok])
            for f in S.threshold_fits(v[ok], groups=groups, draws=200, seed=1):
                rows.append(dict(dataset=ds, family=fam, target=tgt, model=col[2:], n_values=d["n"], mean=d["mean"], p95=d["p95"], p99=d["p99"], max=d["max"], cvar95=d["cvar95"], **{("n_exceedances" if k == "n" else k): v for k, v in f.items() if k != "bootstrap"},
                                 kappa_ci_low=(f.get("bootstrap") or {}).get("kappa_ci", [None, None])[0], kappa_ci_high=(f.get("bootstrap") or {}).get("kappa_ci", [None, None])[1]))
    return pd.DataFrame(rows)


def token_level_tails(scores: pd.DataFrame):
    """Per-token target surprisal pooled over all target tokens of a family (one value per token), groups = item_id.

    Probe-level fits at P90/P95/P97.5 have 15-60 exceedances with 300-600 probes and are reported as insufficient;
    the token-level variable (300 items x 2-6 target tokens, terminator excluded) reaches the 100-exceedance screen.
    """
    rows = []
    ok = scores[(scores["status"] == "ok") & (scores["horizon"].isin([0, 300]))].copy()
    # pooled probe families: new target for edit-type prompts, true target for locality-type prompts
    keep = {("edit", "new"), ("paraphrase", "new"), ("unseen", "new"), ("locality_item", "true"), ("locality", "true"), ("near_miss_neighbour", "true")}
    pooled = ok[[(a, b) in keep for a, b in zip(ok["family"], ok["target"])]].copy()
    pooled["family"] = "pooled_probes"
    pooled["target"] = "new/true"
    ok = pd.concat([ok, pooled], ignore_index=True)
    for (ds, fam, tgt, model), x in ok.groupby(["dataset", "family", "target", "model"]):
        if fam == "composition":
            continue
        vals, groups = [], []
        for pt, iid in zip(x["per_token_nll"], x["item_id"]):
            v = json.loads(pt)[:-1]  # terminator excluded
            vals += v
            groups += [iid] * len(v)
        v = np.asarray(vals, float)
        if v.size < 200:
            continue
        d = S.describe(v)
        for fit in S.threshold_fits(v, groups=np.asarray(groups), draws=200, seed=3):
            rows.append(dict(dataset=ds, family=fam, target=tgt, model=model, n_tokens=d["n"], n_items=int(x["item_id"].nunique()), mean=d["mean"], p95=d["p95"], p99=d["p99"], max=d["max"], cvar95=d["cvar95"],
                             **{("n_exceedances" if k == "n" else k): val for k, val in fit.items() if k != "bootstrap"},
                             kappa_ci_low=(fit.get("bootstrap") or {}).get("kappa_ci", [None, None])[0], kappa_ci_high=(fit.get("bootstrap") or {}).get("kappa_ci", [None, None])[1]))
    return pd.DataFrame(rows)


def frozen_text_surprisal():
    """Per-token ordinary-text surprisal of the frozen base from a saved vector (identical in every cell: loss_capoff)."""
    vec = PCR / "eval-bp-s0-zsre/harm/vectors.npz"
    _, v = load_delta(vec)
    x = v[:, :, 1].ravel()
    groups = np.repeat(np.arange(v.shape[0]), v.shape[1])
    d = S.describe(x)
    fits = S.threshold_fits(x, groups=groups, draws=200, seed=2)
    return dict(source=str(vec), sha256=sha(vec), field="loss_capoff", describe=d, fits=fits, cvar95=S.cvar(x, 0.95), es99_positive=S.es_positive_fractional(x, 0.99))


def main():
    rep_rows, checks, groups, rep = reproduce_ht17()
    atomic_csv(OUT / "tables" / "ht17_pcreader_rows.csv", rep_rows)
    atomic_csv(OUT / "tables" / "ht17_reproduction_checks.csv", checks)
    atomic_csv(OUT / "tables" / "ht17_groups_0p01.csv", groups)
    mq = new_mquake_harm()
    if not mq.empty:
        atomic_csv(OUT / "tables" / "mquake_pcreader_harm_tails.csv", mq)
    paired = pd.read_parquet(DATA / "data" / "paired_cases.parquet")
    pt = probe_surprisal_tails(paired)
    atomic_csv(OUT / "tables" / "probe_loss_tail_fits.csv", pt)
    scores = pd.read_parquet(DATA / "data" / "scores.parquet")
    tt = token_level_tails(scores)
    atomic_csv(OUT / "tables" / "token_loss_tail_fits.csv", tt)
    atomic_parquet(DATA / "data" / "tail_fits.parquet", pd.concat([pt.assign(source="probes"), mq.assign(source="mquake_harm")], ignore_index=True) if not mq.empty else pt.assign(source="probes"))
    ft = frozen_text_surprisal()
    atomic_json(OUT / "tables" / "frozen_text_surprisal_tails.json", ft)
    st = Status()
    st.artifact("tables/ht17_reproduction_checks", OUT / "tables" / "ht17_reproduction_checks.csv", all_equal=bool(checks.drop(columns=["id"]).all().all()))
    st.artifact("data/tail_fits", DATA / "data" / "tail_fits.parquet")
    st.stage("5_tails", "updated", ht17_cells_reproduced=int(len(checks)), ht17_all_equal=bool(checks.drop(columns=["id"]).all().all()), mquake_new_rows=int(len(mq)), probe_fit_rows=int(len(pt)), token_fit_rows=int(len(tt)))
    print(json.dumps(dict(ht17_cells=len(checks), all_equal=bool(checks.drop(columns=["id"]).all().all()), mquake_rows=len(mq), probe_fits=len(pt), frozen_text=ft["describe"])))


if __name__ == "__main__":
    main()
