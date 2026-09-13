# Full-validation LM drift supplement (X2-05 / SD-3)

Rendered 2026-09-13T17:34:08Z from `results/S4/drift_supplement.json`. Endpoint learner states of the zsRE realization-0, order-0 runs (experiment `frozen-confirmatory-v2-84126123`), scored on 245,110 positions of the validation split (128-token windows, cap-on full recompute per position; the runs' recorded assay used 4,064 positions). Base NLL 4.0802. Run concurrently with the v3 grammar rerun on the same GPU (wall times only). **Supplementary**: it does not change any frozen classification; drift is not a primary endpoint.

| arm | Δ NLL (full split) | perplexity ratio (full) | ratio (recorded 4,064-position assay) |
| --- | ---: | ---: | ---: |
| C0 | +0.00096 | 1.0010 | 1.0000 |
| C1 | +0.00193 | 1.0019 | 1.0025 |
| C2 | +0.00355 | 1.0036 | 1.0000 |
| CR | +0.00303 | 1.0030 | 1.0008 |
| B3 | +0.63356 | 1.8843 | 2.2560 |

Reading: on the whole validation split every cap arm's endpoint state raises the language-model perplexity by at most 0.4% (C2 1.0036, CR 1.0030, C1 1.0019, C0 1.0010); the recorded 4,064-position assay understated C2 and CR (it happened to contain no window on which their caps fired) but placed all four in the same band. B3 (LoRA + replay) raises perplexity by 88% on the full split (the 4,064-position assay said 126%). One order and one realization per arm; the other 55 zsRE endpoints were not scored (≈ 12 min each).
