"""D.11 controls with synthetic observations, never confirmation data."""

import copy
import json

import numpy as np
import pytest

from pccap.analysis.bootstrap import cluster_bootstrap
from pccap.analysis.paired import analyze_paired, main


def rows(benefits=(0.1, 0.1, 0.1), es=(0, 0, 0), ls=(0, 0, 0), items=2):
    return [
        dict(
            arm=arm,
            realization=r,
            order=o,
            item_id=f"item-{i}",
            ret_gs=0.5 + (benefits[r] if arm == "C2" else 0),
            es=0.5 + (es[r] if arm == "C2" else 0),
            ls=0.5 + (ls[r] if arm == "C2" else 0),
        )
        for arm in ("C2", "C1", "CR")
        for r in range(3)
        for o in range(5)
        for i in range(items)
    ]


def test_constant_effect_has_known_interval_and_positive_claim():
    result = analyze_paired(rows())
    assert result["classification"] == "positive" and result["primary_claim_supported"]
    for c in result["contrasts"].values():
        assert len(c["paired_table"]) == 15
        assert all(c["checks"].values())
        effect = c["measures"]["ret_gs"]
        assert effect["estimate"]["value"] == pytest.approx(0.1)
        assert effect["interval"]["lower"] == pytest.approx(0.1)
        assert effect["interval"]["upper"] == pytest.approx(0.1)
        assert effect["draws"] == 10_000 and effect["interval"]["confidence"] == 0.975
        assert effect["estimate"]["n"] == 3  # not 15 orders or 30 item observations
    assert result["comparable_compute_claim"].startswith("not_assessed")
    json.dumps(result, allow_nan=False)


def test_all_orders_travel_with_realization_not_individual_resampling():
    differences = np.tile([-0.4, -0.2, 0, 0.2, 0.4], (3, 1))
    result = cluster_bootstrap(differences)
    assert result["interval"]["lower"] == pytest.approx(0, abs=1e-16)
    assert result["interval"]["upper"] == pytest.approx(0, abs=1e-16)
    assert result["orders_kept_together"]
    assert result["order_min"] == [-0.4] * 3
    assert result["order_max"] == [0.4] * 3
    shifted = cluster_bootstrap(np.repeat([[0], [1], [2]], 5, axis=1))
    assert shifted["interval"]["lower"] == 0
    assert shifted["interval"]["upper"] == 2
    assert shifted["estimate"]["value"] == 1


@pytest.mark.parametrize(
    "benefit,es,ls,expected",
    [
        ((0, 0, 0), (0, 0, 0), (0, 0, 0), "negative"),
        ((0.01, 0.01, 0.01), (0, 0, 0), (0, 0, 0), "negative"),
        ((-0.1, -0.1, -0.1), (0, 0, 0), (0, 0, 0), "negative"),
        ((-0.2, 0.1, 0.3), (0, 0, 0), (0, 0, 0), "inconclusive"),
        ((0.1, 0.1, 0.1), (-0.04, 0.02, 0.02), (0, 0, 0), "qualified"),
        ((0.1, 0.1, 0.1), (0, 0, 0), (-0.02, 0.01, 0.01), "qualified"),
        ((0.1, 0.1, 0.1), (-0.1, -0.1, -0.1), (0, 0, 0), "negative"),
        ((0.1, 0.1, 0.1), (0, 0, 0), (-0.1, -0.1, -0.1), "negative"),
    ],
)
def test_primary_classification_with_all_constraints(benefit, es, ls, expected):
    result = analyze_paired(rows(benefit, es, ls))
    assert result["classification"] == expected
    assert not result["primary_claim_supported"]
    assert set(result["contrasts"]["C2-C1"]["checks"]) == {
        "ret_gs_practical_gain",
        "ret_gs_lower_above_zero",
        "es_noninferiority",
        "ls_noninferiority",
    }


def test_both_controls_required_for_positive_claim():
    table = rows()
    for r in table:
        if r["arm"] == "CR":
            r["ret_gs"] = 0.6
    result = analyze_paired(table)
    assert result["contrasts"]["C2-C1"]["classification"] == "positive"
    assert result["contrasts"]["C2-CR"]["classification"] == "negative"
    assert not result["primary_claim_supported"]


