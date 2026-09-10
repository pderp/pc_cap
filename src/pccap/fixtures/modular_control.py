"""MODULAR-CONTROL fixture (DATA-03; PDF E.1, D.10, PC-1).

A small residual computation graph with three explicit module groups at the three write
depths, satisfying the ``Base`` contract so the unchanged cap runs on it.

Latent layout (width ``d = 32``): each input item is a latent vector ``u`` with blocks
``P1, P2, P3`` (private latents, 4 dims each, read only by module 1, 2, 3 respectively), ``S``
(shared latents, 4 dims, read by modules 1 and 2 through the explicit shared path) and ``C``
(context/nuisance dims). The residual stream has the same width; module ``m`` writes into its
own output block ``O_m`` (4 dims) from ``P_m`` and, for modules 1 and 2, into the shared block
``O_S`` (4 dims) from ``S``; nothing else touches those coordinates.

Sites: bank ``m`` = the residual after module ``m``. The **allowed write subspace** of bank ``m``
is ``O_m`` (plus ``O_S`` for banks 1 and 2, when sharing is enabled) — a permitted write at one
site can change only its own output coordinates. Output logits over ``V = 20`` classes read
disjoint coordinate groups: classes 0–3 ← ``O_1``, 4–7 ← ``O_2``, 8–11 ← ``O_3``, 12–15 ← ``O_S``,
16–19 ← ``O_m`` + ``O_S`` (mixed, bank m ∈ {1, 2, 3} with 19 spare).

Items (``ItemSpec``): ``kind ∈ {private, shared, mixed}``, ``bank`` (private/mixed) and the
planted target class. ``R*(item)`` = banks whose allowed subspace can produce the target:
private → {m}; shared → {1, 2} (both feed ``O_S``); mixed(bank m) → {m} ∪ {1, 2} required
jointly for m = 3 (coverage), {m} for m ∈ {1, 2}. Variants: ``sharing="useful"`` (default),
``"none"`` (modules do not write ``O_S`` and bank subspaces exclude it: shared items must be
fixed one at a time), ``"wrong_router"`` (the supplied permissions point at the wrong bank).
Everything is deterministic from the seed and recorded by ``manifest()``.

The planted targets are attainable by construction: a write ``v`` in ``O_target`` raises the
target class logit linearly (readout is linear in the residual), so the oracle CO arm reaches
them; unrelated items keep their exact outputs because the gate does not fire on them.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases.gpt2_jax import BANK_BLOCK
from pccap.contracts import EditItem, ForwardResult, SiteId
from pccap.harness.ledger import Ledger
from pccap.transport.transport import Transport

D = 32
V = 20
BLK = {"P1": slice(0, 4), "P2": slice(4, 8), "P3": slice(8, 12), "S": slice(12, 16), "C": slice(16, 20),
       "O1": slice(20, 24), "O2": slice(24, 28), "O3": slice(28, 32)}
# the shared output block reuses the context slice of the residual (inputs never write there)
BLK_OS = slice(16, 20)
CLASS_GROUPS = {"O1": range(0, 4), "O2": range(4, 8), "O3": range(8, 12), "OS": range(12, 16), "MIX": range(16, 20)}


@dataclass
class ItemSpec:
    item_id: str
    index: int  # row in the latent table
    kind: str  # private | shared | mixed
    bank: int  # owning bank for private/mixed; 0 for shared
    target: int  # planted target class
    r_star: tuple[int, ...]  # banks with supplied permission and causal support
    permitted: tuple[int, ...]  # what CO receives (== r_star unless wrong_router)
    held_out: bool = False


class ModularControlBase:
    """Fixture base implementing the Base contract (d = 32, three module groups)."""

    name = "MODULAR"

    def __init__(self, seed: int = 0, sharing: str = "useful", n_items: int = 400, ledger: Ledger | None = None):
        assert sharing in ("useful", "none")
        self.sharing = sharing
        rng = np.random.default_rng(seed)
        self.D, self.d, self.vocab = 3, D, V
        self.seed = seed
        # module maps: private block -> own output block; shared block -> shared output block
        self.W = {m: (rng.standard_normal((4, 4)) / 2).astype(np.float32) for m in (1, 2, 3)}
        self.Ws = {m: (rng.standard_normal((4, 4)) / 2).astype(np.float32) for m in (1, 2)}
        # readout: disjoint coordinate groups per class group
        R = np.zeros((D, V), np.float32)
        for grp, cls in (("O1", CLASS_GROUPS["O1"]), ("O2", CLASS_GROUPS["O2"]), ("O3", CLASS_GROUPS["O3"])):
            R[BLK[grp], list(cls)] = rng.standard_normal((4, 4)).astype(np.float32)
        R[BLK_OS, list(CLASS_GROUPS["OS"])] = rng.standard_normal((4, 4)).astype(np.float32)
        for k, m in enumerate((1, 2, 3)):  # mixed classes read O_m + O_S
            R[BLK[f"O{m}"], 16 + k] = rng.standard_normal(4).astype(np.float32)
            R[BLK_OS, 16 + k] = rng.standard_normal(4).astype(np.float32)
        self.R = R
        self.latents = rng.standard_normal((n_items, D)).astype(np.float32)
        self.latents[:, 16:] = 0.0  # inputs never carry output coordinates
        self.sites = [SiteId(m, BANK_BLOCK[m], -1) for m in (1, 2, 3)]
        self.ledger = ledger or Ledger()
        self._grad = jax.jit(jax.grad(self._loss_w))

    # --------------------------------------------------------------- allowed subspaces
    def allowed_subspace(self, bank: int) -> np.ndarray:
        cols = list(range(BLK[f"O{bank}"].start, BLK[f"O{bank}"].stop))
        if self.sharing == "useful" and bank in (1, 2):
            cols += list(range(BLK_OS.start, BLK_OS.stop))
        Q = np.zeros((D, len(cols)), np.float32)
        for j, c in enumerate(cols):
            Q[c, j] = 1.0
        return Q

    def transport(self) -> "ProjectedTransport":
        return ProjectedTransport({m: self.allowed_subspace(m) for m in (1, 2, 3)})

    # --------------------------------------------------------------- forward math
    def _module(self, m: int, h):
        out = jnp.zeros_like(h)
        priv = jnp.tanh(h[..., BLK[f"P{m}"]] @ self.W[m])
        out = out.at[..., BLK[f"O{m}"]].set(priv)
        if self.sharing == "useful" and m in (1, 2):
            sh = jnp.tanh(h[..., BLK["S"]] @ self.Ws[m])
            out = out.at[..., BLK_OS].add(sh)
        return h + out

    def _stages(self, H0: np.ndarray, p: int, Wr: np.ndarray, start: int = 1):
        h = jnp.asarray(H0)
        rows, full = {}, {}
        for m in (1, 2, 3):
            if m < start:
                continue
            if m > start or start == 1:
                h = self._module(m, h)
            rows[m] = np.asarray(h[p])
            full[m] = np.asarray(h)
            h = h.at[p].add(jnp.asarray(Wr[m - 1]))
        logits = np.asarray(h @ jnp.asarray(self.R))
        return logits.astype(np.float32), rows, full

    def _W(self, ids, writes):
        ids = np.asarray(ids, np.int32).reshape(-1)
        p = len(ids) - 1
        Wr = np.zeros((3, D), np.float32)
        for w in writes:
            Wr[w.site.bank - 1] += np.asarray(w.vector, np.float32)
        return ids, p, Wr

    def forward(self, ids, writes=(), retain_sites=False, phase="learning", last_only=False) -> ForwardResult:
        ids, p, Wr = self._W(ids, writes)
        with self.ledger.call(phase, full_forwards=1, tokens=len(ids)) as rec:
            logits, rows, full = self._stages(self.latents[ids], p, Wr, 1)
        return ForwardResult(logits=logits[p] if last_only else logits, sites={SiteId(m, BANK_BLOCK[m], p): rows[m] for m in rows}, cost=rec,
                             hidden=full if retain_sites else {})

    def forward_from(self, bank, hidden, ids, writes=(), phase="learning", retain_sites=False, last_only=False) -> ForwardResult:
        ids, p, Wr = self._W(ids, writes)
        with self.ledger.call(phase, partial_forwards=1, tokens=len(ids)) as rec:
            h = jnp.asarray(hidden).at[p].add(jnp.asarray(Wr[bank - 1]))
            rows, full = {bank: np.asarray(hidden)[p]}, {bank: np.asarray(hidden)}
            for m in range(bank + 1, 4):
                h = self._module(m, h)
                rows[m], full[m] = np.asarray(h[p]), np.asarray(h)
                h = h.at[p].add(jnp.asarray(Wr[m - 1]))
            logits = np.asarray(h @ jnp.asarray(self.R)).astype(np.float32)
        return ForwardResult(logits=logits[p] if last_only else logits, sites={SiteId(m, BANK_BLOCK[m], p): rows[m] for m in rows}, cost=rec,
                             hidden=full if retain_sites else {})

    def _loss_w(self, Wr, H0, p, target):
        h = H0
        for m in (1, 2, 3):
            h = self._module(m, h)
            h = h.at[p].add(Wr[m - 1])
        row = (h @ jnp.asarray(self.R))[p]
        return jax.nn.logsumexp(row) - row[target]

    def adjoint(self, ids, target, writes=(), phase="learning", return_loss=False):
        ids, p, Wr = self._W(ids, writes)
        with self.ledger.call(phase, full_forwards=1, reverses=1, tokens=len(ids)):
            g = np.asarray(self._grad(jnp.asarray(Wr), jnp.asarray(self.latents[ids]), p, int(target)))
        out = {SiteId(m, BANK_BLOCK[m], p): g[m - 1] for m in (1, 2, 3)}
        if return_loss:
            return out, float(self._loss_w(jnp.asarray(Wr), jnp.asarray(self.latents[ids]), p, int(target))), None
        return out

    def checksum(self, recompute=True) -> str:
        h = hashlib.sha256()
        for a in (self.R, self.latents, *[self.W[m] for m in (1, 2, 3)], *[self.Ws[m] for m in (1, 2)]):
            h.update(np.ascontiguousarray(a).tobytes())
        h.update(self.sharing.encode())
        return h.hexdigest()

    # --------------------------------------------------------------- items
    def base_prediction(self, index: int) -> int:
        return int(np.argmax(self.forward(np.int32([index]), phase="query").logits[0]))

    def make_items(self, n_private: int = 120, n_shared: int = 120, n_mixed: int = 120, n_heldout: int = 60,
                   wrong_router: bool = False, seed: int = 1, start_index: int = 0) -> list[ItemSpec]:
        rng = np.random.default_rng(seed)
        items: list[ItemSpec] = []
        idx = start_index

        def target_for(kind: str, bank: int, index: int) -> int:
            base_cls = self.base_prediction(index)
            if kind == "private":
                cls = [c for c in CLASS_GROUPS[f"O{bank}"] if c != base_cls]
            elif kind == "shared":
                cls = [c for c in CLASS_GROUPS["OS"] if c != base_cls]
            else:
                cls = [16 + bank - 1]
            return int(rng.choice(cls))

        def rstar(kind: str, bank: int) -> tuple[int, ...]:
            if kind == "private":
                return (bank,)
            if kind == "shared":
                return (1, 2) if self.sharing == "useful" else ()
            return (bank,) if bank in (1, 2) else ((3, 1) if self.sharing == "useful" else (3,))

        def wrong(r: tuple[int, ...]) -> tuple[int, ...]:
            return tuple(((b % 3) + 1) for b in r) if r else (1,)

        for kind, n in (("private", n_private), ("shared", n_shared), ("mixed", n_mixed)):
            for i in range(n):
                bank = (i % 3) + 1 if kind != "shared" else 0
                r = rstar(kind, bank)
                items.append(ItemSpec(f"mc-{kind}-{i}", idx, kind, bank, target_for(kind, bank, idx), r, wrong(r) if wrong_router else r))
                idx += 1
        for i in range(n_heldout):  # held-out combinations: private + shared changes on the same item
            bank = (i % 3) + 1
            items.append(ItemSpec(f"mc-heldout-{i}", idx, "mixed", bank, 16 + bank - 1, rstar("mixed", bank), rstar("mixed", bank), held_out=True))
            idx += 1
        return items

    def edit_item(self, spec: ItemSpec) -> EditItem:
        return EditItem(item_id=spec.item_id, digest=hashlib.sha256(spec.item_id.encode()).digest()[:16], prompt=spec.item_id,
                        answer=str(spec.target), aliases=[str(spec.target)], paraphrases=[], locality_prompts=[],
                        prompt_ids=np.int32([spec.index]), answer_ids=np.int32([spec.target]), dataset="modular_control",
                        fact_id=spec.item_id, strata={"kind": spec.kind, "bank": spec.bank, "held_out": spec.held_out})

    def manifest(self, items: list[ItemSpec]) -> dict:
        return {"fixture": "MODULAR-CONTROL", "seed": self.seed, "sharing": self.sharing, "d": D, "classes": V,
                "blocks": {k: [v.start, v.stop] for k, v in BLK.items()} | {"OS": [BLK_OS.start, BLK_OS.stop]},
                "sites": {m: f"residual after module {m} (bank {m})" for m in (1, 2, 3)},
                "allowed_subspace_columns": {m: np.flatnonzero(self.allowed_subspace(m).sum(1)).tolist() for m in (1, 2, 3)},
                "class_groups": {k: list(v) for k, v in CLASS_GROUPS.items()}, "checksum": self.checksum(),
                "items": [it.__dict__ for it in items]}


class ProjectedTransport(Transport):
    """Transport that projects every direction onto the bank's allowed subspace before normalizing
    (PDF E.1: applied to every arm on this fixture)."""

    def __init__(self, subspaces: dict[int, np.ndarray], sign: float = -1.0):
        super().__init__(sign)
        self.subspaces = subspaces

    def direction(self, signal, site: SiteId, allowed_subspace=None):
        return super().direction(signal, site, allowed_subspace=self.subspaces.get(site.bank))


@dataclass
class FixtureRun:
    acquired: int = 0
    total: int = 0
    rows: list = field(default_factory=list)


def learn_and_score(base: ModularControlBase, items: list[ItemSpec], arm: str, A: float = 1.0, radius: float = 0.0,
                    R: int = 5, seed: int = 0, unrelated: list[ItemSpec] | None = None) -> dict:
    """Run one cap arm over the items and score planted-target recovery (argmax == target after
    learning) and unrelated-output invariance (max |Δp| over unrelated items)."""
    from pccap.cap.cap import Cap, CapConfig
    from pccap.cap.learn import update_item
    from pccap.contracts import Budget
    from pccap.routers import make_router

    # residual scales: median site norms over the items (cap-disabled)
    norms = {m: [] for m in (1, 2, 3)}
    for it in items[:50]:
        fr = base.forward(np.int32([it.index]), phase="query")
        for m in (1, 2, 3):
            norms[m].append(float(np.linalg.norm(fr.sites[SiteId(m, BANK_BLOCK[m], 0)])))
    b_m = {m: max(1e-8, float(np.median(norms[m]))) for m in (1, 2, 3)}
    cap = Cap(base, CapConfig(arm=arm, radii={1: radius, 2: radius, 3: radius}, bank_scales=b_m, seed=seed, d=D), base.ledger)
    router = make_router(arm)
    budget = Budget(A=A, R=R, tau_edit=0.1)
    tr = base.transport()
    unrelated = unrelated or []
    p_before = [np.asarray(jax.nn.softmax(jnp.asarray(cap.predict(np.int32([u.index])).logits))) for u in unrelated]
    rows = []
    for spec in items:
        it = base.edit_item(spec)
        out = update_item(cap, it, router, budget, tr, seed=seed, permitted_banks=spec.permitted if arm == "CO" else None)
        pred = int(np.argmax(cap.predict(np.int32([spec.index])).logits))
        rows.append({"item_id": spec.item_id, "kind": spec.kind, "bank": spec.bank, "target": spec.target, "pred": pred,
                     "recovered": pred == spec.target, "threshold": out.acquired_threshold_all_prefixes, "rounds": out.rounds_used,
                     "routes": [c for po in out.prefix_outcomes for c in po["codes"] if c.startswith("accepted")]})
    p_after = [np.asarray(jax.nn.softmax(jnp.asarray(cap.predict(np.int32([u.index])).logits))) for u in unrelated]
    max_dp = max((float(np.abs(a - b).max()) for a, b in zip(p_before, p_after)), default=0.0)
    return {"arm": arm, "recovered": sum(r["recovered"] for r in rows), "total": len(rows),
            "recovery_rate": sum(r["recovered"] for r in rows) / len(rows), "unrelated_max_abs_dp": max_dp,
            "b_m": b_m, "rows": rows, "memory": cap.memory_bytes().__dict__}


def write_manifest(path, base: ModularControlBase, items: list[ItemSpec]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(base.manifest(items), indent=1))
