"""Terminal accounting, real torn evidence, and same-session queue continuation."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
import os
from contextlib import contextmanager

import pytest

from aw import r_run as r


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


@pytest.fixture
def torn(tmp_path, monkeypatch):
    monkeypatch.setattr(r.queue, "ROOT", tmp_path)
    monkeypatch.setattr(r, "OUTPUT", tmp_path / "results")
    monkeypatch.setattr(r, "RECEIPTS", tmp_path / "queue")
    c = dict(
        cell_id="tiny",
        recipe={"path": "recipe", "sha256": "a" * 64},
        condition="v0_stable",
        dataset="zsre",
        ceilings=dict(wall_seconds=17),
    )
    monkeypatch.setattr(r, "matrix", lambda: dict(cells=[c]))
    attempt = r.OUTPUT / "tiny/attempt-0000"
    write(attempt / "phases/open.json", {"phase": "drift:1000", "status": "open"})
    session = r.RECEIPTS / "original"
    write(session / "session-start.json", dict(matrix=r.ref(r.MATRIX), decision={}))
    write(session / "session-finish.json", dict(elapsed_wall_seconds=20))
    start = dict(cell_id="tiny", matrix_sha256=r.native.sha(r.MATRIX))
    receipt = session / "tiny/dispatch-00"
    write(receipt / "start.json", start)
    write(
        receipt / "finish.json",
        dict(
            start,
            start_sha256=r.native.sha(receipt / "start.json"),
            charged_process_wall_seconds=17.1,
            new_attempts=[str(attempt)],
        ),
    )
    return c, attempt, session, receipt


def test_torn_accounting_closed_once_without_repairing_science(torn):
    c, attempt, _, _ = torn
    before = r.attempt_files(attempt.parent)
    assert r.status(c, r.native.sha(r.MATRIX))["cost"]["unknown_attempts"]
    preview = r.reconcile("tiny")
    assert not (attempt.parent / "reconciliation.json").exists()
    assert r.reconcile("tiny", execute=True) == preview
    assert r.reconcile("tiny", execute=True) == preview
    assert r.attempt_files(attempt.parent) == before
    state = r.status(c, r.native.sha(r.MATRIX))
    assert not state["complete"] and state["terminal"] == "incomplete_by_ceiling"
    assert state["cost"]["known_attempt_wall_seconds"] == 17.1
    assert not state["cost"]["unknown_attempts"]
    with pytest.raises(RuntimeError, match="no retry budget"):
        r.retry_allowed(state, attempt.parent)
    assert r.resume_inventory()["incomplete"] == ["tiny"]
    write(attempt / "phases/late.json", {"success": True})
    with pytest.raises(ValueError, match="no longer matches"):
        r.status(c, r.native.sha(r.MATRIX))


@pytest.mark.parametrize("problem", ["uncovered", "budget_left", "open_session", "tamper"])
def test_refuse_unproved_reconciliation(torn, problem):
    c, attempt, session, receipt = torn
    if problem == "uncovered":
        (attempt.parent / "attempt-0001").mkdir()
    elif problem == "budget_left":
        c["ceilings"]["wall_seconds"] = 20
    elif problem == "open_session":
        write(session / "resumes/0001/session-start.json", dict(matrix=r.ref(r.MATRIX)))
    else:
        value = json.loads((receipt / "finish.json").read_text())
        value["cell_id"] = "wrong"
        write(receipt / "finish.json", value)
    with pytest.raises(ValueError):
        r.reconcile("tiny", execute=True)


def test_resume_keeps_session_skips_terminal_and_charges_only_segments(torn, monkeypatch):
    from pccap.harness import lease

    c, _, session, _ = torn
    r.reconcile("tiny", execute=True)
    more = [dict(c, cell_id="done"), dict(c, cell_id="next")]
    monkeypatch.setattr(r, "matrix", lambda: dict(cells=[c, *more]))
    original_status = r.status

    def state(cell, matrix_hash):
        if cell["cell_id"] == "tiny":
            return original_status(cell, matrix_hash)
        return dict(
            complete=cell["cell_id"] == "done",
            terminal=None,
            dispatches=0,
            cost=dict(known_attempt_wall_seconds=0, unknown_attempts=[]),
        )

    monkeypatch.setattr(r, "status", state)
    monkeypatch.setattr(r, "approve", lambda _: {})
    monkeypatch.setattr(r, "sources", lambda: {})
    monkeypatch.setattr(r, "recipe", lambda *_: ({}, {}))
    monkeypatch.setattr(r, "observe", lambda cell: {"cell_id": cell["cell_id"]})
    monkeypatch.setattr(r.watch, "update", lambda *a, **k: None)
    monkeypatch.setattr(r.queue, "memory_available_mib", lambda: 1e9)
    monkeypatch.setattr(r, "lease_probe", lambda _: dict(pid=os.getpid()))
    for cell in [c, *more]:
        cell["ceilings"]["peak_host_mib"] = 1

    @contextmanager
    def gpu(*a, **k):
        yield type("Lease", (), {"other_cuda_processes": lambda self: []})()

    monkeypatch.setattr(lease, "gpu_lease", gpu)
    launched = []

    def dispatch(cell, manifest, target, *args):
        assert target == session
        launched.append(cell["cell_id"])
        return dict(failure_class=None)

    monkeypatch.setattr(r, "dispatch", dispatch)
    original = (session / "session-finish.json").read_bytes()
    result = r.run("decision", resume=session)
    assert launched == ["next"]
    assert result["completed"] == ["done", "next"]
    assert result["incomplete"] == ["tiny"]
    assert result["status"] == "finished_with_incomplete_cells"
    assert (session / "session-finish.json").read_bytes() == original
    assert r.session_cost() == pytest.approx(20 + result["elapsed_wall_seconds"])
    assert (session / "resumes/0001/session-finish.json").is_file()
    assert r.resume_inventory(defer_classes=["v0_stable:zsre"])["deferred"] == ["next"]
    assert c["ceilings"]["wall_seconds"] == 17
    with pytest.raises(ValueError, match="unknown condition"):
        r.resume_inventory(defer_classes=["typo:zsre"])
