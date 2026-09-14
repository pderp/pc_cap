"""R50-07 profile: candidate recall (own record in the store's top-k under the combined cosine+lexical score) and null
activation by role, as a function of memory size, using the cached feature banks and a trained reader. No base calls.
    python scripts/r1_53_scale_profile.py --theta <npz> [--sizes 64,100,300,1000] → results/R1/scale_profile_<tag>.json"""

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


def profile_memory(items, keys_raw, mem, queries, outs, rc, theta, stop, j_q, j_app, threshold):
    from pccap.revision_v1.reader import lex_feature
    K = keys_raw[mem]
    Kn = K / (np.linalg.norm(K, axis=1, keepdims=True) + 1e-8)
    lex_w = float(theta["reader"]["lex"]["score_w"])
    mem_prompts = [items[int(i)].prompt_ids for i in mem]

    def run(q_last, q_span, q_ids):
        q = np.asarray(j_q(theta["reader"], jnp.asarray(q_last), jnp.asarray(q_span)))
        qn = q / (np.linalg.norm(q) + 1e-8)
        lex = np.asarray([lex_feature(q_ids, pr, stop) for pr in mem_prompts], np.float32)
        score = (Kn @ qn) * rc.score_scale + lex_w * lex
        top = np.argsort(-score)[: rc.top_k]
        w, null, _ = j_app(theta["reader"], jnp.asarray(q), jnp.asarray(K[top]), jnp.ones(len(top), bool), jnp.asarray(lex[top]))
        return mem[top], float(null), int(np.argmax(np.asarray(w)))

    st = {"para_top1_fires": [], "para_in_topk": [], "para_null": [], "own_null": [], "loc_null": [], "loc_top1_is_own": [], "out_null": []}
    for qi in queries:
        it = items[int(qi)]
        if it.paraphrases:
            p_last, p_span, prefs = it.paraphrases[0]
            top_ids, null, best = run(p_last, p_span, prefs[0].ids[: prefs[0].n])
            st["para_in_topk"].append(int(qi in top_ids))
            st["para_top1_fires"].append(int(top_ids[best] == qi and null < threshold))
            st["para_null"].append(null)
        _, null, _ = run(it.key_last, it.key_span, it.prompt_ids)
        st["own_null"].append(null)
        if it.locality:
            l_last, l_span, lpf = it.locality[0]
            top_ids, null, best = run(l_last, l_span, lpf.ids[: lpf.n])
            st["loc_null"].append(null)
            st["loc_top1_is_own"].append(int(top_ids[best] == qi))
    for oi in outs:
        it = items[int(oi)]
        _, null, _ = run(it.key_last, it.key_span, it.prompt_ids)
        st["out_null"].append(null)
    out = {k: (float(np.mean(v)) if v else None) for k, v in st.items()}
    for k in ("para_null", "own_null", "loc_null", "out_null"):
        out[k.replace("_null", "_hard_null_rate")] = float(np.mean([x >= threshold for x in st[k]])) if st[k] else None
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theta", required=True)
    ap.add_argument("--banks", default="/home/derp/cap/assets/runs/pc_cap/R1/banks/train_pool_counterfact_v1_1000.pkl,/home/derp/cap/assets/runs/pc_cap/R1/banks/train_pool_zsre_v1_1000.pkl")
    ap.add_argument("--sizes", default="64,100,300,1000")
    ap.add_argument("--queries", type=int, default=200)
    ap.add_argument("--null-threshold", type=float, default=0.5)
    ap.add_argument("--stop-tokens", default="manifests/revision_v1/stop_tokens_v1.json")
    args = ap.parse_args()
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.reader import (
        ReaderConfig,
        applicability,
        init_reader,
        query_embedding,
        record_key,
    )
    from r1_13_stream_eval import load_theta

    stop = tuple(int(t) for t in json.loads((ROOT / args.stop_tokens).read_text())["tokens"])
    rc = ReaderConfig(lexical=True, stop_tokens=stop)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = load_theta(Path(args.theta), {"reader": init_reader(k1, rc), "controller": init_controller(k2, ControllerConfig())})
    v_key = jax.jit(jax.vmap(lambda p, l, s: record_key(p, rc, l, s), in_axes=(None, 0, 0)))
    j_q = jax.jit(lambda p, l, s: query_embedding(p, rc, l, s))
    j_app = jax.jit(lambda p, q, keys, mask, lex: applicability(p, rc, q, keys, mask, lex))
    rng = np.random.default_rng(0)
    out = {}
    for bank_path in args.banks.split(","):
        bank = pickle.loads(Path(bank_path).read_bytes())
        items = bank.items
        keys_raw = np.asarray(v_key(theta["reader"], jnp.asarray(np.stack([it.key_last for it in items])), jnp.asarray(np.stack([it.key_span for it in items]))))
        per_size = {}
        for M in [int(x) for x in args.sizes.split(",")]:
            M = min(M, len(items))
            perm = rng.permutation(len(items))
            mem = perm[:M]
            queries = rng.permutation(mem)[: args.queries]
            outs = perm[M : M + args.queries]
            per_size[str(M)] = profile_memory(items, keys_raw, mem, queries, outs, rc, theta, stop, j_q, j_app, args.null_threshold)
            print(bank.dataset, M, json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in per_size[str(M)].items()}), flush=True)
        out[bank.dataset] = per_size
    tag = Path(args.theta).parent.name
    (ROOT / "results" / "R1" / f"scale_profile_{tag}.json").write_text(json.dumps({"theta": args.theta, "null_threshold": args.null_threshold, "profile": out}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
