"""Cost ledger (S0-03; PDF App. B "Cost ledger"; plan §4.5 rule 5, §4.7).

The ledger lives *outside* learner state: it is never serialized into a snapshot and never
rolled back. Every base call is wrapped in ``ledger.call(...)`` which records wall time and
device time (JAX has no CUDA-event API; device time is measured as wall time around
``jax.block_until_ready`` on the call's outputs and labelled ``accel_seconds`` with that
convention) and increments the operation counters the caller declares.

Two columns are kept: ``query`` (read-only evaluation, probes charged to a query) and
``learning``. ``totals()`` returns both plus their sum; ``write(run_dir)`` writes ``cost.json``.
"""

from __future__ import annotations

import contextlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

import jax

from pccap.contracts import CostRecord


def _peak_mem_mib() -> float:
    try:
        dev = jax.devices()[0]
        stats = dev.memory_stats()
        if stats and "peak_bytes_in_use" in stats:
            return stats["peak_bytes_in_use"] / (1024 * 1024)
    except Exception:  # pragma: no cover - CPU backend
        pass
    return 0.0


@dataclass
class Ledger:
    query: CostRecord = field(default_factory=lambda: CostRecord(phase="query"))
    learning: CostRecord = field(default_factory=lambda: CostRecord(phase="learning"))
    events: int = 0
    started: float = field(default_factory=time.time)

    def column(self, phase: str) -> CostRecord:
        if phase == "query":
            return self.query
        if phase == "learning":
            return self.learning
        raise ValueError(phase)

    def charge(self, rec: CostRecord) -> None:
        """Add a call's CostRecord to its phase column."""
        self.column(rec.phase).add(rec)
        self.events += 1

    @contextlib.contextmanager
    def call(self, phase: str, **counters: int | float) -> Iterator[CostRecord]:
        """Time a base call. Usage::

            with ledger.call("learning", full_forwards=1) as rec:
                out = base_fn(...)
                rec.outputs = out          # optional: block_until_ready is applied to it

        Counters are added on exit; ``accel_seconds`` and ``wall_seconds`` are measured.
        """
        rec = CostRecord(phase=phase)
        for k, v in counters.items():
            setattr(rec, k, getattr(rec, k) + v)
        t0 = time.perf_counter()
        try:
            yield rec
        finally:
            out = getattr(rec, "outputs", None)
            if out is not None:
                jax.block_until_ready(out)
                try:
                    delattr(rec, "outputs")
                except AttributeError:
                    pass
            dt = time.perf_counter() - t0
            rec.wall_seconds += dt
            rec.accel_seconds += dt
            rec.peak_mem_mib = max(rec.peak_mem_mib, _peak_mem_mib())
            self.charge(rec)

    def totals(self) -> dict[str, Any]:
        total = CostRecord(phase="learning")
        total.add(self.query)
        total.add(self.learning)
        return {
            "query": self.query.as_dict(),
            "learning": self.learning.as_dict(),
            "total": {**total.as_dict(), "phase": "total"},
            "events": self.events,
            "elapsed_wall_seconds": time.time() - self.started,
            "accel_time_convention": "wall time around jax.block_until_ready (no CUDA events in JAX)",
        }

    def write(self, run_dir: Path | str) -> Path:
        p = Path(run_dir) / "cost.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.totals(), indent=1, sort_keys=True) + "\n")
        return p


def append_task_cost(path: Path | str, task_id: str, gpu_seconds: float, wall_seconds: float,
                     peak_mem_mib: float = 0.0, note: str = "") -> None:
    """Append one line to results/ledger/tasks.jsonl (plan §4.2 step 8)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as f:
        f.write(
            json.dumps(
                {
                    "task": task_id,
                    "gpu_seconds": gpu_seconds,
                    "wall_seconds": wall_seconds,
                    "peak_mem_mib": peak_mem_mib,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "note": note,
                }
            )
            + "\n"
        )
