"""PC-4 (PDF F.2, F.5): conflict transactions, revisions, eviction order, byte-exact rollback,
and the router's blindness to digests (SD-4)."""

import dataclasses
import random

import numpy as np

from pccap.cap.bank import Bank
from pccap.cap.transaction import BankState, Transaction, evict_one, resolve_write_target
from pccap.contracts import RevisionEvent, RoundContext

D16 = lambda s: s.encode().ljust(16, b"\0")  # noqa: E731


def make(cap=4, radius_default=1.0):
    b = Bank(1, capacity=cap, key_dim=3, value_dim=2, radius_default=radius_default)
    rng = random.Random(0)
    return BankState.new(b, rng_get=rng.getstate, rng_set=rng.setstate), rng


def test_distinct_key_conflict_preserves_old_and_keeps_radii_nonnegative():
    bs, _ = make()
    b = bs.bank
    s0 = b.allocate(np.array([0, 0, 0], np.float32), radius=1.0, digest=D16("a"), target=5)
    b.values[s0] = [1.0, 2.0]
    tx = Transaction(bs).begin()
    q = np.array([0.5, 0, 0], np.float32)  # fires slot 0 (dist 0.5 <= 1.0) with a different target
    wt = resolve_write_target(bs, q, target=9, item_digest=D16("b"), version=1, item_index=1, radius0=1.0)
    assert wt.allocated and wt.slot != s0 and not wt.rejected
    assert np.array_equal(b.keys[s0], [0, 0, 0]) and np.array_equal(b.values[s0], [1.0, 2.0])
    assert abs(float(b.radii[s0]) - 0.49 * 0.5) < 1e-6 and abs(float(b.radii[wt.slot]) - 0.49 * 0.5) < 1e-6
    assert (b.radii >= 0).all()
    assert b.retrieve(q).slot == wt.slot  # retrieval recomputed: new slot is nearest
    tx.commit()


def test_identical_key_ambiguity_rejects_and_preserves():
    bs, _ = make()
    b = bs.bank
    key = np.array([1, 0, 0], np.float32)
    s0 = b.allocate(key, radius=0.0, digest=D16("a"), target=5)
    b.values[s0] = [3.0, 3.0]
    tx = Transaction(bs).begin()
    wt = resolve_write_target(bs, key, target=6, item_digest=D16("b"), version=1, item_index=1, radius0=1.0)
    assert wt.rejected and wt.codes == ["ambiguous_key_conflict"]
    tx.rollback()
    assert b.occupancy() == 1 and np.array_equal(b.values[s0], [3.0, 3.0]) and b.view().last_target(s0) == 5


def test_newer_version_replaces_and_same_version_replays():
    bs, _ = make()
    b = bs.bank
    key = np.array([1, 0, 0], np.float32)
    s0 = b.allocate(key, radius=0.0, digest=D16("fact"), version=1, target=5)
    bs.cindex.add(D16("fact"), 1, s0)
    rev2 = RevisionEvent(fact_id="fact", version=2, previous_version=1, fact_digest=D16("fact"))
    tx = Transaction(bs).begin()
    wt = resolve_write_target(bs, key, target=7, item_digest=D16("fact"), version=2, item_index=3, radius0=1.0,
                              revision=rev2, correction_track=True)
    assert "revision_replaced" in wt.codes and wt.allocated and not wt.rejected
    assert not b.view().active(s0) and bs.cindex.versions(D16("fact")) == {2: [wt.slot]}
    tx.commit()
    # replay of the same version, same target: idempotent
    tx = Transaction(bs).begin()
    wt2 = resolve_write_target(bs, key, target=7, item_digest=D16("fact"), version=2, item_index=4, radius0=1.0,
                               revision=rev2, correction_track=True)
    assert not wt2.rejected and wt2.slot == wt.slot and not wt2.allocated
    # last_target already equals target -> ordinary write; a conflicting replay with same version -> replayed
    tx.commit()
    tx = Transaction(bs).begin()
    wt3 = resolve_write_target(bs, key, target=8, item_digest=D16("fact"), version=2, item_index=5, radius0=1.0,
                               revision=rev2, correction_track=True)
    assert wt3.rejected  # same version, different target: not a newer revision -> ambiguous
    tx.rollback()
    # off the correction track the revision metadata is ignored (SD-4)
    tx = Transaction(bs).begin()
    wt4 = resolve_write_target(bs, key, target=8, item_digest=D16("fact"), version=3, item_index=6, radius0=1.0,
                               revision=RevisionEvent("fact", 3, 2, D16("fact")), correction_track=False)
    assert wt4.rejected
    tx.rollback()


