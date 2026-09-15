"""R1-68b mutation tracking and durable batched phase evidence.

Development-only integration lives in r1_68b_dev_cell.py. Full state and immutable
input verification remain mandatory at checkpoints. No base execution here.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from dataclasses import fields
from pathlib import Path

from pccap.revision_v1.incremental_integrity import RecordDigestIndex
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.memory import RecordStore


def durable_directory(path):
    """Create a new directory chain and persist each link before recording work."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    missing, cursor = [], path
    while not cursor.exists():
        missing.append(cursor)
        cursor = cursor.parent
    for directory in reversed(missing):
        directory.mkdir()
        descriptor = os.open(directory.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def durable_json(path, value):
    path = Path(path)
    raw = (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    descriptor = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return {"path": str(path.resolve()), "sha256": hashlib.sha256(raw).hexdigest()}


class IndexedStore(RecordStore):
    """Intercept the complete current RecordStore mutation surface.

    Direct record/list/NumPy writes are unsupported and fail independent
    verification at the next checkpoint. No lexical-version dirty-bit shortcut.
    """

    @classmethod
    def attach(cls, learner):
        original = learner.store
        if type(original) not in (RecordStore, cls):
            raise TypeError("incremental integrity requires the audited RecordStore")
        store = cls(**{field.name: getattr(original, field.name) for field in fields(RecordStore)})
        store.owner = learner
        store.index = RecordDigestIndex()
        store.depth, store.dirty, store.mutations = 0, set(), []
        store.index.rebuild_after_restore(store.records, metadata=store.metadata())
        learner.store = store
        learner.__dict__.pop("_df_cache", None)
        learner.__dict__.pop("_lexw_cache", None)
        learner.reset_queries()
        return store

    def metadata(self):
        return {
            "dk": self.dk,
            "d_code": self.d_code,
            "ceiling_bytes": self.ceiling_bytes,
            "encoder_version": self.encoder_version,
            "index_version": self.index_version,
            "metric": self.metric,
            "weights_bytes": self.weights_bytes,
            "params_hash": self.owner.params_hash,
            "n_params": self.owner.n_params,
            "semantic_config": self.owner.semantic_config(),
        }

    def mutate(self, name, changed, operation):
        self.depth += 1
        self.dirty.update(changed)
        try:
            return operation()
        finally:
            self.depth -= 1
            if not self.depth:
                live = {record.record_id for record in self.records}
                self.index.update(
                    self.records, changed_ids=sorted(self.dirty & live), metadata=self.metadata()
                )
                self.mutations.append(
                    {
                        "method": name,
                        "changed": sorted(self.dirty & live),
                        "removed": sorted(self.dirty - live),
                    }
                )
                # Bounded current-phase inventory; callers drain it after each phase.
                self.dirty.clear()

    def add(self, record):
        return self.mutate("add", [record.record_id], lambda: super(IndexedStore, self).add(record))

    def supersede(self, old_id, new):
        return self.mutate(
            "supersede",
            [old_id, new.record_id],
            lambda: super(IndexedStore, self).supersede(old_id, new),
        )

    def remove(self, record_id, restore=None):
        return self.mutate(
            "remove",
            [record_id, *([restore] if restore is not None else [])],
            lambda: super(IndexedStore, self).remove(record_id, restore),
        )

    def set_code(self, record_id, code):
        return self.mutate(
            "set_code", [record_id], lambda: super(IndexedStore, self).set_code(record_id, code)
        )

    def set_delta(self, record_id, delta, delta_bytes_budget=True):
        return self.mutate(
            "set_delta",
            [record_id],
            lambda: super(IndexedStore, self).set_delta(record_id, delta, delta_bytes_budget),
        )

    def rebuild_keys(self, key_fn, encoder_version):
        return self.mutate(
            "rebuild_keys",
            [record.record_id for record in self.records],
            lambda: super(IndexedStore, self).rebuild_keys(key_fn, encoder_version),
        )

    def verify(self):
        self.validate()
        if self._by_id != {record.record_id: index for index, record in enumerate(self.records)}:
            raise RuntimeError("record lookup index differs from the complete inventory")
        return self.index.verify(self.records, metadata=self.metadata())


class IndexedAdapter:
    """Keep the original learner class/identity and legacy external state hashes."""

    def __init__(self, adapter):
        if type(adapter.learner) is not RevisionCap:
            raise TypeError("incremental profile is admitted only for exact RevisionCap")
        self.original = adapter
        IndexedStore.attach(adapter.learner)
        self.restored_mutations = []

    def __getattr__(self, name):
        return getattr(self.original, name)

    def tracked_store(self):
        store = self.original.learner.store
        if type(store) is not IndexedStore:
            raise RuntimeError("store replaced outside the audited import path")
        return store

    def root(self):
        return self.tracked_store().index.root()

    def verify(self):
        return self.tracked_store().verify()

    def drain_mutations(self):
        store = self.tracked_store()
        rows = [*self.restored_mutations, *store.mutations]
        self.restored_mutations.clear()
        store.mutations.clear()
        return rows

    def import_state(self, state):
        # Assay clone restores also pass here; retain their mutation evidence.
        store = self.tracked_store()
        self.restored_mutations.extend(store.mutations)
        store.mutations.clear()
        self.original.import_state(state)
        IndexedStore.attach(self.original.learner)
        self.restored_mutations.append({"method": "import_state", "changed": "full_rebuild"})

    def update_item(self, item):
        self.tracked_store()
        return self.original.update_item(item)


class DurablePhaseJournal:
    """Fsync a batch intent before work; bind completed batches with receipts.

    An unclosed intent or torn batch/receipt refuses automatic resume. Caught
    exceptions flush their charged phase records and are resumable. No estimate
    of unobserved GPU work is silently substituted for measured counters.
    """

    def __init__(self, directory, *, batch_edits=16):
        if type(batch_edits) is not int or batch_edits < 1:
            raise ValueError("positive integer batch_edits required")
        self.directory = Path(directory)
        durable_directory(self.directory)
        self.batch_edits = batch_edits
        self.pending, self.bindings = [], []
        self.intent, self.previous = None, None
        self.next_phase, self.edit_count = 0, 0

    def before_phase(self, label, ledger):
        if self.intent is None:
            self.intent = durable_json(
                self.directory / f"batch-{len(self.bindings):06d}.intent.json",
                {
                    "schema_version": 1,
                    "first_phase": self.next_phase,
                    "first_label": label,
                    "previous_sha256": self.previous,
                    "ledger_before": copy.deepcopy(ledger),
                    "incomplete_policy": "refuse automatic resume; resource spend not reconstructed",
                },
            )

    def add(self, record):
        if self.intent is None:
            raise RuntimeError("phase work has no durable intent")
        self.pending.append({"phase_index": self.next_phase, **copy.deepcopy(record)})
        self.next_phase += 1
        if record["phase"].startswith("immediate:"):
            self.edit_count += 1
            if self.edit_count >= self.batch_edits:
                self.flush()

    def flush(self):
        if self.intent is None:
            return
        if not self.pending:
            raise RuntimeError("open phase intent has no completed cost record")
        index = len(self.bindings)
        batch = durable_json(
            self.directory / f"batch-{index:06d}.json",
            {
                "schema_version": 1,
                "previous_sha256": self.previous,
                "intent": self.intent,
                "rows": self.pending,
            },
        )
        receipt = durable_json(
            self.directory / f"batch-{index:06d}.receipt.json",
            {
                "schema_version": 1,
                "batch": batch,
                "intent": self.intent,
                "previous_sha256": self.previous,
                "phases": len(self.pending),
            },
        )
        self.bindings.append(receipt)
        self.previous = receipt["sha256"]
        self.pending, self.intent, self.edit_count = [], None, 0

    def receipt(self):
        self.flush()
        return {
            "schema_version": 1,
            "directory": str(self.directory.resolve()),
            "batches": copy.deepcopy(self.bindings),
            "last_sha256": self.previous,
            "phases": self.next_phase,
        }

    @staticmethod
    def verify(directory, checkpoint=None):
        directory = Path(directory).resolve()
        paths = sorted(directory.glob("batch-*.receipt.json"))
        expected_names = {
            f"batch-{index:06d}{suffix}"
            for index in range(len(paths))
            for suffix in (".json", ".intent.json", ".receipt.json")
        }
        if {path.name for path in directory.iterdir()} != expected_names:
            raise ValueError(
                "incomplete journal: unclosed intent, torn batch, or unexpected file; resume refused"
            )
        previous, rows, bindings = None, [], []

        def read(binding, expected):
            path = Path(binding["path"]).resolve()
            if path != expected:
                raise ValueError("journal path/order mismatch")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
                raise ValueError("journal content hash mismatch")
            return json.loads(raw)

        for index, path in enumerate(paths):
            binding = {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            receipt = json.loads(path.read_bytes())
            batch = read(receipt["batch"], directory / f"batch-{index:06d}.json")
            intent = read(receipt["intent"], directory / f"batch-{index:06d}.intent.json")
            if (
                receipt["schema_version"] != 1
                or batch["schema_version"] != 1
                or intent["schema_version"] != 1
                or batch["intent"] != receipt["intent"]
                or any(doc["previous_sha256"] != previous for doc in (receipt, batch, intent))
                or intent["first_phase"] != len(rows)
                or not batch["rows"]
                or receipt["phases"] != len(batch["rows"])
            ):
                raise ValueError("journal chain/phase inventory mismatch")
            rows.extend(batch["rows"])
            previous = binding["sha256"]
            bindings.append(binding)
        if [row["phase_index"] for row in rows] != list(range(len(rows))):
            raise ValueError("journal phase indices not contiguous")
        if checkpoint is not None:
            count = len(checkpoint["batches"])
            if (
                checkpoint["schema_version"] != 1
                or checkpoint["directory"] != str(directory)
                or checkpoint["batches"] != bindings[:count]
                or checkpoint["last_sha256"] != (bindings[count - 1]["sha256"] if count else None)
            ):
                raise ValueError("checkpoint journal prefix mismatch")
            prefix_rows = []
            for binding in bindings[:count]:
                receipt = json.loads(Path(binding["path"]).read_bytes())
                prefix_rows.extend(json.loads(Path(receipt["batch"]["path"]).read_bytes())["rows"])
            if checkpoint["phases"] != len(prefix_rows):
                raise ValueError("checkpoint journal phase count mismatch")
        return rows


def phase_summary(rows):
    result = {}
    for row in rows:
        kind = row["phase"].split(":", 1)[0]
        item = result.setdefault(
            kind, {"count": 0, "errors": 0, "wall_seconds": 0.0, "operation_seconds": 0.0}
        )
        item["count"] += 1
        item["errors"] += row["status"] != "ok"
        item["wall_seconds"] += row["phase_wall_seconds"]
        item["operation_seconds"] += row["operation_seconds"]
    return result
