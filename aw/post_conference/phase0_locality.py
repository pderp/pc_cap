"""Phase 0, item 4: what the item-locality deteriorations are (CPU only).

The supplement found that both caps got worse than frozen GPT-2 on 7.7 % of MQuAKE item-locality prompts with about 33
deteriorations above 2 nats per seed, while the 50-prompt sealed locality endpoint read 100 %. This module audits those
prompts against the record: did the cap fire, on which record, does the prompt share the taught item's relation
template, and how much non-stop token overlap does it have with the taught prompt. Near-miss neighbours (constructed
same-relation prompts) are audited the same way.

Outputs: locality_audit.csv (per probe), locality_audit_summary.csv, template_overlap.csv.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from aw.extremes.probes import build_probes
from aw.post_conference.common import DATA, HORIZON, READERS, SEVERE, TABLES, Status, atomic_csv, ensure_dirs, frozen_losses, label, read_json, rule_of, scores

CONFIG = "results/additional_work/PC-reader/eval-bp-s0-zsre/stream/config.json"


def stop_tokens() -> set[int]:
    from aw.extremes.common import ROOT

    c = read_json(ROOT / CONFIG)["semantic_config"]
    c = json.loads(c) if isinstance(c, str) else c
    return set(int(t) for t in c["reader"]["stop_tokens"])


def build() -> dict:
    ensure_dirs()
    from pccap.data.tokenize import GPT2Tokenizer

    tok = GPT2Tokenizer()
    stop = stop_tokens()
    s = scores(HORIZON)
    fz = frozen_losses(s)
    sel = pd.read_parquet(DATA / "selection_table.parquet")
    rows = []
    for ds in ("zsre", "counterfact", "mquake"):
        probes, _ = build_probes(ds)
        by_id = {p["probe_id"]: p for p in probes}
        items = {p["item_id"]: p for p in probes if p["family"] == "edit"}
        enc = {}

        def toks(text):
            if text not in enc:
                enc[text] = set(tok.encode(text)) - stop
            return enc[text]

        fam = s[(s.dataset == ds) & (s.family.isin(["locality_item", "locality_item_taught", "near_miss_neighbour"])) & (s.target == "true") & (s.model.isin(READERS)) & (s.status == "ok")]
        fam = fam.merge(fz, on=["dataset", "probe_id", "target"], how="left").merge(sel[["model", "dataset", "probe_id", "top_record", "own_in_candidates", "own_is_top", "veto", "n_candidates"]], on=["model", "dataset", "probe_id"], how="left")
        for r in fam.itertuples(index=False):
            p = by_id.get(r.probe_id)
            if p is None:
                continue
            if r.family in ("locality_item", "locality_item_taught"):
                taught = items.get(r.item_id)
            else:
                taught = items.get(p.get("edit_item_id")) or items.get(r.item_id)
            taught_prompt = taught["prompt"] if taught else None
            q, t = toks(p["prompt"]), (toks(taught_prompt) if taught_prompt else set())
            D = r.nll_token - r.L_frozen
            fired_record = r.top_record if r.fired else None
            fired_taught = bool(r.fired and taught and (":" + str(taught["item_id"]) + ":") in str(fired_record))
            src_item = p.get("locality_item_id") or p.get("neighbour_item_id")
            rows.append(dict(dataset=ds, model=r.model, rule=rule_of(r.model), family=r.family, probe_id=r.probe_id, item_id=r.item_id, prompt=p["prompt"], taught_prompt=taught_prompt,
                             source_item_is_taught=bool(p["prompt"] in {it["prompt"] for it in items.values()}), source_item_id=src_item, fired_source_item_record=bool(r.fired and src_item and (":" + str(src_item) + ":") in str(r.top_record)),
                             same_relation=(p.get("relation_id") == taught.get("relation_id")) if (taught and p.get("relation_id") and taught.get("relation_id")) else None,
                             shared_nonstop_tokens=len(q & t), prompt_nonstop_tokens=len(q), overlap_fraction=(len(q & t) / len(q) if q else np.nan),
                             fired=bool(r.fired), fired_taught_record=fired_taught, fired_other_record=bool(r.fired and not fired_taught), veto=r.veto, null_mass=r.null_mass,
                             L_frozen=r.L_frozen, L_cap=r.nll_token, D=D, severe=bool(D > SEVERE), harmful=bool(D > 1), deteriorated=bool(D > 1e-3), exact_frozen=r.X_frozen, exact_cap=r.exact))
    a = pd.DataFrame(rows)
    atomic_csv(TABLES / "locality_audit.csv", a)
    # contamination summary: locality prompts that are themselves taught stream items
    rows_c = []
    for (ds, model), x in a[a.family.isin(["locality_item", "locality_item_taught"])].groupby(["dataset", "model"]):
        c = x[x.source_item_is_taught]
        o = x[~x.source_item_is_taught]
        rows_c.append(dict(dataset=ds, model=model, rule=rule_of(model), label=label(model), n_locality_probes=len(x), n_source_item_taught=len(c), frac_source_item_taught=len(c) / len(x),
                           taught_fired=int(c.fired.sum()), taught_fired_source_record=int(c.fired_source_item_record.sum()), taught_severe=int(c.severe.sum()), taught_mean_D=(c.D.mean() if len(c) else np.nan),
                           other_n=len(o), other_fired=int(o.fired.sum()), other_deteriorated=int(o.deteriorated.sum()), other_severe=int(o.severe.sum()), other_frac_worse=(o.deteriorated.mean() if len(o) else np.nan), other_max_D=(o.D.max() if len(o) else np.nan),
                           supplement_frac_worse_all=x.deteriorated.mean(), supplement_severe_all=int(x.severe.sum())))
    atomic_csv(TABLES / "locality_contamination.csv", pd.DataFrame(rows_c))

    rows = []
    for (ds, fam_, model), x in a.groupby(["dataset", "family", "model"]):
        sev = x[x.severe]
        det = x[x.deteriorated]
        rows.append(dict(dataset=ds, family=fam_, model=model, rule=rule_of(model), label=label(model), n=len(x), fired_rate=x.fired.mean(), frac_deteriorated=x.deteriorated.mean(), frac_harmful_gt1=x.harmful.mean(), n_severe=int(len(sev)),
                         severe_fired=int(sev.fired.sum()), severe_fired_taught_record=int(sev.fired_taught_record.sum()), severe_fired_other_record=int(sev.fired_other_record.sum()),
                         severe_same_relation=(sev.same_relation.mean() if sev.same_relation.notna().any() else np.nan),
                         deteriorated_fired=int(det.fired.sum()), fired_frac_deteriorated=(x[x.fired].deteriorated.mean() if x.fired.any() else np.nan), fired_frac_severe=(x[x.fired].severe.mean() if x.fired.any() else np.nan),
                         fired_mean_D=(x[x.fired].D.mean() if x.fired.any() else np.nan), fired_max_D=(x[x.fired].D.max() if x.fired.any() else np.nan),
                         overlap_fired=(x[x.fired].overlap_fraction.mean() if x.fired.any() else np.nan), overlap_abstained=(x[~x.fired].overlap_fraction.mean() if (~x.fired).any() else np.nan),
                         same_relation_rate=(x.same_relation.mean() if x.same_relation.notna().any() else np.nan)))
    summ = pd.DataFrame(rows)
    atomic_csv(TABLES / "locality_audit_summary.csv", summ)

    # template overlap: fire rate as a function of shared non-stop tokens with the taught prompt (pooled over seeds per rule)
    a["shared_bucket"] = pd.cut(a.shared_nonstop_tokens, [-1, 0, 1, 2, 100], labels=["0", "1", "2", ">=3"])
    rows = []
    for keys, x in a.groupby(["dataset", "family", "rule", "shared_bucket"], observed=True):
        rows.append(dict(dataset=keys[0], family=keys[1], rule=keys[2], shared_nonstop_tokens=keys[3], n=len(x), fired_rate=x.fired.mean(), severe_rate=x.severe.mean(), mean_D=x.D.mean()))
    atomic_csv(TABLES / "template_overlap.csv", pd.DataFrame(rows))

    st = Status()
    for name in ("locality_audit", "locality_audit_summary", "template_overlap", "locality_contamination"):
        st.artifact(f"tables/{name}", TABLES / f"{name}.csv")
    st.stage("locality", "complete", n_rows=int(len(a)))
    return dict(rows=len(a))


if __name__ == "__main__":
    print(build())
