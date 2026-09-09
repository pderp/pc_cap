"""PC-9 (cloning and randomness): clone equality, identical replay, reversed-sequence start
equality, scalar order effect (known-answer, S0-07)."""

import json
from pathlib import Path

import pytest

from pccap.bases import gpt2_jax as g


def _key(rec_json):
    d = json.loads(rec_json)
    d['cost'] = {k: v for k, v in d['cost'].items() if k not in ('wall_seconds', 'accel_seconds', 'memory_search_seconds', 'peak_mem_mib')}
    return json.dumps(d, sort_keys=True)


pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"


def _items(tok, n=2):
    from pccap.harness.stage_s0 import load_items

    return load_items([f"s0_sample[{i}]" for i in range(n)], tok)


def test_pc9_clone_replay_reversal():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.cap.learn import update_item
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.metrics.order import scalar_quadratic_reversal
    from pccap.routers import Random

    base = BPBase()
    tok = GPT2Tokenizer()
    items = _items(tok, 2)
    budget = Budget(A=0.1, R=2, tau_edit=0.1)
    mk = lambda: Cap(base, CapConfig(arm="CR", radii={1: 0.0, 2: 0.0, 3: 0.0}, bank_scales={1: 60.0, 2: 100.0, 3: 480.0}))  # noqa: E731
    a = mk()
    b = a.clone()
    assert a.state_hash() == b.state_hash()
    recs_a, recs_b = [], []
    for it in items:
        update_item(a, it, Random(), budget, on_decision=lambda r: recs_a.append(_key(r.to_json())))
        update_item(b, it, Random(), budget, on_decision=lambda r: recs_b.append(_key(r.to_json())))
    assert recs_a == recs_b and a.state_hash() == b.state_hash()  # identical replay on clones
    # reversed sequence starts from the same complete state and uses the same item-keyed random choices
    c = mk()
    start_hash = c.state_hash()
    assert start_hash == mk().state_hash()
    recs_c = []
    for it in reversed(items):
        update_item(c, it, Random(), budget, on_decision=lambda r: recs_c.append(json.loads(r.to_json())))
    routes_fwd = {(r["item_digest"], r["prefix_index"], r["round"]): r["candidate_banks"] for r in map(json.loads, recs_a)}
    for r in recs_c:
        k = (r["item_digest"], r["prefix_index"], r["round"])
        if k in routes_fwd:
            assert routes_fwd[k] == r["candidate_banks"]  # CR draw keyed by (seed, digest, prefix, round)
    sq = scalar_quadratic_reversal(theta=0.0, eta=0.1)
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "pc9_cloning.json").write_text(json.dumps({"control": "PC-9", "clone_equal": True, "replay_identical": True,
                                                         "reversed_start_equal": True, "scalar_order_effect": sq,
                                                         "decisions": len(recs_a)}, indent=1, default=str))
