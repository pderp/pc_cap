"""REG-00: JAX distillation driver reproducing the sibling's ePC training step (DEC-006, DEC-014).

One optimizer step (# reproduces hdpc/train_distill.py:601-760 ``run_step``), for a batch of
``B`` sequences split into micro-batches of ``m``:

1. teacher logits (frozen original GPT-2) for the micro-batch;
2. relaxation: ``T`` SGD steps on the error variables of the FabricPC graph
   (``pccap.pc.epc_inference.relax_errors``: zero init, ``e ← e − 0.1·∂E/∂e``, energy
   ``Σ_l ½‖e_l‖² + KDEnergy``), energies ``E_0..E_T`` recorded;
3. weight phase: ``∂/∂θ`` of ``pccap.pc.weight_phase.local_weight_energy`` at the settled errors
   (per-block ``−J_lᵀ e_l``; KD reaches ln_f and the tied wte only);
4. accumulate ``(1/B)·Σ_micro`` (exact: the energy is a per-sample sum) and apply Adam
   (lr 1e-6, β (0.9, 0.999), ε 1e-8, no weight decay) once per batch.

Everything runs inside one ``jax.jit`` per (T, m, B) with a ``lax.scan`` over micro-batches, so
device memory holds one micro-batch of activations. Host side: the homotopy schedule, the
tracking-residual hold monitor, milestones (prompt KL / held-out perplexity of the sibling plus a
held-out KL on the untouched shard tail), resumable checkpoints (params as ``gpt2_jax`` npz +
Adam moments + JSON state), CSV logs under ``results/REG/<run>/``, checkpoints under
``assets/models/epc/<run>/``. ``bp_loss`` = ``E_0`` (zero errors ⇒ the energy is the KD loss
itself), ``pc_loss`` = the accumulated local energy, ``tracking_residual = E_T / max(E_0, floor)``.

Intentional omissions (diagnostics that never touch the weights or the schedule): the sibling's
per-step BP-gradient cosine table, the sparsity histogram, the distinctness and pc-consistency
probes. The abort rules (prompt KL > 0.05, relaxation divergence, unreachable terminal τ) and
the hold/subdivision logic are implemented.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import optax

import pccap  # noqa: F401  (determinism flags)
from pccap.bases import gpt2_jax as g
from pccap.distill import data as D
from pccap.distill import recipe as R
from pccap.distill import schedule as S
from pccap.pc import epc_inference as epc
from pccap.pc.kd_energy import KDEnergy, kd_kl_loss
from pccap.pc.nodes import build_gpt2_graph, graph_params_from_numpy, node_names
from pccap.pc.weight_phase import local_weight_energy

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results" / "REG"


# ----------------------------------------------------------------------------- model pieces
def batched_logits(params: dict, ids: jnp.ndarray, cfg: g.GPT2Config) -> jnp.ndarray:
    """Vanilla logits ``[B, T, V]`` with the functional GPT-2 (teacher and evaluation forward)."""
    def one(i):
        h = g.embed(params, i)
        for blk in params["blocks"]:
            h = g.block(blk, h, cfg)
        return g.head(params, h, cfg)
    return jax.vmap(one)(ids)


class Trainer:
    """Holds the graph structures (one per T), jitted step functions and the optimizer."""

    def __init__(self, cfg: g.GPT2Config, r: R.Recipe, seq_len: int | None = None):
        self.cfg, self.r = cfg, r
        self.L = int(seq_len or r.seq_len)
        self.names = node_names(cfg.n_layer)
        self._structs: dict[int, object] = {}
        self._steps: dict[tuple, object] = {}
        self.opt = optax.adam(learning_rate=r.weight_lr, b1=r.adam_betas[0], b2=r.adam_betas[1], eps=r.adam_eps)
        self._eval_logits = jax.jit(lambda p, ids: batched_logits(p, ids, cfg))

    def structure(self, T: int):
        if T not in self._structs:
            self._structs[T] = build_gpt2_graph(self.cfg, self.L, epc.EPCInference(self.r.error_lr, T),
                                                head_energy=KDEnergy(self.r.kd_temperature))
        return self._structs[T]

    # ---- the step
    def step_fn(self, T: int, micro: int, batch: int, debug_grads: bool = False):
        key = (int(T), int(micro), int(batch), bool(debug_grads))
        if key in self._steps:
            return self._steps[key]
        structure = self.structure(T)
        cfg, names, r = self.cfg, self.names, self.r
        n_micro = batch // micro
        if n_micro * micro != batch:
            raise ValueError("micro_batch_size must divide batch_size")
        weight = 1.0 / batch  # hdpc/train_distill.py:640 (scale=m folded into the per-sample sum)

        def micro_pass(params, teacher, ids_m):
            gparams = graph_params_from_numpy(params, cfg)
            t_logits = batched_logits(teacher, ids_m, cfg)
            clamps = {names["ids"]: ids_m, names["logits"]: t_logits}
            _, errors, energies, gnorms, _ = epc.relax_errors(gparams, structure, clamps, None, None, int(T), r.error_lr)

            def local(p):
                return local_weight_energy(graph_params_from_numpy(p, cfg), structure, clamps, errors)

            pc_loss, grads = jax.value_and_grad(local)(params)
            err_norms = jnp.stack([jnp.sqrt(jnp.sum(jnp.square(errors[n]))) for n in names["blocks"]])
            return grads, pc_loss, energies, gnorms, err_norms

        def train_step(params, opt_state, teacher, ids):
            ids_mb = ids.reshape(n_micro, micro, ids.shape[-1])
            zero = jax.tree_util.tree_map(jnp.zeros_like, params)

            def body(acc, ids_m):
                grads, pc_loss, energies, gnorms, err_norms = micro_pass(params, teacher, ids_m)
                acc = jax.tree_util.tree_map(lambda a, gr: a + weight * gr, acc, grads)
                return acc, (pc_loss, energies, gnorms, err_norms)

            acc, (pc_losses, energies, gnorms, err_norms) = jax.lax.scan(body, zero, ids_mb)
            updates, opt_state = self.opt.update(acc, opt_state, params)
            params = optax.apply_updates(params, updates)
            stats = {
                "pc_loss": weight * jnp.sum(pc_losses),
                "inner_energy_start": weight * jnp.sum(energies[:, 0]),
                "inner_energy_end": weight * jnp.sum(energies[:, -1]),
                "inner_grad_norm_last": weight * jnp.sum(gnorms[:, -1]),
                "pc_grad_norm": epc._tree_norm(acc),
                "relaxation_energies_micro0": energies[0],
                "relaxation_grad_norms_micro0": gnorms[0],
                "error_norms_micro0": err_norms[0],
            }
            if debug_grads:
                stats["grads"] = acc  # tests only: the accumulated (1/B) Σ_samples gradient
            return params, opt_state, stats

        self._steps[key] = jax.jit(train_step)
        return self._steps[key]

    # ---- evaluation helpers
    def logits(self, params, ids: np.ndarray) -> jnp.ndarray:
        return self._eval_logits(params, jnp.asarray(ids, jnp.int32))


# ----------------------------------------------------------------------------- milestones
def prompt_ids(tok, r: R.Recipe) -> np.ndarray:
    """EVAL_PROMPTS right-padded with EOS to eval_seq_len (# reproduces train_distill.py:886-907;
    HF GPT-2 fast tokenizer, pad = eos, padding side right, truncation)."""
    out = np.full((len(R.EVAL_PROMPTS), r.eval_seq_len), D.EOS_ID, np.int32)
    for i, enc in enumerate(tok.encode_batch(R.EVAL_PROMPTS, add_special_tokens=False)):
        ids = enc.ids[: r.eval_seq_len]
        out[i, : len(ids)] = ids
    return out


def ce_mean(logits: jnp.ndarray, labels: np.ndarray) -> float:
    lp = jax.nn.log_softmax(logits.astype(jnp.float32), axis=-1)
    nll = -jnp.take_along_axis(lp, jnp.asarray(labels)[..., None], axis=-1)[..., 0]
    return float(jnp.mean(nll))


class Milestones:
    def __init__(self, trainer: Trainer, teacher, r: R.Recipe, tok, probe_tokens: np.ndarray, tail_tokens: np.ndarray | None):
        self.tr, self.teacher, self.r = trainer, teacher, r
        self.prompts = prompt_ids(tok, r)
        self.probe = probe_tokens
        self.tail = tail_tokens
        self._teacher_cache: dict = {}
        cfg = trainer.cfg

        def tail_stats(params, teacher, chunk):
            x, y = chunk[:, :-1], chunk[:, 1:]
            tl = batched_logits(teacher, x, cfg)
            sl = batched_logits(params, x, cfg)
            t_lp, s_lp = jax.nn.log_softmax(tl, axis=-1), jax.nn.log_softmax(sl, axis=-1)
            kl = jnp.mean(jnp.sum(jnp.exp(t_lp) * (t_lp - s_lp), axis=-1))
            t_nll = -jnp.mean(jnp.take_along_axis(t_lp, y[..., None], axis=-1))
            s_nll = -jnp.mean(jnp.take_along_axis(s_lp, y[..., None], axis=-1))
            return kl, t_nll, s_nll

        self._tail_stats = jax.jit(tail_stats)

    def _teacher_logits(self, key, ids):
        if key not in self._teacher_cache:
            self._teacher_cache[key] = self.tr.logits(self.teacher, ids)
        return self._teacher_cache[key]

    def evaluate(self, params) -> dict:
        r = self.r
        t = self._teacher_logits("prompts", self.prompts)
        s = self.tr.logits(params, self.prompts)
        kl = float(kd_kl_loss(s, t, beta=2.0))
        max_abs = float(jnp.max(jnp.abs(s - t)))
        t_losses, s_losses = [], []
        for i in range(r.eval_batches):
            ids, labels = D.labeled_batch(self.probe, r.eval_seq_len, r.eval_batch_size, r.eval_start_index + i)
            t_losses.append(ce_mean(self._teacher_logits(("heldout", i), ids), labels))
            s_losses.append(ce_mean(self.tr.logits(params, ids), labels))
        t_nll, s_nll = float(np.mean(t_losses)), float(np.mean(s_losses))
        row = {"prompt_kl": kl, "prompt_max_abs_logit_diff": max_abs, "teacher_nll": t_nll, "student_nll": s_nll,
               "teacher_ppl": math.exp(t_nll), "student_ppl": math.exp(s_nll),
               "heldout_ppl_relative_delta": (math.exp(s_nll) - math.exp(t_nll)) / math.exp(t_nll)}
        if self.tail is not None and self.tail.size >= (r.seq_len + 1) * r.heldout_windows:
            # extra fidelity probe on the untouched shard tail (not in the sibling; informative only).
            # Two windows per call, teacher recomputed (no cache: 64 windows of [512, V] logits would be 6.6 GB).
            n, L = r.heldout_windows, r.seq_len
            ids = self.tail[: n * (L + 1)].reshape(n, L + 1)
            kls, tn, sn = [], [], []
            for j in range(0, n, 2):
                chunk = jnp.asarray(ids[j: j + 2], jnp.int32)
                kl, t_nll, s_nll = self._tail_stats(params, self.teacher, chunk)
                kls.append(float(kl))
                tn.append(float(t_nll))
                sn.append(float(s_nll))
            row.update({"tail_kl_beta1": float(np.mean(kls)), "tail_teacher_nll": float(np.mean(tn)),
                        "tail_student_nll": float(np.mean(sn)), "tail_windows": n})
        return row


# ----------------------------------------------------------------------------- checkpoints
def _write_json(path: Path, obj) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=1, default=float))
    tmp.replace(path)


def save_checkpoint(ckpt_dir: Path, kind: str, keep_last: int, params, opt_state, state: dict) -> Path:
    step = int(state["global_step"])
    final = ckpt_dir / f"{kind}-{step:06d}"
    tmp = ckpt_dir / f".tmp-{kind}-{step:06d}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    params_np = jax.tree_util.tree_map(np.asarray, params)
    sha = g.save_params_npz(params_np, tmp / "params.npz")
    mu, nu = opt_state[0].mu, opt_state[0].nu
    np.savez(tmp / "adam.npz", count=np.asarray(opt_state[0].count),
             **{f"mu/{k}": np.asarray(v) for k, v in g.flatten_named(jax.tree_util.tree_map(np.asarray, mu))},
             **{f"nu/{k}": np.asarray(v) for k, v in g.flatten_named(jax.tree_util.tree_map(np.asarray, nu))})
    _write_json(tmp / "state.json", {**state, "params_sha256": sha, "kind": kind})
    if final.exists():
        shutil.rmtree(final)
    tmp.replace(final)
    (ckpt_dir / "latest").write_text(final.name + "\n")
    if kind == "step" and keep_last > 0:
        olds = sorted(p for p in ckpt_dir.glob("step-*") if p.is_dir())
        for p in olds[:-keep_last]:
            shutil.rmtree(p)
    return final


def _unflatten(z, prefix: str, template: dict) -> dict:
    flat = {k: z[f"{prefix}/{k}"] for k, _ in g.flatten_named(template)}
    return _nested_from_flat(flat, template)


def _nested_from_flat(flat: dict, template: dict) -> dict:
    blocks = []
    for l in range(len(template["blocks"])):
        blk: dict = {}
        for grp, sub, _ in g.PARAM_KEYS_BLOCK:
            blk.setdefault(grp, {})[sub] = flat[f"h.{l}.{grp}.{sub}"]
        blocks.append(blk)
    return {"wte": flat["wte"], "wpe": flat["wpe"], "ln_f": {"g": flat["ln_f.g"], "b": flat["ln_f.b"]}, "blocks": blocks}


def load_checkpoint(path: Path, opt) -> tuple[dict, object, dict]:
    path = Path(path)
    if path.is_file() and path.name == "latest":
        path = path.parent / path.read_text().strip()
    elif (path / "latest").exists() and not (path / "params.npz").exists():
        path = path / (path / "latest").read_text().strip()
    params = g.load_params_npz(path / "params.npz")
    z = np.load(path / "adam.npz")
    mu = _unflatten(z, "mu", params)
    nu = _unflatten(z, "nu", params)
    opt_state = opt.init(params)
    opt_state = (opt_state[0]._replace(count=jnp.asarray(z["count"]), mu=jax.tree_util.tree_map(jnp.asarray, mu),
                                       nu=jax.tree_util.tree_map(jnp.asarray, nu)),) + tuple(opt_state[1:])
    state = json.loads((path / "state.json").read_text())
    return params, opt_state, state


# ----------------------------------------------------------------------------- logs
MAIN_COLUMNS = ["step", "tokens_seen", "stage_index", "T", "error_lr", "tau", "tracking_residual", "tracking_residual_skipped",
                "pc_grad_norm", "inner_energy_start", "inner_energy_end", "inner_grad_norm_last", "bp_loss", "pc_loss",
                "hold", "hold_ema", "hold_baseline", "hold_threshold", "hold_reason", "stage_end_step", "pending_hold_steps",
                "step_seconds"]
RELAX_COLUMNS = ["step", "tokens_seen", "micro_batch", "T", "tau", "relax_step", "energy", "error_grad_norm"]
HOLD_COLUMNS = ["step", "tokens_seen", "stage_index", "T", "tau", "tracking_residual", "hold_ema", "hold_baseline",
                "hold_threshold", "hold_reason", "pending_hold_steps"]
MILESTONE_COLUMNS = ["step", "tokens_seen", "T", "tau", "prompt_kl", "prompt_max_abs_logit_diff", "teacher_nll", "student_nll",
                     "teacher_ppl", "student_ppl", "heldout_ppl_relative_delta", "tail_kl_beta1", "tail_teacher_nll",
                     "tail_student_nll", "tail_windows", "seconds"]


class Logs:
    def __init__(self, run_dir: Path, resume_step: int | None):
        run_dir.mkdir(parents=True, exist_ok=True)
        self.files = {}
        for name, cols in (("metrics", MAIN_COLUMNS), ("relaxation", RELAX_COLUMNS), ("holds", HOLD_COLUMNS),
                           ("milestones", MILESTONE_COLUMNS)):
            p = run_dir / f"{name}.csv"
            if p.exists() and resume_step is not None:
                # drop rows past the resume point so a resumed run leaves no duplicate rows
                rows = list(csv.DictReader(p.open()))
                keep = [r for r in rows if int(r["step"]) < resume_step or (name == "milestones" and int(r["step"]) <= resume_step)]
                with p.open("w", newline="") as f:
                    w = csv.DictWriter(f, fieldnames=cols)
                    w.writeheader()
                    w.writerows(keep)
            elif not p.exists() or resume_step is None:
                with p.open("w", newline="") as f:
                    csv.DictWriter(f, fieldnames=cols).writeheader()
            self.files[name] = (p, cols)

    def write(self, name: str, row: dict) -> None:
        p, cols = self.files[name]
        with p.open("a", newline="") as f:
            csv.DictWriter(f, fieldnames=cols, extrasaction="ignore").writerow({k: row.get(k, "") for k in cols})


# ----------------------------------------------------------------------------- main loop
def run(args) -> dict:
    r = R.Recipe(micro_batch_size=args.micro_batch_size, checkpoint_every=args.checkpoint_every, keep_last_k=args.keep_last_k,
                 heldout_windows=args.heldout_windows)
    run_dir = RESULTS / args.run_name
    ckpt_dir = R.RUNS_DIR / args.run_name / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    snapshot = Path(args.snapshot) if args.snapshot else g.DEFAULT_SNAPSHOT
    cfg = g.GPT2Config.from_snapshot(snapshot)
    teacher_np = g.load_params_numpy(snapshot, cfg)
    tok = g.load_tokenizer(snapshot)
    shard = D.load_shard(Path(args.data_file), min_tokens=(r.total_steps + 1) * r.tokens_per_step)
    data_sha = D.file_sha256(Path(args.data_file))
    probes = D.load_shard(Path(args.probe_file), min_tokens=D.probe_token_count(r))
    raw_shard = D.load_shard(Path(args.data_file))
    tail = raw_shard[r.training_tokens:] if raw_shard.size > r.training_tokens else None

    trainer = Trainer(cfg, r)
    teacher = jax.tree_util.tree_map(jnp.asarray, teacher_np)
    stage_list = S.stages(r.error_lr, r.schedule())
    total_steps = r.total_steps  # the schedule is always the protocol's; --chunk-steps only pauses the run
    monitor = S.TrackingResidualMonitor(r.hold_ema_decay, r.hold_window_steps)

    resume_from = None
    if args.resume:
        resume_from = Path(args.resume)
    elif (ckpt_dir / "latest").exists():
        resume_from = ckpt_dir
    if resume_from is not None:
        params, opt_state, st = load_checkpoint(resume_from, trainer.opt)
        if st["protocol_hash"] != r.protocol_hash() or st["data_sha256"] != data_sha:
            raise RuntimeError("checkpoint protocol/data mismatch")
        params = jax.tree_util.tree_map(jnp.asarray, params)
        stage_list = [S.HomotopyStage.from_dict(d) for d in st["stages"]]
        monitor = S.TrackingResidualMonitor.from_dict(st["monitor"])
        global_step, stage_index = int(st["global_step"]), int(st["stage_index"])
        stage_advance_pending, pending_hold_steps = bool(st["stage_advance_pending"]), int(st["pending_hold_steps"])
        divergence_steps = int(st["divergence_steps"])
        subdivision_counts = {(int(a), int(b)): int(c) for a, b, c in st["subdivision_counts"]}
        stage_end_step, next_milestone, tokens_seen = int(st["stage_end_step"]), int(st["next_milestone"]), int(st["tokens_seen"])
        milestone_rows = list(st["milestone_rows"])
        elapsed_before = float(st["elapsed_seconds"])
        gpu_seconds_before = float(st.get("gpu_seconds", elapsed_before))
        print(f"resumed from {resume_from} at step {global_step}", flush=True)
    else:
        params = jax.tree_util.tree_map(jnp.asarray, teacher_np)  # student starts as the teacher
        opt_state = trainer.opt.init(params)
        global_step = stage_index = 0
        stage_advance_pending, pending_hold_steps, divergence_steps = False, 0, 0
        subdivision_counts = {}
        stage_end_step = S.next_stage_end_step(0, total_steps, 0, len(stage_list))
        next_milestone, tokens_seen = r.milestone_tokens, 0
        milestone_rows = []
        elapsed_before = gpu_seconds_before = 0.0
    logs = Logs(run_dir, resume_step=global_step if resume_from is not None else None)
    ms = Milestones(trainer, teacher, r, tok, probes, tail)
    if resume_from is None:
        t0 = time.time()
        row = {"step": 0, "tokens_seen": 0, "T": stage_list[0].steps, "tau": stage_list[0].tau, **ms.evaluate(params)}
        row["seconds"] = time.time() - t0
        milestone_rows.append(row)
        logs.write("milestones", row)
        print(f"milestone step 0: prompt_kl={row['prompt_kl']:.3e} student_ppl={row['student_ppl']:.4f}", flush=True)

    def state_dict(elapsed: float, gpu_s: float) -> dict:
        return {"global_step": global_step, "tokens_seen": tokens_seen, "stage_index": stage_index,
                "stages": [s.to_dict() for s in stage_list], "stage_end_step": stage_end_step,
                "stage_advance_pending": stage_advance_pending, "pending_hold_steps": pending_hold_steps,
                "divergence_steps": divergence_steps, "subdivision_counts": [[a, b, c] for (a, b), c in subdivision_counts.items()],
                "next_milestone": next_milestone, "monitor": monitor.to_dict(), "milestone_rows": milestone_rows,
                "elapsed_seconds": elapsed, "gpu_seconds": gpu_s, "protocol_hash": r.protocol_hash(), "protocol": r.protocol_dict(),
                "data_sha256": data_sha, "probe_sha256": D.file_sha256(Path(args.probe_file)), "micro_batch_size": r.micro_batch_size,
                "total_steps": total_steps, "sibling_commit": R.SIBLING_COMMIT, "determinism": pccap.determinism_report(),
                "run_name": args.run_name}

    start = time.time() - elapsed_before
    gpu_seconds = gpu_seconds_before
    status, abort_reason, aborted = "completed", "", False
    stop_at = global_step + args.chunk_steps if args.chunk_steps else total_steps
    stop_at = min(stop_at, total_steps)
    deadline = time.time() + args.max_seconds if args.max_seconds else None
    compile_seconds: dict[int, float] = {}
    step_times: list[float] = []
    while global_step < stop_at:
        stage_advanced_now = False
        stage = stage_list[min(stage_index, len(stage_list) - 1)]
        ids = D.unlabeled_batch(shard, r.seq_len, r.batch_size, global_step)
        fn = trainer.step_fn(stage.steps, r.micro_batch_size, r.batch_size)
        t_step = time.time()
        first_of_T = stage.steps not in compile_seconds
        params, opt_state, stats = fn(params, opt_state, teacher, jnp.asarray(ids, jnp.int32))
        stats = jax.tree_util.tree_map(np.asarray, stats)
        dt = time.time() - t_step
        if first_of_T:
            compile_seconds[stage.steps] = dt
        else:
            step_times.append(dt)
        gpu_seconds += dt
        e0, eT = float(stats["inner_energy_start"]), float(stats["inner_energy_end"])
        residual = S.inner_energy_convergence_ratio(e0, eT, r.hold_energy_floor)
        if residual is None:
            hold, divergence_steps = False, 0
        else:
            hold = monitor.update(residual)
            if monitor.ema is not None and monitor.ema > R.RELAXATION_DIVERGENCE_THRESHOLD:
                divergence_steps += 1
            else:
                divergence_steps = 0
        tokens_seen += r.tokens_per_step
        row = {"step": global_step, "tokens_seen": tokens_seen, "stage_index": stage_index, "T": stage.steps,
               "error_lr": stage.error_lr, "tau": stage.tau, "tracking_residual": residual if residual is not None else 0.0,
               "tracking_residual_skipped": residual is None, "pc_grad_norm": float(stats["pc_grad_norm"]),
               "inner_energy_start": e0, "inner_energy_end": eT, "inner_grad_norm_last": float(stats["inner_grad_norm_last"]),
               "bp_loss": e0, "pc_loss": float(stats["pc_loss"]), "hold": hold,
               "hold_ema": monitor.ema if monitor.ema is not None else 0.0,
               "hold_baseline": monitor.baseline if monitor.baseline is not None else 0.0,
               "hold_threshold": monitor.hold_threshold if math.isfinite(monitor.hold_threshold) else 0.0,
               "hold_reason": monitor.last_hold_reason, "stage_end_step": stage_end_step,
               "pending_hold_steps": pending_hold_steps, "step_seconds": dt}
        logs.write("metrics", row)
        if global_step % args.relax_log_every == 0:
            en, gn = stats["relaxation_energies_micro0"], stats["relaxation_grad_norms_micro0"]
            for k in range(en.shape[0]):
                logs.write("relaxation", {"step": global_step, "tokens_seen": tokens_seen, "micro_batch": 0, "T": stage.steps,
                                          "tau": stage.tau, "relax_step": k, "energy": float(en[k]), "error_grad_norm": float(gn[k])})
        if hold:
            logs.write("holds", {**row, "tokens_seen": tokens_seen})
        if global_step % args.print_every == 0:
            print(f"step {global_step} T={stage.steps} bp={e0:.3e} pc={row['pc_loss']:.3e} resid={row['tracking_residual']:.4f} "
                  f"gnorm={row['pc_grad_norm']:.3e} {dt:.2f}s", flush=True)
        if divergence_steps >= R.RELAXATION_DIVERGENCE_STEPS:
            aborted, status = True, "relaxation_divergence"
            abort_reason = f"hold EMA {monitor.ema} exceeded {R.RELAXATION_DIVERGENCE_THRESHOLD} for {R.RELAXATION_DIVERGENCE_STEPS} updates"
            global_step += 1
            break
        if tokens_seen >= next_milestone:
            t0 = time.time()
            mrow = {"step": global_step + 1, "tokens_seen": tokens_seen, "T": stage.steps, "tau": stage.tau, **ms.evaluate(params)}
            mrow["seconds"] = time.time() - t0
            milestone_rows.append(mrow)
            logs.write("milestones", mrow)
            print(f"milestone step {global_step + 1}: prompt_kl={mrow['prompt_kl']:.3e} student_ppl={mrow['student_ppl']:.4f} "
                  f"tail_kl={mrow.get('tail_kl_beta1', float('nan')):.3e}", flush=True)
            if float(mrow["prompt_kl"]) > r.kl_abort_threshold:
                aborted, status = True, "prompt_kl_abort"
                abort_reason = f"prompt KL {mrow['prompt_kl']} exceeded {r.kl_abort_threshold}"
                global_step += 1
                break
            next_milestone += r.milestone_tokens
        completed = global_step + 1
        if not stage_advance_pending and stage_index < len(stage_list) - 1 and completed >= stage_end_step:
            stage_advance_pending = True
        if stage_advance_pending and hold:
            pending_hold_steps += 1
            if pending_hold_steps >= r.hold_patience_steps:
                nxt = stage_list[stage_index + 1] if stage_index + 1 < len(stage_list) else None
                sub = S.subdivide_stage(stage, nxt, subdivision_counts) if nxt is not None else None
                if sub is None:
                    aborted, status = True, "unreachable_terminal_tau"
                    abort_reason = f"tau ascent from T={stage.steps} blocked for {r.hold_patience_steps} steps; no subdivision left"
                    global_step += 1
                    break
                stage_list.insert(stage_index + 1, sub)
                pending_hold_steps = 0
        if stage_advance_pending and not hold:
            stage_index = min(stage_index + 1, len(stage_list) - 1)
            monitor.enter_stage()
            stage_advance_pending, pending_hold_steps, stage_advanced_now = False, 0, True
            stage_end_step = S.next_stage_end_step(completed, total_steps, stage_index, len(stage_list))
            print(f"stage -> T={stage_list[stage_index].steps} at step {completed}; next end {stage_end_step}", flush=True)
        global_step += 1
        at_end = global_step >= total_steps or global_step >= stop_at or (deadline is not None and time.time() > deadline)
        if r.checkpoint_every > 0 and (stage_advanced_now or global_step % r.checkpoint_every == 0 or at_end):
            kind = "final" if global_step >= total_steps else ("stage" if stage_advanced_now else "step")
            save_checkpoint(ckpt_dir, kind, r.keep_last_k, params, opt_state, state_dict(time.time() - start, gpu_seconds))
        if deadline is not None and time.time() > deadline:
            status = "paused_deadline"
            break
    if global_step >= total_steps and not aborted:
        final_stage = stage_list[min(stage_index, len(stage_list) - 1)]
        if final_stage.steps < stage_list[-1].steps:
            aborted, status = True, "unreachable_terminal_tau"
            abort_reason = f"token budget ended at T={final_stage.steps}"
    elif global_step < total_steps and not aborted and status == "completed":
        status = "paused_chunk"
    if aborted:
        save_checkpoint(ckpt_dir, "abort", 0, params, opt_state, state_dict(time.time() - start, gpu_seconds))
    summary = {"run_name": args.run_name, "status": status, "abort_reason": abort_reason, "global_step": global_step,
               "total_steps": total_steps, "tokens_seen": tokens_seen, "stage_index": stage_index,
               "schedule": [s.steps for s in stage_list], "elapsed_seconds": time.time() - start, "gpu_seconds": gpu_seconds,
               "compile_seconds_by_T": compile_seconds, "mean_step_seconds_this_chunk": float(np.mean(step_times)) if step_times else None,
               "steps_this_chunk": len(step_times) + len(compile_seconds), "micro_batch_size": r.micro_batch_size,
               "peak_mem_mib": _peak_mib(), "milestones": milestone_rows[-3:], "protocol_hash": r.protocol_hash(),
               "data_sha256": data_sha, "checkpoint_dir": str(ckpt_dir), "pilot": bool(args.pilot)}
    _write_json(run_dir / "summary.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "milestones"}, indent=1, default=float), flush=True)
    return summary


def _peak_mib() -> float:
    try:
        st = jax.devices()[0].memory_stats()
        return st["peak_bytes_in_use"] / 2**20 if st else 0.0
    except Exception:
        return 0.0


def parse(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run-name", default="epc-50m")
    ap.add_argument("--data-file", default=str(R.SHARD_PATH))
    ap.add_argument("--probe-file", default=str(R.PROBES_PATH))
    ap.add_argument("--snapshot", default=None)
    ap.add_argument("--micro-batch-size", type=int, default=R.Recipe.micro_batch_size)
    ap.add_argument("--checkpoint-every", type=int, default=R.Recipe.checkpoint_every)
    ap.add_argument("--keep-last-k", type=int, default=R.Recipe.keep_last_k)
    ap.add_argument("--heldout-windows", type=int, default=R.Recipe.heldout_windows)
    ap.add_argument("--pilot", action="store_true", help="label only: a pilot run (use --chunk-steps to stop early)")
    ap.add_argument("--chunk-steps", type=int, default=None, help="run this many steps then checkpoint and exit (resumable)")
    ap.add_argument("--max-seconds", type=float, default=None, help="wall-clock budget for this invocation (checkpoint and exit)")
    ap.add_argument("--resume", default=None, help="checkpoint dir (default: <run>/checkpoints/latest if present)")
    ap.add_argument("--relax-log-every", type=int, default=50)
    ap.add_argument("--print-every", type=int, default=10)
    return ap.parse_args(argv)


def main(argv=None) -> int:
    run(parse(argv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
