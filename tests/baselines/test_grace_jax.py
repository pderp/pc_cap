"""CPU controls for the JAX GRACE implementation; no production data or GPU."""
import numpy as np
import pytest

from pccap.baselines.grace_jax import GraceLearner, cold_uniform
from pccap.bases.bp import BPBase
from pccap.bases.gpt2_jax import GPT2Config
from pccap.contracts import EditItem
from pccap.fixtures.grammar_model import init_params
from pccap.harness.snapshot import SnapshotError, serialize


def tiny():
    cfg = GPT2Config(n_layer=2, n_head=2, d=8, vocab=32, n_pos=16)
    return BPBase(params_np=init_params(10, cfg), cfg=cfg)


def item(i=0):
    return EditItem(str(i), bytes([i]) * 16, "p", "a", ["a"], [], [],
                    np.asarray([1, 2, 3], np.int32), np.asarray([4], np.int32))


def test_cold_random_stream_matches_pinned_cpu_source():
    np.testing.assert_array_equal(cold_uniform(np.random.RandomState(0), 4),
                                  [0.49625658988952637, 0.7682217955589294, 0.08847743272781372, 0.13203048706054688])


def test_empty_hook_identity_and_read_only_predictions():
    base = tiny()
    learner = GraceLearner(base, block=0, value_steps=3)
    ids = np.asarray([1, 2, 3], np.int32)
    before = learner.state_hash()
    np.testing.assert_allclose(learner.predict(ids), np.asarray(base.forward(ids).logits), atol=2e-6, rtol=2e-6)
    assert learner.state_hash() == before
    out = learner.update_item(item())
    before = learner.state_hash()
    learner.predict([1, 2, 3, 4], key_position=2)
    assert learner.state_hash() == before
    assert base.checksum() == learner.base_checksum()
    assert out.cost.reverses == 3 and out.cost.partial_forwards == 4
    assert len(out.prefix_outcomes[0]["source_losses"]) == 3


def test_source_expansion_conflict_and_zero_distance_tie():
    learner = GraceLearner(tiny(), block=0, value_steps=1)
    q = np.zeros(8, np.float32)
    value = np.ones(32, np.float32)
    learner._admit(q, np.array([7], np.int64), value)
    q[0] = 1.5
    learner._admit(q, np.array([7], np.int64), value)
    np.testing.assert_allclose(learner.radii, [1.5])
    q[0] = 1
    learner._admit(q, np.array([8], np.int64), value)
    np.testing.assert_allclose(learner.radii, [0.5 - 1e-5, 0.5], atol=1e-7)
    other = GraceLearner(tiny(), block=0, value_steps=1)
    q[:] = 0
    other._admit(q, np.array([7], np.int64), value)
    chosen, active = other._admit(q, np.array([8], np.int64), value)
    assert chosen == 0 and not active and other.radii[0] < 0


def test_snapshot_restores_future_update_and_rejects_bad_state():
    base = tiny()
    a = GraceLearner(base, block=0, value_steps=3)
    a.update_item(item())
    state = a.export_state()
    b = GraceLearner(base, block=0, value_steps=3)
    b.import_state(state)
    assert b.state_hash() == a.state_hash()
    a.update_item(item(1))
    b.update_item(item(1))
    assert a.state_hash() == b.state_hash()
    bad = state.clone()
    bad.arrays["values"][0, 0] = np.nan
    unchanged = b.state_hash()
    with pytest.raises(SnapshotError):
        b.import_state(bad)
    assert b.state_hash() == unchanged
    assert b.memory_bytes().allocated_bytes == len(serialize(b.export_state()))


def test_eviction_is_lowest_learning_use_then_oldest_and_bound_is_enforced():
    base = tiny()
    learner = GraceLearner(base, block=0, value_steps=1)
    for i in range(3):
        q = np.zeros(8, np.float32)
        q[0] = 10*i
        learner._admit(q, np.array([i], np.int64), np.ones(32, np.float32)*i)
    learner.use_counts[:] = [2, 1, 1]
    limit = learner.memory_bytes().allocated_bytes - 100
    learner.ceiling_bytes, learner.eviction = limit, "use_count_then_age"
    learner._enforce_ceiling()
    assert 1 not in learner.ages and 0 in learner.ages
    assert learner.memory_bytes().allocated_bytes <= limit
    with pytest.raises(ValueError):
        GraceLearner(base, block=0, ceiling_bytes=1)
