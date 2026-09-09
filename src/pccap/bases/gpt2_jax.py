"""GPT-2 small in JAX (S0-04; DEC-001). Functional core shared by the BP and ePC wrappers.

Architecture follows the HF ``GPT2LMHeadModel`` eager path exactly (pinned snapshot
``openai-community/gpt2`` @ ``607a30d7…``): learned absolute positions, pre-LN blocks,
fused ``c_attn`` Conv1D (``y = x @ W + b`` with ``W`` stored as ``[in, out]``), attention scores
divided by ``sqrt(head_dim)``, causal mask by ``where(mask, s, finfo.min)``, ``gelu_new`` (tanh
approximation), ``ln_f`` then tied ``wte`` head. No dropout path exists in this code.

Site convention (PDF F.1, SD-7): bank m reads the residual after block ``BANK_BLOCK[m]``
(HF ``transformer.h[l]`` output; for bank 3 this is before ``ln_f``) at position ``p = n-1``
and writes an additive vector there before the next block.

Every function here takes a single sequence ``ids [T]`` padded to a bucket length with the
true length ``n`` passed separately; the causal mask makes padded positions inert for the
first ``n`` positions. Writes are a dense ``[3, d]`` array (zero rows are exact no-ops in IEEE
arithmetic, which is what makes cap-off identity hold by construction; SD-10).
"""

from __future__ import annotations

import dataclasses
import functools
import json
import math
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
from jax import lax
from safetensors import safe_open

from pccap import ASSETS_ROOT

DEFAULT_SNAPSHOT = Path(ASSETS_ROOT) / "models" / "gpt2"
PINNED_REVISION = "607a30d783dfa663caf39e06633721c8d4cfcd7e"

BANK_BLOCK: dict[int, int] = {1: 3, 2: 7, 3: 11}  # SD-7: l_m = round(m*12/3) -> block index l_m - 1
BLOCK_BANK: dict[int, int] = {v: k for k, v in BANK_BLOCK.items()}
BUCKETS: tuple[int, ...] = (16, 32, 64, 128, 256, 512, 1024)


@dataclasses.dataclass(frozen=True)
class GPT2Config:
    n_layer: int = 12
    n_head: int = 12
    d: int = 768
    vocab: int = 50257
    n_pos: int = 1024
    eps: float = 1e-5

    @classmethod
    def from_snapshot(cls, snapshot: Path) -> "GPT2Config":
        c = json.loads((Path(snapshot) / "config.json").read_text())
        assert c["activation_function"] == "gelu_new", c["activation_function"]
        return cls(
            n_layer=c["n_layer"], n_head=c["n_head"], d=c["n_embd"], vocab=c["vocab_size"],
            n_pos=c["n_positions"], eps=c["layer_norm_epsilon"],
        )


PARAM_KEYS_BLOCK = [
    ("ln_1", "g", "ln_1.weight"), ("ln_1", "b", "ln_1.bias"),
    ("c_attn", "w", "attn.c_attn.weight"), ("c_attn", "b", "attn.c_attn.bias"),
    ("c_proj", "w", "attn.c_proj.weight"), ("c_proj", "b", "attn.c_proj.bias"),
    ("ln_2", "g", "ln_2.weight"), ("ln_2", "b", "ln_2.bias"),
    ("c_fc", "w", "mlp.c_fc.weight"), ("c_fc", "b", "mlp.c_fc.bias"),
    ("c_proj2", "w", "mlp.c_proj.weight"), ("c_proj2", "b", "mlp.c_proj.bias"),
]


def load_params_numpy(snapshot: Path = DEFAULT_SNAPSHOT, cfg: GPT2Config | None = None) -> dict:
    """Load the safetensors weights into a nested dict of float32 NumPy arrays (HF layout)."""
    snapshot = Path(snapshot)
    cfg = cfg or GPT2Config.from_snapshot(snapshot)
    with safe_open(str(snapshot / "model.safetensors"), "np") as f:
        keys = set(f.keys())

        def get(k):
            return np.ascontiguousarray(f.get_tensor(k).astype(np.float32))

        blocks = []
        for l in range(cfg.n_layer):
            blk: dict = {}
            for grp, sub, hf in PARAM_KEYS_BLOCK:
                blk.setdefault(grp, {})[sub] = get(f"h.{l}.{hf}")
            blocks.append(blk)
        params = {
            "wte": get("wte.weight"),
            "wpe": get("wpe.weight"),
            "ln_f": {"g": get("ln_f.weight"), "b": get("ln_f.bias")},
            "blocks": blocks,
        }
    assert "lm_head.weight" not in keys or np.array_equal(params["wte"], get("lm_head.weight"))
    return params


