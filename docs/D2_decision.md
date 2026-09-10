# D2 decision memo — development results, diagnoses, S6 recommendation, freeze readiness (S3-06)

Written 2026-09-10 12:54 UTC from `results/S3/short_editing.json`, `results/S3/fixture/summary.json`, `manifests/cr_distribution.json`, `results/S2/{throughput,projection}.json`, `results/REG/`.

## 1. Development results (100-edit streams per arm and dataset; one order; descriptive)

| arm | zsRE ES | zsRE RET-GS | zsRE LS | zsRE drift | CF ES | CF RET-ES | CF LS | CF drift |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | 0.99 | 0.43 | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.0000 |
| C1 | 1.00 | 0.31 | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.0000 |
| C2 | 0.99 | 0.30 | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.0000 |
| CR(uniform) | 0.99 | 0.18 | 0.93 | 1.0000 | 0.98 | 0.98 | 1.00 | 1.0000 |
| CR(learned) | 1.00 | 0.38 | 1.00 | 1.0000 | 1.00 | 1.00 | 1.00 | 1.0000 |
| B0 | 0.00 | 0.00 | 1.00 | 1.0000 | 0.00 | 0.00 | 1.00 | 1.0000 |
| B1 | 0.08 | 0.15 | 0.00 | 1.1442 | 0.08 | 0.11 | 0.00 | 3.1676 |
| B3 | 0.10 | 0.13 | 0.00 | 1.2089 | 0.07 | 0.10 | 0.00 | 3.9369 |

Constructed fixture (S3-02): C2 precision/recall vs oracle/random/majority in `results/S3/fixture/summary.json`; CR distribution (S3-05): zsRE {'1': 0.012953367875647668, '2': 0.012953367875647668, '3': 0.9740932642487047}, CounterFact {'1': 0.0, '2': 0.0, '3': 1.0}.

## 2. Correctness versus science — diagnoses (≤ 3 each, cheapest discriminating test first)

**F1. C2 routes almost only to bank 3 (97% zsRE, 100% CounterFact) and retains less on zsRE than C0 (RET-GS 0.30 vs 0.43), the last-depth-only control (bank 3 with the whole byte ceiling; PDF §7, `ARM_BANKS`).**
1. Hypothesis (not yet tested): since C0 and C2 both write almost only at bank 3, the gap is not a depth effect; candidates are C2's rare early routes (3% of rounds), its rejected candidates (5), and per-bank ceilings/slot layout (a third of the ceiling per bank in C2 vs all of it in C0 — no evictions occurred at 100 items, so capacity pressure is unlikely). Cheapest test: pair the two runs item by item on retained-ES, list the items C2 lost and their routes, and re-run C2 with the early routes forced to bank 3 (development only). The S3-02 fixture shows the router mechanism recovers planted depths (precision 0.88), so this is a landscape/protocol question, not a defect.
2. Correctness: probe scores could favour bank 3 through the normalization (tie rule SD-16 picks the smallest bank, so ties do not explain it). Test: the per-round signed scores in `decisions.jsonl` (bank 3 wins by margins ≫ ε in 97% of rounds); no defect.
3. Science (capacity/keys): CounterFact exact keys (SD-17) give zero retrieval generalization by construction (CR-4), so C2 vs C1 on CounterFact is an ES/RET-ES comparison only. No test needed; recorded as a dataset-level limitation.
Decision: not a defect; C2 vs C1 and C2 vs CR remain the required contrasts; C0 vs C2 identifies the effect of access to earlier depths (descriptive; PDF §7). Note (S3-05 re-profile; DEC-018): the learned-distribution CR (97% bank 3) reaches zsRE RET-GS 0.38 in the same order (uniform-CR profiling run 0.18; C2 0.30; C1 0.31; C0 0.43) — the two CR policies are distinct runs and are always named (`CR(uniform)` = SD-11 profiling, `CR(learned)` = confirmatory); the current point estimates do not favour C2, and the planned C2-vs-CR contrast is kept with a valid negative outcome accepted.

