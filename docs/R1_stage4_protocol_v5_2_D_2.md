# Stage 4 protocol v5.2-D.2 — DEC-063 full-validation amendment

September 18, 2026. Experimental completion remains **October 9**; October 10–14 is reserved for analysis and presentation before the October 15 talk. This amendment supplies the ordinary-text endpoint contract. It grants no draw, seal, freeze, execution or cost authority.

This document incorporates [v5.2-D.1](R1_stage4_protocol_v5_2_D_1.md), including its complete normative dependency closure. The replacements below govern ordinary-text validation population, cadence, storage, admission and resource evidence. All other rules remain as adopted: DEC-060 dataset layouts; DEC-061 near-miss semantics; DEC-062 coordinated allocation with multiple disjoint pairs per family; 360 core cells plus 45 separately admitted extension cells; selected condition identities; the nominal 63-interval primary family; and missingness/retry/accounting rules. Historical readiness statements in incorporated documents are not current gate closures.

## Full validation and the descriptive sample

Every admitted core or extension cell evaluates full ordinary-text validation at its **final declared checkpoint**: 1,000 attempted edits for zsRE/CounterFact and 300 for MQuAKE. Its existing 128-window drift sample is evaluated at every declared checkpoint, including the final one: 100/300/1,000 or 100/300 respectively. The final sample and full assay use the same checkpoint state. This implements DEC-063; the previously installed loops had sampled only at the final checkpoint, so intermediate sampled phases are an additional cost.

The source is the SHA-bound `drift_tokens` file in `manifests/dev/lm_sets.json`: 247,289 validation tokens. Take its first 247,168 tokens in source order as **1,931 nonoverlapping complete 128-token windows**. Reset context at every window. Score target positions 1 through 127 from prefixes starting at position zero, giving **245,237 predictions**. Drop the final **121 tokens** as one incomplete trailing window. Do not wrap, repeat, pad the tail into a scientific observation, join context across windows, select by observed loss, or use the test split. Batch padding is computational work only and contributes no observation.

The recipe, executable protocol, frozen manifest and independent population bind the source inventory/file SHA-256, source length, canonical complete-window hash, window size/count, denominator, tail/context policy, references and cadence. The constructor and seal check the sample against the first 128 windows of this source. The sampled denominator is **16,256 predictions**. Every cell, including each extension cell, carries the full contract; an omitted field cannot silently downgrade new production to sampled-only validation.

Selection is recomputed independently for every scored prefix using the audited batch implementation. Compare cap-on with both **the original base** and **the cell's own cap-off base**. For S1 these are distinct: own cap-off is the continued base. Record the two model identities and run the original-base comparison separately. When they are the same object the audited shared forward is permitted.

## Values, summaries and integrity

Retain complete finite float64 per-position NLL for cap-on, own cap-off and original base, plus KL(own-cap-off || cap-on) and KL(original || cap-on), in hash-bound compressed NPZ storage. The array order is `(window, target-position-minus-one, field)`, shape `(1931,127,5)`. No retained full-population hidden-state or logits array is required; inference memory is bounded by the declared physical batch. Tiny negative KL roundoff within 1e-10 may be clipped to zero as disclosed; larger negative/nonfinite values fail the assay.

For each reference report mean signed loss change, exp(mean signed change), mean positive loss harm, maximum and its position, strict exceedance counts above .01/.1/1 nat, and fractional empirical **ES95** and **ES99** of positive harm. The R1-68f producer stores ES95; the independent consumer computes ES99 as well, preserving the incorporated v5.1 reporting requirement. Report the corresponding complete KL means and tail summaries. For positive harms sorted descending and tail mass q=.05N or .01N, ES is the sum of the first floor(q) values plus the fractional next value, divided by q. Include zero mass; do not condition on harm being positive.

At the final checkpoint, compare the first 16,256 full-assay loss rows with the existing sampled assay at that same checkpoint. Require maximum absolute loss difference ≤.001 nat for all three losses and identical .01/.1/1 exceedance counts for the signed loss changes against both references. A missing, reordered, nonfinite or mismatched overlap fails the gate. The independent analysis recomputes this check from vectors and sampled rows instead of trusting a saved `pass` flag.

A completed checkpoint receipt binds the report, state, source identities and vector-file hash. Vectors must have the exact declared shape, ordered fields, finite values and complete coverage. Resume and independent analysis recheck the external vector dependency. Missing vectors or a missing full endpoint remain unavailable; they cannot be reconstructed from sampled means. Corruption is invalid evidence. Preserve interrupted/failed work for resource accounting.

