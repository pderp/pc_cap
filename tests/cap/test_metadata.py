"""CAP-02: 128-byte layout; use_count once per (slot, item); inference never increments; memory report."""

import numpy as np
import pytest

from pccap.cap import memory
from pccap.cap.bank import Bank
from pccap.cap.metadata import FLAG_LOSS_EMA, SLOT_BYTES, SLOT_DTYPE, MetadataView, UseTracker


def test_layout_is_128_bytes():
    assert SLOT_DTYPE.itemsize == 128 == SLOT_BYTES
    # documented field offsets
    offs = {n: SLOT_DTYPE.fields[n][1] for n in SLOT_DTYPE.names}
    assert offs["radius"] == 0 and offs["use_count"] == 4 and offs["created"] == 8 and offs["last_use"] == 16
    assert offs["last_target"] == 24 and offs["owner_digest"] == 28 and offs["version"] == 44
    assert offs["loss_ema"] == 48 and offs["active"] == 52 and offs["flags"] == 53 and offs["_pad"] == 54


def test_use_count_once_per_item_across_prefixes_and_rounds():
    b = Bank(1, capacity=4, key_dim=3, value_dim=2)
    s = b.allocate(np.zeros(3, np.float32), radius=1.0, digest=b"item-A")
    tr = UseTracker(b.metadata, capacity=4)
    tr.begin_item(b"item-A")
    for _prefix in range(3):  # three prefixes ...
        for _round in range(5):  # ... five rounds each touch the same slot
            tr.note_use(s)
    assert tr.end_item() == 1
    assert b.view().use_count(s) == 1
    tr.begin_item(b"item-B")
    tr.note_use(s)
    tr.end_item()
    assert b.view().use_count(s) == 2


def test_inference_cannot_increment():
    b = Bank(1, capacity=2, key_dim=3, value_dim=2)
    s = b.allocate(np.zeros(3, np.float32), radius=1.0)
    v: MetadataView = b.view()
    assert not any(n.startswith("set") or n.startswith("on_") or n == "note_use" for n in dir(v))
    ro = v.as_readonly_array()
    with pytest.raises(ValueError):
        ro["use_count"][s] = 5
    b.value_for(np.zeros(3, np.float32))  # a read
    assert v.use_count(s) == 0


def test_note_use_outside_item_or_over_capacity_raises():
    b = Bank(1, capacity=2, key_dim=3, value_dim=2)
    tr = UseTracker(b.metadata, capacity=2)
    with pytest.raises(RuntimeError):
        tr.note_use(0)
    tr.begin_item(b"x")
    tr.note_use(0)
    tr.note_use(1)
    with pytest.raises(RuntimeError):
        tr.note_use(2)
    tr.end_item()


def test_on_commit_metadata_and_loss_ema():
    b = Bank(1, capacity=2, key_dim=3, value_dim=2)
    s = b.allocate(np.zeros(3, np.float32), radius=0.5, created=7, digest=b"d1", version=1, target=42)
    md = b.metadata
    md.on_commit(s, target=43, digest=b"d2", version=2, item_index=9, pre_update_loss=2.0)
    md.on_commit(s, target=43, digest=b"d2", version=2, item_index=10, pre_update_loss=1.0)
    v = b.view()
    assert v.last_target(s) == 43 and v.version(s) == 2 and v.owner_digest(s).startswith(b"d2")
    assert b.meta["last_use"][s] == 10 and b.meta["created"][s] == 7
    assert abs(float(b.meta["loss_ema"][s]) - (0.8 * 2.0 + 0.2 * 1.0)) < 1e-6
    assert b.meta["flags"][s] & FLAG_LOSS_EMA
    with pytest.raises(ValueError):
        md.set_radius(s, -0.1)


def test_memory_report_formula():
    d, dk, S = 768, 768, 100
    b = Bank(3, capacity=S, key_dim=dk, value_dim=d)
    for i in range(10):
        b.allocate(np.full(dk, i, np.float32), radius=0.1)
    lay = memory.BankLayout.plan(3, memory.b_cap(d), dk, d, fixed_overhead=memory.measured_overhead(b))
    rep = memory.memory_report({3: b}, {3: memory.BankLayout(3, lay.ceiling_bytes, dk, d, lay.fixed_overhead, S)}, memory.b_cap(d))
    assert rep.allocated_bytes == S * (4 * dk + 4 * d + 128) + rep.index_bytes
    assert rep.occupied_bytes == 10 * (4 * dk + 4 * d + 128) + rep.index_bytes
    assert rep.per_bank[3]["within_ceiling"] and rep.occupancy[3] == 0.1
