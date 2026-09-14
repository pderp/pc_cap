"""R1-24b runtime: informative language-model continuation of the base (DEC-040 option 3, second treatment).

Same execution flow, fidelity probe and evaluation block as Codex's literal runtime (`scripts/r1_24_runtime.py`, reused by
import); only the training phase differs: ordinary next-token cross-entropy on consecutive chunks of the pinned
OpenWebText shard (chunk = seq_len inputs + one lookahead target token; causal context resets per chunk; the last logit
is scored), fresh Adam, no weight decay, no teacher. Refuses any manifest whose recipe is not the hard-target LM recipe.
    python scripts/r1_24_lm_runtime.py --manifest manifests/revision_v1/r1_24_control_lm_v2.json --run-id <id>"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path("/home/derp/cap/assets")
sys.path.insert(0, str(ROOT / "scripts"))
from r1_24_runtime import evaluate, fidelity, sha, write_new  # noqa: E402


def lm_continue(m, original, cfg, out, deadline):
    import jax
    import jax.numpy as jnp
    import numpy as np
    import optax

    from pccap.distill.data import load_shard
    from pccap.distill.train import batched_logits
    r = m["recipe"]
    if r.get("estimator") != "exact_bp_next_token_base_continuation":
        raise ValueError("this runtime only executes the hard-target LM continuation recipe")
    data = load_shard(Path(m["data"]["path"]))
    params = jax.tree_util.tree_map(lambda x: jnp.array(x, copy=True), jax.tree_util.tree_map(jnp.asarray, original))
    opt = optax.adam(r["weight_lr"], b1=r["betas"][0], b2=r["betas"][1], eps=r["eps"])
    state = opt.init(params)
    seq = int(r["seq_len"])

    @jax.jit
    def step(p, opt_state, ids, targets, n_valid):
        def loss(x):
            logits = batched_logits(x, ids, cfg)[0]  # [T, V]
            lp = jax.nn.log_softmax(logits, axis=-1)
            nll = -lp[jnp.arange(ids.shape[1]), targets]
            mask = (jnp.arange(ids.shape[1]) < n_valid).astype(jnp.float32)
            return jnp.sum(nll * mask) / jnp.maximum(n_valid, 1)
        value, grad = jax.value_and_grad(loss)(p)
        update, new_state = opt.update(grad, opt_state, p)
        new_p = optax.apply_updates(p, update)
        finite = jnp.isfinite(value) & jnp.all(jnp.stack([jnp.all(jnp.isfinite(x)) for x in jax.tree_util.tree_leaves((grad, new_p))]))
        return new_p, new_state, value, optax.global_norm(grad), finite

    target_positions = int(m["budget"]["arithmetic"]["student_forward_tokens"])
    train_end = int(m["data"]["train_end_exclusive"])
    if target_positions + 1 > train_end:
        raise ValueError("the lookahead target would enter the held-out tail")
    train_deadline = min(deadline, time.monotonic() + m["stopping"]["training_wall_seconds"])
    consumed = steps = 0
    status = "complete"
    with (out / "training_steps.jsonl").open("x") as log:
        while consumed < target_positions:
            if time.monotonic() >= train_deadline:
                status = "training_time_stop"
                break
            n = min(seq, target_positions - consumed)
            chunk = data[consumed : consumed + n + 1]
            ids = np.zeros((1, seq), np.int32)
            tgt = np.zeros((seq,), np.int32)
            ids[0, :n] = chunk[:n]
            tgt[:n] = chunk[1 : n + 1]
            started = time.monotonic()
            new_params, new_state, loss, gradnorm, finite = step(params, state, jnp.asarray(ids), jnp.asarray(tgt), jnp.int32(n))
            jax.block_until_ready((new_params, new_state, loss, gradnorm, finite))
            consumed += n
            steps += 1
            ok = bool(finite)
            log.write(json.dumps({"step": steps, "input_positions": n, "forward_pass_tokens": n, "reverses": 1, "accepted": ok,
                                  "loss": float(loss) if np.isfinite(loss) else None, "grad_norm": float(gradnorm) if np.isfinite(gradnorm) else None,
                                  "wall_seconds": time.monotonic() - started}, allow_nan=False) + "\n")
            log.flush()
            if not ok:
                status = "nonfinite_update_rejected"
                break
            params, state = new_params, new_state
    return params, {"status": status, "source_positions": consumed, "forward_pass_tokens": consumed, "student_forwards": steps, "student_reverses": steps,
                    "teacher_forwards": 0, "requested_source_positions": target_positions, "optimizer": "fresh Adam, no weight decay",
                    "budget_complete": status == "complete" and consumed == target_positions, "matched_budget_claim": m["budget"]["exact_training_passes_verified"]}


def execute(m, manifest_path, run_id):
    import pccap  # noqa: F401
    from pccap.harness.lease import gpu_lease
    out = ROOT / "results/R1/r1_24" / run_id
    weights_dir = ASSETS / "runs/pc_cap/R1/r1_24" / run_id
    snapshots_dir = ASSETS / "runs/R1/r1_24" / run_id
    if any(p.exists() for p in (out, weights_dir, snapshots_dir)):
        raise FileExistsError("run, weights and snapshot trees must all be new")
    out.mkdir(parents=True, exist_ok=False)
    weights_dir.mkdir(parents=True, exist_ok=False)
    record = {"manifest": str(manifest_path), "manifest_sha256": sha(manifest_path), "treatment": "informative_lm_continuation", "status": "started",
              "training": None, "evaluations": [], "gpu_execution_requested": True,
              "interpretation": "matched" if m["budget"]["exact_training_passes_verified"] else "reported-ledger diagnostic only"}
    write_new(out / "launch.json", record)
    try:
        with gpu_lease("R1-24b:" + run_id, stage="R1", projected_seconds=m["stopping"]["total_wall_seconds"]) as lease:
            import jax
            import numpy as np

            from pccap.bases import gpt2_jax as g
            from pccap.bases.bp import _digest
            if not jax.devices("gpu"):
                raise RuntimeError("requires a JAX CUDA device")
            deadline = time.monotonic() + m["stopping"]["total_wall_seconds"]
            snapshot = Path(m["student_start"]["path"]).parent
            cfg = g.GPT2Config.from_snapshot(snapshot)
            original_np = g.load_params_numpy(snapshot, cfg)
            original = g.to_device(original_np)
            continued, record["training"] = lm_continue(m, original, cfg, out, deadline)
            continued_np = jax.tree_util.tree_map(np.asarray, continued)
            ckpt = weights_dir / "continued_params.npz"
            g.save_params_npz(continued_np, ckpt)
            record["checkpoint"] = {"path": str(ckpt), "sha256": sha(ckpt), "original_tensor_digest": _digest(original_np), "continued_tensor_digest": _digest(continued_np)}
            record["fidelity"] = fidelity(m, original, continued, cfg, deadline)
            record["evaluations"] = evaluate(m, original_np, continued_np, cfg, out, deadline)
            record["status"] = "complete" if record["training"]["budget_complete"] else "partial_training_budget"
        record["lease"] = lease.report
    except Exception as exc:
        record["status"] = "incomplete"
        record["error"] = {"type": type(exc).__name__, "message": str(exc)}
        write_new(out / "summary.json", record)
        raise
    write_new(out / "summary.json", record)
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    manifest_path = Path(args.manifest)
    m = json.loads(manifest_path.read_text())
    if m.get("task") != "R1-24b":
        raise ValueError("manifest is not an R1-24b recipe")
    for p, expected in m.get("sources_sha256", {}).items():
        if Path(p).exists() and sha(Path(p)) != expected:
            raise ValueError("source changed; prepare a new manifest version: " + p)
    return execute(m, manifest_path, args.run_id)


if __name__ == "__main__":
    raise SystemExit(main())
