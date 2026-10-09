"""Stage 2 assembly (CPU): long-format scores, paired cases and the matched three-model benchmark tables.

    JAX_PLATFORMS=cpu python -m aw.extremes.assemble

Reads every completed scoring directory (frozen + readers x horizons x datasets), the frozen-record PC-reader checkpoints,
this study's MQuAKE evaluations (when present), and writes:
  data/scores.parquet          one row per (model, dataset, horizon, probe, target)
  data/paired_cases.parquet    one row per (dataset, probe, target) with every model's per-token loss at each horizon
  tables/benchmark_original.csv   registered metrics per (dataset, model, horizon) with numerators/denominators
  tables/benchmark_standardized.csv  teacher-forced losses, exact-match and margins per family
Rows are joined on explicit keys only; a probe missing in any model is kept as NaN, never as zero.
"""

from __future__ import annotations

import glob
import json
import math

import numpy as np
import pandas as pd

from aw.extremes.common import DATA, OUT, Status, atomic_csv, atomic_parquet, read_json
from aw.extremes.models import PCR, eval_dir
from aw.extremes.score import M_MODELS, scores_dir

HORIZONS = {"frozen": [None], **{m: [100, 300] for m in M_MODELS() if m != "frozen"}}
DATASETS = ("zsre", "counterfact", "mquake")


def load_scores():
    rows, gens = [], []
    probes_meta = {}
    for model in M_MODELS():
        for ds in DATASETS:
            for h in HORIZONS[model]:
                d = scores_dir(model, ds, h)
                man = d / "chunks.json"
                if not man.exists():
                    continue
                m = read_json(man)
                if m.get("status") != "complete":
                    continue
                if ds not in probes_meta:
                    probes_meta[ds] = {p["probe_id"]: p for p in json.loads((d / "probes.json").read_bytes())}
                for f in sorted(glob.glob(str(d / "chunk-*.jsonl"))):
                    for line in open(f):
                        r = json.loads(line)
                        sel = r.get("selection") or {}
                        g = r.get("generation")
                        base = dict(model=model, dataset=ds, horizon=(h or 0), probe_id=r["probe_id"], family=r["family"], item_id=r.get("item_id"), prompt_tokens=r["prompt_tokens"],
                                    fired=(None if not sel else (not sel["hard_null"])), null_mass=sel.get("null_mass"), best_score=sel.get("best_score"), n_records=len(sel.get("record_ids", [])) if sel else None,
                                    selected_own_record=(any(rid.endswith(":" + str(r.get("item_id")) + ":r1") or (":" + str(r.get("item_id")) + ":") in rid for rid in sel.get("record_ids", [])) if sel else None))
                        if g:
                            wn = g.get("write_norms") or []
                            gens.append(dict(base, text=g["text"], stopped_by=g["stopped_by"], truncated=g["truncated"], steps=g["steps"], logprob_sum=g["logprob_sum"],
                                             **{f"exact_{k}": v for k, v in g["exact"].items()}, gen_write_abs_max=max((max(x["abs"]) for x in wn), default=0.0) if wn else None))
                        for key, t in r["targets"].items():
                            if t.get("status") != "ok":
                                rows.append(dict(base, target=key, status=t.get("status")))
                                continue
                            wn = t.get("write_norms") or []
                            wrow = {}
                            if wn:
                                A = np.asarray([x["abs"] for x in wn], float)
                                R = np.asarray([[v if v is not None else np.nan for v in x["rel"]] for x in wn], float)
                                for s in range(3):
                                    wrow[f"write_abs_s{s + 1}_mean"] = float(A[:, s].mean()); wrow[f"write_abs_s{s + 1}_max"] = float(A[:, s].max())
                                    wrow[f"write_rel_s{s + 1}_mean"] = float(np.nanmean(R[:, s])); wrow[f"write_rel_s{s + 1}_max"] = float(np.nanmax(R[:, s]))
                                wrow["write_energy_sum"] = float(sum(x["energy"] for x in wn)); wrow["write_energy_mean"] = float(np.mean([x["energy"] for x in wn]))
                                wrow["write_rel_max_over_sites"] = float(np.nanmax(R)); wrow["write_abs_max_over_sites"] = float(A.max())
                            rows.append(dict(base, target=key, status="ok", target_text=t["text"], n_tokens=t["n_tokens"], nll_total=t["nll_total"], nll_token=t["nll_token"],
                                             nll_total_no_terminator=t["nll_total_no_terminator"], nll_token_no_terminator=t["nll_token_no_terminator"], per_token_nll=json.dumps(t["per_token_nll"]),
                                             exact=(g["exact"].get(key) if g else None), **wrow))
    return pd.DataFrame(rows), pd.DataFrame(gens), probes_meta


