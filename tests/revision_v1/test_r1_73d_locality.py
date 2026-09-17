"""Whole-stream locality exclusions, exact development deltas, and final seal refusals."""

import copy
import json
from pathlib import Path

import pytest
from scripts import r1_73d_locality_recipes as recipes
from scripts import r1_d9_receipt_core as core
from scripts.r1_locality_contract import select_unrelated, validate_locality

from tests.revision_v1.test_r1_d9_receipts import COUNTS
from tests.revision_v1.test_r1_d10c_endpoints import build, setup


def test_future_edit_and_paraphrase_excluded_before_any_occupancy():
    items = [
        {"prompt": "first", "paraphrases": ["first para"]},
        {"prompt": "later", "paraphrases": ["later para"]},
    ]
    selected, audit = select_unrelated(items, ["later", "later para", "safe", "safe", "other"], 2)
    assert [r["prompt"] for r in selected] == ["safe", "other"]
    assert audit["selected_source_indices"] == [2, 4]
    assert audit["excluded_overlap_indices"] == [0, 1]
    for prompt in ("first", "first para", "later", "later para"):
        with pytest.raises(ValueError, match="reserved edit/paraphrase"):
            validate_locality(items, [{"prompt": prompt}])
    with pytest.raises(ValueError, match="shortfall"):
        select_unrelated(items, ["first", "first para", "safe"], 2)


@pytest.mark.parametrize("prompt_role", ["prompt", "paraphrase"])
def test_constructor_and_seal_refuse_reserved_prompt(prompt_role):
    r, cells, catalog, plan, drift = setup()
    payloads, population, _ = build(r, cells, catalog, plan, drift)
    cell = cells[0]
    cid = core.coordinate_id(cell)
    data = payloads[cid]
    own = data["items"][-1]
    prompt = own["prompt"] if prompt_role == "prompt" else own["paraphrases"][0]
    data["endpoints"]["locality"]["rows"][0]["prompt"] = prompt
    with pytest.raises(ValueError, match="locality overlaps"):
        core.validate_seal(
            r,
            cells,
            payloads,
            population,
            counts=COUNTS,
            realizations=2,
            checkpoints=(1, 2),
            locality_count=1,
        )
    outside = next(
        g
        for g in r["allocations"]
        if g["dataset"] == cell["dataset"]
        and g["realization"] == cell["realization"]
        and g["role"] == "outside"
    )
    row = outside["records"][0]
    row["locality_prompts"] = [prompt]
    outside["items"][0]["payload_sha256"] = core.content_digest(row)
    next(p for p in plan["rows"] if p["item_id"] == row["item_id"])["payload_sha256"] = (
        core.content_digest(row)
    )
    with pytest.raises(ValueError, match="locality overlaps"):
        build(r, cells, catalog, plan, drift)


def test_actual_rebuilt_recipes_preserve_every_nonlocality_setting():
    root = Path(__file__).resolve().parents[2]
    receipts = json.loads((root / "docs/tasks/R1-73d/inspection-receipts.json").read_text())
    assert len(receipts) == 8
    for receipt in receipts:
        binding = receipt["recipe"]
        m, payload = recipes.driver.load_development_cell(binding["path"], binding["sha256"])
        recipes.verify(m, payload)
        assert len(payload["items"]) == 300
        assert len(payload["endpoints"]["locality"]["rows"]) == 50
        assert receipt["locality_overlap_count"] == 0 and not receipt["model_constructed"]
    bad = copy.deepcopy(payload)
    bad["items"][0]["answer"] = "unapproved other change"
    with pytest.raises(ValueError, match="only the deterministic locality"):
        recipes.verify(m, bad)
    bad_recipe = copy.deepcopy(m)
    bad_recipe["r1_73d"]["selection_audit"]["eligible_unique"] += 1
    with pytest.raises(ValueError, match="selection audit"):
        recipes.verify(bad_recipe, payload)
