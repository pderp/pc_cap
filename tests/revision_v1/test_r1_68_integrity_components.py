"""R1-68: CPU integrity components, checkpoint semantics and failure refusal."""

from __future__ import annotations

import copy
import json
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import adapt_record
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.incremental_integrity import (
    PhaseJournal,
    RecordDigestIndex,
    read_only_immediate,
    verified_checkpoint,
)
from pccap.revision_v1.learner import RevisionCap, Selection
from pccap.revision_v1.selection_trace import selection_trace
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.revision_v1.stage4_assays import CellAssays
from tests.revision_v1.test_learner_cpu import _cfg, _support
from tests.revision_v1.test_stage4_cell import TinyTok
from tests.revision_v1.tiny_base import TinyBase


def cap():
    cfg = _cfg(null_threshold=1.01)
    cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
    return RevisionCap(TinyBase(), cfg, Ledger())


def clean(value):
    # Exact behavioral/state report comparison; costs and wall are independently observed.
    if isinstance(value, dict):
        return {
            k: clean(v)
            for k, v in value.items()
            if k not in ("returned_cost", "cost", "wall_seconds", "ledger_delta")
        }
    if isinstance(value, list):
        return [clean(v) for v in value]
    return value


def test_profiles_identical_immediate_checkpoint_reports_and_resume(tmp_path):
    c = cap()
    tok = TinyTok()
    items = [
        as_edit(
            {
                "item_id": str(i),
                "fact_id": str(i),
                "dataset": "mquake",
                "subject": str(i),
                "prompt": f"q{i}?",
                "answer": "new",
                "aliases": ["new"],
                "paraphrases": [f"para{i}?"],
            },
            tok,
        )
        for i in range(3)
    ]
    for i in range(3):
        adapt_record(c, _support(i), c.cfg.fast)
    initial = c.export_state().clone()
    results = []
    for mode in ("full", "incremental"):
        c.import_state(initial)
        adapter = CellAdapter(c, "R1_learned_ff")
        assays = CellAssays(adapter, tok, max_new=4)
        before = c.state_hash()
        rows = [read_only_immediate(adapter, assays, it, integrity_profile=mode) for it in items]
        cp = {
            "history": rows,
            "retention": assays.retention(items),
            "locality": assays.locality(
                {"expected_ids": ["x"], "rows": [{"item_id": "x", "prompt": "other?"}]}
            ),
        }
        receipt = verified_checkpoint(adapter)
        assert receipt["state_sha256"] == before == c.state_hash()
        cp["state_sha256"] = receipt["state_sha256"]
        # The verified snapshot is a restart boundary; reproduce next query.
        from pccap.harness.snapshot import restore

        c.import_state(restore(receipt["snapshot"], expected_hash=receipt["state_sha256"]))
        cp["after_resume"] = assays.item(items[0])
        results.append(clean(cp))
    assert results[0] == results[1]


def test_incremental_skips_clone_but_checks_state(monkeypatch):
    c = cap()
    adapt_record(c, _support(0), c.cfg.fast)
    adapter = CellAdapter(c, "R1_learned_ff")
    calls = []
    from pccap.harness.snapshot import LearnerState

    monkeypatch.setattr(LearnerState, "clone", lambda self: calls.append(True))
    assays = SimpleNamespace(item=lambda item: c.predict(np.int32([1, 2, 3])).logits.shape)
    assert read_only_immediate(adapter, assays, None, integrity_profile="incremental")
    assert calls == []

    def bad(_):
        c.store.records[0].active = False
        return {}

    with pytest.raises(RuntimeError, match="mutated persistent"):
        read_only_immediate(
            adapter, SimpleNamespace(item=bad), None, integrity_profile="incremental"
        )
    # The attempt is now invalid and requires the caller's checkpoint restore.


def test_unsupported_cap_cannot_bypass_clone():
    with pytest.raises(ValueError, match="no read-only gate"):
        read_only_immediate(
            SimpleNamespace(learner=object()), None, None, integrity_profile="incremental"
        )


