"""S0-03: ledger counts survive a simulated learner rollback; phases stay separate."""

import copy

import jax.numpy as jnp

from pccap.contracts import CostRecord
from pccap.harness.ledger import Ledger


class MockLearner:
    def __init__(self):
        self.state = {"values": [0.0, 0.0], "counter": 0}

    def snapshot(self):
        return copy.deepcopy(self.state)

    def restore(self, snap):
        self.state = copy.deepcopy(snap)


def test_ledger_outside_rollback():
    ledger = Ledger()
    learner = MockLearner()
    snap = learner.snapshot()
    with ledger.call("learning", full_forwards=1, search_candidates=4) as rec:
        learner.state["values"][0] = 1.0
        learner.state["counter"] += 1
        rec.outputs = jnp.ones(3) * 2
    before = ledger.totals()["learning"]["full_forwards"]
    learner.restore(snap)  # rejected candidate: learner state rolls back
    after = ledger.totals()["learning"]["full_forwards"]
    assert learner.state == snap
    assert before == after == 1
    assert ledger.learning.search_candidates == 4
    assert ledger.learning.wall_seconds > 0 and ledger.learning.accel_seconds > 0


def test_phases_separate_and_total_sums():
    ledger = Ledger()
    with ledger.call("query", full_forwards=2):
        pass
    with ledger.call("learning", reverses=1, router_probes=3):
        pass
    t = ledger.totals()
    assert t["query"]["full_forwards"] == 2 and t["learning"]["full_forwards"] == 0
    assert t["learning"]["reverses"] == 1 and t["query"]["reverses"] == 0
    assert t["total"]["full_forwards"] == 2 and t["total"]["router_probes"] == 3
    assert ledger.events == 2


def test_costrecord_add_keeps_peak_max():
    a = CostRecord(peak_mem_mib=10, full_forwards=1)
    b = CostRecord(peak_mem_mib=5, full_forwards=2)
    a.add(b)
    assert a.peak_mem_mib == 10 and a.full_forwards == 3


def test_cost_json_validates(tmp_path):
    from pccap.harness import schema

    ledger = Ledger()
    with ledger.call("learning", full_forwards=1):
        pass
    p = ledger.write(tmp_path)
    import json

    schema.validate("cost", json.loads(p.read_text()))
