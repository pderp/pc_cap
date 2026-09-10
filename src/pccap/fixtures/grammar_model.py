"""GRAM-02: the six-layer grammar transformer and its ``Base`` wrapper (plan §6.5 GRAM-02; PDF E.1).

Replacement fixture — no continuity with R8/R9 (PA-2). Pre-norm transformer with GPT-2 block
conventions (``pccap.bases.gpt2_jax.block/embed/head`` unchanged: d = 128, 4 heads, 6 blocks, vocab 64,
length 64, tied head). Bank sites ``round(m·6/3) = 2, 4, 6`` → block outputs 1, 3, 5 (the last before
the final norm): ``bank_blocks = {1: 1, 2: 3, 3: 5}``. ``GrammarBase`` mirrors ``BPBase``'s API
(``forward``, ``forward_from``, ``adjoint``, ``loss``, ``last_logits_batch``, ``forward_batch``,
``forward_from_batch``, ``checksum``) with its own kernels so the GPT-2 module is untouched; the cap
reads ``base.bank_blocks`` and ``base.d`` (R2-09). Training (``train_base``) uses AdamW on the base
grammar with next-token cross-entropy at every content position and reports held-out accuracy at the
designated positions; the weights go to ``assets/models/grammar/grammar_base.npz``.
"""

from __future__ import annotations

import functools
import hashlib
import json
import time
from pathlib import Path
from typing import Sequence

import jax
import jax.numpy as jnp
import numpy as np
from jax import lax

from pccap import ASSETS_ROOT
from pccap.bases import gpt2_jax as g
from pccap.contracts import ForwardResult, SiteId, Write
from pccap.harness.ledger import Ledger

CFG = g.GPT2Config(n_layer=6, n_head=4, d=128, vocab=64, n_pos=64, eps=1e-5)
BANK_BLOCKS = {1: 1, 2: 3, 3: 5}
BLOCK_BANK = {v: k for k, v in BANK_BLOCKS.items()}
WEIGHTS = Path(ASSETS_ROOT) / "models" / "grammar" / "grammar_base.npz"


def init_params(seed: int = 0, cfg: g.GPT2Config = CFG) -> dict:
    rng = np.random.default_rng(seed)
    d = cfg.d

    def n(*shape, s=0.02):
        return (s * rng.standard_normal(shape)).astype(np.float32)

    blocks = [{"ln_1": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)},
               "c_attn": {"w": n(d, 3 * d), "b": np.zeros(3 * d, np.float32)},
               "c_proj": {"w": n(d, d, s=0.02 / np.sqrt(2 * cfg.n_layer)), "b": np.zeros(d, np.float32)},
               "ln_2": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)},
               "c_fc": {"w": n(d, 4 * d), "b": np.zeros(4 * d, np.float32)},
               "c_proj2": {"w": n(4 * d, d, s=0.02 / np.sqrt(2 * cfg.n_layer)), "b": np.zeros(d, np.float32)}} for _ in range(cfg.n_layer)]
    return {"wte": n(cfg.vocab, d), "wpe": n(cfg.n_pos, d, s=0.01), "ln_f": {"g": np.ones(d, np.float32), "b": np.zeros(d, np.float32)}, "blocks": blocks}


# ----------------------------------------------------------------------------- kernels (sites at 1/3/5)
def run_blocks(params, h, p, writes, cfg, start_block):
    rows, full = {}, {}
    for l in range(start_block, cfg.n_layer):
        h = g.block(params["blocks"][l], h, cfg)
        m = BLOCK_BANK.get(l)
        if m is not None:
            row = lax.dynamic_index_in_dim(h, p, axis=0, keepdims=False)
            rows[m], full[m] = row, h
            h = lax.dynamic_update_index_in_dim(h, row + writes[m - 1], p, axis=0)
    return h, rows, full


def _head_rows(params, h, p, cfg, last_only):
    if last_only:
        row = lax.dynamic_index_in_dim(h, p, axis=0, keepdims=False)
        return g.layer_norm(row, params["ln_f"]["g"], params["ln_f"]["b"], cfg.eps) @ params["wte"].T
    return g.head(params, h, cfg)


@functools.partial(jax.jit, static_argnames=("cfg", "retain", "last_only"))
def forward_jit(params, ids, n, writes, cfg, retain, last_only=False):
    p = n - 1
    h, rows, full = run_blocks(params, g.embed(params, ids), p, writes, cfg, 0)
    return _head_rows(params, h, p, cfg, last_only), rows, (full if retain else {})


