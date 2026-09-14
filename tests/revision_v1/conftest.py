"""Keep the historical R1-26 counterexample suite bound to the source it audited.

These eight controls include strict expected failures and extract a particular
version of the driver's AST. Ordinary current-core regression tests remain active.
A successor repair requires a successor audit, not reinterpretation of old probes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def pytest_collection_modifyitems(items):
    historical = [item for item in items if item.path == Path(__file__).with_name("test_r1_26_boundary_audit_cpu.py")]
    if not historical:
        return
    evidence = json.loads((ROOT / "logs/r1_round4/r1_26_controls.json").read_text())
    changed = [name for name, expected in evidence["sources_after"].items()
               if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected]
    if changed:
        marker = pytest.mark.skip(reason="historical R1-26 controls superseded by changed core/driver sources; see docs/tasks/R1-X3-response.md and run the successor audit")
        for item in historical:
            item.add_marker(marker)
