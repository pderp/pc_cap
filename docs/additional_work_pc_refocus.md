# Put predictive coding first after the current run

2026-09-24 — Capex, for charlie and Claude. Proposed replacement for the supplemental portfolio in [additional_work_plan_final.md](additional_work_plan_final.md), following the colleague's review. This document does not change the running queue or authorize a GPU launch. Experimental completion remains **October 9, 2026, 17:00 America/New_York**; presentation is October 15.

**Recommendation:** complete the current block through cell 225, pause the remaining queue, and prioritize a corrected **SE-E versus SE-A** experiment on the original v0 cap. Then test whether that credit procedure transfers to the fixed v1 reader. Defer the layer-training portfolio, the extra fresh realization, and the historical-reader extension. Keep a small ordinary-text harm analysis beside the PC results.

The earlier supplemental plan concentrated on better retrieval and bounded output corrections. Those are useful questions, but they would not answer the missing predictive-coding question. I helped develop that plan; this is a substantive change of scientific priority, not an additional lane to fit on top of it.

## 1. The running study is not affected by the SE-E error

The defect is **SD-24**, fixed September 13. At a cap-write site the intended error penalty was `½‖e‖²`, but the implementation used `½‖e + w‖²`, where `w` is the cap's write. This introduced an unwanted component opposing the write into the error-derived credit signal. The old natural-language SE-E result therefore measures that defective rule. It is not a clean negative result for the corrected algorithm.

The current R1 queue uses a different path:

- The selected v5 reader acquires per-position deltas with five normalized **adjoint** steps. Its reader weights were trained by BP.
- The stable/live v0 and matched-update comparators also use adjoint credit.
- The S1 continuation controls construct `BPBase` objects, including when loading continued NPZ weights. Their cap credit is adjoint.
- The optional historical v2 reader is another feedforward reader condition, not SE-E.

I traced the queue backend through `scripts/r1_77b_sealed_backend.py`, the standard constructor in `scripts/r1_61_cell_driver.py`, and `src/pccap/revision_v1/stage4_adapters.py`. The latter constructs v0 `CapConfig` with its default `credit="adjoint"`; v1 acquisition calls `base.adjoint` directly in `revision_v1/adapt.py`. None of these conditions requests the affected error-inference procedure. The corrected energy also exists in the present source.

Thus **SD-24 is not a reason to discard or restart R1**. This is a conclusion about that specific defect, not a claim that the entire project is bug-free. The scientific reason to shorten the queue would be the value of a direct PC experiment before the deadline.

At the September 24, approximately 14:42 EDT read-only snapshot, the queue had 213 starts, 211 distinct successful finishes, and two outstanding starts. The completed cells comprised:

| Work | Completed / planned | Relevance of finishing |
|---|---:|---|
| Primary learned/random/stable triplet, all three datasets and realizations | 135 / 135 | The central R1 comparison already exists. |
| Matched-update and live C1/C2 controls, zsRE/CounterFact | 76 / 90 | Finish this block to retain complete comparator coverage. |
| S1 continuation controls | 0 / 60 | Additional evidence about continued base training; useful, but less direct for the PC question. |
| Optional historical v2 reader | 0 / 45 | Historical architecture context; lowest priority now. |

All 14 unfinished block-4 cells were CounterFact/live-C2. Its first completed cell took 132.8 process-minutes; extrapolating to two workers gives about **15–16 hours** for 14 cells before allowing for already elapsed work. This estimate has only one cell of direct evidence. Compared with the existing September 27 evening release forecast, pausing at 225 plausibly frees roughly **two days**, with substantial scheduling uncertainty.

My preferred cut is therefore **225, not an immediate kill and not automatic completion of all 330**. If the existing September 27 release forecast holds, a small PC rerun could still fit after all 330; shortening is a choice to gain implementation and troubleshooting time, not evidence that the deadline is otherwise impossible. Deferring S1 weakens the continuation comparison, and unfinished registered contrasts must remain explicitly unavailable. It does not invalidate the completed triplet or establish that extra base training cannot help. Preserve all results and the original planned denominators; state the scheduling/PC-priority reason for the amendment without selecting cells by outcomes.

