# PC-trained reader — partial report

Capex · generated from saved artifacts · 10/12 completed evaluations, six planned trainings.
Machine-readable source and input hashes: `/home/derp/cap/pc_cap/logs/additional_work/reproductions/round61-verified/pc-reader/report.json`.

This changes **reader/controller training** (BP versus ePC); acquisition uses adjoint in every arm. Same exposed realization 0, order 100, first 300 edits on each dataset. Three paired training seeds are not three subject realizations. Missing/failed cells remain visible. No superiority claim or new decision threshold is assigned.

Fully paired training seeds: 0, 1 (2/3 planned). The table uses **ePC minus BP** in percentage points for paraphrase retention; ordinary-text positions per available cell: [245237]. Own-prompt retention is shown for each arm, not assumed identical.

| Dataset | Seed | BP RET-ES | ePC RET-ES | RET-GS difference (percentage points) | BP fired | ePC fired |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 1 | 1 | -2.666667 | 18 | 0 |
| counterfact | 0 | 1 | 1 | -24.16667 | 256 | 185 |
| zsre | 1 | 1 | 1 | -2 | 13 | 6 |
| counterfact | 1 | 0.99 | 1 | -2.166667 | 660 | 720 |

ePC paraphrase retention is lower in every fully paired row available here. The deficits range from 2.00 to 24.17 percentage points; the magnitude matters. On counterfact, the ePC-minus-BP firing direction reverses across seeds. The three-seed comparison remains partial. Read seed-specific magnitudes and directions together: a quieter reader is not itself improved editing. Descriptive spreads are not confidence intervals. Comparisons intersect seed identities, never a mean of three BP seeds minus fewer ePC seeds. Training seeds reuse one subject realization. No training losses are compared as though settled ePC CE and feedforward BP CE were the same objective.



## Training and measured costs

The earlier **37×** ratio in lead-queue item 144 was a ten-update profile projection (about 37 minutes BP versus 22.6 hours ePC), not completed-run timing. Actual whole-training ratios below supersede it for measured cost. Components are not added to their parent receipts. Profiles, failed attempts and completed runs remain in the JSON cost inventory; unclosed runs have unknown cost, not zero. Process-hours do not imply elapsed portfolio hours.

| Rule | Seed | Status | Steps | Parameters | Process seconds | Hours |
| --- | --- | --- | --- | --- | --- | --- |
| bp | 0 | complete | 300 | 3348228 | 866.5778 | 0.2407161 |
| bp | 1 | complete | 300 | 3348228 | 906.5266 | 0.251813 |
| bp | 2 | complete | 300 | 3348228 | 872.0438 | 0.2422344 |
| epc | 0 | complete | 300 | 3348228 | 88483.01 | 24.57862 |
| epc | 1 | complete | 300 | 3348228 | 86801.75 | 24.1116 |
| epc | 2 | unfinished; no terminal report | — | — | — | — |

| Paired seed | Measured ePC/BP training time |
| --- | --- |
| 0 | 102.1063 |
| 1 | 95.75201 |
| 2 | — |

All known top-level process receipts (including profiles): 55.2364 hours; 1 directories have no terminal cost yet.

## Per-cell efficacy

| Cell | Status | ES | RET-ES | RET-GS | LS | near_miss | revision | Unseen fires / observed / planned |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bp s0 zsre | complete | 1 | 1 | 0.9733333 | 1 | 0.85 | 1 | 4 / 100 / 100 |
| bp s0 counterfact | complete | 1 | 1 | 0.81 | 1 | 1 | 1 | 0 / 100 / 100 |
| bp s1 zsre | complete | 1 | 1 | 0.99 | 1 | 0.67 | 1 | 14 / 100 / 100 |
| bp s1 counterfact | complete | 0.99 | 0.99 | 0.8 | 1 | 0.99 | 0.98 | 1 / 100 / 100 |
| bp s2 zsre | complete | 1 | 1 | 0.9766667 | 1 | 0.73 | 1 | 11 / 100 / 100 |
| bp s2 counterfact | complete | 1 | 1 | 0.835 | 1 | 1 | 1 | 0 / 100 / 100 |
| epc s0 zsre | complete | 1 | 1 | 0.9466667 | 1 | 0.91 | 1 | 2 / 100 / 100 |
| epc s0 counterfact | complete | 1 | 1 | 0.5683333 | 1 | 0.98 | 1 | 0 / 100 / 100 |
| epc s1 zsre | complete | 1 | 1 | 0.97 | 1 | 0.85 | 1 | 5 / 100 / 100 |
| epc s1 counterfact | complete | 1 | 1 | 0.7783333 | 1 | 0.95 | 1 | 1 / 100 / 100 |
| epc s2 zsre | missing | — | — | — | — | — | — | — |
| epc s2 counterfact | missing | — | — | — | — | — | — | — |

