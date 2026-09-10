"""GRAM-02 competence table (plan §6.5): frozen-base accuracy b_i on every task's evaluation set (designated
positions; expected low by construction), on the base grammar, on the held-out switch combinations, per
mechanism kind; plus the joint-training reference (same total examples as a stream at the given per-task
count) trained on CPU. Writes results/GRAM/competence.json. CPU only."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.data.grammar_streams import eval_items, heldout_items, joint_reference
from pccap.fixtures.grammar_generator import CONTEXTS, Grammar, Switches
from pccap.fixtures.grammar_model import CFG, WEIGHTS, GrammarBase, _batch_loss
from pccap.fixtures.grammar_model import g as gj

ROOT = Path(__file__).resolve().parents[1]


def accuracy(base: GrammarBase, items) -> dict:
    by_kind: dict[str, list[int]] = {}
    for k in range(0, len(items), 256):
        chunk = items[k: k + 256]
        lg = base.last_logits_batch([it.prompt_ids for it in chunk])
        pred = lg.argmax(-1)
        for it, p in zip(chunk, pred):
            by_kind.setdefault(it.strata["kind"], []).append(int(p == int(it.answer_ids[0])))
    allv = [v for vs in by_kind.values() for v in vs]
    return {"acc": float(np.mean(allv)), "n": len(allv), "by_kind": {kd: float(np.mean(v)) for kd, v in by_kind.items()}}


def train_joint(n_per_task: int, steps: int, seed: int = 0) -> dict:
    import optax

    items = joint_reference(0, n_per_task, seed)
    params = jax.tree_util.tree_map(jnp.asarray, gj.load_params_npz(WEIGHTS))  # continue from the base grammar (the same starting point as the streams)
    opt = optax.adamw(3e-4, weight_decay=0.01)
    st = opt.init(params)

    @jax.jit
    def step(params, st, ids, m):
        loss, grads = jax.value_and_grad(_batch_loss)(params, ids, m, CFG)
        upd, st = opt.update(grads, st, params)
        return optax.apply_updates(params, upd), st, loss

    B = 64
    rng = np.random.default_rng(seed)
    t0 = time.time()
    for _ in range(steps):
        idx = rng.integers(len(items), size=B)
        ids = np.zeros((B, 64), np.int32)
        m = np.zeros((B, 64), np.float32)
        for j, i in enumerate(idx):
            x = items[i]
            L = len(x.prompt_ids)
            ids[j, :L] = x.prompt_ids
            ids[j, L] = x.answer_ids[0]
            m[j, L] = 1.0  # learn the designated target only (one item = one target)
        params, st, loss = step(params, st, jnp.asarray(ids), jnp.asarray(m))
    base = GrammarBase(params_np=jax.tree_util.tree_map(np.asarray, params))
    return {"n_per_task": n_per_task, "steps": steps, "examples_seen": steps * B, "seconds": time.time() - t0,
            "per_task": {str(t): accuracy(base, eval_items(t, n=500)) for t in range(CONTEXTS)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--joint-n", type=int, default=1024)
    ap.add_argument("--joint-steps", type=int, default=400)
    a = ap.parse_args()
    base = GrammarBase(weights=WEIGHTS)
    g = Grammar()
    out = {"weights": str(WEIGHTS), "sha256": base.checksum(), "label": "replacement fixture, no continuity with R8/R9 (PA-2)", "backend": jax.devices()[0].platform}
    base_items = []
    for c in range(CONTEXTS):
        for i in range(250):
            toks, p, label = g.sequence(c, Switches.base(), 210_000 + 2_500 * c + i)
            from pccap.data.grammar_streams import _item
            base_items.append(_item(toks, p, label, f"gb{c}-{i}", c))
    out["base_grammar"] = accuracy(base, base_items)
    out["tasks_frozen_base"] = {str(t): accuracy(base, eval_items(t, n=500)) for t in range(CONTEXTS)}
    out["heldout"] = {which: {str(t): accuracy(base, heldout_items(t, which, n=200)) for t in range(CONTEXTS)} for which in ("private_only", "shared_only")}
    out["joint_reference"] = train_joint(a.joint_n, a.joint_steps)
    p = ROOT / "results" / "GRAM" / "competence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=1))
    print("base grammar acc", out["base_grammar"]["acc"], "| frozen on tasks", {t: round(v["acc"], 3) for t, v in out["tasks_frozen_base"].items()},
          "| joint ref", {t: round(v["acc"], 3) for t, v in out["joint_reference"]["per_task"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
