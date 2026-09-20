"""CPU behavioral tests of acquisition, fallback, identity and exact R1 parity."""

import copy
from dataclasses import asdict

import pccap  # noqa: F401

# isort: split

import numpy as np
import pytest
from tests.revision_v1.tiny_base import TinyBase

from aw.interface import InterfaceCap, InterfaceConfig, _MaskedBase
from aw.tests.test_wrapper import _cfg, _queries, _support
from pccap.contracts import SiteId
from pccap.harness.ledger import Ledger
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.controller import aggregate, bound_writes, raw_writes
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.reader import param_count


def delta_cfg():
    cfg = _cfg()
    cfg.fast = FastConfig(steps=0, delta_steps=5, delta_lr=0.1, tau=0.1)
    return cfg


@pytest.mark.parametrize("delta", [False, True])
def test_all_site_exact_acquisition_restore_and_predictions(delta):
    cfg = delta_cfg() if delta else _cfg()
    a, b = RevisionCap(TinyBase(), cfg, Ledger()), InterfaceCap(TinyBase(), cfg, Ledger())
    for i in range(2):
        ta, ca = adapt_record(a, _support(i), a.cfg.fast)
        tb, cb = adapt_record(b, _support(i), b.cfg.fast)
        assert asdict(ta) == asdict(tb)
        assert asdict(ca) == asdict(cb)
    assert a.state_hash() == b.state_hash()
    b.import_state(a.export_state())
    for q in _queries():
        x, y = a.predict(q), b.predict(q)
        assert np.array_equal(x.logits, y.logits)
        assert asdict(x.cost) == asdict(y.cost)
    assert a.cost_counters == b.cost_counters


@pytest.mark.parametrize("sites", [(3,), (2,), (2, 3)])
def test_masked_delta_acquisition_and_controller(sites):
    base = TinyBase()
    seen = []
    original = base.adjoint

    def track(ids, target, writes, **kw):
        seen.extend(writes)
        return original(ids, target, writes, **kw)

    base.adjoint = track
    cap = InterfaceCap(base, delta_cfg(), Ledger(), interface=InterfaceConfig(write_sites=sites))
    trace, _ = adapt_record(cap, _support(0), cap.cfg.fast)
    assert trace.steps_used <= 5 * len(_support(0).answer_ids)
    assert seen
    for w in seen:
        if w.site.bank not in sites:
            assert np.count_nonzero(w.vector) == 0
    assert cap.store.records[0].delta is not None
    dl = cap.store.records[0].delta
    inactive = [m - 1 for m in (1, 2, 3) if m not in sites]
    assert np.count_nonzero(dl[:, inactive]) == 0
    assert all(aggregate(w, cap.cfg.controller) <= 0.300001 for w in dl)
    # Guard rejects caller-injected inactive deltas, including nonfinite slots.
    corrupted = dl.copy()
    corrupted[:, inactive] = np.nan
    with pytest.raises(ValueError):
        cap.store.set_delta(cap.store.records[0].record_id, corrupted)
    calls = []
    old = base.forward_from

    def forward(bank, hidden, ids, writes, **kw):
        calls.append((bank, writes))
        return old(bank, hidden, ids, writes, **kw)

    base.forward_from = forward
    cap.predict(np.asarray(_support(0).prompt_ids))
    assert calls and calls[0][0] == min(sites)
    assert {w.site.bank for w in calls[0][1]} == set(sites)
    q = np.ones(cap.cfg.reader.width, np.float32)
    code = np.ones(cap.cfg.reader.d_code, np.float32)
    W = np.asarray(cap.jit_writes(cap.params["controller"], q, code, 1.0))
    raw = np.asarray(raw_writes(cap.params["controller"], cap.cfg.controller, q, code)).copy()
    raw[inactive] = 0
    expected = np.asarray(bound_writes(raw, cap.cfg.controller)[0])
    assert np.allclose(W, expected, rtol=1e-6, atol=1e-8)
    assert np.count_nonzero(W[inactive]) == 0
    assert cap.interface_accounting()["delta_allocated_bytes"] == dl.nbytes
    clone = InterfaceCap(base, delta_cfg(), Ledger(), params=cap.params, interface=cap.interface)
    clone.import_state(cap.export_state())
    assert clone.state_hash() == cap.state_hash()


def test_adjoint_is_masked_before_norm_even_nonfinite_inactive():
    class Fake:
        def adjoint(self, *args, **kw):
            return {SiteId(m, m, 0): np.full(2, np.nan if m < 3 else 1.0) for m in (1, 2, 3)}

    grads = _MaskedBase(Fake(), (3,)).adjoint([1], 1, [])
    assert all(np.array_equal(g, np.zeros(2)) for s, g in grads.items() if s.bank < 3)


def test_pruning_counts_and_changed_identity_clears_queries():
    original = RevisionCap(TinyBase(), _cfg(), Ledger())
    cap = InterfaceCap(
        original.base,
        _cfg(),
        Ledger(),
        params=original.params,
        interface=InterfaceConfig(read_taps=(2, 3)),
    )
    assert set(cap.params["reader"]["tap"]) == {"2", "3"}
    removed = param_count(original.params["reader"]["tap"]["1"])
    assert original.n_params - cap.n_params == removed
    assert (
        original.memory_bytes().allocated_bytes - cap.memory_bytes().allocated_bytes == 4 * removed
    )
    cap.predict(np.int32([1, 2, 3]))
    assert cap._sel
    cap.interface = InterfaceConfig(read_taps=(3,))
    with pytest.raises(RuntimeError, match="fresh learner"):
        cap.predict(np.int32([1, 2, 3]))
    assert not cap._sel


def test_incompatible_snapshot_refused_without_mutation():
    cap = InterfaceCap(
        TinyBase(), delta_cfg(), Ledger(), interface=InterfaceConfig(write_sites=(3,))
    )
    adapt_record(cap, _support(0), cap.cfg.fast)
    st = copy.deepcopy(cap.export_state())
    before = cap.state_hash()
    key = next(k for k in st.arrays if k.startswith("delta"))
    st.arrays[key][:, 0] = 1
    with pytest.raises(ValueError):
        cap.import_state(st)
    assert cap.state_hash() == before


@pytest.mark.parametrize(
    "cfg", [InterfaceConfig(read_taps=(3,)), InterfaceConfig(write_sites=(3,))]
)
def test_hard_null_no_corrected_pass(cfg):
    cap = InterfaceCap(TinyBase(), _cfg(null_threshold=0.0), Ledger(), interface=cfg)
    adapt_record(cap, _support(0), cap.cfg.fast)
    p = np.int32(_support(0).prompt_ids)
    assert np.array_equal(cap.predict(p).logits, cap.raw_base.forward(p).logits)
    assert cap.cost_counters["corrected_partial_passes"] == 0


def test_storage_add_rejects_inactive_and_clear_delta_keeps_parent_api():
    cap = InterfaceCap(
        TinyBase(), delta_cfg(), Ledger(), interface=InterfaceConfig(write_sites=(3,))
    )
    adapt_record(cap, _support(0), cap.cfg.fast)
    rec = cap.store.records[0]
    bad = copy.deepcopy(rec)
    bad.record_id = "injected"
    bad.delta[:, 0] = 1
    with pytest.raises(ValueError, match="inactive"):
        cap.store.add(bad)
    assert len(cap.store.records) == 1
    cap.store.set_delta(rec.record_id, None)
    assert rec.delta is None
