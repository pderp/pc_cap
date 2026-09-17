"""CPU scalar/batch gates for all six comparator families; no real model or results writes."""

# isort: off
import pccap  # noqa: F401 -- determinism before JAX
import jax.numpy as jnp
import numpy as np
# isort: on

import pytest
from scripts import r1_68e_batched_drift_v0 as batch

from pccap.bases import gpt2_jax as g
from pccap.cap.cap import CapConfig
from pccap.contracts import CostRecord, ForwardResult, SiteId
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.revision_v1.stage4_assays import CellAssays
from tests.revision_v1.tiny_base import TinyBase, tiny_params


class RetainedTinyBase(TinyBase):
    """TinyBase with retained partial sites, required by scalar v0's live retrieval."""

    def forward_from(
        self, bank, hidden, ids, writes=(), phase="query", retain_sites=False, last_only=True
    ):
        _, n_d, W, n, p = self._prep(ids, writes)
        self.calls["forward_from"] += 1
        logits, rows, full = g.forward_from_jit(
            self.params, jnp.asarray(hidden), n_d, W, self.cfg, bank, retain_sites, last_only
        )
        return ForwardResult(
            logits=logits if last_only else logits[:n],
            sites={SiteId(m, g.BANK_BLOCK[m], p): rows[m] for m in rows},
            cost=CostRecord(phase=phase, partial_forwards=1, tokens=n),
            hidden=full,
        )


def adapter(condition):
    base = RetainedTinyBase()
    original = RetainedTinyBase(tiny_params(7)) if condition.startswith("S1_") else base
    cfg = CapConfig(arm="C2" if condition == "v0_live_C2" else "C1", d=base.d)
    learner = batch.CONDITION_CLASSES[condition](base, cfg, None)
    return CellAdapter(learner, condition, locality_base=original)


def populate(a, *, dense=True):
    cap = a.learner
    ids = np.array([2, 3, 4], np.int32)
    result = a.base.forward(ids)
    for m in (1, 2, 3):
        q = cap.key(result.sites[SiteId(m, g.BANK_BLOCK[m], 2)])
        value = np.linspace(-0.35, 0.45, a.base.d, dtype=np.float32) * m
        cap.banks[m].bank.allocate(q, 100.0 if dense else 1e-4, value)


@pytest.mark.parametrize("condition", list(batch.CONDITION_CLASSES))
@pytest.mark.parametrize("occupied", [False, True])
def test_all_adapters_per_position(condition, occupied):
    a = adapter(condition)
    if occupied:
        populate(a)
    definition = {"windows": [[2, 3, 4, 5, 6], [7, 8, 9]], "expected_positions": 6}
    before = a.state_hash()
    scalar = CellAssays(a, None).drift(definition)
    assays = CellAssays(a, None)
    result = batch.batched_drift(assays, definition, batch_size=4)
    assert result["source_sha256"] == scalar["source_sha256"]
    assert a.state_hash() == before
    assert [r["item_id"] for r in result["rows"]] == [r["item_id"] for r in scalar["rows"]]
    max_error = 0
    for r, s in zip(result["rows"], scalar["rows"]):
        for key in ("capoff", "original", "cap"):
            error = abs(r[key] - s[key])
            max_error = max(max_error, error)
            assert error <= 1e-4
    print(f"PARITY {condition} occupied={occupied} max_per_position_nats={max_error:.12g}")
    for threshold in (0.01, 0.1, 1.0):
        assert sum(r["cap"] - r["capoff"] > threshold for r in result["rows"]) == sum(
            r["cap"] - r["capoff"] > threshold for r in scalar["rows"]
        )
    if not occupied:
        assert all(r["cap"] == r["capoff"] for r in result["rows"])
    if condition.startswith("S1_"):
        assert any(abs(r["original"] - r["capoff"]) > 0.01 for r in result["rows"])
        assert any(e.get("model") == "original_batch" for e in assays.events)
    selections = [s for e in assays.events for s in e.get("selections", [])]
    assert len(selections) == 6
    initial = [e for e in assays.events if e.get("model") == "shared_capoff_selection"]
    assert len(initial) == 2
    assert sum(e["returned_cost"]["full_forwards"] for e in initial) == 8


