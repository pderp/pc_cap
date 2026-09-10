"""Learning a complete edit (CAP-06 ``round_update``, CAP-07 ``update_item``; PDF F.3; PC-3/5/6).

``round_update`` (one round at one gold prefix):
 1. current prediction through the cap (live retrieval) → ``L = CE(p, y_t)``;
 2. candidate directions: one reverse pass of the base at the current writes → ``d_m = −g/‖g‖``
    (``Transport``); ``no_direction`` recorded per bank;
 3./4. the router schedules ``b`` banks from a ``RoundContext`` (no slot metadata, SD-4);
 5. transactional search per scheduled bank in increasing depth: reserve ``A/b`` (no
    redistribution); after an accepted earlier write recompute features, gates, loss and credit;
    resolve the conflict/allocation in a private transaction (F.2); candidates
    ``Δv = w·a·b_m·d_m`` for ``a ∈ {A/b, A/2b, A/4b, A/8b}`` plus no-op, each evaluated from the
    same transaction snapshot with ordinary live retrieval; choose the smallest loss, tie → smaller
    increment; commit only if the improvement exceeds ``max(1e-8, 1e-6·L)`` else restore exactly;
 6. aggregate ``Σ‖Δv_m‖/b_m ≤ A`` asserted; every forward/reverse charged; a decision record per
    round (F.7).

``update_item``: visit every gold prefix ``(x, y_<t)`` including the terminating newline; at most
``R = 5`` rounds per prefix; stop at ``CE ≤ τ_edit``; per-prefix threshold attainment recorded
separately from end-of-item free generation (evaluated by the harness, not here); metadata on
commit (target, digest, version, use count once per item, last use, optional loss EMA);
``ItemOutcome`` with codes; ``acquisition_failure`` is an outcome, not an exception.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.cap.transaction import Transaction, resolve_write_target
from pccap.contracts import Budget, CostRecord, EditItem, ItemOutcome, RoundContext, Router, SiteId
from pccap.harness.records import DecisionRecord, OutcomeCode
from pccap.transport.transport import Transport

GRID = (1.0, 0.5, 0.25, 0.125)  # multiples of A/b


@dataclass
class RoundResult:
    loss_before: float
    loss_after: float
    route: list[int]
    scores: dict[int, float]
    accepted: dict[int, float]  # bank -> ||dv||/b_m
    codes: list[str]
    per_bank: dict[int, dict]
    cost: CostRecord
    aggregate_normalized: float = 0.0
    record: DecisionRecord | None = None


@dataclass
class PrefixOutcome:
    prefix_index: int
    target: int
    loss_start: float
    loss_end: float
    rounds: int
    reached_threshold: bool
    codes: list[str] = field(default_factory=list)


def _digest16(item: EditItem) -> bytes:
    d = item.digest
    if isinstance(d, str):
        d = bytes.fromhex(d) if len(d) == 32 else d.encode()
    return bytes(d)[:16].ljust(16, b"\0")


def directions_at(cap, ids, target: int, writes: dict[int, np.ndarray], transport: Transport, phase: str = "learning"):
    """Credit signal at the three sites at the current writes (retrieval frozen: the writes are fixed
    vectors), turned into unit directions by ``transport``.

    * ``cap.cfg.credit == "adjoint"`` (SB, SE-A): one reverse pass; the transport's sign −1 descends
      the gradient. Charged by the caller as 1 forward + 1 reverse.
    * ``cap.cfg.credit == "error"`` (SE-E): the settled ePC error ``e_site`` after ``credit_iters``
      iterations (``base.infer_errors``, PDF D.6/F.6; SD-6); the descent direction is ``+e`` (the
      wrapper's ``descent_sign``), delivered through the same transport by passing
      ``−descent_sign·e`` so the transport's −1 yields ``+e/‖e‖``. Charged from the inference's own
      cost record (``iters+1`` forwards and reverses, ``settle_iters``), returned as ``extra``.
    """
    p = len(ids) - 1
    wl = cap._writes_list(p, writes)
    out = {}
    extra = None
    blocks = getattr(cap.base, "bank_blocks", None) or g.BANK_BLOCK  # a base may declare its own sites (grammar: 1/3/5)
    if getattr(cap.cfg, "credit", "adjoint") == "error":
        er = cap.base.infer_errors(ids, target, iters=int(cap.cfg.credit_iters), writes=wl, phase=phase)
        sign = float(getattr(cap.base, "descent_sign", 1.0))
        for m in cap.cfg.banks():
            site = SiteId(m, blocks[m], p)
            e = np.asarray(cap.base.error_at_site(er, m), np.float32)
            out[m] = transport.direction(-sign * e, site)
        extra = er.cost
    else:
        grads = cap.base.adjoint(ids, target, wl, phase=phase)
        for m in cap.cfg.banks():
            site = SiteId(m, blocks[m], p)
            out[m] = transport.direction(np.asarray(grads[site], np.float32), site)
    directions_at.last_extra_cost = extra
    return out


def _charge_credit(cost: CostRecord) -> None:
    """Round-level counters for one credit computation: adjoint = 1 forward + 1 reverse; error credit =
    the inference's own record (iters+1 forwards/reverses and settle_iters)."""
    extra = getattr(directions_at, "last_extra_cost", None)
    if extra is None:
        cost.reverses += 1
        cost.full_forwards += 1
    else:
        cost.full_forwards += int(extra.full_forwards)
        cost.reverses += int(extra.reverses)
        cost.settle_iters += int(extra.settle_iters)
        directions_at.last_extra_cost = None


def round_update(cap, ids: np.ndarray, target: int, item: EditItem, router: Router, budget: Budget,
                 prefix_index: int, round_index: int, transport: Transport | None = None,
                 weight_fn: Callable[[int, int], float] | None = None, correction_track: bool = False,
                 seed: int = 0, permitted_banks=None) -> RoundResult:
    transport = transport or Transport()
    ids = np.asarray(ids, np.int32).reshape(-1)
    p = len(ids) - 1
    digest = _digest16(item)
    cost = CostRecord(phase="learning")
    codes: list[str] = []
    per_bank: dict[int, dict] = {}

    # 1. current prediction
    ep = cap.edited_forward(ids)
    cost.add(ep.cost)
    L = cap.loss_of(ep, target)
    # 2. directions
    dirs = directions_at(cap, ids, target, ep.writes, transport)
    _charge_credit(cost)
    # 3./4. route
    ctx = RoundContext(prefix_ids=ids, loss=L, directions=dirs, bank_scales=dict(cap.cfg.bank_scales),
                       rng_material=(seed, digest, prefix_index, round_index), permitted_banks=permitted_banks, position=p)
    if hasattr(router, "bind_probe"):  # C2: loss oracle for temporary forced writes (probes charged by the base)
        router.bind_probe(lambda m, v: cap.loss_of(cap.edited_forward(ids, extra={m: v}), target))
    dec = router.schedule(ctx)
    cost.add(dec.cost)
    codes += dec.codes
    scores = dict(dec.scores)
    accepted: dict[int, float] = {}
    if dec.abstain or not dec.banks:
        if OutcomeCode.abstain.value not in codes and not dec.banks:
            codes.append(OutcomeCode.abstain.value)
        return RoundResult(L, L, [], scores, {}, codes, per_bank, cost)

    b = len(dec.banks)
    share = budget.A / b
    L_cur = L
    ep_cur = ep
    dirs_cur = dirs
    for m in dec.banks:  # increasing depth
        if accepted and m != dec.banks[0]:
            # 5. recompute features, gates, loss and credit after an accepted earlier write
            ep_cur = cap.edited_forward(ids)
            cost.add(ep_cur.cost)
            L_cur = cap.loss_of(ep_cur, target)
            dirs_cur = directions_at(cap, ids, target, ep_cur.writes, transport)
            _charge_credit(cost)
        d = dirs_cur[m]
        if d.status != "ok":
            codes.append(f"{OutcomeCode.no_direction.value}:{m}")
            per_bank[m] = {"code": OutcomeCode.no_direction.value}
            continue
        bs = cap.banks[m]
        bank = bs.bank
        q = ep_cur.keys[m]
        tx = Transaction(bs).begin()
        wt = resolve_write_target(bs, q, target, digest, item.version, cap.item_index, cap.cfg.radii.get(m, 0.0),
                                  revision=item.revision, correction_track=correction_track)
        if wt.rejected:
            tx.rollback()
            codes += [f"{c}:{m}" for c in wt.codes]
            per_bank[m] = {"code": wt.codes[-1], "slot": -1}
            continue
        slot = wt.slot
        base_value = bank.values[slot].copy()
        w = 1.0 if weight_fn is None else float(weight_fn(m, slot))
        b_m = float(cap.cfg.bank_scales[m])
        cands = []
        best = (L_cur, 0.0, None)  # (loss, normalized increment, dv) ; no-op first
        for mult in GRID:
            a = share * mult
            dv = (w * a * b_m) * np.asarray(d.direction, np.float32)
            bank.values[slot] = base_value + dv  # from the same snapshot, not cumulative
            ep_c = cap.edited_forward(ids)
            cost.add(ep_c.cost)
            cost.search_candidates += 1
            Lc = cap.loss_of(ep_c, target)
            if not np.isfinite(Lc):
                tx.rollback()
                raise FloatingPointError(f"non-finite candidate loss at bank {m}")  # Op. rule 8
            norm_inc = float(np.linalg.norm(dv) / b_m)
            cands.append({"a": a, "loss": Lc, "normalized_increment": norm_inc, "fired": ep_c.fired.get(m, -1)})
            if Lc < best[0] or (Lc == best[0] and best[2] is not None and norm_inc < best[1]):
                best = (Lc, norm_inc, dv)
        bank.values[slot] = base_value  # restore the evaluated origin before deciding
        improvement = L_cur - best[0]
        if best[2] is not None and improvement > budget.min_improvement(L_cur):
            bank.values[slot] = base_value + best[2]  # exactly the evaluated candidate
            bank.metadata.on_commit(slot, target=target, digest=digest, version=item.version, item_index=cap.item_index,
                                  pre_update_loss=L_cur if weight_fn is not None else None)
            if bs.tracker.active:
                bs.tracker.note_use(slot)
            else:  # round driven outside update_item (tests/diagnostics): a one-round item scope
                bs.tracker.begin_item(digest)
                bs.tracker.note_use(slot)
                bs.tracker.end_item()
            tx_codes = list(wt.codes) + [OutcomeCode.accepted.value]
            tx.commit()
            accepted[m] = best[1]
            codes += [f"{c}:{m}" for c in tx_codes]
            per_bank[m] = {"code": OutcomeCode.accepted.value, "slot": slot, "allocated": wt.allocated,
                           "evicted": wt.evicted, "chosen_a": float(best[1] * b_m / (w * b_m) if w else 0.0),
                           "candidates": cands, "loss_before": L_cur, "loss_after": best[0]}
            L_cur = best[0]
        else:
            tx.rollback()
            codes.append(f"{OutcomeCode.rejected_no_improvement.value}:{m}")
            per_bank[m] = {"code": OutcomeCode.rejected_no_improvement.value, "slot": slot, "candidates": cands,
                           "loss_before": L_cur}
    agg = float(sum(accepted.values()))
    if agg > budget.A * (1 + 1e-6):
        raise AssertionError(f"aggregate normalized increment {agg} exceeds A={budget.A}")  # PC-6
    if accepted:
        ep_end = cap.edited_forward(ids)
        cost.add(ep_end.cost)
        L_after = cap.loss_of(ep_end, target)
    else:
        L_after = L
    rec = DecisionRecord(item_digest=digest.hex(), prefix_index=prefix_index, round=round_index,
                         candidate_banks=list(dec.banks), signed_scores={str(k): float(v) for k, v in scores.items()},
                         chosen_route=[m for m in dec.banks], accepted_increment={str(k): float(v) for k, v in accepted.items()},
                         loss_before=L, loss_after=L_after, codes=[c.split(":")[0] for c in codes if c.split(":")[0] in
                                                                     {e.value for e in OutcomeCode}],
                         cost=cost.as_dict(), rule=dec.rule, per_bank={str(k): v for k, v in per_bank.items()})
    return RoundResult(L, L_after, list(dec.banks), scores, accepted, codes, per_bank, cost, agg, rec)


def update_item(cap, item: EditItem, router: Router, budget: Budget, transport: Transport | None = None,
                on_decision: Callable[[DecisionRecord], None] | None = None, correction_track: bool = False,
                seed: int = 0, permitted_banks=None, weight_fn=None) -> ItemOutcome:
    transport = transport or Transport()
    digest = _digest16(item)
    cap.item_index += 1
    for bs in cap.banks.values():
        bs.tracker.begin_item(digest)
    cost = CostRecord(phase="learning")
    prefixes: list[PrefixOutcome] = []
    ids = np.asarray(item.prompt_ids, np.int32).reshape(-1)
    rounds_total = 0
    codes: list[str] = []
    try:
        for t, y in enumerate(np.asarray(item.answer_ids, np.int32)):
            y = int(y)
            ep = cap.edited_forward(ids)
            cost.add(ep.cost)
            L0 = cap.loss_of(ep, y)
            L = L0
            used = 0
            reached = L <= budget.tau_edit
            pcodes: list[str] = []
            while not reached and used < budget.R:
                rr = round_update(cap, ids, y, item, router, budget, t, used, transport, weight_fn, correction_track,
                                  seed, permitted_banks)
                cost.add(rr.cost)
                cost.prefix_microsteps += 1
                # base calls were charged by the base; charge the round-level counters once here
                cap.ledger.charge(CostRecord(phase="learning", prefix_microsteps=1, search_candidates=rr.cost.search_candidates,
                                             router_probes=rr.cost.router_probes))
                used += 1
                rounds_total += 1
                pcodes += rr.codes
                if on_decision is not None and rr.record is not None:
                    on_decision(rr.record)
                L = rr.loss_after
                reached = L <= budget.tau_edit
            prefixes.append(PrefixOutcome(t, y, L0, L, used, reached, pcodes))
            ids = np.concatenate([ids, np.int32([y])])
    finally:
        for bs in cap.banks.values():
            bs.tracker.end_item()
    all_reached = all(p.reached_threshold for p in prefixes)
    code = OutcomeCode.accepted.value if all_reached else OutcomeCode.acquisition_failure.value
    return ItemOutcome(item_id=item.item_id, code=code, acquired_threshold_all_prefixes=all_reached,
                       prefix_outcomes=[p.__dict__ for p in prefixes], rounds_used=rounds_total, cost=cost, codes=codes)
