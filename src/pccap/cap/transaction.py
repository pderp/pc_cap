"""Transactions, conflicts, eviction and revisions (CAP-04; PDF F.2; PC-4; SD-4).

* ``Transaction``: ``begin()`` snapshots the bank arrays (keys, values, 128-byte metadata), the
  correction index, the per-item use set and an optional RNG state; ``rollback()`` restores all
  of them byte-exactly; ``commit()`` drops the snapshot. Candidates of one round are evaluated
  from the *same* begin-snapshot (``rollback`` keeps the transaction open).
* ``CorrectionIndex``: bounded map ``fact digest → {version: [slot, ...]}`` of active digests,
  counted in memory (``bytes()``).
* ``resolve_write_target``: F.2 conflict handling before a slot's value or key changes:
  - nothing fires → allocate (evicting when full: lowest ``use_count``, then oldest ``last_use``,
    then smallest id); eviction is inside the transaction so it commits only with the write;
  - the firing slot's last target equals the presented token (or is unset) → write there;
  - distinct keys (``d_qs > 0``) with a different target → old radius ← ``min(ρ_s, 0.49·d_qs)``,
    new slot with radius ``min(ρ_0, 0.49·d_qs)``; old key and value untouched; retrieval
    recomputed;
  - identical keys, incompatible targets: with a ``RevisionEvent`` for the same fact digest and a
    newer version → retire the older version's slots and allocate (``revision_replaced``); the
    same version already stored → ``revision_replayed`` (idempotent, no change); otherwise
    ``ambiguous_key_conflict`` → this bank is rejected, old memory preserved.
The router never sees any of this: ``RoundContext`` carries no slot metadata (test in
``tests/controls/test_pc4_conflict.py``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from pccap.cap.bank import Bank
from pccap.cap.metadata import NO_TARGET, UseTracker
from pccap.contracts import RevisionEvent
from pccap.harness.records import OutcomeCode

SHRINK = 0.49


class CorrectionIndex:
    """Active fact digests → versions → slots. Bounded by ``max_entries`` (the bank capacity)."""

    ENTRY_BYTES = 16 + 4 + 4  # digest, version, slot

    def __init__(self, max_entries: int):
        self.max_entries = int(max_entries)
        self._map: dict[bytes, dict[int, list[int]]] = {}

    def add(self, digest: bytes, version: int, slot: int) -> None:
        d = self._map.setdefault(digest, {})
        d.setdefault(int(version), [])
        if slot not in d[int(version)]:
            d[int(version)].append(int(slot))
        if self.entries() > self.max_entries:
            raise RuntimeError("correction index exceeded its bound")

    def remove_slot(self, slot: int) -> None:
        for digest in list(self._map):
            for v in list(self._map[digest]):
                if slot in self._map[digest][v]:
                    self._map[digest][v].remove(slot)
                if not self._map[digest][v]:
                    del self._map[digest][v]
            if not self._map[digest]:
                del self._map[digest]

    def versions(self, digest: bytes) -> dict[int, list[int]]:
        return {v: list(s) for v, s in self._map.get(digest, {}).items()}

    def entries(self) -> int:
        return sum(len(s) for d in self._map.values() for s in d.values())

    def bytes(self) -> int:
        return self.entries() * self.ENTRY_BYTES

    def export(self) -> dict[str, list]:
        return {dg.hex(): [[v, list(s)] for v, s in sorted(vs.items())] for dg, vs in sorted(self._map.items())}

    def load(self, data: dict[str, list]) -> None:
        self._map = {bytes.fromhex(k): {int(v): list(s) for v, s in vs} for k, vs in data.items()}

    def copy(self) -> "CorrectionIndex":
        c = CorrectionIndex(self.max_entries)
        c.load(self.export())
        return c


@dataclass
class BankState:
    """A bank plus its bookkeeping (what one transaction protects)."""

    bank: Bank
    cindex: CorrectionIndex
    tracker: UseTracker
    rng_get: Callable[[], Any] | None = None
    rng_set: Callable[[Any], None] | None = None

    @classmethod
    def new(cls, bank: Bank, rng_get=None, rng_set=None) -> "BankState":
        return cls(bank, CorrectionIndex(bank.S), UseTracker(bank.metadata, bank.S), rng_get, rng_set)

    def index_bytes(self) -> int:
        return self.cindex.bytes()


@dataclass
class Snapshot:
    keys: np.ndarray
    values: np.ndarray
    meta: np.ndarray
    cindex: dict
    tracker: tuple
    rng: Any


class Transaction:
    def __init__(self, bs: BankState):
        self.bs = bs
        self._snap: Snapshot | None = None
        self.codes: list[str] = []

    def begin(self) -> "Transaction":
        b = self.bs.bank
        self._snap = Snapshot(b.keys.copy(), b.values.copy(), b.meta.copy(), self.bs.cindex.export(),
                              self.bs.tracker.snapshot(), self.bs.rng_get() if self.bs.rng_get else None)
        self.codes = []
        return self

    @property
    def open(self) -> bool:
        return self._snap is not None

    def rollback(self) -> None:
        if self._snap is None:
            raise RuntimeError("no open transaction")
        b = self.bs.bank
        b.keys[...] = self._snap.keys
        b.values[...] = self._snap.values
        b.meta[...] = self._snap.meta
        self.bs.cindex.load(self._snap.cindex)
        self.bs.tracker.restore(self._snap.tracker)
        if self.bs.rng_set is not None:
            self.bs.rng_set(self._snap.rng)
        self.codes = []

    def commit(self) -> list[str]:
        if self._snap is None:
            raise RuntimeError("no open transaction")
        self._snap = None
        codes, self.codes = self.codes, []
        return codes


@dataclass
class WriteTarget:
    slot: int
    allocated: bool
    codes: list[str] = field(default_factory=list)
    evicted: int = -1
    shrunk_from: float | None = None
    rejected: bool = False


def evict_one(bank: Bank, cindex: CorrectionIndex) -> int:
    """Deterministic eviction: lowest use_count, then oldest last_use, then smallest id."""
    m = bank.meta
    act = np.flatnonzero(m["active"] == 1)
    if act.size == 0:
        raise RuntimeError("nothing to evict")
    order = np.lexsort((act, m["last_use"][act], m["use_count"][act]))
    s = int(act[order[0]])
    cindex.remove_slot(s)
    bank.release(s)
    return s


def _allocate(bs: BankState, key: np.ndarray, radius: float, item_digest: bytes, version: int, target: int,
              item_index: int, wt: WriteTarget) -> int:
    bank = bs.bank
    if bank.is_full():
        wt.evicted = evict_one(bank, bs.cindex)
        wt.codes.append(OutcomeCode.evicted.value)
    s = bank.allocate(key, radius=radius, created=item_index, digest=item_digest, version=version, target=target)
    bs.cindex.add(item_digest[:16], version, s)
    wt.allocated = True
    return s


def resolve_write_target(bs: BankState, q: np.ndarray, target: int, item_digest: bytes, version: int,
                         item_index: int, radius0: float, revision: RevisionEvent | None = None,
                         correction_track: bool = False) -> WriteTarget:
    """Decide which slot a candidate write for query ``q`` (target ``target``) may change.
    Must be called inside an open ``Transaction`` (the caller rolls back on rejection)."""
    bank = bs.bank
    q = np.asarray(q, np.float32)
    wt = WriteTarget(slot=-1, allocated=False)
    r = bank.retrieve(q)
    if r.slot < 0:
        wt.slot = _allocate(bs, q, radius0, item_digest, version, target, item_index, wt)
        return wt
    s = r.slot
    last = int(bank.meta["last_target"][s])
    if last == NO_TARGET or last == int(target):
        wt.slot = s
        return wt
    # conflict: firing slot has a different last target
    d_qs = float(np.linalg.norm(q - bank.keys[s]))
    if d_qs > 0.0:
        old = float(bank.meta["radius"][s])
        new_old = min(old, SHRINK * d_qs)
        bank.metadata.set_radius(s, max(new_old, 0.0))
        wt.shrunk_from = old
        wt.slot = _allocate(bs, q, min(radius0, SHRINK * d_qs), item_digest, version, target, item_index, wt)
        # retrieval recomputed by the caller's forward; nothing else changes on the old slot
        return wt
    # identical keys, incompatible targets
    owner = bytes(bank.meta["owner_digest"][s]).ljust(16, b"\0")  # NumPy S16 strips trailing NULs
    if correction_track and revision is not None and revision.fact_digest[:16].ljust(16, b"\0") == owner:
        stored = bs.cindex.versions(owner)
        if revision.version in stored and int(bank.meta["last_target"][s]) == int(target):
            wt.slot = s
            wt.codes.append(OutcomeCode.revision_replayed.value)
            return wt
        if all(v < revision.version for v in stored):
            for _v, slots in stored.items():
                for old_slot in slots:
                    bs.cindex.remove_slot(old_slot)
                    bank.metadata.retire(old_slot)
                    bank.release(old_slot)
            wt.slot = _allocate(bs, q, radius0, revision.fact_digest, revision.version, target, item_index, wt)
            wt.codes.append(OutcomeCode.revision_replaced.value)
            return wt
    wt.rejected = True
    wt.codes.append(OutcomeCode.ambiguous_key_conflict.value)
    return wt
