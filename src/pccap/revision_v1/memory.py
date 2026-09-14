"""Bounded record memory (design §memory; X0-06 gates).

Records are appended with immutable ids; a revision supersedes an older record (it stays, inactive, with
``superseded_by``) — nothing is overwritten. Retrieval is deterministic: ascending key distance, ties by created order
then id. Keys carry the encoder version that produced them; a query from another version is refused until
``rebuild_keys`` re-derives every key from the stored support prefixes. All persistent bytes are counted (keys, codes,
128-byte metadata per record, 4 bytes per stored source token, index) against a ceiling enforced on every insertion.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from pccap.harness.snapshot import LearnerState
from pccap.revision_v1.contracts import MemoryRecord, RetrievalCandidate

META_BYTES_PER_RECORD = 128
TOKEN_BYTES = 4
DEFAULT_CEILING = 64 * 1024 * 1024


class CapacityError(RuntimeError):
    pass


class KeyVersionMismatch(RuntimeError):
    pass


@dataclass
class RecordStore:
    dk: int
    d_code: int
    ceiling_bytes: int = DEFAULT_CEILING
    encoder_version: int = 1
    index_version: int = 0
    weights_bytes: int = 0  # R23-07: reusable weights count against the same persistent-state ceiling
    records: list[MemoryRecord] = field(default_factory=list)
    _by_id: dict[str, int] = field(default_factory=dict, repr=False)

    # ------------------------------------------------------------------ bytes
    def bytes(self) -> dict[str, int]:
        n = len(self.records)
        toks = sum(r.source_tokens for r in self.records)
        b = {"keys": n * self.dk * 4, "codes": n * self.d_code * 4, "metadata": n * META_BYTES_PER_RECORD, "tokens": toks * TOKEN_BYTES, "index": 0, "weights": int(self.weights_bytes)}
        b["total"] = sum(b.values())
        return b

    def _would_exceed(self, rec: MemoryRecord) -> bool:
        extra = self.dk * 4 + self.d_code * 4 + META_BYTES_PER_RECORD + rec.source_tokens * TOKEN_BYTES
        return self.bytes()["total"] + extra > self.ceiling_bytes

    # ------------------------------------------------------------------ mutation (adapt path only)
    def add(self, rec: MemoryRecord) -> MemoryRecord:
        if rec.record_id in self._by_id:
            raise ValueError(f"record id {rec.record_id!r} already exists (ids are immutable; use supersede)")
        if rec.key.shape != (self.dk,) or rec.code.shape != (self.d_code,):
            raise ValueError(f"shapes key {rec.key.shape} code {rec.code.shape} != ({self.dk},) ({self.d_code},)")
        if self._would_exceed(rec):
            raise CapacityError(f"adding {rec.record_id!r} would exceed the {self.ceiling_bytes}-byte ceiling")
        rec.key = np.ascontiguousarray(rec.key, np.float32)
        rec.code = np.ascontiguousarray(rec.code, np.float32)
        rec.created_order = len(self.records)
        self.records.append(rec)
        self._by_id[rec.record_id] = len(self.records) - 1
        return rec

    def supersede(self, old_id: str, new: MemoryRecord) -> MemoryRecord:
        old = self.get(old_id)
        if not old.active:
            raise ValueError(f"{old_id!r} is already inactive")
        if new.fact_id != old.fact_id:
            raise ValueError("a revision must keep the fact id")
        if new.revision_id <= old.revision_id:
            raise ValueError("a revision must carry a later revision id")
        added = self.add(new)
        old.active = False
        old.superseded_by = added.record_id
        return added

    def remove(self, record_id: str, restore: str | None = None) -> None:
        """Undo a failed insertion (R23-04): drop the record (it must be the newest) and reactivate ``restore`` if given."""
        rec = self.get(record_id)
        if rec is not self.records[-1]:
            raise ValueError("only the newest record can be removed")
        self.records.pop()
        del self._by_id[record_id]
        if restore is not None:
            old = self.get(restore)
            old.active, old.superseded_by = True, None

    def set_code(self, record_id: str, code: np.ndarray) -> None:
        """The only in-place change ``adapt`` may make to an existing record."""
        rec = self.get(record_id)
        if not rec.active:
            raise ValueError(f"{record_id!r} is inactive")
        code = np.asarray(code, np.float32)
        if code.shape != (self.d_code,) or not np.all(np.isfinite(code)):
            raise ValueError("code shape/finite check failed")
        rec.code = np.ascontiguousarray(code)

    # ------------------------------------------------------------------ read path
    def get(self, record_id: str) -> MemoryRecord:
        try:
            return self.records[self._by_id[record_id]]
        except KeyError as e:
            raise KeyError(record_id) from e

    def active_records(self) -> list[MemoryRecord]:
        return [r for r in self.records if r.active]

    metric: str = "dot"  # R23-10: the same score the reader trains with (q·k); "l2" kept for tests/diagnostics

    def retrieve(self, query_key: np.ndarray, k: int, query_version: int | None = None) -> list[RetrievalCandidate]:
        """Deterministic top-k over active records by the declared metric (dot product descending, the reader's training
        score; ties: created order, then id). ``distance`` reports the negative score for dot. Read-only."""
        if query_version is not None and query_version != self.encoder_version:
            raise KeyVersionMismatch(f"query encoder version {query_version} != store keys version {self.encoder_version}; rebuild_keys first")
        act = self.active_records()
        if not act or k <= 0:
            return []
        q = np.asarray(query_key, np.float32).reshape(self.dk)
        K = np.stack([r.key for r in act])
        if self.metric == "dot":
            d = -(K @ q).astype(np.float32)
        else:
            d = np.sqrt(np.sum((K - q[None, :]) ** 2, axis=1, dtype=np.float32))
        order = sorted(range(len(act)), key=lambda i: (float(d[i]), act[i].created_order, act[i].record_id))[:k]
        return [RetrievalCandidate(record_id=act[i].record_id, distance=float(d[i]), rank=r) for r, i in enumerate(order)]

    # ------------------------------------------------------------------ rebuild
    def rebuild_keys(self, key_fn: Callable[[np.ndarray], np.ndarray], encoder_version: int) -> dict[str, float]:
        """Re-derive every key (active or not) from its stored support prefix; refuse if any record lacks one."""
        missing = [r.record_id for r in self.records if r.source_ids is None]
        if missing:
            raise KeyVersionMismatch(f"{len(missing)} records have no stored support prefix; cannot rebuild: {missing[:3]}")
        moved = []
        for r in self.records:
            new = np.ascontiguousarray(key_fn(r.source_ids), np.float32).reshape(self.dk)
            moved.append(float(np.linalg.norm(new - r.key)))
            r.key = new
        self.encoder_version = int(encoder_version)
        self.index_version += 1
        return {"records": len(self.records), "key_shift_mean": float(np.mean(moved)) if moved else 0.0, "key_shift_max": float(np.max(moved)) if moved else 0.0}

    # ------------------------------------------------------------------ snapshot
    def export(self) -> LearnerState:
        n = len(self.records)
        arrays = {"keys": np.stack([r.key for r in self.records]) if n else np.zeros((0, self.dk), np.float32),
                  "codes": np.stack([r.code for r in self.records]) if n else np.zeros((0, self.d_code), np.float32),
                  "active": np.asarray([r.active for r in self.records], np.uint8),
                  "revision_id": np.asarray([r.revision_id for r in self.records], np.int64)}
        for r in self.records:
            if r.source_ids is not None:
                arrays[f"src/{r.record_id}"] = np.asarray(r.source_ids, np.int32)
        scalars = {"dk": self.dk, "d_code": self.d_code, "ceiling_bytes": self.ceiling_bytes, "encoder_version": self.encoder_version,
                   "index_version": self.index_version, "metric": self.metric,
                   "records": json.dumps([{"record_id": r.record_id, "fact_id": r.fact_id, "provenance": list(r.provenance), "superseded_by": r.superseded_by} for r in self.records])}
        return LearnerState(arrays=arrays, scalars=scalars)

    @classmethod
    def from_state(cls, st: LearnerState) -> "RecordStore":
        sc = st.scalars
        store = cls(dk=int(sc["dk"]), d_code=int(sc["d_code"]), ceiling_bytes=int(sc["ceiling_bytes"]), encoder_version=int(sc["encoder_version"]), index_version=int(sc["index_version"]), metric=str(sc.get("metric", "l2")))
        meta = json.loads(sc["records"])
        for i, mrec in enumerate(meta):
            src = st.arrays.get(f"src/{mrec['record_id']}")
            rec = MemoryRecord(record_id=mrec["record_id"], fact_id=mrec["fact_id"], revision_id=int(st.arrays["revision_id"][i]), created_order=i,
                               key=np.ascontiguousarray(st.arrays["keys"][i]), code=np.ascontiguousarray(st.arrays["codes"][i]), provenance=tuple(mrec["provenance"]),
                               source_ids=None if src is None else np.asarray(src, np.int32), active=bool(st.arrays["active"][i]), superseded_by=mrec["superseded_by"])
            store.records.append(rec)
            store._by_id[rec.record_id] = i
        return store

    def content_hash(self) -> str:
        return self.export().content_hash()
