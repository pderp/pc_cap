"""Audit existing classifier behavior; do not amend the scientific policy."""

import json
import uuid

import pytest
from scripts import r1_49g_inference as inference
from scripts import r1_49l_fidelity_audit as audit
from scripts import r1_75_analysis_stage4_v1 as analysis


def test_failed_gate_keeps_intervals_and_suppresses_only_affected_labels():
    r = audit.classifier_rehearsal()["scenarios"]
    for name, expected in (
        ("all_admitted", 0),
        ("one_primary_cell_failed_fidelity", 7),
        ("one_control_cell_failed_fidelity", 1),
    ):
        zsre = [x for x in r[name] if x["dataset"] == "zsre"]
        assert sum(x["classification"] == "unavailable" for x in zsre) == expected
        assert all(
            m["status"] == "complete" and m["adjusted_interval"]
            for x in zsre
            for m in x["metrics"].values()
        )
        assert all(x["pairing_issues"] == [] for x in zsre)
        assert all(
            x["classification"] == "positive" for x in r[name] if x["dataset"] == "counterfact"
        )
        assert all(
            x["classification"] == "unavailable" for x in r[name] if x["dataset"] == "mquake"
        )
        assert sum(x["interval_count"] for x in r[name]) == 63
    before, after = r["all_admitted"], r["one_primary_cell_failed_fidelity"]
    assert [x["metrics"] for x in before] == [x["metrics"] for x in after]


@pytest.mark.parametrize(
    "passes,complete,expected", [(True, True, True), (False, True, False), (None, False, False)]
)
def test_cell_status_distinguishes_measured_failure_from_absence(
    monkeypatch, passes, complete, expected
):
    directory = analysis.ROOT / "results/R1/r1_49l_cpu_tests" / uuid.uuid4().hex
    attempt = directory / "attempt-0000"
    attempt.mkdir(parents=True)
    coords = dict(condition="R1_learned_ff", dataset="zsre", realization=0, order=100)
    pop = dict(
        item_ids=["edit"],
        paraphrase_counts=[1],
        endpoints=dict(locality=["loc"], unseen=[], near_miss=[], revision=[]),
        drift=dict(expected_positions=1),
        full_validation={"synthetic_control_flow": True},
    )
    cell = dict(
        coords,
        cell_id=analysis.coordinate_id(coords),
        block_number=1,
        within_block_order=1,
        population=pop,
        checkpoints=[1],
        admitted=True,
        result_dir=str(directory),
        manifest_sha256="a" * 64,
    )

    def write(path, value):
        with path.open("x") as f:
            json.dump(value, f)
        return audit.binding(path)

    write(
        directory / "cell.json",
        dict(
            cell=coords,
            manifest_sha256="a" * 64,
            checkpoints=[1],
            mode="stage4_sealed_cell",
            adapter_identity={},
        ),
    )
    row = dict(item_id="edit", status="ok", paraphrase_n=1, es=1.0, gs=1.0)
    generation = dict(generated="same", truncated=False)
    report = dict(
        checkpoint=1,
        state_sha256="s",
        mode="stage4_sealed_cell",
        history=[row],
        retention=dict(rows=[row]),
        locality=dict(
            rows=[dict(item_id="loc", status="ok", reference=generation, query=generation)]
        ),
        endpoints=dict(drift=dict(rows=[dict(item_id="w0:p1", cap=2.0, original=2.0, capoff=2.0)])),
    )
    report_ref = write(attempt / "checkpoint-1.json", report)
    receipt = dict(
        checkpoint=1,
        report=report_ref,
        manifest_sha256="a" * 64,
        state_sha256="s",
        mode="stage4_sealed_cell",
        previous_receipt_sha256=None,
    )
    receipt["receipt_sha256"] = analysis.digest(receipt)
    write(attempt / "checkpoint-1.receipt.json", receipt)
    write(
        attempt / "result.json",
        dict(
            cell=coords,
            manifest_sha256="a" * 64,
            status="complete",
            completed_checkpoint=1,
            last_receipt_sha256=receipt["receipt_sha256"],
        ),
    )
    # Isolate admission wiring. Numeric/vector integrity is tested by R1-63l;
    # this fixture deliberately supplies a summary instead of running a model.
    monkeypatch.setattr(
        analysis.full_contract,
        "summary",
        lambda *a, **k: dict(
            complete=complete, fidelity=None if not complete else dict(passes=passes)
        ),
    )
    observed = analysis.load_cell(cell, analysis.Files(), "confirmatory")
    assert observed["status"] == "complete_artifacts"
    assert observed["primary_metrics_complete"]
    assert observed["endpoint_complete"] is complete
    assert observed["scientific_admission"] is expected
    assert observed["checkpoints"]["1"]["primary"]["RET-GS"]["value"] == 1.0


def test_failed_admission_precedes_even_negative_dec058_metrics():
    from tests.revision_v1.test_r1_49g_analysis import stats

    measured = stats(g=0.01, gl=-0.02, gu=0.04)
    assert inference.classify(measured, admitted=True) == "negative"
    assert inference.classify(measured, admitted=False) == "unavailable"
