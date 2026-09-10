"""B3: LoRA plus a byte-bounded, growing-capacity replay reservoir (S2-04).

Capacity = min(floor(fraction * seen), floor(byte_ceiling / slot_bytes)).
Slots hold only token IDs and two length fields, padded to a fixed maximum
size to avoid preferential admission of short answers. The new item is
admitted only AFTER its update; each step samples one previous stored item.

When capacity grows, append the current item; otherwise apply Algorithm R
replacement (draw j uniformly from [0, seen), replace if j < occupancy).
This common growing-capacity adaptation is NOT a uniform sample of all past
edits: floor rounding loses the first 19 candidates at fraction=.05, and
capacity growth favors its current item. Exact all-history uniformity would
require retaining discarded history beyond the specified storage ceiling.
The policy is serialized so this limitation cannot be hidden by a checkpoint.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np

from pccap.baselines.lora import state_memory
from pccap.cap.memory import b_cap
from pccap.contracts import CostRecord, ItemOutcome
from pccap.harness.snapshot import LearnerState, SnapshotError

POLICY = "growing_capacity_algorithm_r_not_uniform_all_history"


class ReplayLearner:
    name = "B3"

    def __init__(self, lora_learner, seed=0, ceiling_items_fraction=0.05, ceiling_bytes=None):
        fraction = Fraction(str(ceiling_items_fraction))
        if not 0 < fraction <= 1:
            raise ValueError("replay fraction must be in (0, 1]")
        ceiling = b_cap(lora_learner.base.d) if ceiling_bytes is None else ceiling_bytes
        if type(ceiling) is not int or ceiling < 0:
            raise ValueError("replay byte ceiling must be a nonnegative integer")
        self.lora = lora_learner
        self.base, self.ledger = lora_learner.base, lora_learner.ledger
        self.seed, self.rng = int(seed), np.random.default_rng(seed)
        self.fraction, self.ceiling_bytes = fraction, ceiling
        # Two int32 length fields + prompt/answer storage (max input length + final target).
        self.slot_words = self.base.cfg.n_pos + 3
        self.slot_bytes = self.slot_words * np.dtype(np.int32).itemsize
        self.buffer = np.empty((0, self.slot_words), np.int32)
        self.seen = 0
        self.initial_items_seen = self.lora.items_seen

    @property
    def capacity(self):
        return self.capacity_at(self.seen)

    def capacity_at(self, seen):
        return min(seen * self.fraction.numerator // self.fraction.denominator,
                   self.ceiling_bytes // self.slot_bytes)

    def _encode(self, pair):
        prompt, answer = self.lora.prepare_tokens(*pair)
        row = np.zeros(self.slot_words, np.int32)
        row[:2] = len(prompt), len(answer)
        row[2:2 + len(prompt) + len(answer)] = np.concatenate((prompt, answer))
        return row

    @staticmethod
    def _decode(row):
        p, a = int(row[0]), int(row[1])
        return row[2:2 + p].copy(), row[2 + p:2 + p + a].copy()

    def observe(self, prompt_ids, answer_ids):
        """Admit one completed edit. Exposed separately for reservoir controls."""
        row = self._encode((prompt_ids, answer_ids))
        self.seen += 1
        if self.capacity == 0:
            return {"action": "not_stored", "reason": "zero_capacity", "slot": None}
        if len(self.buffer) < self.capacity:
            self.buffer = np.concatenate((self.buffer, row[None]), axis=0)
            return {"action": "append", "slot": len(self.buffer) - 1}
        j = int(self.rng.integers(self.seen))
        if j < len(self.buffer):
            self.buffer[j] = row
            return {"action": "replace", "slot": j}
        return {"action": "not_stored", "reason": "reservoir_draw", "slot": None}

    def sample(self):
        """Uniform draw from the current reservoir; never called by predict."""
        if not len(self.buffer):
            return None, None
        slot = int(self.rng.integers(len(self.buffer)))
        return self._decode(self.buffer[slot]), slot

    def update_item(self, item):
        pair = self.lora.prepare_item(item)
        cost, records = CostRecord(), []
        for step in range(self.lora.steps):
            replay, slot = self.sample()
            pairs = [pair] if replay is None else [pair, replay]
            loss, rec = self.lora.train_step(pairs)
            cost.add(rec)
            records.append({"optimizer_step": step + 1, "mean_item_loss_before_step": loss,
                            "replay_slot": slot, "replay_input_tokens":
                            0 if replay is None else len(replay[0]) + len(replay[1]) - 1})
        self.lora.items_seen += 1
        admission = self.observe(*pair)
        records[-1]["reservoir_admission"] = admission
        return ItemOutcome(item.item_id, "accepted", False, records, self.lora.steps, cost,
                           codes=["fixed_step_baseline", POLICY])

    def predict(self, ids):
        return self.lora.predict(ids)

    def base_checksum(self):
        return self.lora.base_checksum()

    def export_state(self):
        inner = self.lora.export_state()
        return LearnerState(
            arrays={**inner.arrays, "replay_buffer": self.buffer.copy()},
            scalars={"kind": "B3", "learner": inner.scalars, "seen": self.seen,
                     "initial_items_seen": self.initial_items_seen, "seed": self.seed,
                     "fraction": [self.fraction.numerator, self.fraction.denominator],
                     "ceiling_bytes": self.ceiling_bytes, "slot_words": self.slot_words,
                     "rounding": "floor", "sampling_policy": POLICY},
            rng=LearnerState.capture_rng(np_gen=self.rng),
        )

    def import_state(self, state):
        expected = self.export_state()
        if state.schema_version != expected.schema_version or state.correction_index or state.use_tracker != (None, []):
            raise SnapshotError("unexpected replay snapshot metadata")
        if set(state.scalars) != set(expected.scalars) or set(state.arrays) != set(expected.arrays):
            raise SnapshotError("replay snapshot inventory differs")
        mutable = {"learner", "seen", "initial_items_seen", "seed"}
        for key in expected.scalars.keys() - mutable:
            if state.scalars[key] != expected.scalars[key]:
                raise SnapshotError(f"incompatible replay snapshot: {key}")
        for key in ("seen", "initial_items_seen", "seed"):
            if type(state.scalars[key]) is not int or state.scalars[key] < 0:
                raise SnapshotError(f"invalid replay counter: {key}")
        buffer = state.arrays["replay_buffer"]
        if buffer.ndim != 2 or buffer.shape[1] != self.slot_words or buffer.dtype != np.int32:
            raise SnapshotError("invalid replay buffer shape/dtype")
        if len(buffer) > self.capacity_at(state.scalars["seen"]) or buffer.nbytes > self.ceiling_bytes:
            raise SnapshotError("restored replay buffer exceeds a ceiling")
        for row in buffer:
            p, a = int(row[0]), int(row[1])
            if p < 1 or a < 1 or p + a > self.slot_words - 2:
                raise SnapshotError("invalid replay length fields")
            if np.any(row[2:2 + p + a] < 0) or np.any(row[2:2 + p + a] >= self.base.vocab) or np.any(row[2 + p + a:] != 0):
                raise SnapshotError("invalid replay token IDs or padding")
        if set(state.rng) != {"numpy"}:
            raise SnapshotError("replay RNG missing or unsupported")
        candidate_rng = np.random.default_rng()
        try:
            candidate_rng.bit_generator.state = state.rng["numpy"]
        except (TypeError, ValueError, KeyError) as exc:
            raise SnapshotError("invalid replay RNG") from exc
        inner = LearnerState(arrays={k: v for k, v in state.arrays.items() if k != "replay_buffer"},
                             scalars=state.scalars["learner"], schema_version=state.schema_version)
        self.lora.import_state(inner)
        self.buffer = buffer.copy()
        self.rng = candidate_rng
        self.seen, self.seed = state.scalars["seen"], state.scalars["seed"]
        self.initial_items_seen = state.scalars["initial_items_seen"]

    def state_hash(self):
        return self.export_state().content_hash()

    def memory_bytes(self):
        state = self.export_state()
        adapters = sum(a.nbytes for k, a in state.arrays.items() if k.startswith("lora."))
        optimizer = sum(a.nbytes for k, a in state.arrays.items() if k.startswith("adam"))
        report = state_memory(state, self.base.d, adapters, optimizer, self.buffer.nbytes)
        report.per_bank[0].update({"buffer_items": len(self.buffer), "seen": self.seen,
                                   "buffer_capacity": self.capacity,
                                   "buffer_ceiling_bytes": self.ceiling_bytes,
                                   "slot_bytes": self.slot_bytes, "sampling_policy": POLICY})
        return report
