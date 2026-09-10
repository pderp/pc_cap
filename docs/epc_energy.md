# Declared ePC energy, solver and conventions (S0-06)

Recorded 2026-09-09 from the implementation in `src/pccap/pc/{nodes,epc_inference}.py` and
`src/pccap/bases/epc.py` (built on FabricPC 0.5.2, DEC-002), reproducing the sibling's
definitions (`llm-by-neural-predictive-coding` @ `298fc719`, read-only, DEC-003). This is the
"complete energy" PDF D.6 asks S0 to record; every ePC arm uses it unchanged. Any change is an
explicit experiment with a logged comparison (PDF F.6).

## Error sites

One error tensor `e_l ∈ ℝ^{T×d}` per transformer block `l = 0..11`, added to the block's output
residual (post-attention, post-MLP, i.e. the residual stream entering the next block); for
`l = 11` the error is added **before `ln_f`**. No error on the embedding, none between attention
and MLP. (Sibling `hdpc/wrap.py:134-164`; ours: `GPT2BlockNode` with `epc_free=True`, `GPT2EmbedNode`
with `epc_free=False`.) The three cap sites (SD-7) are the error sites of blocks 3, 7, 11 at
position `p`; cap writes are added at `p` *after* the error and the site is read *before* the
write (PDF F.1).

## Energy

```
E(e; x, y) = ½ Σ_{l=0}^{11} ‖e_l‖²_F  +  γ · Σ_t Σ_v −y_{t,v} · log softmax(f(x; e))_{t,v},   γ = 1
```

* Errors, states and logits in **float32**. Identity precision (no precision matrices, no
  per-layer weights, no boundary terms). Sums, not means. (Sibling `hdpc/energy.py:85-97`: the
  quadratic term is `0.5·Σ‖ε_i‖²` over all blocks; its task loss for distillation is KD at
  temperature 2, which we replace by cross-entropy per PDF D.6 — the distillation objective is
  a REG concern, not the credit energy.)
* The clamp `y` is a one-hot matrix `[T, V]` on the FabricPC `logits` node with all-zero rows
  where no target is declared. **Token-credit calls** clamp only row `p` (the current target;
  PDF D.6 "only the current prediction target enters"); **report-card calls** clamp every
  declared position (`target` = int array with `−1` = none), giving the declared summed
  sequence loss of D.3.
* **Unclamped variant** (`target=None`): no `logits` clamp; following FabricPC's evaluation
  rule an unclamped output node contributes zero energy, so `E = ½Σ‖e‖²`, whose minimizer from
  zero init is `e = 0`: the result equals the feedforward computation. Reported as a
  consistency check, not as inference (PDF D.1).
* Padded positions (`t ≥ n` in the sequence bucket) carry zero clamp rows and are causally
  inert; their errors stay at zero.
* Cap retrieval choices are frozen within a call: writes enter `derive_states` as a fixed
  `[3, d]` array (test `test_writes_enter_the_energy`).

In FabricPC terms: `E = graph_energy(state, structure)` where each block node's
`GaussianEnergy(precision=1)` supplies `½Σ‖e_l‖²` and the head node's
`TokenCrossEntropyEnergy` supplies the CE term.

## Solver

* Variables: the 12 error tensors. Weights never receive a gradient: `jax.value_and_grad` is
  taken of `energy_of(errors)` whose only argument is the error pytree (`relax_errors`).
* Initialization: **zeros on every call**; no state carried between calls or examples.
* Update: simultaneous plain gradient descent on all errors,
  `e ← e − η ∂E/∂e`, `η = error_lr = 0.1`. No momentum, no Adam, no line search, no clipping.
  (Sibling `hdpc/relax.py:26-120`.)
* Iterations: fixed count, **no stopping rule**. Nominal credit horizon `k = 8`; reference
  horizon `64` (PDF D.6). Each iteration = one derive (forward) + one reverse.
* Terminal residual: `E_k` and `‖∇_e E_k‖` are evaluated **explicitly at the terminal iterate**
  (one extra forward + reverse), so `r_k = ‖∇E_k‖ / max(1, ‖∇E_0‖)` is not the pre-update norm.
  Charged: `full_forwards = reverses = k + 1`, `settle_iters = k`. (The plan's S0-06(e) line
  "8 forwards and 8 reverses for iters=8" omits this required evaluation; we charge it.)
