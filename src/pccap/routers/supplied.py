"""CO: schedule the supplied permitted banks in depth order (PDF §7 CO; E.1 oracle only)."""

from __future__ import annotations

from pccap.contracts import RoundContext, RouteDecision
from pccap.routers._common import decision, usable_banks


class Supplied:
    name = "CO"

    def schedule(self, ctx: RoundContext) -> RouteDecision:
        if ctx.permitted_banks is None:
            raise ValueError("CO requires permitted_banks in the RoundContext (fixture only)")
        banks, codes = usable_banks(ctx, list(ctx.permitted_banks))
        return decision(banks, {}, codes, self.name)