def flatten_named(params: dict) -> list[tuple[str, np.ndarray]]:
    """Deterministic (name, array) listing used by the checksum."""
    out = [("wte", params["wte"]), ("wpe", params["wpe"]), ("ln_f.g", params["ln_f"]["g"]),
           ("ln_f.b", params["ln_f"]["b"])]
    for l, blk in enumerate(params["blocks"]):
        for grp, sub, _ in PARAM_KEYS_BLOCK:
            out.append((f"h.{l}.{grp}.{sub}", blk[grp][sub]))
    return out


# ----------------------------------------------------------------------------- math


def layer_norm(x: jax.Array, g: jax.Array, b: jax.Array, eps: float) -> jax.Array:
    mu = jnp.mean(x, axis=-1, keepdims=True)
    var = jnp.mean(jnp.square(x - mu), axis=-1, keepdims=True)
    return (x - mu) / jnp.sqrt(var + eps) * g + b


def gelu_new(x: jax.Array) -> jax.Array:
    # HF gelu_new == 0.5 x (1 + tanh(sqrt(2/pi) (x + 0.044715 x^3)))
    return 0.5 * x * (1.0 + jnp.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * jnp.power(x, 3.0))))


def attention(p: dict, x: jax.Array, cfg: GPT2Config) -> jax.Array:
    T = x.shape[0]
    hd = cfg.d // cfg.n_head
    qkv = x @ p["c_attn"]["w"] + p["c_attn"]["b"]
    q, k, v = jnp.split(qkv, 3, axis=-1)
    q = q.reshape(T, cfg.n_head, hd).transpose(1, 0, 2)
    k = k.reshape(T, cfg.n_head, hd).transpose(1, 0, 2)
    v = v.reshape(T, cfg.n_head, hd).transpose(1, 0, 2)
    s = jnp.einsum("hqd,hkd->hqk", q, k) / math.sqrt(hd)
    mask = jnp.tril(jnp.ones((T, T), dtype=bool))
    s = jnp.where(mask, s, jnp.finfo(s.dtype).min)
    a = jax.nn.softmax(s, axis=-1)
    o = jnp.einsum("hqk,hkd->hqd", a, v).transpose(1, 0, 2).reshape(T, cfg.d)
    return o @ p["c_proj"]["w"] + p["c_proj"]["b"]


def mlp(p: dict, x: jax.Array) -> jax.Array:
    h = gelu_new(x @ p["c_fc"]["w"] + p["c_fc"]["b"])
    return h @ p["c_proj2"]["w"] + p["c_proj2"]["b"]


def block(p: dict, x: jax.Array, cfg: GPT2Config) -> jax.Array:
    x = x + attention(p, layer_norm(x, p["ln_1"]["g"], p["ln_1"]["b"], cfg.eps), cfg)
    x = x + mlp(p, layer_norm(x, p["ln_2"]["g"], p["ln_2"]["b"], cfg.eps))
    return x


def embed(params: dict, ids: jax.Array) -> jax.Array:
    T = ids.shape[0]
    return params["wte"][ids] + params["wpe"][:T]


def head(params: dict, h: jax.Array, cfg: GPT2Config) -> jax.Array:
    return layer_norm(h, params["ln_f"]["g"], params["ln_f"]["b"], cfg.eps) @ params["wte"].T


