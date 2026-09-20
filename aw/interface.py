"""Supplemental read/write interfaces without changing the frozen R1 source.

The base proxy masks adjoints *before* adapt.py normalizes each site gradient.
Thus the original five-step acquisition, early stopping, rollback and aggregate
projection remain intact. Inactive dense delta slots are zero, but their real
allocated bytes are still charged; no fictitious compact-storage saving.
"""

from __future__ import annotations

import copy
import json
from dataclasses import dataclass, replace

import pccap  # noqa: F401 -- before JAX

# isort: split

import jax
import jax.numpy as jnp
import numpy as np

from pccap.contracts import ForwardResult, SiteId, Write
from pccap.revision_v1.contracts import RevisionCost
from pccap.revision_v1.controller import bound_writes, raw_writes
from pccap.revision_v1.learner import RevisionCap, RevisionConfig
from pccap.revision_v1.memory import RecordStore
from pccap.revision_v1.observations import observation_from_pass, prompt_mask
from pccap.revision_v1.reader import obs_arrays

ALL = (1, 2, 3)


@dataclass(frozen=True)
class InterfaceConfig:
    read_taps: tuple[int, ...] = ALL
    write_sites: tuple[int, ...] = ALL

    def __post_init__(self):
        for name in ("read_taps", "write_sites"):
            sites = getattr(self, name)
            if not sites or tuple(sorted(set(sites))) != sites or not set(sites) <= set(ALL):
                raise ValueError(f"{name} must be a nonempty sorted unique subset of {ALL}")


DEFAULT_INTERFACE = InterfaceConfig()


class _MaskedBase:
    """Mask physical writes and returned gradients before the locked fast rule."""

    def __init__(self, base, sites):
        self.raw = base
        self.sites = sites

    def __getattr__(self, name):
        return getattr(self.raw, name)

    def masked(self, writes):
        return [
            Write(w.site, w.vector if w.site.bank in self.sites else np.zeros_like(w.vector))
            for w in writes
        ]

    def forward(self, ids, writes=(), **kwargs):
        return self.raw.forward(ids, self.masked(writes), **kwargs)

    def forward_from(self, bank, hidden, ids, writes=(), **kwargs):
        return self.raw.forward_from(bank, hidden, ids, self.masked(writes), **kwargs)

    def loss(self, ids, target, writes, **kwargs):
        return self.raw.loss(ids, target, self.masked(writes), **kwargs)

    def adjoint(self, ids, target, writes, **kwargs):
        result = self.raw.adjoint(ids, target, self.masked(writes), **kwargs)
        grads = result[0] if kwargs.get("return_loss", False) else result
        masked = {
            site: value if site.bank in self.sites else np.zeros_like(value)
            for site, value in grads.items()
        }
        return (masked, *result[1:]) if kwargs.get("return_loss", False) else masked


class _MaskedStore(RecordStore):
    def _validate_mask(self, delta):
        if delta is None:
            return
        delta = np.asarray(delta)
        if delta.ndim != 3 or delta.shape[1] != 3:
            raise ValueError("three-bank delta array required")
        inactive = [m - 1 for m in ALL if m not in self.write_sites]
        if inactive and np.any(delta[:, inactive] != 0):
            raise ValueError("inactive acquisition delta is not exactly zero")

    def add(self, record):
        self._validate_mask(record.delta)
        return super().add(record)

    def set_delta(self, record_id, delta, delta_bytes_budget=True):
        self._validate_mask(delta)
        return super().set_delta(record_id, delta, delta_bytes_budget=delta_bytes_budget)


def prune_reader(params, read_taps):
    """Remove projections physically, preserving all retained tensor values."""
    if read_taps == ALL:
        return params
    result = dict(params, reader=dict(params["reader"]))
    result["reader"]["tap"] = {str(m): params["reader"]["tap"][str(m)] for m in read_taps}
    return result


