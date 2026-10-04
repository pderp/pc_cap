# PC-16b — complete three-seed reader and tail refresh

**Status:** complete. **Agent:** Capex. **Date:** 2026-10-04. **Authority:** Round 63 and lead-queue item 160.

**Inputs:** all six terminal reader trainings, twelve evaluation/report/cost pairs and saved harm vectors; the original selected-v5 historical reference; HT-17's fixed analysis recipe. No model or GPU call.

**Outputs:** `logs/additional_work/PC-reader/report-round63-final/`, `logs/additional_work/HT-17/snapshot-20261004-complete/`, both canonical readable reports, refreshed tail figures, slide drafts/diagrams, ledger, Q&A, number sheet and rehearsal pack. `report-round63-initial` was the first analysis pass; the final directory includes the dataset-specific interpretation and exact source bindings.

**Finding:** all twelve evaluations and three seeds are paired. ePC−BP RET-GS is −2.67/−2.00/+0.33 percentage points on zsRE and −24.17/−2.17/−17.50 on CounterFact. Thus the deficit recurs on CounterFact in all seeds, and on zsRE in two of three. Own-prompt retention is nearly equal. CounterFact firing and harm change direction across seeds; zsRE has less ordinary-text firing/harm with ePC. Training ratios are 102.1×/95.8×/96.7×. No safer-learning, general superiority or new-subject inference is assigned.

HT-17 has 303 cells: all 301 preceding cell statistics and all non-reader group summaries reproduce exactly. It includes all twelve reader vectors and no pending reader cells; Option R/AW-L remain in their own reports, without expanding this tail-fit population. Conditional window intervals do not cover seed/subject uncertainty. The three-seed CounterFact harmful-change frequency difference is +.02134 percentage points, while conditional severity differs by −.1066 nats with an interval spanning zero. zsRE severity still lacks an interval because two bootstrap draws have no harmful events.

**Verification:** `python -m aw.pc_reader_report --refresh-tail <new-tail-directory> --output <new-report-directory>` with the CPU environment; final rendering used `--tail logs/additional_work/HT-17/snapshot-20261004-complete/report.json`. Focused tests include a three-seed dataset-specific reversal regression. Round 63: 31 focused tests and scoped Ruff pass, X25 all 25 groups PASS, X26's three unmatched rounding/sign occurrences explicitly traced. `logs/additional_work/round63/validation.json` checks coverage, prior statistics and all 40 pack exports/2,294 source bindings. Visual review covers the revised slides and new upper-layer backup.

**Done-when:** report, tails, current presentation statements and pack all use 12/12. **Cost:** CPU only; tail pass 89.93 seconds; GPU 0, model calls 0. **Deviations:** none; date-stamped historical meeting documents retain their historical counts. **Unresolved/questions:** none for this lane. Final scientific freeze approval remains charlie's. No commit.
