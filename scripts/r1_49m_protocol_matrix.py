"""Publish the DEC-064 D.3 planned definition, without drawing or admitting cells."""

from __future__ import annotations

import copy
import hashlib
import json

from scripts import r1_49m_fidelity_policy as policy
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_d9_receipts as d9
from scripts.r1_49m_normative_closure import PROTOCOL, closure
from scripts.r1_d10a_review import ROOT, write_new


def document():
    parent = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_2.json")
    matrix = d9.read_metadata(parent)
    matrix.update(
        schema_version=10,
        policy_revision="DEC064_D3",
        task="R1-49m",
        protocol=d9.ref(ROOT / PROTOCOL),
        normative_closure=closure(),
        historical_matrix=parent,
        producer=d9.ref(__file__),
        cap_fidelity_policy=copy.deepcopy(policy.POLICY),
        status="amended_unsigned_costs_backend_and_population_pending",
        execution_identity="D.3 binds DEC-064; final recipe/code/population/ceilings require successor candidate v14",
    )
    cells = matrix["cells"] + matrix["extension"]["cells"]
    for cell in cells:
        previous = cell["expected_definition_sha256"]
        cell.update(
            previous_D2_definition_sha256=previous,
            cap_fidelity_policy=copy.deepcopy(policy.POLICY),
            expected_definition_sha256=full.digest(
                dict(previous_D2_definition_sha256=previous, cap_fidelity_policy=policy.POLICY)
            ),
        )
        assert cell["population"] is None and not cell["admitted"] and not cell["launch_allowed"]
    row = next(
        line
        for line in (ROOT / "docs/decisions.md").read_text().splitlines()
        if line.startswith("| DEC-064 |")
    )
    matrix["accepted_decisions"]["DEC-064"] = dict(
        row=row, sha256=hashlib.sha256(row.encode()).hexdigest()
    )
    for name in (*matrix["analysis_implementation"], "r1_49m_fidelity_policy", "ht7_concentration"):
        matrix["analysis_implementation"][name] = d9.ref(ROOT / f"scripts/{name}.py")
    policy.validate_matrix(matrix, cells)
    d9.check_matrix_layout(matrix)
    assert (
        not matrix["draw_authorized"]
        and not matrix["launch_allowed"]
        and not matrix["budget"]["costs_admitted"]
    )
    return matrix


if __name__ == "__main__":
    print(
        json.dumps(
            write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_3.json", document()), indent=2
        )
    )
