"""PC-8 (read-only evaluation): learner hash unchanged after predict and decode with slots present."""

import json
from pathlib import Path

import numpy as np
import pytest

from pccap.bases import gpt2_jax as g

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"


def test_pc8_predict_and_decode_read_only():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.data.decode import greedy_decode
    from pccap.data.tokenize import GPT2Tokenizer

    base = BPBase()
    tok = GPT2Tokenizer()
    cap = Cap(base, CapConfig(arm="C1", radii={1: 0.4, 2: 0.4, 3: 0.4}))
    ids = tok.encode("The capital of France is")
    ep = cap.edited_forward(ids)
    for m in (1, 2, 3):
        cap.banks[m].bank.allocate(ep.keys[m], radius=0.4, value=np.full(base.d, 0.3, np.float32))
    h = cap.state_hash()
    cap.predict(ids)
    dec = greedy_decode(lambda x: cap.edited_forward(x, phase="query").logits, ids, tok, max_new=8, state_hash=cap.state_hash)
    assert cap.state_hash() == h
    assert cap.banks[1].bank.meta["use_count"].max() == 0  # evaluation never counts as use
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "pc8_readonly.json").write_text(json.dumps({"control": "PC-8", "hash_before": h, "hash_after": cap.state_hash(),
                                                          "decoded": dec.text, "pass": True}, indent=1))
