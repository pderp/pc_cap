# Revision v1 confirmatory execution plan v1 (2026-09-17)

Status: provisional cost admission from chains I / K (measured 300-edit development cells, batched drift); MQuAKE
non-learned costs pending chain M; MQuAKE cadence under DEC-060 (300 edits × 3 realizations, checkpoints 100 / 300).
Matrix v5.1 core = 360 cells in the DEC-051 block order; the 45-cell no-gate extension is separate and last.

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
usable hours; margin ≈ 110–140 h (≈ 45 %) before the extension, ≈ 30–40 % with it. Concurrency admitted (probes 1 and 2: 1.65× and 1.67× throughput, per-cell slowdown ≤ 1.10×, identical results,
host memory ≥ 20 GB): every block runs **two cells at a time**; per-cell ceilings under concurrency = 1.5 × 1.1 × the
solo cost. Wall-clock estimate: core ≈ 140 h, with the extension ≈ 150 h, against ≈ 360–375 usable hours — a 2.4×
buffer. Requires the queue's two-worker mode (R1-77e).

## Order of operations to launch

1. Chain M (MQuAKE comparator profiles) → MQuAKE column measured → this plan v2 with admitted ceilings.
2. R1-D10e review applied (DEC-060) → matrix / protocol v5.2 (R1-D10d, option A) → freeze candidate v7 (R1-63f).
3. Teacher-token review (chain N) → clearance evidence complete → lead: clearance dry-run + signature.
4. Lead: draw (master seed), seal; endpoint construction (R1-D10c) between draw and seal.
5. Lead: freeze (candidate v7 → frozen manifest). Sealed backend (R1-77c) bound.
6. Queue launch: `scripts.r1_77_queue run --execute` in block order; results committed at each block boundary;
   the DEC-052 inventory printed by `status` daily.

## Crash and interruption policy

One GPU job at a time (unless the concurrency admission says two); MemAvailable guard ≥ 4 GiB in every runner;
system and process-memory monitors; checkpoint resume from the last certified receipt; any cell that fails twice is
reported as incomplete and the queue moves on (DEC-052); results committed at every block boundary; the lead can
stop after any block with a coherent subset.
