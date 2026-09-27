"""PC-6: restore a supplemental cap and project an exact read-only RevisionCap view.

Acquisition credit changes training, not inference. The registered batch reader
receives an actual RevisionCap, constructed normally, with the same fixed weights
and restored records. Only the error-credit acquisition metadata is omitted from
the query view's configuration. Nothing is patched in the registered reader.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
from pathlib import Path

import numpy as np
from scripts.r1_68c_batched_drift import PositionBatchReader

from aw.pc_v0_report import sha
from aw.pc_v1_acquire import PCRevisionCap
from pccap.harness.snapshot import restore
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.stage4_adapters import CellAdapter


def query_view(cap):
    if type(cap) is not PCRevisionCap:
        raise TypeError("requires exact PCRevisionCap; other subclasses are not admitted")
    for name in ("predict", "selection_for", "reset_queries"):
        if getattr(type(cap), name) is not getattr(RevisionCap, name) or name in cap.__dict__:
            raise TypeError("PC prediction implementation differs from registered inference")
    view = RevisionCap(cap.base, cap.cfg, cap.ledger, params=cap.params)
    state = cap.export_state()
    config = json.loads(state.scalars["config"])
    if cap.acquisition_credit == "error":
        expected = dict(
            credit="error",
            iters=cap.credit_iters,
            error_lr=cap.base.error_lr,
            energy="SD-24 corrected",
        )
        if config.pop("pc_acquisition", None) != expected:
            raise ValueError("error-credit configuration differs")
    if config != json.loads(view.semantic_config()):
        raise ValueError("query projection would change inference semantics")
    # This is a new in-memory query object, never written over the training checkpoint.
    state.scalars["config"] = view.semantic_config()
    view.import_state(state)
    if view.store.export().content_hash() != cap.store.export().content_hash():
        raise ValueError("query view changed memory")
    return view


class _ReadoutAdapter(CellAdapter):
    def __init__(self, cap, view):
        super().__init__(cap, "R1_learned_ff")
        self.view = view
        self._source_state = cap.state_hash()
        self._view_state = view.state_hash()

    def state_hash(self):
        # Called at assay boundaries, not per batch (large record-state hashes).
        if (
            self.view.state_hash() != self._view_state
            or self.learner.state_hash() != self._source_state
        ):
            raise RuntimeError("PC readout mutated source or query-view state")
        if (
            params_hash(self.learner.params) != self.learner.params_hash
            or params_hash(self.view.params) != self.learner.params_hash
        ):
            raise RuntimeError("PC readout changed reusable reader weights")
        return self._source_state


class PCPositionBatchReader:
    """The PC-5 read_arm interface, backed by the unchanged registered query kernel."""

    def __init__(self, cap, *, batch_size=16):
        self.view = query_view(cap)
        self.adapter = _ReadoutAdapter(cap, self.view)
        self._reader = PositionBatchReader(
            CellAdapter(self.view, "R1_learned_ff"), batch_size=batch_size
        )
        self.batch_size = batch_size
        self.events = self._reader.events
        self.last_capoff = None
        self.checkpoint = None

    @classmethod
    def from_checkpoint(cls, base, cfg, params, binding, *, batch_size=16):
        """Binding: path, sha256, state_sha256, base_sha256, reader_sha256, credit, iters.

        The caller constructs the original BP base with the EPC interface. This
        function never chooses weights from the v0 ePC replication checkpoint.
        """
        if binding["credit"] not in ("adjoint", "error") or binding["iters"] != 8:
            raise ValueError("supplemental fixed-v5 credit must be adjoint/error with eight steps")
        path = Path(binding["path"]).resolve()
        if sha(path) != binding["sha256"]:
            raise ValueError("supplemental snapshot file hash differs")
        if (
            base.checksum(recompute=True) != binding["base_sha256"]
            or params_hash(params) != binding["reader_sha256"]
        ):
            raise ValueError("supplemental base/reader identity differs")
        cap = PCRevisionCap(
            base,
            cfg,
            base.ledger,
            params=params,
            acquisition_credit=binding["credit"],
            credit_iters=binding["iters"],
        )
        state = restore(path.read_bytes(), expected_hash=binding["state_sha256"])
        cap.import_state(state)  # strict credit/config/weights match; no treatment conversion here
        if cap.state_hash() != binding["state_sha256"]:
            raise ValueError("restored state differs")
        reader = cls(cap, batch_size=batch_size)
        reader.checkpoint = dict(binding, path=str(path))
        return reader

    def last_logits_batch(self, seqs, phase="query"):
        self.last_capoff = None
        # The legacy reader flattens inputs: validate rank/dtype here first.
        if not seqs or phase != "query" or len(seqs) > self.batch_size:
            raise ValueError("nonempty bounded query batch required")
        if any(np.asarray(s).ndim != 1 or np.asarray(s).dtype.kind not in "iu" for s in seqs):
            raise ValueError("one-dimensional integer prefixes required")
        before = self.adapter.base.ledger.totals()["query"].copy()
        first = len(self.events)
        try:
            on = self._reader.last_logits_batch(seqs, phase=phase)
            self.last_capoff = self._reader.last_capoff
            return on
        except Exception:
            # The registered reader records an operation after return. Preserve
            # any failed work charged by the base but not yet in its event list.
            after = self.adapter.base.ledger.totals()["query"]
            fields = (
                "full_forwards",
                "partial_forwards",
                "reverses",
                "tokens",
                "wall_seconds",
                "accel_seconds",
            )
            missing = {
                k: max(
                    0,
                    after[k]
                    - before[k]
                    - sum(e.get("returned_cost", {}).get(k, 0) for e in self.events[first:]),
                )
                for k in fields
            }
            self.events.append(
                dict(
                    model="failed_work_not_already_reported", status="failed", returned_cost=missing
                )
            )
            raise
        finally:
            self._reader.adapter.reset_queries()
