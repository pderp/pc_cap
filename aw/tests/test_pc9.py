"""Exercise staged PC-9 code without changing/import-replacing live runners."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import hashlib
import json
import sys
from contextlib import nullcontext
from types import ModuleType, SimpleNamespace

import jax
import numpy as np
import pytest
from tests.revision_v1.tiny_base import CFG, tiny_params

from aw import pc9_stage, pc_sweep
from aw.pc_v1_acquire import PCRevisionCap
from aw.tests.test_pc_v0 import TinyEPC, nonzero_writes
from aw.tests.test_pc_v1_acquire import cfg
from aw.tests.test_pc_v1_run import fixture
from pccap.bases.epc import EPCBase
from pccap.contracts import Budget, EditItem
from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.routers import make_router


def staged(name):
    module = ModuleType("staged_" + name)
    module.__file__ = str(pc9_stage.ROOT / "aw" / name)
    path = pc9_stage.DEST / name
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


def base(rate):
    b = TinyEPC.__new__(TinyEPC)
    EPCBase.__init__(b, params_np=jax.tree_util.tree_map(np.asarray, tiny_params()),
                     cfg=CFG, ledger=Ledger(), error_lr=rate)
    return b


def test_exact_patch_still_matches_live_bytes_and_generator():
    record = json.loads((pc9_stage.DEST / "sources.json").read_text())
    for name, transform in (("pc_v0.py", pc9_stage.v0), ("pc_v1_run.py", pc9_stage.v1)):
        before = (pc9_stage.ROOT / "aw" / name).read_bytes()
        candidate = (pc9_stage.DEST / name).read_bytes()
        assert hashlib.sha256(before).hexdigest() == record["aw/"+name]["before_sha256"]
        assert transform(before.decode()).encode() == candidate
        assert hashlib.sha256(candidate).hexdigest() == record["aw/"+name]["candidate_sha256"]


@pytest.mark.parametrize("rate", [0, -1, float("nan"), float("inf")])
def test_invalid_rates_rejected(rate):
    with pytest.raises(ValueError):
        pc_sweep.settings("SE-E", 16, rate)


def test_default_and_control_settings():
    parser = argparse.ArgumentParser()
    pc_sweep.add_options(parser)
    a = parser.parse_args([])
    assert (a.credit_iters, a.error_lr) == (8, 0.1)
    s = pc_sweep.settings("SE-A", 32, 0.03)
    assert (s["credit_iters"], s["error_lr"], s["error_solver_active"]) == (8, 0.1, False)
    with pytest.raises(ValueError):
        pc_sweep.settings("SE-E", 9)


@pytest.mark.parametrize("steps", [16, 32])
def test_actual_solver_and_v0_acquisition_use_selected_horizon(steps, monkeypatch):
    b = base(0.03)
    ids = np.int32([4, 11])
    writes = nonzero_writes(b, ids)
    adj = b.adjoint(ids, 17, writes)
    error = b.infer_errors(ids, 17, iters=1, writes=writes)
    for site in adj:
        np.testing.assert_allclose(error.site_errors[site], -0.03*np.asarray(adj[site]), atol=3e-7, rtol=3e-5)
    r = staged("pc_v0.py")
    cap = r.build_cap(b, "zsre", "SE-E", 23, credit_iters=steps)
    calls, original = [], b.infer_errors

    def tracked(*args, **kwargs):
        result = original(*args, **kwargs)
        calls.append(result.cost)
        return result

    monkeypatch.setattr(b, "infer_errors", tracked)
    item = EditItem(item_id="tiny", digest=b"0"*16, prompt="p", answer="a", aliases=["a"],
                    prompt_ids=ids, answer_ids=np.int32([17]), dataset="tiny", paraphrases=[], locality_prompts=[])
    before = b.checksum(recompute=True)
    cap.update_item(item, make_router("C1"), Budget(R=1, A=0.3))
    assert calls and all(c.settle_iters == steps and c.reverses == steps+1 for c in calls)
    assert b.checksum(recompute=True) == before


def test_v1_actual_stream_records_solver_on_success_and_failure(tmp_path, monkeypatch):
    r = staged("pc_v1_run.py")
    tok, items, eps = fixture()
    config = cfg()
    config.fast.delta_steps = 1
    for failed in (False, True):
        b = base(0.03)
        cap = PCRevisionCap(b, config, b.ledger, acquisition_credit="error", credit_iters=16)
        adapter = CellAdapter(cap, "R1_learned_ff")
        out = tmp_path / str(failed)
        if failed:
            def fail(item):
                raise FloatingPointError("test failure")
            monkeypatch.setattr(adapter, "update_item", fail)
        arguments = (adapter, tok, items, eps, [2], out, tmp_path / (str(failed)+"-resources"),
                     dict(population="cpu_smoke", solver=pc_sweep.settings("SE-E", 16, 0.03)))
        if failed:
            with pytest.raises(FloatingPointError):
                r.execute_stream(*arguments, max_new=2)
        else:
            r.execute_stream(*arguments, max_new=2)
        for name in ("config.json", "finish.json"):
            saved = json.loads((out/name).read_text())
            assert saved["credit_iters"] == 16 and saved["error_lr"] == 0.03
        if not failed:
            assert saved["ledger"]["learning"]["settle_iters"] > 0


@pytest.mark.parametrize("name", ["pc_v0.py", "pc_v1_run.py"])
def test_plan_cli_is_cpu_only_and_propagates_options(name, monkeypatch, capsys):
    r = staged(name)
    monkeypatch.setattr(sys, "argv", [name, "plan", "--credit-iters", "32", "--error-lr", "0.03"])
    r.main()
    p = json.loads(capsys.readouterr().out)
    assert not p["model_execution"] and p["sweep_cost"]["status"] == "pending"
    s = p["credit"].get("arm_settings", p["credit"])
    assert s["SE-E"]["credit_iters"] == 32 and s["SE-E"]["error_lr"] == 0.03
    assert s["SE-A"]["credit_iters"] == 8 and s["SE-A"]["error_lr"] == 0.1


@pytest.mark.parametrize("name", ["pc_v0.py", "pc_v1_run.py"])
def test_group_forwards_options_without_launching_model(name, tmp_path, monkeypatch):
    r = staged(name)
    dest = tmp_path / name
    def new0(path):
        dest.mkdir()
        return dest
    if name == "pc_v0.py":
        monkeypatch.setattr(r, "_new_output", new0)
    else:
        monkeypatch.setattr(r, "new_path", lambda path: (dest, tmp_path / "resources"))
    commands = []
    def fake(cmd, **kw):
        commands.append(cmd)
        return SimpleNamespace(returncode=1)
    monkeypatch.setattr(r.subprocess, "run", fake)
    r.run_group(SimpleNamespace(execute=True, output=str(dest), command="profile", items=10,
                               orders=1, wall_seconds=10, credit_iters=32, error_lr=0.03))
    assert len(commands) == 1
    cmd = commands[0]
    assert cmd[cmd.index("--credit-iters")+1] == "32"
    assert cmd[cmd.index("--error-lr")+1] == "0.03"


def test_fixed_v5_profile_gate_rejects_different_solver(tmp_path):
    r = staged("pc_v1_run.py")
    (tmp_path / "plan.json").write_text(json.dumps(r.plan(True)))
    with pytest.raises(ValueError, match="profile"):
        r.validate_profile(tmp_path, credit_iters=32, error_lr=0.03)


@pytest.mark.parametrize("arm", ["SE-A", "SE-E"])
def test_fixed_v5_constructor_passes_settings_without_changing_query_state(arm, monkeypatch):
    from scripts import r1_61_cell_driver

    from aw.tests.test_pc_v1_run import adapter

    r = staged("pc_v1_run.py")
    original = adapter("SE-A")
    monkeypatch.setattr(r1_61_cell_driver, "construct_owner_adapter", lambda recipe: (original, "tiny-tokenizer"))
    monkeypatch.setattr(r, "checked", lambda binding: dict(adapter_identity=original.identity()))
    actual, tok = r.construct(dict(construction_recipe={}), arm, credit_iters=32, error_lr=0.03)
    assert actual.base.checksum(recompute=True) == original.base.checksum(recompute=True)
    assert r.query_view(actual.learner).state_hash() == original.state_hash()
    assert actual.learner.credit_iters == (32 if arm == "SE-E" else 8)
    assert actual.base.error_lr == (0.03 if arm == "SE-E" else 0.1)
    assert tok == "tiny-tokenizer"


def test_v0_pre_model_failure_still_records_solver(tmp_path, monkeypatch):
    from pccap.harness import lease

    r = staged("pc_v0.py")
    monkeypatch.setattr(r, "_new_output", lambda path: tmp_path)
    monkeypatch.setattr(lease, "gpu_lease", lambda *a, **k: nullcontext(SimpleNamespace(other_cuda_processes=lambda: [])))
    assert jax.default_backend() == "cpu"
    args = SimpleNamespace(execute=True, dataset="zsre", arm="SE-E", output=str(tmp_path),
                           wall_seconds=10, credit_iters=32, error_lr=0.03)
    with pytest.raises(RuntimeError, match="CUDA"):
        r.run_cell(args)
    f = json.loads((tmp_path / "finish.json").read_text())
    assert f["status"] == "failed" and f["credit_iters"] == 32 and f["error_lr"] == 0.03


def synthetic_profile(path):
    cells = [dict(dataset=ds, arm=a, realization=0, order=100, items=10)
             for ds in ("zsre", "counterfact") for a in ("SE-A", "SE-E")]
    plan = dict(population="development", cells=cells, sources={"historical.py": "old-sha"})
    completed = []
    for c in cells:
        f = dict(status="complete", items_completed=10, elapsed_process_seconds=100,
                 ledger=dict(learning=dict(wall_seconds=20), query=dict(wall_seconds=60)))
        folder = path / f"{c['dataset']}-r0-o100-{c['arm']}"
        folder.mkdir()
        (folder / "finish.json").write_text(json.dumps(f))
        (folder / "config.json").write_text(json.dumps(dict(c, population="development", sources=plan["sources"], credit_iters=8, error_lr=0.1)))
        completed.append(dict(cell=c, exit_code=0, finish=f))
    (path / "plan.json").write_text(json.dumps(plan))
    (path / "summary.json").write_text(json.dumps(dict(planned=4, finished=completed)))
    return cells


def test_cost_projection_exact_profile_scope_and_explicit_extrapolation(tmp_path):
    cells = synthetic_profile(tmp_path)
    report = pc_sweep.projected_sweep(tmp_path, cells, [0.1, 0.03])
    assert len(report["variants"]) == 6
    assert report["variants"][0]["fixed_query_seconds"] == 400
    assert report["variants"][0]["scaled_query_seconds"] == 400
    assert report["variants"][4]["fixed_query_seconds"] == pytest.approx(2*100+2*(80+20*33/9))
    assert report["variants"][0]["fixed_query_seconds"] == report["variants"][1]["fixed_query_seconds"]
    enlarged = [dict(c, items=300) for c in cells]
    out = pc_sweep.projected_sweep(tmp_path, enlarged)
    assert out["variants"][0]["fixed_query_seconds"] == 4*(20+600+60)
    assert out["variants"][0]["scaled_query_seconds"] == 4*(20+600+1800)
    # A cost estimate must never treat an incomplete run as a profile.
    summary = json.loads((tmp_path/"summary.json").read_text())
    summary["finished"][0]["exit_code"] = 1
    (tmp_path/"summary.json").write_text(json.dumps(summary))
    with pytest.raises(ValueError, match="inconsistent"):
        pc_sweep.projected_sweep(tmp_path, cells)
