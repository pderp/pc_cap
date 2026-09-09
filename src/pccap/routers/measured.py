"""C2: measured routing by signed loss-improving probes (PDF F.3 step 3; PC-5).

For each bank with a direction, a temporary forced write ``ε·b_m·d_m`` (ε = 0.01) is applied on
top of the current cap state and the downstream forward is recomputed **with live discrete
retrieval** (``probe_fn``, supplied by the cap; nothing is committed). Score
``r_m = (L − L_probe) / ε``. Select the bank with the largest positive score whose loss
reduction exceeds ``max(1e-8, 1e-6·L)``; ties → smallest bank index (SD-16); otherwise abstain.
Probe cost is charged (``router_probes``).
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from pccap.contracts import CostRecord, RoundContext, RouteDecision
from pccap.harness.records import OutcomeCode
from pccap.routers._common import decision, usable_banks

ProbeFn = Callable[[int, np.ndarray], float]  # (bank, write vector) -> probed loss


class Measured:
    name = "C2"

    def __init__(self, probe_fn: ProbeFn, epsilon: float = 0.01, improvement_abs: float = 1e-8,
                 improvement_rel: float = 1e-6):
        self.probe_fn = probe_fn
        self.epsilon = float(epsilon)
        self.improvement_abs = improvement_abs
        self.improvement_rel = improvement_rel

    def schedule(self, ctx: RoundContext) -> RouteDecision:
        banks, codes = usable_banks(ctx, [1, 2, 3])
        L = float(ctx.loss)
        scores: dict[int, float] = {}
        cost = CostRecord(phase="learning")
        for m in banks:
            d = np.asarray(ctx.directions[m].direction, np.float32)
            probe = np.float32(self.epsilon * ctx.bank_scales[m]) * d
            L_probe = float(self.probe_fn(m, probe))
            if not np.isfinite(L_probe):
                raise FloatingPointError(f"non-finite probed loss at bank {m}")  # Op. rule 8
            scores[m] = (L - L_probe) / self.epsilon
            cost.router_probes += 1
        threshold = max(self.improvement_abs, self.improvement_rel * L)
        best, best_score = None, 0.0
        for m in sorted(scores):  # increasing depth: ties keep the smallest index
            improvement = scores[m] * self.epsilon
            if scores[m] > 0 and improvement > threshold and scores[m] > best_score:
                best, best_score = m, scores[m]
        if best is None:
            codes.append(OutcomeCode.abstain.value)
            return decision([], scores, codes, self.name, cost=cost, abstain=True)
        return decision([best], scores, codes, self.name, cost=cost, abstain=False)
