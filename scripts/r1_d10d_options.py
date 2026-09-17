"""Emit CPU-only Q14 matrix/protocol/D9 candidates; never draw or authorize."""

from __future__ import annotations

import argparse
import copy
import json
from collections import Counter
from pathlib import Path

from scripts.r1_d9_receipts import read_resource, ref
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10a_review_core import DATASETS, digest

ROLES = dict(edits=1000, outside=100, near_miss_support=100, near_miss_neighbour=100, revision=50)
ADAPTATIONS = {
    "scripts/r1_d9_receipts.py": "check_matrix_layout/prepare/draw_value/seal_values: validate v5.2 dataset layouts, pass per-dataset counts/cadences, preserve exact stage authorizations",
    "scripts/r1_d9_receipt_core.py": "review_candidates/allocate/audit_reservations/validate_seal: consume dataset layouts; keep global identity disjointness, Hall checks, RNG streams and whole-draw abort",
    "scripts/r1_d10b_teacher_review.py": "replace fixed 4050 capacity guard with the admitted layout; final teacher certification unchanged",
    "scripts/r1_d10c_endpoints.py": "construct per-dataset realizations/counts/checkpoints, then audit globally; new role plan needed if v5 evidence is promoted",
    "scripts/r1_58c_draw_seal_preflight.py": "check_receipt must compare exact admitted per-dataset role demand rather than 4050 each",
    "final recipes/queue/analysis": "bind each cell's actual cadence, preserve 63 planned intervals and unavailable MQuAKE 1000 claims; reprice reduced cells including full endpoints",
}


def layouts(option):
    if option not in "ABCD" or len(option) != 1:
        raise ValueError("option must be A/B/C/D")
    result = {}
    for ds in DATASETS:
        if ds == "mquake" and option == "C":
            continue
        roles = dict(ROLES)
        if ds == "mquake" and option in "AD":
            roles["edits"] = 300
        realizations = [0] if ds == "mquake" and option == "B" else [0, 1, 2]
        result[ds] = {
            "realizations": realizations,
            "roles_per_realization": roles,
            "checkpoints": [100, 300] if roles["edits"] == 300 else [100, 300, 1000],
            "demand_per_realization": sum(roles.values()),
            "demand_subjects": sum(roles.values()) * len(realizations),
            "demand_by_role": {r: n * len(realizations) for r, n in roles.items()},
        }
    return result


def capacity(evidence, layout):
    result = {}
    for ds in DATASETS:
        eligible = [
            d for d in evidence["dispositions"] if d["dataset"] == ds and d["preteacher_eligible"]
        ]
        subjects = len({d["entity_id"] for d in eligible})
        demand = layout.get(ds, {}).get("demand_subjects", 0)
        result[ds] = dict(
            preteacher_items=len(eligible),
            preteacher_subjects=subjects,
            demand_subjects=demand,
            margin=subjects - demand,
            scalar_capacity_sufficient=subjects >= demand,
            teacher_and_joint_role_capacity_certified=False,
        )
    return result


