"""Exact approval, sequential state, durable refusal and rollback; no real actions."""

from __future__ import annotations

import copy
from pathlib import Path
from uuid import uuid4

import pytest
from scripts import r1_58g_operator as op
from scripts import r1_d9_receipts as d9

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture
def operator_workspace():
    # Production admission reads deliberately refuse metadata outside repo logs/docs.
    # Keep synthetic receipts within that real boundary, even with default pytest tmpdir.
    path = REPO / "logs/r1_round27" / ("operator-test-" + uuid4().hex)
    path.mkdir()
    return path


def sign(report):
    form = copy.deepcopy(report["lead_sets"])
    form.update(
        lead_approved=True, lead_signature=dict(name="Synthetic test lead", date="2026-09-17")
    )
    return form


def test_signature_must_match_current_fields_and_named_lead():
    request = dict(step="protocol-admit", fields={"extension_admitted": False})
    form = dict(
        step="protocol-admit",
        request_sha256=d9.core.content_digest(request),
        lead_approved=True,
        lead_signature=dict(name="Synthetic lead", date="2026-09-17"),
    )
    op.validate_signature(form, request)
    for bad in [
        {**form, "lead_approved": False},
        {**form, "request_sha256": "changed"},
        {**form, "lead_signature": {"name": None}},
    ]:
        with pytest.raises((ValueError, PermissionError)):
            op.validate_signature(bad, request)
    with pytest.raises(PermissionError):
        op.validate_signature(form, {**request, "fields": {"extension_admitted": True}})


def test_journal_detects_tampering_and_torn_tail(operator_workspace):
    tmp_path = operator_workspace
    p = tmp_path / "receipts.jsonl"
    op.journal_append(p, [], dict(status="dry_run", step="clearance"))
    rows = op.journal_read(p)
    op.journal_append(p, rows, dict(status="failed", step="clearance"))
    assert len(op.journal_read(p)) == 2
    raw = p.read_text()
    p.write_text(raw.replace("failed", "complete"))
    with pytest.raises(ValueError):
        op.journal_read(p)
    p.write_text(raw + '{"torn":')
    with pytest.raises(ValueError):
        op.journal_read(p)


@pytest.mark.parametrize("coordinated", [False, True])
def test_one_step_requires_signature_and_failure_cannot_sign_downstream(
    operator_workspace, monkeypatch, coordinated
):
    tmp_path = operator_workspace
    monkeypatch.setattr(op, "ROOT", tmp_path)
    monkeypatch.setattr(op, "verify_candidate", lambda _: None)
    base = REPO / f"docs/tasks/R1-D9-inputs-v{6 if coordinated else 5}.json"
    candidate = REPO / "manifests/revision_v1/freeze_candidate_v9.json"
    session = tmp_path / "logs/session"
    args = dict(inputs=base, candidate=candidate, session=session)
    early = op.run("draw", **args)
    assert early["blocked"] and "next unsigned step" in early["blocked"][0]
    initial = op.run("protocol-admit", **args)
    assert initial["blocked"]
    form = initial["lead_sets"]
    form["fields"].update(
        extension_admitted=False,
        near_family_reviewed=True,
        zsre_empty_baseline_reviewed=True,
        queue_ceiling_and_failure_policy_reviewed=True,
        family_pair_unit_policy_reviewed=coordinated,
        synthetic=True,
    )
    ready = op.run("protocol-admit", form=form, **args)
    assert not ready["blocked"]
    with pytest.raises(PermissionError):
        op.run("protocol-admit", form=form, execute=True, **args)
    result = op.run("protocol-admit", form=sign(ready), execute=True, **args)
    assert result["status"] == "complete"
    new_spec = d9.read_metadata(result["inputs"])
    assert d9.read_metadata(new_spec["receipts"]["protocol_admission"])["lead_approved"]
    assert not d9.read_metadata(new_spec["receipts"]["rng_admission"])["lead_approved"]
    if coordinated:
        decision = d9.read_metadata(new_spec["near_allocation_decision"])
        assert decision["lead_approved"] is True and decision["status"] == "closed"
        assert decision["lead_signature"]["name"] == "Synthetic test lead"
        assert not d9.read_metadata(d9.read_metadata(d9.ref(base))["near_allocation_decision"])[
            "lead_approved"
        ]
    assert not d9.read_metadata(d9.read_metadata(d9.ref(base))["receipts"]["protocol_admission"])[
        "lead_approved"
    ]
    with pytest.raises(PermissionError):
        op.run("draw", execute=True, form=sign(early), **args)
    rows = op.journal_read(session / "receipts.jsonl")
    assert [r["step"] for r in rows if r["status"] == "complete"] == ["protocol-admit"]
    assert rows[-1]["downstream_signed"] is False


def test_freeze_publication_failure_rolls_back_only_new_files(operator_workspace, monkeypatch):
    tmp_path = operator_workspace
    monkeypatch.setattr(op, "ROOT", tmp_path)
    source = tmp_path / "docs/tasks/source.json"
    binding = op.new_json(source, dict(synthetic=True))
    preexisting = tmp_path / "docs/tasks/keep.json"
    preexisting.write_text("untouched")
    target = tmp_path / "docs/tasks/new.json"
    frozen = tmp_path / op.backend.FROZEN_RELATIVE
    bundle = {
        "artifacts": [
            dict(destination=str(frozen), source=binding),
            dict(destination=str(target), source=binding),
        ]
    }
    seen = []

    def fail(_):
        seen.append(frozen.is_file() and target.is_file())
        raise ValueError("synthetic validation failure")

    with pytest.raises(ValueError):
        op.publish_bundle(bundle, validator=fail)
    assert seen == [True] and not frozen.exists() and not target.exists()
    assert preexisting.read_text() == "untouched" and source.exists()


def test_unsigned_cost_source_is_not_a_complete_typed_admission():
    spec = d9.read_metadata(d9.ref(REPO / "docs/tasks/R1-D9-inputs-v4.json"))
    fields = op.fields_for("cost-admit", spec)
    with pytest.raises(ValueError, match="reviewed"):
        op.check_fields("cost-admit", fields, spec)
    fields.update(full_endpoint_cost_basis_reviewed=True, shared_process_hours=400)
    with pytest.raises((TypeError, ValueError)):
        op.check_fields("cost-admit", fields, spec)
    assert len(fields["cells"]) == 27


def test_recorded_mode_and_pair_unit_review_are_required():
    spec = d9.read_metadata(d9.ref(REPO / "docs/tasks/R1-D9-inputs-v6.json"))
    fields = op.fields_for("protocol-admit", spec)
    assert fields["near_allocation"] == "family_coordinated"
    with pytest.raises(ValueError, match="multiple-disjoint"):
        op.protocol_allocation_decision(fields)
    fields.update(
        extension_admitted=False,
        near_family_reviewed=True,
        zsre_empty_baseline_reviewed=True,
        queue_ceiling_and_failure_policy_reviewed=True,
        family_pair_unit_policy_reviewed=True,
    )
    op.check_fields("protocol-admit", fields, spec)
    fields["near_allocation"] = "independent"
    with pytest.raises(ValueError, match="bound operator"):
        op.check_fields("protocol-admit", fields, spec)
