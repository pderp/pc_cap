# R1-30a — Stage 3 cap-level predictive-coding design draft

Codex, 2026-09-14. **Specification only; no implementation, new experiment allocation, or launch authorization.** This supplements [plan 9, Stage 3](updated_plan9.md) using the [current read path](revision_v1_design.md) and [FabricPC survey](../logs/fabricpc_survey.md). Proposed changes to the plan's architecture or comparison policy require the lead's decision before implementation.

## Research question and present gate

Can a small target-free latent solve improve selection of a stored edit and its applicability to a new question, enough to improve full-answer transfer while preserving locality? Lower energy is a mechanism diagnostic; better answers under the same memory, write bound and information budget are the scientific endpoint.

D-R5 makes Stage 3 conditional on a working Stage 1–2 feedforward cap. The random tied-reader/delta reference works on one zsRE development stream; CounterFact locality and learned-null transfer remain unresolved. The Stage 2 review is [R1-X4](../logs/review_r1_stage2.md). Preparing this specification is useful now. Beginning another training campaign is conditional, and skipping Stage 3 remains consistent with plan 9.

## The current architecture changes where settling can help

Each active memory record holds a stable observation-derived key, a code and a taught delta tensor `D_j[t, bank, width]`. The delta is indexed by answer position. A tied reader retrieves records from the original prompt, fixes one selection/null decision for that whole question, and the bounded delta replaces the code-driven controller write when present. The base and reusable cap weights remain frozen during stream adaptation/evaluation.

Consequently, **settling only the code-controller latents while holding the chosen record and delta fixed cannot change that record's answer-position writes**. A solver attached to an unused controller branch could show declining energy with no route to the measured answer. The initial Stage 3 experiment must expose its causal connection to selection or to an explicitly new write path.

Proposed first branch: settle a small record/selection state over a **fixed candidate set**, then choose a record/null once and use the existing per-position delta path. Candidate membership is frozen inside a query's solve; reranking within that set may change. This declares a departure from interpreting “same gated decoder” as fixing the chosen record itself. It preserves the existing support update and write mechanism.

A second, separate branch could learn a bounded residual on top of a selected delta. It would change the write path, byte/parameter/compute comparison and gradient conditioning. It is not part of this first proposal. In particular, do not silently reintroduce the large raw controller output that previously overwhelmed the delta before projection.

## Inputs, state and read sequence

| Object | Lifetime | Mutation permitted |
| --- | --- | --- |
| Base parameters, cap parameters, encoder/version/calibration identities | Entire evaluation stream | None |
| Record keys, codes, delta arrays, versions and active/retired flags | Persistent support memory | Only a support update or explicit reviewed rebuild |
| Original prompt token IDs/mask and write-free tapped observation | One independent query | None during settling |
| Deterministic top-k candidate IDs, keys/codes/deltas and eligibility mask | One independent query | No membership changes inside settling |
| Width-256 latents z1, z2; node predictions/errors/gradients; latent optimizer state | One independent query | Solver only; never exported as persistent fast state |
| Final chosen record/null, prompt length and query trace | All answer positions for one query | Fixed until the query ends |
| Per-position write and base activation caches | One decode step / declared cache lifetime | Recomputed from the frozen selection and current causal prefix |
| Cost counters | Whole run | Accumulate all work, including failures and discarded clones |

Read procedure:

