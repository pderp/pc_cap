from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest
from scripts.r1_d10a_review_core import digest, review
from scripts.r1_d10b_teacher_review import (
    atomic_new,
    eligible_rows,
    evaluate,
    memory_guard,
    merge,
    validate_chunk,
)

from tests.revision_v1.test_r1_d10a_review import fixture


def evaluated():
    _, sources, _, tok, limits = fixture()
    rows = sources["zsre"][:2]

    def decode(base, prompts, tokenizer, **kwargs):
        assert [p.tolist() for p in prompts] == [r["prompt_ids"] for r in rows]
        assert kwargs == {"max_new": 32, "batch_size": 2, "phase": "query"}
        return [
            SimpleNamespace(text=text, new_ids=[2], stopped_by="max_new", truncated=True, steps=32)
            for text in [" NEW ", "different"]
        ]

    return rows, evaluate(rows, object(), tok, limits, batch_size=2, decode=decode)


def test_e2_uses_normalized_answer_and_does_not_change_truncation_rule():
    _, results = evaluated()
    assert [r["teacher_pass"] for r in results] == [False, True]
    assert all(r["truncated"] and r["tokens_pass"] for r in results)


def test_invalid_tokens_do_not_reach_model():
    _, sources, _, tok, limits = fixture()
    row = sources["zsre"][0]
    row["paraphrases"] = ["x" * 600]

    def forbidden(*args, **kwargs):
        raise AssertionError("invalid token row reached teacher")

    result = evaluate([row], object(), tok, limits, batch_size=2, decode=forbidden)[0]
    assert result["teacher_pass"] is None and not result["tokens_pass"]


def test_complete_merge_retains_exclusions_and_does_not_certify_roles():
    f = fixture()
    e, _ = review(*f, target=2)
    e.update(base_tensor_sha256="b" * 64, tokenizer_sha256="t" * 64, evidence_bindings=[])
    groups = eligible_rows(e, f[1])
    reviewed = [
        {
            "dataset": ds,
            "item_id": r["item_id"],
            "payload_sha256": digest(r),
            "teacher_pass": True,
            "tokens_pass": True,
        }
        for ds, rows in groups.items()
        for r in rows
    ]
    merged = merge(e, reviewed, [{"path": "synthetic", "sha256": "s" * 64}])
    assert merged["teacher_token_review_complete"]
    assert not merged["role_compatibility_complete"]
    assert all(d["decision"] == "exclude" for d in merged["dispositions"])
    assert all(c["eligible_subjects"] == 2 for c in merged["teacher_counts"].values())
    with pytest.raises(ValueError, match="complete"):
        merge(e, reviewed[:-1], [])


@pytest.mark.parametrize("fault", ["hash", "duplicate", "alias"])
def test_eligible_input_refuses_changed_sources_or_unreviewed_aliases(fault):
    f = fixture()
    e, _ = review(*f)
    if fault == "hash":
        f[1]["zsre"][0]["answer"] = "changed"
    elif fault == "duplicate":
        e["dispositions"].append(copy.deepcopy(e["dispositions"][0]))
    else:
        e["dispositions"][0]["alias_clear"] = False
    with pytest.raises(ValueError):
        eligible_rows(e, f[1])


@pytest.mark.parametrize("fault", [None, "contract", "rows", "score", "order"])
def test_resume_exact_contract_sources_order_and_e2_scoring(fault):
    rows, results = evaluated()
    chunk = {
        "contract_sha256": "c",
        "dataset": "zsre",
        "number": 0,
        "source_rows_sha256": digest(rows),
        "rows": results,
        "rows_sha256": digest(results),
    }
    if fault == "contract":
        chunk["contract_sha256"] = "different"
    elif fault == "rows":
        chunk["rows"].pop()
    elif fault == "score":
        chunk["rows"][0]["teacher_pass"] = True
    elif fault == "order":
        chunk["rows"].reverse()
    if fault is None:
        assert validate_chunk(chunk, "c", "zsre", 0, rows) == results
    else:
        with pytest.raises(ValueError):
            validate_chunk(chunk, "c", "zsre", 0, rows)


def test_memory_guard_and_atomic_no_overwrite(tmp_path):
    mem = tmp_path / "meminfo"
    mem.write_text("MemAvailable: 1048576 kB\n")
    assert memory_guard(0.5, mem) == 2**30
    with pytest.raises(MemoryError):
        memory_guard(2, mem)
    with pytest.raises(ValueError):
        memory_guard(0, mem)
    output = tmp_path / "result.json"
    binding = atomic_new(output, {"complete": True})
    assert len(binding["sha256"]) == 64
    with pytest.raises(FileExistsError):
        atomic_new(output, {"complete": False})
    assert json.loads(output.read_text()) == {"complete": True}
