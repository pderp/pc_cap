"""S0-03: schema validation, frozen-manifest strictness."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from pccap.harness import schema

ROOT = Path(__file__).resolve().parents[2]


def frozen_ok():
    return {
        "name": "frozen-test", "mode": "confirm", "stage": "S4", "seed": 0,
        "code_commit": "abc", "env_lock_sha": "x", "pdf_sha": "y",
        "base_checkpoints": {"bp": "h"}, "tokenizer_rev": "r", "bank_sites": [3, 7, 11],
        "radii": {"bank": {}, "read": "h"}, "b_m": [1, 1, 1], "A": 0.1, "epsilon": 0.01, "R": 5,
        "tau_edit": 0.1, "byte_ceiling": 38535168, "slot_capacities": [2048, 2048, 2048],
        "cr_distribution": [1 / 3, 1 / 3, 1 / 3],
        "dataset_ids": {"zsre": "a", "counterfact": "b", "grammar": "c"},
        "realizations": [0, 1, 2], "order_seeds": [100, 101, 102, 103, 104],
        "cap_seed": 1, "router_seed": 2, "replay_seed": 3,
        "stream_lengths": {"zsre": 300, "counterfact": 300, "grammar_train_count": 256},
        "arms": ["C1", "C2", "CR"], "contrasts": [["C2", "C1"], ["C2", "CR"]],
        "primary_endpoint": "RET-GS", "margins": {"ret_gs": 0.02, "es": -0.02, "ls": -0.01},
        "interval": {"method": "paired-cluster-bootstrap", "draws": 10000, "level": 0.975},
        "checkpoints": [100, 300, 1000, 3000], "challenge_policy": "separate",
        "resource_rules": {"headroom": 0.25, "kappa": 1.0, "stop_boundary": "item"},
        "analysis_code_commit": "abc", "negative_case_interpretation": "text",
        "spec_defect_resolutions": ["SD-1"],
    }


def test_frozen_manifest_valid():
    schema.validate("manifest_frozen", frozen_ok())


@pytest.mark.parametrize("field", ["cr_distribution", "analysis_code_commit", "margins", "order_seeds"])
def test_frozen_manifest_missing_field_fails(field):
    m = frozen_ok()
    del m[field]
    errs = schema.errors("manifest_frozen", m)
    assert any(field in e for e in errs), errs
    assert field in schema.missing_frozen_fields(m)


def test_frozen_manifest_cannot_change_margins():
    m = frozen_ok()
    m["margins"]["ret_gs"] = 0.01
    assert schema.errors("manifest_frozen", m)


def test_dev_manifest_minimal():
    schema.validate("manifest_dev", {"name": "s0", "mode": "dev", "stage": "S0", "seed": 7})
    with pytest.raises(schema.SchemaError):
        schema.validate("manifest_dev", {"name": "s0"})


def test_metric_schema_rejects_nan_free_statuses():
    from pccap.contracts import metric

    schema.validate("metric", metric(0.5, units="fraction", numerator=1, denominator=2, n=2))
    schema.validate("metric", metric(None, units="fraction", status="undefined"))
    with pytest.raises(schema.SchemaError):
        schema.validate("metric", {"value": 1.0, "status": "weird"})


def test_cli_validate_tasks_and_assets(tmp_path):
    for f in ["manifests/tasks.json", "manifests/assets.json"]:
        r = subprocess.run([sys.executable, "-m", "pccap.harness.schema", "validate", str(ROOT / f)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    bad = tmp_path / "frozen.json"
    m = frozen_ok()
    del m["cap_seed"]
    bad.write_text(json.dumps(m))
    r = subprocess.run([sys.executable, "-m", "pccap.harness.schema", "validate", str(bad)],
                       capture_output=True, text=True)
    assert r.returncode == 2 and "cap_seed" in r.stderr