The owner should use the already tested parent-only drain procedure in [R1-77g-resume.md](tasks/R1-77g-resume.md), after explicit approval to shorten the run. Arrange it when the last block-4 cells have been dispatched so they can finish without admitting block 5. The current process does not hot-reload a changed stop setting. No process was signalled for this review.

## 2. First experiment: repair the missing original comparison

**Question:** with the same frozen base and cap architecture, does finite-iteration predictive-coding credit produce useful factual edits and retention, and what does it cost relative to ordinary adjoint credit?

Use the original PDF's S5 comparison, rather than redesigning the cap at the same time:

| Setting | SE-A rerun | Corrected SE-E rerun |
|---|---|---|
| Base weights | Existing regenerated ePC checkpoint | Identical checkpoint |
| Cap | Original v0 C1, live R-h keys, all three banks | Identical |
| Acquisition credit | Negative normalized adjoint | Normalized error after 8 inference steps |
| Solver | No error relaxation | Existing corrected solver, error learning rate 0.1 |
| Memory and evaluation | Fresh empty memory, fixed stream and evaluation inventory | Same initial state, stream, inventory and budgets |

“Frozen v0 cap” here means the **architecture, configuration and base weights** are fixed. Its memories must be acquired afresh under each credit rule. Evaluating an already learned SE-A memory while changing a flag would not test SE-E acquisition. C1 writes all three banks; it is not a top-layer-only treatment.

Use the regenerated checkpoint at `assets/models/epc/epc-50m/checkpoints/final-009766/params.npz` (under `/home/derp/cap/`; recorded SHA-256 `ea4c561d3963ffd89f866337ef5e789a4ef15b7558b4c717594dbef88cd26f51`). Load it explicitly with `EPCBase.from_npz`. **The default `EPCBase()` loads BP teacher weights**, which would silently change the historical comparison. Reuse the corresponding S5 calibration and stream-selection rules from the archived v2 manifest, not R1's differently calibrated live controls.

The historical SE-A row is useful context, but fresh paired controls are inexpensive enough to avoid making an invariance argument across many intervening code changes. Do not rerun base distillation or make SB versus SE-A the main new question.

Start with **12 complete cells**: two credit rules × two datasets × three original realizations × one preselected original order. Keep the old stream lengths: 1,000 zsRE edits and 300 CounterFact edits. If the development timing profile predicts that the full original five-order matrix will fit the 24-hour v0 ceiling, commit to all **60 cells before examining comparison outcomes**. Otherwise retain the 12-cell scope. Orders share a population; neither five orders nor thousands of tokens supplies additional independent realization replicates.

These are exposed historical populations. Label the work a **supplemental defect-correction replication**, not new untouched confirmation. Keep the fresh subjects reserved for Option R unconsumed; any reassignment of DEC-073's allocation is a separate decision. The existing S5 frozen execution identity must not be bypassed or rewritten: use a small runner in `aw/`, new output directories, and the corrected current implementation.

Saved S5 `cost.json` records provide a useful scale, but not a promise:

| Historical cell type | Runs | Mean full elapsed seconds |
|---|---:|---:|
| CounterFact SE-A | 15 | 428.6 |
| CounterFact SE-E, defective rule | 15 | 505.0 |
| zsRE SE-A | 15 | 951.4 |
| zsRE SE-E, defective rule | 15 | 1,673.7 |

All 60 historical cells sum to **14.83 elapsed process-hours**, whereas their synchronized model-call timers sum to **8.89 hours**. The latter must not be used as total wall time. The 12-cell scope is approximately **2.97 process-hours** at those historical group means. Corrected credit can change update acceptance and runtime; compilation, new diagnostics and any larger fidelity assay add cost. Also, DEC-036's parenthetical “20 of them SE-E” is a bookkeeping error: the saved inventory contains **30 SE-E and 30 SE-A** executions, with SB reused separately.

