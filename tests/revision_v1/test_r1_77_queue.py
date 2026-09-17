"""CPU queue checks; all test logs live under logs/r1_round18, never results/R1."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from scripts import r1_77_queue as q
from scripts.r1_75_development_matrix import population

from tests.revision_v1 import test_r1_68c_driver as driver_cases


class FixtureRoot:
    """In-memory path redirection for legacy driver tests, not a production switch."""

    def __init__(self, root, outputs):
        self.root, self.outputs = root, outputs
        self.parent = root.parent

    def __fspath__(self):
        return str(self.root)

    def __truediv__(self, value):
        if str(value) in ("results", "results/R1/stage4_dev_cells"):
            return self.outputs
        return self.root / value


def put(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
    return Path(path)


@pytest.fixture
def tiny(tmp_path, monkeypatch):
    outputs = tmp_path / "driver"
    proxy = FixtureRoot(q.ROOT, outputs)
    monkeypatch.setattr(q.driver, "ROOT", proxy)
    monkeypatch.setattr(q.driver, "OUTPUT_ROOT", outputs)
    monkeypatch.setattr(q.analysis, "ROOT", proxy)
    case = driver_cases.DriverTests(methodName="runTest")
    case.setUp()
    try:
        recipe, tok, _ = case.fixture("incremental")
        manifest = q.read(recipe)
        cell = {
            **manifest["cell"],
            "cell_id": q.analysis.coordinate_id(manifest["cell"]),
            "block_number": 1,
            "within_block_order": 1,
            "checkpoints": [1, 2],
            "manifest_sha256": q.sha(recipe),
            "code_sha256": manifest["code_sha256"],
            "payload_sha256": manifest["payload"]["sha256"],
            "adapter_identity": manifest["adapter_identity"],
            "population": population(q.read(manifest["payload"]["path"])),
            "result_dir": str(outputs / q.driver.cell_name(manifest, q.sha(recipe))),
            "ceilings": {"wall_seconds": 100.0},
            "admitted": False,
        }
        matrix = {"scope": "development", "cells": [cell]}
        mp = put(tmp_path / "matrix.json", matrix)
        bp = put(
            tmp_path / "bindings.json",
            {
                "matrix_sha256": q.sha(mp),
                "recipes": {cell["cell_id"]: {"path": str(recipe), "sha256": q.sha(recipe)}},
            },
        )

        def execute(binding, m, *, resume, output, pause=False):
            q.driver.run_development_cell(
                binding["path"],
                binding["sha256"],
                case.adapter(),
                tok,
                output_root=outputs,
                resource_root=case.resources / "queue-snapshots",
                resume=resume,
                stop_after_checkpoint=1 if pause else None,
            )
            return 0

        yield dict(
            matrix=matrix,
            mp=mp,
            bp=bp,
            cell=cell,
            execute=execute,
            receipts=tmp_path / "queue",
            outputs=outputs,
        )
    finally:
        case.doCleanups()


def run(tiny, **kw):
    return q.run_queue(
        tiny["mp"], tiny["bp"], receipt_root=tiny["receipts"], memory_reader=lambda: 8192.0, **kw
    )


def test_real_tiny_pause_resume_complete_and_skip_with_costs(tiny):
    calls = []

    def first(*args, **kw):
        calls.append(kw["resume"])
        return tiny["execute"](*args, **kw, pause=True)

    one = run(tiny, executor=first)
    assert one["status"] == "cell_incomplete_stop"
    assert one["inventory"]["incomplete_cells"][0]["missing_checkpoints"] == [2]
    two = run(tiny, executor=tiny["execute"])
    assert two["status"] == "selected_blocks_complete"
    assert two["inventory"]["complete_blocks"] == [1]
    assert two["inventory"]["cost"]["known_attempt_hours"] > 0
    assert len(two["inventory"]["queue"][0]["cost"]["attempts"]) == 2
    assert len(two["inventory"]["queue"][0]["cost"]["process_receipts"]) == 2
    three = run(tiny, executor=lambda *a, **k: pytest.fail("completed cell relaunched"))
    assert three["inventory"]["cost"] == two["inventory"]["cost"]
    assert calls == [False]


def test_memory_guard_prevents_model_construction(tiny):
    result = q.run_queue(
        tiny["mp"],
        tiny["bp"],
        receipt_root=tiny["receipts"],
        memory_reader=lambda: 1.0,
        executor=lambda *a, **k: pytest.fail("must not launch"),
    )
    assert result["status"] == "memory_guard_stop"
    assert not tiny["outputs"].exists()


def test_ceiling_guard_prevents_launch(tiny):
    result = run(tiny, ceiling_hours=0.001, executor=lambda *a, **k: pytest.fail("must not launch"))
    assert result["status"] == "budget_stop"


def test_recipe_drift_refused_before_executor(tiny, monkeypatch):
    actual = q.sha
    recipe_path = q.read(tiny["bp"])["recipes"][tiny["cell"]["cell_id"]]["path"]
    monkeypatch.setattr(q, "sha", lambda p: "f" * 64 if str(p) == recipe_path else actual(p))
    with pytest.raises(ValueError, match="identity mismatch"):
        run(tiny, executor=lambda *a, **k: pytest.fail("must not launch"))


def test_snapshot_corruption_refuses_resume_without_editing_fixture(tiny, monkeypatch):
    run(tiny, executor=lambda *a, **kw: tiny["execute"](*a, **kw, pause=True))
    actual = q.sha
    monkeypatch.setattr(q, "sha", lambda p: "0" * 64 if str(p).endswith(".snapshot") else actual(p))
    with pytest.raises(ValueError, match="snapshot identity"):
        run(tiny, executor=lambda *a, **k: pytest.fail("must not launch"))


def test_process_failure_cost_is_charged_before_any_driver_attempt(tiny):
    def fail(*a, **kw):
        raise RuntimeError("construction failed")

    result = run(tiny, executor=fail)
    assert result["status"] == "selected_blocks_processed_with_incomplete"
    inventory = q.inventory(
        tiny["matrix"], receipt_root=tiny["receipts"], matrix_hash=q.sha(tiny["mp"])
    )
    assert inventory["cost"]["known_attempt_hours"] > 0
    assert len(inventory["queue"][0]["cost"]["process_receipts"]) == 2
    assert inventory["queue"][0]["retry"]["exhausted"]


def test_lost_process_receipt_is_unknown_not_free(tiny):
    p = tiny["receipts"] / "interrupted"
    p.mkdir(parents=True)
    put(p / "start.json", {"cell_id": tiny["cell"]["cell_id"], "matrix_sha256": q.sha(tiny["mp"])})
    with pytest.raises(ValueError, match="unknown attempt costs"):
        run(tiny, executor=lambda *a, **k: pytest.fail("must not launch"))


def test_dec051_order_and_stop_boundary():
    m = q.read(q.ROOT / "manifests/revision_v1/run_matrix_v5.json")
    all_cells = q.ordered(m)
    assert len(all_cells) == 405
    assert [sum(c["block_number"] == b for c in all_cells) for b in range(1, 7)] == [
        45,
        45,
        90,
        90,
        90,
        45,
    ]
    assert len(q.ordered(m, 3)) == 180
    assert all(c["block_number"] <= 3 for c in q.ordered(m, 3))
    with pytest.raises(ValueError):
        q.ordered(m, 7)
    bad = copy.deepcopy(m)
    bad["cells"][1]["within_block_order"] = bad["cells"][0]["within_block_order"]
    with pytest.raises(ValueError, match="duplicate execution"):
        q.ordered(bad)


def test_final_draft_inventory_and_execution_firewall(tmp_path):
    m = q.read(q.ROOT / "manifests/revision_v1/run_matrix_v5.json")
    report = q.inventory(m)
    assert len(report["incomplete_cells"]) == 405 and report["complete_blocks"] == []
    assert report["cost"]["projected_total_hours"] is None
    scenario = q.inventory(m, fallback_cell_seconds=1000, ceiling_hours=306)
    assert scenario["cost"]["projected_total_hours"] == 112.5
    bindings = put(tmp_path / "final-bindings.json", {})
    with pytest.raises(
        PermissionError, match="explicit development or confirmatory matrix scope required"
    ):
        q.run_queue(
            q.ROOT / "manifests/revision_v1/run_matrix_v5.json",
            bindings,
            receipt_root=tmp_path / "never-launch",
        )


def test_saved_development_inventory_is_read_only():
    m = q.read(q.ROOT / "docs/tasks/R1-75-development.matrix.json")
    r = q.inventory(m)
    assert r["complete_blocks"] == [1] and not r["incomplete_cells"]
    assert all(x["observed"]["artifact_complete"] for x in r["queue"])
    assert r["cost"]["known_attempt_hours"] > 0


def test_memory_units_and_missingness(tmp_path):
    p = tmp_path / "meminfo"
    p.write_text("MemAvailable: 8192000 kB\n")
    assert q.memory_available_mib(p) == 8000
    empty = tmp_path / "empty"
    empty.write_text("MemFree: 100 kB\n")
    with pytest.raises(ValueError, match="MemAvailable missing"):
        q.memory_available_mib(empty)
