"""R1-68c per-position drift batches for exact RevisionCap; no training changes."""

from __future__ import annotations

import copy
import time

# isort: off
import pccap  # noqa: F401 -- determinism before JAX
import jax.numpy as jnp
import numpy as np
# isort: on

from pccap.bases import gpt2_jax as g
from pccap.contracts import CostRecord, ForwardResult, SiteId
from pccap.revision_v1.endpoints import row_hash
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.observations import observation_from_pass, prompt_mask
from pccap.revision_v1.reader import obs_arrays


class _SelectionPass:
    """A shallow read-only learner view consumes one already charged base pass."""

    def __init__(self, base, ids, result):
        self.original, self.ids, self.result = base, np.asarray(ids, np.int32), result
        self.calls = 0

    def __getattr__(self, name):
        return getattr(self.original, name)

    def forward(self, ids, writes=(), *, retain_sites=True, phase="query", last_only=True):
        if (
            self.calls
            or writes
            or not retain_sites
            or not last_only
            or phase != "query"
            or not np.array_equal(ids, self.ids)
        ):
            raise RuntimeError("selection made an unexpected base request")
        self.calls += 1
        return self.result


def _forward_batch(base, seqs):
    if hasattr(base, "forward_batch"):
        return base.forward_batch(seqs, phase="query")
    # TinyBase CPU gate uses the exact production kernels without extending its file.
    if base.checksum() != "tiny":
        raise TypeError("base requires audited batch surface")
    n = np.asarray([len(s) for s in seqs], np.int32)
    width = g.bucket_len(int(n.max()))
    ids = np.stack([g.pad_ids(s, width) for s in seqs])
    logits, rows, hidden = g.forward_batch_jit(
        base.params, jnp.asarray(ids), jnp.asarray(n), jnp.zeros((len(seqs), 3, base.d)), base.cfg
    )
    return logits, rows, hidden, n


def _partial_batch(base, bank, hidden, lengths, writes):
    if hasattr(base, "forward_from_batch"):
        return base.forward_from_batch(bank, hidden, lengths, writes, phase="query")[0]
    if base.checksum() != "tiny":
        raise TypeError("base requires audited partial batch surface")
    return g.forward_from_batch_jit(
        base.params, hidden, jnp.asarray(lengths), jnp.asarray(writes), base.cfg, bank
    )[0]


class PositionBatchReader:
    """Fresh selection per prefix; fixed physical batch shapes, padded rows charged.

    The installed learner's last_logits_batch is a scalar list comprehension.
    This additive implementation uses its selection_for and JAX's existing batch
    kernels, sharing each unedited base pass with the cap-off comparison.
    """

    def __init__(self, adapter, *, batch_size=16):
        if type(adapter.learner) is not RevisionCap:
            raise TypeError("batch drift supports exact RevisionCap only")
        if type(batch_size) is not int or not 1 <= batch_size <= 32:
            raise ValueError("batch_size must be an integer in [1,32]")
        if not adapter.learner.cfg.cache_prompt_pass:
            raise ValueError("batch drift requires the admitted prompt-pass cache")
        self.adapter, self.batch_size = adapter, batch_size
        self.events = []
        self.last_capoff = None

    def last_logits_batch(self, seqs, phase="query"):
        if phase != "query" or not seqs or len(seqs) > self.batch_size:
            raise ValueError("nonempty bounded query batch required")
        seqs = [np.asarray(s, np.int32).reshape(-1) for s in seqs]
        base = self.adapter.base
        if any(
            not len(s) or len(s) > base.cfg.n_pos or np.any(s < 0) or np.any(s >= base.cfg.vocab)
            for s in seqs
        ):
            raise ValueError("invalid drift prefix")
        count = len(seqs)
        physical = seqs + [seqs[-1]] * (self.batch_size - count)
        started = time.monotonic()
        logits, rows, hidden, lengths = _forward_batch(base, physical)
        off = np.asarray(logits, np.float32)
        site_rows = np.asarray(rows, np.float32)
        hidden_np = np.asarray(hidden, np.float32)
        elapsed = time.monotonic() - started
        self.events.append(
            {
                "phase": "query",
                "model": "shared_capoff_selection",
                "physical_prefixes": len(physical),
                "logical_prefixes": count,
                "returned_cost": CostRecord(
                    phase="query",
                    full_forwards=len(physical),
                    tokens=int(lengths.sum()),
                    wall_seconds=elapsed,
                    accel_seconds=elapsed,
                ).as_dict(),
            }
        )
        original = self.adapter.learner
        cap = copy.copy(original)
        cap._sel = {}
        writes = np.zeros((len(physical), 3, base.d), np.float32)
        corrected = np.zeros(count, bool)
        decisions = []
        for i, ids in enumerate(seqs):
            cap.reset_queries()
            fr = ForwardResult(
                logits=off[i],
                sites={
                    SiteId(m, original.blocks[m], len(ids) - 1): site_rows[i, m - 1]
                    for m in (1, 2, 3)
                },
                hidden={m: hidden_np[i, m - 1] for m in (1, 2, 3)},
                cost=CostRecord(phase="query"),
            )
            proxy = _SelectionPass(base, ids, fr)
            cap.base = proxy
            selection = cap.selection_for(ids)
            if proxy.calls != 1 or selection.prompt_len != len(ids):
                raise RuntimeError("one independent selection per prefix required")
            decisions.append(
                {
                    "hard_null": bool(selection.hard_null),
                    "record_ids": selection.record_ids,
                    "prompt_len": selection.prompt_len,
                }
            )
            if selection.hard_null:
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
            mass = 1.0 if cap.cfg.binary_mass else 1.0 - selection.null_mass
            if selection.delta is None or selection.delta.shape[0] == 0:
                if selection.delta is not None and cap.cfg.controller.delta_replaces_controller:
                    continue
                value = cap.jit_writes(
                    cap.params["controller"], q, jnp.asarray(selection.code), jnp.asarray(mass)
                )
            else:
                value = cap.jit_writes_with_delta(
                    cap.params["controller"],
                    q,
                    jnp.asarray(selection.code),
                    jnp.asarray(selection.delta[0]),
                    jnp.asarray(mass),
                )
            writes[i] = np.asarray(value, np.float32)
            if cap.cfg.single_site:
                writes[i, :2] = 0
            corrected[i] = True
        on = off[:count].copy()
        if corrected.any():
            bank = 3 if original.cfg.single_site else 1
            started = time.monotonic()
            logits = np.asarray(
                _partial_batch(base, bank, jnp.asarray(hidden_np[:, bank - 1]), lengths, writes),
                np.float32,
            )
            elapsed = time.monotonic() - started
            on[corrected] = logits[:count][corrected]
            self.events.append(
                {
                    "phase": "query",
                    "model": "cap_corrected_batch",
                    "physical_prefixes": len(physical),
                    "logical_corrected_prefixes": int(corrected.sum()),
                    "returned_cost": CostRecord(
                        phase="query",
                        partial_forwards=len(physical),
                        tokens=int(lengths.sum()),
                        wall_seconds=elapsed,
                        accel_seconds=elapsed,
                    ).as_dict(),
                }
            )
            original.cost_counters["corrected_partial_passes"] += int(corrected.sum())
        original.cost_counters["cached_prompt_reads"] += count
        if not np.isfinite(on).all() or not np.isfinite(off).all():
            raise FloatingPointError("nonfinite batched drift logits")
        self.last_capoff = off[:count]
        self.events.append(
            {
                "selection_policy": "one selection_for per logical prefix; no prefix-cache carry",
                "selections": decisions,
                "physical_padding": self.batch_size - count,
            }
        )
        self.adapter.reset_queries()
        return on


