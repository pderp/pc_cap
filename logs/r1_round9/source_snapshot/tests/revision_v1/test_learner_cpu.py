"""RevisionCap on the tiny CPU base: gate 4 (empty memory = cap-off exactly; hard null), per-query selection held across
positions, adapt touches only the taught record, snapshot round-trip, and the R1-16 cost variants."""

from __future__ import annotations

import os

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import numpy as np  # noqa: E402
import pytest  # noqa: E402

from pccap.harness.ledger import Ledger  # noqa: E402
from pccap.revision_v1.adapt import FastConfig, adapt_record  # noqa: E402
from pccap.revision_v1.contracts import SupportExample  # noqa: E402
from pccap.revision_v1.controller import ControllerConfig  # noqa: E402
from pccap.revision_v1.learner import RevisionCap, RevisionConfig  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig  # noqa: E402
from tests.revision_v1.tiny_base import CFG, TinyBase  # noqa: E402

RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


def _cfg(**kw):
    return RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=2, lr=1e-2), null_threshold=kw.pop("null_threshold", 0.5), **kw)


def _support(i: int, fact: str | None = None, rev: int = 1):
    r = np.random.default_rng(i)
    return SupportExample(record_id=f"s{i}", fact_id=fact or f"f{i}", revision=rev, entity_id="e", family_id="g",
                          prompt_ids=tuple(int(x) for x in r.integers(1, 60, size=7)), answer_ids=tuple(int(x) for x in r.integers(1, 60, size=3)))


def test_empty_memory_is_capoff_and_predict_is_pure():
    base = TinyBase()
    cap = RevisionCap(base, _cfg(), Ledger())
    ids = np.int32([5, 6, 7, 8])
    off = np.asarray(base.forward(ids).logits)
    h = cap.state_hash()
    assert np.array_equal(off, cap.predict(ids).logits)
    assert cap.state_hash() == h and cap.cost_counters["corrected_partial_passes"] == 0


def test_adapt_changes_only_the_taught_record_and_selection_is_held():
    base = TinyBase()
    cap = RevisionCap(base, _cfg(null_threshold=1.01), Ledger())  # never hard-null: exercise the corrected path
    s0, s1 = _support(0), _support(1)
    adapt_record(cap, s0, cap.cfg.fast)
    code0 = cap.store.get("s0").code.copy()
    key0 = cap.store.get("s0").key.copy()
    tr, cost = adapt_record(cap, s1, cap.cfg.fast)
    assert cost.reverses == cap.cfg.fast.steps * len(s1.answer_ids) and cost.records_touched == 1
    assert np.array_equal(cap.store.get("s0").code, code0) and np.array_equal(cap.store.get("s0").key, key0)
    cap.reset_queries()
    prompt = np.asarray(s1.prompt_ids, np.int32)
    sel = cap.selection_for(prompt)
    longer = np.concatenate([prompt, np.int32(s1.answer_ids[:2])])
    assert cap.selection_for(longer) is sel  # held for every answer position of the query
    assert len(cap._sel) == 1
    cap.predict(longer)
    assert cap.cost_counters["corrected_partial_passes"] == 1
    # supersession keeps the fact id, retires the old record
    s2 = _support(2, fact="f1", rev=2)
    tr2, _ = adapt_record(cap, s2, cap.cfg.fast)
    assert tr2.superseded == "s1" and cap.store.get("s1").active is False and cap.store.get("s2").active


def test_snapshot_round_trip_and_hash_check():
    base = TinyBase()
    cap = RevisionCap(base, _cfg(), Ledger())
    adapt_record(cap, _support(0), cap.cfg.fast)
    st = cap.export_state()
    cap2 = RevisionCap(base, _cfg(), Ledger(), params=cap.params)
    cap2.import_state(st)
    assert cap2.state_hash() == cap.state_hash()
    other = RevisionCap(base, RevisionConfig(reader=RC, controller=CC, seed=5), Ledger())
    with pytest.raises(RuntimeError):
        other.import_state(st)


