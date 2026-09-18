"""D.1 metadata amendment; preserve all scientific cell coordinates and definitions."""

from __future__ import annotations

import json

from scripts import r1_d9_receipts as d9
from scripts.r1_49j_normative_closure import PROTOCOL, closure
from scripts.r1_d9f_allocation import CONTRACT
from scripts.r1_d10a_review import ROOT, write_new


def build():
    parent = d9.ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_DEC061.json")
    matrix = d9.read_metadata(parent)
    before = d9.core.content_digest([matrix["cells"], matrix["extension"]["cells"]])
    row = next(
        r
        for r in (ROOT / "docs/decisions.md").read_text().splitlines()
        if r.startswith("| DEC-062 |")
    )
    matrix.update(
        schema_version=8,
        policy_revision="DEC062_D1",
        task="R1-49j",
        protocol=d9.ref(ROOT / PROTOCOL),
        normative_closure=closure(),
        near_allocation="family_coordinated",
        near_allocation_contract=CONTRACT,
        historical_matrix=parent,
        producer=d9.ref(__file__),
        status="amended_unsigned_full_scope_cost_evidence_and_population_pending",
    )
    matrix["accepted_decisions"]["DEC-062"] = {
        "row": row,
        "sha256": __import__("hashlib").sha256(row.encode()).hexdigest(),
        "clarification": d9.ref(ROOT / "docs/tasks/DEC-062-pair-unit-clarification.md"),
    }
    assert before == d9.core.content_digest([matrix["cells"], matrix["extension"]["cells"]])
    d9.check_matrix_layout(matrix)
    return write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_1.json", matrix)


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
