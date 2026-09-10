"""PC-2 (PDF F.5): cap-off logits equal the base on 256 probes exactly; an oracle-false gate on
unrelated inputs reproduces the cap-disabled computation exactly."""

import json
from pathlib import Path

import numpy as np
import pytest

from pccap.bases import gpt2_jax as g

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"


def _probes(tok, n=256):
    sample = json.loads((ROOT / "manifests" / "dev" / "s0_sample.json").read_text())["items"]
    texts = [it["prompt"] for it in sample] + [p for it in sample for p in it["locality_prompts"][:3]]
    texts += [p for it in sample for p in it["paraphrases"][:2]]
    texts = list(dict.fromkeys(texts))[:n]
    return [np.asarray(tok.encode(t).ids, np.int32) for t in texts if t.strip()]


def test_pc2_cap_off_identity_and_oracle_false_gate():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig

    base = BPBase()
    tok = g.load_tokenizer()
    cap = Cap(base, CapConfig(arm="C1", radii={1: 0.0, 2: 0.0, 3: 0.0}))
    probes = _probes(tok)
    assert len(probes) >= 200
    worst = 0.0
    for ids in probes:
        a = np.asarray(base.forward(ids).logits)
        b = cap.predict(ids, full=True).logits
        worst = max(worst, float(np.abs(a - b).max()))
    # oracle-false gate: slots exist (exact-key radius 0) but never fire on unrelated inputs
    ep = cap.edited_forward(probes[0])
    for m in (1, 2, 3):
        cap.banks[m].bank.allocate(ep.keys[m], radius=0.0, value=np.full(base.d, 3.0, np.float32))
    gate_worst = 0.0
    fired = 0
    for ids in probes[1:]:
        e = cap.edited_forward(ids, phase="query", full=True)
        fired += any(v >= 0 for v in e.fired.values())
        gate_worst = max(gate_worst, float(np.abs(np.asarray(base.forward(ids).logits) - e.logits).max()))
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "pc2_identity.json").write_text(json.dumps({"control": "PC-2", "probes": len(probes), "max_abs_logit_diff_cap_off": worst,
                                                          "oracle_false_gate_max_abs_diff": gate_worst, "unrelated_fired": fired,
                                                          "pass": worst == 0.0 and gate_worst == 0.0 and fired == 0}, indent=1))
    assert worst == 0.0 and gate_worst == 0.0 and fired == 0
