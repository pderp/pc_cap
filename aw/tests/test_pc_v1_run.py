"""PC-7: real tiny solver, native assays, paired inputs, snapshots and failures."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from aw import pc_v1_run as r
from aw.pc_harm_readout import read_arm, window_hash
from aw.pc_harm_smoke import TinyBatchEPC
from aw.pc_v1_acquire import PCRevisionCap
from aw.pc_v1_readout import PCPositionBatchReader
from aw.tests.test_pc_v1_acquire import cfg
from pccap.contracts import CostRecord
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.stage4_adapters import CellAdapter


class Tokens:
    """Character tokens within the tiny vocabulary; decoder truncation explicit."""

    alphabet = " abcdefghijklmnopqrstuvwxyz?\n"

    def encode(self, text):
        return np.int32([self.alphabet.index(c) for c in text])

    def decode(self, ids):
        return "".join(self.alphabet[int(i)] if int(i) < len(self.alphabet) else "!" for i in ids)


def fixture():
    tok = Tokens()
    rows = [
        dict(
            item_id=f"item-{i}",
            fact_id=f"fact-{i}",
            prompt=q,
            answer="z",
            aliases=["z"],
            paraphrases=[q + "?"],
            dataset="zsre",
        )
        for i, q in enumerate(("a?", "b?"))
    ]
    endpoints = {
        "locality": dict(expected_ids=["loc"], rows=[dict(item_id="loc", prompt="c?")]),
        "near_miss": dict(
            expected_ids=["near"],
            rows=[
                dict(
                    item_id="near",
                    dataset="zsre",
                    edit_item_id="outside",
                    edit_prompt="d?",
                    edit_answer="z",
                    neighbour_prompt="e?",
                )
            ],
        ),
        "revision": dict(
            expected_ids=["rev"],
            rows=[
                dict(
                    item_id="rev",
                    dataset="zsre",
                    fact_id="outside-revision",
                    prompt="f?",
                    paraphrases=["g?"],
                    versions=[dict(version=1, answer="z"), dict(version=2, answer="y")],
                )
            ],
        ),
    }
    return tok, [as_edit(row, tok) for row in rows], endpoints


def adapter(arm):
    base, config = TinyBatchEPC(), cfg()
    config.fast.delta_steps = (
        1  # disclosed CPU fixture only; production uses registered cfg unchanged
    )
    cap = PCRevisionCap(base, config, base.ledger, acquisition_credit=r.ARMS[arm])
    return CellAdapter(cap, "R1_learned_ff")


def test_plan_is_metadata_only_and_imports_owner_guard(monkeypatch):
    from aw.pc_v0 import blocking_cuda_processes

    assert r.blocking_cuda_processes is blocking_cuda_processes
    original = Path.read_bytes

    def check(p):
        assert not (p.suffix == ".json" and "assets" in p.parts), "plan opened a data payload"
        return original(p)

    monkeypatch.setattr(Path, "read_bytes", check)
    p = r.plan()
    assert len(p["cells"]) == 4 and p["checkpoints"] == [100, 300]
    assert all(
        c["realization"] == 0 and c["order"] == 100 and c["items"] == 300 for c in p["cells"]
    )
    assert not p["model_execution"] and not p["payload_opened"]


def test_actual_paired_stream_checkpoints_native_metrics_and_pc6_restore(tmp_path):
    tok, items, eps = fixture()
    configs = []
    for arm in r.ARMS:
        a = adapter(arm)
        out, resources = tmp_path / arm, tmp_path / ("snapshots-" + arm)
        result = r.execute_stream(
            a,
            tok,
            items,
            eps,
            [1, 2],
            out,
            resources,
            dict(
                cell=dict(dataset="zsre", realization=0, order=100, arm=arm, items=2),
                population="cpu_smoke",
                sources=r.sources(),
            ),
            max_new=2,
        )
        assert result["status"] == "complete" and result["checkpoints_completed"] == [1, 2]
        assert result["base_hash_before"] == result["base_hash_after"]
        assert result["reader_hash_before"] == result["reader_hash_after"]
        configs.append(json.loads((out / "config.json").read_bytes()))
        for n in (1, 2):
            cp = json.loads((out / f"checkpoint-{n}.json").read_bytes())
            assert cp["metrics"]["ES"]["planned"] == cp["metrics"]["RET-GS"]["scored"] == n
            assert cp["metrics"]["LS"]["value"] == cp["locality"]["summary"]["preserved_fraction"]
            assert cp["metrics"]["near_miss"]["scored"] == cp["metrics"]["revision"]["scored"] == 1
            assert all(
                row["state_restored"]
                for k in ("near_miss", "revision")
                for row in cp["endpoints"][k]["rows"]
            )
            reader = PCPositionBatchReader.from_checkpoint(
                a.base, a.cfg, a.params, cp["snapshot"], batch_size=2
            )
            assert reader.adapter.state_hash() == cp["state_sha256"]
        phases = [json.loads(line) for line in (out / "phases.jsonl").read_text().splitlines()]
        assert all(
            x["state_before"] == x["state_after"]
            for x in phases
            if not x["phase"].startswith("edit:")
        )
        assert len(a.store.records) == 2  # challenge teaching did not leak into stream memory
        w = np.int32([[4, 11, 17]])
        read_arm(reader, w, dict(positions=2, windows_sha256=window_hash(w)), out / "harm")
        if arm == "SE-E":
            assert result["ledger"]["learning"]["settle_iters"] > 0
    for k in (
        "item_ids",
        "endpoints_sha256",
        "initial_inference_state",
        "base_sha256",
        "reader_sha256",
    ):
        assert configs[0][k] == configs[1][k]
    assert configs[0]["initial_state"] != configs[1]["initial_state"]  # treatment config is bound


def test_failed_acquisition_keeps_cost_and_never_marks_cell_complete(tmp_path, monkeypatch):
    tok, items, eps = fixture()
    a = adapter("SE-A")

    def fail(item):
        a.ledger.charge(CostRecord(phase="learning", full_forwards=2))
        raise FloatingPointError("synthetic failure")

    monkeypatch.setattr(a, "update_item", fail)
    out = tmp_path / "failed"
    with pytest.raises(FloatingPointError, match="synthetic"):
        r.execute_stream(
            a,
            tok,
            items,
            eps,
            [2],
            out,
            tmp_path / "resources",
            dict(population="cpu_smoke"),
            max_new=2,
        )
    f = json.loads((out / "finish.json").read_bytes())
    assert f["status"] == "failed" and f["items_completed"] == 0
    assert f["ledger"]["learning"]["full_forwards"] == 2
    assert not (out / "checkpoint-2.json").exists()


def test_execution_and_profile_gates(tmp_path):
    with pytest.raises(ValueError, match="execute"):
        r.run_cell(SimpleNamespace(execute=False))
    p = r.plan(True)
    (tmp_path / "plan.json").write_text(json.dumps(p))
    with pytest.raises(FileNotFoundError):
        r.validate_profile(tmp_path)
    p["population"] = r.POPULATION
    (tmp_path / "plan.json").write_text(json.dumps(p))
    with pytest.raises(ValueError, match="profile"):
        r.validate_profile(tmp_path)


def test_missing_revision_evidence_is_not_imputed_success():
    row = dict(
        item_id="rev",
        status="ok",
        latest_answer_success=True,
        old_record_retired=None,
        new_record_active=True,
    )
    cp = dict(
        history=[],
        retention=dict(rows=[]),
        locality=dict(rows=[]),
        endpoints=dict(near_miss=dict(rows=[]), revision=dict(rows=[row])),
    )
    eps = {k: dict(expected_ids=[]) for k in ("locality", "near_miss")}
    eps["revision"] = dict(expected_ids=["rev"])
    result = r.metrics(cp, [], eps)
    assert result["revision"]["value"] is None and result["revision_latest_answer"]["value"] == 1