1. Start an explicit query boundary. Clear prior selection, all latents, latent optimizer state and cached masks. A new question whose tokens extend another question's prompt is still a new boundary.
2. Take the usual write-free prompt observation at the current taps; charge its full-base forward. Encode q, retrieve top-k by the declared stable metric, deterministic tie rules and version checks. Store an immutable candidate snapshot and optional null candidate. No support-answer or query-label container is passed into this operation.
3. Initialize z1 and z2 at the feedforward values. Copy the initial values needed by the residual routing head. Build the FabricPC graph state and clamps from the query observation and candidate snapshot.
4. Refine for exactly T in {0, 1, 4, 8} steps. Observations, candidates, base parameters, reusable weights and persistent records stay fixed. No full-base forward/reverse or support adaptation occurs inside this loop.
5. Read the routing/null output from the terminal state. Apply the declared gate and deterministic hard selection once. Keep this decision for every generated token. For T=0, require exact equivalence to the chosen feedforward baseline, including ties, threshold boundaries and empty memory.
6. Decode with the common stopping rules and max length. At answer position t, apply only the selected record's bounded delta D_j[t]. Retain the current behavior beyond its taught delta length; do not silently extrapolate the last write. Hard null/empty memory produces exact zero writes and cap-off logits.
7. Record the complete trace, discard all transient latent state, and reset before the next independent prompt. Export/state hashes must show no persistent change from any query.

Training supports may contain answers, and stored fast state may encode them: that is the intended editing mechanism. **Held-out query labels** must never enter the prediction solve, its initialization, its iteration budget or its stopping decision.

## Energy and routing: explicit candidate specification

Start from the plan's form, with width-normalized terms rather than an unspecified sum:

```text
E(z1,z2 ; q,C,o,theta)
  = alpha/(2d1) || z1 - f1_theta(q,C) ||^2
  + beta /(2d2) || z2 - f2_theta(z1)  ||^2
  + lambda/2 sum_m [ || g_m_theta(z2,C) - stopgrad(o_m) ||^2 / d_m ].
```

Here C is the frozen masked candidate representation. Observations o are write-free prompt features; g predicts those features, not the actual applied delta. All alpha/beta/lambda, feature normalization, padding masks and whether the tap sum is averaged must be recorded in the eventual configuration. Disable implicit muPC scaling initially or bind the exact scaling configuration and verify it explicitly.

This energy is not guaranteed to help retrieval. At feedforward initialization, the first two residuals vanish. The observation term must supply a nontrivial, memory-dependent gradient. If g reconstructs the observation exactly, or ignores the candidates, the solver can be stationary or irrelevant. Include an explicit zero-residual control and a toy that changes its optimum when the relevant memory is altered. Do not add an answer target to prediction merely to make inference nontrivial.

A concrete route head for development is:

```text
routing_logits_T = baseline_logits(q,C)
                 + rho * bounded[h_theta(z2_T,C) - h_theta(z2_0,C)].
```

The subtraction makes the residual zero at T=0 and allows an exact same-checkpoint feedforward comparison. Specify the residual bound and unit: a cosine margin, temperature-scaled logit and a probability are different quantities. Never compare a modified score to the old 0.93 cosine threshold as though it remained a calibrated cosine.

Initially retain the fixed cosine gate as an explicit reference policy. One conservative route-only condition can mask records below the **original cosine** eligibility threshold before the final reranking. Match the baseline's strictness and tie behavior exactly at threshold equality. A learnable null-logit residual is a **separate condition**: its calibration must be evaluated independently and cannot inherit the Stage 2 fallback's locality claim. Both conditions retain an explicit empty-memory/null state with zero writes.

The route-only branch cannot retrieve a supporting record absent from the initial top-k set. Report candidate recall separately from reranking and null errors; changing k is a new cost/selection condition. Hard top-1 deployment is nondifferentiable. During training either use a declared soft routing relaxation through bounded candidate writes or a named surrogate; disclose the soft/hard mismatch and evaluate hard selection. Do not present a straight-through estimator as the exact derivative of hard argmax.

## Answer-objective coupling (X0-07)

The outer training loss must include query-answer cross-entropy and preservation, not only feature reconstruction or energy descent:

```text
L(theta) = L_answer(base_read(q, selected_or_relaxed_D(z_T)))
         + w_keep L_preserve(original_base, adapted_read)
         + w_route L_support_selection
         + w_reg L_declared_regularization.
```

