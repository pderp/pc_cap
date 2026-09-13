# Resource views (confirmatory grammar v3 (60 runs))

Rendered 2026-09-13 21:54 UTC by `python -m pccap.analysis.s4_05`.

## Comparable-compute eligibility (mean update accelerator seconds per edit vs C2; within 20% → comparable)

| stream | arm | mean update s | ratio to C2 | eligible |
| --- | --- | ---: | ---: | --- |
| grammar/0/0 | C0 | 0.015 | 0.22 | no |
| grammar/0/0 | C1 | 0.056 | 0.81 | yes |
| grammar/0/0 | C2 | 0.069 | 1.00 | yes |
| grammar/0/0 | CR | 0.020 | 0.29 | no |
| grammar/0/1 | C0 | 0.015 | 0.21 | no |
| grammar/0/1 | C1 | 0.056 | 0.79 | no |
| grammar/0/1 | C2 | 0.070 | 1.00 | yes |
| grammar/0/1 | CR | 0.020 | 0.28 | no |
| grammar/0/2 | C0 | 0.015 | 0.20 | no |
| grammar/0/2 | C1 | 0.058 | 0.79 | no |
| grammar/0/2 | C2 | 0.073 | 1.00 | yes |
| grammar/0/2 | CR | 0.020 | 0.27 | no |
| grammar/0/3 | C0 | 0.014 | 0.11 | no |
| grammar/0/3 | C1 | 0.135 | 0.99 | yes |
| grammar/0/3 | C2 | 0.136 | 1.00 | yes |
| grammar/0/3 | CR | 0.020 | 0.15 | no |
| grammar/0/4 | C0 | 0.014 | 0.51 | no |
| grammar/0/4 | C1 | 0.158 | 5.56 | no |
| grammar/0/4 | C2 | 0.028 | 1.00 | yes |
| grammar/0/4 | CR | 0.020 | 0.69 | no |
| grammar/1/0 | C0 | 0.015 | 0.52 | no |
| grammar/1/0 | C1 | 0.057 | 1.99 | no |
| grammar/1/0 | C2 | 0.028 | 1.00 | yes |
| grammar/1/0 | CR | 0.020 | 0.69 | no |
| grammar/1/1 | C0 | 0.015 | 0.52 | no |
| grammar/1/1 | C1 | 0.057 | 1.99 | no |
| grammar/1/1 | C2 | 0.028 | 1.00 | yes |
| grammar/1/1 | CR | 0.020 | 0.69 | no |
| grammar/1/2 | C0 | 0.015 | 0.52 | no |
| grammar/1/2 | C1 | 0.057 | 1.99 | no |
| grammar/1/2 | C2 | 0.029 | 1.00 | yes |
| grammar/1/2 | CR | 0.020 | 0.69 | no |
| grammar/1/3 | C0 | 0.015 | 0.52 | no |
| grammar/1/3 | C1 | 0.057 | 1.99 | no |
| grammar/1/3 | C2 | 0.028 | 1.00 | yes |
| grammar/1/3 | CR | 0.020 | 0.69 | no |
| grammar/1/4 | C0 | 0.015 | 0.52 | no |
| grammar/1/4 | C1 | 0.057 | 1.99 | no |
| grammar/1/4 | C2 | 0.029 | 1.00 | yes |
| grammar/1/4 | CR | 0.020 | 0.70 | no |
| grammar/2/0 | C0 | 0.015 | 0.51 | no |
| grammar/2/0 | C1 | 0.056 | 1.96 | no |
| grammar/2/0 | C2 | 0.029 | 1.00 | yes |
| grammar/2/0 | CR | 0.020 | 0.68 | no |
| grammar/2/1 | C0 | 0.015 | 0.51 | no |
| grammar/2/1 | C1 | 0.056 | 1.97 | no |
| grammar/2/1 | C2 | 0.029 | 1.00 | yes |
| grammar/2/1 | CR | 0.020 | 0.68 | no |
| grammar/2/2 | C0 | 0.015 | 0.53 | no |
| grammar/2/2 | C1 | 0.057 | 2.01 | no |
| grammar/2/2 | C2 | 0.028 | 1.00 | yes |
| grammar/2/2 | CR | 0.019 | 0.69 | no |
| grammar/2/3 | C0 | 0.015 | 0.53 | no |
| grammar/2/3 | C1 | 0.058 | 2.05 | no |
| grammar/2/3 | C2 | 0.028 | 1.00 | yes |
| grammar/2/3 | CR | 0.019 | 0.69 | no |
| grammar/2/4 | C0 | 0.015 | 0.52 | no |
| grammar/2/4 | C1 | 0.058 | 2.05 | no |
| grammar/2/4 | C2 | 0.028 | 1.00 | yes |
| grammar/2/4 | CR | 0.020 | 0.69 | no |

