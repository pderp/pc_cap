"""Exercise the actual seven-step operator; substitute only synthetic resource I/O."""

import copy
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
from scripts import r1_63n_assembly_inputs as build

op, d9 = build.op, build.d9
ROOT = build.ROOT


@pytest.fixture(scope="module")
def signed_session():
    root = ROOT / "logs/r1_round38" / ("operator-test-" + uuid4().hex)
    session = root / "logs/session"
    spec = json.loads((ROOT / "docs/tasks/R1-D9-inputs-v9.json").read_text())
    for stage in d9.RECEIPT_NAMES:
        spec["d9"][stage]["receipt_output"] = str(root / f"{stage}.json")
    inputs = root / "inputs.json"
    op.new_json(inputs, spec)
    op.new_json(root / "docs/tasks/R1-D10c-construction-inputs-template-v4.json", {})
    candidate = json.loads((ROOT / "manifests/revision_v1/freeze_candidate_v14.json").read_text())
    candidate["d9_inputs"] = d9.ref(inputs)
    cp = root / "candidate.json"
    op.new_json(cp, candidate)
    resource = dict(path="/synthetic/opaque/not-opened.json", sha256="a" * 64)
    endpoint = dict(identities={"synthetic-only": {"population": 3}},
                    bundle=resource, independent_population=resource)

    def prepare(s, stage):
        return dict(request_sha256=d9.contract(s, stage), blocked=[]), None

    def execute(s, stage):
        r = dict(op.common(s), status="closed", lead_approved=True,
                 producer=d9.ref(d9.__file__),
                 core=d9.ref(ROOT / "scripts/r1_d9_receipt_core.py"),
                 authorization=s["receipts"][stage + "_authorization"],
                 request_sha256=d9.contract(s, stage), synthetic=True)
        if stage == "clearance":
            r.update(policy="DEC-048-option-C;DEC-042-CounterFact;zsRE-priority",
                     cleared_subjects={k:v["demand_subjects"] for k,v in s["dataset_layouts"].items()},
                     **{k:True for k in ("alias_review_complete", "context_review_complete",
                         "teacher_token_review_complete", "role_compatibility_complete",
                         "cross_dataset_disjoint", "cumulative_exposure_current")})
        else:
            r.update(datasets=list(d9.core.DATASETS), all_roles_disjoint=True,
                     composition_dependencies_closed=True, reservations=resource)
            if stage == "draw":
                r["clearance_receipt"] = s["receipts"]["joint_clearance"]
                r["master_seed"] = s["d9"]["draw"]["master_seed"]
            else:
                r.update(draw_receipt=s["receipts"]["draw_receipt"],
                         analysis_population=resource, payload_inventory=resource)
        return dict(receipt=op.new_json(s["d9"][stage]["receipt_output"], r))

    def subprocess_run(command, **kwargs):
        assert command[2] == "scripts.r1_d10c_endpoints"
        if "--write" in command:
            op.new_json(session / "endpoints-written.json", endpoint)
        return SimpleNamespace(stdout=json.dumps(endpoint))

    with pytest.MonkeyPatch.context() as m:
        m.setattr(op, "ROOT", root)
        # Synthetic candidate changes output destinations. Real source verification
        # is covered separately; no fake candidate reaches a production command.
        m.setattr(op, "verify_candidate", lambda c: c == candidate or pytest.fail("candidate"))
        m.setattr(d9, "prepare", prepare)
        m.setattr(d9, "execute", execute)
        m.setattr(op.subprocess, "run", subprocess_run)
        args = dict(inputs=inputs, candidate=cp, session=session)
        for step in op.STEPS[:7]:
            preview = op.run(step, **args)
            form = preview["lead_sets"]
            for k, v in form["fields"].items():
                if type(v) is bool:
                    form["fields"][k] = k != "extension_admitted"
            if step == "protocol-admit":
                form["fields"]["extension_admitted"] = False
            if step == "rng-admit":
                form["fields"]["master_seed"] = 38
            preview = op.run(step, form=form, **args)
            assert not preview["blocked"], preview["blocked"]
            form = copy.deepcopy(preview["lead_sets"])
            form.update(lead_approved=True,
                        lead_signature=dict(name="SYNTHETIC TEST ONLY", date="2026-09-18"))
            op.run(step, form=form, execute=True, **args)
    return dict(root=root, session=session, inputs=inputs, candidate=cp)


