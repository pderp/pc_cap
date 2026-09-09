"""PC-5 (search half): non-monotone loss handled without bracketing assumptions; the accepted
state equals the evaluated candidate byte-for-byte; a rejected search restores exactly and is charged."""

import numpy as np

from pccap.cap.learn import GRID, round_update
from pccap.contracts import Budget
from pccap.routers import Last
from tests.cap.mock_base import make_cap, make_item


def test_nonmonotone_candidates_pick_min_without_crash():
    base, cap = make_cap(arm="C0")
    item = make_item()
    ids = item.prompt_ids
    seq = iter([2.0, 1.9, 2.5, 1.7, 3.0, 1.7])  # baseline, four candidates (non-monotone), final
    cap.loss_of = lambda ep, target: next(seq)  # noqa: E731
    rr = round_update(cap, ids, 5, item, Last(), Budget(A=0.1), 0, 0)
    assert rr.route == [3] and "accepted" in [c.split(":")[0] for c in rr.codes]
    pb = rr.per_bank[3]
    assert [c["loss"] for c in pb["candidates"]] == [1.9, 2.5, 1.7, 3.0]
    assert pb["loss_after"] == 1.7 and rr.loss_after == 1.7
    # the accepted increment is the third grid point: a = A/b * 0.25 with b = 1
    a = 0.1 * GRID[2]
    assert abs(rr.accepted[3] - a) < 1e-7  # ||dv||/b_m = a since ||d|| = 1


def test_accepted_state_equals_evaluated_candidate_exactly():
    base, cap = make_cap(arm="C0", radii=0.5)
    item = make_item()
    ids = item.prompt_ids
    seen = {}
    orig = cap.loss_of

    def spy(ep, target):
        L = orig(ep, target)
        seen.setdefault("values", []).append(cap.banks[3].bank.values.copy())
        return L

    cap.loss_of = spy
    rr = round_update(cap, ids, 5, item, Last(), Budget(A=1.0), 0, 0)
    assert rr.per_bank[3]["code"] in ("accepted", "rejected_no_improvement")
    if rr.per_bank[3]["code"] == "accepted":
        cands = rr.per_bank[3]["candidates"]
        best_i = int(np.argmin([c["loss"] for c in cands]))
        evaluated = seen["values"][1 + best_i]  # index 0 is the baseline call
        assert np.array_equal(cap.banks[3].bank.values, evaluated)


def test_rejected_search_restores_exactly_and_is_charged():
    base, cap = make_cap(arm="C1", radii=0.5)
    item = make_item()
    ids = item.prompt_ids
    cap.loss_of = lambda ep, target: 2.0  # no candidate improves  # noqa: E731
    h = cap.state_hash()
    f0 = base.ledger.learning.full_forwards + base.ledger.learning.partial_forwards
    from pccap.routers import Full

    rr = round_update(cap, ids, 5, item, Full(), Budget(A=0.1), 0, 0)
    assert cap.state_hash() == h
    assert all(c.startswith("rejected_no_improvement") or c.startswith("no_direction") for c in rr.codes)
    assert rr.cost.search_candidates == 4 * len(rr.route)
    assert base.ledger.learning.full_forwards + base.ledger.learning.partial_forwards > f0
    assert all(bs.bank.occupancy() == 0 for bs in cap.banks.values())  # allocations rolled back
