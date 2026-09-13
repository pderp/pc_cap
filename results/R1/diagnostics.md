# Revision v1 — Stage 0 diagnostics D0 / D1 / D2 (v0 cap, zsRE development, 100 edits; X0-14 revision)

## C1 (stream: ES 1.000, RET-ES 0.920, RET-GS 0.240, LS 1.000; occupancy {'1': 362, '2': 361, '3': 362})

| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 query key L2 mean (max) | D2 retrieval differs (stored keys / rebuilt keys) | key rebuild L2 mean (max) vs radius |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | 96 / 1 / 3 | 0.26 / 0.30 / 0.44 | 0.000 | 0.0000 (0.000) | 0.000 / 0.000 | 0.0008 (0.193) vs 0.281 |
| 2 | 88 / 9 / 3 | 0.19 / 0.54 / 0.27 | 0.000 | 0.2182 (0.525) | 0.410 / 0.390 | 0.2176 (0.642) vs 0.414 |
| 3 | 92 / 5 / 3 | 0.23 / 0.72 / 0.05 | 0.000 | 0.1790 (0.379) | 0.490 / 0.380 | 0.2304 (1.326) vs 0.189 |

| D1/D2 outcomes | n | policy | exact answer | TF NLL / answer | TF NLL / token | first-token NLL | unavailable oracle positions |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| prompt | 100 | live | 0.920 | 0.556 | 0.168 | 0.496 | 0 |
| prompt | 100 | oracle | 0.930 | 0.466 | 0.131 | 0.014 | 126 |
| prompt | 100 | stable | 0.350 | 5.867 | 1.725 | 4.508 | 0 |
| prompt | 100 | stable_rebuilt | 1.000 | 0.065 | 0.019 | 0.014 | 0 |
| paraphrase | 100 | live | 0.240 | 7.642 | 2.492 | 7.021 | 0 |
| paraphrase | 100 | oracle | 0.940 | 0.478 | 0.139 | 0.038 | 126 |
| paraphrase | 100 | stable | 0.110 | 9.571 | 2.974 | 7.854 | 0 |
| paraphrase | 100 | stable_rebuilt | 0.670 | 4.369 | 1.359 | 3.881 | 0 |

Oracle verification (bank × prefix entries): claimed 1094, verified 1080, reused/inactive 14, target mismatch 0, missing prefix 112.
Ledger: stream Δ accel 88.3 s; diagnostics Δ accel 14.7 s vs by-purpose sum 14.7 s (live 2.8, oracle 2.7, stable_read 2.4, stable_rebuilt_read 2.7, stable_keys 2.6, rebuild_keys 0.5, d0_probe 0.6, unrelated 0.3).

## C2 (stream: ES 1.000, RET-ES 0.790, RET-GS 0.290, LS 1.000; occupancy {'1': 6, '2': 4, '3': 364})

| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 query key L2 mean (max) | D2 retrieval differs (stored keys / rebuilt keys) | key rebuild L2 mean (max) vs radius |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 1 | 4 / 55 / 41 | 0.01 / 0.58 / 0.41 | 0.000 | 0.0000 (0.000) | 0.000 / 0.000 | 0.0000 (0.000) vs 0.281 |
| 2 | 2 / 79 / 19 | 0.01 / 0.73 / 0.26 | 0.000 | 0.1755 (0.544) | 0.180 / 0.180 | 0.0000 (0.000) vs 0.414 |
| 3 | 77 / 18 / 5 | 0.32 / 0.58 / 0.10 | 0.000 | 0.1296 (0.361) | 0.465 / 0.350 | 0.0262 (0.361) vs 0.189 |

| D1/D2 outcomes | n | policy | exact answer | TF NLL / answer | TF NLL / token | first-token NLL | unavailable oracle positions |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| prompt | 100 | live | 0.790 | 2.353 | 0.744 | 2.343 | 0 |
| prompt | 100 | oracle | 0.920 | 0.578 | 0.157 | 0.186 | 832 |
| prompt | 100 | stable | 0.620 | 4.370 | 1.253 | 3.899 | 0 |
| prompt | 100 | stable_rebuilt | 0.980 | 0.538 | 0.088 | 0.162 | 0 |
| paraphrase | 100 | live | 0.290 | 8.122 | 2.399 | 7.133 | 0 |
| paraphrase | 100 | oracle | 0.940 | 0.549 | 0.148 | 0.189 | 832 |
| paraphrase | 100 | stable | 0.290 | 9.347 | 2.802 | 8.302 | 0 |
| paraphrase | 100 | stable_rebuilt | 0.490 | 8.328 | 2.484 | 7.344 | 0 |

Oracle verification (bank × prefix entries): claimed 374, verified 374, reused/inactive 0, target mismatch 0, missing prefix 832.
Ledger: stream Δ accel 20.2 s; diagnostics Δ accel 9.8 s vs by-purpose sum 9.8 s (live 1.6, oracle 1.4, stable_read 1.4, stable_rebuilt_read 1.5, stable_keys 2.6, rebuild_keys 0.5, d0_probe 0.5, unrelated 0.3).

