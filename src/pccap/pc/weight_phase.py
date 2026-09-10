"""Local weight-phase energy of the ePC training recipe (REG-00; DEC-006, DEC-014).

After the errors have settled (``pccap.pc.epc_inference.relax_errors``), the sibling updates the
weights from a *local* energy in which every block sees a detached input and a detached target
(# reproduces hdpc/wrap.py:166-186 ``local_prediction_pairs`` and hdpc/energy.py:130-162
``local_weight_energy``):

    x_0 = embed(ids)                                 (NOT detached: wte/wpe receive block 0's term)
    for l:  pred_l = Block_l(x_l);  target_l = stop(pred_l + e_l);  x_{l+1} = target_l
            E_l = ½ ‖pred_l − stop(pred_l) − e_l‖²   ⇒  ∂E_l/∂θ_l = −J_lᵀ e_l
    logits = head(stop(x_L));  E_task = KD(logits)   (only ln_f and the tied wte see the task term)

This module walks the FabricPC graph structure with the same node ``forward`` calls the solver
uses, so the weight phase and the relaxation share one definition of every block. The Gaussian
node energy ``½‖z_latent − z_mu‖²`` with ``z_latent = stop(z_mu + e)`` is exactly the
``pred − stop(pred) − e`` trick (same value, same gradient). The head's energy is whatever the
graph was built with (``KDEnergy`` for distillation, one-hot CE otherwise).

``local_weight_energy`` returns the *sum* over the batch axis (FabricPC ``graph_energy``
convention), so a micro-batch of ``m`` samples contributes ``Σ_samples`` and the caller weights by
``1/B`` — the sibling's exact micro-batch accumulation (hdpc/train_distill.py:640-700).
"""

from __future__ import annotations

from typing import Dict

import jax
import jax.numpy as jnp
from fabricpc.core.inference import gather_inputs
from fabricpc.core.types import GraphParams, GraphState, NodeState

from pccap.pc.epc_inference import zero_graph_state


def local_weight_energy(params: GraphParams, structure, clamps: Dict[str, jnp.ndarray],
                        errors: Dict[str, jnp.ndarray]) -> jnp.ndarray:
    """Σ_batch of the local energy above, differentiable in ``params`` only through each node's own
    prediction (inputs of error-bearing nodes are ``stop_gradient``-ed)."""
    batch = next(iter(clamps.values())).shape[0]
    state: GraphState = zero_graph_state(structure, batch, clamps)
    total = jnp.zeros((), jnp.float32)
    for name in structure.node_order:
        node = structure.nodes[name]
        info = node.node_info
        if info.in_degree == 0:
            continue
        inputs = gather_inputs(info, structure, state)
        ns: NodeState = info.node_class.forward(params.nodes[name], inputs, state.nodes[name], info)
        if name in clamps:
            z = jnp.asarray(clamps[name])  # e.g. teacher logits / one-hot targets on the head
        elif name in errors:
            z = jax.lax.stop_gradient(ns.z_mu + errors[name])  # detached target = next node's input
        else:
            z = ns.z_mu  # error-free node (embedding): its output carries gradient into the next block
        ns = ns._replace(z_latent=z, error=z - ns.z_mu)
        if name not in clamps and info.out_degree == 0:
            ns = ns._replace(energy=jnp.zeros_like(ns.energy))
        else:
            ns = info.node_class.energy_functional(ns, info)
        total = total + jnp.sum(ns.energy)
        state = state._replace(nodes={**state.nodes, name: ns})
    return total
