"""Interface contracts v0 (updated_plan2.md §5; PDF F.7).

This module holds the shared dataclasses and Protocols and nothing else. It is frozen at ENV-03;
changes are proposed as ``docs/tasks/<ID>.patch`` and applied by the orchestrator. Arrays are
``jax.Array`` on the device side and ``numpy.ndarray`` on the host side; ``Tensor`` accepts both.

Design notes
* ``SiteId`` identifies a residual-stream site: bank m in {1,2,3}, the block whose output is read
  (GPT-2 small: 3, 7, 11 = HF ``transformer.h[l]`` outputs, the last before ``ln_f``; SD-7), and
  the token position p (the last input position in v0).
* ``Write`` is an additive correction at exactly one site.
* ``CostRecord`` carries the Appendix B ledger counters for one call; the harness ledger sums
  them by phase (query vs learning).
* ``Metric`` is the structured value of PDF Appendix D: every ratio carries operands and a
  status; undefined/unreachable/unsupported/unavailable are distinct from NaN.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, NamedTuple, Protocol, Sequence, TypedDict, Union

import jax
import numpy as np

Tensor = Union[jax.Array, np.ndarray]

MetricStatus = Literal["ok", "undefined", "unreachable", "unsupported", "unavailable"]


class SiteId(NamedTuple):
    bank: int
    block: int
    position: int


@dataclass(frozen=True)
class Write:
    """Additive write of ``vector`` (shape [d]) to the residual at ``site`` (position p only)."""

    site: SiteId
    vector: Tensor


@dataclass
class CostRecord:
    """Ledger counters for one call (PDF App. B "Cost ledger"; plan §4.7).

    ``phase`` is "query" or "learning"; the ledger keeps the two columns separate.
    """

    phase: Literal["query", "learning"] = "learning"
    full_forwards: int = 0
    partial_forwards: int = 0
    reverses: int = 0
    settle_iters: int = 0
    prefix_microsteps: int = 0
    router_probes: int = 0
    search_candidates: int = 0
    memory_search_seconds: float = 0.0
    wall_seconds: float = 0.0
    accel_seconds: float = 0.0
    peak_mem_mib: float = 0.0
    tokens: int = 0

    def add(self, other: "CostRecord") -> "CostRecord":
        for k in (
            "full_forwards",
            "partial_forwards",
            "reverses",
            "settle_iters",
            "prefix_microsteps",
            "router_probes",
            "search_candidates",
            "memory_search_seconds",
            "wall_seconds",
            "accel_seconds",
            "tokens",
        ):
            setattr(self, k, getattr(self, k) + getattr(other, k))
        self.peak_mem_mib = max(self.peak_mem_mib, other.peak_mem_mib)
        return self

    def as_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class ForwardResult:
    """Logits ``[T, V]`` for one prefix, pre-write residual sites, and the call's cost."""

    logits: Tensor
    sites: dict[SiteId, Tensor]
    cost: CostRecord
    hidden: dict[int, Tensor] = field(default_factory=dict)  # block index -> [T, d] when retained


@dataclass
class ErrorResult:
    """Finite-iteration ePC error inference (PDF D.6; SD-6).

    ``errors`` maps every error site (block index 0..D-1) to the terminal error tensor ``[T, d]``;
    ``site_errors`` restricts to the three bank sites at position p. ``energies`` is
    ``[E_0, ..., E_k]``. ``r_k`` is ``||grad_e E_k|| / max(1, ||grad_e E_0||)`` computed explicitly
    at the terminal iterate.
    """

    errors: dict[int, Tensor]
    site_errors: dict[SiteId, Tensor]
    energies: list[float]
    grad_norm_0: float
    grad_norm_k: float
    r_k: float
    iters: int
    logits: Tensor
    cost: CostRecord
    solver: dict = field(default_factory=dict)  # error_lr, gamma, init, reduction, dtype


@dataclass
class DirectionResult:
    """Unit descent direction at a site, or an explicit no-direction outcome."""

    site: SiteId
    direction: Tensor | None
    status: Literal["ok", "no_direction"]
    signal_norm: float
    projected: bool = False


@dataclass
class RouteDecision:
    """Output of a Router for one round (PDF F.3 steps 3-4)."""

    banks: list[int]  # scheduled banks in increasing depth order; empty when abstaining
    scores: dict[int, float]  # signed probe scores (C2) or empty
    abstain: bool
    cost: CostRecord
    codes: list[str] = field(default_factory=list)  # e.g. no_direction:1, abstain
    rule: str = ""


@dataclass
class RevisionEvent:
    """Correction-track revision metadata (PDF E.2; SD-4). Only present on that track."""

    fact_id: str
    version: int
    previous_version: int | None
    fact_digest: bytes  # 16 bytes


