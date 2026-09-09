"""GPT-2 as a FabricPC predictive-coding graph (S0-06; DEC-002).

Nodes (all subclasses of ``fabricpc.nodes.base.NodeBase``; shapes exclude the batch axis):

* ``ids``      ``fabricpc.nodes.Linear(shape=(T,))`` source node clamped to int32 token ids;
* ``embed``    ``GPT2EmbedNode(shape=(T, d))``: ``z_mu = wte[ids] + wpe[:T]``; no free error
               (the sibling wrapper has no error on the embedding: hdpc/wrap.py:134-164);
* ``block_l``  ``GPT2BlockNode(shape=(T, d))`` for l = 0..11: ``z_mu = Block_l(x)``; the node's
               ``error = z_latent - z_mu`` **is** the ePC error variable e_l, and the default
               ``GaussianEnergy(precision=1)`` gives ``½Σ‖e_l‖²`` (sibling hdpc/energy.py:85-91);
               ``node_config["epc_free"] = True`` marks it as a free variable of the solver and
               ``node_config["bank"]`` marks the three cap sites (SD-7);
* ``logits``   ``GPT2HeadNode(shape=(T, V))``: ``z_mu = ln_f(x) @ wteᵀ`` with
               ``TokenCrossEntropyEnergy``: ``E = Σ_t Σ_v −y_tv · log_softmax(z_mu)_tv`` where the
               clamp ``y`` is a one-hot matrix whose rows are zero at positions without a target,
               so "current target only" (credit) and "declared positions" (report card) are the
               same energy with different clamps (PDF D.6).

``build_gpt2_graph`` assembles the chain and ``graph_params_from_numpy`` maps the HF weights
into ``GraphParams`` (the head shares the ``wte`` array object with the embedding: no copy).
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import jax
import jax.numpy as jnp
import numpy as np
from fabricpc.core.activations import IdentityActivation
from fabricpc.core.energy import EnergyFunctional, GaussianEnergy
from fabricpc.core.initializers import InitializerBase, NormalInitializer
from fabricpc.core.topology import Edge
from fabricpc.core.types import GraphParams, NodeInfo, NodeParams, NodeState
from fabricpc.graph_assembly import TaskMap, graph
from fabricpc.nodes import Linear
from fabricpc.nodes.base import NodeBase, SlotSpec

from pccap.bases import gpt2_jax as g

BLOCK_WEIGHTS = ["ln_1.g", "c_attn.w", "c_proj.w", "ln_2.g", "c_fc.w", "c_proj2.w"]
BLOCK_BIASES = ["ln_1.b", "c_attn.b", "c_proj.b", "ln_2.b", "c_fc.b", "c_proj2.b"]


def _single_input(inputs: Dict[str, jnp.ndarray]) -> jnp.ndarray:
    if len(inputs) != 1:
        raise ValueError(f"expected exactly one incoming edge, got {list(inputs)}")
    return next(iter(inputs.values()))


def _finish(state: NodeState, z_mu: jnp.ndarray, node_info: NodeInfo) -> NodeState:
    """Steps 2-5 of the NodeBase.forward contract."""
    state = state._replace(z_mu=z_mu, error=state.z_latent - z_mu)
    return node_info.node_class.energy_functional(state, node_info)


class TokenCrossEntropyEnergy(EnergyFunctional):
    """``E(y, z) = Σ_{t,v} −y_tv · log_softmax(z)_tv`` per sample; ``y`` = clamped one-hot targets
    with all-zero rows where no target is declared. Raw logits, ``logsumexp`` (no clipping)."""

    def __init__(self):
        super().__init__()

    @staticmethod
    def energy(z_latent, z_mu, config=None):
        logp = jax.nn.log_softmax(z_mu, axis=-1)
        return -jnp.sum(z_latent * logp, axis=tuple(range(1, z_mu.ndim)))

    @staticmethod
    def grad_latent(z_latent, z_mu, config=None):
        return -jax.nn.log_softmax(z_mu, axis=-1)


class GPT2EmbedNode(NodeBase):
    def __init__(self, shape: Tuple[int, int], name: str, vocab: int, n_pos: int):
        super().__init__(shape=shape, name=name, activation=IdentityActivation(), energy=GaussianEnergy(),
                         latent_init=NormalInitializer(std=0.0), weight_init=NormalInitializer(std=0.02),
                         vocab=vocab, n_pos=n_pos, epc_free=False)

    @staticmethod
    def get_slots() -> Dict[str, SlotSpec]:
        return {"in": SlotSpec(name="in", is_multi_input=False, is_variance_scalable=False)}

    @staticmethod
    def initialize_params(key, node_shape, input_shapes, weight_init, config) -> NodeParams:
        T, d = node_shape
        return NodeParams(weights={"wte": jnp.zeros((config["vocab"], d)), "wpe": jnp.zeros((config["n_pos"], d))},
                          biases={})

    @staticmethod
    def forward(params: NodeParams, inputs, state: NodeState, node_info: NodeInfo) -> NodeState:
        ids = _single_input(inputs).astype(jnp.int32)  # [B, T]
        T = node_info.shape[0]
        z_mu = params.weights["wte"][ids] + params.weights["wpe"][:T][None]
        return _finish(state, z_mu, node_info)


class GPT2BlockNode(NodeBase):
    def __init__(self, shape: Tuple[int, int], name: str, layer: int, cfg: g.GPT2Config, bank: int = 0):
        super().__init__(shape=shape, name=name, activation=IdentityActivation(), energy=GaussianEnergy(),
                         latent_init=NormalInitializer(std=0.0), weight_init=NormalInitializer(std=0.02),
                         layer=layer, bank=bank, epc_free=True, n_head=cfg.n_head, eps=cfg.eps)

    @staticmethod
    def get_slots() -> Dict[str, SlotSpec]:
        return {"in": SlotSpec(name="in", is_multi_input=False)}

    @staticmethod
    def initialize_params(key, node_shape, input_shapes, weight_init, config) -> NodeParams:
        T, d = node_shape
        shapes = {"ln_1.g": (d,), "c_attn.w": (d, 3 * d), "c_proj.w": (d, d), "ln_2.g": (d,),
                  "c_fc.w": (d, 4 * d), "c_proj2.w": (4 * d, d)}
        bshapes = {"ln_1.b": (d,), "c_attn.b": (3 * d,), "c_proj.b": (d,), "ln_2.b": (d,),
                   "c_fc.b": (4 * d,), "c_proj2.b": (d,)}
        return NodeParams(weights={k: jnp.zeros(s) for k, s in shapes.items()},
                          biases={k: jnp.zeros(s) for k, s in bshapes.items()})

    @staticmethod
    def block_params(params: NodeParams) -> dict:
        w, b = params.weights, params.biases
        return {"ln_1": {"g": w["ln_1.g"], "b": b["ln_1.b"]}, "c_attn": {"w": w["c_attn.w"], "b": b["c_attn.b"]},
                "c_proj": {"w": w["c_proj.w"], "b": b["c_proj.b"]}, "ln_2": {"g": w["ln_2.g"], "b": b["ln_2.b"]},
                "c_fc": {"w": w["c_fc.w"], "b": b["c_fc.b"]}, "c_proj2": {"w": w["c_proj2.w"], "b": b["c_proj2.b"]}}

    @staticmethod
    def forward(params: NodeParams, inputs, state: NodeState, node_info: NodeInfo) -> NodeState:
        x = _single_input(inputs)  # [B, T, d]
        cfg = g.GPT2Config(n_head=node_info.node_config["n_head"], d=x.shape[-1], eps=node_info.node_config["eps"])
        bp = GPT2BlockNode.block_params(params)
        z_mu = jax.vmap(lambda xs: g.block(bp, xs, cfg))(x)
        return _finish(state, z_mu, node_info)


class GPT2HeadNode(NodeBase):
    def __init__(self, shape: Tuple[int, int], name: str, eps: float):
        super().__init__(shape=shape, name=name, activation=IdentityActivation(), energy=TokenCrossEntropyEnergy(),
                         latent_init=NormalInitializer(std=0.0), weight_init=NormalInitializer(std=0.02),
                         eps=eps, epc_free=False)

    @staticmethod
    def get_slots() -> Dict[str, SlotSpec]:
        return {"in": SlotSpec(name="in", is_multi_input=False)}

    @staticmethod
    def initialize_params(key, node_shape, input_shapes, weight_init, config) -> NodeParams:
        T, V = node_shape
        d = next(iter(input_shapes.values()))[-1]
        return NodeParams(weights={"wte": jnp.zeros((V, d)), "ln_f.g": jnp.zeros((d,))}, biases={"ln_f.b": jnp.zeros((d,))})

    @staticmethod
    def forward(params: NodeParams, inputs, state: NodeState, node_info: NodeInfo) -> NodeState:
        x = _single_input(inputs)
        eps = node_info.node_config["eps"]
        # vmapped per sequence so the GEMM layout matches gpt2_jax.head exactly (SD-10)
        z_mu = jax.vmap(lambda xs: g.layer_norm(xs, params.weights["ln_f.g"], params.biases["ln_f.b"], eps)
                        @ params.weights["wte"].T)(x)
        return _finish(state, z_mu, node_info)


def node_names(n_layer: int) -> Dict[str, Any]:
    return {"ids": "ids", "embed": "embed", "blocks": [f"block_{l}" for l in range(n_layer)], "logits": "logits"}


def build_gpt2_graph(cfg: g.GPT2Config, T: int, inference) -> Any:
    """Chain ids -> embed -> block_0 -> ... -> block_11 -> logits as a FabricPC GraphStructure."""
    names = node_names(cfg.n_layer)
    ids = Linear(shape=(T,), name=names["ids"])
    embed = GPT2EmbedNode(shape=(T, cfg.d), name=names["embed"], vocab=cfg.vocab, n_pos=cfg.n_pos)
    blocks = [GPT2BlockNode(shape=(T, cfg.d), name=names["blocks"][l], layer=l, cfg=cfg, bank=g.BLOCK_BANK.get(l, 0))
              for l in range(cfg.n_layer)]
    head = GPT2HeadNode(shape=(T, cfg.vocab), name=names["logits"], eps=cfg.eps)
    nodes = [ids, embed, *blocks, head]
    edges = [Edge(source=ids, target=embed.slot("in"))]
    prev = embed
    for b in blocks:
        edges.append(Edge(source=prev, target=b.slot("in")))
        prev = b
    edges.append(Edge(source=prev, target=head.slot("in")))
    return graph(nodes=nodes, edges=edges, task_map=TaskMap(x=ids, y=head), inference=inference)


def graph_params_from_numpy(params_np: dict, cfg: g.GPT2Config, device: bool = True) -> GraphParams:
    conv = jnp.asarray if device else np.asarray
    names = node_names(cfg.n_layer)
    wte = conv(params_np["wte"])
    nodes = {
        names["ids"]: NodeParams(weights={}, biases={}),
        names["embed"]: NodeParams(weights={"wte": wte, "wpe": conv(params_np["wpe"])}, biases={}),
        names["logits"]: NodeParams(weights={"wte": wte, "ln_f.g": conv(params_np["ln_f"]["g"])},
                                    biases={"ln_f.b": conv(params_np["ln_f"]["b"])}),
    }
    for l, blk in enumerate(params_np["blocks"]):
        w = {"ln_1.g": blk["ln_1"]["g"], "c_attn.w": blk["c_attn"]["w"], "c_proj.w": blk["c_proj"]["w"],
             "ln_2.g": blk["ln_2"]["g"], "c_fc.w": blk["c_fc"]["w"], "c_proj2.w": blk["c_proj2"]["w"]}
        b = {"ln_1.b": blk["ln_1"]["b"], "c_attn.b": blk["c_attn"]["b"], "c_proj.b": blk["c_proj"]["b"],
             "ln_2.b": blk["ln_2"]["b"], "c_fc.b": blk["c_fc"]["b"], "c_proj2.b": blk["c_proj2"]["b"]}
        nodes[names["blocks"][l]] = NodeParams(weights={k: conv(v) for k, v in w.items()},
                                               biases={k: conv(v) for k, v in b.items()})
    return GraphParams(nodes=nodes)


__all__ = ["GPT2BlockNode", "GPT2EmbedNode", "GPT2HeadNode", "TokenCrossEntropyEnergy", "build_gpt2_graph",
           "graph_params_from_numpy", "node_names", "InitializerBase"]