def meta_frame(probes_meta):
    out = []
    for ds, pm in probes_meta.items():
        for p in pm.values():
            out.append(dict(dataset=ds, probe_id=p["probe_id"], family=p["family"], item_id=p.get("item_id"), stream_index=p.get("stream_index"), subject=p.get("subject"), relation_id=p.get("relation_id"),
                            answer_tokens=p.get("answer_tokens"), hop_count=p.get("hop_count"), n_edits=p.get("n_edits"), case_id=p.get("case_id"), question_index=p.get("question_index"), paraphrase_index=p.get("paraphrase_index"),
                            locality_index=p.get("locality_index"), family_key=p.get("family_key"), edit_item_id=p.get("edit_item_id"), targets=",".join(sorted(p["targets"]))))
    return pd.DataFrame(out)


def paired(scores: pd.DataFrame, meta: pd.DataFrame):
    ok = scores[scores["status"] == "ok"].copy()
    ok["col"] = ok.apply(lambda r: f"{r['model']}_h{int(r['horizon'])}", axis=1)
    wide = ok.pivot_table(index=["dataset", "probe_id", "target"], columns="col", values="nll_token", aggfunc="first")
    wide.columns = [f"L_{c}" for c in wide.columns]
    tot = ok.pivot_table(index=["dataset", "probe_id", "target"], columns="col", values="nll_total", aggfunc="first")
    tot.columns = [f"T_{c}" for c in tot.columns]
    ex = ok.pivot_table(index=["dataset", "probe_id", "target"], columns="col", values="exact", aggfunc="first")
    ex.columns = [f"X_{c}" for c in ex.columns]
    fired = ok.pivot_table(index=["dataset", "probe_id", "target"], columns="col", values="fired", aggfunc="first")
    fired.columns = [f"F_{c}" for c in fired.columns]
    wrel = ok.pivot_table(index=["dataset", "probe_id", "target"], columns="col", values="write_rel_max_over_sites", aggfunc="first")
    wrel.columns = [f"W_{c}" for c in wrel.columns]
    out = pd.concat([wide, tot, ex, fired, wrel], axis=1).reset_index()
    out = out.merge(meta, on=["dataset", "probe_id"], how="left")
    return out


def _metric_row(ds, model, family, horizon, metrics, extra=None):
    row = dict(dataset=ds, model=model, family=family, horizon=horizon)
    for k, v in metrics.items():
        if isinstance(v, dict) and "value" in v:
            row[k] = v["value"]; row[k + "_num"] = v.get("numerator"); row[k + "_den"] = v.get("planned")
        else:
            row[k] = v
    row.update(extra or {})
    return row


def benchmark_original(scores, gens):
    rows = []
    for rule in ("bp", "epc"):
        for seed in (0, 1, 2):
            model = f"{rule}_reader_s{seed}"
            for ds in DATASETS:
                d = eval_dir(rule, seed, ds)
                for h in (100, 300):
                    cp = d / "stream" / f"checkpoint-{h}.json"
                    if not cp.exists():
                        continue
                    c = read_json(cp)
                    extra = dict(source=str(cp), family="PCR" if ds != "mquake" else "EXT")
                    if "unseen" in c and isinstance(c["unseen"], dict) and "summary" in c["unseen"]:
                        s = c["unseen"]["summary"]
                        extra.update(unseen_false_fires=s.get("false_fires"), unseen_false_fire_rate=s.get("false_fire_rate_evaluated"), unseen_answer_changes=s.get("answer_changes"), unseen_scored=s.get("scored_n"))
                    if ds == "mquake" and (d / "composition.json").exists() and h == 300:
                        s = read_json(d / "composition.json")["summary"]
                        extra.update(composition_success=s["evaluated_fraction"], composition_num=s["successes"], composition_den=s["scored"], composition_paraphrase_hits=s["paraphrase_successes"], composition_paraphrases=s["paraphrases_scored"])
                    rows.append(_metric_row(ds, model, extra.pop("family"), h, c["metrics"], extra))
    # frozen: original conventions where defined, by-definition values stated explicitly
    for ds in DATASETS:
        g = gens[(gens["model"] == "frozen") & (gens["dataset"] == ds)]
        if g.empty:
            continue
        def rate(fam, col):
            x = g[g["family"] == fam]
            return dict(value=(float(x[col].mean()) if len(x) else None), numerator=int(x[col].sum()) if len(x) else None, planned=int(len(x)))
        m = {"ES": rate("edit", "exact_new"), "RET-ES": rate("edit", "exact_new"), "RET-GS": rate("paraphrase", "exact_new"),
             "LS": dict(value=1.0, numerator=50, planned=50), "near_miss": dict(value=1.0, numerator=100, planned=100), "revision": dict(value=None, numerator=None, planned=50), "revision_latest_answer": dict(value=None, numerator=None, planned=50)}
        extra = dict(source="ext-20261009 frozen scoring", note="ES/RET-ES/RET-GS: frozen greedy answers vs taught aliases (no adaptation possible); LS and near-miss are 1 by definition (the frozen response is the reference); revision and unseen firing are N/A",
                     original_fact_exact_edit=(float(g[g["family"] == "edit"]["exact_true"].mean()) if "exact_true" in g and g[g["family"] == "edit"]["exact_true"].notna().any() else None),
                     unseen_false_fires=None)
        if ds == "mquake":
            x = g[g["family"] == "composition"]
            extra.update(composition_question_new_exact=float(x["exact_new"].mean()), composition_question_old_exact=float(x["exact_old"].mean()), composition_questions=int(len(x)))
        for h in (100, 300):
            rows.append(_metric_row(ds, "frozen", "FROZEN", h, m, extra))
    return pd.DataFrame(rows)


