"""C1: schedule all three banks (PDF §7 C1; F.3 step 4)."""

from __future__ import annotations

from pccap.contracts import RoundContext, RouteDecision
from pccap.routers._common import decision, usable_banks


class Full:
    name = "C1"

    def schedule(self, ctx: RoundContext) -> RouteDecision:
        banks, codes = usable_banks(ctx, [1, 2, 3])
        return decision(banks, {}, codes, self.name)
