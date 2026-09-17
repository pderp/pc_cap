# Revision v1 confirmatory execution plan v1 (2026-09-17)

Status: provisional cost admission from chains I / K (measured 300-edit development cells, batched drift); MQuAKE
corrected MQuAKE profiles pending the post-R1-77d run list; MQuAKE cadence under DEC-060 (300 edits × 3 realizations, checkpoints 100 / 300).
Matrix v5.2-D core = 360 cells in the DEC-051 block order; the 45-cell no-gate extension is separate and last.

## Per-cell cost (hours; 1,000 edits, three checkpoints, drift once; batched drift where applicable)

| condition class | zsRE | CounterFact | MQuAKE (300 edits, DEC-060) |
| --- | ---: | ---: | ---: |
| R1_learned_ff, R1_nonlearned | 0.35 | 0.35 | 0.15 (est.) |
| v0_stable, matched_update, v0_live_C1 / C2 | 0.48 | 1.22 | 0.6 (est.; chain M) |
| S1_LM, S1_literal | 0.50 | 1.28 | 0.65 (est.; chain M) |

Queue ceilings = 1.5 × these solo costs (× 1.1 under two-cell concurrency) (a cell exceeding its ceiling is stopped, charged and reported; resume is manual).

## Blocks (DEC-051), cells and hours

| block | content | cells | est. hours | cumulative |
| --- | --- | ---: | ---: | ---: |
| 1 | primary v5, random reader, v0_stable; realization 0; five orders; three datasets | 45 | 20 | 20 |
| 2 | matched_update, v0_live_C1, v0_live_C2; realization 0 | 45 | 35 | 55 |
| 3 | the six conditions above; realization 1 | 90 | 55 | 110 |
| 4 | the six conditions above; realization 2 | 90 | 55 | 165 |
| 5 | S1_LM, S1_literal; realizations 0–2 | 90 | 70 | 235 |
| ext | R1_learned_ff_v2 (no gate); realizations 0–2 | 45 | 16 | 251 |

Available: from a September 19–20 launch to the October 9 stop ≈ 480–500 wall-clock hours; at 75 % ≈ 360–375
usable hours; margin ≈ 110–140 h (≈ 45 %) before the extension, ≈ 30–40 % with it. Concurrency admitted (probes 1 and 2: 1.65× and 1.67× throughput, identical final state hashes in the saved pairs; attempt slowdowns up to 1.1335×,
host memory ≥ 20 GB): every block runs **two cells at a time**; per-cell ceilings under concurrency = 1.5 × 1.1 × the
solo cost. Wall-clock estimate: core ≈ 140 h, with the extension ≈ 150 h, against ≈ 360–375 usable hours — a 2.4×
buffer. Requires the queue's two-worker mode (R1-77e).

## Order of operations to launch

1. Finish the eight corrected MQuAKE profiles in `docs/tasks/R1-73d-post77d/`; measure full
   endpoint/validation and process-envelope costs, reconcile the ceiling factor, and admit plan v2.
2. DEC-060 option D: review protocol/matrix v5.2-D and X15 corrections; explicitly admit Q15
   near-family semantics, RNG and extension choice. R1-77d is installed; dry candidate v8 inventories it.
3. Teacher certification and joint-role review are complete (R1-D10h). The lead reviews the
   new `R1-D9-inputs-v3-post77d.json` clearance dry-run and signs its exact request.
4. Lead: attest current exposure, authorize draw (master seed), construct endpoints, then seal.
   Recompute each request after binding its actual prerequisite receipts.
5. Lead: close all gates and freeze the final package, replacing dry candidate v8 with the
   actual frozen manifest. Bind the patched sealed backend, admitted costs and final recipes.
6. Queue launch: `scripts.r1_77_queue run --execute` in block order; results committed at each block boundary;
   the DEC-052 inventory printed by `status` daily.

## Crash and interruption policy

One GPU job at a time (unless the concurrency admission says two); MemAvailable guard ≥ 4 GiB in every runner;
system and process-memory monitors; checkpoint resume from the last certified receipt. A failure stops new dispatch; under two-worker
execution the other worker drains and both process costs are recorded. The owner reconciles the
failure and explicitly resumes or records incomplete cells under DEC-052; there is no automatic
two-retry/skip implementation; results committed at every block boundary; the lead can
stop after any block with a coherent subset.
