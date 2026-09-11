#!/usr/bin/env python3
"""Validate the prepared B4 edits in memory; do not apply them to repository files.

Run with PYTHONPATH=. and the CPU environment in the edit request. The source
files deliberately remain unchanged until the lead approves the three patches.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401
from pccap.baselines.grace_batch import last_logits_batch  # noqa: E402
from pccap.baselines.grace_jax import GraceLearner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/S2/grace_jax"


def candidate_module(path, name, replacements):
    source = path.read_text()
    for before, after in replacements:
        assert before in source
        source = source.replace(before, after)
    mod = types.ModuleType(name)
    mod.__file__ = str(path)
    exec(compile(source, str(path) + " [unapplied candidate]", "exec"), mod.__dict__)
    return mod


def main():
    result_path = OUT / "batch_candidate_check.json"
    assert not result_path.exists()
    watched = [ROOT / p for p in ("src/pccap/baselines/grace_jax.py", "src/pccap/baselines/grace_adapter.py", "tests/baselines/test_grace_batch.py", "scripts/grace_batch_smoke.py", "src/pccap/baselines/grace_batch.py")]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    tests = candidate_module(ROOT / "tests/baselines/test_grace_batch.py", "candidate_batch_tests", [
        ("learner.ledger.report()", "learner.ledger.totals()"),
        ("expected = scalar.last_logits_batch(seqs, key_positions=positions)", "expected = np.stack([scalar.predict(ids, key_position=pos, last_only=True) for ids, pos in zip(seqs, positions)])"),
    ])
    smoke = candidate_module(ROOT / "scripts/grace_batch_smoke.py", "candidate_batch_smoke", [
        ("expected = scalar.last_logits_batch(seqs, key_positions=boundaries)", "expected = np.stack([scalar.predict(ids, key_position=pos, last_only=True) for ids, pos in zip(seqs, boundaries)])"),
    ])
    smoke.OUT = OUT / "batch_smoke_candidate.json"
    passed = []
    # Same delegation as the prepared canonical-method patch.
    with patch.object(GraceLearner, "last_logits_batch", last_logits_batch):
        for trained in (False, True):
            tests.test_vmapped_logits_preserve_row_order_boundaries_and_state(trained)
            passed.append("numeric/state/ragged trained=" + str(trained))
        tests.test_batch_charges_every_sequence_to_requested_phase()
        passed.append("ledger charges")
        tests.test_invalid_boundaries_refuse_before_any_work_and_empty_batch_is_defined()
        passed.append("validation and empty batch")
        smoke.main()
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
    assert before == after
    result = {"scope": "in-memory validation of unapplied source/test edits; not a claim that checked-in tests passed", "passed": passed, "full_size_smoke": str(smoke.OUT.relative_to(ROOT)), "source_before": before, "source_after": after, "files_unchanged": True}
    with result_path.open("x") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
