from __future__ import annotations

from pccap.contracts import CostRecord, RoundContext, RouteDecision
from pccap.harness.records import OutcomeCode


def usable_banks(ctx: RoundContext, candidates) -> tuple[list[int], list[str]]:
    """Banks in increasing depth order that have a direction; ``no_direction`` codes for the rest."""
    banks, codes = [], []
    for m in sorted(candidates):
        d = ctx.directions.get(m)
        if d is None or d.status != "ok" or d.direction is None:
            codes.append(f"{OutcomeCode.no_direction.value}:{m}")
        else:
            banks.append(m)
    return banks, codes


def decision(banks, scores, codes, rule, cost=None, abstain=None) -> RouteDecision:
    return RouteDecision(banks=list(banks), scores=dict(scores), abstain=(not banks) if abstain is None else abstain,
                         cost=cost or CostRecord(phase="learning"), codes=list(codes), rule=rule)
