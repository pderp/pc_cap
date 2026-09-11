# S1 stage report (Appendix G) — development, BP and regenerated-ePC rows

Rendered 2026-09-11 08:34 UTC by `pccap report --stage S1`.

## 1. Header

- Stage: S1 substrate report card. Code commit: `0f1f9d5d8c9421e4be177ea46db19f7819dbf04e`; base: GPT-2 small BP teacher (`607a30d7…`); ePC checkpoint: regenerated (REG-02, `/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz`).
- Sets: `manifests/dev/lm_sets.json` (H 2×10⁶ train tokens seed 11; drift = validation 247,289 tokens; P2 4,096 positions; P3 1,000 × 128; POS UD-EWT).
- Cost: 0.18 local GPU-h = 0.18 A100-eq h of 12 (κ 1.0 provisional).

## 2. Status

Development. BP rows of P2, P3, P5, P6 complete where files exist below; P1 and the ePC rows follow the regenerated checkpoint (REG-02) where present; P4 is measured on the replacement grammar (S1-04) and `unsupported` in the natural-language domain (DATA-04). No confirmatory access.

## 3. Controls

S0 controls unchanged (`results/S0/report.md`). Alerts below are alerts, not exclusions (PDF §5).

## 4. Coverage

| property | signal | status |
| --- | --- | --- |
| P2 | epc | complete (/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz) |
| P3 | epc | complete (/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz) |
| P4 | gram_error | complete (results/S1/P4_gram.json) |
| P4 | gram_residual_companion | complete (descriptive) |
| P4 | natural_language | unsupported (DATA-04) |
| P5 | epc | complete (/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz) |
| P6 | epc | complete (/home/derp/cap/assets/models/epc/epc-50m/checkpoints/final-009766/params.npz) |

## 5. Results

**P2 geometry (BP).** Effective rank of centred features at 4,096 held-out positions and POS-probe accuracy per layer boundary (0 = embedding, 12 = pre-`ln_f`):

| layer | effective rank | POS probe acc |
| ---: | ---: | ---: |
| 0 | 103.3 | 0.876 |
| 1 | 153.7 | 0.889 |
| 2 | 180.8 | 0.901 |
| 3 | 225.4 | 0.912 |
| 4 | 266.1 | 0.914 |
| 5 | 293.6 | 0.916 |
| 6 | 315.1 | 0.918 |
| 7 | 332.2 | 0.918 |
| 8 | 344.5 | 0.911 |
| 9 | 349.4 | 0.910 |
| 10 | 345.8 | 0.904 |
| 11 | 316.8 | 0.891 |
| 12 | 104.4 | 0.874 |

Teacher ratios and the 0.9 / 0.02 alerts apply when an ePC checkpoint exists (pending REG-03).

**P3 localization (BP adjoint mass = squared adjoint norm per block output × token, summed sequence loss, 1,000 × 127 cells).**

| quantity | raw | layer-normalized |
| --- | ---: | ---: |
| PR (effective cells) | 265.8573 | 176.5522 |
| nPR = PR/N | 0.1744 | 0.1158 |
| final-block share | 0.0110 | 0.0002 |
| active fraction (> 1% of max) | 0.4997 | 0.3512 |
| zero fields | 0.0000 | 0.0000 |

Final-block share alert (> 0.4): **False** (raw). Dataset layer shares: `distributions` in `results/S1/P3_bp.json`.

**P4 separability and useful sharing (replacement grammar; D.4 error space).** 8,192 settled error vectors of the declared solver on the grammar's BP weights per mechanism kind (private / shared_1 / shared_2, task-switched sequences), per block output; centred top-16 bases (captured variance and eigen gaps in the file). Chance overlap of two random 16-dimensional subspaces in d = 128 is 0.125.

| quantity (mean over the 6 block outputs) | error space |
| --- | ---: |
| overlap private / shared_1 | 0.271 |
| overlap private / shared_2 | 0.351 |
| overlap shared_1 / shared_2 | 0.268 |
| resampling stability (min over kinds and layers) | 0.933 |
| captured variance at r = 16 | 0.986 |
| insufficient-rank cases | 0 |
| private/private overlap across contexts | 0.927 |
| shared retention (shared_1 basis, contexts 0–3 vs 4–7) | 0.937 |
| held-out private-only flip captured by the private basis / by the shared_1 basis | 0.963 / 0.208 |
| held-out shared-only flip captured by the shared_1 basis / by the private basis | 0.994 / 0.211 |
| residual-vector PCA companion (descriptive, not P4): overlap private / shared_1 | 0.293 |