def build_matrix(parent, option):
    layout = layouts(option)
    matrix = {
        k: copy.deepcopy(parent[k])
        for k in (
            "bootstrap",
            "contrasts",
            "multiplicity",
            "classifier",
            "secondary_benchmarks",
            "queue",
        )
    }
    delta = {"removed": [], "recadenced": [], "retained": []}

    def cells(old):
        result = []
        counters = Counter()
        for source in old:
            ds = source["dataset"]
            key = {
                k: source[k]
                for k in ("cell_id", "dataset", "condition", "realization", "order", "block_number")
            }
            if ds not in layout or source["realization"] not in layout[ds]["realizations"]:
                delta["removed"].append(key)
                continue
            cell = {
                k: copy.deepcopy(source[k])
                for k in (
                    "cell_id",
                    "dataset",
                    "condition",
                    "realization",
                    "order",
                    "block_number",
                    "model_seed",
                    "outside_population_id",
                    "pairing_id",
                    "result_path_template",
                    "ceilings",
                )
            }
            counters[cell["block_number"]] += 1
            cell["within_block_order"] = counters[cell["block_number"]]
            cell["checkpoints"] = list(layout[ds]["checkpoints"])
            cell["attempted_edits"] = layout[ds]["roles_per_realization"]["edits"]
            cell["ceilings"]["checkpoint_seconds"] = {str(n): None for n in cell["checkpoints"]}
            cell.update(
                admitted=False,
                launch_allowed=False,
                population=None,
                recipe_template=None,
                manifest_sha256=None,
                result_dir=None,
            )
            cell["historical_recipe_template"] = source["recipe_template"]
            cell["historical_expected_definition_sha256"] = source["expected_definition_sha256"]
            cell["expected_definition_sha256"] = digest(
                {
                    "schema": "stage4-v5.2-planned-definition",
                    "historical_definition": source["expected_definition_sha256"],
                    "cell_id": cell["cell_id"],
                    "layout": layout[ds],
                }
            )
            if cell["checkpoints"] != source["checkpoints"]:
                delta["recadenced"].append(
                    {
                        **key,
                        "old_checkpoints": source["checkpoints"],
                        "new_checkpoints": cell["checkpoints"],
                    }
                )
            else:
                delta["retained"].append(key)
            result.append(cell)
        return result

    matrix["cells"] = cells(parent["cells"])
    matrix["extension"] = {
        "allocation_approved": False,
        "cells": cells(parent["extension"]["cells"]),
        "interpretation": "historical v2 package; separately admitted",
    }
    all_cells = matrix["cells"] + matrix["extension"]["cells"]
    sizes = Counter(c["block_number"] for c in all_cells)
    matrix["queue"]["block_sizes"] = [sizes[i] for i in range(1, 7)]
    matrix.update(
        schema_version=7,
        name="run_matrix_v5_2_option_" + option,
        task="R1-D10d",
        option=option,
        status="candidate_pending_context_endpoint_and_execution_admission",
        axes={
            "conditions": parent["axes"]["conditions"],
            "datasets": list(layout),
            "orders": parent["axes"]["orders"],
            "realizations_by_dataset": {d: x["realizations"] for d, x in layout.items()},
        },
        dataset_layouts=layout,
        layout_sha256=digest(layout),
        population={
            "required_subjects_by_dataset": {d: x["demand_subjects"] for d, x in layout.items()},
            "final_role_population_bound": False,
            "guaranteed_clearance": False,
        },
        budget={
            "core_cells": len(matrix["cells"]),
            "extension_cells": len(matrix["extension"]["cells"]),
            "total_cells": len(all_cells),
            "costs_admitted": False,
            "measured_total_ceiling_seconds": None,
        },
        mquake_primary_1000_status="unavailable_missing_three_realization_1000_population",
        coordinate_identity=parent["coordinate_identity"],
        execution_identity="v5.2 planned definition binds historical template and dataset layout; final code/recipe/population/cost receipt still required",
        confirmation_protocol_frozen=False,
        draw_authorized=False,
        launch_allowed=False,
        context_review_required=option == "D",
        context_review_admitted=False,
        historical_candidate_definitions_reused_as_execution_recipes=False,
        gpu_seconds=0,
        model_calls=0,
        sealed_payloads_opened=0,
    )
    return matrix, delta


