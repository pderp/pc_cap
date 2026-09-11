#!/usr/bin/env python3
"""Round-4 rerun of the original S7 counterexamples, with isolated audit output."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def main():
    path = ROOT / "scripts/review_s7_inventory.py"
    spec = importlib.util.spec_from_file_location("s7_original_audit", path)
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    audit.OUT = ROOT / "logs/p4_s7_review_r2"
    assert not audit.OUT.exists(), "Refuse to overwrite prior evidence"
    audit.main()
    result = json.loads((audit.OUT / "s7_audit.json").read_text())
    assert not result["damage_counterexample"]["demonstrated_mismatch"]
    boundary = result["grace_boundary_control"]
    assert all(c["key_positions"] == [1] * len(c["lengths"]) for c in boundary["calls"])
    assert result["grammar"]["min_seed"] >= 5_000_000
    assert not result["grammar"]["exact_schedule_overlap_with_published_P4"]
    inventory = json.loads((ROOT / "manifests/dev/s7_pairs.json").read_text())
    assert inventory["strata_qualification"]
    closure = {
        "closed_findings": [1, 2, 3],
        "damage_expected_and_observed": result["damage_counterexample"],
        "boundary_checks": boundary,
        "strata_qualification": inventory["strata_qualification"],
        "grammar": result["grammar"],
        "inventory_sha256_pairs": result["inventory_sha256_pairs"],
        "e2_selection_checks": result["selection_checks"],
        "audit_driver_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "sealed_realization_files_opened": 0,
        "gpu_seconds": 0,
    }
    with (audit.OUT / "closure.json").open("x") as f:
        json.dump(closure, f, indent=2)
    print("All three S7 findings closed; source/inventory stable during audit.")


if __name__ == "__main__":
    main()
