"""CAP-01: deterministic radius-gated nearest retrieval (PDF F.1)."""

import numpy as np

from pccap.cap.bank import Bank


def mk(S=8, dk=4, d=3):
    return Bank(bank_id=1, capacity=S, key_dim=dk, value_dim=d)


def test_boundary_inclusive_and_nearest():
    b = mk()
    b.allocate(np.array([0, 0, 0, 0], np.float32), radius=1.0)
    b.allocate(np.array([2, 0, 0, 0], np.float32), radius=1.0)
    r = b.retrieve(np.array([1.0, 0, 0, 0], np.float32))  # exactly on both boundaries (dist 1.0)
    assert r.slot == 0 and r.candidates == 2  # tie in distance -> smallest id
    r = b.retrieve(np.array([1.25, 0, 0, 0], np.float32))
    assert r.slot == 1
    r = b.retrieve(np.array([3.5, 0, 0, 0], np.float32))
    assert r.slot == -1 and r.candidates == 0 and r.distance == float("inf")


def test_tie_smallest_id_regardless_of_allocation_order():
    b = mk()
    b.allocate(np.array([1, 1, 0, 0], np.float32), radius=5.0)  # id 0
    b.allocate(np.array([0, 0, 0, 0], np.float32), radius=5.0)  # id 1
    b.allocate(np.array([0, 0, 0, 0], np.float32), radius=5.0)  # id 2, duplicate key
    r = b.retrieve(np.zeros(4, np.float32))
    assert r.slot == 1


def test_zero_radius_exact_only():
    b = mk()
    key = np.array([0.1, 0.2, 0.3, 0.4], np.float32)
    b.allocate(key, radius=0.0)
    assert b.retrieve(key).slot == 0
    assert b.retrieve(key + np.float32(1e-7)).slot == -1
    assert b.retrieve(key.astype(np.float64) * 1.0).slot == 0  # same values after float32 cast


def test_zero_vector_query():
    b = mk()
    b.allocate(np.zeros(4, np.float32), radius=0.0)
    assert b.retrieve(np.zeros(4, np.float32)).slot == 0
    b2 = mk()
    assert b2.retrieve(np.zeros(4, np.float32)).slot == -1


def test_retrieval_identical_across_insertion_orders():
    rng = np.random.default_rng(0)
    keys = rng.standard_normal((6, 4)).astype(np.float32)
    queries = rng.standard_normal((20, 4)).astype(np.float32)
    ref = None
    for shuffle in range(100):
        perm = rng.permutation(6)
        b = mk()
        for i in perm:
            b.allocate(keys[i], radius=1.5, value=np.full(3, float(i), np.float32))
        got = []
        for q in queries:
            v, r = b.value_for(q)
            got.append((None if r.slot < 0 else float(v[0]), r.candidates))  # value identifies the key
        if ref is None:
            ref = got
        assert got == ref


def test_inactive_slots_never_fire():
    b = mk()
    s = b.allocate(np.zeros(4, np.float32), radius=10.0)
    b.release(s)
    assert b.retrieve(np.zeros(4, np.float32)).slot == -1
    assert b.free_slot() == 0
