"""Derive prepublication gate evidence from seven exact signed operator requests.

Read-only with respect to the operator session. Outputs inherit existing approvals;
they are not new signatures, a freeze, a launch clearance, or experimental results.
No sealed payload is opened; candidate verification hashes its bound sources.
Publication still needs operator step 8 approval.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from scripts import r1_58c_draw_seal_preflight as preflight
from scripts import r1_58g_operator as op
from scripts import r1_63j_production_bundle as assembly
from scripts import r1_d9_receipts as d9

ROOT = op.ROOT
STEP_KEYS = dict(zip(op.STEPS[:7], (
    "protocol_admission", "chain_i_cell_ceilings", "clearance_authorization",
    "rng_admission", "draw_authorization", "endpoint_construction", "seal_authorization",
), strict=True))
# Each row is a closure of pre-execution admissibility, not of future measurement.
GATES = {
    "U01": (("protocol-admit",), "Candidate-bound D.4/D.5 comparisons, DEC-064 and optional extension; D.5 additionally binds DEC-068/069 and the approved locality selection."),
    "U02": (("protocol-admit", "clearance", "seal"), "Primary v5/reference identities and sealed populations; retain zsRE empty-baseline disclosure."),
    "U03": (("protocol-admit", "clearance", "cost-admit"), "DEC-047 historical S1 certification and calibration; NOT exact-v5-compute-matched controls or exclusion of all continued-base explanations."),
    "U04": (("clearance", "draw"), "zsRE teacher/role clearance and current exposure through the actual draw."),
    "U05": (("protocol-admit", "clearance", "draw"), "CounterFact DEC-042 exception; no strict-source fresh-remainder claim."),
    "U06": (("protocol-admit", "clearance", "rng-admit", "draw"), "Exact current clearance, RNG and draw, role capacity and disjoint reservations."),
    "U07": (("draw", "endpoints", "seal"), "Actual authorized draw, deterministic endpoint identities and independent sealed populations."),
    "U08": (("protocol-admit", "endpoints", "seal", "cost-admit"), "DEC-063 sampled cadence and final full 245,237-position assays against both references; independent endpoint populations."),
    "U09": (("protocol-admit", "rng-admit", "endpoints", "seal"), "DEC-061/062 family coordination, multiple disjoint pairs per family; reviewed missing slots remain missing."),
    "U10": (("protocol-admit", "endpoints"), "DEC-053 bounded-text scoring and termination/truncation diagnostics in the candidate-bound implementation."),
    "U11": (("protocol-admit", "clearance", "endpoints", "seal"), "Candidate-bound implementation and rebuilt runtime identities; production bundle still must pass whole-matrix backend validation before publication."),
    "U12": (("protocol-admit", "endpoints", "seal"), "Registered 63-interval family unchanged; 21 MQuAKE-1000 intervals unavailable, 75 omitted cells not imputed. D.5: preliminary summaries, all realization/order dispersions and secondary pointwise t sensitivity; no demonstrated familywise coverage."),
    "U13": (("protocol-admit", "seal"), "DEC-064 cap benchmarks are labels, not admission vetoes; DEC-047 continuation admission remains separate."),
    "U14": (("protocol-admit", "endpoints", "seal", "cost-admit"), "DEC-059 zsRE/CounterFact secondary rule; MQuAKE actual-300 descriptive only, no transferred thresholds."),
    "U15": (("protocol-admit", "endpoints", "seal"), "Independent expected populations and missingness policy admitted; future results and incomplete cells remain to be measured and reported."),
    "U16": (("protocol-admit", "cost-admit"), "Typed revision-4 signed costs, reviewed transfers, failure charging, single concurrency factor and host guard; estimates are not new measurements."),
    "U17": (op.STEPS[:7], "Prepublication dependencies bound; this derived receipt does not publish a freeze or authorize launch. Step 8 must validate and approve the exact bundle."),
    "U18": (("protocol-admit", "cost-admit"), "Candidate-bound execution plan, D.4/D.5 scope, 750 process-hour cap and October 9 stop; forecasts are conditional."),
}


class Snapshot:
    def __init__(self):
        self.bindings = {}

    def read(self, binding, *, parse=True):
        value = d9.read_metadata(binding, parse=parse)
        self.bindings[binding["path"]] = binding["sha256"]
        return value

    def verify(self):
        for path, expected in self.bindings.items():
            if d9.sha(path) != expected:
                raise ValueError("assembly input changed during read: " + path)


def request_for(step, previous_binding, spec, signed, candidate, session, snap):
    """Reconstruct only fields in the installed operator contract, never run it."""
    fields = {k: copy.deepcopy(signed[k]) for k in op.fields_for(step, spec)}
    if step == "protocol-admit":
        # Operator replaces this template with a signed allocation-contract receipt.
        fields["near_allocation_decision"] = spec.get("near_allocation_decision")
    op.check_fields(step, fields, spec)
    outputs = op.ROOT / "docs/tasks" / ("R1-58g-" + session.name)
    number = op.STEPS.index(step) + 1
    request = dict(version=1, step=step, inputs=previous_binding, candidate=candidate,
                   cost_admission_source=op.cost_binding(spec), fields=fields,
                   receipt_output=str(outputs / f"{number:02d}-{step}.receipt.json"),
                   next_inputs=str(outputs / f"{number:02d}-inputs.json"),
                   producer=d9.ref(op.__file__), implementation=d9.implementation_bindings())
    if step in d9.RECEIPT_NAMES:
        request["producer_request_sha256"] = d9.contract(spec, step)
    elif step == "endpoints":
        binding = d9.ref(outputs / "endpoints-request.json")
        construction = snap.read(binding)
        expected = snap.read(spec["construction_inputs"])
        protocol = snap.read(spec["receipts"]["protocol_admission"])
        expected.update(draw_receipt=spec["receipts"]["draw_receipt"], matrix=spec["matrix"],
                        role_plan=spec["d9"]["clearance"]["role_plan"],
                        catalog=spec["d9"]["draw"]["composition_catalog"],
                        extension_admitted=protocol["extension_admitted"],
                        output=str(op.ROOT.parent / "assets/runs/pc_cap/R1" /
                                   ("operator-" + session.name) / "endpoints"),
                        report=str(session / "endpoints-written.json"))
        if construction != expected:
            raise ValueError("endpoint construction differs from signed input chain")
        result = snap.read(d9.ref(session / "endpoints-written.json"))
        request.update(construction=binding,
                       endpoint_identities_sha256=d9.core.content_digest(result["identities"]))
        if any(signed[k] != result[k] for k in ("bundle", "independent_population")):
            raise ValueError("endpoint output differs from signed receipt")
    return request


def transition(step, before, after, signed, receipt_binding, request, snap):
    expected = copy.deepcopy(before)
    key = STEP_KEYS[step]
    expected["receipts"][key] = receipt_binding
    preflight.check_receipt(key, signed, before)
    if step == "protocol-admit":
        expected.update(near_allocation=signed["near_allocation"],
                        near_allocation_decision=signed.get("near_allocation_decision"))
        if signed["near_allocation"] == "family_coordinated":
            decision = snap.read(signed["near_allocation_decision"])
            original = op.protocol_allocation_decision(request["fields"])
            original.update(lead_signature=signed["lead_signature"],
                            operator_request_sha256=signed["operator_request_sha256"])
            if decision != original:
                raise ValueError("allocation decision not inherited from protocol signature")
    elif step == "cost-admit":
        if signed.get("cost_admission_source") != op.cost_binding(before):
            raise ValueError("cost source differs")
        expected["shared_process_hours"] = signed["shared_process_hours"]
    elif step == "rng-admit":
        expected["d9"]["draw"].update(master_seed=signed["master_seed"],
                                    near_allocation=signed["near_allocation"])
    elif step in d9.RECEIPT_NAMES:
        producer_digest = request["producer_request_sha256"]
        if signed.get("operation") != step or signed.get("request_sha256") != producer_digest:
            raise ValueError("producer authorization differs from exact signed request")
        produced_key = d9.RECEIPT_NAMES[step]
        binding = after["receipts"][produced_key]
        produced = snap.read(binding)
        preflight.check_receipt(produced_key, produced, before)
        if (produced.get("authorization") != receipt_binding
                or produced.get("request_sha256") != producer_digest
                or produced.get("producer") != d9.ref(d9.__file__)
                or produced.get("core") != d9.ref(ROOT / "scripts/r1_d9_receipt_core.py")
                or binding["path"] != before["d9"][step]["receipt_output"]):
            raise ValueError("produced receipt is not linked to signed authorization")
        if step == "draw" and (
            produced.get("clearance_receipt") != before["receipts"]["joint_clearance"]
            or produced.get("master_seed") != before["d9"]["draw"]["master_seed"]
        ):
            raise ValueError("draw differs from current clearance/RNG")
        expected["receipts"][produced_key] = binding
    elif step == "endpoints":
        expected["d9"]["seal"].update(bundle=signed["bundle"],
                                    independent_population=signed["independent_population"])
    if after != expected:
        raise ValueError("unexpected operator input transition at " + step)


def verify_session(inputs, candidate, session):
    session = Path(session).resolve()
    if not session.is_relative_to(ROOT / "logs"):
        raise ValueError("operator session must be under repo logs")
    journal = session / "receipts.jsonl"
    raw = journal.read_bytes()
    if not raw or not raw.endswith(b"\n"):
        raise ValueError("missing or torn operator journal")
    history = op.journal_read(journal)
    successful = [r for r in history if r.get("status") == "complete"]
    if [r["step"] for r in successful] != list(op.STEPS[:7]):
        raise ValueError("exactly seven completed signed steps required, before freeze")
    tail = history[history.index(successful[-1]) + 1:]
    if any(r.get("status") != "dry_run" for r in tail):
        raise ValueError("unreconciled operator failure after step 7")
    snap = Snapshot()
    initial, candidate_binding = d9.ref(inputs), d9.ref(candidate)
    spec, cand = snap.read(initial), snap.read(candidate_binding)
    if cand["d9_inputs"] != initial or cand["schema_version"] not in (14, 15):
        raise ValueError("candidate v14/v15 must bind exact initial inputs")
    op.verify_candidate(cand)
    snap.bindings.update(cand["bindings_sha256"])
    if any(spec[k] != cand[k] for k in ("matrix", "protocol", "register")):
        raise ValueError("candidate/input identities differ")
    config = spec["d9"]["clearance"]["configuration_bindings"]
    if config["execution_plan"] != cand["execution_plan"]:
        raise ValueError("execution plan is not bound by signed clearance configuration")
    snap.read(cand["execution_plan"], parse=False)
    snap.read(spec["protocol"], parse=False)
    previous, approvals = initial, {}
    for row in successful:
        step = row["step"]
        signed, after = snap.read(row["receipt"]), snap.read(row["inputs"])
        request = request_for(step, previous, spec, signed, candidate_binding, session, snap)
        digest = d9.core.content_digest(request)
        if (row["request_sha256"] != digest
                or signed.get("operator_request_sha256") != digest
                or row["receipt"]["path"] != request["receipt_output"]
                or row["inputs"]["path"] != request["next_inputs"]):
            raise ValueError("exact operator request/state digest mismatch at " + step)
        op.validate_signature(dict(step=step, request_sha256=digest,
                                   lead_approved=signed.get("lead_approved"),
                                   lead_signature=signed.get("lead_signature", {})), request)
        if not any(r.get("status") == "dry_run" and r.get("step") == step
                   and r.get("request_sha256") == digest and r.get("blocked") == []
                   for r in history[:history.index(row)]):
            raise ValueError("missing unblocked exact-request preview at " + step)
        transition(step, spec, after, signed, row["receipt"], request, snap)
        approvals[step] = dict(receipt=row["receipt"], request_sha256=digest,
                               lead_signature=signed["lead_signature"])
        previous, spec = row["inputs"], after
    for name in assembly.RECEIPTS:
        if name not in ("closed_gate_receipts", "september20_admission"):
            preflight.check_receipt(name, snap.read(spec["receipts"][name]), spec)
    cost = snap.read(spec["receipts"]["chain_i_cell_ceilings"])
    if (cost.get("cost_schema_version") != 2 or cost.get("receipt_revision") != 4 or cost.get("shared_process_hours") != 750
            or spec.get("shared_process_hours") != 750
            or spec["cost_admission_source_unsigned"]["path"] !=
            str(ROOT / f"docs/tasks/R1-cost-admission-receipt-v{5 if cand['schema_version'] == 15 else 4}.json")):
        raise ValueError("this mapping requires candidate-versioned typed revision-4 cost and the 750-hour admission")
    # Assembly's normal cross-receipt checks run after adding the derived wrappers.
    snap.verify()
    if journal.read_bytes() != raw:
        raise ValueError("operator journal changed during verification")
    return dict(spec=spec, latest_inputs=previous, candidate=candidate_binding,
                approvals=approvals, execution_plan=cand["execution_plan"],
                journal=dict(path=str(journal), sha256=hashlib.sha256(raw).hexdigest(),
                             rows=len(history)), snapshot=snap)


def gate_table(state):
    lines = ["| Gate | Inherited signed steps | Scope and qualification |",
             "|---|---|---|"]
    for gate, (steps, note) in GATES.items():
        lines.append(f"| {gate} | {', '.join(steps)} | {note} |")
    return "\n".join(lines) + "\n"


def emit(state, output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "docs/tasks") or output.exists():
        raise ValueError("new output directory under docs/tasks required")
    state["snapshot"].verify()
    if d9.sha(state["journal"]["path"]) != state["journal"]["sha256"]:
        raise ValueError("operator journal changed before emission")
    spec = copy.deepcopy(state["spec"])
    common = dict(op.common(spec), status="closed", lead_approved=True,
                  approval_basis="derived from verified exact signed requests; no new signature",
                  candidate=state["candidate"], operator_journal=state["journal"],
                  source_inputs=state["latest_inputs"], producer=d9.ref(__file__),
                  publication_authorized=False, launch_authorized=False)
    output.mkdir(parents=True, exist_ok=False)
    gates = {}
    for gate, (steps, note) in GATES.items():
        gates[gate] = op.new_json(output / f"{gate}.json", dict(common, gate=gate,
            scope="prepublication admission dependencies", qualification=note,
            inherited_approvals={s:state["approvals"][s] for s in steps},
            evidence_receipts=spec["receipts"]))
    spec["receipts"]["closed_gate_receipts"] = op.new_json(output / "closed-gates.json",
        dict(common, gates=gates, inherited_approvals=state["approvals"]))
    spec["receipts"]["september20_admission"] = op.new_json(output / "schedule-admission.json",
        dict(common, admission_date="2026-09-20", experimental_completion_date="2026-10-09",
             admission_date_semantics="legacy schema name for scheduled review milestone; actual signature dates are in inherited_approvals",
             full_scope_retained=True,
             scope_semantics="all candidate-bound core cells plus only the explicitly admitted extension",
             execution_plan=state["execution_plan"], shared_process_hours=750,
             signed_cost=spec["receipts"]["chain_i_cell_ceilings"],
             inherited_approvals={s:state["approvals"][s] for s in ("protocol-admit", "cost-admit", "clearance")}))
    spec["freeze_candidate"] = state["candidate"]
    checked = assembly.inspect(spec)
    if checked["blocked"]:
        raise ValueError("derived assembly preflight failed: " + str(checked["blocked"]))
    state["snapshot"].verify()
    if d9.sha(state["journal"]["path"]) != state["journal"]["sha256"]:
        raise ValueError("operator journal changed before assembly input publication")
    table = gate_table(state)
    with (output / "gate-table.md").open("x") as f:
        f.write("# Derived prepublication gate evidence\n\n" + table +
                "\nNo new signature, publication or launch authority. Step 8 reviews this exact bundle.\n")
    binding = op.new_json(output / "assembly-inputs.json", spec)
    return dict(task="R1-63n", inputs=binding, gates=18, payloads_opened=0,
                signed=False, frozen=False, launch_authorized=False,
                operator_journal=state["journal"], gate_table=table)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, default=ROOT / "docs/tasks/R1-D9-inputs-v11.json")
    p.add_argument("--candidate", type=Path, default=ROOT / "manifests/revision_v1/freeze_candidate_v15.json")
    p.add_argument("--session", type=Path, default=ROOT / "logs/R1/operator_v10")
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        report = emit(verify_session(a.inputs, a.candidate, a.session), a.output)
    except (OSError, KeyError, TypeError, ValueError, PermissionError) as error:
        print(json.dumps(dict(task="R1-63n", blocked=str(error), signed=False,
                              frozen=False, launch_authorized=False)))
        return 2
    print(report["gate_table"])
    print(json.dumps({k:v for k,v in report.items() if k != "gate_table"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
