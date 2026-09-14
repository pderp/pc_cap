"""Unseen-prompt admission, denominators, read purity and tiny CPU execution."""

from __future__ import annotations

import copy

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.harness.ledger import Ledger
from pccap.revision_v1.contracts import MemoryRecord
from pccap.revision_v1.endpoints_unseen import UnseenPromptEvaluator
from pccap.revision_v1.learner import RevisionCap
from tests.revision_v1.test_endpoints import Cap, Tokenizer
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.tiny_base import TinyBase

POOL = [
    {"item_id": "edit", "fact_id": "f-edit", "subject": "Edited", "prompt": "edit?"},
    {"item_id": "outside", "fact_id": "f-outside", "subject": "Outside", "prompt": "outside?"},
    {"item_id": "long", "fact_id": "f-long", "subject": "Long", "prompt": "long?"},
]
SOURCE = "a" * 64


def fixture():
    tok = Tokenizer()
    cap = Cap(tok, {"outside?": "base", "long?": "other"})
    cap.store.add(
        MemoryRecord("r-edit", "f-edit", 1, -1, np.ones(2, np.float32), np.zeros(2, np.float32))
    )
    return tok, cap


def observe_fire(_learner, _ids):
    return {"hard_null": False, "false_fire": True, "selected_record_ids": ["r-edit"]}


def evaluate(cap, tok, queries=("outside",), pool=None, **kwargs):
    ev = UnseenPromptEvaluator(
        cap, tok, pool or POOL, pool_id="fixture", source_sha256=SOURCE, **kwargs
    )
    return ev.evaluate(
        queries, edited_item_ids=["edit"], expected_n=len(queries), checkpoint_id="M1"
    )


def test_firing_and_answer_change_are_distinct():
    tok, cap = fixture()
    before = cap.state_hash()
    same = evaluate(cap, tok, selection_observer=observe_fire)
    assert same["summary"]["false_fire_rate_full_inventory"] == 1
    assert same["summary"]["answer_change_rate_full_inventory"] == 0
    assert same["summary"]["complete_answer_preservation_rate_full_inventory"] == 1
    assert cap.state_hash() == before and cap.selected is None
    cap.answers[tuple(tok.encode("outside?"))] = "changed"
    changed = evaluate(cap, tok, selection_observer=observe_fire)
    assert changed["summary"]["answer_change_rate_full_inventory"] == 1
    assert changed["rows"][0]["reference"]["generated"].strip() == "base"
    assert changed["rows"][0]["cap_query"]["generated"].strip() == "changed"


def test_missing_firing_observer_is_unavailable_not_zero():
    tok, cap = fixture()
    result = evaluate(cap, tok)
    assert result["summary"]["firing_observed_n"] == 0
    assert result["summary"]["false_fire_rate_full_inventory"] is None
    assert result["summary"]["answer_change_rate_full_inventory"] == 0


def test_edited_alias_subject_prompt_and_unknown_are_retained_as_unreachable():
    tok, cap = fixture()
    aliases = [
        {"item_id": "same-fact", "fact_id": "f-edit", "subject": "Different", "prompt": "alias?"},
        {
            "item_id": "same-subject",
            "fact_id": "other",
            "subject": "  EDITED ",
            "prompt": "alias2?",
        },
        {"item_id": "same-prompt", "fact_id": "another", "subject": "Another", "prompt": " EDIT? "},
    ]
    result = evaluate(
        cap,
        tok,
        ["edit", "same-fact", "same-subject", "same-prompt", "missing"],
        pool=POOL + aliases,
    )
    assert result["summary"]["status_counts"] == {"unreachable": 5}
    assert result["summary"]["coverage"] == 0
    assert result["summary"]["answer_change_rate_full_inventory"] is None
    assert not cap.queries


def test_full_history_excludes_retired_records_and_requires_memory_coverage():
    tok, cap = fixture()
    cap.store.records[0].active = False
    result = evaluate(cap, tok, ["edit"])
    assert result["rows"][0]["status"] == "unreachable"
    ev = UnseenPromptEvaluator(cap, tok, POOL, pool_id="fixture", source_sha256=SOURCE)
    with pytest.raises(ValueError, match="cover"):
        ev.evaluate(["outside"], edited_item_ids=[], expected_n=1, checkpoint_id="M1")
    assert not cap.queries