## Exposure-matched retention per contrast (checkpoints both arms completed)

- grammar/0/0 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.68 RET-GS 0.28 LS 1.00
- grammar/0/0 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.69 RET-GS 0.3 LS 1.00
- grammar/0/0 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C1: RET-ES 0.69 RET-GS 0.27 LS 1.00
- grammar/0/0 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/0/0 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.94 RET-GS 0.28 LS 1.00
- grammar/0/0 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.92 RET-GS 0.3 LS 1.00
- grammar/0/0 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; CR: RET-ES 0.90 RET-GS 0.27 LS 1.00
- grammar/0/0 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/0 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/0/0 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/0/0 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C0: RET-ES 1.00 RET-GS 0.27 LS 1.00
- grammar/0/0 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; C1: RET-ES 0.58 RET-GS 0.23 LS 1.00
- grammar/0/1 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C1: RET-ES 0.64 RET-GS 0.27 LS 1.00
- grammar/0/1 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.70 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.70 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; CR: RET-ES 0.85 RET-GS 0.23 LS 1.00
- grammar/0/1 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; CR: RET-ES 0.88 RET-GS 0.27 LS 1.00
- grammar/0/1 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; C0: RET-ES 1.00 RET-GS 0.23 LS 1.00
- grammar/0/1 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C0: RET-ES 1.00 RET-GS 0.27 LS 1.00
- grammar/0/1 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/1 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.70 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.74 RET-GS 0.3 LS 1.00
- grammar/0/2 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C1: RET-ES 0.71 RET-GS 0.31 LS 1.00
- grammar/0/2 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.90 RET-GS 0.3 LS 1.00
- grammar/0/2 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; CR: RET-ES 0.90 RET-GS 0.31 LS 1.00
- grammar/0/2 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/2 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/0/2 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C0: RET-ES 1.00 RET-GS 0.31 LS 1.00
- grammar/0/2 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; C1: RET-ES 0.78 RET-GS 0.37 LS 1.00
- grammar/0/3 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.70 RET-GS 0.28 LS 1.00
- grammar/0/3 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; CR: RET-ES 0.91 RET-GS 0.37 LS 1.00
- grammar/0/3 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.87 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.90 RET-GS 0.28 LS 1.00
- grammar/0/3 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.89 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; C0: RET-ES 1.00 RET-GS 0.37 LS 1.00
- grammar/0/3 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/3 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/0/3 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/0/4 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.66 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C1: RET-ES 0.71 RET-GS 0.31 LS 1.00
- grammar/0/4 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.71 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/0/4 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.88 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; CR: RET-ES 0.89 RET-GS 0.31 LS 1.00
- grammar/0/4 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.90 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/0/4 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C0: RET-ES 1.00 RET-GS 0.31 LS 1.00
- grammar/0/4 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/0/4 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.33 LS 1.00; C1: RET-ES 0.68 RET-GS 0.33 LS 1.00
- grammar/1/0 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; C1: RET-ES 0.70 RET-GS 0.26 LS 1.00
- grammar/1/0 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.70 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.33 LS 1.00; CR: RET-ES 0.87 RET-GS 0.33 LS 1.00
- grammar/1/0 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; CR: RET-ES 0.88 RET-GS 0.26 LS 1.00
- grammar/1/0 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.89 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.33 LS 1.00; C0: RET-ES 1.00 RET-GS 0.33 LS 1.00
- grammar/1/0 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; C0: RET-ES 1.00 RET-GS 0.26 LS 1.00
- grammar/1/0 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/0 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/1 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.36 LS 1.00; C1: RET-ES 0.70 RET-GS 0.36 LS 1.00
- grammar/1/1 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C1: RET-ES 0.69 RET-GS 0.32 LS 1.00
- grammar/1/1 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.69 RET-GS 0.3 LS 1.00
- grammar/1/1 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/1 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.36 LS 1.00; CR: RET-ES 0.89 RET-GS 0.36 LS 1.00
- grammar/1/1 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; CR: RET-ES 0.90 RET-GS 0.32 LS 1.00
- grammar/1/1 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.90 RET-GS 0.3 LS 1.00
- grammar/1/1 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.89 RET-GS 0.29 LS 1.00
- grammar/1/1 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.36 LS 1.00; C0: RET-ES 1.00 RET-GS 0.36 LS 1.00
- grammar/1/1 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C0: RET-ES 1.00 RET-GS 0.32 LS 1.00
- grammar/1/1 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/1/1 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/2 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.34 LS 1.00; C1: RET-ES 0.69 RET-GS 0.34 LS 1.00
- grammar/1/2 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C1: RET-ES 0.71 RET-GS 0.31 LS 1.00
- grammar/1/2 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.71 RET-GS 0.3 LS 1.00
- grammar/1/2 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/2 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.34 LS 1.00; CR: RET-ES 0.90 RET-GS 0.34 LS 1.00
- grammar/1/2 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; CR: RET-ES 0.91 RET-GS 0.31 LS 1.00
- grammar/1/2 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.92 RET-GS 0.3 LS 1.00
- grammar/1/2 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.91 RET-GS 0.29 LS 1.00
- grammar/1/2 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.34 LS 1.00; C0: RET-ES 1.00 RET-GS 0.34 LS 1.00
- grammar/1/2 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C0: RET-ES 1.00 RET-GS 0.31 LS 1.00
- grammar/1/2 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/1/2 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/3 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.66 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C1: RET-ES 0.70 RET-GS 0.32 LS 1.00
- grammar/1/3 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.70 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/3 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.92 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; CR: RET-ES 0.91 RET-GS 0.32 LS 1.00
- grammar/1/3 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.90 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/1/3 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C0: RET-ES 1.00 RET-GS 0.32 LS 1.00
- grammar/1/3 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/1/3 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; C1: RET-ES 0.74 RET-GS 0.37 LS 1.00
- grammar/1/4 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.70 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.69 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; CR: RET-ES 0.94 RET-GS 0.37 LS 1.00
- grammar/1/4 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.91 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.89 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.37 LS 1.00; C0: RET-ES 1.00 RET-GS 0.37 LS 1.00
- grammar/1/4 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/1/4 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/2/0 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.69 RET-GS 0.28 LS 1.00
- grammar/2/0 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.71 RET-GS 0.29 LS 1.00
- grammar/2/0 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.72 RET-GS 0.3 LS 1.00
- grammar/2/0 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.69 RET-GS 0.28 LS 1.00
- grammar/2/0 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.95 RET-GS 0.28 LS 1.00
- grammar/2/0 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.92 RET-GS 0.29 LS 1.00
- grammar/2/0 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.90 RET-GS 0.3 LS 1.00
- grammar/2/0 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/0 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/0 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/2/0 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/2/0 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/1 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C1: RET-ES 0.71 RET-GS 0.3 LS 1.00
- grammar/2/1 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C1: RET-ES 0.71 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C1: RET-ES 0.68 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.68 RET-GS 0.28 LS 1.00
- grammar/2/1 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; CR: RET-ES 0.88 RET-GS 0.3 LS 1.00
- grammar/2/1 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; CR: RET-ES 0.89 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; CR: RET-ES 0.89 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/1 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.3 LS 1.00; C0: RET-ES 1.00 RET-GS 0.3 LS 1.00
- grammar/2/1 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C0: RET-ES 1.00 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C0: RET-ES 1.00 RET-GS 0.27 LS 1.00
- grammar/2/1 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C1: RET-ES 0.64 RET-GS 0.29 LS 1.00
- grammar/2/2 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C1: RET-ES 0.68 RET-GS 0.27 LS 1.00
- grammar/2/2 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.70 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.68 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; CR: RET-ES 0.90 RET-GS 0.29 LS 1.00
- grammar/2/2 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; CR: RET-ES 0.88 RET-GS 0.27 LS 1.00
- grammar/2/2 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.90 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.29 LS 1.00; C0: RET-ES 1.00 RET-GS 0.29 LS 1.00
- grammar/2/2 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.27 LS 1.00; C0: RET-ES 1.00 RET-GS 0.27 LS 1.00
- grammar/2/2 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/2 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C1: RET-ES 0.70 RET-GS 0.31 LS 1.00
- grammar/2/3 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C1: RET-ES 0.72 RET-GS 0.32 LS 1.00
- grammar/2/3 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.70 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.69 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; CR: RET-ES 0.90 RET-GS 0.31 LS 1.00
- grammar/2/3 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; CR: RET-ES 0.90 RET-GS 0.32 LS 1.00
- grammar/2/3 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.31 LS 1.00; C0: RET-ES 1.00 RET-GS 0.31 LS 1.00
- grammar/2/3 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.32 LS 1.00; C0: RET-ES 1.00 RET-GS 0.32 LS 1.00
- grammar/2/3 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/3 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00
- grammar/2/4 C2-C1 @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; C1: RET-ES 0.58 RET-GS 0.23 LS 1.00
- grammar/2/4 C2-C1 @ 300 items: C2: RET-ES 1.00 RET-GS 0.25 LS 1.00; C1: RET-ES 0.64 RET-GS 0.25 LS 1.00
- grammar/2/4 C2-C1 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; C1: RET-ES 0.68 RET-GS 0.26 LS 1.00
- grammar/2/4 C2-C1 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C1: RET-ES 0.69 RET-GS 0.28 LS 1.00
- grammar/2/4 C2-CR @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; CR: RET-ES 0.87 RET-GS 0.23 LS 1.00
- grammar/2/4 C2-CR @ 300 items: C2: RET-ES 1.00 RET-GS 0.25 LS 1.00; CR: RET-ES 0.87 RET-GS 0.25 LS 1.00
- grammar/2/4 C2-CR @ 1000 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; CR: RET-ES 0.90 RET-GS 0.26 LS 1.00
- grammar/2/4 C2-CR @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; CR: RET-ES 0.89 RET-GS 0.28 LS 1.00
- grammar/2/4 C2-C0 @ 100 items: C2: RET-ES 1.00 RET-GS 0.23 LS 1.00; C0: RET-ES 1.00 RET-GS 0.23 LS 1.00
- grammar/2/4 C2-C0 @ 300 items: C2: RET-ES 1.00 RET-GS 0.25 LS 1.00; C0: RET-ES 1.00 RET-GS 0.25 LS 1.00
- grammar/2/4 C2-C0 @ 1000 items: C2: RET-ES 1.00 RET-GS 0.26 LS 1.00; C0: RET-ES 1.00 RET-GS 0.26 LS 1.00
- grammar/2/4 C2-C0 @ 2048 items: C2: RET-ES 1.00 RET-GS 0.28 LS 1.00; C0: RET-ES 1.00 RET-GS 0.28 LS 1.00

