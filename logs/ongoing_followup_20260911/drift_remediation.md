# Drift-coverage remediation requirements for lead review

This document proposes a bounded repair process. It does not authorize an edit, a refreeze, a changed endpoint, or a GPU run. The active v2 source remains frozen. Evidence: [drift_coverage.json](drift_coverage.json), `src/pccap/harness/{runs,stage_s3,stage_s4,stage_s5}.py`, SD-3, and the completed run records named in the JSON.

## Reproduced scope of the gap

SD-3 replaces the original million-token request with the entire available WikiText-103 validation split, tokenized once: 247,289 unique tokens. S4 calls `Evaluator(..., drift_sample(4096))`; S5 confirm-mode chooses `drift_n = 4096`. The evaluator independently defaults to `drift_positions = 4096`, uses 128-token full windows, and reports 127 next-token predictions per window.

The model-free counterexample shows two independent limits. Enlarging only `drift_sample` does not increase evaluation coverage. Wiring the complete token count into both interfaces admits 1,931 full windows, scoring 245,237 positions, but discards the last 121 tokens. Supporting that partial window requires changes to the loop as well: the current `_drift_nll` assumes every window has the first window's length.

No inference of changed ES/RET-GS follows from this finding. It concerns drift-assay completeness, reported denominators and the cost of completing that assay.

## Decisions needed before implementation

1. **Choose the evaluation contract for the approved split.** Record the unique input-token count, window/context policy, scored-position count and excluded context/tail positions explicitly. With independent 128-token windows and the final 121-token window included, there would be 245,357 next-token positions and 1,932 initial context-only tokens. A different overlapping-context policy has a different denominator and must not be silently substituted.
2. **Choose versioned handling.** The frozen source hash covers `src/pccap`. An in-place source change will refuse the next confirm-mode job. The lead and run owner must decide between a versioned code/manifest transition and an explicitly approved supplementary evaluation of saved checkpoints, preserving v2 provenance. Do not merge incompatible identities as if they were one run.
3. **Price the remedy.** The number of full windows increases from 32 to 1,931 (60.34 times), which is an input-workload ratio, not a measured runtime estimate. The final partial window adds further work. Benchmark representative checkpoints before promising an ETA or headroom. Charge original attempts, added evaluation, compilation and failures as required.
4. **Preserve checkpoint coverage.** An endpoint-only rescore does not replace all specified checkpoint assays. Inventory each required saved learner state before selecting a supplementary evaluation route. If a state is unavailable, report the gap and determine whether reproduction is needed; do not infer a missing measurement from another checkpoint.

## Concrete implementation and verification checklist

- Load and hash-check the SD-3 corpus and pass the intended extent explicitly in both S4 and S5; reject accidental fallback to the development default.
- Make the evaluator's empty, short-input, full-window and partial-tail behavior explicit, with recorded counts. Keep inputs deterministic and identical across paired arms.
- Bound batch size. The current drift loop batches across all windows and the base's `last_logits_batch` forwards the supplied batch to the kernel. Passing 1,931 windows at once needs a memory assessment; split into fixed-size microbatches where necessary.
- Combine loss numerators and position denominators across microbatches and partial windows. An unweighted mean of chunk means is wrong when chunks contain unequal numbers of positions.
- Verify the old 4,064-position prefix produces the same NLL under the new batching path within the declared numerical tolerance. Verify tail coverage with a hand-computable synthetic corpus and compare weighted reductions against a scalar oracle.
- Test that locality references, base weights, cap state, retrieval metadata, RNG and replay are unchanged by the rescore. Include ledger checks and an injected failure with its consumed cost retained.
- Record corpus SHA-256, source/manifest identity, original checkpoint identity, token and prediction counts, window/batch policy, elapsed and accelerator cost, and any missing checkpoint for each output.
- Preserve the old small-sample results as such. Update public claims only when the required new assay exists; completing this diagnostic is not completing LM-drift validation.

## Concurrency

CPU work can prepare the coverage contract, synthetic count/reduction controls, checkpoint inventory and proposed versioning/accounting changes. Any real checkpoint rescore, new performance measurement or changed confirmatory execution belongs to the run owner under the GPU lease. Do not interrupt the active queue merely to run this diagnostic.

The only immediate edits requested by the present follow-up are documentation corrections in the separate approval patch. No production source patch has been applied or presented as ready before the contract and versioning decisions above.
