"""S2-04: reservoir statistics, strict byte bounds, replay costs and exact restore.

The fixed-capacity control tests Algorithm R's uniformity. The separate
growing-capacity control explicitly tests its declared warm-up exclusion;
it deliberately does not claim uniform sampling of the full history.
"""

from types import SimpleNamespace

import numpy as np
import pytest
from tests.baselines.test_lora import item, small_base

from pccap.baselines.lora import LoRALearner
from pccap.baselines.replay import POLICY, ReplayLearner
from pccap.harness.snapshot import ItemGuard, SnapshotError, restore, serialize


class ReservoirOnly:
    """No model or optimizer needed to test the NumPy reservoir mechanism."""

    base = SimpleNamespace(d=16, vocab=1000, cfg=SimpleNamespace(n_pos=8))
    ledger = None
    items_seen = 0

    @staticmethod
    def prepare_tokens(prompt, answer):
        return np.asarray(prompt, np.int32), np.asarray(answer, np.int32)


def test_fixed_capacity_reservoir_has_uniform_inclusion_statistics():
    # fraction=1 isolates constant-capacity Algorithm R; three equal-size slots.
    counts = np.zeros(20, np.int32)
    repetitions = 2000
    for seed in range(repetitions):
        learner = ReplayLearner(ReservoirOnly(), seed, ceiling_items_fraction=1,
                                ceiling_bytes=3 * 44)
        for index in range(20):
            learner.observe([index], [21])
        assert learner.buffer.shape == (3, 11)
        counts[learner.buffer[:, 2]] += 1
    expected = repetitions * 3 / 20
    chi_squared = float(np.sum((counts - expected) ** 2 / expected))
    assert chi_squared < 65, (counts.tolist(), chi_squared)


def test_floor_rounding_growth_and_warmup_exclusion_are_explicit():
    learner = ReplayLearner(ReservoirOnly(), 1)
    for n in range(1, 101):
        learner.observe([n], [999])
        assert learner.capacity == n // 20
        assert len(learner.buffer) == n // 20
        assert learner.buffer.nbytes <= learner.ceiling_bytes
        if n == 20:
            assert learner.buffer[0, 2] == 20
    assert np.all(learner.buffer[:, 2] >= 20)
    assert POLICY.endswith("not_uniform_all_history")


def test_replay_draw_is_uniform_over_stored_items():
    learner = ReplayLearner(ReservoirOnly(), 7, ceiling_items_fraction=1)
    for n in range(4):
        learner.observe([n], [999])
    counts = np.zeros(4, np.int32)
    for _ in range(4000):
        pair, slot = learner.sample()
        assert int(pair[0][0]) == slot
        counts[slot] += 1
    assert np.sum((counts - 1000) ** 2 / 1000) < 30, counts


def test_byte_limits_variable_lengths_and_zero_capacity():
    base = small_base()
    lora = LoRALearner(base, rank=2, steps=1)
    # 67 int32 words per slot; 535 bytes can hold one slot, never two.
    learner = ReplayLearner(lora, 5, ceiling_items_fraction=1, ceiling_bytes=535)
    assert learner.slot_bytes == 268
    for length in (1, 3, 12, 60):
        learner.observe(np.arange(length, dtype=np.int32) % 32, [3])
        assert learner.buffer.nbytes == 268
        assert learner.capacity == 1
    before = learner.state_hash()
    with pytest.raises(ValueError):
        learner.observe(np.ones(65, np.int32), [2])
    assert learner.state_hash() == before
    report = learner.memory_bytes()
    assert report.per_bank[0]["buffer_bytes"] == 268
    assert report.allocated_bytes == len(serialize(learner.export_state()))
    assert report.per_bank[0]["optimizer_bytes"] > 0
    empty = ReplayLearner(lora, ceiling_items_fraction=1, ceiling_bytes=267)
    for _ in range(5):
        empty.observe([1], [2])
    assert empty.capacity == len(empty.buffer) == 0
    assert empty.sample() == (None, None)


def test_replay_training_costs_only_past_items_and_restore_future_equality():
    base = small_base()
    before_base = base.checksum()
    learner = ReplayLearner(LoRALearner(base, rank=2, steps=2), 123,
                            ceiling_items_fraction=1, ceiling_bytes=536)
    first = learner.update_item(item(1))
    assert first.cost.full_forwards == first.cost.reverses == 2
    assert all(row["replay_slot"] is None for row in first.prefix_outcomes)
    second_item = item(2)
    second_item.answer_ids = np.array([10, 11, 12], np.int32)
    second = learner.update_item(second_item)
    assert second.cost.full_forwards == second.cost.reverses == 4
    assert second.cost.tokens == 20
    assert second.rounds_used == 2
    assert all(row["replay_slot"] == 0 for row in second.prefix_outcomes)
    assert learner.seen == learner.lora.items_seen == 2
    saved = restore(serialize(learner.export_state()))
    fork = ReplayLearner(LoRALearner(base, rank=2, steps=2, seed=44), 999,
                        ceiling_items_fraction=1, ceiling_bytes=536)
    fork.import_state(saved)
    assert fork.state_hash() == learner.state_hash()
    result = learner.update_item(item(3))
    fork_result = fork.update_item(item(3))
    assert [r["replay_slot"] for r in result.prefix_outcomes] == [r["replay_slot"] for r in fork_result.prefix_outcomes]
    assert learner.state_hash() == fork.state_hash()
    before = learner.state_hash()
    reverses = base.ledger.learning.reverses
    with ItemGuard(learner):
        learner.update_item(item(4))
    assert learner.state_hash() == before
    assert base.ledger.learning.reverses == reverses + 4
    query = learner.predict(item().prompt_ids)
    assert query.shape == (3, 32) and query.logits is query
    assert learner.state_hash() == before
    assert base.checksum() == before_base


def test_buffer_and_rng_corruption_refused_before_any_state_change():
    learner = ReplayLearner(LoRALearner(small_base(), rank=2, steps=1), 8,
                            ceiling_items_fraction=1)
    learner.update_item(item())
    before = learner.export_state()
    bad = before.clone()
    bad.arrays["replay_buffer"][0, 0] = 100000
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    bad = before.clone()
    bad.rng = {}
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    bad = before.clone()
    bad.arrays["adam_count"] = np.array(999, np.int32)
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    bad = before.clone()
    bad.scalars["seen"] = 0
    with pytest.raises(SnapshotError):
        learner.import_state(bad)
    assert learner.state_hash() == before.content_hash()


def test_memory_counts_token_buffer_optimizer_and_rng_metadata():
    learner = ReplayLearner(LoRALearner(small_base(), rank=2, steps=1), 8,
                            ceiling_items_fraction=1)
    learner.update_item(item())
    state = learner.export_state()
    assert state.scalars["sampling_policy"] == POLICY
    assert state.scalars["rounding"] == "floor"
    assert not any(key in state.scalars for key in ("prompt", "answer", "item_id", "digest"))
    report = learner.memory_bytes()
    arrays = sum(a.nbytes for a in state.arrays.values())
    assert report.allocated_bytes == arrays + report.index_bytes == len(serialize(state))
    assert report.allocated_bytes == report.occupied_bytes
    assert report.per_bank[0]["buffer_bytes"] == learner.buffer.nbytes
    assert report.per_bank[0]["buffer_items"] == 1
