import pccap  # noqa: F401 # isort: skip

# isort: split

import numpy as np
import pytest

from aw.pc_matched_credit import MatchedCreditCap, units
from aw.tests.test_pc_v0 import TinyEPC
from pccap.cap.cap import Cap, CapConfig
from pccap.contracts import Budget, EditItem
from pccap.routers import make_router


def item():
    return EditItem(
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


def cap(allowance):
    b = TinyEPC()
    cfg = CapConfig(d=b.d, credit="adjoint", radii={m: 0.5 for m in (1, 2, 3)})
    return MatchedCreditCap(b, cfg, b.ledger, allowances={"tiny": allowance})


def test_useful_updates_spend_reference_budget_without_padding():
    c = cap(150)
    base_before = c.base.checksum(recompute=True)
    rows, budgets = [], []
    c.on_decision, c.on_budget = rows.append, budgets.append
    result = c.update_item(item(), make_router("C1"), Budget(R=1, A=0.3, tau_edit=0))
    assert result.rounds_used > 1  # extra budget buys actual further acquisition rounds
    assert len(rows) == result.rounds_used
    assert result.cost.reverses > 1 and result.cost.settle_iters == 0
    assert units(result.cost) <= 150 and 150 - units(result.cost) <= 1
    assert any(r.loss_after < r.loss_before for r in rows)
    assert c.base.checksum(recompute=True) == base_before
    assert budgets[0]["stop"] == "operation_allowance"
    assert c.clone().state_hash() == c.state_hash()


def test_partial_round_restores_state_but_charges_work():
    c = cap(4)  # prefix prediction + round prediction + adjoint; no search fits
    before = Cap.export_state(c)
    result = c.update_item(item(), make_router("C1"), Budget(R=5, A=0.3, tau_edit=0))
    assert units(result.cost) == 4 and result.rounds_used == 0
    after = Cap.export_state(c)
    for key in before.arrays:
        np.testing.assert_array_equal(before.arrays[key], after.arrays[key])
    assert after.use_tracker == (None, [])
    assert c.item_index == 1


def test_threshold_stops_without_wasting_allowance():
    c = cap(1000)
    result = c.update_item(item(), make_router("C1"), Budget(R=5, tau_edit=100))
    assert result.acquired_threshold_all_prefixes and result.rounds_used == 0
    assert units(result.cost) == 1


def test_missing_budget_refuses_and_snapshot_binds_allowance():
    c = cap(10)
    other = cap(12)
    with pytest.raises(ValueError, match="allowance"):
        other.restore(c.serialize())
    it = item()
    it.item_id = "absent"
    with pytest.raises(ValueError, match="missing"):
        c.update_item(it, make_router("C1"), Budget())


def test_allowance_measured_from_actual_eight_step_reference():
    base = TinyEPC()
    reference = Cap(
        base,
        CapConfig(d=base.d, credit="error", credit_iters=8, radii={m: 0.5 for m in (1, 2, 3)}),
        base.ledger,
    )
    out = reference.update_item(item(), make_router("C1"), Budget(R=1, A=0.3, tau_edit=0))
    allowance = units(out.cost)
    matched = cap(allowance)
    attempts = []
    matched.on_budget = attempts.append
    got = matched.update_item(item(), make_router("C1"), Budget(R=1, A=0.3, tau_edit=0))
    # This small allowance funds another real search attempt but not a whole
    # additional transactional round; the incomplete round must roll back.
    assert attempts[0]["attempted_rounds"] > out.rounds_used
    assert 0 <= allowance - units(got.cost) < 2
    assert got.cost.settle_iters == 0