def run_blocks(params: dict, h: jax.Array, p: jax.Array, writes: jax.Array, cfg: GPT2Config,
               start_block: int, errors: list[jax.Array] | None = None):
    """Blocks ``start_block..n_layer-1`` on residual ``h [T,d]``.

    At each bank site the pre-write residual row at position ``p`` and the full pre-write
    residual are recorded, then ``writes[m-1]`` is added at ``p``. ``errors`` (ePC) are added to
    every block output *before* the site is read (they are part of the base computation);
    ``errors[l]`` has shape ``[T, d]``.
    Returns ``(h, site_rows, site_full)``.
    """
    site_rows: dict[int, jax.Array] = {}
    site_full: dict[int, jax.Array] = {}
    for l in range(start_block, cfg.n_layer):
        h = block(params["blocks"][l], h, cfg)
        if errors is not None:
            h = h + errors[l]
        m = BLOCK_BANK.get(l)
        if m is not None:
            row = lax.dynamic_index_in_dim(h, p, axis=0, keepdims=False)
            site_rows[m] = row
            site_full[m] = h
            h = lax.dynamic_update_index_in_dim(h, row + writes[m - 1], p, axis=0)
    return h, site_rows, site_full


@functools.partial(jax.jit, static_argnames=("cfg", "retain"))
def forward_jit(params: dict, ids: jax.Array, n: jax.Array, writes: jax.Array, cfg: GPT2Config,
                retain: bool):
    p = n - 1
    h = embed(params, ids)
    h, rows, full = run_blocks(params, h, p, writes, cfg, 0)
    logits = head(params, h, cfg)
    return logits, rows, (full if retain else {})


@functools.partial(jax.jit, static_argnames=("cfg", "bank", "retain"))
def forward_from_jit(params: dict, hidden: jax.Array, n: jax.Array, writes: jax.Array,
                     cfg: GPT2Config, bank: int, retain: bool = False):
    """Resume after bank ``bank``'s site. ``hidden`` is the *pre-write* residual at that site;
    this applies ``writes[bank-1]`` at ``p`` and every later bank's write downstream.
    ``retain`` also returns the full pre-write residual of every later site."""
    p = n - 1
    row = lax.dynamic_index_in_dim(hidden, p, axis=0, keepdims=False)
    h = lax.dynamic_update_index_in_dim(hidden, row + writes[bank - 1], p, axis=0)
    h, rows, full = run_blocks(params, h, p, writes, cfg, BANK_BLOCK[bank] + 1)
    rows[bank] = row
    full[bank] = hidden
    logits = head(params, h, cfg)
    return logits, rows, (full if retain else {})


def loss_at(logits: jax.Array, p: jax.Array, target: jax.Array) -> jax.Array:
    row = lax.dynamic_index_in_dim(logits, p, axis=0, keepdims=False)
    return jax.nn.logsumexp(row) - row[target]


@functools.partial(jax.jit, static_argnames=("cfg",))
def adjoint_jit(params: dict, ids: jax.Array, n: jax.Array, writes: jax.Array, target: jax.Array,
                cfg: GPT2Config):
    """One reverse pass: ``dL/d(writes)`` = ``dL/dh_p`` at every site (post-write residual)."""
    p = n - 1

    def loss_fn(w):
        h = embed(params, ids)
        h, rows, _ = run_blocks(params, h, p, w, cfg, 0)
        logits = head(params, h, cfg)
        return loss_at(logits, p, target), (logits, rows)

    (loss, (logits, rows)), g = jax.value_and_grad(loss_fn, has_aux=True)(writes)
    return loss, g, logits, rows


def bucket_len(n: int, buckets: tuple[int, ...] = BUCKETS) -> int:
    for b in buckets:
        if n <= b:
            return b
    raise ValueError(f"sequence length {n} exceeds the largest bucket {buckets[-1]}")


def pad_ids(ids: np.ndarray, T: int, pad_id: int = 50256) -> np.ndarray:
    out = np.full((T,), pad_id, dtype=np.int32)
    out[: len(ids)] = ids
    return out


def to_device(params_np: dict) -> dict:
    return jax.tree_util.tree_map(jnp.asarray, params_np)


def load_tokenizer(snapshot: Path = DEFAULT_SNAPSHOT):
    from tokenizers import Tokenizer

    return Tokenizer.from_file(str(Path(snapshot) / "tokenizer.json"))