def test_record_index_mutation_supersession_deletion_and_unreported_corruption():
    c = cap()
    for i in range(3):
        adapt_record(c, _support(i), c.cfg.fast)
    records = c.store.records
    index = RecordDigestIndex()
    meta = {"config": c.semantic_config(), "params": c.params_hash}
    index.update(records, changed_ids=[r.record_id for r in records], metadata=meta)
    count = index.records_hashed
    c.store.set_code("s1", np.ones_like(records[1].code))
    index.update(records, changed_ids=["s1"], metadata=meta)
    assert index.records_hashed == count + 1
    index.verify(records, metadata=meta)
    c.store.set_code("s2", np.ones_like(records[2].code))
    with pytest.raises(RuntimeError, match="full recomputation"):
        index.verify(records, metadata=meta)
    index.update(records, changed_ids=["s2"], metadata=meta)
    adapt_record(c, _support(4, fact="f0", rev=2), c.cfg.fast)
    index.update(records, changed_ids=["s0", "s4"], metadata=meta)
    index.verify(records, metadata=meta)
    c.store.remove("s4", restore="s0")
    index.update(records, changed_ids=["s0"], metadata=meta)
    index.verify(records, metadata=meta)
    snap = verified_checkpoint(CellAdapter(c, "R1_learned_ff"))
    assert snap["state_sha256"] == c.state_hash()
    index.rebuild_after_restore(c.store.records, metadata=meta)


def test_index_new_and_duplicate_inventory_refusal():
    c = cap()
    adapt_record(c, _support(0), c.cfg.fast)
    index = RecordDigestIndex()
    with pytest.raises(ValueError, match="missing mutation"):
        index.update(c.store.records, changed_ids=[], metadata={})
    with pytest.raises(ValueError, match="duplicate"):
        index.update(c.store.records * 2, changed_ids=["s0"], metadata={})
    with pytest.raises(ValueError, match="unknown"):
        index.update(c.store.records, changed_ids=["missing"], metadata={})


def test_journal_batches_checkpoint_flush_and_tamper(tmp_path):
    p = tmp_path / "phases"
    j = PhaseJournal(p, edits_per_file=2)
    for n in range(1, 4):
        j.add_edit(n, edit={"state": str(n), "cost": 7}, immediate={"ok": True})
    assert len(list(p.iterdir())) == 1
    receipt = j.receipt()
    assert len(receipt["batches"]) == 2
    assert [r["index"] for r in PhaseJournal.verify(receipt, directory=p)] == [1, 2, 3]
    bad = copy.deepcopy(receipt)
    bad["last_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="inventory"):
        PhaseJournal.verify(bad, directory=p)
    # Create a different directory instead of changing an existing file.
    other = tmp_path / "other"
    other.mkdir()
    target = other / "batch-000000.json"
    target.write_text(json.dumps({"schema_version": 1, "previous_sha256": None, "rows": [{}]}))
    bad = copy.deepcopy(receipt)
    bad["batches"][0]["path"] = str(target)
    with pytest.raises(ValueError, match="path"):
        PhaseJournal.verify(bad, directory=p)


def test_journal_failure_tail_is_flushable_and_existing_dir_refused(tmp_path):
    p = tmp_path / "phases"
    j = PhaseJournal(p, edits_per_file=16)
    j.add_edit(1, edit={"status": "error", "cost": 9}, immediate=None)
    r = j.receipt()
    assert PhaseJournal.verify(r, directory=p)[0]["edit"]["cost"] == 9
    with pytest.raises(FileExistsError):
        PhaseJournal(p)
    with pytest.raises(ValueError, match="contiguous"):
        j.add_edit(4, edit={}, immediate={})


@pytest.mark.parametrize("minimum,verdict", [(1, "not_evaluated_empty_memory"), (None, "disabled")])
def test_empty_selection_cosine_gate(minimum, verdict):
    sel = Selection(prompt_len=3, record_ids=[], weights=np.array([]), null_mass=1.0, code=None, hard_null=True)
    cfg = SimpleNamespace(rare_overlap_min=minimum, null_threshold=0.5, min_score=0.93)
    assert selection_trace(sel, config=cfg)["rare_gate_verdict"] == verdict
