"""Bind DEC-063 to all 405 planned cells without drawing or admitting execution."""

from __future__ import annotations

import copy
import hashlib
import json

from scripts import r1_63l_full_validation_contract as full
from scripts import r1_d9_receipts as d9
from scripts.r1_49k_normative_closure import PROTOCOL, closure
from scripts.r1_d10a_review import ROOT, write_new


def document():
    parent = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_1.json")
    matrix = d9.read_metadata(parent)
    validation = full.production_contract()
    matrix.update(
        schema_version=9,
        policy_revision="DEC063_D2",
        task="R1-49k",
        protocol=d9.ref(ROOT / PROTOCOL),
        normative_closure=closure(),
        historical_matrix=parent,
        producer=d9.ref(__file__),
        endpoint_contract_version=1,
        full_validation=validation,
        full_validation_implementation=full.ref(full.__file__),
        status="amended_unsigned_full_validation_costs_and_population_pending",
        execution_identity=(
            "D.2 definition binds the D.1 planned definition plus DEC-063; "
            "final recipe/code/population/ceilings require a successor package"
        ),
    )
    for cell in matrix["cells"] + matrix["extension"]["cells"]:
        previous = cell["expected_definition_sha256"]
        cell.update(
            previous_D1_definition_sha256=previous,
            full_validation=copy.deepcopy(validation),
            expected_definition_sha256=full.digest(
                {"previous_D1_definition_sha256": previous, "full_validation": validation}
            ),
        )
        assert cell["population"] is None
        assert not cell["admitted"] and not cell["launch_allowed"]
    row = next(
        line
        for line in (ROOT / "docs/decisions.md").read_text().splitlines()
        if line.startswith("| DEC-063 |")
    )
    matrix["accepted_decisions"]["DEC-063"] = dict(
        row=row, sha256=hashlib.sha256(row.encode()).hexdigest()
    )
    for name in (*matrix["analysis_implementation"], "r1_63l_full_validation_contract"):
        matrix["analysis_implementation"][name] = d9.ref(ROOT / f"scripts/{name}.py")
    d9.check_matrix_layout(matrix)
    assert not matrix["draw_authorized"] and not matrix["launch_allowed"]
    assert not matrix["budget"]["costs_admitted"]
    return matrix


if __name__ == "__main__":
    print(
        json.dumps(
            write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_2.json", document()), indent=2
        )
    )
