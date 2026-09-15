"""Distribution definitions and schema/identity refusal gates for stored-results audit."""

import math

import pytest
from scripts.ht_audit_existing import row_sets, series_from_rows, statistics, tail_sum


def test_fractional_tail_ties_and_atom():
    x = [0.0] * 20 + [10.0]
    s = statistics(x, list(range(21)))
    assert s["ES95_positive"] == pytest.approx(10 / 1.05)
    assert s["worst_1pct_share_positive"] == pytest.approx(0.21)
    assert s["atom_zero_positive"] == {"count": 20, "denominator": 21}
    assert tail_sum([2, 2, 2], 0.5) == 3
    assert s["maximum_location"] == 20


def test_signed_and_positive_are_separate():
    s = statistics([-3, 0, 1, 2], list("abcd"))
    assert s["mean_signed"] == 0
    assert s["mean_positive"] == 0.75
    assert s["negative_count"] == 1
    assert s["exceedances_nats"]["1.0"]["count"] == 1
    z = statistics([0, 0], ["a", "b"], "error_fraction")
    assert z["worst_1pct_share_positive"] is None
    assert z["exceedances_nats"] is None


def test_nonfinite_or_duplicate_fails_explicitly():
    with pytest.raises(ValueError, match="nonfinite"):
        statistics([math.nan], ["x"])
    rows = [{"item_id": "x", "es": 1}, {"item_id": "x", "es": 0}]
    result, gaps = series_from_rows(rows, "$", {})
    assert not result and "duplicate" in gaps[0]["reason"]


def test_drift_reference_and_window_identity():
    rows = [
        {"item_id": "w0:p1", "cap": 4, "capoff": 3, "original": 2},
        {"item_id": "w1:p1", "cap": 1, "capoff": 2, "original": 2},
    ]
    result, gaps = series_from_rows(rows, "$.drift.rows", {"source_sha256": "a" * 64})
    assert not gaps and len(result) == 2
    assert result[0]["windows"] == 2
    assert result[0]["statistics"]["mean_signed"] == 0.5
    changed, _ = series_from_rows(rows, "$.drift.rows", {"source_sha256": "b" * 64})
    assert not result[0]["_values"].keys() & changed[0]["_values"].keys()


def test_direct_row_files_and_learning_loss_labels():
    rows = [{"item_id": "x", "dataset": "zsre", "revision_success": True, "nll": 8}]
    assert len(list(row_sets(rows))) == 1
    result, gaps = series_from_rows(rows, "$", {})
    assert not gaps
    assert {r["statistics"]["unit"] for r in result} == {
        "error_fraction",
        "target_nats_not_preservation",
    }