def protocol(parent_text, option, matrix, capacities):
    """Full predecessor plus normative replacement sections, with precedence explicit."""
    layout = matrix["dataset_layouts"]
    rows = []
    for ds in DATASETS:
        v = layout.get(ds)
        rows.append(
            f"| {ds} | {len(v['realizations']) if v else 0} | {v['roles_per_realization']['edits'] if v else 0} | "
            f"{', '.join(map(str, v['checkpoints'])) if v else 'absent'} | {v['demand_subjects'] if v else 0} | "
            f"{capacities[ds]['preteacher_subjects']} | {capacities[ds]['margin']} |"
        )
    sizes = matrix["queue"]["block_sizes"]
    status = (
        "DEC-060 selects D; context adjudication and orchestrator review are still required."
        if option == "D"
        else "Counterfactual option package; DEC-060 selected D, not this alternative."
    )
    return f"""# Revision v1 — Stage 4 protocol v5.2 option {option} candidate (R1-D10d)

{status} This candidate grants no draw, seal, freeze, launch or endpoint admission.
Experimental completion stops **October 9**; the presentation is October 15.

## Normative replacements to v5.1 §§2, 4, 5.1, 5.3, 6 and U01/U06/U08/U14/U17

The following replacements govern this option. The complete v5.1 text below is retained as a
labelled historical appendix for unchanged condition, metric, scoring, scientific and restoration
details. Its uniform 1,000-edit scope, capacity table, 168-subject headroom, block counts and
then-pending driver/calibration statuses do not describe this candidate.

| Dataset | Realizations | Edits each | Checkpoints | Total distinct subjects | D10a v4 preteacher | Margin |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
{chr(10).join(rows)}

Each included realization reserves its listed edits plus outside100, near-support100,
near-neighbour100 and revision50. Global subject/fact disjointness spans roles, realizations
and datasets. Five orders100–104 reuse each realization's same reserved facts and endpoints.
Composition uses only dependencies already in the edit set; additional subjects require a new
admitted demand, never implicit borrowing. Counts above precede teacher and joint-role review.

**U08:** zsRE/CounterFact retain 100/300/1,000 attempted edits and three realizations.
MQuAKE follows only the table. Under A/D it has no 1,000-edit or 1,000-record observation.
Under B only realization0 exists; orders do not supply independent realization clusters.
Under C MQuAKE has no confirmatory cells. Actual occupancy is measured separately from attempts.
Challenge cadence and full-validation inventory/costs still require explicit binding.

**U12 / DEC-057:** preserve the entire planned 63-interval family and .05/63 allocation;
zsRE/CounterFact retain their three-cluster, five-paired-order procedure unchanged. MQuAKE's
seven 1,000-edit contrasts (21 intervals) are unavailable in all four options, for missing
cadence (A/D), missing two independent realizations (B), or no dataset (C). No reallocation to
42 intervals, no treating orders as clusters, no 300→1,000 substitution and no primary
classification from incomplete populations. MQuAKE100/300 is secondary descriptive;
option B's single realization at1,000 is descriptive without a three-cluster interval.
DEC-058's exact classifier and DEC-053 bounded equality/termination diagnostics remain unchanged.

**U14 / DEC-059:** A/D cannot estimate MQuAKE F1000, F1000−F100 or 100→1,000 changes in
RET-GS/ES/LS; all are unavailable. Its 100/300 results and common-outside difference are descriptive
and do not inherit the admitted 1,000-record benchmark. Under B, a complete single-realization
cell may report its observed 1,000-point descriptive tolerance, but a population cluster interval
or equivalence claim is unavailable. Under C all MQuAKE endpoints are absent. Revision50,
near100, bounded scoring, termination/truncation and fixed missingness remain explicit.
No change to zsRE/CounterFact benchmarks or to separately admitted resource ceilings.

**DEC-048 context policy:** v4 machine evidence waives only its three exact known-subject
true-fact locality/unrelated query reasons. Historical near reservations and ambiguous query
mentions remain quarantined; v5.1's broader verified-near wording is not a blanket waiver.
R1-D10e supplies a separately hash-bound candidate evidence resource; adoption needs an explicit
review. Its proposal does not certify homonyms, erase direct subject exposure or admit teacher
eligibility. No candidate rows may be used for new development. A larger MQuAKE cadence, even
if capacity improves, returns to the lead as required by DEC-060.

**DEC-051 blocks:** B1–B6 contain {", ".join(map(str, sizes))} cells respectively;
core={matrix["budget"]["core_cells"]}, separately admitted extension={matrix["budget"]["extension_cells"]}.
Retain block numbers and coordinate cell IDs, compact surviving within-block slots only.
The machine delta lists every removed and recadenced cell. All new planned definitions bind
the dataset layout; historical development recipes are not executable final recipes.

**U06/U07/U09/U16/U17:** final teacher review, current exposure supplement, near-family admission,
joint role allocation, RNG/clearance/draw/seal receipts, versioned D9 heterogeneous-layout
support, final recipes and September20 measured cost admission remain open. The D9 option
inputs are unsigned configuration candidates. They deliberately fail old v5.1-only validators.
Freeze candidate v7 is an inventory, never an authority to execute.

## Historical appendix: complete v5.1 text (superseded where stated above)

{parent_text}
"""


