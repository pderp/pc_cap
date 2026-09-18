"""D.5: preserve all coordinates and computations; change interpretation/order only."""

import copy
import hashlib
from collections import Counter

from scripts import r1_49g_inference as inference
from scripts import r1_49o_sensitivity as sensitivity
from scripts import r1_d9_receipts as d9
from scripts.r1_49o_normative_closure import PROTOCOL, closure
from scripts.r1_d10a_review import ROOT, write_new


def document():
    parent = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json")
    matrix = copy.deepcopy(d9.read_metadata(parent))
    matrix.update(
        schema_version=12,
        policy_revision="DEC068_DEC069_D5",
        task="R1-63o",
        protocol=d9.ref(ROOT / PROTOCOL),
        normative_closure=closure(),
        historical_matrix=parent,
        producer=d9.ref(__file__),
        inference_interpretation=copy.deepcopy(sensitivity.CONTRACT),
        locality_selection_approval=d9.ref(
            ROOT / "docs/tasks/R1-63o-locality-selection-approval.md"
        ),
        status="unsigned_D5_admissions_pending",
        execution_identity="D.5 prospective order; retained coordinates and no historical execution relabelled",
    )
    for cell in matrix["cells"]:
        condition = cell["condition"]
        cell["block_number"] = (
            cell["realization"] + 1
            if condition in ("R1_learned_ff", "R1_nonlearned", "v0_stable")
            else 5
            if condition.startswith("S1_")
            else 4
        )
    matrix["cells"].sort(key=lambda c: c["block_number"])
    counts = Counter()
    for cell in matrix["cells"] + matrix["extension"]["cells"]:
        counts[cell["block_number"]] += 1
        previous = cell["expected_definition_sha256"]
        cell.update(
            previous_D4_definition_sha256=previous, within_block_order=counts[cell["block_number"]]
        )
        cell["expected_definition_sha256"] = d9.core.content_digest(
            dict(
                previous_D4_definition_sha256=previous,
                decision="DEC-068",
                block_number=cell["block_number"],
                within_block_order=cell["within_block_order"],
            )
        )
    matrix["queue"].update(
        block_sizes=[counts[i] for i in range(1, 7)],
        block_labels=[
            "primary/random/stable r0",
            "primary/random/stable r1",
            "primary/random/stable r2",
            "matched/liveC1/liveC2 all realizations",
            "S1 both all realizations",
            "historical v2 extension",
        ],
        block_order_decision="DEC-068",
        triplet_complete_after_block=3,
    )
    for decision in ("DEC-068", "DEC-069"):
        row = next(
            r
            for r in (ROOT / "docs/decisions.md").read_text().splitlines()
            if r.startswith("| " + decision + " |")
        )
        matrix["accepted_decisions"][decision] = dict(
            row=row, sha256=hashlib.sha256(row.encode()).hexdigest()
        )
    for name in (
        *matrix["analysis_implementation"],
        "r1_49o_sensitivity",
        "r1_d14_report",
        "r1_63o_locality",
    ):
        matrix["analysis_implementation"][name] = d9.ref(ROOT / f"scripts/{name}.py")
    matrix["classifier"]["implementation"] = d9.ref(inference.__file__)
    d9.check_matrix_layout(matrix)
    inference.validate_family(matrix)
    assert matrix["queue"]["block_sizes"] == [45, 45, 45, 90, 60, 45]
    return matrix


if __name__ == "__main__":
    print(write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_5.json", document()))