Values use planned denominators; no unavailable slot is reinterpreted as a correct answer. ES is immediate acquisition success; RET-ES/RET-GS are retained own-prompt/paraphrase scores.

| Cell | Endpoint | Numerator | Scored / planned | Status |
| --- | --- | --- | --- | --- |
| bp s0 zsre | ES | 300 | 300 / 300 | complete |
| bp s0 zsre | RET-ES | 300 | 300 / 300 | complete |
| bp s0 zsre | RET-GS | 292 | 300 / 300 | complete |
| bp s0 zsre | LS | 50 | 50 / 50 | complete |
| bp s0 zsre | near_miss | 85 | 100 / 100 | complete |
| bp s0 zsre | revision | 50 | 50 / 50 | complete |
| bp s0 counterfact | ES | 300 | 300 / 300 | complete |
| bp s0 counterfact | RET-ES | 300 | 300 / 300 | complete |
| bp s0 counterfact | RET-GS | 243 | 300 / 300 | complete |
| bp s0 counterfact | LS | 50 | 50 / 50 | complete |
| bp s0 counterfact | near_miss | 100 | 100 / 100 | complete |
| bp s0 counterfact | revision | 50 | 50 / 50 | complete |
| bp s1 zsre | ES | 300 | 300 / 300 | complete |
| bp s1 zsre | RET-ES | 300 | 300 / 300 | complete |
| bp s1 zsre | RET-GS | 297 | 300 / 300 | complete |
| bp s1 zsre | LS | 50 | 50 / 50 | complete |
| bp s1 zsre | near_miss | 67 | 100 / 100 | complete |
| bp s1 zsre | revision | 50 | 50 / 50 | complete |
| bp s1 counterfact | ES | 297 | 300 / 300 | complete |
| bp s1 counterfact | RET-ES | 297 | 300 / 300 | complete |
| bp s1 counterfact | RET-GS | 240 | 300 / 300 | complete |
| bp s1 counterfact | LS | 50 | 50 / 50 | complete |
| bp s1 counterfact | near_miss | 99 | 100 / 100 | complete |
| bp s1 counterfact | revision | 49 | 50 / 50 | complete |
| bp s2 zsre | ES | 300 | 300 / 300 | complete |
| bp s2 zsre | RET-ES | 300 | 300 / 300 | complete |
| bp s2 zsre | RET-GS | 293 | 300 / 300 | complete |
| bp s2 zsre | LS | 50 | 50 / 50 | complete |
| bp s2 zsre | near_miss | 73 | 100 / 100 | complete |
| bp s2 zsre | revision | 50 | 50 / 50 | complete |
| bp s2 counterfact | ES | 300 | 300 / 300 | complete |
| bp s2 counterfact | RET-ES | 300 | 300 / 300 | complete |
| bp s2 counterfact | RET-GS | 250.5 | 300 / 300 | complete |
| bp s2 counterfact | LS | 50 | 50 / 50 | complete |
| bp s2 counterfact | near_miss | 100 | 100 / 100 | complete |
| bp s2 counterfact | revision | 50 | 50 / 50 | complete |
| epc s0 zsre | ES | 300 | 300 / 300 | complete |
| epc s0 zsre | RET-ES | 300 | 300 / 300 | complete |
| epc s0 zsre | RET-GS | 284 | 300 / 300 | complete |
| epc s0 zsre | LS | 50 | 50 / 50 | complete |
| epc s0 zsre | near_miss | 91 | 100 / 100 | complete |
| epc s0 zsre | revision | 50 | 50 / 50 | complete |
| epc s0 counterfact | ES | 300 | 300 / 300 | complete |
| epc s0 counterfact | RET-ES | 300 | 300 / 300 | complete |
| epc s0 counterfact | RET-GS | 170.5 | 300 / 300 | complete |
| epc s0 counterfact | LS | 50 | 50 / 50 | complete |
| epc s0 counterfact | near_miss | 98 | 100 / 100 | complete |
| epc s0 counterfact | revision | 50 | 50 / 50 | complete |
| epc s1 zsre | ES | 300 | 300 / 300 | complete |
| epc s1 zsre | RET-ES | 300 | 300 / 300 | complete |
| epc s1 zsre | RET-GS | 291 | 300 / 300 | complete |
| epc s1 zsre | LS | 50 | 50 / 50 | complete |
| epc s1 zsre | near_miss | 85 | 100 / 100 | complete |
| epc s1 zsre | revision | 50 | 50 / 50 | complete |
| epc s1 counterfact | ES | 300 | 300 / 300 | complete |
| epc s1 counterfact | RET-ES | 300 | 300 / 300 | complete |
| epc s1 counterfact | RET-GS | 233.5 | 300 / 300 | complete |
| epc s1 counterfact | LS | 50 | 50 / 50 | complete |
| epc s1 counterfact | near_miss | 95 | 100 / 100 | complete |
| epc s1 counterfact | revision | 50 | 50 / 50 | complete |

