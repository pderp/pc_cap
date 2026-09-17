"""Isolated actual sealed admission and TinyBase execution; no owner results writes."""

from __future__ import annotations

import copy
import json
import uuid
from dataclasses import replace
from pathlib import Path

import pytest
from scripts import r1_68c_dev_cell as donor
from scripts import r1_75_analysis_stage4_v1 as analysis
from scripts import r1_77b_sealed_backend as backend

import pccap  # noqa: F401
from pccap.harness.ledger import Ledger
from pccap.revision_v1 import stage4_cell as core
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_stage4_cell import CAL, TinyTok, payload
from tests.revision_v1.tiny_base import TinyBase

REPO = Path(__file__).resolve().parents[2]


class FixtureRoot:
    def __init__(self, path):
        self.path = path

    def __truediv__(self, other):
        return self.path / other

    @property
    def parent(self):
        return REPO.parent


def new_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True)
    return {"path": str(path), "sha256": backend.sha(path)}


@pytest.fixture
def make(monkeypatch):
    root = REPO / "logs/r1_round19/sealed_tests" / uuid.uuid4().hex
    resources = REPO.parent / "assets/test_scratch/r1_round19" / root.name
    monkeypatch.setattr(backend, "ROOT", FixtureRoot(root))
    monkeypatch.setattr(backend, "OUTPUT_ROOT", root / "results/R1/stage4_sealed_cells")
    monkeypatch.setattr(backend, "RESOURCE_ROOT", resources / "snapshots")
    monkeypatch.setattr(backend, "RECEIPT_ROOT", root / "logs/execution")
    monkeypatch.setattr(analysis, "ROOT", root)
    # Small cadence only in the isolated test process. All sealed checks execute.
    monkeypatch.setattr(core, "CHECKPOINTS", (1, 2))

    def fixture(
        *,
        profile="incremental",
        change=None,
        bad_reservation=False,
        missing_locality=False,
        condition="R1_learned_ff",
        drift_implementation=None,
        data_override=None,
        reservations_override=None,
        realization="tiny",
        order="0",
    ):
        data = (
            copy.deepcopy(data_override)
            if data_override is not None
            else payload(2, composition=True)
        )
        if missing_locality:
            data["endpoints"]["locality"]["rows"] = []
        tok = TinyTok()

        def prime(value, key=""):
            if isinstance(value, dict):
                for k, v in sorted(value.items()):
                    prime(v, k)
            elif isinstance(value, list):
                for v in value:
                    prime(v, key)
            elif isinstance(value, str) and key in {
                "prompt",
                "edit_prompt",
                "neighbour_prompt",
                "paraphrases",
                "questions",
                "answer",
                "edit_answer",
                "new_answer",
            }:
                tok.encode(" " + value + "\n" if "answer" in key else value)

        prime(data)
        tok.file_sha256 = lambda: "a" * 64

        def factory(m):
            cfg = _cfg()
            cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
            from tests.revision_v1.test_r1_68e_batched_drift_v0 import RetainedTinyBase

            cap = build_adapter(
                condition,
                TinyBase() if condition.startswith("R1_") else RetainedTinyBase(),
                Ledger(),
                calibration=CAL,
                synthetic=True,
                revision_config=cfg if condition.startswith("R1_") else None,
            )
            return cap, tok

        cap, _ = factory(None)
        m = {
            "schema_version": 1,
            "mode": backend.MODE,
            "cell": {
                "condition": cap.condition,
                "dataset": data["items"][0]["dataset"],
                "realization": realization,
                "order": order,
            },
            "backend": backend.backend_binding(),
            "code_sha256": core.code_identity(REPO),
            "adapter_identity": cap.identity(),
            "tokenizer_sha256": "a" * 64,
            "checkpoints": [1, 2],
            "max_new": 32,
            "integrity_profile": profile,
            "integrity_batch_edits": 1,
            "drift_batch_size": 2,
            "integrity_driver_bindings": donor.driver_bindings(REPO),
            "admission": dict(
                lead_approved=True,
                protocol_frozen=True,
                condition_admitted=True,
                launch_authorized=True,
                endpoint_bundle_sha256=core.content_digest(data["endpoints"]),
                ordered_item_ids_sha256=core.digest([r["item_id"] for r in data["items"]]),
            ),
        }
        if drift_implementation is not None:
            m["drift_implementation"] = drift_implementation
        m["payload"] = new_json(resources / "payload.json", data)
        roles = [
            {
                "dataset": "mquake",
                "realization": "tiny",
                "role": role,
                "items": [
                    dict(
                        r, payload_sha256=("0" * 64 if bad_reservation else core.content_digest(r))
                    )
                    for r in rows
                ],
            }
            for role, rows in [
                ("edits", data["items"]),
                ("outside", data["endpoints"]["unseen"]["rows"]),
            ]
        ]
        m["reservations"] = new_json(
            resources / "reservations.json",
            reservations_override
            if reservations_override is not None
            else {"mode": "content_sealed_fact_reservations", "allocations": roles},
        )
        m["protocol"] = new_json(
            root / "manifests/revision_v1/protocol.json",
            {
                "schema_version": 1,
                "mode": "stage4_final_protocol",
                "lead_approved": True,
                "open_gates": [],
                "checkpoints": [1, 2],
                "max_new": 32,
                "locality_score": "bounded_text_equality_DEC053",
                "experiment_deadline": "2026-10-09",
            },
        )
        m["population"] = new_json(
            resources / "population.json",
            {"cells": {analysis.coordinate_id(m["cell"]): backend.planned_population(data)}},
        )
        gates = {
            g: new_json(
                root / f"docs/tasks/{g}.json",
                {"gate": g, "status": "closed", "lead_approved": True},
            )
            for g in backend.GATES
        }
        frozen = {
            "schema_version": 1,
            "mode": "stage4_final_freeze",
            "lead_approved": True,
            "launch_authorized": True,
            "open_gates": [],
            "closed_gates": gates,
            "bindings_sha256": {
                str(REPO / "requirements.lock"): backend.sha(REPO / "requirements.lock")
            },
            **{
                k: m[k]
                for k in (
                    "backend",
                    "code_sha256",
                    "integrity_driver_bindings",
                    "protocol",
                    "reservations",
                    "population",
                )
            },
        }
        if change:
            change(m, frozen, data)
        frozen["recipe_contracts"] = {analysis.coordinate_id(m["cell"]): backend.contract_digest(m)}
        if reservations_override is not None:
            new_json(
                root / "docs/tasks/synthetic-freeze-candidate.json",
                {**frozen, "mode": "synthetic_candidate_not_frozen", "launch_authorized": False},
            )
        m["freeze"] = new_json(root / backend.FROZEN_RELATIVE, frozen)
        binding = new_json(root / "docs/tasks/recipe.json", m)

        def execute(**kw):
            return backend.execute(
                binding["path"], binding["sha256"], code_root=REPO, factory=factory, **kw
            )

        return {
            "m": m,
            "data": data,
            "binding": binding,
            "root": root,
            "factory": factory,
            "execute": execute,
            "resources": resources,
        }

    return fixture