@pytest.mark.parametrize("condition", list(batch.CONDITION_CLASSES))
def test_sparse_and_zero_value_hits_are_exact_null(condition):
    a = adapter(condition)
    cap = a.learner
    seqs = [np.array([2, 3, 4]), np.array([8, 9]), np.array([10, 11, 12])]
    for i in (0, 1):
        fr = a.base.forward(seqs[i])
        q = cap.key(fr.sites[SiteId(1, g.BANK_BLOCK[1], len(seqs[i]) - 1)])
        value = (
            np.linspace(-0.4, 0.4, a.base.d, dtype=np.float32)
            if i == 0
            else np.zeros(a.base.d, np.float32)
        )
        cap.banks[1].bank.allocate(q, 1e-4, value)

    # Poison an uncorrected partial row: the reader must never accept this row.
    class PoisonBatchBase(RetainedTinyBase):
        def forward_from_batch(self, bank, hidden, lengths, writes, phase="query"):
            logits, rows, full = g.forward_from_batch_jit(
                self.params, hidden, jnp.asarray(lengths), jnp.asarray(writes), self.cfg, bank
            )
            mask = jnp.asarray(np.any(writes[:, bank - 1], axis=1))
            return (
                jnp.where(mask[:, None], logits, logits + 100),
                jnp.where(mask[:, None, None], rows, rows + 100),
                jnp.where(mask[:, None, None, None], full, full + 100),
            )

    replacement = PoisonBatchBase(a.base.params)
    cap.base = replacement
    a.base = replacement
    reader = batch.V0PositionBatchReader(a, batch_size=4)
    scalar = [cap.edited_forward(ids, phase="query") for ids in seqs]
    out = reader.last_logits_batch(seqs)
    assert reader.last_selections[0][1]["nonzero_write"]
    assert reader.last_selections[1][1] == {"slot": 1, "nonzero_write": False}
    assert reader.last_selections[2][1]["slot"] == -1
    assert np.array_equal(out[1:], reader.last_capoff[1:])
    for i in range(3):
        np.testing.assert_allclose(out[i], scalar[i].logits, rtol=0, atol=1e-4)
        assert {m: v["slot"] for m, v in reader.last_selections[i].items()} == scalar[i].fired
    second = reader.last_logits_batch([seqs[2], seqs[0]])
    assert np.array_equal(second[0], reader.last_capoff[0])
    assert reader.last_selections[0][1]["slot"] == -1


@pytest.mark.parametrize("condition", ["v0_live_C1", "v0_stable"])
def test_live_downstream_key_uses_upstream_write(condition):
    a = adapter(condition)
    cap = a.learner
    ids = np.array([2, 3, 4])
    fr = a.base.forward(ids)
    key1 = cap.key(fr.sites[SiteId(1, g.BANK_BLOCK[1], 2)])
    cap.banks[1].bank.allocate(key1, 1e-4, np.linspace(-2, 2, a.base.d, dtype=np.float32))
    intermediate = cap.edited_forward(ids, phase="query")
    live_key = cap.key(intermediate.sites[2])
    stable_key = cap.key(fr.sites[SiteId(2, g.BANK_BLOCK[2], 2)])
    assert np.linalg.norm(live_key - stable_key) > 0.01
    cap.banks[2].bank.allocate(live_key, 1e-4, np.full(a.base.d, 0.5, np.float32))
    reader = batch.V0PositionBatchReader(a, batch_size=2)
    out = reader.last_logits_batch([ids])
    scalar = cap.edited_forward(ids, phase="query")
    assert reader.last_selections[0][2]["slot"] == (0 if condition == "v0_live_C1" else -1)
    np.testing.assert_allclose(out[0], scalar.logits, rtol=0, atol=1e-4)


def test_rejects_invalid_inputs_before_forward():
    a = adapter("v0_stable")
    for size in (0, True, 33, 1.5):
        with pytest.raises(ValueError):
            batch.V0PositionBatchReader(a, batch_size=size)
    reader = batch.V0PositionBatchReader(a, batch_size=2)
    for seqs in ([], [[]], [[-1]], [[64]], [[2.5]], [[True]], [[1] * 129]):
        with pytest.raises(ValueError):
            reader.last_logits_batch(seqs)
    with pytest.raises(ValueError, match="inventory"):
        batch.batched_drift(CellAssays(a, None), {"windows": [[1, 2]], "expected_positions": 2})
    assert a.base.calls["forward"] == 0


def test_failed_partial_work_is_charged(monkeypatch):
    a = adapter("v0_stable")
    populate(a)

    def fail(*args):
        raise RuntimeError("synthetic partial failure")

    monkeypatch.setattr(batch, "_partial", fail)
    assays = CellAssays(a, None)
    before = a.state_hash()
    with pytest.raises(RuntimeError, match="synthetic partial"):
        batch.batched_drift(assays, {"windows": [[1, 2, 3]], "expected_positions": 2}, batch_size=4)
    event = next(e for e in assays.events if e.get("status") == "failed")
    assert event["returned_cost"]["partial_forwards"] == 4
    assert event["physical_padding"] == 2
    assert a.state_hash() == before
