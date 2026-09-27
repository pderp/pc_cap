# Owner reconciliation of the DEC-074b halt (Capstan, 2026-09-27 00:00 EDT)

- Trigger: one SIGINT to the scheduler (pid 3641891, identity verified) at the 270th start receipt, 2026-09-26 22:18:59 EDT.
- Unwind: the two active cells (S1_literal zsRE realization 2, orders 103 and 104) finished under their ceilings; the scheduler exited 23:43:25 (exit 254, KeyboardInterrupt in the executor wait, as at the block-2 cutover); lease released; `Q21_RESUME/interrupted.json` written by the consumer.
- Receipts: 270 starts, 270 finishes, 0 failures, 0 retries; 266 decision records. Missing `decision.json`: v0_stable MQuAKE r1 orders 103/104 (block-2 cutover) and S1_literal zsRE r2 orders 103/104 (this halt) — the interrupted parents never processed them; disclosed, not manufactured.
- Watch: observations for the two S1_literal cells verified read-only and applied with `scripts.ht8_fidelity_watch` (both breach the old 0.001 mean-KL bound like every zsRE S1 cell; no veto). 274 observations, 32 alerts.
- Boundary report: `logs/R1/operations/HALT_REPORT/` (D13 boundary, block 4 as the last complete block; 270 cells known; no accounting or watch gaps; `boundary_ready` true).
- Unrun by decision (DEC-074b): block-5 positions 46–60 (S1_literal CounterFact, 15 cells) and the extension (45). Every registered contrast that needs them is reported unavailable.
- GPU handed to the PC refocus at 23:55 (PC-v0 diagnostic, profile, 60-cell replication).
