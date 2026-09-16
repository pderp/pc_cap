"""HT-5 six-cell supervisor: one lease, 4h aggregate wall ceiling, memory guard.

Inspection is the default. Execution requires a hash-bound owner Q5 receipt.
All starts/results are new files; unknown interrupted spend refuses further work.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scripts.r1_68b_integrity_runtime import durable_json

from pccap.revision_v1.stage4_cell import ROOT, read_binding

BUDGET_SECONDS = 14400
ACCOUNTS = ROOT / "results/R1/stage4_dev_cells/ht_panel/_budget"
DEADLINE = datetime(2026, 10, 10, tzinfo=ZoneInfo("America/New_York")).timestamp()
MIN_AVAILABLE_BYTES = 3 * 1024**3


def spent(directory):
    total = 0.0
    starts = sorted(Path(directory).glob("*.start.json"))
    for path in starts:
        result = path.with_name(path.name.replace(".start.json", ".result.json"))
        if not result.exists():
            raise RuntimeError(
                "unclosed budget intent; reconcile unknown spend and orphan process before resuming"
            )
        start, end = json.loads(path.read_text()), json.loads(result.read_text())
        if start["intent_id"] != end["intent_id"]:
            raise ValueError("budget receipt identity mismatch")
        from pccap.revision_v1.stage4_cell import sha

        if end["start_sha256"] != sha(path):
            raise ValueError("budget start binding changed")
        value = end["charged_wall_seconds"]
        if not math.isfinite(value) or value < 0:
            raise ValueError("invalid charged time")
        total += value
    if len(list(Path(directory).glob("*.result.json"))) != len(starts):
        raise ValueError("orphan budget result")
    return total


def available_memory():
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) * 1024
    raise RuntimeError("MemAvailable missing")


def supervise(command, *, allowance, output, env, memory=available_memory):
    """Charge caller's setup + this child's entire lifetime; kill on resource limit."""
    if allowance <= 0 or time.time() >= DEADLINE:
        raise RuntimeError("budget/deadline exhausted")
    if memory() < MIN_AVAILABLE_BYTES:
        raise RuntimeError("less than 3 GiB MemAvailable")
    start = time.monotonic()
    child = None
    reason = "completed"
    with Path(output).open("xb") as log:
        try:
            child = subprocess.Popen(
                command, stdout=log, stderr=subprocess.STDOUT, env=env, start_new_session=True
            )
            while child.poll() is None:
                if time.monotonic() - start >= allowance:
                    reason = "budget_timeout"
                    break
                if time.time() >= DEADLINE:
                    reason = "experimental_deadline"
                    break
                if memory() < MIN_AVAILABLE_BYTES:
                    reason = "host_memory_guard"
                    break
                time.sleep(min(0.25, max(0.01, allowance - (time.monotonic() - start))))
        finally:
            if child is not None and child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
    return {
        "returncode": child.returncode,
        "reason": reason,
        "child_wall_seconds": time.monotonic() - start,
    }


def inspect(bundle_ref):
    from scripts import ht5_dev_cell as driver

    bundle = read_binding(bundle_ref)
    if bundle["mode"] != driver.MODE or bundle["budget_seconds"] != BUDGET_SECONDS:
        raise ValueError("development four-hour bundle required")
    cells = []
    for ref in bundle["recipes"]:
        manifest, _ = driver.load_development_cell(ref["path"], ref["sha256"])
        if (
            manifest.get("test_fixture")
            or manifest["reader_provenance"] != bundle["reader_provenance"]
        ):
            raise ValueError("real recipes must share selected primary")
        if manifest["ht_panel"] != bundle["ht_panel"]:
            raise ValueError("panel bindings differ")
        cells.append((manifest["cell"]["dataset"], manifest["cell"]["order"]))
    if len(cells) != 6 or set(cells) != {
        (ds, s) for ds in ("zsre", "counterfact", "mquake") for s in ("shuffled", "clustered")
    }:
        raise ValueError("exactly six unique declared cells required")
    return bundle


def execute(bundle_ref, approval_ref, *, resume=False):
    from scripts import ht5_dev_cell as driver

    from pccap.harness.lease import gpu_lease
    from pccap.revision_v1.stage4_cell import cell_name

    bundle = inspect(bundle_ref)
    approval = read_binding(approval_ref)
    if (
        approval.get("Q5_accepted") is not True
        or approval.get("launch_authorized") is not True
        or approval.get("bundle") != bundle_ref
        or approval.get("selected_primary") != bundle["reader_provenance"]["primary"]
        or approval.get("metadata_families_reviewed") is not True
    ):
        raise PermissionError("owner Q5 receipt must bind this bundle, primary and family review")
    ACCOUNTS.mkdir(parents=True, exist_ok=True)
    # Shared lease serializes account updates as well as GPU use.
    with gpu_lease(task="HT-5", stage="development stress panel", projected_seconds=BUDGET_SECONDS):
        for ref in bundle["recipes"]:
            manifest, _ = driver.load_development_cell(ref["path"], ref["sha256"])
            run = driver.OUTPUT_ROOT / cell_name(manifest, ref["sha256"])
            if run.exists() and not resume:
                raise FileExistsError("cell exists; use --resume after checking its receipts")
            if run.exists():
                # Even complete cells pass through the driver's resume validation;
                # no unchecked summary shortcut is allowed.
                cell_resume = True
            else:
                cell_resume = False
            remaining = min(BUDGET_SECONDS - spent(ACCOUNTS), DEADLINE - time.time())
            if remaining <= 0:
                raise RuntimeError("aggregate budget/deadline exhausted")
            number = len(list(ACCOUNTS.glob("*.start.json")))
            stem = f"{number:06d}"
            started = time.monotonic()
            intent = durable_json(
                ACCOUNTS / f"{stem}.start.json",
                {
                    "intent_id": stem,
                    "bundle": bundle_ref,
                    "recipe": ref,
                    "approval": approval_ref,
                    "pid": os.getpid(),
                    "started_epoch": time.time(),
                    "remaining_seconds": remaining,
                },
            )
            result = {"status": "error"}
            try:
                command = [
                    sys.executable,
                    "-B",
                    "-m",
                    "scripts.ht5_dev_cell",
                    "--manifest",
                    ref["path"],
                    "--manifest-sha256",
                    ref["sha256"],
                    "--execute",
                ]
                if cell_resume:
                    command.append("--resume")
                env = {
                    **os.environ,
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PCCAP_HT5_PARENT_PID": str(os.getpid()),
                }
                result.update(
                    supervise(
                        command,
                        allowance=remaining - (time.monotonic() - started),
                        output=ACCOUNTS / f"{stem}.child.log",
                        env=env,
                    )
                )
                result["status"] = (
                    "complete"
                    if result["returncode"] == 0 and result["reason"] == "completed"
                    else "error"
                )
            except BaseException as exc:
                result.update(error_type=type(exc).__name__, error=str(exc))
                raise
            finally:
                result.update(
                    intent_id=stem,
                    start_sha256=intent["sha256"],
                    charged_wall_seconds=time.monotonic() - started,
                    accounting="all child startup/construction/probes/retries/failures included",
                )
                durable_json(ACCOUNTS / f"{stem}.result.json", result)
            if result["status"] != "complete":
                raise RuntimeError("cell failed; failure retained in budget, queue stopped")
    return {"status": "complete", "charged_wall_seconds": spent(ACCOUNTS)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--bundle-sha256", required=True)
    ap.add_argument("--approval", type=Path)
    ap.add_argument("--approval-sha256")
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    ref = {"path": str(args.bundle.resolve()), "sha256": args.bundle_sha256}
    if args.execute:
        if not args.approval or not args.approval_sha256:
            ap.error("execution requires a bound Q5 approval receipt")
        result = execute(
            ref,
            {"path": str(args.approval.resolve()), "sha256": args.approval_sha256},
            resume=args.resume,
        )
    else:
        if args.resume:
            ap.error("--resume requires --execute")
        bundle = inspect(ref)
        result = {
            "cells": len(bundle["recipes"]),
            "model_constructed": False,
            "remaining_seconds": BUDGET_SECONDS - spent(ACCOUNTS),
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
