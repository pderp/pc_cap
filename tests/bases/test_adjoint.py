"""S0-05: hidden-site adjoints (one reverse pass, frozen parameters, finite-difference agreement)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.contracts import SiteId, Write
from pccap.harness.ledger import Ledger

from . import ref_numpy_gpt2 as ref

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "results" / "S0" / "controls"

PROMPTS = [
    "The capital of France is", "Albert Einstein was born in", "In 1492, Columbus sailed",
    "def fibonacci(n):", "The quick brown fox jumps over the lazy dog.", "Water boils at",
    "My favourite colour is", "The Eiffel Tower is located in",
]


@pytest.fixture(scope="module")
def base():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent")
    return BPBase(ledger=Ledger())


@pytest.fixture(scope="module")
def tok():
    return g.load_tokenizer()


@pytest.fixture(scope="module")
def params_np():
    return g.load_params_numpy()


def _ce64(logits64, target):
    row = logits64[-1]
    m = row.max()
    return float(np.log(np.exp(row - m).sum()) + m - row[target])


def test_finite_difference_agreement(base, tok, params_np):
    """Directional derivative along d = -g/|g| at each site (fp32 JAX adjoint) agrees with a
    central finite difference of step 1e-2 taken in the float64 NumPy reference model
    (tests/bases/ref_numpy_gpt2.py, writes at block outputs). Relative error < 1e-3.

    The same finite difference taken in the fp32 wrapper itself is recorded as a secondary
    measurement: its error is dominated by the fp32 logit noise floor (~1e-4 abs / 2*step),
    which for |g| ~ 0.1 exceeds 1e-3 relative at steps <= 0.1 (see docs/tasks/S0-05.md).
    """
    step = 1e-2
    worst64 = 0.0
    worst32 = 0.0
    rows = []
    for text in PROMPTS:
        ids = np.asarray(tok.encode(text).ids, dtype=np.int32)
        p = len(ids) - 1
        fr = base.forward(ids)
        target = int(np.asarray(fr.logits[p]).argsort()[-2])  # second-best token: nonzero gradient
        grads, L, _ = base.adjoint(ids, target, return_loss=True)
        for site, gsite in grads.items():
            gnp = np.asarray(gsite, np.float64)
            gn = np.linalg.norm(gnp)
            d = -gnp / gn
            analytic = float(np.dot(gnp, d))  # = -|g|
            lp = _ce64(ref.forward(params_np, ids, writes={site.block: step * d}), target)
            lm = _ce64(ref.forward(params_np, ids, writes={site.block: -step * d}), target)
            fd64 = (lp - lm) / (2 * step)
            rel64 = abs(fd64 - analytic) / abs(analytic)
            plus, _ = base.loss(ids, target, [Write(site, (step * d).astype(np.float32))])
            minus, _ = base.loss(ids, target, [Write(site, (-step * d).astype(np.float32))])
            fd32 = (plus - minus) / (2 * step)
            rel32 = abs(fd32 - analytic) / abs(analytic)
            worst64 = max(worst64, rel64)
            worst32 = max(worst32, rel32)
            rows.append({"prompt": text, "bank": site.bank, "analytic": analytic, "fd_f64_ref": fd64,
                         "rel_err_f64_ref": rel64, "fd_fp32_wrapper": fd32, "rel_err_fp32_wrapper": rel32,
                         "loss": L, "site_norm": float(np.linalg.norm(np.asarray(fr.sites[site])))})
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "s0_05_finite_difference.json").write_text(json.dumps(
        {"step": step, "worst_rel_err_vs_f64_reference": worst64, "worst_rel_err_fp32_wrapper_fd": worst32,
         "assertion": "f64 reference < 1e-3", "rows": rows}, indent=1))
    assert worst64 < 1e-3, worst64


def test_one_reverse_per_call_and_frozen_params(base, tok):
    ids = np.asarray(tok.encode(PROMPTS[0]).ids, dtype=np.int32)
    before = base.checksum()
    r0 = base.ledger.learning.reverses
    f0 = base.ledger.learning.full_forwards
    base.adjoint(ids, 5)
    assert base.ledger.learning.reverses == r0 + 1
    assert base.ledger.learning.full_forwards == f0 + 1
    assert base.checksum() == before  # parameters received no update (they are immutable arrays)


def test_adjoint_shapes_and_sites(base, tok):
    ids = np.asarray(tok.encode(PROMPTS[1]).ids, dtype=np.int32)
    p = len(ids) - 1
    grads = base.adjoint(ids, 7)
    assert set(grads) == {SiteId(1, 3, p), SiteId(2, 7, p), SiteId(3, 11, p)}
    for v in grads.values():
        assert v.shape == (base.d,) and np.isfinite(np.asarray(v)).all()


def test_adjoint_at_written_state(base, tok):
    """The adjoint is taken at the post-write residual: with a write present the gradient differs."""
    ids = np.asarray(tok.encode(PROMPTS[2]).ids, dtype=np.int32)
    p = len(ids) - 1
    g0 = base.adjoint(ids, 3)
    v = (np.random.default_rng(0).standard_normal(base.d) * 3).astype(np.float32)
    g1 = base.adjoint(ids, 3, [Write(SiteId(1, 3, p), v)])
    assert not np.array_equal(np.asarray(g0[SiteId(2, 7, p)]), np.asarray(g1[SiteId(2, 7, p)]))
