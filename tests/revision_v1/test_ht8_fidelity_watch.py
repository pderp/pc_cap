"""Watch boundaries, independent references, durable idempotence and certified inputs."""

import copy
import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import numpy as np
import pytest
from scripts import ht8_fidelity_watch as watch
from scripts import r1_63l_full_validation_contract as full

from tests.revision_v1.test_r1_49m_fidelity_policy import receipt_cell, save_report


@pytest.fixture
def scratch(monkeypatch):
    root = watch.ROOT.parent / "assets/runs/pc_cap/R1/rehearsal_fixtures/round34" / uuid4().hex
    root.mkdir(parents=True)
    monkeypatch.setattr(watch, "ROOT", root)
    return root


def observation(
    n,
    *,
    kl=0.001,
    nll=0.01,
    other_kl=0.001,
    other_nll=0.01,
    condition="primary",
    dataset="mquake",
    scope="development",
):
    cell = dict(condition=condition, dataset=dataset, realization=scope, order=n)
    identity = dict(mode=scope, recipe_sha256=str(n) * 64, cell=cell)
    # Journal behavior fixture only: real receipt/vector validation tested below.
    values = np.full((2, 2, 5), 2.0)
    values[:, :, 3:] = 0.001
    references = {
        name: dict(
            kl=dict(mean_signed=k),
            loss=dict(mean_signed=d, ES95_positive=max(d, 0), maximum_positive=max(d, 0)),
        )
        for name, k, d in (("original", kl, nll), ("capoff", other_kl, other_nll))
    }
    return dict(
        identity=identity,
        cell_id=full.digest(identity),
        cell=cell,
        scope=scope,
        recipe=dict(path="synthetic", sha256=str(n) * 64),
        checkpoint=300,
        actual_records=300,
        references=references,
        concentration=watch.concentration.concentration(values),
        bindings_sha256={},
    )


def journal(root):
    return [
        json.loads(line)
        for line in (root / "results/R1/fidelity_watch/observations.jsonl").read_text().splitlines()
    ]


@pytest.mark.parametrize(
    "kwargs,breaches",
    [
        ({}, 0),
        ({"kl": 0.00100001}, 1),
        ({"nll": 0.01000001}, 1),
        ({"other_kl": 0.00100001}, 1),
        ({"other_nll": 0.01000001}, 1),
    ],
)
def test_equality_passes_and_either_reference_can_breach(scratch, kwargs, breaches):
    out = watch.update([observation(1, **kwargs)])
    assert out["audited_cells"] == 1 and out["breaches"] == breaches
    assert out["alerts"] == 0 and not out["admission_veto"]


def test_running_maxima_and_fixed_development_reference(scratch):
    baseline = observation(1, kl=0.002, nll=0.0)
    watch.update([baseline])
    equal = watch.update([observation(2, kl=0.002, nll=0.0, scope="confirmatory")])
    assert not equal["new_alerts"]
    raised = watch.update([observation(3, kl=0.004, nll=0.0, scope="confirmatory")])
    assert {r["kind"] for r in raised["new_alerts"][0]["reasons"]} == {"new_running_maximum"}
    over = watch.update([observation(4, kl=0.0041, nll=0.0, scope="confirmatory")])
    assert {r["kind"] for r in over["new_alerts"][0]["reasons"]} == {
        "new_running_maximum",
        "above_twice_development_reference",
    }
    # Below running maximum but still >2x frozen development reference remains an alert.
    again = watch.update([observation(5, kl=0.00405, nll=0.0, scope="development")])
    assert {r["kind"] for r in again["new_alerts"][0]["reasons"]} == {
        "above_twice_development_reference"
    }
    state = watch.replay(journal(scratch))
    assert state["development_references"]["primary:mquake"]["cell_id"] == baseline["cell_id"]
    assert state["maxima"]["primary:mquake"]["original"]["mean_kl"]["value"] == 0.0041


def test_groups_references_and_zero_development_reference_are_separate(scratch):
    watch.update([observation(1, kl=0, nll=0, other_kl=0, other_nll=0)])
    out = watch.update([observation(2, kl=0, nll=0, other_kl=0.002, other_nll=0)])
    assert {r["reference"] for r in out["new_alerts"][0]["reasons"]} == {"capoff"}
    other = watch.update([observation(3, kl=0.1, condition="other")])
    assert not other["new_alerts"]
    third = watch.update([observation(4, kl=0.1, dataset="zsre", scope="confirmatory")])
    assert not third["new_alerts"]
    assert "primary:zsre" not in watch.replay(journal(scratch))["development_references"]


def test_duplicate_concurrent_writers_and_manual_notes_preserved(scratch):
    doc = scratch / "docs/fidelity_watch.md"
    doc.parent.mkdir()
    manual = "# Fidelity watch\n\nManual first entry is retained.\n"
    doc.write_text(manual)
    obs = observation(1, kl=0.00554)
    with ThreadPoolExecutor(max_workers=2) as pool:
        out = list(pool.map(lambda _: watch.update([obs]), range(2)))
    assert sum(r["new_cells"] for r in out) == 1
    assert len(journal(scratch)) == 1
    assert doc.read_text().startswith(manual)
    assert doc.read_text().count(watch.BEGIN) == 1
    before = doc.read_bytes()
    assert watch.update([obs])["new_cells"] == 0
    assert doc.read_bytes() == before
    bad = copy.deepcopy(obs)
    bad["references"]["original"]["kl"]["mean_signed"] *= 2
    with pytest.raises(ValueError, match="changed evidence"):
        watch.update([bad])