## Fidelity and ordinary-text gate telemetry

Own cap-off reference; original-base summaries and full exceedance records are also retained in the JSON. Mean KL .001 is a descriptive fidelity watch, not data-integrity status. Harmful changes and gate firings are different quantities.

| Cell | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL | Δ>.01 / >.1 / >1 | Fired / hard null / positions |
| --- | --- | --- | --- | --- | --- | --- |
| bp s0 zsre | 0.0001107215 | 0.000109969 | 0.01170186 | 6.506296 | 15/14/9 | 18 / 245219 / 245237 |
| bp s0 counterfact | 0.002012263 | 0.002020257 | 0.2070025 | 8.51933 | 227/217/149 | 256 / 244981 / 245237 |
| bp s1 zsre | 0.0001344412 | 0.0001254599 | 0.01273685 | 7.922522 | 12/12/9 | 13 / 245224 / 245237 |
| bp s1 counterfact | 0.005166184 | 0.005352227 | 0.5512697 | 12.50178 | 567/548/363 | 660 / 244577 / 245237 |
| bp s2 zsre | 0.000169764 | 0.0001800639 | 0.01832748 | 10.57568 | 19/19/15 | 21 / 245216 / 245237 |
| bp s2 counterfact | 0.001119561 | 0.001183002 | 0.1207727 | 9.864664 | 138/136/83 | 149 / 245088 / 245237 |
| epc s0 zsre | 0 | 0 | 0 | 0 | 0/0/0 | 0 / 245237 / 245237 |
| epc s0 counterfact | 0.001269378 | 0.001280413 | 0.132428 | 7.706048 | 162/156/112 | 185 / 245052 / 245237 |
| epc s1 zsre | 5.335085e-05 | 4.562495e-05 | 0.004845909 | 4.449725 | 4/4/4 | 6 / 245231 / 245237 |
| epc s1 counterfact | 0.006185039 | 0.006282489 | 0.6412834 | 12.36299 | 636/612/419 | 720 / 244517 / 245237 |

## Evaluation costs and allocated storage

Process seconds include construction, acquisition, endpoints and harm. Stream and harm are subsets, not extra charges. Inactive dense write slots remain charged; active-coordinate bytes are not a storage saving.

| Cell | Process s | Stream s (subset) | Harm s (subset) | Parameters | Delta allocated bytes | Delta active bytes | Total allocated bytes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bp s0 zsre | 1716.045 | 511.6396 | 1200.518 | 3348228 | 10229760 | 10229760 | 24288920 |
| bp s0 counterfact | 1696.773 | 508.0424 | 1184.849 | 3348228 | 5529600 | 5529600 | 19584784 |
| bp s1 zsre | 1717.861 | 513.0456 | 1200.929 | 3348228 | 10229760 | 10229760 | 24288920 |
| bp s1 counterfact | 1696.976 | 509.1746 | 1183.908 | 3348228 | 5529600 | 5529600 | 19584784 |
| bp s2 zsre | 1725.536 | 513.0481 | 1208.589 | 3348228 | 10229760 | 10229760 | 24288920 |
| bp s2 counterfact | 1686.338 | 507.0371 | 1175.395 | 3348228 | 5529600 | 5529600 | 19584784 |
| epc s0 zsre | 1744.051 | 516.673 | 1223.442 | 3348228 | 10229760 | 10229760 | 24288920 |
| epc s0 counterfact | 1729.058 | 528.6436 | 1196.47 | 3348228 | 5529600 | 5529600 | 19584784 |
| epc s1 zsre | 1757.871 | 515.6639 | 1237.648 | 3348228 | 10229760 | 10229760 | 24288920 |
| epc s1 counterfact | 1758.425 | 513.8211 | 1240.488 | 3348228 | 5529600 | 5529600 | 19584784 |
| epc s2 zsre | — | — | — | — | — | — | — |
| epc s2 counterfact | — | — | — | — | — | — | — |

