"""Error-optimization predictive coding (ePC) solver on FabricPC (S0-06; PDF D.6, F.6; SD-6).

FabricPC 0.5.2 optimizes *latents* (``InferenceSGD``); its ``NodeState.error`` is derived. ePC
(Goemaere et al., arXiv:2505.20137; sibling ``hdpc/relax.py``) makes the errors the free
variables and reconstructs the latents forward: ``z_latent_l = z_mu_l(z_latent_{l-1}) + e_l``.
This module supplies that solver as an ``InferenceBase`` subclass (``EPCInference``) so the
graph built by ``pccap.pc.nodes.build_gpt2_graph`` is a valid FabricPC graph, plus the pure
functions the wrapper calls directly:

* ``derive_states(params, structure, clamps, errors, writes, p)`` — one forward "derive": walk
  ``structure.node_order``; for each node call its FabricPC ``forward`` on the current latents,
  set ``z_latent = z_mu + e`` for free nodes (``node_config["epc_free"]``), the clamp for clamped
  nodes, and ``z_mu`` otherwise; cap writes are added at position ``p`` after the error at the
  three bank sites (sites are read *before* the write, PDF F.1). Returns the ``GraphState``.
* ``energy_of(errors)`` = ``fabricpc.core.energy.graph_energy`` of that state (Σ over all
  ``in_degree > 0`` nodes: ``½Σ‖e_l‖²`` from each block's ``GaussianEnergy`` plus the head's
  ``TokenCrossEntropyEnergy``). Nothing else is added: γ = 1, identity precision, no boundary
  terms (SD-6; sibling ``hdpc/energy.py:85-97``).
* ``relax_errors(...)`` — errors zero-initialized; ``iters`` steps of simultaneous gradient
  descent on all error variables, ``e ← e − error_lr · ∂E/∂e`` (plain SGD, no momentum, no
  stopping rule; sibling ``hdpc/relax.py:26-120``); returns the terminal state, ``E_0..E_k``,
  ``‖∇E_0‖``, and the explicitly evaluated terminal ``‖∇E_k‖`` (one extra value_and_grad).
  Weights never receive a gradient: the differentiated function's only argument is the error
  pytree.

Everything is fp32. ``jax.jit`` is applied to the whole relax with the structure closed over
(``GraphStructure`` is an all-static pytree).
"""

from __future__ import annotations

from typing import Any, Dict

import jax
import jax.numpy as jnp
from fabricpc.core.energy import graph_energy
from fabricpc.core.inference import InferenceBase, gather_inputs
from fabricpc.core.types import GraphParams, GraphState, NodeState


def free_nodes(structure) -> tuple[str, ...]:
    return tuple(n for n in structure.node_order if structure.nodes[n].node_info.node_config.get("epc_free", False))


def bank_nodes(structure) -> Dict[int, str]:
    out = {}
    for n in structure.node_order:
        b = structure.nodes[n].node_info.node_config.get("bank", 0)
        if b:
            out[int(b)] = n
    return out


def zero_graph_state(structure, batch: int, clamps: Dict[str, jnp.ndarray]) -> GraphState:
    """A GraphState with zero latents/errors (clamps applied). No forward is run here."""
    nodes = {}
    for name, node in structure.nodes.items():
        shape = (batch, *node.node_info.shape)
        z = jnp.asarray(clamps[name]) if name in clamps else jnp.zeros(shape, jnp.float32)
        nodes[name] = NodeState(z_latent=z, z_mu=jnp.zeros(shape, jnp.float32), error=jnp.zeros(shape, jnp.float32),
                                energy=jnp.zeros((batch,), jnp.float32), latent_grad=jnp.zeros(shape, jnp.float32))
    return GraphState(nodes=nodes, batch_size=batch)


def zero_errors(structure, batch: int) -> Dict[str, jnp.ndarray]:
    return {n: jnp.zeros((batch, *structure.nodes[n].node_info.shape), jnp.float32) for n in free_nodes(structure)}


def derive_states(params: GraphParams, structure, clamps: Dict[str, jnp.ndarray], errors: Dict[str, jnp.ndarray],
                  writes: jnp.ndarray | None = None, p: jnp.ndarray | int | None = None,
                  state: GraphState | None = None) -> tuple[GraphState, Dict[int, jnp.ndarray]]:
    """Forward reconstruction of every latent from the error variables (one 'forward')."""
    batch = next(iter(clamps.values())).shape[0]
    state = state if state is not None else zero_graph_state(structure, batch, clamps)
    site_rows: Dict[int, jnp.ndarray] = {}
    for name in structure.node_order:
        node = structure.nodes[name]
        info = node.node_info
        if info.in_degree == 0:
            continue
        ns = state.nodes[name]
        inputs = gather_inputs(info, structure, state)
        ns = info.node_class.forward(params.nodes[name], inputs, ns, info)
        if name in clamps:
            z = jnp.asarray(clamps[name])
        elif name in errors:
            z = ns.z_mu + errors[name]
        else:
            z = ns.z_mu
        m = info.node_config.get("bank", 0)
        if m and writes is not None:
            site_rows[int(m)] = z[:, p]
            z = z.at[:, p].add(writes[int(m) - 1][None])
        elif m:
            site_rows[int(m)] = z[:, p] if p is not None else None
        # The node's error is the free variable itself (exact), not the rounded ``z − z_mu``: with
        # z_mu = O(10–10³) in GPT-2's residual stream, ``(z_mu + e) − z_mu`` loses e whenever
        # |e| < ulp(z_mu), which would zero the prior term ½‖e‖² and its gradient (REG-01 dissection).
        ns = ns._replace(z_latent=z, error=errors[name] if name in errors else z - ns.z_mu)
        if name not in clamps and info.out_degree == 0:
            # FabricPC evaluation-mode rule (NodeBase.forward_and_latent_grads): an unclamped
            # output node contributes no energy (the "unclamped" variant of D.1).
            ns = ns._replace(energy=jnp.zeros_like(ns.energy))
        else:
            ns = info.node_class.energy_functional(ns, info)
        state = state._replace(nodes={**state.nodes, name: ns})
    return state, site_rows


