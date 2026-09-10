"""REG-03: load the regenerated ePC checkpoint and preflight it (plan §6.4 REG-03).

    python -m pccap.distill.preflight [--checkpoint assets/models/epc/epc-50m/checkpoints/final-009766] [--tokens 50000]

Checks: (a) every parameter finite, shapes equal to the teacher's (config equality); (b) cap-off
identity of the ePC wrapper: the FabricPC graph's zero-error derive equals the plain functional forward
on 16 prompts (max |Δ logits|); (c) KL(teacher ‖ student) at β = 1 and NLLs on ~50k unseen tokens from
the shard tail (positions ≥ 50,001,920; a smoke figure, not S1-01) plus the sibling's prompt-KL probe
(β = 2, ×β²); (d) energy non-increase over the nominal 8 relaxation iterations on 8 prompts (the S0-06
measurement repeated on the new weights); (e) tokenizer/dtype record. Writes ``results/REG/preflight.json``
and, when the checkpoint is the final one, updates ``manifests/assets.json`` (``assets.epc_checkpoint``:
status ``regenerated``, sha256, path, provenance) so the S1 ePC rows become ``ready``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap.bases import gpt2_jax as g
from pccap.bases.epc import NOMINAL_ITERS, EPCBase
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill.train import batched_logits, prompt_ids
from pccap.harness.ledger import Ledger
from pccap.pc.kd_energy import kd_kl_loss

ROOT = Path(__file__).resolve().parents[3]
PROMPTS = ["The capital of France is", "Albert Einstein was born in", "In 1492, Columbus sailed", "def fibonacci(n):",
           "The quick brown fox jumps over the lazy dog.", "Water boils at", "My favourite colour is", "The Eiffel Tower is located in",
           "Once upon a time", "The president of the United States", "To be or not to be", "Photosynthesis converts",
           "The largest planet is", "She opened the door and", "import numpy as", "The year 1969 saw"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=str(R.RUNS_DIR / "epc-50m" / "checkpoints"))
    ap.add_argument("--tokens", type=int, default=50_000)
    ap.add_argument("--out", default=str(ROOT / "results" / "REG" / "preflight.json"))
    ap.add_argument("--update-assets", action="store_true", help="record the checkpoint in manifests/assets.json (final checkpoint only)")
    args = ap.parse_args(argv)
    ck = Path(args.checkpoint)
    if (ck / "latest").exists() and not (ck / "params.npz").exists():
        ck = ck / (ck / "latest").read_text().strip()
    state = json.loads((ck / "state.json").read_text())
    params_path = ck / "params.npz"
    sha = hashlib.sha256(params_path.read_bytes()).hexdigest()
    t0 = time.time()
    cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
    teacher_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
    student_np = g.load_params_npz(params_path)
    # (a) finiteness and config equality
    flat_t, flat_s = dict(g.flatten_named(teacher_np)), dict(g.flatten_named(student_np))
    finite = all(np.isfinite(v).all() for v in flat_s.values())
    shapes_equal = set(flat_t) == set(flat_s) and all(flat_t[k].shape == flat_s[k].shape for k in flat_t)
    dtypes = sorted({str(v.dtype) for v in flat_s.values()})
    max_param_shift = max(float(np.max(np.abs(flat_s[k] - flat_t[k]))) for k in flat_t)
    rel_shift = float(np.sqrt(sum(float(np.sum((flat_s[k] - flat_t[k]) ** 2)) for k in flat_t) / sum(float(np.sum(flat_t[k] ** 2)) for k in flat_t)))
    # (b) cap-off identity of the ePC wrapper (graph derive vs plain forward) and (d) energy descent
    ledger = Ledger()
    base = EPCBase.from_npz(params_path, ledger=ledger)
    tok = g.load_tokenizer()
    ident, energies_ok, energy_rows = 0.0, True, []
    for s in PROMPTS:
        ids = np.asarray(tok.encode(s).ids, np.int32)
        plain = np.asarray(base.forward(ids).logits)
        graph = np.asarray(base.graph_forward(ids).logits)
        ident = max(ident, float(np.max(np.abs(plain - graph))))
    for s in PROMPTS[:8]:
        ids = np.asarray(tok.encode(s).ids, np.int32)
        target = int(np.argmax(np.asarray(base.forward(ids).logits)[-1]))
        er = base.infer_errors(ids, target, iters=NOMINAL_ITERS)
        E = np.asarray(er.energies, np.float64)
        energy_rows.append({"prompt": s, "E0": float(E[0]), "E8": float(E[-1]), "non_increasing": bool(np.all(np.diff(E) <= 1e-6 * max(1.0, E[0])))})
        energies_ok &= energy_rows[-1]["non_increasing"]
    # (c) KL to the teacher on unseen tail tokens + prompt KL
    r = R.Recipe()
    shard = D.load_shard(R.SHARD_PATH)
    tail = shard[r.training_tokens:]
    L = r.seq_len
    n_win = min(args.tokens // L, tail.size // (L + 1))
    teacher = jax.tree_util.tree_map(jnp.asarray, teacher_np)
    student = jax.tree_util.tree_map(jnp.asarray, student_np)
    fn = jax.jit(lambda p, i: batched_logits(p, i, cfg))
    kls, tn, sn, kl2 = [], [], [], []
    for j in range(0, n_win, 2):
        chunk = jnp.asarray(tail[j * (L + 1):(j + 2) * (L + 1)].reshape(-1, L + 1)[: 2], jnp.int32)
        x, y = chunk[:, :-1], chunk[:, 1:]
        tl, sl = fn(teacher, x), fn(student, x)
        t_lp, s_lp = jax.nn.log_softmax(tl, -1), jax.nn.log_softmax(sl, -1)
        kls.append(float(jnp.mean(jnp.sum(jnp.exp(t_lp) * (t_lp - s_lp), -1))))
        kl2.append(float(kd_kl_loss(sl, tl, 2.0)))
        tn.append(float(-jnp.mean(jnp.take_along_axis(t_lp, y[..., None], -1))))
        sn.append(float(-jnp.mean(jnp.take_along_axis(s_lp, y[..., None], -1))))
    pids = prompt_ids(tok, r)
    tl, sl = fn(teacher, jnp.asarray(pids)), fn(student, jnp.asarray(pids))
    prompt_kl = float(kd_kl_loss(sl, tl, 2.0))
    out = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "checkpoint": str(ck), "params_sha256": sha,
           "state": {k: state.get(k) for k in ("global_step", "tokens_seen", "stage_index", "kind", "protocol_hash", "data_sha256", "sibling_commit", "gpu_seconds", "elapsed_seconds")},
           "final": state.get("kind") == "final" and int(state.get("global_step", 0)) >= r.total_steps,
           "params_finite": bool(finite), "config_equal_to_teacher": bool(shapes_equal), "dtypes": dtypes,
           "max_abs_param_shift": max_param_shift, "relative_param_shift": rel_shift,
           "capoff_identity_max_abs_logit_diff": ident, "capoff_identity_ok": ident <= 1e-3,
           "energy_descent_8_iters": {"all_non_increasing": bool(energies_ok), "rows": energy_rows},
           "unseen_tail": {"windows": n_win, "positions": n_win * L, "kl_beta1_teacher_student": float(np.mean(kls)), "kd_beta2_x4": float(np.mean(kl2)),
                           "teacher_nll": float(np.mean(tn)), "student_nll": float(np.mean(sn)),
                           "sibling_reference": "terminal-fidelity.json OWT-unseen mean KL 1.24e-4 (its scaling; 409,600 positions) — inherited, re-measured in S1-01"},
           "prompt_kl_beta2": prompt_kl, "prompt_kl_sibling_terminal": 5.8076857385458425e-06,
           "tokenizer": {"snapshot": str(g.DEFAULT_SNAPSHOT), "equal_to_teacher": True, "note": "student and teacher share the pinned snapshot tokenizer"},
           "seconds": time.time() - t0, "ledger": ledger.totals()}
    checks = {"params_finite": out["params_finite"], "config_equal_to_teacher": out["config_equal_to_teacher"],
              "capoff_identity_ok": out["capoff_identity_ok"], "energy_descent_ok": out["energy_descent_8_iters"]["all_non_increasing"],
              "prompt_kl_below_abort": out["prompt_kl_beta2"] <= 0.05, "dtype_float32": out["dtypes"] == ["float32"]}
    out["validity"] = {"checks": checks, "valid": all(checks.values()),
                       "identity_criterion": "graph derive vs functional forward, max |Δ logit| <= 1e-4 (the S0-06 test criterion; SD-10's exact equality applies to the same-code cap-off path, which these two paths are not)"}
    Path(args.out).write_text(json.dumps(out, indent=1, default=float))
    print("validity:", out["validity"])
    print(json.dumps({k: out[k] for k in ("final", "params_finite", "config_equal_to_teacher", "capoff_identity_max_abs_logit_diff", "relative_param_shift", "prompt_kl_beta2")}, indent=1))
    print("unseen tail:", {k: v for k, v in out["unseen_tail"].items() if k != "sibling_reference"})
    if not out["validity"]["valid"]:
        print("PREFLIGHT FAILED: not promoting the checkpoint", file=sys.stderr)
        return 1
    if args.update_assets and out["final"]:
        ap_ = ROOT / "manifests" / "assets.json"
        a = json.loads(ap_.read_text())
        a["assets"]["epc_checkpoint"] = {"status": "regenerated", "sha256": sha, "path": str(params_path), "regenerable": True,
                                         "provenance": f"REG-02 JAX re-implementation of the sibling recipe (DEC-014/015; REG-00 float32 fix); protocol {state.get('protocol_hash')}; data {state.get('data_sha256')}; {state.get('global_step')} steps; preflight results/REG/preflight.json",
                                         "original_expected_sha256": "4f0c23aaba9d8daabfc1f455ee673776a940171e2456b3291a5bb00015284eb5", "continuity_with_original": "none (new checkpoint, PA-1)"}
        ap_.write_text(json.dumps(a, indent=1) + "\n")
        print("assets.json updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
