"""DEC-066 changes execution counts, never the inferential family or observations."""

import copy

import pytest
from scripts import r1_49g_analyze as analysis
from scripts import r1_49g_inference as inference
from scripts import r1_49n_protocol_matrix as producer


def test_reduced_execution_still_declares_63_intervals():
    matrix = producer.document()
    result = analysis.analyze(matrix)
    assert len(result["cells"]) == 330
    assert result["primary_family"]["family_size"] == 63
    assert len(result["contrasts"]) == 21
    assert sum(r["interval_count"] for r in result["contrasts"]) == 63
    mq = [r for r in result["contrasts"] if r["dataset"] == "mquake"]
    assert len(mq) == 7
    assert all(r["classification"] == "unavailable" for r in mq)
    assert len(result["prospectively_omitted_cells"]) == 75
    assert all(r["measured_result"] is None for r in result["prospectively_omitted_cells"])


@pytest.mark.parametrize("fault", ["family", "extra_omission", "undecided_subset"])
def test_missing_scope_or_family_cannot_gain_admission(fault):
    matrix = copy.deepcopy(producer.document())
    if fault == "family":
        matrix["multiplicity"]["family_size"] = 42
    elif fault == "extra_omission":
        matrix["cells"].pop()
    else:
        matrix.pop("prospective_scope")
    with pytest.raises(ValueError):
        inference.validate_family(matrix)
