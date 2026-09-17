"""Retry policy through real CPU drivers, including live-worker continuation."""
import json
import threading

import pytest
from scripts import r1_77_queue as q
from scripts.r1_77f_scheduler import CEILING_DEFINITION, failure_class

from tests.revision_v1.test_r1_77_queue import run, tiny  # noqa: F401
from tests.revision_v1.test_r1_77b_sealed_backend import make  # noqa: F401
from tests.revision_v1.test_r1_77e_workers import pair  # noqa: F401


@pytest.mark.parametrize("workers", [1, 2])
def test_failure_after_checkpoint_retries_certified_state(tiny, workers):  # noqa: F811
    resumes = []

    def execute(*a, **kw):
        resumes.append(kw["resume"])
        result = tiny["execute"](*a, **kw, pause=len(resumes) == 1)
        if len(resumes) == 1:
            raise RuntimeError("failed after checkpoint publication")
        return result

    result = run(tiny, workers=workers, executor=execute)
    assert resumes == [False, True]
    assert result["status"] == "selected_blocks_complete"
    row = result["inventory"]["queue"][0]
    assert row["observed"]["artifact_complete"]
    assert len(row["cost"]["process_receipts"]) == 2
    starts = [q.read(p) for p in tiny["receipts"].glob("*/start.json")]
    assert sorted(s["previous_cell_failures"] for s in starts) == [0, 1]
    assert max(s["admitted_prior_charged_seconds"] for s in starts) > 0


def test_second_failure_refills_slot_without_draining_other_worker(pair):  # noqa: F811
    pair["matrix"]["cells"][2].update(block_number=1, within_block_order=3)
    with open(pair["mp"]["path"], "w") as f:
        json.dump(pair["matrix"], f)
    bindings = q.read(pair["bp"]["path"])
    bindings["matrix_sha256"] = q.sha(pair["mp"]["path"])
    with open(pair["bp"]["path"], "w") as f:
        json.dump(bindings, f)
    other_started, replacement_started = threading.Event(), threading.Event()
    calls = []

    def execute(b, m, **kw):
        order = m["cell"]["order"]
        calls.append(order)
        if order == "0":
            assert other_started.wait(20)
            return 7
        if order == "1":
            other_started.set()
            assert replacement_started.wait(20), "other worker was drained before slot refill"
        else:
            replacement_started.set()
        return pair["execute"](b, m, **kw)

    result = pair["run"](executor=execute)
    assert result["status"] == "selected_blocks_processed_with_incomplete"
    assert calls.count("0") == 2
    assert len(result["inventory"]["incomplete_cells"]) == 1
    decisions = [q.read(p) for p in pair["receipts"].glob("*/decision.json")]
    assert any(d["outcome"] == "incomplete_after_two_failures" and d["retained_other_workers"] == 1 for d in decisions)
    pair["run"](executor=lambda *a, **k: pytest.fail("exhausted cell was retried again"))


@pytest.mark.parametrize("kind", ["memory", "signal", "lease"])
def test_host_failures_stop_dispatch_without_cell_retry(tiny, kind):  # noqa: F811
    calls = []
    live = [True]

    def execute(*a, **kw):
        calls.append(1)
        if kind == "memory":
            raise MemoryError("synthetic host pressure")
        if kind == "lease":
            live[0] = False
            return 7
        return 137

    result = run(tiny, executor=execute, lease_reader=lambda: {"pid": 123} if live[0] else None)
    assert result["status"] in ("host_failure_stop", "lease_guard_stop")
    assert len(calls) == 1
    assert len(list(tiny["receipts"].glob("*/finish.json"))) == 1


def test_contradictory_ceiling_definition_refused(tiny):  # noqa: F811
    tiny["matrix"]["queue_ceiling_contract"] = {**CEILING_DEFINITION, "workers_2_factor": 1.65}
    tiny["mp"].write_text(json.dumps(tiny["matrix"]))
    b = q.read(tiny["bp"])
    b["matrix_sha256"] = q.sha(tiny["mp"])
    tiny["bp"].write_text(json.dumps(b))
    with pytest.raises(ValueError, match="ceiling/retry"):
        run(tiny, executor=lambda *a, **kw: pytest.fail("contradictory policy launched"))


def test_failure_class_reads_bounded_process_diagnostics(tmp_path):
    log = tmp_path / "process.log"
    log.write_text("x" * 20000 + "RESOURCE_EXHAUSTED: out of memory")
    assert failure_class(1, None, [], log) == "host"
