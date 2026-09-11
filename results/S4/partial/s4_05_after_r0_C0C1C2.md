# Resource views (partial (realization 0, C0/C1/C2))

Rendered 2026-09-11 18:56 UTC by `python -m pccap.analysis.s4_05`.

## Comparable-compute eligibility (mean update accelerator seconds per edit vs C2; within 20% → comparable)

| stream | arm | mean update s | ratio to C2 | eligible |
| --- | --- | ---: | ---: | --- |
| zsre/0/0 | C0 | 0.071 | 0.74 | no |
| zsre/0/0 | C1 | 0.281 | 2.95 | no |
| zsre/0/0 | C2 | 0.095 | 1.00 | yes |
| zsre/0/1 | C0 | 0.073 | 0.73 | no |
| zsre/0/1 | C1 | 0.277 | 2.76 | no |
| zsre/0/1 | C2 | 0.100 | 1.00 | yes |
| zsre/0/2 | C0 | 0.072 | 0.73 | no |
| zsre/0/2 | C1 | 0.278 | 2.83 | no |
| zsre/0/2 | C2 | 0.098 | 1.00 | yes |
| zsre/0/3 | C0 | 0.066 | 0.65 | no |
| zsre/0/3 | C1 | 0.276 | 2.73 | no |
| zsre/0/3 | C2 | 0.101 | 1.00 | yes |
| zsre/0/4 | C0 | 0.073 | 0.75 | no |
| zsre/0/4 | C1 | 0.278 | 2.84 | no |
| zsre/0/4 | C2 | 0.098 | 1.00 | yes |

## Exposure-matched retention per contrast (checkpoints both arms completed)

- zsre/0/0 C2-C1 @ 100 items: C2: RET-ES 0.76 RET-GS 0.27 LS 0.99; C1: RET-ES 0.91 RET-GS 0.33 LS 0.99
- zsre/0/0 C2-C1 @ 300 items: C2: RET-ES 0.55 RET-GS 0.16 LS 0.99; C1: RET-ES 0.86 RET-GS 0.28 LS 0.99
- zsre/0/0 C2-C1 @ 1000 items: C2: RET-ES 0.29 RET-GS 0.09 LS 0.95; C1: RET-ES 0.50 RET-GS 0.12 LS 1.00
- zsre/0/0 C2-C0 @ 100 items: C2: RET-ES 0.76 RET-GS 0.27 LS 0.99; C0: RET-ES 0.99 RET-GS 0.38 LS 0.94
- zsre/0/0 C2-C0 @ 300 items: C2: RET-ES 0.55 RET-GS 0.16 LS 0.99; C0: RET-ES 0.99 RET-GS 0.34 LS 0.99
- zsre/0/1 C2-C1 @ 100 items: C2: RET-ES 0.70 RET-GS 0.35 LS 0.99; C1: RET-ES 0.95 RET-GS 0.38 LS 0.99
- zsre/0/1 C2-C1 @ 300 items: C2: RET-ES 0.57 RET-GS 0.27 LS 0.96; C1: RET-ES 0.88 RET-GS 0.29 LS 1.00
- zsre/0/1 C2-C1 @ 1000 items: C2: RET-ES 0.23 RET-GS 0.08 LS 0.97; C1: RET-ES 0.51 RET-GS 0.12 LS 0.99
- zsre/0/1 C2-C0 @ 100 items: C2: RET-ES 0.70 RET-GS 0.35 LS 0.99; C0: RET-ES 0.99 RET-GS 0.47 LS 1.00
- zsre/0/1 C2-C0 @ 300 items: C2: RET-ES 0.57 RET-GS 0.27 LS 0.96; C0: RET-ES 0.98 RET-GS 0.36 LS 0.95
- zsre/0/2 C2-C1 @ 100 items: C2: RET-ES 0.82 RET-GS 0.39 LS 0.97; C1: RET-ES 0.94 RET-GS 0.3 LS 0.99
- zsre/0/2 C2-C1 @ 300 items: C2: RET-ES 0.52 RET-GS 0.22 LS 0.94; C1: RET-ES 0.85 RET-GS 0.27 LS 0.94
- zsre/0/2 C2-C1 @ 1000 items: C2: RET-ES 0.29 RET-GS 0.1 LS 0.99; C1: RET-ES 0.52 RET-GS 0.13 LS 0.99
- zsre/0/2 C2-C0 @ 100 items: C2: RET-ES 0.82 RET-GS 0.39 LS 0.97; C0: RET-ES 0.99 RET-GS 0.52 LS 0.99
- zsre/0/2 C2-C0 @ 300 items: C2: RET-ES 0.52 RET-GS 0.22 LS 0.94; C0: RET-ES 0.98 RET-GS 0.39 LS 0.96
- zsre/0/3 C2-C1 @ 100 items: C2: RET-ES 0.86 RET-GS 0.44 LS 0.97; C1: RET-ES 0.96 RET-GS 0.37 LS 1.00
- zsre/0/3 C2-C1 @ 300 items: C2: RET-ES 0.67 RET-GS 0.27 LS 0.99; C1: RET-ES 0.85 RET-GS 0.25 LS 1.00
- zsre/0/3 C2-C1 @ 1000 items: C2: RET-ES 0.24 RET-GS 0.09 LS 0.97; C1: RET-ES 0.52 RET-GS 0.13 LS 0.98
- zsre/0/3 C2-C0 @ 100 items: C2: RET-ES 0.86 RET-GS 0.44 LS 0.97; C0: RET-ES 0.99 RET-GS 0.46 LS 0.98
- zsre/0/3 C2-C0 @ 300 items: C2: RET-ES 0.67 RET-GS 0.27 LS 0.99; C0: RET-ES 0.99 RET-GS 0.33 LS 0.99
- zsre/0/4 C2-C1 @ 100 items: C2: RET-ES 0.61 RET-GS 0.29 LS 0.99; C1: RET-ES 0.94 RET-GS 0.36 LS 0.96
- zsre/0/4 C2-C1 @ 300 items: C2: RET-ES 0.64 RET-GS 0.25 LS 0.96; C1: RET-ES 0.86 RET-GS 0.28 LS 0.93
- zsre/0/4 C2-C1 @ 1000 items: C2: RET-ES 0.33 RET-GS 0.13 LS 0.96; C1: RET-ES 0.50 RET-GS 0.13 LS 0.99
- zsre/0/4 C2-C0 @ 100 items: C2: RET-ES 0.61 RET-GS 0.29 LS 0.99; C0: RET-ES 1.00 RET-GS 0.47 LS 1.00
- zsre/0/4 C2-C0 @ 300 items: C2: RET-ES 0.64 RET-GS 0.25 LS 0.96; C0: RET-ES 1.00 RET-GS 0.38 LS 0.96

