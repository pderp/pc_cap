"""S0-09: reference greedy decoder — no cache, full recompute, read-only, no answer argument;
BP-base decode equals the float64 reference model's greedy decode (HF oracle rows pending REF-01)."""

import inspect
import json
from pathlib import Path

import numpy as np
import pytest

import pccap
from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.data.decode import greedy_decode, score_generation, teacher_forced_nll
from pccap.data.tokenize import GPT2Tokenizer
from tests.bases import ref_numpy_gpt2 as ref

ROOT = Path(__file__).resolve().parents[2]
ORACLE = Path(pccap.ASSETS_ROOT) / "reference" / "gpt2" / "greedy_8.json"


@pytest.fixture(scope="module")
def tok():
    return GPT2Tokenizer()


def test_no_answer_argument():
    assert "answer" not in inspect.signature(greedy_decode).parameters
    assert "aliases" not in inspect.signature(greedy_decode).parameters


def test_mock_decoder_semantics(tok):
    V = 50257
    seq = [464, 3139, 286, 4881, 318, 6342, 198]  # "The capital of France is Paris\n"

    def predict(ids):
        # returns a [V] row whose argmax is the next token of `seq` (ties handled by argmax)
        row = np.zeros(V, np.float32)
        row[seq[len(ids)]] = 5.0
        return row

    r = greedy_decode(predict, np.array(seq[:5], np.int32), tok)
    assert r.stopped_by == "newline" and not r.truncated and r.text == " Paris" and r.steps == 2
    r2 = greedy_decode(lambda ids: np.zeros(V, np.float32), np.array(seq[:5], np.int32), tok, max_new=3)
    assert r2.stopped_by == "max" and r2.truncated and r2.steps == 3 and list(r2.new_ids) == [0, 0, 0]


@pytest.mark.gpu
def test_bp_decode_matches_f64_reference(tok):
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    base = BPBase()
    params = g.load_params_numpy()
    calls = {"n": 0}

    def predict(ids):
        calls["n"] += 1
        return base.forward(ids, phase="query").logits

    for prompt in ["The capital of France is", "In 1492, Columbus"]:
        ids = tok.encode(prompt)
        r = greedy_decode(predict, ids, tok, max_new=8, state_hash=base.checksum)
        cur = ids.copy()
        for t in range(r.steps):  # reference: full recompute each step, no cache
            nxt = int(np.argmax(ref.forward(params, cur)[-1]))
            assert nxt == int(r.new_ids[t]), (prompt, t)
            cur = np.append(cur, np.int32(nxt))
    assert calls["n"] >= 2  # one predict per generated token, none cached
    nll = teacher_forced_nll(lambda ids: base.forward(ids, phase="query").logits, tok.encode("The capital of France is"),
                             tok.encode(" Paris\n"))
    assert nll["status"] == "ok" and nll["value"] > 0


@pytest.mark.gpu
def test_bp_decode_vs_hf_oracle(tok):
    if not ORACLE.exists():
        pytest.skip("REF-01 oracle absent (recorded as pending in docs/tasks/S0-09.md)")
    z = json.loads(ORACLE.read_text())
    base = BPBase()
    for case in z["cases"][:8]:
        r = greedy_decode(lambda ids: base.forward(ids, phase="query").logits, np.asarray(case["prompt_ids"], np.int32),
                          tok, max_new=32)
        assert list(r.new_ids) == list(case["generated_ids_no_cache"])[: len(r.new_ids)]


def test_score_generation_uses_aliases(tok):
    from pccap.data.decode import DecodeResult

    ok = DecodeResult(np.array([1]), " Paris", "newline", False, 1)
    assert score_generation(ok, ["paris", "Paris "])["value"] == 1.0
    bad = DecodeResult(np.array([1]), " Paris, France", "newline", False, 1)
    assert score_generation(bad, ["Paris"])["value"] == 0.0