Support adaptation constructs memory first. Query targets enter only these training losses, outside the target-free inference energy and prediction API. For the initial finite-T BP reference, differentiate through the small latent iterations and the declared soft routing relaxation; the frozen base can supply the answer gradient at the final read without any base pass inside the latent loop. Verify that the answer-gradient path actually reaches the energy/routing parameters. Report zero/near-zero gradients and effects of hard nulls, bounds and saturation.

FabricPC local weight gradients of node energy at a detached terminal state are **a different estimator** from differentiating the outer answer loss through T steps. They cannot be substituted without adding and documenting how answer supervision influences the training-phase state/energy, where it is clamped, what is detached, and how the final local update is formed. If a training-only answer-coupled phase calls the base per iteration, count that additional training work and name the condition separately. Prediction remains target-free. Stage 2's base ePC surrogate and Stage 3's cap-latent inference are also distinct mechanisms.

Run three training-gradient gates before a real experiment: finite differences for a smooth tiny problem, nonzero answer-to-routing/energy gradients under a positive control, and held-out-label permutation invariance for the prediction solve. Reconstruction-energy improvement without answer improvement is an informative negative, not an endpoint substitute.

## FabricPC integration without sibling edits

The current local [NodeBase implementation](/home/derp/cap/FabricPC/fabricpc/nodes/base.py) supplies pure JAX node forwards and autodiff latent/weight gradients. NodeState is the fixed tuple `z_latent, z_mu, error, energy, latent_grad`; a node computes its prediction first, sets the error as latent minus prediction, then fills per-sample energy. Create project-specific node/energy classes under pc_cap when implementation is authorized. Do not add fields or modify FabricPC.

Use [EnergyFunctional](/home/derp/cap/FabricPC/fabricpc/core/energy.py) for the explicit residual/observation terms, [InferenceSGD](/home/derp/cap/FabricPC/fabricpc/core/inference.py) for bounded fixed-step updates, and [compute_local_weight_gradients](/home/derp/cap/FabricPC/fabricpc/core/learning.py) only for the separately declared local estimator. InferenceSGD runs a fixed `lax.fori_loop`; graph/node arrays can be padded to a fixed k with strict masks. No dynamic retrieval or token decoding belongs inside that compiled solver.

**Terminal-node trap:** NodeBase's default evaluation behavior for an unclamped output with no successors copies its prediction into its latent and zeros its energy/gradients. A leaf node intended to contribute a nonzero observation/relevance energy can therefore silently contribute nothing. Represent the observed feature target as a genuinely clamped observed sink, connected to the selection latents, or implement/review a custom gradient method with an explicit test. Clamping a write-free input observation is allowed; clamping a held-out answer at prediction is not. Source/input nodes are also treated specially, so merely attaching an energy object to a disconnected latent does not define the intended optimization.

Record FabricPC commit and file hashes in any eventual run, together with node topology, clamps, scaling and dtype. Reuse installed JAX/FabricPC infrastructure; do not install an alternative environment or introduce PyTorch.

## Solver contract and failure handling

Use float32 latent arrays, an explicit initialization seed if any, fixed inference step size and fixed T. Start with zero latent momentum/decay. If gradient clipping, damping, projection or decay is later introduced, report it as part of the solver; the residual logged must correspond to the actual declared energy and constraints.

Log E at initialization and every step, each energy component, gradient norm, latent displacement, valid candidate count and terminal selection margin. A fixed SGD step is not guaranteed to decrease a nonconvex energy monotonically; check the quadratic stability bound in the toy and report increases in real runs rather than suppressing them.

On nonfinite energy/gradient/state, stop this query, reset transient state and return an explicit resource/numerical status under the chosen endpoint policy. Charge attempted work. Do not silently replace a failed T>0 solve with T=0 and report the result as a successful settled query. A separately reported fallback policy may be operationally useful, but is a distinct condition.

The transient solver may not mutate reusable weights, stored deltas, keys, record activity or the encoder version. Snapshot restoration and exception paths must preserve these invariants. Support updates continue to use atomic admission and capacity rollback. Any index rebuild is a support/maintenance operation with separate cost, never a query side effect.

## Controls and acceptance checkpoints

