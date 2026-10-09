# STATUS — ext-20261009

Updated: 2026-10-09 22:50 UTC (18:50 EDT) · Capstan

## Current stage
GPU chain (`scripts/run_gpu_chain.sh`, log `logs/gpu_chain.log`): frozen scoring and reader scoring on zsRE/CounterFact (both horizons) **complete**; MQuAKE supplemental evaluations running (first: bp s0, started 22:34 UTC); then reader scoring on MQuAKE. CPU stages 2, 4, 5, 6, 7 have run on the complete zsRE/CounterFact data; interim report + PDF built (`reports/`). Everything is rerun once the MQuAKE evaluations finish.

## Stage plan and state
| stage | content | state |
|---|---|---|
| 1 | audit, inventory, analysis matrix, probes, validation tests | **complete** — `audit/`, `validation/gpu_checks.json` (9/9 pass), `aw/tests/test_extremes_stats.py` (10 pass) |
| 2 | frozen scoring + reader scoring (teacher-forced losses, generations, write norms); assembly | **complete for zsRE/CounterFact** (frozen 1,350/2,300 probes; 6 readers × 2 horizons); MQuAKE reader scoring after Stage 3; `scores.parquet` 65,230 rows |
| 3 | MQuAKE gap: six saved readers on the sealed MQuAKE stream (new supplemental, family EXT) | running (1/6 in progress) |
| 4 | dataset statistics | **complete** — `tables/dataset_statistics.{json,csv}`, `data/case_populations.parquet`, `data/frequency/` |
| 5 | tails: HT-17 reproduction + extensions | HT-17 PC-reader cells reproduced exactly (12/12 field-equal); probe-loss fits written; MQuAKE harm pending Stage 3 |
| 6 | paired analysis | run on zsRE/CounterFact: 576 gain rows, CVaR A/B, deciles, regressions, correlations, joint extremes, sequential |
| 7 | Nelson supplementary | complete (informational-scale identity holds for all fits; coupled-entropy profiles 60 rows; self-tests pass) |
| 8 | figures, report, PDF | interim: 9 figures, `reports/research_report.md` + `.pdf` build; final after Stage 3 |

## Completed evaluations (probes per model / dataset; see manifest.json)
frozen: zsre 1,350; counterfact 2,300; mquake 1,890. Readers: see `logs/gpu_chain.log`.

## Latest outputs
`tables/benchmark_original.csv`, `tables/benchmark_standardized.csv`, `tables/preference_margins.csv`, `tables/dataset_statistics.json`, `tables/ht17_reproduction_checks.csv`, `tables/probe_loss_tail_fits.csv`, `tables/frozen_text_surprisal_tails.json`, `data/*.parquet`.

## Warnings / validation failures
none. The teacher-forced hand check tolerance is 1e-3 nats (float32 bucket-length reduction noise ≈ 1e-4, same scale as the agreement with the saved vectors).

## GPU / CPU status
GPU: chain running under the exclusive project lease. CPU: free for analysis reruns.

## Remaining work
Stage 3 (chain), reruns of 2/5/6 on complete data, Stage 7, Stage 8 (report MD+PDF), final STATUS, commits.