@functools.partial(jax.jit, static_argnames=("cfg", "bank", "retain", "last_only"))
def forward_from_jit(params, hidden, n, writes, cfg, bank, retain=False, last_only=False):
    p = n - 1
    row = lax.dynamic_index_in_dim(hidden, p, axis=0, keepdims=False)
    h = lax.dynamic_update_index_in_dim(hidden, row + writes[bank - 1], p, axis=0)
    h, rows, full = run_blocks(params, h, p, writes, cfg, BANK_BLOCKS[bank] + 1)
    rows[bank], full[bank] = row, hidden
    return _head_rows(params, h, p, cfg, last_only), rows, (full if retain else {})


@functools.partial(jax.jit, static_argnames=("cfg",))
def adjoint_jit(params, ids, n, writes, target, cfg):
    p = n - 1

    def loss_fn(w):
        h, rows, _ = run_blocks(params, g.embed(params, ids), p, w, cfg, 0)
        logits = g.head(params, h, cfg)
        return g.loss_at(logits, p, target), (logits, rows)

    (loss, (logits, rows)), grad = jax.value_and_grad(loss_fn, has_aux=True)(writes)
    return loss, grad, logits, rows


@functools.partial(jax.jit, static_argnames=("cfg",))
def forward_batch_jit(params, ids, n, writes, cfg):
    def one(i, k, w):
        p = k - 1
        h, rows, full = run_blocks(params, g.embed(params, i), p, w, cfg, 0)
        return _head_rows(params, h, p, cfg, True), jnp.stack([rows[1], rows[2], rows[3]]), jnp.stack([full[1], full[2], full[3]])

    return jax.vmap(one)(ids, n, writes)


@functools.partial(jax.jit, static_argnames=("cfg", "bank"))
def forward_from_batch_jit(params, hidden, n, writes, cfg, bank):
    def one(hid, k, w):
        p = k - 1
        row = lax.dynamic_index_in_dim(hid, p, axis=0, keepdims=False)
        h = lax.dynamic_update_index_in_dim(hid, row + w[bank - 1], p, axis=0)
        h, rows, full = run_blocks(params, h, p, w, cfg, BANK_BLOCKS[bank] + 1)
        later = [m for m in (1, 2, 3) if m > bank]
        rows_s = jnp.stack([rows[m] for m in later]) if later else jnp.zeros((0, cfg.d), jnp.float32)
        full_s = jnp.stack([full[m] for m in later]) if later else jnp.zeros((0, hid.shape[0], cfg.d), jnp.float32)
        return _head_rows(params, h, p, cfg, True), rows_s, full_s

    return jax.vmap(one)(hidden, n, writes)


@functools.partial(jax.jit, static_argnames=("cfg",))
def last_logits_batch_jit(params, ids, n, cfg):
    def one(i, k):
        p = k - 1
        h, _, _ = run_blocks(params, g.embed(params, i), p, jnp.zeros((3, cfg.d), jnp.float32), cfg, 0)
        return _head_rows(params, h, p, cfg, True)

    return jax.vmap(one)(ids, n)


def _digest(params_np: dict) -> str:
    h = hashlib.sha256()
    for k, v in g.flatten_named(params_np):
        h.update(k.encode())
        h.update(np.ascontiguousarray(v).tobytes())
    return h.hexdigest()


