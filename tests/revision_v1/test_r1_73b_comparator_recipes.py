import copy
from pathlib import Path

import pytest
from scripts import r1_73b_comparator_recipes as recipes


@pytest.fixture(scope="module")
def manifests():
    payload, bindings = recipes.make_payload()
    from tempfile import mkdtemp

    resource = Path(mkdtemp(prefix="r173b-preflight-", dir=recipes.driver.PAYLOAD_ROOT))
    binding = recipes.driver.write_json(resource / "payload.json", payload)
    cal = recipes.ROOT / "manifests/revision_v1/calibration_v3.json"
    return payload, [
        recipes.build(
            recipes.ROOT / f"docs/tasks/R1-64d/R1-64d-zsre-{c}.recipe.json", cal, binding, bindings
        )
        for c in recipes.CONDITIONS
    ]


def test_complete_eight_distinct_identities_and_exposure(manifests):
    payload, rows = manifests
    assert len(rows) == 8
    assert {m["cell"]["condition"] for m in rows} == set(recipes.CONDITIONS)
    assert payload["development_summary"]["challenge_shortfalls"] == {
        "near_miss": 100,
        "revision": 50,
    }
    assert len(payload["items"]) == 300
    for m in rows:
        assert m["cell"]["dataset"] == "mquake"
        assert m["construction"]["calibration"]["radii"] == {"1": 0.0, "2": 0.0, "3": 0.0}
        assert m["r1_73b"]["exact_key_note"] == recipes.EXACT_NOTE
        if m["cell"]["condition"].startswith("S1_"):
            assert m["construction"]["continued_weights"]
            assert m["construction"]["original_base"]
            assert (
                m["adapter_identity"]["base_sha256"]
                != m["adapter_identity"]["locality_base_sha256"]
            )


@pytest.mark.parametrize(
    "fault", ["drift", "dataset", "radius", "code", "cadence", "note", "producer"]
)
def test_inspection_refuses_recipe_tampering(manifests, fault):
    m = copy.deepcopy(manifests[1][0])
    if fault == "drift":
        m["drift_implementation"] = "v0_batched_v1"
    elif fault == "dataset":
        m["cell"]["dataset"] = "zsre"
    elif fault == "radius":
        m["construction"]["calibration"]["radii"]["1"] = 0.1
    elif fault == "code":
        m["code_sha256"] = "f" * 64
    elif fault == "cadence":
        m["checkpoints"] = [300]
    elif fault == "note":
        m["r1_73b"]["exact_key_note"] = ""
    elif fault == "producer":
        m["r1_73b"]["bindings"]["producer"]["sha256"] = "f" * 64
    with pytest.raises(ValueError):
        recipes.verify(m)
