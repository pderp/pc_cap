"""Direct composition tests: controlled ground truth and actual TinyBase CPU smoke."""

from types import SimpleNamespace

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.contracts import CostRecord, EditItem
from pccap.harness.ledger import Ledger
from pccap.revision_v1.endpoints_composition import (
    CompositionEvaluator,
    expected_case_counts,
    select_for_realizations,
)
from pccap.revision_v1.learner import RevisionCap
from tests.revision_v1.test_endpoints import Cap, Tokenizer
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.tiny_base import TinyBase


def case(ids=("a", "b"), number=1):
    return {
        "composition_id": f"case:{number}",
        "case_id": number,
        "verified_source": "MQuAKE",
        "all_rewrite_dependencies_available": True,
        "questions": ["composed one?", "composed two?", "composed three?"],
        "answer": "old",
        "answer_aliases": ["old"],
        "new_answer": "final",
        "new_answer_aliases": ["final", "FINAL ALIAS"],
        "dependencies": [
            {"item_id": i, "status": "available_source_item", "required_target_new": {"str": "new"}}
            for i in ids
        ],
    }


def items(ids=("a", "b")):
    return {
        i: {
            "item_id": i,
            "dataset": "mquake",
            "prompt": i + "?",
            "answer": "new",
            "aliases": ["new"],
            "paraphrases": [],
            "locality_prompts": [],
        }
        for i in ids
    }


class ComposingCap(Cap):
    def __init__(self, tok):
        super().__init__(tok, {q: "old" for q in case()["questions"]})
        self.teaching_order = []
        self.bad_one = False
        self.behavior_failure = False
        self.resource_failure = False

    def update_item(self, item):
        self.teaching_order.append(item.item_id)
        if self.resource_failure:
            return SimpleNamespace(
                code="acquisition_failure",
                codes=["resource_failure:capacity"],
                cost=CostRecord(phase="learning", full_forwards=1),
            )
        if self.behavior_failure:
            return SimpleNamespace(
                code="acquisition_failure",
                codes=["threshold_miss"],
                cost=CostRecord(phase="learning", full_forwards=1),
            )
        return super().update_item(item)

    def predict(self, ids):
        self.selection_for(ids)
        self.queries.append(tuple(ids))
        answers = dict(self.base.answers)
        if len(self.store.active_records()) >= 2:
            answers.update(
                {tuple(self.base.tok.encode(q)): "final alias" for q in case()["questions"]}
            )
        if self.bad_one:
            answers[tuple(self.base.tok.encode(case()["questions"][1]))] = "old"
        return self.base.result(ids, answers)


def test_teach_all_dependencies_in_stream_order_three_alias_queries_and_restore():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    before = cap.state_hash()
    out = CompositionEvaluator(cap, tok).evaluate([case()], items(), edit_order=["b", "a"])
    row, summary = out["rows"][0], out["summary"]
    assert row["status"] == "ok" and row["composition_success"]
    assert row["dependency_ids"] == cap.teaching_order == ["b", "a"]
    assert all(q["cap_off_pre_edit_exact"] and q["post_edit_exact"] for q in row["queries"])
    assert not row["pre_edit_answer_reappeared"]
    assert summary["planned"] == summary["evaluable"] == summary["scored"] == 1
    assert summary["paraphrase_successes"] == 3 and summary["full_inventory_fraction"] == 1
    assert cap.state_hash() == before and not cap.store.records


def test_one_failed_paraphrase_fails_whole_case_and_records_old_reappearance():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    cap.bad_one = True
    row = CompositionEvaluator(cap, tok).evaluate([case()], items())["rows"][0]
    assert not row["composition_success"] and row["paraphrase_successes"] == 2
    assert row["pre_edit_answer_reappeared"]


@pytest.mark.parametrize(
    "problem",
    ["missing", "conflict", "excluded", "target_mismatch", "no_verification", "two_questions"],
)
def test_unavailable_cases_do_no_teaching_and_preserve_denominator(problem):
    tok = Tokenizer()
    cap = ComposingCap(tok)
    c, pool = case(), items()
    if problem == "missing":
        pool.pop("b")
    elif problem == "conflict":
        c["all_rewrite_dependencies_available"] = False
    elif problem == "excluded":
        c["dependencies"][1]["status"] = "excluded_subject"
    elif problem == "target_mismatch":
        c["dependencies"][1]["required_target_new"]["str"] = "other"
    elif problem == "no_verification":
        c["verified_source"] = "inferred"
    else:
        c["questions"].pop()
    out = CompositionEvaluator(cap, tok).evaluate([c], pool, expected_n=2)
    assert out["rows"][0]["status"] == "unavailable" and not cap.teaching_order
    assert (
        out["summary"]["planned"] == 2
        and out["summary"]["evaluable"] == out["summary"]["scored"] == 0
    )
    assert out["summary"]["full_inventory_fraction"] is None