def test_shortfalls_duplicates_and_missing_edit_history():
    tok, cap = fixture()
    ev = UnseenPromptEvaluator(cap, tok, POOL, pool_id="fixture", source_sha256=SOURCE)
    result = ev.evaluate(["outside"], edited_item_ids=["edit"], expected_n=3, checkpoint_id="M1")
    assert result["summary"]["source_shortfall"] == 2
    assert result["summary"]["coverage"] == 1 / 3
    assert result["summary"]["answer_change_rate_full_inventory"] is None
    with pytest.raises(ValueError, match="unique"):
        ev.evaluate(
            ["outside", "outside"], edited_item_ids=["edit"], expected_n=2, checkpoint_id="M1"
        )
    with pytest.raises(ValueError, match="contained"):
        ev.evaluate(["outside"], edited_item_ids=["missing"], expected_n=1, checkpoint_id="M1")


def test_source_and_expected_denominator_admission():
    tok, cap = fixture()
    with pytest.raises(ValueError, match="SHA-256"):
        UnseenPromptEvaluator(cap, tok, POOL, pool_id="fixture", source_sha256="bad")
    with pytest.raises(ValueError, match="duplicate"):
        UnseenPromptEvaluator(cap, tok, POOL + [POOL[0]], pool_id="fixture", source_sha256=SOURCE)
    ev = UnseenPromptEvaluator(cap, tok, POOL, pool_id="fixture", source_sha256=SOURCE)
    for value in (0, True, -1):
        with pytest.raises(ValueError):
            ev.evaluate(["outside"], edited_item_ids=["edit"], expected_n=value, checkpoint_id="M1")


def test_labels_do_not_change_query_metadata_or_predictions():
    tok, cap = fixture()
    pool = copy.deepcopy(POOL)
    for item in pool:
        item.update(answer="unread label", aliases=["unread alias"], answer_ids=[999])
    before = evaluate(cap, tok)
    after = evaluate(cap, tok, pool=pool)
    assert before["pool_query_metadata_sha256"] == after["pool_query_metadata_sha256"]
    assert before["rows"][0]["source_row_sha256"] == after["rows"][0]["source_row_sha256"]
    assert before["summary"] == after["summary"]


def test_mutating_reads_restore_state_and_raise():
    tok, cap = fixture()
    cap.mutate_read = True
    before = cap.state_hash()
    with pytest.raises(RuntimeError, match="mutated"):
        evaluate(cap, tok)
    assert cap.state_hash() == before and cap.selected is None


class TinyTokenizer:
    def encode(self, text):
        return np.int32([2, 3] if text == "outside?" else [2, 3, 4])

    def decode(self, ids):
        return " ".join(str(int(i)) for i in ids)


def test_tiny_base_independent_queries_and_truncation():
    cap = RevisionCap(TinyBase(), _cfg(), Ledger())
    before = cap.state_hash()
    ev = UnseenPromptEvaluator(
        cap, TinyTokenizer(), POOL, pool_id="tiny", source_sha256=SOURCE, max_new=1
    )
    result = ev.evaluate(["outside", "long"], edited_item_ids=[], expected_n=2, checkpoint_id="M0")
    assert result["summary"]["false_fire_rate_full_inventory"] == 0
    assert result["summary"]["answer_change_rate_full_inventory"] == 0
    assert result["summary"]["incomplete_answer_pairs_n"] == 2
    assert result["summary"]["complete_answer_preservation_rate_full_inventory"] == 0
    assert [r["cap_query"]["prompt_tokens"] for r in result["rows"]] == [2, 3]
    assert cap.cost_counters["selection_passes"] == 2
    assert not cap._sel and cap.state_hash() == before
    assert sum(r["cap_query"]["returned_cost"]["full_forwards"] for r in result["rows"]) == 2


def test_tiny_base_forced_gate_reports_false_fire():
    cap = RevisionCap(TinyBase(), _cfg(null_threshold=1.01), Ledger())
    cap.store.add(
        MemoryRecord(
            "r-edit",
            "f-edit",
            1,
            -1,
            np.ones(8, np.float32),
            np.zeros(6, np.float32),
            source_ids=np.int32([4, 5]),
        )
    )
    before = cap.state_hash()
    ev = UnseenPromptEvaluator(
        cap, TinyTokenizer(), POOL, pool_id="tiny", source_sha256=SOURCE, max_new=1
    )
    result = ev.evaluate(["outside"], edited_item_ids=["edit"], expected_n=1, checkpoint_id="M1")
    assert result["summary"]["false_fire_rate_full_inventory"] == 1
    assert result["rows"][0]["selection"]["selected_record_ids"] == ["r-edit"]
    assert cap.state_hash() == before and not cap._sel
