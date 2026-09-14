"""Round-7 candidate admission and unfrozen-matrix artifact checks; CPU/read-only."""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

import pytest
from scripts import r1_40c_matrix as matrix_module
from scripts import r1_d2_candidates as candidates_module

ROOT = Path(__file__).resolve().parents[2]


def read(rel):
    return json.loads((ROOT / rel).read_text())


@pytest.fixture(scope="module")
def inventory():
    manifest = read("manifests/revision_v1/counterfact_fresh_candidates_v1.json")
    source = read("manifests/dev/pools.json")["counterfact"]["confirm_pool_path"]
    rows = [json.loads(line) for line in Path(source).read_text().splitlines()]
    sidecars = [read(f"manifests/confirm/counterfact_r{i}.meta.json") for i in range(3)]
    reserved, checks = candidates_module.old_reservations([r["item_id"] for r in rows], sidecars)
    return {
        "manifest": manifest,
        "rows": rows,
        "sidecars": sidecars,
        "reserved": reserved,
        "checks": checks,
        "prior": read("manifests/revision_v1/exclusions.json"),
        "current": read("manifests/revision_v1/exclusions_v3.json"),
        "training": read("manifests/revision_v1/train_pool_counterfact_v1.json"),
    }


@pytest.fixture(scope="module")
def matrix():
    return read("manifests/revision_v1/run_matrix_draft_v3.json")


def test_candidate_order_and_every_record_hash(inventory):
    manifest, source = inventory["manifest"], inventory["rows"]
    option = manifest["option_a"]
    entries = option["candidates"]
    payload = option["payload"]
    assert candidates_module.sha(payload["path"]) == payload["sha256"]
    records = [json.loads(line) for line in Path(payload["path"]).read_text().splitlines()]
    assert len(entries) == len(records) == 12246
    assert candidates_module.digest(entries) == option["candidates_sha256"]
    indices = [r["eligible_source_index"] for r in entries]
    assert indices == sorted(set(indices))
    for rank, (entry, record) in enumerate(zip(entries, records, strict=True)):
        original = source[entry["eligible_source_index"]]
        assert entry["candidate_rank"] == rank
        assert entry["item_id"] == original["item_id"] == record["item_id"]
        assert entry["source_record_sha256"] == candidates_module.digest(original)
        assert entry["prepared_record_sha256"] == candidates_module.digest(record)
        assert entry["prompt_sha256"] == hashlib.sha256(original["prompt"].encode()).hexdigest()
        assert entry["candidate_sha256"] == candidates_module.digest(
            {k: v for k, v in entry.items() if k != "candidate_sha256"}
        )
        assert {k: record[k] for k in original} == original
        assert entry["conditional_candidate"] and not entry["confirmatory_admitted"]


def test_no_other_v3_reason_or_training_reservation_is_waived(inventory):
    entries = inventory["manifest"]["option_a"]["candidates"]
    reasons = {}
    for row in inventory["current"]["exclusions"]:
        reasons.setdefault(row["canonical_subject_key"], set()).update(row["reasons"])
    train_subjects = {candidates_module.norm(r["subject"]) for r in inventory["training"]["items"]}
    for entry in entries:
        assert reasons[entry["canonical_subject_key"]] == {"old_eligible:counterfact"}
        assert entry["item_id"] not in inventory["reserved"]
        assert entry["normalized_subject"] not in train_subjects
    assert len({e["canonical_subject_key"] for e in entries}) == len(entries)
    assert len(inventory["checks"]) == 15 and all(c["verified"] for c in inventory["checks"])


def test_filter_replay_reconciles_counts_and_excluded_payload(inventory):
    accepted, decisions, counts, _ = candidates_module.filter_remainder(
        inventory["rows"],
        inventory["reserved"],
        inventory["prior"],
        inventory["current"],
        inventory["training"],
    )
    manifest = inventory["manifest"]
    assert counts == manifest["counts"]
    assert counts["eligible"] == 20091
    assert counts["historical_reservations_removed"] == 3000
    assert counts["v1_other_exposures_removed"] == 950
    assert counts["historical_remainder_before_training"] == 16141
    assert counts["dec037_training_removed"] == 3000
    assert counts["nominal_remainder_after_dec037"] == 13141
    assert counts["additional_v3_exposures_removed"] == 895
    assert counts["conditional_remainder_candidates"] == 12246
    assert counts["strict_v3_candidates_without_exception"] == 0
    assert [row["item_id"] for _, row, _ in accepted] == [
        e["item_id"] for e in manifest["option_a"]["candidates"]
    ]
    resource = manifest["option_a"]["additional_exclusions"]
    assert candidates_module.sha(resource["path"]) == resource["sha256"]
    assert decisions == [
        json.loads(line) for line in Path(resource["path"]).read_text().splitlines()
    ]


def test_tampered_public_historical_metadata_is_refused(inventory):
    sidecars = copy.deepcopy(inventory["sidecars"])
    sidecars[1]["orders"]["103"] = "bad-order"
    with pytest.raises(ValueError, match="order metadata"):
        candidates_module.old_reservations([r["item_id"] for r in inventory["rows"]], sidecars)


def test_changed_training_identity_order_is_refused(inventory):
    training = copy.deepcopy(inventory["training"])
    training["items"][0], training["items"][1] = training["items"][1], training["items"][0]
    with pytest.raises(ValueError, match="DEC-037 training identity"):
        candidates_module.filter_remainder(
            inventory["rows"],
            inventory["reserved"],
            inventory["prior"],
            inventory["current"],
            training,
        )


