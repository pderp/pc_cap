"""ePC base wrapper (S0-06): ``pccap.contracts.EPCBase`` on FabricPC (DEC-002).

The same GPT-2 architecture as ``BPBase`` plus error variables ``e_l`` at every post-block
residual (all 12 blocks, before ``ln_f``; sibling ``hdpc/wrap.py:134-164``). Built and tested on
the BP teacher weights first; ``EPCBase(params_np=...)`` / ``EPCBase.from_npz(path)`` swap in
distilled weights without code changes (REG-03).

* ``forward`` / ``forward_from`` / ``adjoint`` / ``checksum``: identical code path to ``BPBase``
  (an ePC network with zero errors *is* the feedforward network); ``graph_forward`` runs the
  FabricPC graph derive with zero errors and is compared with ``forward`` in test (a).
* ``infer_errors(ids, target, iters, writes)``: the declared finite-iteration error credit of
  ``docs/epc_energy.md``: zero-initialized errors, ``iters`` simultaneous SGD steps at
  ``error_lr = 0.1`` on ``E = ½Σ‖e‖² + CE(logits[p], target)``; ``target=None`` is the unclamped
  variant (with zero init it equals the feedforward computation; D.1 consistency check);
  ``target`` may also be an int array ``[n]`` with ``-1`` for "no target" (report-card calls).
* ``descent_sign = +1``: the settled error at a site points toward the target-conditioned state
  (at a stationary point ``e = −∂CE/∂h``), so ``+e/‖e‖`` is the descent direction; verified by
  ``epc_sign_control`` (S0-05 analogue) and recorded once.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g
from pccap.bases.bp import BPBase
from pccap.contracts import CostRecord, ErrorResult, ForwardResult, SiteId, Write
from pccap.harness.ledger import Ledger
from pccap.pc import epc_inference as epc
from pccap.pc.nodes import build_gpt2_graph, graph_params_from_numpy, node_names

ERROR_LR = 0.1
NOMINAL_ITERS = 8
REFERENCE_ITERS = 64


class EPCBase(BPBase):
    name = "EPC"
    descent_sign = +1.0

    def __init__(self, snapshot: Path | str = g.DEFAULT_SNAPSHOT, ledger: Ledger | None = None,
                 params_np: dict | None = None, cfg: g.GPT2Config | None = None, error_lr: float = ERROR_LR,
                 weights_label: str = "bp_teacher"):
        super().__init__(snapshot=snapshot, ledger=ledger, params_np=params_np, cfg=cfg)
        self.error_lr = float(error_lr)
        self.weights_label = weights_label
        self._graphs: dict[int, object] = {}
        self._gparams = graph_params_from_numpy(jax.tree_util.tree_map(np.asarray, self.params), self.cfg) \
            if params_np is None else graph_params_from_numpy(params_np, self.cfg)
        # share device arrays with self.params where possible (no second copy of wte)
        self.names = node_names(self.cfg.n_layer)

    @classmethod
    def from_npz(cls, path: Path | str, **kw) -> "EPCBase":
        params_np = g.load_params_npz(path)
        return cls(params_np=params_np, weights_label=str(path), **kw)

    # ------------------------------------------------------------------ graph helpers
    def graph(self, T: int):
        if T not in self._graphs:
            self._graphs[T] = build_gpt2_graph(self.cfg, T, epc.EPCInference(self.error_lr, NOMINAL_ITERS))
        return self._graphs[T]

    def _clamps(self, ids_d: jax.Array, target, n: int, T: int) -> dict:
        clamps = {self.names["ids"]: ids_d[None]}
        if target is not None:
            y = np.zeros((1, T, self.cfg.vocab), np.float32)
            tgt = np.asarray(target).reshape(-1)
            if tgt.size == 1:
                y[0, n - 1, int(tgt[0])] = 1.0
            else:
                if tgt.size != n:
                    raise ValueError("per-position targets must have length n (use -1 for none)")
                for t, v in enumerate(tgt):
                    if v >= 0:
                        y[0, t, int(v)] = 1.0
            clamps[self.names["logits"]] = jnp.asarray(y)
        return clamps

    def graph_forward(self, ids, writes: Sequence[Write] = (), phase: str = "learning") -> ForwardResult:
        """Feedforward through the FabricPC graph with zero errors (the wrapper's own vanilla forward)."""
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        T = int(ids_d.shape[0])
        structure = self.graph(T)
        clamps = self._clamps(ids_d, None, n, T)
        with self.ledger.call(phase, full_forwards=1, tokens=n) as rec:
            state, rows = epc.derive_fn(structure)(self._gparams, clamps, W, jnp.int32(p))
            rec.outputs = state
        logits = state.nodes[self.names["logits"]].z_mu[0]
        sites = {SiteId(m, g.BANK_BLOCK[m], p): rows[m][0] for m in sorted(rows)}
        return ForwardResult(logits=logits[:n], sites=sites, cost=rec)

    # ------------------------------------------------------------------ contract
    def infer_errors(self, ids, target, iters: int = NOMINAL_ITERS, writes: Sequence[Write] = (),
                     phase: str = "learning") -> ErrorResult:
        ids_d, n_d, W, n, p = self._prep(ids, writes)
        T = int(ids_d.shape[0])
        structure = self.graph(T)
        clamps = self._clamps(ids_d, target, n, T)
        with self.ledger.call(phase, full_forwards=iters + 1, reverses=iters + 1, settle_iters=iters, tokens=n) as rec:
            state, errors, energies, gnorms, rows = epc.relax_fn(structure, int(iters), self.error_lr)(
                self._gparams, clamps, W, jnp.int32(p))
            rec.outputs = (state, errors, energies, gnorms)
        energies = np.asarray(energies, np.float64)
        gnorms = np.asarray(gnorms, np.float64)
        if not (np.isfinite(energies).all() and np.isfinite(gnorms).all()):
            raise FloatingPointError("non-finite energy or gradient norm during error inference")  # Op. rule 8
        errs = {int(structure.nodes[name].node_info.node_config["layer"]): errors[name][0, :n] for name in errors}
        site_errors = {SiteId(m, g.BANK_BLOCK[m], p): errs[g.BANK_BLOCK[m]][p] for m in (1, 2, 3)}
        logits = state.nodes[self.names["logits"]].z_mu[0, :n]
        return ErrorResult(
            errors=errs, site_errors=site_errors, energies=[float(x) for x in energies],
            grad_norm_0=float(gnorms[0]), grad_norm_k=float(gnorms[-1]),
            r_k=float(gnorms[-1] / max(1.0, gnorms[0])), iters=int(iters), logits=logits, cost=rec,
            solver={"solver": "simultaneous SGD on all error variables", "error_lr": self.error_lr, "gamma": 1.0,
                    "init": "zeros per call", "reduction": "CE summed over declared targets", "dtype": "float32",
                    "precision": "identity", "stopping": "none (fixed iteration count)",
                    "terminal_residual_eval": True, "weights": self.weights_label,
                    "error_sites": "post-block residual, all 12 blocks, before ln_f"},
        )

    @staticmethod
    def error_at_site(result: ErrorResult, bank: int) -> jax.Array:
        for site, e in result.site_errors.items():
            if site.bank == bank:
                return e
        raise KeyError(bank)

    def cost_snapshot(self) -> CostRecord:
        return super().cost_snapshot()


def epc_sign_control(out_path: Path | None = None, seed: int = 0, iters: int = 200, lr: float = 0.1) -> dict:
    """Analytic control for the ePC credit sign (S0-05 analogue, PDF F.3 step 2).

    Toy: ``h`` fixed, free error ``e``, ``E(e) = ½‖e‖² + (w·(h+e) − y)²``. After settling, the
    direction ``+e/‖e‖`` applied to ``h`` must reduce the task loss ``(w·h − y)²``.
    """
    import json

    rng = np.random.default_rng(seed)
    w = jnp.asarray(rng.standard_normal(8), jnp.float32)
    h = jnp.asarray(rng.standard_normal(8), jnp.float32)
    y = jnp.float32(3.0)

    def task(hh):
        return (jnp.dot(w, hh) - y) ** 2

    def energy(e):
        return 0.5 * jnp.sum(e**2) + task(h + e)

    e = jnp.zeros(8, jnp.float32)
    g_ = jax.grad(energy)
    for _ in range(iters):
        e = e - lr * g_(e)
    d = e / jnp.linalg.norm(e)
    step = 1e-2
    l0, l1, lf = float(task(h)), float(task(h + step * d)), float(task(h - step * d))
    adj = jax.grad(task)(h)
    cos = float(jnp.dot(-adj, e) / (jnp.linalg.norm(adj) * jnp.linalg.norm(e)))
    rec = {"control": "epc_sign", "energy": "0.5|e|^2 + (w.(h+e)-y)^2", "iters": iters, "error_lr": lr,
           "loss_before": l0, "loss_after_plus_e": l1, "loss_after_minus_e": lf,
           "plus_e_reduces_loss": l1 < l0, "minus_e_increases_loss": lf > l0,
           "cos(settled_error, -adjoint)": cos, "descent_sign": +1.0, "seed": seed}
    if out_path is not None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(rec, indent=1))
    return rec
