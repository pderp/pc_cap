"""Phase 0, item 2: failure atlas from saved results (CPU only).

For every paraphrase / near-miss / unseen / item-locality probe of the six readers at 300 edits, classify the outcome by
what the reader did (which record it retrieved, whether it fired, which gate stopped it) and what happened to the loss
and the generated answer. Adds the review's "oracle selection rate": how many failures had the correct record among
the retrieved candidates (so that perfect selection could in principle rescue them) versus not retrieved at all.

Outputs (results/post_conference/phase0/tables): failure_atlas.csv, failure_atlas_summary.csv, payload_vs_gating.csv,
oracle_selection_rate.csv, failures_by_difficulty.csv; assets/post_conference/phase0/selection_table.parquet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from aw.post_conference.common import DATA, HORIZON, NOISE, READERS, SEVERE, TABLES, Status, atomic_csv, atomic_parquet, ensure_dirs, frozen_losses, label, rule_of, scores, selection_table

CATEGORIES = [
    "correct record fired, success",
    "correct record fired, failed (payload)",
    "wrong record fired",
    "abstained by null threshold, correct record retrieved",
    "abstained by rare-token veto, correct record retrieved",
    "abstained, correct record not retrieved",
    "abstained, no candidates",
]
COLLATERAL_CATEGORIES = ["appropriate null", "false fire, benign (|D| <= 1 nat)", "false fire, harmful (1 < D <= 2)", "false fire, severe (D > 2)", "false fire, beneficial (D < -1)"]


def classify_item(row) -> str:
    if row.fired:
        if row.own_is_top:
            return CATEGORIES[0] if row.exact else CATEGORIES[1]
        return CATEGORIES[2]
    if row.n_candidates == 0:
        return CATEGORIES[6]
    if not row.own_in_candidates:
        return CATEGORIES[5]
    return CATEGORIES[3] if row.veto == "null_threshold" else CATEGORIES[4]


def classify_collateral(row) -> str:
    if not row.fired:
        return COLLATERAL_CATEGORIES[0]
    D = row.D
    if D > SEVERE:
        return COLLATERAL_CATEGORIES[3]
    if D > 1:
        return COLLATERAL_CATEGORIES[2]
    if D < -1:
        return COLLATERAL_CATEGORIES[4]
    return COLLATERAL_CATEGORIES[1]


def build() -> dict:
    ensure_dirs()
    s = scores(HORIZON)
    sel = selection_table()
    atomic_parquet(DATA / "selection_table.parquet", sel)
    fz = frozen_losses(s)
    r = s[(s.model.isin(READERS)) & (s.status == "ok")].merge(fz, on=["dataset", "probe_id", "target"], how="left")
    r = r.merge(sel[["model", "dataset", "probe_id", "n_candidates", "top_record", "own_in_candidates", "own_is_top", "veto"]], on=["model", "dataset", "probe_id"], how="left")
    r["D"] = r.nll_token - r.L_frozen
    r["fired"] = r.fired.astype(bool)
    r["rule"] = r.model.map(rule_of)

    item = r[(r.family == "paraphrase") & (r.target == "new")].copy()
    item["category"] = item.apply(classify_item, axis=1)
    coll = r[(r.family.isin(["near_miss_neighbour", "unseen", "locality_item"])) & (r.target.isin(["true", "new"]))].copy()
    coll = coll[~((coll.family == "unseen") & (coll.target != "new")) & ~((coll.family != "unseen") & (coll.target != "true"))]
    coll["category"] = coll.apply(classify_collateral, axis=1)

    atlas = pd.concat([item[["dataset", "model", "rule", "family", "probe_id", "item_id", "category", "nll_token", "L_frozen", "D", "exact", "fired", "null_mass", "best_score", "veto", "own_in_candidates", "own_is_top", "answer_tokens", "stream_index"]],
                       coll[["dataset", "model", "rule", "family", "probe_id", "item_id", "category", "nll_token", "L_frozen", "D", "exact", "fired", "null_mass", "best_score", "veto", "own_in_candidates", "own_is_top", "answer_tokens", "stream_index"]]])
    atomic_csv(TABLES / "failure_atlas.csv", atlas)

    # summary: counts and shares per dataset x model x family x category, plus seed means per rule
    g = atlas.groupby(["dataset", "family", "model", "rule", "category"]).size().rename("n").reset_index()
    tot = atlas.groupby(["dataset", "family", "model"]).size().rename("n_total").reset_index()
    g = g.merge(tot, on=["dataset", "family", "model"])
    g["share"] = g.n / g.n_total
    sm = g.groupby(["dataset", "family", "rule", "category"]).agg(n_seed_mean=("n", "mean"), share_seed_mean=("share", "mean"), share_min=("share", "min"), share_max=("share", "max"), n_total=("n_total", "first")).reset_index()
    sm["model"] = sm.rule.map(lambda x: f"{x}_mean")
    summary = pd.concat([g, sm], ignore_index=True)
    summary["label"] = summary.model.map(lambda m: label(m) if m in READERS else {"bp_mean": "BP-CAP seed mean", "epc_mean": "PC-CAP seed mean"}[m])
    atomic_csv(TABLES / "failure_atlas_summary.csv", summary)

    # payload vs gating: paraphrase failures = not exact (generation) and, separately, loss > 1 nat/token
    rows = []
    for (ds, model), x in item.groupby(["dataset", "model"]):
        fail_gen = x[~x.exact.astype(bool)]
        fail_loss = x[x.nll_token > 1.0]
        for name, f in (("not_exact", fail_gen), ("loss_gt_1nat", fail_loss)):
            rows.append(dict(dataset=ds, model=model, rule=rule_of(model), label=label(model), failure_definition=name, n_probes=len(x), n_failures=len(f), failure_rate=len(f) / len(x),
                             abstained=int((~f.fired).sum()), abstained_threshold=int((f.veto == "null_threshold").sum()), abstained_rare_veto=int((f.veto == "rare_token_veto").sum()),
                             abstained_not_retrieved=int(((~f.fired) & (~f.own_in_candidates)).sum()),
                             fired_correct_record=int((f.fired & f.own_is_top).sum()), fired_wrong_record=int((f.fired & ~f.own_is_top).sum()),
                             share_of_failures_fired=(f.fired.mean() if len(f) else np.nan),
                             fired_failures_mean_loss=(f[f.fired].nll_token.mean() if f.fired.any() else np.nan), fired_failures_max_loss=(f[f.fired].nll_token.max() if f.fired.any() else np.nan),
                             abstained_failures_mean_loss=(f[~f.fired].nll_token.mean() if (~f.fired).any() else np.nan),
                             fired_success_rate=x[x.fired].exact.astype(bool).mean() if x.fired.any() else np.nan, abstain_rate=(~x.fired).mean(),
                             worst5pct_share_abstained=((~x.nlargest(max(1, int(np.ceil(0.05 * len(x)))), "nll_token").fired).mean())))
    pv = pd.DataFrame(rows)
    atomic_csv(TABLES / "payload_vs_gating.csv", pv)

    # oracle selection rate: among failures, correct record among the candidates (rescuable by selection) vs not
    rows = []
    for (ds, model), x in item.groupby(["dataset", "model"]):
        f = x[~x.exact.astype(bool)]
        rows.append(dict(dataset=ds, model=model, rule=rule_of(model), label=label(model), n_failures=len(f),
                         correct_record_retrieved=int(f.own_in_candidates.sum()), correct_record_top=int(f.own_is_top.sum()),
                         oracle_selection_rate=(f.own_in_candidates.mean() if len(f) else np.nan),
                         already_selected_but_failed=int((f.fired & f.own_is_top).sum()), note="rescue by selection is bounded above by failures whose correct record was retrieved and not yet applied; measured rescue comes from the replay (frontier module)"))
    atomic_csv(TABLES / "oracle_selection_rate.csv", pd.DataFrame(rows))

    # failures by difficulty (frozen-loss tercile) and answer length
    item["frozen_tercile"] = item.groupby("dataset").L_frozen.transform(lambda v: pd.qcut(v.rank(method="first"), 3, labels=["easy", "medium", "hard"]))
    item["answer_len"] = pd.cut(item.answer_tokens.fillna(0), [0, 2, 4, 100], labels=["<=2 tokens", "3-4 tokens", ">=5 tokens"])
    rows = []
    for keys, x in item.groupby(["dataset", "rule", "frozen_tercile", "answer_len"], observed=True):
        rows.append(dict(dataset=keys[0], rule=keys[1], frozen_tercile=keys[2], answer_len=keys[3], n=len(x), success=x.exact.astype(bool).mean(), abstain_rate=(~x.fired).mean(), fired_failed_rate=(x.fired & ~x.exact.astype(bool)).mean(), mean_loss=x.nll_token.mean()))
    atomic_csv(TABLES / "failures_by_difficulty.csv", pd.DataFrame(rows))

    st = Status()
    for name in ("failure_atlas", "failure_atlas_summary", "payload_vs_gating", "oracle_selection_rate", "failures_by_difficulty"):
        st.artifact(f"tables/{name}", TABLES / f"{name}.csv")
    st.artifact("data/selection_table", DATA / "selection_table.parquet")
    st.stage("atlas", "complete", n_item_probes=int(len(item)), n_collateral_probes=int(len(coll)))
    return dict(item=len(item), collateral=len(coll))


if __name__ == "__main__":
    print(build())
