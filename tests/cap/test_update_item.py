"""CAP-07 (mock base): update_item visits every gold prefix incl. the terminator, records
per-prefix and per-item outcomes, charges every microstep; PC-3 idempotence on the mock."""

from pccap.cap.learn import update_item
from pccap.contracts import Budget
from pccap.harness.records import DecisionRecord
from pccap.routers import Full
from tests.cap.mock_base import make_cap, make_item


def test_prefixes_outcomes_and_ledger():
    base, cap = make_cap(arm="C1", radii=0.8)
    item = make_item(answer=(5, 6, 7))
    recs = []
    out = update_item(cap, item, Full(), Budget(A=2.0, R=5, tau_edit=0.1), on_decision=recs.append)
    assert len(out.prefix_outcomes) == 3
    assert all(set(p) >= {"prefix_index", "target", "loss_start", "loss_end", "rounds", "reached_threshold"} for p in out.prefix_outcomes)
    assert out.rounds_used == sum(p["rounds"] for p in out.prefix_outcomes) == len(recs)
    assert out.cost.prefix_microsteps == out.rounds_used
    assert all(isinstance(r, DecisionRecord) for r in recs)
    assert out.code in ("accepted", "acquisition_failure")
    assert cap.item_index == 1


def test_pc3_idempotence_on_mock():
    base, cap = make_cap(arm="C1", radii=0.8)
    item = make_item(answer=(5, 6))
    budget = Budget(A=3.0, R=5, tau_edit=0.1)
    out1 = update_item(cap, item, Full(), budget)
    occ = {m: bs.bank.occupancy() for m, bs in cap.banks.items()}
    out2 = update_item(cap, item, Full(), budget)
    if out1.acquired_threshold_all_prefixes:
        assert out2.rounds_used == 0 and out2.code == "accepted"
        assert {m: bs.bank.occupancy() for m, bs in cap.banks.items()} == occ  # no new slots
    else:  # acquisition failure is an outcome, not an exception
        assert out1.code == "acquisition_failure"


def test_use_count_once_per_item_through_learning():
    base, cap = make_cap(arm="C0", radii=0.8)
    item = make_item(answer=(5,))
    update_item(cap, item, Full(), Budget(A=3.0, R=5, tau_edit=0.1))
    bank = cap.banks[3].bank
    assert bank.meta["use_count"].max() <= 1