def test_missing_pair_is_incomplete_never_imputed_or_resampled():
    table = rows()
    table = [
        r
        for r in table
        if not (
            r["arm"] == "CR"
            and r["realization"] == 1
            and r["order"] == 2
            and r["item_id"] == "item-0"
        )
    ]
    result = analyze_paired(table)
    assert result["classification"] == "incomplete"
    assert result["contrasts"]["C2-C1"]["classification"] == "positive"
    missing = result["contrasts"]["C2-CR"]
    assert missing["measures"] is None
    assert missing["missing"] == [
        {
            "realization": 1,
            "order": 2,
            "item_id": "item-0",
            "reason": "missing_pair",
            "arms": ["CR"],
        }
    ]
    json.dumps(result, allow_nan=False)


def test_missing_entire_order_and_null_outcome_are_visible():
    table = [r for r in rows() if r["order"] != 4]
    report = analyze_paired(table)
    assert report["classification"] == "incomplete"
    assert all(c["measures"] is None for c in report["contrasts"].values())
    table = rows()
    table[0]["ls"] = None
    report = analyze_paired(table)
    assert report["contrasts"]["C2-C1"]["missing"][0]["reason"] == "unavailable_outcome"


def test_frozen_inventory_catches_items_missing_from_every_arm():
    table = rows(items=1)
    report = analyze_paired(table, expected_items={r: ["item-0", "item-1"] for r in range(3)})
    assert report["coverage_basis"] == "frozen_inventory"
    assert report["classification"] == "incomplete"
    assert len(report["contrasts"]["C2-C1"]["missing"]) == 15
    with pytest.raises(ValueError, match="unexpected items"):
        analyze_paired(rows(), expected_items={r: ["item-0"] for r in range(3)})


def test_pairing_matches_ids_not_row_positions_and_is_deterministic():
    table = rows((-0.1, 0.2, 0.3))
    expected = analyze_paired(table, seed=21)
    np.random.default_rng(123).shuffle(table)
    assert analyze_paired(table, seed=21) == expected
    assert analyze_paired(table, seed=21) == analyze_paired(copy.deepcopy(table), seed=21)


def test_means_weight_realizations_equally_despite_item_counts():
    table = rows((0.1, 0.2, 0.3), items=3)
    table = [r for r in table if int(r["item_id"][-1]) <= r["realization"]]
    result = analyze_paired(table)
    assert result["contrasts"]["C2-C1"]["measures"]["ret_gs"]["estimate"]["value"] == pytest.approx(
        0.2
    )


def test_per_item_loss_information_not_only_equal_aggregate_accuracy():
    table = rows((0, 0, 0))
    for row in table:
        i = int(row["item_id"][-1])
        row["ret_gs"] = float(i == (0 if row["arm"] == "C2" else 1))
    result = analyze_paired(table)
    contrast = result["contrasts"]["C2-C1"]
    assert contrast["measures"]["ret_gs"]["estimate"]["value"] == 0
    losses = [r for r in contrast["item_changes"] if r["direction"] == "lost"]
    assert len(losses) == 15
    assert all(
        r["item_id"] == "item-1" and r["all_comparator_paraphrase_success_lost"] for r in losses
    )


def test_invalid_or_mixed_records_raise_instead_of_fabricating_results():
    table = rows()
    with pytest.raises(ValueError, match="duplicate item"):
        analyze_paired(table + [table[0]])
    table[0]["ret_gs"] = float("nan")
    with pytest.raises(ValueError, match="finite fraction"):
        analyze_paired(table)
    table = rows()
    table[0]["stream_id"] = "zsre"
    table[1]["stream_id"] = "counterfact"
    with pytest.raises(ValueError, match="separately"):
        analyze_paired(table)
    with pytest.raises(ValueError, match="three realizations"):
        analyze_paired(rows(), realizations=[0, 1])
    with pytest.raises(ValueError, match="matrix required"):
        cluster_bootstrap(np.zeros((3, 4)))
    with pytest.raises(ValueError, match="finite"):
        cluster_bootstrap(np.full((3, 5), np.nan))


def test_empty_input_and_cli(tmp_path):
    assert analyze_paired([])["classification"] == "incomplete"
    input_path, output = tmp_path / "input.jsonl", tmp_path / "report.json"
    input_path.write_text("\n".join(json.dumps(row) for row in rows()))
    assert main([str(input_path), "--output", str(output), "--stream-id", "synthetic-control"]) == 0
    report = json.loads(output.read_text())
    assert report["classification"] == "positive"
    assert report["stream_id"] == "synthetic-control"
    input_path.write_text("")
    assert main([str(input_path), "--output", str(output)]) == 2
