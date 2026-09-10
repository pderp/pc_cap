"""Functional Q/V-only LoRA for HF's [input, output] Conv1D layout (S2-03).

B is [input, rank], A is [rank, output], so the stored delta is B @ A.
The effective LoRA scale is 1 (alpha = rank); no dropout or weight decay.
Only the adapters are differentiated by the learner, never the frozen base.
"""

from functools import partial

import jax
import jax.numpy as jnp
import numpy as np

from pccap.bases import gpt2_jax as g


class Prediction(np.ndarray):
    """Logits array with a .logits view for the current generic harness."""

    def __new__(cls, values):
        return np.asarray(values).view(cls)

    @property
    def logits(self):
        return self


def attention_delta(adapter):
    q = adapter["q"]["B"] @ adapter["q"]["A"]
    v = adapter["v"]["B"] @ adapter["v"]["A"]
    return jnp.concatenate((q, jnp.zeros_like(q), v), axis=-1)


def forward(params, adapters, ids, cfg):
    h = g.embed(params, ids)
    for original, adapter in zip(params["blocks"], adapters, strict=True):
        attn = {**original["c_attn"], "w": original["c_attn"]["w"] + attention_delta(adapter)}
        h = g.block({**original, "c_attn": attn}, h, cfg)
    return g.head(params, h, cfg)


forward_jit = jax.jit(forward, static_argnames=("cfg",))


def answer_loss(params, adapters, ids, targets, mask, cfg):
    """Mean answer-token CE; mask excludes prompt and padded positions."""
    logits = forward(params, adapters, ids, cfg)
    selected = jnp.take_along_axis(logits, targets[:, None], axis=-1)[:, 0]
    losses = jax.nn.logsumexp(logits, axis=-1) - selected
    return jnp.sum(jnp.where(mask, losses, 0.0)) / jnp.sum(mask)


@partial(jax.jit, static_argnames=("cfg",))
def batch_value_and_grad(params, adapters, ids, targets, masks, cfg):
    """Equal item weighting for the new item and optional replay item."""
    def loss(a):
        return jax.vmap(answer_loss, in_axes=(None, None, 0, 0, 0, None))(
            params, a, ids, targets, masks, cfg
        ).mean()

    return jax.value_and_grad(loss)(adapters)