* Descent sign for credit: the settled error `e` at a site is the direction from the
  feedforward state toward the target-conditioned state (at a stationary point
  `e = −∂CE/∂h`), so the transport uses `+e/‖e‖` (`EPCBase.descent_sign = +1`). Verified once on
  the analytic control `E = ½‖e‖² + (w·(h+e) − y)²`: `+e` reduces the task loss, `−e` increases
  it, `cos(e, −∇_h loss) = 0.99999994` (`results/S0/controls/epc_sign_convention.json`). Never
  flipped per example.
* Label: **"finite-iteration error credit"** unless S1-06 finds `r_64 ≤ 1e-3` with small
  terminal changes. On BP teacher weights at `k = 8`, `η = 0.1`: `r_8 ≈ 0.2–0.4` on the 16
  development prompts (`results/S0/controls/s0_06_energy_descent.json`); energy was
  non-increasing on all 16.

## Production checkpoint regime (for the record)

The sibling's 50M-token distillation ran a homotopy of relaxation horizons
`T ∈ {1, 2, 4, 8, 16, 32, 64}` (τ = 0.1·T, terminal τ = 6.4) with this same solver and
`error_lr = 0.1`, updating weights from settled errors by a local per-block energy
(`hdpc/train_distill.py` `run_step`, `homotopy.py`; DEC-006). Its `summary.json`
`relaxation_steps = 1` is an unused default. The nominal 8-step credit is therefore a horizon
the checkpoint saw during training, but not its terminal one; S1-06 measures, nothing assumes.

## REG-00: the training recipe on the same graph (DEC-014)

The regeneration driver (`pccap.distill.train`) reuses the graph and solver above with two
additions, both FabricPC-shaped:

* `pccap.pc.kd_energy.KDEnergy(beta)` — the head node's `EnergyFunctional` during distillation:
  the clamp on `logits` holds the *teacher* logits and the per-sample energy is
  `β²·mean_t KL(softmax(y/β) ‖ softmax(z/β))` (sibling `kd_kl_loss`, hdpc/energy.py:34-53, times
  the micro-batch size so that `graph_energy`'s per-sample sum equals the sibling's scaled loss).
  Relaxation is then exactly `relax_errors` with this energy: `Σ_l ½‖e_l‖² + KD`.
* `pccap.pc.weight_phase.local_weight_energy` — the weight-phase objective: the same node
  `forward`s with every error-bearing node's input detached and target `stop(z_mu + e)`, so the
  Gaussian node energy `½‖z_latent − z_mu‖²` has gradient `−J_lᵀ e_l` in block `l`'s parameters
  (sibling `local_prediction_pairs` / `local_weight_energy`, hdpc/wrap.py:166-186,
  energy.py:130-162); the embedding is not detached (wte/wpe receive block 0's term) and the
  head sees a detached input (KD reaches ln_f and the tied wte only).

**Float32 note (REG-01 dissection).** GPT-2's residual stream is O(10–10³), so any form that adds a
small error to an activation and subtracts the activation again loses the error
(`(z_mu + e) − z_mu = 0` for |e| < ulp(z_mu) ≈ 1e-6 at z_mu ≈ 10). Two places are therefore written
in the exact order: the free-node weight-phase energy is `½‖(z_mu − stop(z_mu)) − e‖²` (the
sibling's `pred − pred.detach() − err`), and `derive_states` keeps the node error equal to the
free variable `e` rather than recomputing `z_latent − z_mu`. The forward itself still uses
`z_mu + e` (rounded exactly as the sibling's `pred + err`).

Micro-batching is exact because both energies are per-sample sums; `tests/distill/` checks the
FabricPC path against an independent plain-JAX implementation of the sibling's formulas.

## Dtypes, determinism, memory

fp32 throughout; matmul precision `highest` (TF32 off, DEC-007); `--xla_gpu_deterministic_ops`.
The reverse over the derive stores activations for all 12 blocks (backprop-scale memory);
batch = 1 sequence per call, sequences padded to bucket lengths `{16, …, 1024}`.

## Identity checks (S0-06 test (a))

Zero errors through the FabricPC graph vs the plain JAX forward on BP weights: site rows
bit-exact (`max |Δ| = 0`); logits see `results/S0/controls/s0_06_zero_error_identity.json`.
Unclamped inference with zero init reproduces the feedforward logits and leaves all errors at
exactly zero.
