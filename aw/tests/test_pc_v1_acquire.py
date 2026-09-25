"""PC-2 parity, sign/cost, support boundary, rollback and deployment tests."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
from dataclasses import asdict, replace

import numpy as np
import pytest
from tests.revision_v1.tiny_base import TinyBase

from aw.pc_v1_acquire import PCRevisionCap, adapt_record
from aw.tests.test_pc_v0 import TinyEPC
from aw.tests.test_wrapper import _cfg, _queries, _support
from pccap.contracts import CostRecord, ErrorResult, SiteId
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig
from pccap.revision_v1.adapt import adapt_record as original_adapt
from pccap.revision_v1.contracts import support_from_edit_item
from pccap.revision_v1.controller import aggregate
from pccap.revision_v1.learner import RevisionCap


def cfg():
    c = _cfg()
    c.fast = FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=0.1)
    return c


def test_adjoint_bitwise_state_predictions_cost_and_no_global_changes():
    from pccap.revision_v1 import adapt as installed
    from pccap.revision_v1 import learner as installed_learner

    identities = (installed.adapt_record, installed._delta_steps, installed_learner.adapt_record)
    a, b = RevisionCap(TinyBase(), cfg(), Ledger()), PCRevisionCap(TinyBase(), cfg(), Ledger())
    for i in range(2):
        ta, ca = original_adapt(a, _support(i), a.cfg.fast)
        tb, cb = adapt_record(b, _support(i), b.cfg.fast)
        assert asdict(ta) == asdict(tb)
        assert asdict(ca) == asdict(cb)
    assert a.state_hash() == b.state_hash()
    for q in _queries():
        x, y = a.predict(q), b.predict(q)
        np.testing.assert_array_equal(x.logits, y.logits)
        assert asdict(x.cost) == asdict(y.cost)
    assert a.cost_counters == b.cost_counters
    assert identities == (installed.adapt_record, installed._delta_steps, installed_learner.adapt_record)


def test_actual_solver_error_acquisition_is_support_only_costed_and_readonly(monkeypatch):
    base = TinyEPC()
    cap = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit="error", credit_iters=8)
    old = base.infer_errors
    calls = []

    def track(ids, target, **kw):
        er = old(ids, target, **kw)
        calls.append((tuple(np.asarray(ids)), target, kw, er.cost))
        return er

    monkeypatch.setattr(base, "infer_errors", track)
    hashes = base.checksum(recompute=True), cap.params_hash
    sup = _support(0)
    tr, c = adapt_record(cap, sup, cap.cfg.fast)
    assert calls and tr.accepted
    expected = {(tuple(sup.prompt_ids + sup.answer_ids[:t]), y) for t, y in enumerate(sup.answer_ids)}
    assert all((ids, target) in expected and kw["phase"] == "learning" for ids, target, kw, _ in calls)
    assert c.settle_iters == 8 * len(calls)
    assert c.reverses == len(sup.answer_ids) + 9 * len(calls)  # unchanged setup adjoint + PC
    assert all(x.full_forwards == x.reverses == 9 for _, _, _, x in calls)
    assert hashes == (base.checksum(recompute=True), cap.params_hash)
    rec = cap.store.records[0]
    assert rec.delta is not None and all(aggregate(w, cap.cfg.controller) <= 0.300001 for w in rec.delta)
    # Acceptance is real feedforward loss, not the lower clamped inference energy.
    from pccap.contracts import Write
    losses = []
    for t, y in enumerate(sup.answer_ids):
        ids = np.int32(sup.prompt_ids + sup.answer_ids[:t])
        ws = [Write(SiteId(m, cap.blocks[m], len(ids) - 1), rec.delta[t, m - 1]) for m in (1, 2, 3)]
        loss, _ = base.loss(ids, y, ws)
        losses.append(loss)
    np.testing.assert_allclose(tr.per_prefix_loss_after, losses, rtol=0, atol=0)
    count, state = len(calls), cap.state_hash()
    for q in _queries():
        cap.predict(q)
    assert len(calls) == count and state == cap.state_hash()


def test_nonfinite_credit_restores_superseded_record_and_charges_failure(monkeypatch):
    base = TinyEPC()
    cap = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit="adjoint")
    sup = _support(0)
    adapt_record(cap, sup, cap.cfg.fast)
    original_record = copy.deepcopy(cap.store.active_records()[0])
    revision = replace(sup, record_id="revision", revision=2)

    def broken(*args, **kw):
        base.ledger.charge(CostRecord(full_forwards=9, reverses=9, settle_iters=8))
        raise FloatingPointError("synthetic failed inference after charged work")

    monkeypatch.setattr(base, "infer_errors", broken)
    tr, cost = adapt_record(cap, revision, cap.cfg.fast, credit="error")
    assert not tr.accepted and tr.rolled_back_reason == "non_finite_credit"
    assert cost.reverses == len(sup.answer_ids) + 9 and cost.settle_iters == 8
    active = cap.store.active_records()
    assert len(active) == 1 and active[0].record_id == original_record.record_id
    np.testing.assert_array_equal(active[0].delta, original_record.delta)


def test_error_direction_cost_with_mock_and_parent_update_interface(monkeypatch):
    # Plumbing check separate from the actual-solver tests above; choose e=-grad
    # to obtain bitwise normalized-direction parity with the original path.
    from pccap.contracts import EditItem

    a_base, b_base = TinyBase(), TinyBase()
    b_base.descent_sign, b_base.ledger, b_base.error_lr = 1, Ledger(), 0.1

    def infer(ids, target, iters, writes, phase):
        grads = b_base.adjoint(ids, target, writes, phase=phase)
        return ErrorResult(errors={}, site_errors={s: -g for s, g in grads.items()}, energies=[999.0] * 9,
                           grad_norm_0=1, grad_norm_k=1, r_k=1, iters=iters, logits=None,
                           cost=CostRecord(phase=phase, full_forwards=9, reverses=9, settle_iters=8))

    monkeypatch.setattr(b_base, "infer_errors", infer, raising=False)
    a, b = RevisionCap(a_base, cfg(), Ledger()), PCRevisionCap(b_base, cfg(), b_base.ledger, acquisition_credit="error")
    sup = _support(0)
    item = EditItem(item_id=sup.record_id, fact_id=sup.fact_id, digest=b"0" * 16, prompt="p", answer="a",
                    aliases=["a"], paraphrases=[], locality_prompts=[],
                    prompt_ids=np.int32(sup.prompt_ids), answer_ids=np.int32(sup.answer_ids))
    x, y = a.update_item(item), b.update_item(item)
    assert x.code == y.code and x.prefix_outcomes == y.prefix_outcomes
    assert a.store.export().content_hash() == b.store.export().content_hash()
    assert y.cost.settle_iters == 8 * y.rounds_used
    assert y.cost.reverses - x.cost.reverses == 8 * y.rounds_used
    assert support_from_edit_item(item).answer_ids == sup.answer_ids


def test_unsupported_credit_and_code_adaptation_refuse_before_teaching():
    cap = RevisionCap(TinyBase(), _cfg(), Ledger())
    before = cap.state_hash()
    with pytest.raises(ValueError, match="delta-only"):
        adapt_record(cap, _support(0), cap.cfg.fast, credit="error")
    with pytest.raises(ValueError, match="positive integer"):
        adapt_record(cap, _support(0), cap.cfg.fast, credit="error", iters=0)
    assert before == cap.state_hash()


def test_snapshot_rejects_wrong_credit_horizon_without_mutation():
    base = TinyEPC()
    a = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit="error", credit_iters=8)
    b = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit="error", credit_iters=1)
    c = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit="adjoint")
    state = a.export_state()
    for cap in (b, c):
        before = cap.state_hash()
        with pytest.raises(RuntimeError, match="semantic configuration"):
            cap.import_state(state)
        assert cap.state_hash() == before
