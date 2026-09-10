"""GRAM-01: the LATENT-GRAMMAR generator (PDF E.1; plan §6.5 GRAM-01). Pure NumPy, seeded, manifest-driven.

Replacement fixture — no continuity with the missing R8/R9 grammar (PA-2).

**Vocabulary (64).** 0 = PAD, 1 = BOS (reserved, never emitted), 2–9 = the eight context tokens
``c0..c7``, 10–63 = 54 content tokens in six classes of nine (class k = tokens ``10+9k .. 18+9k``).

**Sequences (length 64).** The context token sits at position 0 and is re-emitted at 16, 32, 48 — the
context is always observable. Every other position holds a content token produced by a deterministic
class chain plus three *mechanisms* that fix the exact next token from the prefix:

* the class of the next token follows the previous content token's class through a fixed cyclic table
  ``0→1→2→3→4→5→0`` (filler classes 4 and 5 draw a uniformly random member of the class);
* **shared switch 1** ("successor"): after a class-0 token the next token is class 1 and its identity is
  ``perm_S1[value]`` where ``perm_S1`` is one of two fixed permutations of the nine class-1 tokens,
  selected by the switch (default 0 / flipped 1). The same rule family applies in all contexts.
* **shared switch 2** ("copy"): after a class-2 token the next token is class 3 and is a copy of the
  content token ``lag`` content positions earlier (``lag`` = 6 default, 12 flipped) — because the class
  chain has period six, that token is the previous (lag 6) or the second-previous (lag 12) class-3
  token, so the class-3 tokens of a sequence read A, A, A, … under the default and A, B, A, B, … when
  flipped; the first one or two class-3 tokens (no antecedent) are drawn at random. Same rule in all
  contexts.
* **private switch** (one per context): after a class-3 token the next token is class 4 and its
  identity is ``perm_P[c][flip][prev_index]`` — a context-specific permutation family; flipping
  ``P_c`` changes only sequences of context ``c``.
* after class 1 the next token is class 2, drawn at random; after 4 → 5 and after 5 → 0 at random.

Because the chain cycles every six content positions, each mechanism fires about ten times per
sequence, including inside the evaluation window 48–63. The **designated evaluated position** ``p*``
is sampled (seeded) among positions in 48–63 where the requested mechanism fires; the supplied
causal label is ``(kind ∈ {private, shared_1, shared_2}, context)``. One sequence/target pair is one
learning item: prompt = tokens[:p*], target = tokens[p*] (a single token; no terminator).

**Switch settings.** Base grammar: all switches default. Task ``i`` (continual stream): context ``i``
with its private switch flipped and both shared switches at their non-default value (consistent
across the immutable stream). Held-out combinations: ``(private flipped, shared default)`` and
``(private default, shared flipped)`` per context, for evaluation only.

**Manifests** (`manifests/grammar/`): ``generator.json`` records the permutations, the class table,
the seeds and sample hashes so that regeneration is byte-identical; ``orders.json`` the five balanced
eight-task orders per realization (rotation by three of a realization-seeded base permutation: every
task appears at least once in positions {0, 1} and once in {6, 7} across the five orders).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

VOCAB = 64
PAD, BOS = 0, 1
CONTEXTS = 8
CONTEXT_TOKENS = list(range(2, 10))
CONTENT_BASE = 10
N_CLASSES = 6
CLASS_SIZE = 9
LENGTH = 64
CONTEXT_POSITIONS = (0, 16, 32, 48)
EVAL_WINDOW = (48, 63)
KINDS = ("private", "shared_1", "shared_2")
COPY_LAG = {0: 6, 1: 12}
ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIR = ROOT / "manifests" / "grammar"


def class_of(tok: int) -> int:
    return (tok - CONTENT_BASE) // CLASS_SIZE


def class_tokens(k: int) -> list[int]:
    return [CONTENT_BASE + CLASS_SIZE * k + j for j in range(CLASS_SIZE)]


@dataclass(frozen=True)
class Switches:
    private: tuple[int, ...] = (0,) * CONTEXTS  # one per context
    shared_1: int = 0
    shared_2: int = 0

    @staticmethod
    def base() -> "Switches":
        return Switches()

    @staticmethod
    def task(context: int) -> "Switches":
        p = [0] * CONTEXTS
        p[context] = 1
        return Switches(private=tuple(p), shared_1=1, shared_2=1)

    @staticmethod
    def heldout(context: int, which: str) -> "Switches":
        p = [0] * CONTEXTS
        if which == "private_only":
            p[context] = 1
            return Switches(private=tuple(p))
        if which == "shared_only":
            return Switches(private=tuple(p), shared_1=1, shared_2=1)
        raise ValueError(which)

    def to_dict(self) -> dict:
        return {"private": list(self.private), "shared_1": self.shared_1, "shared_2": self.shared_2}


@dataclass
class Grammar:
    """Fixed rule tables, derived from ``rule_seed`` (recorded in the manifest)."""

    rule_seed: int = 7
    perm_s1: np.ndarray = field(default=None)  # [2, 9] index permutations
    perm_p: np.ndarray = field(default=None)  # [8, 2, 9]

    def __post_init__(self):
        rng = np.random.default_rng(self.rule_seed)
        self.perm_s1 = np.stack([rng.permutation(CLASS_SIZE) for _ in range(2)])
        while np.array_equal(self.perm_s1[0], self.perm_s1[1]):
            self.perm_s1[1] = rng.permutation(CLASS_SIZE)
        pp = np.zeros((CONTEXTS, 2, CLASS_SIZE), np.int64)
        for c in range(CONTEXTS):
            pp[c, 0] = rng.permutation(CLASS_SIZE)
            pp[c, 1] = rng.permutation(CLASS_SIZE)
            while np.array_equal(pp[c, 0], pp[c, 1]):
                pp[c, 1] = rng.permutation(CLASS_SIZE)
        self.perm_p = pp

    def to_dict(self) -> dict:
        return {"rule_seed": self.rule_seed, "perm_s1": self.perm_s1.tolist(), "perm_p": self.perm_p.tolist(), "copy_lag": COPY_LAG,
                "class_table": "0->1 (shared_1), 1->2 (random), 2->3 (shared_2 copy), 3->4 (private), 4->5 (random), 5->0 (random)"}

    # ------------------------------------------------------------------ one sequence
    def sequence(self, context: int, sw: Switches, seed: int, kind: str | None = None,
                 latent_override: dict | None = None) -> tuple[np.ndarray, int, dict]:
        """Returns (tokens[64], p*, label). ``kind`` requests the mechanism firing at p*; None = seeded choice.
        ``latent_override={"class3": token}`` replaces the random draw that seeds the copy chain (the sequence's
        class-3 latent) while every other random draw stays identical — the counterfactual used by tracing
        (DATA-07): all rule-determined consequences of the latent change consistently."""
        rng = np.random.default_rng(seed)
        override3 = (latent_override or {}).get("class3")
        toks = np.zeros(LENGTH, np.int64)
        content_hist: list[int] = []  # content tokens in order
        fired: list[tuple[int, str]] = []  # (position, kind) where a deterministic rule produced the token
        prev = None
        start_class = int(rng.integers(N_CLASSES))
        for t in range(LENGTH):
            if t in CONTEXT_POSITIONS:
                toks[t] = CONTEXT_TOKENS[context]
                continue
            if prev is None:
                k = start_class
                draw = int(rng.integers(CLASS_SIZE))
                tok = class_tokens(k)[draw] if not (k == 3 and override3 is not None) else int(override3)
                kind_here = None
            else:
                pk = class_of(prev)
                k = (pk + 1) % N_CLASSES
                if pk == 0:  # shared_1: successor permutation on class 1
                    idx = self.perm_s1[sw.shared_1][prev - CONTENT_BASE]
                    tok = class_tokens(1)[int(idx)]
                    kind_here = "shared_1"
                elif pk == 2:  # shared_2: copy of the content token `lag` content positions earlier (a class-3 token)
                    lag = COPY_LAG[sw.shared_2]
                    i = len(content_hist)
                    if i >= lag and class_of(content_hist[i - lag]) == 3:
                        tok = content_hist[i - lag]
                        kind_here = "shared_2"
                    else:
                        draw = int(rng.integers(CLASS_SIZE))  # no antecedent yet: random, not a mechanism firing
                        tok = class_tokens(3)[draw] if override3 is None else int(override3)
                        kind_here = None
                elif pk == 3:  # private: context-specific permutation on class 4
                    idx = self.perm_p[context][sw.private[context]][prev - CONTENT_BASE - 3 * CLASS_SIZE]
                    tok = class_tokens(4)[int(idx)]
                    kind_here = "private"
                else:
                    tok = class_tokens(k)[int(rng.integers(CLASS_SIZE))]
                    kind_here = None
            toks[t] = tok
            content_hist.append(int(tok))
            prev = int(tok)
            if kind_here is not None:
                fired.append((t, kind_here))
        window = [(t, kd) for t, kd in fired if EVAL_WINDOW[0] <= t <= EVAL_WINDOW[1]]
        if kind is None:
            kind = KINDS[int(rng.integers(len(KINDS)))]
        choices = [t for t, kd in window if kd == kind]
        if not choices:
            raise RuntimeError(f"mechanism {kind} does not fire in the evaluation window (seed {seed})")
        p_star = int(choices[int(rng.integers(len(choices)))])
        return toks, p_star, {"kind": kind, "context": context}

    # ------------------------------------------------------------------ prefix → target (the learnable rule)
    def rule_target(self, prefix: np.ndarray, context: int, sw: Switches) -> tuple[int | None, str | None]:
        """The token the rules force at position ``len(prefix)`` given the prefix (None if random there)."""
        t = len(prefix)
        if t in CONTEXT_POSITIONS:
            return CONTEXT_TOKENS[context], "context"
        content = [int(x) for i, x in enumerate(prefix) if i not in CONTEXT_POSITIONS]
        if not content:
            return None, None
        prev = content[-1]
        pk = class_of(prev)
        if pk == 0:
            return class_tokens(1)[int(self.perm_s1[sw.shared_1][prev - CONTENT_BASE])], "shared_1"
        if pk == 2:
            lag = COPY_LAG[sw.shared_2]
            i = len(content)
            if i >= lag and class_of(content[i - lag]) == 3:
                return content[i - lag], "shared_2"
            return None, None
        if pk == 3:
            return class_tokens(4)[int(self.perm_p[context][sw.private[context]][prev - CONTENT_BASE - 3 * CLASS_SIZE])], "private"
        return None, None

    # ------------------------------------------------------------------ sets
    def dataset(self, context: int, sw: Switches, seed0: int, n: int, kinds_balanced: bool = True) -> list[dict]:
        out = []
        for i in range(n):
            kind = KINDS[i % 3] if kinds_balanced else None
            toks, p, label = self.sequence(context, sw, seed0 + i, kind)
            out.append({"item_id": f"g{context}-{seed0 + i}", "context": context, "seed": seed0 + i, "tokens": toks.tolist(), "p_star": p,
                        "target": int(toks[p]), "label": label, "switches": sw.to_dict()})
        return out


def balanced_orders(realization_seed: int) -> list[list[int]]:
    """Five eight-task orders: rotation by three of a seeded base permutation. Every task appears at least
    once in positions {0, 1} and once in {6, 7} across the five orders (verified in tests)."""
    rng = np.random.default_rng(1000 + realization_seed)
    base = [int(x) for x in rng.permutation(CONTEXTS)]
    return [base[3 * k % 8:] + base[: 3 * k % 8] for k in range(5)]


def sample_hash(g: Grammar, n: int = 1000, seed0: int = 90_000) -> str:
    h = hashlib.sha256()
    for c in range(CONTEXTS):
        for item in g.dataset(c, Switches.base(), seed0 + 125 * c, n // CONTEXTS):
            h.update(np.asarray(item["tokens"], np.int64).tobytes())
            h.update(bytes([item["p_star"]]))
    return h.hexdigest()


def write_generator_manifest(out: Path = MANIFEST_DIR / "generator.json", rule_seed: int = 7) -> dict:
    g = Grammar(rule_seed)
    man = {"fixture": "LATENT-GRAMMAR replacement (PA-2); no continuity with R8/R9", "vocab": VOCAB, "length": LENGTH,
           "reserved": {"PAD": PAD, "BOS": BOS}, "context_tokens": CONTEXT_TOKENS, "content_base": CONTENT_BASE, "classes": N_CLASSES, "class_size": CLASS_SIZE,
           "context_positions": list(CONTEXT_POSITIONS), "eval_window": list(EVAL_WINDOW), "kinds": list(KINDS), "grammar": g.to_dict(),
           "seed_ranges": {"base_train": [0, 200_000], "base_heldout": [200_000, 220_000], "task_train": "300_000 + 20_000*context + 1_000*realization + i",
                           "task_eval": "500_000 + 20_000*context + i (2,000 per task)", "heldout_combinations": "600_000 + 20_000*context + i", "sample_hash": 90_000},
           "sample_sha256_1000": sample_hash(g), "orders": {str(r): balanced_orders(r) for r in range(3)}}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(man, indent=1))
    return man


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rule-seed", type=int, default=7)
    a = ap.parse_args(argv)
    man = write_generator_manifest(rule_seed=a.rule_seed)
    print(json.dumps({k: man[k] for k in ("sample_sha256_1000", "orders")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
