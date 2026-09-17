"""Heterogeneous populations retain RNG, Hall and exact source/role refusals."""

import copy
import json
from pathlib import Path

import pytest
from scripts import r1_d9_layouts as layouts
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9_receipts as producer
from scripts.r1_58c_draw_seal_preflight import check_receipt
from scripts.r1_d10c_endpoints import construct
from scripts.r1_d10d_options import layouts as option_layouts

from tests.revision_v1.test_r1_d9_receipts import COUNTS, REG, fixture
from tests.revision_v1.test_r1_d10c_endpoints import setup


def small_layout():
    return {
        ds: layouts.entry(
            {**COUNTS, "edits": 1 if ds == "mquake" else 2},
            range(2),
            [1] if ds == "mquake" else [1, 2],
        )
        for ds in core.DATASETS
    }


def test_production_demands_exact_and_source_order_irrelevant():
    assert layouts.production("D") == option_layouts("D")
    malformed = layouts.production("D")
    malformed["mquake"]["demand_subjects"] = 1950.0
    with pytest.raises(ValueError, match="demand fields"):
        layouts.admitted(malformed)
    layout = small_layout()
    rows, _ = core.review_candidates(*fixture(), layout=layout)
    a = core.allocate(rows, seed=17, register_sha256=REG["sha256"], layout=layout)
    b = core.allocate(
        {d: list(reversed(r)) for d, r in rows.items()},
        seed=17,
        register_sha256=REG["sha256"],
        layout=layout,
    )
    assert a == b
    legacy = core.allocate(
        rows, seed=17, register_sha256=REG["sha256"], counts=COUNTS, realizations=2
    )
    assert [g for g in a["allocations"] if g["dataset"] != "mquake"] == [
        g for g in legacy["allocations"] if g["dataset"] != "mquake"
    ]
    assert {k: v for k, v in a["rng_substreams"].items() if not k.startswith("mquake")} == {
        k: v for k, v in legacy["rng_substreams"].items() if not k.startswith("mquake")
    }
    r = core.reservation_document(a, REG)
    core.audit_reservations(r, layout=layout)
    assert len(r["allocations"]) == 30
    r["dataset_layouts"]["mquake"]["roles_per_realization"]["edits"] = 2
    with pytest.raises(ValueError, match="layout"):
        core.audit_reservations(r, layout=layout)


@pytest.mark.parametrize("fault", ["bool", "demand", "cadence", "dataset", "realization"])
def test_bad_layout_refused(fault):
    x = layouts.production("D")
    if fault == "bool":
        x["mquake"]["realizations"][0] = False
    if fault == "demand":
        x["mquake"]["demand_subjects"] = 4050
    if fault == "cadence":
        x["mquake"]["checkpoints"] = [100, 300, 1000]
    if fault == "dataset":
        del x["zsre"]
    if fault == "realization":
        x["mquake"]["realizations"] = [0]
    with pytest.raises(ValueError):
        layouts.admitted(x)


def test_matrix_receipt_layout_tampering_refused():
    root = Path(__file__).resolve().parents[2]
    m = json.loads((root / "manifests/revision_v1/run_matrix_v5_2_option_D.json").read_text())
    assert producer.check_matrix_layout(m) == layouts.production("D")
    spec = dict(
        schema_version=3,
        dataset_layouts=layouts.production("D"),
        layout_sha256=layouts.digest(layouts.production("D")),
        register=REG,
        matrix={"path": "matrix", "sha256": "m"},
        protocol={"path": "protocol", "sha256": "p"},
    )
    receipt = dict(
        status="closed",
        lead_approved=True,
        register=REG,
        contract_version=2,
        dataset_layouts=spec["dataset_layouts"],
        layout_sha256=spec["layout_sha256"],
        matrix=spec["matrix"],
        protocol=spec["protocol"],
        policy=core.POLICY,
        cleared_subjects=dict(zsre=4050, counterfact=4050, mquake=1950),
        **dict.fromkeys(core.REVIEW_FLAGS, True),
    )
    check_receipt("joint_clearance", receipt, spec)
    malformed = copy.deepcopy(receipt)
    malformed["dataset_layouts"]["mquake"]["realizations"][0] = False
    with pytest.raises(ValueError, match="versioned"):
        check_receipt("joint_clearance", malformed, spec)
    receipt["cleared_subjects"]["mquake"] = 1949
    with pytest.raises(ValueError, match="capacity"):
        check_receipt("joint_clearance", receipt, spec)
    receipt["cleared_subjects"]["mquake"] = 1950
    receipt["contract_version"] = 1
    with pytest.raises(ValueError, match="versioned"):
        check_receipt("joint_clearance", receipt, spec)
    m["cells"][-1]["checkpoints"] = [100, 300, 1000]
    with pytest.raises(ValueError, match="cadence"):
        producer.check_matrix_layout(m)


def test_layout_bound_endpoints_and_missing_denominators():
    r, cells, catalog, plan, drift = setup()
    # Existing pure fixture draws two edits; remove one MQ edit deterministically
    # only in this synthetic fixture, keeping every reservation hash consistent.
    layout = small_layout()
    for g in r["allocations"]:
        if g["dataset"] == "mquake" and g["role"] == "edits":
            g["items"] = g["items"][:1]
            g["records"] = g["records"][:1]
    r.update(dataset_layouts=layout, layout_sha256=layouts.digest(layout))
    r.update(producer.paired_orders(r))
    r["planned_compositions"] = producer.planned_compositions(r, catalog)
    payloads, pop, report = construct(
        r, cells, catalog, plan, drift, layout=layout, locality_count=1
    )
    assert len(payloads) == 60 and not report["missing"]
    for cell in cells:
        assert (
            len(payloads[core.coordinate_id(cell)]["items"])
            == layout[cell["dataset"]]["roles_per_realization"]["edits"]
        )
    broken = copy.deepcopy(payloads)
    cid = core.coordinate_id(cells[0])
    broken[cid]["endpoints"]["near_miss"]["expected_ids"] = []
    with pytest.raises(ValueError):
        core.validate_seal(r, cells, broken, pop, layout=layout, locality_count=1)
