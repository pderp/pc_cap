"""Independent NumPy float64 GPT-2 reference (test oracle for S0-04 internal checks).

Written from the HF GPT-2 definition without reference to pccap.bases.gpt2_jax so that a
transposition/shape mistake in one is caught by the other. Used only in tests.
"""

import numpy as np


def ln(x, g, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = x.var(-1, keepdims=True)
    return (x - mu) / np.sqrt(var + eps) * g + b


def gelu_new(x):
    return 0.5 * x * (1 + np.tanh(np.sqrt(2 / np.pi) * (x + 0.044715 * x**3)))


def softmax(x):
    x = x - x.max(-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(-1, keepdims=True)


def forward(params, ids, writes=None, n_head=12, return_hidden=False):
    """params: NumPy dict as loaded by gpt2_jax.load_params_numpy (cast to float64 here).
    writes: dict {block_index: vector} added at the last position after that block."""
    P = lambda a: np.asarray(a, dtype=np.float64)  # noqa: E731
    T = len(ids)
    h = P(params["wte"])[ids] + P(params["wpe"])[:T]
    hidden = {}
    d = h.shape[-1]
    hd = d // n_head
    for l, blk in enumerate(params["blocks"]):
        x = ln(h, P(blk["ln_1"]["g"]), P(blk["ln_1"]["b"]))
        qkv = x @ P(blk["c_attn"]["w"]) + P(blk["c_attn"]["b"])
        q, k, v = qkv[:, :d], qkv[:, d:2 * d], qkv[:, 2 * d:]
        out = np.zeros((T, d))
        for hh in range(n_head):
            qh, kh, vh = (a[:, hh * hd:(hh + 1) * hd] for a in (q, k, v))
            s = qh @ kh.T / np.sqrt(hd)
            s = np.where(np.tril(np.ones((T, T), bool)), s, -np.inf)
            out[:, hh * hd:(hh + 1) * hd] = softmax(s) @ vh
        h = h + out @ P(blk["c_proj"]["w"]) + P(blk["c_proj"]["b"])
        x = ln(h, P(blk["ln_2"]["g"]), P(blk["ln_2"]["b"]))
        h = h + gelu_new(x @ P(blk["c_fc"]["w"]) + P(blk["c_fc"]["b"])) @ P(blk["c_proj2"]["w"]) + P(blk["c_proj2"]["b"])
        hidden[l] = h.copy()
        if writes and l in writes:
            h = h.copy()
            h[-1] += np.asarray(writes[l], dtype=np.float64)
    logits = ln(h, P(params["ln_f"]["g"]), P(params["ln_f"]["b"])) @ P(params["wte"]).T
    return (logits, hidden) if return_hidden else logits
