# Revision v1 — Stage 0 diagnostics D0 / D1 / D2 (v0 cap, zsRE development, 100 edits)

## C1 (stream: ES 1.000, RET-ES 0.920, RET-GS 0.240, LS 1.000; occupancy {'1': 362, '2': 361, '3': 362})

| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 key L2 mean (max) | D2 retrieval differs |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | 96 / 1 / 3 | 0.26 / 0.30 / 0.44 | 0.000 | 0.0000 (0.000) | 0.000 |
| 2 | 88 / 9 / 3 | 0.19 / 0.54 / 0.27 | 0.000 | 0.2182 (0.525) | 0.410 |
| 3 | 92 / 5 / 3 | 0.23 / 0.72 / 0.05 | 0.000 | 0.1790 (0.379) | 0.490 |

| D1 | n | exact answer, live retrieval | exact answer, oracle slots | first-token NLL live → oracle |
| --- | ---: | ---: | ---: | --- |
| prompt | 100 | 0.920 | 0.800 | 0.496 → 0.014 |
| paraphrase | 100 | 0.240 | 0.800 | 7.021 → 0.038 |

## C2 (stream: ES 1.000, RET-ES 0.790, RET-GS 0.290, LS 1.000; occupancy {'1': 6, '2': 4, '3': 364})

| site | prompt fires own / none / other | paraphrase recall (own) / none / other | unrelated firing rate | D2 key L2 mean (max) | D2 retrieval differs |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | 4 / 55 / 41 | 0.01 / 0.58 / 0.41 | 0.000 | 0.0000 (0.000) | 0.000 |
| 2 | 2 / 79 / 19 | 0.01 / 0.73 / 0.26 | 0.000 | 0.1755 (0.544) | 0.180 |
| 3 | 77 / 18 / 5 | 0.32 / 0.58 / 0.10 | 0.000 | 0.1296 (0.361) | 0.465 |

| D1 | n | exact answer, live retrieval | exact answer, oracle slots | first-token NLL live → oracle |
| --- | ---: | ---: | ---: | --- |
| prompt | 100 | 0.790 | 0.770 | 2.343 → 0.186 |
| paraphrase | 100 | 0.290 | 0.770 | 7.133 → 0.189 |

