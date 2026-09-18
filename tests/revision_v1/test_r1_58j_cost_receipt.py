"""Revision 3 may not manufacture full-split evidence or turn transfer proposals into peaks."""

import copy

import pytest
from scripts import r1_58h_cost_contract as validator
from scripts import r1_58j_cost_receipt as producer
from scripts.r1_58j_validation_inventory import audit
from scripts.r1_d10a_review import ROOT, write_new

from tests.revision_v1.test_r1_58h_cost_receipt import complete


def test_direct_sampled_and_extrapolated_are_distinct():
    for method in ("direct_gnu_time", "monitor_temporal_match"):
        value, pending = producer.host_measurement(dict(method=method, measured_peak_host_mib=2048))
        assert value == 2048 and not pending
    value, pending = producer.host_measurement(
        dict(method="extrapolated_proposal", proposed_peak_host_mib=2048)
    )
    assert value is None and pending


def test_real_full_split_coverage_cannot_be_inferred_from_prefix():
    result = audit()
    assert result["validation_tokens"] == 247289
    assert result["complete_window_prediction_positions"] == 245237
    assert result["trailing_tokens"] == 121
    assert all(
        r["source_prefix_equal"] and r["scored_positions"] == 16256 for r in result["recipes"]
    )
    assert result["full_validation_evidence_status"] == "pending"


def test_signature_and_status_flags_do_not_replace_bound_validation(tmp_path):
    _, r = complete(tmp_path)
    from uuid import uuid4

    folder = ROOT / "logs/r1_round29/cost-tests" / uuid4().hex
    r.update(
        receipt_revision=3, validation_inventory=write_new(folder / "validation.json", audit())
    )
    changed = copy.deepcopy(r)
    changed.update(
        lead_approved=True, pending_evidence=[], full_validation_evidence_status="complete"
    )
    with pytest.raises(ValueError, match="full validation split evidence pending"):
        validator.validate(changed)


def test_legacy_typed_positive_path_still_passes(tmp_path):
    _, receipt = complete(tmp_path)
    assert validator.validate(receipt)["typed_cost_rows"] == 27
