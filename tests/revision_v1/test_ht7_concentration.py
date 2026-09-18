"""Concentration boundaries, zero mass, both references and independent Gini."""

import numpy as np
import pytest
from scripts import ht7_concentration as ht7


def test_fractional_shares_integer_half_mass_and_gini():
    a = np.array([0.0, 0.0, 1.0, 3.0])
    out = ht7.mass_summary(a, [0.1, 0.25, 0.5, 1.0])
    assert out["top_shares"] == {"0.1": pytest.approx(0.3), "0.25": 0.75, "0.5": 1.0, "1.0": 1.0}
    assert out["minimum_count_for_half_mass"] == 1
    assert out["fraction_for_half_mass"] == 0.25
    independent = np.abs(a[:, None] - a[None, :]).sum() / (2 * len(a) * a.sum())
    assert out["gini"] == independent
    ties = ht7.mass_summary([1, 1, 1, 1], [0.1])
    assert ties["gini"] == 0 and ties["minimum_count_for_half_mass"] == 2


def test_all_zero_has_undefined_concentration_without_fabricated_harm():
    out = ht7.mass_summary(np.zeros(4), [0.01])
    assert out["total"] == 0 and out["zero_count"] == 4
    assert out["top_shares"] == {"0.01": None}
    assert (
        out["minimum_count_for_half_mass"] is out["fraction_for_half_mass"] is out["gini"] is None
    )


def test_both_references_windows_and_loss_are_distinct():
    v = np.full((3, 2, 5), 2.0)
    v[:, :, 3] = [[0.001, 0.001], [0.01, 0.01], [0.1, 0.1]]
    v[:, :, 4] = 0
    v[0, 0, 1] = 3.0  # negative loss delta is zero positive harm
    v[0, 1, 1] = 1.0
    out = ht7.concentration(v)
    own, original = out["references"]["capoff"], out["references"]["original"]
    assert own["near_zero_loss_change"]["count"] == 4
    assert own["loss_positive_positions"]["positive_count"] == 1
    assert own["window_mean_kl"]["benchmark_pass_count"] == 1
    assert own["window_mean_kl"]["strict_exceedances"] == {"0.01": 1, "0.1": 0}
    assert own["window_mean_kl"]["quantiles"]["0.5"] == 0.01
    assert original["kl_positions"]["gini"] is None
    assert original["near_zero_loss_change"]["count"] == 6
    assert "does not prove" in out["interpretation"]


@pytest.mark.parametrize("value", [[], [-1], [np.nan], [np.inf]])
def test_invalid_mass_refuses(value):
    with pytest.raises(ValueError):
        ht7.mass_summary(value, [0.01])


def test_vector_hash_checked(tmp_path):
    from scripts.r1_63l_full_validation_contract import ref

    path = tmp_path / "values.npz"
    np.savez_compressed(path, values=np.ones((1, 2, 5)))
    binding = ref(path)
    assert ht7.from_binding(binding)["positions"] == 2
    path.write_bytes(path.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="hash changed"):
        ht7.from_binding(binding)
