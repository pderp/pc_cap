"""Stage 4 (CPU): dataset characterisation — frequency concentration, rarity, diversity, entropy, train/test shift.

    JAX_PLATFORMS=cpu python -m aw.extremes.datasets

Populations per dataset (independent-case level = one row per edit item / MQuAKE case):
  eligible      the screened pool the realizations were drawn from (zsRE 10,420; CounterFact 20,091; MQuAKE 6,043 single-hop items)
  mquake_raw    the 9,218 MQuAKE-CF cases (hop count, number of requested edits, relation chains)
  reader_train  the reader-training pool actually used (first 1,000 / 1,000 / 500 items of the v1/v1/v3 train pools)
  sealed_r0/r1/r2   the sealed realization streams (1,000 / 1,000 / 300 items), r0 being the PC-reader population
  pcr_r0_300    the first 300 items of r0 (the PC-reader study's 300-edit horizon)
Train/test comparisons use reader_train as "train" and sealed_r0 / pcr_r0_300 as "test"; the overlap of item ids and
subjects between them is reported (it is zero by construction of the draws) so that rarity is a benchmark property.
"""

from __future__ import annotations

import ast
import json
import math
from collections import Counter

import numpy as np
import pandas as pd

from aw.extremes import stats as S
from aw.extremes.common import ASSETS, DATA, OUT, ROOT, Status, atomic_csv, atomic_json, atomic_parquet, read_json, sha
from aw.extremes.models import RECIPES, recipe
from pccap.metrics.editing import normalize_answer

TRAIN_POOLS = {"zsre": ("manifests/revision_v1/train_pool_zsre_v1.json", 1000), "counterfact": ("manifests/revision_v1/train_pool_counterfact_v1.json", 1000), "mquake": ("manifests/revision_v1/train_pool_mquake_v3.json", 500)}
ELIGIBLE = {"zsre": ASSETS / "data/prepared/editing/zsre_eligible.jsonl", "counterfact": ASSETS / "data/prepared/editing/counterfact_eligible.jsonl", "mquake": ROOT / "manifests/revision_v1/mquake_pool_v1.json"}
RAW_MQUAKE = ASSETS / "data/raw/mquake/MQuAKE-CF.json"
R1_RECIPES = {("zsre", 1): "6b089d284c00a4418a1d3af4", ("zsre", 2): "0417f598d89548e3200a3fe4", ("counterfact", 1): "826332f387bd487a045d412f", ("counterfact", 2): "fa46e16c8436f7ea4a5c3f06", ("mquake", 1): "19964c4e7f737707baad94a5", ("mquake", 2): "fcd702d12d5d6bfae824379b"}


def _lit(v):
    if isinstance(v, str) and v[:1] in "[{":
        try:
            return ast.literal_eval(v)
        except Exception:
            return v
    return v


def _tstr(v):
    v = _lit(v)
    return v.get("str") if isinstance(v, dict) else v


def case_rows(items, dataset, population):
    rows = []
    for i, it in enumerate(items):
        pids, aids = _lit(it.get("prompt_ids")), _lit(it.get("answer_ids"))
        rows.append(dict(dataset=dataset, population=population, index=i, item_id=it.get("item_id"), subject=normalize_answer(str(it.get("subject") or it.get("subject_key") or "")),
                         relation_id=it.get("relation_id"), target_new=normalize_answer(str(it.get("answer") or "")), target_true=normalize_answer(str(_tstr(it.get("target_true")) or "")) or None,
                         prompt=it.get("prompt"), prompt_tokens=len(pids) if isinstance(pids, list) else None, answer_tokens=len(aids) if isinstance(aids, list) else None,
                         n_paraphrases=len(_lit(it.get("paraphrases")) or []), n_locality=len(_lit(it.get("locality_prompts")) or _lit(it.get("locality")) or []),
                         source_case_id=it.get("source_case_id"), source_split=it.get("source_split"), source_record_index=it.get("source_record_index", it.get("eligible_source_index"))))
    return pd.DataFrame(rows)


