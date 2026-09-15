"""Production comparator adapters exercised on the actual tiny CPU base."""

from dataclasses import replace

import numpy as np
import pytest

from pccap.contracts import CostRecord
from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import (
    CORE_CONDITIONS,
    SECONDARY_CONDITION,
    CellAdapter,
    build_adapter,
)
from tests.revision_v1.test_endpoints import Cap, Tokenizer
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.tiny_base import TinyBase

CAL = {"radii": {"1": 0.0, "2": 0.0, "3": 0.0}, "bank_scales": {"1": 1.0, "2": 1.0, "3": 1.0}}


@pytest.mark.parametrize("condition", [*CORE_CONDITIONS, SECONDARY_CONDITION])
def test_actual_tiny_all_condition_reads_restore_and_observers(condition):
    base, ledger = TinyBase(), Ledger()
    cfg = _cfg()
    cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
    kw = {"revision_config": cfg} if condition.startswith("R1_") else {}
    adapter = build_adapter(
        condition, base, ledger, calibration=CAL, synthetic=True, locality_base=base, **kw
    )
    state = adapter.export_state().clone()
    before = adapter.state_hash()
    ids = np.int32([2, 3])
    adapter.reset_queries()
    result = adapter.predict(ids)
    assert np.all(np.isfinite(result.logits)) and result.cost.full_forwards > 0
    observed = adapter.observe_firing(ids)
    adapter.import_state(state)
    assert adapter.state_hash() == before
    view = adapter.observe()
    assert view["memory_status"] == "ok"
    assert view["memory"]["occupied_bytes"] >= 0
    if condition.startswith("R1_"):
        assert observed["false_fire"] is False
        assert adapter.cfg.rare_overlap_min == (1 if condition == "R1_learned_ff" else None)
        assert adapter.cfg.min_score == (0.93 if condition == "R1_nonlearned" else None)
        assert view["active_records"] == 0
    else:
        assert observed is None and view["active_records"] is None and view["active_slots"] == 0
        assert adapter.memory_inventory([]) == []
    if condition == "matched_update":
        assert adapter.rule.steps == 5
    assert adapter.identity()["condition"] == condition


def test_real_missing_weights_and_s1_reference_refused():
    with pytest.raises(ValueError, match="pinned"):
        build_adapter("R1_learned_ff", TinyBase(), Ledger(), calibration=CAL)
    with pytest.raises(ValueError, match="original base"):
        build_adapter("S1_LM", TinyBase(), Ledger(), calibration=CAL)


def test_missing_observer_not_zero_and_behavioral_rejection_not_resource():
    from types import SimpleNamespace

    cap = Cap(Tokenizer())
    cap.update_item = lambda item: SimpleNamespace(
        code="acquisition_failure", codes=["no_improvement"], cost=CostRecord(phase="learning")
    )
    adapter = CellAdapter(cap, "v0_stable")
    assert adapter.observe()["memory"] is None
    out = adapter.update_item(None)
    assert (
        out.code == "rejected_no_improvement"
        and adapter.last_original_outcome == "acquisition_failure"
    )
    assert out.cost.phase == "learning"


def test_real_slot_owner_must_match_history():
    adapter = build_adapter("v0_stable", TinyBase(), Ledger(), calibration=CAL, synthetic=True)
    bank = adapter.banks[1].bank
    bank.metadata.on_allocate(0, 0.0, 1, b"a" * 16, 1, 3)
    with pytest.raises(ValueError, match="owner"):
        adapter.memory_inventory([])
    assert adapter.observe()["active_slots"] == 1
    assert adapter.observe()["active_records"] is None
