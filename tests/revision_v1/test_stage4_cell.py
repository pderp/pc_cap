"""Cell preflight, exact checkpoint resume, failure charging and CPU execution."""

from __future__ import annotations

import copy
import json
import uuid
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from pccap.contracts import CostRecord
from pccap.harness.ledger import Ledger
from pccap.harness.snapshot import LearnerState
from pccap.revision_v1.stage4_adapters import CellAdapter, build_adapter
from pccap.revision_v1.stage4_cell import (
    ROOT,
    load_cell,
    run_cell,
    sha,
    validate_payload,
    write_json,
)
from tests.revision_v1.test_endpoints import Cap, near_row, revision_row
from tests.revision_v1.test_endpoints import Tokenizer as EndpointTokenizer
from tests.revision_v1.test_endpoints_composition import ComposingCap as CompositionOnlyCap
from tests.revision_v1.test_endpoints_composition import case
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.tiny_base import TinyBase


# A general editing fixture must preserve taught answers in addition to the
# composition-only behavior of the narrower R1-60 fixture.
class ComposingCap(CompositionOnlyCap):
    def predict(self, ids):
        if int(ids[0]) in {int(self.base.tok.encode(q)[0]) for q in case()["questions"]}:
            return super().predict(ids)
        return Cap.predict(self, ids)


class Tokenizer(EndpointTokenizer):
    def token(self, text):
        if text not in self.ids:
            i = max((v for v in self.ids.values() if v != 198), default=1) + 1
            if i == 198:
                i += 1
            self.ids[text] = i
            self.strings[i] = text
        return self.ids[text]


CAL = {"radii": {"1": 0.0, "2": 0.0, "3": 0.0}, "bank_scales": {"1": 1.0, "2": 1.0, "3": 1.0}}


def payload(n=3, composition=True):
    ids = ["a", "b"] + [f"i{i}" for i in range(2, n)] if n >= 2 else ["a"]
    items = [
        {
            "item_id": i,
            "fact_id": i,
            "subject": i,
            "dataset": "mquake",
            "prompt": i + "?",
            "answer": "new",
            "aliases": ["new"],
            "paraphrases": [i + " para?"],
        }
        for i in ids
    ]
    outside = {
        "item_id": "outside",
        "fact_id": "outside",
        "subject": "outside",
        "dataset": "mquake",
        "prompt": "outside?",
    }
    nr, rr = near_row(), revision_row()
    nr.update(item_id="near", dataset="mquake", edit_item_id="near-support")
    rr.update(item_id="revision", dataset="mquake", fact_id="revision-support")
    return {
        "items": items,
        "pool_rows": [*items, outside],
        "endpoints": {
            "locality": {
                "expected_ids": ["loc"],
                "rows": [{"item_id": "loc", "prompt": "locality?"}],
            },
            "unseen": {"expected_ids": ["outside"], "rows": [outside]},
            "near_miss": {"expected_ids": ["near"], "rows": [nr]},
            "revision": {"expected_ids": ["revision"], "rows": [rr]},
            "composition": {
                "expected_ids": ["case:1"] if composition else [],
                "rows": [case()] if composition else [],
            },
            "drift": {"expected_positions": 2, "windows": [[2, 3, 4]]},
        },
    }


