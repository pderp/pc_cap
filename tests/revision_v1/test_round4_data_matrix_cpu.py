"""CPU contract checks for the candidate review and unfrozen run matrix."""
from __future__ import annotations

import importlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

import pccap  # noqa: F401
from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def candidate_module(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    return importlib.import_module("r1_d1c_candidates")


@pytest.fixture(scope="module")
def tokenizer():
    return GPT2Tokenizer()


def source_row():
    return {"subject": "Example City", "src": "Where is Example City?", "rephrase": "In what nation is Example City?",
            "answers": ["Canada", "CANADA"], "alt": "France", "pred": "Germany",
            "loc": "nq question: Who wrote this unrelated novel?", "loc_ans": "Example Author"}


@pytest.mark.parametrize("suffix", ["", " ", "\n"])
def test_canonical_target_and_token_boundary_match_shared_helper(candidate_module, tokenizer, suffix):
    row = source_row()
    row["src"] += suffix
    assert candidate_module.structural_reasons(row) == []
    item, reasons = candidate_module.map_item(17, row, tokenizer.tok)
    expected = tokenize_pair(tokenizer, row["src"], row["answers"][0])
    assert not reasons and not expected.excluded
    assert item["answer"] == "Canada" and item["aliases"] == ["canada"]
    assert item["prompt_ids"] == expected.prompt_ids.tolist()
    assert item["answer_ids"] == expected.answer_ids.tolist()
    assert item["answer_ids"][-1] == 198
    assert item["item_id"] == "zsre-train-17" and item["source_split"] == "mend_train"
    assert item["locality_prompts"] == [row["loc"]]
    assert item["teacher_eligible"] is None and item["final_assignment"] is None


@pytest.mark.parametrize("change, reason", [
    ({"answers": []}, "missing_or_invalid_answers"),
    ({"answers": ["Canada", None]}, "missing_or_invalid_answers"),
    ({"answers": ["two\nlines"]}, "embedded_answer_terminator"),
    ({"rephrase": "  WHERE IS EXAMPLE CITY? "}, "rephrase_equals_prompt"),
    ({"loc": "Where is Example City?"}, "locality_equals_edit_query"),
    ({"loc_ans": ""}, "missing_or_invalid_loc_ans"),
])
def test_malformed_edit_fields_refused(candidate_module, change, reason):
    row = {**source_row(), **change}
    assert reason in candidate_module.structural_reasons(row)


def test_long_answer_refused_with_terminator_counted(candidate_module, tokenizer):
    row = {**source_row(), "answers": [" word" * 40]}
    item, reasons = candidate_module.map_item(18, row, tokenizer.tok)
    assert item["answer_tokens"] > 32
    assert "answer_tokens_outside_1_32" in reasons


def test_exclusion_word_boundaries_and_punctuation_are_conservative(candidate_module):
    matcher = candidate_module.ExclusionMatcher(["york", "new york", "u.s.", "a-b"])
    assert matcher.matches("Yorkshire") == []
    assert matcher.matches("NEW YORK!") == ["new york", "york"]
    assert matcher.matches("The U S population and A B group") == ["a-b", "u.s."]
    assert matcher.matches("A ＹＯＲＫ address") == ["york"]


def test_complete_candidate_inventory_hashes_partition_and_source_identity(candidate_module):
    m = json.loads((ROOT / "manifests/revision_v1/zsre_fresh_candidates_v1.json").read_text())
    for path, expected in m["sources_sha256"].items():
        assert candidate_module.sha(Path(path)) == expected, path
    for artifact in m["artifacts"].values():
        assert candidate_module.sha(Path(artifact["path"])) == artifact["sha256"]
    raw_path = next(Path(p) for p in m["sources_sha256"] if p.endswith("zsre_mend_train.json"))
    raw = json.loads(raw_path.read_text())
    rows = {r["source_record_index"]: r for r in m["records"]}
    assert len(rows) == len(m["records"]) == m["counts"]["after_subject_dedup"]
    subjects, facts, all_indices, clear_indices, flagged_indices = set(), set(), [], set(), set()
    with Path(m["artifacts"]["ordered_candidates"]["path"]).open() as f:
        for line in f:
            item = json.loads(line)
            idx = item["source_record_index"]
            record = rows[idx]
            assert candidate_module.digest(raw[idx]) == record["source_record_sha256"] == item["source_record_sha256"]
            assert candidate_module.digest(item) == record["mapped_item_sha256"]
            assert item["normalized_subject"] not in subjects and item["fact_id"] not in facts
            assert item["review_flags"] == record["review_flags"]
            assert item["teacher_eligible"] is None and item["final_assignment"] is None
            subjects.add(item["normalized_subject"])
            facts.add(item["fact_id"])
            all_indices.append(idx)
            (flagged_indices if item["review_flags"] else clear_indices).add(idx)
    assert all_indices == sorted(rows)
    for name, expected_indices in (("clear_candidates", clear_indices), ("flagged_candidates", flagged_indices)):
        actual = []
        with Path(m["artifacts"][name]["path"]).open() as f:
            for line in f:
                item = json.loads(line)
                idx = item["source_record_index"]
                assert candidate_module.digest(item) == rows[idx]["mapped_item_sha256"]
                actual.append(idx)
        assert actual == sorted(expected_indices)
    assert len(clear_indices) == m["counts"]["clear_pre_e2"]
    assert len(flagged_indices) == m["counts"]["flagged"]
    statuses, reviews = Counter(), set()
    with Path(m["artifacts"]["record_review"]["path"]).open() as f:
        for line in f:
            row = json.loads(line)
            idx = row["source_record_index"]
            assert idx not in reviews
            reviews.add(idx)
            assert candidate_module.digest(raw[idx]) == row["source_record_sha256"]
            for field, expected in row["field_sha256"].items():
                assert candidate_module.digest(raw[idx].get(field)) == expected
            statuses[row["status"]] += 1
    counts = m["counts"]
    assert len(reviews) == counts["after_v2_exclusions"]
    assert statuses["duplicate_fact"] == counts["duplicate_fact"]
    assert statuses["duplicate_subject"] == counts["duplicate_subject"]
    assert statuses["rejected_structural"] == counts["after_v2_exclusions"] - counts["after_token_validation"]
    assert statuses["clear_pre_e2_candidate"] == len(clear_indices)
    assert statuses["flagged_review_required"] == len(flagged_indices)
    assert m["requested_final_capacity"]["final_realizations_assigned"] == 0


@pytest.fixture
def matrix_module(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    return importlib.import_module("r1_40_matrix")


@pytest.fixture
def matrix():
    return json.loads((ROOT / "manifests/revision_v1/run_matrix_draft.json").read_text())


def test_matrix_deduplicates_contrasts_and_pins_all_sources(matrix_module, matrix):
    matrix_module.validate_matrix(matrix)
    assert len(matrix["cells"]) == 660
    # The stored draft preserves historical input identities; live source binding
    # belongs to a freshly built draft as append-only decisions continue to grow.
    fresh = matrix_module.build()
    matrix_module.validate_matrix(fresh)
    required = {str(ROOT / p) for p in ("docs/decisions.md", "scripts/r1_40_matrix.py")}
    assert required <= fresh["sources_sha256"].keys()
    for path, expected in fresh["sources_sha256"].items():
        assert matrix_module.sha(Path(path)) == expected, path
    counts = Counter(c["condition_id"] for c in matrix["cells"] if c["scope"] == "core")
    assert len(counts) == 6 and set(counts.values()) == {30}
    assert len({c["checkpoint_path_template"] for c in matrix["cells"]}) == len(matrix["cells"])
    for cell in matrix["cells"]:
        assert all(k in matrix["checkpoint_registry"] for k in cell["checkpoint_ids"])
        assert cell["tokens"]["exact_final_stream_tokens"] is None
    for contrast in matrix["contrasts"]:
        assert contrast["reuse_existing_cells"]
        assert set(contrast["conditions"]) <= matrix["conditions"].keys()
    core = [c for c in matrix["cells"] if c["scope"] == "core"]
    expected = sum(c["ceilings"]["proposed_seconds"] + c["ceilings"]["failure_reserve_seconds"] for c in core)
    assert expected == matrix["budget"]["core_draft_seconds_including_20pct_reserve"]
    assert matrix["gpu_seconds"] == 0 and matrix["sealed_payloads_opened"] == 0


@pytest.mark.parametrize("violation", ["duplicate", "launch", "freeze", "short_stream", "reserve", "alias"])
def test_invalid_matrix_admission_or_identity_refused(matrix_module, matrix, violation):
    bad = deepcopy(matrix)
    c = bad["cells"][0]
    if violation == "duplicate":
        bad["cells"].append(deepcopy(c))
    elif violation == "launch":
        c["launch_allowed"] = True
    elif violation == "freeze":
        c["ceilings"]["frozen"] = True
    elif violation == "short_stream":
        c["stream_length"] = 100
    elif violation == "reserve":
        c["ceilings"]["failure_reserve_seconds"] = 0
    else:
        c["checkpoint_ids"] = ["different"]
    with pytest.raises(ValueError):
        matrix_module.validate_matrix(bad)