## Time-matched (items completed and running immediate-ES acquisition curve within an accelerator budget; retained performance at checkpoints is `retained_vs_accel_budget` in the JSON)

- grammar/0/0 @ 30 s: C0: 1405 items, ES 1.0; C1: 339 items, ES 0.71; C2: 294 items, ES 1.0; CR: 893 items, ES 0.9
- grammar/0/0 @ 120 s: C0: 2048 items, ES 1.0; C1: 1827 items, ES 0.7; C2: 1433 items, ES 1.0; CR: 2048 items, ES 0.91
- grammar/0/0 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.91
- grammar/0/1 @ 30 s: C0: 1456 items, ES 1.0; C1: 358 items, ES 0.65; C2: 265 items, ES 1.0; CR: 959 items, ES 0.89
- grammar/0/1 @ 120 s: C0: 2048 items, ES 1.0; C1: 1867 items, ES 0.7; C2: 1403 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/1 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/2 @ 30 s: C0: 1382 items, ES 1.0; C1: 302 items, ES 0.73; C2: 270 items, ES 1.0; CR: 836 items, ES 0.91
- grammar/0/2 @ 120 s: C0: 2048 items, ES 1.0; C1: 1748 items, ES 0.7; C2: 1347 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/2 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/3 @ 30 s: C0: 1461 items, ES 1.0; C1: 335 items, ES 0.7; C2: 294 items, ES 1.0; CR: 921 items, ES 0.9
- grammar/0/3 @ 120 s: C0: 2048 items, ES 1.0; C1: 1642 items, ES 0.7; C2: 686 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/3 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/4 @ 30 s: C0: 1509 items, ES 1.0; C1: 124 items, ES 0.69; C2: 694 items, ES 1.0; CR: 974 items, ES 0.9
- grammar/0/4 @ 120 s: C0: 2048 items, ES 1.0; C1: 674 items, ES 0.72; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/0/4 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/0 @ 30 s: C0: 1452 items, ES 1.0; C1: 350 items, ES 0.68; C2: 691 items, ES 1.0; CR: 954 items, ES 0.9
- grammar/1/0 @ 120 s: C0: 2048 items, ES 1.0; C1: 1830 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/0 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/1 @ 30 s: C0: 1455 items, ES 1.0; C1: 350 items, ES 0.7; C2: 699 items, ES 1.0; CR: 944 items, ES 0.9
- grammar/1/1 @ 120 s: C0: 2048 items, ES 1.0; C1: 1827 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/1 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/2 @ 30 s: C0: 1456 items, ES 1.0; C1: 348 items, ES 0.71; C2: 697 items, ES 1.0; CR: 958 items, ES 0.92
- grammar/1/2 @ 120 s: C0: 2048 items, ES 1.0; C1: 1825 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.92
- grammar/1/2 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.92
- grammar/1/3 @ 30 s: C0: 1420 items, ES 1.0; C1: 345 items, ES 0.7; C2: 673 items, ES 1.0; CR: 909 items, ES 0.9
- grammar/1/3 @ 120 s: C0: 2048 items, ES 1.0; C1: 1809 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/3 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/4 @ 30 s: C0: 1434 items, ES 1.0; C1: 349 items, ES 0.69; C2: 683 items, ES 1.0; CR: 941 items, ES 0.91
- grammar/1/4 @ 120 s: C0: 2048 items, ES 1.0; C1: 1814 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/1/4 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/2/0 @ 30 s: C0: 1418 items, ES 1.0; C1: 326 items, ES 0.69; C2: 657 items, ES 1.0; CR: 901 items, ES 0.9
- grammar/2/0 @ 120 s: C0: 2048 items, ES 1.0; C1: 1811 items, ES 0.7; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/0 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/1 @ 30 s: C0: 1429 items, ES 1.0; C1: 348 items, ES 0.69; C2: 660 items, ES 1.0; CR: 936 items, ES 0.89
- grammar/2/1 @ 120 s: C0: 2048 items, ES 1.0; C1: 1814 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/1 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/2 @ 30 s: C0: 1447 items, ES 1.0; C1: 349 items, ES 0.7; C2: 704 items, ES 1.0; CR: 982 items, ES 0.9
- grammar/2/2 @ 120 s: C0: 2048 items, ES 1.0; C1: 1821 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/2/2 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/2/3 @ 30 s: C0: 1447 items, ES 1.0; C1: 336 items, ES 0.71; C2: 699 items, ES 1.0; CR: 980 items, ES 0.89
- grammar/2/3 @ 120 s: C0: 2048 items, ES 1.0; C1: 1786 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/3 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.89
- grammar/2/4 @ 30 s: C0: 1457 items, ES 1.0; C1: 327 items, ES 0.65; C2: 706 items, ES 1.0; CR: 965 items, ES 0.9
- grammar/2/4 @ 120 s: C0: 2048 items, ES 1.0; C1: 1777 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9
- grammar/2/4 @ 600 s: C0: 2048 items, ES 1.0; C1: 2048 items, ES 0.69; C2: 2048 items, ES 1.0; CR: 2048 items, ES 0.9

## Longest common completed prefix per contrast

- grammar/0/0: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/0/1: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/0/2: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/0/3: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/0/4: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/1/0: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/1/1: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/1/2: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/1/3: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/1/4: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/2/0: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/2/1: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/2/2: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/2/3: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
- grammar/2/4: {'C2-C1': 2048, 'C2-CR': 2048, 'C2-C0': 2048}
