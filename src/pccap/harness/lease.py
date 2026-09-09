"""GPU lease (plan §4.5 rule 2).

Any process that will use CUDA for more than 60 s first acquires ``results/.gpu_lease`` with an
``fcntl`` exclusive lock and writes ``{pid, task, stage, projected_seconds, started}`` into it.
One lease at a time. ``exclusive=True`` additionally captures ``nvidia-smi --query-compute-apps``
before and after so that throughput profiles can prove no other CUDA process was running.

Usage::

    with gpu_lease("S2-06", stage="S2", projected_seconds=3600, exclusive=True) as lease:
        ...
    lease.report  # dict with before/after compute-app lists and timings
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[3]
LEASE_PATH = ROOT / "results" / ".gpu_lease"


def compute_apps() -> list[dict]:
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
            text=True,
            timeout=20,
        )
    except Exception as e:  # pragma: no cover
        return [{"error": str(e)}]
    apps = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 3:
            apps.append({"pid": parts[0], "name": parts[1][:80], "used_memory": parts[2]})
    return apps


class Lease:
    def __init__(self, task: str, stage: str, projected_seconds: float, exclusive: bool,
                 path: Path = LEASE_PATH):
        self.task, self.stage, self.projected, self.exclusive = task, stage, projected_seconds, exclusive
        self.path = path
        self.report: dict = {}
        self._fh = None

    def __enter__(self) -> "Lease":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "a+")
        t0 = time.time()
        fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX)  # blocks until free
        self.report["waited_seconds"] = time.time() - t0
        self.report["started"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self._fh.seek(0)
        self._fh.truncate()
        self._fh.write(
            json.dumps(
                {
                    "pid": os.getpid(),
                    "task": self.task,
                    "stage": self.stage,
                    "projected_seconds": self.projected,
                    "started": self.report["started"],
                    "exclusive": self.exclusive,
                }
            )
        )
        self._fh.flush()
        if self.exclusive:
            self.report["compute_apps_before"] = compute_apps()
        return self

    def __exit__(self, *exc) -> None:
        if self.exclusive:
            self.report["compute_apps_after"] = compute_apps()
        self.report["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        try:
            self._fh.seek(0)
            self._fh.truncate()
        finally:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            self._fh.close()

    def other_cuda_processes(self, own_pid: int | None = None) -> list[dict]:
        """Compute apps other than this process (desktop processes count: they must be reported)."""
        own = str(own_pid or os.getpid())
        return [a for a in self.report.get("compute_apps_before", []) if a.get("pid") != own]


@contextlib.contextmanager
def gpu_lease(task: str, stage: str = "", projected_seconds: float = 0.0,
              exclusive: bool = False, path: Path = LEASE_PATH) -> Iterator[Lease]:
    lease = Lease(task, stage, projected_seconds, exclusive, path)
    with lease:
        yield lease


def current_holder(path: Path = LEASE_PATH) -> dict | None:
    if not path.exists():
        return None
    txt = path.read_text().strip()
    return json.loads(txt) if txt else None
