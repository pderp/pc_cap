# Mandatory Amendment — Alignment With Existing pc_cap Research

**This amendment takes precedence over the earlier "Research Agent Handoff: Dataset Extremes, Heavy Tails, and Predictive-Coding CAP Robustness" wherever the instructions differ. All other measurement, validation, reporting, raw-data and incremental-saving requirements remain in force.**

## 1. Review authoritative research artifacts first

Before implementing or executing any analyses, read and reconcile these project documents:

- `docs/R1_stage4_report.md`
- `docs/additional_work_report.md`
- `docs/additional_work/PC-reader_report.md`
- `docs/additional_work/HT-17_report.md`
- `docs/additional_work/PC-v0_report.md`
- `docs/additional_work/PC-v1_report.md`
- `docs/freeze_handoff_20261009_draft.md`
- `docs/REPRODUCE_additional_work.md`
- The associated experiment manifests, reports, raw outputs and decision records.

The original research has already generated extensive numerical data. **Do not repeat computations or model evaluations unnecessarily.** Validate existing artifacts, preserve their provenance and build on them.

Create a matrix describing which requested analyses are already complete, which can be calculated from saved data, and which require new evaluation.

Use the authoritative local, receipt-backed version if a local file differs from the public GitHub copy. Record any discrepancy.

## 2. Correct identification of the model comparisons

The repository contains several different experiments that must remain distinct.

### A. Primary comparison for our requested analysis

The principal comparison is:

1. Frozen GPT-2 Small without CAP.
2. GPT-2 Small with the ePC-trained reader/CAP.
3. GPT-2 Small with the BP-trained reader/CAP.

The completed `PC-reader_report.md` directly compares reader training by ePC versus BP, with three paired training seeds, 300 edits, and two datasets: zsRE and CounterFact.

**Both reader-training arms use adjoint-based acquisition.** Thus this is a comparison of reader training methods, not a comparison of PC versus BP acquisition credit.

Preserve the exact existing architecture, checkpoint, training seeds, adaptation protocol and evaluation population.

The three paired training seeds do not represent three independent subject-population draws.

The PC-reader report does not establish a corresponding MQuAKE comparison. Determine whether the saved reader checkpoints can legitimately be evaluated on MQuAKE using the existing evaluator. If this requires new work, treat it as a separate supplemental evaluation rather than as a result already present.

### B. Fixed-v5 acquisition-credit comparison

The repository separately tests changing acquisition credit from adjoint/BP to corrected finite-step predictive-coding error credit while holding the trained reader fixed.

Report this experiment separately because changing the acquisition algorithm is not equivalent to changing how the reader was trained.

### C. PC-v0 comparison

The historical PC-v0 SE-E versus SE-A study uses the **regenerated ePC 50M frozen backbone**, not the 124M GPT-2 Small backbone used in the principal study.

Do not include these results in a GPT-2 Small three-model aggregate or describe them as measurements of the same backbone.

They may be included in a clearly labeled supplementary section.

### D. Main Stage 4

The Stage 4 `R1_learned_ff` condition uses a BP-trained learned memory reader. It is not automatically the same evaluation protocol as the supplemental PC-trained reader comparison.

Its many controls are valuable context, but they cannot be relabeled as PC-trained-reader outcomes.

Maintain explicit experiment-family identifiers in the canonical data.

## 3. Mandatory no-CAP baseline — corrected procedure

We still require a no-CAP comparison throughout the principal study.

However, `v0_stable`, an untrained/random reader, a zero-radius CAP and a condition's `own_capoff` reference are not automatically interchangeable with a direct original GPT-2 Small baseline.

For every comparison:

1. Identify the exact frozen backbone used by the PC/BP models.
2. Determine whether its original capless outputs are already saved.
3. Reconstruct or run the baseline on identical examples, prompt templates, checkpoints and evaluation conditions if necessary.
4. Validate the outputs against directly running that same frozen backbone without any reader, cap correction or active memory.
5. Preserve both the original-base and own-cap-off references when they differ.

For sequential factual-edit experiments, the frozen model should still be evaluated at the corresponding checkpoints on the same probes, even though it does not acquire edit memories.

**Do not confuse zero edit retention with zero ordinary factual-QA accuracy.** The original frozen model may know original facts while failing to adopt requested counterfactual edits.

The required report must therefore contain the frozen-baseline comparison wherever the protocol permits it, but explicitly mark genuinely missing or incomparable conditions.

A complete three-model comparison across all three datasets remains our desired supplemental deliverable; do not fabricate the missing MQuAKE PC-reader results.

## 4. Preserve the actual sequential evaluation protocol

The established main-study horizons are:

- zsRE: 100, 300 and 1,000 edits.
- CounterFact: 100, 300 and 1,000 edits.
- MQuAKE: 100 and 300 edits.

The supplemental PC-trained reader evaluation uses the first 300 edits on zsRE and CounterFact.

Do not combine 300-edit and 1,000-edit results into a single matched comparison.

Use the project's original metrics:

- `ES`: immediate edit acquisition success.
- `RET-ES`: end-of-stream retention on original edit prompts.
- `RET-GS`: end-of-stream paraphrase retention.
- `LS`: bounded exact-text agreement with the original-base response.

Do not describe LS as factual-QA accuracy. Also retain near-miss preservation, revision behavior and unseen-prompt firing where available.

The registered near-miss controls use distinct subjects within matched relation/template families, not arbitrary semantic nearest neighbors. Their reference is the actual cell's cap-off neighbor response.

