"""S1-01: P1 fidelity of the regenerated ePC checkpoint against the BP teacher (plan §6.7 S1-01; PDF D.1).

    python -m pccap.analysis.s1_p1 --epc-weights <params.npz> [--tokens 2000000]

* KL(p_T ‖ p_S) per token on H (DATA-04 ``H_tokens``; 2×10⁶ tokens sampled by document from
  WikiText-103 train, SD-1) at matched teacher-forced positions, feedforward; mean, p95, p99, max
  (finite); the "unclamped-after-8" variant equals the feedforward one by construction (zero-init errors,
  unclamped head ⇒ zero energy ⇒ zero error gradient) — checked on 8 windows and labelled the consistency
  check, not a second measurement.
* base task accuracy = next-token argmax accuracy on H for each base; argmax agreement between the bases
  on H positions and on the development edit-prompt pool (last position of each prompt).
* initially-correct fraction per base on the BP-selected development stream (teacher-forced complete
  answer greedy-correct; no reselection) and the common initially-incorrect subset (secondary).
* Reconciliation with the sibling's 1.24e-4 (its ``kd_kl_loss`` scaling: temperature 2 and ×β² = ×4 of
  the β = 2 KL) and the PDF's inherited 3e-5 figure: both scalings reported.

Writes ``results/S1/P1_epc.json`` (and ``P1_bp.json``: the teacher against itself, all zeros) with the
eligibility line: both means ≤ 1e-3 → eligible for matched-fidelity claims.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

import pccap  # noqa: F401
from pccap import ASSETS_ROOT
from pccap.bases import gpt2_jax as g
from pccap.bases.epc import EPCBase
from pccap.contracts import metric
from pccap.distill.train import batched_logits
from pccap.harness.ledger import Ledger
from pccap.harness.stage_s2 import load_dev_items
from pccap.pc.kd_energy import kd_kl_loss

ROOT = Path(__file__).resolve().parents[3]
S1 = ROOT / "results" / "S1"
LM = Path(ASSETS_ROOT) / "data" / "prepared" / "lm"
L = 512


def kl_stats(teacher, student, tokens: np.ndarray, n_tokens: int, cfg) -> dict:
    n_win = min(n_tokens // L, (tokens.size - 1) // L)
    fn = jax.jit(lambda p, i: batched_logits(p, i, cfg))

    @jax.jit
    def stats(tl, sl, y):
        t_lp, s_lp = jax.nn.log_softmax(tl, -1), jax.nn.log_softmax(sl, -1)
        kl = jnp.sum(jnp.exp(t_lp) * (t_lp - s_lp), -1)  # [B, L]
        kl2 = kd_kl_loss(sl, tl, 2.0)
        t_arg, s_arg = jnp.argmax(tl, -1), jnp.argmax(sl, -1)
        return kl, kl2, jnp.mean(t_arg == y), jnp.mean(s_arg == y), jnp.mean(t_arg == s_arg), -jnp.mean(jnp.take_along_axis(t_lp, y[..., None], -1)), -jnp.mean(jnp.take_along_axis(s_lp, y[..., None], -1))

    kls, kl2s, ta, sa, agree, tn, sn = [], [], [], [], [], [], []
    B = 4
    for j in range(0, n_win, B):
        idx = np.arange(j, min(j + B, n_win))
        x = np.stack([tokens[i * L:(i + 1) * L] for i in idx]).astype(np.int32)
        y = np.stack([tokens[i * L + 1:(i + 1) * L + 1] for i in idx]).astype(np.int32)
        tl, sl = fn(teacher, jnp.asarray(x)), fn(student, jnp.asarray(x))
        kl, kl2, a1, a2, ag, n1, n2 = stats(tl, sl, jnp.asarray(y))
        kls.append(np.asarray(kl, np.float64).ravel())
        kl2s.append(float(kl2))
        ta.append(float(a1))
        sa.append(float(a2))
        agree.append(float(ag))
        tn.append(float(n1))
        sn.append(float(n2))
    kl = np.concatenate(kls)
    finite = kl[np.isfinite(kl)]
    return {"positions": int(kl.size), "windows": int(n_win), "mean": float(finite.mean()), "p95": float(np.percentile(finite, 95)), "p99": float(np.percentile(finite, 99)),
            "max_finite": float(finite.max()), "nonfinite": int(kl.size - finite.size), "kd_beta2_x4_mean": float(np.mean(kl2s)),
            "teacher_argmax_accuracy": float(np.mean(ta)), "student_argmax_accuracy": float(np.mean(sa)), "argmax_agreement": float(np.mean(agree)),
            "teacher_nll": float(np.mean(tn)), "student_nll": float(np.mean(sn))}


def main(argv=None) -> int:
    from pccap.harness.lease import gpu_lease

    ap = argparse.ArgumentParser()
    ap.add_argument("--epc-weights", required=True)
    ap.add_argument("--tokens", type=int, default=2_000_000)
    ap.add_argument("--dev-items", type=int, default=300)
    args = ap.parse_args(argv)
    S1.mkdir(parents=True, exist_ok=True)
    cfg = g.GPT2Config.from_snapshot(g.DEFAULT_SNAPSHOT)
    teacher_np = g.load_params_numpy(g.DEFAULT_SNAPSHOT, cfg)
    student_np = g.load_params_npz(args.epc_weights)
    H = np.load(LM / "H_tokens.npy").astype(np.int32)
    t0 = time.time()
    with gpu_lease("S1-01", stage="S1", projected_seconds=1800) as lease:
        teacher = jax.tree_util.tree_map(jnp.asarray, teacher_np)
        student = jax.tree_util.tree_map(jnp.asarray, student_np)
        st = kl_stats(teacher, student, H, args.tokens, cfg)
        # consistency check: unclamped-after-8 relaxation equals feedforward (8 windows)
        ledger = Ledger()
        base = EPCBase.from_npz(args.epc_weights, ledger=ledger)
        cons = 0.0
        for i in range(8):
            ids = H[i * 128:(i + 1) * 128].astype(np.int32)
            ff = np.asarray(base.forward(ids).logits)
            er = base.infer_errors(ids, None, iters=8)  # unclamped head: zero energy → errors stay zero
            gf = np.asarray(base.graph_forward(ids).logits)
            cons = max(cons, float(np.max(np.abs(ff - gf))), float(np.max(np.abs(np.asarray(er.energies)))))
        # development edit-prompt pool: argmax agreement at the last prompt position and initially-correct fractions
        fn = jax.jit(lambda p, i, n: g.last_logits_batch_jit(p, i, n, cfg))
        zs, _ = load_dev_items("zsre", args.dev_items, seed=0)
        cf, _ = load_dev_items("counterfact", args.dev_items, seed=0)
        rows = {}
        for ds, items in (("zsre", zs), ("counterfact", cf)):
            agree = 0
            correct = {"bp": 0, "epc": 0, "both_incorrect": 0}
            for k in range(0, len(items), 32):
                chunk = items[k:k + 32]
                T = g.bucket_len(max(len(it.prompt_ids) for it in chunk))
                ids = jnp.asarray(np.stack([g.pad_ids(np.asarray(it.prompt_ids, np.int32), T) for it in chunk]))
                n = jnp.asarray([len(it.prompt_ids) for it in chunk], jnp.int32)
                tl, sl = np.asarray(fn(teacher, ids, n)), np.asarray(fn(student, ids, n))
                ta, sa = tl.argmax(-1), sl.argmax(-1)
                agree += int((ta == sa).sum())
                for it, a, b in zip(chunk, ta, sa):
                    first = int(it.answer_ids[0])
                    cb, ce = int(a) == first, int(b) == first
                    correct["bp"] += cb
                    correct["epc"] += ce
                    correct["both_incorrect"] += (not cb and not ce)
            rows[ds] = {"n": len(items), "last_position_argmax_agreement": agree / len(items),
                        "initially_correct_first_token_fraction": {k: v / len(items) for k, v in correct.items() if k != "both_incorrect"},
                        "common_initially_incorrect_first_token_fraction": correct["both_incorrect"] / len(items),
                        "note": "first answer token at the prompt's last position (the stream is BP-selected: teacher-incorrect by construction, DATA-01 E.2)"}
        report = lease.report
    eligible = st["mean"] <= 1e-3
    out = {"stage": "S1", "property": "P1", "base": "EPC (regenerated, REG-02) vs BP teacher", "weights": args.epc_weights, "H": {"tokens_used": st["windows"] * L, "source": "DATA-04 H_tokens (SD-1)"},
           "metrics": {"kl_mean": metric(st["mean"], units="nats", n=st["positions"]), "kl_p95": metric(st["p95"], units="nats", n=st["positions"]),
                       "kl_p99": metric(st["p99"], units="nats", n=st["positions"]), "kl_max_finite": metric(st["max_finite"], units="nats", n=st["positions"]),
                       "kl_feedforward_vs_unclamped8_consistency_max_abs": metric(cons, units="logits", n=8),
                       "teacher_argmax_accuracy_H": metric(st["teacher_argmax_accuracy"], units="fraction", n=st["positions"]),
                       "student_argmax_accuracy_H": metric(st["student_argmax_accuracy"], units="fraction", n=st["positions"]),
                       "argmax_agreement_H": metric(st["argmax_agreement"], units="fraction", n=st["positions"]),
                       "teacher_nll_H": metric(st["teacher_nll"], units="nats", n=st["positions"]), "student_nll_H": metric(st["student_nll"], units="nats", n=st["positions"]),
                       "kd_beta2_x4_mean_H": metric(st["kd_beta2_x4_mean"], units="nats(beta=2, x4)", n=st["positions"])},
           "dev_pool": rows, "nonfinite_positions": st["nonfinite"],
           "reconciliation": {"sibling_terminal_fidelity_kl": 1.24e-4, "sibling_scaling": "kd_kl_loss at temperature 2 times beta^2 = 4 (OWT-unseen, 409,600 positions)",
                              "pdf_inherited_figure": 3e-5, "ours_beta1_mean": st["mean"], "ours_beta2_x4_mean": st["kd_beta2_x4_mean"],
                              "note": "the regenerated checkpoint is a new run (PA-1); its OWT-tail figures are in results/REG/preflight.json"},
           "eligibility": {"matched_fidelity_claims": "eligible" if eligible else "ineligible", "rule": "mean KL <= 1e-3 on H (both bases; the BP row is the teacher against itself = 0)"},
           "lease": report, "seconds": time.time() - t0}
    (S1 / "P1_epc.json").write_text(json.dumps(out, indent=1, default=float))
    bp = {"stage": "S1", "property": "P1", "base": "BP teacher vs itself", "metrics": {"kl_mean": metric(0.0, units="nats", n=st["positions"])}, "eligibility": {"matched_fidelity_claims": "eligible"}}
    (S1 / "P1_bp.json").write_text(json.dumps(bp, indent=1, default=float))
    print(json.dumps({k: v["value"] for k, v in out["metrics"].items()}, indent=1))
    print("eligibility:", out["eligibility"]["matched_fidelity_claims"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
