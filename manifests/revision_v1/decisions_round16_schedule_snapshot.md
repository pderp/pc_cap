# Round16 schedule decisions — immutable source-row snapshot

Copied from docs/decisions.md during the September16 round. Only DEC-051/052 are added here; register v6 retains its earlier immutable DEC-043…050 snapshot and unchanged scientific membership.

| Decision | Date | Decision | Source | Authority |
| --- | --- | --- | --- | --- |
| DEC-051 | 2026-09-16 | **Block order for the confirmatory matrix** (lead: "approval on Q6 as you propose"): per dataset, primary v5 + random-reader control + v0-stable on realization 0 across all five orders first; then matched-update and the two v0 live conditions; then realizations 1 and 2; then the two S1 continuation conditions; then the 45-cell no-gate extension. Any stop leaves a coherent subset with its cells listed by identity. | `docs/heavy_tail_counter_review.md` §5.1; `docs/lead_queue.md` Q6. | Lead decision. |
| DEC-052 | 2026-09-16 | **Feasibility (Q7) as proposed**: no scope cut (DEC-044 stands); execution in the DEC-051 block order; the measured cell cost is re-taken on September 20 after Codex's R1-68c; if the full matrix cannot complete before the October 9 stop, the matrix is reported as complete blocks plus an explicit list of incomplete cells — never as a complete matrix. | `docs/heavy_tail_counter_review.md` §5.3; `docs/lead_queue.md` Q7. | Lead decision. |
