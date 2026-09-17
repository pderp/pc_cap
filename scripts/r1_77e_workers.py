"""Two-worker queue scheduler; shared conservative process-time account, block barriers."""

from __future__ import annotations

import fcntl
import itertools
import math
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

from scripts.r1_68b_integrity_runtime import durable_directory


def run_two_workers(
    namespace,
    matrix_path,
    bindings_path,
    *,
    receipt_root,
    stop_after,
    min_memory_mib,
    ceiling_hours,
    executor,
    memory_reader,
):
    q = SimpleNamespace(**namespace)
    matrix_path, bindings_path = Path(matrix_path).resolve(), Path(bindings_path).resolve()
    matrix_hash, binding_hash = q.sha(matrix_path), q.sha(bindings_path)
    producer_hash, scheduler_hash = q.sha(q.__file__), q.sha(__file__)
    matrix, bindings = q.read(matrix_path), q.read(bindings_path)
    if matrix["scope"] not in ("development", "confirmatory"):
        raise PermissionError("explicit development or confirmatory scope required")
    if bindings.get("matrix_sha256") != matrix_hash:
        raise ValueError("queue bindings reference a different matrix")
    if matrix["scope"] == "confirmatory":
        q.verify_sealed_matrix(matrix, bindings)
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
    factor, begun = q.worker_factor(2), time.monotonic()

    def inventory():
        return q.inventory(
            matrix,
            stop_after=stop_after,
            ceiling_hours=ceiling_hours,
            receipt_root=output,
            matrix_hash=matrix_hash,
            workers=2,
        )

    def response(status, **extra):
        return dict(
            status=status,
            inventory=inventory(),
            workers=2,
            concurrency_ceiling_factor=factor,
            queue_wall_seconds=time.monotonic() - begun,
            cost_basis="sum of full child-process envelopes, including overlap; one shared account; no speedup discount",
            **extra,
        )

    def inputs_current():
        if q.sha(matrix_path) != matrix_hash or q.sha(bindings_path) != binding_hash:
            raise ValueError("queue inputs changed")
        if q.sha(q.__file__) != producer_hash or q.sha(__file__) != scheduler_hash:
            raise ValueError("queue implementation changed")

    def execute_cell(binding, manifest, cell, folder, start, started):
        before = {str(p.resolve()) for p in Path(cell["result_dir"]).glob("attempt-*")}
        tick = time.monotonic()
        code, error = None, None
        started.set()
        try:
            kwargs = dict(resume=start["resume"], output=folder / "process.log")
            if executor is q.launch:
                kwargs["max_wall_seconds"] = start["effective_wall_ceiling_seconds"]
            code = executor(binding, manifest, **kwargs)
        except BaseException as exc:
            error = exc
        finally:
            q.durable_json(
                folder / "finish.json",
                {
                    **start,
                    "status": "executor_exception" if error else "process_exited",
                    "exit_code": code,
                    "exception": repr(error) if error else None,
                    "charged_process_wall_seconds": time.monotonic() - tick,
                    "start_sha256": q.sha(folder / "start.json"),
                    "new_attempts": sorted(
                        str(p.resolve())
                        for p in Path(cell["result_dir"]).glob("attempt-*")
                        if str(p.resolve()) not in before
                    ),
                },
            )
        return cell["cell_id"], code, error

    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="r1-77e") as pool:
            for _, block in itertools.groupby(
                q.ordered(matrix, stop_after), key=lambda c: c["block_number"]
            ):
                pending = list(block)
                while pending:
                    inputs_current()
                    observed = inventory()
                    if any(r["observed"]["status"] == "invalid" for r in observed["queue"]):
                        raise ValueError("invalid existing cell; queue stops")
                    if observed["cost"]["unknown_attempts"]:
                        raise ValueError("unknown attempt costs; owner reconciliation required")
                    rows = {r["cell_id"]: r for r in observed["queue"]}
                    spent = observed["cost"]["known_attempt_hours"] * 3600
                    reserved, futures, stop = 0.0, [], None
                    try:
                        while pending and len(futures) < 2:
                            if any(
                                f.done() and (f.result()[1] != 0 or f.result()[2] is not None)
                                for f in futures
                            ):
                                break
                            inputs_current()
                            cell = pending[0]
                            binding, manifest = q.recipe_for(cell, bindings)
                            if rows[cell["cell_id"]]["observed"]["artifact_complete"]:
                                q.verify_resume(cell, manifest)
                                pending.pop(0)
                                continue
                            q.recipe_for(cell, bindings, execute=True)
                            backend = q.sealed if manifest["mode"] == q.sealed.MODE else q.driver
                            expected = backend.OUTPUT_ROOT / q.driver.cell_name(
                                manifest, binding["sha256"]
                            )
                            if Path(cell["result_dir"]).resolve() != expected.resolve():
                                raise ValueError(
                                    "matrix result directory differs from driver destination"
                                )
                            solo = (cell.get("ceilings") or {}).get("wall_seconds")
                            if (
                                isinstance(solo, bool)
                                or not isinstance(solo, (int, float))
                                or not math.isfinite(solo)
                                or solo <= 0
                            ):
                                raise ValueError(
                                    "per-cell solo wall ceiling required for concurrent admission"
                                )
                            effective = factor * solo
                            if (
                                ceiling_hours is not None
                                and spent + reserved + effective > ceiling_hours * 3600
                            ):
                                # Another worker's ceiling is reserved, not free budget. Drain
                                # it and reconsider against actual charged cost before stopping.
                                if not futures:
                                    stop = ("budget_stop", {})
                                break
                            mem = memory_reader()
                            floor = max(min_memory_mib, 6144.0 if futures else min_memory_mib)
                            if not math.isfinite(mem) or mem < floor:
                                stop = (
                                    "memory_guard_stop",
                                    {"MemAvailable_MiB": mem, "required_MiB": floor},
                                )
                                break
                            if (
                                datetime.now(ZoneInfo("America/New_York")).date().isoformat()
                                > "2026-10-09"
                            ):
                                stop = ("experiment_deadline_stop", {})
                                break
                            resume = Path(cell["result_dir"]).exists()
                            if resume:
                                q.verify_resume(cell, manifest)
                            # The unchanged cell writer creates parent chains exclusively.
                            # Establish shared parents before either worker can race on them;
                            # per-cell destinations remain absent and retain canonical locks.
                            for parent in (backend.OUTPUT_ROOT, backend.RESOURCE_ROOT):
                                if not Path(parent).exists():
                                    durable_directory(parent)
                            folder = output / f"{cell['cell_id']}-{uuid.uuid4().hex}"
                            folder.mkdir()
                            start = dict(
                                cell_id=cell["cell_id"],
                                matrix_sha256=matrix_hash,
                                bindings_sha256=binding_hash,
                                recipe=binding,
                                resume=resume,
                                started_at=datetime.now(timezone.utc).isoformat(),
                                MemAvailable_MiB=mem,
                                producer_sha256=producer_hash,
                                scheduler_sha256=scheduler_hash,
                                workers=2,
                                solo_wall_ceiling_seconds=solo,
                                effective_wall_ceiling_seconds=effective,
                                admitted_other_reservations_seconds=reserved,
                                admitted_prior_charged_seconds=spent,
                                required_MemAvailable_MiB=floor,
                            )
                            q.durable_json(folder / "start.json", start)
                            event = threading.Event()
                            futures.append(
                                pool.submit(
                                    execute_cell, binding, manifest, cell, folder, start, event
                                )
                            )
                            event.wait()
                            reserved += effective
                            pending.pop(0)
                    finally:
                        # An admission failure or worker error never abandons the other
                        # running cell. Observe results only after both receipts are durable.
                        results = [f.result() for f in futures]
                    if futures:
                        after = inventory()
                        completed = {
                            r["cell_id"]: r["observed"]["artifact_complete"] for r in after["queue"]
                        }
                        errors = [err for _, _, err in results if err is not None]
                        if errors:
                            raise errors[0]
                        bad = [
                            (cid, code)
                            for cid, code, _ in results
                            if code != 0 or not completed[cid]
                        ]
                        if bad:
                            return response(
                                "cell_incomplete_stop",
                                failed_cells=[c for c, _ in bad],
                                exit_code=bad[0][1],
                            )
                    if stop:
                        return response(stop[0], **stop[1])
            return response("selected_blocks_complete")
    finally:
        os.close(fd)
