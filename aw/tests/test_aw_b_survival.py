import numpy as np

from aw.aw_b_tail_figure import survival


def test_strict_survival_includes_zero_mass_and_steps_after_observation():
    x, y = survival([-2, 0, 0, 1, 1, 2])
    np.testing.assert_array_equal(x, [0, 1, 2])
    np.testing.assert_allclose(y, [3 / 6, 1 / 6, 0])
    assert np.interp(1, x, y) == 1 / 6
