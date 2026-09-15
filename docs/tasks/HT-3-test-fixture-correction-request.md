# HT-3 test-fixture correction request

Only tests/revision_v1/test_ht_kappa_actual.py changes. All corrected test functions pass in memory, including both parametrized bound cases.

1. synthetic_episode requires history_size >= 2; use 2 instead of 1.
2. At kappa=1e-4 and surprisal 8.39636, the real mathematical difference from ordinary CE is approximately kappa*S^2/2 = 0.003525. The original 0.0008 tolerance was too tight even for exact arithmetic. Use 0.005 absolute tolerance for this limit check; exact equality for explicit kappa=0 remains separately required. This does not excuse the separately reproduced float32 cancellation at kappa=1e-10.

Exact patch: HT-3-test-fixture-correction.patch. No trainer or objective change is included.
