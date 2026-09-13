# S7-01/02 — cloned-state reversals and damage matrices (PDF D.9)

Rendered 2026-09-13T06:57:22Z from 4 checkpoint runs (`results/S7/frozen-confirmatory-v2-84126123/`).

D_ij = mean JS (nats) over Q = both edits' prefixes (prompt + paraphrases) and unrelated controls; I_ij = mean over Q_i of L_i(U_j U_i s) − L_i(U_i s) (complete-answer NLL, nats; positive = harm); I_ji symmetric. 100 fixed pairs per checkpoint (CounterFact 75: shared stratum 9, DEC-023).

## counterfact / C2 / end (300-edit endpoint; 300 items; state `c8fb3b2f78aa…`)

| stratum | n | I_ij (learn i, then j) | I_ji | both orders | harmful fraction | D_ij mean | D_ij max | rounds/update | allocations | evictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shared | 9 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 2.00 | 72 | 72 |
| private | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 2.00 | 264 | 264 |
| near_neighbour | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 2.00 | 264 | 264 |
| all | 75 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 2.00 | 600 | 600 |

First edit no longer exact after the second: 0.00 (i after i→j), 0.00 (j after j→i); identical endpoint states in 0% of pairs; 29 accelerator s.

## grammar / C2 / ckpt1000 (≈ end of task 4 (1000 of 1024 sequences; the frozen checkpoint nearest the task boundary); 1000 items; state `a8469596a820…`)

| stratum | n | I_ij (learn i, then j) | I_ji | both orders | harmful fraction | D_ij mean | D_ij max | rounds/update | allocations | evictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shared | 34 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 180 | 680 |
| private | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 260 | 590 |
| near_neighbour | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 260 | 554 |
| all | 100 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 700 | 1824 |

First edit no longer exact after the second: 0.00 (i after i→j), 0.00 (j after j→i); identical endpoint states in 0% of pairs; 18 accelerator s.

## grammar / C2 / end (end of task 8 (2048 sequences); 2048 items; state `70a761f6a757…`)

| stratum | n | I_ij (learn i, then j) | I_ji | both orders | harmful fraction | D_ij mean | D_ij max | rounds/update | allocations | evictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shared | 34 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 180 | 680 |
| private | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 260 | 590 |
| near_neighbour | 33 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 260 | 554 |
| all | 100 | +0.000 | +0.000 | +0.000 | 0.00 | 0.0000 | 0.0000 | 5.00 | 700 | 1824 |

First edit no longer exact after the second: 0.00 (i after i→j), 0.00 (j after j→i); identical endpoint states in 0% of pairs; 18 accelerator s.

## zsre / C2 / ckpt300 (300-edit checkpoint of the 1000-item stream; 300 items; state `2141b824c462…`)

| stratum | n | I_ij (learn i, then j) | I_ji | both orders | harmful fraction | D_ij mean | D_ij max | rounds/update | allocations | evictions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| shared | 34 | +0.661 | +0.722 | +0.692 | 0.16 | 0.0406 | 0.2293 | 3.86 | 482 | 525 |
| private | 33 | +0.319 | +0.000 | +0.160 | 0.03 | 0.0035 | 0.1155 | 3.84 | 482 | 507 |
| near_neighbour | 33 | +3.049 | +1.778 | +2.414 | 0.33 | 0.0396 | 0.3463 | 3.34 | 384 | 433 |
| all | 100 | +1.336 | +0.832 | +1.084 | 0.17 | 0.0280 | 0.3463 | 3.68 | 1348 | 1465 |

First edit no longer exact after the second: 0.06 (i after i→j), 0.03 (j after j→i); identical endpoint states in 0% of pairs; 85 accelerator s.

## Reading

- counterfact end: damage ranks shared (+0.00) > private (+0.00) > near_neighbour (+0.00); D_ij by stratum shared 0.000, private 0.000, near_neighbour 0.000.
- grammar ckpt1000: damage ranks shared (+0.00) > private (+0.00) > near_neighbour (+0.00); D_ij by stratum shared 0.000, private 0.000, near_neighbour 0.000.
- grammar end: damage ranks shared (+0.00) > private (+0.00) > near_neighbour (+0.00); D_ij by stratum shared 0.000, private 0.000, near_neighbour 0.000.
- zsre ckpt300: damage ranks near_neighbour (+2.41) > shared (+0.69) > private (+0.16); D_ij by stratum near_neighbour 0.040, shared 0.041, private 0.004.

Strata are operational proxies on the natural-language datasets and generator-defined on the grammar (`manifests/dev/s7_pairs.json`, `strata_qualification`). No analytic inverse of the allocation/eviction map is assumed; the same-endpoint fraction reports how often the two orders reached an identical complete state.
