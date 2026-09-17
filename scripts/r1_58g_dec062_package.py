"""Bind recorded DEC-062 B in unsigned forms; preserve preceding package evidence.

The exact pair-unit details still need the lead's protocol-form review. No
signature, seed, reservation, endpoint, seal or freeze is created here.
"""

from __future__ import annotations

import copy
import json

from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d9f_allocation import CONTRACT
from scripts.r1_d10a_review import ROOT, write_new


def build():
    log = ROOT / "logs/r1_round27"
    old_path = ROOT / "manifests/revision_v1/freeze_candidate_v10.json"
    candidate = copy.deepcopy(d9.read_metadata(d9.ref(old_path)))
    history = json.loads((log / "source_snapshot/dec062-migration.json").read_text())
    decision_source = ROOT / "docs/decisions.md"
    row = next(r for r in decision_source.read_text().splitlines() if r.startswith("| DEC-062 |"))
    if "**Q16: option B** (lead)" not in row:
        raise ValueError("accepted DEC-062 B required")
    snapshot = log / "source_snapshot/decisions-DEC062.md"
    with snapshot.open("xb") as f:
        f.write(decision_source.read_bytes())
    decision = write_new(
        ROOT / "docs/tasks/R1-D9f-allocation-contract-unsigned.json",
        dict(
            decision="DEC-062",
            decision_row=row,
            decision_source=d9.ref(snapshot),
            decision_source_original=str(decision_source),
            near_allocation="family_coordinated",
            allocation_contract=CONTRACT,
            status="draft",
            lead_approved=False,
            template_only=True,
            clarification="100 pair slots; several disjoint pairs from one family permitted; lead review required",
        ),
    )
    # ongoing.md explicitly requests the bound choice in v4. Archive its old bytes;
    # v6 is the operative unsigned form set, and no old signed request is rewritten.
    v4 = ROOT / "docs/tasks/R1-D9-rng-admission-template-v4.json"
    if d9.ref(v4)["sha256"] != history[str(v4)]["sha256"]:
        raise ValueError("v4 changed concurrently")
    value = d9.read_metadata(d9.ref(v4))
    if value.get("lead_approved") is not False:
        raise PermissionError("v4 is signed; do not edit")
    value.update(
        near_allocation="family_coordinated",
        near_allocation_contract=CONTRACT,
        near_allocation_decision=decision,
        superseded_for_execution_by="docs/tasks/R1-D9-rng-admission-template-v6.json",
    )
    v4.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    for path, sha in list(candidate["bindings_sha256"].items()):
        current_sha = d9.sha(path)
        if current_sha != sha:
            if path not in history or history[path]["sha256"] != sha:
                raise ValueError("unexpected concurrent drift: " + path)
            candidate["bindings_sha256"][history[path]["path"]] = sha
            candidate["bindings_sha256"][path] = current_sha
    spec = d9.read_metadata(candidate["d9_inputs"])
    spec.update(
        status="unsigned_operator_DEC062_B_selected_pair_unit_review_pending",
        near_allocation="family_coordinated",
        near_allocation_decision=decision,
    )
    spec["d9"]["draw"]["near_allocation"] = "family_coordinated"
    templates = {}
    for key, binding in spec["receipts"].items():
        if not binding.get("path") or key.endswith("_authorization"):
            continue
        value = d9.read_metadata(binding)
        if value.get("lead_approved") is not False:
            raise PermissionError("no signed receipt may be rebound")
        value.update(candidate_name="v11")
        if key in ("protocol_admission", "rng_admission"):
            value.update(
                near_allocation="family_coordinated",
                near_allocation_contract=CONTRACT,
                near_allocation_decision=decision,
                family_pair_unit_policy_reviewed=False,
            )
        templates[key] = write_new(
            ROOT / f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v6.json", value
        )
    spec["receipts"].update(templates)
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = d9.read_metadata(spec["receipts"][key])
        value.update(
            candidate_name="v11",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        templates[key] = write_new(
            ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v6.json", value
        )
        spec["receipts"][key] = templates[key]
    spec_ref = write_new(ROOT / "docs/tasks/R1-D9-inputs-v6.json", spec)

    def bind(binding):
        if d9.ref(binding["path"]) != binding:
            raise ValueError("package source changed: " + binding["path"])
        candidate["bindings_sha256"][binding["path"]] = binding["sha256"]
        return binding

    for b in (spec_ref, decision, d9.ref(snapshot), *templates.values()):
        bind(b)
    candidate.update(
        schema_version=11,
        name="freeze_candidate_v11",
        producer=bind(d9.ref(__file__)),
        historical_candidate=bind(d9.ref(old_path)),
        d9_inputs=spec_ref,
        d9_templates=templates,
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        near_allocation="family_coordinated",
        near_allocation_decision=decision,
        operator=bind(d9.ref(ROOT / "scripts/r1_58g_operator.py")),
        status="unsigned_DEC062_B_selected_X16_repairs_pair_unit_review_cost_and_signatures_pending",
    )
    checked = verify(candidate)
    result = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v11.json", candidate)
    checked.update(
        candidate=result,
        inputs=spec_ref,
        near_allocation="family_coordinated",
        DEC062_recorded=True,
        allocation_contract_signed=False,
        cost_lead_approved=False,
    )
    write_new(log / "r1-58g-DEC062-package-verification.json", checked)
    return checked


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
