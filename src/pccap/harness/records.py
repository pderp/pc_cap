"""Closed outcome-code enum and decision records (S0-03; PDF F.7, Op. rule 8).

Outcome codes are strings, never numbers, so they can never be confused with a NaN in a
computation graph. ``docs/outcome_codes.md`` lists every code, its meaning and where it is
emitted; ``tests/harness/test_records.py`` checks that the document and this enum agree.
"""

from __future__ import annotations

import dataclasses
import json
import math
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class OutcomeCode(str, Enum):
    # candidate / round level
    accepted = "accepted"
    rejected_no_improvement = "rejected_no_improvement"
    no_direction = "no_direction"
    abstain = "abstain"
    ambiguous_key_conflict = "ambiguous_key_conflict"
    evicted = "evicted"
    # item level
    acquisition_failure = "acquisition_failure"
    # measurement level (PDF App. D)
    unreachable = "unreachable"
    undefined = "undefined"
    unsupported = "unsupported"
    unavailable = "unavailable"
    # run level
    resource_stop = "resource_stop"
    nonfinite_failure = "nonfinite_failure"
    # correction track (SD-4)
    revision_replaced = "revision_replaced"
    revision_replayed = "revision_replayed"


class RunStatus(str, Enum):
    complete = "complete"
    resource_stop = "resource_stop"
    correctness_failure = "correctness_failure"
    running = "running"


ALL_CODES: tuple[str, ...] = tuple(c.value for c in OutcomeCode)


def is_code(x: Any) -> bool:
    return isinstance(x, str) and x in ALL_CODES


def _finite_or_none(x: float | None) -> float | None:
    if x is None:
        return None
    x = float(x)
    if math.isnan(x) or math.isinf(x):
        raise ValueError("non-finite value in a decision record; emit nonfinite_failure instead")
    return x


@dataclass
class DecisionRecord:
    """One routing/search decision (PDF F.7). All cost counters are copied from the ledger."""

    item_digest: str  # hex of the 16-byte owner-edit digest
    prefix_index: int
    round: int
    candidate_banks: list[int]
    signed_scores: dict[str, float]  # bank (as str) -> r_m
    chosen_route: list[int]
    accepted_increment: dict[str, float]  # bank -> ||dv||/b_m accepted (0 if rejected)
    loss_before: float
    loss_after: float
    codes: list[str]  # allocation / conflict / eviction / abstain codes for this round
    cost: dict[str, Any]
    rule: str = ""
    per_bank: dict[str, dict] = field(default_factory=dict)  # bank -> {candidates, chosen_a, code}

    def __post_init__(self) -> None:
        self.loss_before = _finite_or_none(self.loss_before)
        self.loss_after = _finite_or_none(self.loss_after)
        for c in self.codes:
            if not is_code(c):
                raise ValueError(f"unknown outcome code {c!r}")

    def to_json(self) -> str:
        return json.dumps(dataclasses.asdict(self), sort_keys=True)


def append_jsonl(path: Path | str, rec: DecisionRecord | dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = rec.to_json() if isinstance(rec, DecisionRecord) else json.dumps(rec, sort_keys=True)
    with open(path, "a") as f:
        f.write(line + "\n")


def read_jsonl(path: Path | str) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def write_error_json(run_dir: Path | str, exc: BaseException, item_id: str | None, tb: str) -> Path:
    """Op. rule 8: any exception writes error.json and the run becomes correctness_failure."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    p = run_dir / "error.json"
    p.write_text(
        json.dumps(
            {
                "status": RunStatus.correctness_failure.value,
                "exception": type(exc).__name__,
                "message": str(exc),
                "item_id": item_id,
                "traceback": tb,
            },
            indent=1,
        )
    )
    return p
