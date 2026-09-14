"""M4 diagnostic: do the tapped observation features separate a record's paraphrases from its locality near-neighbours?
For every bank item: cosine(query embedding, own record key) for own prompt / paraphrase / locality prompt, the rank of the
own record among all bank records for paraphrases and locality prompts, and which record a locality prompt scores highest
against. Random reader vs trained readers; raw tap features (no reader) as a third view.
    python scripts/r1_51_feature_separability.py --bank <pkl> [--theta ...] → results/R1/pilot/feature_separability.json"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", default="/home/derp/cap/assets/runs/pc_cap/R1/banks/train_pool_counterfact_v1_1000.pkl")
    ap.add_argument("--thetas", default="random,/home/derp/cap/assets/runs/pc_cap/R1/pilot/r1_50_stream_cf1k/theta.npz")
    ap.add_argument("--items", type=int, default=400)
    args = ap.parse_args()
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.reader import ReaderConfig, init_reader, query_embedding, record_key
    from r1_13_stream_eval import load_theta

    bank = pickle.loads(Path(args.bank).read_bytes())
    items = bank.items[: args.items]
    rc = ReaderConfig()
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    template = {"reader": init_reader(k1, rc), "controller": init_controller(k2, ControllerConfig())}
    out = {}

    def unit(x):
        return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)

    views = {}
    for name in args.thetas.split(","):
        if name == "random":
            views["random_reader"] = template
        else:
            views[Path(name).parent.name] = load_theta(Path(name), template)
    v_key = jax.jit(jax.vmap(lambda p, l, s: record_key(p, rc, l, s), in_axes=(None, 0, 0)))
    v_q = jax.jit(jax.vmap(lambda p, l, s: query_embedding(p, rc, l, s), in_axes=(None, 0, 0)))
    sup_last = jnp.asarray(np.stack([it.key_last for it in items]))
    sup_span = jnp.asarray(np.stack([it.key_span for it in items]))
    for view, theta in list(views.items()) + [("raw_features", None)]:
        if theta is None:
            keys = unit(np.concatenate([np.stack([it.key_last for it in items]).reshape(len(items), -1), np.stack([it.key_span for it in items]).reshape(len(items), -1)], axis=1))
            def embed_q(last, span):
                return unit(np.concatenate([np.asarray(last).reshape(1, -1), np.asarray(span).reshape(1, -1)], axis=1))[0]
        else:
            keys = unit(np.asarray(v_key(theta["reader"], sup_last, sup_span)))
            def embed_q(last, span, theta=theta):
                return unit(np.asarray(v_q(theta["reader"], jnp.asarray(last)[None], jnp.asarray(span)[None])))[0]
        stats = {k: [] for k in ("own_cos", "para_cos", "loc_cos", "para_rank", "loc_rank", "loc_best_is_own", "para_best_is_own", "out_best_cos")}
        for i, it in enumerate(items):
            q_own = embed_q(it.key_last, it.key_span)
            stats["own_cos"].append(float(q_own @ keys[i]))
            for p_last, p_span, _ in it.paraphrases[:1]:
                q = embed_q(p_last, p_span)
                sc = keys @ q
                stats["para_cos"].append(float(sc[i]))
                stats["para_rank"].append(int((sc > sc[i]).sum()) + 1)
                stats["para_best_is_own"].append(int(np.argmax(sc) == i))
            for l_last, l_span, _ in it.locality[:1]:
                q = embed_q(l_last, l_span)
                sc = keys @ q
                stats["loc_cos"].append(float(sc[i]))
                stats["loc_rank"].append(int((sc > sc[i]).sum()) + 1)
                stats["loc_best_is_own"].append(int(np.argmax(sc) == i))
                stats["out_best_cos"].append(float(np.max(np.delete(sc, i))))
        out[view] = {k: {"mean": float(np.mean(v)), "p10": float(np.percentile(v, 10)), "p90": float(np.percentile(v, 90))} if k.endswith("cos") else {"mean": float(np.mean(v)), "median": float(np.median(v))} for k, v in stats.items() if v}
        print(view, json.dumps({k: (round(v["mean"], 3), round(v.get("p10", v.get("median", 0)), 3), round(v.get("p90", v.get("median", 0)), 3)) for k, v in out[view].items()}), flush=True)
    Path("results/R1/pilot/feature_separability.json").write_text(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