| Checkpoint | Experiment/test | Required evidence |
| --- | --- | --- |
| S3-A | Positive-definite quadratic energy with analytic optimum | T=0 exact initializer; finite-T deterministic path; gradient finite differences; convergent stable-step behavior |
| S3-B | Target-free prediction and state boundaries | Permuting/removing held-out labels changes no predictions or traces; prefix-related independent queries reset; persistent hashes unchanged |
| S3-C | Topology and memory sensitivity | Clamped observation energy contributes gradients; removing/shuffling relevant memory changes the intended route; no masked/padded record leakage |
| S3-D | Exact baseline parity | Same checkpoint/config at T=0 matches the baseline's selection, gate, writes and logits, including threshold/tie/empty-memory cases |
| S3-E | Answer-gradient coupling | Smooth tiny training loss has checked gradients through the latent solve and final answer read; reconstruction-only negative control reported |
| S3-F | Matched controls | Same cap/checkpoint T=0/1/4/8; independently trained parameter-matched feedforward cap; recurrent controller with measured comparable compute |
| S3-G | Resources | Actual full/partial-base calls independent of T at fixed decode length; explicit cap-solver iterations/work; all failed work billed; real persistent bytes and transient peak reported |
| S3-H | Behavioral gate | Planted acquisition, unseen formulation, near-miss, older unrelated fact and revision; then both natural development datasets with full-answer endpoints |
| S3-I | Evidence decision | Paired gains with ES/LS/drift constraints and declared uncertainty; if only energy improves, reconsider the energy or stop Stage 3 |

Parameter matching includes energy encoders, route heads and any extra decoder; report exact totals and persistent weight bytes against the 5 M / 64 MiB policies. The independently trained feedforward comparator is not interchangeable with zero-step inference using a model trained for T=8. The recurrent comparator must receive the same candidates/features, memory and labels and have comparable measured cap FLOPs/time; matching iteration counts alone is insufficient.

At prediction, charge observation/retrieval, every latent step and the final corrected base pass separately. Compare base calls at fixed decode length because different answers can otherwise change generation cost. At training, distinguish base answer-gradient work, solver differentiation, support adaptation and optimizer state. R1-X4 showed why a reconciled ledger can still omit real work.

## Implementation work breakdown and concurrency

1. **Lead/design review (CPU):** accept or reject route-latent scope; specify fixed-gate versus learned-null conditions, candidate k, normalization, bounds, training estimator and provisional development thresholds. Resolve the changed coupling relative to plan 9 before writing pc_cap.py.
2. **Toy/solver lane (CPU, new files):** analytic quadratic, FabricPC topology/clamp tests, T=0 semantics, deterministic fixed-step loop and numerical-status traces. Independent of real-base training.
3. **Adapter lane (CPU, after the contract):** query boundary wrapper, immutable candidate snapshot, one-selection-per-answer integration, zero-step/delta parity and resource rollback tests. Coordinate shared learner edits with its owner.
4. **Loss/control lane (CPU, after the contract):** tiny smooth soft-routing objective, finite differences, hard/soft comparison and feedforward/recurrent control specifications. Can run alongside the adapter lane once interfaces are fixed.
5. **Accounting/report lane (CPU):** ledger schema, per-query latent trace, exact parameter/byte totals, endpoint integration and analysis templates. Can begin from this specification.
6. **Owner GPU smoke:** only after S3-A…G pass and D-R5 is accepted; profile one frozen-base condition, check exact counts and endpoint invariants before any sweep.
7. **Owner comparative development runs:** T controls, both datasets, fixed order/seed inventory, paired analyses and declared negative outcomes. No fresh realization is used to tune.
8. **Lead Stage 4 decision:** retain, revise or skip Stage 3; freeze all chosen architecture/solver/threshold choices and code identities before confirmatory execution.

The optional approximately three-hour Stage 3 budget in plan 9 is a planning estimate, not a new grant or a measured runtime for this revised design. No lane above takes the GPU while the current Stage 2 work is active.
