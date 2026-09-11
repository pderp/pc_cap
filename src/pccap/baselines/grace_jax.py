"""JAX GRACE implementation; source-reference parity and optional SD-8 eviction.

Canonical imports are exposed by grace_adapter; DEC-020 eligibility is a separate gate.
Algorithm: read-only GRACE f674183f, grace/editors/grace.py:57-204.
Frozen base parameters are never optimized. Query evaluation never mutates state.
"""
from __future__ import annotations

import functools
from dataclasses import asdict

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.contracts import CostRecord, ItemOutcome, MemoryReport
from pccap.harness.snapshot import LearnerState, SnapshotError, serialize


def cold_uniform(rng, size):
    """Reproduce torch 2.0 CPU float uniform from MT19937, without importing torch.

    ATen/core/MT19937RNGEngine.h:138-180 and TransformationHelper.h:82-87:
    uint32 MT output, low 24 bits times 2**-24 (not NumPy's float sampler).
    """
    return (rng.randint(0, 2**32, size, dtype=np.uint32) & np.uint32(0xFFFFFF)).astype(np.float32) * np.float32(2**-24)


@functools.partial(jax.jit, static_argnames=("cfg", "block"))
def hook_prefix(params, ids, cfg, block):
    h = g.embed(params, ids)
    for layer in range(block):
        h = g.block(params["blocks"][layer], h, cfg)
    p = params["blocks"][block]
    h = h + g.attention(p, g.layer_norm(h, p["ln_1"]["g"], p["ln_1"]["b"], cfg.eps), cfg)
    normalized = g.layer_norm(h, p["ln_2"]["g"], p["ln_2"]["b"], cfg.eps)
    projected = normalized @ p["c_fc"]["w"] + p["c_fc"]["b"]
    return h, normalized, projected


def hook_suffix(params, residual, projected, value, key_position, active, cfg, block):
    # Source replace_prompt excludes the key-position token itself.
    selected = (jnp.arange(residual.shape[0]) < key_position)[:, None] & active
    projected = jnp.where(selected, value[None, :], projected)
    p = params["blocks"][block]
    h = residual + g.gelu_new(projected) @ p["c_proj2"]["w"] + p["c_proj2"]["b"]
    for layer in range(block + 1, cfg.n_layer):
        h = g.block(params["blocks"][layer], h, cfg)
    return h


@functools.partial(jax.jit, static_argnames=("cfg", "block", "last_only"))
def predict_kernel(params, ids, n, key_position, keys, values, radii, cfg, block, last_only):
    h, normalized, projected = hook_prefix(params, ids, cfg, block)
    if keys.shape[0]:
        distances = jnp.sqrt(jnp.sum(jnp.square(keys - normalized[key_position]), axis=-1))
        nearest = jnp.argmin(distances)
        value, active = values[nearest], distances[nearest] <= radii[nearest]
    else:
        value, active = jnp.zeros((4 * cfg.d,), jnp.float32), jnp.bool_(False)
    h = hook_suffix(params, h, projected, value, key_position, active, cfg, block)
    if last_only:
        row = g.layer_norm(h[n - 1], params["ln_f"]["g"], params["ln_f"]["b"], cfg.eps)
        return row @ params["wte"].T
    return g.head(params, h, cfg)


@functools.partial(jax.jit, static_argnames=("cfg", "block", "steps"))
def optimize_value(params, h, projected, value, targets, mask, key_position, active, cfg, block, steps, lr):
    # Only the selected row can have a gradient. Reset Adam each edit, as source.
    def loss_fn(v):
        hidden = hook_suffix(params, h, projected, v, key_position, active, cfg, block)
        logits = g.head(params, hidden, cfg)
        losses = jax.nn.logsumexp(logits, axis=-1) - jnp.take_along_axis(logits, targets[:, None], axis=-1)[:, 0]
        return jnp.sum(losses * mask) / jnp.sum(mask)

    def body(carry, t):
        v, mean, variance = carry
        loss, grad = jax.value_and_grad(loss_fn)(v)
        # torch Adam's first moment uses lerp_; second moment mul_ then addcmul_.
        mean = mean + np.float32(0.1) * (grad - mean)
        variance = np.float32(0.999) * variance + np.float32(0.001) * grad * grad
        # Bias factors are generated in host double then rounded to fp32.
        c1 = jnp.asarray([1 - 0.9**i for i in range(1, steps + 1)], jnp.float32)[t]
        c2 = jnp.asarray([(1 - 0.999**i)**0.5 for i in range(1, steps + 1)], jnp.float32)[t]
        denominator = jnp.sqrt(variance) / c2 + np.float32(1e-8)
        v = v - (lr / c1) * mean / denominator
        return (v, mean, variance), loss

    (value, _, _), losses = jax.lax.scan(body, (value, jnp.zeros_like(value), jnp.zeros_like(value)), jnp.arange(steps))
    return value, losses


