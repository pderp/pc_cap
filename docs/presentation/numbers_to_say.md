# Numbers to say — October 4 evidence snapshot

Use rounded values below. These are measured results or explicitly labeled scope; no pending value is zero. Source keys refer to the precise records below and to `manifest.json`/`rehearsal-manifest.json` for hashes.

- **Main learned-reader paraphrase retention:** zsRE **96.0%**, CounterFact **67.8%** after 1,000 edits; MQuAKE **71.6%** at its separate 300-edit endpoint. Three realizations, five dependent orders each. [S]
- **Fidelity:** all **45/45** main learned-reader cells exceed mean KL **0.001**. Integrity and preservation are different checks. [S]
- **AW-B mixture severity:** zsRE **1.619→0.542 nats**; CounterFact **1.925→0.581** conditional on loss increase >.01 nat. Roughly one-third, not half; harmful-change frequency is nearly unchanged. Ten exposed 300-edit memories, five orders/dataset. [H]
- **Analytic mixture ceiling:** **one nat per token at the same prefix** for base weight exp(−1). Not a one-nat whole-answer guarantee. [B]
- **PC-reader:** **12/12** evaluations available; fully paired seeds: 0, 1, 2. Completed training ePC/BP process-time ratios **95.8–102.1×**; 37× was a forecast. All three seeds paired; interpretation requires review. [P]
- **Option R:** **20 complete, 1 incomplete, 9 deferred**; four-realization learned−random paraphrase sensitivity: zsre **44.07 percentage points**; counterfact **56.20 percentage points**. Unadjusted t(3), assumed normal realization errors; not a reissued classifier. [R]
- **Upper-layer writes:** last-only mean-loss ratio **2.64–4.37×** all-write across twelve paired comparisons; **24 cells**, six shared controls. All readers trained with full-write objective. [L]
- **Main execution:** **270 cells, 392.42 process-hours**. Concurrent process time, not elapsed GPU time; supplemental work is additional. **GPT-2 small, 124M**; transfer to production scale unestablished. [A]
- **Schedule:** experiment cutoff **October 9, 17:00 EDT**; presentation **October 15**. [A]

[S] `logs/R1/reports/triplet/summary.json`: learned condition, dataset, `primary.RET-GS`; benchmark counts per group.
[H] `/home/derp/cap/pc_cap/logs/additional_work/HT-17/snapshot-20261004-complete/report.json`: AW-B groups, threshold .01, `conditional_mean_loss`.
[B] `docs/additional_work/AW-B_report.md`: declared mixture and scope.
[P] `/home/derp/cap/pc_cap/logs/additional_work/PC-reader/report-round63-final/report.json`: coverage, per-seed endpoint numerators/denominators and `training_cost_ratios` for completed trainings.
[A] `docs/R1_stage4_report.md`: accounting and limitations.
[R] `/home/derp/cap/pc_cap/logs/additional_work/R/report-round63-final/report.json`: inventory and final-checkpoint sensitivity.
[L] `/home/derp/cap/pc_cap/logs/additional_work/AW-L/report-round63-final/report.json`: write comparisons and cost-gate disclosure.

Detailed spoken numbers use `docs/talk_claim_ledger_v7.md` and `docs/presentation/deck_v3/pc-result-sources.json`. Rerun `aw.script_numbers_check` after every export; its occurrence inventory states rounding tolerances and untraced/review items. Numerical ledger matches alone do not establish contextual correctness. Do not improvise a favorable PC conclusion, an asymptotic tail class or W(N). The October 2 review requested no changes to the programme or framing (DEC-082). Planned GPU work completed October 4; charlie's freeze review remains.
