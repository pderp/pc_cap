# Stage 4 protocol v5.2-D.3 — DEC-064 cap-fidelity scope

September 18, 2026. Adopted choice: **Q17 option 1**, DEC-064 (lead, 07:20 EDT). Experimental completion remains **October 9**; October 10–14 is reserved for analysis and presentation before October 15. This amendment grants no draw, seal, freeze, execution, budget or signature authority.

This document incorporates [v5.2-D.2](R1_stage4_protocol_v5_2_D_2.md) and its complete normative dependency closure. The replacements below supersede its cap-fidelity admission language and any conflicting inherited language. The DEC-063 full-validation population, cadence, coverage, vectors, reference identities and independent overlap checks remain required. Historical readiness statements are not current gate closures.

## Fidelity: distinguish base certification from cap benchmarks

**Continued-base certification is unchanged (DEC-047).** With the cap disabled, continued S1 base versus original base must meet the registered mean KL ≤0.001 nat and mean signed NLL increase ≤0.01 nat on its registered certification population. Existing continuation, identity, cost and protocol admission requirements remain in force. No cap benchmark result can admit an uncertified base.

**Cap fidelity is a declared secondary benchmark, without an admission veto (DEC-064).** For every cell, evaluate the fixed full-validation endpoint at the final declared checkpoint against both the original base and the cell's own cap-off base. Report mean KL(reference || cap) against **0.001 nat**, and mean signed NLL increase against **0.01 nat**, with explicit pass/fail labels for each reference and each quantity. Equality passes. Also retain the joint numeric benchmark pass flag, separately from evidence completeness and primary comparison admission. For S1 the references are distinct and both forwards remain required.

A numeric cap benchmark failure never sets `scientific_admission = False`. Retention, generalization and locality comparisons and the DEC-058 classifier are computed regardless of those benchmark labels. This applies when KL fails, NLL fails, or both fail, against either reference. Missing or corrupted evidence remains unavailable/invalid under the unchanged measurement-integrity requirements; this is not a numeric benchmark failure. Unadmitted recipes, incomplete primary observations and uncertified continuation bases do not become admitted. MQuAKE's absent 1,000-edit primary endpoints remain unavailable under option D.

The D.3 analysis matrix binds the DEC-064 policy at its root and in every core and extension cell. Missing or inconsistent D.3 policy bindings are invalid. Pre-D.3 matrices may be replayed with explicitly labelled historical behavior; such replays are not current-policy analyses. Publish a newly bound successor matrix and package for current use, without rewriting old reports or artifacts.

## HT-7 descriptive concentration and tail reporting

Keep D.2's mean, strict exceedance counts, maximum/location, positive-harm ES95/ES99 and zero-mass summaries for both references. Add the following deterministic descriptive summaries on **all full-validation positions**, separately for each reference. Display fixed-prefix summaries separately; do not substitute that prefix for full validation.

- Number and fraction of positions with absolute signed target-token NLL change **<1e-6 nat**. This means nearly unchanged loss on the observed token; it does **not** demonstrate an unchanged full prediction distribution or absence of reader firing.
- Smallest integer number and fraction of positions carrying at least 50% of total KL after descending sorting; KL mass shares in the top **0.1% and 1%** of positions; finite-population Gini over all positions, including zeros. Also report position concentration for positive NLL harm.
- Per-window mean KL for the 127 scored positions: number of windows ≤0.001 nat, strict counts >0.01 and >0.1 nat, median/p90/p99/maximum, and KL mass shares in the top **1%, 5% and 10%** of windows. Equal window lengths make shares of window means identical to shares of window sums.
- Top fractions use fractional boundary mass: sum the first floor(qN) descending observations and the remaining fractional next observation, divided by the total mass. Quantiles interpolate linearly at (N−1)q. Gini is Σ(2i−N−1)x[i] / (N Σx[i]) with ascending x and i=1…N; no sample-bias correction. When total mass is zero, shares, half-mass count/fraction and Gini are undefined (`null`), with zero mass/counts still reported.

These statistics introduce no hypothesis, cutoff, multiplicity-family member or classifier term. A small set of large changes is a description of these positions; it does not by itself identify a power law, mechanism, causal effect of reader firing, or a κ benefit. The October talk remains framed by DEC-054. Development profiles remain development evidence, including when their full-validation coverage is complete.

## U13 — inference and fidelity scope

Use the unchanged DEC-057 nominal 63-interval primary family and DEC-058 classifier inequalities and priority. Numeric cap KL/NLL benchmark labels are visible alongside primary comparisons, never used as their veto. Preserve DEC-047 continued-base certification and every independent population, identity and completeness requirement. Tests must show unchanged primary metrics/intervals/labels when only cap benchmark flags change, retained unavailability for incomplete/invalid evidence or unadmitted cells, unchanged MQuAKE missingness, and explicit labels for both references at and beyond each benchmark boundary.

## U16 — measured costs and admission

D.2's full-validation cost requirements remain in force: all four chain-S profiles, typed cost receipt v4, intermediate sampled phases, full outer phases and durable writing, host/device observations, failed attempts, reviewed CounterFact and other transfers, S1's additional original-base forward, 1,000-record occupancy, and unresolved near-miss/revision coverage. A numerically failing cap benchmark remains usable cost evidence when measurement integrity passes. Neither a passing nor a failing benchmark supplies missing costs, scientific certification or signatures. Retain 1.5× solo ceilings, the single 1.15× two-worker adjustment, retry charging, shared 750 process-hours and the October 9 stop. Candidate v14 must bind this amendment and its analysis implementations alongside the subsequent cost and backend identities.

## D.3 change log, alternatives and normative closure

- Implements the lead's DEC-064 option 1. Withdraws D.2's unadopted extension of the base fidelity gate into a cap-fidelity veto; the original continued-base gate remains unchanged. D.2's statement that it changed no classifier did not describe the admission-predicate effect; R1-49l documents that provenance.
- Preserves numeric benchmark thresholds, values, references, validation population and tail summaries; changes the effect of numeric cap benchmark failure on primary admission.
- Registers HT-7 concentration definitions as descriptive statistics, with explicit zero-total behavior and limits on interpretation.
- Option 2 (NLL cap gate, KL descriptive) and option 3 (retain the D.2 joint cap gate) were considered and **not adopted or built**. Legacy replay support is historical compatibility, not implementation of option 3 as a selectable new policy.
- Changes no edit population, condition identity, RNG/allocation, missingness, primary inequality, family size, retry allowance or deadline. Costs, successor package and signatures remain pending their own evidence.

`scripts/r1_49m_normative_closure.py` binds D.3 → D.2 → D.1 and its ancestors: **eight normative documents**. The planned D.3 matrix carries the exact DEC-064 decision row, policy and concentration contract, analysis source hashes and new definition hashes for all **360 core + 45 extension** cells, with no cell admitted. Changed normative or implementation bytes require new package/request digests before signatures.
