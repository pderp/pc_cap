"""Two actual sealed TinyBase cells share queue cost, locks and a block barrier."""

from __future__ import annotations

import copy
import functools
import json
import threading
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import r1_77_queue as q
from scripts import r1_77b_sealed_backend as backend

from tests.revision_v1.test_r1_77b_sealed_backend import REPO, make, new_json  # noqa: F401


@pytest.fixture
def pair(make, monkeypatch):  # noqa: F811
    f = make(change=lambda m, frozen, data: m.update(ceilings={"wall_seconds": 100.0}))
    monkeypatch.setattr(q, "ROOT", backend.ROOT)
    monkeypatch.setattr(
        backend, "inspect_manifest", functools.partial(backend.inspect_manifest, code_root=REPO)
    )
    load = backend.load_sealed_cell

    def scoped_load(*a, **kw):
        kw["code_root"] = REPO
        return load(*a, **kw)

    monkeypatch.setattr(backend, "load_sealed_cell", scoped_load)
    manifests = [copy.deepcopy(f["m"]) for _ in range(3)]
    for i, m in enumerate(manifests):
        m["cell"]["order"] = str(i)
    population = new_json(
        f["resources"] / "joint-population.json",
        {
            "cells": {
                q.analysis.coordinate_id(m["cell"]): backend.planned_population(f["data"])
                for m in manifests
            }
        },
    )
    for m in manifests:
        m["population"] = population
    frozen_path = Path(f["m"]["freeze"]["path"])
    frozen = json.loads(frozen_path.read_text())
    frozen.update(
        population=population,
        recipe_contracts={
            q.analysis.coordinate_id(m["cell"]): backend.contract_digest(m) for m in manifests
        },
    )
    frozen_path.write_text(json.dumps(frozen, sort_keys=True) + "\n")
    cells, recipes = [], {}
    for i, m in enumerate(manifests):
        m["freeze"] = {"path": str(frozen_path), "sha256": q.sha(frozen_path)}
        b = new_json(f["root"] / f"docs/tasks/parallel-{i}.json", m)
        cid = q.analysis.coordinate_id(m["cell"])
        recipes[cid] = {**b, "backend": backend.backend_binding()}
        cells.append(
            dict(
                **m["cell"],
                cell_id=cid,
                block_number=1 if i < 2 else 2,
                within_block_order=i + 1 if i < 2 else 1,
                result_dir=str(backend.OUTPUT_ROOT / backend.cell_name(m, b["sha256"])),
                manifest_sha256=b["sha256"],
                checkpoints=m["checkpoints"],
                admitted=True,
                population=backend.planned_population(f["data"]),
                payload_sha256=m["payload"]["sha256"],
                **{k: m[k] for k in ("adapter_identity", "code_sha256", "ceilings")},
            )
        )
    matrix = dict(schema_version=1, scope="confirmatory", cells=cells)
    mp = new_json(f["root"] / "docs/tasks/parallel-matrix.json", matrix)
    bp = new_json(
        f["root"] / "docs/tasks/parallel-bindings.json",
        dict(matrix_sha256=mp["sha256"], recipes=recipes),
    )
    receipts = f["root"] / "logs/parallel-queue"

    def execute(binding, manifest, *, resume, output):
        def factory(m):
            cap, tok = f["factory"](m)
            return cap, copy.deepcopy(tok)

        backend.execute(
            binding["path"], binding["sha256"], code_root=REPO, factory=factory, resume=resume
        )
        return 0

    def run(**kwargs):
        args = dict(
            receipt_root=receipts,
            executor=execute,
            memory_reader=lambda: 100000,
            workers=2,
            stop_after=1,
        )
        args.update(kwargs)
        return q.run_queue(mp["path"], bp["path"], **args)

    return dict(
        f=f, cells=cells, matrix=matrix, mp=mp, bp=bp, receipts=receipts, run=run, execute=execute
    )


def test_two_tiny_cells_overlap_and_preserve_blocks_cost_and_skip(pair):
    barrier = threading.Barrier(2)
    active, peak, lock = set(), [], threading.Lock()

    def execute(b, m, **kw):
        with lock:
            active.add(m["cell"]["order"])
            peak.append(len(active))
        barrier.wait(timeout=20)
        result = pair["execute"](b, m, **kw)
        with lock:
            active.remove(m["cell"]["order"])
        return result

    r = pair["run"](executor=execute)
    assert max(peak) == 2 and r["status"] == "selected_blocks_complete"
    assert r["inventory"]["complete_blocks"] == [1]
    assert not Path(pair["cells"][2]["result_dir"]).exists()
    assert not r["inventory"]["cost"]["unknown_attempts"]
    starts = [json.loads(p.read_text()) for p in pair["receipts"].glob("*/start.json")]
    assert len(starts) == 2
    assert sorted(s["admitted_other_reservations_seconds"] for s in starts) == [0, 165]
    assert all(s["effective_wall_ceiling_seconds"] == pytest.approx(165) for s in starts)
    again = pair["run"](executor=lambda *a, **k: pytest.fail("completed cell relaunched"))
    assert again["inventory"]["cost"] == r["inventory"]["cost"]


