B4-S sensitivity result — 2026-09-11, Codex

DEC-020's conditioning prerequisite is not established. The two JAX-only perturbations preserve final greedy outputs, answer NLL and the declared loss-trajectory comparisons, but their learned-value gaps are much smaller than the original cross-framework discrepancy. B4 remains unregistered; PC-10 form (b) and S3-01's fully passing control table must wait. No reference, tolerance or existing PC-10 result was changed.

The [policy](../docs/tasks/B4-S-sensitivity-policy.json) was written before execution and its bytes verified at completion. The [driver](../scripts/grace_sensitivity.py) and [full result](../results/S2/grace_jax/sensitivity.json) retain per-case measurements at steps 1, 10 and 100, including value gaps, absolute/relative loss changes, decoded IDs and NLL. The run used the 20 fixed isolated cases, original seeds, cold-value RNG and Adam hyperparameters; 98.33 seconds, CPU only, base parameters unchanged.

| Control | Max final value gap | Median final gap | Median same-case ratio to prior cross-framework gap | Trajectory passes | Final greedy / NLL passes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial value + float32(1e-7) | 0.073916 | 0.011215 | 0.008547 | 60/60 | 20/20 each |
| Algebraically equal hook addition reassociation | 0.152517 | 0.007668 | 0.011529 | 60/60 | 20/20 each |

The association variant changes (residual + projection) + bias into residual + (projection + bias), with an optimization barrier preserving grouping. It does not move operations across GELU, normalization or attention. The initial-value perturbation is a conditioning probe, not an algebraic identity. Both use the unchanged inference evaluator after learning to isolate learned-state sensitivity.

The policy required the algebraic control's maximum step-100 gap to reach at least one tenth of the already recorded cross-framework maximum 22.439135: threshold 2.243913. Its observed maximum, 0.152517, misses that threshold. Both controls exceed 0.001, so neither the reproduction verdict nor the strict “insensitive” branch applies; the recorded verdict is inconclusive_or_equality_failure. There was no output/loss equality failure: the inconclusive branch is caused by insufficient divergence magnitude.

The existing summed-answer NLL tolerance (absolute 0.001, relative 0.0001) was applied to mean training loss multiplied by answer-token count, including newline, at all three steps. The maximum absolute mean-loss difference was 1.144409e-5 and the maximum relative difference 6.236e-4. No new tolerance was fitted. Loss entries are the loss evaluated before the named optimizer update; value entries are the state after that update, following the existing trace convention.

This result supports some numerical sensitivity but does not explain a value gap of 22.4 or exclude an adapter defect. In particular, the case responsible for that maximum has only ~0.00772 association-induced gap. The prior first-step trace still matters: source initialization matches, the isolated Adam arithmetic agrees closely when given the same gradient, but independently computed gradients differ. The next diagnosis should localize that first gradient difference through hook suffix, GELU, residual addition, layer normalization, attention, output head and loss reduction with fixed inputs. Compare vector-Jacobian products at successive boundaries and validate masks/prompt indexing alongside numerical kernels. Preserve current thresholds and record any further conditioning control before running it; do not search perturbations until one earns the desired label.

Checkpoint disposition:

- Sensitivity experiment and verdict: complete.
- Form-(b) PC-10 acceptance: blocked by the failed prerequisite, including the isolated and sequential requirements.
- Batched adapter implementation: an independent new-file prototype is under review; it does not change this scientific verdict.
- DEC-020 reference label in the canonical adapter/task record: withheld pending a qualifying gate.
- S3-01 full passing table: conditional work remains blocked.

The existing pc10.json still records the original elementwise parity failure. Its 40 output-level agreements are evidence, but do not substitute for the additional condition the lead approved.
