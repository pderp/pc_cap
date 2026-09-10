# Resource views (development, one order (pre-R2-06 runs: learner cost only))

Rendered 2026-09-10 12:55 UTC by `python -m pccap.analysis.s4_05`.

## Comparable-compute eligibility (mean update accelerator seconds per edit vs C2; within 20% → comparable)

| stream | arm | mean update s | ratio to C2 | eligible |
| --- | --- | ---: | ---: | --- |
| counterfact/0/0 | C0 | 0.025 | 1.04 | yes |
| counterfact/0/0 | C1 | 0.111 | 4.52 | no |
| counterfact/0/0 | C2 | 0.025 | 1.00 | yes |
| counterfact/0/0 | CR | 0.068 | 2.77 | no |
| counterfact/0/0 | B0 | 0.000 | 0.00 | no |
| counterfact/0/0 | B1 | 0.061 | 2.49 | no |
| counterfact/0/0 | B3 | 0.062 | 2.52 | no |
| zsre/0/0 | C0 | 0.055 | 1.03 | yes |
| zsre/0/0 | C1 | 0.254 | 4.75 | no |
| zsre/0/0 | C2 | 0.054 | 1.00 | yes |
| zsre/0/0 | CR | 0.119 | 2.21 | no |
| zsre/0/0 | B0 | 0.000 | 0.00 | no |
| zsre/0/0 | B1 | 0.078 | 1.46 | no |
| zsre/0/0 | B3 | 0.094 | 1.75 | no |

## Exposure-matched retention per contrast (checkpoints both arms completed)

- counterfact/0/0 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; C1: RET-ES 1.00 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; CR: RET-ES 0.98 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; C0: RET-ES 1.00 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-B3 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; B3: RET-ES 0.10 RET-GS 0.07 LS 0.00
- zsre/0/0 C2-C1 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; C1: RET-ES 0.90 RET-GS 0.31 LS 1.00
- zsre/0/0 C2-CR @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; CR: RET-ES 0.53 RET-GS 0.18 LS 0.93
- zsre/0/0 C2-C0 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; C0: RET-ES 0.99 RET-GS 0.43 LS 1.00
- zsre/0/0 C2-B3 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; B3: RET-ES 0.16 RET-GS 0.13 LS 0.00

## Time-matched (items completed and running immediate-ES acquisition curve within an accelerator budget; retained performance at checkpoints is `retained_vs_accel_budget` in the JSON)

- counterfact/0/0 @ 30 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 0.98; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- counterfact/0/0 @ 120 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 0.98; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- counterfact/0/0 @ 600 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 0.98; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- zsre/0/0 @ 30 s: C0: 100 items, ES 0.99; C1: 100 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 0.99; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1
- zsre/0/0 @ 120 s: C0: 100 items, ES 0.99; C1: 100 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 0.99; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1
- zsre/0/0 @ 600 s: C0: 100 items, ES 0.99; C1: 100 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 0.99; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1

## Longest common completed prefix per contrast

- counterfact/0/0: {'C2-C1': 100, 'C2-CR': 100, 'C2-C0': 100, 'C2-B3': 100}
- zsre/0/0: {'C2-C1': 100, 'C2-CR': 100, 'C2-C0': 100, 'C2-B3': 100}
