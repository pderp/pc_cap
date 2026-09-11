# B4-D: localization of the first GRACE gradient difference

Codex, 2026-09-11. CPU only; GPU seconds **0**. No existing implementation,
reference repository, optimizer setting, eligibility rule or tolerance was changed.

**The dominant first-step differences in the two fixed cases are localized to
the original CPU reference's loss reduction and, in case 1, its output-head
backward reduction.** Common-input comparisons against float64 arithmetic favor
the current JAX reductions on these cases. There is no supported JAX algorithm
repair to apply from this investigation. This is stronger evidence about the
first gradient than the earlier GEMM conjecture, but it does not establish the
cause of every 100-step learned-value gap or satisfy DEC-020's sensitivity gate.
**B4 remains unavailable/unregistered.**

## Fixed inputs and method

The [diagnostic policy](../docs/tasks/B4-D-localization-policy.json) was written
before the boundary run. Cases 0 and 1 are the same two predetermined cases used
in the preceding first-step trace: the first case and the case with the largest
isolated learned-value mismatch. No new case, optimizer or control perturbation
was selected to obtain a favorable gate result.

The original read-only GRACE revision is `f674183f17a995d109e10ee6140d4c3e6d016115`;
the GPT-2 snapshot is `607a30d783dfa663caf39e06633721c8d4cfcd7e`.
The original oracle uses the approved CPU Torch environment; the candidate uses
the existing JAX environment. Both use fp32, gelu_new and layer-norm epsilon
1e-5; JAX reports highest matmul precision. The original edit learning rate,
initialization and replacement convention are preserved.

Forward hooks save values and incoming cotangents at 28 boundaries per case:
the hook GELU/projection, residual add, blocks 9–11 and their layer norms,
attention and MLP operations, final layer norm, tied output head and loss.
Each component's VJP is then evaluated using **the same reference input and
the same incoming cotangent on both frameworks**. This avoids confusing an
upstream activation difference with a local backward-kernel difference.

The first instrumentation attempt failed because Transformers 4.20 shares one
stateless activation module across GPT-2 blocks: a block-8 hook also saw block 0,
before any trainable value existed. The additive launcher creates separate
in-memory copies of that stateless activation solely to attach distinct hooks.
It changes no source file or function. The resulting initial value, first
gradient and first Adam output are **bit identical** to the prior uninstrumented
trace for both cases; all replayed reference component outputs are exact.
The failed attempt is preserved in `logs/grace_gradient_reference_round4.txt`.

## Indexing and replacement checks

| Case | Tokens including answer | Prompt tokens | Answer tokens | Key position | Replaced positions |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 12 | 10 | 2 | 9 | 0–8 |
| 1 | 11 | 9 | 2 | 8 | 0–7 |

Source replacement excludes the key-position token itself, exactly as the
candidate does. Selected projected rows equal the cold value exactly; every
unselected projected row is unchanged. Shifted mean-cross-entropy target IDs
match all nonignored source labels, including the answer terminator. The source
attention mask is all ones; causal masking leaves padded suffix positions inert.

True-length and 16-token padded candidate executions give identical measured
first gradients in these two probes. Replaying the source prefix into the
unchanged JAX suffix does not eliminate the gap: relative L2 errors remain about
2.21e-4 / 1.26e-4. Prefix arithmetic, padding and prompt indexing therefore do not
explain the dominant discrepancy in these cases.

## Component measurements

Relative L2 error means norm(actual − reference) / norm(reference), calculated
in float64 from the saved fp32 arrays. It is a diagnostic quantity, not a new
pass tolerance. [candidate.json](../results/S2/grace_jax/gradient_localization/candidate.json)
contains every component and its maximum absolute error.

| Common-input VJP | Case 0 relative L2 | Case 1 relative L2 |
| --- | ---: | ---: |
| Hook GELU, projection, residual add and later layer components | Each below 1e-6 | Each below 1.4e-6 |
| Final layer norm | Below 1e-7 | Below 2e-7 |
| Head | 6.17e-7 | **7.41e-5** |
| Loss reduction | **5.10e-6** | **6.72e-6** |
| Unchanged full value gradient | **2.19657e-4** | **1.27922e-4** |

The explicit two-input residual-add VJP is exact in both cases. In forward
execution the hook's addition association still differs from the original;
the earlier preregistered reassociation control already measures that variation.
This audit does not silently reinterpret the explicit-add check as proof of
bit-identical whole-block arithmetic.

## Float64 references distinguish the two sides

The head check computes the exact same saved incoming cotangent times the
exact same saved fp32 weights, accumulated using NumPy float64. The loss check
uses a centered float64 softmax/mean cross-entropy on the identical saved fp32
logit matrix. These references are confined to diagnostics; production remains
JAX fp32.