## Paired BP minus ePC, by seed

Positive behavior differences favor BP; positive harm differences mean BP has more loss. These are differences of each arm's ES99, not the ES99 of pointwise differences.

| Dataset | Seed | Status | ES | RET-ES | RET-GS | LS | near_miss | revision | mean_kl | mean_delta_nll | es99_positive | maximum_positive | Fired |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | paired | 0 | 0 | 0.02666667 | 0 | -0.06 | 0 | 0.0001107215 | 0.000109969 | 0.01170186 | 6.506296 | 18 |
| zsre | 1 | paired | 0 | 0 | 0.02 | 0 | -0.18 | 0 | 8.109036e-05 | 7.98349e-05 | 0.007890938 | 3.472797 | 7 |
| zsre | 2 | missing pair | — | — | — | — | — | — | — | — | — | — | — |
| counterfact | 0 | paired | 0 | 0 | 0.2416667 | 0 | 0.02 | 0 | 0.0007428849 | 0.0007398435 | 0.0745745 | 0.8132821 | 71 |
| counterfact | 1 | paired | -0.01 | -0.01 | 0.02166667 | 0 | 0.04 | -0.02 | -0.001018855 | -0.0009302617 | -0.09001367 | 0.1387877 | -60 |
| counterfact | 2 | missing pair | — | — | — | — | — | — | — | — | — | — | — |

## Training-seed spread (descriptive)

Sample SD is undefined for one seed; ranges are not confidence intervals. Paired seed spread is in the JSON.

| Dataset | Rule | Metric | Seeds / 3 | Mean | Min | Max | Sample SD |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | bp | ES | 3 | 1 | 1 | 1 | 0 |
| zsre | bp | RET-ES | 3 | 1 | 1 | 1 | 0 |
| zsre | bp | RET-GS | 3 | 0.98 | 0.9733333 | 0.99 | 0.008819171 |
| zsre | bp | LS | 3 | 1 | 1 | 1 | 0 |
| zsre | bp | near_miss | 3 | 0.75 | 0.67 | 0.85 | 0.09165151 |
| zsre | bp | revision | 3 | 1 | 1 | 1 | 0 |
| zsre | bp | mean_kl | 3 | 0.0001383089 | 0.0001107215 | 0.000169764 | 2.971065e-05 |
| zsre | bp | mean_delta_nll | 3 | 0.0001384976 | 0.000109969 | 0.0001800639 | 3.682134e-05 |
| zsre | bp | es99_positive | 3 | 0.01425539 | 0.01170186 | 0.01832748 | 0.003564292 |
| zsre | bp | maximum_positive | 3 | 8.334832 | 6.506296 | 10.57568 | 2.065785 |
| zsre | bp | fired | 3 | 17.33333 | 13 | 21 | 4.041452 |
| zsre | epc | ES | 2 | 1 | 1 | 1 | 0 |
| zsre | epc | RET-ES | 2 | 1 | 1 | 1 | 0 |
| zsre | epc | RET-GS | 2 | 0.9583333 | 0.9466667 | 0.97 | 0.01649916 |
| zsre | epc | LS | 2 | 1 | 1 | 1 | 0 |
| zsre | epc | near_miss | 2 | 0.88 | 0.85 | 0.91 | 0.04242641 |
| zsre | epc | revision | 2 | 1 | 1 | 1 | 0 |
| zsre | epc | mean_kl | 2 | 2.667542e-05 | 0 | 5.335085e-05 | 3.772474e-05 |
| zsre | epc | mean_delta_nll | 2 | 2.281248e-05 | 0 | 4.562495e-05 | 3.226171e-05 |
| zsre | epc | es99_positive | 2 | 0.002422954 | 0 | 0.004845909 | 0.003426575 |
| zsre | epc | maximum_positive | 2 | 2.224862 | 0 | 4.449725 | 3.146431 |
| zsre | epc | fired | 2 | 3 | 0 | 6 | 4.242641 |
| counterfact | bp | ES | 3 | 0.9966667 | 0.99 | 1 | 0.005773503 |
| counterfact | bp | RET-ES | 3 | 0.9966667 | 0.99 | 1 | 0.005773503 |
| counterfact | bp | RET-GS | 3 | 0.815 | 0.8 | 0.835 | 0.01802776 |
| counterfact | bp | LS | 3 | 1 | 1 | 1 | 0 |
| counterfact | bp | near_miss | 3 | 0.9966667 | 0.99 | 1 | 0.005773503 |
| counterfact | bp | revision | 3 | 0.9933333 | 0.98 | 1 | 0.01154701 |
| counterfact | bp | mean_kl | 3 | 0.002766003 | 0.001119561 | 0.005166184 | 0.002126002 |
| counterfact | bp | mean_delta_nll | 3 | 0.002851829 | 0.001183002 | 0.005352227 | 0.002205503 |
| counterfact | bp | es99_positive | 3 | 0.293015 | 0.1207727 | 0.5512697 | 0.227773 |
| counterfact | bp | maximum_positive | 3 | 10.29526 | 8.51933 | 12.50178 | 2.025843 |
| counterfact | bp | fired | 3 | 355 | 149 | 660 | 269.5014 |
| counterfact | epc | ES | 2 | 1 | 1 | 1 | 0 |
| counterfact | epc | RET-ES | 2 | 1 | 1 | 1 | 0 |
| counterfact | epc | RET-GS | 2 | 0.6733333 | 0.5683333 | 0.7783333 | 0.1484924 |
| counterfact | epc | LS | 2 | 1 | 1 | 1 | 0 |
| counterfact | epc | near_miss | 2 | 0.965 | 0.95 | 0.98 | 0.0212132 |
| counterfact | epc | revision | 2 | 1 | 1 | 1 | 0 |
| counterfact | epc | mean_kl | 2 | 0.003727209 | 0.001269378 | 0.006185039 | 0.003475897 |
| counterfact | epc | mean_delta_nll | 2 | 0.003781451 | 0.001280413 | 0.006282489 | 0.003537002 |
| counterfact | epc | es99_positive | 2 | 0.3868557 | 0.132428 | 0.6412834 | 0.3598151 |
| counterfact | epc | maximum_positive | 2 | 10.03452 | 7.706048 | 12.36299 | 3.292958 |
| counterfact | epc | fired | 2 | 452.5 | 185 | 720 | 378.3021 |

