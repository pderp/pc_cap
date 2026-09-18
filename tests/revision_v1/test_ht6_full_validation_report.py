"""Prefix identity, independent loss reporting and tied strict CCDF checks."""

import copy

import numpy as np
import pytest
from scripts import ht6_full_validation_report as ht


def example():
    v = np.full((3, 2, 5), 2.0)
    v[:, :, 0] += np.array([[0.2, -0.1], [0.0, 0.0], [1.2, 0.3]])
    v[:, :, 3:] = 0.002
    rows = [
        dict(item_id=f"w0:p{i + 1}", cap=float(v[0, i, 0]), capoff=2.0, original=2.0)
        for i in range(2)
    ]
    return v, rows


def test_prefix_statistics_preserve_population_difference_and_kl_origin():
    v, rows = example()
    r = ht.sample_statistics(v, rows, width=3, sample_windows=1)
    ref = r["references"]["original"]
    assert ref["loss"]["mean_signed"] == pytest.approx(0.05)
    assert ref["loss"]["ES95_positive"] == pytest.approx(0.2)
    assert ref["loss"]["ES99_positive"] == pytest.approx(0.2)
    assert ref["kl"]["mean_signed"] == 0.002
    assert ref["remainder_loss_mean"] == pytest.approx(0.375)
    assert "no separate" in ref["kl_measurement"]
    assert r["overlap"]["status"] == "pass"


@pytest.mark.parametrize("fault", ["missing", "order", "nonfinite", "loss", "counts"])
def test_bad_sample_refuses(fault):
    v, rows = example()
    if fault == "missing":
        rows.pop()
    if fault == "order":
        rows.reverse()
    if fault == "nonfinite":
        rows[0]["cap"] = float("nan")
    if fault == "loss":
        rows[0]["cap"] += 0.01
    if fault == "counts":
        v[0, 0, 0] = 2.10001
        rows[0]["cap"] = 2.09999  # within loss tolerance but crosses exceedance threshold
    with pytest.raises(ValueError):
        ht.sample_statistics(v, rows, width=3, sample_windows=1)


def test_strict_survival_with_ties_and_zero_atom():
    x, y = ht.survival([-1.0, 0.0, 1.0, 1.0, 2.0])
    np.testing.assert_array_equal(x, [0.0, 1.0, 2.0])
    np.testing.assert_allclose(y, [3 / 5, 1 / 5, 0.0])
    np.testing.assert_array_equal(ht.survival([2.0, 2.0])[0], [0.0, 2.0])


def test_final_report_refuses_partial_inventory(monkeypatch):
    inventory = dict(
        completed=1, cells={str(i): dict(status="awaiting_completed_result") for i in range(4)}
    )
    monkeypatch.setattr(ht.measured, "inventory", lambda: copy.deepcopy(inventory))
    with pytest.raises(ValueError, match="all four"):
        ht.build()
