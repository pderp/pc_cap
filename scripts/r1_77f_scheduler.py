"""Retry-once queue: bounded workers, durable shared cost, host-failure stops."""

from __future__ import annotations

import errno
import fcntl
import itertools
import json
import math
import os
import time
import uuid
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from scripts.r1_68b_integrity_runtime import durable_directory

POLICY = "R1-77f-retry-once-v1"
CEILING_DEFINITION = {
    "version": 1,
    "wall_seconds": "admitted_solo_ceiling",
    "solo_safety_factor": 1.5,
    "workers_1_factor": 1.0,
    "workers_2_factor": 1.15,
    "charged_budget": "sum_of_process_envelopes_including_overlap_and_failures",
    "maximum_cell_failures": 2,
}


def failure_history(namespace, cell_id, receipt_root, matrix_hash):
    q = SimpleNamespace(**namespace)
    if receipt_root is None:
        return 0
    failures = 0
    for p in Path(receipt_root).glob("**/finish.json"):
        row = q.read(p)
        if row.get("cell_id") != cell_id or row.get("matrix_sha256") != matrix_hash:
            continue
        start = p.parent / "start.json"
        if not start.is_file() or q.sha(start) != row.get("start_sha256"):
            raise ValueError("retry history start identity changed")
        original = q.read(start)
        if any(row.get(k) != v for k, v in original.items()):
            raise ValueError("retry history differs from start")
        if row.get("retry_policy") == POLICY and row.get("failure_class") == "cell":
            failures += 1
    return failures


def lease_probe(root):
    """Read an externally held lease, verify its holder lives and its lock persists."""
    path = Path(root) / "results/.gpu_lease"
    try:
        with path.open("r") as f:
            row = json.load(f)
            if type(row.get("pid")) is not int or row["pid"] <= 0:
                return None
            os.kill(row["pid"], 0)
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return {k: row.get(k) for k in ("pid", "task", "stage", "started")}
            else:
                fcntl.flock(f, fcntl.LOCK_UN)
                return None
    except (OSError, ValueError, TypeError):
        return None


def failure_class(code, error, new_attempts, process_log):
    """Signals/OOM/lease failures are host failures, never ordinary cell retries."""
    if isinstance(error, (MemoryError, KeyboardInterrupt, SystemExit)):
        return "host"
    if isinstance(error, OSError) and error.errno in (errno.ENOMEM, errno.ENOSPC, errno.EIO):
        return "host"
    if code is not None and (code < 0 or code in (130, 137, 143)):
        return "host"
    reasons = [str(error or "")]
    for directory in new_attempts:
        path = Path(directory) / "failure.json"
        if path.is_file():
            row = json.loads(path.read_text())
            reasons += [row.get("error_type", ""), row.get("reason", "")]
    if Path(process_log).is_file() and (error is not None or code != 0):
        with Path(process_log).open("rb") as f:
            f.seek(max(0, f.seek(0, os.SEEK_END) - 16384))
            reasons.append(f.read().decode(errors="replace"))
    message = " ".join(reasons).lower()
    if any(s in message for s in ("memoryerror", "memavailable", "memory guard", "out of memory",
                                  "resource_exhausted", "lease lost", "lease loss")):
        return "host"
    return "cell" if error is not None or code != 0 else None


