"""D.2 closes the normative graph and adds no launch authority or primary claims."""

import copy

import pytest
from scripts import r1_49k_normative_closure as norm
from scripts import r1_49k_protocol_matrix as producer
from scripts import r1_75_analysis_stage4_v1 as analysis


@pytest.fixture
def workspace(tmp_path):
    for name in (*norm.prior.GRAPH, norm.PROTOCOL):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((norm.ROOT / name).read_bytes())
    return tmp_path


def test_seven_bound_normative_files_and_no_new_incorporation(workspace):
    closed = norm.closure(workspace)
    c = dict(normative_closure=closed, bindings_sha256=copy.deepcopy(closed["bindings_sha256"]))
    assert norm.verify(c, workspace)["normative_files"] == 7
    del c["bindings_sha256"][str(workspace / norm.PROTOCOL)]
    with pytest.raises(ValueError, match="normative file"):
        norm.verify(c, workspace)
    p = workspace / norm.PROTOCOL
    p.write_text(p.read_text() + "\n\nAdditional rules incorporate [other](other.md).\n")
    with pytest.raises(ValueError, match="undeclared D.2"):
        norm.closure(workspace)


@pytest.mark.parametrize("name", [*norm.prior.GRAPH, norm.PROTOCOL])
def test_every_normative_parent_is_bound(workspace, name):
    closed = norm.closure(workspace)
    c = dict(normative_closure=closed, bindings_sha256=copy.deepcopy(closed["bindings_sha256"]))
    p = workspace / name
    p.write_bytes(p.read_bytes() + b"\nchanged")
    with pytest.raises(ValueError, match="closure differs"):
        norm.verify(c, workspace)


def test_405_definitions_change_only_for_endpoint_and_keep_all_gates_closed():
    m = producer.document()
    old = producer.d9.read_metadata(m["historical_matrix"])
    assert len(m["cells"]) == 360 and len(m["extension"]["cells"]) == 45
    for key in ("multiplicity", "classifier", "contrasts", "budget", "axes", "dataset_layouts"):
        assert m[key] == old[key]
    for c, previous in zip(
        m["cells"] + m["extension"]["cells"], old["cells"] + old["extension"]["cells"], strict=True
    ):
        assert c["full_validation"] == m["full_validation"]
        assert c["previous_D1_definition_sha256"] == previous["expected_definition_sha256"]
        assert c["expected_definition_sha256"] != previous["expected_definition_sha256"]
        retained = {
            k: v
            for k, v in c.items()
            if k
            not in (
                "expected_definition_sha256",
                "previous_D1_definition_sha256",
                "full_validation",
            )
        }
        assert retained == {k: v for k, v in previous.items() if k != "expected_definition_sha256"}
    analysis.validate_matrix(m)
    # An admitted cell cannot use the draft's absent independent population.
    m["cells"][0]["admitted"] = True
    with pytest.raises(ValueError, match="frozen population"):
        analysis.validate_matrix(m)