def save_params_npz(params_np: dict, path: Path) -> str:
    """Write the nested param dict as an ``.npz`` of ``flatten_named`` entries; returns sha256."""
    import hashlib

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(path, **{k: np.asarray(v, np.float32) for k, v in flatten_named(params_np)})
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_params_npz(path: Path) -> dict:
    """Inverse of ``save_params_npz`` (used by REG-03 to load a distilled checkpoint by path)."""
    z = np.load(Path(path))
    n_layer = 1 + max(int(k.split(".")[1]) for k in z.files if k.startswith("h."))
    blocks = []
    for l in range(n_layer):
        blk: dict = {}
        for grp, sub, _ in PARAM_KEYS_BLOCK:
            blk.setdefault(grp, {})[sub] = z[f"h.{l}.{grp}.{sub}"]
        blocks.append(blk)
    return {"wte": z["wte"], "wpe": z["wpe"], "ln_f": {"g": z["ln_f.g"], "b": z["ln_f.b"]}, "blocks": blocks}


def _last_row_logits(params: dict, ids: jax.Array, n: jax.Array, cfg: GPT2Config) -> jax.Array:
    """Logits at position p = n-1 only (no writes); the head projects one row."""
    p = n - 1
    h = embed(params, ids)
    h, _, _ = run_blocks(params, h, p, jnp.zeros((3, cfg.d), jnp.float32), cfg, 0)
    row = lax.dynamic_index_in_dim(h, p, axis=0, keepdims=False)
    return layer_norm(row, params["ln_f"]["g"], params["ln_f"]["b"], cfg.eps) @ params["wte"].T


@functools.partial(jax.jit, static_argnames=("cfg",))
def last_logits_batch_jit(params: dict, ids: jax.Array, n: jax.Array, cfg: GPT2Config) -> jax.Array:
    """Batched cap-off last-position logits ``[B, V]`` for padded ``ids [B, T]`` with lengths ``n [B]``.
    Used for bulk teacher generation (DATA-01 selection); the reference decoder stays single-sequence."""
    return jax.vmap(lambda i, k: _last_row_logits(params, i, k, cfg))(ids, n)


def _all_hidden(params: dict, ids: jax.Array, cfg: GPT2Config) -> jax.Array:
    """Residual stream at every layer boundary: ``[n_layer+1, T, d]`` (row 0 = embedding output,
    row l+1 = block l output, the last before ``ln_f``). Cap-off."""
    h = embed(params, ids)
    hs = [h]
    for l in range(cfg.n_layer):
        h = block(params["blocks"][l], h, cfg)
        hs.append(h)
    return jnp.stack(hs)


@functools.partial(jax.jit, static_argnames=("cfg",))
def all_hidden_batch_jit(params: dict, ids: jax.Array, cfg: GPT2Config) -> jax.Array:
    """``[B, n_layer+1, T, d]`` for padded ``ids [B, T]`` (positions beyond each sequence's length
    are causally inert; the caller masks them)."""
    return jax.vmap(lambda i: _all_hidden(params, i, cfg))(ids)


def _seq_loss_with_errors(params: dict, errors: jax.Array, ids: jax.Array, targets: jax.Array, mask: jax.Array, cfg: GPT2Config):
    """Summed next-token CE over ``mask`` positions with zero 'errors' ``[n_layer, T, d]`` added at
    every block output; the gradient w.r.t. ``errors`` is the adjoint field of D.3."""
    h = embed(params, ids)
    for l in range(cfg.n_layer):
        h = block(params["blocks"][l], h, cfg) + errors[l]
    logits = head(params, h, cfg)
    lp = jax.nn.log_softmax(logits, axis=-1)
    nll = -jnp.take_along_axis(lp, targets[:, None], axis=-1)[:, 0]
    return jnp.sum(nll * mask)


@functools.partial(jax.jit, static_argnames=("cfg",))
def seq_adjoint_all_layers_jit(params: dict, ids: jax.Array, targets: jax.Array, mask: jax.Array, cfg: GPT2Config):
    """Adjoint of the summed sequence loss at every block output and position: ``[n_layer, T, d]``
    plus the loss. One reverse pass per sequence (vmapped over a batch)."""

    def one(i, t, m):
        e0 = jnp.zeros((cfg.n_layer, i.shape[0], cfg.d), jnp.float32)
        loss, g = jax.value_and_grad(_seq_loss_with_errors, argnums=1)(params, e0, i, t, m, cfg)
        return loss, g

    return jax.vmap(one)(ids, targets, mask)
