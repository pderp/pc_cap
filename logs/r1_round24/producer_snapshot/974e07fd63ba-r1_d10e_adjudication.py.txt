"""Outcome-independent context worksheet and non-operative v5 evidence overlay."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter, defaultdict
from pathlib import Path

from scripts.r1_d9_receipts import read_resource, ref
from scripts.r1_d10a_review import ASSETS, ROOT, write_new
from scripts.r1_d10a_review_core import DATASETS, Entities, digest

RULE = {
    "id": "ordinary-text-only-context-review-v1",
    "waivable_reasons": ["ordinary_text_training_prefix", "development_drift_text"],
    "definition": "Waive a blocking event only if its exact reason denotes ordinary training-prefix or drift text, it has nonempty text, and it has no subject or waiver-subject annotation. Preserve every other event, including all edit, answer, paraphrase, locality, near, revision, composition and ambiguous query contexts and all direct subject reservations.",
    "homonyms": "No homonym is inferred or released from lexical matching, dataset mismatch or answer identity. A verified entity-linking supplement would require separate evidence and review.",
    "interpretation": "Ordinary-text mentions are not task-specific counterfactual edit exposure under the proposed rule. They may still influence the trained reader or model; subject-naivety is not asserted.",
    "selection": "No outcome, teacher output, loss, retention, answer correctness or capacity target used to decide an event waiver.",
    "bounded_review": "Use exactly the v4 reviewed rows; do not advance into unreviewed rows or discard existing eligible rows. Recheck cross-dataset identity disjointness; a newly proposed release may not displace any v4 eligible entity in another dataset.",
}


def waive(event):
    return (
        event["reason"] in RULE["waivable_reasons"]
        and bool(event.get("text"))
        and not event.get("subject")
        and not event.get("waiver_subjects")
    )


def adjudicate(evidence, inputs, checks):
    dispositions = {(d["dataset"], d["item_id"]): d for d in evidence["dispositions"]}
    if len(dispositions) != len(evidence["dispositions"]) or len(checks) != len(dispositions):
        raise ValueError("unique exhaustive row checks required")
    if {(c["dataset"], c["item_id"]) for c in checks} != set(dispositions):
        raise ValueError("row-check coverage differs")
    entities = Entities(inputs["verified_alias_pairs"])
    fixed = defaultdict(set)
    for d in evidence["dispositions"]:
        if d["preteacher_eligible"]:
            fixed[d["entity_id"]].add(d["dataset"])
    if any(len(ds) > 1 for ds in fixed.values()):
        raise ValueError("v4 eligible subjects overlap across datasets")
    worksheet, proposed, claimed, groups = [], [], dict(fixed), defaultdict(list)
    details = {(c["dataset"], c["item_id"]): c for c in checks}
    # v4 register order and dataset priority are preserved; eligible identities
    # across all datasets are reserved first so an overlay never evicts them.
    for original in evidence["dispositions"]:
        d = copy.deepcopy(original)
        check = details[d["dataset"], d["item_id"]]
        indices = check.get("blocking_event_indices", [])
        events = []
        for i in indices:
            if type(i) is not int or not 0 <= i < len(inputs["events"]):
                raise ValueError("invalid source-event index")
            event = inputs["events"][i]
            direct = (
                bool(event.get("subject"))
                and entities.identity(event["subject"])[0] == d["entity_id"]
            )
            events.append(
                {
                    "event_index": i,
                    "source_event": event,
                    "direct_subject_match": direct,
                    "proposed_action": "waive_ordinary_text_context"
                    if waive(event)
                    else "retain_quarantine",
                }
            )
        token_ok = check.get("token_context_check", {}).get("pass") is True
        # Every context-only candidate gets a row, including those still blocked
        # by query contexts. Non-context blockers must never be silently lifted.
        context_only = (
            bool(events)
            and not any(e["direct_subject_match"] for e in events)
            and bool(check.get("entity_key"))
            and token_ok
            and set(d["reasons"]) == {"exposed_context_name_match"}
        )
        if context_only:
            retained = [e for e in events if e["proposed_action"] == "retain_quarantine"]
            collision = bool(claimed.get(d["entity_id"], set()) - {d["dataset"]})
            release = not retained and not collision
            row = {
                k: d[k]
                for k in ("dataset", "item_id", "canonical_subject", "entity_id", "payload_sha256")
            }
            row.update(
                events=events,
                reasons=sorted({e["source_event"]["reason"] for e in events}),
                proposed_preteacher_release=release,
                remaining_event_indices=[e["event_index"] for e in retained],
                cross_dataset_collision=collision,
                decision="exclude",
                teacher_and_role_review_pending=True,
            )
            worksheet.append(row)
            for reason in row["reasons"]:
                groups[d["dataset"] + ":" + reason].append(d["item_id"])
            if release:
                d.update(
                    preteacher_eligible=True,
                    alias_clear=True,
                    context_clear=True,
                    exposure_clear=True,
                    reasons=["pending_final_teacher_token_and_role_review"],
                    teacher_pass=None,
                    tokens_pass=None,
                    roles=[],
                )
                claimed[d["entity_id"]] = {d["dataset"]}
        proposed.append(d)
    counts = {}
    for ds in DATASETS:
        old = [
            d for d in evidence["dispositions"] if d["dataset"] == ds and d["preteacher_eligible"]
        ]
        new = [d for d in proposed if d["dataset"] == ds and d["preteacher_eligible"]]
        old_ids, new_ids = {d["entity_id"] for d in old}, {d["entity_id"] for d in new}
        if not old_ids <= new_ids:
            raise ValueError("proposal displaced existing evidence")
        counts[ds] = dict(
            v4_items=len(old),
            v4_subjects=len(old_ids),
            proposed_items=len(new),
            proposed_subjects=len(new_ids),
            restored_subjects=len(new_ids - old_ids),
            context_only_items=sum(w["dataset"] == ds for w in worksheet),
            proposed_margin_4050=len(new_ids) - 4050,
            proposed_margin_DEC060=len(new_ids) - (1950 if ds == "mquake" else 4050),
        )
    # Keep operative dispositions exactly intact. Only a later reviewed/promoted
    # evidence artifact may replace the D9 evidence binding.
    candidate = copy.deepcopy(evidence)
    candidate.update(
        schema_version=5,
        mode="unsealed_context_adjudication_candidate",
        status="proposed_only_not_admitted_not_D9_clearance",
        review_rule=RULE,
        review_rule_sha256=digest(RULE),
        dispositions=copy.deepcopy(evidence["dispositions"]),
        proposed_dispositions=proposed,
        proposed_counts=counts,
        context_adjudication_admitted=False,
        orchestrator_review_receipt=None,
        teacher_token_review_complete=False,
        role_compatibility_complete=False,
    )
    return (
        candidate,
        {"rows": worksheet, "grouped_by_reason": dict(sorted(groups.items())), "rule": RULE},
        counts,
    )


def run(review_path, output, report_path):
    if output.exists() or not output.resolve().is_relative_to(ASSETS):
        raise ValueError("new assets directory required")
    if not report_path.resolve().is_relative_to(ROOT / "logs"):
        raise ValueError("repository report required")
    review = json.loads(review_path.read_text())
    evidence, inputs, checks = [
        read_resource(review[k]) for k in ("evidence", "inputs", "row_checks")
    ]
    candidate, worksheet, counts = adjudicate(evidence, inputs, checks)
    bindings = [
        ref(review_path),
        *(review[k] for k in ("evidence", "inputs", "row_checks")),
        ref(__file__),
        ref(ROOT / "scripts/r1_d10a_review_core.py"),
    ]
    candidate["evidence_bindings"] += bindings
    candidate["parent_v4"] = review["evidence"]
    worksheet["evidence_bindings"] = bindings
    output.mkdir(parents=True)
    write_new(output / "evidence-v5-candidate.json", candidate)
    write_new(output / "context-worksheet.json", worksheet)
    result = dict(
        task="R1-D10e",
        status="mechanical proposal ready for orchestrator review",
        parent_v4=review["evidence"],
        candidate_v5=ref(output / "evidence-v5-candidate.json"),
        worksheet=ref(output / "context-worksheet.json"),
        rule=RULE,
        counts=counts,
        reason_item_counts_nonexclusive={
            k: len(v) for k, v in worksheet["grouped_by_reason"].items()
        },
        retained_quarantine_reason_counts=dict(
            Counter(
                e["source_event"]["reason"]
                for w in worksheet["rows"]
                for e in w["events"]
                if e["proposed_action"] == "retain_quarantine"
            )
        ),
        operative_dispositions_unchanged=candidate["dispositions"] == evidence["dispositions"],
        evidence_bindings=bindings,
        exposure_as_of_commit=evidence["exposure_as_of_commit"],
        later_exposure_supplement_required=True,
        admission=False,
        gpu_seconds=0,
        draws=0,
        seals=0,
    )
    write_new(report_path, result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--review-report", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    result = run(args.review_report, args.output, args.report)
    print(json.dumps(result["counts"], indent=2))


if __name__ == "__main__":
    main()
