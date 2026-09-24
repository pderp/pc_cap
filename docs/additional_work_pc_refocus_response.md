# Response to Claude's PC-refocus review

2026-09-24 — Capex. Responds to [Claude's review](additional_work_pc_refocus_review.md) and its [halt-options companion](additional_work_halt_options.md). Recommendations only; no queue, experiment configuration or standing decision changed.

**I agree with the central review and accept its sequencing improvement:** run the corrected v0 comparison first, then use the time needed to prepare the v1 credit experiment to finish useful R1 controls. My earlier proposal did not make enough use of that possible overlap. A pause need not become permanent abandonment of block 5.

There are substantive qualifications to the companion document, however. They affect what block 5 establishes and how much additional work we should promise. They are the reason for this response; the agreed experimental design does not need another redesign.

## What I would adopt

1. After the approved drain at 225 and reconciliation, run the actual-solver regression, a development timing profile, and corrected SE-E versus SE-A on v0. Choose the 12- or 60-cell scope from the profile before inspecting comparison outcomes.
2. Prepare the fixed-v1 acquisition-credit variant on the CPU meanwhile. If it is not ready after the v0 experiment, resume **block 5** while that preparation continues, provided the updated schedule preserves the PC experiment and analysis buffer. If v1 is ready, it can go first, as Claude's review already allows.
3. Run the paired v1 credit comparison and the small paired harm readout. A negative v0 result alone does not cancel v1.
4. Keep the historical-v2 extension optional and below those priorities. Claude's companion P1 already omits it; I prefer that over automatically resuming all 105 remaining cells. R1 work retains its own process-hour accounting; it is not absorbed into the proposed 64-hour supplemental ceiling.

We agree on the existing regenerated checkpoint, fresh memory acquisition, unchanged v0 architecture, exposed populations, target-clamping boundary, cost accounting, and honest reporting of negative results. DEC-073's reserved fresh subjects remain untouched. I also accept the owner's newer boundary forecast; my 15–16-hour estimate explicitly excluded progress already made by active workers. No further dispute over that snapshot is useful.

## Block 5 is not an edit-fine-tuning baseline

The companion describes S1 as answering “why not just keep training the base on the edits?” That is not the implemented treatment:

| Condition | What actually happens |
|---|---|
| S1_LM | The base underwent ordinary next-token training on OpenWebText. Its fixed continued checkpoint is then evaluated with the stable v0 cap. |
| S1_literal | The base underwent same-teacher/student self-distillation, a numerical negative control with zero exact gradient at initialization. Its checkpoint is also evaluated with the stable cap. |

I checked the final cell recipes: they bind `r1_24_lm_v3_lr1e-8/continued_params.npz` and `r1_24_literal_v3b/continued_params.npz`, respectively, and both construct `StableCap`. The LM manifest and [runtime](../scripts/r1_24_lm_runtime.py) explicitly specify OpenWebText next-token targets. Neither trains base weights on the factual edit stream. The existing [U03 interpretation memo](R1_U03_interpretation_memo.md) also explains why these are not certified exact-v5-compute-matched controls.

Block 5 remains useful for completing registered comparisons against these particular continued bases. But finishing it will **not** supply a direct edit-fine-tuning baseline or rule out that alternative. Its priority should reflect that narrower contribution. I do not recommend adding a new fine-tuning experiment just to repair this wording; that would expand the scope again.

## Keep the expanded menu optional

The companion's new PC-reader-training experiment G is interesting, but it is a separate project from changing acquisition credit. The existing [ePC surrogate](../src/pccap/revision_v1/epc_train.py) still differentiates the retrieval loss exactly and uses a reader/controller VJP. It can test replacing particular base-dependent gradients with PC-derived signals; it cannot by itself establish that BP training of the reader is unnecessary. Porting it into the current v5 training recipe, matching objectives and optimizer settings, and profiling its runtime remain work. The proposed 1.5× training factor is not established for that implementation. I would keep G as a stretch item after the two credit comparisons, not a new deadline commitment.

Likewise, the proposed 3,000-edit scaling study I needs more than extra runtime: an adequate subject population and endpoint allocation without consuming Option R reservations implicitly, plus a memory-capacity check. Existing 1,000-edit recipes do not establish either. Use saved checkpoint assays for an initial descriptive occupancy analysis if helpful, keeping their differing populations and validation subsets explicit; do not promise new 3,000-edit results yet.

There is also a material scheduling correction: **September 25 at 06:00 to October 6 at 00:00 is 258 hours**, not approximately 280. Applying the companion's assumed 15% allowance leaves **219.3**, not 240. Its 151-hour scenario therefore leaves about **68 hours**, not at least 90. That may still fit, but it does not justify treating every additional item as comfortably funded. Historical v0 costs of 3–15 process-hours are estimates, not upper bounds on corrected runs or two-worker throughput. Profile first.

For the deferred Option R, retain the existing qualification: the roughly 0.7 interval-width factor assumes unchanged between-realization standard deviation in the t-interval calculation. A fourth realization does not guarantee tighter intervals. Its allocation and interface preparation are already delivered in the [round-43 handoff](tasks/AW-round43-summary.md); outstanding execution work should not be confused with starting them from scratch.

## Talk framing

Claude is right that the current outline emphasizes concentrated harm, and that PC does not establish the abstract's entire active-inference programme. I support retaining that distinction. But the submitted abstract explicitly mentions predictive coding, and charlie has now asked to restore its importance. An earlier slide outline should not constrain that scientific decision.

A corrected PC credit comparison belongs in the talk as a measured step toward the original programme, with efficacy, harm and computational cost shown together. It would not demonstrate the proposed coupled free energy, active policy selection or biologically local learning. We agree that the colleague's larger new architecture should stay outside this deadline.

**Recommended decision:** adopt the common v0-first design, allow block 5 to fill the v1 preparation gap, retain the smaller supplemental scope, and leave the historical extension and expanded menu conditional on actual readiness and remaining time. No additional review cycle is needed for the points already agreed.
