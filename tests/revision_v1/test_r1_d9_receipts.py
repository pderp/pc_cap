"""Synthetic clearance/draw/seal; never read or select real confirmation rows."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from scripts import r1_d9_receipt_core as c
from scripts import r1_d9_receipts as producer

COUNTS = dict(edits=2, outside=1, near_miss_support=1, near_miss_neighbour=1, revision=1)
REG = {"path": "synthetic-register.json", "sha256": "a" * 64}


def fixture():
    register = {"schema_version": 6, "candidates": {}}
    rows = {}
    evidence = {
        "policy": c.POLICY,
        "model_limits": {"vocabulary": 64, "max_context": 128},
        "tokenizer_sha256": "b" * 64,
        "base_tensor_sha256": "c" * 64,
        **dict.fromkeys(c.REVIEW_FLAGS, True),
        "dispositions": [],
    }
    for ds in c.DATASETS:
        register["candidates"][ds], rows[ds] = [], []
        for n in range(24):
            iid = ds + str(n)
            row = dict(
                item_id=iid,
                fact_id=iid,
                subject=iid,
                dataset=ds,
                prompt=iid + "?",
                answer="new",
                aliases=["new"],
                paraphrases=[iid + " again?"],
                prompt_ids=[2],
                answer_ids=[3, 63],
                source_record_sha256="d" * 64,
            )
            meta = dict(
                item_id=iid,
                canonical_subject=iid,
                payload_sha256=c.content_digest(row),
                source_record_sha256="d" * 64,
            )
            register["candidates"][ds].append(meta)
            rows[ds].append(row)
            evidence["dispositions"].append(
                dict(
                    meta,
                    dataset=ds,
                    entity_id=iid,
                    decision="eligible",
                    reasons=[],
                    roles=list(COUNTS),
                    alias_clear=True,
                    context_clear=True,
                    exposure_clear=True,
                    teacher_pass=True,
                    tokens_pass=True,
                    base_tensor_sha256=evidence["base_tensor_sha256"],
                    tokenizer_sha256=evidence["tokenizer_sha256"],
                )
            )
    return register, rows, evidence


def cleared():
    return c.review_candidates(*fixture(), counts=COUNTS, realizations=2)[0]


def test_clearance_every_disposition_and_role_capacity():
    r, rows, e = fixture()
    eligible, counts = c.review_candidates(r, rows, e, counts=COUNTS, realizations=2)
    assert all(v["reviewed_items"] == 24 for v in counts.values())
    assert all(len(v) == 24 for v in eligible.values())
    for d in e["dispositions"]:
        d["roles"] = ["edits"]
    with pytest.raises(ValueError, match="capacity"):
        c.review_candidates(r, rows, e, counts=COUNTS, realizations=2)


@pytest.mark.parametrize(
    "fault",
    [
        "missing",
        "duplicate",
        "unresolved",
        "alias",
        "tokenizer",
        "payload",
        "teacher",
        "cross_dataset",
    ],
)
def test_clearance_refuses_incomplete_or_changed_evidence(fault):
    r, rows, e = fixture()
    d = e["dispositions"][0]
    if fault == "missing":
        e["dispositions"].pop()
    elif fault == "duplicate":
        e["dispositions"].append(copy.deepcopy(d))
    elif fault == "unresolved":
        d["decision"] = "pending"
    elif fault == "alias":
        d["alias_clear"] = False
    elif fault == "tokenizer":
        d["tokenizer_sha256"] = "x"
    elif fault == "payload":
        rows["zsre"][0]["answer"] = "changed"
    elif fault == "teacher":
        d["teacher_pass"] = False
    elif fault == "cross_dataset":
        e["dispositions"][24]["entity_id"] = d["entity_id"]
    with pytest.raises(ValueError):
        c.review_candidates(r, rows, e, counts=COUNTS, realizations=2)


def test_draw_deterministic_independent_register_bound_and_disjoint():
    rows = cleared()
    a = c.allocate(rows, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2)
    assert a == c.allocate(
        rows, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2
    )
    reordered = {ds: list(reversed(v)) for ds, v in rows.items()}
    assert a == c.allocate(
        reordered, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2
    )
    b = c.allocate(rows, seed=17, register_sha256="f" * 64, counts=COUNTS, realizations=2)
    assert a["rng_substreams"] != b["rng_substreams"]
    assert len({v["derived_seed"] for v in a["rng_substreams"].values()}) == len(
        a["rng_substreams"]
    )
    reservations = c.reservation_document(a, REG)
    c.audit_reservations(reservations, counts=COUNTS, realizations=2)
    orders = producer.paired_orders(reservations)
    assert len(orders["orders"]) == 30
    for g in reservations["allocations"]:
        if g["role"] == "edits":
            values = [
                orders["orders"][f"{g['dataset']}:{g['realization']}:{o}"] for o in range(100, 105)
            ]
            assert all(set(v) == {r["item_id"] for r in g["items"]} for v in values)


@pytest.mark.parametrize("fault", ["capacity", "duplicate", "seed", "hash"])
def test_draw_fails_before_partial_receipt(fault):
    rows = cleared()
    seed = 17
    h = REG["sha256"]
    if fault == "capacity":
        rows["mquake"] = rows["mquake"][:5]
    elif fault == "duplicate":
        rows["mquake"][0]["_entity"] = rows["zsre"][0]["_entity"]
    elif fault == "seed":
        seed = True
    elif fault == "hash":
        h = "bad"
    with pytest.raises(ValueError):
        c.allocate(rows, seed=seed, register_sha256=h, counts=COUNTS, realizations=2)


def seal_fixture(reviewed_rows=None):
    a = c.allocate(
        reviewed_rows if reviewed_rows is not None else cleared(),
        seed=17,
        register_sha256=REG["sha256"],
        counts=COUNTS,
        realizations=2,
    )
    r = c.reservation_document(a, REG)
    r.update(producer.paired_orders(r))
    groups = c.audit_reservations(r, counts=COUNTS, realizations=2)
    cells, payloads, population = [], {}, {"cells": {}}
    for ds in c.DATASETS:
        for real in range(2):
            g = {role: groups[ds, str(real), role]["records"] for role in COUNTS}
            for order in range(100, 105):
                cell = dict(condition="R1_learned_ff", dataset=ds, realization=real, order=order)
                cid = c.coordinate_id(cell)
                cells.append(cell)
                pool = [x for rr in g.values() for x in rr]
                byid = {x["item_id"]: x for x in pool}
                data = {
                    "items": [byid[i] for i in r["orders"][f"{ds}:{real}:{order}"]],
                    "pool_rows": pool,
                    "endpoints": {
                        "locality": {
                            "expected_ids": ["loc"],
                            "rows": [{"item_id": "loc", "prompt": "loc?"}],
                        },
                        "unseen": {
                            "expected_ids": [x["item_id"] for x in g["outside"]],
                            "rows": g["outside"],
                        },
                        "near_miss": {"expected_ids": ["near"], "rows": []},
                        "revision": {"expected_ids": ["revision"], "rows": []},
                        "composition": {"expected_ids": [], "rows": []},
                        "drift": {"expected_positions": 2, "windows": [[2, 3, 4]]},
                    },
                }
                payloads[cid] = data
                population["cells"][cid] = c.planned_population(data)
    return r, cells, payloads, population


def validate(r, cells, payloads, population):
    return c.validate_seal(
        r,
        cells,
        payloads,
        population,
        counts=COUNTS,
        realizations=2,
        checkpoints=(1, 2),
        locality_count=1,
    )


def test_seal_preserves_missing_denominators_and_all_paired_cells():
    r, cells, payloads, population = seal_fixture()
    result = validate(r, cells, payloads, population)
    assert len(result) == 30
    for p in population["cells"].values():
        assert p["endpoints"]["near_miss"] == ["near"]
        assert p["endpoints"]["revision"] == ["revision"]


@pytest.mark.parametrize(
    "fault",
    [
        "missing_cell",
        "edit",
        "pool",
        "outside",
        "duplicate_role",
        "population",
        "composition",
        "condition_drift",
        "order_endpoints",
    ],
)
def test_seal_rejects_changed_population_or_content(fault):
    r, cells, payloads, population = seal_fixture()
    first = next(iter(payloads))
    p = payloads[first]
    if fault == "missing_cell":
        del payloads[first]
    elif fault == "edit":
        p["items"][0]["answer"] = "altered"
    elif fault == "pool":
        p["pool_rows"] = p["pool_rows"][:-1]
    elif fault == "outside":
        p["endpoints"]["unseen"]["expected_ids"] = [p["items"][0]["item_id"]]
    elif fault == "duplicate_role":
        r["allocations"][1] = copy.deepcopy(r["allocations"][0])
    elif fault == "population":
        population["cells"][first]["paraphrase_counts"][0] = 99
    elif fault == "composition":
        p["endpoints"]["composition"] = {
            "expected_ids": ["x"],
            "rows": [{"composition_id": "x", "dependencies": [{"item_id": "absent"}]}],
        }
    elif fault == "condition_drift":
        cell = dict(cells[0], condition="v0_stable")
        cells.append(cell)
        cid = c.coordinate_id(cell)
        q = copy.deepcopy(p)
        q["items"].reverse()
        payloads[cid] = q
        population["cells"][cid] = c.planned_population(q)
    elif fault == "order_endpoints":
        q = copy.deepcopy(p)
        q["endpoints"]["locality"]["rows"][0]["prompt"] = "different?"
        payloads[first] = q
        population["cells"][first] = c.planned_population(q)
    with pytest.raises(ValueError):
        validate(r, cells, payloads, population)


def test_dry_run_missing_receipts_never_draws(monkeypatch):
    spec = json.loads((producer.ROOT / "docs/tasks/R1-58c-dry-inputs-v2.json").read_text())

    def forbidden(*a, **k):
        raise AssertionError("dry run attempted a draw")

    monkeypatch.setattr(c, "allocate", forbidden)
    result, _ = producer.prepare(spec, "draw")
    assert result["blocked"] and not result["rng_used"] and result["draws_emitted"] == 0
    with pytest.raises(PermissionError):
        producer.execute(spec, "draw")
    with pytest.raises(PermissionError):
        producer.execute(spec, "seal")


def test_unapproved_receipt_cannot_authorize(monkeypatch):
    spec = {
        "register": REG,
        "receipts": {"clearance_authorization": {"path": "fake", "sha256": "a" * 64}},
    }
    monkeypatch.setattr(
        producer,
        "read_metadata",
        lambda b: {"status": "closed", "lead_approved": False, "register": REG},
    )
    with pytest.raises(ValueError, match="unapproved"):
        producer.admitted_receipts(spec, "clearance")


def test_validated_reserved_item_executes_on_tinybase():
    from dataclasses import replace

    from pccap.harness.ledger import Ledger
    from pccap.revision_v1.endpoints_composition import as_edit
    from pccap.revision_v1.stage4_adapters import build_adapter
    from tests.revision_v1.test_learner_cpu import _cfg
    from tests.revision_v1.test_stage4_cell import CAL, TinyTok
    from tests.revision_v1.tiny_base import TinyBase

    r, cells, payloads, population = seal_fixture()
    validate(r, cells, payloads, population)
    row = copy.deepcopy(next(iter(payloads.values()))["items"][0])
    # This model smoke retokenizes fixture text; production review binds exact IDs.
    row.pop("prompt_ids")
    row.pop("answer_ids")
    tok = TinyTok()
    item = as_edit(row, tok)
    cfg = _cfg()
    cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
    adapter = build_adapter(
        "R1_learned_ff", TinyBase(), Ledger(), calibration=CAL, synthetic=True, revision_config=cfg
    )
    outcome = adapter.update_item(item)
    assert not str(outcome.code).startswith("resource")
    assert adapter.export_state().content_hash()


def test_three_owner_writers_keep_receipt_last_and_match_preflight(monkeypatch, tmp_path):
    """Exercise actual serialization/receipt schemas with isolated synthetic resources."""
    import uuid

    r, cells, payloads, population = seal_fixture()
    root = producer.ROOT / "logs/r1_round21/synthetic_tests" / uuid.uuid4().hex
    assets = producer.ASSETS / "test_scratch/r1_round21" / root.name
    root.mkdir(parents=True)
    # Patch only root boundaries and authorization fixtures, never source/result files.
    monkeypatch.setattr(producer, "ROOT", root)
    monkeypatch.setattr(producer, "ASSETS", assets)
    monkeypatch.setattr(producer, "ref", lambda p: {"path": str(p), "sha256": "a" * 64})
    monkeypatch.setattr(producer, "verify_register", lambda r: r)
    monkeypatch.setattr(producer, "read_metadata", lambda b, **kwargs: {})
    monkeypatch.setattr(producer, "admitted_receipts", lambda s, st: {})
    monkeypatch.setattr(producer, "sha", lambda p: "a" * 64)
    monkeypatch.setattr(producer, "draw_value", lambda s, rr: r)
    monkeypatch.setattr(
        producer,
        "seal_values",
        lambda s, rr, m: (
            dict(r, mode="content_sealed_fact_reservations"),
            payloads,
            population,
            validate(r, cells, payloads, population),
        ),
    )
    spec = {
        "register": REG,
        "matrix": {},
        "protocol": {},
        "receipts": dict.fromkeys(
            [
                "clearance_authorization",
                "draw_authorization",
                "seal_authorization",
                "joint_clearance",
                "draw_receipt",
            ],
            {},
        ),
    }
    spec["d9"] = {
        stage: {
            "receipt_output": str(root / f"docs/tasks/{stage}.json"),
            "resource_output": str(assets / f"runs/pc_cap/R1/{stage}"),
            "master_seed": 17,
        }
        for stage in ("clearance", "draw", "seal")
    }
    state = {
        "receipts": {},
        "matrix": {},
        "clearance": {"counts": {ds: {"usable_subjects": 4050} for ds in c.DATASETS}},
    }
    monkeypatch.setattr(
        producer,
        "prepare",
        lambda s, st: ({"blocked": [], "task": "R1-D9", "request_sha256": "a" * 64}, state),
    )
    for stage in ("clearance", "draw", "seal"):
        result = producer.execute(spec, stage)
        receipt = json.loads(Path(result["receipt"]["path"]).read_text())
        producer.check_receipt(producer.RECEIPT_NAMES[stage], receipt, spec)
        assert receipt["launch_authorized"] is False
        assert Path(spec["d9"][stage]["resource_output"]).exists()
        with pytest.raises(ValueError, match="new"):
            producer.execute(spec, stage)


@pytest.mark.parametrize("fault", [None, "missing_cell", "orders", "demand", "extension"])
def test_exact_v51_matrix_population_required(fault):
    matrix = json.loads((producer.ROOT / "manifests/revision_v1/run_matrix_v5_1.json").read_text())
    if fault == "missing_cell":
        matrix["cells"].pop()
    elif fault == "orders":
        matrix["axes"]["orders"].pop()
    elif fault == "demand":
        matrix["population"]["required_subjects_each_dataset"] = 3750
    elif fault == "extension":
        matrix["extension"]["cells"].pop()
    if fault is None:
        producer.check_matrix_layout(matrix)
    else:
        with pytest.raises(ValueError):
            producer.check_matrix_layout(matrix)


def test_seal_rejects_duplicate_revision_fact(monkeypatch):
    monkeypatch.setitem(COUNTS, "revision", 2)
    r, cells, payloads, population = seal_fixture()
    for cell in cells:
        cid = c.coordinate_id(cell)
        group = next(
            g
            for g in r["allocations"]
            if g["dataset"] == cell["dataset"]
            and g["realization"] == cell["realization"]
            and g["role"] == "revision"
        )
        original = group["records"][0]
        payloads[cid]["endpoints"]["revision"] = {
            "expected_ids": ["revision-a", "revision-b"],
            "rows": [
                {
                    "item_id": iid,
                    "dataset": cell["dataset"],
                    "fact_id": original["fact_id"],
                    "prompt": original["prompt"],
                }
                for iid in ("revision-a", "revision-b")
            ],
        }
        population["cells"][cid] = c.planned_population(payloads[cid])
    with pytest.raises(ValueError, match="revision role reused"):
        validate(r, cells, payloads, population)


def test_seal_rejects_near_miss_dataset_change():
    r, cells, payloads, population = seal_fixture()
    cell = cells[0]
    cid = c.coordinate_id(cell)
    roles = {
        g["role"]: g["records"]
        for g in r["allocations"]
        if g["dataset"] == cell["dataset"] and g["realization"] == cell["realization"]
    }
    own, other = roles["near_miss_support"][0], roles["near_miss_neighbour"][0]
    payloads[cid]["endpoints"]["near_miss"]["rows"] = [
        dict(
            item_id="near",
            dataset="wrong",
            edit_item_id=own["item_id"],
            neighbour_item_id=other["item_id"],
            edit_prompt=own["prompt"],
            edit_answer=own["answer"],
            neighbour_prompt=other["prompt"],
        )
    ]
    with pytest.raises(ValueError, match="endpoint dataset differs"):
        validate(r, cells, payloads, population)


@pytest.mark.parametrize("change_after_approval", [False, True])
def test_owner_approval_binds_exact_producer_request(monkeypatch, change_after_approval):
    spec = {
        "register": REG,
        "matrix": {"path": "matrix", "sha256": "b" * 64},
        "protocol": {"path": "protocol", "sha256": "c" * 64},
        "d9": {"clearance": {"evidence": {"path": "synthetic-review", "sha256": "d" * 64}}},
        "receipts": {
            "clearance_authorization": {"path": "synthetic-authorization", "sha256": "e" * 64}
        },
    }
    receipt = {
        "status": "closed",
        "lead_approved": True,
        "register": REG,
        "operation": "clearance",
        "request_sha256": producer.contract(spec, "clearance"),
    }
    monkeypatch.setattr(producer, "read_metadata", lambda b: copy.deepcopy(receipt))
    if change_after_approval:
        spec["d9"]["clearance"]["evidence"]["sha256"] = "f" * 64
        with pytest.raises(ValueError, match="exact producer request"):
            producer.admitted_receipts(spec, "clearance")
    else:
        assert producer.admitted_receipts(spec, "clearance")["clearance_authorization"] == receipt
