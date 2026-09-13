"""Stage 2 — alternating ePC surrogate (R1-22; docs/revision_v1_losses.md, logs/fabricpc_survey.md).

Same episodes, seeds, loss definitions, weights and optimizer schedule as ``train.py``; only the gradient estimator of
the base-dependent terms (L1 answer CE, L3 preservation KL) differs. Instead of exact backprop through GPT-2, the
gradient of the loss with respect to the three write vectors is taken from the ePC base's settled site errors
(``−descent_sign · error_at_site``; FabricPC graph, fixed iteration count), and θ receives it through the local loss
``Σ_m ⟨stop_grad(g_m), w_m(θ)⟩`` (a VJP through the controller and reader only). L2 (retrieval) involves no base pass
and is computed exactly in both trainers. No gradient ever reaches the base weights (they are not differentiated).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import jax
import jax.numpy as jnp
import numpy as np
import optax

from pccap.bases import gpt2_jax as g
from pccap.contracts import SiteId, Write
from pccap.revision_v1.controller import ControllerConfig, writes
from pccap.revision_v1.reader import ReaderConfig, query_embedding
from pccap.revision_v1.train import (
    ANSWER_ROLES,
    EpisodeFeatures,
    LossConfig,
    _records,
    _selection,
    retrieval_loss,
)


def prefix_writes(theta, rc: ReaderConfig, cc: ControllerConfig, feats: EpisodeFeatures, qi: int, ti: int):
    """The controller's writes for one query prefix as a pure function of θ (identical to train.prefix_loss's path)."""
    keys, codes = _records(theta, rc, feats)
    q = feats.queries[qi]
    pf = q.prefixes[ti]
    q_sel = query_embedding(theta["reader"], rc, jnp.asarray(q.last), jnp.asarray(q.span))
    _, w, null = _selection(theta, rc, keys, q_sel)
    code_mix = (w @ codes) / jnp.maximum(w.sum(), 1e-12)
    q_t = query_embedding(theta["reader"], rc, jnp.asarray(pf.last), jnp.asarray(pf.span))
    W, _ = writes(theta["controller"], cc, q_t, code_mix, 1.0 - null)
    return W


class EPCWriteGradients:
    """Surrogate ∂L/∂W from the ePC base: CE head for answer roles, KD (KL to the write-free logits) for preserve roles."""

    def __init__(self, base, iters: int = 8, kd_beta: float = 1.0):
        self.base, self.iters, self.kd_beta = base, int(iters), float(kd_beta)
        self._kd_graphs: dict[int, object] = {}
        self.sign = float(getattr(base, "descent_sign", 1.0))

    def _kd_graph(self, T: int):
        if T not in self._kd_graphs:
            from pccap.pc import epc_inference as epc
            from pccap.pc.kd_energy import KDEnergy
            from pccap.pc.nodes import build_gpt2_graph
            self._kd_graphs[T] = build_gpt2_graph(self.base.cfg, T, epc.EPCInference(self.base.error_lr, self.iters), head_energy=KDEnergy(self.kd_beta))
        return self._kd_graphs[T]

    def __call__(self, ids_unpadded: np.ndarray, target: int, W: np.ndarray, role: str) -> tuple[np.ndarray, float, dict]:
        base = self.base
        n = len(ids_unpadded)
        p = n - 1
        blocks = getattr(base, "bank_blocks", None) or g.BANK_BLOCK
        wl = [Write(SiteId(m, blocks[m], p), np.asarray(W[m - 1], np.float32)) for m in (1, 2, 3)]
        if role in ANSWER_ROLES:
            er = base.infer_errors(ids_unpadded, int(target), iters=self.iters, writes=wl, phase="learning")
            grad = np.stack([-self.sign * np.asarray(base.error_at_site(er, m), np.float32) for m in (1, 2, 3)])
            row = np.asarray(er.logits[p], np.float64)  # settled logits: a diagnostic, not the feedforward CE
            loss = float(np.log(np.exp(row - row.max()).sum()) + row.max() - row[int(target)])
            return grad, loss, {"energies": er.energies[0], "energy_k": er.energies[-1], "r_k": er.r_k, "settled_ce": True}
        # preserve: KL(write-free || corrected) through a KD head; teacher = write-free logits over all T positions
        from pccap.pc import epc_inference as epc
        ids_d, n_d, W_d, _, _ = base._prep(ids_unpadded, wl)
        T = int(ids_d.shape[0])
        with base.ledger.call("learning", full_forwards=1, tokens=n) as rec:
            teacher, _, _ = g.forward_jit(base.params, ids_d, n_d, jnp.zeros((3, base.d), jnp.float32), base.cfg, False, False)
            rec.outputs = teacher
        structure = self._kd_graph(T)
        clamps = {base.names["ids"]: ids_d[None], base.names["logits"]: jnp.asarray(teacher)[None]}
        with base.ledger.call("learning", full_forwards=self.iters + 1, reverses=self.iters + 1, settle_iters=self.iters, tokens=n) as rec:
            state, errors, energies, gnorms, _ = epc.relax_fn(structure, self.iters, base.error_lr)(base._gparams, clamps, W_d, jnp.int32(p))
            rec.outputs = (state, errors, energies, gnorms)
        errs = {int(structure.nodes[name].node_info.node_config["layer"]): errors[name][0, :n] for name in errors}
        grad = np.stack([-self.sign * np.asarray(errs[blocks[m]][p], np.float32) for m in (1, 2, 3)])
        # logged value: the FEEDFORWARD KL under the current writes (comparable with the reference's L3); the settled
        # state's KL is near zero by construction and is not a loss value
        with base.ledger.call("learning", full_forwards=1, tokens=n) as rec:
            ff, _, _ = g.forward_jit(base.params, ids_d, n_d, W_d, base.cfg, False, True)
            rec.outputs = ff
        ff = np.asarray(ff, np.float64)
        te = np.asarray(teacher[p], np.float64)
        p_t = np.exp(te - te.max()) / np.exp(te - te.max()).sum()
        ls = ff - ff.max() - np.log(np.exp(ff - ff.max()).sum())
        kl = float(np.sum(p_t * (np.log(p_t + 1e-30) - ls)))
        en = np.asarray(energies, np.float64)
        return grad, kl, {"energies": float(en[0]), "energy_k": float(en[-1]), "r_k": float(gnorms[-1] / max(1.0, gnorms[0]))}


def episode_grads_epc(theta, rc, cc, feats: EpisodeFeatures, lc: LossConfig, write_grads) -> tuple[dict, dict]:
    """Surrogate gradient over one episode: exact L2; L1/L3 through the ePC write gradients and a controller/reader VJP."""
    metrics = {"answer": 0.0, "answer_n": 0, "preserve": 0.0, "preserve_n": 0, "retrieval": 0.0, "code_norm": 0.0, "r_k": 0.0, "settle_n": 0}
    grads = jax.tree_util.tree_map(jnp.zeros_like, theta)

    def acc(gr, scale):
        return jax.tree_util.tree_map(lambda a, b: a + scale * b, grads, gr)

    if lc.w_retrieval:
        l, gr = jax.value_and_grad(retrieval_loss)(theta, rc, feats)
        metrics["retrieval"] = float(l)
        grads = acc(gr, lc.w_retrieval)
    for qi, q in enumerate(feats.queries):
        for ti, pf in enumerate(q.prefixes):
            W, vjp = jax.vjp(lambda th, qi=qi, ti=ti: prefix_writes(th, rc, cc, feats, qi, ti), theta)
            gW, loss, diag = write_grads(pf.ids[: pf.n], pf.target, np.asarray(W), q.role)
            gr = vjp(jnp.asarray(gW, jnp.float32))[0]  # local loss Σ_m ⟨stop_grad(g_m), w_m(θ)⟩
            kind = "answer" if q.role in ANSWER_ROLES else "preserve"
            metrics[kind] += loss
            metrics[f"{kind}_n"] += 1
            metrics["r_k"] += diag.get("r_k", 0.0)
            metrics["settle_n"] += 1
            grads = acc(gr, lc.w_answer if kind == "answer" else lc.w_preserve)
    metrics["answer"] /= max(1, metrics["answer_n"])
    metrics["preserve"] /= max(1, metrics["preserve_n"])
    metrics["r_k"] /= max(1, metrics["settle_n"])
    return grads, metrics


@dataclass
class EPCTrainer:
    rc: ReaderConfig
    cc: ControllerConfig
    write_grads: object  # EPCWriteGradients (or a stand-in in tests)
    lc: LossConfig = field(default_factory=LossConfig)
    lr: float = 1e-4
    clip: float = 1.0
    weight_decay: float = 0.0

    def __post_init__(self):
        self.opt = optax.chain(optax.clip_by_global_norm(self.clip), optax.adamw(self.lr, weight_decay=self.weight_decay))

    def init(self, theta):
        return self.opt.init(theta)

    def outer_step(self, theta, opt_state, episodes: list[EpisodeFeatures]):
        total, agg = None, {}
        for feats in episodes:
            gr, m = episode_grads_epc(theta, self.rc, self.cc, feats, self.lc, self.write_grads)
            total = gr if total is None else jax.tree_util.tree_map(jnp.add, total, gr)
            for k, v in m.items():
                agg[k] = agg.get(k, 0.0) + v
        total = jax.tree_util.tree_map(lambda x: x / len(episodes), total)
        gnorm = float(optax.global_norm(total))
        updates, opt_state = self.opt.update(total, opt_state, theta)
        theta = optax.apply_updates(theta, updates)
        metrics = {k: v / len(episodes) for k, v in agg.items()}
        metrics["grad_norm"] = gnorm
        return theta, opt_state, metrics