def run_workers(namespace, matrix_path, bindings_path, *, receipt_root, stop_after,
                min_memory_mib, ceiling_hours, executor, memory_reader, workers, lease_reader=None):
    q = SimpleNamespace(**namespace)
    matrix_path, bindings_path = Path(matrix_path).resolve(), Path(bindings_path).resolve()
    matrix_hash, binding_hash = q.sha(matrix_path), q.sha(bindings_path)
    producer_hash, scheduler_hash = q.sha(q.__file__), q.sha(__file__)
    matrix, bindings = q.read(matrix_path), q.read(bindings_path)
    if matrix["scope"] not in ("development", "confirmatory"):
        raise PermissionError("explicit development or confirmatory matrix scope required")
    if bindings.get("matrix_sha256") != matrix_hash:
        raise ValueError("queue bindings reference a different matrix")
    if matrix["scope"] == "confirmatory":
        q.verify_sealed_matrix(matrix, bindings)
    if "queue_ceiling_contract" in matrix and matrix["queue_ceiling_contract"] != CEILING_DEFINITION:
        raise ValueError("matrix queue ceiling/retry definition differs")
    if not math.isfinite(min_memory_mib) or min_memory_mib <= 0:
        raise ValueError("positive MemAvailable threshold required")
    if ceiling_hours is not None and (not math.isfinite(ceiling_hours) or ceiling_hours <= 0):
        raise ValueError("positive ceiling required")
    output = Path(receipt_root).resolve()
    if not output.is_relative_to(q.ROOT / "logs"):
        raise PermissionError("queue receipts belong under repo logs")
    output.mkdir(parents=True, exist_ok=True)
    locks = q.ROOT / "logs/r1_77_queue_locks"
    locks.mkdir(parents=True, exist_ok=True)
    fd = os.open(locks / f"queue-{matrix_hash}.lock", os.O_RDONLY | os.O_CREAT, 0o600)
    factor, begun = q.worker_factor(workers), time.monotonic()
    if lease_reader is None and executor is q.launch:
        def lease_reader():
            return lease_probe(q.ROOT)
    lease_identity = lease_reader() if lease_reader else None

    def inventory():
        return q.inventory(matrix, stop_after=stop_after, ceiling_hours=ceiling_hours,
                           receipt_root=output, matrix_hash=matrix_hash, workers=workers)

    def response(status, **extra):
        return dict(status=status, inventory=inventory(), workers=workers,
                    concurrency_ceiling_factor=factor, retry_policy=POLICY,
                    queue_wall_seconds=time.monotonic()-begun,
                    cost_basis=CEILING_DEFINITION["charged_budget"], **extra)

    def inputs_current():
        if q.sha(matrix_path) != matrix_hash or q.sha(bindings_path) != binding_hash:
            raise ValueError("queue inputs changed")
        if q.sha(q.__file__) != producer_hash or q.sha(__file__) != scheduler_hash:
            raise ValueError("queue implementation changed")

    def execute_cell(binding, manifest, cell, folder, start):
        before = {str(p.resolve()) for p in Path(cell["result_dir"]).glob("attempt-*")}
        tick, code, error = time.monotonic(), None, None
        try:
            kwargs = dict(resume=start["resume"], output=folder / "process.log")
            if executor is q.launch:
                kwargs["max_wall_seconds"] = start["effective_wall_ceiling_seconds"]
            code = executor(binding, manifest, **kwargs)
        except BaseException as exc:
            error = exc
        new = sorted(str(p.resolve()) for p in Path(cell["result_dir"]).glob("attempt-*")
                     if str(p.resolve()) not in before)
        category = failure_class(code, error, new, folder / "process.log")
        finish = dict(start, status="executor_exception" if error else "process_exited",
                      exit_code=code, exception=repr(error) if error else None, failure_class=category,
                      charged_process_wall_seconds=time.monotonic()-tick,
                      start_sha256=q.sha(folder / "start.json"), new_attempts=new)
        q.durable_json(folder / "finish.json", finish)
        return dict(cell=cell, folder=folder, code=code, error=error, failure_class=category)

    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        observed = inventory()
        rows = {r["cell_id"]: r for r in observed["queue"]}
        if any(r["observed"]["status"] == "invalid" for r in rows.values()):
            raise ValueError("invalid existing cell; queue stops")
        if observed["cost"]["unknown_attempts"]:
            raise ValueError("unknown attempt costs; owner reconciliation required")
        if lease_reader and not lease_identity:
            return response("lease_guard_stop", reason="live externally held GPU lease required")
        stop, exhausted = None, set()
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="r1-77f") as pool:
            for _, group in itertools.groupby(q.ordered(matrix, stop_after), key=lambda c: c["block_number"]):
                pending, active = list(group), {}
                while pending or active:
                    inputs_current()
                    if lease_reader and lease_reader() != lease_identity:
                        stop = ("lease_guard_stop", {"reason": "lease identity or lock lost"})
                    # No active output is read: completed rows replace only their own cached row.
                    while pending and len(active) < workers and stop is None:
                        inputs_current()
                        cell = pending[0]
                        cid = cell["cell_id"]
                        binding, manifest = q.recipe_for(cell, bindings)
                        row = rows[cid]
                        if row["observed"]["artifact_complete"]:
                            q.verify_resume(cell, manifest)
                            pending.pop(0)
                            continue
                        failures = failure_history(namespace, cid, output, matrix_hash)
                        if failures >= 2:
                            exhausted.add(cid)
                            pending.pop(0)
                            continue
                        q.recipe_for(cell, bindings, execute=True)
                        backend = q.sealed if manifest["mode"] == q.sealed.MODE else q.driver
                        expected = backend.OUTPUT_ROOT / q.driver.cell_name(manifest, binding["sha256"])
                        if Path(cell["result_dir"]).resolve() != expected.resolve():
                            raise ValueError("matrix result directory differs from driver destination")
                        solo = (cell.get("ceilings") or {}).get("wall_seconds")
                        if isinstance(solo, bool) or not isinstance(solo, (int, float)) or not math.isfinite(solo) or solo <= 0:
                            raise ValueError("per-cell admitted solo wall ceiling required")
                        effective = factor * solo
                        spent = math.fsum(r["cost"]["known_attempt_wall_seconds"] for r in rows.values())
                        reserved = math.fsum(a["ceiling"] for a in active.values())
                        if ceiling_hours is not None and spent + reserved + effective > ceiling_hours * 3600:
                            if not active:
                                stop = ("budget_stop", {})
                            break
                        mem = memory_reader()
                        floor = max(min_memory_mib, 6144.0 if active else min_memory_mib)
                        if not math.isfinite(mem) or mem < floor:
                            stop = ("memory_guard_stop", {"MemAvailable_MiB": mem, "required_MiB": floor})
                            break
                        if datetime.now(ZoneInfo("America/New_York")).date().isoformat() > "2026-10-09":
                            stop = ("experiment_deadline_stop", {})
                            break
                        if lease_reader and lease_reader() != lease_identity:
                            stop = ("lease_guard_stop", {"reason": "lease lost before dispatch"})
                            break
                        resume = Path(cell["result_dir"]).exists()
                        if resume:
                            q.verify_resume(cell, manifest)
                        for parent in (backend.OUTPUT_ROOT, backend.RESOURCE_ROOT):
                            if not Path(parent).exists():
                                durable_directory(parent)
                        folder = output / f"{cid}-{uuid.uuid4().hex}"
                        folder.mkdir()
                        start = dict(cell_id=cid, matrix_sha256=matrix_hash, bindings_sha256=binding_hash,
                                     recipe=binding, resume=resume, started_at=datetime.now(timezone.utc).isoformat(),
                                     MemAvailable_MiB=mem, producer_sha256=producer_hash, scheduler_sha256=scheduler_hash,
                                     workers=workers, retry_policy=POLICY, previous_cell_failures=failures,
                                     solo_wall_ceiling_seconds=solo, effective_wall_ceiling_seconds=effective,
                                     admitted_other_reservations_seconds=reserved, admitted_prior_charged_seconds=spent,
                                     required_MemAvailable_MiB=floor, lease_identity=lease_identity)
                        q.durable_json(folder / "start.json", start)
                        future = pool.submit(execute_cell, binding, manifest, cell, folder, start)
                        active[future] = dict(cell=cell, ceiling=effective)
                        pending.pop(0)
                    if not active:
                        if stop:
                            break
                        continue
                    done, _ = wait(active, timeout=1., return_when=FIRST_COMPLETED)
                    for future in done:
                        result = future.result()
                        active.pop(future)
                        cell = result["cell"]
                        cid = cell["cell_id"]
                        row, _ = q.observe_cell(matrix, cell, receipt_root=output, matrix_hash=matrix_hash)
                        rows[cid] = row
                        if result["failure_class"] == "host":
                            stop = ("host_failure_stop", {"cell_id": cid, "exit_code": result["code"],
                                                           "exception": repr(result["error"])})
                        if row["observed"]["status"] == "invalid" or row["cost"]["unknown_attempts"]:
                            stop = ("reconciliation_stop", {"cell_id": cid, "reason": "invalid artifacts or unknown/torn attempt; automatic resume refused"})
                        failures = failure_history(namespace, cid, output, matrix_hash)
                        if result["failure_class"] == "cell" and not row["observed"]["artifact_complete"]:
                            if failures < 2 and stop is None:
                                pending.insert(0, cell)
                                outcome = "retry_pending"
                            else:
                                exhausted.add(cid)
                                outcome = "incomplete_after_two_failures" if failures >= 2 else "host_stopped"
                        elif not row["observed"]["artifact_complete"] and result["failure_class"] is None:
                            stop = ("cell_incomplete_stop", {"cell_id": cid, "reason": "successful process did not complete; explicit pause/reconciliation required"})
                            outcome = "paused_or_incomplete"
                        else:
                            outcome = "complete" if row["observed"]["artifact_complete"] else "host_stopped"
                        q.durable_json(result["folder"] / "decision.json", dict(
                            cell_id=cid, matrix_sha256=matrix_hash, retry_policy=POLICY,
                            finish_sha256=q.sha(result["folder"] / "finish.json"),
                            outcome=outcome, failed_attempts=failures,
                            retained_other_workers=len(active)))
                    if stop and not active:
                        break
                if stop:
                    break
        if stop:
            return response(stop[0], **stop[1])
        return response("selected_blocks_processed_with_incomplete" if exhausted else "selected_blocks_complete",
                        retry_exhausted_cell_ids=sorted(exhausted))
    finally:
        os.close(fd)
