# R1-X21 — report skeleton against protocol D.4

**Review complete; eight edit requests remain.** The primary-family, MQuAKE, near-miss, concentration and watch structures are covered. Report-only gaps and the upstream composition omission are distinguished below. No installed source or existing report was changed.

Normative closure: 9 files. Inputs include the full synthetic D.4 analysis and its exact filled report; no new experiment or protected confirmatory payload was opened.

## Table and interpretation crosswalk

| Obligation | Output | Analysis key(s) | Protocol | Assessment / request |
|---|---|---|---|---|
| T1: D4 declared blocks and completed-block inventory | blocks (6 rows) | /blocks; /complete_blocks | D4 execution blocks; D1 DEC052 | covered / None |
| T2: Planned/missing/invalid cells and independent endpoint completeness | cell_inventory (330 rows) | /cells; /incomplete_cells | D1 DEC052 | partial / X21-G4 |
| T3: 21 dataset contrasts ×3 metrics, both intervals, three realization values, classifier, pairing | primary (63 rows) | /contrasts/*/metrics/*; /contrasts/*/classification; /primary_family | v5.1 §5.3; D4 U12 | covered / None |
| T4: 11 per-cell descriptive secondary benchmarks, counts/Wilson and availability | secondary_cells (3630 rows) | /secondary_benchmarks/cells/*/benchmarks | v5.1 §5.1 | covered_with_explicit_unavailability / X21-G7 |
| T5: Equal-weight dataset macros, paired equivalence intervals and failed-cell inventory | secondary_macros (297 rows) | /secondary_benchmarks/macros | v5.1 §5.1/5.3 | covered / None |
| T5a: Near-family independent denominators and bounded/terminated diagnostics | near_miss (330 rows) | /near_miss_family/cells | D1 DEC061/062 | covered / None |
| T5b: Actual checkpoint ES/RET-ES/RET-GS/LS values, counts and cell coordinates | trajectories (3720 rows) | /cells/*/checkpoints/*/primary | D4 U08 | covered / None |
| T5c: Endpoint counters, truncation and unsupported/unavailable observations | endpoint_observations (6360 rows) | /cells/*/checkpoints/*/secondary | v5.1 §5.1 | partial / X21-G6 |
| T6: MQuAKE actual300 occupancy, outside fires, Wilson and change from100; no1000 threshold | mquake300 (60 rows) | /secondary_benchmarks/cells/*/actual_occupancy_descriptive | D1 actual occupancy; D4 U08/U12 | covered / None |
| T6a: Five calibration-determined omitted conditions/75 coordinates; never measured zeros | omissions (75 rows) | /prospectively_omitted_cells | D4 scope | covered / None |
| T7: Both cap references and KL/NLL labels, joint numeric flag, no primary veto | fidelity (660 rows) | /cells/*/cap_fidelity_benchmark | D3 DEC064 | partial / X21-G2 |
| T8: Watch entries/creep alerts, exact-matrix/global scope, no implicit notification acknowledgement | watch_summary (1 rows) | watch:/entries; watch:/alerts; watch:/observations | DEC064a in decisions; D3 fidelity | covered / None |
| T9: Full/sample signed and positive means, ES95/99, exceedances, exp(mean), maximum/location and zero masses | tails (3180 rows) | /cells/*/checkpoints/*/secondary/full_validation/references/*/{loss,kl}; /cells/*/checkpoints/*/secondary/sampled_drift/references/* | v5.1 §5.2; D2/D3 tails | partial / X21-G1 |
| T10: Near-zero loss fraction, half mass/top shares/Gini, window KL summaries and undefined zero-total shares | concentration (660 rows) | /cells/*/checkpoints/*/secondary/full_validation/concentration/references | D3 HT7 | covered / None |
| U03: Qualified historical LM/literal continuation controls, no exact-v5-compute claim | None (None rows) |  | D4 final paragraph; U03 memo | partial / X21-G5 |
| Secondary-extension: Historical-v2 secondary paired package contrast at each declared checkpoint | None (None rows) | /historical_pointwise_contrasts/*[contrast.role=secondary] | v5.1 §5.3; D4 optional extension | missing_formatter_output / X21-G3 |
| Composition: Predetermined dependency-closed composition, fixed planned cases/questions, conflicts/unavailability | None (None rows) | raw checkpoint:/endpoints/composition; absent from installed analysis JSON | v5.1 §5.1; D1 population | missing_analysis_output / X21-G6 |
| Accounting: Known charged process costs, unknown records, retry exhaustion/host failure and block reconciliation | None (None rows) | D11/D13 reporting outputs; not joined by scientific formatter | D1 DEC052; D4 U16 | missing_report_integration / X21-G4 |

## Figure crosswalk

| Figure | Bound table | Interpretation |
|---|---|---|
| disposition | blocks (6 rows) | artifact counts only; not full cost/retry accounting (G4) |
| primary-intervals | primary (63 rows) | 63 slots; unavailable MQuAKE explicit; existing adjusted intervals only |
| checkpoint-trajectories | trajectories (3720 rows) | means of available cell values, not an uncertainty interval or independent-orders analysis |
| cap-fidelity | fidelity (660 rows) | two references and threshold lines; explicit joint flag still needed in table (G2) |
| full-validation-tails | tails (3180 rows) | per-cell summaries, not pooled tokens; omitted tail fields requested for table (G1) |
| watch-sequence | watch_observations (330 rows) | KL sequence only; NLL remains in watch tables; observation index is not elapsed time |

## Verified observations

- 330 planned cells, 63 primary metric rows, 21 explicitly unavailable MQuAKE1000 rows and75 prospective omissions are retained.
- Eight secondary historical-v2 source contrasts /24 metric rows are not consumed by the current formatter.
- Full-validation exponential mean, maximum locations/ties and zero-mass fields exist upstream but are omitted from the current tail table. The joint numeric cap-benchmark flag is also omitted.
- A synthetic composition section is ignored by the installed checkpoint consumer. This is reproduced by the audit, not inferred solely from searching source text.
- U03 memo is linked but its bytes are not bound in the report source inventory.
- Accounting and resource-measurement integration remain explicit work; missing values are not treated as measured zeros or passes.

Exact requested fields, replacement wording, implementation boundaries and acceptance checks: [R1-X21-edit-requests.md](../../docs/tasks/R1-X21-edit-requests.md). All changes are proposed only.

Reproduce: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 ../venv/bin/python -m scripts.r1_x21_report_audit --output logs/NEW_X21_AUDIT.json`. This uses the locally retained round39 rehearsal, reconstructible from its task record. The audit checks all bound report sources before comparing coverage.
