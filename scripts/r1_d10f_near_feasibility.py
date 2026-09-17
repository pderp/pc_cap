"""Prove structural pair capacity on the preteacher pool without making a draw."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from scripts.r1_d9_receipts import read_resource, ref
from scripts.r1_d10a_review import ASSETS, ROOT, write_new
from scripts.r1_d10a_review_core import DATASETS, digest
from scripts.r1_d10d_options import layouts

ADMISSION_TEXT = """Proposed near-miss family NM-template-v1. In each realization reserve 100 support subjects and
100 different neighbour subjects, disjoint from all other roles, realizations and datasets under the
bound name/verified-alias entity policy. A support/neighbor pair is structurally compatible when its
two source rows have the same nonempty near_key: exact source relation_id for CounterFact/MQuAKE,
or exactly equal subject-masked question template for zsRE. zsRE normalizes subject and prompt using
pccap.metrics.editing.normalize_answer and requires exactly one complete-word subject occurrence;
replace that occurrence with {subject}. Bind the implementation hash. This is different-subject,
same-relation/template specificity, not the historical same-subject/other-relation assay, nor proof
that two facts are semantic nearest neighbours. No lexical distance or causal closeness is inferred.

Pair only within already reserved roles, in lexical support-item order with the first unused
lexical neighbour of equal near_key, as in R1-D10c. Do not change the admitted role RNG, retry a
draw, select on outcomes or borrow another role to improve pair availability. The structural
capacity certificate is not a guarantee about independently drawn support/neighbour subsets.
An allocation that deliberately coordinates families would need separate RNG/role admission.

Use an isolated restored episode per available pair: apply the support's bound edit and measure
the neighbour query against its pre-edit baseline under DEC-053 bounded text equality, retaining
termination and truncation diagnostics. Old/own-answer acquisition is recorded, never used as an
admission filter. No answer is invented. Missing compatible pairs remain named unavailable slots
in the planned 100-case inventory per realization. Report evaluated/preserved/missing counts and
the observed-case rate; a full 100-case rate is unavailable if any required slot is missing. Do not
replace the planned denominator by the observed count or count missing cases as failures/successes.

