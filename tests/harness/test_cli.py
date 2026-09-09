"""S0-03: the CLI validates manifests for its mode and exits non-zero listing missing fields."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*args):
    return subprocess.run([sys.executable, "-m", "pccap.cli", *args], capture_output=True, text=True)


def test_dev_manifest_dry_run(tmp_path):
    m = tmp_path / "dev.json"
    m.write_text(json.dumps({"name": "t", "mode": "dev", "stage": "S0", "seed": 1}))
    r = run("run", "--stage", "S0", "--arm", "C1", "--manifest", str(m), "--dry-run")
    assert r.returncode == 0, r.stderr
    cfg = json.loads(r.stdout)
    assert cfg["manifest_sha256"] and cfg["determinism"]["jax_default_matmul_precision"] == "highest"


def test_confirm_mode_refuses_missing_frozen_fields(tmp_path):
    m = tmp_path / "conf.json"
    m.write_text(json.dumps({"name": "t", "mode": "confirm", "stage": "S4", "seed": 1, "A": 0.1}))
    r = run("run", "--stage", "S4", "--arm", "C2", "--manifest", str(m), "--mode", "confirm", "--dry-run")
    assert r.returncode == 2
    assert "missing frozen field: cr_distribution" in r.stderr
    assert "missing frozen field: analysis_code_commit" in r.stderr


def test_status_subcommand():
    r = run("status")
    assert r.returncode == 0 and "STATUS.md written" in r.stdout
