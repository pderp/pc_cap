import json
import math

import numpy as np
import pytest

from aw import aw_b_report as report


def test_final_report_refuses_running_or_failed_evaluation_before_reading_outcomes(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(report, "EVALUATION", tmp_path / "evaluation")
    report.EVALUATION.mkdir()
    with pytest.raises(ValueError, match="still running"):
        report.build(final=True, output=tmp_path / "out")
    assert not (tmp_path / "out").exists()
    (report.EVALUATION / "report.json").write_text(json.dumps({"status": "complete"}))
    (report.EVALUATION / "cost.json").write_text(json.dumps({"status": "failed"}))
    assert not report.ready(report.EVALUATION)


def test_selected_mixture_fixed_prefix_ceiling_without_greedy_preservation_guarantee():
    from aw.bounded import mixture

    base = np.array([0.99, 0.01])
    cap = np.array([0.4, 0.6])
    rho = math.exp(-1)
    logq = mixture(np.log(base), np.log(cap), rho)
    assert np.max(np.log(base) - logq) <= 1
    assert np.argmax(logq) != np.argmax(
        cap
    )  # Mixture weight does not ensure unchanged greedy answer.
    assert report.bound(("mixture", rho)) == 1 and report.bound(("clip", 0.5)) == 1
    assert report.bound(("shrink", 0.5)) is None


def test_calibration_selection_qualified_as_development():
    p = report.OUTPUT / "calibration-review.json"
    r = json.loads(p.read_bytes())
    assert (
        r["status"] == "calibration_verified_evaluation_pending"
        and len(r["verified_settings"]) == 32
    )
    assert r["selection"]["chosen"]["comparator"] is None
    assert r["selection"]["chosen"]["bound"]["efficacy_changes"]["counterfact"][
        "RET-GS"
    ] == pytest.approx(-1 / 120)
