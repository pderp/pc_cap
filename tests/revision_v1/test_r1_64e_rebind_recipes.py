"""Current identity rebuilds preserve experiments and retain all runtime fences."""

import copy
import json

import pytest
from scripts import r1_64e_rebind_recipes as build


def test_all_postpatch_recipes_and_exact_comparator_delta():
    report = json.loads((build.ROOT / "logs/r1_round25/r1-64e-build.json").read_text())
    assert len(report["comparator_recipes"]) == 16
    assert len(report["mquake_recipes"]) == 8
    for row in [*report["comparator_recipes"], report["primary"], *report["mquake_recipes"]]:
        b = row["recipe"]
        value, payload = build.driver.load_development_cell(b["path"], b["sha256"])
        assert value["code_sha256"] == report["installed_driver_code_sha256"]
        assert value["code_sha256"] != report["old_driver_code_sha256"]
        if value["cell"]["dataset"] == "mquake":
            build.locality.verify(value, payload)
            assert row["locality_overlap_count"] == 0
        else:
            source = build.driver.read_binding(value["integrity_rebind"]["source_recipe"])
            excluded = {"code_sha256", "integrity_driver_bindings", "integrity_rebind"}
            assert {k: v for k, v in value.items() if k not in excluded} == {
                k: v for k, v in source.items() if k not in excluded}


@pytest.mark.parametrize("fault", ["code", "driver", "payload", "setting", "audit"])
def test_current_locality_verifier_rejects_tampering(fault):
    path = build.ROOT / "docs/tasks/R1-73d-post77d/R1-73d-mquake-v0_stable.recipe.json"
    m, payload = build.driver.load_development_cell(path, build.driver.sha(path))
    m, payload = copy.deepcopy(m), copy.deepcopy(payload)
    if fault == "code":
        m["code_sha256"] = "0" * 64
    elif fault == "driver":
        m["integrity_driver_bindings"]["scripts/r1_68c_dev_cell.py"] = "0" * 64
    elif fault == "payload":
        payload["items"][0]["answer"] = "changed"
    elif fault == "setting":
        m["drift_batch_size"] = 8
    else:
        m["r1_73d"]["selection_audit"]["eligible_unique"] += 1
    with pytest.raises(ValueError):
        build.locality.verify(m, payload)


def test_old_recipe_remains_refused_on_current_tree():
    path = build.ROOT / "docs/tasks/R1-73d/R1-73d-mquake-v0_stable.recipe.json"
    with pytest.raises(ValueError, match="code identity"):
        build.driver.load_development_cell(path, build.driver.sha(path))