@dataclass
class EditItem:
    """One immutable edit (x, y_1..M) with scoring-only aliases and evaluation prompt sets."""

    item_id: str
    digest: bytes  # 16-byte owner-edit digest (sha256(item_id|prompt|answer)[:16])
    prompt: str
    answer: str  # canonical answer WITHOUT the trailing newline; tokens include "\n"
    aliases: list[str]
    paraphrases: list[str]
    locality_prompts: list[str]
    prompt_ids: np.ndarray  # int32 [Tp]
    answer_ids: np.ndarray  # int32 [M], including the terminating newline token
    dataset: str = ""
    fact_id: str | None = None
    version: int = 1
    revision: RevisionEvent | None = None
    strata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class Budget:
    """F.6 numerics for one arm (frozen at S4)."""

    A: float = 0.1  # aggregate normalized write budget per round
    epsilon: float = 0.01  # probe size
    R: int = 5  # rounds per prefix
    tau_edit: float = 0.1  # stop loss (nats)
    search_trials: int = 4  # geometric candidates per bank per round (plus no-op)
    improvement_abs: float = 1e-8
    improvement_rel: float = 1e-6

    def min_improvement(self, loss: float) -> float:
        return max(self.improvement_abs, self.improvement_rel * loss)


@dataclass
class RoundContext:
    """What a Router may see (SD-4, PC-8): no slot metadata, no answers, no digests except as
    opaque RNG key material."""

    prefix_ids: np.ndarray
    loss: float
    directions: dict[int, DirectionResult]  # bank -> direction at that bank's site
    bank_scales: dict[int, float]  # b_m
    rng_material: tuple[int, bytes, int, int]  # (seed, item digest, prefix index, round)
    permitted_banks: tuple[int, ...] | None = None  # CO only
    position: int = 0


@dataclass
class ItemOutcome:
    """Item-level outcome of ``Cap.update_item`` (F.3), with per-prefix records."""

    item_id: str
    code: str  # closed enum in pccap.harness.records.OutcomeCode
    acquired_threshold_all_prefixes: bool
    prefix_outcomes: list[dict]
    rounds_used: int
    cost: CostRecord
    codes: list[str] = field(default_factory=list)


@dataclass
class MemoryReport:
    """Bytes as PDF App. B "Memory ceiling" requires (allocated and occupied, per bank, indices)."""

    allocated_bytes: int
    occupied_bytes: int
    per_bank: dict[int, dict]
    index_bytes: int
    key_dim: int
    value_dim: int
    occupancy: dict[int, float]
    ceiling_bytes: int = 0


class Metric(TypedDict):
    value: float | None
    status: MetricStatus
    units: str
    numerator: float | None
    denominator: float | None
    n: int
    strata: dict
    exclusions: list


def metric(
    value: float | None,
    *,
    units: str,
    numerator: float | None = None,
    denominator: float | None = None,
    n: int = 0,
    strata: dict | None = None,
    exclusions: list | None = None,
    status: MetricStatus = "ok",
) -> Metric:
    """Build a ``Metric``. A non-``ok`` status forces ``value`` to ``None`` (never NaN)."""
    if status != "ok":
        value = None
    elif value is not None and not np.isfinite(value):
        raise ValueError("metric(): non-finite value with status ok; use an explicit status")
    return Metric(
        value=None if value is None else float(value),
        status=status,
        units=units,
        numerator=None if numerator is None else float(numerator),
        denominator=None if denominator is None else float(denominator),
        n=int(n),
        strata=dict(strata or {}),
        exclusions=list(exclusions or []),
    )


class Base(Protocol):
    """Frozen base wrapper (PDF F.1, F.7)."""

    D: int
    d: int
    sites: list[SiteId]

    def forward(
        self, ids: Tensor, writes: Sequence[Write] = (), retain_sites: bool = False
    ) -> ForwardResult: ...

    def forward_from(
        self, bank: int, hidden: Tensor, ids: Tensor, writes: Sequence[Write] = ()
    ) -> ForwardResult:
        """Resume the block loop after bank ``bank``'s site given ``hidden`` ([T, d], with any
        earlier writes already applied). Counted as a partial forward."""
        ...

    def adjoint(self, ids: Tensor, target: int, writes: Sequence[Write]) -> dict[SiteId, Tensor]:
        """One reverse pass; ``dL/dh`` at every site for ``L = CE(logits[p], target)``."""
        ...

    def checksum(self) -> str:
        """SHA-256 over parameters and persistent buffers."""
        ...


class EPCBase(Base, Protocol):
    def infer_errors(
        self, ids: Tensor, target: int | None, iters: int, writes: Sequence[Write] = ()
    ) -> ErrorResult: ...


class Transport(Protocol):
    def direction(
        self, signal: Tensor, site: SiteId, allowed_subspace: Tensor | None
    ) -> DirectionResult: ...


class Router(Protocol):
    def schedule(self, ctx: RoundContext) -> RouteDecision: ...


class Cap(Protocol):
    def predict(self, ids: Tensor) -> ForwardResult: ...

    def update_item(self, item: EditItem, router: Router, budget: Budget) -> ItemOutcome: ...

    def serialize(self) -> bytes: ...

    def restore(self, blob: bytes) -> None: ...

    def clone(self) -> "Cap": ...

    def memory_bytes(self) -> MemoryReport: ...


__all__ = [
    "Any",
    "Base",
    "Budget",
    "Cap",
    "CostRecord",
    "DirectionResult",
    "EPCBase",
    "EditItem",
    "ErrorResult",
    "ForwardResult",
    "ItemOutcome",
    "MemoryReport",
    "Metric",
    "MetricStatus",
    "RevisionEvent",
    "RoundContext",
    "RouteDecision",
    "Router",
    "SiteId",
    "Tensor",
    "Transport",
    "Write",
    "metric",
]
