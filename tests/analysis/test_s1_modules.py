"""CPU checks of the S1 analysis helpers on synthetic inputs."""

import numpy as np

from pccap.analysis.s1_p2 import linear_probe
from pccap.analysis.s1_p3 import summarize
from pccap.cap.calibrate import calibrate_radii  # noqa: F401  (import smoke)


def test_p3_summarize_known_fields():
    N, L, T = 5, 12, 7
    uniform = np.ones((N, L, T))
    s = summarize(uniform, "raw")
    assert abs(s["pr_mean_raw"]["value"] - L * T) < 1e-9 and abs(s["npr_mean_raw"]["value"] - 1.0) < 1e-9
    assert abs(s["final_block_share_mean_raw"]["value"] - 1 / L) < 1e-9
    assert s["active_fraction_mean_raw"]["value"] == 1.0 and s["zero_fields_raw"]["value"] == 0
    conc = np.zeros((N, L, T))
    conc[:, -1, 3] = 1.0  # all mass in one final-block cell
    conc[0] = 0.0  # one zero field
    s = summarize(conc, "raw")
    assert s["pr_mean_raw"]["value"] == 1.0 and s["final_block_share_mean_raw"]["value"] == 1.0
    assert s["final_block_share_mean_raw"]["strata"]["alert_above_0.4"] is True
    assert s["zero_fields_raw"]["value"] == 1 and s["pr_mean_raw"]["n"] == N - 1


def test_linear_probe_separable():
    rng = np.random.default_rng(0)
    centers = rng.standard_normal((4, 16)) * 4
    y_tr = rng.integers(0, 4, 400)
    y_ev = rng.integers(0, 4, 100)
    x_tr = centers[y_tr] + rng.standard_normal((400, 16))
    x_ev = centers[y_ev] + rng.standard_normal((100, 16))
    r = linear_probe(x_tr.astype(np.float32), y_tr, x_ev.astype(np.float32), y_ev, 4, steps=200)
    assert r["eval_acc"] > 0.9 and r["n_train"] == 400 and r["n_eval"] == 100
