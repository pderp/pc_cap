"""BoundedCap on the tiny CPU base: unrestricted equals RevisionCap to the bit (same logits, same cost counters) on the
hard-null, cached-prompt and corrected paths; a wrapper equals the oracle applied to the recorded base/cap pair and
respects the 2b bound; a stricter null threshold is a config change, not a wrapper."""
from __future__ import annotations

import dataclasses
import os
import sys

os.environ.setdefault("JAX_PLATFORMS", "cpu")

import numpy as np  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from aw import bounded as B  # noqa: E402
from aw.wrapper import BoundedCap  # noqa: E402
from pccap.harness.ledger import Ledger  # noqa: E402
from pccap.revision_v1.adapt import FastConfig, adapt_record  # noqa: E402
from pccap.revision_v1.contracts import SupportExample  # noqa: E402
from pccap.revision_v1.controller import ControllerConfig  # noqa: E402
from pccap.revision_v1.learner import RevisionCap, RevisionConfig  # noqa: E402
from pccap.revision_v1.reader import ReaderConfig  # noqa: E402
from tests.revision_v1.tiny_base import CFG, TinyBase  # noqa: E402

RC = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
CC = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))


def _cfg(**kw):
    return RevisionConfig(reader=RC, controller=CC, fast=FastConfig(steps=2, lr=1e-2), null_threshold=kw.pop("null_threshold", 1.01), **kw)


def _support(i: int):
    r = np.random.default_rng(i)
    return SupportExample(record_id=f"s{i}", fact_id=f"f{i}", revision=1, entity_id="e", family_id="g",
                          prompt_ids=tuple(int(x) for x in r.integers(1, 60, size=7)), answer_ids=tuple(int(x) for x in r.integers(1, 60, size=3)))


def _taught(cls, **kw):
    base = TinyBase()
    cap = cls(base, _cfg(**kw), Ledger())
    for i in range(2):
        adapt_record(cap, _support(i), cap.cfg.fast)
    cap.reset_queries()
    return base, cap


def _queries():
    s = _support(1)
    prompt = np.asarray(s.prompt_ids, np.int32)
    return [prompt, np.concatenate([prompt, np.int32(s.answer_ids[:1])]), np.concatenate([prompt, np.int32(s.answer_ids)]),
            np.int32([3, 9, 27, 40, 41])]


def test_unrestricted_is_the_parent_to_the_bit():
    _, ref = _taught(RevisionCap)
    _, cap = _taught(BoundedCap)
    for q in _queries():
        a, b = ref.predict(q), cap.predict(q)
        assert np.array_equal(np.asarray(a.logits), np.asarray(b.logits))
        assert np.array_equal(cap.last_cap, np.asarray(b.logits))
    assert ref.cost_counters == cap.cost_counters
    assert cap.wrapper_counters["queries"] == len(_queries())
    assert cap.wrapper_counters["corrected"] >= 1


def test_hard_null_path_is_identity_and_base_equals_cap():
    _, cap = _taught(BoundedCap, null_threshold=0.0)  # every query hard-nulled
    cap.wrapper = ("clip", 0.5)
    base = cap._proxy.original
    for q in _queries():
        out = np.asarray(cap.predict(q).logits)
        assert np.array_equal(out, np.asarray(base.forward(q).logits))
        assert cap.last_base is cap.last_cap
    assert cap.wrapper_counters["corrected"] == 0


def test_wrapper_matches_oracle_and_bound():
    _, plain = _taught(BoundedCap)
    _, cap = _taught(BoundedCap)
    cap.wrapper = ("clip", 0.5)
    for q in _queries():
        v5 = np.asarray(plain.predict(q).logits)
        out = np.asarray(cap.predict(q).logits)
        assert np.array_equal(cap.last_cap, v5)  # the wrapper never changes the cap's own computation
        if cap.last_base is cap.last_cap:
            assert np.array_equal(out, v5)
            continue
        expect = B.clip_tilt(B.log_normalise(cap.last_base), B.log_normalise(v5), 0.5)
        assert np.allclose(out, expect, atol=1e-6)
        lp0 = B.log_normalise(cap.last_base)
        assert (lp0 - B.log_normalise(out)).max() <= 1.0 + 1e-6
    assert cap.wrapper_counters["corrected"] >= 1
    cap.wrapper = ("clip", np.inf)
    for q in _queries():
        assert np.allclose(np.asarray(cap.predict(q).logits), B.log_normalise(np.asarray(plain.predict(q).logits)), atol=1e-6)


def test_stricter_threshold_is_a_config_change():
    _, loose = _taught(BoundedCap, null_threshold=1.01)
    _, strict = _taught(BoundedCap, null_threshold=0.0)
    assert dataclasses.replace(loose.cfg, null_threshold=0.0).null_threshold == strict.cfg.null_threshold
    for q in _queries():
        loose.predict(q)
        strict.predict(q)
    assert loose.wrapper_counters["corrected"] > strict.wrapper_counters["corrected"] == 0
