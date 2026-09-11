"""Baseline arms through the harness (Lane F integration): batched evaluation parity and a
run_stream smoke for B0/B1/B3/B4 (GPU, short; no lease). B4 (GRACE, DEC-020) additionally checks that the
boundary-keyed batched path equals the learner's own predict at the original prompt position."""

from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.bases.bp import BPBase
from pccap.contracts import Budget
from pccap.data.decode import _last_logits
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.arms import make_learner, router_for
from pccap.harness.ledger import Ledger
from pccap.harness.runs import Evaluator, run_stream
from pccap.harness.stage_s2 import load_dev_items

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def setup():
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    tok = GPT2Tokenizer()
    items, unrelated = load_dev_items("zsre", 4, seed=7)
    return ledger, base, tok, items, unrelated


@pytest.mark.parametrize("arm", ["B0", "B1", "B3", "B4"])
def test_batched_last_logits_matches_sequential_predict(setup, arm):
    ledger, base, tok, items, unrelated = setup
    learner = make_learner(arm, base, ledger, seed=0)
    if arm != "B0":
        learner.update_item(items[0])
    prompts = [np.asarray(it.prompt_ids, np.int32) for it in items] + [np.asarray(tok.encode(u), np.int32) for u in unrelated[:4]]
    batched = learner.last_logits_batch(prompts)
    seq = np.stack([_last_logits(getattr(out := learner.predict(p), "logits", out)) for p in prompts])  # B4's predict returns the array itself
    assert batched.shape == seq.shape
    assert np.max(np.abs(batched - seq)) <= 1e-3
    assert np.array_equal(np.argmax(batched, -1), np.argmax(seq, -1))


@pytest.mark.parametrize("arm", ["B1", "B3", "B4"])
def test_run_stream_smoke(setup, arm):
    ledger, base, tok, items, unrelated = setup
    tmp_path = ROOT / "results" / "tests" / "baseline_smoke"  # run_stream requires a results/ subpath
    shutil.rmtree(tmp_path / arm, ignore_errors=True)
    learner = make_learner(arm, base, ledger, seed=0)
    ev = Evaluator(base, tok, unrelated[:3], None)
    h = base.checksum()
    m = run_stream(learner, items[:3], router_for(arm), Budget(A=0.3), ev, tmp_path / arm, ledger, checkpoints=(), arm=arm)
    assert base.checksum() == h
    assert m["items_completed"] == 3 and m["status"] == "complete"
    assert m["metrics"]["es_immediate"]["value"] is not None
    assert (tmp_path / arm / "items.jsonl").exists()
    rows = [line for line in (tmp_path / arm / "items.jsonl").read_text().splitlines() if line]
    assert len(rows) == 3
    assert ledger.totals()["learning"]["full_forwards"] >= 30  # 10 steps × ≥1 sequence × 3 items


def test_b4_boundary_keyed_batch_matches_predict_at_prompt_position(setup):
    ledger, base, tok, items, unrelated = setup
    learner = make_learner("B4", base, ledger, seed=0)
    assert learner.decode_key_positions and learner.name == "B4"
    learner.update_item(items[0])
    it = items[0]
    prefixes, bounds = [], []
    ids = np.asarray(it.prompt_ids, np.int32)
    for y in np.asarray(it.answer_ids, np.int32)[:3]:
        prefixes.append(ids)
        bounds.append(len(it.prompt_ids) - 1)
        ids = np.concatenate([ids, np.int32([y])])
    batched = learner.last_logits_batch(prefixes, key_positions=bounds)
    seq = np.stack([learner.learner.predict(p, key_position=b, last_only=True) for p, b in zip(prefixes, bounds)])
    assert np.max(np.abs(batched - seq)) <= 1e-4
    # keyed at the growing last position instead, the codebook lookup can differ once the answer tokens are appended
    unkeyed = learner.last_logits_batch(prefixes)
    assert unkeyed.shape == batched.shape
