"""Condition-specific integrity selection and preserved S1 construction."""

import copy
import json
from pathlib import Path

import pytest
from scripts import r1_64c_comparator_recipes as c


@pytest.mark.parametrize("condition", c.previous.CONDITIONS)
def test_profile_matches_actual_adapter_contract(condition):
    expected = "incremental" if condition in ("R1_nonlearned", "R1_learned_ff_v2") else "full"
    assert c.profile_for(condition) == expected


def test_unknown_condition_refused():
    with pytest.raises(ValueError):
        c.profile_for("invented")


@pytest.mark.parametrize("condition", ("S1_literal", "S1_LM"))
def test_s1_uses_verified_npz_constructor(condition, monkeypatch):
    manifest = {"cell": {"condition": condition}}
    monkeypatch.setattr(c, "verify", lambda m: "full")
    monkeypatch.setattr(c.previous, "construct", lambda m: ("continued", m))
    assert c.construct(manifest) == ("continued", manifest)


def test_wrong_class_never_enters_incremental():
    manifest = {
        "cell": {"condition": "R1_nonlearned"},
        "integrity_profile": "incremental",
        "adapter_identity": {"class": "pccap.cap.cap.Cap"},
    }
    with pytest.raises(ValueError, match="exact RevisionCap"):
        c.verify(manifest)


def test_generated_recipes_preserve_population_parameters_and_base():
    for path in sorted((c.ROOT / "docs/tasks").glob("R1-64c-*.recipe.json")):
        m = json.loads(path.read_text())
        old = json.loads(Path(m["r1_64c"]["bindings"]["source_recipe"]["path"]).read_text())
        assert m["code_sha256"] == c.driver.code_identity()
        for field in ("payload", "adapter_identity", "construction", "cell", "checkpoints"):
            assert m[field] == old[field]
        original = copy.deepcopy(m)
        c.verify(m)
        assert m == original
