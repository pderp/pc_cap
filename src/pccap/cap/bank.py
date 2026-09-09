"""Fixed-capacity bank storage and deterministic retrieval (CAP-01; PDF F.1).

* keys ``[S, dk]`` and values ``[S, d]`` float32 NumPy arrays (host-side learner state, so
  snapshots are byte-exact); immutable slot ids ``0..S-1``; ``active`` mask; radii ``[S]``.
* ``retrieve(q)``: among active slots with ``‖q − k_s‖₂ ≤ ρ_s`` (inclusive) return the nearest;
  ties → smallest id; a zero radius fires only on an exactly equal key (``‖q − k‖ = 0`` in
  float32 arithmetic iff ``q == k`` elementwise). Implemented on sorted arrays; no dict/set
  iteration order is involved (PDF F.1 "distance and tie rules must not depend on unordered
  containers").

Metadata, use counts, transactions and eviction live in ``cap.metadata`` / ``cap.transaction``
(CAP-02/04); this module only holds arrays and the read path.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


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
        self.radii = np.zeros((self.S,), np.float32)
        self.active = np.zeros((self.S,), bool)
        self.ids = np.arange(self.S, dtype=np.int64)  # immutable

    # ---------------------------------------------------------------- read path
    def distances(self, q: np.ndarray) -> np.ndarray:
        q = np.asarray(q, np.float32).reshape(self.dk)
        diff = self.keys - q[None, :]
        return np.sqrt(np.sum(diff * diff, axis=1, dtype=np.float32)).astype(np.float32)

    def retrieve(self, q: np.ndarray) -> Retrieval:
        dist = self.distances(q)
        eligible = self.active & (dist <= self.radii)
        n = int(eligible.sum())
        if n == 0:
            return Retrieval(slot=-1, distance=float("inf"), candidates=0)
        idx = np.flatnonzero(eligible)
        order = np.lexsort((self.ids[idx], dist[idx]))  # primary: distance, secondary: id
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
        inactive = np.flatnonzero(~self.active)
        return int(inactive[0]) if inactive.size else -1

    def occupancy(self) -> int:
        return int(self.active.sum())

    def is_full(self) -> bool:
        return self.occupancy() >= self.S

    def allocate(self, key: np.ndarray, radius: float | None = None, value: np.ndarray | None = None) -> int:
        s = self.free_slot()
        if s < 0:
            raise RuntimeError("bank full; eviction is CAP-04's responsibility")
        self.keys[s] = np.asarray(key, np.float32).reshape(self.dk)
        self.values[s] = 0.0 if value is None else np.asarray(value, np.float32).reshape(self.d)
        self.radii[s] = self.radius_default if radius is None else float(radius)
        self.active[s] = True
        return s

    def release(self, slot: int) -> None:
        self.active[slot] = False
        self.keys[slot] = 0.0
        self.values[slot] = 0.0
        self.radii[slot] = 0.0

    # ---------------------------------------------------------------- bytes / snapshot
    def array_bytes(self) -> dict[str, int]:
        return {"keys": self.keys.nbytes, "values": self.values.nbytes, "radii": self.radii.nbytes,
                "active": self.active.nbytes, "ids": self.ids.nbytes}

    def arrays(self) -> dict[str, np.ndarray]:
        return {"keys": self.keys, "values": self.values, "radii": self.radii, "active": self.active}

    def load_arrays(self, arrays: dict[str, np.ndarray]) -> None:
        for k in ("keys", "values", "radii", "active"):
            src = arrays[k]
            dst = getattr(self, k)
            if src.shape != dst.shape or src.dtype != dst.dtype:
                raise ValueError(f"array {k}: shape/dtype mismatch {src.shape}/{src.dtype} vs {dst.shape}/{dst.dtype}")
            dst[...] = src
