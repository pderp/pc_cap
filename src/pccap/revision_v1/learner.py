"""RevisionCap: the revision v1 learner behind the v0 harness surface (design §API, §Harness adapter).

Read path (``predict``): the record and the null decision are selected ONCE per query from the prompt (X0-05) and held
for every answer position of that query; a hard null gives the cap-off logits exactly. Each read is one write-free full
pass (the observation) plus one partial corrected pass from site 1 when writes are non-zero. Learning path
(``update_item``): ``adapt_record`` — support only; the reusable weights are frozen and hashed (gate 2).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.contracts import (
    CostRecord,
    EditItem,
    ForwardResult,
    ItemOutcome,
    MemoryReport,
    SiteId,
    Write,
)
from pccap.harness.snapshot import LearnerState
from pccap.revision_v1.adapt import FastConfig, adapt_record
from pccap.revision_v1.contracts import RevisionCost, support_from_edit_item
from pccap.revision_v1.controller import (
    ControllerConfig,
    init_controller,
    writes,
    writes_with_delta,
)
from pccap.revision_v1.memory import DEFAULT_CEILING, RecordStore
from pccap.revision_v1.observations import (
    ENCODER_VERSION,
    ObservationEncoder,
    observation_from_pass,
    prompt_mask,
)
from pccap.revision_v1.reader import (
    ReaderConfig,
    applicability,
    init_reader,
    obs_arrays,
    param_count,
    params_hash,
    query_embedding,
)


@dataclass
class RevisionConfig:
    reader: ReaderConfig = field(default_factory=ReaderConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    fast: FastConfig = field(default_factory=FastConfig)
    null_threshold: float = 0.5  # hard null at evaluation when null mass ≥ threshold
    hard_top1: bool = True  # deployment selection: the best-scoring record alone (v0's nearest slot); soft mixing only in training
    min_score: float | None = None  # non-learned fallback gate: hard null when the best cosine score is below this (v0's radius, in cosine units)
    cache_prompt_pass: bool = True  # R1-16: reuse the selection pass as the observation of the prompt position (saves one pass per query)
    single_site: bool = False  # R1-16 variant: writes only at site 3 (partial pass from block 11 instead of block 3)
    ceiling_bytes: int = DEFAULT_CEILING
    seed: int = 0
    tau_edit: float = 0.1


@dataclass
class Selection:
    prompt_len: int
    record_ids: list[str]
    weights: np.ndarray
    null_mass: float
    code: np.ndarray | None  # applicability-weighted code (None on a hard null)
    hard_null: bool
    prompt_pass: object = None
    best_score: float | None = None  # cosine of the best candidate (diagnostics / min_score gate)
    delta: np.ndarray | None = None  # applicability-weighted delta write of the selected records (None when none carries one)  # the selection pass (ForwardResult) kept for the prompt-position read when caching is on


class RevisionCap:
    name = "R1"
    decode_key_positions = False

    def __init__(self, base, cfg: RevisionConfig, ledger, params: dict | None = None):
        self.base, self.cfg, self.ledger = base, cfg, ledger
        self.blocks = dict(getattr(base, "bank_blocks", None) or g.BANK_BLOCK)
        self.enc = ObservationEncoder(base, taps=cfg.reader.taps, encoder_version=ENCODER_VERSION)
        if params is None:
            k1, k2 = jax.random.split(jax.random.PRNGKey(cfg.seed))
            params = {"reader": init_reader(k1, cfg.reader), "controller": init_controller(k2, cfg.controller)}
        self.params = params
        self.params_hash = params_hash(params)
        self.n_params = param_count(params)
        self.store = RecordStore(dk=cfg.reader.width, d_code=cfg.reader.d_code, ceiling_bytes=cfg.ceiling_bytes, encoder_version=ENCODER_VERSION, weights_bytes=4 * self.n_params)
        self._sel: dict[bytes, Selection] = {}
        self.cost_counters = {"selection_passes": 0, "cached_prompt_reads": 0, "corrected_partial_passes": 0}
        rc, cc = cfg.reader, cfg.controller
        self.jit_query = jax.jit(lambda p, last, span: query_embedding(p, rc, last, span))
        self.jit_key_apply = jax.jit(lambda p, q, keys, mask: applicability(p, rc, q, keys, mask))
        self.jit_writes = jax.jit(lambda p, q, code, mass: writes(p, cc, q, code, mass)[0])
        self.jit_writes_with_delta = jax.jit(lambda p, q, code, delta, mass: writes_with_delta(p, cc, q, code, delta, mass)[0])
        self._vjp_fn = lambda p, q, code: jax.vjp(lambda c: writes(p, cc, q, c, jnp.asarray(1.0))[0], code)
        self.vjp_writes = self._vjp_fn

    # ------------------------------------------------------------------ selection (once per query)
    def _select(self, prompt: np.ndarray) -> Selection:
        fr = self.base.forward(prompt, (), retain_sites=True, phase="query", last_only=True)
        self.cost_counters["selection_passes"] += 1
        obs = observation_from_pass(fr, prompt, None, self.enc.base_hash, self.enc.encoder_version, self.cfg.reader.taps)
        q = self.jit_query(self.params["reader"], *obs_arrays(obs, self.cfg.reader))
        cands = self.store.retrieve(np.asarray(q), self.cfg.reader.top_k, query_version=self.enc.encoder_version)
        keep = fr if self.cfg.cache_prompt_pass else None
        if not cands:
            return Selection(len(prompt), [], np.zeros(0, np.float32), 1.0, None, True, prompt_pass=keep)
        k = self.cfg.reader.top_k
        keys = np.zeros((k, self.cfg.reader.width), np.float32)
        mask = np.zeros(k, bool)
        recs = [self.store.get(c.record_id) for c in cands]
        for i, r in enumerate(recs):
            keys[i], mask[i] = r.key, True
        w, null, _ = self.jit_key_apply(self.params["reader"], q, jnp.asarray(keys), jnp.asarray(mask))
        w, null = np.asarray(w, np.float32), float(null)
        qn = np.asarray(q, np.float32)
        qn = qn / (np.linalg.norm(qn) + 1e-8)
        cos = keys[: len(recs)] @ qn / (np.linalg.norm(keys[: len(recs)], axis=1) + 1e-8)
        best_score = float(np.max(cos))
        if self.cfg.hard_top1 and w[: len(recs)].sum() > 0:
            one = np.zeros_like(w)
            one[int(np.argmax(w[: len(recs)]))] = 1.0
            w = one
        hard = null >= self.cfg.null_threshold or (self.cfg.min_score is not None and best_score < self.cfg.min_score)
        code, delta = None, None
        if not hard:
            wsum = max(float(w.sum()), 1e-12)
            code = np.asarray(sum(float(w[i]) * recs[i].code for i in range(len(recs))) / wsum, np.float32)
            with_d = [(float(w[i]), recs[i].delta) for i in range(len(recs)) if recs[i].delta is not None]
            if with_d:
                T = max(dl.shape[0] for _, dl in with_d)
                delta = np.zeros((T,) + with_d[0][1].shape[1:], np.float32)
                for wi, dl in with_d:
                    delta[: dl.shape[0]] += np.float32(wi) * dl
                delta /= np.float32(wsum)
        return Selection(len(prompt), [r.record_id for r in recs], w[: len(recs)], null, code, hard, prompt_pass=keep, delta=delta, best_score=best_score)

    def selection_for(self, ids: np.ndarray) -> Selection:
        ids = np.asarray(ids, np.int32).reshape(-1)
        for L in range(len(ids), 0, -1):  # longest cached prompt that prefixes this query
            s = self._sel.get(ids[:L].tobytes())
            if s is not None:
                return s
        s = self._select(ids)
        self._sel[ids.tobytes()] = s
        return s

    def reset_queries(self) -> None:
        self._sel.clear()

    # ------------------------------------------------------------------ read path
    def predict(self, ids, full: bool = False) -> ForwardResult:
        ids = np.asarray(ids, np.int32).reshape(-1)
        sel = self.selection_for(ids)
        cost = RevisionCost(phase="query")
        if sel.prompt_pass is not None and not full and len(ids) == sel.prompt_len:
            fr = sel.prompt_pass  # cached observation of the prompt position (already charged by the selection)
            self.cost_counters["cached_prompt_reads"] += 1
        else:
            fr = self.base.forward(ids, (), retain_sites=True, phase="query", last_only=not full)
            cost.add(fr.cost)
            cost.extra_pass_forwards += 1
        if sel.hard_null:
            return ForwardResult(logits=np.asarray(fr.logits), sites={}, cost=cost)
        obs = observation_from_pass(fr, ids, prompt_mask(min(sel.prompt_len, len(ids)), len(ids)), self.enc.base_hash, self.enc.encoder_version, self.cfg.reader.taps)
        q = self.jit_query(self.params["reader"], *obs_arrays(obs, self.cfg.reader))
        t = len(ids) - sel.prompt_len  # answer position of this read (0 = the prompt's last position)
        if sel.delta is None or t >= sel.delta.shape[0]:
            if sel.delta is not None and self.cfg.controller.delta_replaces_controller:
                return ForwardResult(logits=np.asarray(fr.logits), sites={}, cost=cost)  # beyond the taught answer: no write
            W = np.array(self.jit_writes(self.params["controller"], q, jnp.asarray(sel.code), jnp.asarray(1.0 - sel.null_mass)), np.float32)
        else:
            W = np.array(self.jit_writes_with_delta(self.params["controller"], q, jnp.asarray(sel.code), jnp.asarray(sel.delta[t]), jnp.asarray(1.0 - sel.null_mass)), np.float32)
        p = len(ids) - 1
        if self.cfg.single_site:
            W[0] = 0.0
            W[1] = 0.0
        first = 3 if self.cfg.single_site else 1
        wl = [Write(SiteId(m, self.blocks[m], p), W[m - 1]) for m in (1, 2, 3) if m >= first]
        fr2 = self.base.forward_from(first, fr.hidden[first], ids, wl, phase="query", retain_sites=False, last_only=not full)
        cost.add(fr2.cost)
        self.cost_counters["corrected_partial_passes"] += 1
        cost.records_touched += len(sel.record_ids)
        return ForwardResult(logits=np.asarray(fr2.logits), sites={}, cost=cost)

    def predict_logits(self, ids) -> np.ndarray:
        return self.predict(ids).logits

    def last_logits_batch(self, seqs: list[np.ndarray], phase: str = "query") -> np.ndarray:
        return np.stack([self.predict(s).logits for s in seqs])

    # ------------------------------------------------------------------ learning path
    def update_item(self, item: EditItem, router=None, budget=None) -> ItemOutcome:
        before = self.params_hash
        support = support_from_edit_item(item)
        trace, cost = adapt_record(self, support, self.cfg.fast)
        self.reset_queries()
        if params_hash(self.params) != before:
            raise RuntimeError("reusable weights changed during adaptation (gate 2)")
        tau = self.cfg.tau_edit
        acquired = trace.accepted and all(np.isfinite(v) and v <= tau for v in trace.per_prefix_loss_after)
        code = "accepted" if trace.accepted else "rejected_no_improvement"
        prefix_outcomes = [{"prefix_index": t, "loss_before": None, "loss_after": v, "code": code} for t, v in enumerate(trace.per_prefix_loss_after)]
        c = CostRecord(phase="learning")
        c.add(cost)
        return ItemOutcome(item_id=item.item_id, code=code, acquired_threshold_all_prefixes=bool(acquired), prefix_outcomes=prefix_outcomes,
                           rounds_used=trace.steps_used, cost=c, codes=[code])

    # ------------------------------------------------------------------ state
    def export_state(self) -> LearnerState:
        st = self.store.export()
        st.scalars["params_hash"] = self.params_hash
        st.scalars["n_params"] = self.n_params
        st.scalars["config"] = self.semantic_config()
        return st

    def semantic_config(self) -> str:
        return json.dumps({"reader": self.cfg.reader.__dict__, "controller": {**self.cfg.controller.__dict__, "bank_scales": list(self.cfg.controller.bank_scales)},
                           "fast": self.cfg.fast.__dict__, "null_threshold": self.cfg.null_threshold, "single_site": self.cfg.single_site,
                           "cache_prompt_pass": self.cfg.cache_prompt_pass, "hard_top1": self.cfg.hard_top1, "min_score": self.cfg.min_score, "base": self.enc.base_hash, "encoder_version": self.enc.encoder_version}, default=str, sort_keys=True)

    def import_state(self, st: LearnerState) -> None:
        if st.scalars.get("params_hash") != self.params_hash:
            raise RuntimeError("snapshot was produced with different reusable weights")
        if st.scalars.get("config") != self.semantic_config():
            raise RuntimeError("snapshot was produced under a different semantic configuration (R23-06)")
        self.store = RecordStore.from_state(st)
        self.reset_queries()

    def state_hash(self) -> str:
        return self.export_state().content_hash()

    def memory_bytes(self) -> MemoryReport:
        b = self.store.bytes()
        return MemoryReport(allocated_bytes=b["total"], occupied_bytes=b["total"], per_bank={0: b}, index_bytes=b["index"], key_dim=self.cfg.reader.width,
                            value_dim=self.cfg.reader.d_code, occupancy={0: len(self.store.active_records())}, ceiling_bytes=self.cfg.ceiling_bytes)

    def base_checksum(self) -> str:
        return self.enc.base_hash
