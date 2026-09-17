"""No duplicated subject capacity, cross-role borrowing or manufactured pairs."""

import copy

import pytest
from scripts.r1_d10f_near_feasibility import feasibility


def fixture():
    dispositions, rows = [], []
    for i in range(5):
        dispositions.append(
            dict(
                dataset="mquake",
                item_id=str(i),
                entity_id=str(i),
                payload_sha256=str(i),
                preteacher_eligible=True,
            )
        )
        rows.append(
            dict(
                dataset="mquake",
                item_id=str(i),
                payload_sha256=str(i),
                near_key="family",
                roles=["edits", "outside", "near_miss_support", "near_miss_neighbour", "revision"],
            )
        )
    return dict(dispositions=dispositions), dict(rows=rows)


def test_exact_disjoint_capacity_and_missingness():
    e, p = fixture()
    summary, detail = feasibility(e, p)
    q = summary["mquake"]
    assert q["maximum_disjoint_pairs"] == 2
    assert not q["near_pair_capacity_sufficient"]
    assert q["requested_pairs"] == 300
    assert not q["joint_preteacher_existence_proven"]
    assert detail["families"][0]["possible_unordered_pairs"] == 10
    assert len(detail["existence_witnesses"]) == 2


def test_repeated_entity_in_other_family_cannot_inflate_capacity():
    e, p = fixture()
    d, r = copy.deepcopy(e["dispositions"][0]), copy.deepcopy(p["rows"][0])
    d["item_id"] = r["item_id"] = "extra"
    r["near_key"] = "other family"
    e["dispositions"].append(d)
    p["rows"].append(r)
    summary, detail = feasibility(e, p)
    assert summary["mquake"]["subjects"] == 5
    assert summary["mquake"]["maximum_disjoint_pairs"] == 2
    assert len(detail["families"]) == 1


def test_unknown_or_one_sided_family_cannot_supply_pairs():
    e, p = fixture()
    p["rows"][0]["near_key"] = None
    p["rows"][1]["roles"].remove("near_miss_neighbour")
    summary, _ = feasibility(e, p)
    assert summary["mquake"]["maximum_disjoint_pairs"] == 1


def test_cross_dataset_duplicate_and_payload_mismatch_refuse():
    e, p = fixture()
    e["dispositions"][1]["entity_id"] = "0"
    e["dispositions"][1]["dataset"] = p["rows"][1]["dataset"] = "zsre"
    with pytest.raises(ValueError, match="global subject collision"):
        feasibility(e, p)
    e, p = fixture()
    p["rows"][0]["payload_sha256"] = "changed"
    with pytest.raises(ValueError, match="payload mismatch"):
        feasibility(e, p)
