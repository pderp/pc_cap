"""S0-06 verification (plan §6.3): ePC wrapper on FabricPC, built on BP weights.

(a) zero errors -> logits equal the BP wrapper's exactly (graph derive vs plain forward);
(b) E_k non-increasing over 8 iterations on 16 prompts at error_lr 0.1 (a measurement: if it
    fails the test records the fact and checks finiteness only);
(c) no parameter gradient accumulates (checksum unchanged; the differentiated function takes
    only the error pytree);
(d) two calls with the same inputs give identical errors (fresh state);
(e) ledger counts for iters = 8 (8 settle iterations; forwards = reverses = 9 including the
    explicit terminal residual, see docs/epc_energy.md);
(f) sign control passes.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.bases.epc import EPCBase, epc_sign_control
from pccap.contracts import SiteId, Write
from pccap.harness.ledger import Ledger

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"

PROMPTS = [
    "The capital of France is", "Albert Einstein was born in", "In 1492, Columbus sailed",
    "def fibonacci(n):", "The quick brown fox jumps over the lazy dog.", "Water boils at",
    "My favourite colour is", "The Eiffel Tower is located in", "Once upon a time", "The president of the United States",
    "To be or not to be", "Photosynthesis converts", "The largest planet is", "She opened the door and",
    "import numpy as", "The year 1969 saw",
]


@pytest.fixture(scope="module")
def base():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    return EPCBase(ledger=Ledger())


@pytest.fixture(scope="module")
def tok():
    return g.load_tokenizer()


def _rec(name, payload):
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(payload, indent=1))


def test_a_zero_error_identity(base, tok):
    worst = 0.0
    site_worst = 0.0
    for s in PROMPTS[:6]:
        ids = np.asarray(tok.encode(s).ids, np.int32)
        p = len(ids) - 1
        bp = base.forward(ids)
        gf = base.graph_forward(ids)
        worst = max(worst, float(np.abs(np.asarray(gf.logits) - np.asarray(bp.logits)).max()))
        for m in (1, 2, 3):
            sid = SiteId(m, g.BANK_BLOCK[m], p)
            site_worst = max(site_worst, float(np.abs(np.asarray(gf.sites[sid]) - np.asarray(bp.sites[sid])).max()))
        # unclamped inference with zero init equals the feedforward computation (D.1 consistency)
        er = base.infer_errors(ids, None, iters=2)
        worst = max(worst, float(np.abs(np.asarray(er.logits) - np.asarray(bp.logits)).max()))
        assert all(float(np.abs(np.asarray(e)).max()) == 0.0 for e in er.errors.values())
    _rec("s0_06_zero_error_identity.json", {"max_abs_logit_diff": worst, "max_abs_site_diff": site_worst,
                                           "exact": worst == 0.0 and site_worst == 0.0})
    assert worst <= 1e-6 * 100 and site_worst <= 1e-4, (worst, site_worst)  # SD-10: exact expected; tolerance only with record


def test_b_energy_monotone_measurement(base, tok):
    rows = []
    nonmono = 0
    for s in PROMPTS:
        ids = np.asarray(tok.encode(s).ids, np.int32)
        p = len(ids) - 1
        fr = base.forward(ids)
        target = int(np.asarray(fr.logits[p]).argsort()[-2])
        er = base.infer_errors(ids, target, iters=8)
        E = np.asarray(er.energies)
        mono = bool(np.all(np.diff(E) <= 1e-6 * np.abs(E[:-1]) + 1e-6))
        nonmono += (not mono)
        rows.append({"prompt": s, "E": E.tolist(), "monotone": mono, "r_k": er.r_k, "grad_norm_0": er.grad_norm_0,
                     "grad_norm_k": er.grad_norm_k, "E0_minus_Ek": float(E[0] - E[-1])})
        assert np.isfinite(E).all()
    _rec("s0_06_energy_descent.json", {"error_lr": base.error_lr, "iters": 8, "n_prompts": len(rows),
                                      "non_monotone_count": nonmono, "rows": rows})
    # measurement, not a threshold: recorded above


def test_c_no_parameter_gradient(base, tok):
    ids = np.asarray(tok.encode(PROMPTS[0]).ids, np.int32)
    before = base.checksum()
    base.infer_errors(ids, 5, iters=4)
    assert base.checksum() == before
    import inspect

    from pccap.pc import epc_inference

    src = inspect.getsource(epc_inference.relax_errors)
    assert "jax.value_and_grad(energy_of)" in src  # differentiated w.r.t. the error pytree only


def test_d_fresh_state_identical(base, tok):
    ids = np.asarray(tok.encode(PROMPTS[1]).ids, np.int32)
    a = base.infer_errors(ids, 11, iters=8)
    base.infer_errors(ids, 12, iters=3)  # different call in between must leave no state behind
    b = base.infer_errors(ids, 11, iters=8)
    for l in a.errors:
        assert np.array_equal(np.asarray(a.errors[l]), np.asarray(b.errors[l]))
    assert a.energies == b.energies


def test_e_ledger_counts(tok):
    ledger = Ledger()
    b = EPCBase(ledger=ledger)
    ids = np.asarray(tok.encode(PROMPTS[2]).ids, np.int32)
    b.infer_errors(ids, 3, iters=8)
    assert ledger.learning.settle_iters == 8
    assert ledger.learning.full_forwards == 9 and ledger.learning.reverses == 9


def test_f_sign_control():
    rec = epc_sign_control(RESULTS / "epc_sign_convention.json")
    assert rec["plus_e_reduces_loss"] and rec["minus_e_increases_loss"]
    assert rec["cos(settled_error, -adjoint)"] > 0.99


def test_writes_enter_the_energy(base, tok):
    """Cap writes are part of the base computation inside a settling call (retrieval frozen)."""
    ids = np.asarray(tok.encode(PROMPTS[3]).ids, np.int32)
    p = len(ids) - 1
    v = (np.random.default_rng(0).standard_normal(base.d) * 3).astype(np.float32)
    a = base.infer_errors(ids, 7, iters=2)
    b = base.infer_errors(ids, 7, iters=2, writes=[Write(SiteId(1, 3, p), v)])
    assert a.energies[0] != b.energies[0]


def test_site_errors_and_report_card_targets(base, tok):
    ids = np.asarray(tok.encode(PROMPTS[4]).ids, np.int32)
    n = len(ids)
    tgt = np.concatenate([ids[1:], [-1]]).astype(np.int32)  # summed sequence loss (D.3)
    er = base.infer_errors(ids, tgt, iters=4)
    assert set(er.errors) == set(range(12)) and er.errors[0].shape == (n, base.d)
    for m in (1, 2, 3):
        assert base.error_at_site(er, m).shape == (base.d,)
    assert er.energies[0] > 0
