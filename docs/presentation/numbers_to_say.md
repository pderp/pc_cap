# Numbers to say — October 1 evidence snapshot

Use rounded values below. These are measured results or explicitly labeled scope; no pending value is zero. Source keys refer to the precise records below and to `manifest.json`/`rehearsal-manifest.json` for hashes.

- **Main learned-reader paraphrase retention:** zsRE **96.0%**, CounterFact **67.8%** after 1,000 edits; MQuAKE **71.6%** at its separate 300-edit endpoint. Three realizations, five dependent orders each. [S]
- **Fidelity:** all **45/45** main learned-reader cells exceed mean KL **0.001**. Integrity and preservation are different checks. [S]
- **AW-B mixture severity:** zsRE **1.619→0.542 nats**; CounterFact **1.925→0.581** conditional on loss increase >.01 nat. Roughly one-third, not half; harmful-change frequency is nearly unchanged. Ten exposed 300-edit memories, five orders/dataset. [H]
- **Analytic mixture ceiling:** **one nat per token at the same prefix** for base weight exp(−1). Not a one-nat whole-answer guarantee. [B]
- **PC-reader:** **8/12** evaluations available; only seed0 paired. Completed ePC/BP training process-time ratio **102.1×**; 37× was a forecast. No three-seed finding yet. [P]
- **Main execution:** **270 cells, 392.42 process-hours**. Concurrent process time, not elapsed GPU time; supplemental work is additional. **GPT-2 small, 124M**; transfer to production scale unestablished. [A]
- **Schedule:** experiment cutoff **October 9, 17:00 EDT**; presentation **October 15**. [A]

[S] `logs/R1/reports/triplet/summary.json`: learned condition, dataset, `primary.RET-GS`; benchmark counts per group.
[H] `logs/additional_work/HT-17/snapshot-20261001-v2/report.json`: AW-B groups, threshold .01, `conditional_mean_loss`.
[B] `docs/additional_work/AW-B_report.md`: declared mixture and scope.
[P] `logs/additional_work/PC-reader/report-round57-final/report.json`: coverage and `training_cost_ratios[seed=0]`.
[A] `docs/R1_stage4_report.md`: accounting and limitations.

For detailed PC effects use the resolved scripts' source slots. Do not improvise a favorable PC conclusion, an asymptotic tail class, W(N), or a completed Option R/upper-layer result. Refresh after new evaluations and the October 2 review.
