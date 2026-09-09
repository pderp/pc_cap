"""The cap: three radius-gated banks over a frozen base (S0-10 core; PDF F.1, F.4, F.7).

Read/write semantics (F.1): banks act in increasing depth; each bank reads its key
``q_m = z(h_p^{(l_m)})`` from the *current edited pass* (R-h; earlier writes already applied),
retrieves, and adds the firing slot's value at position ``p`` before the next block. The edited
forward is therefore sequential: one full forward with no writes, then a partial forward from
bank ``m``'s site whenever bank ``m`` fires (``base.forward_from``), so later banks see the
effect of earlier writes ("retrieval drift", logged per query).

``Cap`` exposes the contract: ``predict`` (read-only; asserts the learner hash is unchanged),
``update_item`` (CAP-07, delegated to ``cap.learn``), ``serialize``/``restore``/``clone``
(byte-exact via ``harness.snapshot``), ``memory_bytes`` (PDF App. B). Cap-off is the same code
with no banks firing: writes are all-zero rows, which the base applies exactly (SD-10).

Probe and candidate evaluation for routers/search use ``edited_forward(..., extra=...)``: an
extra additive write at one bank on top of the current retrieved values, recomputed downstream
with live discrete retrieval, without committing anything.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.cap import memory as mem
from pccap.cap.bank import Bank
from pccap.cap.features import z as key_feature
from pccap.cap.transaction import BankState
from pccap.contracts import (
    Budget,
    CostRecord,
    EditItem,
    ForwardResult,
    ItemOutcome,
    MemoryReport,
    Router,
    SiteId,
    Write,
)
from pccap.harness.ledger import Ledger
from pccap.harness.snapshot import LearnerState

ARM_BANKS = {"C0": (3,), "C1": (1, 2, 3), "C2": (1, 2, 3), "CR": (1, 2, 3), "CO": (1, 2, 3)}


@dataclass
class EditedPass:
    """Result of one edited forward: logits, per-bank keys, retrievals, writes, cost."""

    logits: np.ndarray
    keys: dict[int, np.ndarray]
    sites: dict[int, np.ndarray]  # pre-write residual rows at p (edited pass)
    hidden: dict[int, np.ndarray]  # pre-write full residual per site (for forward_from)
    fired: dict[int, int]  # bank -> slot (-1 none)
    writes: dict[int, np.ndarray]  # bank -> applied vector (zeros when nothing fired)
    cost: CostRecord
    n: int = 0
    p: int = 0


@dataclass
class CapConfig:
    arm: str = "C1"
    read: str = "h"
    radii: dict[int, float] = field(default_factory=lambda: {1: 0.0, 2: 0.0, 3: 0.0})
    bank_scales: dict[int, float] = field(default_factory=lambda: {1: 1.0, 2: 1.0, 3: 1.0})  # b_m
    seed: int = 0
    overhead_bytes: int = 0
    d: int = 768
    key_dim: int | None = None

    def banks(self) -> tuple[int, ...]:
        return ARM_BANKS[self.arm]


class Cap:
    def __init__(self, base, cfg: CapConfig, ledger: Ledger | None = None):
        self.base = base
        self.cfg = cfg
        self.ledger = ledger if ledger is not None else getattr(base, "ledger", Ledger())
        self.d = int(cfg.d)
        self.dk = int(cfg.key_dim or cfg.d)
        self.rng = random.Random(cfg.seed)
        ceilings = mem.bank_ceilings(cfg.arm, self.d)
        self.layouts = {m: mem.BankLayout.plan(m, ceilings[m], self.dk, self.d, cfg.overhead_bytes) for m in cfg.banks()}
        self.banks: dict[int, BankState] = {}
        for m in cfg.banks():
            bank = Bank(m, self.layouts[m].capacity, self.dk, self.d, radius_default=cfg.radii.get(m, 0.0))
            self.banks[m] = BankState.new(bank, rng_get=self.rng.getstate, rng_set=self.rng.setstate)
        self.item_index = 0
        self.drift_log: list[dict] = []

    # ------------------------------------------------------------------ keys
    def key(self, site_row: np.ndarray) -> np.ndarray:
        if self.cfg.read != "h":
            raise NotImplementedError("read variants other than R-h arrive with CAP-08")
        return key_feature(np.asarray(site_row, np.float32))

    # ------------------------------------------------------------------ edited forward
    def _writes_list(self, p: int, wr: dict[int, np.ndarray]) -> list[Write]:
        return [Write(SiteId(m, g.BANK_BLOCK[m], p), v) for m, v in wr.items() if np.any(v)]

    def edited_forward(self, ids, extra: dict[int, np.ndarray] | None = None, phase: str = "learning",
                       frozen_retrieval: dict[int, int] | None = None) -> EditedPass:
        """Sequential live-retrieval forward. ``extra[m]`` is added at bank m on top of the
        retrieved value (probes / candidates). ``frozen_retrieval`` pins bank→slot choices
        (used inside a settling/adjoint call so gates do not switch)."""
        ids = np.asarray(ids, np.int32).reshape(-1)
        n = len(ids)
        p = n - 1
        extra = extra or {}
        cost = CostRecord(phase=phase)
        fr = self.base.forward(ids, (), retain_sites=True, phase=phase)
        cost.add(fr.cost)
        writes: dict[int, np.ndarray] = {}
        keys: dict[int, np.ndarray] = {}
        sites: dict[int, np.ndarray] = {}
        hidden: dict[int, np.ndarray] = {}
        fired: dict[int, int] = {}
        for m in self.cfg.banks():
            sid = SiteId(m, g.BANK_BLOCK[m], p)
            site_row = np.asarray(fr.sites[sid], np.float32)
            sites[m] = site_row
            hidden[m] = np.asarray(fr.hidden[m], np.float32)
            q = self.key(site_row)
            keys[m] = q
            bank = self.banks[m].bank
            if frozen_retrieval is not None and m in frozen_retrieval:
                slot = frozen_retrieval[m]
                value = bank.values[slot].copy() if slot >= 0 else np.zeros(self.d, np.float32)
            else:
                value, r = bank.value_for(q)
                slot = r.slot
            fired[m] = int(slot)
            v = value + extra.get(m, 0.0)
            v = np.asarray(v, np.float32)
            writes[m] = v
            if np.any(v):  # downstream must see this write: partial forward from this site
                fr = self.base.forward_from(m, hidden[m], ids, self._writes_list(p, writes), phase=phase, retain_sites=True)
                cost.add(fr.cost)
        return EditedPass(logits=np.asarray(fr.logits), keys=keys, sites=sites, hidden=hidden, fired=fired,
                          writes=writes, cost=cost, n=n, p=p)

    def loss_of(self, ep: EditedPass, target: int) -> float:
        row = ep.logits[ep.p].astype(np.float64)
        m = row.max()
        return float(m + np.log(np.exp(row - m).sum()) - row[int(target)])

    # ------------------------------------------------------------------ contract
    def predict(self, ids) -> ForwardResult:
        before = self.state_hash()
        ep = self.edited_forward(ids, phase="query")
        if self.state_hash() != before:
            raise RuntimeError("predict mutated learner state (PC-8)")
        sites = {SiteId(m, g.BANK_BLOCK[m], ep.p): ep.sites[m] for m in ep.sites}
        return ForwardResult(logits=ep.logits, sites=sites, cost=ep.cost)

    def predict_logits(self, ids) -> np.ndarray:
        return self.predict(ids).logits

    def update_item(self, item: EditItem, router: Router, budget: Budget) -> ItemOutcome:
        from pccap.cap.learn import update_item

        return update_item(self, item, router, budget)

    # ------------------------------------------------------------------ state
    def export_state(self) -> LearnerState:
        arrays = {}
        cindex = {}
        for m, bs in self.banks.items():
            for k, v in bs.bank.arrays().items():
                arrays[f"bank{m}/{k}"] = v.copy()
            cindex[str(m)] = bs.cindex.export()
        tracker = self.banks[self.cfg.banks()[0]].tracker.snapshot()
        return LearnerState(
            arrays=arrays,
            scalars={"item_index": self.item_index, "arm": self.cfg.arm, "read": self.cfg.read,
                     "radii": {str(k): float(v) for k, v in self.cfg.radii.items()},
                     "bank_scales": {str(k): float(v) for k, v in self.cfg.bank_scales.items()},
                     "capacities": {str(m): self.layouts[m].capacity for m in self.layouts}, "seed": self.cfg.seed},
            correction_index={"per_bank": cindex},
            use_tracker=(tracker[0].hex() if tracker[0] else None, list(tracker[1])),
            rng=LearnerState.capture_rng(py_random=self.rng),
        )

    def import_state(self, st: LearnerState) -> None:
        for m, bs in self.banks.items():
            bs.bank.load_arrays({k.split("/", 1)[1]: v for k, v in st.arrays.items() if k.startswith(f"bank{m}/")})
            bs.cindex.load(st.correction_index["per_bank"][str(m)])
        self.item_index = int(st.scalars["item_index"])
        digest, used = st.use_tracker
        for bs in self.banks.values():
            bs.tracker.restore((bytes.fromhex(digest) if digest else None, tuple(used)))
        LearnerState.apply_rng(st.rng, py_random=self.rng)

    def state_hash(self) -> str:
        return self.export_state().content_hash()

    def serialize(self) -> bytes:
        from pccap.harness.snapshot import serialize

        return serialize(self.export_state())

    def restore(self, blob: bytes) -> None:
        from pccap.harness.snapshot import restore

        self.import_state(restore(blob))

    def clone(self) -> "Cap":
        c = Cap(self.base, self.cfg, self.ledger)
        c.import_state(self.export_state().clone())
        return c

    def memory_bytes(self) -> MemoryReport:
        rep = mem.memory_report({m: bs.bank for m, bs in self.banks.items()}, self.layouts, mem.b_cap(self.d))
        idx = sum(bs.index_bytes() for bs in self.banks.values())
        rep.index_bytes += idx
        rep.allocated_bytes += idx
        rep.occupied_bytes += idx
        return rep

    def base_checksum(self) -> str:
        return self.base.checksum()


def item_digest_bytes(item: EditItem) -> bytes:
    return item.digest if isinstance(item.digest, bytes) else hashlib.sha256(str(item.digest).encode()).digest()[:16]


__all__ = ["Cap", "CapConfig", "EditedPass", "item_digest_bytes", "Sequence"]
