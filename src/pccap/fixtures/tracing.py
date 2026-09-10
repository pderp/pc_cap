"""DATA-07: causal tracing pairs on the learned grammar (plan §6.6 DATA-07; PDF D.10, E.1).

A pair changes **one latent** and holds the rest fixed. The latent of the successor mechanism
(shared_1) is the previous content token; the corrupted sequence replaces it by another member of its
class. The latent of the private and copy mechanisms is the sequence's class-3 value, which the copy
rule repeats at every class-3 position (A, A, A, …), so *one latent* means every copy of it in the
prefix: the corrupted sequence replaces all of them by A′ (replacing a single occurrence leaves the
latent readable from the other copies — measured: R ≈ 0, gap ≈ 0.02). Patch sites are the residual
stream at the bank blocks (1, 3, 5) at two positions fixed **before** any tracing outcome is seen: the
mechanism input position ``t_in`` (the last occurrence of the latent) and the prediction position
``p* − 1`` (the last prefix token, whose residual carries the prediction).
Restoring a site = running the corrupted sequence with the clean residual copied in at (block, position).

Score (D.10): ``R = (p_restore − p_corrupt) / (p_clean − p_corrupt)`` on the clean target's probability;
pairs with ``p_clean − p_corrupt < 0.1`` are *weak* and excluded but counted. Every site is scored and
kept: ``≥ 0.5`` sites, continuous scores, overshoot (R > 1), weak, no-site (no site ≥ 0.5) and
multi-site (≥ 2 sites ≥ 0.5) cases are all retained (D.10 rules). Tracing on the learned model is a
diagnostic, distinct from the constructed fixture's R*.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from jax import lax

from pccap.bases import gpt2_jax as g
from pccap.fixtures.grammar_generator import (
    CONTEXT_POSITIONS,
    CONTEXTS,
    KINDS,
    Grammar,
    Switches,
    class_of,
    class_tokens,
)
from pccap.fixtures.grammar_model import BANK_BLOCKS, CFG, GrammarBase

MANIFEST = Path(__file__).resolve().parents[3] / "manifests" / "grammar" / "tracing.json"
GAP_MIN = 0.1
SITE_THRESHOLD = 0.5


def restoration_score(p_clean: float, p_corrupt: float, p_restore: float) -> tuple[float | None, str]:
    """D.10 normalized score; ``None`` with reason ``weak`` when the clean–corrupt gap is below 0.1."""
    gap = p_clean - p_corrupt
    if gap < GAP_MIN:
        return None, "weak"
    return (p_restore - p_corrupt) / gap, "ok"


def classify(scores: dict[str, float]) -> str:
    strong = [k for k, v in scores.items() if v >= SITE_THRESHOLD]
    if not strong:
        return "no_site"
    if any(v > 1.0 for v in scores.values()):
        return "overshoot" if len(strong) == 1 else "multi_site_overshoot"
    return "single_site" if len(strong) == 1 else "multi_site"


# ----------------------------------------------------------------------------- patched forward
@functools.partial(jax.jit, static_argnames=("cfg", "block"))
def _patched_forward(params, ids, n, block, pos, patch_row, cfg):
    """Run the model; at the output of ``block`` replace the residual row at ``pos`` by ``patch_row``. Returns the
    log-probabilities at position n−1 and the residual rows at the bank blocks (for collecting clean rows)."""
    p = n - 1
    h = g.embed(params, ids)
    rows = {}
    for l in range(cfg.n_layer):
        h = g.block(params["blocks"][l], h, cfg)
        if l == block:
            h = lax.dynamic_update_index_in_dim(h, patch_row, pos, axis=0)
        if l in BANK_BLOCKS.values():
            rows[l] = h
    logits = g.head(params, h, cfg)
    return jax.nn.log_softmax(lax.dynamic_index_in_dim(logits, p, axis=0, keepdims=False)), rows


def run_probs(base: GrammarBase, ids: np.ndarray, block: int = -1, pos: int = 0, patch_row=None):
    ids = np.asarray(ids, np.int32)
    n = len(ids)
    padded = jnp.asarray(g.pad_ids(ids, CFG.n_pos, 0))
    if patch_row is None:
        patch_row = jnp.zeros((CFG.d,), jnp.float32)
        block = -1
    lp, rows = _patched_forward(base.params, padded, jnp.int32(n), block, jnp.int32(pos), jnp.asarray(patch_row, jnp.float32), CFG)
    return np.asarray(lp), {l: np.asarray(r) for l, r in rows.items()}


# ----------------------------------------------------------------------------- pairs
def make_pairs(n_per_kind: int = 40, seed: int = 0, grammar: Grammar | None = None, switches: str = "base") -> list[dict]:
    """Clean/corrupt pairs with fixed patch sites, chosen from the generator by seed before any tracing.
    ``switches="base"`` traces the grammar the frozen base was trained on (its competent regime); ``"task"``
    builds pairs under the task switches for tracing a model after it has learned a task (S3-03)."""
    gr = grammar or Grammar()
    rng = np.random.default_rng(seed)
    pairs = []
    for kind in KINDS:
        made = 0
        s = 700_000
        while made < n_per_kind:
            c = int(rng.integers(CONTEXTS))
            sw = Switches.base() if switches == "base" else Switches.task(c)
            toks, p, label = gr.sequence(c, sw, s, kind)
            s += 1
            t_in = p - 1
            while t_in in CONTEXT_POSITIONS:
                t_in -= 1
            corrupt = toks.copy()
            if kind == "shared_1":
                prev = int(toks[t_in])
                alternatives = [x for x in class_tokens(class_of(prev)) if x != prev]
                corrupt[t_in] = alternatives[int(rng.integers(len(alternatives)))]
                changed = [int(t_in)]
            else:
                # the latent is the sequence's class-3 value (seeded once, then repeated by the copy rule and consumed by the
                # private rule): the counterfactual regenerates the sequence with the same seed and a different class-3 latent,
                # so every rule-determined consequence changes consistently while all random draws stay identical
                occ = [i for i in range(p) if i not in CONTEXT_POSITIONS and class_of(int(toks[i])) == 3]
                if not occ:
                    continue
                a = int(toks[occ[0]])
                alternatives = [x for x in class_tokens(3) if x != a]
                a2 = alternatives[int(rng.integers(len(alternatives)))]
                corrupt, p2, _ = gr.sequence(c, sw, s - 1, kind, latent_override={"class3": a2})
                if p2 != p:
                    continue
                changed = [int(i) for i in np.flatnonzero(corrupt[:p] != toks[:p])]
                if not changed:
                    continue
                t_in = occ[-1]
            tgt_c, _ = gr.rule_target(corrupt[:p], c, sw)
            if tgt_c is None or tgt_c == int(toks[p]):
                continue
            pairs.append({"pair_id": f"tr-{kind}-{made}", "kind": kind, "context": c, "seed": s - 1, "p_star": p, "t_in": int(t_in), "changed_positions": changed,
                          "switches": sw.to_dict(), "clean": toks.tolist(), "corrupt": corrupt.tolist(), "target_clean": int(toks[p]), "target_corrupt": int(tgt_c),
                          "patch_sites": [{"block": b, "bank": m, "position": pos} for m, b in BANK_BLOCKS.items() for pos in sorted({int(t_in), int(p - 1)})]})
            made += 1
    return pairs


def write_manifest(out: Path = MANIFEST, n_per_kind: int = 40, seed: int = 0, switches: str = "base") -> dict:
    pairs = make_pairs(n_per_kind, seed, switches=switches)
    man = {"switches": switches, "rule": "one latent changed per pair (the mechanism input token, or the copy antecedent for shared_2); patch sites fixed before tracing: residual at blocks 1/3/5 at t_in and p*",
           "score": "R = (p_restore - p_corrupt) / (p_clean - p_corrupt) on the clean target; gap < 0.1 -> weak (excluded, counted); site >= 0.5 kept; overshoot/no-site/multi-site retained (D.10)",
           "n_per_kind": n_per_kind, "seed": seed, "pairs": pairs}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(man))
    return man


def trace(base: GrammarBase, pairs: list[dict]) -> dict:
    results, counts = [], {"weak": 0, "no_site": 0, "single_site": 0, "multi_site": 0, "overshoot": 0, "multi_site_overshoot": 0}
    for pr in pairs:
        clean, corrupt, p = np.asarray(pr["clean"], np.int32), np.asarray(pr["corrupt"], np.int32), pr["p_star"]
        tgt = pr["target_clean"]
        lp_clean, rows_clean = run_probs(base, clean[:p])
        lp_corr, _ = run_probs(base, corrupt[:p])
        p_clean, p_corr = float(np.exp(lp_clean[tgt])), float(np.exp(lp_corr[tgt]))
        scores, verdicts = {}, {}
        for site in pr["patch_sites"]:
            b, pos = site["block"], site["position"]
            lp_r, _ = run_probs(base, corrupt[:p], block=b, pos=pos, patch_row=rows_clean[b][pos])
            R, why = restoration_score(p_clean, p_corr, float(np.exp(lp_r[tgt])))
            key = f"bank{site['bank']}@{'t_in' if pos == pr['t_in'] else 'p*-1'}"
            scores[key], verdicts[key] = R, why
        weak = any(v == "weak" for v in verdicts.values())
        cat = "weak" if weak else classify({k: v for k, v in scores.items() if v is not None})
        counts[cat] += 1
        results.append({"pair_id": pr["pair_id"], "kind": pr["kind"], "context": pr["context"], "p_clean": p_clean, "p_corrupt": p_corr, "scores": scores, "category": cat})
    by_kind = {}
    for kd in KINDS:
        rs = [r for r in results if r["kind"] == kd and r["category"] != "weak"]
        if rs:
            keys = rs[0]["scores"].keys()
            by_kind[kd] = {"n": len(rs), "mean_R": {k: float(np.mean([r["scores"][k] for r in rs])) for k in keys},
                           "frac_site_ge_0.5": {k: float(np.mean([r["scores"][k] >= SITE_THRESHOLD for r in rs])) for k in keys}}
    return {"counts": counts, "by_kind": by_kind, "pairs": results, "label": "diagnostic on the learned replacement grammar; not the constructed R*"}


def main(argv=None) -> int:
    import argparse
    import time

    ap = argparse.ArgumentParser()
    ap.add_argument("--n-per-kind", type=int, default=40)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[3] / "results" / "GRAM" / "tracing.json"))
    a = ap.parse_args(argv)
    man = write_manifest(n_per_kind=a.n_per_kind)
    from pccap.fixtures.grammar_model import WEIGHTS

    base = GrammarBase(weights=WEIGHTS)
    t0 = time.time()
    rep = trace(base, man["pairs"]) | {"weights_sha256": base.checksum(), "seconds": time.time() - t0, "manifest": str(MANIFEST)}
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(rep, indent=1))
    print(json.dumps({"counts": rep["counts"], "by_kind": {k: v["frac_site_ge_0.5"] for k, v in rep["by_kind"].items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
