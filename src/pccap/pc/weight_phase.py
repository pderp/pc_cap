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
uses, so the weight phase and the relaxation share one definition of every block. For the
error-bearing (free) nodes the energy is formed **exactly as the sibling writes it**,
``½‖(z_mu − stop(z_mu)) − e‖²``: the zero difference is taken first, so the tiny error survives
in float32. (The algebraically equal ``½‖stop(z_mu + e) − z_mu‖²`` — FabricPC's Gaussian node
energy on ``z_latent = z_mu + e`` — rounds ``e`` away whenever ``|e| < ulp(z_mu)``; GPT-2's
residual stream is O(10–10³), so a 1e-8 error is lost entirely. Found by REG-01's real-model
dissection, `scripts/reg_dissect.py`.) The head's energy is whatever the graph was built with
(``KDEnergy`` for distillation, one-hot CE otherwise) and is evaluated through its functional.

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
            ns = ns._replace(z_latent=z, error=z - ns.z_mu)
            ns = info.node_class.energy_functional(ns, info)
        elif name in errors:
            e = errors[name]
            z = jax.lax.stop_gradient(ns.z_mu + e)  # detached target = next node's input (rounded like the sibling's forward)
            delta = (ns.z_mu - jax.lax.stop_gradient(ns.z_mu)) - e  # exact: value −e, gradient J_lᵀ(−e)
            energy = 0.5 * jnp.sum(jnp.square(delta), axis=tuple(range(1, delta.ndim)))
            ns = ns._replace(z_latent=z, error=-delta, energy=energy)
        else:
            z = ns.z_mu  # error-free node (embedding): its output carries gradient into the next block
            ns = ns._replace(z_latent=z, error=jnp.zeros_like(z), energy=jnp.zeros_like(ns.energy))
        total = total + jnp.sum(ns.energy)
        state = state._replace(nodes={**state.nodes, name: ns})
    return total
