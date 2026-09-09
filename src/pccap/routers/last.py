"""C0: schedule the last bank only (PDF §7 C0; F.3 step 4)."""

from __future__ import annotations

from pccap.contracts import RoundContext, RouteDecision
from pccap.routers._common import decision, usable_banks


class Last:
    name = "C0"

    def schedule(self, ctx: RoundContext) -> RouteDecision:
        banks, codes = usable_banks(ctx, [3])
        return decision(banks, {}, codes, self.name)
