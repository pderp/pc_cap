"""Matched-update control (X0-02; DEC-034(a); R1-15): the v0-shaped cap with stable keys whose slot VALUES are taught by
the same support-only optimizer interface as the revision's fast rule — K gradient steps with a step size, a
loss-threshold stopping rule, an accepted-step check with rollback, and the v0 aggregate bound Σ_m ‖Δv_m‖/b_m ≤ A —
instead of v0's geometric candidate search. Everything else (banks, radii, allocation, conflict handling, eviction,
snapshots, evaluation) is inherited from StableCap/Cap. The step direction is the base adjoint at each site
(normalized per bank; one step of size lr·b_m), so one step with lr = A/3 equals v0's full per-bank share.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from pccap.cap.cap import CapConfig
from pccap.cap.learn import _digest16
from pccap.cap.transaction import Transaction, resolve_write_target
from pccap.contracts import Budget, CostRecord, EditItem, ItemOutcome, SiteId, Write
from pccap.harness.records import OutcomeCode
from pccap.revision_v1.v0_stable import StableCap


@dataclass
class MatchedRule:
    steps: int = 3
    lr: float = 0.1  # step size in units of b_m along the normalized site gradient
    improvement_abs: float = 1e-8


class MatchedUpdateCap(StableCap):
    """StableCap + gradient-step value updates (the common fast-update rule)."""

    own_update_path = True  # run_stream calls this class's update_item instead of pccap.cap.learn.update_item

    def __init__(self, base, cfg: CapConfig, ledger, rule: MatchedRule | None = None):
        super().__init__(base, cfg, ledger)
        self.rule = rule or MatchedRule()

    def update_item(self, item: EditItem, router=None, budget: Budget | None = None) -> ItemOutcome:
        budget = budget or Budget()
        digest = _digest16(item)  # the same 16-byte owner digest v0 records in slot metadata
        self.item_index += 1
        for bs in self.banks.values():
            bs.tracker.begin_item(digest)
        cost = CostRecord(phase="learning")
        prefixes, codes = [], []
        ids = np.asarray(item.prompt_ids, np.int32).reshape(-1)
        rounds_total = 0
        try:
            for t, y in enumerate(np.asarray(item.answer_ids, np.int32)):
                y = int(y)
                ep = self.edited_forward(ids)
                cost.add(ep.cost)
                L0 = self.loss_of(ep, y)
                L, used, pcodes = L0, 0, []
                reached = L <= budget.tau_edit
                if not reached:
                    L, used, pcodes = self._teach_prefix(ids, y, item, digest, budget, cost)
                    rounds_total += used
                    reached = L <= budget.tau_edit
                codes += pcodes
                prefixes.append({"prefix_index": t, "target": y, "loss_before": L0, "loss_after": L, "rounds": used, "reached_threshold": reached, "codes": pcodes})
                ids = np.concatenate([ids, np.int32([y])])
        finally:
            for bs in self.banks.values():
                bs.tracker.end_item()
        all_reached = all(p["reached_threshold"] for p in prefixes)
        code = OutcomeCode.accepted.value if all_reached else OutcomeCode.acquisition_failure.value
        return ItemOutcome(item_id=item.item_id, code=code, acquired_threshold_all_prefixes=all_reached, prefix_outcomes=prefixes,
                           rounds_used=rounds_total, cost=cost, codes=codes)

    def _teach_prefix(self, ids: np.ndarray, y: int, item: EditItem, digest: bytes, budget: Budget, cost: CostRecord) -> tuple[float, int, list[str]]:
        p = len(ids) - 1
        ep = self.edited_forward(ids)
        cost.add(ep.cost)
        L0 = self.loss_of(ep, y)
        txs, slots, base_values, codes = {}, {}, {}, []
        for m in self.cfg.banks():
            bs = self.banks[m]
            tx = Transaction(bs).begin()
            wt = resolve_write_target(bs, ep.keys[m], y, digest, item.version, self.item_index, self.cfg.radii.get(m, 0.0), revision=item.revision)
            if wt.rejected:
                tx.rollback()
                codes += [f"{c}:{m}" for c in wt.codes]
                continue
            txs[m], slots[m] = tx, wt.slot
            base_values[m] = bs.bank.values[wt.slot].copy()
            codes += [f"{c}:{m}" for c in wt.codes]
        if not slots:
            return L0, 0, codes + [OutcomeCode.abstain.value]
        L, used = L0, 0
        for _ in range(self.rule.steps):
            ep_k = self.edited_forward(ids)
            cost.add(ep_k.cost)
            wl = [Write(SiteId(m, self.blocks[m], p), ep_k.writes[m]) for m in self.cfg.banks() if np.any(ep_k.writes[m])]
            grads = self.base.adjoint(ids, y, wl, phase="learning")
            cost.reverses += 1
            cost.full_forwards += 1
            for m, s in slots.items():
                g = np.asarray(grads[SiteId(m, self.blocks[m], p)], np.float32)
                n = float(np.linalg.norm(g))
                if n > 0:
                    self.banks[m].bank.values[s] -= np.float32(self.rule.lr * float(self.cfg.bank_scales[m])) * g / np.float32(n)
            used += 1
            # aggregate bound on the total increment, as v0's per-round budget: Σ_m ‖Δv_m‖ / b_m ≤ A
            inc = {m: self.banks[m].bank.values[s] - base_values[m] for m, s in slots.items()}
            agg = sum(float(np.linalg.norm(v)) / float(self.cfg.bank_scales[m]) for m, v in inc.items())
            if agg > budget.A:
                for m, s in slots.items():
                    self.banks[m].bank.values[s] = base_values[m] + inc[m] * np.float32(budget.A / agg)
            ep_e = self.edited_forward(ids)
            cost.add(ep_e.cost)
            L = self.loss_of(ep_e, y)
            if not np.isfinite(L):
                for tx in txs.values():
                    tx.rollback()
                raise FloatingPointError("non-finite loss during matched update")
            if L <= budget.tau_edit:
                break
        if L < L0 - self.rule.improvement_abs:
            for m, s in slots.items():
                self.banks[m].bank.metadata.on_commit(s, target=y, digest=digest, version=item.version, item_index=self.item_index)
                self.banks[m].tracker.note_use(s)
                codes += [f"{c}:{m}" for c in txs[m].commit()]
            codes.append(OutcomeCode.accepted.value)
            return L, used, codes
        for tx in txs.values():
            tx.rollback()
        codes.append(OutcomeCode.rejected_no_improvement.value)
        return L0, used, codes
