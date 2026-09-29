import pccap  # noqa: F401 # isort: skip

# isort: split

import json

import numpy as np
import pytest

from aw import aw_b_calibrate as b
from aw.pc_harm_readout import window_hash
from aw.pc_harm_smoke import TinyBatchEPC
from aw.tests.test_pc_v1_acquire import cfg
from aw.tests.test_pc_v1_run import fixture
from pccap.revision_v1.learner import RevisionCap


def tiny():
    base, config = TinyBatchEPC(), cfg()
    config.fast.delta_steps = 1
    cap = RevisionCap(base, config, base.ledger)
    tok, items, endpoints = fixture()
    for it in items:
        cap.update_item(it)
    return cap, tok, items, endpoints


def test_real_tiny_all_16_settings_and_native_endpoints(tmp_path):
    cap, tok, items, endpoints = tiny()
    before = cap.state_hash()
    windows = np.int32([[1, 2, 3, 4], [2, 3, 4, 5]])
    metadata = dict(mode="cpu_smoke", positions=6, windows_sha256=window_hash(windows))
    harm = b.fixed_prefix(
        cap, windows, metadata, b.CONFIGS, tmp_path / "harm", tmp_path / "vectors", batch_size=2
    )
    scores = b.efficacy(cap, tok, items, endpoints, b.CONFIGS, tmp_path / "efficacy", max_new=2)
    assert set(harm) == set(scores) == {b.scoring.config_key(c) for c in b.CONFIGS}
    assert len(harm) == 16 and len(b.NUMERICAL) == 13
    assert harm["capoff"]["summary"]["original"]["loss"]["maximum_signed"] == 0
    assert cap.state_hash() == before
    for key, h in harm.items():
        assert h["telemetry"]["logical_positions"] == 6
        assert h["telemetry"]["hard_null"] + h["telemetry"]["selected"] == 6
        with np.load(h["vectors"]["path"]) as f:
            assert f["values"].shape == (2, 3, 5)
        assert scores[key]["metrics"]["ES"] == scores[key]["metrics"]["RET-ES"]
    # No claim from these synthetic results; selection itself is checked separately.


def synthetic():
    result = {}
    for ds in b.DATASETS:
        result[ds] = dict(efficacy={}, harm={})
        for config in b.CONFIGS:
            key = b.scoring.config_key(config)
            result[ds]["efficacy"][key] = dict(
                metrics={m: dict(value=0.8) for m in ("RET-ES", "RET-GS", "LS", "near_miss")}
            )
            result[ds]["harm"][key] = dict(
                summary=dict(original=dict(loss=dict(maximum_signed=10, es99_positive=2)))
            )
    return result


def test_selection_both_datasets_eligibility_and_max_then_es():
    data = synthetic()
    for ds in b.DATASETS:
        data[ds]["harm"]["clip:0.5"]["summary"]["original"]["loss"].update(
            maximum_signed=1, es99_positive=0.3
        )
        data[ds]["harm"]["clip:1"]["summary"]["original"]["loss"].update(
            maximum_signed=1, es99_positive=0.2
        )
    selected = b.select(data, "minimum")
    assert selected["chosen"]["bound"]["key"] == "clip:1"
    data["counterfact"]["efficacy"]["clip:1"]["metrics"]["RET-GS"]["value"] = 0.779
    assert b.select(data, "minimum")["chosen"]["bound"]["key"] == "clip:0.5"
    data["zsre"]["efficacy"]["clip:0.5"]["metrics"]["near_miss"]["value"] = None
    assert not next(r for r in b.select(data, "minimum")["candidates"] if r["key"] == "clip:0.5")[
        "eligible"
    ]
    with pytest.raises(ValueError, match="approved"):
        b.select(data, None)


def test_selection_no_eligible_category_is_explicit():
    data = synthetic()
    for ds in b.DATASETS:
        for key in data[ds]["efficacy"]:
            if key != "v5":
                data[ds]["efficacy"][key]["metrics"]["LS"]["value"] = 0
    result = b.select(data, "minimum")
    assert result["chosen"] == dict(bound=None, comparator=None)
    assert result["final_configs"] == [["v5", None], ["capoff", None]]
    assert json.loads(json.dumps(result)) == result


def test_changed_snapshot_and_population_mismatch_are_refused(tmp_path):
    _, name = b.DEVELOPMENT["zsre"]
    with pytest.raises(ValueError, match="declared first 300"):
        b.qualify(
            b.ROOT / "docs/tasks/R1-post63l-active/R1-64e/R1-64e-zsre-primary-v5.recipe.json",
            b.ROOT / "results/R1/stage4_dev_cells" / name / "attempt-0000",
            b.ASSETS
            / "runs/pc_cap/R1/stage4_dev_cells"
            / name
            / "attempt-0000/checkpoint-300.snapshot",
            population="intentionally incorrect r16 fixture",
        )
    p = tmp_path / "binding.json"
    p.write_text("{}")
    ref = b.binding(p)
    p.write_text('{"changed":true}')
    with pytest.raises(ValueError, match="changed"):
        b.checked(ref)


def test_evaluation_success_requires_every_order_and_both_tails():
    data = synthetic()
    for ds in b.DATASETS:
        for key in data[ds]["efficacy"]:
            data[ds]["efficacy"][key]["metrics"]["revision"] = dict(value=0.8)
        data[ds]["harm"]["clip:0.5"]["summary"]["original"]["loss"].update(
            maximum_signed=9, es99_positive=1
        )
    assert b.evaluation_success(data)["all_coordinates_by_config"]["clip:0.5"]
    data["counterfact"]["harm"]["clip:0.5"]["summary"]["original"]["loss"]["es99_positive"] = 2
    assert not b.evaluation_success(data)["all_coordinates_by_config"]["clip:0.5"]
    data["counterfact"]["harm"]["clip:0.5"]["summary"]["original"]["loss"]["es99_positive"] = 1
    data["zsre"]["efficacy"]["clip:0.5"]["metrics"]["RET-GS"]["value"] = 0.779
    assert not b.evaluation_success(data)["all_coordinates_by_config"]["clip:0.5"]
