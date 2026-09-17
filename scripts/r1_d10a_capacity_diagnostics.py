"""Explain conservative exposure losses; sensitivity counts never clear rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from scripts.r1_d9_receipts import read_resource, ref
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import Entities

NEAR = {"reserved_near_miss_candidate", "mquake_unverified_near_miss_query_subject"}


def explain(evidence, inputs, checks):
    dispositions = {(r["dataset"], r["item_id"]): r for r in evidence["dispositions"]}
    events = inputs["events"]
    entities = Entities(inputs["verified_alias_pairs"])
    strict, without_near, subject_only = set(), set(), set()
    by_reason, examples = Counter(), {}
    for check in checks:
        if check["dataset"] != "mquake":
            continue
        disp = dispositions["mquake", check["item_id"]]
        blocked = [events[i] for i in check.get("blocking_event_indices", [])]
        reasons = {e["reason"] for e in blocked}
        by_reason.update(reasons)
        for event in blocked:
            examples.setdefault(
                event["reason"], {"candidate_subject": check["entity_key"], "event": event}
            )
        if disp["preteacher_eligible"]:
            strict.add(disp["entity_id"])
        if not (reasons - NEAR) and check["token_context_check"]["pass"]:
            without_near.add(disp["entity_id"])
        if not any(
            e.get("subject")
            and e["reason"] not in NEAR
            and entities.identity(e["subject"])[0] == disp["entity_id"]
            for e in blocked
        ):
            subject_only.add(disp["entity_id"])
    return {
        "task": "R1-D10a",
        "dataset": "mquake",
        "demand_subjects": 4050,
        "strict_preteacher_subjects": len(strict),
        "sensitivity_ignore_all_near_reservations_subjects": len(without_near),
        "sensitivity_ignore_near_and_all_text_only_matches_subjects": len(subject_only),
        "blocking_reason_item_counts_nonexclusive": dict(by_reason),
        "examples": examples,
        "interpretation": [
            "Strict uses the frozen implementation's three exact query waivers; no verified-near-miss waiver was inferred.",
            "Protocol v5.1 section4 mentions verified near-miss true queries; reconcile this wording with DEC-048 and register v5/v6 implementation before admitting any such release.",
            "Ignoring all near reservations is an optimistic diagnostic, not verification that every presentation was a true-fact query or that counterfactual support was absent.",
            "Ignoring text-only matches would discard the required context review and is not an admissible clearance policy.",
            "A text match can be a homonym or incidental object mention. These are review candidates, not proof of primary counterfactual editing.",
            "Counts are before final-base teacher review and role capacity checks. No dispositions, exemptions or experiment scope were changed.",
        ],
        "gpu_seconds": 0,
        "draws": 0,
        "seals": 0,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--review-report", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if not args.output.resolve().is_relative_to(ROOT / "logs"):
        ap.error("repository report required")
    report = json.loads(args.review_report.read_text())
    evidence, inputs, checks = [
        read_resource(report[k]) for k in ("evidence", "inputs", "row_checks")
    ]
    result = explain(evidence, inputs, checks)
    result["evidence_bindings"] = [
        ref(args.review_report),
        *(report[k] for k in ("evidence", "inputs", "row_checks")),
        ref(__file__),
        ref(ROOT / "docs/R1_stage4_protocol_draft_v5_1.md"),
        ref(ROOT / "scripts/r1_d1h_register_v5.py"),
    ]
    write_new(args.output, result)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in {"examples", "evidence_bindings"}},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
