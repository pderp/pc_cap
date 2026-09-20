"""Realization-3 seam: deterministic streams, distinct subjects and tamper refusal."""

import copy

import pytest
from tests.revision_v1.test_r1_d9f_allocation import COUNTS, REG, pool

from aw import r_extension as r


def layout():
    return {
        ds: dict(realizations=[3], roles_per_realization=COUNTS, checkpoints=[100, 300, 1000])
        for ds in r.DATASETS
    }


def draw(rows=None):
    rows = rows or {ds: rr for ds, rr in pool().items() if ds in r.DATASETS}
    return r.family_allocate(
        rows,
        seed=17,
        register_sha256=REG["sha256"],
        counts=COUNTS,
        layout=layout(),
        mode="family_coordinated",
    )


def test_deterministic_disjoint_full_pairs_and_realization_coordinates():
    a = draw()
    rows = {ds: list(reversed(rr)) for ds, rr in pool().items() if ds in r.DATASETS}
    assert a == draw(rows)
    assert {g["realization"] for g in a["allocations"]} == {3}
    reservation = r.family.reservation_document(a, REG)
    r.audit_reservations(reservation, layout=layout())
    r.family.audit(reservation)
    assert all(v["matched"] == 3 and not v["missing"] for v in a["near_pair_receipts"].values())
    for receipt in a["rng_substreams"].values():
        assert receipt["coordinates"]["realization"] == 3
    orders = r.paired_orders(reservation)
    assert len(orders["orders"]) == 10
    assert all(":3:" in k for k in orders["orders"])


@pytest.mark.parametrize("field", ["item_id", "fact_id", "_entity", "_canonical_subject"])
def test_each_prior_identity_excludes_independently(field):
    rows = {ds: rr[:1] for ds, rr in pool().items() if ds in r.DATASETS}
    names = {
        "item_id": "item_id",
        "fact_id": "fact_id",
        "_entity": "entity_id",
        "_canonical_subject": "canonical_subject",
    }
    meta = {v: "unrelated-" + v for v in names.values()}
    meta[names[field]] = rows["zsre"][0][field]
    previous = dict(allocations=[dict(items=[meta])])
    out = r.exclude_reserved(rows, previous)
    assert not out["zsre"] and len(out["counterfact"]) == 1


def test_tampered_row_and_duplicate_reservation_rejected():
    reservation = r.family.reservation_document(draw(), REG)
    bad = copy.deepcopy(reservation)
    bad["allocations"][0]["records"][0]["answer"] = "changed"
    with pytest.raises(ValueError, match="content"):
        r.audit_reservations(bad, layout=layout())
    bad = copy.deepcopy(reservation)
    bad["allocations"][0]["items"][0]["entity_id"] = bad["allocations"][1]["items"][0]["entity_id"]
    with pytest.raises(ValueError, match="duplicate"):
        r.audit_reservations(bad, layout=layout())


def test_reject_primary_coordinate_and_capacity_shortfall():
    bad = layout()
    bad["zsre"]["realizations"] = [0]
    with pytest.raises(ValueError, match="realization 3"):
        r.resolve_layout(bad)
    with pytest.raises(ValueError, match="capacity"):
        draw({ds: rr[:5] for ds, rr in pool().items() if ds in r.DATASETS})


def test_sorted_json_layout_roundtrip_preserves_role_traversal():
    import json

    saved = json.loads(json.dumps(layout(), sort_keys=True))
    assert list(r.resolve_layout(saved)["zsre"]["roles_per_realization"]) == list(r.ROLES)
    reservation = r.family.reservation_document(draw(), REG)
    saved_reservation = json.loads(json.dumps(reservation, sort_keys=True))
    r.audit_reservations(saved_reservation, layout=saved)
