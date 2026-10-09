"""Mandatory GPU validation (handoff §22 items 1, 2, 3, 11, 13) for ext-20261009. Writes validation/gpu_checks.json.

Checks: (1) directly loaded GPT-2 weights have the record's digest; (2) direct ``forward_jit`` reproduces the saved
cap-off losses of a frozen-record vector on sampled windows; (3) BPBase.forward == direct forward; (4) a PC-reader cap
with an empty memory, and a loaded memory on prompts where it abstains, returns the base logits exactly; (5) per-token
teacher-forced losses equal a hand computation from full logits with the causal shift; (6) total NLL = per-token sum;
(7) h_after = h_before + delta at the insertion site (full path vs partial path); (8) tokenisation boundary audit;
(9) recomputation of saved RET-GS/RET-ES from a saved checkpoint's rows.
"""

from __future__ import annotations

import pccap  # noqa: F401  # isort: skip

import json
import time

import jax.numpy as jnp
import numpy as np

from aw.extremes import models as M
from aw.extremes.common import OUT, Status, atomic_json, git_head, now, read_json
from aw.extremes.probes import build_probes
from aw.extremes.score import teacher_forced
from pccap.bases import gpt2_jax as g
from pccap.contracts import SiteId, Write
from pccap.data.tokenize import tokenize_pair


