"""Check real tokenizer boundaries and fail-closed missing preservation labels."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import asdict, replace
from pathlib import Path

import pytest

from pccap.data.tokenize import NEWLINE_ID, GPT2Tokenizer

ROOT = Path('/home/derp/cap/pc_cap')


def load(name):
    spec = importlib.util.spec_from_file_location(name, (Path('/home/derp/cap/pc_cap/logs/r1_codex_20260913/proposed_v2') / f"{name}.py") if name == "r1_20_episodes" else ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ep, adapter = load("r1_20_episodes"), load("r1_20_text_adapter")


def episode():
    rows, _ = ep.load_development(ROOT)
    return ep.natural_episode(rows, 42, "train")


def test_real_tokenizer_keeps_query_labels_out_of_input():
    e, tok = episode(), GPT2Tokenizer()
    tokenized = adapter.tokenize_natural_episode(e, tok)
    supports = tokenized.inputs.support_history + tokenized.inputs.new_support
    for support in supports:
        assert tok.decode(support.prompt_ids) == support.prompt
        assert support.answer_ids[-1] == NEWLINE_ID
        assert tok.decode(support.answer_ids).strip() == support.answer.strip()
    for q in tokenized.prediction_inputs():
        assert tok.decode(q.prompt_ids) == q.prompt
    poisoned = replace(e, query_labels=tuple(replace(label, target="different held-out answer")
                                           if label.target is not None else label for label in e.query_labels))
    assert adapter.tokenize_natural_episode(poisoned, tok).inputs.input_digest() == tokenized.inputs.input_digest()


def test_unresolved_teacher_labels_block_training():
    tokenized = adapter.tokenize_natural_episode(episode(), GPT2Tokenizer())
    assert sum(label.target_source == "teacher_prediction_required" for label in tokenized.query_labels) == 2
    with pytest.raises(ValueError, match="not training-ready"):
        adapter.require_training_targets(tokenized)


def test_design_payload_separates_scoring_metadata():
    payload = adapter.design_payload(episode())
    assert len(payload["history"]) == 4
    assert len(payload["support_new"]) == 1
    assert len(payload["queries_new"]) == 2
    assert len(payload["queries_old"]) == len(payload["near_miss"]) == len(payload["unrelated"]) == 1
    assert len(payload["labels"]) == 5
    assert payload["composition"] == ()
    for key in ("queries_new", "queries_old", "near_miss", "unrelated"):
        for q in payload[key]:
            assert set(asdict(q)) == {"query_id", "prompt_ids", "prompt"}


def test_no_implicit_vocabulary_switch_or_double_tokenization():
    tok = GPT2Tokenizer()
    with pytest.raises(ValueError, match="own vocabulary"):
        adapter.tokenize_natural_episode(ep.synthetic_episode(2), tok)
    tokenized = adapter.tokenize_natural_episode(episode(), tok)
    with pytest.raises(ValueError, match="already tokenized"):
        adapter.tokenize_natural_episode(tokenized, tok)
