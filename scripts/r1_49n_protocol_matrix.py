"""Version D.3 into the lead's DEC-066 prospective D.4 matrix; no admission."""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter

from scripts import r1_49m_fidelity_policy as fidelity
from scripts import r1_49n_scope as scope
from scripts import r1_d9_receipts as d9
from scripts.r1_49n_normative_closure import PROTOCOL, closure
from scripts.r1_d10a_review import ROOT, write_new


def document():
    parent = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_3.json")
    matrix = d9.read_metadata(parent)
    original = copy.deepcopy(matrix)
    matrix.update(
        schema_version=11,
        policy_revision="DEC066_D4",
        task="R1-63m/DEC-066",
        protocol=d9.ref(ROOT / PROTOCOL),
        normative_closure=closure(),
        historical_matrix=parent,
        producer=d9.ref(__file__),
        prospective_scope=copy.deepcopy(scope.CONTRACT),
        status="unsigned_D4_costs_and_admissions_pending",
        execution_identity="D.4 prospective retained coordinates; no historical execution relabelled",
    )
    matrix["axes"]["core_conditions_by_dataset"] = copy.deepcopy(
        scope.CONTRACT["core_conditions_by_dataset"]
    )
    matrix["cells"] = [
        c
        for c in matrix["cells"]
        if c["dataset"] != "mquake" or c["condition"] in scope.MQUAKE_CORE
    ]
    matrix["prospectively_omitted_cells"] = [
        dict(
            cell_id=c["cell_id"],
            condition=c["condition"],
            dataset=c["dataset"],
            realization=c["realization"],
            order=c["order"],
            decision="DEC-066",
            status="not_run_calibration_determined",
            measured_result=None,
        )
        for c in original["cells"]
        if c["dataset"] == "mquake" and c["condition"] in scope.OMITTED
    ]
    counts = Counter()
    for cell in matrix["cells"] + matrix["extension"]["cells"]:
        counts[cell["block_number"]] += 1
        previous = cell["expected_definition_sha256"]
        cell.update(
            previous_D3_definition_sha256=previous,
            within_block_order=counts[cell["block_number"]],
            expected_definition_sha256=d9.core.content_digest(
                dict(
                    previous_D3_definition_sha256=previous,
                    scope=scope.CONTRACT,
                    within_block_order=counts[cell["block_number"]],
                )
            ),
        )
        assert not cell["admitted"] and not cell["launch_allowed"] and cell["population"] is None
    matrix["queue"]["block_sizes"] = [counts[i] for i in range(1, 7)]
    matrix["budget"].update(core_cells=285, extension_cells=45, total_cells=330)
    row = next(
        r
        for r in (ROOT / "docs/decisions.md").read_text().splitlines()
        if r.startswith("| DEC-066 |")
    )
    matrix["accepted_decisions"]["DEC-066"] = dict(
        row=row, sha256=hashlib.sha256(row.encode()).hexdigest()
    )
    for name in (*matrix["analysis_implementation"], "r1_49n_scope"):
        matrix["analysis_implementation"][name] = d9.ref(ROOT / f"scripts/{name}.py")
    d9.check_matrix_layout(matrix)
    fidelity.validate_matrix(matrix, matrix["cells"] + matrix["extension"]["cells"])
    assert len(matrix["cells"]) == 285 and len(matrix["prospectively_omitted_cells"]) == 75
    assert matrix["multiplicity"] == original["multiplicity"]
    assert matrix["dataset_layouts"] == original["dataset_layouts"]
    return matrix


if __name__ == "__main__":
    print(
        json.dumps(
            write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json", document()), indent=2
        )
    )
