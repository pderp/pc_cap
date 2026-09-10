"""GRAM-01 verification (plan §6.5): private switches change only their context; shared switches change the
designated mechanism in every context; the context is always observable; the five orders are balanced;
regeneration is byte-identical; the target at p* is a deterministic function of the prefix."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from pccap.fixtures.grammar_generator import (
    CONTEXT_POSITIONS,
    CONTEXT_TOKENS,
    CONTEXTS,
    KINDS,
    LENGTH,
    VOCAB,
    Grammar,
    Switches,
    balanced_orders,
    sample_hash,
    write_generator_manifest,
)

ROOT = Path(__file__).resolve().parents[2]


def _seqs(g, context, sw, seeds, kind=None):
    return [g.sequence(context, sw, s, kind)[0] for s in seeds]


def test_private_switch_changes_only_its_context():
    g = Grammar()
    seeds = range(100)
    for c in range(CONTEXTS):
        flipped = Switches.heldout(c, "private_only")
        for c2 in range(CONTEXTS):
            base = _seqs(g, c2, Switches.base(), seeds, "private")
            alt = _seqs(g, c2, flipped, seeds, "private")
            changed = sum(not np.array_equal(a, b) for a, b in zip(base, alt))
            if c2 == c:
                assert changed > 80, (c, changed)  # the flip matters only when the private rule fires at a differing entry
            else:
                assert changed == 0, (c, c2, changed)


def test_shared_switches_change_their_mechanism_in_every_context():
    g = Grammar()
    seeds = range(60)
    for c in range(CONTEXTS):
        for attr in ("shared_1", "shared_2"):
            sw = Switches(shared_1=1 if attr == "shared_1" else 0, shared_2=1 if attr == "shared_2" else 0)
            base = _seqs(g, c, Switches.base(), seeds, attr)
            alt = _seqs(g, c, sw, seeds, attr)
            assert sum(not np.array_equal(a, b) for a, b in zip(base, alt)) > 50, (c, attr)


def test_context_observable_and_vocab():
    g = Grammar()
    for c in range(CONTEXTS):
        toks, p, label = g.sequence(c, Switches.task(c), 11)
        assert all(toks[t] == CONTEXT_TOKENS[c] for t in CONTEXT_POSITIONS)
        assert toks.min() >= 2 and toks.max() < VOCAB and len(toks) == LENGTH
        assert 48 <= p <= 63 and label["context"] == c and label["kind"] in KINDS


def test_target_is_a_deterministic_function_of_the_prefix():
    g = Grammar()
    for c in range(CONTEXTS):
        for sw in (Switches.base(), Switches.task(c)):
            for s in range(30):
                toks, p, label = g.sequence(c, sw, 700 + s)
                tgt, kind = g.rule_target(toks[:p], c, sw)
                assert tgt == toks[p] and kind == label["kind"], (c, s, tgt, toks[p], kind, label)


def test_orders_balanced():
    for r in range(3):
        orders = balanced_orders(r)
        assert len(orders) == 5 and all(sorted(o) == list(range(CONTEXTS)) for o in orders)
        for task in range(CONTEXTS):
            assert any(o.index(task) in (0, 1) for o in orders), (r, task)
            assert any(o.index(task) in (6, 7) for o in orders), (r, task)


def test_regeneration_is_byte_identical(tmp_path):
    man = write_generator_manifest(tmp_path / "generator.json")
    g2 = Grammar(man["grammar"]["rule_seed"])
    assert np.array_equal(np.asarray(man["grammar"]["perm_p"]), g2.perm_p)
    assert sample_hash(g2) == man["sample_sha256_1000"]
    committed = ROOT / "manifests" / "grammar" / "generator.json"
    if committed.exists():
        assert json.loads(committed.read_text())["sample_sha256_1000"] == man["sample_sha256_1000"]