def load_populations():
    pops = {}
    for ds in ("zsre", "counterfact", "mquake"):
        path = ELIGIBLE[ds]
        if path.suffix == ".jsonl":
            items = [json.loads(l) for l in path.open()]
        else:
            items = read_json(path)["items"]
        pops[(ds, "eligible")] = case_rows(items, ds, "eligible")
        tp, n = TRAIN_POOLS[ds]
        pops[(ds, "reader_train")] = case_rows(read_json(ROOT / tp)["items"][:n], ds, "reader_train")
        r0, _ = recipe(ds)
        items0 = read_json(r0["payload"]["path"])["items"]
        pops[(ds, "sealed_r0")] = case_rows(items0, ds, "sealed_r0")
        pops[(ds, "pcr_r0_300")] = case_rows(items0[:300], ds, "pcr_r0_300")
        for r in (1, 2):
            rp = ROOT / "docs/tasks/R1-final-cell-recipes" / (R1_RECIPES[(ds, r)] + ".json")
            pops[(ds, f"sealed_r{r}")] = case_rows(read_json(read_json(rp)["payload"]["path"])["items"], ds, f"sealed_r{r}")
    return pops


def concentration(counts: Counter) -> dict:
    c = np.asarray(sorted(counts.values(), reverse=True), float)
    n, K = c.sum(), c.size
    if K == 0:
        return {}
    ent = S.entropy_of_counts(c)
    out = dict(n=int(n), K=int(K), singleton_fraction=float((c == 1).sum() * 1 / n), at_most_five_fraction=float(c[c <= 5].sum() / n), H=ent["H"], H_normalized=ent["H_normalized"], N_effective=ent["N_effective"])
    for pct in (1, 5, 10):
        k = max(1, int(math.ceil(K * pct / 100)))
        out[f"top{pct}pct_categories_share"] = float(c[:k].sum() / n)
    # descriptive Zipf slope on log rank vs log count over ranks 1..min(K, 100) and over all ranks (documented ranges)
    ranks = np.arange(1, K + 1)
    for label, lim in (("zipf_slope_top100", min(K, 100)), ("zipf_slope_all", K)):
        if lim >= 5:
            x, y = np.log(ranks[:lim]), np.log(c[:lim])
            out[label] = float(np.polyfit(x, y, 1)[0])
    return out


def length_stats(series) -> dict:
    x = pd.to_numeric(series, errors="coerce").dropna().to_numpy()
    if x.size == 0:
        return {}
    return dict(n=int(x.size), median=float(np.median(x)), p90=float(np.percentile(x, 90)), p95=float(np.percentile(x, 95)), p99=float(np.percentile(x, 99)), max=float(x.max()), mean=float(x.mean()))


def describe_population(df: pd.DataFrame) -> dict:
    out = dict(cases=int(len(df)))
    for var in ("relation_id", "subject", "target_new", "target_true"):
        vals = df[var].dropna()
        vals = vals[vals != ""]
        if len(vals) == 0:
            out[var] = dict(available=False)
            continue
        out[var] = dict(available=True, **concentration(Counter(vals)))
    if df["relation_id"].notna().any():
        pairs = [(r, t) for r, t in zip(df["relation_id"], df["target_new"]) if isinstance(r, str) and t]
        out["H_target_new_given_relation"] = S.conditional_entropy(pairs)
    out["prompt_tokens"] = length_stats(df["prompt_tokens"])
    out["answer_tokens"] = length_stats(df["answer_tokens"])
    out["n_paraphrases"] = length_stats(df["n_paraphrases"])
    np_ = df["prompt"].map(lambda s: normalize_answer(str(s)))
    out["duplicates"] = dict(exact_prompt_duplicates=int(np_.duplicated().sum()), subject_relation_target_duplicates=int(df[["subject", "relation_id", "target_new"]].astype(str).duplicated().sum()), subject_duplicates=int(df["subject"].duplicated().sum()))
    return out