class GraceLearner:
    """Source-compatible unbounded reference; optional byte-bounded learning-use eviction."""
    name = "B4"

    def __init__(self, base, block=8, radius=1.0, value_steps=100, value_lr=1.0,
                 seed=0, ceiling_bytes=None, eviction="none"):
        if type(block) is not int or not 0 <= block < base.cfg.n_layer:
            raise ValueError("block outside the base")
        if not np.isfinite(radius) or radius < 0 or not np.isfinite(value_lr) or value_lr <= 0:
            raise ValueError("invalid radius or learning rate")
        if type(value_steps) is not int or value_steps < 1:
            raise ValueError("value_steps must be positive")
        if type(seed) is not int or not 0 <= seed < 2**64:
            raise ValueError("seed must be an unsigned 64-bit integer")
        if eviction not in ("none", "use_count_then_age"):
            raise ValueError("unsupported eviction policy")
        if ceiling_bytes is not None and (type(ceiling_bytes) is not int or ceiling_bytes < 1):
            raise ValueError("ceiling_bytes must be a positive integer or None")
        self.base, self.ledger = base, base.ledger
        self.block, self.radius, self.value_steps, self.value_lr = block, float(radius), value_steps, float(value_lr)
        self.seed, self.ceiling_bytes, self.eviction = seed, ceiling_bytes, eviction
        self.keys = np.empty((0, base.d), np.float32)
        self.values = np.empty((0, 4 * base.d), np.float32)
        self.radii = np.empty((0,), np.float32)
        self.labels = []
        self.use_counts = np.empty((0,), np.int64)
        self.ages = np.empty((0,), np.int64)
        self.rng = np.random.RandomState(seed & 0xFFFFFFFF)
        self.items_seen = self.evictions = self.allocations = 0
        self._base_hash = base.checksum()
        if ceiling_bytes is not None and self.memory_bytes().allocated_bytes > ceiling_bytes:
            raise ValueError("ceiling cannot hold empty learner metadata")

    def base_checksum(self):
        return self.base.checksum()

    def _ids(self, ids):
        a = np.asarray(ids)
        if a.ndim != 1 or not a.size or a.dtype.kind not in "iu" or np.any(a < 0) or np.any(a >= self.base.vocab):
            raise ValueError("expected nonempty valid token IDs")
        if len(a) > self.base.cfg.n_pos:
            raise ValueError("prefix exceeds context window")
        return a.astype(np.int32)

    def _padded(self, ids):
        n = len(ids)
        width = min(g.bucket_len(n), self.base.cfg.n_pos)
        return np.pad(ids, (0, width - n)), n

    def predict(self, ids, *, key_position=None, phase="query", last_only=False):
        ids = self._ids(ids)
        padded, n = self._padded(ids)
        pos = n - 1 if key_position is None else key_position
        if type(pos) is not int or not 0 <= pos < n:
            raise ValueError("invalid GRACE key position")
        with self.ledger.call(phase, full_forwards=1, tokens=n) as rec:
            out = predict_kernel(self.base.params, jnp.asarray(padded), jnp.int32(n), jnp.int32(pos),
                                 jnp.asarray(self.keys), jnp.asarray(self.values), jnp.asarray(self.radii),
                                 self.base.cfg, self.block, last_only)
            rec.outputs = out
        return np.asarray(out if last_only else out[:n])

    def last_logits_batch(self, seqs, phase="query", key_positions=None):
        from pccap.baselines.grace_batch import last_logits_batch

        return last_logits_batch(self, seqs, phase, key_positions)

    def _admit(self, query, label, new_value):
        nearest, distance = None, None
        if len(self.keys):
            distances = np.sqrt(np.sum(np.square(self.keys - query), axis=-1, dtype=np.float32))
            nearest = int(np.argmin(distances))
            distance = np.float32(distances[nearest])
        conflict = nearest is not None and np.mean(label, dtype=np.float32) != np.mean(self.labels[nearest], dtype=np.float32)
        far = nearest is None or distance > self.radius + self.radii[nearest]
        if far or conflict:
            self.keys = np.concatenate([self.keys, query[None, :]])
            self.values = np.concatenate([self.values, new_value[None, :]])
            self.radii = np.append(self.radii, np.float32(self.radius))
            self.labels.append(label.copy())
            self.use_counts = np.append(self.use_counts, np.int64(0))
            self.ages = np.append(self.ages, np.int64(self.allocations))
            self.allocations += 1
            if conflict and not far:
                self.radii[nearest] = distance / np.float32(2) - np.float32(1e-5)
                self.radii[-1] = distance / np.float32(2)
        elif distance > self.radii[nearest]:
            self.radii[nearest] = distance
        distances = np.sqrt(np.sum(np.square(self.keys - query), axis=-1, dtype=np.float32))
        idx = int(np.argmin(distances))
        return idx, bool(distances[idx] <= self.radii[idx])

    def _enforce_ceiling(self):
        if self.ceiling_bytes is None:
            return
        while self.memory_bytes().allocated_bytes > self.ceiling_bytes:
            if self.eviction == "none" or len(self.keys) == 0:
                raise MemoryError("GRACE state exceeds ceiling; eviction disabled or metadata too large")
            victim = int(np.lexsort((self.ages, self.use_counts))[0])
            self.keys = np.delete(self.keys, victim, axis=0)
            self.values = np.delete(self.values, victim, axis=0)
            self.radii = np.delete(self.radii, victim)
            self.use_counts = np.delete(self.use_counts, victim)
            self.ages = np.delete(self.ages, victim)
            self.labels.pop(victim)
            self.evictions += 1

    def update_item(self, item):
        prompt, answer = self._ids(item.prompt_ids), self._ids(item.answer_ids)
        ids = self._ids(np.concatenate([prompt, answer]))
        padded, n = self._padded(ids)
        before = self.export_state()
        total = CostRecord(phase="learning")
        try:
            # Frozen prefix to MLP hook is invariant over value steps, so cache
            # it within this edit. Actual partial-forward work is ledgered.
            with self.ledger.call("learning", partial_forwards=1, tokens=n) as rec:
                h, normalized, projected = hook_prefix(self.base.params, jnp.asarray(padded), self.base.cfg, self.block)
                rec.outputs = (h, normalized, projected)
            total.add(rec)
            label = np.concatenate([np.full(len(prompt), -100, np.int64), answer.astype(np.int64)])
            new_value = cold_uniform(self.rng, self.values.shape[1])
            chosen, active = self._admit(np.asarray(normalized[len(prompt) - 1]), label, new_value)
            # The reference allocates and discards a cold value on each later
            # optimization forward. Evaluation RNG draws are restored by its driver.
            for _ in range(self.value_steps - 1):
                cold_uniform(self.rng, self.values.shape[1])
            targets = np.zeros(len(padded), np.int32)
            mask = np.zeros(len(padded), np.float32)
            targets[len(prompt) - 1:n - 1] = answer
            mask[len(prompt) - 1:n - 1] = 1
            with self.ledger.call("learning", partial_forwards=self.value_steps, reverses=self.value_steps,
                                  tokens=n * self.value_steps) as rec:
                value, losses = optimize_value(self.base.params, h, projected, jnp.asarray(self.values[chosen]),
                                               jnp.asarray(targets), jnp.asarray(mask), jnp.int32(len(prompt) - 1),
                                               jnp.bool_(active), self.base.cfg, self.block, self.value_steps,
                                               jnp.float32(self.value_lr))
                rec.outputs = (value, losses)
            total.add(rec)
            if not np.isfinite(value).all() or not np.isfinite(losses).all():
                raise FloatingPointError("nonfinite GRACE optimization")
            self.values[chosen] = np.asarray(value)
            self.use_counts[chosen] += self.value_steps if active else 0
            self.items_seen += 1
            self._enforce_ceiling()
        except BaseException:
            self.import_state(before)
            raise
        return ItemOutcome(item.item_id, "accepted", False, [{"source_losses": np.asarray(losses).tolist()}], self.value_steps, total, codes=["accepted"])

    def export_state(self):
        rs = self.rng.get_state()
        arrays = {"keys": self.keys.copy(), "values": self.values.copy(), "radii": self.radii.copy(),
                  "use_counts": self.use_counts.copy(), "ages": self.ages.copy(), "rng_mt": rs[1].copy()}
        arrays.update({f"label_{i}": a.copy() for i, a in enumerate(self.labels)})
        return LearnerState(arrays=arrays, scalars={
            "kind": "grace_jax_v1", "base_checksum": self._base_hash, "cfg": asdict(self.base.cfg),
            "block": self.block, "radius": self.radius, "value_steps": self.value_steps, "value_lr": self.value_lr,
            "seed": self.seed, "ceiling_bytes": self.ceiling_bytes, "eviction": self.eviction,
            "items_seen": self.items_seen, "allocations": self.allocations, "evictions": self.evictions,
            "rng_position": int(rs[2]), "rng_has_gauss": int(rs[3]), "rng_cached_gauss": float(rs[4]),
        })

    def import_state(self, state):
        template = self.export_state()
        if state.schema_version != template.schema_version or state.rng or state.correction_index or state.use_tracker != (None, []):
            raise SnapshotError("unexpected GRACE snapshot auxiliary state")
        mutable = {"seed", "items_seen", "allocations", "evictions", "rng_position", "rng_has_gauss", "rng_cached_gauss"}
        if set(state.scalars) != set(template.scalars):
            raise SnapshotError("GRACE snapshot fields differ")
        for key in set(template.scalars) - mutable:
            if state.scalars[key] != template.scalars[key]:
                raise SnapshotError("incompatible GRACE snapshot: " + key)
        if self.base_checksum() != self._base_hash:
            raise SnapshotError("base checksum changed")
        n = len(state.arrays.get("keys", []))
        expected = {"keys": ((n, self.base.d), np.float32), "values": ((n, 4*self.base.d), np.float32),
                    "radii": ((n,), np.float32), "use_counts": ((n,), np.int64), "ages": ((n,), np.int64),
                    "rng_mt": ((624,), np.uint32)}
        if set(state.arrays) != set(expected) | {f"label_{i}" for i in range(n)}:
            raise SnapshotError("GRACE snapshot array inventory differs")
        for key, (shape, dtype) in expected.items():
            a = state.arrays[key]
            if a.shape != shape or a.dtype != dtype or not np.isfinite(a).all():
                raise SnapshotError("invalid GRACE snapshot array: " + key)
        for i in range(n):
            label = state.arrays[f"label_{i}"]
            if label.ndim != 1 or not label.size or label.dtype != np.int64:
                raise SnapshotError("invalid GRACE labels")
        for key in ("seed", "items_seen", "allocations", "evictions", "rng_position", "rng_has_gauss"):
            if type(state.scalars[key]) is not int or state.scalars[key] < 0:
                raise SnapshotError("invalid GRACE scalar: " + key)
        if not 0 <= state.scalars["rng_position"] <= 624 or state.scalars["rng_has_gauss"] != 0:
            raise SnapshotError("invalid MT19937 position/state")
        if np.any(state.arrays["use_counts"] < 0) or np.any(state.arrays["ages"] < 0):
            raise SnapshotError("negative use count or age")
        if state.scalars["rng_cached_gauss"] != 0.0 or state.scalars["seed"] >= 2**64:
            raise SnapshotError("invalid RNG metadata")
        if state.scalars["allocations"] != n + state.scalars["evictions"] or len(set(state.arrays["ages"].tolist())) != n or np.any(state.arrays["ages"] >= state.scalars["allocations"]):
            raise SnapshotError("invalid allocation/age accounting")
        if self.ceiling_bytes is not None and len(serialize(state)) > self.ceiling_bytes:
            raise SnapshotError("snapshot exceeds ceiling")
        rng = np.random.RandomState(0)
        rng.set_state(("MT19937", state.arrays["rng_mt"].copy(), state.scalars["rng_position"], 0, 0.0))
        for name in ("keys", "values", "radii", "use_counts", "ages"):
            setattr(self, name, state.arrays[name].copy())
        self.labels = [state.arrays[f"label_{i}"].copy() for i in range(n)]
        self.rng = rng
        for name in ("seed", "items_seen", "allocations", "evictions"):
            setattr(self, name, state.scalars[name])

    def state_hash(self):
        return self.export_state().content_hash()

    def memory_bytes(self):
        state = self.export_state()
        array_bytes = sum(a.nbytes for a in state.arrays.values())
        total = len(serialize(state))
        return MemoryReport(allocated_bytes=total, occupied_bytes=total,
                            per_bank={0: {"entries": len(self.keys), "array_bytes": array_bytes,
                                          "metadata_bytes": total - array_bytes}},
                            index_bytes=total - self.keys.nbytes - self.values.nbytes,
                            key_dim=self.base.d, value_dim=4 * self.base.d,
                            occupancy=({0: total / self.ceiling_bytes} if self.ceiling_bytes else {}), ceiling_bytes=self.ceiling_bytes or 0)
