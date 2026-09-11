#!/usr/bin/env python3
"""Verify approved B4 integration through its real canonical import on CPU.

Only the smoke output destination and the class instantiated by the smoke driver
are selected in memory. Production source and the independent scalar oracle are
loaded from disk unchanged.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402,F401
from pccap.baselines import grace_batch, grace_jax  # noqa: E402
from pccap.baselines.grace_adapter import GraceLearner  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/S2/grace_jax/batch_applied"


def main():
    assert not (OUT / "canonical_verification.json").exists()
    receipt = json.loads((OUT / "application.json").read_text())
    before = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in receipt["after"]}
    assert before == receipt["after"], "approved source changed before verification"
    assert GraceLearner is grace_jax.GraceLearner
    spec = importlib.util.spec_from_file_location("applied_grace_smoke", ROOT / "scripts/grace_batch_smoke.py")
    smoke = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(smoke)
    with patch.object(smoke, "OUT", OUT / "canonical_smoke.json"), patch.object(smoke, "BatchedGraceLearner", GraceLearner), patch.object(grace_batch, "last_logits_batch", wraps=grace_batch.last_logits_batch) as delegated:
        smoke.main()
        assert delegated.call_count == 1, "canonical learner did not delegate exactly one query batch"
        calls = delegated.call_count
    result = json.loads((OUT / "canonical_smoke.json").read_text())
    assert result["pass"] and len(result["cases"]) == 20 and result["prefixes"] == 61
    after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in receipt["after"]}
    assert before == after
    report = {
        "canonical_import_is_GraceLearner": True,
        "canonical_helper_calls": calls,
        "full_size_cases_passed": len(result["cases"]),
        "answer_prefixes": result["prefixes"],
        "maximum_logit_absolute_gap": max(r["max_abs_logit_gap"] for r in result["cases"]),
        "maximum_answer_nll_absolute_gap": max(r["nll_abs_gap"] for r in result["cases"]),
        "base_unchanged": result["base_unchanged"],
        "learner_unchanged": result["learner_unchanged"],
        "source_unchanged_during_verification": True,
        "source_before": before, "source_after": after,
        "gpu_seconds": 0,
        "scope": "canonical batch integration only; DEC-020 sensitivity prerequisite remains unmet",
    }
    with (OUT / "canonical_verification.json").open("x") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
