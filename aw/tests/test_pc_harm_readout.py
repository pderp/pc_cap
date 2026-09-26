"""PC-5: real saved smoke checkpoints, scalar/batch parity and tail definitions."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import json

import numpy as np
import pytest
from scripts.r1_68e_batched_drift_v0 import V0PositionBatchReader

from aw import pc_harm_readout as h
from aw import scoring
from aw.pc_harm_smoke import TinyBatchEPC
from aw.pc_v0_report import load_group
from pccap.revision_v1.stage4_adapters import CellAdapter

SMOKE = h.ROOT / "results/additional_work/PC-v0/cpu-smoke-round45"


def test_fractional_es_not_percentile_and_ties():
    x = np.zeros(250)
    x[:3] = [10, 10, 5]
    s = h.tails(x, 5)
    assert s["es99_positive"] == 9  # (10+10+0.5*5)/2.5; 99th percentile is 2.55
    assert s["maximum_location"] == "w0:p1" and s["maximum_ties"] == 2
    assert s["half_mass_positions"] == 2
    assert s["exceedance"]["1.0"]["count"] == 3
    assert h.tails([-2, -1, 0, 0], 2)["es99_positive"] == 0
    assert h.tails([0, 0], 2)["half_mass_positions"] is None
    assert h.tails([0.01, 0.1, 1.0, 2.0], 2)["exceedance"]["1.0"]["count"] == 1
    with pytest.raises(ValueError):
        h.tails([np.nan], 1)


def test_selected_populations():
    a, ma = h.selection("v0")
    b, mb = h.selection("v5")
    assert a.shape == (32, 128) and ma["positions"] == 4064
    assert b.shape == (1931, 128) and mb["positions"] == 245237
    assert np.array_equal(a, b[:32])


def test_real_smoke_checkpoints_and_scalar_predictions(tmp_path):
    if not SMOKE.exists():
        pytest.skip("generate aw.pc_v0_smoke first")
    rows = load_group(SMOKE, {}, smoke=True)
    windows = np.int32([[4, 11, 17, 9], [4, 12, 17, 7]])
    meta = dict(mode="cpu_smoke", positions=6, windows_sha256=h.window_hash(windows))
    base = TinyBatchEPC()
    results = []
    for row in rows:
        cap = h.restore_v0(base, row, {}, smoke=True)
        state = cap.state_hash()
        reader = V0PositionBatchReader(CellAdapter(cap, "v0_live_C1"), batch_size=2)
        result = h.read_arm(reader, windows, meta, tmp_path / row["arm"])
        expected = []
        for w in windows:
            for pos in range(1, len(w)):
                on = np.asarray(cap.predict(w[:pos]).logits)[None, :]
                off = np.asarray(base.forward(w[:pos], last_only=True, phase="query").logits)[
                    None, :
                ]
                expected.append(
                    scoring.score_configs(on, off, off, np.int32([w[pos]]), [("v5", None)])["v5"][0]
                )
        v = np.load(result["vectors"]["path"])["values"]
        np.testing.assert_allclose(v.reshape(-1, 5), expected, atol=2e-6, rtol=1e-5)
        assert cap.state_hash() == state
        cost = json.loads((tmp_path / row["arm"] / "cost.json").read_text())
        assert cost["positions_completed"] == 6 and cost["status"] == "complete"
        assert cost["query_costs"]["shared_capoff_selection"]["returned_cost"]["full_forwards"] == 6
        results.append(result)
    p = h.pair(*results, tmp_path / "paired.npz")
    v = np.load(tmp_path / "paired.npz")["values"]
    a, e = [np.load(r["vectors"]["path"])["values"] for r in results]
    np.testing.assert_array_equal(v, e - a)
    assert p["positionwise"]["original"]["loss"]["mean_signed"] == pytest.approx(
        (e[:, :, 0] - a[:, :, 0]).mean()
    )
    bad = copy.deepcopy(results[1])
    bad["selection"]["positions"] = 5
    with pytest.raises(ValueError, match="identities"):
        h.pair(results[0], bad, tmp_path / "bad.npz")
    with open(results[1]["vectors"]["path"], "ab") as f:
        f.write(b"changed")
    with pytest.raises(ValueError, match="vectors changed"):
        h.pair(*results, tmp_path / "bad2.npz")


def test_failure_retains_cost_without_publishing_vectors(tmp_path):
    base = TinyBatchEPC()
    row = load_group(SMOKE, {}, smoke=True)[0]
    cap = h.restore_v0(base, row, {}, smoke=True)
    reader = V0PositionBatchReader(CellAdapter(cap, "v0_live_C1"), batch_size=2)

    def failed(*args):
        reader.events.append(
            dict(model="failed", status="failed", returned_cost=dict(full_forwards=2))
        )
        raise RuntimeError("simulated interruption")

    reader.last_logits_batch = failed
    windows = np.int32([[4, 11, 17]])
    with pytest.raises(RuntimeError, match="simulated"):
        h.read_arm(
            reader,
            windows,
            dict(positions=2, windows_sha256=h.window_hash(windows)),
            tmp_path / "out",
        )
    cost = json.loads((tmp_path / "out/cost.json").read_text())
    assert (
        cost["status"] == "failed"
        and cost["query_costs"]["failed"]["returned_cost"]["full_forwards"] == 2
    )
    assert not (tmp_path / "out/vectors.npz").exists()
