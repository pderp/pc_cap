"""R1-77: ordered, identity-checked queue and DEC-052 inventory.

Dry-run/status are read-only. Sealed execution uses the explicit R1-77b backend
with approved frozen contracts and independent populations. Development execution
retains its existing admission firewall.
No backend is silently substituted and no admission flag is rewritten.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts import r1_68c_dev_cell as driver
from scripts import r1_75_analysis_stage4_v1 as analysis
from scripts import r1_77b_sealed_backend as sealed
from scripts.r1_68b_integrity_runtime import DurablePhaseJournal, durable_json

import pccap  # noqa: F401 -- determinism before importing the JAX driver

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    path = Path(path).resolve()
    if "confirm" in path.parts or not path.is_relative_to(ROOT.parent):
        raise PermissionError("unsealed local metadata only")
    raw = path.read_bytes()
    if sha(path) != hashlib.sha256(raw).hexdigest():
        raise ValueError("input changed during read")
    return json.loads(raw)


def ordered(matrix, stop_after=None):
    cells = analysis.validate_matrix(matrix)
    if any(c["block_number"] < 1 or c["within_block_order"] < 1 for c in cells):
        raise ValueError("positive block/within-block indices required")
    if stop_after is not None and stop_after not in {c["block_number"] for c in cells}:
        raise ValueError("stop-after must name a declared block")
    return sorted(
        (c for c in cells if stop_after is None or c["block_number"] <= stop_after),
        key=lambda c: (c["block_number"], c["within_block_order"]),
    )


def memory_available_mib(path=Path("/proc/meminfo")):
    for line in Path(path).read_text().splitlines():
        if line.startswith("MemAvailable:"):
            fields = line.split()
            if len(fields) != 3 or fields[2] != "kB":
                raise ValueError("unrecognized MemAvailable units")
            return int(fields[1]) / 1024
    raise ValueError("MemAvailable missing; cannot admit another process")


def recipe_for(cell, bindings, *, execute=False):
    binding = bindings.get("recipes", {}).get(cell["cell_id"])
    if binding is None:
        raise ValueError("recipe not bound")
    path = Path(binding["path"]).resolve()
    if "confirm" in path.parts:
        raise PermissionError("sealed recipes await a certified R1-68d confirmation backend")
    if sha(path) != binding["sha256"] or binding["sha256"] != cell["manifest_sha256"]:
        raise ValueError("recipe file/matrix identity mismatch")
    m = read(path)
    if (
        m["cell"] != {k: cell[k] for k in analysis.COORDS}
        or m["checkpoints"] != cell["checkpoints"]
    ):
        raise ValueError("recipe coordinate/cadence mismatch")
    for key in ("code_sha256", "adapter_identity"):
        if cell.get(key) is not None and m[key] != cell[key]:
            raise ValueError("matrix recipe binding mismatch: " + key)
    if cell.get("payload_sha256") is not None and m["payload"]["sha256"] != cell["payload_sha256"]:
        raise ValueError("matrix payload binding mismatch")
    if m.get("mode") == sealed.MODE:
        if binding.get("backend") != sealed.backend_binding():
            raise ValueError("queue sealed backend module/file binding mismatch")
        sealed.inspect_manifest(path, binding["sha256"])
        if execute:
            sealed.load_sealed_cell(path, binding["sha256"], allow_sealed=True)
    elif m.get("mode") == driver.MODE and "reservations" not in m and "protocol" not in m:
        if execute:
            driver.load_development_cell(path, binding["sha256"])
    else:
        raise PermissionError("explicit development or sealed backend required")
    return binding, m


def cell_cost(directory):
    """No prior-attempt totals are summed again; each physical attempt charged once."""
    result = dict(known_attempt_wall_seconds=0.0, unknown_attempts=[], attempts=[])
    if not directory:
        return result
    for attempt in sorted(Path(directory).glob("attempt-*")):
        endings = [p for p in (attempt / "result.json", attempt / "failure.json") if p.is_file()]
        if len(endings) != 1:
            result["unknown_attempts"].append(str(attempt))
            continue
        obj = read(endings[0])
        seconds = obj.get("attempt_wall_seconds")
        if seconds is None:
            result["unknown_attempts"].append(str(attempt))
            continue
        if (
            isinstance(seconds, bool)
            or not isinstance(seconds, (int, float))
            or not math.isfinite(seconds)
            or seconds < 0
        ):
            raise ValueError("invalid attempt cost")
        result["known_attempt_wall_seconds"] += seconds
        result["attempts"].append(
            {"path": str(endings[0]), "sha256": sha(endings[0]), "wall_seconds": seconds}
        )
    return result


def verify_resume(cell, manifest):
    """Verify checkpoint reports via analysis and snapshot bytes/journals here.

    The driver verifies restored state/adapter identity again before execution.
    Torn or open incremental intent is deliberately refused, not auto-retried.
    """
    directory = Path(cell["result_dir"]).resolve()
    if not directory.exists():
        return
    for path in directory.glob("attempt-*/checkpoint-*.receipt.json"):
        rec = read(path)
        snap = Path(rec["snapshot"]["path"]).resolve()
        if (
            not snap.is_relative_to(ROOT.parent / "assets")
            or sha(snap) != rec["snapshot"]["sha256"]
        ):
            raise ValueError("checkpoint snapshot identity/location mismatch")
    if manifest["integrity_profile"] == "incremental":
        for attempt in sorted(directory.glob("attempt-*")):
            DurablePhaseJournal.verify(attempt / "phases")
    if cell_cost(directory)["unknown_attempts"]:
        raise ValueError("unknown failed/interrupted-attempt spend requires owner reconciliation")


def charged_cost(cell, cost, receipt_root, matrix_hash):
    """Replace covered driver-attempt time with the full child-process envelope."""
    cost = dict(cost)
    cost["driver_attempt_wall_seconds"] = cost["known_attempt_wall_seconds"]
    cost["process_receipts"] = []
    if receipt_root is None:
        return cost
    covered = set()
    process_seconds = 0.0
    for start_path in sorted(Path(receipt_root).glob("**/start.json")):
        start = read(start_path)
        if start.get("matrix_sha256") != matrix_hash or start.get("cell_id") != cell["cell_id"]:
            continue
        finish_path = start_path.parent / "finish.json"
        if not finish_path.exists():
            cost["unknown_attempts"] = [*cost["unknown_attempts"], str(start_path)]
            continue
        finish = read(finish_path)
        if finish.get("start_sha256") != sha(start_path) or any(
            finish.get(k) != start.get(k) for k in start
        ):
            raise ValueError("queue process receipt identity mismatch")
        seconds = finish["charged_process_wall_seconds"]
        if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds < 0:
            raise ValueError("invalid process-envelope cost")
        new = set(finish["new_attempts"])
        if covered.intersection(new):
            raise ValueError("driver attempt covered by multiple process receipts")
        covered.update(new)
        process_seconds += seconds
        cost["process_receipts"].append(
            {"path": str(finish_path), "sha256": sha(finish_path), "wall_seconds": seconds}
        )
    old = math.fsum(
        r["wall_seconds"] for r in cost["attempts"] if str(Path(r["path"]).parent) not in covered
    )
    cost["known_attempt_wall_seconds"] = old + process_seconds
    return cost


def inventory(
    matrix,
    *,
    stop_after=None,
    ceiling_hours=None,
    fallback_cell_seconds=None,
    receipt_root=None,
    matrix_hash=None,
):
    cells = ordered(matrix, stop_after)
    files = analysis.Files()
    rows = []
    for cell in cells:
        try:
            observed = analysis.load_cell(
                cell, files, "development" if matrix["scope"] == "development" else "confirmatory"
            )
            cost = charged_cost(cell, cell_cost(cell.get("result_dir")), receipt_root, matrix_hash)
        except (OSError, ValueError, KeyError, TypeError, PermissionError) as exc:
            observed = {
                "cell_id": cell["cell_id"],
                "status": "invalid",
                "artifact_complete": False,
                "missing_checkpoints": cell["checkpoints"],
                "error": str(exc),
            }
            cost = {
                "known_attempt_wall_seconds": 0.0,
                "unknown_attempts": [cell.get("result_dir")],
                "attempts": [],
            }
        rows.append(
            {
                "cell_id": cell["cell_id"],
                "block": cell["block_number"],
                "within_block_order": cell["within_block_order"],
                "condition": cell["condition"],
                "dataset": cell["dataset"],
                "observed": observed,
                "cost": cost,
            }
        )
    files.verify()
    blocks = []
    for block in sorted({c["block"] for c in rows}):
        group = [c for c in rows if c["block"] == block]
        incomplete = [c["cell_id"] for c in group if not c["observed"]["artifact_complete"]]
        blocks.append(
            {
                "block": block,
                "cells": len(group),
                "complete": not incomplete,
                "incomplete_cell_ids": incomplete,
            }
        )
    spent = math.fsum(r["cost"]["known_attempt_wall_seconds"] for r in rows)
    unknown = [p for r in rows for p in r["cost"]["unknown_attempts"]]
    remaining = []
    for c, r in zip(cells, rows, strict=True):
        if r["observed"]["artifact_complete"]:
            continue
        s = (c.get("ceilings") or {}).get("wall_seconds")
        if s is None:
            s = fallback_cell_seconds
        if s is not None and (isinstance(s, bool) or not math.isfinite(s) or s <= 0):
            raise ValueError("projection must be finite positive seconds")
        remaining.append(s)
    projected = (
        spent + math.fsum(remaining)
        if all(s is not None for s in remaining) and not unknown
        else None
    )
    return {
        "scope": matrix["scope"],
        "queue": rows,
        "blocks": blocks,
        "complete_blocks": [b["block"] for b in blocks if b["complete"]],
        "incomplete_cells": [
            {"cell_id": r["cell_id"], "missing_checkpoints": r["observed"]["missing_checkpoints"]}
            for r in rows
            if not r["observed"]["artifact_complete"]
        ],
        "cost": {
            "known_attempt_hours": spent / 3600,
            "unknown_attempts": unknown,
            "projected_total_hours": None if projected is None else projected / 3600,
            "ceiling_hours": ceiling_hours,
            "projected_within_ceiling": None
            if projected is None or ceiling_hours is None
            else projected <= ceiling_hours * 3600,
            "basis": "Driver attempt wall times once each, replaced by full child-process time when a queue receipt covers that attempt. Older cells exclude construction; missing process receipts make spend unknown. Remaining cells use whole-cell ceilings (conservative on partial cells), or the explicitly labeled scenario fallback.",
            "scenario_fallback_cell_seconds": fallback_cell_seconds,
        },
        "backend_status": "development and hash-bound sealed dispatch; final execution requires closed frozen gates",
        "sources_sha256": files.sources,
    }


def verify_sealed_matrix(matrix, bindings):
    """Owner execution only: full population metadata, never model/payload here.

    Contracts omit only the freeze reference, so neither final recipe nor matrix
    file hashes create a circular freeze dependency. Queue files remain immutable
    and hash-bound to each other throughout the invocation.
    """
    cells = analysis.validate_matrix(matrix)
    frozen_binding = None
    frozen_contracts = None
    for cell in cells:
        binding, m = recipe_for(cell, bindings)
        if m["mode"] != sealed.MODE or cell.get("admitted") is not True:
            raise PermissionError("every confirmatory slot needs sealed admitted recipe")
        if frozen_binding is None:
            frozen_binding = m["freeze"]
            frozen_contracts = sealed.metadata(frozen_binding)["recipe_contracts"]
        if frozen_binding != m["freeze"]:
            raise ValueError("one final freeze per matrix required")
        declared = sealed.read_binding(m["population"])
        if cell.get("population") != declared["cells"][cell["cell_id"]]:
            raise ValueError("matrix population differs from final frozen declaration")
        if cell.get("ceilings") != m.get("ceilings") or not cell.get("ceilings"):
            raise ValueError("matrix/recipe admitted resource ceilings required")
        seconds = cell["ceilings"].get("wall_seconds")
        if (
            isinstance(seconds, bool)
            or not isinstance(seconds, (int, float))
            or not math.isfinite(seconds)
            or seconds <= 0
        ):
            raise ValueError("positive admitted cell wall ceiling required")
        expected = sealed.OUTPUT_ROOT / sealed.cell_name(m, binding["sha256"])
        if Path(cell["result_dir"]).resolve() != expected.resolve():
            raise ValueError("noncanonical sealed destination")
    if frozen_contracts is None or set(frozen_contracts) != {c["cell_id"] for c in cells}:
        raise ValueError(
            "matrix must contain the entire frozen cell inventory; use stop-after for partial execution"
        )


def launch(binding, manifest, *, resume, output):
    if manifest.get("test_fixture"):
        raise PermissionError("TinyBase uses injected CPU executor in tests, not CLI launch")
    if manifest.get("mode") == sealed.MODE:
        if binding.get("backend") != sealed.backend_binding():
            raise ValueError("sealed launch backend binding mismatch")
        sealed.inspect_manifest(binding["path"], binding["sha256"])
        module = sealed.MODULE
    else:
        module = (
            "scripts.r1_64c_comparator_recipes"
            if "r1_64c" in manifest
            else "scripts.r1_68c_dev_cell"
        )
    if (
        manifest["cell"]["condition"].startswith("S1_")
        and "r1_64c" not in manifest
        and manifest.get("mode") != sealed.MODE
    ):
        raise ValueError("S1 requires the continued-NPZ comparator entry point")
    command = [sys.executable, "-m", module]
    if module == "scripts.r1_64c_comparator_recipes":
        command.append("run")
    command += ["--manifest", binding["path"], "--manifest-sha256", binding["sha256"], "--execute"]
    if resume:
        command.append("--resume")
    with Path(output).open("xb") as stream:
        deadline = datetime(2026, 10, 10, tzinfo=ZoneInfo("America/New_York")).timestamp()
        timeout = deadline - time.time()
        if timeout <= 0:
            raise TimeoutError("October 9 experimental deadline passed")
        result = subprocess.run(
            command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, check=False, timeout=timeout
        )
    return result.returncode


def run_queue(
    matrix_path,
    bindings_path,
    *,
    receipt_root,
    stop_after=None,
    min_memory_mib=4096.0,
    ceiling_hours=None,
    executor=launch,
    memory_reader=memory_available_mib,
):
    matrix_path, bindings_path = Path(matrix_path).resolve(), Path(bindings_path).resolve()
    matrix_hash, binding_hash = sha(matrix_path), sha(bindings_path)
    matrix, bindings = read(matrix_path), read(bindings_path)
    if matrix["scope"] not in ("development", "confirmatory"):
        raise PermissionError("explicit development or confirmatory matrix scope required")
    if bindings.get("matrix_sha256") != matrix_hash:
        raise ValueError("queue bindings reference a different matrix")
    if matrix["scope"] == "confirmatory":
        verify_sealed_matrix(matrix, bindings)
    if not math.isfinite(min_memory_mib) or min_memory_mib <= 0:
        raise ValueError("positive MemAvailable threshold required")
    if ceiling_hours is not None and (not math.isfinite(ceiling_hours) or ceiling_hours <= 0):
        raise ValueError("positive ceiling required")
    output = Path(receipt_root).resolve()
    if not output.is_relative_to(ROOT / "logs"):
        raise PermissionError("queue receipts belong under repo logs")
    output.mkdir(parents=True, exist_ok=True)
    # Stable lock per matrix prevents two invocations from selecting the same cell.
    lockroot = ROOT / "logs/r1_77_queue_locks"
    lockroot.mkdir(parents=True, exist_ok=True)
    lockpath = lockroot / f"queue-{matrix_hash}.lock"
    fd = os.open(lockpath, os.O_RDONLY | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for cell in ordered(matrix, stop_after):
            if sha(matrix_path) != matrix_hash or sha(bindings_path) != binding_hash:
                raise ValueError("queue inputs changed")
            observed = inventory(
                matrix,
                stop_after=stop_after,
                ceiling_hours=ceiling_hours,
                receipt_root=output,
                matrix_hash=matrix_hash,
            )
            if any(r["observed"]["status"] == "invalid" for r in observed["queue"]):
                raise ValueError("invalid existing cell; queue stops")
            row = next(r for r in observed["queue"] if r["cell_id"] == cell["cell_id"])
            # Even a completed cell must match its bound recipe before it is skipped.
            binding, manifest = recipe_for(cell, bindings)
            if row["observed"]["artifact_complete"]:
                verify_resume(cell, manifest)
                continue
            recipe_for(cell, bindings, execute=True)
            backend = sealed if manifest["mode"] == sealed.MODE else driver
            expected = backend.OUTPUT_ROOT / driver.cell_name(manifest, binding["sha256"])
            if Path(cell["result_dir"]).resolve() != expected.resolve():
                raise ValueError("matrix result directory differs from driver destination")
            if observed["cost"]["unknown_attempts"]:
                raise ValueError("unknown attempt costs; owner reconciliation required")
            if ceiling_hours is not None:
                seconds = (cell.get("ceilings") or {}).get("wall_seconds")
                if seconds is None:
                    raise ValueError("per-cell ceiling required for budget admission")
                if observed["cost"]["known_attempt_hours"] * 3600 + seconds > ceiling_hours * 3600:
                    return {"status": "budget_stop", "inventory": observed}
            mem = memory_reader()
            if not math.isfinite(mem) or mem < min_memory_mib:
                return {
                    "status": "memory_guard_stop",
                    "MemAvailable_MiB": mem,
                    "inventory": observed,
                }
            if datetime.now(ZoneInfo("America/New_York")).date().isoformat() > "2026-10-09":
                return {"status": "experiment_deadline_stop", "inventory": observed}
            resume = Path(cell["result_dir"]).exists()
            if resume:
                verify_resume(cell, manifest)
            attempt = output / f"{cell['cell_id']}-{uuid.uuid4().hex}"
            attempt.mkdir()
            before_attempts = {str(p.resolve()) for p in Path(cell["result_dir"]).glob("attempt-*")}

            def new_attempts(directory=cell["result_dir"], before=before_attempts):
                return sorted(
                    str(p.resolve())
                    for p in Path(directory).glob("attempt-*")
                    if str(p.resolve()) not in before
                )

            start = {
                "cell_id": cell["cell_id"],
                "matrix_sha256": matrix_hash,
                "bindings_sha256": binding_hash,
                "recipe": binding,
                "resume": resume,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "MemAvailable_MiB": mem,
                "producer_sha256": sha(__file__),
            }
            durable_json(attempt / "start.json", start)
            begun = time.monotonic()
            try:
                code = executor(binding, manifest, resume=resume, output=attempt / "process.log")
            except BaseException as exc:
                durable_json(
                    attempt / "finish.json",
                    {
                        **start,
                        "status": "executor_exception",
                        "exception": repr(exc),
                        "charged_process_wall_seconds": time.monotonic() - begun,
                        "start_sha256": sha(attempt / "start.json"),
                        "new_attempts": new_attempts(),
                    },
                )
                raise
            finish = {
                **start,
                "status": "process_exited",
                "exit_code": code,
                "charged_process_wall_seconds": time.monotonic() - begun,
                "start_sha256": sha(attempt / "start.json"),
                "new_attempts": new_attempts(),
            }
            durable_json(attempt / "finish.json", finish)
            after = inventory(
                matrix,
                stop_after=stop_after,
                ceiling_hours=ceiling_hours,
                receipt_root=output,
                matrix_hash=matrix_hash,
            )
            row = next(r for r in after["queue"] if r["cell_id"] == cell["cell_id"])
            if code != 0 or not row["observed"]["artifact_complete"]:
                return {"status": "cell_incomplete_stop", "exit_code": code, "inventory": after}
        return {
            "status": "selected_blocks_complete",
            "inventory": inventory(
                matrix,
                stop_after=stop_after,
                ceiling_hours=ceiling_hours,
                receipt_root=output,
                matrix_hash=matrix_hash,
            ),
        }
    finally:
        os.close(fd)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("status", "run"), nargs="?", default="status")
    p.add_argument("--matrix", type=Path, default=ROOT / "manifests/revision_v1/run_matrix_v5.json")
    p.add_argument("--bindings", type=Path)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--stop-after", type=int)
    p.add_argument("--ceiling-hours", type=float)
    p.add_argument("--scenario-cell-seconds", type=float)
    p.add_argument("--min-memory-mib", type=float, default=4096.0)
    p.add_argument("--receipt-root", type=Path, default=ROOT / "logs/r1_round18/queue_receipts")
    args = p.parse_args(argv)
    if args.command == "run" and not args.dry_run:
        if not args.execute or not args.bindings:
            p.error("execution needs --execute and --bindings; otherwise use --dry-run")
        report = run_queue(
            args.matrix,
            args.bindings,
            receipt_root=args.receipt_root,
            stop_after=args.stop_after,
            min_memory_mib=args.min_memory_mib,
            ceiling_hours=args.ceiling_hours,
        )
    else:
        if args.execute:
            p.error("--execute is incompatible with status/dry-run")
        report = inventory(
            read(args.matrix),
            stop_after=args.stop_after,
            ceiling_hours=args.ceiling_hours,
            fallback_cell_seconds=args.scenario_cell_seconds,
            receipt_root=args.receipt_root,
            matrix_hash=sha(args.matrix),
        )
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
