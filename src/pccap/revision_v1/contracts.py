"""Revision v1 contracts (docs/revision_v1_design.md §Records, §API; DEC-033/DEC-034).

v0 contracts (``pccap.contracts``) are adapted here, never edited. Episode containers are the installed generator's
(``pccap.revision_v1.episodes``): support carries teaching labels, queries carry none, and labels live only in
``LabeledEpisode.query_labels`` — ``predict`` never receives them (gate 1).
"""

from __future__ import annotations

import hashlib
import inspect
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

from pccap.contracts import CostRecord, EditItem
from pccap.revision_v1.episodes import (  # noqa: F401  (re-exported episode containers)
    EpisodeInputs,
    LabeledEpisode,
    PredictionQuery,
    QueryLabel,
    SupportExample,
)

TAPS: tuple[int, ...] = (1, 2, 3)  # v0 bank indices; the base maps them to blocks 3/7/11


@dataclass(frozen=True)
class Observation:
    """Features of one prefix from a single unedited base pass (stable observations, guide §1)."""

    ids: np.ndarray  # int32 [T]
    mask: np.ndarray  # bool [T]; True on the prompt span used for the span summary
    last: dict[int, np.ndarray]  # tap -> float32 [d] residual at the last position
    span: dict[int, np.ndarray]  # tap -> float32 [d] masked mean over the prompt span
    base_hash: str
    encoder_version: int

    @property
    def length(self) -> int:
        return int(self.ids.shape[0])

    def taps(self) -> tuple[int, ...]:
        return tuple(sorted(self.last))


@dataclass
class MemoryRecord:
    """One bounded memory record. ``record_id`` is immutable; revisions supersede, never overwrite."""

    record_id: str
    fact_id: str
    revision_id: int
    created_order: int
    key: np.ndarray  # float32 [dk]
    code: np.ndarray  # float32 [d_code] fast state (the only thing ``adapt`` may change on an existing record)
    provenance: tuple[str, ...] = ()  # support ids that produced this record
    source_ids: np.ndarray | None = None  # int32 [S] support prefix tokens kept for key rebuilds (counted)
    delta: np.ndarray | None = None  # float32 [n_banks, d] fast-state write taught from support (counted; zero when absent)
    active: bool = True
    superseded_by: str | None = None

    @property
    def source_tokens(self) -> int:
        return 0 if self.source_ids is None else int(self.source_ids.shape[0])


@dataclass(frozen=True)
class RetrievalCandidate:
    record_id: str
    distance: float
    rank: int


@dataclass
class RevisionCost(CostRecord):
    """v0 ledger counters plus the revision extension (design §API)."""

    extra_pass_forwards: int = 0
    reader_flops: float = 0.0
    records_touched: int = 0
    rebuild_seconds: float = 0.0

    def add(self, other: CostRecord) -> "RevisionCost":  # type: ignore[override]
        super().add(other)
        for k in ("extra_pass_forwards", "reader_flops", "records_touched", "rebuild_seconds"):
            setattr(self, k, getattr(self, k) + getattr(other, k, 0))
        return self


@dataclass
class PredictResult:
    logits: np.ndarray  # [V] at the last position
    trace: dict[str, Any]  # per tap: candidates, scores, null mass, chosen record, write norms
    cost: RevisionCost


@dataclass
class AdaptResult:
    state: Any  # the new CapState (fast state only may differ)
    trace: dict[str, Any]
    cost: RevisionCost


@dataclass
class OuterResult:
    params: Any
    metrics: dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------------------------- adapters
def support_from_edit_item(item: EditItem, revision: int | None = None, record_id: str | None = None) -> SupportExample:
    """A v0 edit item as a support example (prompt/answer tokens; scoring aliases and paraphrases are NOT carried)."""
    fact_id = item.fact_id or item.item_id
    rev = int(item.version if revision is None else revision)
    rid = record_id or f"{item.dataset or 'v0'}:{item.item_id}:r{rev}"
    return SupportExample(record_id=rid, fact_id=str(fact_id), revision=rev, entity_id=str(fact_id), family_id=str(item.dataset or "v0"),
                          prompt_ids=tuple(int(x) for x in np.asarray(item.prompt_ids)), answer_ids=tuple(int(x) for x in np.asarray(item.answer_ids)),
                          prompt=item.prompt, answer=item.answer)


def query_from_ids(query_id: str, ids, prompt: str = "") -> PredictionQuery:
    return PredictionQuery(query_id=query_id, prompt_ids=tuple(int(x) for x in np.asarray(ids)), prompt=prompt)


def support_prefix(s: SupportExample, t: int) -> np.ndarray:
    """prompt + answer[:t] as int32 ids (t = answer-prefix index, as in v0's decision records)."""
    return np.asarray(tuple(s.prompt_ids) + tuple(s.answer_ids)[:t], np.int32)


def digest_ids(ids) -> str:
    return hashlib.sha256(np.asarray(ids, np.int32).tobytes()).hexdigest()[:16]


def assert_no_target_parameter(fn: Callable, forbidden: tuple[str, ...] = ("target", "targets", "label", "labels", "answer", "answer_ids", "y")) -> None:
    """Gate 1 (design §Gates): a read path has no parameter through which a target could arrive."""
    names = set(inspect.signature(fn).parameters)
    bad = sorted(names & set(forbidden))
    if bad:
        raise TypeError(f"{getattr(fn, '__qualname__', fn)} exposes target-like parameters {bad}")
