import copy
import json

import numpy as np
import pytest
from scripts import r1_73b_calibration_v3 as cal


@pytest.fixture(scope="module")
def audited():
    return cal.build()


def test_preserves_all_historical_calibration(audited):
    parent = json.loads(cal.PARENT.read_text())
    restored = copy.deepcopy(audited["calibration"])
    del restored["BP"]["radii"]["mquake"]
    assert restored == parent["calibration"]
    assert audited["b_m"] == parent["b_m"]
    assert audited["confirmation_admitted"] is False
    assert audited["launch_authorized"] is False
    assert audited["development_admitted"] is True


def test_independent_saved_array_reproduction(audited):
    for row in audited["audit"].values():
        assert row["radius"] == 0
        assert row["selected_coverage_count"] == 0
        assert row["selected_coverage_denominator"] == 100
        assert row["selected_false_fire_count"] == 0
        assert row["selected_false_fire_denominator"] == 500
        assert len(row["candidates"]) == 20
        assert not any(c["admissible"] for c in row["candidates"])


@pytest.fixture(scope="module")
def inputs():
    candidate = json.loads(cal.CANDIDATE.read_text())
    specification = json.loads(cal.SPEC.read_text())
    with np.load(candidate["arrays"]["path"], allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    return candidate, specification, arrays


@pytest.mark.parametrize(
    "fault",
    [
        "radius",
        "coverage",
        "grid",
        "base",
        "admission",
        "population",
        "ownership",
        "nan",
        "dtype",
        "missing_bank",
    ],
)
def test_rejects_altered_evidence(inputs, fault):
    candidate, specification, arrays = copy.deepcopy(inputs)
    owner = arrays["owner"].copy()
    if fault == "radius":
        candidate["radii"]["mquake"]["1"] = 1.0
    elif fault == "coverage":
        candidate["per_dataset"]["mquake"]["2"]["selected_coverage_count"] = 1
    elif fault == "grid":
        candidate["per_dataset"]["mquake"]["3"]["candidates"][0]["admissible"] = True
    elif fault == "base":
        candidate["base_tensor_sha256"] = "bad"
    elif fault == "admission":
        candidate["calibration_admitted"] = True
    elif fault == "population":
        specification["population"]["outside_count"] = 499
    elif fault == "ownership":
        arrays["owner"][0] = 101
    elif fault == "nan":
        arrays["edit_1"][0, 0] = np.nan
    elif fault == "dtype":
        arrays["edit_2"] = arrays["edit_2"].astype(np.float64)
    elif fault == "missing_bank":
        del arrays["outside_3"]
    with pytest.raises(ValueError):
        cal.validate_candidate(
            candidate,
            specification,
            arrays,
            dimension=768,
            expected_owner=owner,
            expected_base_hash=inputs[0]["base_tensor_sha256"],
        )