def observed(f, result):
    m = f["m"]
    c = {
        **m["cell"],
        "cell_id": analysis.coordinate_id(m["cell"]),
        "block_number": 1,
        "within_block_order": 1,
        "result_dir": result["run_dir"],
        "manifest_sha256": f["binding"]["sha256"],
        "checkpoints": m["checkpoints"],
        "admitted": True,
        "population": backend.planned_population(f["data"]),
        **{k: m[k] for k in ("adapter_identity", "code_sha256")},
        "payload_sha256": m["payload"]["sha256"],
    }
    files = analysis.Files()
    o = analysis.load_cell(c, files, "confirmatory")
    files.verify()
    return o, c


def test_metadata_does_not_read_payload(make, monkeypatch):
    f = make()

    def fail(*a, **kw):
        raise AssertionError("sealed payload must not open during inspect")

    monkeypatch.setattr(core, "load_cell", fail)
    info = backend.inspect(
        **{
            "path": f["binding"]["path"],
            "expected_sha256": f["binding"]["sha256"],
            "code_root": REPO,
        }
    )
    assert not info["payload_read"] and not info["model_constructed"]


@pytest.mark.parametrize("profile", ["full", "incremental"])
def test_sealed_complete_population_and_resume(make, profile):
    f = make(profile=profile)
    first = f["execute"](stop_after_checkpoint=1)
    assert first["status"] == "paused_at_checkpoint"
    o, _ = observed(f, first)
    assert not o["artifact_complete"] and o["missing_checkpoints"] == [2]
    result = f["execute"](resume=True)
    o, _ = observed(f, result)
    assert o["artifact_complete"] and o["primary_metrics_complete"] and o["scientific_admission"]
    assert [b["boundary"] for b in result["boundary_identity_checks"]] == [
        "attempt_start",
        "resume_after_restore",
        "checkpoint:2",
        "completion",
    ]
    with pytest.raises(ValueError, match="already complete"):
        f["execute"](resume=True)


@pytest.mark.parametrize("target", ["code", "backend", "gate", "protocol", "admission", "adapter"])
def test_wrong_identity_refuses_and_charges(make, target):
    def change(m, f, p):
        if target == "code":
            m["code_sha256"] = "0" * 64
        if target == "backend":
            m["backend"] = {**m["backend"], "sha256": "0" * 64}
        if target == "gate":
            f["open_gates"] = ["U12"]
        if target == "protocol":
            f["protocol"] = {**m["protocol"], "sha256": "0" * 64}
        if target == "admission":
            m["admission"]["launch_authorized"] = False
        if target == "adapter":
            m["adapter_identity"] = {**m["adapter_identity"], "base_sha256": "wrong"}

    f = make(change=change)
    with pytest.raises((ValueError, PermissionError)):
        f["execute"]()
    endings = list((f["root"] / "logs/execution").glob("*/finish.json"))
    assert len(endings) == 1
    row = json.loads(endings[0].read_text())
    assert row["status"] == "failed" and row["charged_process_wall_seconds"] >= 0


