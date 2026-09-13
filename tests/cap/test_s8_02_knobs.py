"""S8-02 ablation knobs: the byte-ceiling factor scales bank capacities (default 1.0 = the frozen ceiling) and the
calibration's false-fire bound is a parameter (default 1%, the frozen criterion)."""

import numpy as np

from pccap.cap import memory as mem
from pccap.cap.calibrate import FALSE_FIRE_MAX, calibrate_radii
from tests.cap.mock_base import make_cap


def test_ceiling_factor_scales_capacity():
    from pccap.cap.cap import Cap, CapConfig

    base, cap1 = make_cap(arm="C2", radii=0.5)
    cap_half = Cap(base, CapConfig(arm="C2", radii={1: .5, 2: .5, 3: .5}, bank_scales={1: 2., 2: 3., 3: 4.}, seed=0, d=8, ceiling_factor=0.5))
    cap_double = Cap(base, CapConfig(arm="C2", radii={1: .5, 2: .5, 3: .5}, bank_scales={1: 2., 2: 3., 3: 4.}, seed=0, d=8, ceiling_factor=2.0))
    for m in (1, 2, 3):
        c1, ch, cd = cap1.layouts[m].capacity, cap_half.layouts[m].capacity, cap_double.layouts[m].capacity
        assert ch < c1 < cd and abs(ch / c1 - 0.5) < 0.05 and abs(cd / c1 - 2.0) < 0.05
    assert mem.bank_ceilings("C2", 8) == mem.bank_ceilings("C2", 8, 1.0)
    assert cap_half.memory_bytes().ceiling_bytes == int(round(mem.b_cap(8) * 0.5))
    assert cap1.memory_bytes().ceiling_bytes == mem.b_cap(8)


def test_false_fire_bound_is_a_parameter():
    rng = np.random.default_rng(0)
    E = {m: rng.standard_normal((20, 4)) for m in (1, 2, 3)}
    P = {m: E[m] + 0.1 * rng.standard_normal((20, 4)) for m in (1, 2, 3)}
    U = {m: rng.standard_normal((200, 4)) * 3 for m in (1, 2, 3)}
    strict = calibrate_radii(E, P, np.arange(20), U)
    loose = calibrate_radii(E, P, np.arange(20), U, false_fire_max=0.05)
    assert FALSE_FIRE_MAX == 0.01
    for m in ("1", "2", "3"):  # calibrate_radii keys banks as strings (JSON-ready)
        assert loose[m]["radius"] >= strict[m]["radius"]
