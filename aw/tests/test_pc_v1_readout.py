"""Checkpoint-mode checks, bitwise registered-reader parity, and PC-5 integration."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import json
import os
import time

import jax
import numpy as np
import pytest
from scripts.r1_68c_batched_drift import PositionBatchReader

from aw.pc_harm_readout import read_arm, window_hash
from aw.pc_harm_smoke import TinyBatchEPC
from aw.pc_v0_report import sha
from aw.pc_v1_acquire import PCRevisionCap, adapt_record
from aw.pc_v1_readout import PCPositionBatchReader
from aw.tests.test_pc_v1_acquire import cfg
from aw.tests.test_pc_v1_devcheckpoint import RECIPE, ROOT, SNAPSHOT
from aw.tests.test_wrapper import _support
from pccap.bases.epc import EPCBase
from pccap.contracts import CostRecord
from pccap.harness.ledger import Ledger
from pccap.harness.snapshot import restore, save
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.stage4_adapters import CellAdapter


def saved(cap, path):
    digest = save(cap.export_state(), path)
    return dict(
        path=str(path),
        sha256=digest,
        state_sha256=cap.state_hash(),
        base_sha256=cap.base.checksum(recompute=True),
        reader_sha256=cap.params_hash,
        credit=cap.acquisition_credit,
        iters=cap.credit_iters,
    )


@pytest.mark.parametrize("credit", ["adjoint", "error"])
def test_supplemental_restore_query_view_and_harm_readout(credit, tmp_path):
    base = TinyBatchEPC()
    cap = PCRevisionCap(base, cfg(), base.ledger, acquisition_credit=credit)
    trace, _ = adapt_record(cap, _support(0), cap.cfg.fast)
    assert trace.accepted
    binding = saved(cap, tmp_path / "supplemental.snapshot")
    reader = PCPositionBatchReader.from_checkpoint(base, cap.cfg, cap.params, binding, batch_size=2)
    assert type(reader.view) is RevisionCap
    # The original exact-class guard must still refuse a PCRevisionCap.
    with pytest.raises(TypeError, match="exact RevisionCap"):
        PositionBatchReader(CellAdapter(cap, "R1_learned_ff"), batch_size=2)
    before = cap.state_hash(), reader.adapter.state_hash()
    reference = RevisionCap(base, cap.cfg, base.ledger, params=cap.params)
    state = cap.export_state()
    state.scalars["config"] = reference.semantic_config()
    reference.import_state(state)
    native = PositionBatchReader(CellAdapter(reference, "R1_learned_ff"), batch_size=2)
    seqs = [np.int32([4, 11]), np.int32([4, 12])]
    np.testing.assert_array_equal(reader.last_logits_batch(seqs), native.last_logits_batch(seqs))
    np.testing.assert_array_equal(reader.last_capoff, native.last_capoff)
    assert (cap.state_hash(), reader.adapter.state_hash()) == before
    reader.events.clear()
    windows = np.int32([[4, 11, 17, 9], [4, 12, 17, 7]])
    result = read_arm(
        reader,
        windows,
        dict(mode="cpu_fixture", positions=6, windows_sha256=window_hash(windows)),
        tmp_path / "readout",
    )
    assert result["summary"]["original"]["loss"]["positions"] == 6
    assert sha(binding["path"]) == binding["sha256"]
    wrong = copy.deepcopy(binding)
    wrong["credit"] = "error" if credit == "adjoint" else "adjoint"
    with pytest.raises(RuntimeError, match="semantic configuration"):
        PCPositionBatchReader.from_checkpoint(base, cap.cfg, cap.params, wrong, batch_size=2)
    wrong = copy.deepcopy(binding)
    wrong["base_sha256"] = "wrong"
    with pytest.raises(ValueError, match="identity"):
        PCPositionBatchReader.from_checkpoint(base, cap.cfg, cap.params, wrong)
    wrong = copy.deepcopy(binding)
    wrong["sha256"] = "wrong"
    with pytest.raises(ValueError, match="file hash"):
        PCPositionBatchReader.from_checkpoint(base, cap.cfg, cap.params, wrong)
    reader.adapter.learner.cfg.null_threshold += 0.01
    with pytest.raises(RuntimeError, match="mutated"):
        reader.adapter.state_hash()


def test_failed_batch_records_unreported_cost_once(tmp_path, monkeypatch):
    base = TinyBatchEPC()
    cap = PCRevisionCap(base, cfg(), base.ledger)
    reader = PCPositionBatchReader(cap, batch_size=2)

    def failed(*args, **kwargs):
        base.ledger.charge(CostRecord(phase="query", full_forwards=2, tokens=8))
        reader.events.append(
            dict(model="already_reported", returned_cost=dict(full_forwards=1, tokens=4))
        )
        raise RuntimeError("simulated batch interruption")

    monkeypatch.setattr(reader._reader, "last_logits_batch", failed)
    windows = np.int32([[4, 11, 17]])
    with pytest.raises(RuntimeError, match="simulated"):
        read_arm(
            reader,
            windows,
            dict(positions=2, windows_sha256=window_hash(windows)),
            tmp_path / "failed",
        )
    cost = json.loads((tmp_path / "failed/cost.json").read_text())
    assert cost["status"] == "failed"
    assert sum(r["returned_cost"]["full_forwards"] for r in cost["query_costs"].values()) == 2
    assert not (tmp_path / "failed/vectors.npz").exists()


@pytest.mark.slow
def test_saved_development_checkpoint_registered_batch_bit_parity(tmp_path):
    if not RECIPE.exists() or not SNAPSHOT.exists():
        pytest.skip("PC-4 saved development resources absent")
    assert jax.default_backend() == "cpu"
    from scripts.r1_61_cell_driver import construct_owner_adapter

    start = time.monotonic()
    recipe = json.loads(RECIPE.read_bytes())
    sidecar = json.loads(SNAPSHOT.with_suffix(".snapshot.json").read_bytes())
    assert sha(SNAPSHOT) == sidecar["snapshot_sha256"]
    assert sha(recipe["payload"]["path"]) == recipe["payload"]["sha256"]
    reference, _ = construct_owner_adapter(recipe)
    assert reference.identity() == recipe["adapter_identity"]
    state = restore(SNAPSHOT.read_bytes(), expected_hash=sidecar["state_sha256"])
    reference.import_state(state)
    base = EPCBase(
        params_np=jax.tree_util.tree_map(np.asarray, reference.base.params),
        cfg=reference.base.cfg,
        ledger=Ledger(),
        error_lr=0.1,
    )
    cap = PCRevisionCap(base, reference.learner.cfg, base.ledger, params=reference.learner.params)
    cap.import_state(state)
    binding = saved(cap, tmp_path / "adjoint-supplemental.snapshot")
    reader = PCPositionBatchReader.from_checkpoint(base, cap.cfg, cap.params, binding, batch_size=2)
    native = PositionBatchReader(reference, batch_size=2)
    rows = json.loads(open(recipe["payload"]["path"]).read())["items"]
    seqs = [
        np.int32(ids)
        for r in rows[:4]
        for ids in (r["prompt_ids"], r["prompt_ids"] + r["answer_ids"][:1])
    ]
    seqs += [np.int32([464, 2068, 7586]), np.int32([1212, 318, 257, 1332])]
    checks = []
    for offset in range(0, len(seqs), 2):
        chunk = seqs[offset : offset + 2]
        on = reader.last_logits_batch(chunk)
        expected = native.last_logits_batch(chunk)
        np.testing.assert_array_equal(on, expected)
        np.testing.assert_array_equal(reader.last_capoff, native.last_capoff)
        a = [e["selections"] for e in reader.events if "selections" in e][-1]
        b = [e["selections"] for e in native.events if "selections" in e][-1]
        assert a == b
        checks.extend(
            dict(
                length=len(ids),
                cap_logits_exact=True,
                base_logits_exact=True,
                hard_null=s["hard_null"],
                logits_changed=not np.array_equal(on[i], reader.last_capoff[i]),
            )
            for i, (ids, s) in enumerate(zip(chunk, a, strict=True))
        )
        reader.events.clear()
        native.events.clear()
    assert reader.adapter.state_hash() == cap.state_hash() == state.content_hash()
    assert (
        base.checksum(recompute=True)
        == reference.base.checksum(recompute=True)
        == binding["base_sha256"]
    )
    assert reader.view.params_hash == reference.learner.params_hash
    assert any(not x["hard_null"] for x in checks), "parity must include an active correction"
    assert any(x["logits_changed"] for x in checks), "the correction must change predictions"
    result = dict(
        task="PC-6",
        gpu_seconds=0,
        device=str(jax.devices()),
        checks=checks,
        exact_prefixes=len(checks),
        unchanged_checkpoint=True,
        wall_seconds=time.monotonic() - start,
        supplemental_checkpoint=binding,
        sources_sha256={
            str(p): sha(p)
            for p in (
                RECIPE,
                SNAPSHOT,
                SNAPSHOT.with_suffix(".snapshot.json"),
                ROOT / "aw/pc_v1_readout.py",
                ROOT / "aw/tests/test_pc_v1_readout.py",
                ROOT / "aw/pc_v1_acquire.py",
                ROOT / "scripts/r1_68c_batched_drift.py",
                ROOT / "src/pccap/revision_v1/learner.py",
                ROOT / "src/pccap/bases/epc.py",
            )
        },
        qualification="Saved development state copied to an adjoint supplemental fixture; no new efficacy result. Actual error-mode acquisition/restore tested on the tiny solver; no full real-base validation sweep here.",
    )
    dest = os.environ.get("PC6_OUTPUT")
    if dest:
        from pathlib import Path

        path = Path(dest)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as f:
            json.dump(result, f, indent=2)
    print(
        json.dumps(
            dict(
                exact_prefixes=len(checks),
                wall_seconds=result["wall_seconds"],
                non_null=sum(not c["hard_null"] for c in checks),
            )
        )
    )
