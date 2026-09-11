# B4-D — first-gradient localization

Status: diagnostic investigation complete for the two declared cases; B4 qualification remains unmet. Agent: Codex. Date: 2026-09-11.

Inputs: original GRACE/reference snapshot pins, committed parity cases and first-step traces; unchanged candidate/source math; round-3 sensitivity policy and result; ongoing.md round-4 lane.

Outputs: `logs/grace_gradient_localization.md`; `docs/tasks/B4-D-localization-policy.json`; additive scripts `grace_gradient_localize.py`, `grace_gradient_localize_isolated_activations.py`, `grace_head_loss_diagnostic.py`, `grace_gradient_reduction_replay.py`; five JSON reports in `results/S2/grace_jax/gradient_localization/`; console logs under `logs/`; numerical arrays under `assets/reference/grace_diagnostics/gradient_localization_20260911_independent_activations/`.

Verify commands: run the isolated-activation launcher in reference and candidate modes, the head/loss diagnostic, and reduction replay in reference and candidate modes. The report supplies the environments and order. Reference runs use the approved CPU-only legacy Torch oracle; candidate runs use the existing JAX environment. No GPU lease is used.

Verify output: first value, gradient and Adam output bit-identical to the prior original trace; all reference component forward replays exact; 27 common-input VJP comparisons per case; masks, shifted targets, key boundary and replacement rows agree. Head/loss float64 probes and counterfactual backward replay localize the dominant differences. Joint head/loss replay reduces the unchanged JAX-vs-original gradient gap from 2.19657e-4/1.27922e-4 to 1.43803e-5/1.00096e-5. Base hashes stay unchanged; new scripts pass Ruff.

Done-when check: fixed-input boundary/VJP localization and indexing checks are documented with numerical artifacts. No candidate algorithm defect was found in the tested path; no learner patch is justified by these measurements. The report explicitly limits inference to these first steps and keeps B4 unavailable under DEC-020. This is not a claim that all 40 learned-value mismatches have been explained or that the sensitivity gate passed.

Cost: GPU seconds 0. Successful diagnostic passes report approximately 51.61 s wall time in their JSONs. A failed initial hook-instrumentation attempt is preserved separately. Review/preparation time is not classified as accelerator use.

Deviations: the original hook driver requires the additive launcher because Transformers shares a stateless GELU module across blocks. The launcher separates only in-memory module identities and proves the resulting first step remains bit exact. Float64 is used only for diagnostic reductions, not production execution. No change to the preregistered sensitivity control, strict PC-10 test, threshold, optimizer or codebook was made.

Unresolved: the residual first-gradient gap and the relationship to all 100-step trajectories remain unproven; the round-3 sensitivity prerequisite remains unmet. No form-(b) gate rewrite or repeated optimization run was triggered because there was no implementation repair. Shared SD-21/decision wording should not assert more than this report establishes.

Questions for lead: a one-word count correction in the newly written report (28 to 27) is separately prepared in `B4-D-report-count-edit-request.json`, awaiting the standing permission-before-edit rule. The diagnostic JSON and this task record already state the correct count. No source-code edit is requested or needed for these conclusions.
