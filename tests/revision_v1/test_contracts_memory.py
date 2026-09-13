"""Stage 1 gates 1, 3 and 4 for the record store, contracts and observation encoder (CPU; synthetic base)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from pccap.contracts import CostRecord
from pccap.revision_v1.contracts import MemoryRecord, RevisionCost, assert_no_target_parameter
from pccap.revision_v1.memory import (
    META_BYTES_PER_RECORD,
    CapacityError,
    KeyVersionMismatch,
    RecordStore,
)
from pccap.revision_v1.observations import ObservationEncoder, prompt_mask


def _rec(i: int, key, fact="f", rev=1, src=None, dk=4, dc=3):
    return MemoryRecord(record_id=f"r{i}", fact_id=fact, revision_id=rev, created_order=-1, key=np.asarray(key, np.float32).reshape(dk), code=np.full(dc, float(i), np.float32), source_ids=src)


def test_retrieval_is_deterministic_with_created_order_ties():
    st = RecordStore(dk=4, d_code=3)
    for i in range(5):
        st.add(_rec(i, [1, 0, 0, 0]))  # identical keys → ties
    out = st.retrieve(np.array([1, 0, 0, 0]), k=3)
    assert [c.record_id for c in out] == ["r0", "r1", "r2"] and [c.rank for c in out] == [0, 1, 2]
    st2 = RecordStore(dk=4, d_code=3)
    for i in range(5):
        st2.add(_rec(i, [1, 0, 0, 0]))
    assert [c.record_id for c in st2.retrieve(np.array([1, 0, 0, 0]), k=3)] == ["r0", "r1", "r2"]


def test_supersession_keeps_old_record_inactive_and_immutable_ids():
    st = RecordStore(dk=4, d_code=3)
    st.add(_rec(0, [1, 0, 0, 0], fact="f"))
    new = st.supersede("r0", _rec(1, [0, 1, 0, 0], fact="f", rev=2))
    assert st.get("r0").active is False and st.get("r0").superseded_by == "r1" and new.active
    assert [c.record_id for c in st.retrieve(np.array([1, 0, 0, 0]), k=5)] == ["r1"]  # inactive never retrieved
    with pytest.raises(ValueError):
        st.add(_rec(1, [0, 0, 1, 0]))  # duplicate id
    with pytest.raises(ValueError):
        st.supersede("r1", _rec(2, [0, 0, 1, 0], fact="g", rev=3))  # fact id must be kept
    with pytest.raises(ValueError):
        st.supersede("r1", _rec(3, [0, 0, 1, 0], fact="f", rev=1))  # later revision required


def test_ceiling_counts_every_byte_and_refuses():
    per = 4 * 4 + 3 * 4 + META_BYTES_PER_RECORD
    st = RecordStore(dk=4, d_code=3, ceiling_bytes=2 * per + 8)
    st.add(_rec(0, [1, 0, 0, 0]))
    st.add(_rec(1, [1, 0, 0, 0], src=np.int32([5, 6])))  # 8 token bytes
    assert st.bytes()["total"] == 2 * per + 8
    with pytest.raises(CapacityError):
        st.add(_rec(2, [1, 0, 0, 0]))


def test_key_version_refusal_and_rebuild():
    st = RecordStore(dk=4, d_code=3, encoder_version=1)
    st.add(_rec(0, [1, 0, 0, 0], src=np.int32([1, 2, 3])))
    with pytest.raises(KeyVersionMismatch):
        st.retrieve(np.array([1, 0, 0, 0]), k=1, query_version=2)
    st.add(_rec(1, [0, 1, 0, 0]))  # no source prefix → rebuild refused
    with pytest.raises(KeyVersionMismatch):
        st.rebuild_keys(lambda ids: np.ones(4), encoder_version=2)
    st.records[1].source_ids = np.int32([9])
    rep = st.rebuild_keys(lambda ids: np.full(4, float(len(ids))), encoder_version=2)
    assert rep["records"] == 2 and st.encoder_version == 2 and st.index_version == 1
    assert np.allclose(st.get("r0").key, 3.0) and np.allclose(st.get("r1").key, 1.0)
    assert st.retrieve(np.full(4, 3.0), k=1, query_version=2)[0].record_id == "r0"


def test_snapshot_round_trip_and_hash():
    st = RecordStore(dk=4, d_code=3)
    st.add(_rec(0, [1, 0, 0, 0], src=np.int32([1, 2])))
    st.supersede("r0", _rec(1, [0, 1, 0, 0], rev=2))
    st.set_code("r1", np.array([7, 8, 9]))
    h = st.content_hash()
    back = RecordStore.from_state(st.export())
    assert back.content_hash() == h
    assert back.get("r0").active is False and back.get("r0").superseded_by == "r1" and back.get("r1").code.tolist() == [7, 8, 9]
    assert back.get("r0").source_ids.tolist() == [1, 2] and back.get("r1").source_ids is None
    with pytest.raises(ValueError):
        st.set_code("r0", np.zeros(3))  # inactive record cannot change
    with pytest.raises(ValueError):
        st.set_code("r1", np.array([np.nan, 0, 0]))


def test_revision_cost_adds_both_families():
    a = RevisionCost(phase="query", full_forwards=1, extra_pass_forwards=1)
    a.add(CostRecord(phase="query", full_forwards=2))
    a.add(RevisionCost(phase="query", extra_pass_forwards=3, records_touched=2))
    assert a.full_forwards == 3 and a.extra_pass_forwards == 4 and a.records_touched == 2


def test_signature_gate_rejects_target_parameters():
    def predict(prefix, state):
        return None

    def bad(prefix, state, target):
        return None

    assert_no_target_parameter(predict)
    with pytest.raises(TypeError):
        assert_no_target_parameter(bad)


@dataclass
class _CausalBase:
    """hidden[m][t] depends only on ids[:t+1] (a running hash of the prefix); mimics the base's forward surface."""

    d: int = 6

    def checksum(self):
        return "fake"

    def forward(self, ids, writes=(), retain_sites=True, phase="query", last_only=True):
        ids = np.asarray(ids, np.int64)
        T = len(ids)
        hidden = {}
        for m in (1, 2, 3):
            h = np.zeros((T, self.d), np.float32)
            acc = 0.0
            for t in range(T):
                acc = acc * 0.5 + float(ids[t]) * m
                h[t] = acc + np.arange(self.d)
            hidden[m] = h
        from pccap.contracts import ForwardResult
        return ForwardResult(logits=np.zeros(3), sites={}, cost=CostRecord(phase=phase, full_forwards=1, tokens=T), hidden=hidden)


def test_observation_is_causal_and_span_masked():
    enc = ObservationEncoder(_CausalBase())
    ids = np.int32([3, 1, 4, 1, 5])
    full, c = enc.observe(ids, prompt_mask(3, 5), keep_rows=True)
    short, _ = enc.observe(ids[:3], keep_rows=True)
    for m in (1, 2, 3):
        assert np.allclose(short.last[m], full._rows[m][2])  # prefix features unchanged by later tokens
        assert np.allclose(full.span[m], full._rows[m][:3].mean(axis=0))
    assert c.full_forwards == 1 and full.encoder_version == 1 and full.base_hash == "fake"
    with pytest.raises(ValueError):
        enc.observe(ids, np.zeros(5, bool))
