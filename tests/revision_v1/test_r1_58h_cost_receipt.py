"""Pending evidence cannot become admission by changing a signature flag."""

import copy
import json

import pytest
from scripts import r1_58h_cost_contract as cost
from scripts import r1_d9_receipts as d9
from scripts.r1_d10a_review import ROOT


def save(path, value):
    path.write_text(json.dumps(value))
    return d9.ref(path)


def complete(tmp_path):
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v6.json"))
    ceiling = d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json")
    receipt = {
        k: spec[k]
        for k in (
            "register",
            "matrix",
            "protocol",
            "dataset_layouts",
            "layout_sha256",
            "near_miss_family_contract",
        )
    }
    measurement = save(
        tmp_path / "synthetic-measurement.json",
        dict(
            pending=[],
            full_endpoint_evidence_status="complete",
            measured_peak_host_mib=4000,
            measured_peak_device_mib=800,
            source_bindings=[],
        ),
    )
    receipt.update(
        cost_schema_version=2,
        contract_version=2,
        status="closed",
        lead_approved=True,
        failures_included=True,
        pending_evidence=[],
        bindings={"cell_ceilings": ceiling},
        full_validation_evidence_status="complete",
        shared_process_hours=750,
        host_mem_available_floor_mib=6144,
        cells=[],
    )
    for key, price in cost.read(ceiling)["cells"].items():
        c, ds = key.split(":")
        receipt["cells"].append(
            dict(
                condition=c,
                dataset=ds,
                wall_seconds=price["ceiling_seconds"],
                peak_host_mib=6000,
                peak_device_mib=1200,
                measurement=measurement,
            )
        )
    return spec, receipt


def test_complete_synthetic_shape_and_missing_or_duplicate_cell(tmp_path):
    spec, r = complete(tmp_path)
    d9.check_receipt("chain_i_cell_ceilings", r, spec)
    for cells in (r["cells"][:-1], r["cells"] + [r["cells"][0]]):
        with pytest.raises(ValueError, match="all27"):
            cost.validate({**r, "cells": cells})


def test_pending_real_receipt_stays_blocked_after_flag_change():
    r = json.loads((ROOT / "docs/tasks/R1-cost-admission-receipt-v2.json").read_text())
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v6.json"))
    r.update(lead_approved=True, status="closed")
    with pytest.raises(ValueError, match="cost evidence pending"):
        d9.check_receipt("chain_i_cell_ceilings", r, spec)
    assert len(r["cells"]) == 27 and r["shared_process_hours"] == 750
    assert all(c["peak_host_mib"] is None for c in r["cells"])


def test_measurement_mutation_and_cleared_pending_list_do_not_bypass_checks(tmp_path):
    _, r = complete(tmp_path)
    bad = copy.deepcopy(r)
    bad["cells"][0]["peak_device_mib"] = 800
    with pytest.raises(ValueError, match="ceiling differs"):
        cost.validate(bad)
    p = tmp_path / "synthetic-measurement.json"
    v = json.loads(p.read_text())
    v["measured_peak_host_mib"] = None
    binding = save(p, v)
    with pytest.raises(ValueError, match="identity changed"):
        cost.validate(r)
    for c in r["cells"]:
        c["measurement"] = binding
    with pytest.raises(ValueError, match="memory ceiling"):
        cost.validate(r)


def test_full_validation_and_host_floor_are_separate(tmp_path):
    _, r = complete(tmp_path)
    with pytest.raises(ValueError, match="full validation"):
        cost.validate({**r, "full_validation_evidence_status": "pending"})
    with pytest.raises(ValueError, match="host launch floor"):
        cost.validate({**r, "host_mem_available_floor_mib": 4096})
