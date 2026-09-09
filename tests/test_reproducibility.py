"""Op. rule 9: two full replays of the same configuration give identical decisions and metrics
(1e-6 rel / 1e-8 abs)."""

import json
from pathlib import Path

import pytest

from pccap.bases import gpt2_jax as g


def _key(rec_json):
    d = json.loads(rec_json)
    d['cost'] = {k: v for k, v in d['cost'].items() if k not in ('wall_seconds', 'accel_seconds', 'memory_search_seconds', 'peak_mem_mib')}
    return json.dumps(d, sort_keys=True)


pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[1]


def test_two_replays_identical():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.cap.learn import update_item
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.stage_s0 import evaluate_item, load_items
    from pccap.routers import Full

    base = BPBase()
    tok = GPT2Tokenizer()
    items = load_items(["s0_sample[0]", "s0_sample[40]"], tok)
    outs = []
    for _ in range(2):
        cap = Cap(base, CapConfig(arm="C1", radii={1: 0.0, 2: 0.0, 3: 0.0}, bank_scales={1: 60.0, 2: 100.0, 3: 480.0}))
        recs: list = []
        metrics = []
        for it in items:
            update_item(cap, it, Full(), Budget(A=0.1, R=3), on_decision=lambda r, recs=recs: recs.append(_key(r.to_json())))
            ev = evaluate_item(cap, it, tok)
            metrics.append((ev["es"]["value"], ev["teacher_forced_nll"]["value"]))
        outs.append((recs, metrics, cap.state_hash()))
    assert outs[0][0] == outs[1][0]  # identical decisions
    for (e0, n0), (e1, n1) in zip(outs[0][1], outs[1][1]):
        assert e0 == e1 and abs(n0 - n1) <= 1e-8 + 1e-6 * abs(n0)
    assert outs[0][2] == outs[1][2]
    (ROOT / "results" / "S0" / "controls" / "reproducibility.json").write_text(
        json.dumps({"control": "reproducibility", "decisions": len(outs[0][0]), "identical": True,
                    "metrics": outs[0][1]}, indent=1, default=float))