def test_candidates_do_not_admit_draw_seal_or_invent_source(inventory):
    m = inventory["manifest"]
    assert m["selected_option"] is None and not m["final_sealing_ready"]
    assert m["draws_emitted"] == m["sealed_payloads_opened"] == m["gpu_seconds"] == 0
    assert not m["teacher_executed"] and not m["tokenization_executed"]
    assert m["option_b"]["candidate_count"] == 0
    assert m["option_b"]["status"] == "unavailable_no_additional_local_counterfact_source"
    assert m["option_b"]["counterfact_files_found"] == ["counterfact/counterfact.json"]
    assert not m["historical_reservation_verification"]["new_random_sampling_performed"]
    assert all(
        "/manifests/confirm/" not in p or p.endswith(".meta.json") for p in m["sources_sha256"]
    )
    # Refuses before writing a second manifest or resource file.
    with pytest.raises(ValueError, match="new manifest"):
        candidates_module.prepare(
            ROOT / "manifests/revision_v1/counterfact_fresh_candidates_v1.json",
            Path(m["option_a"]["payload"]["path"]).parent,
        )


def test_matrix_is_full_paired_cartesian_design_with_shared_S0_R0(matrix):
    assert matrix_module.validate(matrix) is matrix
    expected = set(
        itertools.product(matrix["conditions"], ["counterfact", "zsre"], range(3), range(100, 105))
    )
    actual = {
        (c["condition_id"], c["dataset"], c["realization_seed"], c["order_seed"])
        for c in matrix["cells"]
    }
    assert actual == expected and len(expected) == 240
    assert Counter(c["condition_id"] for c in matrix["cells"]) == {
        k: 30 for k in matrix["conditions"]
    }
    assert matrix["extension"]["S0_reused"] == "v0_stable"
    assert matrix["extension"]["R0_reused"] == "R1_learned_ff"
    assert len({c["checkpoint_path_template"] for c in matrix["cells"]}) == 240


def test_continuation_treatments_bind_recipes_and_charge_shared_training_once(matrix):
    for cid, treatment in matrix_module.NEW_CONDITIONS.items():
        condition = matrix["conditions"][cid]
        assert condition["settings"]["family"] == "StableCap"
        assert condition["settings"]["arm"] == "C1"
        assert not condition["settings"]["cap_retrained"]
        job = matrix["shared_training_jobs"]["continuation_" + treatment]
        assert job["charge_once"] and not job["multiply_by_evaluation_cells"]
        assert job["shared_reference_budget_tokens"] == 771581
        recipe = read(job["recipe_manifest"])
        assert candidates_module.sha(ROOT / job["recipe_manifest"]) == job["recipe_sha256"]
        assert recipe["budget"]["arithmetic"] == job["planned_arithmetic"]
        checkpoint = matrix["checkpoint_registry"]["base_continued_" + treatment]
        assert checkpoint["sha256"] is None and checkpoint["path"] is None
        assert "original base" in condition["settings"]["locality_reference"]
        assert "continued cap-off" in condition["settings"]["unseen_reference"]
    primary = read("manifests/revision_v1/primary_condition_v1.json")
    assert (
        matrix["reference_condition_binding"]["reader_weights_sha256"]
        == primary["weights"]["seed0"]["sha256"]
    )


def test_new_endpoint_work_is_unpriced_and_population_unselected(matrix):
    b = matrix["budget"]
    assert b["legacy_endpoint_proxy_subtotal_seconds"] == 802440
    assert b["previous_180_cell_legacy_proxy_seconds"] == 538920
    assert b["new_S1_borrowed_stable_proxy_seconds"] == 263520
    assert b["expanded_full_matrix_ceiling_seconds"] is None
    assert b["new_unseen_prompt_pairs"] == 72000
    assert b["new_unseen_greedy_decodes"] == 144000
    assert len(matrix["profiling_jobs"]) == 4
    assert matrix["data_gates"]["minimum_distinct_edit_plus_outside_facts_per_dataset"] == 3300
    assert matrix["data_gates"]["counterfact_source_option_selected"] is None
    assert matrix["endpoint_catalog"]["memory_size_profile"]["target_active_record_counts"] == [
        100,
        300,
        1000,
    ]
    assert matrix["endpoint_catalog"]["unseen_edit_prompt"]["expected_n_per_checkpoint"] == 100
    assert matrix["endpoint_catalog"]["unseen_edit_prompt"]["decision_margin"] is None
    for c in matrix["cells"]:
        assert c["ceilings"]["proposed_seconds"] is None
        assert "P3-unseen-scale" in c["profile_dependencies"]


@pytest.mark.parametrize(
    "fault",
    [
        "launch",
        "freeze",
        "short_stream",
        "priced",
        "missing_endpoint",
        "duplicate",
        "checkpoint",
        "unknown_profile",
        "budget",
    ],
)
def test_matrix_validator_refuses_unsafe_or_inconsistent_cells(matrix, fault):
    m = copy.deepcopy(matrix)
    c = m["cells"][0]
    if fault == "launch":
        c["launch_allowed"] = True
    elif fault == "freeze":
        c["ceilings"]["frozen"] = True
    elif fault == "short_stream":
        c["stream_length"] = 300
    elif fault == "priced":
        c["ceilings"]["proposed_seconds"] = 1
    elif fault == "missing_endpoint":
        c["endpoint_ids"].remove("unseen_edit_prompt")
    elif fault == "duplicate":
        m["cells"][1] = copy.deepcopy(c)
    elif fault == "checkpoint":
        c["checkpoint_ids"] = ["absent"]
    elif fault == "unknown_profile":
        c["profile_dependencies"].append("missing")
    elif fault == "budget":
        m["budget"]["expanded_full_matrix_ceiling_seconds"] = 802440
    with pytest.raises(ValueError):
        matrix_module.validate(m)
