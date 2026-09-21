"""The scorer reuses the registered full-validation metrics: the unwrapped configuration equals ``fv.metrics`` exactly,
the cap-off configuration has zero KL and zero loss delta, and clipped configurations respect the 2b bound per position."""
import os
import sys

import numpy as np

os.environ.setdefault("JAX_PLATFORMS", "cpu")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from aw import scoring as S  # noqa: E402
from scripts import r1_68f_full_validation as fv  # noqa: E402

RNG = np.random.default_rng(7)


def batch(n=64, v=5000):
    off = RNG.normal(0, 6, size=(n, v))
    on = off + RNG.normal(0, 2, size=(n, v)) * (RNG.random((n, 1)) < 0.3)  # 30 % of positions changed
    original = off + RNG.normal(0, 0.01, size=(n, v))
    targets = RNG.integers(0, v, size=n)
    return on, off, original, targets


def test_unwrapped_equals_registered_metrics_and_capoff_is_identity():
    on, off, original, targets = batch()
    rows = S.score_configs(on, off, original, targets, [("v5", None), ("capoff", None)])
    assert np.array_equal(rows["v5"], fv.metrics(on, off, original, targets))
    off_rows = rows["capoff"]
    assert np.allclose(off_rows[:, 0], off_rows[:, 1]) and np.allclose(off_rows[:, 3], 0.0, atol=1e-12)


def test_clip_bound_per_position_and_accumulator_summary():
    acc = S.Accumulator([("v5", None), ("clip", 0.5), ("clip", 2.0), ("mixture", np.exp(-1.0)), ("shrink", 0.5)])
    for _ in range(3):
        acc.add(*batch())
    vec = acc.vectors()
    assert set(vec) == {"v5", "clip:0.5", "clip:2", "mixture:0.367879", "shrink:0.5"}
    for key, b in (("clip:0.5", 0.5), ("clip:2", 2.0)):
        d = vec[key][:, 0] - vec[key][:, 1]
        assert d.max() <= 2 * b + 1e-9 and d.min() >= -2 * b - 1e-9
        assert vec[key][:, 3].max() <= 2 * b + 1e-9
    d_mix = vec["mixture:0.367879"][:, 0] - vec["mixture:0.367879"][:, 1]
    assert d_mix.max() <= 1.0 + 1e-9
    s = acc.summary()
    assert s["v5"]["positions"] == 192 and 0.0 < s["v5"]["changed_fraction"] < 1.0
    assert s["clip:0.5"]["max_delta"] <= s["v5"]["max_delta"] + 1e-9