If MQuAKE multi-hop question accuracy can be calculated from available records, it is an additional metric and must not replace the registered RET-GS endpoint.

All figures and tables must show evaluation horizon, observation unit, model condition and the actual denominator.

## 5. Preserve existing tail-analysis conventions

The research already contains a detailed ordinary-text fidelity assay:

- 1,931 complete validation windows.
- 245,237 scored token positions.
- Context reset for every 128-token window.
- An additional fixed 128-window descriptive prefix.

Reuse the saved full-validation vectors and existing HT-17 analysis.

For the same-prefix ordinary-text comparison, define:

`Delta_NLL = NLL(cap) - NLL(reference)`

A positive value is harmful deterioration; a negative value is improvement.

Keep two distinct reference conditions where available:

- Original frozen base.
- The model's own cap-off base.

Calculate/report separately:

1. Fraction of positions with a harmful increase greater than 0.01 nat.
2. Mean severity conditional on exceeding that threshold.
3. Mean signed Delta_NLL.
4. Positive-part ES95/ES99 using the project's registered conventions, including zero mass.
5. Maximum harmful change.
6. Mean KL divergence in the original registered direction, `KL(reference || cap)`.
7. Concentration of harm, including how many positions account for 50% of the total KL.
8. Firing frequency and harmful-change frequency as distinct variables.

Do not change the existing definition of `ES99+` to the mean of only positive nonzero samples.

The existing HT-17 analysis has already fitted GPD versus exponential tails to saved positive harmful-change exceedances, including held-out-window tests and resampling.

**First reproduce and summarize HT-17.** Extend it only where the new study introduces genuinely different observables, datasets, populations or model conditions.

Do not pool repeated ordinary-text windows from different cells as independent observations. Use paired window identities when comparing models on the same validation corpus.

For the registered main study, three subject realizations are the independent population clusters; five orders within a realization are not five independent replicates.

The PC-reader study's paired training seeds share one subject population. Bootstrap uncertainty must respect this distinction and cannot turn token-level or order-level resampling into population-level replication.

## 6. Preserve negative and inconclusive findings

The existing project reports do not establish broad PC superiority.

In the PC-trained reader comparison, ePC has lower CounterFact paraphrase retention than BP in all three tested paired seeds, and measured reader training is approximately 96–102 times slower.

For zsRE, the results are mixed, with ePC paraphrase retention lower in two of three paired seeds.

These results must be retained and interpreted, not replaced by favorable results from a different PC acquisition experiment.

Separate:

- Reader training effects.
- Acquisition-credit effects.
- Reader firing frequency.
- Prediction harm conditional on firing.
- Factual-edit success and paraphrase retention.
- Computational cost.

The statistical analysis must clearly distinguish measured findings, exploratory analyses and hypotheses.

Existing Stage 4 registered classifier labels and preliminary uncertainty summaries must remain unchanged. New analyses can use additional bootstrap procedures but must be labeled separately.

## 7. Nelson paper and previous research

The repository already contains:

- A bounded κ-deformed answer-loss pilot.
- An HT-17 empirical heavy-tail investigation.
- Bounded-correction experiments.
- Discussion of Nelson's proposed calibrated entropy and informational scale.

Do not confuse the bounded κ-surprisal loss tested previously with the calibrated coupled entropy in Nelson's paper.

The prior κ pilot is not an empirical test of the full coupled-entropy or coupled-free-energy training objective.

Reuse existing HT-17 fitted tail shapes and confidence diagnostics. Describe these as finite-range statistical fits, not established asymptotic complexity classes.

The coupled-entropy sensitivity calculation in the original handoff remains optional and exploratory. It is not needed to validate the primary model comparison, and it should not be mixed into HT-17's fitted-tail results without a clearly specified probability distribution and calibration.

Report any novel dataset-entropy and distribution-shift measurements separately from the established nonlinear statistical coupling research.

## 8. New work and preservation of the registered experimental freeze

The original research has a declared October 9, 2026 experimental freeze.

Never modify the frozen registered matrix, sealed inputs, existing checkpoints, historical result files, metric classifications or provenance records.

Any GPU evaluations performed now belong to a clearly labeled **new supplemental study**, with their own manifest, output directory, code revision, run ID and report.

A new baseline evaluation or missing MQuAKE experiment must not retroactively convert an unavailable original-study cell into a completed registered result.

Use the existing JAX implementation for model execution, retaining the original algorithms and backend. Standard CPU statistical analysis can use compatible numerical libraries.

Save raw and derived outputs continuously as required by the original handoff.

## 9. Revised priority order

1. Audit and reconcile existing Stage 4, PC-reader, PC-v1, PC-v0 and HT-17 artifacts.
2. Complete the ordinary three-model comparison on genuinely matched GPT-2 Small conditions, including missing direct frozen/no-CAP tests.
3. Evaluate MQuAKE gaps if technically valid using existing model checkpoints, as new supplemental results.
4. Calculate dataset distributions, rarity, entropy, KL/JS and baseline surprisal.
5. Extend extreme-event measurements to the matched three-model comparisons, building on HT-17.
6. Compare performance in extreme cases, correction magnitudes, locality and computational costs.
7. Perform additional Nelson-related calculations only after the main empirical analyses are complete.
8. Generate the complete, detailed research report, figures, data dictionary, raw data and reproducible scripts.

**Keep all original deliverable requirements.**

The completed report must make it easy to distinguish what was previously established, what was recomputed from saved data, and what was newly evaluated. It must compare no-CAP, PC-CAP and BP-CAP wherever genuinely possible, without obscuring negative outcomes or mixing incompatible experimental families.