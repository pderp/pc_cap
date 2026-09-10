"""B1: Q/V LoRA with whole-answer Adam updates and complete snapshots (S2-03).

Defaults follow PDF S2: rank 8, lr 1e-4, 10 steps per complete edit. The
training loss is mean answer-token CE including the supplied newline. Replay
uses the mean of two item losses, one optimizer step per new/replay pair.
"""

from __future__ import annotations

from dataclasses import asdict

import jax
import jax.numpy as jnp
import numpy as np
import optax

from pccap.baselines import lora_forward as lf
from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.cap.memory import b_cap
from pccap.contracts import CostRecord, EditItem, ItemOutcome, MemoryReport
from pccap.harness.snapshot import LearnerState, SnapshotError, serialize


def _ids(value, vocab, label):
    a = np.asarray(value)
    if a.ndim != 1 or not a.size or a.dtype.kind not in "iu":
        raise ValueError(f"{label} must be a nonempty integer vector")
    if np.any(a < 0) or np.any(a >= vocab):
        raise ValueError(f"{label} token outside vocabulary")
    return a.astype(np.int32, copy=True)


def _named(tree, prefix):
    return {f"{prefix}.{i}.{projection}.{factor}": value
            for i, layer in enumerate(tree)
            for projection, matrices in sorted(layer.items())
            for factor, value in sorted(matrices.items())}


def _tree(arrays, prefix, depth):
    return [{p: {f: jnp.asarray(arrays[f"{prefix}.{i}.{p}.{f}"])
                 for f in ("A", "B")} for p in ("q", "v")} for i in range(depth)]


def state_memory(state, width, adapter_bytes=0, optimizer_bytes=0, buffer_bytes=0):
    """Resident numerical state plus exact serialized metadata; excludes frozen base."""
    array_bytes = sum(a.nbytes for a in state.arrays.values())
    total = len(serialize(state))
    overhead = total - array_bytes
    return MemoryReport(
        allocated_bytes=total, occupied_bytes=total,
        per_bank={0: {"adapter_bytes": adapter_bytes, "optimizer_bytes": optimizer_bytes,
                      "buffer_bytes": buffer_bytes, "metadata_bytes": overhead}},
        index_bytes=overhead, key_dim=0, value_dim=width, occupancy={},
        ceiling_bytes=b_cap(width),
    )


