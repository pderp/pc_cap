#!/usr/bin/env python3
"""Expire closed sysmon/process-memory log files after 48 hours via logrotate.

A dry run is the default. Native logrotate deletes only the explicit, rechecked
eligible files; no glob, copytruncate, compression, or active-file rename is used.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
import re
import shutil
import stat
import subprocess
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = {
    "sysmon": re.compile(r"sysmon-\d{8}\.log(?:\.1)?"),
    "process_memory": re.compile(r"memory-[A-Za-z0-9_.-]+\.jsonl(?:\.1)?"),
}
DEFAULT_REPORTS = ROOT / "logs" / "monitor_retention"


def fingerprint(info):
    return [info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_nlink]


def open_log_inodes(proc=Path("/proc")):
    """Inspect our UID's accessible descriptors; fail closed for unreadable known loggers."""
    opened, denied = set(), 0
    for process in proc.iterdir():
        if not process.name.isdigit():
            continue
        try:
            if process.stat().st_uid != os.getuid():
                continue
            descriptors = list((process / "fd").iterdir())
            for descriptor in descriptors:
                try:
                    info = descriptor.stat()
                    if stat.S_ISREG(info.st_mode):
                        opened.add((info.st_dev, info.st_ino))
                except FileNotFoundError:
                    continue
        except (FileNotFoundError, ProcessLookupError):
            continue
        except PermissionError:
            denied += 1
            try:
                raw = (process / "cmdline").read_bytes()
            except OSError:
                raw = b""
            if b"process_memory_monitor.py" in raw or b"sysmon.sh" in raw:
                raise RuntimeError(
                    "cannot inspect a running logger's descriptors; retention refused"
                ) from None
    return opened, {"other_process_descriptor_denials": denied}


def plan_expiry(log_root, *, now_ns, retention_hours=48, opened=()):
    cutoff = now_ns - int(retention_hours * 3600 * 1e9)
    expired, kept = [], []
    today = dt.datetime.fromtimestamp(now_ns / 1e9).strftime("%Y%m%d")
    for family, pattern in FAMILIES.items():
        directory = Path(log_root) / family
        if not directory.exists():
            continue
        if directory.is_symlink():
            raise ValueError("monitor log directory may not be a symlink")
        for path in sorted(directory.iterdir()):
            if not pattern.fullmatch(path.name):
                continue
            info = path.lstat()
            reason = None
            if not stat.S_ISREG(info.st_mode):
                reason = "not_a_regular_file"
            elif info.st_uid != os.getuid() or info.st_nlink != 1:
                reason = "foreign_owner_or_hardlink"
            elif (info.st_dev, info.st_ino) in opened:
                reason = "open_file"
            elif family == "sysmon" and path.name == f"sysmon-{today}.log":
                reason = "current_sysmon_day"
            elif info.st_mtime_ns >= cutoff:
                reason = "within_retention"
            row = {
                "path": str(path.absolute()),
                "family": family,
                "bytes": info.st_size,
                "age_hours_since_last_write": (now_ns - info.st_mtime_ns) / 3.6e12,
                "fingerprint": fingerprint(info),
            }
            if reason is not None:
                kept.append({**row, "reason": reason})
            else:
                expired.append(row)
    return {
        "retention_hours": retention_hours,
        "cutoff_unix_ns": cutoff,
        "eligible": expired,
        "kept": kept,
        "eligible_bytes": sum(row["bytes"] for row in expired),
    }


def configuration(rows):
    if not rows:
        return "# No closed monitor logs older than the retention cutoff.\n"
    blocks = []
    for row in rows:
        path = row["path"]
        if not Path(path).is_absolute() or any(ch in path for ch in '"\\\n\r*?[]{}'):
            raise ValueError("unsafe literal logrotate path")
        blocks.append(
            f'"{path}" {{\n    rotate 0\n    nocreate\n    missingok\n'
            "    ifempty\n    nocompress\n    nodateext\n    size 0\n}\n"
        )
    return "\n".join(blocks)


def write_new(path, text):
    with Path(path).open("x") as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())


def perform(plan, directory, *, apply=False, binary=None, opened=()):
    """Recheck each inode/size/mtime before passing literal paths to logrotate."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    accepted, changed = [], []
    for row in plan["eligible"]:
        path = Path(row["path"])
        try:
            info = path.lstat()
        except FileNotFoundError:
            changed.append({"path": str(path), "reason": "already_removed"})
            continue
        if (
            fingerprint(info) != row["fingerprint"]
            or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or (info.st_dev, info.st_ino) in opened
        ):
            changed.append({"path": str(path), "reason": "changed_or_open"})
            continue
        accepted.append(row)
    config = directory / "logrotate.conf"
    write_new(config, configuration(accepted))
    write_new(directory / "plan.json", json.dumps(plan, indent=2) + "\n")
    result = {
        "mode": "apply" if apply else "dry_run",
        "selected": len(accepted),
        "skipped_on_recheck": changed,
        "deleted": [],
        "deleted_bytes": 0,
        "logrotate_returncode": None,
        "status": "ok",
    }
    if accepted and apply:
        executable = binary or shutil.which("logrotate")
        if executable is None:
            raise FileNotFoundError("logrotate executable not installed")
        command = [str(executable), "--force", "--state", "/dev/null", "--verbose", str(config)]
        result["command"] = command
        try:
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=30, check=False
            )
            result["logrotate_returncode"] = completed.returncode
            result["status"] = "ok" if completed.returncode == 0 else "error"
            write_new(directory / "logrotate.log", completed.stdout + completed.stderr)
        except (OSError, subprocess.TimeoutExpired) as error:
            result.update(status="error", error=str(error))
        for row in accepted:
            path = Path(row["path"])
            if not path.exists() and not Path(str(path) + ".1").exists():
                result["deleted"].append(row["path"])
                result["deleted_bytes"] += row["bytes"]
            elif result["status"] == "ok":
                result.update(
                    status="error", error="logrotate left an eligible file or intermediate archive"
                )
    write_new(directory / "result.json", json.dumps(result, indent=2) + "\n")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--retention-hours", type=float, default=48)
    args = parser.parse_args(argv)
    if not 0 < args.retention_hours < float("inf"):
        parser.error("--retention-hours must be finite and positive")
    # This workstation uses systemd as host PID 1; a coding sandbox sees only itself.
    if args.apply and Path("/proc/1/comm").read_text().strip() != "systemd":
        parser.error("--apply must run on this systemd host, not inside a restricted PID namespace")
    DEFAULT_REPORTS.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(DEFAULT_REPORTS / ".retention.lock", os.O_RDWR | os.O_CREAT, 0o600)
    with os.fdopen(descriptor, "rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        opened, coverage = open_log_inodes()
        plan = plan_expiry(
            ROOT / "logs",
            now_ns=time.time_ns(),
            retention_hours=args.retention_hours,
            opened=opened,
        )
        plan["descriptor_scan"] = coverage
        # Close the scan-to-action interval and notice newly opened files.
        reopened, _ = open_log_inodes()
        stamp = dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        directory = DEFAULT_REPORTS / f"run-{stamp}-{uuid.uuid4().hex[:8]}"
        result = perform(plan, directory, apply=args.apply, opened=opened | reopened)
        print(json.dumps({"report": str(directory), **result}))
        return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
