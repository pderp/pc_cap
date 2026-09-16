"""R1-73 calibration parity and failure reporting, CPU arrays only."""

import copy

import numpy as np
import pytest
from scripts.r1_73_mquake_calibration import from_keys, populations

from pccap.cap.calibrate import calibrate_radii


def test_radius_grid_and_choice_match_v0_exactly():
    rng = np.random.default_rng(173)
    edit = {k: rng.normal(size=(4, 6)).astype(np.float32) for k in (1, 2, 3)}
    owner = np.array([0, 0, 1, 2, 3])
    para = {
        k: edit[k][owner] + 0.01 * rng.normal(size=(5, 6)).astype(np.float32) for k in (1, 2, 3)
    }
    outside = {k: rng.normal(size=(500, 6)).astype(np.float32) + 2 for k in (1, 2, 3)}
    expected = calibrate_radii(edit, para, owner, outside)
    result = from_keys(edit, para, owner, outside)
    for bank, old in expected.items():
        assert all(result[bank][k] == v for k, v in old.items())
        assert result[bank]["selected_false_fire_count"] <= 5
        assert result[bank]["selected_false_fire_denominator"] == 500


def test_exact_key_fallback_can_fail_the_criterion():
    edit = {k: np.array([[1.0, 0.0]], np.float32) for k in (1, 2, 3)}
    result = from_keys(edit, edit, np.array([0]), edit)
    for r in result.values():
        assert r["radius"] == 0 and r["exact_key_fallback"]
        assert r["selected_false_fire_count"] == r["selected_false_fire_denominator"] == 1
        assert r["selected_meets_empirical_bound"] is False


@pytest.mark.parametrize("fault", ["nonfinite", "bad_owner", "missing_bank"])
def test_incomplete_or_invalid_populations_refused(fault):
    edit = {k: np.ones((2, 3), np.float32) for k in (1, 2, 3)}
    para = copy.deepcopy(edit)
    outside = copy.deepcopy(edit)
    owner = np.array([0, 1])
    if fault == "nonfinite":
        outside[2][0, 0] = np.nan
    elif fault == "bad_owner":
        owner[1] = 2
    else:
        del para[3]
    with pytest.raises(ValueError):
        from_keys(edit, para, owner, outside)


def test_outside_source_and_subject_separation_are_checked():
    items = [
        {
            "item_id": f"e{i}",
            "subject": f"Edit {i}",
            "prompt": f"edit{i}",
            "paraphrases": [f"para{i}"],
        }
        for i in range(100)
    ]
    train = {
        "items": [
            {"item_id": f"t{i}", "subject": f"Train {i}", "prompt": f"outside{i}"}
            for i in range(500)
        ]
    }
    dev = {"items": items, "unrelated_prompts": [r["prompt"] for r in train["items"]]}
    assert tuple(map(len, populations(dev, train))) == (100, 100, 100, 500)
    bad = copy.deepcopy(train)
    bad["items"][0]["subject"] = " EDIT  0 "
    with pytest.raises(ValueError, match="subject"):
        populations(dev, bad)
    bad = copy.deepcopy(dev)
    bad["unrelated_prompts"].reverse()
    with pytest.raises(ValueError, match="exactly"):
        populations(bad, train)
