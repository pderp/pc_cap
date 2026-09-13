"""A tiny random GPT-2-shaped base (12 blocks so the bank sites exist; d = 16; vocab 64) with the pccap base surface
(forward, forward_from, adjoint, loss, checksum) for CPU tests of the revision learner."""

from __future__ import annotations

import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.contracts import CostRecord, ForwardResult, SiteId

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
    def __init__(self, params=None):
        self.params, self.cfg, self.d = (tiny_params() if params is None else params), CFG, CFG.d
        self.calls = {"forward": 0, "forward_from": 0, "adjoint": 0}

    def checksum(self, recompute: bool = True):
        return "tiny"

    def _prep(self, ids, writes):
        ids = np.asarray(ids, np.int32).reshape(-1)
        n = len(ids)
        T = g.bucket_len(n)
        W = np.zeros((3, self.d), np.float32)
        for wr in writes:
            W[wr.site.bank - 1] += np.asarray(wr.vector, np.float32)
        return jnp.asarray(g.pad_ids(ids, T, 0)), jnp.int32(n), jnp.asarray(W), n, n - 1

    def forward(self, ids, writes=(), retain_sites=True, phase="query", last_only=True):
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        self.calls["forward"] += 1
        logits, rows, full = g.forward_jit(self.params, ids_d, n_d, W, self.cfg, retain_sites, last_only)
        return ForwardResult(logits=logits if last_only else logits[:n], sites={SiteId(m, g.BANK_BLOCK[m], p): rows[m] for m in rows},
                             cost=CostRecord(phase=phase, full_forwards=1, tokens=n), hidden={m: full[m] for m in full})

    def forward_from(self, bank, hidden, ids, writes=(), phase="query", retain_sites=False, last_only=True):
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        self.calls["forward_from"] += 1
        logits, rows, full = g.forward_from_jit(self.params, jnp.asarray(hidden), n_d, W, self.cfg, bank, retain_sites, last_only)
        return ForwardResult(logits=logits if last_only else logits[:n], sites={}, cost=CostRecord(phase=phase, partial_forwards=1, tokens=n), hidden={m: full[m] for m in full})

    def adjoint(self, ids, target, writes=(), phase="learning", return_loss=False):
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        self.calls["adjoint"] += 1
        loss, grad, logits, rows = g.adjoint_jit(self.params, ids_d, n_d, W, jnp.int32(target), self.cfg)
        out = {SiteId(m, g.BANK_BLOCK[m], p): grad[m - 1] for m in (1, 2, 3)}
        return (out, float(loss), logits[:n]) if return_loss else out

    def loss(self, ids, target, writes=(), phase="query"):
        fr = self.forward(ids, writes, phase=phase, last_only=True)
        row = np.asarray(fr.logits, np.float64)
        m = row.max()
        return float(m + np.log(np.exp(row - m).sum()) - row[int(target)]), fr