def shift(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    out = dict(train_cases=int(len(train)), test_cases=int(len(test)), item_id_overlap=int(len(set(train["item_id"]) & set(test["item_id"]))), subject_overlap=int(len(set(train["subject"]) & set(test["subject"]))))
    for var in ("relation_id", "subject", "target_new", "target_true"):
        a, b = Counter(train[var].dropna()), Counter(test[var].dropna())
        a.pop("", None); b.pop("", None)
        if not a or not b:
            continue
        _, pa, pb = S.categorical_vectors(a, b)
        seen = test[var].dropna().map(lambda v: v in a)
        tf = test[var].dropna().map(lambda v: a.get(v, 0))
        out[var] = dict(js=S.js(pa, pb), kl_train_test_smoothed_0p5=S.smoothed_kl(a, b, 0.5), unseen_in_train_fraction=float(1 - seen.mean()) if len(seen) else None,
                        train_count_percentiles={p: float(np.percentile(tf, p)) for p in (10, 25, 50, 75, 90)} if len(tf) else None, rare_le1_fraction=float((tf <= 1).mean()) if len(tf) else None)
    tr = set(zip(train["subject"], train["relation_id"].astype(str), train["target_new"]))
    te = list(zip(test["subject"], test["relation_id"].astype(str), test["target_new"]))
    out["triple_overlap_fraction"] = float(np.mean([t in tr for t in te])) if te else None
    return out


def mquake_raw() -> dict:
    cases = read_json(RAW_MQUAKE)
    hops = Counter(len(c["orig"]["triples"]) for c in cases)
    edits = Counter(len(c["requested_rewrite"]) for c in cases)
    chains = Counter(" > ".join(t[1] for t in c["orig"]["triples_labeled"]) for c in cases)
    rels = Counter(r["relation_id"] for c in cases for r in c["requested_rewrite"])
    return dict(cases=len(cases), sha256=sha(RAW_MQUAKE), hop_count=dict(sorted(hops.items())), n_requested_edits=dict(sorted(edits.items())), relation_chain=concentration(chains), edit_relation=concentration(rels),
                questions_per_case=dict(Counter(len(c["questions"]) for c in cases)))


def main():
    pops = load_populations()
    summary, long_rows, freq_tables = {}, [], {}
    for (ds, pop), df in pops.items():
        d = describe_population(df)
        summary.setdefault(ds, {})[pop] = d
        for var in ("relation_id", "subject", "target_new", "target_true"):
            vals = df[var].dropna()
            vals = vals[vals != ""]
            if len(vals):
                c = Counter(vals).most_common()
                freq_tables[f"{ds}_{pop}_{var}"] = pd.DataFrame([dict(rank=i + 1, category=k, count=v) for i, (k, v) in enumerate(c)])
        def flat(prefix, obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    flat(f"{prefix}.{k}" if prefix else str(k), v)
            elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
                long_rows.append(dict(dataset=ds, population=pop, statistic=prefix, value=float(obj)))
        flat("", d)
    shifts = {}
    for ds in ("zsre", "counterfact", "mquake"):
        shifts[ds] = dict(reader_train_vs_sealed_r0=shift(pops[(ds, "reader_train")], pops[(ds, "sealed_r0")]), reader_train_vs_pcr_r0_300=shift(pops[(ds, "reader_train")], pops[(ds, "pcr_r0_300")]),
                          eligible_vs_sealed_r0=shift(pops[(ds, "eligible")], pops[(ds, "sealed_r0")]))
    raw = mquake_raw()
    # composition cases of r0 (hop counts / edits of the registered multi-hop endpoint)
    r0, _ = recipe("mquake")
    comp = read_json(r0["payload"]["path"])["endpoints"]["composition"]["rows"]
    raw["sealed_r0_composition"] = dict(cases=len(comp), hop_count=dict(Counter(len(c["orig"]["triples"]) for c in comp)), n_edits=dict(Counter(len(c["dependencies"]) for c in comp)))
    out = dict(run_id="ext-20261009", populations=summary, train_test_shift=shifts, mquake_raw=raw, sources=dict(eligible={k: str(v) for k, v in ELIGIBLE.items()}, train_pools=TRAIN_POOLS, raw_mquake=str(RAW_MQUAKE)))
    atomic_json(OUT / "tables" / "dataset_statistics.json", out)
    frame = pd.DataFrame(long_rows)
    atomic_csv(OUT / "tables" / "dataset_statistics.csv", frame)
    atomic_parquet(DATA / "data" / "dataset_statistics.parquet", frame)
    allcases = pd.concat(pops.values(), ignore_index=True)
    atomic_parquet(DATA / "data" / "case_populations.parquet", allcases)
    for name, t in freq_tables.items():
        atomic_csv(DATA / "data" / "frequency" / f"{name}.csv", t)
    st = Status()
    st.artifact("tables/dataset_statistics", OUT / "tables" / "dataset_statistics.json")
    st.artifact("data/case_populations", DATA / "data" / "case_populations.parquet", rows=int(len(allcases)))
    st.stage("4_dataset_statistics", "complete", populations=len(pops))
    print(json.dumps({ds: {p: summary[ds][p]["cases"] for p in summary[ds]} for ds in summary}))
    for ds in shifts:
        s = shifts[ds]["reader_train_vs_sealed_r0"]
        print(ds, "overlap ids/subjects", s["item_id_overlap"], s["subject_overlap"], {k: round(v["js"], 4) for k, v in s.items() if isinstance(v, dict) and "js" in v})


if __name__ == "__main__":
    main()
