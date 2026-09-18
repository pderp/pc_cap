"""Real measured basis plus adversarial unsigned costing; no model or admission."""

import copy
from pathlib import Path
from uuid import uuid4

import pytest
from scripts import r1_58g_operator as operator
from scripts import r1_58h_cost_contract as contract
from scripts import r1_58l_cost_v4 as v4
from scripts import r1_d9_receipts as d9
from scripts.r1_d10a_review import write_new


@pytest.fixture(scope="module")
def prepared():
    root = v4.ROOT / "logs/r1_round36" / ("test-cost-" + uuid4().hex)
    binding = v4.build(root / "receipt.json", root / "evidence", root / "ceilings.json")
    return root, binding, v4.read(binding)


def test_real_all27_cost_basis_stays_unsigned(prepared):
    _, _, receipt = prepared
    assert contract.validate(receipt)["typed_cost_rows"] == 27
    assert receipt["lead_approved"] is False and not receipt["lead_signature"]["name"]
    measured = [v4.read(c["measurement"]) for c in receipt["cells"]]
    assert sum(r["endpoint_cost_kind"] == "reviewed_same_dataset_transfer" for r in measured) == 14
    assert receipt["projection"]["combined"]["cells"] == 330
    assert (
        receipt["projection"]["combined"]["ceiling_process_hours"]
        > receipt["projection"]["combined"]["two_worker_process_hours"]
    )
    assert receipt["projection"]["combined"]["two_worker_process_hours"] < 750
    assert any(e["endpoint_inventory"]["near_miss"]["supplied"] < 100 for e in measured)


def test_receipt_revision4_cannot_relabel_old_generic_receipt(tmp_path):
    from tests.revision_v1.test_r1_58h_cost_receipt import complete

    _, old = complete(tmp_path)
    with pytest.raises(ValueError, match="explicit transfer/source supplement"):
        contract.validate({**old, "receipt_revision": 4})


@pytest.mark.parametrize(
    "fault",
    [
        "full",
        "sample",
        "endpoint",
        "startup",
        "concurrency",
        "memory",
        "coverage",
        "label",
        "projection",
        "ceilings",
        "failure",
        "pending",
        "review",
    ],
)
def test_modified_evidence_or_policy_is_rejected(prepared, fault):
    root, _, original = prepared
    receipt = copy.deepcopy(original)
    directory = root / fault
    directory.mkdir()
    cell = next(c for c in receipt["cells"] if c["condition"] == "S1_LM" and c["dataset"] == "zsre")
    evidence = v4.read(cell["measurement"])
    component = {
        "full": "full_outer_seconds",
        "sample": "sampled_all_checkpoints_seconds",
        "endpoint": "endpoints_all_checkpoints_seconds",
        "startup": "startup_validation_seconds_estimate",
        "concurrency": "two_worker_ceiling_seconds",
    }
    if fault in component:
        evidence["cost_components"][component[fault]] *= 1.5
    elif fault == "memory":
        evidence["measured_peak_host_mib"] *= 0.5
        cell["peak_host_mib"] *= 0.5
    elif fault == "coverage":
        evidence["endpoint_inventory"]["near_miss"]["supplied"] = 100
    elif fault == "label":
        evidence["endpoint_cost_kind"] = "measured"
    elif fault == "projection":
        receipt["projection"]["combined"]["ceiling_process_hours"] = 726
    elif fault == "ceilings":
        ceiling = v4.read(receipt["bindings"]["cell_ceilings"])
        ceiling["cells"]["S1_LM:zsre"]["ceiling_seconds"] *= 1.15
        cell["wall_seconds"] *= 1.15
        receipt["bindings"]["cell_ceilings"] = write_new(directory / "ceilings.json", ceiling)
    elif fault == "failure":
        receipt["failures_included"] = False
    elif fault == "pending":
        receipt.update(lead_approved=True, pending_evidence=["unresolved cost"])
    elif fault == "review":
        review = v4.read(receipt["bindings"]["transfer_reviews"])
        review["endpoint_transfers_reviewed"] = False
        receipt["bindings"]["transfer_reviews"] = write_new(directory / "review.json", review)
    cell["measurement"] = write_new(directory / "evidence.json", evidence)
    with pytest.raises(ValueError):
        contract.validate(receipt)


def test_operator_uses_receipt_bound_v2_ceilings(prepared):
    _, binding, receipt = prepared
    spec = d9.read_metadata(d9.ref(v4.ROOT / "docs/tasks/R1-D9-inputs-v8.json"))
    spec.update({k: receipt[k] for k in ("matrix", "protocol", "full_validation")})
    spec["cost_admission_source_unsigned"] = binding
    fields = operator.fields_for("cost-admit", spec)
    with pytest.raises(ValueError, match="reviewed"):
        operator.check_fields("cost-admit", fields, spec)
    fields["full_endpoint_cost_basis_reviewed"] = True
    operator.check_fields("cost-admit", fields, spec)
    assert receipt["lead_approved"] is False
    assert not Path(v4.ROOT / "manifests/revision_v1/frozen_stage4.json").exists()
    fields["cells"][0]["wall_seconds"] *= 1.15
    with pytest.raises(ValueError, match="ceiling"):
        operator.check_fields("cost-admit", fields, spec)


def test_cf_s1_formula_does_not_double_count_reference(prepared):
    _, _, receipt = prepared
    basis = v4.read(receipt["bindings"]["transfer_basis"])
    cf = basis["rows"]["v0_stable:counterfact"]["historical_sample"]
    s1, kind, donor = v4.full_cost("S1_LM:counterfact", basis)
    assert s1 == pytest.approx(cf["seconds"] / cf["positions"] * 245237 * 1.5)
    assert donor == "v0_stable:counterfact" and "S1" in kind


def test_challenges_charge_final_once_while_sample_repeats(prepared):
    _, _, receipt = prepared
    for cell in receipt["cells"]:
        e = v4.read(cell["measurement"])
        c = e["cost_components"]
        assert c["endpoint_checkpoint_count"] == 1
        assert c["endpoints_all_checkpoints_seconds"] == c["endpoint_seconds_per_checkpoint"]
        assert c["sampled_checkpoint_count"] == (2 if cell["dataset"] == "mquake" else 3)


def test_measured_whole_process_cannot_be_undercut_by_inherited_estimate(prepared):
    _, _, receipt = prepared
    basis = v4.read(receipt["bindings"]["transfer_basis"])
    for cell in receipt["cells"]:
        key = cell["condition"] + ":" + cell["dataset"]
        components = v4.read(cell["measurement"])["cost_components"]
        if key in basis["donors"]:
            assert components["solo_seconds"] >= basis["donors"][key]["process_seconds"]
            assert components["solo_seconds"] == max(
                components["component_solo_seconds"],
                components["measured_whole_process_floor_seconds"],
            )