class LoRALearner:
    name = "B1"

    def __init__(self, base: BPBase, rank=8, lr=1e-4, steps=10, seed=0):
        if type(rank) is not int or rank < 1 or rank > base.d:
            raise ValueError("rank must be an integer in [1, base.d]")
        if type(steps) is not int or steps < 1:
            raise ValueError("steps must be a positive integer")
        if not np.isfinite(lr) or lr <= 0:
            raise ValueError("lr must be finite and positive")
        self.base, self.ledger = base, base.ledger
        self.rank, self.lr, self.steps, self.seed = rank, float(lr), steps, int(seed)
        self.update_steps = self.items_seen = 0
        self._base_hash = base.checksum()
        rng = np.random.default_rng(seed)
        self.adapters = [
            {p: {"A": jnp.asarray(rng.normal(0, 0.02, (rank, base.d)), dtype=jnp.float32),
                 "B": jnp.zeros((base.d, rank), dtype=jnp.float32)} for p in ("q", "v")}
            for _ in range(base.D)
        ]
        self.optimizer = optax.adam(self.lr)
        self.opt_state = self.optimizer.init(self.adapters)

        @jax.jit
        def apply(adapters, opt_state, grads):
            updates, new_state = self.optimizer.update(grads, opt_state, adapters)
            updated = optax.apply_updates(adapters, updates)
            finite = jnp.all(jnp.stack([
                jnp.all(jnp.isfinite(a)) for a in jax.tree_util.tree_leaves((updated, new_state))
            ]))
            return updated, new_state, finite

        self._apply = apply

    def trainable_tensors(self):
        return _named(self.adapters, "lora")

    def base_checksum(self):
        return self.base.checksum()

    def predict(self, ids):
        ids = _ids(ids, self.base.vocab, "prefix")
        n = len(ids)
        if n > self.base.cfg.n_pos:
            raise ValueError("prefix exceeds model context")
        size = min(g.bucket_len(n), self.base.cfg.n_pos)
        with self.ledger.call("query", full_forwards=1, tokens=n) as rec:
            logits = lf.forward_jit(self.base.params, self.adapters,
                                    jnp.asarray(g.pad_ids(ids, size, 0)), self.base.cfg)
            rec.outputs = logits
            result = lf.Prediction(logits[:n])
        return result

    def prepare_tokens(self, prompt_ids, answer_ids):
        prompt = _ids(prompt_ids, self.base.vocab, "prompt")
        answer = _ids(answer_ids, self.base.vocab, "answer")
        n = len(prompt) + len(answer) - 1
        if n > self.base.cfg.n_pos:
            raise ValueError("complete teacher-forced edit exceeds model context")
        return prompt, answer

    def prepare_item(self, item: EditItem):
        return self.prepare_tokens(item.prompt_ids, item.answer_ids)

    def _batch(self, pairs):
        lengths = [len(p) + len(a) - 1 for p, a in pairs]
        size = min(g.bucket_len(max(lengths)), self.base.cfg.n_pos)
        ids = np.zeros((len(pairs), size), np.int32)
        targets = np.zeros_like(ids)
        masks = np.zeros_like(ids, dtype=bool)
        for i, (prompt, answer) in enumerate(pairs):
            start = len(prompt) - 1
            ids[i, :lengths[i]] = np.concatenate((prompt, answer[:-1]))
            targets[i, start:start + len(answer)] = answer
            masks[i, start:start + len(answer)] = True
        return tuple(jnp.asarray(a) for a in (ids, targets, masks)), sum(lengths)

    def train_step(self, pairs):
        """One Adam update, charging all complete input sequences including replay."""
        pairs = [self.prepare_tokens(*pair) for pair in pairs]
        if not 1 <= len(pairs) <= 2:
            raise ValueError("one new item and at most one replay item are supported")
        batch, tokens = self._batch(pairs)
        with self.ledger.call("learning", full_forwards=len(pairs), reverses=len(pairs),
                              tokens=tokens) as rec:
            loss, grads = lf.batch_value_and_grad(
                self.base.params, self.adapters, *batch, self.base.cfg
            )
            adapters, state, finite = self._apply(self.adapters, self.opt_state, grads)
            rec.outputs = (loss, adapters, state, finite)
            # Prevent committing corrupt state. The external ledger still keeps the cost.
            if not bool(finite) or not np.isfinite(float(loss)):
                raise FloatingPointError("nonfinite LoRA update")
            self.adapters, self.opt_state = adapters, state
            self.update_steps += 1
        return float(loss), rec

    def update_item(self, item: EditItem) -> ItemOutcome:
        pair = self.prepare_item(item)
        cost, losses = CostRecord(), []
        for _ in range(self.steps):
            loss, rec = self.train_step([pair])
            cost.add(rec)
            losses.append(loss)
        self.items_seen += 1
        return ItemOutcome(item.item_id, "accepted", False,
                           [{"optimizer_step": i + 1, "mean_answer_nll_before_step": loss}
                            for i, loss in enumerate(losses)], self.steps, cost,
                           codes=["fixed_step_baseline"])

    def export_state(self) -> LearnerState:
        adam = self.opt_state[0]
        arrays = {**_named(self.adapters, "lora"), **_named(adam.mu, "adam_mu"),
                  **_named(adam.nu, "adam_nu"), "adam_count": adam.count}
        return LearnerState(
            arrays={k: np.array(v, copy=True) for k, v in arrays.items()},
            scalars={"kind": "B1", "rank": self.rank, "lr": self.lr, "steps": self.steps,
                     "seed": self.seed, "update_steps": self.update_steps,
                     "items_seen": self.items_seen, "base_checksum": self._base_hash,
                     "base_config": asdict(self.base.cfg), "scale": 1.0,
                     "loss_reduction": "mean_answer_tokens_then_mean_items"},
        )

    def import_state(self, state: LearnerState):
        template = self.export_state()
        if state.schema_version != template.schema_version or state.rng or state.correction_index or state.use_tracker != (None, []):
            raise SnapshotError("unexpected LoRA snapshot metadata")
        if set(state.scalars) != set(template.scalars) or set(state.arrays) != set(template.arrays):
            raise SnapshotError("LoRA snapshot field inventory differs")
        mutable = {"seed", "update_steps", "items_seen"}
        for key, value in template.scalars.items():
            if key not in mutable and state.scalars[key] != value:
                raise SnapshotError(f"incompatible LoRA snapshot: {key}")
        for key in mutable:
            if type(state.scalars[key]) is not int or state.scalars[key] < 0:
                raise SnapshotError(f"invalid LoRA counter: {key}")
        if self.base_checksum() != state.scalars["base_checksum"]:
            raise SnapshotError("base weights changed")
        for name, expected in template.arrays.items():
            actual = state.arrays[name]
            if actual.shape != expected.shape or actual.dtype != expected.dtype or not np.isfinite(actual).all():
                raise SnapshotError(f"invalid LoRA array: {name}")
        if int(state.arrays["adam_count"]) != state.scalars["update_steps"]:
            raise SnapshotError("Adam count differs from update counter")
        if any(np.any(a < 0) for k, a in state.arrays.items() if k.startswith("adam_nu.")):
            raise SnapshotError("negative Adam second moment")
        adapters = _tree(state.arrays, "lora", self.base.D)
        adam = self.opt_state[0]._replace(
            count=jnp.asarray(state.arrays["adam_count"]),
            mu=_tree(state.arrays, "adam_mu", self.base.D),
            nu=_tree(state.arrays, "adam_nu", self.base.D),
        )
        self.adapters, self.opt_state = adapters, (adam, *self.opt_state[1:])
        self.seed = state.scalars["seed"]
        self.update_steps, self.items_seen = state.scalars["update_steps"], state.scalars["items_seen"]

    def state_hash(self):
        return self.export_state().content_hash()

    def memory_bytes(self):
        state = self.export_state()
        adapter_bytes = sum(a.nbytes for k, a in state.arrays.items() if k.startswith("lora."))
        optimizer_bytes = sum(a.nbytes for k, a in state.arrays.items() if k.startswith("adam"))
        return state_memory(state, self.base.d, adapter_bytes, optimizer_bytes)
