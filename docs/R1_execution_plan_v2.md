# Revision v1 confirmatory execution plan v2 — cost admission (2026-09-17, 18:00 EDT)

Supersedes v1 for costs and ceilings (v1 retained). Every number below is from a measured 300-edit development cell of
the same condition and dataset on the installed tree (chains I, K, M, Q; batched drift for the six non-learned
families; MQuAKE with calibration v3 and corrected locality); 1,000-edit costs scale the per-edit phases linearly and
count the drift assay once. Admitted by the orchestrator under DEC-052's re-measurement clause (brought forward
from September 20); ceilings in `manifests/revision_v1/cell_ceilings_v1.json`.

## Admitted solo cost per confirmatory cell (hours)

| condition class | zsRE (1,000 edits) | CounterFact (1,000 edits) | MQuAKE (300 edits, DEC-060) |
| --- | ---: | ---: | ---: |
| R1_learned_ff, R1_nonlearned, R1_learned_ff_v2 | 0.35 | 0.35 | 0.11 |
| v0_stable, matched_update, v0_live_C1 / C2 | 0.48 | 1.22 | 0.33 |
| S1_LM, S1_literal | 0.50 | 1.28 | 0.33 |

Ceiling = 1.5 × solo cost; with two workers the queue applies × 1.15 (measured concurrent slowdown ≤ 1.13, X15).

## Blocks (DEC-051), solo hours

| block | cells | zsRE | CounterFact | MQuAKE | block h | cumulative h |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 45 | 5.9 | 9.6 | 2.8 | 18.2 | 18.2 |
| 2 | 45 | 7.2 | 18.3 | 5.0 | 30.4 | 48.7 |
| 3 | 90 | 13.1 | 27.9 | 7.7 | 48.7 | 97.4 |
| 4 | 90 | 13.1 | 27.9 | 7.7 | 48.7 | 146.1 |
| 5 | 90 | 15.0 | 38.4 | 9.9 | 63.3 | 209.4 |
| ext | 45 | 5.3 | 5.3 | 1.7 | 12.2 | 221.6 |

Two workers (admitted 1.65× throughput): core ≈ 127 wall-clock hours, with the extension ≈ 134 h, against ≈ 360–375
usable hours from a September 19–20 launch — a buffer of ≈ 2.7× before the extension. Failure policy (R1-77f): retry
once from the last certified checkpoint, then mark incomplete and continue; results committed at every block
boundary; the DEC-052 inventory printed daily.

## What remains before launch

Codex: R1-77f (queue ceilings × 1.15, retry policy), R1-D9e (near-miss family), R1-49i (protocol v5.2-D final text),
R1-63h (candidate v9 binding this admission), R1-58f (operator sheet v4). Lead: clearance signature, draw (master
seed), seal, freeze. Orchestrator: endpoint construction between draw and seal, queue launch.
