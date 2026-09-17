from __future__ import annotations

import copy

import pytest
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9_receipts as producer
from scripts.r1_d10a_review_core import digest
from scripts.r1_d10c_endpoints import catalog_from_rows, construct, near_key, role_plan

from tests.revision_v1.test_r1_d9_receipts import COUNTS, REG, fixture
from tests.revision_v1.test_r1_d10a_review import Tokenizer


def setup():
    register, rows, evidence = fixture()
    plan = {"rows": []}
    for ds in core.DATASETS:
        for row in rows[ds]:
            row.update(relation_id="P1", locality_prompts=["a held-out query?"])
            plan["rows"].append(role_plan(row, "old", Tokenizer(), {"max_context": 128}))
            for meta in register["candidates"][ds]:
                if meta["item_id"] == row["item_id"]:
                    meta["payload_sha256"] = digest(row)
            for disp in evidence["dispositions"]:
                if disp["item_id"] == row["item_id"]:
                    disp["payload_sha256"] = digest(row)
    usable, _ = core.review_candidates(register, rows, evidence, counts=COUNTS, realizations=2)
    allocation = core.allocate(
        usable, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2
    )
    reservation = core.reservation_document(allocation, REG)
    reservation.update(producer.paired_orders(reservation))
    ids = next(
        g["items"]
        for g in reservation["allocations"]
        if g["dataset"] == "mquake" and g["role"] == "edits"
    )
    case = {
        "composition_id": "case",
        "verified_source": "MQuAKE",
        "source_case_sha256": "s" * 64,
        "dependencies": [{"item_id": r["item_id"]} for r in ids],
    }
    catalog = catalog_from_rows([case])
    reservation["planned_compositions"] = producer.planned_compositions(reservation, catalog)
    cells = [
        {"condition": condition, "dataset": ds, "realization": real, "order": order}
        for condition in ("R1_learned_ff", "matched_update")
        for ds in core.DATASETS
        for real in range(2)
        for order in range(100, 105)
    ]
    drift = {"expected_positions": 2, "windows": [[2, 3, 4]]}
    return reservation, cells, catalog, plan, drift


def build(*args):
    return construct(*args, counts=COUNTS, realizations=2, locality_count=1, checkpoints=(1, 2))


def test_construction_exact_d9_schema_paired_orders_and_source_roles():
    r, cells, catalog, plan, drift = setup()
    payloads, population, report = build(r, cells, catalog, plan, drift)
    assert len(payloads) == len(population["cells"]) == 60
    assert report["unique_payloads"] == 30 and report["missing"] == []
    for data in payloads.values():
        assert len(data["endpoints"]["near_miss"]["rows"]) == 1
        assert len(data["endpoints"]["revision"]["rows"][0]["versions"]) == 2
    assert len({digest(p["endpoints"]) for p in payloads.values()}) == 6
    assert report["model_calls"] == report["draws"] == report["seals"] == 0


def test_missing_neighbour_retains_planned_denominator():
    r, cells, catalog, plan, drift = setup()
    neighbours = {
        x["item_id"]
        for g in r["allocations"]
        if g["role"] == "near_miss_neighbour"
        for x in g["items"]
    }
    changed = {}
    for group in r["allocations"]:
        for meta, row in zip(group["items"], group["records"], strict=True):
            if row["item_id"] in neighbours:
                row.update(relation_id="P2", prompt="different " + row["prompt"])
                meta["payload_sha256"] = digest(row)
                changed[row["item_id"]] = row
    for row in plan["rows"]:
        if row["item_id"] in neighbours:
            source = changed[row["item_id"]]
            row.update(near_key=near_key(source), payload_sha256=digest(source))
    payloads, population, report = build(r, cells, catalog, plan, drift)
    assert len(report["missing"]) == 6
    assert all(len(p["endpoints"]["near_miss"]) == 1 for p in population["cells"].values())
    assert all(not p["endpoints"]["near_miss"]["rows"] for p in payloads.values())


@pytest.mark.parametrize("fault", ["role_hash", "draw_order", "catalog"])
def test_construction_refuses_binding_drift(fault):
    args = list(setup())
    if fault == "role_hash":
        for row in args[3]["rows"]:
            row["payload_sha256"] = "changed"
    elif fault == "draw_order":
        args[0]["orders"]["zsre:0:100"] = []
    else:
        args[2]["mquake"] = []
    with pytest.raises(ValueError):
        build(*args)


def test_near_keys_and_revision_answers_are_source_based():
    row = {
        "dataset": "zsre",
        "subject": "Person A",
        "prompt": "Where did Person A live?",
        "item_id": "a",
        "answer": "Paris",
        "aliases": ["Paris"],
    }
    assert near_key(row) == "question_template:where did {subject} live?"
    assert near_key({**row, "prompt": "Person A and Person A?"}) is None
    same = role_plan(row, " PARIS ", Tokenizer(), {"max_context": 128})
    assert "revision" not in same["roles"]
    changed = role_plan(row, "London", Tokenizer(), {"max_context": 128})
    assert changed["revision_versions"][1]["answer"] == row["answer"]


def test_catalog_retains_source_unavailability_and_refuses_duplicate_ids():
    row = {
        "composition_id": "a",
        "verified_source": "MQuAKE",
        "source_case_sha256": "s" * 64,
        "all_rewrite_dependencies_available": False,
        "dependencies": [{"item_id": "unavailable"}],
    }
    assert catalog_from_rows([row])["mquake"] == [row]
    with pytest.raises(ValueError, match="duplicate"):
        catalog_from_rows([row, copy.deepcopy(row)])
