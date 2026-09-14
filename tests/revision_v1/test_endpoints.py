"""Endpoint scoring/purity tests with controlled answers and a real tiny CPU cap."""

from __future__ import annotations

import json
from types import SimpleNamespace

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.contracts import CostRecord, ForwardResult
from pccap.harness.ledger import Ledger
from pccap.revision_v1.contracts import MemoryRecord, support_from_edit_item
from pccap.revision_v1.endpoints import (
    EndpointEvaluator,
    bridge_template,
    load_dev_challenges,
    row_hash,
    summarize,
)
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import RecordStore
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.tiny_base import TinyBase


class Tokenizer:
    def __init__(self):
        self.strings = {198: "\n"}
        self.ids = {"\n": 198}

    def token(self, text):
        if text not in self.ids:
            i = len(self.ids) + 1
            self.ids[text] = i
            self.strings[i] = text
        return self.ids[text]

    def encode(self, text):
        if text.endswith("\n"):
            return np.int32([self.token(text[:-1]), 198])
        return np.int32([self.token(text)])

    def decode(self, ids):
        return "".join(self.strings[int(i)] for i in ids)


class Base:
    def __init__(self, tok, answers):
        self.tok = tok
        self.answers = {tuple(tok.encode(p)): a for p, a in answers.items()}

    def checksum(self, recompute=True):
        return "fixture-base"

    def result(self, ids, answers):
        choices = [(p, a) for p, a in answers.items() if tuple(ids[: len(p)]) == p]
        prompt, answer = (
            max(choices, key=lambda x: len(x[0])) if choices else ((int(ids[0]),), "unknown")
        )
        token = self.tok.token(" " + answer) if len(ids) == len(prompt) else 198
        logits = np.full(512, -100.0)
        logits[token] = 0
        return ForwardResult(
            logits=logits,
            sites={},
            cost=CostRecord(phase="query", full_forwards=1, tokens=len(ids)),
        )

    def forward(self, ids, **kw):
        return self.result(ids, self.answers)


class Cap:
    def __init__(self, tok, answers=None):
        self.base = Base(tok, answers or {})
        self.store = RecordStore(2, 2)
        self.answers = {}
        self.selected = None
        self.reset_count = 0
        self.fail_revision = False
        self.wrong_bridge = False
        self.mutate_read = False
        self.queries = []

    def export_state(self):
        st = self.store.export()
        st.scalars["fixture_answers"] = json.dumps([[[int(i) for i in k], v] for k, v in self.answers.items()])
        return st

    def import_state(self, st):
        self.store = RecordStore.from_state(st)
        self.answers = {tuple(k): v for k, v in json.loads(st.scalars["fixture_answers"])}
        self.reset_queries()

    def state_hash(self):
        return self.export_state().content_hash()

    def reset_queries(self):
        self.selected = None
        self.reset_count += 1

    def selection_for(self, ids):
        if self.selected is None:
            self.selected = SimpleNamespace(
                record_ids=[r.record_id for r in self.store.active_records()],
                null_mass=0.0,
                best_score=1.0,
                prompt_len=len(ids),
            )
        return self.selected

    def predict(self, ids):
        self.selection_for(ids)
        self.queries.append(tuple(ids))
        if self.mutate_read:
            self.answers[(999,)] = "mutation"
        answers = {**self.base.answers, **self.answers}
        if self.wrong_bridge:
            answers[tuple(self.base.tok.encode("first?"))] = "wrong"
        return self.base.result(ids, answers)

    def update_item(self, item):
        cost = CostRecord(
            phase="learning", full_forwards=1, tokens=len(item.prompt_ids) + len(item.answer_ids)
        )
        if self.fail_revision and item.version == 2:
            return SimpleNamespace(
                code="acquisition_failure", codes=["resource_failure:delta_capacity"], cost=cost
            )
        s = support_from_edit_item(item)
        rec = MemoryRecord(
            s.record_id, s.fact_id, s.revision, -1, np.zeros(2, np.float32), np.zeros(2, np.float32)
        )
        old = [r for r in self.store.active_records() if r.fact_id == s.fact_id]
        if old:
            self.store.supersede(old[0].record_id, rec)
        else:
            self.store.add(rec)
        self.answers[tuple(item.prompt_ids)] = item.answer
        for prompt in item.paraphrases:
            self.answers[tuple(self.base.tok.encode(prompt))] = item.answer
        return SimpleNamespace(code="accepted", codes=["accepted"], cost=cost)


def near_row():
    return {
        "dataset": "fixture",
        "edit_item_id": "fact",
        "edit_prompt": "edit?",
        "edit_answer": "new",
        "neighbour_prompt": "neighbour?",
        "neighbour_answer": "deliberately incorrect label",
    }


def revision_row():
    return {
        "dataset": "fixture",
        "fact_id": "fact",
        "prompt": "edit?",
        "paraphrases": ["rephrased?"],
        "versions": [
            {"version": 1, "answer": "old", "aliases": ["old"]},
            {"version": 2, "answer": "new", "aliases": ["new"]},
        ],
    }


def comp_row():
    return {
        "dataset": "fixture",
        "first_item_id": "fact1",
        "first_prompt": "first?",
        "o1": "Bridge",
        "second_item_id": "fact2",
        "second_prompt": "Where is Bridge?",
        "o2": "Final",
    }


