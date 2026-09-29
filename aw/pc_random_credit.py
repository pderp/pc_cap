"""DEC-075 random-direction credit, using the unchanged transactional learner.

The reference signal is the corrected eight-step error. Its norm, zero-signal
behavior and actual 9-forward/9-reverse cost are retained. Only orientation is
randomized, independently per bank and credit call. No installed module is
patched. The separate RNG is included in snapshots and leaves eviction RNG alone.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
from types import FunctionType

import numpy as np

from pccap.cap import learn
from pccap.cap.cap import Cap
from pccap.harness.snapshot import LearnerState

TREATMENT = dict(
    credit="random",
    arm="SE-R",
    reference_credit="error",
    reference_credit_iters=8,
    error_lr=0.1,
    orientation="independent isotropic Gaussian direction per bank per credit call",
    norm="reference raw site-error norm before unchanged unit-direction transport",
    rng="NumPy PCG64, SeedSequence([cap_seed, 0x50433132]); separately snapshotted",
    matching="same true eight-step error computation; 9 forwards + 9 reverses per credit call",
    update_rule="unchanged transactional line search, thresholds and R=5 per-prefix budget",
)


class RandomTransport:
    def __init__(self, transport, rng):
        self.transport, self.rng = transport, rng

    def direction(self, signal, site, allowed_subspace=None):
        signal = np.asarray(signal, np.float32)
        norm = float(np.linalg.norm(signal.astype(np.float64)))
        if not np.isfinite(norm):
            raise FloatingPointError("nonfinite reference credit norm")
        if norm == 0:
            randomized = np.zeros_like(signal)
        else:
            vector = self.rng.standard_normal(signal.shape)
            length = float(np.linalg.norm(vector))
            if length == 0 or not np.isfinite(length):
                raise FloatingPointError("invalid isotropic draw")
            randomized = (vector * (norm / length)).astype(np.float32)
        return self.transport.direction(randomized, site, allowed_subspace)


def private_kernel():
    scope = dict(learn.__dict__)

    def clone(fn):
        copied = FunctionType(fn.__code__, scope, fn.__name__, fn.__defaults__, fn.__closure__)
        copied.__kwdefaults__ = fn.__kwdefaults__
        return copied

    reference = clone(learn.directions_at)

    def directions_at(cap, ids, target, writes, transport, phase="learning"):
        directions_at.last_extra_cost = None
        return reference(
            cap, ids, target, writes, RandomTransport(transport, cap.credit_rng), phase
        )

    scope["directions_at"] = directions_at
    for name in ("_charge_credit", "round_update", "update_item"):
        scope[name] = clone(getattr(learn, name))
    return scope


class RandomCreditCap(Cap):
    own_update_path = True

    def __init__(self, base, cfg, ledger=None):
        if cfg.credit != "error" or cfg.credit_iters != 8 or base.error_lr != 0.1:
            raise ValueError("DEC-075 random control requires the eight-step/rate-0.1 reference")
        super().__init__(base, cfg, ledger)
        self.credit_rng = np.random.default_rng(np.random.SeedSequence([cfg.seed, 0x50433132]))
        self.kernel = private_kernel()
        self.on_decision = None
        self.router_seed = 0

    def update_item(self, item, router, budget):
        return self.kernel["update_item"](
            self, item, router, budget, on_decision=self.on_decision, seed=self.router_seed
        )

    def export_state(self):
        state = super().export_state()
        state.scalars["pc12_treatment"] = copy.deepcopy(TREATMENT)
        state.rng["pc12_credit"] = LearnerState.capture_rng(np_gen=self.credit_rng)
        return state

    def import_state(self, state):
        if state.scalars.get("pc12_treatment") != TREATMENT:
            raise ValueError("random-credit snapshot treatment differs")
        # Validate before mutating the ordinary cap state.
        probe = np.random.default_rng()
        LearnerState.apply_rng(state.rng["pc12_credit"], np_gen=probe)
        super().import_state(state)
        LearnerState.apply_rng(state.rng["pc12_credit"], np_gen=self.credit_rng)

    def clone(self):
        result = type(self)(self.base, self.cfg, self.ledger)
        result.import_state(self.export_state().clone())
        result.router_seed = self.router_seed
        result.on_decision = self.on_decision
        return result
