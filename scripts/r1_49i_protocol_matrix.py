"""Version the adopted protocol/queue/family metadata without admitting execution."""
from __future__ import annotations

import json

from scripts.r1_77f_scheduler import CEILING_DEFINITION
from scripts.r1_d9_receipts import check_matrix_layout, read_metadata, ref
from scripts.r1_d9e_near_family import CONTRACT
from scripts.r1_d10a_review import ROOT, write_new


def build():
    parent = ref(ROOT / "manifests/revision_v1/run_matrix_v5_2_D.json")
    matrix = read_metadata(parent)
    before = [(c["cell_id"], c["expected_definition_sha256"]) for c in matrix["cells"] + matrix["extension"]["cells"]]
    matrix.update(schema_version=7, policy_revision="DEC061_R177f", name="run_matrix_v5_2_option_D",
                  task="R1-49i/R1-77f/R1-D9e", status="final_protocol_text_awaiting_costs_population_and_signatures",
                  historical_matrix=parent, producer=ref(__file__),
                  protocol=ref(ROOT / "docs/R1_stage4_protocol_v5_2_D_final.md"),
                  near_miss_family_contract=CONTRACT, queue_ceiling_contract=CEILING_DEFINITION,
                  queue_policy=ref(ROOT / "docs/R1_stage4_queue_concurrency_v2.md"),
                  context_review_admitted=True)
    for name in matrix["analysis_implementation"]:
        matrix["analysis_implementation"][name] = ref(ROOT / f"scripts/{name}.py")
    matrix["analysis_implementation"]["r1_d9e_near_family"] = ref(ROOT / "scripts/r1_d9e_near_family.py")
    matrix["classifier"]["implementation"] = ref(ROOT / "scripts/r1_49g_inference.py")
    matrix["secondary_benchmarks"]["implementation"] = ref(ROOT / "scripts/r1_49g_secondary.py")
    row = next(line for line in (ROOT / "docs/decisions.md").read_text().splitlines() if line.startswith("| DEC-061 |"))
    from hashlib import sha256

    matrix["accepted_decisions"]["DEC-061"] = dict(row=row, sha256=sha256(row.encode()).hexdigest())
    matrix["queue"].update(retry="R1-77f: one automatic retry from certified state; second failure incomplete, continue next cell without draining other worker; preserve same queue receipt root",
                           host_failure="stop new dispatch on memory/lease/host failure; charge running workers; torn state or unknown cost needs owner reconciliation",
                           maximum_workers=2, workers_2_factor=1.15,
                           ceiling_definition="wall_seconds is admitted solo ceiling = 1.5 * measured full solo process cost",
                           charged_budget="sum of process envelopes, including overlap and failures; separate from elapsed queue wall time")
    check_matrix_layout(matrix)
    assert before == [(c["cell_id"], c["expected_definition_sha256"]) for c in matrix["cells"] + matrix["extension"]["cells"]]
    assert not matrix["draw_authorized"] and not matrix["launch_allowed"]
    assert not matrix["budget"]["costs_admitted"]
    return write_new(ROOT / "manifests/revision_v1/run_matrix_v5_2_D_DEC061.json", matrix)


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
