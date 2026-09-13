# FabricPC and pccap ePC survey for Stage 2/3 (read-only survey, 2026-09-13 evening)

Prepared by a read-only subagent for the orchestrator; file:line references were checked against the repositories.

## FabricPC is JAX
`FabricPC/pyproject.toml:30-38` (jax ≥ 0.7, optax, chex, jaxtyping). Model = nodes + edges + task map + inference
object. `NodeBase` (`fabricpc/nodes/base.py:156`) with `get_slots` (:286), `initialize_params` (:305), `forward` (:330);
per-node `NodeState(z_latent, z_mu, error, energy, latent_grad)`. Energies: `EnergyFunctional` (`core/energy.py:51`)
with static `energy` / `grad_latent`; `graph_energy` (`core/energy.py:459`) sums per-node energies. Settling:
`InferenceSGD(eta_infer, infer_steps, latent_decay)` (`core/inference.py:278`), a fixed `lax.fori_loop` of
`z -= eta·dE/dz`. Weight updates are block-local: `compute_local_weight_gradients` (`core/learning.py:6`) differentiates
each node's own energy w.r.t. its own params. Entry points: `graph(...)` (`graph_assembly/graph_construction.py:108`),
`initialize_params`, `train(..., algorithm="pc"|"backprop")` (`training/trainer.py:505`), `pc_weight_gradients` (:372).
User energy terms: subclass `EnergyFunctional` (pccap already does: `src/pccap/pc/nodes.py:57 TokenCrossEntropyEnergy`,
`src/pccap/pc/kd_energy.py:25 KDEnergy`).

## pccap ePC base
`EPCBase(BPBase)` (`src/pccap/bases/epc.py:38`): `infer_errors(ids, target, iters=8, writes=(), phase)` (:95) runs the
FabricPC graph built by `build_gpt2_graph` (`src/pccap/pc/nodes.py:167`) through `relax_errors`
(`src/pccap/pc/epc_inference.py:93`): errors are the free variables (zero-init; `iters` simultaneous SGD steps under
`lax.scan`), latents reconstructed as `z = z_mu + e_l`, cap writes added at position p after the error, sites read
pre-write. `ErrorResult` (`src/pccap/contracts.py:99-117`) carries `errors`, `site_errors`, `energies`, `grad_norm_0/k`,
`r_k`, `iters`, `logits`, `cost`, `solver`. Cost charged as `full_forwards=iters+1, reverses=iters+1,
settle_iters=iters`. `descent_sign=+1`: the settled site error points toward the target-conditioned state; v0's
`credit="error"` path uses `-sign·error_at_site(er, m)` as the write direction (`src/pccap/cap/learn.py:88-94`).

## Alternating ePC surrogate for the reader/controller (R1-22)
1. Error phase (no backprop through GPT-2): `er = base.infer_errors(ids, target, iters, writes=W(θ))`;
   surrogate `∂L/∂w_m := −descent_sign · error_at_site(er, m)`.
2. Controller phase: local loss `L_θ = Σ_m ⟨stop_grad(g_m), w_m(θ)⟩`, `jax.value_and_grad` w.r.t. θ only, optax step —
   the structure of `src/pccap/distill/train.py:99-123` (relax → detached errors → local energy → grad → optax).
Reusable pieces: `graph_energy`, `EnergyFunctional` subclassing, `core/learning.py:6` local gradients,
`src/pccap/pc/weight_phase.py:40` (float32-safe local form). Validate sign/monotonicity with `epc_sign_control`
(`epc.py:153`) and the `r_k` / `energies` fields.
