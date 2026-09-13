"""Stable observations (design §observations): one unedited base pass per prefix, tapped at the v0 bank blocks.

The encoder never applies writes and never mutates the base. ``last`` is the residual entering the tapped block at the
last position; ``span`` is the masked mean of the same residual over the prompt span. Because the base is causal, the
features of a prefix depend only on that prefix (gate 4; tested with a synthetic causal base and on the real base).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pccap.contracts import CostRecord
from pccap.revision_v1.contracts import TAPS, Observation

ENCODER_VERSION = 1


@dataclass
class ObservationEncoder:
    base: object  # anything with forward(ids, (), retain_sites=True, phase=..., last_only=True) -> hidden{tap: [T, d]}, cost
    taps: tuple[int, ...] = TAPS
    encoder_version: int = ENCODER_VERSION
    phase: str = "query"

    def __post_init__(self) -> None:
        cs = getattr(self.base, "checksum", None)
        self.base_hash = str(cs()) if callable(cs) else "unknown"
        self.d = int(getattr(self.base, "d", 0))

    def observe(self, ids, mask=None, keep_rows: bool = False) -> tuple[Observation, CostRecord]:
        """One unedited pass. ``mask`` (bool [T]) marks the prompt span; default: every position."""
        ids = np.asarray(ids, np.int32).reshape(-1)
        T = int(ids.shape[0])
        if T == 0:
            raise ValueError("empty prefix")
        if mask is None:
            mask = np.ones(T, bool)
        mask = np.asarray(mask, bool).reshape(-1)
        if mask.shape[0] != T:
            raise ValueError(f"mask length {mask.shape[0]} != prefix length {T}")
        if not mask.any():
            raise ValueError("mask selects no position")
        fr = self.base.forward(ids, (), retain_sites=True, phase=self.phase, last_only=True)
        last, span, rows = {}, {}, {}
        for m in self.taps:
            h = np.asarray(fr.hidden[m], np.float32)[:T]
            last[m] = np.ascontiguousarray(h[T - 1])
            span[m] = np.ascontiguousarray(h[mask].mean(axis=0, dtype=np.float32))
            if keep_rows:
                rows[m] = h
        obs = Observation(ids=ids, mask=mask, last=last, span=span, base_hash=self.base_hash, encoder_version=self.encoder_version)
        if keep_rows:
            object.__setattr__(obs, "_rows", rows)
        return obs, fr.cost

    def observe_many(self, prefixes: list, masks: list | None = None) -> tuple[list[Observation], CostRecord]:
        total = CostRecord(phase=self.phase)  # type: ignore[arg-type]
        out = []
        for i, ids in enumerate(prefixes):
            obs, c = self.observe(ids, None if masks is None else masks[i])
            total.add(c)
            out.append(obs)
        return out, total


def prompt_mask(prompt_len: int, total_len: int) -> np.ndarray:
    """Span mask covering the prompt tokens of a prompt+answer-prefix sequence."""
    if not 0 < prompt_len <= total_len:
        raise ValueError((prompt_len, total_len))
    m = np.zeros(total_len, bool)
    m[:prompt_len] = True
    return m