**F2. B1/B3 at the prescribed defaults (rank 8, lr 1e-4, 10 steps) acquire little (ES 0.08–0.10), lose locality entirely (LS 0.00) and drift (perplexity ratio 1.14–3.9).**
1. Correctness: the LoRA update could be mis-specified. Test: `tests/baselines/test_lora.py` (gradient inventory, merged-weight equivalence, NLL decrease on one item) passes; the harness parity test (`tests/harness/test_baseline_arms.py`) passes. Not a defect.
2. Science (step size): 10 Adam steps at 1e-4 from B = 0 move the answer NLL by ~1 nat per item (codex's smoke: 23.7 → 22.8) — too little to acquire, while Adam's per-item moments accumulate a drift direction across 100 items. Cheapest test: the PDF's own learning-rate screen {3e-5, 1e-4, 3e-4} on the same development allocation (lr3e-5: zsRE ES 0.03 LS 0.40 drift 1.075, lr3e-4: zsRE ES 0.23 LS 0.00 drift 2.148).
3. Science (loss): mean-over-answer-tokens CE including the newline dilutes the target tokens for short answers. Test: stratify ES by answer length in `items.jsonl` (available; descriptive).
Decision: B1/B3 are practical references, not validity gates (PDF: "Beating LoRA is not a validity gate; it is a result"); the frozen manifest fixes the learning rate by DEC-017 (highest mean development RET-GS, the primary endpoint: 1e-4 → 0.10, 3e-4 → 0.09, 3e-5 → 0.04; so the prescribed 1e-4 stands) and records the full screen (ES/LS/drift), including that an LS-constrained rule would have picked 3e-5 with ES 0.03.

**F3. ePC substrate rows unavailable at D1.** Regeneration is running (REG-02: step 5000 of 9766, status paused_chunk; pilot projection 12.2 h). Not a defect; S1-01 and the ePC rows follow REG-03.

## 3. Core feasibility

Projection with measured B1/B3 rows (D1 refresh): selected scope {'zsre': 1000, 'counterfact': 300, 'grammar': 10000, 'seconds': 90504.85192767635}, 25.1 local h of 27.0 h budget; assumed arms ['B4/counterfact', 'B4/zsre']. B4 (GRACE) waits on Lane D; grammar cost waits on GRAM-02. The BP-only confirmatory core (zsRE 1000 / CounterFact 300, C1/C2/CR/B3 × 15 + C0 initial 300) is feasible on this host inside the S4 ceiling.

## 4. S6 deficit recommendation

**Defer.** S6 (error-feature regularizer on the ePC substrate) requires the regenerated ePC checkpoint (REG-03) and the S5 matched-fidelity rows; the deficit statement cannot be drafted before those exist. Recommendation: no S6 authorization at D2; revisit at the S5 report.

## 5. Freeze readiness checklist (S4-01)

| item | status |
| --- | --- |
| S2-01 radii / b_m, S2-02 A = 0.3 | ready |
| S3-05 CR distribution (`manifests/cr_distribution.json`) | ready; re-profile with the development distribution: done |
| DATA-02 sealed realizations/orders (the DATA-02 SHA256SUMS) | ready |
| DATA-02a sealed loader (Lane H) | not on board |
| B4 GRACE adapter (S2-05, Lane D → orchestrator) | pending |
| Grammar base + streams (GRAM-02, DATA-06/07) | pending — PA-2 clock 2026-09-11 23:59 ET |
| B1 learning-rate screen | done |
| ANA-01 frozen analysis code | done |
| REG-03 ePC checkpoint preflight (S5 only; not required for the BP freeze) | pending |
| Draft manifest (`manifests/frozen.draft.json`, schema-validated) | see `python -m pccap.harness.freeze --draft` |

Freeze rule: `manifests/frozen.json` is written only by the lead's decision at CP-E after this checklist is all-ready except the items explicitly deferred (B4, grammar) — those arms are then recorded `unavailable` in the manifest rather than delaying the BP core.
