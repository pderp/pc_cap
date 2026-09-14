"""R1-24 runtime, imported only by explicit --gpu execution of r1_24_control.

This module adds evaluation boundaries locally without changing shared harnesses.
It does not launch anything on import.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from r1_24_control import ASSETS, ROOT, sha, write_new


def kd_loss(student_logits, teacher_logits, temperature=2.0):
    import jax
    import jax.numpy as jnp
    t = jax.lax.stop_gradient(teacher_logits) / temperature
    log_t = jax.nn.log_softmax(t, axis=-1)
    log_s = jax.nn.log_softmax(student_logits / temperature, axis=-1)
    return temperature ** 2 * jnp.mean(jnp.sum(jnp.exp(log_t) * (log_t - log_s), axis=-1))


def deadline_check(deadline):
    if time.monotonic() >= deadline:
        raise TimeoutError("R1-24 wall-time ceiling reached before next compute unit")


def boundary_evaluator_class():
    import numpy as np

    from pccap.data.decode import _last_logits, greedy_decode
    from pccap.harness.runs import Evaluator

    class BoundaryEvaluator(Evaluator):
        def __init__(self, *args, deadline, **kwargs):
            self.deadline = deadline
            deadline_check(deadline)
            super().__init__(*args, **kwargs)

        def _decode_many(self, learner, prompts, tok):
            deadline_check(self.deadline)
            if not hasattr(learner, "reset_queries"):
                return super()._decode_many(learner, prompts, tok)
            out = []
            for p in prompts:
                deadline_check(self.deadline)
                learner.reset_queries()
                learner.selection_for(p)
                def predict(ids):
                    deadline_check(self.deadline)
                    return learner.predict(ids).logits
                out.append(greedy_decode(predict, p, tok, max_new=self.max_new))
            return out

        def _batch_last(self, learner, seqs, key_positions=None):
            deadline_check(self.deadline)
            if not hasattr(learner, "reset_queries"):
                return super()._batch_last(learner, seqs, key_positions)
            out = []
            for i, seq in enumerate(seqs):
                deadline_check(self.deadline)
                learner.reset_queries()
                boundary = len(seq) if key_positions is None else key_positions[i] + 1
                learner.selection_for(seq[:boundary])
                out.append(_last_logits(learner.predict(seq).logits))
            return np.stack(out)
    return BoundaryEvaluator


def distill(m, original, cfg, out, deadline):
    import jax
    import jax.numpy as jnp
    import numpy as np
    import optax

    from pccap.distill.data import load_shard
    from pccap.distill.train import batched_logits
    r = m["recipe"]
    data = load_shard(Path(m["data"]["path"]))
    teacher = jax.tree_util.tree_map(jnp.asarray, original)
    params = jax.tree_util.tree_map(lambda x: jnp.array(x, copy=True), teacher)
    opt = optax.adam(r["weight_lr"], b1=r["betas"][0], b2=r["betas"][1], eps=r["eps"])
    state = opt.init(params)

    @jax.jit
    def step(p, opt_state, ids):
        t_logits = jax.lax.stop_gradient(batched_logits(teacher, ids, cfg))
        def loss(x):
            return kd_loss(batched_logits(x, ids, cfg), t_logits, r["temperature"])
        value, grad = jax.value_and_grad(loss)(p)
        update, new_state = opt.update(grad, opt_state, p)
        new_p = optax.apply_updates(p, update)
        finite = jnp.isfinite(value) & jnp.all(jnp.stack([jnp.all(jnp.isfinite(x)) for x in jax.tree_util.tree_leaves((grad, new_p))]))
        return new_p, new_state, value, optax.global_norm(grad), finite

    target = m["budget"]["arithmetic"]["source_tokens"]
    train_deadline = min(deadline, time.monotonic() + m["stopping"]["training_wall_seconds"])
    consumed = steps = 0
    status = "complete"
    with (out / "training_steps.jsonl").open("x") as log:
        while consumed < target:
            if time.monotonic() >= train_deadline:
                status = "training_time_stop"
                break
            n = min(r["seq_len"], target - consumed)
            ids = jnp.asarray(data[consumed:consumed+n][None, :])
            started = time.monotonic()
            new_params, new_state, loss, gradnorm, finite = step(params, state, ids)
            jax.block_until_ready((new_params, new_state, loss, gradnorm, finite))
            consumed += n  # rejected/nonfinite calls still cost their passes
            steps += 1
            ok = bool(finite)
            log.write(json.dumps({"step": steps, "input_positions": n, "forward_pass_tokens": 2*n,
                "reverses": 1, "accepted": ok, "loss": float(loss) if np.isfinite(loss) else None,
                "grad_norm": float(gradnorm) if np.isfinite(gradnorm) else None,
                "wall_seconds": time.monotonic()-started}, allow_nan=False) + "\n")
            log.flush()
            if not ok:
                status = "nonfinite_update_rejected"
                break
            params, state = new_params, new_state
    return params, {"status": status, "source_tokens": consumed, "forward_pass_tokens": 2*consumed,
        "teacher_forwards": steps, "student_forwards": steps, "student_reverses": steps,
        "requested_source_tokens": target, "optimizer": "fresh Adam, no weight decay",
        "budget_complete": status == "complete" and consumed == target,
        "matched_budget_claim": m["budget"]["exact_training_passes_verified"]}


def fidelity(m, original, continued, cfg, deadline):
    import jax
    import jax.numpy as jnp
    import numpy as np

    from pccap.distill.data import load_shard
    from pccap.distill.train import batched_logits
    ids = load_shard(Path(m["data"]["path"]))
    start = m["data"]["heldout_start"]
    e = m["evaluation"]
    length = e["fidelity_window"]
    logits = jax.jit(lambda p, x: batched_logits(p, x, cfg))
    kl_sum = old_nll = new_nll = 0.0
    for i in range(e["fidelity_windows"]):
        deadline_check(deadline)
        chunk = ids[start+i*(length+1):start+(i+1)*(length+1)]
        if len(chunk) != length+1:
            raise ValueError("fidelity tail too short")
        x = jnp.asarray(chunk[:-1][None, :])
        t, s = logits(original, x), logits(continued, x)
        lp_t, lp_s = jax.nn.log_softmax(t[0]), jax.nn.log_softmax(s[0])
        kl_sum += float(jnp.sum(jnp.exp(lp_t) * (lp_t-lp_s)))
        target = jnp.asarray(chunk[1:])
        old_nll -= float(jnp.sum(lp_t[jnp.arange(length), target]))
        new_nll -= float(jnp.sum(lp_s[jnp.arange(length), target]))
    n = length * e["fidelity_windows"]
    kl, delta = kl_sum/n, (new_nll-old_nll)/n
    return {"positions": n, "ordinary_kl_nats": kl, "nll_original": old_nll/n,
        "nll_continued": new_nll/n, "nll_increase": delta, "perplexity_ratio": float(np.exp(delta)),
        "fidelity_pass": kl <= e["margins"]["kl_nats"] and delta <= e["margins"]["nll_increase"],
        "forward_pass_tokens": 2*n, "charged_phase": "query, excluded from matched training budget"}


def evaluate(m, original, continued, cfg, out, deadline):
    import jax
    import numpy as np

    from pccap.bases.bp import BPBase
    from pccap.cap.cap import CapConfig
    from pccap.contracts import Budget
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.arms import router_for
    from pccap.harness.ledger import Ledger
    from pccap.harness.runs import run_stream
    from pccap.harness.stage_s2 import load_dev_items
    from pccap.revision_v1.adapt import FastConfig
    from pccap.revision_v1.controller import ControllerConfig, init_controller
    from pccap.revision_v1.learner import RevisionCap, RevisionConfig
    from pccap.revision_v1.reader import ReaderConfig, init_reader, params_hash
    from pccap.revision_v1.v0_stable import StableCap
    ev_cls = boundary_evaluator_class()
    e = m["evaluation"]
    frozen = json.loads(Path(e["calibration"]).read_text())
    tok = GPT2Tokenizer()
    scales = {int(k): float(v) for k, v in frozen["b_m"].items()}
    drift = np.load(e["drift"]["path"], mmap_mode="r")
    rows = []
    for dataset in e["datasets"]:
        items, unrelated = load_dev_items(dataset, e["edits_per_stream"], seed=e["selection_seed"])
        if len(items) != 100:
            raise ValueError("development stream contains fewer than 100 items")
        for base_name, weights in (("original", original), ("continued", continued)):
            for cap_name in e["caps"]:
                deadline_check(deadline)
                ledger = Ledger()
                base = BPBase(params_np=weights, cfg=cfg, ledger=ledger)
                reference = BPBase(params_np=original, cfg=cfg, ledger=ledger)
                ev = ev_cls(reference, tok, unrelated[:e["locality_prompts"]], None, deadline=deadline)
                if cap_name == "v0_stable_C1":
                    cap = StableCap(base, CapConfig(arm="C1", read=frozen["radii"]["read"],
                        radii={int(k): float(v) for k,v in frozen["radii"]["bank"][dataset].items()},
                        bank_scales=scales, seed=e["cap_seed"], d=base.d), ledger)
                    router, arm, rounds = router_for("C1", cr_distribution=None), "C1", int(frozen["R"])
                    reusable_hash = None
                else:
                    rc = ReaderConfig(**e["reader"])
                    cc = ControllerConfig(A=float(frozen["A"]), bank_scales=tuple(scales[i] for i in (1,2,3)))
                    k1, k2 = jax.random.split(jax.random.PRNGKey(e["cap_seed"]))
                    template = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
                    paths, tree = jax.tree_util.tree_flatten_with_path(template)
                    with np.load(e["theta"]["path"]) as z:
                        leaves = [np.asarray(z[jax.tree_util.keystr(p)]) for p, x in paths]
                    if any(x.shape != a.shape for (_, x), a in zip(paths, leaves)):
                        raise ValueError("selected theta incompatible with declared reader/controller")
                    theta = jax.tree_util.tree_unflatten(tree, leaves)
                    cap = RevisionCap(base, RevisionConfig(reader=rc, controller=cc,
                        fast=FastConfig(steps=e["fast_steps"], delta_steps=e["delta_steps"], delta_lr=e["delta_lr"], tau=float(frozen["tau_edit"])),
                        null_threshold=e["null_threshold"], min_score=e["min_score"], tau_edit=float(frozen["tau_edit"])), ledger, params=theta)
                    router, arm, rounds = None, "R1", max(1, e["fast_steps"], e["delta_steps"])
                    reusable_hash = params_hash(cap.params)
                rd = out / dataset / base_name / cap_name
                metrics = run_stream(cap, items, router, Budget(A=float(frozen["A"]), epsilon=float(frozen["epsilon"]),
                    R=rounds, tau_edit=float(frozen["tau_edit"])), ev, rd, ledger,
                    checkpoints=(), seed=e["update_seed"], arm=arm,
                    resource_stop_seconds=max(0.0, deadline-time.monotonic()))
                if reusable_hash is not None and params_hash(cap.params) != reusable_hash:
                    raise RuntimeError("revision reusable weights mutated during editing")
                dev = ev_cls(reference, tok, [], drift, drift_positions=e["drift_windows"]*e["drift_window"],
                    drift_window=e["drift_window"], deadline=deadline)
                before = cap.state_hash()
                drift_result = dev.drift(cap)
                if cap.state_hash() != before:
                    raise RuntimeError("drift assay mutated persistent state")
                row = {"dataset": dataset, "base": base_name, "cap": cap_name, "metrics": metrics,
                    "drift": drift_result, "ledger_including_drift": ledger.totals(),
                    "ordered_item_ids": [it.item_id for it in items], "base_checksum": base.checksum()}
                write_new(rd / "control_endpoint.json", row)
                rows.append(row)
    return rows


def execute(m, manifest_path, run_id):
    # Import determinism setup BEFORE JAX, and acquire lease BEFORE CUDA discovery.
    import pccap  # noqa: F401
    from pccap.harness.lease import gpu_lease
    out = ROOT / "results/R1/r1_24" / run_id
    weights_dir = ASSETS / "runs/pc_cap/R1/r1_24" / run_id
    snapshots_dir = ASSETS / "runs/R1/r1_24" / run_id
    if any(p.exists() for p in (out, weights_dir, snapshots_dir)):
        raise FileExistsError("run, weights and snapshot trees must all be new")
    out.mkdir(parents=True, exist_ok=False)
    weights_dir.mkdir(parents=True, exist_ok=False)
    record = {"manifest": str(manifest_path), "manifest_sha256": sha(manifest_path),
        "status": "started", "training": None, "evaluations": [], "gpu_execution_requested": True,
        "interpretation": "matched" if m["budget"]["exact_training_passes_verified"] else "reported-ledger diagnostic only"}
    write_new(out / "launch.json", record)
    try:
        with gpu_lease("R1-24:"+run_id, stage="R1", projected_seconds=m["stopping"]["total_wall_seconds"]) as lease:
            import jax
            import numpy as np

            from pccap.bases import gpt2_jax as g
            from pccap.bases.bp import _digest
            if not jax.devices("gpu"):
                raise RuntimeError("--gpu requires a JAX CUDA device")
            deadline = time.monotonic() + m["stopping"]["total_wall_seconds"]
            snapshot = Path(m["student_start"]["path"]).parent
            cfg = g.GPT2Config.from_snapshot(snapshot)
            original_np = g.load_params_numpy(snapshot, cfg)
            original = g.to_device(original_np)
            continued, record["training"] = distill(m, original, cfg, out, deadline)
            continued_np = jax.tree_util.tree_map(np.asarray, continued)
            ckpt = weights_dir / "continued_params.npz"
            g.save_params_npz(continued_np, ckpt)
            record["checkpoint"] = {"path": str(ckpt), "sha256": sha(ckpt),
                "original_tensor_digest": _digest(original_np), "continued_tensor_digest": _digest(continued_np)}
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
