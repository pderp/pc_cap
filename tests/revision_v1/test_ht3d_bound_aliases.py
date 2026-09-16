"""Explicit source aliases cannot turn a different experiment into ordinary seed2."""

import copy
import json

import pytest
from scripts import ht3d_bound_aliases as a


def entries():
    return json.loads(a.ALIASES.read_text())["aliases"]


def test_actual_aliases_match_checkpoint_and_exact_populations():
    for entry in entries():
        inputs = a.core.Inputs(a.ROOT)
        result = a.verify_alias(inputs, entry)
        assert result["summary"]["false_fires"] == 0
        assert inputs.unchanged() == []


@pytest.mark.parametrize("change", ["hash", "checkpoint", "population", "seed"])
def test_mismatched_alias_refused(change):
    entry = copy.deepcopy(entries()[0])
    if change == "hash":
        entry["observed_sha256"] = "0" * 64
    elif change == "checkpoint":
        entry["theta"]["sha256"] = "0" * 64
    elif change == "population":
        entry["population_reference"] = entries()[1]["population_reference"]
    else:
        entry["seed"] = 0
    with pytest.raises(ValueError):
        a.verify_alias(a.core.Inputs(a.ROOT), entry)


def test_aliases_are_visible_and_framing_preserved():
    report = a.aggregate()
    assert len(report["rows"]) == 36
    assert report["framing"] in a.markdown(report)
    assert all(e["observed_sha256"] in a.markdown(report) for e in report["legacy_name_aliases"])
    assert all(
        report["arms"]["ordinary"]["unseen_by_dataset"][d] is not None for d in a.core.DATASETS
    )
