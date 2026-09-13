"""v0-stable control (DEC-035; R1-14): the v0 cap with keys computed from the unedited residual at every site.

v0's ``Cap.edited_forward`` reads bank m's key from the residual *after* upstream banks' writes at the same position, so
keys and queries move with whatever was written earlier at sites 1..m-1 (Stage 0 memo §3.2). ``StableCap`` keeps the
sequential value writes and everything else (learning path, budgets, calibration, snapshots) and changes exactly one
thing: every key — at write time and at read time — comes from the first, write-free pass. The learning path inherits
this because it takes write keys from ``edited_forward(...).keys`` (``pccap.cap.learn``).
"""

from __future__ import annotations

import numpy as np

from pccap.cap.cap import Cap, EditedPass
from pccap.contracts import CostRecord, SiteId


class StableCap(Cap):
    stable_keys = True

    def edited_forward(self, ids, extra: dict[int, np.ndarray] | None = None, phase: str = "learning",
                       frozen_retrieval: dict[int, int] | None = None, full: bool = False) -> EditedPass:
        ids = np.asarray(ids, np.int32).reshape(-1)
        n = len(ids)
        p = n - 1
        extra = extra or {}
        cost = CostRecord(phase=phase)
        fr = self.base.forward(ids, (), retain_sites=True, phase=phase, last_only=not full)
        cost.add(fr.cost)
        # stable observation: keys for every site from the write-free pass
        keys = {m: self.key(np.asarray(fr.sites[SiteId(m, self.blocks[m], p)], np.float32)) for m in self.cfg.banks()}
        writes: dict[int, np.ndarray] = {}
        sites: dict[int, np.ndarray] = {}
        hidden: dict[int, np.ndarray] = {}
        fired: dict[int, int] = {}
        for m in self.cfg.banks():
            sid = SiteId(m, self.blocks[m], p)
            sites[m] = np.asarray(fr.sites[sid], np.float32)  # residual actually entering the site (with upstream writes)
            hidden[m] = fr.hidden[m]
            q = keys[m]
            bank = self.banks[m].bank
            if frozen_retrieval is not None and m in frozen_retrieval:
                slot = frozen_retrieval[m]
                value = bank.values[slot].copy() if slot >= 0 else np.zeros(self.d, np.float32)
            else:
                value, r = bank.value_for(q)
                slot = r.slot
            fired[m] = int(slot)
            v = np.asarray(value + extra.get(m, 0.0), np.float32)
            writes[m] = v
            if np.any(v):
                fr = self.base.forward_from(m, hidden[m], ids, self._writes_list(p, writes), phase=phase, retain_sites=True,
                                            last_only=not full)
                cost.add(fr.cost)
        return EditedPass(logits=np.asarray(fr.logits), keys=keys, sites=sites, hidden=hidden, fired=fired,
                          writes=writes, cost=cost, n=n, p=p)

    def edited_forward_batch(self, seqs: list[np.ndarray], phase: str = "query") -> tuple[np.ndarray, list[dict[int, int]]]:
        B = len(seqs)
        logits, rows, full, n = self.base.forward_batch(seqs, None, phase=phase)
        rows = np.array(rows)  # [B, 3, d] write-free residuals at the three sites
        stable_keys = [[self.key(rows[b, m - 1]) for m in (1, 2, 3)] for b in range(B)]
        W = np.zeros((B, 3, self.d), np.float32)
        fired = [dict() for _ in range(B)]
        cur_full = full
        for m in self.cfg.banks():
            bank = self.banks[m].bank
            hit = []
            for b in range(B):
                value, r = bank.value_for(stable_keys[b][m - 1])
                fired[b][m] = int(r.slot)
                if r.slot >= 0:
                    W[b, m - 1] = value
                    hit.append(b)
            if hit:
                logits, later_rows, later_full = self.base.forward_from_batch(m, cur_full[:, m - 1], n, W, phase=phase)
                if later_full.shape[1]:
                    cur_full = cur_full.at[:, m:].set(later_full)
        return np.asarray(logits), fired