## Historical selected v5 reference

Same exposed streams and adjoint acquisition; the previously selected artifact is not a new paired seed or an unbiased sample of training outcomes. Selection and recipe history differ. Its values do not establish causal superiority over these newly trained readers. The underlying fixed-v5 report includes the independently repaired harm completion record.

| Dataset | ES | RET-ES | RET-GS | LS | near_miss | revision | Mean KL | ES99+ | Max ΔNLL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 1 | 1 | 0.9833333 | 1 | 0.76 | 1 | 0.001860621 | 0.195585 | 9.262267 |
| counterfact | 1 | 1 | 0.8066667 | 1 | 1 | 1 | 0.004175656 | 0.4586865 | 11.74424 |

## HT-17 reader rows

Source: `/home/derp/cap/pc_cap/logs/additional_work/reproductions/round61-verified/ht17/report.json`. Rows below match the exact saved vector hashes. 0 completed reader rows lack a matching tail refresh. Training seeds and repeated ordinary-text positions do not become independent subject samples. Conditional severity is undefined when no position exceeds the threshold.

| Rule | Seed | Dataset | Frequency Δ>.01 | Conditional severity | Fit status |
| --- | --- | --- | --- | --- | --- |
| bp | 0 | zsre | 6.116532e-05 | 1.913153 | not_identified |
| bp | 0 | counterfact | 0.0009256352 | 2.236311 | eligible |
| bp | 1 | zsre | 4.893226e-05 | 2.602955 | not_identified |
| bp | 1 | counterfact | 0.002312049 | 2.384318 | eligible |
| bp | 2 | zsre | 7.747607e-05 | 2.365566 | not_identified |
| bp | 2 | counterfact | 0.000562721 | 2.146227 | eligible |
| epc | 0 | zsre | 0 | — | not_identified |
| epc | 0 | counterfact | 0.0006605855 | 2.004707 | eligible |
| epc | 1 | zsre | 1.631075e-05 | 2.97099 | not_identified |
| epc | 1 | counterfact | 0.00259341 | 2.472731 | eligible |

The full [HT-17 report](HT-17_report.md) retains threshold checks, joint-window intervals and invalid fits. This snapshot matches 10 of 10 completed reader evaluations; any exceptions are listed above. Rerun into a **new** directory when remaining seeds finish:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
../venv/bin/python -m aw.pc_reader_report \
  --refresh-tail logs/additional_work/HT-17/reader-complete-NEW \
  --output logs/additional_work/PC-reader/report-NEW
```

This runs the CPU HT-17 refresh (200 joint-window draws, secondary conditions included), then reads its newly matched reader rows and refreshes this document. The figure refresh command is in HT-17_report.md. No model is loaded and no GPU work is scheduled. Experimental cutoff remains October 9 at 17:00 EDT.