def setup_cell(tmp_path, monkeypatch, *, data=None, adapter=None, tok=None, checkpoints=None):
    import pccap.revision_v1.stage4_cell as module

    monkeypatch.setattr(module, "code_identity", lambda root=ROOT: "a" * 64)
    data = copy.deepcopy(data or payload())
    tok = tok or Tokenizer()
    # Freeze this fixture tokenizer before the first run so resume uses the same
    # vocabulary. It is deliberately not a GPT-2 admission fixture.
    for text in (
        " unknown",
        " new",
        " old",
        " final",
        "base answer",
        "neighbour?",
        "edit?",
        "rephrased?",
    ):
        tok.encode(text)
    for row in data["items"]:
        tok.encode(row["prompt"])
        tok.encode(" " + row["answer"] + "\n")
        for q in row["paraphrases"]:
            tok.encode(q)
    adapter = adapter or CellAdapter(ComposingCap(tok), "R1_learned_ff")
    root = ROOT / "logs/r1_round10/driver_tests" / uuid.uuid4().hex
    resources = ROOT.parent / "assets/test_scratch/r1_round10_driver" / root.name
    binding = write_json(tmp_path / "payload.json", data)
    manifest = {
        "schema_version": 1,
        "mode": "synthetic",
        "cell": {"condition": adapter.condition, "dataset": "mquake", "realization": 0, "order": 0},
        "code_sha256": "a" * 64,
        "adapter_identity": adapter.identity(),
        "payload": binding,
        "checkpoints": checkpoints or list(range(1, len(data["items"]) + 1)),
        "max_new": 4,
    }
    path = tmp_path / "cell.json"
    write_json(path, manifest)
    return path, manifest, data, adapter, tok, root, resources


def invoke(setup, **kwargs):
    path, manifest, data, adapter, tok, root, resources = setup
    return run_cell(
        path, sha(path), adapter, tok, output_root=root, resource_root=resources, **kwargs
    )


