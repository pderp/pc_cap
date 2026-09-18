"""Stepwise Stage-4 operator. Dry by default; only exact signed requests execute.

A signature is a local lead attestation, not a cryptographic identity service.
No command manufactures a signature or changes an existing receipt or candidate.
"""

from __future__ import annotations

import argparse
import copy
import fcntl
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts import r1_58c_draw_seal_preflight as preflight
from scripts import r1_77_queue as queue
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify as verify_candidate
from scripts.r1_d9f_allocation import CONTRACT, admitted_mode
from scripts.r1_d10a_review import ROOT

STEPS = (
    "protocol-admit",
    "cost-admit",
    "clearance",
    "rng-admit",
    "draw",
    "endpoints",
    "seal",
    "freeze",
    "launch",
)
COST = ROOT / "docs/tasks/R1-cost-admission-receipt-v1.json"


def new_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return d9.ref(path)


def journal_read(path):
    rows, previous = [], None
    if path.exists():
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row.get("previous") != previous or row.get("sha256") != d9.core.content_digest(
                {k: v for k, v in row.items() if k != "sha256"}
            ):
                raise ValueError(
                    "operator receipt log changed or torn; reconcile before continuing"
                )
            previous = row["sha256"]
            rows.append(row)
    return rows


def journal_append(path, rows, value):
    row = dict(
        value,
        previous=rows[-1]["sha256"] if rows else None,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    row["sha256"] = d9.core.content_digest(row)
    with path.open("a") as f:
        f.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return row


def fields_for(step, spec):
    if step == "protocol-admit":
        return dict(
            extension_admitted=None,
            near_family_reviewed=False,
            zsre_empty_baseline_reviewed=False,
            queue_ceiling_and_failure_policy_reviewed=False,
            near_allocation=spec.get("near_allocation", "independent"),
            near_allocation_decision=spec.get("near_allocation_decision"),
            family_pair_unit_policy_reviewed=False,
        )
    if step == "cost-admit":
        ceilings = d9.read_metadata(d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json"))
        return dict(
            shared_process_hours=None,
            full_endpoint_cost_basis_reviewed=False,
            cells=[
                dict(
                    condition=k.split(":")[0],
                    dataset=k.split(":")[1],
                    wall_seconds=v["ceiling_seconds"],
                    peak_host_mib=None,
                    peak_device_mib=None,
                    measurement=None,
                )
                for k, v in ceilings["cells"].items()
            ],
        )
    if step == "rng-admit":
        return dict(
            master_seed=None,
            near_allocation=spec.get("near_allocation", "independent"),
            near_allocation_decision=spec.get("near_allocation_decision"),
        )
    if step in ("clearance", "draw"):
        return dict(cumulative_exposure_current=False)
    if step == "endpoints":
        return dict(missingness_reviewed=False)
    if step == "seal":
        return dict(endpoint_inventory_reviewed=False)
    if step == "freeze":
        return dict(publication_bundle=None, september20_admission=None, closed_gate_receipts=None)
    return dict(
        matrix=None, bindings=None, receipt_root=str(ROOT / "logs/R1/final_queue"), workers=2
    )


def common(spec):
    return {
        k: copy.deepcopy(spec[k])
        for k in (
            "register",
            "matrix",
            "protocol",
            "dataset_layouts",
            "layout_sha256",
            "near_miss_family_contract",
        )
    } | {"contract_version": 2}


def cost_source():
    value = d9.read_metadata(d9.ref(COST))
    for b in value["bindings"].values():
        if d9.ref(ROOT / b["path"])["sha256"] != b["sha256"]:
            raise ValueError("cost admission v1 source changed")
    return value


def protocol_allocation_decision(fields):
    """Validate a recorded decision plus unsigned details before this step's signature."""
    if fields.get("near_allocation", "independent") != "family_coordinated":
        return None
    decision = d9.read_metadata(fields["near_allocation_decision"])
    if decision.get("status") == "draft":
        source = decision["decision_source"]
        if d9.ref(source["path"]) != source:
            raise ValueError("recorded DEC-062 source changed")
        row = decision["decision_row"]
        if (
            not row.startswith("| DEC-062 |")
            or row not in Path(source["path"]).read_text().splitlines()
            or "**Q16: option B** (lead)" not in row
            or "near_allocation = family_coordinated" not in row
            or decision.get("lead_approved") is not False
        ):
            raise ValueError("explicit recorded DEC-062 option B required")
        if fields.get("family_pair_unit_policy_reviewed") is not True:
            raise ValueError(
                "review multiple-disjoint-pairs-per-family contract before protocol signature"
            )
        # Schema preview only. No receipt is signed until validate_signature succeeds.
        decision = {**decision, "status": "closed", "lead_approved": True}
    return decision


def check_fields(step, fields, spec):
    if step == "protocol-admit":
        if type(fields.get("extension_admitted")) is not bool or any(
            fields.get(k) is not True
            for k in (
                "near_family_reviewed",
                "zsre_empty_baseline_reviewed",
                "queue_ceiling_and_failure_policy_reviewed",
            )
        ):
            raise ValueError("explicit extension choice and all three protocol reviews required")
        mode = fields.get("near_allocation", "independent")
        if mode != spec.get("near_allocation", "independent"):
            raise ValueError("allocation mode differs from bound operator inputs")
        decision = protocol_allocation_decision(fields)
        admitted_mode(
            dict(near_allocation=mode, near_allocation_contract=CONTRACT),
            dict(near_allocation=mode),
            decision,
        )
    elif step == "cost-admit":
        cost_source()
        if fields.get("full_endpoint_cost_basis_reviewed") is not True:
            raise ValueError(
                "full endpoint/process cost basis must be reviewed; padding is not a measurement"
            )
        hours = fields.get("shared_process_hours")
        if (
            isinstance(hours, bool)
            or not isinstance(hours, (int, float))
            or not math.isfinite(hours)
            or hours <= 0
        ):
            raise ValueError("positive explicitly signed shared process-hour budget required")
        cells = fields.get("cells", [])
        expected = d9.read_metadata(d9.ref(ROOT / "manifests/revision_v1/cell_ceilings_v1.json"))[
            "cells"
        ]
        keys = [c["condition"] + ":" + c["dataset"] for c in cells]
        if len(keys) != len(set(keys)) or set(keys) != set(expected):
            raise ValueError("all27 unique condition/dataset cost ceilings required")
        for c, k in zip(cells, keys, strict=True):
            if c["wall_seconds"] != expected[k]["ceiling_seconds"]:
                raise ValueError("changed ceiling requires a versioned cost admission")
            d9.read_metadata(c["measurement"])
        preflight.check_receipt(
            "chain_i_cell_ceilings",
            {
                **common(spec),
                **fields,
                "lead_approved": True,
                "status": "closed",
                "failures_included": True,
            },
            spec,
        )
    elif step == "rng-admit":
        if type(fields.get("master_seed")) is not int or fields["master_seed"] < 0:
            raise ValueError("lead's nonnegative integer master seed required")
        if fields.get("near_allocation", "independent") != spec.get(
            "near_allocation", "independent"
        ):
            raise ValueError("allocation mode differs from signed protocol")
        decision = (
            d9.read_metadata(fields["near_allocation_decision"])
            if fields.get("near_allocation") == "family_coordinated"
            else None
        )
        admitted_mode({**fields, "near_allocation_contract": CONTRACT}, fields, decision)
    elif step in ("clearance", "draw"):
        if fields.get("cumulative_exposure_current") is not True:
            raise ValueError("current exposure attestation required")
    elif step == "endpoints" and fields.get("missingness_reviewed") is not True:
        raise ValueError("dry endpoint identities and missingness require review")
    elif step == "seal" and fields.get("endpoint_inventory_reviewed") is not True:
        raise ValueError("exact endpoint inventory requires review")


def validate_signature(form, request):
    expected = d9.core.content_digest(request)
    signature = form.get("lead_signature", {})
    if (
        form.get("step") != request["step"]
        or form.get("request_sha256") != expected
        or form.get("lead_approved") is not True
    ):
        raise PermissionError("signed form must approve this exact current step request digest")
    if not isinstance(signature.get("name"), str) or not signature["name"].strip():
        raise PermissionError("named lead signature required")
    datetime.fromisoformat(signature["date"])
    return expected


def publication_preview(binding, spec=None):
    bundle = d9.read_metadata(binding)
    seen = set()
    freeze = ROOT / backend.FROZEN_RELATIVE
    for artifact in bundle["artifacts"]:
        destination = Path(artifact["destination"]).resolve()
        if (
            destination in seen
            or destination.exists()
            or not any(
                destination.is_relative_to(ROOT / p)
                for p in ("docs/tasks", "manifests/revision_v1")
            )
        ):
            raise ValueError(
                "publication needs unique new metadata paths under docs/tasks or manifests/revision_v1"
            )
        seen.add(destination)
        d9.read_metadata(artifact["source"])
    if freeze not in seen:
        raise ValueError("final frozen_stage4 manifest must be in reviewed publication bundle")
    if not bundle.get("matrix") or not bundle.get("bindings"):
        raise ValueError("final matrix and queue bindings required in publication bundle")
    if spec is not None:
        documents = {
            str(Path(a["destination"]).resolve()): d9.read_metadata(a["source"])
            for a in bundle["artifacts"]
        }
        frozen = documents[str(freeze)]
        for key, receipt in (
            ("protocol_admission", "protocol_admission"),
            ("seal_receipt", "seal_receipt"),
            ("cost_admission", "chain_i_cell_ceilings"),
        ):
            if frozen.get(key) != spec["receipts"][receipt]:
                raise ValueError("publication freeze must bind current " + key)
        seal = d9.read_metadata(spec["receipts"]["seal_receipt"])
        if (
            frozen.get("reservations") != seal["reservations"]
            or frozen.get("population") != seal["analysis_population"]
        ):
            raise ValueError("publication population differs from signed seal")
        gates = d9.read_metadata(spec["receipts"]["closed_gate_receipts"])
        if frozen.get("closed_gates") != gates["gates"]:
            raise ValueError("publication gate inventory differs")
        matrix_path = str(Path(bundle["matrix"]["path"]).resolve())
        matrix = documents.get(matrix_path)
        if matrix is None:
            raise ValueError("final matrix must be part of publication")
        source_binding = next(
            a["source"]
            for a in bundle["artifacts"]
            if str(Path(a["destination"]).resolve()) == matrix_path
        )
        if source_binding["sha256"] != bundle["matrix"]["sha256"]:
            raise ValueError("publication matrix hash differs")
        declaration = d9.read_metadata(spec["matrix"])
        protocol = d9.read_metadata(spec["receipts"]["protocol_admission"])
        required = d9.matrix_cells({"document": declaration, "binding": spec["matrix"]}, protocol)
        expected = {tuple(c[k] for k in d9.COORDS) for c in required}
        final_cells = queue.analysis.all_cells(matrix)
        if (
            len(final_cells) != len(expected)
            or {tuple(c[k] for k in d9.COORDS) for c in final_cells} != expected
        ):
            raise ValueError("final matrix must preserve full admitted coordinate inventory")
    return bundle


def publish_bundle(bundle, *, validator=None):
    """Create only approved new files; publish freeze last; remove this attempt on failure."""
    made = []
    frozen = ROOT / backend.FROZEN_RELATIVE
    try:
        artifacts = sorted(
            bundle["artifacts"], key=lambda a: Path(a["destination"]).resolve() == frozen
        )
        for a in artifacts:
            source = d9.read_metadata(a["source"])
            destination = Path(a["destination"]).resolve()
            # Byte-exact copies preserve precomputed recipe/matrix/publication hashes.
            raw = Path(a["source"]["path"]).read_bytes()
            if d9.sha(a["source"]["path"]) != a["source"]["sha256"] or not isinstance(source, dict):
                raise ValueError("publication source changed")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with destination.open("xb") as f:
                made.append(destination)
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
        if validator:
            validator(bundle)
        else:
            queue.verify_sealed_matrix(
                d9.read_metadata(bundle["matrix"]), d9.read_metadata(bundle["bindings"])
            )
        return dict(freeze=d9.ref(frozen), matrix=bundle["matrix"], bindings=bundle["bindings"])
    except BaseException:
        for p in reversed(made):
            p.unlink()  # only files exclusively created in this transaction
        raise


def run(step, *, inputs, candidate, session, form=None, execute=False, form_output=None):
    session = Path(session).resolve()
    if not session.is_relative_to(ROOT / "logs"):
        raise ValueError("operator session/log must be under repo logs")
    session.mkdir(parents=True, exist_ok=True)
    with (session / "operator.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        journal = session / "receipts.jsonl"
        history = journal_read(journal)
        successful = [r for r in history if r.get("status") == "complete"]
        if [r["step"] for r in successful] != list(STEPS[: len(successful)]):
            raise ValueError("operator step history is not a valid prefix")
        expected_step = STEPS[len(successful)] if len(successful) < len(STEPS) else None
        state_binding = successful[-1]["inputs"] if successful else d9.ref(inputs)
        spec = d9.read_metadata(state_binding)
        candidate_binding = d9.ref(candidate)
        fields = copy.deepcopy(form.get("fields", {})) if form else fields_for(step, spec)
        number = STEPS.index(step) + 1
        outputs = ROOT / "docs/tasks" / ("R1-58g-" + session.name)
        receipt_path = outputs / f"{number:02d}-{step}.receipt.json"
        next_path = outputs / f"{number:02d}-inputs.json"
        request = dict(
            version=1,
            step=step,
            inputs=state_binding,
            candidate=candidate_binding,
            cost_admission_source=d9.ref(COST),
            fields=fields,
            receipt_output=str(receipt_path),
            next_inputs=str(next_path),
            producer=d9.ref(__file__),
            implementation=d9.implementation_bindings(),
        )
        blocked = []
        dry = {}
        plan = copy.deepcopy(spec)
        try:
            if step != expected_step:
                raise ValueError(f"next unsigned step is {expected_step}; no downstream advance")
            verify_candidate(d9.read_metadata(candidate_binding))
            if step in ("clearance", "draw", "seal"):
                dry, _ = d9.prepare(spec, step)
                request["producer_request_sha256"] = dry.get("request_sha256")
                # Own unsigned authorization is expected at preview; other blockers remain visible.
                dry["authorization_to_supply"] = step + "_authorization"
            elif step == "endpoints":
                construction = d9.read_metadata(
                    d9.ref(ROOT / "docs/tasks/R1-D10c-construction-inputs-template-v4.json")
                )
                protocol = d9.read_metadata(spec["receipts"]["protocol_admission"])
                construction.update(
                    draw_receipt=spec["receipts"]["draw_receipt"],
                    matrix=spec["matrix"],
                    role_plan=spec["d9"]["clearance"]["role_plan"],
                    catalog=spec["d9"]["draw"]["composition_catalog"],
                    extension_admitted=protocol["extension_admitted"],
                    output=str(
                        ROOT.parent
                        / "assets/runs/pc_cap/R1"
                        / ("operator-" + session.name)
                        / "endpoints"
                    ),
                    report=str(session / "endpoints-written.json"),
                )
                construction_path = outputs / "endpoints-request.json"
                if not construction_path.exists():
                    new_json(construction_path, construction)
                elif d9.read_metadata(d9.ref(construction_path)) != construction:
                    raise ValueError("endpoint request changed; new reviewed session required")
                command = [
                    sys.executable,
                    "-m",
                    "scripts.r1_d10c_endpoints",
                    "construct",
                    "--spec",
                    str(construction_path),
                ]
                result = subprocess.run(
                    command + ["--dry-run"], cwd=ROOT, capture_output=True, text=True, check=True
                )
                dry = json.loads(result.stdout)
                request.update(
                    construction=d9.ref(construction_path),
                    endpoint_identities_sha256=d9.core.content_digest(dry["identities"]),
                )
            elif step == "freeze":
                plan["freeze_candidate"] = candidate_binding
                for k in ("september20_admission", "closed_gate_receipts"):
                    plan["receipts"][k] = fields[k]
                    preflight.check_receipt(k, d9.read_metadata(fields[k]), plan)
                bundle = publication_preview(fields["publication_bundle"], plan)
                request["publication_bundle"] = fields["publication_bundle"]
                dry = preflight.preflight(plan, "freeze")
            elif step == "launch":
                matrix = d9.read_metadata(fields["matrix"])
                bindings = d9.read_metadata(fields["bindings"])
                queue.verify_sealed_matrix(matrix, bindings)
                if fields["workers"] != 2:
                    raise ValueError("this operator contract admits two workers")
                dry = queue.inventory(
                    matrix,
                    receipt_root=fields["receipt_root"],
                    matrix_hash=fields["matrix"]["sha256"],
                    workers=2,
                    ceiling_hours=spec["shared_process_hours"],
                )
                if dry["cost"]["unknown_attempts"]:
                    raise ValueError("unknown process costs require reconciliation")
            check_fields(step, fields, spec)
        except (
            OSError,
            KeyError,
            TypeError,
            ValueError,
            PermissionError,
            subprocess.CalledProcessError,
        ) as error:
            blocked.append(str(error))
        digest = d9.core.content_digest(request)
        report = dict(
            step=step,
            request_sha256=digest,
            request=request,
            blocked=blocked,
            dry_run=dry,
            lead_sets=dict(
                step=step,
                request_sha256=digest,
                lead_approved=False,
                lead_signature=dict(name=None, date=None),
                fields=fields,
            ),
            execute=False,
        )
        if form_output:
            target = Path(form_output).resolve()
            if not target.is_relative_to(ROOT / "docs/tasks"):
                raise ValueError("unsigned forms belong under docs/tasks")
            new_json(target, report["lead_sets"])
        if not execute:
            journal_append(
                journal,
                history,
                dict(status="dry_run", step=step, request_sha256=digest, blocked=blocked),
            )
            return report
        try:
            if blocked:
                raise PermissionError("; ".join(blocked))
            validate_signature(form or {}, request)
            if receipt_path.exists() or next_path.exists():
                raise FileExistsError(
                    "step output exists; reconcile partial publication, never overwrite"
                )
            signed = {
                **common(spec),
                **fields,
                "status": "closed",
                "lead_approved": True,
                "lead_signature": form["lead_signature"],
                "operator_request_sha256": digest,
            }
            if step in ("protocol-admit", "rng-admit"):
                key = "protocol_admission" if step == "protocol-admit" else "rng_admission"
                if step == "protocol-admit" and fields["near_allocation"] == "family_coordinated":
                    decision = protocol_allocation_decision(fields)
                    decision.update(
                        lead_signature=form["lead_signature"],
                        operator_request_sha256=digest,
                    )
                    signed["near_allocation_decision"] = new_json(
                        outputs / "01-allocation-contract.receipt.json", decision
                    )
                receipt = d9.read_metadata(spec["receipts"][key]) | signed
                if step == "protocol-admit":
                    plan.update(
                        near_allocation=fields["near_allocation"],
                        near_allocation_decision=signed.get("near_allocation_decision"),
                    )
                else:
                    receipt["near_allocation_contract"] = CONTRACT
                    plan["d9"]["draw"].update(
                        master_seed=fields["master_seed"], near_allocation=fields["near_allocation"]
                    )
                plan["receipts"][key] = new_json(receipt_path, receipt)
            elif step == "cost-admit":
                signed.update(failures_included=True, cost_admission_source=d9.ref(COST))
                plan["receipts"]["chain_i_cell_ceilings"] = new_json(receipt_path, signed)
                plan["shared_process_hours"] = fields["shared_process_hours"]
            elif step in ("clearance", "draw", "seal"):
                signed.update(operation=step, request_sha256=d9.contract(plan, step))
                plan["receipts"][step + "_authorization"] = new_json(receipt_path, signed)
                before, _ = d9.prepare(plan, step)
                if before["blocked"]:
                    raise PermissionError(str(before["blocked"]))
                emitted = d9.execute(plan, step)
                plan["receipts"][d9.RECEIPT_NAMES[step]] = emitted["receipt"]
            elif step == "endpoints":
                subprocess.run(
                    command + ["--write"], cwd=ROOT, check=True, capture_output=True, text=True
                )
                output = d9.read_metadata(d9.ref(construction["report"]))
                if (
                    d9.core.content_digest(output["identities"])
                    != request["endpoint_identities_sha256"]
                ):
                    raise ValueError("endpoint write differs from approved dry result")
                draw = d9.read_metadata(spec["receipts"]["draw_receipt"])
                signed.update(
                    draw_receipt=spec["receipts"]["draw_receipt"],
                    reservations=draw["reservations"],
                    bundle=output["bundle"],
                    independent_population=output["independent_population"],
                    datasets=list(d9.core.DATASETS),
                    all_roles_disjoint=True,
                    composition_dependencies_closed=True,
                )
                plan["receipts"]["endpoint_construction"] = new_json(receipt_path, signed)
                plan["d9"]["seal"].update(
                    bundle=output["bundle"], independent_population=output["independent_population"]
                )
            elif step == "freeze":
                signed.update(operation="freeze", request_sha256=digest)
                plan["receipts"]["freeze_authorization"] = new_json(receipt_path, signed)
                checked = preflight.preflight(plan, "freeze")
                if checked["blocked"]:
                    raise PermissionError(str(checked["blocked"]))
                plan["published_freeze"] = publish_bundle(bundle)
            else:
                # The orchestrator must already hold the live GPU lease; queue enforces it.
                result = queue.run_queue(
                    fields["matrix"]["path"],
                    fields["bindings"]["path"],
                    receipt_root=fields["receipt_root"],
                    workers=2,
                    ceiling_hours=spec["shared_process_hours"],
                )
                new_json(receipt_path, {**signed, "queue_result": result})
                if result["status"] != "selected_blocks_complete":
                    raise RuntimeError(
                        "queue stopped or incomplete; use its preserved receipt root for owner reconciliation"
                    )
            next_binding = new_json(next_path, plan)
            journal_append(
                journal,
                journal_read(journal),
                dict(
                    status="complete",
                    step=step,
                    request_sha256=digest,
                    inputs=next_binding,
                    receipt=d9.ref(receipt_path),
                ),
            )
            return dict(
                step=step, status="complete", inputs=next_binding, receipt=d9.ref(receipt_path)
            )
        except BaseException as error:
            journal_append(
                journal,
                journal_read(journal),
                dict(
                    status="failed",
                    step=step,
                    request_sha256=digest,
                    error=repr(error),
                    downstream_signed=False,
                ),
            )
            raise


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("step", choices=STEPS)
    p.add_argument("--inputs", type=Path, default=ROOT / "docs/tasks/R1-D9-inputs-v6.json")
    p.add_argument(
        "--candidate", type=Path, default=ROOT / "manifests/revision_v1/freeze_candidate_v11.json"
    )
    p.add_argument("--session", type=Path, default=ROOT / "logs/R1/operator_v5")
    p.add_argument("--form", type=Path)
    p.add_argument("--write-form", type=Path)
    p.add_argument("--execute", action="store_true")
    a = p.parse_args(argv)
    form = json.loads(a.form.read_text()) if a.form else None
    result = run(
        a.step,
        inputs=a.inputs,
        candidate=a.candidate,
        session=a.session,
        form=form,
        execute=a.execute,
        form_output=a.write_form,
    )
    print(json.dumps(result, indent=2, allow_nan=False))
    return 2 if result.get("blocked") else 0


if __name__ == "__main__":
    raise SystemExit(main())
