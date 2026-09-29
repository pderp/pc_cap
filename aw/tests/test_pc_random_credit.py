import pccap  # noqa: F401 # isort: skip

# isort: split

import numpy as np
import pytest

from aw.pc_random_credit import RandomCreditCap, RandomTransport
from aw.tests.test_pc_v0 import TinyEPC
from pccap.cap import learn
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem, SiteId
from pccap.routers import make_router
from pccap.transport.transport import Transport


def fixture(seed=23):
    base = TinyEPC()
    cfg = CapConfig(
        d=base.d, seed=seed, credit="error", credit_iters=8, radii={m: 0.5 for m in (1, 2, 3)}
    )
    return RandomCreditCap(base, cfg, base.ledger)


def test_norm_zero_and_independent_orientation():
    signal = np.float32([1, 2, -3, 4])
    transport = RandomTransport(Transport(), np.random.default_rng(22))
    site = SiteId(1, 3, 2)
    a, b = (transport.direction(signal, site) for _ in range(2))
    assert a.signal_norm == pytest.approx(np.linalg.norm(signal), rel=2e-6)
    assert np.linalg.norm(a.direction) == pytest.approx(1, rel=2e-6)
    assert not np.allclose(a.direction, b.direction)
    assert not np.allclose(a.direction, -signal / np.linalg.norm(signal))
    assert transport.direction(np.zeros(4), site).status == "no_direction"
    with pytest.raises(FloatingPointError):
        transport.direction(np.full(4, np.nan), site)


def test_real_credit_reproduces_seed_cost_and_snapshot():
    cap = fixture()
    before = cap.serialize()
    ids = np.int32([4, 11])
    directions = cap.kernel["directions_at"]
    original = learn.directions_at
    eviction_rng = cap.rng.getstate()
    cost_before = cap.ledger.totals()["learning"]
    a = directions(cap, ids, 17, {}, Transport())
    extra = directions.last_extra_cost
    assert (extra.full_forwards, extra.reverses, extra.settle_iters) == (9, 9, 8)
    after = cap.ledger.totals()["learning"]
    assert after["reverses"] - cost_before["reverses"] == 9
    assert after["full_forwards"] - cost_before["full_forwards"] == 9
    assert cap.rng.getstate() == eviction_rng
    assert learn.directions_at is original
    cap.restore(before)
    b = directions(cap, ids, 17, {}, Transport())
    for bank in a:
        np.testing.assert_array_equal(a[bank].direction, b[bank].direction)
    cloned = cap.clone()
    assert cloned.state_hash() == cap.state_hash()
    left = directions(cap, ids, 17, {}, Transport())
    right = cloned.kernel["directions_at"](cloned, ids, 17, {}, Transport())
    for bank in left:
        np.testing.assert_array_equal(left[bank].direction, right[bank].direction)


def test_actual_update_preserves_base_and_records_decisions():
    cap = fixture()
    item = EditItem(
        item_id="tiny",
        digest=b"0" * 16,
        prompt="p",
        answer="a",
        aliases=["a"],
        prompt_ids=np.int32([4, 11]),
        answer_ids=np.int32([17]),
        dataset="tiny",
        paraphrases=[],
        locality_prompts=[],
    )
    original_memory = Cap.export_state(cap).content_hash()
    base_before = cap.base.checksum(recompute=True)
    rows = []
    cap.on_decision = rows.append
    out = cap.update_item(item, make_router("C1"), Budget(R=1, A=0.3))
    assert rows and out.cost.reverses > 0
    assert out.cost.reverses == sum(row.cost["reverses"] for row in rows)
    assert out.cost.reverses == 9 * (out.cost.settle_iters // 8)
    assert cap.base.checksum(recompute=True) == base_before
    assert Cap.export_state(cap).content_hash() != original_memory
    before = cap.state_hash()
    cap.predict(np.int32([4, 11]))
    assert cap.state_hash() == before


def test_driver_plan_and_frozen_module_isolation():
    from aw import pc_random_run, pc_v0

    original = pc_v0.build_cap
    plan = pc_random_run.plan()
    assert len(plan["cells"]) == 12 and not plan["model_execution"]
    assert {c["arm"] for c in plan["cells"]} == {"SE-A", "SE-R"}
    assert plan["credit"]["SE-R"]["control_treatment"]["credit"] == "random"
    assert pc_v0.build_cap is original
    with pytest.raises(ValueError):
        pc_random_run.settings("SE-R", 32)