def test_full_cell_all_endpoints_costs_and_restore(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    out = invoke(setup)
    assert out["status"] == "complete" and out["completed_checkpoint"] == 3
    run = Path(out["run_dir"])
    receipts = sorted(run.glob("attempt-*/checkpoint-*.receipt.json"))
    assert len(receipts) == 3
    report = json.loads((run / "attempt-0000/checkpoint-3.json").read_text())
    assert [r["item_id"] for r in report["retention"]["rows"]] == ["a", "b", "i2"]
    assert all(r["es"] == 1 and r["gs"] == 1 for r in report["retention"]["rows"])
    assert report["locality"]["rows"][0]["preserved"]
    assert report["unseen"]["summary"]["firing_observed_n"] == 0
    assert report["unseen"]["summary"]["false_fire_rate_full_inventory"] is None
    assert report["endpoints"]["composition"]["summary"]["scored"] == 1
    assert report["endpoints"]["revision"]["rows"][0]["revision_success"]
    assert report["endpoints"]["drift"]["scored_positions"] == 2
    phases = [json.loads(p.read_text()) for p in run.glob("attempt-*/phases/*.json")]
    assert all(
        p["state_before"] == p["state_after_restore"] for p in phases if p["restore_required"]
    )
    assert any(
        e["returned_cost"]["full_forwards"] > 0 for p in phases for e in p["returned_events"]
    )
    assert len(setup[3].store.records) == 3


def test_resume_preserves_existing_bytes_and_matches_uninterrupted_state(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    first = invoke(setup, stop_after_checkpoint=1)
    run = Path(first["run_dir"])
    original = {p: sha(p) for p in run.rglob("*") if p.is_file()}
    resumed = list(setup)
    resumed[3] = CellAdapter(ComposingCap(setup[4]), "R1_learned_ff")
    result = invoke(resumed, resume=True)
    assert result["status"] == "complete"
    assert all(sha(p) == h for p, h in original.items())
    reference = CellAdapter(ComposingCap(setup[4]), "R1_learned_ff")
    from pccap.revision_v1.endpoints_composition import as_edit

    for row in setup[2]["items"]:
        reference.update_item(as_edit(row, setup[4]))
    assert resumed[3].state_hash() == reference.state_hash()
    again = list(setup)
    again[3] = CellAdapter(ComposingCap(setup[4]), "R1_learned_ff")
    assert invoke(again, resume=True)["status"] == "complete"


def test_failed_update_keeps_cost_and_resumes_completed_prefix(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    first = invoke(setup, stop_after_checkpoint=1)
    resumed = list(setup)
    cap = ComposingCap(setup[4])
    cap.resource_failure = True
    resumed[3] = CellAdapter(cap, "R1_learned_ff")
    with pytest.raises(RuntimeError):
        invoke(resumed, resume=True)
    attempt = Path(first["run_dir"]) / "attempt-0001"
    failure = json.loads((attempt / "failure.json").read_text())
    event = json.loads(next((attempt / "phases").glob("*.json")).read_text())
    assert failure["last_completed_checkpoint"] == 1
    assert event["returned_events"][0]["returned_cost"]["full_forwards"] == 1
    assert event["state_before"] == event["state_after_restore"]
    resumed[3] = CellAdapter(ComposingCap(setup[4]), "R1_learned_ff")
    assert invoke(resumed, resume=True)["status"] == "complete"


def test_preflight_hash_refusals_before_model_work(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    path, manifest, _, adapter, *_ = setup
    with pytest.raises(ValueError, match="hash"):
        run_cell(path, "0" * 64, adapter, setup[4], output_root=setup[5], resource_root=setup[6])
    import pccap.revision_v1.stage4_cell as module

    monkeypatch.setattr(module, "code_identity", lambda root=ROOT: "b" * 64)
    with pytest.raises(ValueError, match="code identity"):
        invoke(setup)
    assert not adapter.queries and not setup[5].exists()


def test_wrong_adapter_refused(tmp_path, monkeypatch):
    setup = list(setup_cell(tmp_path, monkeypatch))
    setup[3] = CellAdapter(Cap(setup[4]), "v0_stable")
    with pytest.raises(ValueError, match="identity"):
        invoke(setup)
    assert not setup[5].exists()


def test_reservation_manifest_not_a_launch_seal(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    manifest = {**setup[1], "mode": "content_sealed_fact_reservations"}
    path = tmp_path / "reservations-only.json"
    write_json(path, manifest)
    with pytest.raises(ValueError, match="not a launch seal"):
        load_cell(path, sha(path))
    manifest = {**setup[1], "mode": "stage4_sealed_cell"}
    path = tmp_path / "sealed.json"
    write_json(path, manifest)
    with pytest.raises(PermissionError, match="owner"):
        load_cell(path, sha(path))
    with pytest.raises(PermissionError, match="admission"):
        load_cell(path, sha(path), allow_sealed=True)


@pytest.mark.parametrize(
    "change",
    [
        "duplicate_edit",
        "wrong_checkpoint",
        "wrong_endpoint",
        "outside_edit",
        "drift_overflow",
        "cross_realization_comp",
    ],
)
def test_payload_admission_rejects_invalid_inventory(tmp_path, monkeypatch, change):
    setup = setup_cell(tmp_path, monkeypatch)
    m, p = copy.deepcopy(setup[1]), copy.deepcopy(setup[2])
    if change == "duplicate_edit":
        p["items"][1] = p["items"][0]
    elif change == "wrong_checkpoint":
        m["checkpoints"] = [1, 3, 2]
    elif change == "wrong_endpoint":
        p["endpoints"]["locality"]["expected_ids"] = ["different"]
    elif change == "outside_edit":
        p["endpoints"]["unseen"]["expected_ids"] = ["a"]
    elif change == "drift_overflow":
        p["endpoints"]["drift"]["expected_positions"] = 1
    else:
        p["endpoints"]["composition"]["rows"][0]["dependencies"][0]["item_id"] = (
            "another-realization"
        )
    with pytest.raises(ValueError):
        validate_payload(m, p)


def test_registered_checkpoint_contract_is_100_300_1000(tmp_path, monkeypatch):
    setup = setup_cell(tmp_path, monkeypatch)
    m, p = copy.deepcopy(setup[1]), copy.deepcopy(setup[2])
    m["mode"] = "stage4_sealed_cell"
    with pytest.raises(ValueError, match="registered checkpoints"):
        validate_payload(m, p)


class TinyTok(EndpointTokenizer):
    def __init__(self):
        self.strings = {63: "\n"}
        self.ids = {"\n": 63}

    def encode(self, text):
        if text.endswith("\n"):
            return np.int32([self.token(text[:-1]), 63])
        return np.int32([self.token(text)])

    def decode(self, ids):
        return "".join(self.strings.get(int(i), str(int(i))) for i in ids)


def test_actual_tiny_base_checkpoint_execution(tmp_path, monkeypatch):
    tok, base = TinyTok(), TinyBase()
    cfg = _cfg()
    cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
    adapter = build_adapter(
        "R1_learned_ff", base, Ledger(), calibration=CAL, synthetic=True, revision_config=cfg
    )
    p = payload(1, composition=False)
    # Missing challenge rows stay planned, so this smoke does not require
    # learning out-of-vocabulary fixture labels on the 64-token base.
    p["endpoints"]["near_miss"]["rows"] = []
    p["endpoints"]["revision"]["rows"] = []
    setup = setup_cell(tmp_path, monkeypatch, data=p, adapter=adapter, tok=tok)
    result = invoke(setup)
    assert result["status"] == "complete"
    report = json.loads((Path(result["attempt_dir"]) / "checkpoint-1.json").read_text())
    assert len(report["retention"]["rows"]) == 1
    assert report["unseen"]["summary"]["firing_observed_n"] == 1
    assert base.calls["forward"] > 0


def test_v0_missing_revision_observer_keeps_answer_metric(tmp_path, monkeypatch):
    from pccap.revision_v1.stage4_assays import _Challenges

    tok = Tokenizer()
    cap = Cap(tok)

    # A cap-shaped fixture with genuine slot-like memory but no store API.
    class V0:
        base = cap.base

        def __getattr__(self, name):
            if name == "store":
                raise AttributeError(name)
            return getattr(cap, name)

    adapter = CellAdapter(V0(), "v0_stable")
    adapter.memory_inventory = lambda history: []
    result = _Challenges(adapter, tok).revision(revision_row())
    assert result["status"] == "ok" and result["latest_answer_success"]
    assert result["revision_success"] is None and result["old_record_retired"] is None


def test_100_300_1000_scheduling_with_behavioral_misses(tmp_path, monkeypatch):
    tok = Tokenizer()
    for text in (" unknown", " new", " old", " final"):
        tok.encode(text)

    class Counting:
        def __init__(self):
            from tests.revision_v1.test_endpoints import Base

            self.base = Base(tok, {})
            self.n = 0
            self.store = SimpleNamespace(records=[])

        def export_state(self):
            return LearnerState(scalars={"n": self.n})

        def import_state(self, st):
            self.n = st.scalars["n"]

        def state_hash(self):
            return self.export_state().content_hash()

        def predict(self, ids):
            return self.base.forward(ids)

        def update_item(self, it):
            self.n += 1
            return SimpleNamespace(
                code="rejected_no_improvement",
                codes=["miss"],
                cost=CostRecord(phase="learning", full_forwards=1),
            )

    p = payload(1000, composition=False)
    p["endpoints"]["near_miss"]["rows"] = []
    p["endpoints"]["revision"]["rows"] = []
    setup = setup_cell(
        tmp_path,
        monkeypatch,
        data=p,
        adapter=CellAdapter(Counting(), "R1_learned_ff"),
        tok=tok,
        checkpoints=[100, 300, 1000],
    )
    result = invoke(setup)
    run = Path(result["run_dir"])
    receipts = [json.loads(p.read_text()) for p in run.glob("attempt-*/checkpoint-*.receipt.json")]
    assert sorted(r["checkpoint"] for r in receipts) == [100, 300, 1000]
    report = json.loads((Path(result["attempt_dir"]) / "checkpoint-1000.json").read_text())
    assert len(report["history"]) == len(report["retention"]["rows"]) == 1000
    assert all(r["es"] == 0 for r in report["retention"]["rows"])
    assert all(r["outcome"]["code"] == "rejected_no_improvement" for r in report["history"])
