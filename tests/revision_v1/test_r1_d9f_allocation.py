"""Outcome-independent paired allocation and its admission gate."""

import copy

import pytest
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9f_allocation as family
from scripts.r1_d9_layouts import entry
from scripts.r1_d9e_near_family import pair_reserved

REG = {"path": "synthetic", "sha256": "a" * 64}
COUNTS = dict(edits=2, outside=1, near_miss_support=3, near_miss_neighbour=3, revision=1)


def pool(*, sparse=False):
    result = {}
    for ds in core.DATASETS:
        result[ds] = []
        for i in range(90):
            iid = f"{ds}-{i:03d}"
            f = i // 2 if sparse else 0
            result[ds].append(
                dict(
                    dataset=ds,
                    item_id=iid,
                    fact_id=iid,
                    subject=iid,
                    prompt=f"family {f}: where is {iid}?",
                    answer="unused",
                    relation_id=f"P{f}",
                    source_record_sha256="c" * 64,
                    _entity=iid,
                    _canonical_subject=iid,
                    _roles=list(COUNTS),
                    _stratum="one",
                )
            )
    return result


def draw(rows, mode="family_coordinated", seed=17):
    return family.allocate(
        rows, seed=seed, register_sha256=REG["sha256"], counts=COUNTS, realizations=2, mode=mode
    )


def test_independent_identity_and_paired_backbone_and_stream_replay():
    rows = pool(sparse=True)
    baseline = core.allocate(
        rows, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2
    )
    assert draw(rows, "independent") == baseline
    paired = draw(rows)
    assert paired == draw({ds: list(reversed(r)) for ds, r in rows.items()})
    assert paired == draw(rows)
    assert paired != draw(rows, seed=18)

    def keep(a):
        return [g for g in a["allocations"] if g["role"] not in (family.SUPPORT, family.NEIGHBOUR)]

    assert keep(baseline) == keep(paired)
    r = family.reservation_document(paired, REG)
    core.audit_reservations(r, counts=COUNTS, realizations=2)
    family.audit(r)
    assert len(r["near_pair_receipts"]) == 6
    assert all(c["matched"] == 3 and not c["missing"] for c in r["near_pair_receipts"].values())
    assert all(c["initial_state"] != c["final_state"] for c in r["near_pair_receipts"].values())


def test_sparse_singleton_shortfall_retains_full_role_and_endpoint_inventory():
    rows = pool(sparse=True)
    for rr in rows.values():
        for i, r in enumerate(rr):
            r["relation_id"] = f"unique{i}"
            r["prompt"] = f"unique{i}: where is {r['subject']}?"
    result = draw(rows)
    for ds in core.DATASETS:
        for real in range(2):
            roles = {
                g["role"]: g["records"]
                for g in result["allocations"]
                if g["dataset"] == ds and g["realization"] == real
            }
            section = pair_reserved(
                roles[family.SUPPORT],
                roles[family.NEIGHBOUR],
                [f"{ds}:{real}:near:{i}" for i in range(3)],
                dataset=ds,
            )
            assert len(section["missing"]) == 3 and not section["rows"]
    r = family.reservation_document(result, REG)
    core.audit_reservations(r, counts=COUNTS, realizations=2)
    family.audit(r)
    assert all(c["planned"] == 3 and c["matched"] == 0 for c in r["near_pair_receipts"].values())


def test_many_pairs_may_share_one_family():
    result = draw(pool())
    assert all(
        c["matched"] == 3 and c["source_family_count"] == 1
        for c in result["near_pair_receipts"].values()
    )


def test_role_exclusive_pairing_does_not_consume_dual_row_first():
    rows = pool()["counterfact"][:6]
    for r, roles in zip(
        rows,
        [[family.SUPPORT]] * 2
        + [[family.NEIGHBOUR]] * 2
        + [[family.SUPPORT, family.NEIGHBOUR]] * 2,
        strict=True,
    ):
        r["_roles"] = roles
    rng, _ = family.stream(17, REG["sha256"], "counterfact", 0, "test")
    pairs = family.units(rows, rng)
    assert len(pairs) == 3
    assert len({r["item_id"] for _, a, b in pairs for r in (a, b)}) == 6


def test_admission_default_and_missing_decision_refusal():
    assert family.admitted_mode({}, {}) == "independent"
    rng = dict(near_allocation="family_coordinated", near_allocation_contract=family.CONTRACT)
    cfg = dict(near_allocation="family_coordinated")
    with pytest.raises(ValueError, match="DEC-062"):
        family.admitted_mode(rng, cfg)
    approved = dict(
        decision="DEC-062",
        near_allocation="family_coordinated",
        allocation_contract=family.CONTRACT,
        lead_approved=True,
        status="closed",
    )
    assert family.admitted_mode(rng, cfg, approved) == "family_coordinated"
    for field in ["status", "lead_approved", "allocation_contract", "decision"]:
        bad = copy.deepcopy(approved)
        bad[field] = None
        with pytest.raises(ValueError):
            family.admitted_mode(rng, cfg, bad)
    with pytest.raises(ValueError, match="differs"):
        family.admitted_mode(rng, {})


def test_pair_inventory_and_stream_tampering_rejected():
    result = family.reservation_document(draw(pool()), REG)
    for mutate in [
        lambda r: next(iter(r["near_pair_receipts"].values())).update(matched=0),
        lambda r: next(iter(r["near_pair_receipts"].values())).update(derived_seed=0),
        lambda r: next(iter(r["near_pair_receipts"].values()))["selected_pair_units"].pop(),
    ]:
        bad = copy.deepcopy(result)
        mutate(bad)
        with pytest.raises(ValueError):
            family.audit(bad)


def test_outcome_fields_do_not_control_selection():
    rows = pool(sparse=True)

    def ids(r):
        return [[x["item_id"] for x in g["records"]] for g in r["allocations"]]

    before = draw(rows)
    for rr in rows.values():
        for i, r in enumerate(rr):
            r.update(answer=f"new {i}", observed_score=i, cap_answer="ignored")
    assert ids(before) == ids(draw(rows))


def test_per_dataset_layouts_and_global_disjointness():
    rows = pool()
    layout = {
        d: entry(
            {**COUNTS, "edits": 1 if d == "mquake" else 2},
            range(2),
            [1] if d == "mquake" else [1, 2],
        )
        for d in core.DATASETS
    }
    result = family.allocate(
        rows, seed=17, register_sha256=REG["sha256"], layout=layout, mode="family_coordinated"
    )
    reservation = family.reservation_document(result, REG)
    core.audit_reservations(reservation, layout=layout)
    family.audit(reservation)
    rows["counterfact"][0]["_entity"] = rows["zsre"][0]["_entity"]
    with pytest.raises(ValueError, match="globally unique"):
        family.allocate(
            rows, seed=17, register_sha256=REG["sha256"], layout=layout, mode="family_coordinated"
        )
