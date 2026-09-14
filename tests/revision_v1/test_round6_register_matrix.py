"""Round-6 exclusion coverage, matrix admission and answer-position byte boundaries."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from scripts.r1_40b_matrix import delta_bytes, validate
from scripts.r1_d1e_exclusions_v3 import digest, fold

ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / "manifests/revision_v1" / name).read_text())


@pytest.fixture(scope="module")
def register():
    return (
        read("exclusions_v2.json"),
        read("train_pool_zsre_candidates_v1.json"),
        read("exclusions_v3.json"),
    )


@pytest.fixture(scope="module")
def matrix():
    return read("run_matrix_draft_v2.json")


def test_register_preserves_prior_and_reserves_every_draw(register):
    old, reservation, new = register
    before = {r["normalized_subject"]: r for r in old["exclusions"]}
    after = {r["normalized_subject"]: r for r in new["exclusions"]}
    subjects = set(reservation["drawn_subjects_normalized"])
    assert len(subjects) == 6000
    assert set(after) == set(before) | subjects
    for key, r in before.items():
        assert set(r["reasons"]) <= set(after[key]["reasons"])
        assert r["canonical_subject_key"] == after[key]["canonical_subject_key"]
    assert all("train_pool_zsre_v1" in after[s]["reasons"] for s in subjects)
    assert new["reservation"]["accepted_training_items"] == 3000
    assert new["reservation"]["unused_and_teacher_rejected_candidates_remain_excluded"]
    assert new["counts_v3"]["exclusion_subjects_after"] == 38029


def test_candidate_artifacts_match_hash_counts_and_reservations(register):
    _, reservation, new = register
    excluded = {r["normalized_subject"] for r in new["exclusions"]}
    reserved_indices = {r["source_record_index"] for r in reservation["items"]}
    for key, count in (("candidates", 143753), ("clear_candidate_subject_survivors", 52498)):
        artifact = new[key]
        content = Path(artifact["path"]).read_bytes()
        assert hashlib.sha256(content).hexdigest() == artifact["sha256"]
        rows = [json.loads(line) for line in content.splitlines()]
        assert len(rows) == count
        if key == "candidates":
            assert not excluded.intersection(r["normalized_subject"] for r in rows)
            assert len({r["normalized_subject"] for r in rows}) == 81857
        else:
            assert not reserved_indices.intersection(r["source_record_index"] for r in rows)
    assert new["counts_v3"]["confirmed_context_clear_after_new_exposure"] is None
    assert new["counts_v3"]["teacher_eligible_fresh_candidates"] is None
    assert new["counts_v3"]["final_realizations_emitted"] == 0
    assert not new["final_sealing_ready"]


@pytest.mark.parametrize(
    "damage", ["count", "items_hash", "coverage", "additions", "candidate_hash", "eligibility"]
)
def test_damaged_reservation_is_refused(register, damage):
    old, original, _ = register
    reservation = copy.deepcopy(original)
    if damage == "count":
        reservation["items"].pop()
    elif damage == "items_hash":
        reservation["items_sha256"] = "0" * 64
    elif damage == "coverage":
        reservation["drawn_subjects_normalized"].pop()
    elif damage == "additions":
        reservation["exclusion_register"]["additions"].pop()
    elif damage == "candidate_hash":
        reservation["items"][0]["answer"] = "altered"
        reservation["items_sha256"] = digest(reservation["items"])
    else:
        row = reservation["items"][0]
        row["confirmatory_eligible"] = True
        row["candidate_sha256"] = digest({k: v for k, v in row.items() if k != "candidate_sha256"})
        reservation["items_sha256"] = digest(reservation["items"])
    with pytest.raises(ValueError):
        fold(old, reservation)


def test_matrix_axes_primary_rule_and_unlaunchable_budget(matrix):
    assert validate(matrix) is matrix
    cells = matrix["cells"]
    assert len(cells) == 2 * 3 * 5 * 6 == 180
    axes = {
        (c["condition_id"], c["dataset"], c["realization_seed"], c["order_seed"]) for c in cells
    }
    assert len(axes) == len(cells)
    assert matrix["pruning"]["removed_conditional_cells"] == 480
    assert matrix["pruning"]["required_core_cells_silently_removed"] == 0
    primary = matrix["conditions"]["R1_learned_ff"]
    assert primary["role"] == "primary"
    assert primary["checkpoint_ids"] == ["base_original", "reader_mixed"]
    assert primary["settings"]["null_threshold"] == 0.5
    assert primary["settings"]["min_score"] is None
    assert primary["settings"]["lexical"] is True
    assert matrix["conditions"]["R1_nonlearned"]["settings"]["lexical"] is False
    budget = matrix["budget"]
    assert budget["core_draft_seconds_including_20pct_reserve"] == 538920
    assert budget["core_fits_15h_at_draft_ceilings"] is False
    assert (
        matrix["data_gates"]["register_sha256"]
        == hashlib.sha256(
            (ROOT / "manifests/revision_v1/exclusions_v3.json").read_bytes()
        ).hexdigest()
    )
    assert all(c["tokens"]["exact_final_stream_tokens"] is None for c in cells)


@pytest.mark.parametrize(
    "damage",
    [
        "launch",
        "freeze",
        "length",
        "duplicate",
        "checkpoint",
        "reserve",
        "budget",
        "primary",
        "gate",
    ],
)
def test_invalid_matrix_is_refused(matrix, damage):
    m = copy.deepcopy(matrix)
    c = m["cells"][0]
    if damage == "launch":
        c["launch_allowed"] = True
    elif damage == "freeze":
        c["ceilings"]["frozen"] = True
    elif damage == "length":
        c["stream_length"] = 999
    elif damage == "duplicate":
        m["cells"][1] = copy.deepcopy(c)
    elif damage == "checkpoint":
        c["checkpoint_ids"] = ["different"]
    elif damage == "reserve":
        c["ceilings"]["failure_reserve_seconds"] = 0
    elif damage == "budget":
        m["budget"]["core_draft_seconds_including_20pct_reserve"] += 1
    elif damage == "primary":
        m["primary_condition"] = "R1_nonlearned"
    else:
        m["conditions"]["R1_learned_ff"]["settings"]["min_score"] = 0.93
    with pytest.raises(ValueError):
        validate(m)


@pytest.mark.parametrize("weights", [13392912, 12604420])
def test_position_bytes_linear_and_hard_ceiling_boundary(weights):
    first = delta_bytes(1002, 5, 992, weights)
    second = delta_bytes(1002, 6, 992, weights)
    assert second["total"] - first["total"] == 1002 * 3 * 768 * 4
    assert first["total"] < 64 * 1024 * 1024 < second["total"]
    assert delta_bytes(0, 32, 992, weights)["total"] == weights
    assert delta_bytes(1002, 32, 992, weights)["total"] > 64 * 1024 * 1024


@pytest.mark.parametrize("value", [-1, True, 1.5])
def test_invalid_position_count_rejected(value):
    with pytest.raises(ValueError):
        delta_bytes(1000, value, 10, 13392912)


def test_mean_fit_does_not_admit_maximum_length_or_select_truncation(matrix):
    for cell in matrix["cells"]:
        if cell["condition_id"] not in ("R1_learned_ff", "R1_nonlearned"):
            continue
        projection = cell["memory_projection"]
        assert projection["estimate_from_observed_100_edit_mix"]["fits_with_clone_records"]
        assert not projection["declared_maximum_32_answer_positions_992_prompt_tokens"]["fits"]
        assert projection["bounded_position_option"]["fits"]
        assert projection["bounded_position_option"]["selected"] is False
        assert projection["exact_final_fit"] is None
