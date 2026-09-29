"""Useful adjoint updates under a per-item eight-step-PC operation allowance.

DEC-075 clarified by charlie: extra budget buys additional acquisition updates,
never repeated gradients at unchanged writes. The allowance comes from the same
item in its completed SE-E stream, fixed before this control is run. All learning
full/partial forwards and reverses cost one unit each. This is an operation proxy,
not a FLOP or wall-time equivalence. A partially evaluated round is rolled back;
its work remains charged. Threshold attainment may leave unused allowance.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import copy

import numpy as np

from pccap.cap import learn
from pccap.cap.cap import Cap
from pccap.contracts import CostRecord, ItemOutcome
from pccap.transport.transport import Transport

COUNTERS = ("full_forwards", "partial_forwards", "reverses")
TREATMENT = dict(
    credit="adjoint-matched",
    arm="SE-AM",
    reference_credit="error",
    reference_credit_iters=8,
    matching="per-item measured SE-E learning full_forwards + partial_forwards + reverses",
    extra_compute="additional transactional acquisition rounds, not repeated unchanged-write gradients",
    prefix_policy="gold-prefix order; same threshold and per-round A; R ceiling replaced by remaining operation allowance",
    stop="threshold attained for all prefixes, or next base call exceeds allowance; unfinished round rolled back",
    accounting="actual charged operations including rolled-back attempts; report unused allowance and completed rounds",
    interpretation="equal offered per-item operation allowance; not equal FLOPs, wall time, number of writes, or always equal realized spend",
)


def units(cost):
    return sum(cost[k] if isinstance(cost, dict) else getattr(cost, k) for k in COUNTERS)


class AllowanceExhausted(Exception):
    pass


class LimitedBase:
    """Admission check at each native base call, with no artificial ledger charge."""

    def __init__(self, base, allowance):
        self.base, self.allowance = base, allowance
        self.initial = units(base.ledger.totals()["learning"])

    @property
    def used(self):
        return units(self.base.ledger.totals()["learning"]) - self.initial

    def __getattr__(self, name):
        return getattr(self.base, name)

    def call(self, name, price, *args, **kwargs):
        if self.used + price > self.allowance:
            raise AllowanceExhausted
        before = self.used
        result = getattr(self.base, name)(*args, **kwargs)
        if self.used - before != price:
            raise RuntimeError(f"unexpected native operation price for {name}")
        return result

    def forward(self, *args, **kwargs):
        return self.call("forward", 1, *args, **kwargs)

    def forward_from(self, *args, **kwargs):
        return self.call("forward_from", 1, *args, **kwargs)

    def adjoint(self, *args, **kwargs):
        return self.call("adjoint", 2, *args, **kwargs)


def ledger_difference(before, after):
    return CostRecord(
        **{
            k: "learning"
            if k == "phase"
            else after[k]
            if k == "peak_mem_mib"
            else after[k] - before[k]
            for k in CostRecord.__dataclass_fields__
        }
    )


class MatchedCreditCap(Cap):
    own_update_path = True

    def __init__(self, base, cfg, ledger=None, *, allowances):
        if cfg.credit != "adjoint":
            raise ValueError("matched credit requires adjoint")
        if not allowances or any(type(n) is not int or n < 0 for n in allowances.values()):
            raise ValueError("nonnegative integer per-item operation allowances required")
        super().__init__(base, cfg, ledger)
        self.allowances = dict(allowances)
        self.on_decision = None
        self.on_budget = None
        self.router_seed = 0

    def export_state(self):
        state = super().export_state()
        state.scalars["pc12_treatment"] = copy.deepcopy(TREATMENT)
        state.scalars["pc12_allowances"] = dict(self.allowances)
        return state

    def import_state(self, state):
        if (
            state.scalars.get("pc12_treatment") != TREATMENT
            or state.scalars.get("pc12_allowances") != self.allowances
        ):
            raise ValueError("matched-credit snapshot treatment or allowance differs")
        super().import_state(state)

    def clone(self):
        result = type(self)(self.base, self.cfg, self.ledger, allowances=self.allowances)
        result.import_state(self.export_state().clone())
        result.on_decision, result.on_budget, result.router_seed = (
            self.on_decision,
            self.on_budget,
            self.router_seed,
        )
        return result

    def update_item(self, item, router, budget):
        if item.item_id not in self.allowances:
            raise ValueError("item missing from bound reference allowance")
        before = self.ledger.totals()["learning"]
        original_base = self.base
        limited = LimitedBase(original_base, self.allowances[item.item_id])
        self.base = limited
        self.item_index += 1
        for bs in self.banks.values():
            bs.tracker.begin_item(learn._digest16(item))
        prefixes, codes, rounds, stopped, attempted = [], [], 0, False, 0
        ids = np.asarray(item.prompt_ids, np.int32).reshape(-1)
        try:
            for t, target in enumerate(np.asarray(item.answer_ids, np.int32)):
                target = int(target)
                try:
                    ep = self.edited_forward(ids)
                    start = loss = self.loss_of(ep, target)
                except AllowanceExhausted:
                    stopped = True
                    break
                used, reached = 0, loss <= budget.tau_edit
                while not reached:
                    # Snapshot at the round boundary, retaining all earlier accepted rounds.
                    boundary = self.export_state()
                    attempted += 1
                    try:
                        rr = learn.round_update(
                            self,
                            ids,
                            target,
                            item,
                            router,
                            budget,
                            t,
                            used,
                            Transport(),
                            seed=self.router_seed,
                        )
                    except AllowanceExhausted:
                        self.import_state(boundary)
                        stopped = True
                        break
                    self.ledger.charge(
                        CostRecord(
                            phase="learning",
                            prefix_microsteps=1,
                            search_candidates=rr.cost.search_candidates,
                            router_probes=rr.cost.router_probes,
                        )
                    )
                    used += 1
                    rounds += 1
                    codes.extend(rr.codes)
                    loss = rr.loss_after
                    reached = loss <= budget.tau_edit
                    if self.on_decision is not None and rr.record is not None:
                        self.on_decision(rr.record)
                prefixes.append(
                    dict(
                        prefix_index=t,
                        target=target,
                        loss_start=start,
                        loss_end=loss,
                        rounds=used,
                        reached_threshold=reached,
                        codes=[],
                    )
                )
                if stopped:
                    break
                ids = np.concatenate([ids, np.int32([target])])
        finally:
            self.base = original_base
            for bs in self.banks.values():
                bs.tracker.end_item()
        cost = ledger_difference(before, self.ledger.totals()["learning"])
        attained = len(prefixes) == len(item.answer_ids) and all(
            p["reached_threshold"] for p in prefixes
        )
        record = dict(
            item_id=item.item_id,
            allowance=self.allowances[item.item_id],
            used=units(cost),
            unused=self.allowances[item.item_id] - units(cost),
            completed_rounds=rounds,
            attempted_rounds=attempted,
            rolled_back_incomplete_round=attempted > rounds,
            stop="operation_allowance" if stopped else "thresholds_attained",
            cost=cost.as_dict(),
            prefix_outcomes=prefixes,
        )
        if record["unused"] < 0:
            raise RuntimeError("matched control exceeded its reference operation allowance")
        if self.on_budget is not None:
            self.on_budget(record)
        return ItemOutcome(
            item_id=item.item_id,
            code="accepted" if attained else "acquisition_failure",
            acquired_threshold_all_prefixes=attained,
            prefix_outcomes=prefixes,
            rounds_used=rounds,
            cost=cost,
            codes=codes + (["operation_allowance"] if stopped else []),
        )