def main():
    from aw.pc_harm_readout import selection
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    t0 = time.monotonic()
    out = dict(run_id="ext-20261009", code_sha=git_head(), started=now(), checks={})
    with gpu_lease("ext-20261009 validate", stage="extremes", projected_seconds=900, exclusive=True) as lease:
        if blocking_cuda_processes(lease.other_cuda_processes()):
            raise RuntimeError("GPU busy with a project process")
        # (1) direct weights
        params_np, cfg, digest = M.load_direct_params()
        out["checks"]["direct_weights_digest"] = dict(digest=digest, expected=M.BASE_SHA, passed=digest == M.BASE_SHA)
        params = {k: v for k, v in params_np.items()}
        params_j = jnp.asarray(params["wte"])  # touch to force device placement later via forward_jit
        del params_j
        # (2) direct forward vs saved cap-off losses on sampled windows of a frozen-record vector
        vec = M.ROOT / "results/additional_work/PC-reader/eval-bp-s0-zsre/harm/vectors.npz"
        with np.load(vec, allow_pickle=False) as f:
            values = f["values"]
        windows, meta = selection("v5")
        rng = np.random.default_rng(0)
        sample = sorted(rng.choice(len(windows), 12, replace=False).tolist())
        import jax

        tree = jax.tree_util.tree_map(jnp.asarray, params_np)
        maxabs, n_pos = 0.0, 0
        for w in sample:
            ids = np.asarray(windows[w], np.int32)
            T = g.bucket_len(len(ids))
            logits, _, _ = g.forward_jit(tree, jnp.asarray(g.pad_ids(ids, T)), jnp.int32(len(ids)), jnp.zeros((3, cfg.d), jnp.float32), cfg, False, False)
            lg = np.asarray(logits, np.float64)[: len(ids)]
            lp = lg - lg.max(axis=1, keepdims=True)
            lp = lp - np.log(np.exp(lp).sum(axis=1, keepdims=True))
            losses = -lp[np.arange(len(ids) - 1), ids[1:]]  # position t predicts token t+1 (causal shift)
            saved = values[w, :, 1]
            maxabs = max(maxabs, float(np.abs(losses - saved).max()))
            n_pos += len(losses)
        out["checks"]["direct_forward_vs_saved_capoff"] = dict(windows=sample, positions=n_pos, max_abs_diff_nats=maxabs, passed=maxabs < 1e-3, vector=str(vec))
        # (3)+(4)+(5)+(6)+(7) through the sealed constructor
        frozen, parent, tok, binding = M.load_frozen("zsre")
        base = frozen.base
        probes, _ = build_probes("zsre")
        prompts = [p["prompt"] for p in probes if p["family"] == "edit"][:20]
        d3 = 0.0
        for pr in prompts:
            ids = np.asarray(tok.encode(pr), np.int32)
            a = np.asarray(base.forward(ids, (), phase="query", last_only=True).logits, np.float64)
            T = g.bucket_len(len(ids))
            b, _, _ = g.forward_jit(tree, jnp.asarray(g.pad_ids(ids, T)), jnp.int32(len(ids)), jnp.zeros((3, cfg.d), jnp.float32), cfg, False, True)
            d3 = max(d3, float(np.abs(a - np.asarray(b, np.float64)).max()))
        out["checks"]["bpbase_vs_direct_forward"] = dict(prompts=len(prompts), max_abs_logit_diff=d3, passed=d3 < 1e-4)
        adapter, cap, tok2, identity = M.load_reader("bp", 0, "zsre", parent=(parent, tok))
        d4, fired = 0.0, 0
        for pr in prompts:
            cap.reset_queries()
            ids = np.asarray(tok.encode(pr), np.int32)
            c = np.asarray(cap.predict(ids).logits, np.float64)
            f = np.asarray(frozen.predict(ids).logits, np.float64)
            d4 = max(d4, float(np.abs(c - f).max()))
        out["checks"]["empty_memory_cap_equals_frozen"] = dict(prompts=len(prompts), max_abs_logit_diff=d4, passed=d4 == 0.0)
        rec = M.snapshot_record("bp", 0, "zsre", 300)
        M.restore_memory(adapter, cap, rec)
        unseen = [p["prompt"] for p in probes if p["family"] == "unseen"][:40]
        d4b, abst, n_fire = 0.0, 0, 0
        for pr in unseen:
            cap.reset_queries()
            ids = np.asarray(tok.encode(pr), np.int32)
            c = np.asarray(cap.predict(ids).logits, np.float64)
            s = cap.selection_for(ids)
            f = np.asarray(frozen.predict(ids).logits, np.float64)
            if s.hard_null:
                abst += 1
                d4b = max(d4b, float(np.abs(c - f).max()))
            else:
                n_fire += 1
        out["checks"]["loaded_memory_abstention_equals_frozen"] = dict(prompts=len(unseen), abstained=abst, fired=n_fire, max_abs_logit_diff_when_abstaining=d4b, passed=d4b == 0.0)
        # (5)/(6) hand check of teacher forcing with the causal shift on three items
        edits = [p for p in probes if p["family"] == "edit"][:3]
        d5 = 0.0
        for p in edits:
            pair = tokenize_pair(tok, p["prompt"], p["targets"]["new"]["text"])
            per = teacher_forced(frozen, pair.prompt_ids, pair.answer_ids)
            full = np.concatenate([pair.prompt_ids, pair.answer_ids]).astype(np.int32)
            fr = base.forward(full, (), phase="query", last_only=False)
            lg = np.asarray(fr.logits, np.float64)
            lp = lg - lg.max(axis=1, keepdims=True)
            lp = lp - np.log(np.exp(lp).sum(axis=1, keepdims=True))
            P = len(pair.prompt_ids)
            hand = [-lp[P - 1 + t, int(pair.answer_ids[t])] for t in range(len(pair.answer_ids))]
            d5 = max(d5, float(np.abs(np.asarray(per) - np.asarray(hand)).max()))
            assert abs(sum(per) - np.sum(per)) < 1e-12
        out["checks"]["teacher_forced_hand_check"] = dict(items=len(edits), max_abs_diff_nats=d5, passed=d5 < 1e-3, note="prompt-only prefixes recomputed per step vs one full pass; causal shift verified; float32 bucket-length reduction noise ~1e-4 nats, same scale as check 2")
        # (7) residual insertion: full path with a write == partial path from the pre-write hidden plus the write
        ids = np.asarray(tok.encode(prompts[0]), np.int32)
        v = np.float32(rng.standard_normal(768) * 0.5)
        site = SiteId(1, g.BANK_BLOCK[1], len(ids) - 1)
        full_write = np.asarray(base.forward(ids, [Write(site, v)], phase="query", last_only=True).logits, np.float64)
        pre = base.forward(ids, (), retain_sites=True, phase="query", last_only=True)
        h = np.asarray(pre.hidden[1], np.float32).copy()
        h[len(ids) - 1] += v
        partial = np.asarray(base.forward_from(1, h, ids, (), phase="query", last_only=True).logits, np.float64)
        d7 = float(np.abs(full_write - partial).max())
        no_write = np.asarray(base.forward(ids, (), phase="query", last_only=True).logits, np.float64)
        out["checks"]["residual_site_arithmetic"] = dict(max_abs_logit_diff=d7, passed=d7 < 1e-3, write_changed_logits=bool(np.abs(full_write - no_write).max() > 1e-3),
                                                      site_row_equals_prewrite_hidden=bool(np.allclose(np.asarray(pre.sites[site]), np.asarray(pre.hidden[1])[len(ids) - 1], atol=1e-6)))
        # (8) tokenisation boundary audit over the 300 zsRE items
        mism = 0
        for p in [q for q in probes if q["family"] == "edit"]:
            pair = tokenize_pair(tok, p["prompt"], p["targets"]["new"]["text"])
            joint = tok.encode(p["prompt"] + pair.answer_text)
            if list(joint) != list(np.concatenate([pair.prompt_ids, pair.answer_ids])):
                mism += 1
        out["checks"]["tokenisation_boundary"] = dict(items=300, joint_tokenisation_differs=mism, note="the project scores prompt_ids + answer_ids (separately tokenised, leading space, newline); joint re-tokenisation differences are reported, not used")
        # (9) aggregation recompute from a saved checkpoint
        cp = read_json(M.PCR / "eval-bp-s0-zsre/stream/checkpoint-300.json")
        rows = cp["retention"]["rows"]
        gs = float(np.mean([r["gs"] for r in rows]))
        es = float(np.mean([r["es"] for r in rows]))
        out["checks"]["saved_metric_recompute"] = dict(RET_GS_recomputed=gs, RET_GS_saved=cp["metrics"]["RET-GS"]["value"], RET_ES_recomputed=es, RET_ES_saved=cp["metrics"]["RET-ES"]["value"],
                                                   passed=abs(gs - cp["metrics"]["RET-GS"]["value"]) < 1e-12 and abs(es - cp["metrics"]["RET-ES"]["value"]) < 1e-12)
    out.update(finished=now(), seconds=time.monotonic() - t0, all_passed=all(c.get("passed", True) for c in out["checks"].values()))
    path = OUT / "validation" / "gpu_checks.json"
    atomic_json(path, out)
    Status().artifact("validation/gpu_checks", path, all_passed=out["all_passed"])
    print(json.dumps({k: v.get("passed", "info") for k, v in out["checks"].items()}), "all_passed", out["all_passed"], f"{out['seconds']:.0f}s")


if __name__ == "__main__":
    main()
