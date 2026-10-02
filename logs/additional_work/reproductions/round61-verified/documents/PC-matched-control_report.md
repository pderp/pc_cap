# PC-12 SE-AM control

exposed S5; exploratory DEC-075 control; one order, three realizations. Differences are SE-AM minus SE-A.

Treatment: `{"accounting": "actual charged operations including rolled-back attempts; report unused allowance and completed rounds", "arm": "SE-AM", "credit": "adjoint-matched", "extra_compute": "additional transactional acquisition rounds, not repeated unchanged-write gradients", "interpretation": "equal offered per-item operation allowance; not equal FLOPs, wall time, number of writes, or always equal realized spend", "matching": "per-item measured SE-E learning full_forwards + partial_forwards + reverses", "prefix_policy": "gold-prefix order; same threshold and per-round A; R ceiling replaced by remaining operation allowance", "reference_credit": "error", "reference_credit_iters": 8, "stop": "threshold attained for all prefixes, or next base call exceeds allowance; unfinished round rolled back"}`.

| Dataset | Realization | ES | RET-ES | RET-GS | LS | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | -0.019 | -0.012 | 0.01 | 0 | -0.019 | -0.012 | 0.01 | 0 |
| zsre | 1 | -0.013 | -0.002 | 0.018 | 0.015 | -0.013 | -0.002 | 0.018 | 0.015 |
| zsre | 2 | -0.013 | -0.008 | 0.006 | 0.035 | -0.013 | -0.008 | 0.006 | 0.035 |
| counterfact | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

| Dataset | Realization | Arm | Process seconds | Forwards | Partial forwards | Reverses | Settling |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | 985.897 | 139630 | 237711 | 11334 | 0 |
| zsre | 0 | SE-AM | 994.388 | 139354 | 237191 | 11322 | 0 |
| zsre | 1 | SE-A | 968.786 | 138528 | 233410 | 11047 | 0 |
| zsre | 1 | SE-AM | 1007.04 | 138675 | 232136 | 11047 | 0 |
| zsre | 2 | SE-A | 984.444 | 139227 | 235222 | 11261 | 0 |
| zsre | 2 | SE-AM | 1000.29 | 138000 | 234252 | 11300 | 0 |
| counterfact | 0 | SE-A | 440.765 | 90025 | 37476 | 1826 | 0 |
| counterfact | 0 | SE-AM | 444.884 | 90025 | 37476 | 1826 | 0 |
| counterfact | 1 | SE-A | 426.254 | 87823 | 38544 | 1836 | 0 |
| counterfact | 1 | SE-AM | 429.775 | 87823 | 38544 | 1836 | 0 |
| counterfact | 2 | SE-A | 432.501 | 88193 | 38772 | 1818 | 0 |
| counterfact | 2 | SE-AM | 434.034 | 88193 | 38772 | 1818 | 0 |

Three realizations, one order each; no independence or superiority claim from tokens. The matched arm has an equal offered operation allowance, not guaranteed equal realized spend or FLOPs. The random arm pays the true error-credit cost before replacing orientation. Separate ordinary-text harm is not inferred from efficacy.

| Dataset | Realization | Offered ops | Used ops | Threshold stops | Incomplete round rollbacks |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | 391311 | 225484 | 945 | 55 |
| zsre | 1 | 380888 | 219015 | 953 | 43 |
| zsre | 2 | 388261 | 225589 | 962 | 35 |
| counterfact | 0 | 61344 | 32996 | 300 | 0 |
| counterfact | 1 | 62026 | 33456 | 300 | 0 |
| counterfact | 2 | 61096 | 32628 | 300 | 0 |

