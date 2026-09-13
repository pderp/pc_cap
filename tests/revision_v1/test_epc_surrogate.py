"""Gate 5 (ePC part) on the tiny CPU base: with write gradients supplied by the exact adjoint, the surrogate's θ-gradient
equals the reference's for the base-dependent terms (stop-gradient boundary at the writes; nothing reaches the base), and
the surrogate never differentiates the base parameters."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax  # noqa: E402
import numpy as np  # noqa: E402

from pccap.contracts import SiteId, Write  # noqa: E402
from pccap.revision_v1.controller import ControllerConfig, init_controller  # noqa: E402
from pccap.revision_v1.epc_train import EPCTrainer, episode_grads_epc  # noqa: E402
from pccap.revision_v1.episodes import synthetic_episode  # noqa: E402
from pccap.revision_v1.observations import ObservationEncoder  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig, init_reader  # noqa: E402
from pccap.revision_v1.train import ANSWER_ROLES, LossConfig, episode_grads, featurize  # noqa: E402
from tests.revision_v1.tiny_base import CFG, TinyBase  # noqa: E402

RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


class AdjointWriteGrads:
    """Stand-in estimator: exact dL/dW from the tiny base's adjoint (answer roles) — isolates the θ-side plumbing."""

    def __init__(self, base):
        self.base = base
        self.calls = 0

    def __call__(self, ids, target, W, role):
        self.calls += 1
        p = len(ids) - 1
        wl = [Write(SiteId(m, self.base.cfg and __import__("pccap.bases.gpt2_jax", fromlist=["BANK_BLOCK"]).BANK_BLOCK[m], p), W[m - 1]) for m in (1, 2, 3)]
        if role in ANSWER_ROLES:
            grads, loss, _ = self.base.adjoint(ids, int(target), wl, return_loss=True)
            return np.stack([np.asarray(grads[s]) for s in sorted(grads, key=lambda s: s.bank)]), float(loss), {"r_k": 0.0}
        return np.zeros_like(W), 0.0, {"r_k": 0.0}


def _setup():
    base = TinyBase()
    enc = ObservationEncoder(base, taps=RC.taps)
    feats = featurize(base, enc, synthetic_episode(4), RC)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = {"reader": init_reader(k1, RC), "controller": init_controller(k2, CC)}
    return base, feats, theta


def test_surrogate_matches_reference_when_write_grads_are_exact():
    base, feats, theta = _setup()
    lc = LossConfig(w_preserve=0.0)  # the stand-in returns no preserve gradient; compare the answer + retrieval terms
    ref, _ = episode_grads(theta, RC, CC, base.params, base.cfg, feats, lc)
    est = AdjointWriteGrads(base)
    sur, m = episode_grads_epc(theta, RC, CC, feats, lc, est)
    for a, b in zip(jax.tree_util.tree_leaves(ref), jax.tree_util.tree_leaves(sur)):
        assert np.allclose(np.asarray(a), np.asarray(b), atol=1e-4, rtol=1e-3)
    assert est.calls == sum(len(q.prefixes) for q in feats.queries)


def test_trainer_step_runs_and_base_untouched():
    base, feats, theta = _setup()
    before = jax.tree_util.tree_map(lambda x: np.array(x), base.params)
    tr = EPCTrainer(RC, CC, AdjointWriteGrads(base), LossConfig(w_preserve=0.0), lr=1e-3)
    st = tr.init(theta)
    theta2, st, m = tr.outer_step(theta, st, [feats])
    assert np.isfinite(m["grad_norm"]) and m["answer_n"] > 0
    for a, b in zip(jax.tree_util.tree_leaves(before), jax.tree_util.tree_leaves(base.params)):
        assert np.array_equal(a, np.asarray(b))
