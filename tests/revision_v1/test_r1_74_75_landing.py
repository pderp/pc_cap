"""Regression coverage of the approved installed scoring and inventory fixes."""

from __future__ import annotations

import json

import pytest
from scripts.r1_75_development_matrix import ROOT, build

from pccap.revision_v1 import stage4_assays
from tests.revision_v1 import test_r1_74_scoring as cases


@pytest.fixture(autouse=True)
def installed_scoring(monkeypatch):
    """Run the existing behavior cases against installed code, not the preview."""
    monkeypatch.setattr(cases, "proposed", lambda: stage4_assays)


test_both_conventions_and_side_flags = cases.test_both_conventions_and_side_flags
test_actual_tiny_locality_preserves_identical_truncated_text = (
    cases.test_actual_tiny_locality_preserves_identical_truncated_text
)
test_near_miss_both_conventions_with_actual_endpoint_pipeline = (
    cases.test_near_miss_both_conventions_with_actual_endpoint_pipeline
)
test_missing_endpoint_is_not_zero_failure_or_perfect_preservation = (
    cases.test_missing_endpoint_is_not_zero_failure_or_perfect_preservation
)
test_unavailable_near_miss_still_carries_null_flags = (
    cases.test_unavailable_near_miss_still_carries_null_flags
)
test_rescoring_does_not_mutate_the_input = cases.test_rescoring_does_not_mutate_the_input


def test_corrected_inventory_builder_reproduces_independently_saved_matrix():
    expected = json.loads((ROOT / "docs/tasks/R1-75-development.matrix.json").read_text())
    recipes = {
        "zsre": ROOT / "docs/tasks/R1-68b-zsre-v5-full.recipe.json",
        "counterfact": ROOT / "docs/tasks/R1-64-counterfact-v5.recipe.json",
    }
    actual = build([(recipes[c["dataset"]], c["result_dir"]) for c in expected["cells"]])
    assert actual == expected
