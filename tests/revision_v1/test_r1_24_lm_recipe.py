"""Arithmetic and provenance gates for the unlaunched R1-24b LM recipe."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from scripts.r1_24_lm_recipe import batches, lm_budget, read_pilot, validate

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("budget", [1, 127, 128, 129, 256, 493752])
def test_consecutive_targets_and_exact_tail(budget):
    rows = list(batches(budget))
    b = lm_budget(budget)
    assert len(rows) == b["optimizer_steps"]
    assert sum(r["valid_positions"] for r in rows) == budget
    assert rows[0]["input_start"] == 0 and rows[0]["target_start"] == 1
    assert rows[-1]["input_end"] == budget and rows[-1]["target_end"] == budget + 1
    for left, right in zip(rows, rows[1:]):
        assert left["input_end"] == right["input_start"]
        assert left["target_end"] == right["target_start"]
    assert all(r["target_start"] == r["input_start"] + 1 for r in rows)
    assert b["unique_source_tokens_read"] == budget + 1
    assert b["teacher_forward_tokens"] == 0
    assert b["scored_next_token_targets"] == b["student_reverse_token_positions"] == budget


@pytest.mark.parametrize("bad", [0, -1, True, 1.5, "128"])
def test_invalid_budgets_refused(bad):
    with pytest.raises(ValueError):
        lm_budget(bad)


def test_last_label_cannot_cross_training_boundary():
    assert lm_budget(127, train_end=128)["target_end_exclusive"] == 128
    with pytest.raises(ValueError, match="held-out"):
        lm_budget(128, train_end=128)
    for kwargs in ({"seq_len": 0}, {"seq_len": True}, {"train_end": 1}):
        with pytest.raises(ValueError):
            lm_budget(1, **kwargs)


def pilot_file(tmp_path, *, learning=493752, query=10721, total=504473, steps=400, eval_theta=None):
    p = tmp_path / "summary.json"
    p.write_text(
        json.dumps(
            {
                "args": {"steps": steps, "eval_theta": eval_theta, "tag": "selected"},
                "ledger": {
                    "learning": {"tokens": learning},
                    "query": {"tokens": query},
                    "total": {"tokens": total},
                },
            }
        )
    )
    return p


def test_learning_phase_only_and_source_binding(tmp_path):
    p = pilot_file(tmp_path)
    r = read_pilot(p)
    assert r["reported_learning_tokens"] == 493752 and r["query_tokens_excluded"] == 10721
    assert r["sha256"] == hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize(
    "change",
    [
        {"steps": 0},
        {"eval_theta": "checkpoint.npz"},
        {"total": 1},
        {"learning": True},
        {"query": -1},
    ],
)
def test_evaluation_only_or_unreconciled_pilots_refused(tmp_path, change):
    with pytest.raises(ValueError):
        read_pilot(pilot_file(tmp_path, **change))


def test_saved_recipe_same_evaluation_and_separate_compute_units():
    m = json.loads((ROOT / "manifests/revision_v1/r1_24_control_lm.json").read_text())
    literal = json.loads((ROOT / "manifests/revision_v1/r1_24_control_v2.json").read_text())
    assert validate(m) is m
    assert m["evaluation"] == literal["evaluation"]
    assert m["budget"]["matched_tokens"] == literal["budget"]["matched_tokens"] == 493752
    b = m["budget"]["arithmetic"]
    assert (b["full_steps"], b["tail_sequence_tokens"], b["optimizer_steps"]) == (3857, 56, 3858)
    assert b["student_forward_tokens"] == 2 * literal["budget"]["arithmetic"]["source_tokens"]
    assert not m["budget"]["exact_training_passes_verified"]
    assert not m["launch_allowed"] and not m["training_executed"]
    for key in (
        "optimizer",
        "optimizer_reset",
        "weight_lr",
        "betas",
        "eps",
        "weight_decay",
        "seed",
    ):
        assert m["recipe"][key] == literal["recipe"][key]
    for path, expected in m["sources_sha256"].items():
        if Path(path).stat().st_size < 5_000_000:
            assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("budget", "matched_tokens", 493753),
        ("recipe", "teacher_forward_required", True),
        ("recipe", "optimizer_reset", False),
        ("recipe", "objective", "teacher KL"),
    ],
)
def test_manifest_tampering_refused(section, key, value):
    m = json.loads((ROOT / "manifests/revision_v1/r1_24_control_lm.json").read_text())
    bad = copy.deepcopy(m)
    bad[section][key] = value
    with pytest.raises(ValueError):
        validate(bad)