## Time-matched (items completed and running immediate-ES acquisition curve within an accelerator budget; retained performance at checkpoints is `retained_vs_accel_budget` in the JSON)

- zsre/0/0 @ 30 s: C0: 2 items, ES 1.0; C1: 0 items, ES None; C2: 2 items, ES 1.0
- zsre/0/0 @ 120 s: C0: 300 items, ES 1.0; C1: 100 items, ES 1.0; C2: 241 items, ES 1.0
- zsre/0/0 @ 600 s: C0: 300 items, ES 1.0; C1: 1000 items, ES 1.0; C2: 1000 items, ES 1.0
- zsre/0/1 @ 30 s: C0: 4 items, ES 1.0; C1: 0 items, ES None; C2: 4 items, ES 1.0
- zsre/0/1 @ 120 s: C0: 300 items, ES 1.0; C1: 100 items, ES 1.0; C2: 277 items, ES 1.0
- zsre/0/1 @ 600 s: C0: 300 items, ES 1.0; C1: 1000 items, ES 1.0; C2: 1000 items, ES 1.0
- zsre/0/2 @ 30 s: C0: 3 items, ES 1.0; C1: 0 items, ES None; C2: 3 items, ES 1.0
- zsre/0/2 @ 120 s: C0: 300 items, ES 1.0; C1: 100 items, ES 1.0; C2: 294 items, ES 1.0
- zsre/0/2 @ 600 s: C0: 300 items, ES 1.0; C1: 1000 items, ES 1.0; C2: 1000 items, ES 1.0
- zsre/0/3 @ 30 s: C0: 0 items, ES None; C1: 0 items, ES None; C2: 0 items, ES None
- zsre/0/3 @ 120 s: C0: 300 items, ES 1.0; C1: 108 items, ES 1.0; C2: 300 items, ES 1.0
- zsre/0/3 @ 600 s: C0: 300 items, ES 1.0; C1: 1000 items, ES 1.0; C2: 1000 items, ES 1.0
- zsre/0/4 @ 30 s: C0: 2 items, ES 1.0; C1: 1 items, ES 1.0; C2: 2 items, ES 1.0
- zsre/0/4 @ 120 s: C0: 300 items, ES 1.0; C1: 100 items, ES 1.0; C2: 175 items, ES 1.0
- zsre/0/4 @ 600 s: C0: 300 items, ES 1.0; C1: 1000 items, ES 1.0; C2: 1000 items, ES 1.0

## Longest common completed prefix per contrast

- zsre/0/0: {'C2-C1': 1000, 'C2-C0': 300}
- zsre/0/1: {'C2-C1': 1000, 'C2-C0': 300}
- zsre/0/2: {'C2-C1': 1000, 'C2-C0': 300}
- zsre/0/3: {'C2-C1': 1000, 'C2-C0': 300}
- zsre/0/4: {'C2-C1': 1000, 'C2-C0': 300}
