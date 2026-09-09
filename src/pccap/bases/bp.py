"""BP base wrapper (S0-04): frozen GPT-2 small implementing ``pccap.contracts.Base``.

* weights are immutable device arrays loaded once from the pinned snapshot;
* ``forward`` runs the explicit block loop with writes applied at the three bank sites
  (``pccap.bases.gpt2_jax.run_blocks``); sites in ``ForwardResult.sites`` are the *pre-write*
  residual rows at position ``p``; ``retain_sites=True`` also returns the full pre-write residual
  per site (``ForwardResult.hidden``) for ``forward_from``;
* ``forward_from(bank, hidden, ids, writes)`` resumes after ``bank``'s site (partial forward);
* ``adjoint`` returns ``dL/dh`` at every site from one reverse pass;
* ``checksum`` hashes every loaded tensor (there are no other persistent buffers: the causal
  mask is constructed, not stored);
* every call is charged to the ledger (full/partial forwards, reverses, wall and device time).

Sequences are padded to the bucket lengths in ``gpt2_jax.BUCKETS``; the same length always
maps to the same bucket so numerics are reproducible.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Sequence

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.contracts import CostRecord, ForwardResult, SiteId, Write
from pccap.harness.ledger import Ledger


def _digest(params_np: dict) -> str:
    h = hashlib.sha256()
    for name, arr in g.flatten_named(params_np):
        h.update(name.encode())
        h.update(np.ascontiguousarray(arr, dtype=np.float32).tobytes())
    return h.hexdigest()


class BPBase:
    """Frozen GPT-2 small (BASE-BP)."""

    name = "BP"

    def __init__(self, snapshot: Path | str = g.DEFAULT_SNAPSHOT, ledger: Ledger | None = None,
                 params_np: dict | None = None, cfg: g.GPT2Config | None = None):
        self.snapshot = Path(snapshot)
        self.cfg = cfg or g.GPT2Config.from_snapshot(self.snapshot)
        params_np = params_np if params_np is not None else g.load_params_numpy(self.snapshot, self.cfg)
        self._checksum_at_load = _digest(params_np)
        self.params = g.to_device(params_np)
        self.D = self.cfg.n_layer
        self.d = self.cfg.d
        self.vocab = self.cfg.vocab
        self.sites = [SiteId(m, g.BANK_BLOCK[m], -1) for m in (1, 2, 3)]
        self.ledger = ledger or Ledger()

    # -------------------------------------------------------------- helpers
    def _prep(self, ids, writes: Sequence[Write]):
        ids = np.asarray(ids, dtype=np.int32).reshape(-1)
        n = int(ids.shape[0])
        if n < 1:
            raise ValueError("empty prefix")
        T = g.bucket_len(n)
        p = n - 1
        W = np.zeros((3, self.d), dtype=np.float32)
        for w in writes:
            if w.site.position not in (p, -1):
                raise ValueError(f"write at position {w.site.position} != last position {p} (v0 writes only at p)")
            if g.BANK_BLOCK[w.site.bank] != w.site.block:
                raise ValueError(f"site {w.site} inconsistent with SD-7 bank blocks")
            W[w.site.bank - 1] += np.asarray(w.vector, dtype=np.float32)
        return jnp.asarray(g.pad_ids(ids, T)), jnp.int32(n), jnp.asarray(W), n, p

    def _sites(self, rows: dict, p: int) -> dict[SiteId, jax.Array]:
        return {SiteId(m, g.BANK_BLOCK[m], p): rows[m] for m in sorted(rows)}

    # -------------------------------------------------------------- contract
    def forward(self, ids, writes: Sequence[Write] = (), retain_sites: bool = False,
                phase: str = "learning") -> ForwardResult:
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        with self.ledger.call(phase, full_forwards=1, tokens=n) as rec:
            logits, rows, full = g.forward_jit(self.params, ids_d, n_d, W, self.cfg, retain_sites)
            rec.outputs = (logits, rows, full)
        hidden = {m: full[m][:n] for m in full} if retain_sites else {}
        return ForwardResult(logits=logits[:n], sites=self._sites(rows, p), cost=rec, hidden=hidden)

    def forward_from(self, bank: int, hidden, ids, writes: Sequence[Write] = (),
                     phase: str = "learning", retain_sites: bool = False) -> ForwardResult:
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        T = int(ids_d.shape[0])
        hidden = jnp.asarray(hidden, dtype=jnp.float32)
        if hidden.shape[0] != T:
            hpad = jnp.zeros((T, self.d), dtype=jnp.float32).at[: hidden.shape[0]].set(hidden[:T])
            hidden = hpad
        with self.ledger.call(phase, partial_forwards=1, tokens=n) as rec:
            logits, rows, full = g.forward_from_jit(self.params, hidden, n_d, W, self.cfg, bank, retain_sites)
            rec.outputs = (logits, rows, full)
        hid = {m: full[m][:n] for m in full} if retain_sites else {}
        return ForwardResult(logits=logits[:n], sites=self._sites(rows, p), cost=rec, hidden=hid)

    def adjoint(self, ids, target: int, writes: Sequence[Write] = (), phase: str = "learning",
                return_loss: bool = False):
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        with self.ledger.call(phase, full_forwards=1, reverses=1, tokens=n) as rec:
            loss, grad, logits, rows = g.adjoint_jit(self.params, ids_d, n_d, W, jnp.int32(target), self.cfg)
            rec.outputs = (loss, grad, logits, rows)
        out = {SiteId(m, g.BANK_BLOCK[m], p): grad[m - 1] for m in (1, 2, 3)}
        if return_loss:
            return out, float(loss), logits[:n]
        return out

    def loss(self, ids, target: int, writes: Sequence[Write] = (), phase: str = "query") -> tuple[float, ForwardResult]:
        fr = self.forward(ids, writes, phase=phase)
        p = len(np.asarray(ids).reshape(-1)) - 1
        row = fr.logits[p]
        return float(jax.nn.logsumexp(row) - row[target]), fr

    def checksum(self, recompute: bool = True) -> str:
        if not recompute:
            return self._checksum_at_load
        params_np = jax.tree_util.tree_map(np.asarray, self.params)
        return _digest(params_np)

    def cost_snapshot(self) -> CostRecord:
        t = CostRecord()
        t.add(self.ledger.query)
        t.add(self.ledger.learning)
        return t
