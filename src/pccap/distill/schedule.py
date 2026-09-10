"""Homotopy stages and the tracking-residual hold monitor (# reproduces hdpc/homotopy.py, commit 298fc719…).

* ``stages(error_lr, step_values)`` → ``HomotopyStage(error_lr, steps, original_rung)``, τ = error_lr·T.
* ``next_stage_end_step``: ``completed + max(1, ceil(remaining_steps / remaining_stages))`` — for
  9,766 steps and 7 stages this yields the sibling's realized boundaries 1396, 2791, 4186, 5581,
  6976, 8371 (its ``metrics.csv``; no hold ever fired there).
* ``TrackingResidualMonitor``: median baseline over a 64-step window, EMA 0.99, hold when the EMA
  exceeds ``baseline + 0.5·(1 − baseline)`` or 1.02, or the baseline itself is ≥ 1.
* ``subdivide_stage``: geometric-mean rung insertion, at most 2 per original rung.
"""

from __future__ import annotations

import dataclasses
import math
from collections import deque
from statistics import median

from pccap.distill import recipe as R


@dataclasses.dataclass(frozen=True)
class HomotopyStage:
    error_lr: float
    steps: int
    original_rung_start: int | None = None
    original_rung_end: int | None = None

    @property
    def tau(self) -> float:
        return self.error_lr * self.steps

    @property
    def original_rung(self) -> tuple[int, int] | None:
        if self.original_rung_start is None or self.original_rung_end is None:
            return None
        return (self.original_rung_start, self.original_rung_end)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "HomotopyStage":
        return cls(**d)


def stages(error_lr: float, step_values: list[int]) -> list[HomotopyStage]:
    out, prev = [], None
    for s in step_values:
        out.append(HomotopyStage(error_lr=error_lr, steps=int(s), original_rung_start=prev,
                                 original_rung_end=int(s) if prev is not None else None))
        prev = int(s)
    return out


def next_stage_end_step(completed_steps: int, total_steps: int, stage_index: int, stage_count: int) -> int:
    remaining_stages = max(1, stage_count - stage_index)
    remaining_steps = max(0, total_steps - completed_steps)
    return completed_steps + max(1, math.ceil(remaining_steps / remaining_stages))


def inner_energy_convergence_ratio(start: float, end: float, floor: float = 1e-9) -> float | None:
    if start < floor and end < floor:
        return None
    return end / max(start, floor)


def subdivide_stage(current: HomotopyStage, nxt: HomotopyStage, subdivision_counts: dict[tuple[int, int], int],
                    max_subdivisions: int = R.MAX_SUBDIVISIONS_PER_RUNG) -> HomotopyStage | None:
    original_rung = nxt.original_rung or (current.steps, nxt.steps)
    if subdivision_counts.get(original_rung, 0) >= max_subdivisions:
        return None
    subdivided = max(current.steps + 1, int(round(math.sqrt(current.steps * nxt.steps))))
    if subdivided >= nxt.steps:
        return None
    subdivision_counts[original_rung] = subdivision_counts.get(original_rung, 0) + 1
    return HomotopyStage(error_lr=current.error_lr, steps=subdivided, original_rung_start=original_rung[0],
                         original_rung_end=original_rung[1])


class TrackingResidualMonitor:
    def __init__(self, ema_decay: float = 0.99, window_steps: int = 64, headroom_fraction: float = R.HOLD_HEADROOM_FRACTION,
                 absolute_threshold: float = R.HOLD_ABSOLUTE_THRESHOLD):
        self.ema_decay, self.window_steps = float(ema_decay), int(window_steps)
        self.headroom_fraction, self.absolute_threshold = float(headroom_fraction), float(absolute_threshold)
        self.baseline: float | None = None
        self.ema: float | None = None
        self.updates = 0
        self.values: deque[float] = deque()
        self.last_hold_reason = ""

    def enter_stage(self) -> None:
        self.baseline = None
        self.ema = None
        self.updates = 0
        self.values.clear()
        self.last_hold_reason = ""

    def update(self, ratio: float) -> bool:
        self.values.append(float(ratio))
        if len(self.values) > self.window_steps:
            self.values.popleft()
        self.updates += 1
        if len(self.values) >= self.window_steps:
            self.baseline = float(median(self.values))
            if self.ema is None:
                self.ema = self.baseline
            else:
                self.ema = self.ema_decay * self.ema + (1.0 - self.ema_decay) * float(ratio)
        return self.should_hold

    @property
    def hold_threshold(self) -> float:
        if self.baseline is None:
            return math.inf
        return self.baseline + self.headroom_fraction * (1.0 - self.baseline)

    @property
    def should_hold(self) -> bool:
        self.last_hold_reason = ""
        if self.baseline is None or self.ema is None:
            return False
        if self.baseline >= 1.0:
            self.last_hold_reason = "pathological_baseline"
            return True
        if self.ema > self.absolute_threshold:
            self.last_hold_reason = "absolute_threshold"
            return True
        if self.ema > self.hold_threshold:
            self.last_hold_reason = "headroom_threshold"
            return True
        return False

    def to_dict(self) -> dict:
        return {"ema_decay": self.ema_decay, "window_steps": self.window_steps, "headroom_fraction": self.headroom_fraction,
                "absolute_threshold": self.absolute_threshold, "baseline": self.baseline, "ema": self.ema,
                "updates": self.updates, "values": list(self.values), "last_hold_reason": self.last_hold_reason}

    @classmethod
    def from_dict(cls, d: dict) -> "TrackingResidualMonitor":
        m = cls(d["ema_decay"], d["window_steps"], d["headroom_fraction"], d["absolute_threshold"])
        m.baseline, m.ema, m.updates = d["baseline"], d["ema"], int(d["updates"])
        m.values = deque(float(v) for v in d["values"])
        m.last_hold_reason = d["last_hold_reason"]
        return m