## 3. Essential checks and scientific readout

Do a bounded development smoke run before the paired experiment. The checks should directly challenge the algorithm:

1. With **nonzero cap writes**, verify that the prior penalizes free errors rather than writes. From zero error, the one-step site error should agree with `−0.1 × adjoint`, within numerical tolerance. Include a tiny actual-solver regression; a mock returning the expected direction cannot detect SD-24.
2. Verify zero-error forward identity, unchanged base weights, and independent empty memory at each arm's start. Use identical items, seeds, calibration and stopping rules for each pair.
3. Clamp only the currently taught support answer during acquisition. Score retention/paraphrase/locality with ordinary generation and **no evaluation-answer clamp**. A lower clamped energy alone is not successful editing.
4. On a fixed small development prefix sample, measure energy, gradient residual, direction cosine and norm at 1, 8 and 32 iterations, both without writes and with representative acquired writes. Keep eight iterations as the historical primary treatment; other horizons are diagnostics, not a search over evaluation results. Stop on nonfinite computation; finite poor performance remains reportable.
5. Charge the real work. An eight-step `infer_errors` call performs nine forwards and nine reverses, including the terminal residual measurement. Record elapsed time and operation counts alongside efficacy.

Existing evidence supports repairing the comparison but gives no guarantee of improvement. In `results/R1/pilot/surrogate_check_fixed.json`, nine synthetic prefixes have one-step cosines essentially 1.0; at eight steps the sitewise mean cosines are about 0.966, 0.993 and 0.999, with mean terminal gradient residual ratio **0.350**. That is finite-iteration inference, not demonstrated convergence. Separately, the corrected synthetic v1 training pilot favored BP (answer NLL 2.85 versus 4.50); do not omit that unfavorable evidence.

For each paired stream, report immediate edit success **ES**, end-of-stream own-prompt retention **RET-ES**, paraphrase retention **RET-GS**, locality **LS**, and cost. Preserve the old S5 scoring for the replication; any modern bounded-text score is an explicitly separate secondary score. Show each realization and order difference. Emphasize zsRE for the credit comparison: historical CounterFact RET-GS was zero for every arm, so its unchanged paraphrase score may reflect the v0 reader's floor rather than credit quality.

Keep one small ordinary-text harm comparison for the talk: same preselected validation positions, both arms, same checkpoint; mean KL, signed NLL change, upper quantiles, maximum and fraction exceeding declared thresholds. Display efficacy with harm, so failure to learn edits cannot masquerade as improved safety. The legacy S5 drift subset is not the full R1 inventory. Budget a larger paired assay only after the main replication; do not claim a power law from concentrated harm alone.

A valid conclusion might be that corrected PC recovers acquisition but offers no retention advantage, or that it remains worse or too expensive. The objective is to answer the original question honestly, not obtain a favorable PC slide. Equal edit/update budgets are not equal compute: this experiment alone cannot establish compute efficiency over BP.

## 4. Second experiment: PC credit with the fixed v1 reader

The v0 cap has a documented retrieval bottleneck. Therefore a technically valid negative v0 result should **not automatically cancel** the v1 experiment. The branch depends on implementation correctness and remaining time, not the sign of the v0 effect.

Hold the selected v5 reader, its BP base weights, gate, calibration and memory policy fixed. Change only the direction used to acquire the per-position deltas: current adjoint versus corrected eight-step error credit. Reacquire memories independently on paired streams. Start with the already prepared, exposed supplemental realization-0 zsRE/CounterFact populations, 300 edits and one fixed order; describe this as a small exploratory transfer test, with no new-population inference. No MQuAKE expansion or layer ablation in this first test.

This is **v1 with PC acquisition credit**, not the original ePC-base SE-E arm and not a PC-trained reader. Using the regenerated ePC base under the selected BP reader would change both representation and credit. Retraining the reader with `revision_v1/epc_train.py` is a different experiment and remains deferred.