def verified(f, monkeypatch):
    monkeypatch.setattr(op, "ROOT", f["root"])
    monkeypatch.setattr(op, "verify_candidate", lambda c: None)
    return build.verify_session(f["inputs"], f["candidate"], f["session"])


def test_signed_operator_chain_and_assembly_consumer(signed_session, monkeypatch):
    f = signed_session
    state = verified(f, monkeypatch)
    # Emission stays in the isolated fixture's docs tree.
    monkeypatch.setattr(build, "ROOT", f["root"])
    output = f["root"] / "docs/tasks/derived"
    result = build.emit(state, output)
    spec = d9.read_metadata(result["inputs"])
    assert not build.assembly.inspect(spec)["blocked"]
    assert result["gates"] == 18 and not result["signed"] and not result["frozen"]
    gates = d9.read_metadata(spec["receipts"]["closed_gate_receipts"])
    for gate, binding in gates["gates"].items():
        receipt = d9.read_metadata(binding)
        assert "lead_signature" not in receipt
        assert set(receipt["inherited_approvals"]) == set(build.GATES[gate][0])
        assert not receipt["publication_authorized"]
    schedule = d9.read_metadata(spec["receipts"]["september20_admission"])
    assert schedule["execution_plan"] == state["execution_plan"]
    assert schedule["experimental_completion_date"] == "2026-10-09"
    assert "NOT exact-v5-compute" in result["gate_table"]
    with pytest.raises(ValueError, match="new output"):
        build.emit(state, output)


@pytest.mark.parametrize("case", ["unsigned", "digest", "missing", "stale", "torn", "failed"])
def test_refuse_corruption_before_any_emission(signed_session, monkeypatch, case):
    f = signed_session
    state = verified(f, monkeypatch)
    original = op.journal_read
    def altered(path):
        rows = original(path)
        complete = [r for r in rows if r["status"] == "complete"]
        if case == "digest":
            complete[0]["request_sha256"] = "0" * 64
        elif case == "missing":
            rows.remove(complete[-1])
        elif case == "failed":
            rows.append(dict(status="failed", step="freeze"))
        return rows
    monkeypatch.setattr(op, "journal_read", altered)
    original_read = build.Snapshot.read
    target = state["approvals"]["protocol-admit"]["receipt"]
    def read(self, binding, **kwargs):
        r = original_read(self, binding, **kwargs)
        if binding == target:
            if case == "unsigned":
                r.pop("lead_signature")
            elif case == "stale":
                r["extension_admitted"] = True
        return r
    monkeypatch.setattr(build.Snapshot, "read", read)
    if case == "torn":
        raw_read = Path.read_bytes
        monkeypatch.setattr(Path, "read_bytes", lambda p: raw_read(p).rstrip(b"\n")
                            if p == f["session"] / "receipts.jsonl" else raw_read(p))
    with pytest.raises((ValueError, PermissionError, KeyError)):
        build.verify_session(f["inputs"], f["candidate"], f["session"])


def test_unsigned_actual_session_does_not_create_output(monkeypatch):
    def never_emit(*args, **kwargs):
        pytest.fail("live signing advanced during this read-only test; emission forbidden")

    monkeypatch.setattr(build, "emit", never_emit)
    rows = op.journal_read(ROOT / "logs/R1/operator_v8/receipts.jsonl")
    if any(r.get("status") == "complete" for r in rows):
        pytest.skip("real signing has started; no assumption about live progress")
    target = ROOT / "docs/tasks" / ("must-not-exist-" + uuid4().hex)
    assert build.main(["--output", str(target)]) == 2
    assert not target.exists()


def test_metadata_change_between_verification_and_emit(signed_session, monkeypatch):
    state = verified(signed_session, monkeypatch)
    oldsha = d9.sha
    monkeypatch.setattr(d9, "sha", lambda p: "0" * 64 if str(p) == state["latest_inputs"]["path"] else oldsha(p))
    with pytest.raises(ValueError, match="changed"):
        build.emit(state, ROOT / "docs/tasks" / uuid4().hex)
