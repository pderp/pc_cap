"""Current package check and explicit erratum for the initial Q16 status report."""

from __future__ import annotations

import json

from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new


def run():
    log = ROOT / "logs/r1_round27"
    prior = d9.read_metadata(d9.ref(log / "r1-x16-audit.json"))
    candidate_ref = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v11.json")
    candidate = d9.read_metadata(candidate_ref)
    checked = verify(candidate)
    spec = d9.read_metadata(candidate["d9_inputs"])
    decision = d9.read_metadata(spec["near_allocation_decision"])
    source = decision["decision_source"]
    assert d9.ref(source["path"]) == source
    assert decision["decision_row"] in open(source["path"]).read().splitlines()
    assert "**Q16: option B** (lead)" in decision["decision_row"]
    assert candidate["near_allocation"] == "family_coordinated"
    assert not decision["lead_approved"]
    assert not candidate["launch_authorized"]
    assert not (ROOT / "manifests/revision_v1/frozen_stage4.json").exists()
    cost = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-cost-admission-receipt-v1.json"))
    assert cost["lead_approved"] is False
    assert str(ROOT / "docs/R1_stage4_protocol_draft_v5_1.md") not in candidate["bindings_sha256"]
    fields = dict(
        task="X16",
        verdict="NOT_READY_FOR_LEAD_SIGNATURE_OR_LAUNCH",
        supersedes_status_only=d9.ref(log / "r1-x16-audit.json"),
        erratum=(
            "Initial X16-04 and diagnostic metadata incorrectly called DEC-062 pending. "
            "DEC-062 already records option B; its source row is preserved here. "
            "Numerical two-mode diagnostics remain valid. The unresolved detail is whether "
            "100 denotes pair slots or distinct families, not the accepted B choice."
        ),
        decision="DEC-062",
        decision_source=source,
        decision_row=decision["decision_row"],
        candidate=candidate_ref,
        current_verification=checked,
        inputs=candidate["d9_inputs"],
        allocation_contract=spec["near_allocation_decision"],
        near_allocation="family_coordinated",
        contract_lead_review_pending=True,
        inherited_normative_text_bound=False,
        cost_lead_approved=False,
        HT4f="blocked; no final ledger published",
        original_numerical_report=d9.ref(log / "r1-x16-audit.json"),
        findings=[
            f
            if not f.startswith("X16-04")
            else "X16-04 DEC-062 B is recorded and bound; exact multiple-pairs-per-family interpretation awaits review"
            for f in prior["findings"]
        ],
        note="v9/v10 are historical; v11/v6 bind the changed code and v4 choice. No X16 owner-document repairs applied.",
        gpu_seconds=0,
        actual_draws=0,
        seals=0,
        signatures=0,
        producer=d9.ref(__file__),
    )
    write_new(log / "r1-x16-DEC062-addendum.json", fields)
    print(json.dumps(fields, indent=2))


if __name__ == "__main__":
    run()
