"""All reserved versions are unioned; changed teacher rows cannot pass through."""

import copy

import pytest
from scripts.r1_d1g_mquake_exposure_supplement import union_training


def test_overlapping_training_versions_union_without_double_counting():
    binding = {"path": "pool", "sha256": "a" * 64}
    rows = [{"item_id": f"i{i}", "subject": f"s{i}"} for i in range(3)]
    docs = [
        {"sources_sha256": binding, "items": rows[:2]},
        {"sources_sha256": binding, "items": rows},
    ]
    original = copy.deepcopy(docs)
    got = union_training(docs, {r["item_id"]: r for r in rows}, binding)
    assert got == rows and docs == original


@pytest.mark.parametrize("kind", ["binding", "payload", "unknown"])
def test_changed_source_or_row_refused(kind):
    binding = {"path": "pool", "sha256": "a" * 64}
    row = {"item_id": "a", "subject": "a"}
    doc = {"sources_sha256": binding, "items": [row]}
    known = {"a": copy.deepcopy(row)}
    if kind == "binding":
        doc["sources_sha256"] = {}
    elif kind == "payload":
        row["subject"] = "changed"
    else:
        row["item_id"] = "unknown"
    with pytest.raises(ValueError):
        union_training([doc], known, binding)
