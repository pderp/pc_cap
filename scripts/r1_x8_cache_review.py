"""R1-X8: pure-CPU cache counterexamples and an unapplied repair proposal.

Uses source snapshots and small RecordStore objects. It never constructs a base
or runs a model forward, and never edits installed source files.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib
import json
import sys
import types
from pathlib import Path

import numpy as np

import pccap  # noqa: F401
from pccap.revision_v1.contracts import MemoryRecord

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "logs/r1_round9/source_snapshot"
MEMORY = "src/pccap/revision_v1/memory.py"
LEARNER = "src/pccap/revision_v1/learner.py"


def replace_once(source, before, after):
    if source.count(before) != 1:
        raise ValueError("repair context does not match exactly once")
    return source.replace(before, after)


def proposed_sources(memory, learner):
    memory = replace_once(
        memory,
        "    weights_bytes: int = 0",
        "    lexical_version: int = 0  # monotone invalidation epoch for support/active-set mutations\n    weights_bytes: int = 0",
    )
    memory = replace_once(
        memory,
        "        self._by_id[rec.record_id] = len(self.records) - 1\n        return rec",
        "        self._by_id[rec.record_id] = len(self.records) - 1\n        self.lexical_version += 1\n        return rec",
    )
    memory = replace_once(
        memory,
        "        del self._by_id[record_id]\n",
        "        del self._by_id[record_id]\n        self.lexical_version += 1\n",
    )
    learner = replace_once(
        learner,
        "version = (len(self.store.records), len(self.store.active_records()))",
        "version = (id(self.store), self.store.lexical_version)",
    )
    learner = replace_once(
        learner,
        "        self.store = candidate\n        self.reset_queries()",
        '        self.store = candidate\n        self.__dict__.pop("_df_cache", None)\n        self.reset_queries()',
    )
    learner = replace_once(
        learner,
        "recomputed when the store grows",
        "invalidated on store mutation and state restore",
    )
    return memory, learner


def modules(memory, learner):
    names = ("pccap.revision_v1.memory", "pccap.revision_v1.learner")
    old = {name: importlib.import_module(name) for name in names}
    built = []
    try:
        for name, source, path in zip(names, (memory, learner), (MEMORY, LEARNER), strict=True):
            module = types.ModuleType(name)
            module.__file__ = str(SNAPSHOT / path)
            sys.modules[name] = module
            exec(compile(source, module.__file__, "exec"), module.__dict__)
            built.append(module)
        return built
    finally:
        sys.modules.update(old)


def record(name, tokens, fact=None, revision=1):
    return MemoryRecord(
        name,
        fact or name,
        revision,
        0,
        np.ones(2, np.float32),
        np.zeros(2, np.float32),
        source_ids=np.asarray(tokens, np.int32),
    )


def fixture(memory_module, learner_module, sequences, df_max=2):
    # A shell sufficient for RecordStore export/import and the Python gate predicate.
    cap = learner_module.RevisionCap.__new__(learner_module.RevisionCap)
    cap.cfg = learner_module.RevisionConfig(rare_overlap_min=1, rare_df_max=df_max)
    cap.params_hash, cap.n_params = "synthetic-no-weights", 0
    cap.enc = types.SimpleNamespace(base_hash="synthetic-no-base", encoder_version=1)
    cap._sel = {}
    cap.store = memory_module.RecordStore(2, 2)
    for i, tokens in enumerate(sequences):
        cap.store.add(record(f"r{i}", tokens))
    return cap


def probe(memory_source, learner_source):
    mm, lm = modules(memory_source, learner_source)
    a = fixture(mm, lm, [[7], [8], [9]])
    first = a._rare_overlap(np.array([7]), np.array([7]))
    b = fixture(mm, lm, [[7], [7], [7]])
    a.import_state(b.export_state())
    imported = a._rare_overlap(np.array([7]), np.array([7]))
    c = fixture(mm, lm, [[7], [7], [9]])
    c._rare_overlap(np.array([7]), np.array([7]))
    c.store.remove("r2")
    c.store.add(record("replacement", [7]))
    replaced = c._rare_overlap(np.array([7]), np.array([7]))
    d = fixture(mm, lm, [[7], [8], [9]], df_max=1)
    d._rare_overlap(np.array([8]), np.array([8]))
    d.store.supersede("r0", record("new-r0", [8], fact="r0", revision=2))
    superseded = d._rare_overlap(np.array([8]), np.array([8]))
    d.store.remove("new-r0", restore="r0")
    rollback = d._rare_overlap(np.array([8]), np.array([8]))
    e = fixture(mm, lm, [[7], [8], [9]])
    before_bytes, before_hash = e.store.bytes(), e.state_hash()
    repeated = e._rare_overlap(np.array([7] * 100), np.array([7]))
    unrelated_with_token = e._rare_overlap(np.array([101, 102, 7, 103]), np.array([7]))
    return {
        "initial_rare_count": first,
        "same_count_import_overlap_expected_0": imported,
        "remove_add_same_count_overlap_expected_0": replaced,
        "supersession_overlap_expected_0": superseded,
        "rollback_overlap_expected_1": rollback,
        "one_rare_token_repeated_100_times": repeated,
        "otherwise_unrelated_token_sequence_containing_one_rare_token": unrelated_with_token,
        "state_byte_report_unchanged_after_df_cache_creation": before_bytes == e.store.bytes(),
        "state_hash_unchanged_after_df_cache_creation": before_hash == e.state_hash(),
        "cached_df_entries": len(e._df_cache[1]),
        "model_execution": False,
    }


def audit():
    original = [(SNAPSHOT / p).read_text() for p in (MEMORY, LEARNER)]
    fixed = proposed_sources(*original)
    before, after = probe(*original), probe(*fixed)
    for key in ("same_count_import_overlap_expected_0", "remove_add_same_count_overlap_expected_0"):
        if before[key] != 1 or after[key] != 0:
            raise AssertionError("cache counterexample/repair did not reproduce")
    for key, expected in (
        ("supersession_overlap_expected_0", 0),
        ("rollback_overlap_expected_1", 1),
        ("one_rare_token_repeated_100_times", 1),
    ):
        if before[key] != expected or after[key] != expected:
            raise AssertionError("control case failed")
    patch = "".join(
        "".join(
            difflib.unified_diff(
                a.splitlines(keepends=True),
                b.splitlines(keepends=True),
                fromfile="a/" + path,
                tofile="b/" + path,
            )
        )
        for path, a, b in zip((MEMORY, LEARNER), original, fixed, strict=True)
    )
    return {
        "task": "R1-X8",
        "source_snapshots_sha256": {
            p: hashlib.sha256(s.encode()).hexdigest()
            for p, s in zip((MEMORY, LEARNER), original, strict=True)
        },
        "reviewed_implementation": before,
        "proposed_repair_in_memory": after,
        "repair_applied_to_installed_files": False,
        "gpu_seconds": 0,
        "model_execution": False,
        "limitations": "predicate and store/snapshot semantics only; not a complete adversarial base-generation experiment",
        "patch": patch,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--patch", required=True, type=Path)
    args = ap.parse_args()
    for p in (args.output, args.patch):
        if p.exists() or not p.resolve().is_relative_to(ROOT):
            raise ValueError("new repository outputs only")
    result = audit()
    patch = result.pop("patch")
    with args.patch.open("x") as f:
        f.write(patch)
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