def test_behavioral_acquisition_failure_remains_scored():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    cap.behavior_failure = True
    out = CompositionEvaluator(cap, tok).evaluate([case()], items())
    assert out["summary"]["scored"] == 1 and out["summary"]["successes"] == 0
    assert out["rows"][0]["pre_edit_answer_reappeared"]


def test_resource_failure_retains_evaluable_count_and_failed_work():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    cap.resource_failure = True
    out = CompositionEvaluator(cap, tok).evaluate([case()], items())
    assert out["summary"]["evaluable"] == 1 and out["summary"]["scored"] == 0
    assert out["rows"][0]["events"][-1]["returned_cost"]["full_forwards"] == 1
    assert not cap.store.records


def test_independent_start_state_avoids_reteaching_parent_and_restores_parent():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    empty = cap.export_state().clone()
    from pccap.revision_v1.endpoints_composition import as_edit

    cap.update_item(as_edit(items()["a"], tok))
    parent = cap.state_hash()
    out = CompositionEvaluator(cap, tok, teaching_state=empty).evaluate([case()], items())
    assert out["rows"][0]["composition_success"]
    assert cap.state_hash() == parent and len(cap.store.active_records()) == 1


def test_truncated_answers_do_not_pass_complete_answer_score():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    out = CompositionEvaluator(cap, tok, max_new=1).evaluate([case()], items())
    assert out["summary"]["successes"] == 0
    assert all(q["cap_query"]["truncated"] for q in out["rows"][0]["queries"])


def test_selection_is_membership_only_with_unavailable_source_cases_retained():
    good, bad = case(), case(number=2)
    bad["all_rewrite_dependencies_available"] = False
    other = case(("a", "c"), number=3)
    out = select_for_realizations([good, bad, other], {"r0": ["b", "a"], "r1": ["c"]})
    assert out["expected"]["r0"] == {"cases": 2, "paraphrases": 6}
    assert out["expected"]["r1"]["cases"] == 0
    assert out["unattached_case_ids"] == ["case:3"]


def test_overlapping_realizations_refused():
    with pytest.raises(ValueError, match="disjoint"):
        select_for_realizations([case()], {"r0": ["a"], "r1": ["a"]})


def test_exact_stratified_expectation_no_random_draw():
    candidates = [{"item_id": i, "subject": i, "stratum": "s"} for i in "abcd"]
    out = expected_case_counts([case(("a",), 1), case(("a", "b"), 2)], candidates, {"r0": {"s": 2}})
    assert out["by_realization"]["r0"]["expected_cases"] == pytest.approx(0.5 + 1 / 6)
    assert out["by_realization"]["r0"]["expected_paraphrases"] == pytest.approx(2)
    assert out["draws"] == 0


def test_bad_planned_count_refused_before_calls():
    tok = Tokenizer()
    cap = ComposingCap(tok)
    with pytest.raises(ValueError):
        CompositionEvaluator(cap, tok).evaluate([case()], items(), expected_n=0)
    assert not cap.teaching_order and not cap.queries


def test_actual_tinybase_cap_on_cpu_composition_state_and_missingness():
    class TinyTok:
        def encode(self, text):
            return np.int32([2, 3])

        def decode(self, ids):
            return " ".join(str(int(i)) for i in ids)

    tok = TinyTok()
    cfg = _cfg()
    cfg.fast.steps = cfg.fast.delta_steps = 0
    cap = RevisionCap(TinyBase(), cfg, Ledger())
    fixture = {
        i: EditItem(
            i,
            bytes([j]) * 16,
            i + "?",
            "new",
            ["new"],
            [],
            [],
            np.int32([2, 3]),
            np.int32([4]),
            dataset="mquake",
            fact_id=i,
        )
        for j, i in enumerate(("a", "b"), 1)
    }
    before = cap.state_hash()
    out = CompositionEvaluator(cap, tok, max_new=1).evaluate([case()], fixture)
    assert out["summary"]["scored"] == 1
    assert out["summary"]["successes"] == 0 and cap.state_hash() == before
    assert cap.base.calls["forward"] > 0
