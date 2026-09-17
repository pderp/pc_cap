"""Versioned protocol/matrix and additive R1-75 report integration."""

import json
from pathlib import Path

from scripts import r1_49g_analyze as analysis
from scripts.r1_49g_inference import FAMILY

ROOT = Path(__file__).resolve().parents[2]


def test_matrix_keeps_cells_and_execution_gates():
    before = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5.json").read_text())
    after = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5_1.json").read_text())
    assert after["cells"] == before["cells"]
    assert after["extension"] == before["extension"]
    assert after["multiplicity"] == FAMILY
    assert not after["draw_authorized"] and not after["launch_allowed"]
    result = analysis.analyze(after)
    assert len(result["contrasts"]) == 21
    assert all(r["classification"] == "unavailable" for r in result["contrasts"])
    assert len(result["secondary_benchmarks"]["cells"]) == 405
    assert all(r["status"] == "unavailable" for r in result["secondary_benchmarks"]["macros"])


def test_exact_accepted_insertions_and_current_development_report():
    proposal = (ROOT / "docs/tasks/R1-49f-lead-bindings.md").read_text()
    protocol = (ROOT / "docs/R1_stage4_protocol_draft_v5_1.md").read_text()
    for section in proposal.split("**Exact proposed insertion")[1:]:
        block = []
        for line in section.splitlines():
            if line.startswith("> "):
                block.append(line[2:])
            elif block:
                break
        assert "\n".join(block) in protocol
    m = json.loads((ROOT / "docs/tasks/R1-75-development.matrix.json").read_text())
    result = analysis.analyze(m)
    by = {c["cell"]["dataset"]: c["benchmarks"] for c in result["secondary_benchmarks"]["cells"]}
    assert by["counterfact"]["revision_latest"]["value"] == 1
    assert by["zsre"]["revision_latest"]["status"] == "unavailable"
    assert all(v["unseen_1000"]["status"] == "unavailable" for v in by.values())
    assert all(v["outside_change_1000_100"]["status"] == "unavailable" for v in by.values())
