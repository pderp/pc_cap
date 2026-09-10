"""SE-E credit on the real ePC wrapper (GPU, short): one round with ``credit="error"`` on BP weights
reduces the item loss, charges settle iterations, and its bank-3 direction has positive cosine with the
adjoint direction (P6 measured cos ≈ 0.998 at bank 3 for e₈)."""

from __future__ import annotations

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.bases.epc import EPCBase
from pccap.cap.cap import Cap, CapConfig
from pccap.cap.learn import directions_at, update_item
from pccap.contracts import Budget
from pccap.harness.ledger import Ledger
from pccap.harness.stage_s2 import load_dev_items
from pccap.routers import Full
from pccap.transport.transport import Transport

pytestmark = pytest.mark.gpu


def test_error_credit_round_on_epc_wrapper():
    ledger = Ledger()
    base = EPCBase(ledger=ledger)
    item = load_dev_items("zsre", 1, seed=7)[0][0]
    ids = np.asarray(item.prompt_ids, np.int32)
    target = int(item.answer_ids[0])
    radii = {1: 0.3, 2: 0.4, 3: 0.2}
    cap_e = Cap(base, CapConfig(arm="C1", radii=radii, seed=0, credit="error", credit_iters=8), ledger)
    cap_a = Cap(base, CapConfig(arm="C1", radii=radii, seed=0), ledger)
    d_e = directions_at(cap_e, ids, target, {}, Transport())
    d_a = directions_at(cap_a, ids, target, {}, Transport())
    cos3 = float(np.dot(np.asarray(d_e[3].direction), np.asarray(d_a[3].direction)))
    assert d_e[3].status == "ok" and cos3 > 0.9, cos3
    out = update_item(cap_e, item, Full(), Budget(A=0.3), Transport())
    assert out.cost.settle_iters >= 8
    first = out.prefix_outcomes[0]
    l0, l1 = (first["loss_start"], first["loss_end"]) if isinstance(first, dict) else (first.loss_start, first.loss_end)
    assert l1 < l0
