"""PC-6 (write budget): aggregate normalized increment <= A on 100 random rounds; C0/C1/C2/CR
share the byte ceiling."""

import numpy as np

from pccap.cap import memory
from pccap.cap.learn import round_update
from pccap.contracts import Budget
from pccap.routers import Full
from tests.cap.mock_base import make_cap, make_item


def test_aggregate_increment_bounded_over_random_rounds():
    rng = np.random.default_rng(0)
    base, cap = make_cap(arm="C1", radii=0.8)
    budget = Budget(A=0.1)
    accepted_rounds = 0
    for i in range(100):
        item = make_item(f"it{i}", prompt=tuple(rng.integers(0, 32, size=3)), answer=(int(rng.integers(0, 32)),))
        rr = round_update(cap, item.prompt_ids, int(item.answer_ids[0]), item, Full(), budget, 0, i)
        assert rr.aggregate_normalized <= budget.A * (1 + 1e-6)
        accepted_rounds += bool(rr.accepted)
    assert accepted_rounds > 0


def test_arms_share_the_byte_ceiling():
    caps = {arm: make_cap(arm=arm)[1] for arm in ("C0", "C1", "C2", "CR")}
    ceilings = {arm: c.memory_bytes().ceiling_bytes for arm, c in caps.items()}
    assert len(set(ceilings.values())) == 1 == len({memory.b_cap(8)} | set(ceilings.values()))
    for _arm, c in caps.items():
        assert sum(lay.ceiling_bytes for lay in c.layouts.values()) == memory.b_cap(8)
        assert c.memory_bytes().allocated_bytes <= memory.b_cap(8)