def test_cost_variants_match_the_reference_read():
    base = TinyBase()
    ref = RevisionCap(base, _cfg(null_threshold=1.01, cache_prompt_pass=False), Ledger())
    for i in range(3):
        adapt_record(ref, _support(i), ref.cfg.fast)
    ref.reset_queries()
    prompt = np.asarray(_support(1).prompt_ids, np.int32)
    n_before = base.calls["forward"]
    ref_logits = ref.predict(prompt).logits
    assert base.calls["forward"] - n_before == 2  # selection pass + observation pass
    other = RevisionCap(base, _cfg(null_threshold=1.01, cache_prompt_pass=True), Ledger(), params=ref.params)
    with pytest.raises(RuntimeError):
        other.import_state(ref.export_state())  # R23-06: a snapshot carries its semantic configuration
    cached = RevisionCap(base, _cfg(null_threshold=1.01, cache_prompt_pass=False), Ledger(), params=ref.params)
    cached.import_state(ref.export_state())
    cached.cfg.cache_prompt_pass = True  # the variant is switched after import (same stored state)
    n_before = base.calls["forward"]
    assert np.allclose(cached.predict(prompt).logits, ref_logits, atol=1e-5)
    assert base.calls["forward"] - n_before == 1 and cached.cost_counters["cached_prompt_reads"] == 1
    single = RevisionCap(base, _cfg(null_threshold=1.01, cache_prompt_pass=False), Ledger(), params=ref.params)
    single.import_state(ref.export_state())
    single.cfg.single_site = True
    out = single.predict(prompt).logits
    assert out.shape == ref_logits.shape and np.all(np.isfinite(out))
    # single-site read with the same writes at site 3 only equals a reference read whose site-1/2 writes are zero
    sel = single.selection_for(prompt)
    assert sel.record_ids and not sel.hard_null


def test_answer_enters_the_code_and_nonfinite_rolls_back_fully():
    base = TinyBase()
    cap = RevisionCap(base, _cfg(), Ledger())
    s0 = _support(0)
    adapt_record(cap, s0, cap.cfg.fast)
    code_a = cap.store.get("s0").code.copy()
    key_a = cap.store.get("s0").key.copy()
    cap2 = RevisionCap(base, _cfg(), Ledger(), params=cap.params)
    swapped = SupportExample(**{**s0.__dict__, "answer_ids": tuple(int(x) for x in np.random.default_rng(9).integers(1, 60, size=3))})
    adapt_record(cap2, swapped, cap2.cfg.fast)
    assert np.array_equal(cap2.store.get("s0").key, key_a)  # the key depends on the prompt only
    assert not np.array_equal(cap2.store.get("s0").code, code_a)  # the code depends on the taught answer (R23-02)
    # non-finite fast step → the new record is removed and the superseded record restored (R23-04)
    cap3 = RevisionCap(base, RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=0)), Ledger(), params=cap.params)
    adapt_record(cap3, s0, cap3.cfg.fast)
    n_before = len(cap3.store.records)
    tr, _ = adapt_record(cap3, SupportExample(**{**s0.__dict__, "record_id": "s0r2", "revision": 2}), FastConfig(steps=1, lr=float("inf")))
    assert tr.rolled_back_reason in ("non_finite_code", "non_finite_loss") and len(cap3.store.records) == n_before
    assert cap3.store.get("s0").active is True and cap3.store.get("s0").superseded_by is None


def test_delta_steps_acquire_and_round_trip():
    base = TinyBase()
    cfg = RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=0, delta_steps=8, delta_lr=0.05, tau=0.01), null_threshold=1.01)
    cap = RevisionCap(base, cfg, Ledger())
    s0 = _support(0)
    tr, cost = adapt_record(cap, s0, cap.cfg.fast)
    assert tr.accepted and tr.loss_after < tr.loss_before and cost.reverses >= len(s0.answer_ids)
    rec = cap.store.get("s0")
    assert rec.delta is not None and rec.delta.shape == (len(s0.answer_ids), 3, CFG.d) and cap.store.bytes()["deltas"] == len(s0.answer_ids) * 3 * CFG.d * 4
    cap.reset_queries()
    prompt = np.asarray(s0.prompt_ids, np.int32)
    sel = cap.selection_for(prompt)
    assert sel.delta is not None
    logits_with = cap.predict(prompt).logits
    # with delta_replaces_controller the write is the bounded delta alone
    from pccap.revision_v1.controller import aggregate
    assert all(aggregate(rec.delta[t], CC) <= CC.A + 1e-5 for t in range(rec.delta.shape[0]))
    cap.store.set_delta("s0", None)
    cap.reset_queries()
    assert not np.allclose(cap.predict(prompt).logits, logits_with)  # the delta changes the read
    cap.store.set_delta("s0", np.zeros((len(s0.answer_ids), 3, CFG.d), np.float32))
    back = RevisionCap(base, cfg, Ledger(), params=cap.params)
    back.import_state(cap.export_state())
    assert back.state_hash() == cap.state_hash() and back.store.get("s0").delta is not None


