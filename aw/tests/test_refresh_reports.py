"""Fresh-output, CPU and failure boundaries of the report orchestration."""

import json
import os
import subprocess
import sys

import pytest

from aw.refresh_report_steps import reader_number_line, reader_number_sheet
from aw.refresh_reports import DEPENDENCIES, difference, execute, ordered_steps


def test_dependency_closure_and_unknown_gpu_command():
    names = ordered_steps(["pc-reader", "pc-controls"])
    for name in names:
        assert all(names.index(d) < names.index(name) for d in DEPENDENCIES[name])
    assert "ht17" in names
    assert "deck" not in names
    with pytest.raises(ValueError, match="unknown"):
        ordered_steps(["train"])


@pytest.mark.parametrize("existing", ["output", "assets"])
def test_refuses_even_empty_existing_destination(tmp_path, existing):
    paths = {name: tmp_path / name for name in ("output", "assets")}
    paths[existing].mkdir()
    with pytest.raises(FileExistsError):
        execute(**paths, steps=["pc-matched"], root=tmp_path, inventory=lambda _: {})
    assert list(paths[existing].iterdir()) == []


def test_failure_is_recorded_and_dependents_never_run(tmp_path):
    called = []

    def launch(command, root, env, handle):
        called.append(command[command.index("--step") + 1])
        assert env["JAX_PLATFORMS"] == "cpu" and env["CUDA_VISIBLE_DEVICES"] == ""
        handle.write("synthetic failure\n")
        return 7

    out = tmp_path / "out"
    with pytest.raises(RuntimeError, match="failed"):
        execute(
            out,
            tmp_path / "assets",
            ["pc-reader"],
            root=tmp_path,
            inventory=lambda _: {},
            launch=launch,
        )
    record = json.loads((out / "refresh.json").read_text())
    assert called == ["ht17"]
    assert record["status"] == "failed"
    assert record["steps"][0]["returncode"] == 7
    assert "synthetic failure" in (out / "commands/ht17.log").read_text()


def test_change_detection_compares_previous_and_running_inputs(tmp_path):
    previous = tmp_path / "previous.json"
    previous.write_text(json.dumps({"input_hashes": {"gone": "a", "changed": "old", "same": "s"}}))
    inventories = iter(
        [
            {"changed": "new", "same": "s", "added": "x"},
            {"changed": "later", "same": "s", "added": "x"},
        ]
    )
    result = execute(
        tmp_path / "out",
        tmp_path / "assets",
        ["pc-matched"],
        previous=previous,
        root=tmp_path,
        inventory=lambda _: next(inventories),
        launch=lambda *args: 0,
    )
    assert result["changes_since_previous"] == dict(
        added=["added"], removed=["gone"], changed=["changed"]
    )
    assert result["changes_during_refresh"]["changed"] == ["changed"]
    assert result["status"] == "complete_with_input_changes"
    assert result["gpu_seconds"] == 0


def test_stable_inputs_and_outputs_have_finished_receipt(tmp_path):
    record = execute(
        tmp_path / "out",
        tmp_path / "assets",
        ["pc-matched"],
        root=tmp_path,
        inventory=lambda _: {"input": "hash"},
        launch=lambda *args: 0,
    )
    assert record["status"] == "complete"
    assert record["outputs_sha256"]
    assert difference(record["input_hashes"], record["input_hashes"]) == dict(
        added=[], removed=[], changed=[]
    )


def test_native_write_guard_preserves_existing_file(tmp_path):
    canonical = tmp_path / "canonical.txt"
    canonical.write_text("reviewed")
    output = tmp_path / "output"
    output.mkdir()
    code = """from pathlib import Path
import sys
from aw.refresh_report_steps import guard_writes
guard_writes([sys.argv[1]])
Path(sys.argv[1], 'allowed.txt').write_text('new')
try:
    Path(sys.argv[2]).write_text('bad')
except PermissionError:
    pass
else:
    raise AssertionError('canonical mutation allowed')
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(output), str(canonical)],
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert canonical.read_text() == "reviewed"
    assert (output / "allowed.txt").read_text() == "new"


def test_reader_sheet_requires_both_datasets_for_a_paired_seed():
    cells = [
        dict(rule=rule, seed=seed, dataset=dataset, status="complete")
        for rule in ("bp", "epc")
        for seed in range(3)
        for dataset in ("zsre", "counterfact")
    ]
    cells = [
        c
        for c in cells
        if c["rule"] == "bp" or c["seed"] == 0 or (c["seed"] == 1 and c["dataset"] == "zsre")
    ]
    report = dict(
        cells=cells,
        completed_evaluations=9,
        planned_evaluations=12,
        training_cost_ratios=[
            dict(epc_over_bp=102.1),
            dict(epc_over_bp=95.8),
            dict(epc_over_bp=None),
        ],
    )
    line = reader_number_line(report)
    assert "**9/12**" in line and "fully paired seeds: 0." in line
    assert "95.8–102.1×" in line and "No three-seed finding yet" in line
    report["training_cost_ratios"] = []
    assert "unavailable" in reader_number_line(report)
    sheet = reader_number_sheet(
        "- **PC-reader:** old\n[P] `old.json`\n", report, {"old.json": "new/report.json"}
    )
    assert "old.json" not in sheet and "new/report.json" in sheet
    with pytest.raises(ValueError, match="exactly one"):
        reader_number_sheet("no reader row", report, {})


def test_catalog_failure_leaves_a_failed_receipt(tmp_path, monkeypatch):
    from aw import reproduction_catalog

    monkeypatch.setattr(
        subprocess, "run", lambda *args, **kwargs: type("Result", (), {"returncode": 0})()
    )

    def fail(*args):
        raise ValueError("changed source")

    monkeypatch.setattr(reproduction_catalog, "build", fail)
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="changed source"):
        execute(out, tmp_path / "assets", ["pc-matched"], root=tmp_path, inventory=lambda _: {})
    record = json.loads((out / "refresh.json").read_text())
    assert record["status"] == "failed"
    assert record["phase"] == "catalog/output verification"
