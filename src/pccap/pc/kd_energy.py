"""Knowledge-distillation energy functional for the FabricPC head node (REG-00; DEC-014).

``KDEnergy(beta)`` is the FabricPC ``EnergyFunctional`` used on the ``logits`` node during the
regeneration of the ePC checkpoint. The node's clamp ``z_latent`` holds the *teacher logits*
``[B, T, V]`` and ``z_mu`` the student logits; per sample

    E(y, z) = beta² · (1/T) · Σ_t Σ_v p_T(t, v) · (log p_T(t, v) − log p_S(t, v)),
    p_T = softmax(y / beta),  p_S = softmax(z / beta),

i.e. the forward KL at temperature ``beta`` times ``beta²``, averaged over positions — the
sibling's ``kd_kl_loss`` (# reproduces hdpc/energy.py:34-53, mean over the token axis) scaled by
the micro-batch size so that the energy is a per-sample *sum* (hdpc/train_distill.py:640-650:
``scale = micro_batch_size``, weight ``1/batch``). ``graph_energy`` sums per-sample energies, so
this functional plus FabricPC's summation *is* the sibling's ``scale × kd_kl_loss``. Everything
fp32; ``log_softmax`` via ``logsumexp`` (no clipping).
"""

from __future__ import annotations

import jax
import jax.numpy as jnp
from fabricpc.core.energy import EnergyFunctional


class KDEnergy(EnergyFunctional):
    def __init__(self, beta: float = 2.0):
        super().__init__(beta=float(beta))

    @staticmethod
    def energy(z_latent, z_mu, config=None):
        beta = float(config["beta"]) if config else 2.0
        teacher_logp = jax.nn.log_softmax(z_latent.astype(jnp.float32) / beta, axis=-1)
        student_logp = jax.nn.log_softmax(z_mu.astype(jnp.float32) / beta, axis=-1)
        kl = jnp.sum(jnp.exp(teacher_logp) * (teacher_logp - student_logp), axis=-1)  # [B, T]
        return (beta * beta) * jnp.mean(kl, axis=tuple(range(1, kl.ndim)))  # [B]

    @staticmethod
    def grad_latent(z_latent, z_mu, config=None):
        # dE/dy for the teacher clamp is never needed (the clamp is fixed); return zeros.
        return jnp.zeros_like(z_latent)


def kd_kl_loss(student_logits: jnp.ndarray, teacher_logits: jnp.ndarray, beta: float = 2.0) -> jnp.ndarray:
    """Token-mean KD loss over every leading axis (sibling ``kd_kl_loss``): ``beta² · mean_tokens KL``."""
    t = jax.nn.log_softmax(teacher_logits.astype(jnp.float32) / beta, axis=-1)
    s = jax.nn.log_softmax(student_logits.astype(jnp.float32) / beta, axis=-1)
    kl = jnp.sum(jnp.exp(t) * (t - s), axis=-1)
    return (beta * beta) * jnp.mean(kl)
