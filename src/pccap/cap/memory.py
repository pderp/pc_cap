"""Byte ceiling and slot capacities (CAP-03; PDF App. B "Memory ceiling"; PC-6).

``B_cap = 6144 · (8d + 128)`` bytes (= 38,535,168 at d = 768). C0 gives all of it to bank 3;
three-bank arms split it into equal thirds (12,845,056 each; any remainder goes to bank 3 so
the sum is exactly ``B_cap``). With ``dk`` key coordinates the permissible slot count per bank is

    S_m = floor((B_m − fixed_overhead_m) / (4·dk + 4·d + 128))

where ``fixed_overhead_m`` is the *measured* byte size of indices and bookkeeping of an empty
bank (0 for the plain bank: slot ids are implicit; the correction index of CAP-04 adds bytes).
Nominal capacities at zero overhead: 6,144 (C0), 2,048 (thirds, dk = d), 1,374 (thirds, dk = 2d).
"""

from __future__ import annotations

from dataclasses import dataclass

from pccap.cap.metadata import SLOT_BYTES
from pccap.contracts import MemoryReport

THREE_BANK_ARMS = ("C1", "C2", "CR", "CO")
ONE_BANK_ARMS = ("C0",)


def b_cap(d: int) -> int:
    return 6144 * (8 * d + 128)


def slot_bytes(dk: int, d: int) -> int:
    return 4 * dk + 4 * d + SLOT_BYTES


def bank_ceilings(arm: str, d: int) -> dict[int, int]:
    B = b_cap(d)
    if arm in ONE_BANK_ARMS:
        return {3: B}
    if arm in THREE_BANK_ARMS:
        third = B // 3
        return {1: third, 2: third, 3: B - 2 * third}
    raise ValueError(f"unknown arm {arm}")


def capacity(B_m: int, dk: int, d: int, fixed_overhead: int = 0) -> int:
    if fixed_overhead < 0 or fixed_overhead > B_m:
        raise ValueError("overhead must be within [0, B_m]")
    return (B_m - fixed_overhead) // slot_bytes(dk, d)


@dataclass
class BankLayout:
    bank: int
    ceiling_bytes: int
    key_dim: int
    value_dim: int
    fixed_overhead: int
    capacity: int

    @classmethod
    def plan(cls, bank: int, ceiling_bytes: int, dk: int, d: int, fixed_overhead: int = 0) -> "BankLayout":
        return cls(bank, ceiling_bytes, dk, d, fixed_overhead, capacity(ceiling_bytes, dk, d, fixed_overhead))

    def allocated_bytes(self) -> int:
        return self.capacity * slot_bytes(self.key_dim, self.value_dim) + self.fixed_overhead

    def occupied_bytes(self, n_active: int) -> int:
        return n_active * slot_bytes(self.key_dim, self.value_dim) + self.fixed_overhead


def measured_overhead(bank) -> int:
    """Bytes of indices and bookkeeping of a bank beyond keys/values/metadata (CAP-04 adds the
    correction index; the plain bank has none)."""
    b = bank.array_bytes()
    extra = sum(v for k, v in b.items() if k not in ("keys", "values", "meta"))
    return int(extra) + int(getattr(bank, "index_bytes", lambda: 0)())


def memory_report(banks: dict[int, object], layouts: dict[int, BankLayout], ceiling: int) -> MemoryReport:
    per_bank = {}
    alloc = occ = idx = 0
    occupancy = {}
    for m, bank in sorted(banks.items()):
        lay = layouts[m]
        b = bank.array_bytes()
        n_active = bank.occupancy()
        a = b["keys"] + b["values"] + b["meta"] + measured_overhead(bank)
        o = lay.occupied_bytes(n_active)
        per_bank[m] = {"allocated": a, "occupied": o, "capacity": lay.capacity, "active": n_active,
                       "ceiling": lay.ceiling_bytes, "key_dim": lay.key_dim, "value_dim": lay.value_dim,
                       "overhead": measured_overhead(bank), "within_ceiling": a <= lay.ceiling_bytes}
        alloc += a
        occ += o
        idx += measured_overhead(bank)
        occupancy[m] = n_active / lay.capacity if lay.capacity else 0.0
    dk = next(iter(layouts.values())).key_dim
    d = next(iter(layouts.values())).value_dim
    return MemoryReport(allocated_bytes=alloc, occupied_bytes=occ, per_bank=per_bank, index_bytes=idx,
                        key_dim=dk, value_dim=d, occupancy=occupancy, ceiling_bytes=ceiling)
