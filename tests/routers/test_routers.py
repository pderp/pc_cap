"""CAP-05: Last/Full/Supplied schedules; a real-cap probe changes no learner state and is charged."""

import numpy as np
import pytest

from pccap.contracts import DirectionResult, RoundContext, SiteId
from pccap.routers import Full, Last, Supplied, make_router


def dirs(ok=(1, 2, 3)):
    return {m: DirectionResult(SiteId(m, 0, 0), np.ones(3, np.float32), "ok", 1.0) if m in ok
            else DirectionResult(SiteId(m, 0, 0), None, "no_direction", 0.0) for m in (1, 2, 3)}


def ctx(d, permitted=None):
    return RoundContext(prefix_ids=np.array([1], np.int32), loss=1.0, directions=d, bank_scales={1: 1, 2: 1, 3: 1},
                        rng_material=(0, b"a" * 16, 0, 0), permitted_banks=permitted)


def test_last_full_supplied():
    assert Last().schedule(ctx(dirs())).banks == [3]
    assert Full().schedule(ctx(dirs())).banks == [1, 2, 3]
    assert Full().schedule(ctx(dirs(ok=(2,)))).banks == [2]
    assert Supplied().schedule(ctx(dirs(), permitted=(3, 1))).banks == [1, 3]
    with pytest.raises(ValueError):
        Supplied().schedule(ctx(dirs()))
    assert make_router("C0").name == "C0"


@pytest.mark.gpu
def test_real_cap_probe_is_read_only_and_charged():
    from pccap.bases import gpt2_jax as g
    from pccap.bases.bp import BPBase
    from pccap.cap.cap import Cap, CapConfig
    from pccap.harness.ledger import Ledger
    from pccap.routers import Measured
    from pccap.transport.transport import Transport

    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    ledger = Ledger()
    base = BPBase(ledger=ledger)
    cap = Cap(base, CapConfig(arm="C2", radii={1: 0.5, 2: 0.5, 3: 0.5}, bank_scales={1: 60.0, 2: 100.0, 3: 480.0}))
    tok = g.load_tokenizer()
    ids = np.asarray(tok.encode("The capital of France is").ids, np.int32)
    p = len(ids) - 1
    ep0 = cap.edited_forward(ids)
    # plant a slot in bank 1 that fires on this prompt, so the probe's downstream recompute uses live retrieval
    cap.banks[1].bank.allocate(ep0.keys[1], radius=0.5, value=np.full(base.d, 0.5, np.float32))
    ep = cap.edited_forward(ids)
    assert ep.fired[1] >= 0 and ep.fired[2] < 0
    target = int(np.argsort(ep.logits)[-2])  # ep.logits is the last row [V]
    L = cap.loss_of(ep, target)
    grads = base.adjoint(ids, target, [])
    tr = Transport()
    d = {m: tr.direction(np.asarray(grads[SiteId(m, g.BANK_BLOCK[m], p)]), SiteId(m, g.BANK_BLOCK[m], p)) for m in (1, 2, 3)}
    before = cap.state_hash()
    probes_before = ledger.learning.partial_forwards

    def probe(m, v):
        return cap.loss_of(cap.edited_forward(ids, extra={m: v}), target)

    r = Measured(probe).schedule(RoundContext(prefix_ids=ids, loss=L, directions=d, bank_scales=cap.cfg.bank_scales,
                                              rng_material=(0, b"x" * 16, 0, 0)))
    assert cap.state_hash() == before
    assert r.cost.router_probes == 3 and ledger.learning.partial_forwards > probes_before
    assert set(r.scores) == {1, 2, 3}
