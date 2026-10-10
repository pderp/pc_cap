# STATUS — ext-20261009

Updated: 2026-10-10 21:40 UTC (17:40 EDT) · Capstan

## Current stage
**Complete, plus the CAP-value supplement (10 Oct).** `reports/cap_value_report.pdf`, `tables/cap_value/`, `figures/cap_value/` (+ `slides/`) added from the recorded scores; horizon-100 denominators corrected and the main report regenerated. All GPU work finished (chain log `logs/gpu_chain.log`, chain end 01:45:52 UTC); the CPU pipeline (`scripts/run_cpu_pipeline.sh`) has been run on the complete data; the report (`reports/research_report.md` + `.pdf`) and all tables/figures/parquet are final. Only post-hoc wording edits to the report generator would change anything from here.

## Stage plan and state
| stage | content | state |
|---|---|---|
| 1 | audit, inventory, analysis matrix, probes, validation tests | complete — `audit/`, `validation/gpu_checks.json` (9/9 pass), `aw/tests/test_extremes_stats.py` (10 pass) |
| 2 | frozen scoring + reader scoring (teacher-forced losses, generations, write norms); assembly | complete — frozen 1,350 / 2,300 / 1,890 probes; six readers × two horizons × three datasets; `scores.parquet` (all models, all datasets) |
| 3 | MQuAKE gap: six saved readers on the sealed MQuAKE stream (new supplemental, family EXT) | complete — 6/6 (`mquake_eval/eval-*-mquake/report.json`, cost receipts; bp s0 resumed after a batch-size failure at the harm step, see its `resumed_from`) |
| 4 | dataset statistics | complete |
| 5 | tails: HT-17 reproduction (12/12 field-equal) + MQuAKE PC-reader harm + token-level probe-surprisal fits (own and common thresholds) + frozen text surprisal | complete |
| 6 | paired analysis (gains, CVaR A/B, deciles, regressions, correlations, joint extremes, sequential) | complete |
| 7 | Nelson supplementary (informational-scale identity; coupled-entropy profiles; self-tests) | complete |
| 8 | figures, report MD + PDF, data dictionary | complete |
| 9 | CAP-value supplement: three-model tables, figures, slide package, report (CPU only) | complete — `tables/cap_value/`, `reports/cap_value_report.{md,pdf}` |

## Completed evaluations (probes per model / dataset; `manifest.json` has hashes)
frozen: zsRE 1,350, CounterFact 2,300, MQuAKE 1,890. Each of bp_reader_s{0,1,2}, epc_reader_s{0,1,2}: the same probe sets at the 100- and 300-edit memories (zsRE/CounterFact memories from the frozen record; MQuAKE memories from this study). MQuAKE evaluations: 300 edits, checkpoints 100/300, endpoints 50/100/50/100, composition 80 cases, harm 245,237 positions, each.

## Metrics complete
Registered metrics for all 7 models × 3 datasets (frozen by definition where stated); teacher-forced NLL (total, per-token, with/without terminator) for every probe/target/model; margins; harm statistics and tail fits; dataset statistics; bootstrap intervals.

## Unavailable / incomplete (explicit)
- Probe-level GPD fits at P90/P95/P97.5: insufficient exceedances (15–60) with 300–600 probes; reported as descriptive extremes only. Token-level pooled fits replace them (≥ 100 exceedances).
- Per-family token-level fits other than the pooled population: exploratory or insufficient.
- MQuAKE PC-reader harm tails: two of six cells below the 100-excess screen (`not_identified`), as in the record's zsRE reader cells.
- No new realizations, orders or training seeds; intervals are within-population only.
- Sequential extreme analysis on ordinary text: not applicable (context reset per window); edit-order analysis given from the per-edit records.

## Latest outputs
`reports/research_report.md`, `reports/research_report.pdf`, `reports/data_dictionary.md`, `tables/*.csv`, `assets/extremes_analysis/ext-20261009/{data,figures,checkpoints}`.

## Warnings / validation failures
None open. `manifest.json` `warnings` lists interim-run notices (report sections unavailable before data existed); all resolved in the final run.

## GPU / CPU status
GPU released (chain ended). Process-time receipts: MQuAKE evaluations 1,147 s (resumed harm only) + 5 × ≈ 1,740 s; scoring runs 17–100 s each; validation 8 s.
