"""Development inventory is reconstructed from declared sources, not results."""

from scripts.r1_57b_stage4_inventory import build_development

from pccap.revision_v1.analysis import validate_inventory


def test_three_dataset_development_inventory_keeps_missing_conditions():
    inv = build_development()
    populations, cells = validate_inventory(inv)
    assert inv["axes"]["datasets"] == ["zsre", "counterfact", "mquake"]
    assert len(cells) == 15 and len(populations) == 3
    assert all(len(p["item_ids"]) == 100 for p in populations.values())
    assert len(inv["axes"]["realizations"]) == 1
    assert len(inv["axes"]["orders"]) == 1
    assert cells[("mquake", "text_null_v2", "dev21", "source_order")]["stream_dir"] is None
    assert inv["contrasts"][0]["id"] == "rare_gate_minus_no_gate"
    assert "unbound" in inv["composition_status"]