def _nll(logits, target):
    values = np.asarray(logits, np.float64)
    peak = float(values.max())
    if not np.isfinite(values).all():
        raise FloatingPointError("nonfinite drift logits")
    return float(peak + np.log(np.exp(values - peak).sum()) - values[int(target)])


def batched_drift(assays, definition, *, batch_size=16):
    reader = PositionBatchReader(assays.adapter, batch_size=batch_size)
    inventory = [
        (wi, pos, np.asarray(w[:pos], np.int32), int(w[pos]))
        for wi, w in enumerate(definition["windows"])
        for pos in range(1, len(w))
    ]
    if len(inventory) != definition["expected_positions"]:
        raise ValueError("incomplete drift inventory")
    # Group by production length bucket to avoid a long prefix padding every short one.
    groups = {}
    for row in inventory:
        groups.setdefault(g.bucket_len(len(row[2])), []).append(row)
    results = {}
    try:
        for rows in groups.values():
            for offset in range(0, len(rows), batch_size):
                chunk = rows[offset : offset + batch_size]
                seqs = [r[2] for r in chunk]
                before_events = len(reader.events)
                try:
                    on = reader.last_logits_batch(seqs)
                finally:
                    assays.events.extend(reader.events[before_events:])
                off = reader.last_capoff
                if assays.adapter.locality_base is assays.adapter.base:
                    original = off
                else:
                    started = time.monotonic()
                    physical = seqs + [seqs[-1]] * (batch_size - len(seqs))
                    logits, _, _, lengths = _forward_batch(assays.adapter.locality_base, physical)
                    original = np.asarray(logits, np.float32)[: len(seqs)]
                    elapsed = time.monotonic() - started
                    assays.events.append(
                        {
                            "phase": "query",
                            "model": "original_batch",
                            "returned_cost": CostRecord(
                                phase="query",
                                full_forwards=batch_size,
                                tokens=int(lengths.sum()),
                                wall_seconds=elapsed,
                                accel_seconds=elapsed,
                            ).as_dict(),
                        }
                    )
                for i, (wi, pos, _, target) in enumerate(chunk):
                    results[(wi, pos)] = {
                        "item_id": f"w{wi}:p{pos}",
                        "capoff": _nll(off[i], target),
                        "original": _nll(original[i], target),
                        "cap": _nll(on[i], target),
                    }
    finally:
        assays.adapter.reset_queries()
    rows = [results[(wi, pos)] for wi, pos, _, _ in inventory]
    means = {k: float(np.mean([r[k] for r in rows])) for k in ("capoff", "original", "cap")}
    return {
        "rows": rows,
        "scored_positions": len(rows),
        "expected_positions": len(inventory),
        "status": "complete",
        "delta_capoff_nats": means["cap"] - means["capoff"],
        "delta_original_nats": means["cap"] - means["original"],
        "query_boundary_policy": "reset at every scored ordinary-text prefix",
        "source_sha256": row_hash(definition),
        "batch_audit": {
            "batch_size": batch_size,
            "selection_count": len(rows),
            "capoff_shared_with_selection": True,
            "physical_padding_charged": True,
            "floating_point_policy": "batch kernels may differ by roundoff; CPU per-position parity tested, real-base parity/profile remain owner gates",
        },
    }
