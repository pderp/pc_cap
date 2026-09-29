"""CPU tests: actual native stream/checkpoints, payload admission and queue bounds."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import json
import uuid
from pathlib import Path

import pytest
from scripts import r1_68f_full_validation as fv
from tests.revision_v1 import test_r1_68f_full_validation as validation_cases
from tests.revision_v1.test_r1_77b_sealed_backend import make  # noqa: F401
from tests.revision_v1.test_stage4_cell import payload

from aw import r_run as r


def test_production_plan_and_exact_ceiling_factor():
    p = r.plan(validate_payloads=True)
    assert p["cells"] == 30 and p["workers"] == 2 and p["model_calls"] == 0
    assert p["projected_process_hours"] == pytest.approx(38.0302870392)
    assert p["summed_cell_ceiling_hours"] == pytest.approx(64.6514879666)
    assert p["ceiling_schedule"]["wall_hours"] > 30
    assert not p["launch_authorized"] and not p["primary_inference_inclusion"]
    m = r.matrix()
    c = copy.deepcopy(m["cells"][0])
    c["ceilings"]["wall_seconds"] *= 1.7
    with pytest.raises(ValueError, match="identity differs"):
        r.recipe(c, m)


def test_source_or_nonmember_recipe_refused(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{}")
    with pytest.raises(ValueError, match="30 prepared"):
        r.load(path, r.native.sha(path), allow_sealed=True)
    with pytest.raises(PermissionError):
        r.load(path, r.native.sha(path))


def test_native_tiny_engine_full_validation_and_checkpoint_resume(make, monkeypatch):  # noqa: F811
    # Synthetic cadence/population exception only in this isolated CPU process.
    tag = uuid.uuid4().hex
    paths = (
        r.ROOT.parent / "assets/test_scratch/aw-r" / tag,
        r.ROOT / "logs/additional_work/R/cpu-smoke" / tag,
    )
    for p in paths:
        p.mkdir(parents=True)
    tiny, definition, _ = validation_cases.fixture(paths)
    validate = fv.validate_spec
    monkeypatch.setattr(fv, "validate_spec", lambda m: validate(dict(m, test_fixture=True)))
    data = payload(2, composition=True)
    data["endpoints"]["drift"] = definition
    f = make(data_override=data)
    original_loader = r.native.load_sealed_cell

    def loader(path, sha, **kw):
        m, p = original_loader(path, sha, **kw)
        return dict(m, mode=r.MODE, full_validation=tiny["full_validation"]), p

    output = f["root"] / "results/additional_work/R"
    fn = r.engine(loader, output_root=output)
    cap, tok = f["factory"](None)
    args = (f["binding"]["path"], f["binding"]["sha256"], cap, tok)
    kwargs = dict(
        output_root=output,
        resource_root=f["resources"] / "supplemental",
        code_root=r.ROOT,
        allow_sealed=True,
    )
    first = fn(*args, **kwargs, stop_after_checkpoint=1)
    assert first["status"] == "paused_at_checkpoint" and first["mode"] == r.MODE
    cap, tok = f["factory"](None)
    result = fn(*args[:2], cap, tok, **kwargs, resume=True)
    assert result["status"] == "complete" and result["mode"] == r.MODE
    run = Path(result["run_dir"])
    assert json.loads((run / "cell.json").read_text())["mode"] == r.MODE
    cp = json.loads((Path(result["attempt_dir"]) / "checkpoint-2.json").read_text())
    assert cp["endpoints"]["full_validation"]["status"] == "complete"
    assert cp["endpoints"]["full_validation"]["scored_positions"] == 28
    assert len(list(run.glob("attempt-*/checkpoint-*.receipt.json"))) == 2
    with pytest.raises(ValueError, match="already complete"):
        cap, tok = f["factory"](None)
        fn(*args[:2], cap, tok, **kwargs, resume=True)


def test_retry_unknown_cost_and_deadline(tmp_path):
    state = dict(dispatches=0, cost=dict(unknown_attempts=[]))
    r.retry_allowed(state, tmp_path)
    state["dispatches"] = 1
    with pytest.raises(ValueError, match="certified checkpoint"):
        r.retry_allowed(state, tmp_path)
    attempt = tmp_path / "attempt-0000"
    attempt.mkdir()
    (attempt / "checkpoint-100.receipt.json").write_text("{}")
    r.retry_allowed(state, tmp_path)
    state["dispatches"] = 2
    with pytest.raises(RuntimeError, match="one-retry"):
        r.retry_allowed(state, tmp_path)
    state["cost"]["unknown_attempts"] = ["torn"]
    with pytest.raises(ValueError, match="unknown/torn"):
        r.retry_allowed(state, tmp_path)
    r.deadline_check(r.CUTOFF - 1)
    with pytest.raises(TimeoutError):
        r.deadline_check(r.CUTOFF)


def test_supplemental_watch_preserves_primary_function():
    import inspect

    before = inspect.getsource(r.watch.inspect)
    adapted = r.watch_inspector()
    assert adapted is not r.watch.inspect
    assert "additional_work_R_cell" in adapted.__code__.co_consts or any(
        isinstance(x, tuple) and "additional_work_R_cell" in x for x in adapted.__code__.co_consts
    )
    assert "supplemental" in adapted.__code__.co_consts
    assert inspect.getsource(r.watch.inspect) == before


def test_supplemental_watch_checks_actual_bound_vectors(tmp_path, monkeypatch):
    from tests.revision_v1.test_ht8_fidelity_watch import certified_fixture
    from tests.revision_v1.test_r1_49m_fidelity_policy import save_report

    monkeypatch.setattr(r.watch, "ROOT", tmp_path)
    binding, result, cell, report, vector = certified_fixture(monkeypatch, tmp_path)
    path = Path(binding["path"])
    recipe = json.loads(path.read_text())
    recipe["mode"] = r.MODE
    path.write_text(json.dumps(recipe))
    binding = r.ref(path)
    cell["manifest_sha256"] = binding["sha256"]
    report["mode"] = r.MODE
    report["endpoints"]["full_validation"]["manifest_sha256"] = binding["sha256"]
    meta = vector.parent.parent / "cell.json"
    value = json.loads(meta.read_text())
    value.update(mode=r.MODE, manifest_sha256=binding["sha256"])
    meta.write_text(json.dumps(value))
    save_report(cell, report, vector)
    value = json.loads(result.read_text())
    value["mode"] = r.MODE
    result.write_text(json.dumps(value))
    observation = r.watch_inspector()(binding, result)
    assert observation["scope"] == "supplemental" and observation["concentration"]["positions"] == 4
    written = r.watch.update(
        [observation],
        output=tmp_path / "results/additional_work/R/fidelity_watch",
        document=tmp_path / "docs/R_fidelity_watch.md",
    )
    assert written["new_cells"] == 1
    with pytest.raises(ValueError, match="mode"):
        r.watch.inspect(binding, result)
    vector.write_bytes(vector.read_bytes() + b"changed")
    with pytest.raises(ValueError):
        r.watch_inspector()(binding, result)


def test_queue_receipt_supersedes_driver_cost_once(tmp_path, monkeypatch):
    monkeypatch.setattr(r.queue, "ROOT", tmp_path)
    output = tmp_path / "results"
    receipts = tmp_path / "queue"
    session = receipts / "s"
    monkeypatch.setattr(r, "OUTPUT", output)
    monkeypatch.setattr(r, "RECEIPTS", receipts)
    monkeypatch.setattr(r, "sources", lambda: {})
    c = dict(
        cell_id="tiny",
        recipe={"path": "fixture", "sha256": "a" * 64},
        ceilings=dict(wall_seconds=17),
    )

    def launch(cmd, **kw):
        assert 0 < kw["timeout"] <= 17
        attempt = output / "tiny/attempt-0000"
        attempt.mkdir(parents=True)
        (attempt / "result.json").write_text(
            json.dumps(dict(status="complete", attempt_wall_seconds=5))
        )
        return type("Result", (), {"returncode": 0})()

    monkeypatch.setattr(r.subprocess, "run", launch)
    result = r.dispatch(c, {"integrity_profile": "full"}, session, {}, {}, {}, 100)
    state = r.status(c, r.native.sha(r.MATRIX))
    assert state["complete"] and state["dispatches"] == 1 and not state["cost"]["unknown_attempts"]
    assert state["cost"]["known_attempt_wall_seconds"] == result["charged_process_wall_seconds"]
    assert state["cost"]["driver_attempt_wall_seconds"] == 5
    finish = session / "tiny/dispatch-00/finish.json"
    value = json.loads(finish.read_text())
    value["cell_id"] = "wrong"
    finish.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="identity mismatch"):
        r.status(c, r.native.sha(r.MATRIX))