def test_failed_replacement_rolls_back_byte_exactly():
    bs, rng = make(cap=2)
    b = bs.bank
    b.allocate(np.array([0, 0, 0], np.float32), radius=1.0, digest=D16("a"), target=1)
    b.allocate(np.array([5, 5, 5], np.float32), radius=1.0, digest=D16("b"), target=2)
    bs.cindex.add(D16("a"), 1, 0)
    bs.tracker.begin_item(D16("x"))
    bs.tracker.note_use(0)
    rng.random()
    before = (b.keys.tobytes(), b.values.tobytes(), b.meta.tobytes(), bs.cindex.export(), bs.tracker.snapshot(), rng.getstate())
    tx = Transaction(bs).begin()
    wt = resolve_write_target(bs, np.array([0.3, 0, 0], np.float32), target=9, item_digest=D16("c"), version=1,
                              item_index=2, radius0=1.0)  # distinct-key conflict + eviction (bank full)
    assert wt.allocated and wt.evicted >= 0 and "evicted" in wt.codes
    b.values[wt.slot] += 1.0
    bs.tracker.note_use(wt.slot)
    rng.random()
    tx.rollback()
    after = (b.keys.tobytes(), b.values.tobytes(), b.meta.tobytes(), bs.cindex.export(), bs.tracker.snapshot(), rng.getstate())
    assert before == after
    bs.tracker.end_item()


def test_deterministic_eviction_order():
    bs, _ = make(cap=3)
    b = bs.bank
    for i in range(3):
        b.allocate(np.full(3, i, np.float32), radius=0.1, digest=D16(str(i)))
    b.meta["use_count"][:] = [2, 1, 1]
    b.meta["last_use"][:] = [5, 7, 3]
    assert evict_one(b, bs.cindex) == 2  # lowest use_count tie (1,1) -> oldest last_use (3)
    b.allocate(np.full(3, 9, np.float32), radius=0.1)  # reuses slot 2
    b.meta["use_count"][:] = [1, 1, 1]
    b.meta["last_use"][:] = [4, 4, 4]
    assert evict_one(b, bs.cindex) == 0  # full tie -> smallest id


def test_eviction_commits_only_with_a_write():
    bs, _ = make(cap=1)
    b = bs.bank
    b.allocate(np.zeros(3, np.float32), radius=0.0, digest=D16("a"), target=1)
    tx = Transaction(bs).begin()
    wt = resolve_write_target(bs, np.ones(3, np.float32), target=2, item_digest=D16("b"), version=1, item_index=1, radius0=0.5)
    assert wt.evicted == 0 and wt.allocated
    tx.rollback()  # the candidate write was rejected -> the eviction is undone
    assert b.view().active(0) and b.view().owner_digest(0).startswith(b"a")


def test_router_context_carries_no_slot_metadata():
    names = {f.name for f in dataclasses.fields(RoundContext)}
    assert names <= {"prefix_ids", "loss", "directions", "bank_scales", "rng_material", "permitted_banks", "position"}
    for forbidden in ("digest", "owner", "slot", "answer", "target", "version", "metadata"):
        assert not any(forbidden in n for n in names), names
