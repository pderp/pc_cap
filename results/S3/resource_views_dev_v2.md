# Resource views (development v2 (ledger deltas))

Rendered 2026-09-10 23:59 UTC by `python -m pccap.analysis.s4_05`.

## Comparable-compute eligibility (mean update accelerator seconds per edit vs C2; within 20% → comparable)

| stream | arm | mean update s | ratio to C2 | eligible |
| --- | --- | ---: | ---: | --- |
| counterfact/0/0 | C0 | 0.110 | 1.02 | yes |
| counterfact/0/0 | C1 | 0.214 | 1.99 | no |
| counterfact/0/0 | C2 | 0.108 | 1.00 | yes |
| counterfact/0/0 | CR | 0.097 | 0.90 | yes |
| counterfact/0/0 | B0 | 0.090 | 0.83 | yes |
| counterfact/0/0 | B1 | 0.088 | 0.82 | yes |
| counterfact/0/0 | B3 | 0.082 | 0.76 | no |
| zsre/0/0 | C0 | 0.191 | 1.71 | no |
| zsre/0/0 | C1 | 0.433 | 3.90 | no |
| zsre/0/0 | C2 | 0.111 | 1.00 | yes |
| zsre/0/0 | CR | 0.087 | 0.78 | no |
| zsre/0/0 | B0 | 0.042 | 0.38 | no |
| zsre/0/0 | B1 | 0.276 | 2.48 | no |
| zsre/0/0 | B3 | 0.102 | 0.91 | yes |

## Exposure-matched retention per contrast (checkpoints both arms completed)

- counterfact/0/0 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; C1: RET-ES 1.00 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; CR: RET-ES 1.00 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; C0: RET-ES 1.00 RET-GS 0.0 LS 1.00
- counterfact/0/0 C2-B3 @ 100 items: C2: RET-ES 1.00 RET-GS 0.0 LS 1.00; B3: RET-ES 0.10 RET-GS 0.07 LS 0.00
- zsre/0/0 C2-C1 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; C1: RET-ES 0.90 RET-GS 0.31 LS 1.00
- zsre/0/0 C2-CR @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; CR: RET-ES 0.77 RET-GS 0.38 LS 1.00
- zsre/0/0 C2-C0 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; C0: RET-ES 0.99 RET-GS 0.43 LS 1.00
- zsre/0/0 C2-B3 @ 100 items: C2: RET-ES 0.94 RET-GS 0.3 LS 1.00; B3: RET-ES 0.16 RET-GS 0.13 LS 0.00

## Time-matched (items completed and running immediate-ES acquisition curve within an accelerator budget; retained performance at checkpoints is `retained_vs_accel_budget` in the JSON)

- counterfact/0/0 @ 30 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- counterfact/0/0 @ 120 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- counterfact/0/0 @ 600 s: C0: 100 items, ES 1.0; C1: 100 items, ES 1.0; C2: 100 items, ES 1.0; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.07
- zsre/0/0 @ 30 s: C0: 100 items, ES 0.99; C1: 62 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1
- zsre/0/0 @ 120 s: C0: 100 items, ES 0.99; C1: 100 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1
- zsre/0/0 @ 600 s: C0: 100 items, ES 0.99; C1: 100 items, ES 1.0; C2: 100 items, ES 0.99; CR: 100 items, ES 1.0; B0: 100 items, ES 0.0; B1: 100 items, ES 0.08; B3: 100 items, ES 0.1

## Longest common completed prefix per contrast

- counterfact/0/0: {'C2-C1': 100, 'C2-CR': 100, 'C2-C0': 100, 'C2-B3': 100}
- zsre/0/0: {'C2-C1': 100, 'C2-CR': 100, 'C2-C0': 100, 'C2-B3': 100}