Most solver machinery already exists, but v1 acquisition is not a configuration toggle: `adapt.py` calls `base.adjoint` directly. Implement an isolated `aw/` acquisition variant that changes credit while preserving the real feedforward loss used for acceptance, initialization, bounds and stopping. A proxy that substitutes errors for gradients but leaves the hard-coded one-reverse cost accounting is insufficient. Compare its adjoint mode against the existing v5 path before using its PC mode.

Use “error-optimization predictive coding” precisely. Our solver optimizes errors with JAX autodiff through the graph; this is **not a demonstration of backpropagation-free local learning or a biologically plausible implementation**. The [ePC paper cited by the implementation](https://arxiv.org/abs/2505.20137v5) itself distinguishes its digital reparameterization from biological plausibility. Neither this test nor the v0 rerun establishes predictive-coding inference in the reader itself.

## 5. Smaller workload, fewer administrative dependencies

Replace the old 150-hour supplemental portfolio with these **proposed single-GPU wall-time ceilings**, including GPU compilation and failed attempts:

| Priority | Work | Ceiling |
|---|---|---:|
| 1 | v0 solver smoke/profile and corrected paired replication | 24 h, including at most 2 h initial smoke/profile |
| 2 | Fixed-v1 acquisition-credit comparison | 24 h |
| 3 | Paired ordinary-text tail readout; bounded-output follow-up only if it fits | 8 h |
| — | Troubleshooting reserve | 8 h |
| | Total | **64 h** |

These are stop limits, not measured requirements or an assurance that v1 porting will succeed. Profile before expanding. Cut the bounded-output follow-up first, then v1 scope; protect a complete paired v0 comparison. If even that cannot fit, report a clearly labeled development pilot rather than incomplete cells presented as the full replication.

Begin CPU preparation now in `aw/`; leave the running job's locked `scripts/` and `src/pccap/` trees alone. Run locally using JAX and the existing environment. Keep code, logs and reports in `pc_cap`; datasets, models and large caches under `assets`. Sibling repositories stay read-only. Start GPU work only after the owner has drained/released the current queue and reconciled its existing work. The block-4 stop is the recommended new priority; if the lead retains all 330 cells, the same smaller PC plan starts after their release instead.

Use September 25–27, depending on release, for the smoke/profile and v0 replication; September 28–October 3 for v1 and interpretation. Start no new fits after October 6. Reserve October 7–8 for completing evaluation and figures, and freeze by October 9 at 17:00. Move dates with actual release and measured completion forecasts; do not borrow presentation-preparation time.

For this supplement, aim for **one experiment specification/configuration, a runnable command, raw results with model/code identities, a few algorithm-focused tests, and one comparison report**. Record substantive changes in that specification. Do not create a new chain of signing sessions, recursively bound review packages, or independent task receipts for every small change. Keep the protections that answer concrete questions: wrong weights, wrong energy, answer leakage, unmatched comparisons, lost outputs and understated cost.

Concurrent CPU work can be useful without more coordination layers: one agent prepares the v0 runner and actual-solver regression; the other prepares paired scoring and the optional v1 acquisition seam in separate files. One owner dispatches the GPU jobs. Neither edits the active R1 implementation. Results inspection must not determine which populations or orders are admitted to a comparison.

Defer AW-L retraining and the upper-layer-only hypothesis, Option R's additional realization, the historical-v2 extension, and a new large neural-symbolic architecture. Keep their prepared artifacts for later. The colleague's small-scale architecture may motivate a future collaboration, but obtaining it, porting it to JAX and tuning GPT-2 scale is too uncertain to become the October 9 critical path.

Sources for the local assessment: the original [plan PDF](pc_cap_month_plan_readable.pdf), [SD-24](spec_defects.md), [annotated v0 report](report.md), [R1 Stage 2 report](R1_stage2_report.md), [Stage 4 scope and block order](R1_stage4_protocol_v5_2_D_5.md), [queue updates 110–114](lead_queue.md), saved S5 cost records under `results/S5/frozen-confirmatory-v2-84126123/`, and the constructors and credit implementations named above. No new model experiment was run in preparing this proposal.
