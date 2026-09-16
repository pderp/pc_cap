import functools
import types
from pathlib import Path

import pytest
from scripts import r1_77b_sealed_backend as backend

from tests.revision_v1.test_r1_77b_sealed_backend import (
    REPO,
    make,  # noqa: F401 -- shared fixture
    new_json,
)


def proposed_queue():
    source = (REPO / "scripts/r1_77_queue.py").read_text()
    patch = (REPO / "docs/tasks/R1-77b-queue-dispatch.patch").read_text()
    if "def verify_sealed_matrix(" in source:
        return source
    lines = source.splitlines(keepends=True)
    out = []
    cursor = 0
    import re

    for line in patch.splitlines(keepends=True):
        if line.startswith(("---", "+++")):
            continue
        if line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@", line)
            start = int(match[1]) - 1
            out.extend(lines[cursor:start])
            cursor = start
        elif line.startswith(" "):
            assert lines[cursor] == line[1:]
            out.append(lines[cursor])
            cursor += 1
        elif line.startswith("-"):
            assert lines[cursor] == line[1:]
            cursor += 1
        elif line.startswith("+"):
            out.append(line[1:])
    return "".join(out + lines[cursor:])


@pytest.fixture
def queue(monkeypatch, make):  # noqa: F811 -- pytest fixture
    mod = types.ModuleType("queue_proposed")
    mod.__file__ = str(REPO / "scripts/r1_77_queue.py")
    exec(compile(proposed_queue(), mod.__file__, "exec"), mod.__dict__)

    def change(m, f, p):
        m["ceilings"] = {"wall_seconds": 1000}

    f = make(change=change)
    monkeypatch.setattr(mod, "ROOT", backend.ROOT)
    monkeypatch.setattr(
        backend, "inspect_manifest", functools.partial(backend.inspect_manifest, code_root=REPO)
    )
    # Backend's explicit code_root=None from its own caller must still resolve to real code.
    original = backend.load_sealed_cell

    def load(*a, **kw):
        kw["code_root"] = REPO
        return original(*a, **kw)

    monkeypatch.setattr(backend, "load_sealed_cell", load)
    m = f["m"]
    directory = backend.OUTPUT_ROOT / backend.cell_name(m, f["binding"]["sha256"])
    c = {
        **m["cell"],
        "cell_id": mod.analysis.coordinate_id(m["cell"]),
        "block_number": 1,
        "within_block_order": 1,
        "result_dir": str(directory),
        "manifest_sha256": f["binding"]["sha256"],
        "checkpoints": m["checkpoints"],
        "admitted": True,
        "population": backend.planned_population(f["data"]),
        **{k: m[k] for k in ("adapter_identity", "code_sha256", "ceilings")},
        "payload_sha256": m["payload"]["sha256"],
    }
    matrix = {"schema_version": 1, "scope": "confirmatory", "cells": [c]}
    ref = new_json(f["root"] / "docs/tasks/matrix.json", matrix)
    binding = new_json(
        f["root"] / "docs/tasks/bindings.json",
        {
            "matrix_sha256": ref["sha256"],
            "recipes": {c["cell_id"]: {**f["binding"], "backend": backend.backend_binding()}},
        },
    )

    def run(executor):
        return mod.run_queue(
            ref["path"],
            binding["path"],
            receipt_root=f["root"] / "logs/queue",
            executor=executor,
            memory_reader=lambda: 100000,
        )

    return mod, f, run, matrix, binding


def test_partial_block_then_resume(queue):
    mod, f, run, matrix, binding = queue

    def pause(b, m, *, resume, output):
        f["execute"](resume=resume, stop_after_checkpoint=1)
        return 0

    r = run(pause)
    assert r["status"] == "cell_incomplete_stop"
    assert not r["inventory"]["blocks"][0]["complete"]

    def complete(b, m, *, resume, output):
        assert resume
        f["execute"](resume=resume)
        return 0

    r = run(complete)
    assert r["status"] == "selected_blocks_complete"
    assert r["inventory"]["blocks"][0]["complete"]
    assert r["inventory"]["queue"][0]["observed"]["scientific_admission"]
    assert r["inventory"]["cost"]["known_attempt_hours"] > 0


def test_backend_module_binding_refused(queue):
    mod, f, run, matrix, binding = queue
    import json

    bindings = json.loads(Path(binding["path"]).read_text())
    cell = matrix["cells"][0]
    bindings["recipes"][cell["cell_id"]]["backend"]["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="module/file"):
        mod.recipe_for(cell, bindings)


def test_wrong_declared_population_refused(queue):
    import json

    mod, f, run, matrix, binding = queue
    matrix["cells"][0]["population"]["paraphrase_counts"] = [9, 9]
    with pytest.raises(ValueError, match="population"):
        mod.verify_sealed_matrix(matrix, json.loads(Path(binding["path"]).read_text()))
