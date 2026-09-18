"""Normative parents cannot disappear or drift while the top-level text stays fixed."""

import copy

import pytest
from scripts import r1_49j_normative_closure as norm


@pytest.fixture
def workspace(tmp_path):
    for name in norm.GRAPH:
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((norm.ROOT / name).read_bytes())
    return tmp_path


def candidate(root):
    closed = norm.closure(root)
    return {
        "normative_closure": closed,
        "bindings_sha256": copy.deepcopy(closed["bindings_sha256"]),
    }


def test_recursive_parents_and_missing_binding(workspace):
    c = candidate(workspace)
    assert norm.verify(c, workspace)["normative_files"] == 6
    del c["bindings_sha256"][str(workspace / "docs/R1_stage4_protocol_draft_v5_1.md")]
    with pytest.raises(ValueError, match="normative file"):
        norm.verify(c, workspace)


@pytest.mark.parametrize("name", list(norm.GRAPH))
def test_every_normative_file_is_tamper_evident(workspace, name):
    c = candidate(workspace)
    p = workspace / name
    p.write_bytes(p.read_bytes() + b"\nchanged")
    with pytest.raises(ValueError, match="closure differs"):
        norm.verify(c, workspace)


def test_new_incorporation_cannot_be_silently_omitted(workspace):
    p = workspace / norm.PROTOCOL
    p.write_text(p.read_text() + "\n\nAdditional rules are incorporated from [new](new.md).\n")
    with pytest.raises(ValueError, match="undeclared incorporated"):
        norm.closure(workspace)


def test_amendment_retains_denominator_and_removes_independent_only_prohibition():
    text = (norm.ROOT / norm.PROTOCOL).read_text()
    assert "No family-coordinated\nallocation" not in text
    assert "Several pairs may share a family" in text
    assert "100 pair slots" in text
    assert "October 9" in text and "63 intervals" in text
