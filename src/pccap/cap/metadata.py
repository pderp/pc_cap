"""Slot metadata: packed 128-byte records and use-count semantics (CAP-02; PDF F.2; SD-12).

Layout (little-endian, exactly 128 bytes per slot, ``SLOT_DTYPE.itemsize == 128``):

| field | type | bytes | meaning |
| --- | --- | --- | --- |
| radius | f32 | 4 | retrieval radius ρ_s (≥ 0) |
| use_count | u32 | 4 | successful training-item uses, at most once per (slot, item) |
| created | u64 | 8 | item index at allocation |
| last_use | u64 | 8 | item index of the last successful use |
| last_target | i32 | 4 | last target token id (−1 = none) |
| owner_digest | 16 B | 16 | owner-edit digest (fixed size; no text) |
| version | u32 | 4 | fact version (correction track) |
| loss_ema | f32 | 4 | optional pre-update-loss EMA (rate 0.2; off by default) |
| active | u8 | 1 | 1 = allocated |
| flags | u8 | 1 | bit 0: loss_ema valid; bit 1: retired by revision |
| _pad | 74 B | 74 | padding to 128 bytes (documented, always zero) |

The bank's retrieval reads ``radius`` and ``active`` straight from this array, so there is one
source of truth. ``UseTracker`` implements SD-12: a bounded per-item set of slots cleared at item
end; ``use_count`` increments at most once per (slot, item digest); inference never calls it.
``MetadataView`` is the read-only class handed to predict paths (no public setter).
"""

from __future__ import annotations

import numpy as np

SLOT_DTYPE = np.dtype(
    [
        ("radius", "<f4"),
        ("use_count", "<u4"),
        ("created", "<u8"),
        ("last_use", "<u8"),
        ("last_target", "<i4"),
        ("owner_digest", "S16"),
        ("version", "<u4"),
        ("loss_ema", "<f4"),
        ("active", "u1"),
        ("flags", "u1"),
        ("_pad", "V74"),
    ]
)
assert SLOT_DTYPE.itemsize == 128, SLOT_DTYPE.itemsize
SLOT_BYTES = SLOT_DTYPE.itemsize
FLAG_LOSS_EMA = 1
FLAG_RETIRED = 2
NO_TARGET = -1


def new_meta(S: int) -> np.ndarray:
    m = np.zeros((S,), dtype=SLOT_DTYPE)
    m["last_target"] = NO_TARGET
    return m


class MetadataView:
    """Read-only access for predict/evaluation paths. Deliberately has no setters."""

    def __init__(self, meta: np.ndarray):
        self.__meta = meta

    def radius(self, s: int) -> float:
        return float(self.__meta["radius"][s])

    def use_count(self, s: int) -> int:
        return int(self.__meta["use_count"][s])

    def last_target(self, s: int) -> int:
        return int(self.__meta["last_target"][s])

    def owner_digest(self, s: int) -> bytes:
        return bytes(self.__meta["owner_digest"][s]).ljust(16, b"\0")  # always 16 bytes

    def version(self, s: int) -> int:
        return int(self.__meta["version"][s])

    def active(self, s: int) -> bool:
        return bool(self.__meta["active"][s])

    def as_readonly_array(self) -> np.ndarray:
        v = self.__meta.view()
        v.flags.writeable = False
        return v


class SlotMetadata:
    """Mutable access, used only by the transaction/learning path (CAP-04/06/07)."""

    def __init__(self, meta: np.ndarray):
        self.meta = meta

    def view(self) -> MetadataView:
        return MetadataView(self.meta)

    def on_allocate(self, s: int, radius: float, created: int, digest: bytes, version: int, target: int) -> None:
        m = self.meta
        m["radius"][s] = np.float32(radius)
        m["use_count"][s] = 0
        m["created"][s] = created
        m["last_use"][s] = created
        m["last_target"][s] = target
        m["owner_digest"][s] = digest[:16].ljust(16, b"\0")
        m["version"][s] = version
        m["loss_ema"][s] = 0.0
        m["active"][s] = 1
        m["flags"][s] = 0

    def on_commit(self, s: int, target: int, digest: bytes, version: int, item_index: int,
                  pre_update_loss: float | None = None, ema_rate: float = 0.2) -> None:
        """Metadata update after a committed candidate (PDF F.3 step 7). Use count is NOT
        touched here; it goes through ``UseTracker`` (once per item)."""
        m = self.meta
        m["last_target"][s] = target
        m["owner_digest"][s] = digest[:16].ljust(16, b"\0")
        m["version"][s] = version
        m["last_use"][s] = item_index
        if pre_update_loss is not None:
            if m["flags"][s] & FLAG_LOSS_EMA:
                m["loss_ema"][s] = (1 - ema_rate) * m["loss_ema"][s] + ema_rate * pre_update_loss
            else:
                m["loss_ema"][s] = pre_update_loss
                m["flags"][s] |= FLAG_LOSS_EMA

    def on_release(self, s: int) -> None:
        self.meta[s] = np.zeros((), dtype=SLOT_DTYPE)
        self.meta["last_target"][s] = NO_TARGET

    def set_radius(self, s: int, radius: float) -> None:
        if radius < 0:
            raise ValueError("radius must be non-negative")
        self.meta["radius"][s] = np.float32(radius)

    def retire(self, s: int) -> None:
        self.meta["flags"][s] |= FLAG_RETIRED
        self.meta["active"][s] = 0


class UseTracker:
    """SD-12: ``use_count`` increments once per (slot, item). ``begin_item`` opens a bounded set
    (capacity ≤ number of slots); ``note_use`` records a successful use; ``end_item`` clears.
    Inference paths never hold a tracker."""

    def __init__(self, metadata: SlotMetadata, capacity: int):
        self.md = metadata
        self.capacity = int(capacity)
        self._item: bytes | None = None
        self._used: set[int] = set()

    @property
    def active(self) -> bool:
        return self._item is not None

    def begin_item(self, digest: bytes) -> None:
        if self._item is not None:
            raise RuntimeError("previous item not ended")
        self._item = digest
        self._used = set()

    def note_use(self, s: int) -> bool:
        """Returns True if this is the first successful use of slot ``s`` in the current item."""
        if self._item is None:
            raise RuntimeError("note_use outside an item")
        if s in self._used:
            return False
        if len(self._used) >= self.capacity:
            raise RuntimeError("per-item use set exceeded the bank capacity")
        self._used.add(s)
        self.md.meta["use_count"][s] += 1
        return True

    def end_item(self) -> int:
        n = len(self._used)
        self._used = set()
        self._item = None
        return n

    def snapshot(self) -> tuple[bytes | None, tuple[int, ...]]:
        return self._item, tuple(sorted(self._used))

    def restore(self, snap: tuple[bytes | None, tuple[int, ...]]) -> None:
        self._item, self._used = snap[0], set(snap[1])
