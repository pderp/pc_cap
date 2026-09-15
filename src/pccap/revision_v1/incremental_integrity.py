"""R1-68 opt-in integrity components; caller retains admission and checkpoint resume.

The record digest is versioned and is NOT the legacy LearnerState SHA. Only an
explicit mutation inventory permits reuse. Full verification is mandatory at
checkpoints and after restore. Immutable-input checks are never cached here.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np

from pccap.harness.snapshot import restore, serialize
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.learner import RevisionCap


def record_digest(record):
    """All MemoryRecord dataclass fields, including inactive/superseded records."""
    from dataclasses import fields

    values = {}
    for field in fields(record):
        value = getattr(record, field.name)
        if isinstance(value, np.ndarray):
            value = {
                "dtype": value.dtype.str,
                "shape": list(value.shape),
                "sha256": hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest(),
            }
        elif isinstance(value, np.generic):
            value = value.item()
        values[field.name] = value
    return digest(values)


class RecordDigestIndex:
    """Hash only declared changed records; verify every leaf independently at a boundary.

    Callers MUST supply changed ids for code/delta/key writes and BOTH ids for a
    supersession. This API does not intercept direct NumPy writes or trust an
    epoch: RecordStore.lexical_version omits code/delta updates.
    """

    def __init__(self):
        self.leaves = {}
        self.order = []
        self.metadata = None
        self.records_hashed = 0

    def update(self, records, *, changed_ids, metadata):
        rows = {r.record_id: r for r in records}
        order = [r.record_id for r in records]
        if len(rows) != len(order):
            raise ValueError("duplicate record identity")
        changed = list(changed_ids)
        if len(changed) != len(set(changed)):
            raise ValueError("duplicate mutation identity")
        if not set(changed) <= set(rows):
            raise ValueError("unknown changed record")
        if not (set(rows) - set(self.leaves)) <= set(changed):
            raise ValueError("new record missing mutation event")
        leaves = {k: v for k, v in self.leaves.items() if k in rows}
        for rid in changed:
            leaves[rid] = record_digest(rows[rid])
        # Validate serialization before changing the live index.
        new_meta = copy.deepcopy(metadata)
        digest(new_meta)
        self.leaves, self.order, self.metadata = leaves, order, new_meta
        self.records_hashed += len(changed)
        return self.root()

    def root(self):
        return digest(
            {
                "schema": "record-digest-v1",
                "ordered_leaves": [[k, self.leaves[k]] for k in self.order],
                "metadata": self.metadata,
            }
        )

    def verify(self, records, *, metadata):
        rows = list(records)
        full = RecordDigestIndex()
        full.update(rows, changed_ids=[r.record_id for r in rows], metadata=metadata)
        if full.root() != self.root():
            raise RuntimeError("incremental record inventory differs from full recomputation")
        return self.root()

    def rebuild_after_restore(self, records, *, metadata):
        rows = list(records)
        self.leaves, self.order, self.metadata = {}, [], None
        self.update(rows, changed_ids=[r.record_id for r in rows], metadata=metadata)
        return self.verify(rows, metadata=metadata)


class PhaseJournal:
    """One immutable chained file per N edits, with individual phase records inside.

    Flush before writing the checkpoint report/receipt and on caught exceptions.
    A process kill can lose the current unreceipted batch; resume must replay from
    the last complete checkpoint and charge failed-attempt spend independently.
    """

    def __init__(self, directory, *, edits_per_file=16):
        if type(edits_per_file) is not int or edits_per_file < 1:
            raise ValueError("positive batch size required")
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=False)
        self.edits_per_file = edits_per_file
        self.pending = []
        self.previous = None
        self.chunks = []
        self.next_edit = 1

    def add_edit(self, index, *, edit, immediate):
        if type(index) is not int or index != self.next_edit:
            raise ValueError("contiguous per-attempt edit index required")
        row = copy.deepcopy({"index": index, "edit": edit, "immediate": immediate})
        digest(row)
        self.pending.append(row)
        self.next_edit += 1
        if len(self.pending) >= self.edits_per_file:
            self.flush()

    def flush(self):
        if not self.pending:
            return None
        doc = {"schema_version": 1, "previous_sha256": self.previous, "rows": self.pending}
        raw = (json.dumps(doc, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
        path = self.directory / f"batch-{len(self.chunks):06d}.json"
        with path.open("xb") as f:
            f.write(raw)
        binding = {"path": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest()}
        self.previous = binding["sha256"]
        self.chunks.append(binding)
        self.pending = []
        return binding

    def receipt(self):
        self.flush()
        return {
            "schema_version": 1,
            "batches": copy.deepcopy(self.chunks),
            "last_sha256": self.previous,
            "edits": self.next_edit - 1,
        }

    @staticmethod
    def verify(receipt, *, directory):
        root = Path(directory).resolve()
        previous = None
        rows = []
        for i, binding in enumerate(receipt["batches"]):
            path = Path(binding["path"]).resolve()
            if path.parent != root or path.name != f"batch-{i:06d}.json":
                raise ValueError("journal path/order mismatch")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
                raise ValueError("journal content mismatch")
            doc = json.loads(raw)
            if doc["schema_version"] != 1 or doc["previous_sha256"] != previous or not doc["rows"]:
                raise ValueError("journal chain mismatch")
            rows.extend(doc["rows"])
            previous = binding["sha256"]
        if previous != receipt["last_sha256"] or [r["index"] for r in rows] != list(
            range(1, receipt["edits"] + 1)
        ):
            raise ValueError("journal inventory mismatch")
        return rows


def read_only_immediate(adapter, assays, item, *, integrity_profile="full"):
    """Same immediate assay, without a clone/restore only for exact RevisionCap.

    Gate 4: test_learner_cpu.test_empty_memory_is_capoff_and_predict_is_pure,
    plus R1-68 populated-memory query and parity tests. Full hashes remain on both
    sides, so an unexpected mutation aborts before any checkpoint can be accepted.
    On error incremental callers must restore their last verified checkpoint;
    this helper never returns a successful row after an integrity failure.
    Query caches/counters are ephemeral; reset_queries preserves the old boundary.
    """
    if integrity_profile not in ("full", "incremental"):
        raise ValueError("unknown integrity profile")
    if integrity_profile == "incremental" and type(adapter.learner) is not RevisionCap:
        raise ValueError("no read-only gate for this learner; use full profile")
    before = adapter.state_hash()
    identity = adapter.identity()
    snapshot = adapter.export_state().clone() if integrity_profile == "full" else None
    try:
        row = assays.item(item)
        if adapter.state_hash() != before:
            raise RuntimeError("immediate query mutated persistent state")
        if adapter.identity() != identity:
            raise RuntimeError("immediate query mutated immutable parameters")
        return row
    finally:
        if snapshot is not None:
            adapter.import_state(snapshot)
            if adapter.state_hash() != before:
                raise RuntimeError("immediate restore mismatch")
        else:
            adapter.reset_queries()


def verified_checkpoint(adapter):
    """Full legacy hash plus independent serialization/restore equality."""
    state = adapter.export_state()
    expected = state.content_hash()
    blob = serialize(state)
    restored = restore(blob, expected_hash=expected)
    adapter.import_state(restored)
    if adapter.state_hash() != expected:
        raise RuntimeError("checkpoint restore mismatch")
    return {
        "state_sha256": expected,
        "snapshot_sha256": hashlib.sha256(blob).hexdigest(),
        "snapshot": blob,
    }