## Fidelity, inference and the October talk

DEC-033's registered fidelity limits remain **complete finite mean KL ≤.001 nat** and **mean signed loss increase ≤.01 nat**, evaluated on the fixed full-validation population against both declared references. Equality passes. Report each reference's pass/fail result and the joint fidelity admission. A failed fidelity result remains visible as an observed result; it does not become a missing measurement or authorize a different sample. Completeness, fidelity pass and primary editing scores are separate report fields.

The full validation endpoint is the registered confirmatory cell fidelity measurement, conditional on the final approved population/recipe and complete evidence. It is a secondary endpoint; this amendment adds no hypothesis or interval to DEC-057's 63 primary intervals and changes no classifier or threshold. Tail magnitudes, exceedances, ES95/ES99 and KL-tail descriptions have **no new inferential cutoff** and establish neither a power law nor a general distributional claim.

The talk's previously analyzed **128-window tail population remains descriptive**. Label it explicitly as the first 128 validation windows, 16,256 positions, with development condition/seed/checkpoint identities. Display new full-validation results separately with their 1,931-window denominator and development/confirmatory status. Do not relabel previous sampled findings as full-split measurements or splice unscored positions into their statistics. Development cost profiles, even on the complete validation source, are not confirmatory experiment cells.

## U08 — cadence, population and evidence gate

Closure requires the exact DEC-063 contract in the final recipes, executable protocol, frozen manifest, independent population and analysis matrix for all admitted cells; the audited batched implementation for every family; final-checkpoint full coverage; all-checkpoint sample cadence; both references; compact-vector identities; independent overlap and finite-vector checks; and tests at the 300- and 1,000-edit cadences. The owner applies any sealed-backend admission change at an idle boundary and rebuilds affected backend/publication identities. No running job's bound driver/source files may change.

Implementation tests are engineering evidence. A development recipe or synthetic rehearsal does not close the real scientific admission gate. Missing full observations remain explicit even if the primary editing metrics and checkpoint JSONs are otherwise complete.

## U16 — measured costs and admission gate

Bind full-validation outer phase wall time, sampled intermediate-checkpoint additions, initialization/identity checks, durable vector/report writing, host memory, device memory and failed attempts. Capture all four R1-64g measurements on their exact new identities before pricing the proposed two implementation classes and datasets. Lifetime allocator/RSS peaks are labelled as lifetime high-water observations; unavailable telemetry is unavailable, not zero or a phase-isolated measurement.

CounterFact transfer must identify measured donors and the sampled-drift per-position ratio used, with the original timings and formulas bound. Other unmeasured conditions/states also require an explicit reviewed transfer basis or additional measurements. In particular, S1's separate original-base forward and 1,000-record occupancy may not be priced as if measured by a 300-record ordinary primary/v0_stable run. Do not erase outstanding near-miss/revision cost gaps. A signature cannot create absent numerical evidence.

Cost receipt v4 must have an explicit typed validator for its sources, complete vectors/coverage, cost arithmetic and any accepted transfer policy. Refresh cell ceilings v2, process-hour projection, concurrency schedule and remaining gap inventory. Preserve 1.5× stored solo ceilings, the single 1.15× two-worker adjustment, retry charging, shared 750 process-hours and the October 9 stop. A previous schedule estimate excluding DEC-063 cannot close U16. Later signatures authorize the exact reviewed version only.

## D.2 change log and normative closure

- Adds DEC-063's complete-window population, dropped tail, all-cell final cadence and intermediate sample cadence.
- Binds both reference identities and all complete finite loss/KL vectors through production consumers and independent analysis.
- Adds the overlap gate and ES95 reporting while preserving v5.1's ES99 definition and DEC-033 fidelity means.
- Labels the talk's existing sampled tail analysis as descriptive and separates it from full-validation evidence.
- Replaces U08/U16's unresolved cadence/full-split wording with concrete closure requirements; measured cost admission and signatures remain outstanding.
- Changes no condition, edit population, allocation RNG, primary comparison, multiplicity family, fidelity threshold, retry allowance or deadline.

`scripts/r1_49k_normative_closure.py` declares D.2 → D.1 and recursively binds D.1's six-file closure, for seven normative documents in total. Source/exposure records, decisions, matrix, implementation, costs and signatures remain separately bound evidence. Any changed normative bytes require a successor package and new request digests.
