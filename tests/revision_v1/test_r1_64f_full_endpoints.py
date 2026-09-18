"""Real development metadata only; no model construction or execution."""

import copy
import json

import pytest
from scripts import r1_68c_dev_cell as driver
from scripts.r1_d9e_near_family import near_key
from scripts.r1_d10a_review import ROOT
from scripts.r1_locality_contract import validate_locality


@pytest.mark.parametrize("dataset", ["zsre", "mquake"])
def test_two_arms_share_complete_source_bound_endpoints(dataset):
    payloads = []
    for condition in ["R1_learned_ff", "v0_stable"]:
        p = ROOT / f"docs/tasks/R1-64f/R1-64f-{dataset}-{condition}.recipe.json"
        m, data = driver.load_development_cell(p, driver.sha(p))
        payloads.append(data)
        assert len(data["items"]) == 300 and m["checkpoints"] == [100, 300]
        assert not any(m["admission"].values())
        assert m["r1_64f"]["development_only"] and not m["r1_64f"]["full_validation_split"]
        sources = {r["item_id"]: r for r in data["pool_rows"]}
        assert len(sources) == 650
        for k, n in [("near_miss", 100), ("revision", 50), ("locality", 50)]:
            assert (
                len(data["endpoints"][k]["rows"]) == len(data["endpoints"][k]["expected_ids"]) == n
            )
        seen = set()
        for pair in data["endpoints"]["near_miss"]["rows"]:
            a, b = sources[pair["edit_item_id"]], sources[pair["neighbour_item_id"]]
            assert a["subject"] != b["subject"] and near_key(a) == near_key(b) == pair["family_key"]
            assert a["item_id"] not in seen and b["item_id"] not in seen
            seen.update([a["item_id"], b["item_id"]])
        validate_locality(data["items"], data["endpoints"]["locality"]["rows"])
    assert payloads[0] == payloads[1]


def test_primary_mquake_is_selected_v5_and_not_ungated_control():
    p = ROOT / "docs/tasks/R1-64f/R1-64f-mquake-R1_learned_ff.recipe.json"
    m = json.loads(p.read_text())
    primary = json.loads((ROOT / "manifests/revision_v1/primary_condition_v5.json").read_text())
    assert m["construction"]["weights"]["sha256"] == primary["weights"]["sha256"]
    assert m["adapter_identity"]["condition"] == "R1_learned_ff"
    assert m["integrity_profile"] == "incremental"


def test_future_edit_collision_is_rejected():
    p = ROOT / "docs/tasks/R1-64f/R1-64f-zsre-R1_learned_ff.recipe.json"
    _, data = driver.load_development_cell(p, driver.sha(p))
    rows = copy.deepcopy(data["endpoints"]["locality"]["rows"])
    rows[0]["prompt"] = data["items"][-1]["paraphrases"][0]
    with pytest.raises(ValueError):
        validate_locality(data["items"], rows)
