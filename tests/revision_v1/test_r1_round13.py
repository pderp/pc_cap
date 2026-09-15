"""Round-13 CPU contracts: DEC-048 preservation, development preflight, and cached selection trace."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from scripts.r1_d1h_register_v5 import (
    DATASETS,
    WAIVABLE,
    apply_policy,
    build,
    capacity,
    require_usable_capacity,
)

from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.learner import RevisionCap, Selection
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.tiny_base import TinyBase

ROOT = Path(__file__).resolve().parents[2]


def candidate_module(name):
    final = ROOT / "src/pccap/revision_v1" / (name + ".py")
    path = (
        final
        if final.exists()
        else sorted((ROOT / "docs/tasks").glob("R1_67_" + name + "_candidate*.py"))[-1]
    )
    spec = importlib.util.spec_from_file_location("r13_" + name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


LOADER = candidate_module("dev_loader")
TRACE = candidate_module("selection_trace")


class Tokenizer:
    def __init__(self):
        self.reverse = {63: "\n"}
        self.forward = {"\n": 63}

    def file_sha256(self):
        return "a" * 64

    def encode(self, text):
        if text.endswith("\n"):
            return np.array([*self.encode(text[:-1]), 63], np.int32)
        if text not in self.forward:
            i = len(self.forward)
            self.forward[text] = i
            self.reverse[i] = text
        return np.array([self.forward[text]], np.int32)

    def decode(self, ids):
        return "".join(self.reverse[int(i)] for i in ids)


@pytest.fixture
def dev_fixture(tmp_path):
    dev = tmp_path / "manifests/dev"
    revision = tmp_path / "manifests/revision_v1"
    dev.mkdir(parents=True)
    revision.mkdir()
    tok = Tokenizer()
    rows = []
    for i in range(3):
        iid, prompt, answer = f"i{i}", f"subject {i}", f"answer {i}"
        rows.append(
            {
                "item_id": iid,
                "fact_id": f"f{i}",
                "subject": f"subject {i}",
                "dataset": "mquake",
                "prompt": prompt,
                "answer": answer,
                "aliases": [answer],
                "paraphrases": [prompt + "?"],
                "locality_prompts": ["neighbour"],
                "prompt_ids": tok.encode(prompt).tolist(),
                "answer_ids": tok.encode(" " + answer + "\n").tolist(),
                "digest": hashlib.sha256(f"{iid}|{prompt}|{answer}".encode()).digest()[:16].hex(),
            }
        )
    source = json.dumps({"items": rows}).encode()
    source_path = revision / "source.json"
    source_path.write_bytes(source)
    doc = {
        "mode": "dev",
        "dataset": "mquake",
        "items": rows,
        "unrelated_prompts": ["outside one", "outside two"],
        "source": {"path": str(source_path), "sha256": hashlib.sha256(source).hexdigest()},
    }
    return dev, tok, doc, {str(source_path): source}


def validated(fixture, doc=None, **kwargs):
    _, tok, base, sources = fixture
    raw = json.dumps(base if doc is None else doc).encode()
    return LOADER.validate_development_manifest(
        raw,
        dataset="mquake",
        n=kwargs.pop("n", 2),
        seed=21,
        tokenizer=tok,
        expected_sha256=hashlib.sha256(raw).hexdigest(),
        tokenizer_sha256=tok.file_sha256(),
        source_blobs=sources,
        min_unrelated=2,
        **kwargs,
    )


def test_dev_selection_preserves_old_order_and_binds_inventory(dev_fixture):
    loaded = validated(dev_fixture)
    expected = sorted(np.random.default_rng(21).permutation(3)[:2])
    assert loaded.receipt["selected_item_ids"] == [f"i{i}" for i in expected]
    assert loaded.receipt["unrelated_n"] == 2
    assert len(loaded.receipt["manifest_sha256"]) == 64
    assert loaded.receipt["source_bindings_sha256"] == {
        k: hashlib.sha256(v).hexdigest() for k, v in dev_fixture[3].items()
    }


@pytest.mark.parametrize("n", [0, -1, 4, True, 1.5])
def test_dev_count_refusal(dev_fixture, n):
    with pytest.raises(ValueError):
        validated(dev_fixture, n=n)


@pytest.mark.parametrize(
    "mutation",
    [
        "mode",
        "dataset",
        "row_dataset",
        "id",
        "fact",
        "subject",
        "digest",
        "tokens",
        "boolean_tokens",
        "source_hash",
        "unrelated_short",
        "unrelated_duplicate",
        "unrelated_overlap",
    ],
)
def test_dev_schema_and_identity_refusals(dev_fixture, mutation):
    d = copy.deepcopy(dev_fixture[2])
    if mutation == "mode":
        d["mode"] = "confirm"
    elif mutation == "dataset":
        d["dataset"] = "zsre"
    elif mutation == "row_dataset":
        d["items"][0]["dataset"] = "zsre"
    elif mutation == "id":
        d["items"][1]["item_id"] = d["items"][0]["item_id"]
    elif mutation == "fact":
        d["items"][1]["fact_id"] = d["items"][0]["fact_id"]
    elif mutation == "subject":
        d["items"][1]["subject"] = "SUBJECT   0"
    elif mutation == "digest":
        d["items"][0]["digest"] = "00" * 16
    elif mutation == "tokens":
        d["items"][0]["prompt_ids"] = [62]
    elif mutation == "boolean_tokens":
        d["items"][0]["prompt_ids"] = [True]
    elif mutation == "source_hash":
        d["source"]["sha256"] = "0" * 64
    elif mutation == "unrelated_short":
        d["unrelated_prompts"] = ["outside"]
    elif mutation == "unrelated_duplicate":
        d["unrelated_prompts"] = ["outside", "outside"]
    else:
        d["unrelated_prompts"] = [r["prompt"] for r in d["items"]]
    with pytest.raises(ValueError):
        validated(dev_fixture, d)


def test_dev_external_pin_and_missing_source_refuse(dev_fixture):
    _, tok, d, sources = dev_fixture
    raw = json.dumps(d).encode()
    for pin, blobs in [("0" * 64, sources), (hashlib.sha256(raw).hexdigest(), {})]:
        with pytest.raises(ValueError):
            LOADER.validate_development_manifest(
                raw,
                dataset="mquake",
                n=2,
                seed=21,
                tokenizer=tok,
                expected_sha256=pin,
                tokenizer_sha256=tok.file_sha256(),
                source_blobs=blobs,
                min_unrelated=2,
            )


def test_dev_exclusions_never_fall_back(dev_fixture):
    with pytest.raises(ValueError):
        validated(dev_fixture, excluded_item_ids=["i0", "i1", "i2"])
    r = validated(dev_fixture, n=1, excluded_item_ids=["i0", "i1"])
    assert r.receipt["selected_item_ids"] == ["i2"]


def test_loader_symlink_escape_refused_before_read(dev_fixture, tmp_path, monkeypatch):
    dev, tok, d, _ = dev_fixture
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps(d))
    link = dev / "escape.json"
    link.symlink_to(outside)

    def forbidden(*args, **kwargs):
        raise AssertionError("escaped content opened")

    monkeypatch.setattr(Path, "read_bytes", forbidden)
    with pytest.raises(ValueError, match="outside allowed"):
        LOADER.load_development_manifest(
            link,
            dev_root=dev,
            dataset="mquake",
            n=2,
            seed=21,
            tokenizer=tok,
            expected_sha256="0" * 64,
            tokenizer_sha256=tok.file_sha256(),
            min_unrelated=2,
        )


def test_loader_reads_bound_metadata_without_model_calls(dev_fixture):
    dev, tok, d, _ = dev_fixture
    path = dev / "input.json"
    raw = json.dumps(d).encode()
    path.write_bytes(raw)
    base = TinyBase()
    before = copy.deepcopy(base.calls)
    r = LOADER.load_development_manifest(
        path,
        dev_root=dev,
        dataset="mquake",
        n=2,
        seed=21,
        tokenizer=tok,
        expected_sha256=hashlib.sha256(raw).hexdigest(),
        tokenizer_sha256=tok.file_sha256(),
        min_unrelated=2,
    )
    assert base.calls == before
    result = base.forward(r.items[0].prompt_ids)
    assert np.asarray(result.logits).shape[-1] == 64


@pytest.mark.parametrize("rare_min,expected", [(1, "accepted"), (100, "rejected")])
def test_trace_reuses_real_tiny_selection_with_final_gate(rare_min, expected):
    base = TinyBase()
    cfg = _cfg(null_threshold=1.01, rare_overlap_min=rare_min)
    cfg.fast = FastConfig(steps=0)
    cap = RevisionCap(base, cfg, Ledger())
    support = _support(0)
    adapt_record(cap, support, cap.cfg.fast)
    selected = cap.selection_for(np.array(support.prompt_ids, np.int32))
    state = cap.state_hash()
    calls = copy.deepcopy(base.calls)
    counters = copy.deepcopy(cap.cost_counters)
    trace = TRACE.selection_trace(selected, config=cfg)
    assert trace["rare_gate_verdict"] == expected
    assert trace["hard_null"] is (expected == "rejected")
    assert trace["selected_record_id"] == "s0"
    assert trace["applied_record_ids"] == (["s0"] if expected == "accepted" else [])
    assert base.calls == calls and cap.cost_counters == counters and cap.state_hash() == state
    assert cap.selection_for(np.array(support.prompt_ids, np.int32)) is selected


def test_trace_preserves_legacy_and_marks_unknown_cause():
    sel = Selection(2, ["a", "b"], np.array([0.2, 0.8]), 0.1, None, True, best_score=0.9)
    trace = TRACE.selection_trace(sel)
    assert trace["record_ids"] == ["a", "b"] and trace["best_score"] == 0.9
    assert trace["selected_record_id"] == "b" and trace["selected_weight"] == 0.8
    assert trace["hard_null"] and trace["rare_gate_verdict"] == "unavailable"
    assert trace["applied_selected_weight"] == 0


def test_trace_prior_gate_is_not_rare_gate_rejection():
    cfg = SimpleNamespace(rare_overlap_min=1, null_threshold=0.5, min_score=None)
    sel = Selection(1, ["a"], np.ones(1), 0.8, None, True, best_score=0.9)
    assert TRACE.selection_trace(sel, config=cfg)["rare_gate_verdict"] == "not_evaluated_prior_gate"


@pytest.mark.parametrize(
    "reason",
    [
        "mquake_training_reserved_subject",
        "mquake_development_reserved_subject",
        "sealed",
        "drawn",
        "conflict",
        "context_quarantine",
        "cross_dataset_priority:zsre",
        "unknown_near_miss_counterfactual_query_subject",
    ],
)
def test_policy_preserves_every_nonwaived_reason(reason):
    query = sorted(WAIVABLE)[0]
    source = [{"item_id": "x", "subject": "alice"}]
    parent = {"candidates": {ds: [] for ds in DATASETS}, "removals": {ds: [] for ds in DATASETS}}
    parent["removals"]["mquake"] = [
        {"item_id": "x", "canonical_subject": "alice", "reasons": [query, reason]}
    ]
    got = apply_policy(parent, source)
    assert got["candidates"]["mquake"] == []
    assert got["removals"]["mquake"][0]["reasons"] == [reason]
    assert parent["removals"]["mquake"][0]["reasons"] == [query, reason]


def test_policy_is_mquake_only():
    query = sorted(WAIVABLE)[0]
    row = {"item_id": "x", "canonical_subject": "alice", "reasons": [query]}
    parent = {
        "candidates": {ds: [] for ds in DATASETS},
        "removals": {ds: [copy.deepcopy(row)] for ds in DATASETS},
    }
    out = apply_policy(parent, [{"item_id": "x", "subject": "alice"}])
    assert len(out["candidates"]["mquake"]) == 1
    for ds in ("zsre", "counterfact"):
        assert out["removals"][ds] == parent["removals"][ds] and out["candidates"][ds] == []


def test_register_capacity_and_abort_threshold():
    r = build()
    assert [r["counts"][ds]["candidate_subjects"] for ds in DATASETS] == [52411, 12246, 4218]
    assert r["counts"]["mquake"]["candidate_items"] == 4489
    assert capacity(4218, 4489)["first_subject_loss_count_causing_shortfall"] == 169
    cleared = {
        ds: sorted({x["canonical_subject"] for x in r["candidates"][ds]})[:4050] for ds in DATASETS
    }
    assert require_usable_capacity(r, cleared) == {ds: 4050 for ds in DATASETS}
    cleared["mquake"].pop()
    with pytest.raises(ValueError, match="abort before RNG"):
        require_usable_capacity(r, cleared)
    assert r["draw_authorized"] is False


def test_clearance_unknown_and_duplicate_subjects_refuse():
    r = {"candidates": {ds: [{"canonical_subject": "a"}] for ds in DATASETS}}
    for bad in (["a", "a"], ["unknown"]):
        cleared = {ds: ["a"] for ds in DATASETS}
        cleared["mquake"] = bad
        with pytest.raises(ValueError):
            require_usable_capacity(r, cleared, demand=1)
