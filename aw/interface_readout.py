"""Batched fixed-prefix readout for the explicit AW-L interface, without class bypasses."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy
import time

import jax.numpy as jnp
import numpy as np
from scripts.r1_68c_batched_drift import _forward_batch, _partial_batch, _SelectionPass

from aw.interface import ALL, InterfaceCap
from pccap.contracts import CostRecord, ForwardResult, SiteId
from pccap.revision_v1.observations import observation_from_pass, prompt_mask
from pccap.revision_v1.reader import obs_arrays


class InterfacePositionBatchReader:
    """Native batch kernels and selection; the declared mask controls the starting bank."""

    def __init__(self, adapter, *, batch_size=16, treatment=None, guard=lambda: None):
        if type(adapter.learner) is not InterfaceCap:
            raise TypeError("exact InterfaceCap required")
        if type(batch_size) is not int or not 1 <= batch_size <= 32:
            raise ValueError("batch_size must be an integer in [1,32]")
        if not adapter.learner.cfg.cache_prompt_pass:
            raise ValueError("declared prompt pass cache required")
        self.adapter, self.batch_size, self.guard = adapter, batch_size, guard
        self.events, self.last_capoff = [], None
        self.telemetry = dict(logical_positions=0, hard_null=0, selected=0, corrected=0)
        self.treatment = treatment or dict(
            interface=vars(adapter.learner.interface), acquisition="adjoint"
        )

    def last_logits_batch(self, seqs, phase="query"):
        self.guard()
        if phase != "query" or not seqs or len(seqs) > self.batch_size:
            raise ValueError("nonempty bounded query batch required")
        if any(np.asarray(s).ndim != 1 or np.asarray(s).dtype.kind not in "iu" for s in seqs):
            raise ValueError("one-dimensional integer prefixes required")
        original = self.adapter.learner
        original._assert_identity()
        base = original.raw_base
        seqs = [np.asarray(s, np.int32) for s in seqs]
        if any(
            not len(s) or len(s) > base.cfg.n_pos or np.any(s < 0) or np.any(s >= base.cfg.vocab)
            for s in seqs
        ):
            raise ValueError("invalid drift prefix")
        count = len(seqs)
        physical = seqs + [seqs[-1]] * (self.batch_size - count)
        start = time.monotonic()
        logits, rows, hidden, lengths = _forward_batch(base, physical)
        off, rows, hidden = (np.asarray(a, np.float32) for a in (logits, rows, hidden))
        elapsed = time.monotonic() - start
        self.events.append(
            dict(
                phase="query",
                model="shared_capoff_selection",
                physical_prefixes=len(physical),
                logical_prefixes=count,
                returned_cost=CostRecord(
                    phase="query",
                    full_forwards=len(physical),
                    tokens=int(lengths.sum()),
                    wall_seconds=elapsed,
                    accel_seconds=elapsed,
                ).as_dict(),
            )
        )
        cap = copy.copy(original)
        cap._sel = {}
        W = np.zeros((len(physical), 3, base.d), np.float32)
        corrected = np.zeros(count, bool)
        decisions = []
        for i, ids in enumerate(seqs):
            cap.reset_queries()
            fr = ForwardResult(
                logits=off[i],
                sites={SiteId(m, cap.blocks[m], len(ids) - 1): rows[i, m - 1] for m in ALL},
                hidden={m: hidden[i, m - 1] for m in ALL},
                cost=CostRecord(phase="query"),
            )
            proxy = _SelectionPass(base, ids, fr)
            cap.base = proxy
            sel = cap.selection_for(ids)
            if proxy.calls != 1 or sel.prompt_len != len(ids):
                raise RuntimeError("one fresh selection per fixed prefix required")
            decisions.append(
                dict(
                    hard_null=bool(sel.hard_null),
                    record_ids=sel.record_ids,
                    prompt_len=sel.prompt_len,
                )
            )
            if sel.hard_null:
                continue
            obs = observation_from_pass(
                fr,
                ids,
                prompt_mask(len(ids), len(ids)),
                cap.enc.base_hash,
                cap.enc.encoder_version,
                cap.cfg.reader.taps,
            )
            q = cap.jit_query(cap.params["reader"], *obs_arrays(obs, cap.cfg.reader))
            mass = jnp.asarray(1.0 if cap.cfg.binary_mass else 1.0 - sel.null_mass)
            if sel.delta is None or sel.delta.shape[0] == 0:
                if sel.delta is not None and cap.cfg.controller.delta_replaces_controller:
                    continue
                value = cap.jit_writes(cap.params["controller"], q, jnp.asarray(sel.code), mass)
            else:
                value = cap.jit_writes_with_delta(
                    cap.params["controller"],
                    q,
                    jnp.asarray(sel.code),
                    jnp.asarray(sel.delta[0]),
                    mass,
                )
            W[i] = np.asarray(value, np.float32)
            inactive = [m - 1 for m in ALL if m not in cap.interface.write_sites]
            if inactive and np.any(W[i, inactive] != 0):
                raise ValueError("readout encountered inactive nonzero writes")
            corrected[i] = True
        on = off[:count].copy()
        if corrected.any():
            bank = min(original.interface.write_sites)
            start = time.monotonic()
            changed = np.asarray(
                _partial_batch(base, bank, jnp.asarray(hidden[:, bank - 1]), lengths, W), np.float32
            )
            on[corrected] = changed[:count][corrected]
            elapsed = time.monotonic() - start
            self.events.append(
                dict(
                    phase="query",
                    model="cap_corrected_batch",
                    starting_bank=bank,
                    physical_prefixes=len(physical),
                    logical_corrected_prefixes=int(corrected.sum()),
                    returned_cost=CostRecord(
                        phase="query",
                        partial_forwards=len(physical),
                        tokens=int(lengths.sum()),
                        wall_seconds=elapsed,
                        accel_seconds=elapsed,
                    ).as_dict(),
                )
            )
            original.cost_counters["corrected_partial_passes"] += int(corrected.sum())
        original.cost_counters["cached_prompt_reads"] += count
        if not np.isfinite(on).all() or not np.isfinite(off).all():
            raise FloatingPointError("nonfinite interface readout")
        self.last_capoff = off[:count]
        self.telemetry["logical_positions"] += count
        self.telemetry["hard_null"] += sum(d["hard_null"] for d in decisions)
        self.telemetry["selected"] += sum(not d["hard_null"] for d in decisions)
        self.telemetry["corrected"] += int(corrected.sum())
        self.events.append(
            dict(selection_policy="one independent prefix selection", selections=decisions)
        )
        return on