This paragraph is proposed semantic admission text, not an admission receipt. Final teacher review,
current exposure clearance and frozen source/role/endpoint bindings are separate requirements.
"""


def feasibility(evidence, plan, option="D"):
    selected = [d for d in evidence["dispositions"] if d["preteacher_eligible"]]
    plans = {(r["dataset"], r["item_id"]): r for r in plan["rows"]}
    if len(plans) != len(plan["rows"]) or set(plans) != {
        (d["dataset"], d["item_id"]) for d in selected
    }:
        raise ValueError("exact preteacher role-plan coverage required")
    claimed, representatives = {}, {ds: [] for ds in DATASETS}
    for d in selected:
        r = plans[d["dataset"], d["item_id"]]
        if r["payload_sha256"] != d["payload_sha256"]:
            raise ValueError("role-plan payload mismatch")
        if d["entity_id"] in claimed:
            if claimed[d["entity_id"]] != d["dataset"]:
                raise ValueError("global subject collision")
            continue
        claimed[d["entity_id"]] = d["dataset"]
        representatives[d["dataset"]].append({**r, "entity_id": d["entity_id"]})
    family_rows, witnesses, summary = [], [], {}
    layout = layouts(option)
    for ds in DATASETS:
        rows = representatives[ds]
        grouped = defaultdict(list)
        for row in rows:
            if row.get("near_key") and {"near_miss_support", "near_miss_neighbour"} <= set(
                row["roles"]
            ):
                grouped[row["near_key"]].append(row)
        ds_pairs = []
        for family, members in sorted(grouped.items()):
            ordered = sorted(members, key=lambda r: r["item_id"])
            # Canonical first eligible representative partitions entities among
            # families. Thus sum floor(n/2) is exact for this declared policy.
            local_pairs = []
            for i in range(0, len(ordered) - 1, 2):
                support, neighbour = ordered[i : i + 2]
                pair = dict(
                    dataset=ds,
                    family=family,
                    support_item_id=support["item_id"],
                    neighbour_item_id=neighbour["item_id"],
                    support_entity_id=support["entity_id"],
                    neighbour_entity_id=neighbour["entity_id"],
                )
                local_pairs.append(pair)
            ds_pairs.extend(local_pairs)
            family_rows.append(
                dict(
                    dataset=ds,
                    family=family,
                    subjects=len(members),
                    possible_unordered_pairs=len(members) * (len(members) - 1) // 2,
                    maximum_disjoint_pairs=len(local_pairs),
                )
            )
        config = layout.get(ds)
        desired = (
            len(config["realizations"]) * config["roles_per_realization"]["near_miss_support"]
            if config
            else 0
        )
        witness = ds_pairs[:desired]
        used = {p[k] for p in witness for k in ("support_entity_id", "neighbour_entity_id")}
        rest = [r for r in rows if r["entity_id"] not in used]
        revision_need = config["demand_by_role"]["revision"] if config else 0
        nonnear_need = config["demand_subjects"] - 2 * desired if config else 0
        revision_available = sum("revision" in r["roles"] for r in rest)
        # All residual roles must be universally supported, with revision the
        # only stricter eligibility constraint, to use this sufficiency proof.
        basic = all({"edits", "outside"} <= set(r["roles"]) for r in rest)
        proven = (
            len(witness) == desired
            and len(rest) >= nonnear_need
            and revision_available >= revision_need
            and basic
        )
        for i, p in enumerate(witness):
            p = dict(
                p,
                hypothetical_realization=i // 100,
                hypothetical_slot=i % 100,
                purpose="existence_witness_only_not_RNG_or_reservation",
            )
            witnesses.append(p)
        summary[ds] = dict(
            subjects=len(rows),
            families=len(grouped),
            maximum_disjoint_pairs=len(ds_pairs),
            canonical_representative_policy="first preteacher eligible row in v4 register order per entity; alternative relations of repeated subjects not double counted",
            requested_pairs=desired,
            near_pair_capacity_sufficient=len(ds_pairs) >= desired,
            remaining_subjects_in_witness=len(rest),
            nonnear_demand=nonnear_need,
            remaining_revision_eligible=revision_available,
            revision_demand=revision_need,
            joint_preteacher_existence_proven=proven,
            actual_postdraw_pair_count=None,
            actual_draw_guarantees_100_pairs_per_realization=False,
            final_teacher_capacity_certified=False,
        )
    return summary, dict(
        families=family_rows,
        existence_witnesses=witnesses,
        representative_policy="first eligible register row per global entity",
        allocation=False,
        rng_calls=0,
    )


def run(review_path, plan_report_path, output, report_path):
    if output.exists() or not output.resolve().is_relative_to(ASSETS):
        raise ValueError("new assets directory required")
    if not report_path.resolve().is_relative_to(ROOT / "logs"):
        raise ValueError("repository log required")
    review = json.loads(review_path.read_text())
    plan_report = json.loads(plan_report_path.read_text())
    evidence = read_resource(review["evidence"])
    plan = read_resource(plan_report["role_plan"])
    summaries = {}
    summary, detail = feasibility(evidence, plan, "D")
    for option in "ABCD":
        summaries[option] = feasibility(evidence, plan, option)[0]
    bindings = [
        ref(review_path),
        ref(plan_report_path),
        review["evidence"],
        plan_report["role_plan"],
        ref(__file__),
        ref(ROOT / "scripts/r1_d10c_endpoints.py"),
        ref(ROOT / "scripts/r1_d10d_options.py"),
        ref(ROOT / "src/pccap/metrics/editing.py"),
    ]
    detail["evidence_bindings"] = bindings
    output.mkdir(parents=True)
    write_new(output / "families-and-witnesses.json", detail)
    result = dict(
        task="R1-D10f",
        chosen_structure="D",
        counts=summary,
        option_counts=summaries,
        detail=ref(output / "families-and-witnesses.json"),
        proposed_admission_text=ADMISSION_TEXT,
        admission_text_sha256=digest(ADMISSION_TEXT),
        evidence_bindings=bindings,
        semantic_admission=False,
        teacher_review=False,
        gpu_seconds=0,
        draws=0,
        seals=0,
    )
    write_new(report_path, result)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--review-report", required=True, type=Path)
    ap.add_argument("--plan-report", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args = ap.parse_args()
    result = run(args.review_report, args.plan_report, args.output, args.report)
    print(json.dumps(result["counts"], indent=2))


if __name__ == "__main__":
    main()