def _tree_norm(tree) -> jnp.ndarray:
    return jnp.sqrt(sum(jnp.sum(jnp.square(x)) for x in jax.tree_util.tree_leaves(tree)))


def relax_errors(params: GraphParams, structure, clamps: Dict[str, jnp.ndarray], writes: jnp.ndarray,
                 p: jnp.ndarray, iters: int, error_lr: float):
    """Zero-init errors; ``iters`` SGD steps; explicit terminal energy and gradient norm.

    Pure function (jit it through ``relax_fn``). Returns
    ``(state_k, errors_k, energies[iters+1], grad_norms[iters+1], site_rows)`` where ``energies[t]``
    and ``grad_norms[t]`` are evaluated at ``e_t`` (before the t-th update), so the last entries are
    the terminal ``E_k`` and ``‖∇E_k‖``. Forward count = reverse count = iters+1.
    """
    batch = next(iter(clamps.values())).shape[0]
    errors0 = zero_errors(structure, batch)

    def energy_of(errors):
        st, _ = derive_states(params, structure, clamps, errors, writes, p)
        return graph_energy(st, structure)

    vg = jax.value_and_grad(energy_of)

    def step(errors, _):
        E, grad = vg(errors)
        gn = _tree_norm(grad)
        new = jax.tree_util.tree_map(lambda e, ge: e - error_lr * ge, errors, grad)
        return new, (E, gn)

    errors_k, (E_hist, g_hist) = jax.lax.scan(step, errors0, None, length=iters)
    E_k, grad_k = vg(errors_k)  # explicit terminal residual (D.6): not the pre-update norm
    energies = jnp.concatenate([E_hist, E_k[None]])
    grad_norms = jnp.concatenate([g_hist, _tree_norm(grad_k)[None]])
    state_k, site_rows = derive_states(params, structure, clamps, errors_k, writes, p)
    return state_k, errors_k, energies, grad_norms, site_rows


_JIT_CACHE: Dict[tuple, Any] = {}


def relax_fn(structure, iters: int, error_lr: float):
    """Jitted ``relax_errors`` with ``structure``, ``iters`` and ``error_lr`` closed over.

    ``GraphStructure`` holds dicts (unhashable), so it cannot be a static jit argument; the
    compiled function is cached by the structure's identity (the caller keeps one structure per
    sequence bucket alive).
    """
    key = ("relax", id(structure), int(iters), float(error_lr))
    if key not in _JIT_CACHE:
        def _run(params, clamps, writes, p):
            return relax_errors(params, structure, clamps, writes, p, int(iters), float(error_lr))

        _JIT_CACHE[key] = (jax.jit(_run), structure)
    return _JIT_CACHE[key][0]


def derive_fn(structure):
    """Jitted zero-error derive (the graph's own feedforward), cached like ``relax_fn``."""
    key = ("derive", id(structure))
    if key not in _JIT_CACHE:
        def _run(params, clamps, writes, p):
            return derive_states(params, structure, clamps, {}, writes, p)

        _JIT_CACHE[key] = (jax.jit(_run), structure)
    return _JIT_CACHE[key][0]


class EPCInference(InferenceBase):
    """FabricPC inference object for error optimization.

    ``graph(..., inference=EPCInference(error_lr=0.1, infer_steps=8))`` makes the graph's
    ``run_inference`` perform ePC settling with zero-initialized errors on every call. The
    per-node ``compute_new_latent`` extension point is not meaningful for ePC (latents are
    derived, not updated), so it raises.
    """

    def __init__(self, error_lr: float = 0.1, infer_steps: int = 8):
        super().__init__(error_lr=float(error_lr), infer_steps=int(infer_steps))

    @staticmethod
    def compute_new_latent(node_name, node_state, config):
        raise NotImplementedError("ePC updates error variables, not latents; use run_inference")

    @staticmethod
    def run_inference(params: GraphParams, initial_state: GraphState, clamps: Dict[str, Any], structure) -> GraphState:
        cfg = structure.config["inference"].config
        batch = initial_state.batch_size
        T = structure.nodes[structure.node_order[0]].node_info.shape[0]
        writes = jnp.zeros((3, structure.nodes[bank_nodes(structure)[1]].node_info.shape[-1]), jnp.float32)
        p = jnp.int32(T - 1)
        state_k, *_ = relax_fn(structure, int(cfg["infer_steps"]), float(cfg["error_lr"]))(params, clamps, writes, p)
        return state_k._replace(batch_size=batch)