class GrammarBase:
    """Frozen grammar transformer (BASE-GRAM); the same API surface as ``BPBase``."""

    name = "GRAM"
    bank_blocks = BANK_BLOCKS

    def __init__(self, params_np: dict | None = None, weights: Path | str | None = None, ledger: Ledger | None = None, seed: int = 0):
        if params_np is None:
            params_np = g.load_params_npz(weights) if weights else init_params(seed)
        self.cfg = CFG
        self.weights_label = str(weights) if weights else f"random-init(seed={seed})"
        self._checksum_at_load = _digest(params_np)
        self.params = g.to_device(params_np)
        self.D, self.d, self.vocab = self.cfg.n_layer, self.cfg.d, self.cfg.vocab
        self.sites = [SiteId(m, BANK_BLOCKS[m], -1) for m in (1, 2, 3)]
        self.ledger = ledger or Ledger()

    def _prep(self, ids, writes: Sequence[Write]):
        ids = np.asarray(ids, np.int32).reshape(-1)
        n = int(ids.shape[0])
        if n < 1 or n > self.cfg.n_pos:
            raise ValueError("prefix length outside 1..64")
        T = self.cfg.n_pos
        p = n - 1
        W = np.zeros((3, self.d), np.float32)
        for w in writes:
            if w.site.position not in (p, -1):
                raise ValueError("writes only at the last position")
            if BANK_BLOCKS[w.site.bank] != w.site.block:
                raise ValueError(f"site {w.site} inconsistent with the grammar bank blocks {BANK_BLOCKS}")
            W[w.site.bank - 1] += np.asarray(w.vector, np.float32)
        return jnp.asarray(g.pad_ids(ids, T, 0)), jnp.int32(n), jnp.asarray(W), n, p

    def _sites(self, rows, p):
        return {SiteId(m, BANK_BLOCKS[m], p): rows[m] for m in sorted(rows)}

    def forward(self, ids, writes=(), retain_sites=False, phase="learning", last_only=False) -> ForwardResult:
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        with self.ledger.call(phase, full_forwards=1, tokens=n) as rec:
            logits, rows, full = forward_jit(self.params, ids_d, n_d, W, self.cfg, retain_sites, last_only)
            rec.outputs = (logits, rows, full)
        return ForwardResult(logits=logits if last_only else logits[:n], sites=self._sites(rows, p), cost=rec, hidden={m: full[m] for m in full} if retain_sites else {})

    def forward_from(self, bank, hidden, ids, writes=(), phase="learning", retain_sites=False, last_only=False) -> ForwardResult:
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        hidden = jnp.asarray(hidden, jnp.float32)
        if hidden.shape[0] != self.cfg.n_pos:
            hidden = jnp.zeros((self.cfg.n_pos, self.d), jnp.float32).at[: hidden.shape[0]].set(hidden[: self.cfg.n_pos])
        with self.ledger.call(phase, partial_forwards=1, tokens=n) as rec:
            logits, rows, full = forward_from_jit(self.params, hidden, n_d, W, self.cfg, bank, retain_sites, last_only)
            rec.outputs = (logits, rows, full)
        return ForwardResult(logits=logits if last_only else logits[:n], sites=self._sites(rows, p), cost=rec, hidden={m: full[m] for m in full} if retain_sites else {})

    def adjoint(self, ids, target, writes=(), phase="learning", return_loss=False):
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        with self.ledger.call(phase, full_forwards=1, reverses=1, tokens=n) as rec:
            loss, grad, logits, rows = adjoint_jit(self.params, ids_d, n_d, W, jnp.int32(target), self.cfg)
            rec.outputs = (loss, grad, logits, rows)
        out = {SiteId(m, BANK_BLOCKS[m], p): grad[m - 1] for m in (1, 2, 3)}
        return (out, float(loss), logits[:n]) if return_loss else out

    def loss(self, ids, target, writes=(), phase="query"):
        fr = self.forward(ids, writes, phase=phase)
        row = fr.logits[len(np.asarray(ids).reshape(-1)) - 1]
        return float(jax.nn.logsumexp(row) - row[target]), fr

    def last_logits_batch(self, seqs, phase="query"):
        n = np.asarray([len(s) for s in seqs], np.int32)
        ids = np.stack([g.pad_ids(np.asarray(s, np.int32), self.cfg.n_pos, 0) for s in seqs])
        with self.ledger.call(phase, full_forwards=len(seqs), tokens=int(n.sum())) as rec:
            out = last_logits_batch_jit(self.params, jnp.asarray(ids), jnp.asarray(n), self.cfg)
            rec.outputs = out
        return np.asarray(out)

    def forward_batch(self, seqs, writes=None, phase="query"):
        n = np.asarray([len(s) for s in seqs], np.int32)
        ids = np.stack([g.pad_ids(np.asarray(s, np.int32), self.cfg.n_pos, 0) for s in seqs])
        W = np.zeros((len(seqs), 3, self.d), np.float32) if writes is None else np.asarray(writes, np.float32)
        with self.ledger.call(phase, full_forwards=len(seqs), tokens=int(n.sum())) as rec:
            out = forward_batch_jit(self.params, jnp.asarray(ids), jnp.asarray(n), jnp.asarray(W), self.cfg)
            rec.outputs = out
        return out[0], out[1], out[2], n

    def forward_from_batch(self, bank, hidden, n, writes, phase="query"):
        with self.ledger.call(phase, partial_forwards=int(len(n)), tokens=int(np.sum(n))) as rec:
            out = forward_from_batch_jit(self.params, hidden, jnp.asarray(n), jnp.asarray(np.asarray(writes, np.float32)), self.cfg, bank)
            rec.outputs = out
        return out

    def checksum(self, recompute=True):
        if not recompute:
            return self._checksum_at_load
        return _digest(jax.tree_util.tree_map(np.asarray, self.params))


