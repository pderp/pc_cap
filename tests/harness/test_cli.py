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
    assert cfg["manifest_sha256"] and "deferred" in cfg["determinism"]  # the backend initializes only after the lease (R2-05)


def test_confirm_mode_refuses_without_frozen_manifest(tmp_path):
    """§4.5 rule 4 (R2-02): in confirm mode the freeze is checked first and the --manifest file (a sealed
    realization reference) is never opened by the CLI; the frozen-field validation applies to
    manifests/frozen.json itself (exercised in tests/harness/test_confirm_cli.py)."""
    m = tmp_path / "zsre_r0.json"
    m.write_text(json.dumps({"name": "t", "mode": "confirm", "stage": "S4", "seed": 1, "A": 0.1}))
    r = run("run", "--stage", "S4", "--arm", "C2", "--dataset", "zsre", "--manifest", str(m), "--mode", "confirm", "--dry-run")
    assert r.returncode == 2
    assert "requires manifests/frozen.json" in r.stderr


def test_status_subcommand():
    r = run("status")
    assert r.returncode == 0 and "STATUS.md written" in r.stdout
