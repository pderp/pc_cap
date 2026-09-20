"""AW-B query-time wrapper around the frozen R1 learner (``RevisionCap``).

``BoundedCap`` is ``RevisionCap`` with three additions and no change to selection, acquisition, gates or memory:

* after every ``predict`` it exposes ``last_base`` (the unchanged base logits at the predicted position) and
  ``last_cap`` (the unmodified cap logits), taken from the same forward passes the parent already charged;
* if a ``wrapper`` is set, the returned logits are the bounded correction of ``(last_base, last_cap)`` computed by
  ``aw.bounded`` (returned as normalised log-probabilities, which are logits up to a constant);
* with no wrapper it is the parent to the bit (tested), so the unrestricted arm *is* v5.

The base logits are recovered without a second base pass: a thin proxy around the base (the pattern of
``_SelectionPass`` in ``scripts/r1_68c_batched_drift.py``) remembers the logits of each observation pass by the
identity of its retained site tensors, and ``forward_from`` (the corrected partial pass) looks them up from the
``hidden`` it is handed. When the parent returns without a corrected pass (hard null, or beyond the taught answer),
the returned logits are the base logits already.

Stricter gating is not a wrapper: pass ``dataclasses.replace(cfg, null_threshold=t)`` (hard null when
``null_mass >= t``, so *lower* is stricter) and leave ``wrapper=None``.
"""
from __future__ import annotations

from collections import OrderedDict
from typing import Callable

import numpy as np

from aw import bounded
from pccap.revision_v1.learner import ForwardResult, RevisionCap

Wrapper = tuple[str, float] | None  # ("clip", b) | ("mixture", rho) | ("shrink", alpha)


class _RecordingBase:
    """Delegates everything to the real base; remembers observation-pass logits keyed by retained site identity."""

    def __init__(self, base, keep: int = 16):
        self.original = base
        self._by_hidden: OrderedDict[int, np.ndarray] = OrderedDict()
        self._keep = keep
        self.last_partial_base: np.ndarray | None = None
        self.partial_calls = 0

    def __getattr__(self, name):
        return getattr(self.original, name)

    def _remember(self, result):
        hidden = getattr(result, "hidden", None)
        if hidden is None:
            return
        logits = np.asarray(result.logits)
        for bank in (1, 2, 3):
            try:
                h = hidden[bank]
            except (KeyError, IndexError, TypeError):
                continue
            self._by_hidden[id(h)] = logits
            self._by_hidden.move_to_end(id(h))
        while len(self._by_hidden) > 3 * self._keep:
            self._by_hidden.popitem(last=False)

    def forward(self, *args, **kwargs):
        result = self.original.forward(*args, **kwargs)
        self._remember(result)
        return result

    def forward_from(self, first, hidden, *args, **kwargs):
        self.partial_calls += 1
        self.last_partial_base = self._by_hidden.get(id(hidden))
        return self.original.forward_from(first, hidden, *args, **kwargs)


class BoundedCap(RevisionCap):
    name = "R1+AW-B"

    def __init__(self, base, cfg, ledger, params=None, *, wrapper: Wrapper = None):
        self._proxy = _RecordingBase(base)
        super().__init__(self._proxy, cfg, ledger, params)
        self.wrapper = wrapper
        self.last_base: np.ndarray | None = None
        self.last_cap: np.ndarray | None = None
        self.wrapper_counters = {"queries": 0, "corrected": 0, "identity": 0}

    # ------------------------------------------------------------------ wrapper selection
    @property
    def wrapper(self) -> Wrapper:
        return self._wrapper

    @wrapper.setter
    def wrapper(self, value: Wrapper) -> None:
        if value is not None:
            kind, param = value
            if kind not in bounded.WRAPPERS:
                raise ValueError(f"unknown wrapper {kind!r}")
            float(param)
        self._wrapper = value

    def _apply(self, base_logits: np.ndarray, cap_logits: np.ndarray) -> np.ndarray:
        kind, param = self._wrapper
        fn: Callable = bounded.WRAPPERS[kind]
        return fn(bounded.log_normalise(base_logits), bounded.log_normalise(cap_logits), float(param))

    # ------------------------------------------------------------------ read path
    def predict(self, ids, full: bool = False) -> ForwardResult:
        if full and self._wrapper is not None:
            raise NotImplementedError("wrapped predictions are last-position only")
        before = self._proxy.partial_calls
        result = super().predict(ids, full=full)
        cap_logits = np.asarray(result.logits)
        self.wrapper_counters["queries"] += 1
        if self._proxy.partial_calls > before:  # a corrected partial pass happened: recover its observation logits
            self.wrapper_counters["corrected"] += 1
            base_logits = self._proxy.last_partial_base
            if base_logits is None:
                raise RuntimeError("corrected pass without a remembered observation pass; wrapper cannot bound it")
            if base_logits.shape != cap_logits.shape:  # full-sequence observation, last-position correction
                base_logits = base_logits[-1] if base_logits.ndim == cap_logits.ndim + 1 else base_logits
        else:  # hard null or beyond the taught answer: the parent already returned the base logits
            self.wrapper_counters["identity"] += 1
            base_logits = cap_logits
        self.last_base, self.last_cap = base_logits, cap_logits
        if self._wrapper is None or base_logits is cap_logits:
            return result
        wrapped = self._apply(base_logits, cap_logits).astype(cap_logits.dtype, copy=False)
        return ForwardResult(logits=wrapped, sites=result.sites, cost=result.cost)
