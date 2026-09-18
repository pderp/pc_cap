# Host RSS inventory bound by cost revision 3

Snapshot: one direct GNU time result, 25 unique temporal monitor matches, one proposed cross-dataset transfer. Later chain R completions require a new extraction. Values are MiB before 1.5 ceiling padding.

| Condition | zsRE | CounterFact | MQuAKE |
|---|---:|---:|---:|
| R1_learned_ff | 2642.65 (direct) | 2489.76 (sampled/matched) | 2642.65 (proposed transfer) |
| R1_learned_ff_v2 | 2441.96 (sampled/matched) | 2490.94 (sampled/matched) | 2488.67 (sampled/matched) |
| R1_nonlearned | 2447.58 (sampled/matched) | 2481.43 (sampled/matched) | 2490.98 (sampled/matched) |
| S1_LM | 3085.91 (sampled/matched) | 3144.23 (sampled/matched) | 3143.68 (sampled/matched) |
| S1_literal | 3089.82 (sampled/matched) | 3139.78 (sampled/matched) | 3143.55 (sampled/matched) |
| matched_update | 2582.47 (sampled/matched) | 2608.66 (sampled/matched) | 2629.80 (sampled/matched) |
| v0_live_C1 | 2573.10 (sampled/matched) | 2632.78 (sampled/matched) | 2637.69 (sampled/matched) |
| v0_live_C2 | 2519.24 (sampled/matched) | 2620.57 (sampled/matched) | 2623.31 (sampled/matched) |
| v0_stable | 2585.79 (sampled/matched) | 2629.45 (sampled/matched) | 2632.87 (sampled/matched) |

Matched entries use file-mtime windows and sanitized command labels, not embedded recipe/PID receipts. They retain sampled RSS and separate observed kernel HWM in the JSON evidence. The transfer row has a null measured peak; its proposal is never used as an admitted measurement.

Source: `docs/tasks/R1-host-peak-evidence-v3.json`; producer and retained excerpts are hash-bound there.
