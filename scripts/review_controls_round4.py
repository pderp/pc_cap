#!/usr/bin/env python3
"""Run CPU PC controls, including full PC-1, with a new output directory."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True
import pccap  # noqa: E402,F401

# isort: split
import pytest  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/S3/control_audit_round4"


class Evidence:
    def __init__(self):
        self.rows = []

    def pytest_collection_modifyitems(self, items):
        for item in items:
            if item.module.__name__.endswith("test_pc1_planted"):
                item.module.RESULTS = OUT

    def pytest_runtest_logreport(self, report):
        if report.when == "call" or report.failed:
            self.rows.append({"nodeid": report.nodeid, "phase": report.when,
                              "outcome": report.outcome, "duration": report.duration})


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    evidence = Evidence()
    args = ["-q", "tests/controls", "tests/cap/test_memory.py", "tests/known_answer/test_metrics.py",
            "-m", "not gpu", "--ignore=tests/controls/test_pc10_parity.py", "-p", "no:cacheprovider",
            "--basetemp=" + str(ROOT.parent / "assets/tmp/controls-round4")]
    code = pytest.main(args, plugins=[evidence])
    with (OUT / "run.json").open("x") as f:
        json.dump({"time_utc": datetime.now(timezone.utc).isoformat(), "arguments": args,
                   "exit_code": int(code), "gpu_seconds": 0, "results": evidence.rows}, f, indent=2)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
