"""Admission guards for the accepted exposure register wrapper, CPU only."""

import copy
import json

import pytest
from scripts.r1_d1f_freeze_register import ROOT, sha, validate_document, verify


@pytest.fixture(scope="module")
def manifest():
    return json.loads((ROOT / "manifests/revision_v1/exclusions_frozen_v3.json").read_text())


def test_pinned_wrapper_and_all_resources(manifest):
    path = ROOT / "manifests/revision_v1/exclusions_frozen_v3.json"
    verified = verify(path, sha(path))
    assert verified == manifest
    assert len(manifest["bindings_sha256"]) == 14


def test_all_reserved_subjects_and_current_overlay(manifest):
    assert manifest["counts"]["zsre_reservation_subjects"] == 6000
    assert manifest["counts"]["accepted_zsre_training_items"] == 3000
    assert (
        manifest["counts"]["prior_clear_v2"] - manifest["zsre"]["prior_clear_v3_index"]["records"]
        == 6000
    )
    assert manifest["zsre"]["do_not_sample_historical_58498_directly"]


@pytest.mark.parametrize(
    ("keys", "value"),
    [
        (("draw_authorized",), True),
        (("confirmation_protocol_frozen",), True),
        (("counterfact", "selected_reading"), "old_remainder_exception"),
        (("counterfact", "strict_v3_old_pool_count"), 12246),
        (("zsre", "prior_clear_v3_index", "records"), 58498),
        (("counts", "zsre_reservation_subjects"), 3000),
        (("register", "sha256"), "0" * 64),
        (("policy", "sha256"), "0" * 64),
        (("sealed_payloads_opened",), 1),
    ],
)
def test_semantic_admission_refusals(manifest, keys, value):
    changed = copy.deepcopy(manifest)
    node = changed
    for key in keys[:-1]:
        node = node[key]
    node[keys[-1]] = value
    with pytest.raises(ValueError):
        validate_document(changed, check_sources=False)


def test_decision_row_integrity(manifest):
    changed = copy.deepcopy(manifest)
    changed["acceptance"]["decision_row"] += " waived"
    with pytest.raises(ValueError, match="decision text"):
        validate_document(changed, check_sources=False)


def test_bound_resource_integrity(manifest, tmp_path):
    p = tmp_path / "resource.json"
    p.write_text("{}")
    changed = copy.deepcopy(manifest)
    changed["bindings_sha256"] = {str(p): "0" * 64}
    with pytest.raises(ValueError, match="bound input changed"):
        validate_document(changed)


def test_external_wrapper_pin_required(tmp_path):
    p = tmp_path / "wrapper.json"
    p.write_text("{}")
    with pytest.raises(ValueError, match="caller must pin"):
        verify(p, None)
    with pytest.raises(ValueError, match="wrapper identity"):
        verify(p, "0" * 64)


def test_no_draw_or_candidate_admission(manifest):
    assert manifest["draws_emitted"] == manifest["sealed_payloads_opened"] == 0
    assert not manifest["zsre"]["final_draw_ready"]
    assert manifest["counterfact"]["selected_reading"] is None
    assert not manifest["counterfact"]["conditional_old_remainder"]["admitted"]
    assert manifest["counterfact"]["distinct_local_source"]["records"] == 0
