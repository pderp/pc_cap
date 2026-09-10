"""GRAM-02 model/base controls on CPU (plan §6.5; R2-09 interface): the grammar base satisfies the Base
contract at d = 128 with sites at blocks 1/3/5, and the real cap runs on it."""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from pccap.cap.learn import update_item
from pccap.cap.memory import b_cap
from pccap.contracts import Budget, EditItem, SiteId, Write
from pccap.fixtures.grammar_generator import Grammar, Switches
from pccap.fixtures.grammar_model import BANK_BLOCKS, GrammarBase
from pccap.harness.arms import make_learner
from pccap.harness.ledger import Ledger
from pccap.routers import Full
from pccap.transport.transport import Transport


@pytest.fixture(scope="module")
def base():
    from pccap.fixtures.grammar_model import WEIGHTS

    if WEIGHTS.exists():  # the trained replacement base (GRAM-02); random init otherwise
        return GrammarBase(weights=WEIGHTS, ledger=Ledger())
    return GrammarBase(seed=1, ledger=Ledger())


@pytest.fixture(scope="module")
def item():
    toks, p, label = Grammar().sequence(2, Switches.task(2), 42, "private")
    return EditItem(item_id="g2-42", digest=hashlib.sha256(b"g2-42").digest()[:16], prompt="", answer="", aliases=[], paraphrases=[], locality_prompts=[],
                    prompt_ids=np.asarray(toks[:p], np.int32), answer_ids=np.asarray([toks[p]], np.int32), dataset="grammar", strata=label)


def test_sites_and_forward_from(base, item):
    ids = item.prompt_ids
    p = len(ids) - 1
    fr = base.forward(ids, retain_sites=True)
    assert set(fr.sites) == {SiteId(m, BANK_BLOCKS[m], p) for m in (1, 2, 3)} and fr.logits.shape == (len(ids), 64)
    rng = np.random.default_rng(0)
    w = Write(SiteId(1, 1, p), (0.3 * rng.standard_normal(128)).astype(np.float32))  # a random direction (a constant vector is removed by the final layer norm)
    full = base.forward(ids, [w], retain_sites=True)
    resumed = base.forward_from(1, fr.hidden[1], ids, [w])
    np.testing.assert_allclose(np.asarray(full.logits), np.asarray(resumed.logits), rtol=1e-4, atol=1e-4)
    # a write at bank 1 changes sites 2 and 3 and the logits; a write at bank 3 changes only logits
    assert not np.allclose(np.asarray(full.sites[SiteId(2, 3, p)]), np.asarray(fr.sites[SiteId(2, 3, p)]))
    w3 = Write(SiteId(3, 5, p), (0.3 * rng.standard_normal(128)).astype(np.float32))
    f3 = base.forward(ids, [w3])
    np.testing.assert_allclose(np.asarray(f3.sites[SiteId(2, 3, p)]), np.asarray(fr.sites[SiteId(2, 3, p)]))
    assert np.max(np.abs(np.asarray(f3.logits[p]) - np.asarray(fr.logits[p]))) > 1e-3


def test_adjoint_shapes_and_descent(base, item):
    ids, tgt = item.prompt_ids, int(item.answer_ids[0])
    grads, loss, _ = base.adjoint(ids, tgt, return_loss=True)
    assert {s.bank for s in grads} == {1, 2, 3} and all(np.asarray(v).shape == (128,) for v in grads.values())
    p = len(ids) - 1
    gvec = np.asarray(grads[SiteId(3, 5, p)])
    step = -0.05 * gvec / (np.linalg.norm(gvec) + 1e-12)
    l1, _ = base.loss(ids, tgt, [Write(SiteId(3, 5, p), step.astype(np.float32))])
    assert l1 < loss


def test_cap_runs_on_grammar_base(base, item):
    cap = make_learner("C1", base, base.ledger, radii={1: 0.5, 2: 0.5, 3: 0.5}, bank_scales={1: 1.0, 2: 1.0, 3: 1.0}, seed=0)
    assert cap.d == 128 and cap.blocks == BANK_BLOCKS
    assert cap.memory_bytes().ceiling_bytes == b_cap(128)
    before = base.checksum()
    out = update_item(cap, item, Full(), Budget(A=0.3, R=8), Transport())
    assert base.checksum() == before
    assert out.code in ("accepted", "acquisition_failure")  # acquisition depends on the base's competence; the mechanics are what is tested
    po = out.prefix_outcomes[0]
    l0, l1 = (po["loss_start"], po["loss_end"]) if isinstance(po, dict) else (po.loss_start, po.loss_end)
    assert l1 < l0
    assert cap.memory_bytes().occupied_bytes > 0


def test_batched_kernels_match_single(base, item):
    ids = item.prompt_ids
    seqs = [ids, ids[:10], ids[:33]]
    lg = base.last_logits_batch(seqs)
    for k, s in enumerate(seqs):
        np.testing.assert_allclose(lg[k], np.asarray(base.forward(s).logits[len(s) - 1]), rtol=1e-4, atol=1e-4)
    logits, rows, full, n = base.forward_batch(seqs)
    np.testing.assert_allclose(np.asarray(logits)[0], np.asarray(base.forward(ids).logits[len(ids) - 1]), rtol=1e-4, atol=1e-4)
