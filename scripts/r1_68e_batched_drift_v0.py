"""R1-68e: read-only, prefix-independent batched drift for the six v0 families.

The sequential bank semantics reproduce Cap/StableCap.edited_forward. Only
nonzero-write rows receive a partial result; no-hit and zero-value hits keep their
previous logits and residuals exactly. Full hidden tensors stay on device.
"""

from __future__ import annotations

import time

# isort: off
import pccap  # noqa: F401 -- determinism before JAX
import jax.numpy as jnp
import numpy as np
# isort: on

from scripts.r1_68c_batched_drift import _forward_batch, _nll

from pccap.bases import gpt2_jax as g
from pccap.cap.cap import Cap
from pccap.contracts import CostRecord
from pccap.revision_v1.endpoints import row_hash
from pccap.revision_v1.matched_update import MatchedUpdateCap
from pccap.revision_v1.v0_stable import StableCap

CONDITION_CLASSES = {
    "v0_live_C1": Cap,
    "v0_live_C2": Cap,
    "v0_stable": StableCap,
    "matched_update": MatchedUpdateCap,
    "S1_LM": StableCap,
    "S1_literal": StableCap,
}
IMPLEMENTATION = "v0_batched_v1"


def _partial(base, bank, hidden, lengths, writes):
    if hasattr(base, "forward_from_batch"):
        return base.forward_from_batch(bank, hidden, lengths, writes, phase="query")
    if base.checksum() != "tiny":
        raise TypeError("base requires audited partial batch surface")
    return g.forward_from_batch_jit(
        base.params, hidden, jnp.asarray(lengths), jnp.asarray(writes), base.cfg, bank
    )


def _charge(events, model, seqs, logical, operation, *, partial=False):
    event = {
        "phase": "query",
        "model": model,
        "physical_prefixes": len(seqs),
        "logical_prefixes": logical,
        "physical_padding": len(seqs) - logical,
        "status": "attempted",
    }
    events.append(event)
    start = time.monotonic()
    try:
        result = operation()
        # Synchronize the result before recording wall time / reporting success.
        logits = np.asarray(result[0], np.float32)
        if not np.isfinite(logits).all():
            raise FloatingPointError("nonfinite batch logits")
        event["status"] = "complete"
        return (logits, *result[1:])
    except Exception as exc:
        event["status"] = "failed"
        event["error_type"] = type(exc).__name__
        raise
    finally:
        elapsed = time.monotonic() - start
        event["returned_cost"] = CostRecord(
            phase="query",
            full_forwards=0 if partial else len(seqs),
            partial_forwards=len(seqs) if partial else 0,
            tokens=sum(len(s) for s in seqs),
            wall_seconds=elapsed,
            accel_seconds=elapsed,
        ).as_dict()
        event["cost_policy"] = (
            "physical attempted work; elapsed host wall, not independent accelerator telemetry"
        )


