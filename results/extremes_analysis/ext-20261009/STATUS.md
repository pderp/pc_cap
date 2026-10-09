# STATUS — ext-20261009

Updated: 2026-10-09 22:20 UTC (18:20 EDT) · Capstan

## Current stage
GPU chain running (`scripts/run_gpu_chain.sh`, log `logs/gpu_chain.log`): frozen scoring done for all three datasets; reader scoring on zsRE/CounterFact in progress (h300 done, h100 running); then six MQuAKE supplemental evaluations (≈ 0.5–0.7 h each); then reader scoring on MQuAKE. CPU stages 4–6 implemented and run on the data so far; they are rerun after each GPU milestone.

## Stage plan and state
| stage | content | state |
|---|---|---|
| 1 | audit, inventory, analysis matrix, probes, validation tests | **complete** — `audit/`, `validation/gpu_checks.json` (9/9 pass), `aw/tests/test_extremes_stats.py` (10 pass) |
| 2 | frozen scoring + reader scoring (teacher-forced losses, generations, write norms); assembly | frozen: complete (zsRE 1,350 / CounterFact 2,300 / MQuAKE 1,890 probes); readers: zsRE/CF h300 complete, h100 running; `aw.extremes.assemble` rerun after each milestone |
| 3 | MQuAKE gap: six saved readers on the sealed MQuAKE stream (new supplemental, family EXT) | queued in the chain |
| 4 | dataset statistics | **complete** — `tables/dataset_statistics.{json,csv}`, `data/case_populations.parquet`, `data/frequency/` |
| 5 | tails: HT-17 reproduction + extensions | HT-17 PC-reader cells reproduced exactly (12/12 field-equal); probe-loss fits written; MQuAKE harm pending Stage 3 |
| 6 | paired analysis | implemented; rerun when all seeds/horizons are assembled |
| 7 | Nelson supplementary | pending (last) |
| 8 | figures, report, PDF | figures module written; report generator pending |

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
