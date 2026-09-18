"""D.4 strict prospective scope, unchanged populations and primary family."""

import copy
from collections import Counter

import pytest
from scripts import r1_49n_protocol_matrix as producer
from scripts import r1_d9_receipts as d9


def test_d4_retains_exact_coordinates_and_all_full_contracts():
    matrix = producer.document()
    old = d9.read_metadata(matrix["historical_matrix"])
    assert len(matrix["cells"]) == 285 and len(matrix["extension"]["cells"]) == 45
    assert len(matrix["prospectively_omitted_cells"]) == 75
    assert Counter(c["block_number"] for c in matrix["cells"]) == {
        1: 45,
        2: 30,
        3: 75,
        4: 75,
        5: 60,
    }
    assert matrix["multiplicity"] == old["multiplicity"]
    assert matrix["dataset_layouts"] == old["dataset_layouts"]
    assert matrix["population"] == old["population"]
    for cell in matrix["cells"] + matrix["extension"]["cells"]:
        assert cell["full_validation"] == matrix["full_validation"]
        assert cell["cap_fidelity_policy"] == matrix["cap_fidelity_policy"]
        assert not cell["admitted"] and not cell["launch_allowed"]
    assert all(c["measured_result"] is None for c in matrix["prospectively_omitted_cells"])


@pytest.mark.parametrize(
    "fault", ["extra_omission", "added_arm", "scope", "fake_revision", "missing_extension"]
)
def test_reduction_cannot_authorize_arbitrary_missing_cells(fault):
    m = producer.document()
    if fault == "extra_omission":
        m["cells"].pop()
    if fault == "added_arm":
        parent = d9.read_metadata(m["historical_matrix"])
        m["cells"].append(
            next(
                c for c in parent["cells"] if c["dataset"] == "mquake" and c["condition"] == "S1_LM"
            )
        )
    if fault == "scope":
        m["prospective_scope"]["core_conditions_by_dataset"]["zsre"].pop()
    if fault == "fake_revision":
        m["policy_revision"] = "DEC064_D3"
    if fault == "missing_extension":
        m["extension"]["cells"].pop()
    with pytest.raises(ValueError):
        d9.check_matrix_layout(m)


def test_historical_d3_remains_strict():
    m = copy.deepcopy(
        d9.read_metadata(d9.ref(producer.ROOT / "manifests/revision_v1/run_matrix_v5_2_D_3.json"))
    )
    d9.check_matrix_layout(m)
    m["cells"].pop()
    with pytest.raises(ValueError):
        d9.check_matrix_layout(m)
