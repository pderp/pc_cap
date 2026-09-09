"""S2-01 calibration logic on synthetic keys: largest admissible radius, coverage tie-break,
exact-key fallback when no positive radius meets the 1% false-fire criterion."""

import numpy as np

from pccap.cap.calibrate import calibrate_radii


def _keys(rng, n, d=8):
    k = rng.standard_normal((n, d)).astype(np.float32)
    return k / np.linalg.norm(k, axis=1, keepdims=True)


def test_largest_admissible_radius_and_candidates_stored():
    rng = np.random.default_rng(0)
    E = _keys(rng, 50)
    owner = np.repeat(np.arange(50), 2)
    P = E[owner] + 0.05 * rng.standard_normal((100, 8)).astype(np.float32)  # close paraphrases
    U = _keys(rng, 400)  # random unit keys: far from edits (distance ~ sqrt(2))
    ek, pk, uk = ({m: E for m in (1, 2, 3)}, {m: P for m in (1, 2, 3)}, {m: U for m in (1, 2, 3)})
    out = calibrate_radii(ek, pk, owner, uk)
    for m in ("1", "2", "3"):
        r = out[m]
        assert r["radius"] > 0 and r["candidates"] and all("false_fire" in c for c in r["candidates"])
        chosen = [c for c in r["candidates"] if c["radius"] == r["radius"]][0]
        assert chosen["false_fire"] <= 0.01 and chosen["coverage"] > 0.9
        assert all(c["radius"] <= r["radius"] for c in r["candidates"] if c["admissible"])


def test_exact_key_fallback():
    rng = np.random.default_rng(1)
    E = _keys(rng, 20)
    owner = np.arange(20)
    P = E + 0.01 * rng.standard_normal((20, 8)).astype(np.float32)
    U = E + 0.001 * rng.standard_normal((20, 8)).astype(np.float32)  # unrelated keys sit on top of the edits
    out = calibrate_radii({1: E}, {1: P}, owner, {1: U}) if False else calibrate_radii(
        {m: E for m in (1, 2, 3)}, {m: P for m in (1, 2, 3)}, owner, {m: U for m in (1, 2, 3)})
    assert out["1"]["radius"] == 0.0 and "exact-key" in out["1"]["note"]