def emit(option, output):
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "docs/tasks") or output.exists():
        raise ValueError("new repository docs/tasks output directory required")
    parent_path = ROOT / "manifests/revision_v1/run_matrix_v5_1.json"
    parent = json.loads(parent_path.read_text())
    report_path = ROOT / "logs/r1_round22/r1-d10a-review-v4.json"
    review = json.loads(report_path.read_text())
    evidence = read_resource(review["evidence"])
    matrix, delta = build_matrix(parent, option)
    capacities = capacity(evidence, matrix["dataset_layouts"])
    output.mkdir()
    protocol_path = ROOT / f"docs/R1_stage4_protocol_draft_v5_2_option_{option}.md"
    with protocol_path.open("x") as f:
        f.write(
            protocol(
                (ROOT / "docs/R1_stage4_protocol_draft_v5_1.md").read_text(),
                option,
                matrix,
                capacities,
            )
        )
    matrix_path = ROOT / f"manifests/revision_v1/run_matrix_v5_2_option_{option}.json"
    decision_row = next(
        s
        for s in (ROOT / "docs/decisions.md").read_text().splitlines()
        if s.startswith("| DEC-060 |")
    )
    matrix.update(
        historical_matrix=ref(parent_path),
        protocol=ref(protocol_path),
        calibration=ref(ROOT / "manifests/revision_v1/calibration_v3.json"),
        primary_condition=ref(ROOT / "manifests/revision_v1/primary_condition_v5.json"),
        accepted_decisions={
            **parent["accepted_decisions"],
            "DEC-060": {"row": decision_row, "row_sha256": digest(decision_row)},
        },
        producer=ref(__file__),
        preteacher_evidence=review["evidence"],
    )
    write_new(matrix_path, matrix)
    original = ROOT / "docs/tasks/R1-D9-inputs-v2.json"
    spec = json.loads(original.read_text())
    spec.update(
        schema_version=3,
        task="R1-D10d",
        option=option,
        status="unsigned_candidate_requires_versioned_D9_layout_support_and_admissions",
        matrix=ref(matrix_path),
        protocol=ref(protocol_path),
        historical_inputs=ref(original),
        freeze_candidate={"path": None, "sha256": None},
        dataset_layouts=matrix["dataset_layouts"],
        layout_sha256=matrix["layout_sha256"],
        capacity=capacities,
        execution_authorized=False,
        producer=ref(__file__),
        required_consumer_adaptations=ADAPTATIONS,
    )
    spec["pending"]["context_adjudication_review"] = (
        "required_DEC060; proposed v5 cannot be silently promoted"
        if option == "D"
        else "not selected by DEC060"
    )
    spec["pending"]["capacity_resolution"] = {"path": None, "sha256": None}
    spec["note"] = (
        "Role demand is explicit per dataset/realization. Existing v2 authorization templates remain unsigned historical forms; request hashes must be recomputed after layout and review adoption."
    )
    write_new(output / "d9-inputs.json", spec)
    write_new(output / "matrix-delta.json", delta)
    summary = dict(
        task="R1-D10d",
        option=option,
        matrix=ref(matrix_path),
        protocol=ref(protocol_path),
        d9_inputs=ref(output / "d9-inputs.json"),
        delta=ref(output / "matrix-delta.json"),
        evidence=review["evidence"],
        capacity=capacities,
        budget=matrix["budget"],
        block_sizes=matrix["queue"]["block_sizes"],
        delta_counts={k: len(v) for k, v in delta.items()},
        selected_structure=option == "D",
        context_review_admitted=False,
        execution_ready=False,
        required_consumer_adaptations=ADAPTATIONS,
    )
    write_new(output / "summary.json", summary)
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--option", required=True, choices=list("ABCD"))
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()
    result = emit(args.option, args.output)
    print(
        json.dumps(
            {
                k: result[k]
                for k in ("option", "budget", "capacity", "delta_counts", "execution_ready")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