def verification(row):
    return {
        "status": "verified",
        "row_sha256": row_hash(row),
        "method": "planted fixture with explicit two-fact ground truth",
    }


def test_near_miss_uses_capoff_answer_and_restores_state():
    tok = Tokenizer()
    cap = Cap(tok, {"neighbour?": "base answer"})
    before = cap.state_hash()
    result = EndpointEvaluator(cap, tok).near_miss(near_row())
    assert result["status"] == "ok" and result["preserved"] and result["edit_exact"]
    assert result["reference"]["generated"].strip() == "base answer"
    assert not result["stored_neighbour_answer_used_for_scoring"]
    assert cap.state_hash() == before and not cap.store.records
    assert cap.selected is None and cap.reset_count >= 5
    assert sum(e["returned_cost"]["full_forwards"] for e in result["events"]) >= 7


def test_revision_new_answer_and_retirement_both_required():
    tok = Tokenizer()
    cap = Cap(tok)
    result = EndpointEvaluator(cap, tok).revision(revision_row())
    assert (
        result["revision_success"] and result["old_record_retired"] and result["new_record_active"]
    )
    assert result["old_answer_acquired_before_revision"]
    assert result["old_answer_reappearance_n"] == 0 and result["query_n"] == 2
    assert result["paraphrase_new_exact_fraction"] == 1.0
    assert not cap.store.records and not cap.answers


def test_resource_rejection_remains_distinct_and_charged():
    tok = Tokenizer()
    cap = Cap(tok)
    cap.fail_revision = True
    result = EndpointEvaluator(cap, tok).revision(revision_row())
    assert result["status"] == "resource_failure" and "delta_capacity" in result["reason"]
    assert result["events"][-1]["code"] == "acquisition_failure"
    assert not cap.store.records
    summary = summarize([result], "revision_success")
    assert (
        summary["planned"] == 1
        and summary["scored"] == 0
        and summary["full_inventory_fraction"] is None
    )


def test_overlapping_revision_aliases_refused_before_update():
    tok = Tokenizer()
    cap = Cap(tok)
    row = revision_row()
    row["versions"][1]["aliases"] = ["old"]
    result = EndpointEvaluator(cap, tok).revision(row)
    assert result["status"] == "unreachable" and not result["events"]


def test_composition_uses_generated_bridge_and_checks_missing_hops():
    tok = Tokenizer()
    cap = Cap(tok)
    row = comp_row()
    ev = EndpointEvaluator(cap, tok)
    result = ev.composition(row, verification=verification(row))
    assert result["chain_success"] and result["direct_composition"]["status"] == "unreachable"
    assert set(result["support_record_ids"]) == {"fact1", "fact2"}
    cap.wrong_bridge = True
    wrong = ev.composition(row, verification=verification(row))
    assert wrong["status"] == "ok" and not wrong["chain_success"] and not wrong["first_hop_exact"]
    assert tuple(tok.encode("Where is wrong?")) in cap.queries
    missing = ev.composition(row, verification=verification(row), teach=False)
    assert missing["status"] == "unreachable" and missing["reason"].startswith("missing_hop:")
    assert not cap.store.records


def test_unverified_composition_does_no_work():
    tok = Tokenizer()
    cap = Cap(tok)
    result = EndpointEvaluator(cap, tok).composition(comp_row())
    assert result["status"] == "unreachable" and not result["events"] and not cap.queries


def test_read_mutation_raises_and_restores_clone():
    tok = Tokenizer()
    cap = Cap(tok)
    cap.mutate_read = True
    before = cap.state_hash()
    with pytest.raises(RuntimeError, match="mutated"):
        EndpointEvaluator(cap, tok).near_miss(near_row())
    assert cap.state_hash() == before


def test_bridge_template_requires_unique_whole_entity():
    assert bridge_template("Where is BRIDGE?", "Bridge") == "Where is {bridge}?"
    with pytest.raises(ValueError):
        bridge_template("Bridge or Bridge?", "Bridge")
    with pytest.raises(ValueError):
        bridge_template("Where is Bridgerton?", "Bridge")


def test_actual_inventory_counts():
    _doc, binding = load_dev_challenges()
    inv = binding["inventory"]
    assert {k: v["available_rows"] for k, v in inv.items()} == {
        "near_neighbour": 400,
        "composition": 54,
        "temporal_correction": 100,
    }
    assert inv["composition"]["shortfall"] == 46
    assert inv["near_neighbour"]["source_population_n"] != inv["near_neighbour"]["available_rows"]


def test_real_tiny_cap_resets_between_independent_queries():
    class TinyTok:
        def encode(self, text):
            return np.int32([2, 3] if text == "short" else [2, 3, 4])

        def decode(self, ids):
            return " ".join(str(int(i)) for i in ids)

    cap = RevisionCap(TinyBase(), _cfg(), Ledger())
    ev = EndpointEvaluator(cap, TinyTok(), max_new=1)
    before = cap.state_hash()
    _, a = ev._read(cap, "short")
    _, b = ev._read(cap, "long")
    assert a["selection"]["prompt_len"] == 2 and b["selection"]["prompt_len"] == 3
    assert a["returned_cost"]["full_forwards"] == b["returned_cost"]["full_forwards"] == 1
    assert not cap._sel and cap.state_hash() == before
