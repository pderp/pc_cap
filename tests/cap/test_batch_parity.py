"""HARN-BATCH: batched cap-on evaluation matches the sequential reference decoder token for token
(E.2: an optimization may be reported only after parity with the sequential semantics)."""

import json
from pathlib import Path

import pytest

from pccap.bases import gpt2_jax as g

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]


def test_batched_cap_decode_parity():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.cap.learn import update_item
    from pccap.contracts import Budget
    from pccap.data.decode import greedy_decode, greedy_decode_batch_cap
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.stage_s2 import calibration, load_dev_items
    from pccap.routers import Full

    base = BPBase()
    tok = GPT2Tokenizer()
    report = {}
    for ds in ("zsre", "counterfact"):  # zsRE: positive radii; CounterFact: exact keys (SD-17/SD-18)
        b_m, radii = calibration(ds)
        cap = Cap(base, CapConfig(arm="C1", radii=radii, bank_scales=b_m))
        items, unrelated = load_dev_items(ds, 12, seed=5)
        for it in items[:8]:
            update_item(cap, it, Full(), Budget(A=0.3))
        prompts = [it.prompt_ids for it in items] + [tok.encode(p) for it in items[:6] for p in it.paraphrases] + [tok.encode(u) for u in unrelated[:10]]
        seq = [greedy_decode(lambda ids, cap=cap: cap.predict(ids).logits, p, tok) for p in prompts]
        bat = greedy_decode_batch_cap(cap, prompts, tok, batch_size=7)
        mism = [(i, list(s.new_ids), list(b.new_ids)) for i, (s, b) in enumerate(zip(seq, bat)) if list(s.new_ids) != list(b.new_ids)]
        learned_ok = sum(1 for s, it in zip(seq[:8], items[:8]) if s.text.strip().casefold() == it.answer.strip().casefold())
        report[ds] = {"prompts": len(prompts), "learned_items": 8, "learned_items_answered_sequential": learned_ok,
                      "mismatches": len(mism), "examples": mism[:3], "radii": radii}
    (ROOT / "results" / "S0" / "controls" / "harn_batch_parity.json").write_text(json.dumps(report, indent=1))
    assert all(r["mismatches"] == 0 for r in report.values()), report
    assert report["counterfact"]["learned_items_answered_sequential"] >= 6
