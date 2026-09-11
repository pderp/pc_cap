"""Vmapped GRACE queries shared by the canonical learner and development controls.

The query kernel reuses the unchanged GRACE lookup and suffix. Updating, eviction,
snapshots, RNG state and memory accounting remain inherited from GraceLearner.
Batched arithmetic does not establish the DEC-020 sensitivity gate.
"""
from __future__ import annotations

import functools

import jax
import jax.numpy as jnp
import numpy as np

from pccap.baselines.grace_jax import GraceLearner, predict_kernel


@functools.partial(jax.jit, static_argnames=("cfg", "block"))
def predict_batch_kernel(params, ids, lengths, positions, keys, values, radii, cfg, block):
    def one(tokens, n, pos):
        return predict_kernel(params, tokens, n, pos, keys, values, radii, cfg, block, True)

    return jax.vmap(one)(ids, lengths, positions)


def last_logits_batch(learner, seqs, phase="query", key_positions=None):
    """Batch by the scalar path's padding width, restoring the input row order.

    During autoregressive generation or answer NLL, pass each ORIGINAL prompt's
    last index in key_positions for all its continuations. No codebook metadata,
    learner RNG, or learner-persistent cache is mutated by this function.
    """
    seqs = list(seqs)
    if key_positions is not None:
        key_positions = list(key_positions)
        if len(key_positions) != len(seqs):
            raise ValueError("key position batch size differs")
    groups = {}
    for i, seq in enumerate(seqs):
        ids = learner._ids(seq)
        padded, n = learner._padded(ids)
        pos = n-1 if key_positions is None else key_positions[i]
        if isinstance(pos, (bool, np.bool_)) or not isinstance(pos, (int, np.integer)) or not 0 <= pos < n:
            raise ValueError("invalid GRACE key position")
        groups.setdefault(len(padded), []).append((i, padded, n, int(pos)))
    if not seqs:
        return np.empty((0, learner.base.vocab), np.float32)
    output = np.empty((len(seqs), learner.base.vocab), np.float32)
    keys, values, radii = (jnp.asarray(x) for x in (learner.keys, learner.values, learner.radii))
    for members in groups.values():
        ids = jnp.asarray(np.stack([r[1] for r in members]))
        lengths = jnp.asarray([r[2] for r in members], jnp.int32)
        positions = jnp.asarray([r[3] for r in members], jnp.int32)
        with learner.ledger.call(phase, full_forwards=len(members), tokens=sum(r[2] for r in members)) as record:
            logits = predict_batch_kernel(learner.base.params, ids, lengths, positions, keys, values, radii, learner.base.cfg, learner.block)
            record.outputs = logits
        output[[r[0] for r in members]] = np.asarray(logits)
    return output


class BatchedGraceLearner(GraceLearner):
    """Explicit batched subclass for development comparisons and compatibility."""

    def last_logits_batch(self, seqs, phase="query", key_positions=None):
        return last_logits_batch(self, seqs, phase, key_positions)
