# R1-15 — matched-update control (MatchedUpdateCap: stable keys + gradient value steps) on the Stage 0 stream (100 zsRE development edits, v2 calibration)

| arm | variant | ES | RET-ES | RET-GS | LS | occupancy | paraphrase site-3 own / none / other | unrelated firing |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| C1 | live (Stage 0) | 1.000 | 0.920 | 0.240 | 1.000 | {'1': 362, '2': 361, '3': 362} | 23 / 72 / 5 | 0.000 |
| C1 | v0-stable (R1-14) | 1.000 | 0.990 | 0.440 | 1.000 | {'1': 362, '2': 357, '3': 364} | 46 / 36 / 18 | 0.000 |
| C1 | matched-update | 1.000 | 0.990 | 0.440 | 1.000 | {'1': 363, '2': 358, '3': 366} | 45 / 36 / 19 | 0.000 |
| C2 | live (Stage 0) | 1.000 | 0.790 | 0.290 | 1.000 | {'1': 6, '2': 4, '3': 364} | 32 / 58 / 10 | 0.000 |
| C2 | v0-stable (R1-14) | 0.990 | 0.970 | 0.440 | 1.000 | {'1': 6, '2': 3, '3': 365} | 46 / 36 / 18 | 0.000 |
| C2 | matched-update | 1.000 | 0.990 | 0.440 | 1.000 | {'1': 363, '2': 358, '3': 366} | 45 / 36 / 19 | 0.000 |