def benchmark_standardized(scores):
    ok = scores[scores["status"] == "ok"]
    rows = []
    for (ds, model, h, fam, tgt), x in ok.groupby(["dataset", "model", "horizon", "family", "target"]):
        rows.append(dict(dataset=ds, model=model, horizon=h, family=fam, target=tgt, n=int(len(x)), nll_token_mean=float(x["nll_token"].mean()), nll_token_median=float(x["nll_token"].median()),
                         nll_total_mean=float(x["nll_total"].mean()), nll_token_no_term_mean=float(x["nll_token_no_terminator"].mean()), exact_rate=(float(x["exact"].mean()) if x["exact"].notna().any() else None), exact_num=(int(x["exact"].sum()) if x["exact"].notna().any() else None),
                         fired_rate=(float(x["fired"].mean()) if x["fired"].notna().any() else None), cvar95_nll_token=float(np.sort(x["nll_token"].to_numpy())[::-1][: max(1, math.ceil(0.05 * len(x)))].mean())))
    df = pd.DataFrame(rows)
    # counterfactual preference margins where both targets exist on the same probe
    marg = []
    for (ds, model, h, fam), x in ok[ok["target"].isin(["new", "true"])].groupby(["dataset", "model", "horizon", "family"]):
        p = x.pivot_table(index="probe_id", columns="target", values=["nll_total", "nll_token"], aggfunc="first")
        if ("nll_total", "new") in p and ("nll_total", "true") in p:
            both = p.dropna()
            mt = -(both[("nll_total", "new")] - both[("nll_total", "true")])  # logP(new) - logP(true)
            mk = -(both[("nll_token", "new")] - both[("nll_token", "true")])
            marg.append(dict(dataset=ds, model=model, horizon=h, family=fam, n=int(len(both)), margin_total_mean=float(mt.mean()), margin_total_positive_fraction=float((mt > 0).mean()), margin_token_mean=float(mk.mean()), margin_token_positive_fraction=float((mk > 0).mean())))
    return df, pd.DataFrame(marg)


def main():
    scores, gens, probes_meta = load_scores()
    if scores.empty:
        print("no completed scoring directories yet")
        return
    meta = meta_frame(probes_meta)
    scores = scores.merge(meta.drop(columns=["family", "item_id"]), on=["dataset", "probe_id"], how="left")
    atomic_parquet(DATA / "data" / "scores.parquet", scores)
    atomic_parquet(DATA / "data" / "generations.parquet", gens)
    pc = paired(scores, meta)
    atomic_parquet(DATA / "data" / "paired_cases.parquet", pc)
    bo = benchmark_original(scores, gens)
    atomic_csv(OUT / "tables" / "benchmark_original.csv", bo)
    bs, marg = benchmark_standardized(scores)
    atomic_csv(OUT / "tables" / "benchmark_standardized.csv", bs)
    atomic_csv(OUT / "tables" / "preference_margins.csv", marg)
    st = Status()
    st.artifact("data/scores", DATA / "data" / "scores.parquet", rows=int(len(scores)))
    st.artifact("data/paired_cases", DATA / "data" / "paired_cases.parquet", rows=int(len(pc)))
    st.artifact("tables/benchmark_original", OUT / "tables" / "benchmark_original.csv", rows=int(len(bo)))
    st.stage("2_assembly", "updated", models=sorted(scores["model"].unique().tolist()), datasets=sorted(scores["dataset"].unique().tolist()))
    print(json.dumps(dict(scores=len(scores), generations=len(gens), paired=len(pc), models=sorted(scores["model"].unique().tolist()), benchmark_rows=len(bo))))


if __name__ == "__main__":
    main()