class V0PositionBatchReader:
    def __init__(self, adapter, *, batch_size=16):
        if CONDITION_CLASSES.get(adapter.condition) is not type(adapter.learner):
            raise TypeError("requires an exact admitted v0-family adapter class")
        cap = adapter.learner
        if (
            cap.cfg.banks() != (1, 2, 3)
            or cap.cfg.read != "h"
            or cap.blocks != g.BANK_BLOCK
            or cap.d != adapter.base.d
        ):
            raise ValueError("only the registered three-bank R-h architecture is supported")
        expected_arm = "C2" if adapter.condition == "v0_live_C2" else "C1"
        if cap.cfg.arm != expected_arm:
            raise ValueError("adapter condition/arm mismatch")
        if type(batch_size) is not int or not 1 <= batch_size <= 32:
            raise ValueError("batch_size must be an integer in [1,32]")
        self.adapter, self.batch_size = adapter, batch_size
        self.events, self.last_capoff, self.last_selections = [], None, None

    def last_logits_batch(self, seqs, phase="query"):
        self.last_capoff, self.last_selections = None, None
        if phase != "query" or not seqs or len(seqs) > self.batch_size:
            raise ValueError("nonempty bounded query batch required")
        base, cap = self.adapter.base, self.adapter.learner
        clean = []
        for seq in seqs:
            ids = np.asarray(seq)
            if (
                ids.ndim != 1
                or ids.dtype.kind not in "iu"
                or not len(ids)
                or len(ids) > base.cfg.n_pos
                or np.any(ids < 0)
                or np.any(ids >= base.cfg.vocab)
            ):
                raise ValueError("invalid drift prefix")
            clean.append(ids.astype(np.int32))
        seqs, count = clean, len(clean)
        if len({g.bucket_len(len(s)) for s in seqs}) != 1:
            raise ValueError("prefixes must share one context-length bucket")
        physical = seqs + [seqs[-1]] * (self.batch_size - count)
        before = self.adapter.state_hash()
        self.adapter.reset_queries()
        try:
            off, rows, hidden, lengths = _charge(
                self.events,
                "shared_capoff_selection",
                physical,
                count,
                lambda: _forward_batch(base, physical),
            )
            rows = np.array(rows, np.float32)
            stable = type(cap) in (StableCap, MatchedUpdateCap)
            initial_rows = rows.copy() if stable else None
            on = off[:count].copy()
            writes = np.zeros((self.batch_size, 3, base.d), np.float32)
            decisions = [dict() for _ in seqs]
            for bank in (1, 2, 3):
                changed = np.zeros(self.batch_size, bool)
                for i in range(count):
                    query = cap.key((initial_rows if stable else rows)[i, bank - 1])
                    value, retrieval = cap.banks[bank].bank.value_for(query)
                    writes[i, bank - 1] = np.asarray(value, np.float32)
                    if not np.isfinite(writes[i, bank - 1]).all():
                        raise FloatingPointError("nonfinite bank value")
                    changed[i] = bool(np.any(writes[i, bank - 1]))
                    decisions[i][bank] = {
                        "slot": int(retrieval.slot),
                        "nonzero_write": bool(changed[i]),
                    }
                if not changed.any():
                    continue
                logits, later_rows, later_hidden = _charge(
                    self.events,
                    f"cap_partial_bank_{bank}",
                    physical,
                    count,
                    lambda bank=bank, hidden=hidden: _partial(
                        base, bank, hidden[:, bank - 1], lengths, writes
                    ),
                    partial=True,
                )
                self.events[-1]["logical_corrected_prefixes"] = int(changed.sum())
                active = changed[:count]
                on[active] = logits[:count][active]
                if bank < 3:
                    later_rows = np.asarray(later_rows, np.float32)
                    rows[changed, bank:] = later_rows[changed]
                    hidden = hidden.at[:, bank:].set(
                        jnp.where(
                            jnp.asarray(changed)[:, None, None, None],
                            later_hidden,
                            hidden[:, bank:],
                        )
                    )
            self.last_capoff, self.last_selections = off[:count].copy(), decisions
            self.events.append(
                {
                    "selection_policy": "fresh per-prefix, per-bank retrieval; no cache inheritance",
                    "key_policy": "unedited stable" if stable else "sequential live",
                    "selections": decisions,
                    "physical_padding": self.batch_size - count,
                }
            )
            return on
        finally:
            self.adapter.reset_queries()
            if self.adapter.state_hash() != before:
                raise RuntimeError("batched drift query mutated learner state")


def batched_drift(assays, definition, *, batch_size=16):
    """Same ordered per-position outputs as CellAssays.drift; all physical work charged."""
    reader = V0PositionBatchReader(assays.adapter, batch_size=batch_size)
    windows = definition["windows"]
    if not windows or any(len(w) < 2 for w in windows):
        raise ValueError("nonempty drift windows with scored positions required")
    inventory = []
    for wi, window in enumerate(windows):
        ids = np.asarray(window)
        if (
            ids.ndim != 1
            or ids.dtype.kind not in "iu"
            or np.any(ids < 0)
            or np.any(ids >= assays.adapter.base.cfg.vocab)
        ):
            raise ValueError("invalid drift window")
        for pos in range(1, len(ids)):
            inventory.append((wi, pos, ids[:pos], int(ids[pos])))
    if (
        type(definition["expected_positions"]) is not int
        or len(inventory) != definition["expected_positions"]
    ):
        raise ValueError("incomplete drift inventory")
    groups = {}
    for row in inventory:
        groups.setdefault(g.bucket_len(len(row[2])), []).append(row)
    results = {}
    try:
        for rows in groups.values():
            for offset in range(0, len(rows), batch_size):
                chunk = rows[offset : offset + batch_size]
                seqs = [r[2] for r in chunk]
                start = len(reader.events)
                try:
                    on = reader.last_logits_batch(seqs)
                finally:
                    assays.events.extend(reader.events[start:])
                off = reader.last_capoff
                if assays.adapter.locality_base is assays.adapter.base:
                    original = off
                else:
                    physical = seqs + [seqs[-1]] * (batch_size - len(seqs))
                    logits, _, _, _ = _charge(
                        assays.events,
                        "original_batch",
                        physical,
                        len(seqs),
                        lambda physical=physical: _forward_batch(
                            assays.adapter.locality_base, physical
                        ),
                    )
                    original = logits[: len(seqs)]
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
            "implementation": IMPLEMENTATION,
            "batch_size": batch_size,
            "selection_count": len(rows),
            "bank_retrieval_count": 3 * len(rows),
            "capoff_shared_with_selection": True,
            "physical_padding_charged": True,
            "hard_null_policy": "exact unedited batch logits; zero-value hits also unchanged",
            "floating_point_policy": "TinyBase tolerance 1e-4 nats; owner real-base gate <=1e-3 nats and identical exceedance counts",
        },
    }
