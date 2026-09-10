"""SE-E credit rule on the mock base (CPU): ``CapConfig(credit="error")`` takes the settled error at
the site as the credit signal with the wrapper's descent sign and charges the inference's own cost
(iters+1 forwards/reverses, settle_iters). With a one-step mock (e = −lr·∂L/∂h) the direction equals the
adjoint direction, so the two credit rules make identical decisions; only the cost differs."""

from __future__ import annotations

import numpy as np

from pccap.cap.learn import update_item
from pccap.contracts import Budget, CostRecord, ErrorResult, SiteId
from pccap.routers import Full
from pccap.transport.transport import Transport
from tests.cap.mock_base import BANK_BLOCK, make_cap, make_item


class ErrorMock:
    """Wraps a MockBase with an ePC-like ``infer_errors``: errors after one SGD step from zero."""

    descent_sign = +1.0

    def __init__(self, base, iters: int = 8, lr: float = 0.1):
        self._b, self.iters, self.lr = base, iters, lr

    def __getattr__(self, k):
        return getattr(self._b, k)

    def infer_errors(self, ids, target, iters=8, writes=(), phase="learning"):
        grads = self._b.adjoint(ids, target, writes, phase=phase)
        p = len(np.asarray(ids).reshape(-1)) - 1
        site_errors = {SiteId(m, BANK_BLOCK[m], p): -self.lr * np.asarray(grads[SiteId(m, BANK_BLOCK[m], p)]) for m in (1, 2, 3)}
        cost = CostRecord(phase=phase, full_forwards=iters + 1, reverses=iters + 1, settle_iters=iters)
        self._b.ledger.charge(cost)
        return ErrorResult(errors={}, site_errors=site_errors, energies=[1.0] * (iters + 1), grad_norm_0=1.0, grad_norm_k=0.5,
                           r_k=0.5, iters=iters, logits=None, cost=cost, solver={"mock": True})

    @staticmethod
    def error_at_site(result, bank):
        for site, e in result.site_errors.items():
            if site.bank == bank:
                return e
        raise KeyError(bank)


def test_error_credit_matches_adjoint_decisions_and_charges_inference():
    _, cap_a = make_cap(arm="C1", radii=0.8, seed=3)
    _, cap_e = make_cap(arm="C1", radii=0.8, seed=3)
    cap_e.base = ErrorMock(cap_e.base, iters=8)
    cap_e.cfg.credit, cap_e.cfg.credit_iters = "error", 8
    item = make_item(answer=(5, 6, 7))
    out_a = update_item(cap_a, item, Full(), Budget(A=0.3), Transport())
    out_e = update_item(cap_e, item, Full(), Budget(A=0.3), Transport())
    assert out_a.code == out_e.code
    la = [po["loss_end"] if isinstance(po, dict) else po.loss_end for po in out_a.prefix_outcomes]
    le = [po["loss_end"] if isinstance(po, dict) else po.loss_end for po in out_e.prefix_outcomes]
    np.testing.assert_allclose(la, le, rtol=1e-5)  # identical directions up to float32 normalization
    # exact same memories written (identical unit directions)
    for m in cap_a.banks:
        assert np.allclose(cap_a.banks[m].bank.values, cap_e.banks[m].bank.values, atol=1e-5)
    # cost: the error rule charges settle iterations and iters+1 forwards/reverses per credit computation
    assert out_a.cost.settle_iters == 0 and out_e.cost.settle_iters > 0
    assert out_e.cost.reverses > out_a.cost.reverses
    assert out_e.cost.settle_iters % 8 == 0
