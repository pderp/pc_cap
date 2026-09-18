"""Real scheduler with a bounded synthetic executor; no base or GPU execution."""

import json
from types import SimpleNamespace

import pytest
from scripts import ht8_fidelity_watch as watch
from scripts import r1_77f_scheduler as scheduler


def harness(root, *, already_complete=False, watch_error=False):
    outputs = root / "results/cells"
    resources = root / "resources"
    cells = [
        dict(
            cell_id=f"id{i}",
            condition="synthetic",
            dataset="zsre",
            realization=0,
            order=i,
            block_number=1,
            within_block_order=i + 1,
            result_dir=str(outputs / f"cell{i}"),
            ceilings=dict(wall_seconds=10),
        )
        for i in range(3)
    ]
    complete = {c["cell_id"]: already_complete for c in cells}
    trace = []
    matrix = dict(
        scope="development", cells=cells, full_validation={}, fidelity_watch=watch.binding()
    )

    def save(path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    mp, bp = root / "matrix.json", root / "bindings.json"
    save(mp, matrix)
    save(bp, dict(matrix_sha256=watch.full.sha(mp)))

    def row(cell):
        return dict(
            cell_id=cell["cell_id"],
            observed=dict(
                status="complete" if complete[cell["cell_id"]] else "missing",
                artifact_complete=complete[cell["cell_id"]],
            ),
            cost=dict(known_attempt_wall_seconds=0, unknown_attempts=[]),
        )

    def inventory(*a, **kw):
        return dict(queue=[row(c) for c in cells], cost=dict(unknown_attempts=[]))

    def recipe(cell, bindings, **kw):
        return dict(path="synthetic", sha256="fixture"), dict(mode="development", cell=cell)

    def executor(b, manifest, **kw):
        cid = manifest["cell"]["cell_id"]
        trace.append((cid, "execute"))
        complete[cid] = True
        return 0

    def observe(matrix, cell, **kw):
        trace.append((cell["cell_id"], "certified"))
        return row(cell), {}

    def post(matrix, cell, bindings):
        cid = cell["cell_id"]
        assert complete[cid]
        assert (cid, "certified") in trace or (cid, "resume_verified") in trace
        trace.append((cid, "watch"))
        if watch_error:
            raise OSError("simulated watch disk error")
        return dict(
            status="updated", breaches=1, new_alerts=[dict(cell_id=cid)], admission_veto=False
        )

    ns = dict(
        ROOT=root,
        __file__=watch.__file__,
        sha=watch.full.sha,
        read=lambda p: json.loads(p.read_text()),
        validate_watch=watch.validate_queue_binding,
        worker_factor=lambda n: 1 if n == 1 else 1.15,
        launch=lambda *a: None,
        inventory=inventory,
        ordered=lambda *a: cells,
        recipe_for=recipe,
        observe_cell=observe,
        verify_resume=lambda c, m: trace.append((c["cell_id"], "resume_verified")),
        post_cell_watch=post,
        durable_json=save,
        driver=SimpleNamespace(
            OUTPUT_ROOT=outputs,
            RESOURCE_ROOT=resources,
            cell_name=lambda m, h: f"cell{m['cell']['order']}",
        ),
        sealed=SimpleNamespace(MODE="sealed"),
    )

    def run(workers=1):
        return scheduler.run_workers(
            ns,
            mp,
            bp,
            receipt_root=root / "logs/queue",
            stop_after=None,
            min_memory_mib=4096,
            ceiling_hours=None,
            executor=executor,
            memory_reader=lambda: 8192,
            workers=workers,
        )

    return run, trace


@pytest.mark.parametrize("workers", [1, 2])
def test_post_cell_after_certification_breach_does_not_stop(tmp_path, workers):
    run, trace = harness(tmp_path)
    out = run(workers)
    assert out["status"] == "selected_blocks_complete"
    assert sum(step == "watch" for _, step in trace) == 3
    decisions = [
        json.loads(p.read_text()) for p in (tmp_path / "logs/queue").glob("*/decision.json")
    ]
    assert len(decisions) == 3
    assert all(
        d["outcome"] == "complete" and d["fidelity_watch"]["breaches"] == 1 for d in decisions
    )
    starts = [json.loads(p.read_text()) for p in (tmp_path / "logs/queue").glob("*/start.json")]
    assert all(s["fidelity_watch_binding"] == watch.binding() for s in starts)


def test_already_completed_cells_are_backfilled_without_reexecution(tmp_path):
    run, trace = harness(tmp_path, already_complete=True)
    assert run()["status"] == "selected_blocks_complete"
    assert sum(step == "watch" for _, step in trace) == 3
    assert not any(step == "execute" for _, step in trace)


def test_technical_watch_failure_stops_dispatch_and_keeps_completion(tmp_path):
    run, trace = harness(tmp_path, watch_error=True)
    out = run()
    assert out["status"] == "fidelity_watch_error_stop"
    assert sum(step == "execute" for _, step in trace) == 1
    decision = json.loads(next((tmp_path / "logs/queue").glob("*/decision.json")).read_text())
    assert decision["outcome"] == "complete"
    assert decision["fidelity_watch"]["status"] == "error"
    assert not decision["fidelity_watch"]["admission_veto"]
