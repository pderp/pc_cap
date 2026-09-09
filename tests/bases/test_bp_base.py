"""S0-04 verification (plan §6.3): the JAX GPT-2 BP wrapper.

(a) no-write logits vs the HF PyTorch oracle (REF-01 fixture; skipped with a recorded reason
    when the fixture is absent) and vs an independent NumPy float64 reference;
(b) site tensors equal the reference block outputs 3/7/11 (pre-ln_f);
(c) a write at bank 1 changes sites 2, 3 and the logits; a write at bank 3 changes only logits;
    writes at p != last raise;
(d) forward_from equals a full forward with the same writes;
(e) checksum unchanged after 100 forwards;
(f) prompt lengths 1..128 behave; cost counters increment per call.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.contracts import SiteId, Write

from . import ref_numpy_gpt2 as ref

pytestmark = pytest.mark.gpu

ROOT = Path(__file__).resolve().parents[2]
ORACLE = Path(pccap.ASSETS_ROOT) / "reference" / "gpt2"
RESULTS = ROOT / "results" / "S0" / "controls"

PROMPTS = [
    "The capital of France is",
    "Albert Einstein was born in",
    "In 1492, Columbus sailed",
    "def fibonacci(n):",
    "The quick brown fox jumps over the lazy dog.",
    "Water boils at",
    "Hello",
    "A",
]


@pytest.fixture(scope="module")
def base():
    if not (g.DEFAULT_SNAPSHOT / "model.safetensors").exists():
        pytest.skip("GPT-2 snapshot absent (DATA-00)")
    return BPBase()


@pytest.fixture(scope="module")
def params_np():
    return g.load_params_numpy()


@pytest.fixture(scope="module")
def tok():
    return g.load_tokenizer()


def enc(tok, s):
    return np.asarray(tok.encode(s).ids, dtype=np.int32)


def _record(name: str, payload: dict):
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(payload, indent=1))


# ------------------------------------------------------------------ (a) + (b) numpy reference
def test_a_b_numpy_reference(base, params_np, tok):
    worst = 0.0
    site_worst = 0.0
    agree = 0
    total = 0
    for s in PROMPTS[:6]:
        ids = enc(tok, s)
        fr = base.forward(ids)
        logits = np.asarray(fr.logits, dtype=np.float64)
        ref_logits, hidden = ref.forward(params_np, ids, return_hidden=True)
        worst = max(worst, float(np.abs(logits - ref_logits).max()))
        agree += int((logits.argmax(-1) == ref_logits.argmax(-1)).sum())
        total += len(ids)
        for site, row in fr.sites.items():
            site_worst = max(site_worst, float(np.abs(np.asarray(row, np.float64) - hidden[site.block][-1]).max()))
    _record("s0_04_numpy_reference.json", {"max_abs_logit_diff_fp32_vs_f64": worst,
                                          "max_abs_site_diff": site_worst, "argmax_agree": agree, "positions": total})
    assert worst < 2e-2, worst
    assert site_worst < 2e-2, site_worst
    assert agree == total


# ------------------------------------------------------------------ (a) HF oracle (REF-01)
def test_a_hf_oracle(base):
    fx = ORACLE / "logits_256.npz"
    if not fx.exists():
        _record("s0_04_hf_oracle.json", {"status": "unavailable", "reason": "REF-01 fixture absent", "path": str(fx)})
        pytest.skip("REF-01 oracle fixture absent; recorded as unavailable")
    z = np.load(fx, allow_pickle=True)
    worst, site_worst, agree, total = 0.0, 0.0, 0, 0
    n_prompts = int(z["n_prompts"]) if "n_prompts" in z else 256
    for i in range(n_prompts):
        ids = z[f"ids_{i}"].astype(np.int32)
        fr = base.forward(ids)
        logits = np.asarray(fr.logits, np.float64)
        rl = z[f"logits_{i}"].astype(np.float64)
        worst = max(worst, float(np.abs(logits - rl).max()))
        agree += int((logits.argmax(-1) == rl.argmax(-1)).sum())
        total += len(ids)
        for site, row in fr.sites.items():
            hs = z[f"hidden_{i}_{site.block}"].astype(np.float64)[-1]
            site_worst = max(site_worst, float(np.abs(np.asarray(row, np.float64) - hs).max()))
    _record("s0_04_hf_oracle.json", {"status": "ok", "max_abs_logit_diff": worst, "max_abs_site_diff": site_worst,
                                    "argmax_agree": agree, "positions": total, "n_prompts": n_prompts})
    assert worst <= 1e-3, worst  # SD-14 tolerance (fp32 XLA vs fp32 torch-CPU)
    assert site_worst <= 1e-3, site_worst
    assert agree == total


# ------------------------------------------------------------------ (c) writes
def test_c_writes(base, tok):
    ids = enc(tok, PROMPTS[0])
    p = len(ids) - 1
    base0 = base.forward(ids)
    rng = np.random.default_rng(0)
    v = (rng.standard_normal(base.d) * 5.0).astype(np.float32)
    w1 = base.forward(ids, [Write(SiteId(1, 3, p), v)])
    w3 = base.forward(ids, [Write(SiteId(3, 11, p), v)])
    s = lambda fr, m: np.asarray(fr.sites[SiteId(m, g.BANK_BLOCK[m], p)])  # noqa: E731
    # bank-1 write: site 1 (pre-write) unchanged, sites 2 and 3 change, logits change
    assert np.array_equal(s(w1, 1), s(base0, 1))
    assert not np.array_equal(s(w1, 2), s(base0, 2))
    assert not np.array_equal(s(w1, 3), s(base0, 3))
    assert not np.array_equal(np.asarray(w1.logits), np.asarray(base0.logits))
    # bank-3 write: all pre-write sites identical, logits change only at position p
    for m in (1, 2, 3):
        assert np.array_equal(s(w3, m), s(base0, m))
    d = np.abs(np.asarray(w3.logits) - np.asarray(base0.logits))
    assert d[p].max() > 0 and (d[:p].max() == 0 if p > 0 else True)
    # writes at a position other than p are refused
    with pytest.raises(ValueError):
        base.forward(ids, [Write(SiteId(1, 3, 0), v)]) if p != 0 else (_ for _ in ()).throw(ValueError())
    # zero write is an exact no-op (SD-10)
    z = base.forward(ids, [Write(SiteId(2, 7, p), np.zeros(base.d, np.float32))])
    assert np.array_equal(np.asarray(z.logits), np.asarray(base0.logits))


# ------------------------------------------------------------------ (d) forward_from
def test_d_forward_from(base, tok):
    ids = enc(tok, PROMPTS[1])
    p = len(ids) - 1
    rng = np.random.default_rng(1)
    writes = [Write(SiteId(m, g.BANK_BLOCK[m], p), rng.standard_normal(base.d).astype(np.float32)) for m in (1, 2, 3)]
    full = base.forward(ids, writes, retain_sites=True)
    worst = 0.0
    for m in (1, 2, 3):
        part = base.forward_from(m, full.hidden[m], ids, writes)
        worst = max(worst, float(np.abs(np.asarray(part.logits) - np.asarray(full.logits)).max()))
        for mm in range(m + 1, 4):
            sid = SiteId(mm, g.BANK_BLOCK[mm], p)
            worst = max(worst, float(np.abs(np.asarray(part.sites[sid]) - np.asarray(full.sites[sid])).max()))
    _record("s0_04_forward_from.json", {"max_abs_diff_partial_vs_full": worst})
    assert worst <= 1e-4, worst


# ------------------------------------------------------------------ (e) checksum
def test_e_checksum_stable(base, tok):
    before = base.checksum()
    assert before == base.checksum(recompute=False)
    ids = enc(tok, PROMPTS[2])
    for _ in range(100):
        base.forward(ids, phase="query")
    assert base.checksum() == before
    _record("s0_04_checksum.json", {"sha256": before, "forwards": 100})


# ------------------------------------------------------------------ (f) lengths + cost
@pytest.mark.parametrize("n", [1, 2, 3, 5, 8, 16, 17, 64, 128])
def test_f_lengths(base, params_np, n):
    rng = np.random.default_rng(n)
    ids = rng.integers(0, base.vocab, size=n).astype(np.int32)
    fr = base.forward(ids)
    assert fr.logits.shape == (n, base.vocab)
    assert np.isfinite(np.asarray(fr.logits)).all()
    if n <= 17:
        rl = ref.forward(params_np, ids)
        assert np.abs(np.asarray(fr.logits, np.float64) - rl).max() < 2e-2


def test_cost_counters(tok):
    from pccap.harness.ledger import Ledger

    ledger = Ledger()
    b = BPBase(ledger=ledger)
    ids = enc(tok, PROMPTS[3])
    b.forward(ids)
    b.forward(ids, phase="query")
    fr = b.forward(ids, retain_sites=True)
    b.forward_from(2, fr.hidden[2], ids)
    b.adjoint(ids, 0)
    t = ledger.totals()
    assert t["learning"]["full_forwards"] == 3 and t["query"]["full_forwards"] == 1
    assert t["learning"]["partial_forwards"] == 1 and t["learning"]["reverses"] == 1
    assert t["total"]["accel_seconds"] > 0
