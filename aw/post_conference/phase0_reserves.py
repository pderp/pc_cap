"""Phase 0, item 6: inventory of unexposed subjects per dataset (CPU, metadata only).

Replays the certified clearance (aw.r_extension) for zsRE and CounterFact and removes every item, fact, entity and
canonical subject reserved by primary realizations 0-3 (realization 3 = Option R). Reports the overlap of what remains
with the reader-training pool used by the PC-reader study (1,000 items per dataset), because a reader trained on those
items must not be confirmed on them. MQuAKE has no clearance register of the same kind; its count comes from the
case_populations table (eligible minus every sealed/training population, by item and by subject) and is labelled as such.

Output: reserves.csv, reserves.json.
"""

from __future__ import annotations

import json

import pandas as pd

from aw.extremes.common import DATA as EXT_DATA
from aw.post_conference.common import ROOT, TABLES, Status, atomic_csv, atomic_json, ensure_dirs, now, read_json


def build() -> dict:
    ensure_dirs()
    from aw.r_extension import clearance_value, exclude_reserved, load_bound, source_rows

    record = read_json(ROOT / "logs/additional_work/R/preparation-v1.json")
    spec = load_bound(record["input_spec"])
    previous = load_bound(record["original_reservations"])
    option_r = load_bound(record["reservations"])
    register = load_bound(spec["register"])
    evidence = load_bound(record["evidence"])
    cleared = clearance_value(spec, register, evidence, source_rows(register))["candidates"]
    blocked = dict(allocations=previous["allocations"] + option_r["allocations"])
    remaining = exclude_reserved(cleared, blocked)
    pops = pd.read_parquet(EXT_DATA / "data" / "case_populations.parquet")
    rows, detail = [], {}
    for ds in ("zsre", "counterfact"):
        rem = remaining[ds]
        rem_ids = {r["item_id"] for r in rem}
        rem_subj = {str(r.get("normalized_subject") or r.get("subject")).lower() for r in rem}
        train = pops[(pops.dataset == ds) & (pops.population == "reader_train")]
        train_ids, train_subj = set(train.item_id), set(train.subject.str.lower())
        clean = [r for r in rem if r["item_id"] not in train_ids and str(r.get("normalized_subject") or r.get("subject")).lower() not in train_subj]
        reserved_items = sum(len(g["items"]) for g in blocked["allocations"] if g["dataset"] == ds)
        rows.append(dict(dataset=ds, method="certified clearance replay (aw.r_extension), minus reservations r0-r3", cleared=len(cleared[ds]), reserved_items=reserved_items, remaining=len(rem),
                         remaining_subjects=len(rem_subj), overlap_with_reader_train_items=len(rem_ids & train_ids), overlap_with_reader_train_subjects=len(rem_subj & train_subj),
                         remaining_clean_of_reader_train=len(clean), note="dated: later exposures only reduce this; 300-edit confirmation needs 300 edits + 350 endpoint roles per realization"))
        detail[ds] = dict(remaining_item_ids=sorted(rem_ids), clean_item_ids=sorted(r["item_id"] for r in clean))
    ds = "mquake"
    p = pops[pops.dataset == ds]
    elig = p[p.population == "eligible"]
    exposed = p[p.population != "eligible"]
    ex_ids, ex_subj = set(exposed.item_id), set(exposed.subject.str.lower())
    rem = elig[~elig.item_id.isin(ex_ids) & ~elig.subject.str.lower().isin(ex_subj)]
    rows.append(dict(dataset=ds, method="case_populations: eligible minus sealed r0-r2, reader_train and pcr_r0_300 (item and subject); no entity/canonical-subject register", cleared=len(elig), reserved_items=len(ex_ids), remaining=len(rem),
                     remaining_subjects=rem.subject.str.lower().nunique(), overlap_with_reader_train_items=0, overlap_with_reader_train_subjects=0, remaining_clean_of_reader_train=len(rem),
                     note="upper bound: endpoint roles (outside/near-miss/revision) of the sealed realizations are not in case_populations and are not excluded here; composition cases and their dependency subjects not excluded"))
    detail[ds] = dict(remaining_item_ids=sorted(rem.item_id))
    t = pd.DataFrame(rows)
    atomic_csv(TABLES / "reserves.csv", t)
    atomic_json(TABLES / "reserves.json", dict(computed=now(), sources=dict(preparation=str(ROOT / "logs/additional_work/R/preparation-v1.json"), case_populations=str(EXT_DATA / "data" / "case_populations.parquet")), rows=rows, detail=detail))
    st = Status()
    st.artifact("tables/reserves", TABLES / "reserves.csv")
    st.stage("reserves", "complete")
    return {r["dataset"]: r["remaining"] for r in rows}


if __name__ == "__main__":
    print(json.dumps(build(), indent=1))