# ----------------------------------------------------------------------------- training (GRAM-02)
def _batch_loss(params, ids, mask, cfg):
    def one(i, m):
        h, _, _ = run_blocks(params, g.embed(params, i), jnp.int32(0), jnp.zeros((3, cfg.d), jnp.float32), cfg, 0)
        logits = g.head(params, h, cfg)
        lp = jax.nn.log_softmax(logits[:-1], axis=-1)
        nll = -jnp.take_along_axis(lp, i[1:, None], axis=-1)[:, 0]
        return jnp.sum(nll * m[1:]) / jnp.maximum(jnp.sum(m[1:]), 1.0)

    return jnp.mean(jax.vmap(one)(ids, mask))


def train_base(out_path: Path = WEIGHTS, steps: int = 4000, batch: int = 64, lr: float = 3e-4, seed: int = 0, target_acc: float = 0.98,
               max_seconds: float = 1800.0, log_every: int = 100, eval_n: int = 512, quiet: bool = False) -> dict:
    """AdamW on the base grammar (all switches default) with next-token CE at every content position;
    stops at held-out designated-position accuracy ≥ ``target_acc`` (checked every ``log_every`` steps) or the
    time/step limit. Writes the npz, a training log and the competence figures."""
    import optax

    from pccap.fixtures.grammar_generator import CONTEXT_POSITIONS, CONTEXTS, Grammar, Switches

    gr = Grammar()
    params = jax.tree_util.tree_map(jnp.asarray, init_params(seed))
    opt = optax.adamw(lr, weight_decay=0.01)
    st = opt.init(params)
    mask = np.ones(64, np.float32)
    mask[list(CONTEXT_POSITIONS)] = 0.0  # context tokens are observable inputs, not predicted
    mask_b = jnp.asarray(np.tile(mask, (batch, 1)))

    @jax.jit
    def step(params, st, ids):
        loss, grads = jax.value_and_grad(_batch_loss)(params, ids, mask_b, CFG)
        upd, st = opt.update(grads, st, params)
        return optax.apply_updates(params, upd), st, loss

    def heldout():
        seqs, ps, tg = [], [], []
        for c in range(CONTEXTS):
            for i in range(eval_n // CONTEXTS):
                toks, p, _ = gr.sequence(c, Switches.base(), 200_000 + 2_500 * c + i)
                seqs.append(toks[:p])
                ps.append(p)
                tg.append(int(toks[p]))
        return seqs, np.asarray(tg)

    hs, ht = heldout()
    base = GrammarBase(params_np=jax.tree_util.tree_map(np.asarray, params))

    def acc(params):
        base.params = params
        lg = base.last_logits_batch(hs)
        return float(np.mean(lg.argmax(-1) == ht))

    rng = np.random.default_rng(seed)
    t0, log = time.time(), []
    it = 0
    result_acc = acc(params)
    for it in range(1, steps + 1):
        ids = np.stack([gr.sequence(int(rng.integers(CONTEXTS)), Switches.base(), int(rng.integers(0, 200_000)))[0] for _ in range(batch)])
        params, st, loss = step(params, st, jnp.asarray(ids, jnp.int32))
        if it % log_every == 0 or it == steps:
            result_acc = acc(params)
            log.append({"step": it, "loss": float(loss), "heldout_designated_acc": result_acc, "seconds": time.time() - t0})
            if not quiet:
                print(json.dumps(log[-1]), flush=True)
            if result_acc >= target_acc or time.time() - t0 > max_seconds:
                break
    params_np = jax.tree_util.tree_map(np.asarray, params)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sha = g.save_params_npz(params_np, out_path)
    rec = {"weights": str(out_path), "sha256": sha, "steps": it, "batch": batch, "lr": lr, "seed": seed, "heldout_designated_acc": result_acc,
           "target_acc": target_acc, "seconds": time.time() - t0, "log": log, "label": "replacement fixture, no continuity with R8/R9",
           "backend": jax.devices()[0].platform}
    out_path.with_suffix(".train.json").write_text(json.dumps(rec, indent=1))
    return rec


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--out", default=str(WEIGHTS))
    ap.add_argument("--max-seconds", type=float, default=1800.0)
    ap.add_argument("--no-lease", action="store_true", help="CPU training needs no lease")
    a = ap.parse_args(argv)
    if a.no_lease:
        rec = train_base(Path(a.out), steps=a.steps, max_seconds=a.max_seconds)
    else:
        from pccap.harness.lease import gpu_lease

        with gpu_lease("GRAM-02", stage="S3", projected_seconds=a.max_seconds):
            rec = train_base(Path(a.out), steps=a.steps, max_seconds=a.max_seconds)
    print(json.dumps({k: rec[k] for k in ("sha256", "steps", "heldout_designated_acc", "seconds", "backend")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