@pytest.mark.parametrize("exception", [False, True])
def test_one_worker_fails_other_completes_and_every_envelope_is_charged(pair, exception):
    barrier = threading.Barrier(2)

    def execute(b, m, **kw):
        barrier.wait(timeout=20)
        if m["cell"]["order"] == "0":
            if exception:
                raise RuntimeError("synthetic worker failure")
            return 7
        return pair["execute"](b, m, **kw)

    if exception:
        with pytest.raises(RuntimeError, match="synthetic worker failure"):
            pair["run"](executor=execute)
    else:
        r = pair["run"](executor=execute)
        assert r["status"] == "cell_incomplete_stop" and r["exit_code"] == 7
    observed = q.inventory(
        pair["matrix"],
        stop_after=1,
        receipt_root=pair["receipts"],
        matrix_hash=pair["mp"]["sha256"],
        workers=2,
    )
    assert [r["observed"]["artifact_complete"] for r in observed["queue"]] == [False, True]
    assert len(list(pair["receipts"].glob("*/finish.json"))) == 2
    assert observed["cost"]["known_attempt_hours"] > 0 and not observed["cost"]["unknown_attempts"]
    resumed = pair["run"]()
    assert resumed["status"] == "selected_blocks_complete"
    assert len(list(pair["receipts"].glob("*/finish.json"))) == 3


def test_second_launch_requires_six_gib_and_drains_first(pair):
    readings = iter([100000, 6143])
    r = pair["run"](memory_reader=lambda: next(readings))
    assert r["status"] == "memory_guard_stop" and r["required_MiB"] == 6144
    assert [x["observed"]["artifact_complete"] for x in r["inventory"]["queue"]] == [True, False]
    assert len(list(pair["receipts"].glob("*/finish.json"))) == 1


def test_shared_reservation_defers_second_then_uses_actual_cost(pair):
    r = pair["run"](ceiling_hours=200 / 3600)
    assert r["status"] == "selected_blocks_complete"
    starts = [json.loads(p.read_text()) for p in pair["receipts"].glob("*/start.json")]
    assert all(s["admitted_other_reservations_seconds"] == 0 for s in starts)
    assert max(s["admitted_prior_charged_seconds"] for s in starts) > 0
    assert r["inventory"]["cost"]["known_attempt_hours"] < 200 / 3600


def test_scaled_ceiling_stops_before_launch_and_invalid_workers_refuse(pair):
    r = pair["run"](
        ceiling_hours=150 / 3600, executor=lambda *a, **k: pytest.fail("budget violated")
    )
    assert r["status"] == "budget_stop"
    for workers in (0, 3, True):
        with pytest.raises(ValueError, match="workers"):
            pair["run"](workers=workers)


def test_next_block_waits_for_both_workers(pair):
    barrier = threading.Barrier(2)
    completed, lock = set(), threading.Lock()

    def execute(b, m, **kw):
        order = m["cell"]["order"]
        if order in ("0", "1"):
            barrier.wait(timeout=20)
        else:
            with lock:
                assert completed == {"0", "1"}
        result = pair["execute"](b, m, **kw)
        with lock:
            completed.add(order)
        return result

    r = pair["run"](executor=execute, stop_after=None)
    assert r["status"] == "selected_blocks_complete"
    assert r["inventory"]["complete_blocks"] == [1, 2] and not r["inventory"]["incomplete_cells"]


def test_production_child_timeout_uses_effective_ceiling(pair, monkeypatch):
    binding = q.read(pair["bp"]["path"])["recipes"][pair["cells"][0]["cell_id"]]
    manifest = q.read(binding["path"])
    calls = []

    def subprocess_run(*args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(q.subprocess, "run", subprocess_run)
    out = pair["f"]["root"] / "logs/timeout-probe.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    assert q.launch(binding, manifest, resume=False, output=out, max_wall_seconds=165) == 0
    assert calls[0][1]["timeout"] == 165
    assert "scripts.r1_77b_sealed_backend" in calls[0][0][0]
