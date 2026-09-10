"""DATA-03: fixture invariants — masks route private latents only through their path, shared
latents through the shared path; allowed subspaces partition the output coordinates; the Base
contract holds (forward_from == forward, adjoint matches finite differences); manifest is
deterministic."""

import json

import numpy as np

from pccap.bases.gpt2_jax import BANK_BLOCK
from pccap.contracts import SiteId, Write
from pccap.fixtures import modular_control as mc


def test_private_latents_affect_only_their_output_block():
    base = mc.ModularControlBase(seed=0)
    i = 3
    u = base.latents[i].copy()
    fr0 = base.forward(np.int32([i]), phase="query")
    for m in (1, 2, 3):
        base.latents[i] = u
        base.latents[i, mc.BLK[f"P{m}"]] += 1.0  # perturb bank m's private latent
        fr = base.forward(np.int32([i]), phase="query")
        dl = np.abs(np.asarray(fr.logits[0]) - np.asarray(fr0.logits[0]))
        changed = {c for c in range(mc.V) if dl[c] > 1e-7}
        allowed = set(mc.CLASS_GROUPS[f"O{m}"]) | {16 + m - 1}
        assert changed <= allowed and changed, (m, changed)
    base.latents[i] = u


def test_shared_latents_affect_only_shared_and_mixed_classes():
    base = mc.ModularControlBase(seed=0)
    i = 5
    u = base.latents[i].copy()
    fr0 = base.forward(np.int32([i]), phase="query")
    base.latents[i, mc.BLK["S"]] += 1.0
    fr = base.forward(np.int32([i]), phase="query")
    dl = np.abs(np.asarray(fr.logits[0]) - np.asarray(fr0.logits[0]))
    changed = {c for c in range(mc.V) if dl[c] > 1e-7}
    assert changed <= set(mc.CLASS_GROUPS["OS"]) | set(mc.CLASS_GROUPS["MIX"]) and changed
    base.latents[i] = u
    none = mc.ModularControlBase(seed=0, sharing="none")
    f0 = none.forward(np.int32([i]), phase="query").logits[0].copy()
    none.latents[i, mc.BLK["S"]] += 1.0
    assert np.array_equal(none.forward(np.int32([i]), phase="query").logits[0], f0)


def test_allowed_subspaces_partition_outputs():
    base = mc.ModularControlBase(seed=0)
    cols = {m: set(np.flatnonzero(base.allowed_subspace(m).sum(1))) for m in (1, 2, 3)}
    assert cols[3].isdisjoint(cols[1]) and cols[3].isdisjoint(cols[2])
    assert cols[1] & cols[2] == set(range(mc.BLK_OS.start, mc.BLK_OS.stop))  # only the shared path is shared
    # a permitted write at bank 3 cannot change classes of groups O1/O2/OS
    i = 7
    fr0 = base.forward(np.int32([i]), phase="query")
    v = base.allowed_subspace(3) @ np.ones(4, np.float32)
    fr = base.forward(np.int32([i]), [Write(SiteId(3, BANK_BLOCK[3], 0), v)], phase="query")
    dl = np.abs(np.asarray(fr.logits[0]) - np.asarray(fr0.logits[0]))
    assert {c for c in range(mc.V) if dl[c] > 1e-7} <= set(mc.CLASS_GROUPS["O3"]) | {18}


def test_base_contract_forward_from_and_adjoint():
    base = mc.ModularControlBase(seed=2)
    ids = np.int32([11])
    rng = np.random.default_rng(0)
    writes = [Write(SiteId(m, BANK_BLOCK[m], 0), rng.standard_normal(mc.D).astype(np.float32)) for m in (1, 2, 3)]
    full = base.forward(ids, writes, retain_sites=True)
    for m in (1, 2, 3):
        part = base.forward_from(m, full.hidden[m], ids, writes)
        assert np.allclose(part.logits, full.logits, atol=1e-5)
    grads, L, _ = base.adjoint(ids, 4, writes, return_loss=True)
    for m in (1, 2, 3):
        site = SiteId(m, BANK_BLOCK[m], 0)
        g = np.asarray(grads[site], np.float64)
        d = g / np.linalg.norm(g)
        eps = 1e-3
        w = {w_.site.bank: np.asarray(w_.vector, np.float64) for w_ in writes}
        wp = [Write(SiteId(k, BANK_BLOCK[k], 0), (w[k] + (eps * d if k == m else 0)).astype(np.float32)) for k in (1, 2, 3)]
        wm = [Write(SiteId(k, BANK_BLOCK[k], 0), (w[k] - (eps * d if k == m else 0)).astype(np.float32)) for k in (1, 2, 3)]

        def ce(ws):
            row = np.asarray(base.forward(ids, ws, phase="query").logits[0], np.float64)
            return np.log(np.exp(row - row.max()).sum()) + row.max() - row[4]

        fd = (ce(wp) - ce(wm)) / (2 * eps)
        assert abs(fd - np.dot(g, d)) < 1e-2 * max(1.0, abs(np.dot(g, d)))


def test_items_and_manifest_deterministic(tmp_path):
    base = mc.ModularControlBase(seed=0)
    items = base.make_items(n_private=30, n_shared=30, n_mixed=30, n_heldout=12)
    kinds = {k: sum(i.kind == k for i in items) for k in ("private", "shared", "mixed")}
    assert kinds == {"private": 30, "shared": 30, "mixed": 42} and sum(i.held_out for i in items) == 12
    for it in items:
        if it.kind == "private":
            assert it.r_star == (it.bank,) and it.target in mc.CLASS_GROUPS[f"O{it.bank}"]
        if it.kind == "shared":
            assert it.r_star == (1, 2) and it.target in mc.CLASS_GROUPS["OS"]
    wrong = mc.ModularControlBase(seed=0).make_items(n_private=6, n_shared=0, n_mixed=0, n_heldout=0, wrong_router=True)
    assert all(w.permitted != w.r_star for w in wrong)
    mc.write_manifest(tmp_path / "m.json", base, items)
    a = (tmp_path / "m.json").read_text()
    mc.write_manifest(tmp_path / "m2.json", mc.ModularControlBase(seed=0), mc.ModularControlBase(seed=0).make_items(30, 30, 30, 12))
    assert a == (tmp_path / "m2.json").read_text()
    assert json.loads(a)["checksum"] == base.checksum()