def test_crash_between_journal_and_views_is_repaired_without_duplicate(scratch, monkeypatch):
    obs = observation(1, kl=0.1)
    original = watch.atomic_write
    monkeypatch.setattr(
        watch, "atomic_write", lambda *a: (_ for _ in ()).throw(OSError("simulated disk error"))
    )
    with pytest.raises(OSError):
        watch.update([obs])
    assert len(journal(scratch)) == 1
    monkeypatch.setattr(watch, "atomic_write", original)
    out = watch.update([obs])
    assert out["new_cells"] == 0 and out["breaches"] == 1
    assert len((scratch / "results/R1/fidelity_watch/entries.jsonl").read_text().splitlines()) == 1


def test_torn_journal_fails_visibly(scratch):
    watch.update([observation(1)])
    path = scratch / "results/R1/fidelity_watch/observations.jsonl"
    path.write_text(path.read_text() + '{"partial":')
    with pytest.raises(ValueError, match="torn watch journal"):
        watch.update([observation(2)])


def certified_fixture(monkeypatch, scratch):
    cell, report, vector = receipt_cell(monkeypatch, scratch)
    spec = cell["full_validation"]
    spec["sample_windows"] = 1
    recipe = dict(
        mode="stage4_sealed_cell",
        cell={k: cell[k] for k in ("condition", "dataset", "realization", "order")},
        checkpoints=[300],
        full_validation=spec,
        adapter_identity=dict(base_sha256="tiny", locality_base_sha256="tiny"),
    )
    path = scratch / "docs/tasks/recipe.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(recipe))
    b = full.ref(path)
    cell["manifest_sha256"] = b["sha256"]
    report["endpoints"]["full_validation"].update(
        manifest_sha256=b["sha256"], contract_sha256=full.digest(spec)
    )
    meta_path = vector.parent.parent / "cell.json"
    meta = json.loads(meta_path.read_text())
    meta["manifest_sha256"] = b["sha256"]
    meta_path.write_text(json.dumps(meta))
    save_report(cell, report, vector)
    result_path = vector.parent / "result.json"
    result = json.loads(result_path.read_text())
    result["mode"] = recipe["mode"]
    result_path.write_text(json.dumps(result))
    return b, result_path, cell, report, vector


def test_independent_real_vectors_receipts_and_post_cell_hook(scratch, monkeypatch):
    b, result, cell, _, _ = certified_fixture(monkeypatch, scratch)
    obs = watch.inspect(b, result)
    assert obs["scope"] == "confirmatory" and not obs["benchmark"]["passes"]
    assert obs["concentration"]["positions"] == 4
    matrix = dict(full_validation=cell["full_validation"], fidelity_watch=watch.binding())
    out = watch.post_cell(matrix, cell, dict(recipes={cell["cell_id"]: b}))
    assert out["breaches"] == 1 and out["new_cells"] == 1
    assert watch.post_cell(matrix, cell, dict(recipes={cell["cell_id"]: b}))["new_cells"] == 0


@pytest.mark.parametrize(
    "fault", ["vector", "report", "chain", "result", "recipe", "missing", "duplicate"]
)
def test_invalid_evidence_cannot_become_watch_entry(scratch, monkeypatch, fault):
    b, result, cell, report, vector = certified_fixture(monkeypatch, scratch)
    if fault == "vector":
        vector.write_bytes(vector.read_bytes() + b"changed")
    elif fault == "report":
        p = vector.parent / "checkpoint-300.json"
        p.write_text(p.read_text() + " ")
    elif fault == "chain":
        p = vector.parent / "checkpoint-300.receipt.json"
        obj = json.loads(p.read_text())
        obj["previous_receipt_sha256"] = "changed"
        p.write_text(json.dumps(obj))
    elif fault == "result":
        obj = json.loads(result.read_text())
        obj["status"] = "incomplete"
        result.write_text(json.dumps(obj))
    elif fault == "recipe":
        b["sha256"] = "wrong"
    elif fault == "missing":
        del report["endpoints"]["full_validation"]
        save_report(cell, report, vector)
        obj = json.loads(result.read_text())
        obj["mode"] = "stage4_sealed_cell"
        result.write_text(json.dumps(obj))
    else:
        target = result.parent.parent / "attempt-0001/result.json"
        target.parent.mkdir()
        target.write_bytes(result.read_bytes())
    with pytest.raises(ValueError):
        watch.inspect(b, result)
    assert not (scratch / "results/R1/fidelity_watch/observations.jsonl").exists()


def test_queue_binding_rejects_omission_and_source_changes():
    with pytest.raises(ValueError, match="missing or changed"):
        watch.validate_queue_binding(dict(full_validation={}))
    m = dict(full_validation={}, fidelity_watch=watch.binding())
    assert watch.validate_queue_binding(m)
    m["fidelity_watch"]["implementations"][0]["sha256"] = "changed"
    with pytest.raises(ValueError, match="missing or changed"):
        watch.validate_queue_binding(m)
    assert not watch.validate_queue_binding({})


def test_scanner_handles_catalog_inventory_and_report_hook(scratch, monkeypatch):
    b, result, _, _, vector = certified_fixture(monkeypatch, scratch)
    inventory = scratch / "docs/tasks/inspection-receipts.json"
    inventory.write_text("[]")
    observations, unavailable = watch.scan([b["path"], inventory], [scratch / "results"])
    assert len(observations) == 1 and not unavailable
    assert not (scratch / "results/R1/fidelity_watch").exists()  # scan is read-only
    report = dict(
        cells=dict(
            complete=dict(
                status="complete_development_measurement",
                recipe=b,
                full=dict(vectors=full.ref(vector)),
            ),
            pending=dict(status="awaiting_completed_result"),
        )
    )
    out = watch.update_report(report)
    assert out["new_cells"] == 1 and out["breaches"] == 1
    assert watch.update_report(report)["new_cells"] == 0
    assert journal(scratch)[0]["observation"]["result"] == full.ref(result)
