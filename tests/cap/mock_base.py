"""A tiny CPU base with the Base contract (sites at three banks, writes at p, forward_from,
adjoint by autodiff, checksum) for fast learning-loop tests. Nonlinear between sites."""

from __future__ import annotations

import hashlib

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases.gpt2_jax import BANK_BLOCK
from pccap.contracts import ForwardResult, SiteId
from pccap.harness.ledger import Ledger


class MockBase:
    name = "MOCK"

    def __init__(self, d=8, vocab=32, seed=0, ledger=None):
        rng = np.random.default_rng(seed)
        self.D, self.d, self.vocab = 12, d, vocab
        self.E = rng.standard_normal((vocab, d)).astype(np.float32)
        self.A1 = (rng.standard_normal((d, d)) / np.sqrt(d)).astype(np.float32)
        self.A2 = (rng.standard_normal((d, d)) / np.sqrt(d)).astype(np.float32)
        self.Vout = (rng.standard_normal((d, vocab)) * 1.5).astype(np.float32)
        self.sites = [SiteId(m, BANK_BLOCK[m], -1) for m in (1, 2, 3)]
        self.ledger = ledger or Ledger()
        self._grad = jax.jit(jax.grad(self._loss_w))

    # ---------------------------------------------------------------- core math (numpy)
    def _stages(self, H0, p, W, start=1):
        """Return (logits, rows, full) applying writes W[m-1] at p from bank `start`."""
        rows, full = {}, {}
        r = H0
        if start <= 1:
            rows[1], full[1] = r[p].copy(), r.copy()
            r = r.copy()
            r[p] = r[p] + W[0]
        if start <= 2:
            if start == 2:
                r = H0.copy()
                rows[2], full[2] = r[p].copy(), r.copy()
                r[p] = r[p] + W[1]
            else:
                r = np.tanh(r @ self.A1) + r
                rows[2], full[2] = r[p].copy(), r.copy()
                r[p] = r[p] + W[1]
        if start <= 3:
            if start == 3:
                r = H0.copy()
                rows[3], full[3] = r[p].copy(), r.copy()
                r[p] = r[p] + W[2]
            else:
                r = np.tanh(r @ self.A2) + r
                rows[3], full[3] = r[p].copy(), r.copy()
                r[p] = r[p] + W[2]
        logits = np.tanh(r) @ self.Vout
        return logits.astype(np.float32), rows, full

    def _W(self, ids, writes):
        ids = np.asarray(ids, np.int32).reshape(-1)
        p = len(ids) - 1
        W = np.zeros((3, self.d), np.float32)
        for w in writes:
            if w.site.position not in (p, -1):
                raise ValueError("writes only at p")
            W[w.site.bank - 1] += np.asarray(w.vector, np.float32)
        return ids, p, W

    def forward(self, ids, writes=(), retain_sites=False, phase="learning"):
        ids, p, W = self._W(ids, writes)
        with self.ledger.call(phase, full_forwards=1, tokens=len(ids)) as rec:
            logits, rows, full = self._stages(self.E[ids], p, W, 1)
        sites = {SiteId(m, BANK_BLOCK[m], p): rows[m] for m in rows}
        return ForwardResult(logits=logits, sites=sites, cost=rec, hidden=full if retain_sites else {})

    def forward_from(self, bank, hidden, ids, writes=(), phase="learning", retain_sites=False):
        ids, p, W = self._W(ids, writes)
        with self.ledger.call(phase, partial_forwards=1, tokens=len(ids)) as rec:
            logits, rows, full = self._stages(np.asarray(hidden, np.float32), p, W, bank)
        sites = {SiteId(m, BANK_BLOCK[m], p): rows[m] for m in rows}
        return ForwardResult(logits=logits, sites=sites, cost=rec, hidden=full if retain_sites else {})

    # ---------------------------------------------------------------- adjoint (jax)
    def _loss_w(self, W, H0, p, target):
        r = H0
        r = r.at[p].add(W[0])
        r = jnp.tanh(r @ self.A1) + r
        r = r.at[p].add(W[1])
        r = jnp.tanh(r @ self.A2) + r
        r = r.at[p].add(W[2])
        logits = jnp.tanh(r) @ self.Vout
        row = logits[p]
        return jax.nn.logsumexp(row) - row[target]

    def adjoint(self, ids, target, writes=(), phase="learning", return_loss=False):
        ids, p, W = self._W(ids, writes)
        with self.ledger.call(phase, full_forwards=1, reverses=1, tokens=len(ids)):
            gW = np.asarray(self._grad(jnp.asarray(W), jnp.asarray(self.E[ids]), p, int(target)))
        out = {SiteId(m, BANK_BLOCK[m], p): gW[m - 1] for m in (1, 2, 3)}
        if return_loss:
            L = float(self._loss_w(jnp.asarray(W), jnp.asarray(self.E[ids]), p, int(target)))
            return out, L, None
        return out

    def checksum(self, recompute=True):
        h = hashlib.sha256()
        for a in (self.E, self.A1, self.A2, self.Vout):
            h.update(a.tobytes())
        return h.hexdigest()


def make_cap(arm="C1", radii=0.5, seed=0, d=8, vocab=32, A_scales=None):
    from pccap.cap.cap import Cap, CapConfig

    base = MockBase(d=d, vocab=vocab, seed=seed)
    cfg = CapConfig(arm=arm, radii={1: radii, 2: radii, 3: radii}, bank_scales=A_scales or {1: 2.0, 2: 3.0, 3: 4.0},
                    seed=seed, d=d)
    return base, Cap(base, cfg)


def make_item(item_id="it", prompt=(1, 2, 3), answer=(5, 6), version=1):
    from pccap.contracts import EditItem

    return EditItem(item_id=item_id, digest=hashlib.sha256(item_id.encode()).digest()[:16], prompt="p", answer="a",
                    aliases=["a"], paraphrases=[], locality_prompts=[], prompt_ids=np.asarray(prompt, np.int32),
                    answer_ids=np.asarray(answer, np.int32), version=version)
