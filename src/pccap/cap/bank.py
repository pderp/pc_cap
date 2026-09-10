"""Fixed-capacity bank storage and deterministic retrieval (CAP-01/02; PDF F.1, F.2).

* keys ``[S, dk]`` and values ``[S, d]`` float32 NumPy arrays (host-side learner state, so
  snapshots are byte-exact) plus the packed 128-byte metadata record per slot
  (``cap.metadata.SLOT_DTYPE``): radius and the active flag are read from that record, so there
  is exactly one source of truth. Slot ids are implicit array indices (``0..S-1``), immutable,
  and cost no bytes.
* ``retrieve(q)``: among active slots with ``‖q − k_s‖₂ ≤ ρ_s + KEY_TOL`` (inclusive) return the
  nearest; ties → smallest id. ``KEY_TOL = 1e-4`` is the float32 key-equality tolerance (SD-18):
  keys are unit-scale, and the same residual computed through differently fused kernels (single
  call vs batched dispatch) differs by ~1e-5, so "exactly equal key" (zero radius) means equal
  within this tolerance; positive radii shift by 1e-4, far below the calibration grid's
  resolution. Implemented on arrays with ``lexsort``; no dict/set iteration order (PDF F.1).

Use counts, transactions, conflicts and eviction live in ``cap.metadata`` / ``cap.transaction``
(CAP-02/04); this module holds arrays and the read path, plus raw allocate/release used inside
transactions.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pccap.cap.metadata import NO_TARGET, SLOT_BYTES, MetadataView, SlotMetadata, new_meta

KEY_TOL = np.float32(1e-4)  # SD-18 float32 key-equality tolerance (unit-scale keys)


@dataclass
class Retrieval:
    slot: int  # -1 when nothing fires
    distance: float  # distance to the firing slot (inf when nothing fires)
    candidates: int  # number of active slots within their radius


class Bank:
    def __init__(self, bank_id: int, capacity: int, key_dim: int, value_dim: int, radius_default: float = 0.0):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.bank_id = int(bank_id)
        self.S = int(capacity)
        self.dk = int(key_dim)
        self.d = int(value_dim)
        self.radius_default = float(radius_default)
        self.keys = np.zeros((self.S, self.dk), np.float32)
        self.values = np.zeros((self.S, self.d), np.float32)
        self.meta = new_meta(self.S)
        self.metadata = SlotMetadata(self.meta)  # mutable access (learning path only)

    # ---------------------------------------------------------------- derived views
    @property
    def radii(self) -> np.ndarray:
        return self.meta["radius"]

    @property
    def active(self) -> np.ndarray:
        return self.meta["active"] == 1

    @property
    def ids(self) -> np.ndarray:
        return np.arange(self.S, dtype=np.int64)

    def view(self) -> MetadataView:
        return MetadataView(self.meta)

    # ---------------------------------------------------------------- read path
    def distances(self, q: np.ndarray) -> np.ndarray:
        q = np.asarray(q, np.float32).reshape(self.dk)
        diff = self.keys - q[None, :]
        return np.sqrt(np.sum(diff * diff, axis=1, dtype=np.float32)).astype(np.float32)

    def retrieve(self, q: np.ndarray) -> Retrieval:
        dist = self.distances(q)
        eligible = self.active & (dist <= self.meta["radius"] + KEY_TOL)
        n = int(eligible.sum())
        if n == 0:
            return Retrieval(slot=-1, distance=float("inf"), candidates=0)
        idx = np.flatnonzero(eligible)
        order = np.lexsort((idx, dist[idx]))  # primary: distance, secondary: id
        best = int(idx[order[0]])
        return Retrieval(slot=best, distance=float(dist[best]), candidates=n)

    def value_for(self, q: np.ndarray) -> tuple[np.ndarray, Retrieval]:
        """The additive correction for query ``q``: the firing slot's value, or zeros."""
        r = self.retrieve(q)
        if r.slot < 0:
            return np.zeros((self.d,), np.float32), r
        return self.values[r.slot].copy(), r

    # ---------------------------------------------------------------- write path (raw; CAP-04 wraps it)
    def free_slot(self) -> int:
        """Lowest inactive id, or -1 when full."""
        inactive = np.flatnonzero(self.meta["active"] == 0)
        return int(inactive[0]) if inactive.size else -1

    def occupancy(self) -> int:
        return int((self.meta["active"] == 1).sum())

    def is_full(self) -> bool:
        return self.occupancy() >= self.S

    def allocate(self, key: np.ndarray, radius: float | None = None, value: np.ndarray | None = None,
                 created: int = 0, digest: bytes = b"", version: int = 0, target: int = NO_TARGET) -> int:
        s = self.free_slot()
        if s < 0:
            raise RuntimeError("bank full; eviction is CAP-04's responsibility")
        self.keys[s] = np.asarray(key, np.float32).reshape(self.dk)
        self.values[s] = 0.0 if value is None else np.asarray(value, np.float32).reshape(self.d)
        self.metadata.on_allocate(s, self.radius_default if radius is None else float(radius), created, digest,
                                  version, target)
        return s

    def release(self, slot: int) -> None:
        self.keys[slot] = 0.0
        self.values[slot] = 0.0
        self.metadata.on_release(slot)

    # ---------------------------------------------------------------- bytes / snapshot
    def slot_bytes(self) -> int:
        return 4 * self.dk + 4 * self.d + SLOT_BYTES

    def array_bytes(self) -> dict[str, int]:
        return {"keys": self.keys.nbytes, "values": self.values.nbytes, "meta": self.meta.nbytes}

    def index_bytes(self) -> int:
        return 0  # slot ids are implicit; the correction index (CAP-04) reports its own bytes

    def arrays(self) -> dict[str, np.ndarray]:
        return {"keys": self.keys, "values": self.values, "meta": self.meta}

    def load_arrays(self, arrays: dict[str, np.ndarray]) -> None:
        for k in ("keys", "values", "meta"):
            src = arrays[k]
            dst = getattr(self, k)
            if src.shape != dst.shape or src.dtype != dst.dtype:
                raise ValueError(f"array {k}: shape/dtype mismatch {src.shape}/{src.dtype} vs {dst.shape}/{dst.dtype}")
            dst[...] = src
