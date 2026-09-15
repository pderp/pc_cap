# Development analysis dry run — round 10

**NOT CONFIRMATORY.** One seed-21 development population per dataset; model seeds are not independent data realizations.

The compatibility repair in docs/tasks/R1-57b-legacy-input-compatibility.patch was compiled in memory for this report. The installed source remains unpatched pending permission.

| Dataset | Condition | Status | ES | RET-ES | RET-GS | LS |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| zsre | text_null_v2 | complete | 1.000 | 1.000 | 0.960 | 1.000 |
| zsre | rare_gate_v3 | complete | 1.000 | 1.000 | 0.960 | 1.000 |
| zsre | tri_v3_seed0 | complete | 1.000 | 1.000 | 0.980 | 1.000 |
| zsre | tri_v3_seed1 | complete | 1.000 | 1.000 | 0.970 | 1.000 |
| zsre | tri_v3_seed2 | complete | 1.000 | 1.000 | 0.980 | 1.000 |
| counterfact | text_null_v2 | complete | 1.000 | 1.000 | 0.725 | 1.000 |
| counterfact | rare_gate_v3 | complete | 1.000 | 1.000 | 0.715 | 1.000 |
| counterfact | tri_v3_seed0 | complete | 1.000 | 1.000 | 0.660 | 1.000 |
| counterfact | tri_v3_seed1 | complete | 1.000 | 1.000 | 0.850 | 0.980 |
| counterfact | tri_v3_seed2 | complete | 1.000 | 1.000 | 0.830 | 1.000 |
| mquake | text_null_v2 | missing_cell | unavailable | unavailable | unavailable | unavailable |
| mquake | rare_gate_v3 | missing_cell | unavailable | unavailable | unavailable | unavailable |
| mquake | tri_v3_seed0 | complete | 1.000 | 1.000 | 0.800 | 1.000 |
| mquake | tri_v3_seed1 | complete | 1.000 | 1.000 | 0.470 | 0.980 |
| mquake | tri_v3_seed2 | complete | 1.000 | 1.000 | 0.820 | 0.980 |

All 360 fresh registered cells remain missing; each of eight conditions has 45 missing cells and 135 missing checkpoints. The optional v2 contrast needs another 45 separately declared cells, also missing.

Historical v3−v2 changes are 0.000 RET-GS on zsRE and −0.010 on CounterFact. There is no matching historical MQuAKE v2/v3 cell in this inventory. The three-source reader gives MQuAKE RET-GS 0.800/0.470/0.820 and LS 1.000/0.980/0.980. These descriptive results support further calibration/seed-stability investigation, not selection of a favorable seed after confirmation.

Legacy locality aggregates lack per-query IDs; the source manifest supplies intended pairing and the JSON records that limitation. Missing unseen and composition rows stay unavailable. Later threshold sweeps and larger-pool retraining are distinct conditions, outside this snapshot.

Exact expected inventories, source hashes, endpoint coverage and paired comparisons are in [the JSON report](analysis_development_dry_run.json).