def test_x25_repairs_zero_weight_deltas_weights_bytes_and_combined_config():
    base = TinyBase()
    cfg = RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=0, delta_steps=4, delta_lr=0.05, tau=0.01), null_threshold=1.01)
    cap = RevisionCap(base, cfg, Ledger())
    s0, s1 = _support(0), _support(1)
    adapt_record(cap, s0, cap.cfg.fast)  # has a delta
    cap2 = RevisionCap(base, cfg, Ledger(), params=cap.params)  # same semantic configuration for the import
    cap2.import_state(cap.export_state())
    cap2.cfg.fast = FastConfig(steps=0)  # then switch the fast rule off for the next record
    adapt_record(cap2, s1, cap2.cfg.fast)  # no delta
    cap2.reset_queries()
    sel = cap2.selection_for(np.asarray(s1.prompt_ids, np.int32))
    if sel.record_ids and sel.record_ids[int(np.argmax(sel.weights))] == "s1":
        assert sel.delta is None  # X25-01: a zero-weight candidate's delta must not replace the selected record's controller write
    assert cap2.store.bytes()["weights"] == cap.store.bytes()["weights"] > 0  # X25-02
    with pytest.raises(NotImplementedError):
        adapt_record(cap2, _support(2), FastConfig(steps=1, delta_steps=1))  # X25-04
    assert "s2" not in cap2.store._by_id


def test_x26_ceiling_at_construction_and_restore_metric_and_outcome_codes():
    from pccap.revision_v1.memory import CapacityError
    base = TinyBase()
    with pytest.raises(CapacityError):
        RevisionCap(base, RevisionConfig(reader=RC, controller=CC, ceiling_bytes=1), Ledger())  # X26-01: weights alone exceed the ceiling
    cap = RevisionCap(base, _cfg(), Ledger())
    adapt_record(cap, _support(0), cap.cfg.fast)
    small = RevisionCap(base, RevisionConfig(reader=RC, controller=CC, fast=cap.cfg.fast, ceiling_bytes=cap.store.bytes()["total"] - 1), Ledger(), params=cap.params)
    with pytest.raises(RuntimeError):
        small.import_state(cap.export_state())  # the ceiling is part of the semantic configuration
    assert cap.store.metric == "cos"  # X26-02: the store's metric follows the reader configuration
    dot_cap = RevisionCap(base, RevisionConfig(reader=ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2, cosine=False), controller=CC), Ledger())
    assert dot_cap.store.metric == "dot"
    # X26-04: a capacity failure during the delta write is reported as a resource failure, not as no improvement
    from pccap.contracts import EditItem
    cap3 = RevisionCap(base, RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=0, delta_steps=2, delta_lr=0.05, tau=0.01)), Ledger())
    s1 = _support(1)
    cap3.store.ceiling_bytes = cap3.store.bytes()["total"] + 8 * 4 + 6 * 4 + 128 + len(s1.prompt_ids) * 4 + 16  # room for the record, not its delta
    item = EditItem(item_id="i1", digest=b"\x01" * 16, prompt="p", answer="a", aliases=[], paraphrases=[], locality_prompts=[],
                    prompt_ids=np.asarray(s1.prompt_ids, np.int32), answer_ids=np.asarray(s1.answer_ids, np.int32), dataset="t", fact_id="f1")
    out = cap3.update_item(item, None, None)
    assert out.code == "acquisition_failure" and out.codes == ["resource_failure:delta_capacity"]
    # returned cost of the first prediction includes the selection pass
    cap.reset_queries()
    r = cap.predict(np.asarray(_support(0).prompt_ids, np.int32))
    assert r.cost.full_forwards >= 1


def test_r1_56_rare_overlap_gate_rejects_template_only_queries():
    """R1-56: with the gate, a query sharing only memory-common (template) tokens with the selected record is hard-nulled; a
    query that carries one of the record's rare tokens keeps the learned decision; the gate is bound into the snapshot config."""
    base = TinyBase()
    cap = RevisionCap(base, _cfg(null_threshold=1.01, rare_overlap_min=1, rare_df_max=2), Ledger())
    template = (10, 11, 12, 13)  # shared by every record → common
    for i, subject in enumerate((21, 22, 23, 24, 25)):  # each subject token occurs in exactly one record → rare
        s = SupportExample(record_id=f"s{i}", fact_id=f"f{i}", revision=1, entity_id="e", family_id="g", prompt_ids=template + (subject,), answer_ids=(40 + i,))
        adapt_record(cap, s, cap.cfg.fast)
    cap.reset_queries()
    only_template = cap.selection_for(np.asarray(template + (99,), np.int32))  # a new subject: no rare token shared
    assert only_template.hard_null and only_template.delta is None and only_template.code is None
    cap.reset_queries()
    with_subject = cap.selection_for(np.asarray(template + (23,), np.int32))
    assert not with_subject.hard_null  # the learned decision stands (threshold 1.01 never nulls)
    assert cap._rare_overlap(np.asarray(template + (23,), np.int32), np.asarray(template + (23,), np.int32)) == 1
    assert cap._rare_overlap(np.asarray(template, np.int32), np.asarray(template + (23,), np.int32)) == 0
    assert '"rare_overlap_min": 1' in cap.semantic_config()
    off = RevisionCap(base, _cfg(null_threshold=1.01), Ledger(), params=cap.params)
    with pytest.raises(RuntimeError):
        off.import_state(cap.export_state())  # a different gate is a different semantic configuration (R23-06)
