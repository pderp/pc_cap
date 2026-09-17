"""Unsigned operator-v5 inputs and candidate v10 after the authorized draw hook.

Independent allocation remains selected. DEC-062, cost completion and lead
signatures are not inferred. The prior candidate and every prior form survive.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new

LOG = ROOT / "logs/r1_round27"


def build():
    old_path = ROOT / "manifests/revision_v1/freeze_candidate_v9.json"
    old = d9.read_metadata(d9.ref(old_path))
    candidate = copy.deepcopy(old)
    permitted = {str(ROOT / n) for n in ("scripts/r1_d9_draw.py", "scripts/r1_d9_receipts.py")}
    for path, sha in candidate["bindings_sha256"].items():
        if d9.sha(path) != sha and path not in permitted:
            raise ValueError("unexpected source drift requires separate review: " + path)
    snapshots = json.loads((LOG / "source-snapshots.json").read_text())
    for path in permitted:
        historical = snapshots[str(Path(path).relative_to(ROOT))]
        if (
            path in candidate["bindings_sha256"]
            and candidate["bindings_sha256"][path] != historical["sha256"]
        ):
            raise ValueError("prior code snapshot differs")
        candidate["bindings_sha256"][historical["path"]] = historical["sha256"]
        candidate["bindings_sha256"][path] = d9.sha(path)
    spec = d9.read_metadata(old["d9_inputs"])
    spec.update(
        task="R1-58g/R1-D9f",
        status="unsigned_operator_v5_independent_default",
        near_allocation="independent",
        near_allocation_decision=None,
    )
    spec["d9"]["draw"]["near_allocation"] = "independent"
    cost = d9.ref(ROOT / "docs/tasks/R1-cost-admission-receipt-v1.json")
    spec["d9"]["clearance"]["configuration_bindings"]["cost_admission_source_unsigned"] = cost
    templates = {}
    for key, binding in spec["receipts"].items():
        if not binding.get("path") or key.endswith("_authorization"):
            continue
        value = d9.read_metadata(binding)
        if value.get("lead_approved") is not False:
            raise PermissionError("signed receipt cannot become a new template")
        value.update(candidate_name="v10")
        if key in ("protocol_admission", "rng_admission"):
            value.update(near_allocation="independent", near_allocation_decision=None)
        templates[key] = write_new(
            ROOT / f"docs/tasks/R1-D9-{key.replace('_', '-')}-template-v5.json", value
        )
    spec["receipts"].update(templates)
    for stage in ("clearance", "draw", "seal"):
        key = stage + "_authorization"
        value = d9.read_metadata(spec["receipts"][key])
        if value.get("lead_approved") is not False:
            raise PermissionError("signed authorization cannot be rebound")
        value.update(
            candidate_name="v10",
            request_sha256=None,
            inspection_only_request_sha256=d9.contract(spec, stage),
        )
        templates[key] = write_new(
            ROOT / f"docs/tasks/R1-D9-{stage}-authorization-template-v5.json", value
        )
        spec["receipts"][key] = templates[key]
    spec_ref = write_new(ROOT / "docs/tasks/R1-D9-inputs-v5.json", spec)

    def bind(binding):
        if d9.ref(binding["path"]) != binding:
            raise ValueError("binding changed during package assembly")
        candidate["bindings_sha256"][binding["path"]] = binding["sha256"]
        return binding

    for name in (
        "scripts/r1_d9f_allocation.py",
        "scripts/r1_d9f_dry_review.py",
        "scripts/r1_58g_operator.py",
        "scripts/r1_58g_package.py",
    ):
        bind(d9.ref(ROOT / name))
    for b in (spec_ref, cost, *templates.values()):
        bind(b)
    candidate.update(
        schema_version=10,
        name="freeze_candidate_v10",
        task="R1-58g",
        producer=bind(d9.ref(__file__)),
        historical_candidate=bind(d9.ref(old_path)),
        d9_inputs=spec_ref,
        d9_templates=templates,
        d9_request_sha256={s: d9.contract(spec, s) for s in ("clearance", "draw", "seal")},
        near_allocation="independent",
        near_allocation_decision=None,
        cost_admission_source_unsigned=cost,
        cost_admission_receipt=None,
        status="unsigned_operator_package_Q16_and_cost_completion_and_lead_signatures_pending",
        operator=bind(d9.ref(ROOT / "scripts/r1_58g_operator.py")),
        dry_reports=old["dry_reports"],
        dry_reports_note="historical v9 dry runs; operator generates current requests and dry results",
    )
    checked = verify(candidate)
    result = write_new(ROOT / "manifests/revision_v1/freeze_candidate_v10.json", candidate)
    checked.update(
        task="R1-58g",
        candidate=result,
        inputs=spec_ref,
        near_allocation="independent",
        family_mode_authorized=False,
        cost_lead_approved=False,
    )
    write_new(LOG / "r1-58g-package-verification.json", checked)
    return checked


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