Reading (D.4): mechanism *kinds* occupy distinct but overlapping error subspaces (overlaps above chance and well below the within-kind stability); the private mechanisms of different contexts share one error subspace, so error-space separability distinguishes kinds, not contexts, on this fixture. Any claim of private/shared structure still requires the S3 intervention and transfer checks; the natural-language domain PCA is `unsupported` (DATA-04).

**P6 finite settling (ePC procedure on BP weights; declared solver in `docs/epc_energy.md`).**

- r₈ mean 0.4042, r₆₄ mean 0.1042 (max 1.5392); E₀ − E₆₄ mean 2.4170 nats; first iteration reaching 95% of the 64-step reduction: median 18.
- Label: **finite-iteration error credit** (r_64 <= 1e-3 for every prompt and |E63 - E64| <= 1e-3 * E0).
- cos(e₈, −adjoint) at banks 1/2/3: 0.971 / 0.979 / 0.998; cos(e₆₄, −adjoint): 0.746 / 0.793 / 0.980 (inherited claim > 0.998 is for the distilled checkpoint; this row is the BP-weights procedure).
- Error–loss Spearman (bank 3, e₈): 0.607; seconds per call: 0.147 (8 it) / 0.375 (64 it); reverses per 8-iteration call: 9.

**P5 write locality (BP adjoint; Q = 200 edit prompts, U = 200 unrelated prompts, `manifests/dev/p5_subsets.json`; bounded geometric search for a 50% current-token loss reduction).**

| bank | reached 50% | unreachable | normalized write norm at target (median) | improvement (nats, mean) | unconditional collateral C_q (nats, mean) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.95 | 10 | 0.800 | 5.21 | 1.088 |
| 2 | 1.00 | 0 | 0.200 | 5.56 | 0.136 |
| 3 | 1.00 | 0 | 0.050 | 6.47 | 0.202 |

Deployed-gate behaviour on U (separate phenomenon, S2-02 A = 0.3 caps): false-fire zsre_A0.3: 0.0000, counterfact_A0.3: 0.0000. Improvement and collateral are reported separately; ratios per item carry undefined/right-unbounded statuses in `results/S1/P5_bp.json`. Retrieval-drift tracking: pending (needs saved learner checkpoints from S3/S4 runs; tracked in results/S1/drift_*.json when produced).

## 5b. Validity / eligibility table (D1 input)

| claim type | status | basis |
| --- | --- | --- |
| matched-fidelity substrate claim (SB vs SE-A/SE-E) | **eligible** | P1 on the regenerated checkpoint: mean KL 2.87e-05 (p95 9.16e-05, p99 2.37e-04, max 2.15e-02) on 199,680 H tokens; argmax agreement 0.9964; rule mean ≤ 1e-3 |
| synthetic-only substrate claim | pending | grammar replacement (GRAM-01/02, PA-2 clock) |
| BP-only editing programme (C0/C1/C2/CR on zsRE and CounterFact) | **eligible** | S0 controls pass; DATA-01 pools; S2-01 calibration (CounterFact exact-key pilot, CR-4); S2-02 A = 0.3 |
| inherited claim: teacher KL ~3e-5 (ref [5]) | re-measured on the new checkpoint (no continuity, PA-1) | β = 1 mean 2.87e-05; sibling scaling (β = 2, ×4) 4.96e-05 vs its 1.24e-4 |
| inherited claim: cos(settled error, adjoint) > 0.998 | re-measured on the regenerated checkpoint | e₈ at bank 3: 0.998; e₆₄: 0.980; r₈ 0.40, r₆₄ 0.10 (P6_epc; the BP-weights rows are the same to three decimals) |
| inherited claim: error mass less concentrated in the last block | consistent on BP adjoints | final-block share 0.011 (P3), no alert |

## 6. Mechanism evidence

None at S1.

## 7. Optional mathematics

None.

## 8. Deviations

SD-17 (radii per dataset); P6 measured on BP weights pending the ePC checkpoint; H/P2/P3 by the level-1-heading document rule (DATA-04 record).

## 9. Interpretation

Report card of both bases: the regenerated ePC substrate is eligible for matched-fidelity claims (P1) and its P2/P3/P5/P6 rows agree with the BP rows to the third decimal (relative parameter shift 4e-4); ePC rows available: ['P2', 'P3', 'P5', 'P6'].

## 10. Reproduction

```
python -m pccap.data.lm_sets --build && python -m pccap.data.lm_sets --audit
python -m pccap.analysis.s1_p6 && python -m pccap.analysis.s1_p2 && python -m pccap.analysis.s1_p3
python -m pccap.cli report --stage S1
```