def test_wrong_reservation_refuses(make):
    f = make(bad_reservation=True)
    with pytest.raises(ValueError, match="reserved edit payload"):
        f["execute"]()


def test_torn_journal_refuses_resume(make):
    f = make()
    first = f["execute"](stop_after_checkpoint=1)
    new_json(Path(first["attempt_dir"]) / "phases/999999.intent.json", {"unpaired": "intent"})
    with pytest.raises((ValueError, KeyError)):
        f["execute"](resume=True)


def test_duplicate_launch_lock_refuses(make):
    import fcntl

    f = make()
    locks = f["root"] / "logs/r1_77b_locks"
    locks.mkdir(parents=True)
    with (locks / (analysis.coordinate_id(f["m"]["cell"]) + ".lock")).open("x") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(BlockingIOError):
            f["execute"]()


def test_construction_failure_and_deadline_charged(make, monkeypatch):
    f = make()

    def fail(m):
        raise MemoryError("synthetic construction failure")

    with pytest.raises(MemoryError):
        backend.execute(f["binding"]["path"], f["binding"]["sha256"], code_root=REPO, factory=fail)

    def expired():
        raise TimeoutError("October 9")

    monkeypatch.setattr(backend, "deadline_check", expired)
    with pytest.raises(TimeoutError):
        f["execute"]()
    rows = [json.loads(p.read_text()) for p in (f["root"] / "logs/execution").glob("*/finish.json")]
    assert {r["error"]["type"] for r in rows} == {"MemoryError", "TimeoutError"}


def test_deadline_exact_boundary():
    from datetime import datetime
    from zoneinfo import ZoneInfo

    limit = datetime(2026, 10, 10, tzinfo=ZoneInfo("America/New_York")).timestamp()
    backend.deadline_check(limit - 0.001)
    with pytest.raises(TimeoutError):
        backend.deadline_check(limit)


def test_population_missing_locality_never_scientific_complete(make):
    f = make(missing_locality=True)
    r = f["execute"]()
    o, _ = observed(f, r)
    assert (
        o["artifact_complete"]
        and not o["primary_metrics_complete"]
        and not o["scientific_admission"]
    )


def test_query_immutable_mutation_aborts(make, monkeypatch):
    f = make()
    original = backend.CellAssays.item

    def mutate(self, *a, **kw):
        result = original(self, *a, **kw)
        self.adapter.learner.cfg.null_threshold = 123.0
        return result

    monkeypatch.setattr(backend.CellAssays, "item", mutate)
    with pytest.raises(RuntimeError, match="mutated"):
        f["execute"]()
    assert list((f["root"] / "results").glob("**/failure.json"))


def test_no_development_loader_call(make, monkeypatch):
    f = make()

    def fail(*a, **kw):
        raise AssertionError("development loader called")

    monkeypatch.setattr(donor, "load_development_cell", fail)
    assert f["execute"]()["status"] == "complete"


def test_snapshot_identity_refuses_resume(make, monkeypatch):
    f = make()
    f["execute"](stop_after_checkpoint=1)
    old = backend.sha

    def wrong(path):
        return "0" * 64 if str(path).endswith("checkpoint-1.snapshot") else old(path)

    monkeypatch.setattr(backend, "sha", wrong)
    with pytest.raises(ValueError, match="snapshot file"):
        f["execute"](resume=True)


def test_wrong_initial_state_refuses_resume(make):
    from pccap.revision_v1.endpoints_composition import as_edit

    f = make()
    f["execute"](stop_after_checkpoint=1)

    def nonempty(m):
        cap, tok = f["factory"](m)
        cap.update_item(as_edit(f["data"]["items"][0], tok))
        return cap, tok

    with pytest.raises(ValueError, match="initial state"):
        backend.execute(
            f["binding"]["path"],
            f["binding"]["sha256"],
            code_root=REPO,
            factory=nonempty,
            resume=True,
        )


def test_duplicate_checkpoint_refuses(make):
    f = make()
    first = f["execute"](stop_after_checkpoint=1)
    receipt = Path(first["attempt_dir"]) / "checkpoint-1.receipt.json"
    new_json(receipt.parent / "checkpoint-999.receipt.json", json.loads(receipt.read_text()))
    with pytest.raises(ValueError, match="unique contiguous"):
        f["execute"](resume=True)


def test_unknown_execution_cost_refuses(make):
    f = make()
    new_json(f["root"] / "logs/execution/abandoned/start.json", {"recipe": f["binding"]})
    with pytest.raises(ValueError, match="unknown prior"):
        f["execute"]()