class InterfaceCap(RevisionCap):
    def __init__(
        self, base, cfg: RevisionConfig, ledger, params=None, *, interface=DEFAULT_INTERFACE
    ):
        if cfg.single_site:
            raise ValueError("use write_sites; legacy single_site masks deployment only")
        if cfg.controller.n_banks != 3:
            raise ValueError("three-bank base required")
        self.interface = interface
        self.raw_base = base
        cfg = copy.deepcopy(cfg)
        cfg.reader = replace(cfg.reader, taps=interface.read_taps)
        effective = (
            base if interface.write_sites == ALL else _MaskedBase(base, interface.write_sites)
        )
        super().__init__(
            effective,
            cfg,
            ledger,
            None if params is None else prune_reader(params, interface.read_taps),
        )
        self._install_write_functions()
        self._guard_store()
        self._interface_identity = self.semantic_config()

    def _guard_store(self):
        if self.interface.write_sites == ALL:
            return
        # RecordStore has no slots; keep its exact accounting/index implementation.
        self.store.__class__ = _MaskedStore
        self.store.write_sites = self.interface.write_sites
        self._check_deltas(self.store)

    def _check_deltas(self, store):
        inactive = [m - 1 for m in ALL if m not in self.interface.write_sites]
        for record in store.records:
            if record.delta is not None and inactive and np.any(record.delta[:, inactive] != 0):
                raise ValueError("snapshot/store contains inactive nonzero deltas")

    def _install_write_functions(self):
        if self.interface.write_sites == ALL:
            return  # preserve original compiled arithmetic bit for bit
        cc = self.cfg.controller
        mask = jnp.asarray([m in self.interface.write_sites for m in ALL])[:, None]

        def project(raw, mass):
            raw = jnp.where(mask, raw, jnp.zeros_like(raw)) * mass
            value, _ = bound_writes(raw, cc)
            return jnp.where(mask & (mass > 0), value, jnp.zeros_like(value))

        def controller(p, q, code, mass):
            return project(raw_writes(p, cc, q, code), mass)

        def delta(p, q, code, dl, mass):
            raw = dl if cc.delta_replaces_controller else raw_writes(p, cc, q, code) + dl
            return project(raw, mass)

        self.jit_writes = jax.jit(controller)
        self.jit_writes_with_delta = jax.jit(delta)
        self._vjp_fn = lambda p, q, code: jax.vjp(
            lambda c: controller(p, q, c, jnp.asarray(1.0)), code
        )
        self.vjp_writes = self._vjp_fn

    def clear_interface_caches(self):
        self.reset_queries()
        for name in ("jit_query", "jit_key_apply", "jit_writes", "jit_writes_with_delta"):
            fn = getattr(self, name, None)
            if hasattr(fn, "clear_cache"):
                fn.clear_cache()
        self.__dict__.pop("_df_cache", None)
        self.__dict__.pop("_lexw_cache", None)

    def _assert_identity(self):
        if self.semantic_config() != self._interface_identity:
            self.clear_interface_caches()
            raise RuntimeError(
                "interface/config changed; construct a fresh learner and reacquire records"
            )

    def semantic_config(self):
        original = super().semantic_config()
        if self.interface == InterfaceConfig():
            return original  # permits the exact saved all-site R1 checkpoint
        value = json.loads(original)
        value["supplemental_interface_v1"] = dict(
            read_taps=self.interface.read_taps, write_sites=self.interface.write_sites
        )
        return json.dumps(value, sort_keys=True)

    def import_state(self, state):
        self._assert_identity()
        # Reject invalid deltas before mutating learner state.
        self._check_deltas(RecordStore.from_state(state))
        super().import_state(state)
        self._guard_store()
        self.clear_interface_caches()

    def update_item(self, *args, **kwargs):
        self._assert_identity()
        result = super().update_item(*args, **kwargs)
        self._check_deltas(self.store)
        return result

    def selection_for(self, ids):
        self._assert_identity()
        return super().selection_for(ids)

    def interface_accounting(self):
        self._check_deltas(self.store)
        deltas = [r.delta for r in self.store.records if r.delta is not None]
        allocated = sum(d.nbytes for d in deltas)
        return dict(
            read_taps=self.interface.read_taps,
            write_sites=self.interface.write_sites,
            parameters=self.n_params,
            weights_bytes=4 * self.n_params,
            delta_allocated_bytes=allocated,
            delta_active_coordinate_bytes=allocated * len(self.interface.write_sites) // 3,
            total_allocated_bytes=self.memory_bytes().allocated_bytes,
            aggregate_allowance=self.cfg.controller.A,
            delta_steps_per_prefix=self.cfg.fast.delta_steps,
            inactive_storage="dense exact zeros; all bytes charged",
        )

    def predict(self, ids, full=False):
        self._assert_identity()
        if self.interface.write_sites == ALL:
            return super().predict(ids, full=full)
        # Same read path as RevisionCap; only corrected-pass starting bank differs.
        ids = np.asarray(ids, np.int32).reshape(-1)
        sel = self.selection_for(ids)
        cost = RevisionCost(phase="query")
        if sel.pending_cost is not None:
            cost.add(sel.pending_cost)
            cost.extra_pass_forwards += 1
            sel.pending_cost = None
        if sel.prompt_pass is not None and not full and len(ids) == sel.prompt_len:
            fr = sel.prompt_pass
            self.cost_counters["cached_prompt_reads"] += 1
        else:
            fr = self.base.forward(ids, (), retain_sites=True, phase="query", last_only=not full)
            cost.add(fr.cost)
            cost.extra_pass_forwards += 1
        if sel.hard_null:
            return ForwardResult(logits=np.asarray(fr.logits), sites={}, cost=cost)
        obs = observation_from_pass(
            fr,
            ids,
            prompt_mask(min(sel.prompt_len, len(ids)), len(ids)),
            self.enc.base_hash,
            self.enc.encoder_version,
            self.cfg.reader.taps,
        )
        q = self.jit_query(self.params["reader"], *obs_arrays(obs, self.cfg.reader))
        t = len(ids) - sel.prompt_len
        mass = 1.0 if self.cfg.binary_mass else 1.0 - sel.null_mass
        if sel.delta is None or t >= sel.delta.shape[0]:
            if sel.delta is not None and self.cfg.controller.delta_replaces_controller:
                return ForwardResult(logits=np.asarray(fr.logits), sites={}, cost=cost)
            W = self.jit_writes(
                self.params["controller"], q, jnp.asarray(sel.code), jnp.asarray(mass)
            )
        else:
            W = self.jit_writes_with_delta(
                self.params["controller"],
                q,
                jnp.asarray(sel.code),
                jnp.asarray(sel.delta[t]),
                jnp.asarray(mass),
            )
        p = len(ids) - 1
        first = min(self.interface.write_sites)
        wl = [
            Write(SiteId(m, self.blocks[m], p), np.asarray(W[m - 1], np.float32))
            for m in self.interface.write_sites
        ]
        fr2 = self.base.forward_from(
            first, fr.hidden[first], ids, wl, phase="query", retain_sites=False, last_only=not full
        )
        cost.add(fr2.cost)
        self.cost_counters["corrected_partial_passes"] += 1
        cost.records_touched += len(sel.record_ids)
        return ForwardResult(logits=np.asarray(fr2.logits), sites={}, cost=cost)
