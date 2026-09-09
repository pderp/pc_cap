"""Cap core (S0-10 preview): cap-off identity is exact, predict is read-only, clone/serialize
round-trip, memory report within the ceiling."""

import numpy as np
import pytest

from pccap.bases import gpt2_jax as g

pytestmark = pytest.mark.gpu


@pytest.fixture(scope="module")
def setup():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig

    base = BPBase()
    cap = Cap(base, CapConfig(arm="C1", radii={1: 0.3, 2: 0.3, 3: 0.3}))
    tok = g.load_tokenizer()
    return base, cap, tok


def test_cap_off_identity_exact(setup):
    base, cap, tok = setup
    for s in ["The capital of France is", "Once upon a time"]:
        ids = np.asarray(tok.encode(s).ids, np.int32)
        a = np.asarray(base.forward(ids).logits)
        b = cap.predict(ids).logits
        assert np.array_equal(a, b)


def test_predict_read_only_and_clone(setup):
    base, cap, tok = setup
    ids = np.asarray(tok.encode("Water boils at").ids, np.int32)
    h = cap.state_hash()
    cap.predict(ids)
    assert cap.state_hash() == h
    ep = cap.edited_forward(ids)
    cap.banks[2].bank.allocate(ep.keys[2], radius=0.3, value=np.full(base.d, 0.25, np.float32))
    c = cap.clone()
    assert c.state_hash() == cap.state_hash()
    assert np.array_equal(c.predict(ids).logits, cap.predict(ids).logits)
    assert not np.array_equal(cap.predict(ids).logits, np.asarray(base.forward(ids).logits))  # the slot fires
    blob = cap.serialize()
    c2 = cap.clone()
    c2.banks[2].bank.values[:] = 0
    c2.restore(blob)
    assert c2.state_hash() == cap.state_hash()
    rep = cap.memory_bytes()
    assert rep.allocated_bytes <= rep.ceiling_bytes and rep.per_bank[2]["active"] == 1
