"""Population changes preserve block coordinates, inference family and refusals."""

import json
from pathlib import Path

import pytest
from scripts.r1_d10d_options import build_matrix, capacity, layouts, protocol

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "option,counts,blocks,removed,recadenced,demand",
    [
        ("A", (360, 45), [45, 45, 90, 90, 90, 45], 0, 135, 1950),
        ("B", (280, 35), [45, 45, 60, 60, 70, 35], 90, 0, 1350),
        ("C", (240, 30), [30, 30, 60, 60, 60, 30], 135, 0, 0),
        ("D", (360, 45), [45, 45, 90, 90, 90, 45], 0, 135, 1950),
    ],
)
def test_exact_layout_and_complete_delta(option, counts, blocks, removed, recadenced, demand):
    parent = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5_1.json").read_text())
    matrix, delta = build_matrix(parent, option)
    assert (len(matrix["cells"]), len(matrix["extension"]["cells"])) == counts
    assert matrix["queue"]["block_sizes"] == blocks
    assert len(delta["removed"]) == removed
    assert len(delta["recadenced"]) == recadenced
    assert matrix["population"]["required_subjects_by_dataset"].get("mquake", 0) == demand
    assert sum(len(rows) for rows in delta.values()) == 405
    assert matrix["multiplicity"] == parent["multiplicity"]
    assert matrix["multiplicity"]["family_size"] == 63
    old = {c["cell_id"]: c for c in parent["cells"] + parent["extension"]["cells"]}
    for cell in matrix["cells"] + matrix["extension"]["cells"]:
        p = old[cell["cell_id"]]
        assert [
            cell[k] for k in ("dataset", "condition", "realization", "order", "block_number")
        ] == [p[k] for k in ("dataset", "condition", "realization", "order", "block_number")]
        assert not cell["admitted"] and not cell["launch_allowed"]
        assert cell["recipe_template"] is None
        assert cell["expected_definition_sha256"] != p["expected_definition_sha256"]
        if cell["dataset"] != "mquake":
            assert cell["checkpoints"] == [100, 300, 1000]
    for block in range(1, 7):
        slots = [
            c["within_block_order"]
            for c in matrix["cells"] + matrix["extension"]["cells"]
            if c["block_number"] == block
        ]
        assert slots == list(range(1, blocks[block - 1] + 1))


def test_demand_is_per_role_and_realization():
    d = layouts("D")
    assert d["mquake"]["demand_by_role"] == dict(
        edits=900, outside=300, near_miss_support=300, near_miss_neighbour=300, revision=150
    )
    assert d["zsre"]["demand_subjects"] == 4050
    for bad in ("", "AB", "E", "a"):
        with pytest.raises(ValueError):
            layouts(bad)


def test_capacity_counts_entities_not_rows_and_never_certifies_clearance():
    evidence = {
        "dispositions": [dict(dataset="mquake", entity_id="same", preteacher_eligible=True)] * 2
    }
    c = capacity(evidence, layouts("A"))
    assert c["mquake"]["preteacher_items"] == 2
    assert c["mquake"]["preteacher_subjects"] == 1
    assert c["mquake"]["margin"] == -1949
    assert not c["mquake"]["teacher_and_joint_role_capacity_certified"]


def test_protocol_keeps_absence_and_historical_precedence_explicit():
    parent = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5_1.json").read_text())
    matrix, _ = build_matrix(parent, "D")
    c = capacity({"dispositions": []}, layouts("D"))
    text = protocol("historical source", "D", matrix, c)
    for required in (
        "DEC-060",
        "**U08:**",
        "**U14 / DEC-059:**",
        "63-interval",
        "October 9",
        "historical source",
        "versioned D9",
    ):
        assert required in text
