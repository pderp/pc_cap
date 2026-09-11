"""B4-S batch controls: ragged boundaries, real codebook reads, state and cost."""
import numpy as np
import pytest
from tests.baselines.test_grace_jax import item, tiny

from pccap.baselines.grace_batch import BatchedGraceLearner
from pccap.baselines.grace_jax import GraceLearner


@pytest.mark.parametrize("trained", [False, True])
def test_vmapped_logits_preserve_row_order_boundaries_and_state(trained):
    base = tiny()
    scalar = GraceLearner(base, block=0, value_steps=3)
    if trained:
        scalar.update_item(item())
    batch = BatchedGraceLearner(base, block=0, value_steps=3)
    batch.import_state(scalar.export_state())
    seqs = [np.array([1, 2, 3, 4, 5], np.int32), np.array([1, 2, 3], np.int32), np.arange(1, 14, dtype=np.int32), np.array([1, 2, 3, 4], np.int32)]
    positions = [2, 2, 4, 2]
    expected = np.stack([scalar.predict(ids, key_position=pos, last_only=True) for ids, pos in zip(seqs, positions)])
    before, base_before = batch.state_hash(), batch.base_checksum()
    out = batch.last_logits_batch(seqs, key_positions=positions)
    np.testing.assert_allclose(out, expected, rtol=2e-5, atol=2e-5)
    np.testing.assert_array_equal(out.argmax(-1), expected.argmax(-1))
    assert batch.state_hash() == before and batch.base_checksum() == base_before
    assert batch.memory_bytes() == scalar.memory_bytes()
    # A read must not change the next training transition, including RNG.
    scalar.update_item(item(1))
    batch.update_item(item(1))
    assert batch.state_hash() == scalar.state_hash()


def test_batch_charges_every_sequence_to_requested_phase():
    learner = BatchedGraceLearner(tiny(), block=0, value_steps=1)
    seqs = [np.array([1, 2, 3]), np.array([1, 2, 3, 4])]
    before = learner.ledger.totals()
    learner.last_logits_batch(seqs, phase="learning", key_positions=[2, 2])
    after = learner.ledger.totals()
    assert after["learning"]["full_forwards"]-before["learning"]["full_forwards"] == 2
    assert after["learning"]["tokens"]-before["learning"]["tokens"] == 7
    assert after["query"]["full_forwards"] == before["query"]["full_forwards"]


def test_invalid_boundaries_refuse_before_any_work_and_empty_batch_is_defined():
    learner = BatchedGraceLearner(tiny(), block=0, value_steps=1)
    seqs = [np.array([1, 2, 3])]
    before = learner.state_hash()
    for positions in ([], [3], [-1], [1.5], [True]):
        with pytest.raises(ValueError):
            learner.last_logits_batch(seqs, key_positions=positions)
    assert learner.state_hash() == before
    assert learner.ledger.totals()["total"]["full_forwards"] == 0
    assert learner.last_logits_batch([]).shape == (0, 32)
