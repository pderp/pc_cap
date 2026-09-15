"""CPU admission/accounting/query-boundary tests; never run GPT-2 training."""
import copy
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import r1_24_control as control  # noqa: E402
import r1_24_runtime as runtime  # noqa: E402


@pytest.mark.parametrize("tokens,seq,source,tail,unused", [(2,128,1,1,0), (3,128,1,1,1), (512,128,256,0,0), (493752,128,246876,92,0)])
def test_exact_budget_no_roundup(tokens, seq, source, tail, unused):
    b = control.match_budget(tokens, seq)
    assert b["source_tokens"] == source
    assert b["tail_sequence_tokens"] == tail
    assert b["charged_forward_pass_tokens"] + unused == tokens
    assert b["full_steps"] * seq + tail == source


@pytest.mark.parametrize("value", [True, -1, 0, 1, 2.5, "100", 2*(control.TRAIN_END+1)])
def test_invalid_or_tail_crossing_budget(value):
    with pytest.raises(ValueError):
        control.match_budget(value)


def test_ledger_excludes_queries_and_rejects_eval_or_duplicate(tmp_path):
    data = {"args": {"tag": "test", "steps": 10}, "theta_path": "fixture", "ledger": {
        "learning": {"tokens": 30}, "query": {"tokens": 11}, "total": {"tokens": 41}}}
    p = tmp_path / "training.json"
    p.write_text(json.dumps(data))
    rows = control.read_budgets([p])
    assert rows[0]["reported_learning_tokens"] == 30
    assert rows[0]["query_tokens_excluded"] == 11
    with pytest.raises(ValueError, match="duplicate"):
        control.read_budgets([p,p])
    data["args"]["steps"] = 0
    q = tmp_path / "evaluation.json"
    q.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        control.read_budgets([q])


def test_prepared_real_manifest_schema_and_tampering():
    m = json.loads(control.DEFAULT_MANIFEST.read_text())
    control.validate_manifest(m)
    assert m["training_executed"] is False
    assert m["gpu_seconds"] == 0
    assert m["budget"]["exact_training_passes_verified"] is False
    bad = copy.deepcopy(m)
    bad["budget"]["arithmetic"]["source_tokens"] += 1
    with pytest.raises(ValueError, match="arithmetic"):
        control.validate_manifest(bad)
    bad = copy.deepcopy(m)
    bad["evaluation"]["drift_scored_positions"] = 16384
    with pytest.raises(ValueError, match="drift"):
        control.validate_manifest(bad)


def test_manifest_module_and_denied_gpu_admission_never_import_jax():
    code = """
import runpy, sys
sys.path.insert(0, 'scripts')
import r1_24_control as c
assert 'jax' not in sys.modules
try:
    c.main(['--gpu', '--run-id', 'should-never-launch'])
except ValueError as e:
    assert 'unreconciled' in str(e)
else:
    raise AssertionError('unreconciled GPU admission accepted')
assert 'jax' not in sys.modules
"""
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not (ROOT / "results/R1/r1_24/should-never-launch").exists()


def test_self_distillation_is_zero_and_teacher_stopped():
    x = jnp.asarray([[.2, -.3, .7]], dtype=jnp.float32)
    value, grads = jax.value_and_grad(runtime.kd_loss, argnums=(0,1))(x,x)
    assert abs(float(value)) < 1e-7
    np.testing.assert_allclose(grads[0], 0, atol=1e-7)
    np.testing.assert_array_equal(grads[1], 0)
    assert float(runtime.kd_loss(x+jnp.asarray([[.2,0.,0.]]), x)) > 0


def test_teacher_forced_prefixes_use_independent_original_prompt_boundaries():
    class Learner:
        def __init__(self):
            self.selected = None
            self.log = []
        def reset_queries(self):
            self.selected = None
        def selection_for(self, ids):
            self.selected = tuple(ids)
        def predict(self, ids):
            self.log.append((tuple(ids), self.selected))
            return SimpleNamespace(logits=np.arange(4,dtype=np.float32))
    cls = runtime.boundary_evaluator_class()
    ev = object.__new__(cls)
    ev.deadline = float("inf")
    learner = Learner()
    seqs = [np.int32([1,2]), np.int32([1,2,3]), np.int32([1,2,3,4])]
    logits = ev._batch_last(learner, seqs, [1,2,2])
    assert logits.shape == (3,4)
    assert learner.log == [((1,2),(1,2)), ((1,2,3),(1,2,3)), ((1,2,3,4),(1,2,3))]


def test_expired_budget_refuses_before_prediction():
    with pytest.raises(TimeoutError):
        runtime.deadline_check(0)
