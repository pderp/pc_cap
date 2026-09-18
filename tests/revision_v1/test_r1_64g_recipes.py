"""Real development metadata rebinding, never construct a model or launch a run."""

import json
import uuid
from pathlib import Path

import pytest
from scripts import r1_64g_full_validation_recipes as recipes
from scripts import r1_68c_dev_cell as driver
from scripts import r1_68f_full_validation as full

from tests.revision_v1.r1_68f_patch_support import install


def test_four_declared_populations_preserved():
    result = recipes.plan()
    assert len(result["recipes"]) == 4
    assert result["model_constructed"] is False
    for row in result["recipes"]:
        assert row["full_validation"]["expected_positions"] == 245237
        assert row["near_miss"] == 100 and row["revision"] == 50


def test_refuse_build_before_patch_is_installed():
    if hasattr(driver, "full_validation"):
        pytest.skip("owner installed reviewed patch")
    with pytest.raises(RuntimeError, match="not been installed"):
        recipes.require_installed()


def test_proposed_four_recipe_build_preserves_all_experimental_fields(monkeypatch):
    install(monkeypatch)
    # Only substitute the disk-install precondition: execute the real rebinder,
    # source checks and payload loader using the proposed driver in this process.
    monkeypatch.setattr(recipes, "require_installed", lambda: None)
    output = full.ROOT / "docs/tasks/R1-64g-cpu-fixtures" / uuid.uuid4().hex
    result = recipes.build(output)
    assert len(result["inspections"]) == 4
    allowed = {"code_sha256", "integrity_driver_bindings", "integrity_rebind", "full_validation"}
    for row in result["inspections"]:
        current = driver.read_binding(row["recipe"])
        original = driver.read_binding(current["integrity_rebind"]["source_recipe"])
        assert {k: v for k, v in current.items() if k not in allowed} == {
            k: v for k, v in original.items() if k not in allowed
        }
        assert current["full_validation"] == full.make_spec()
        assert row["model_constructed"] is False
    assert "--execute" in (output / "ordered-runlist.md").read_text()
    assert len(json.loads((output / "inspection-receipts.json").read_text())) == 4
    for path in output.glob("*.recipe.json"):
        assert Path(path).is_relative_to(full.ROOT / "docs/tasks/R1-64g-cpu-fixtures")


def test_active_recipe_chain_uses_specialized_inspectors(monkeypatch):
    install(monkeypatch)
    monkeypatch.setattr(recipes, "require_installed", lambda: None)
    output = full.ROOT / "docs/tasks/R1-64g-cpu-fixtures" / uuid.uuid4().hex
    result = recipes.rebind_active(output)
    assert result["rebound_active_recipes"] == 29
    assert result["rebuilt_parent_recipes"] == 8
    assert len(list(output.rglob("*.recipe.json"))) == 37
    for row in result["recipes"]:
        m = driver.read_binding(row["recipe"])
        assert m["integrity_driver_bindings"] == driver.driver_bindings()
