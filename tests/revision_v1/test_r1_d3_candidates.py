"""R1-D3 reservation invariants; read-only source fixtures and no tokenizer."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pytest
from scripts.r1_d3_candidates import digest, select_rows

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "manifests/revision_v1/zsre_fresh_candidates_v1.json"
OUTPUT = ROOT / "manifests/revision_v1/train_pool_zsre_candidates_v1.json"


@pytest.fixture(scope="module")
def data():
    source = json.loads(SOURCE.read_text())
    clear_path = Path(source["artifacts"]["clear_candidates"]["path"])
    clear = [json.loads(line) for line in clear_path.read_text().splitlines()]
    return source, clear, json.loads(OUTPUT.read_text())


def test_exact_reservation_and_seeded_order(data):
    source, clear, result = data
    selected = np.random.Generator(np.random.PCG64(139)).permutation(len(clear))[:6000]
    assert [r["source_record_index"] for r in result["items"]] == [
        clear[int(i)]["source_record_index"] for i in selected
    ]
    assert len(result["items"]) == len(set(result["drawn_subjects_normalized"])) == 6000
    assert (
        result["counts"]["direct_clear_remainder"]
        == source["counts"]["clear_pre_e2"] - 6000
        == 52498
    )
    assert result["counts"]["teacher_eligible"] is None and not result["teacher_executed"]
    assert not result["tokenization_executed"] and result["gpu_seconds"] == 0


def test_source_text_and_per_record_hashes(data):
    _, clear, result = data
    by_index = {r["source_record_index"]: r for r in clear}
    assert digest(result["items"]) == result["items_sha256"]
    for r in result["items"]:
        original = by_index[r["source_record_index"]]
        assert r["source_mapped_item_sha256"] == digest(original)
        assert r["source_record_sha256"] == original["source_record_sha256"]
        assert (
            digest({k: v for k, v in r.items() if k != "candidate_sha256"}) == r["candidate_sha256"]
        )
        for key in (
            "subject",
            "prompt",
            "answer",
            "aliases",
            "paraphrases",
            "locality_prompts",
            "locality_answers",
        ):
            assert r[key] == original[key]
            assert r["field_sha256"][key] == digest(r[key])
        assert "prompt_ids" not in r and "answer_ids" not in r
        assert r["rephrase"] == r["paraphrases"][0]
        assert r["answer"] == original["answer"]


def test_every_reserved_subject_excluded_even_before_teacher(data):
    _, _, result = data
    additions = result["exclusion_register"]["additions"]
    assert {r["normalized_subject"] for r in additions} == set(result["drawn_subjects_normalized"])
    assert all(r["reasons"] == ["train_pool_zsre_v1"] for r in additions)
    assert all(
        r["confirmatory_eligible"] is False and r["teacher_eligible"] is None
        for r in result["items"]
    )
    assert result["exclusion_register"]["register_written"] is False


@pytest.mark.parametrize("mutation", ["hash", "flags", "blocked", "duplicate", "order"])
def test_corrupt_clear_source_is_refused(data, mutation):
    source, all_clear, _ = data
    clear = copy.deepcopy(all_clear[:10])
    inventory = copy.deepcopy(
        [
            r
            for r in source["records"]
            if r["source_record_index"] in {c["source_record_index"] for c in clear}
        ]
    )
    blocked = set()
    if mutation == "hash":
        clear[0]["answer"] = "tampered"
    elif mutation == "flags":
        clear[0]["review_flags"] = ["review_required"]
    elif mutation == "blocked":
        blocked.add(clear[0]["normalized_subject"])
    elif mutation == "duplicate":
        clear.append(copy.deepcopy(clear[0]))
    elif mutation == "order":
        clear.reverse()
    with pytest.raises(ValueError):
        select_rows(clear, inventory, blocked, n=3, seed=139)


@pytest.mark.parametrize("n", [0, True, -1, 60000])
def test_invalid_sample_size(data, n):
    source, clear, _ = data
    with pytest.raises(ValueError):
        select_rows(clear, source["records"], set(), n=n, seed=139)