| Comparison against float64 | Case 0 relative L2 gradient error | Case 1 relative L2 gradient error |
| --- | ---: | ---: |
| Original Torch head VJP | 5.07e-7 | **7.42e-5** |
| JAX head VJP | 7.29e-7 | **4.55e-7** |
| Original Torch loss gradient | **5.09e-6** | **6.73e-6** |
| Current JAX loss gradient | **2.68e-8** | **2.43e-8** |

Replacing only the diagnostic JAX loss expression with log_softmax improves
scalar loss accuracy but barely changes the full value-gradient discrepancy
(2.19657e-4 → 2.19429e-4; 1.27922e-4 → 1.27166e-4). This is not a supported
fix for the parity problem. [head_loss_probes.json](../results/S2/grace_jax/gradient_localization/head_loss_probes.json)
also reports absolute errors and NumPy fp32 head reductions.

## Backward replay tests causality at the selected boundaries

A fresh, ephemeral original-GRACE first-step graph reproduces the saved native
gradient exactly. Holding that graph and its forward activations fixed, the
diagnostic substitutes a float64-computed incoming cotangent at the head/loss
boundary, then backpropagates through the unchanged original lower layers.
No optimizer step or 100-step trajectory is changed or compared in this probe.

The table compares the unchanged JAX value gradient with each backward replay:

| Original-graph backward replay | Case 0 relative L2 | Case 1 relative L2 |
| --- | ---: | ---: |
| Native reductions | 2.19657e-4 | 1.27922e-4 |
| Float64 loss cotangent only | 8.64534e-6 | 3.38043e-4 |
| Float64 head reduction only | 2.27623e-4 | 3.34845e-4 |
| Float64 head and loss together | **1.43803e-5** | **1.00096e-5** |

Both reductions together shrink the gap by about **15.3× / 12.8×**. In case 1,
changing either reduction alone makes the gap larger: their native errors partly
cancel. That interaction is why a single-kernel discrepancy should not have been
assigned the entire 100-step divergence without this experiment. The residual
1e-5 relative gap remains and is not declared zero or harmless.

Evidence: [reduction_replay_reference.json](../results/S2/grace_jax/gradient_localization/reduction_replay_reference.json)
and [reduction_replay_candidate.json](../results/S2/grace_jax/gradient_localization/reduction_replay_candidate.json).

## Gate decision and next useful work

The current JAX computation is closer to the float64 reductions at the localized
boundaries. No formula, mask or index defect was found in the checks above, and
there is no justified candidate-source patch from them. Do not make JAX imitate
the measured lower-accuracy reductions merely to fit saved values. A future
scientific decision about which numerical parity contract is appropriate belongs
to the lead, outside this diagnostic lane.

The original 40 learned-value comparisons remain failed, all 40 greedy/NLL
comparisons remain agreed, and the preregistered same-framework sensitivity
control remains inconclusive: its largest reassociation gap was 0.1525173 versus
the required 2.24391346. None of these probes is a replacement sensitivity control.
There was no implementation fix, so no form-(b) gate rewrite or repeated
20-case optimization experiment was triggered.

If B4 research continues after the freeze, the bounded next step is to repeat
these *fixed* reduction probes across the already committed parity cases and
measure whether the first-gradient reduction discrepancies predict the recorded
trajectory differences. A source-environment kernel comparison can be a separately
declared diagnostic; it must not be presented as the already failed JAX-vs-JAX
control. Avoid further perturbation searches selected to cross the threshold.

The original SD-21 wording attributing the entire discrepancy to GEMMs/flat-valley
amplification is broader than this evidence. The supported statement is the
two-case localization and backward replay above, with the remaining trajectory
and eligibility limitations explicit. Shared decision/spec files were not edited.

## Reproduction and resources

Use two CPU threads, disable bytecode, and invoke these additive scripts from the
repository root. The reference mode uses `../assets/envs/grace/bin/python`; the
candidate and NumPy/JAX probes use `../venv/bin/python`:

1. `scripts/grace_gradient_localize_isolated_activations.py reference`
2. `scripts/grace_gradient_localize_isolated_activations.py candidate`
3. `scripts/grace_head_loss_diagnostic.py`
4. `scripts/grace_gradient_reduction_replay.py reference`
5. `scripts/grace_gradient_reduction_replay.py candidate`

The launcher is the supported entry point for the shared boundary implementation
in `grace_gradient_localize.py`. Scripts refuse to overwrite completed evidence;
a repeat needs fresh destinations. Arrays live outside the repository under
`assets/reference/grace_diagnostics/gradient_localization_20260911_independent_activations/`;
JSON reports and console logs live in pc_cap. Reported source hashes and resource
hashes bind the evidence. The base checksum is unchanged in each candidate probe.
Both reference repositories and both environments remain unmodified.
