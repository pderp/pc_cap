"""Staged variant readers: actual CPU smoke, strict pairing, no treatment pooling."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import json
import sys
from types import ModuleType, SimpleNamespace
from uuid import uuid4

import jax
import numpy as np
import pytest

import aw
from aw.pc9_stage import DEST, ROOT
from aw.pc_sweep import settings
from aw.pc_v1_acquire import PCRevisionCap
from aw.tests.test_pc9 import base
from aw.tests.test_pc_v1_acquire import cfg
from aw.tests.test_pc_v1_readout import saved


def test_combined_patch_applies_exactly_to_disposable_copies(tmp_path):
    import shutil
    import subprocess

    records = json.loads((DEST / "sources.json").read_text()) | json.loads(
        (DEST / "reporting-sources.json").read_text()
    )
    (tmp_path / "aw").mkdir()
    for name, record in records.items():
        if record["before_sha256"]:
            shutil.copyfile(ROOT / name, tmp_path / name)
    subprocess.run(
        ["git", "apply", str(DEST / "combined-PC-9-PC-10.patch")],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    for name in records:
        assert (tmp_path / name).read_bytes() == (DEST / name.split("/")[-1]).read_bytes()


@pytest.fixture
def staged(monkeypatch):
    loaded = {}
    for name in ("pc_treatments", "pc_v0", "pc_v0_report", "pc_harm_readout", "pc_v1_readout"):
        m = ModuleType("aw." + name)
        m.__file__ = str(
            DEST / (name + ".py") if name == "pc_treatments" else ROOT / "aw" / (name + ".py")
        )
        monkeypatch.setitem(sys.modules, "aw." + name, m)
        monkeypatch.setattr(aw, name, m, raising=False)
        exec(
            compile((DEST / (name + ".py")).read_text(), str(DEST / (name + ".py")), "exec"),
            m.__dict__,
        )
        loaded[name] = m
    return SimpleNamespace(
        t=loaded["pc_treatments"],
        r=loaded["pc_v0_report"],
        h=loaded["pc_harm_readout"],
        v1=loaded["pc_v1_readout"],
    )


def mark(group, k=16, lr=0.03):
    plan = json.loads((group / "plan.json").read_text())
    plan["credit"] = {a: settings(a, k, lr) for a in ("SE-A", "SE-E")}
    (group / "plan.json").write_text(json.dumps(plan))
    for c in plan["cells"]:
        folder = group / f"{c['dataset']}-r{c['realization']}-o{c['order']}-{c['arm']}"
        for name in ("config.json", "finish.json"):
            data = json.loads((folder / name).read_text())
            data.update(settings(c["arm"], k, lr))
            (folder / name).write_text(json.dumps(data))
    return group


@pytest.fixture(scope="module")
def variant_smoke():
    # Same actual runner fixture; change the actual construction BEFORE updates.
    from aw import pc_v0_smoke as s

    with pytest.MonkeyPatch.context() as mp:
        cap_config = s.CapConfig
        calls = iter((0.1, 0.03))
        mp.setattr(s, "TinyEPC", lambda: base(next(calls)))

        def config(**kw):
            kw["credit_iters"] = 16 if kw["credit"] == "error" else 8
            return cap_config(**kw)

        mp.setattr(s, "CapConfig", config)
        path = s.generate(ROOT / "results/additional_work/PC-v0/.pytest_cache" / uuid4().hex)
    return mark(path)


def test_actual_default_and_variant_reports_are_separate(
    staged, pc_v0_smoke, variant_smoke, tmp_path
):
    legacy = staged.r.load_group(pc_v0_smoke, {}, smoke=True)
    variant = staged.r.load_group(variant_smoke, {}, smoke=True)
    assert staged.t.homogeneous(legacy) == dict(credit_iters=8, error_lr=0.1)
    assert staged.t.homogeneous(variant) == dict(credit_iters=16, error_lr=0.03)
    assert variant[0]["solver"]["credit_iters"] == 8
    assert variant[1]["finish"]["ledger"]["learning"]["settle_iters"] % 16 == 0
    with pytest.raises(ValueError, match="mixed treatments"):
        staged.r.compare(
            legacy + variant, [dict(dataset="zsre", realization=0, order=100, arm="SE-A", items=1)]
        )
    result = staged.r.build(
        [pc_v0_smoke, variant_smoke], tmp_path / "out", tmp_path / "sweep.md", smoke=True
    )
    assert result["schema"] == "pc-treatment-sweep-v1" and len(result["treatments"]) == 2
    assert "aggregates" not in result  # no pooled estimand
    assert (
        "k=16" in (tmp_path / "sweep.md").read_text()
        and "CPU SMOKE" in (tmp_path / "sweep.md").read_text()
    )
    with pytest.raises(ValueError, match="never pool"):
        staged.r.plot(tmp_path / "out/report.json", tmp_path / "bad-plot")


def test_disagreeing_finish_and_missing_requested_record_rejected(staged, variant_smoke, tmp_path):
    import shutil

    target = tmp_path / "copy"
    shutil.copytree(variant_smoke, target)
    f = target / "zsre-r0-o100-SE-E/finish.json"
    saved = json.loads(f.read_text())
    saved["error_lr"] = 0.1
    f.write_text(json.dumps(saved))
    with pytest.raises(ValueError, match="config/finish"):
        staged.r.load_group(target, {}, smoke=True)
    cfg = dict(arm="SE-E", credit_iters=16, error_lr=0.03)
    with pytest.raises(ValueError, match="explicit requested"):
        staged.t.recorded(cfg)
    cfg.update(settings("SE-E", 16, 0.03))
    with pytest.raises(ValueError, match="differs from plan"):
        staged.t.recorded(cfg, plan={})


def test_sweep_cannot_overwrite_original_experiment_document(
    staged, pc_v0_smoke, variant_smoke, tmp_path, monkeypatch
):
    def forbidden(*args, **kwargs):
        raise AssertionError("sweep writer must not be reached for the original result slot")

    monkeypatch.setattr(staged.t, "build_sweep", forbidden)
    with pytest.raises(ValueError, match="separate document"):
        staged.r.build(
            [pc_v0_smoke, variant_smoke],
            tmp_path / "out",
            ROOT / "docs/additional_work/PC-v0_report.md",
            smoke=True,
        )


def test_duplicate_same_treatment_and_mixed_pair_rejected(staged, variant_smoke, tmp_path):
    import shutil

    with pytest.raises(ValueError, match="duplicate"):
        staged.r.build(
            [variant_smoke, variant_smoke], tmp_path / "out", tmp_path / "r.md", smoke=True
        )
    target = tmp_path / "mixed"
    shutil.copytree(variant_smoke, target)
    f = target / "zsre-r0-o100-SE-A/config.json"
    c = json.loads(f.read_text())
    c.update(settings("SE-A", 32, 0.03))
    f.write_text(json.dumps(c))
    with pytest.raises(ValueError, match="differs from plan"):
        staged.r.load_group(target, {}, smoke=True)


def test_variant_harm_restores_actual_state_and_sweep_never_pools(
    staged, pc_v0_smoke, variant_smoke, tmp_path, monkeypatch
):
    monkeypatch.setattr(staged.h, "OUTPUT", tmp_path)
    outputs = []
    for i, path in enumerate((pc_v0_smoke, variant_smoke)):
        out = tmp_path / str(i)
        result = staged.h.run(path, out, smoke=True, batch_size=2)
        assert result["treatment"]["credit_iters"] == (8 if i == 0 else 16)
        assert all(c["readout"]["treatment"] == result["treatment"] for c in result["cells"])
        outputs.append(out / "report.json")
    result = staged.t.harm_sweep(outputs, tmp_path / "sweep.json", tmp_path / "sweep.md")
    assert len(result["treatments"]) == 2 and result["pooling"] == "none"
    with pytest.raises(ValueError, match="duplicate"):
        staged.t.harm_sweep(outputs * 2, tmp_path / "bad.json", tmp_path / "bad.md")
    with pytest.raises(ValueError, match="base rate"):
        rows = staged.r.load_group(variant_smoke, {}, smoke=True)
        staged.h.restore_v0(base(0.1), rows[1], {}, smoke=True)


@pytest.mark.parametrize("k", [16, 32])
def test_fixed_v5_variant_restore_requires_consistent_config_finish_and_rate(staged, tmp_path, k):
    b = base(0.03)
    cap = PCRevisionCap(b, cfg(), b.ledger, acquisition_credit="error", credit_iters=k)
    binding = saved(cap, tmp_path / "state.snapshot")
    binding["error_lr"] = 0.03
    config = dict(cell=dict(arm="SE-E"), solver=settings("SE-E", k, 0.03))
    finish = dict(
        credit_iters=k, error_lr=0.03, error_solver_active=True, requested_solver=config["solver"]
    )
    reader = staged.v1.PCPositionBatchReader.from_checkpoint(
        b, cap.cfg, cap.params, binding, config=config, finish=finish
    )
    assert reader.adapter.state_hash() == cap.state_hash()
    assert reader.treatment == dict(credit_iters=k, error_lr=0.03)
    with pytest.raises(ValueError, match="requires its config"):
        staged.v1.PCPositionBatchReader.from_checkpoint(b, cap.cfg, cap.params, binding)
    with pytest.raises(ValueError, match="recorded error learning rate"):
        staged.v1.PCPositionBatchReader.from_checkpoint(
            base(0.1), cap.cfg, cap.params, binding, config=config, finish=finish
        )
    wrong = copy.deepcopy(finish)
    wrong["credit_iters"] = 8
    with pytest.raises(ValueError, match="config/finish"):
        staged.v1.PCPositionBatchReader.from_checkpoint(
            b, cap.cfg, cap.params, binding, config=config, finish=wrong
        )
    assert jax.default_backend() == "cpu"
    np.testing.assert_equal(binding["error_lr"], 0.03)
