"""R1-26 repairs and executable evidence for three still-open boundaries.

Strict xfails record the desired contract, not an endorsement of current bugs.
Remove the marks when the owning lane repairs and reviews these cases.
"""
from __future__ import annotations

import pytest
from scripts.r1_26_reaudit import controls

import pccap  # noqa: F401


@pytest.fixture(scope="module")
def audited(tmp_path_factory):
    return controls(tmp_path_factory.mktemp("r1_26_boundaries"))


def test_capacity_rejection_is_atomic_and_failed_work_is_billed(audited):
    r = audited["delta_capacity"]
    assert r["reason"] == "delta_capacity"
    assert r["same_hash"] and r["same_bytes"]
    assert r["old_active"] and r["replacement_removed"]
    assert r["failed_full_forwards_charged"] > 0


def test_mixed_steps_refused_without_state_mutation(audited):
    r = audited["mixed_steps"]
    assert r["rejected"] and r["same_hash"] and r["same_bytes"]


def test_item_guard_restore_preserves_weight_charge(audited):
    assert all(audited["itemguard_restore"].values())


def test_datasets_get_distinct_roots_and_existing_roots_refused(audited):
    r = audited["driver_paths"]
    assert r["dataset_paths_differ"] and r["existing_root_refused"]


@pytest.mark.xfail(strict=True, reason="X26-01: snapshot import adopts source ceiling and bypasses capacity validation")
def test_import_respects_requested_ceiling(audited):
    r = audited["different_requested_ceiling_import"]
    assert not r["accepted"] or r["reported_bytes"] <= r["requested_ceiling"]


@pytest.mark.xfail(strict=True, reason="X26-01: raw RecordStore restore bypasses capacity validation")
def test_raw_store_restore_cannot_accept_over_ceiling_state(audited):
    r = audited["over_ceiling_store_import"]
    assert not r["accepted"] or r["reported_bytes"] <= r["ceiling"]


@pytest.mark.xfail(strict=True, reason="X26-02: non-cosine ReaderConfig is accepted but store remains cosine")
def test_accepted_noncosine_configuration_has_consistent_retrieval(audited):
    r = audited["noncosine_configuration"]
    assert r["training_best"] == r["retrieved"]


@pytest.mark.xfail(strict=True, reason="X26-03: orphan top-level summaries are outside existing-root guard")
def test_orphan_summary_is_refused(audited):
    assert not audited["driver_paths"]["orphan_summary_admitted"]
