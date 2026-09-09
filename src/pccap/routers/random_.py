"""CR: one bank from a fixed distribution, RNG keyed by (seed, item digest, prefix index, round)
(PDF §7 CR; F.3 step 4; SD-11). The same key gives the same choice in any replay order."""

from __future__ import annotations

import hashlib
import random

from pccap.contracts import RoundContext, RouteDecision
from pccap.routers._common import decision, usable_banks

UNIFORM = {1: 1 / 3, 2: 1 / 3, 3: 1 / 3}


class Random:
    name = "CR"

    def __init__(self, distribution: dict[int, float] | None = None, label: str = "cr_profile_uniform"):
        dist = dict(distribution or UNIFORM)
        tot = sum(dist.values())
        if tot <= 0:
            raise ValueError("distribution must have positive mass")
        self.distribution = {int(k): float(v) / tot for k, v in sorted(dist.items())}
        self.label = label

    @staticmethod
    def keyed_rng(rng_material) -> random.Random:
        seed, digest, prefix_index, rnd = rng_material
        h = hashlib.sha256(f"{seed}|{bytes(digest).hex()}|{prefix_index}|{rnd}".encode()).digest()
        return random.Random(int.from_bytes(h[:8], "little"))

    def draw(self, rng_material) -> int:
        r = self.keyed_rng(rng_material)
        u = r.random()
        acc = 0.0
        banks = list(self.distribution)
        for m in banks:
            acc += self.distribution[m]
            if u < acc:
                return m
        return banks[-1]

    def schedule(self, ctx: RoundContext) -> RouteDecision:
        m = self.draw(ctx.rng_material)
        banks, codes = usable_banks(ctx, [m])
        codes.append(f"cr_draw:{m}")
        return decision(banks, {}, codes, self.name)
