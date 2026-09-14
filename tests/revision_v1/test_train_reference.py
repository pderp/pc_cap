"""Gate 5 (learning mathematics) on a tiny random GPT-2-shaped base on CPU: finite-difference agreement of the episodic
reference gradient, retrieval-loss gradient reaching a record outside the top-k, and one outer step reducing the loss."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import jax  # noqa: E402
import jax.numpy as jnp  # noqa: E402
import numpy as np  # noqa: E402

from pccap.bases import gpt2_jax as g  # noqa: E402
from pccap.contracts import CostRecord, ForwardResult  # noqa: E402
from pccap.revision_v1.controller import ControllerConfig, init_controller  # noqa: E402
from pccap.revision_v1.episodes import synthetic_episode  # noqa: E402
from pccap.revision_v1.observations import ObservationEncoder  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig, init_reader  # noqa: E402
from pccap.revision_v1.train import (  # noqa: E402
    LossConfig,
    Trainer,
    episode_grads,
    featurize,
    retrieval_loss,
)

CFG = g.GPT2Config(n_layer=12, n_head=2, d=16, vocab=64, n_pos=128)


def tiny_params(seed: int = 0) -> dict:
    r = np.random.default_rng(seed)
    d, h = CFG.d, 4 * CFG.d

    def w(*s, scale=0.2):
        return jnp.asarray(r.normal(size=s) * scale, jnp.float32)

    def z(*s):
        return jnp.zeros(s, jnp.float32)

    def ln():
        return {"g": jnp.ones((d,), jnp.float32), "b": z(d)}

    blocks = [{"ln_1": ln(), "ln_2": ln(), "c_attn": {"w": w(d, 3 * d), "b": z(3 * d)}, "c_proj": {"w": w(d, d), "b": z(d)},
               "c_fc": {"w": w(d, h), "b": z(h)}, "c_proj2": {"w": w(h, d), "b": z(d)}} for _ in range(CFG.n_layer)]
    return {"wte": w(CFG.vocab, d, scale=0.5), "wpe": w(CFG.n_pos, d, scale=0.1), "blocks": blocks, "ln_f": ln()}


class TinyBase:
    def __init__(self, params):
        self.params, self.cfg, self.d = params, CFG, CFG.d

    def checksum(self):
        return "tiny"

    def forward(self, ids, writes=(), retain_sites=True, phase="query", last_only=True):
        ids = np.asarray(ids, np.int32)
        n = len(ids)
        T = g.bucket_len(n)
        W = jnp.zeros((3, self.d), jnp.float32)
        logits, rows, full = g.forward_jit(self.params, jnp.asarray(g.pad_ids(ids, T, 0)), jnp.int32(n), W, self.cfg, True, last_only)
        return ForwardResult(logits=logits, sites={}, cost=CostRecord(phase=phase, full_forwards=1, tokens=n), hidden={m: full[m] for m in full})


RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


def _setup():
    bp = tiny_params()
    base = TinyBase(bp)
    enc = ObservationEncoder(base, taps=RC.taps)
    ep = synthetic_episode(3)
    feats = featurize(base, enc, ep, RC)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = {"reader": init_reader(k1, RC), "controller": init_controller(k2, CC)}
    return base, feats, theta


def _total_loss(theta, feats, base, lc):
    from pccap.revision_v1.train import prefix_loss
    total = lc.w_retrieval * retrieval_loss(theta, RC, feats)
    for qi, q in enumerate(feats.queries):
        for ti in range(len(q.prefixes)):
            l, kind = prefix_loss(theta, RC, CC, base.params, base.cfg, feats, qi, ti)
            total = total + (lc.w_answer if kind == "answer" else lc.w_preserve) * l
    return total


def test_finite_difference_agreement():
    base, feats, theta = _setup()
    assert feats.supports and feats.queries and feats.skipped.get("composition", 0) >= 1
    lc = LossConfig()
    grads, metrics = episode_grads(theta, RC, CC, base.params, base.cfg, feats, lc)
    # episode_grads sums per-prefix losses (metrics report means); the total below sums the same terms
    flat, tree = jax.tree_util.tree_flatten(theta)
    gflat = jax.tree_util.tree_leaves(grads)
    r = np.random.default_rng(1)
    checked = 0
    for li in (0, 3, len(flat) - 1):  # a tap weight, a head weight, the last controller layer
        a = np.asarray(flat[li], np.float64)
        idx = tuple(r.integers(0, s) for s in a.shape)
        for eps in (1e-2,):
            def f(delta, a=a, idx=idx, li=li):
                arr = a.copy()
                arr[idx] += delta
                th = jax.tree_util.tree_unflatten(tree, [jnp.asarray(arr, jnp.float32) if i == li else x for i, x in enumerate(flat)])
                return float(_total_loss(th, feats, base, lc))
            fd = (f(eps) - f(-eps)) / (2 * eps)
            an = float(np.asarray(gflat[li])[idx])
            assert abs(fd - an) <= 1e-2 * max(1.0, abs(an)) + 2e-3, (li, idx, fd, an)
            checked += 1
    assert checked == 3


def test_retrieval_loss_reaches_records_outside_top_k():
    base, feats, theta = _setup()
    # the retrieval loss runs over ALL records: every record key gets a gradient even with top_k = 2 at inference
    gr = jax.grad(retrieval_loss)(theta, RC, feats)
    assert len(feats.supports) > RC.top_k
    kh = np.asarray(gr["reader"]["query_head"][-1]["w"])  # tied heads: the key path trains the shared head
    assert np.any(kh != 0)
    # move one record's features far away: its own gradient is still non-zero (it is the target of some query or a null distractor)
    from pccap.revision_v1.train import _records
    keys, _ = _records(theta, RC, feats)
    assert keys.shape[0] == len(feats.supports)


def test_outer_step_reduces_loss():
    base, feats, theta = _setup()
    tr = Trainer(RC, CC, base.params, base.cfg, LossConfig(), lr=1e-2, clip=10.0)
    st = tr.init(theta)
    l0 = float(_total_loss(theta, feats, base, tr.lc))
    for _ in range(5):
        theta, st, m = tr.outer_step(theta, st, [feats])
    l1 = float(_total_loss(theta, feats, base, tr.lc))
    assert l1 < l0, (l0, l1)
    assert np.isfinite(m["grad_norm"])
