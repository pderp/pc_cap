# STATUS — ext-20261009

Updated: 2026-10-09 22:10 UTC (18:10 EDT) · Capstan

## Current stage
Stage 1 — audit and alignment: inventory written, analysis matrix written, validation tests being written. No GPU work yet.

## Stage plan and state
| stage | content | state |
|---|---|---|
| 1 | audit, inventory, analysis matrix, example manifest, validation/smoke tests | in progress |
| 2 | matched three-model benchmark tables (PCR + frozen); direct frozen scoring; teacher-forced losses for all three models on identical probes | planned |
| 3 | MQuAKE gap: six saved PCR readers evaluated on MQuAKE (new supplemental, GPU) | planned, feasibility confirmed by audit (see analysis_matrix) |
| 4 | dataset statistics: frequency, rarity, entropy, JS/KL, baseline surprisal | planned (CPU, can overlap GPU) |
| 5 | heavy tails: reproduce HT-17 summary; extend to PCR matched conditions and new observables | planned |
| 6 | CAP behaviour in extremes: paired gains, deciles, CVaR A/B, locality, residual norms | planned |
| 7 | Nelson supplementary: informational-scale identity, optional coupled-entropy profile | planned, last |
| 8 | report (MD + PDF), figures, data dictionary, raw data, reproduction guide | planned |

## Completed evaluations (cases per model / dataset)
none yet in this study; see `audit/analysis_matrix.md` for what the frozen record already holds.

## Latest outputs
- `audit/model_and_dataset_inventory.md`
- `audit/analysis_matrix.md`
- `config.json`

## Warnings / validation failures
none yet.

## GPU / CPU status
GPU idle for this study (another process, `swipl`, holds 1.5 GiB of the 12 GiB; not a project process). CPU: audit only.

## Remaining work
Stages 1 (tests, manifest) through 8.
