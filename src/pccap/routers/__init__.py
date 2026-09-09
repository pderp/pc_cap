"""Delivery rules (PDF F.3 steps 3-4; CAP-05): Last (C0), Full (C1), Measured (C2), Random (CR),
Supplied (CO). Every router receives only a ``RoundContext`` (SD-4) and returns a ``RouteDecision``;
zero-direction banks are logged with ``no_direction`` and never scheduled."""

from pccap.routers.full import Full
from pccap.routers.last import Last
from pccap.routers.measured import Measured
from pccap.routers.random_ import Random
from pccap.routers.supplied import Supplied

__all__ = ["Full", "Last", "Measured", "Random", "Supplied", "make_router"]


def make_router(arm: str, **kw):
    return {"C0": Last, "C1": Full, "C2": Measured, "CR": Random, "CO": Supplied}[arm](**kw)
