"""S0-08: clone/serialize/restore byte-exact; strict resume; kill-and-resume determinism;
resource-stop rollback leaves the ledger total unchanged."""

import random

import numpy as np
import pytest

from pccap.cap.bank import Bank
from pccap.harness import snapshot as snap
from pccap.harness.ledger import Ledger


class MockLearner:
    """A learner whose decisions depend on arrays, counters, Python and NumPy RNG (like the cap)."""

    def __init__(self, seed=0):
        self.bank = Bank(1, capacity=8, key_dim=4, value_dim=2, radius_default=0.5)
        self.py = random.Random(seed)
        self.np = np.random.default_rng(seed)
        self.item_index = 0
        self.cindex = {}
        self.decisions = []

    def export_state(self) -> snap.LearnerState:
        arrs = {f"bank1/{k}": v.copy() for k, v in self.bank.arrays().items()}
        return snap.LearnerState(arrays=arrs, scalars={"item_index": self.item_index, "cfg": "abc"},
                                 correction_index=dict(self.cindex), use_tracker=(None, []),
                                 rng=snap.LearnerState.capture_rng(self.py, self.np))

    def import_state(self, st: snap.LearnerState) -> None:
        self.bank.load_arrays({k.split("/", 1)[1]: v for k, v in st.arrays.items() if k.startswith("bank1/")})
        self.item_index = st.scalars["item_index"]
        self.cindex = dict(st.correction_index)
        snap.LearnerState.apply_rng(st.rng, self.py, self.np)

    def run_item(self, ledger: Ledger, fail_midway=False):
        with ledger.call("learning", full_forwards=1):
            pass
        key = self.np.standard_normal(4).astype(np.float32)
        r = self.bank.retrieve(key)
        choice = self.py.choice([1, 2, 3])
        if r.slot < 0 and not self.bank.is_full():
            s = self.bank.allocate(key, digest=b"item%d" % self.item_index, created=self.item_index)
            self.bank.values[s] += choice
            self.cindex[f"item{self.item_index}"] = [1, s, 1]
        if fail_midway:
            raise RuntimeError("resource stop")
        self.item_index += 1
        d = (self.item_index, int(r.slot), choice, float(self.bank.values.sum()))
        self.decisions.append(d)
        return d


def test_clone_then_mutate_original_unchanged():
    L = MockLearner()
    L.run_item(Ledger())
    st = L.export_state()
    h = st.content_hash()
    c = st.clone()
    c.arrays["bank1/values"][:] = 99
    c.scalars["item_index"] = 42
    c.rng["python"][1][0] = 0
    assert st.content_hash() == h and c.content_hash() != h


def test_serialize_restore_roundtrip_equals_clone_hash(tmp_path):
    L = MockLearner(3)
    for _ in range(3):
        L.run_item(Ledger())
    st = L.export_state()
    blob = snap.serialize(st)
    back = snap.restore(blob)
    assert back.content_hash() == st.clone().content_hash() == st.content_hash()
    for k in st.arrays:
        assert np.array_equal(st.arrays[k].view(np.uint8), back.arrays[k].view(np.uint8))
    p = tmp_path / "learner.ckpt"
    snap.save(st, p)
    assert snap.load(p).content_hash() == st.content_hash()


def test_resume_refuses_on_mismatch(tmp_path):
    st = MockLearner().export_state()
    blob = snap.serialize(st)
    with pytest.raises(snap.SnapshotError):
        snap.restore(blob, expected_schema=99)
    with pytest.raises(snap.SnapshotError):
        snap.restore(blob, expected_hash="0" * 64)
    bad = bytearray(blob)
    bad[-1] ^= 0xFF  # corrupt the last array byte
    with pytest.raises(snap.SnapshotError):
        snap.restore(bytes(bad))
    with pytest.raises(snap.SnapshotError):
        snap.restore(b"nope")


def test_kill_and_resume_reproduces_decisions():
    straight = MockLearner(7)
    led = Ledger()
    ref = [straight.run_item(led) for _ in range(10)]
    a = MockLearner(7)
    first = [a.run_item(led) for _ in range(5)]
    blob = snap.serialize(a.export_state())  # "kill" here
    b = MockLearner(999)  # different seed: everything must come from the snapshot
    b.import_state(snap.restore(blob))
    rest = [b.run_item(led) for _ in range(5)]
    assert first + rest == ref


def test_resource_stop_restores_item_boundary_and_keeps_ledger():
    L = MockLearner(1)
    led = Ledger()
    L.run_item(led)
    L.run_item(led)
    before = L.export_state().content_hash()
    cost_before = led.totals()["learning"]["full_forwards"]
    with pytest.raises(RuntimeError):
        with snap.ItemGuard(L, led) as guard:
            L.run_item(led, fail_midway=True)  # allocated a slot, then stopped
            guard.commit()
    assert guard.rolled_back
    assert L.export_state().content_hash() == before  # pre-item state incl. RNG and arrays
    assert led.totals()["learning"]["full_forwards"] == cost_before + 1  # cost charged, not rolled back
    with snap.ItemGuard(L, led) as guard:
        L.run_item(led)
        guard.commit()
    assert not guard.rolled_back and L.item_index == 3


def test_hash_covers_every_field():
    base = MockLearner(2).export_state()
    h = base.content_hash()
    for mut in (
        lambda s: s.arrays["bank1/keys"].__setitem__((0, 0), 1.0),
        lambda s: s.arrays["bank1/meta"]["use_count"].__setitem__(0, 1),
        lambda s: s.scalars.__setitem__("item_index", 5),
        lambda s: s.correction_index.__setitem__("x", [1, 2, 3]),
        lambda s: setattr(s, "use_tracker", ("ab", [1])),
        lambda s: s.rng["numpy"]["state"].__setitem__("pos", 3),
        lambda s: s.rng["python"][1].__setitem__(5, 0),
    ):
        c = base.clone()
        mut(c)
        assert c.content_hash() != h
