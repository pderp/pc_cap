# R1-49g — DEC-057/058/059 analysis

DEC-066: 285 core cells plus 45 optional. The five omitted MQuAKE arms are prospectively not run; calibration implications are not measured per-cell outcomes.

Scope: confirmatory. GPU/model calls: zero.
DEC-064 secondary benchmarks; numeric cap failures do not veto primary comparisons.

The 63 intervals use nominal Bonferroni allocation of 0.05 and three realization clusters; exact familywise coverage is not claimed.

| Dataset | Contrast | RET-GS realization estimates | Registered RET-GS interval | Preliminary classification |
|---|---|---|---|---|
| zsre | primary-vs-R1_nonlearned | [0.45299999999999996, None, None] | None | unavailable |
| zsre | primary-vs-v0_stable | [0.7707999999999999, None, None] | None | unavailable |
| zsre | primary-vs-matched_update | [None, None, None] | None | unavailable |
| zsre | primary-vs-v0_live_C1 | [None, None, None] | None | unavailable |
| zsre | primary-vs-v0_live_C2 | [None, None, None] | None | unavailable |
| zsre | primary-vs-S1_LM | [None, None, None] | None | unavailable |
| zsre | primary-vs-S1_literal | [None, None, None] | None | unavailable |
| counterfact | primary-vs-R1_nonlearned | [0.5655, None, None] | None | unavailable |
| counterfact | primary-vs-v0_stable | [0.6915, None, None] | None | unavailable |
| counterfact | primary-vs-matched_update | [None, None, None] | None | unavailable |
| counterfact | primary-vs-v0_live_C1 | [None, None, None] | None | unavailable |
| counterfact | primary-vs-v0_live_C2 | [None, None, None] | None | unavailable |
| counterfact | primary-vs-S1_LM | [None, None, None] | None | unavailable |
| counterfact | primary-vs-S1_literal | [None, None, None] | None | unavailable |
| mquake | primary-vs-R1_nonlearned | [None, None, None] | None | unavailable |
| mquake | primary-vs-v0_stable | [None, None, None] | None | unavailable |
| mquake | primary-vs-matched_update | [None, None, None] | None | unavailable |
| mquake | primary-vs-v0_live_C1 | [None, None, None] | None | unavailable |
| mquake | primary-vs-v0_live_C2 | [None, None, None] | None | unavailable |
| mquake | primary-vs-S1_LM | [None, None, None] | None | unavailable |
| mquake | primary-vs-S1_literal | [None, None, None] | None | unavailable |

DEC-069: preliminary summaries, not established population effects or demonstrated 95% familywise control.

| Dataset | Contrast | Metric | Realization/order dispersion | Secondary pointwise 95% t sensitivity (df=2; normal independent realization errors assumed) |
|---|---|---|---|---|
| zsre | primary-vs-R1_nonlearned (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.45299999999999996, 0.45299999999999996, 0.45299999999999996, 0.45299999999999996, 0.45299999999999996], 'complete': True, 'observed_orders': 5, 'mean': 0.45299999999999996, 'minimum': 0.45299999999999996, 'maximum': 0.45299999999999996, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=1000) | ES | [{'realization': 0, 'order_values': [-0.006000000000000005, -0.0050000000000000044, -0.006000000000000005, -0.007000000000000006, -0.008000000000000007], 'complete': True, 'observed_orders': 5, 'mean': -0.0064000000000000055, 'minimum': -0.008000000000000007, 'maximum': -0.0050000000000000044, 'sample_sd': 0.001140175425099139}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=1000) | LS | [{'realization': 0, 'order_values': [0.020000000000000018, 0.020000000000000018, 0.020000000000000018, 0.020000000000000018, 0.020000000000000018], 'complete': True, 'observed_orders': 5, 'mean': 0.020000000000000018, 'minimum': 0.020000000000000018, 'maximum': 0.020000000000000018, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.758, 0.7969999999999999, 0.7689999999999999, 0.7709999999999999, 0.7589999999999999], 'complete': True, 'observed_orders': 5, 'mean': 0.7707999999999999, 'minimum': 0.758, 'maximum': 0.7969999999999999, 'sample_sd': 0.015754364474646374}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | ES | [{'realization': 0, 'order_values': [-0.006000000000000005, -0.0050000000000000044, -0.006000000000000005, -0.007000000000000006, -0.008000000000000007], 'complete': True, 'observed_orders': 5, 'mean': -0.0064000000000000055, 'minimum': -0.008000000000000007, 'maximum': -0.0050000000000000044, 'sample_sd': 0.001140175425099139}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.5655, 0.5655, 0.5655, 0.5655, 0.5655], 'complete': True, 'observed_orders': 5, 'mean': 0.5655, 'minimum': 0.5655, 'maximum': 0.5655, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | ES | [{'realization': 0, 'order_values': [-0.01100000000000001, -0.007000000000000006, -0.007000000000000006, -0.009000000000000008, -0.009000000000000008], 'complete': True, 'observed_orders': 5, 'mean': -0.008600000000000007, 'minimum': -0.01100000000000001, 'maximum': -0.007000000000000006, 'sample_sd': 0.0016733200530681524}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | LS | [{'realization': 0, 'order_values': [0.98, 0.98, 0.98, 0.98, 0.98], 'complete': True, 'observed_orders': 5, 'mean': 0.9800000000000001, 'minimum': 0.98, 'maximum': 0.98, 'sample_sd': 1.2412670766236366e-16}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.6915, 0.6915, 0.6915, 0.6915, 0.6915], 'complete': True, 'observed_orders': 5, 'mean': 0.6915, 'minimum': 0.6915, 'maximum': 0.6915, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | ES | [{'realization': 0, 'order_values': [-0.01100000000000001, -0.007000000000000006, -0.007000000000000006, -0.009000000000000008, -0.009000000000000008], 'complete': True, 'observed_orders': 5, 'mean': -0.008600000000000007, 'minimum': -0.01100000000000001, 'maximum': -0.007000000000000006, 'sample_sd': 0.0016733200530681524}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.39, 0.33999999999999997, 0.41000000000000003, 0.35, 0.30999999999999994], 'complete': True, 'observed_orders': 5, 'mean': 0.36000000000000004, 'minimum': 0.30999999999999994, 'maximum': 0.41000000000000003, 'sample_sd': 0.040000000000000036}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=100) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.44333333333333325, 0.41666666666666663, 0.41333333333333333, 0.4033333333333333, 0.41333333333333333], 'complete': True, 'observed_orders': 5, 'mean': 0.418, 'minimum': 0.4033333333333333, 'maximum': 0.44333333333333325, 'sample_sd': 0.015018507101425048}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=300) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.020000000000000018, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0040000000000000036, 'minimum': 0.0, 'maximum': 0.020000000000000018, 'sample_sd': 0.008944271909999166}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=1000) | ES | [{'realization': 0, 'order_values': [-0.006000000000000005, -0.0050000000000000044, -0.006000000000000005, -0.007000000000000006, -0.008000000000000007], 'complete': True, 'observed_orders': 5, 'mean': -0.0064000000000000055, 'minimum': -0.008000000000000007, 'maximum': -0.0050000000000000044, 'sample_sd': 0.001140175425099139}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.45299999999999996, 0.45299999999999996, 0.45299999999999996, 0.45299999999999996, 0.45299999999999996], 'complete': True, 'observed_orders': 5, 'mean': 0.45299999999999996, 'minimum': 0.45299999999999996, 'maximum': 0.45299999999999996, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-R1_nonlearned (n=1000) | LS | [{'realization': 0, 'order_values': [0.020000000000000018, 0.020000000000000018, 0.020000000000000018, 0.020000000000000018, 0.020000000000000018], 'complete': True, 'observed_orders': 5, 'mean': 0.020000000000000018, 'minimum': 0.020000000000000018, 'maximum': 0.020000000000000018, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.59, 0.49, 0.5700000000000001, 0.51, 0.44999999999999996], 'complete': True, 'observed_orders': 5, 'mean': 0.522, 'minimum': 0.44999999999999996, 'maximum': 0.59, 'sample_sd': 0.05761944116355175}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=100) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.06000000000000005], 'complete': True, 'observed_orders': 5, 'mean': 0.01200000000000001, 'minimum': 0.0, 'maximum': 0.06000000000000005, 'sample_sd': 0.0268328157299975}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.6666666666666666, 0.6299999999999999, 0.6733333333333333, 0.6566666666666666, 0.64], 'complete': True, 'observed_orders': 5, 'mean': 0.6533333333333333, 'minimum': 0.6299999999999999, 'maximum': 0.6733333333333333, 'sample_sd': 0.018104634152000382}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=300) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | ES | [{'realization': 0, 'order_values': [-0.006000000000000005, -0.0050000000000000044, -0.006000000000000005, -0.007000000000000006, -0.008000000000000007], 'complete': True, 'observed_orders': 5, 'mean': -0.0064000000000000055, 'minimum': -0.008000000000000007, 'maximum': -0.0050000000000000044, 'sample_sd': 0.001140175425099139}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.758, 0.7969999999999999, 0.7689999999999999, 0.7709999999999999, 0.7589999999999999], 'complete': True, 'observed_orders': 5, 'mean': 0.7707999999999999, 'minimum': 0.758, 'maximum': 0.7969999999999999, 'sample_sd': 0.015754364474646374}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_stable (n=1000) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-matched_update (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C1 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-v0_live_C2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_LM (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-S1_literal (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| zsre | primary-vs-historical-v2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.625, 0.6000000000000001, 0.6, 0.57, 0.6699999999999999], 'complete': True, 'observed_orders': 5, 'mean': 0.613, 'minimum': 0.57, 'maximum': 0.6699999999999999, 'sample_sd': 0.03734969879396618}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=100) | LS | [{'realization': 0, 'order_values': [0.86, 0.98, 0.92, 0.96, 0.84], 'complete': True, 'observed_orders': 5, 'mean': 0.9119999999999999, 'minimum': 0.84, 'maximum': 0.98, 'sample_sd': 0.06099180272790763}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, -0.0033333333333332993, 0.0], 'complete': True, 'observed_orders': 5, 'mean': -0.0006666666666666598, 'minimum': -0.0033333333333332993, 'maximum': 0.0, 'sample_sd': 0.0014907119849998445}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.6483333333333333, 0.6133333333333334, 0.6033333333333333, 0.6183333333333333, 0.6900000000000001], 'complete': True, 'observed_orders': 5, 'mean': 0.6346666666666667, 'minimum': 0.6033333333333333, 'maximum': 0.6900000000000001, 'sample_sd': 0.035186013635471095}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=300) | LS | [{'realization': 0, 'order_values': [0.98, 0.98, 0.98, 0.96, 0.96], 'complete': True, 'observed_orders': 5, 'mean': 0.9719999999999999, 'minimum': 0.96, 'maximum': 0.98, 'sample_sd': 0.010954451150103333}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | ES | [{'realization': 0, 'order_values': [-0.01100000000000001, -0.007000000000000006, -0.007000000000000006, -0.009000000000000008, -0.009000000000000008], 'complete': True, 'observed_orders': 5, 'mean': -0.008600000000000007, 'minimum': -0.01100000000000001, 'maximum': -0.007000000000000006, 'sample_sd': 0.0016733200530681524}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.5655, 0.5655, 0.5655, 0.5655, 0.5655], 'complete': True, 'observed_orders': 5, 'mean': 0.5655, 'minimum': 0.5655, 'maximum': 0.5655, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-R1_nonlearned (n=1000) | LS | [{'realization': 0, 'order_values': [0.98, 0.98, 0.98, 0.98, 0.98], 'complete': True, 'observed_orders': 5, 'mean': 0.9800000000000001, 'minimum': 0.98, 'maximum': 0.98, 'sample_sd': 1.2412670766236366e-16}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.825, 0.785, 0.76, 0.835, 0.83], 'complete': True, 'observed_orders': 5, 'mean': 0.807, 'minimum': 0.76, 'maximum': 0.835, 'sample_sd': 0.032901367752724175}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=100) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, -0.020000000000000018], 'complete': True, 'observed_orders': 5, 'mean': -0.0040000000000000036, 'minimum': -0.020000000000000018, 'maximum': 0.0, 'sample_sd': 0.008944271909999168}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, -0.0033333333333332993, 0.0], 'complete': True, 'observed_orders': 5, 'mean': -0.0006666666666666598, 'minimum': -0.0033333333333332993, 'maximum': 0.0, 'sample_sd': 0.0014907119849998445}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.8066666666666666, 0.7266666666666667, 0.7483333333333333, 0.7583333333333333, 0.795], 'complete': True, 'observed_orders': 5, 'mean': 0.7669999999999999, 'minimum': 0.7266666666666667, 'maximum': 0.8066666666666666, 'sample_sd': 0.03319554856369216}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=300) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, -0.020000000000000018], 'complete': True, 'observed_orders': 5, 'mean': -0.0040000000000000036, 'minimum': -0.020000000000000018, 'maximum': 0.0, 'sample_sd': 0.008944271909999168}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | ES | [{'realization': 0, 'order_values': [-0.01100000000000001, -0.007000000000000006, -0.007000000000000006, -0.009000000000000008, -0.009000000000000008], 'complete': True, 'observed_orders': 5, 'mean': -0.008600000000000007, 'minimum': -0.01100000000000001, 'maximum': -0.007000000000000006, 'sample_sd': 0.0016733200530681524}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | RET-GS | [{'realization': 0, 'order_values': [0.6915, 0.6915, 0.6915, 0.6915, 0.6915], 'complete': True, 'observed_orders': 5, 'mean': 0.6915, 'minimum': 0.6915, 'maximum': 0.6915, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_stable (n=1000) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-matched_update (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C1 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-v0_live_C2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_LM (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-S1_literal (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=1000) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=1000) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| counterfact | primary-vs-historical-v2 (n=1000) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.68, 0.6, 0.64, 0.66, 0.7], 'complete': True, 'observed_orders': 5, 'mean': 0.656, 'minimum': 0.6, 'maximum': 0.7, 'sample_sd': 0.03847076812334269}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=100) | LS | [{'realization': 0, 'order_values': [1.0, 1.0, 1.0, 1.0, 1.0], 'complete': True, 'observed_orders': 5, 'mean': 1.0, 'minimum': 1.0, 'maximum': 1.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.7033333333333334, 0.7033333333333334, 0.7033333333333334, 0.7033333333333334, 0.7033333333333334], 'complete': True, 'observed_orders': 5, 'mean': 0.7033333333333334, 'minimum': 0.7033333333333334, 'maximum': 0.7033333333333334, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-R1_nonlearned (n=300) | LS | [{'realization': 0, 'order_values': [1.0, 1.0, 1.0, 1.0, 1.0], 'complete': True, 'observed_orders': 5, 'mean': 1.0, 'minimum': 1.0, 'maximum': 1.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=100) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=100) | RET-GS | [{'realization': 0, 'order_values': [0.68, 0.6, 0.64, 0.66, 0.7], 'complete': True, 'observed_orders': 5, 'mean': 0.656, 'minimum': 0.6, 'maximum': 0.7, 'sample_sd': 0.03847076812334269}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=100) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=300) | ES | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=300) | RET-GS | [{'realization': 0, 'order_values': [0.7033333333333334, 0.7033333333333334, 0.7033333333333334, 0.7033333333333334, 0.7033333333333334], 'complete': True, 'observed_orders': 5, 'mean': 0.7033333333333334, 'minimum': 0.7033333333333334, 'maximum': 0.7033333333333334, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_stable (n=300) | LS | [{'realization': 0, 'order_values': [0.0, 0.0, 0.0, 0.0, 0.0], 'complete': True, 'observed_orders': 5, 'mean': 0.0, 'minimum': 0.0, 'maximum': 0.0, 'sample_sd': 0.0}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-matched_update (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C1 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-v0_live_C2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_LM (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-S1_literal (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=100) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=100) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=100) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=300) | ES | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=300) | RET-GS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |
| mquake | primary-vs-historical-v2 (n=300) | LS | [{'realization': 0, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 1, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}, {'realization': 2, 'order_values': [None, None, None, None, None], 'complete': False, 'observed_orders': 0, 'mean': None, 'minimum': None, 'maximum': None, 'sample_sd': None}] | {'method': 'Student_t', 'confidence': 0.95, 'degrees_of_freedom': 2, 'critical_value': 4.302652729696142, 'family_adjusted': False, 'role': 'secondary_sensitivity_not_classifier_input', 'assumptions': 'independent identically distributed normal realization errors; not checked with n=3', 'status': 'unavailable', 'lower': None, 'upper': None, 'between_realization_sample_sd': None, 'zero_variance_caveat': None} |

Both adjusted and unadjusted intervals and all three realization estimates for every metric are in JSON.

| Cell | Benchmark | Value | Pass | Availability |
|---|---|---:|---|---|
| 61348508e40d54351613ab14 | revision_latest | 0.98 | True | complete |
| 61348508e40d54351613ab14 | old_alias_reappearance | 0.0 | True | complete |
| 61348508e40d54351613ab14 | revision_semantic | 0.98 | True | complete |
| 61348508e40d54351613ab14 | unseen_1000 | 0.09 | True | complete |
| 61348508e40d54351613ab14 | outside_change_1000_100 | 0.0 | True | complete |
| 61348508e40d54351613ab14 | retention_change | -0.015000000000000013 | True | complete |
| 61348508e40d54351613ab14 | es_change | -0.006000000000000005 | True | complete |
| 61348508e40d54351613ab14 | ls_change | 0.0 | True | complete |
| 61348508e40d54351613ab14 | state_budget_ratio | None | None | unavailable |
| 61348508e40d54351613ab14 | peak_budget_ratio | None | None | unavailable |
| 61348508e40d54351613ab14 | wall_budget_ratio | None | None | unavailable |
| 88af67fa5945b642e8ba7974 | revision_latest | 0.98 | True | complete |
| 88af67fa5945b642e8ba7974 | old_alias_reappearance | 0.0 | True | complete |
| 88af67fa5945b642e8ba7974 | revision_semantic | 0.98 | True | complete |
| 88af67fa5945b642e8ba7974 | unseen_1000 | 0.09 | True | complete |
| 88af67fa5945b642e8ba7974 | outside_change_1000_100 | 0.02 | True | complete |
| 88af67fa5945b642e8ba7974 | retention_change | -0.03500000000000003 | True | complete |
| 88af67fa5945b642e8ba7974 | es_change | -0.0050000000000000044 | True | complete |
| 88af67fa5945b642e8ba7974 | ls_change | 0.0 | True | complete |
| 88af67fa5945b642e8ba7974 | state_budget_ratio | None | None | unavailable |
| 88af67fa5945b642e8ba7974 | peak_budget_ratio | None | None | unavailable |
| 88af67fa5945b642e8ba7974 | wall_budget_ratio | None | None | unavailable |
| 915f97b05f3fa2a81de09cdf | revision_latest | 0.98 | True | complete |
| 915f97b05f3fa2a81de09cdf | old_alias_reappearance | 0.0 | True | complete |
| 915f97b05f3fa2a81de09cdf | revision_semantic | 0.98 | True | complete |
| 915f97b05f3fa2a81de09cdf | unseen_1000 | 0.09 | True | complete |
| 915f97b05f3fa2a81de09cdf | outside_change_1000_100 | -0.04 | True | complete |
| 915f97b05f3fa2a81de09cdf | retention_change | -0.04500000000000004 | True | complete |
| 915f97b05f3fa2a81de09cdf | es_change | -0.006000000000000005 | True | complete |
| 915f97b05f3fa2a81de09cdf | ls_change | 0.0 | True | complete |
| 915f97b05f3fa2a81de09cdf | state_budget_ratio | None | None | unavailable |
| 915f97b05f3fa2a81de09cdf | peak_budget_ratio | None | None | unavailable |
| 915f97b05f3fa2a81de09cdf | wall_budget_ratio | None | None | unavailable |
| 4aa4849ba414edab2504f56b | revision_latest | 0.98 | True | complete |
| 4aa4849ba414edab2504f56b | old_alias_reappearance | 0.0 | True | complete |
| 4aa4849ba414edab2504f56b | revision_semantic | 0.98 | True | complete |
| 4aa4849ba414edab2504f56b | unseen_1000 | 0.09 | True | complete |
| 4aa4849ba414edab2504f56b | outside_change_1000_100 | 0.05 | True | complete |
| 4aa4849ba414edab2504f56b | retention_change | -0.03500000000000003 | True | complete |
| 4aa4849ba414edab2504f56b | es_change | -0.007000000000000006 | True | complete |
| 4aa4849ba414edab2504f56b | ls_change | 0.0 | True | complete |
| 4aa4849ba414edab2504f56b | state_budget_ratio | None | None | unavailable |
| 4aa4849ba414edab2504f56b | peak_budget_ratio | None | None | unavailable |
| 4aa4849ba414edab2504f56b | wall_budget_ratio | None | None | unavailable |
| 9ebc93cc7912bd5d1c929418 | revision_latest | 0.98 | True | complete |
| 9ebc93cc7912bd5d1c929418 | old_alias_reappearance | 0.0 | True | complete |
| 9ebc93cc7912bd5d1c929418 | revision_semantic | 0.98 | True | complete |
| 9ebc93cc7912bd5d1c929418 | unseen_1000 | 0.09 | True | complete |
| 9ebc93cc7912bd5d1c929418 | outside_change_1000_100 | -0.02 | True | complete |
| 9ebc93cc7912bd5d1c929418 | retention_change | -0.025000000000000022 | True | complete |
| 9ebc93cc7912bd5d1c929418 | es_change | -0.008000000000000007 | True | complete |
| 9ebc93cc7912bd5d1c929418 | ls_change | 0.0 | True | complete |
| 9ebc93cc7912bd5d1c929418 | state_budget_ratio | None | None | unavailable |
| 9ebc93cc7912bd5d1c929418 | peak_budget_ratio | None | None | unavailable |
| 9ebc93cc7912bd5d1c929418 | wall_budget_ratio | None | None | unavailable |
| ce0d0ffc2a58a60e27c460d9 | revision_latest | 1.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | old_alias_reappearance | 0.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | revision_semantic | 1.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | unseen_1000 | 0.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | outside_change_1000_100 | 0.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | retention_change | -0.13349999999999995 | False | complete |
| ce0d0ffc2a58a60e27c460d9 | es_change | -0.01100000000000001 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | ls_change | 0.0 | True | complete |
| ce0d0ffc2a58a60e27c460d9 | state_budget_ratio | None | None | unavailable |
| ce0d0ffc2a58a60e27c460d9 | peak_budget_ratio | None | None | unavailable |
| ce0d0ffc2a58a60e27c460d9 | wall_budget_ratio | None | None | unavailable |
| 95dfb24c6361b2d38dd60e9b | revision_latest | 1.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | old_alias_reappearance | 0.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | revision_semantic | 1.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | unseen_1000 | 0.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | outside_change_1000_100 | 0.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | retention_change | -0.09350000000000003 | False | complete |
| 95dfb24c6361b2d38dd60e9b | es_change | -0.007000000000000006 | True | complete |
| 95dfb24c6361b2d38dd60e9b | ls_change | 0.0 | True | complete |
| 95dfb24c6361b2d38dd60e9b | state_budget_ratio | None | None | unavailable |
| 95dfb24c6361b2d38dd60e9b | peak_budget_ratio | None | None | unavailable |
| 95dfb24c6361b2d38dd60e9b | wall_budget_ratio | None | None | unavailable |
| 6d0915056b1e76d8ee8795ff | revision_latest | 1.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | old_alias_reappearance | 0.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | revision_semantic | 1.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | unseen_1000 | 0.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | outside_change_1000_100 | 0.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | retention_change | -0.0685 | False | complete |
| 6d0915056b1e76d8ee8795ff | es_change | -0.007000000000000006 | True | complete |
| 6d0915056b1e76d8ee8795ff | ls_change | 0.0 | True | complete |
| 6d0915056b1e76d8ee8795ff | state_budget_ratio | None | None | unavailable |
| 6d0915056b1e76d8ee8795ff | peak_budget_ratio | None | None | unavailable |
| 6d0915056b1e76d8ee8795ff | wall_budget_ratio | None | None | unavailable |
| 7c9675a69d832a772070cb2d | revision_latest | 1.0 | True | complete |
| 7c9675a69d832a772070cb2d | old_alias_reappearance | 0.0 | True | complete |
| 7c9675a69d832a772070cb2d | revision_semantic | 1.0 | True | complete |
| 7c9675a69d832a772070cb2d | unseen_1000 | 0.0 | True | complete |
| 7c9675a69d832a772070cb2d | outside_change_1000_100 | 0.0 | True | complete |
| 7c9675a69d832a772070cb2d | retention_change | -0.14349999999999996 | False | complete |
| 7c9675a69d832a772070cb2d | es_change | -0.009000000000000008 | True | complete |
| 7c9675a69d832a772070cb2d | ls_change | 0.0 | True | complete |
| 7c9675a69d832a772070cb2d | state_budget_ratio | None | None | unavailable |
| 7c9675a69d832a772070cb2d | peak_budget_ratio | None | None | unavailable |
| 7c9675a69d832a772070cb2d | wall_budget_ratio | None | None | unavailable |
| 95016bc16e89cfcccccc40b8 | revision_latest | 1.0 | True | complete |
| 95016bc16e89cfcccccc40b8 | old_alias_reappearance | 0.0 | True | complete |
| 95016bc16e89cfcccccc40b8 | revision_semantic | 1.0 | True | complete |
| 95016bc16e89cfcccccc40b8 | unseen_1000 | 0.0 | True | complete |
| 95016bc16e89cfcccccc40b8 | outside_change_1000_100 | 0.0 | True | complete |
| 95016bc16e89cfcccccc40b8 | retention_change | -0.13849999999999996 | False | complete |
| 95016bc16e89cfcccccc40b8 | es_change | -0.009000000000000008 | True | complete |
| 95016bc16e89cfcccccc40b8 | ls_change | 0.020000000000000018 | True | complete |
| 95016bc16e89cfcccccc40b8 | state_budget_ratio | None | None | unavailable |
| 95016bc16e89cfcccccc40b8 | peak_budget_ratio | None | None | unavailable |
| 95016bc16e89cfcccccc40b8 | wall_budget_ratio | None | None | unavailable |
| 43925e53c31860219a85ef90 | revision_latest | 1.0 | True | complete |
| 43925e53c31860219a85ef90 | old_alias_reappearance | 0.0 | True | complete |
| 43925e53c31860219a85ef90 | revision_semantic | 1.0 | True | complete |
| 43925e53c31860219a85ef90 | unseen_1000 | None | None | unavailable |
| 43925e53c31860219a85ef90 | outside_change_1000_100 | None | None | unavailable |
| 43925e53c31860219a85ef90 | retention_change | None | None | unavailable |
| 43925e53c31860219a85ef90 | es_change | None | None | unavailable |
| 43925e53c31860219a85ef90 | ls_change | None | None | unavailable |
| 43925e53c31860219a85ef90 | state_budget_ratio | None | None | unavailable |
| 43925e53c31860219a85ef90 | peak_budget_ratio | None | None | unavailable |
| 43925e53c31860219a85ef90 | wall_budget_ratio | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | revision_latest | 1.0 | True | complete |
| c29ee18fb21ba6b387ede6e8 | old_alias_reappearance | 0.0 | True | complete |
| c29ee18fb21ba6b387ede6e8 | revision_semantic | 1.0 | True | complete |
| c29ee18fb21ba6b387ede6e8 | unseen_1000 | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | outside_change_1000_100 | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | retention_change | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | es_change | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | ls_change | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | state_budget_ratio | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | peak_budget_ratio | None | None | unavailable |
| c29ee18fb21ba6b387ede6e8 | wall_budget_ratio | None | None | unavailable |
| 54879da4dcdb0f106f98080a | revision_latest | 1.0 | True | complete |
| 54879da4dcdb0f106f98080a | old_alias_reappearance | 0.0 | True | complete |
| 54879da4dcdb0f106f98080a | revision_semantic | 1.0 | True | complete |
| 54879da4dcdb0f106f98080a | unseen_1000 | None | None | unavailable |
| 54879da4dcdb0f106f98080a | outside_change_1000_100 | None | None | unavailable |
| 54879da4dcdb0f106f98080a | retention_change | None | None | unavailable |
| 54879da4dcdb0f106f98080a | es_change | None | None | unavailable |
| 54879da4dcdb0f106f98080a | ls_change | None | None | unavailable |
| 54879da4dcdb0f106f98080a | state_budget_ratio | None | None | unavailable |
| 54879da4dcdb0f106f98080a | peak_budget_ratio | None | None | unavailable |
| 54879da4dcdb0f106f98080a | wall_budget_ratio | None | None | unavailable |
| 78ebbc03946239c1d637154c | revision_latest | 1.0 | True | complete |
| 78ebbc03946239c1d637154c | old_alias_reappearance | 0.0 | True | complete |
| 78ebbc03946239c1d637154c | revision_semantic | 1.0 | True | complete |
| 78ebbc03946239c1d637154c | unseen_1000 | None | None | unavailable |
| 78ebbc03946239c1d637154c | outside_change_1000_100 | None | None | unavailable |
| 78ebbc03946239c1d637154c | retention_change | None | None | unavailable |
| 78ebbc03946239c1d637154c | es_change | None | None | unavailable |
| 78ebbc03946239c1d637154c | ls_change | None | None | unavailable |
| 78ebbc03946239c1d637154c | state_budget_ratio | None | None | unavailable |
| 78ebbc03946239c1d637154c | peak_budget_ratio | None | None | unavailable |
| 78ebbc03946239c1d637154c | wall_budget_ratio | None | None | unavailable |
| b1d1e53944241333ec5603d4 | revision_latest | 1.0 | True | complete |
| b1d1e53944241333ec5603d4 | old_alias_reappearance | 0.0 | True | complete |
| b1d1e53944241333ec5603d4 | revision_semantic | 1.0 | True | complete |
| b1d1e53944241333ec5603d4 | unseen_1000 | None | None | unavailable |
| b1d1e53944241333ec5603d4 | outside_change_1000_100 | None | None | unavailable |
| b1d1e53944241333ec5603d4 | retention_change | None | None | unavailable |
| b1d1e53944241333ec5603d4 | es_change | None | None | unavailable |
| b1d1e53944241333ec5603d4 | ls_change | None | None | unavailable |
| b1d1e53944241333ec5603d4 | state_budget_ratio | None | None | unavailable |
| b1d1e53944241333ec5603d4 | peak_budget_ratio | None | None | unavailable |
| b1d1e53944241333ec5603d4 | wall_budget_ratio | None | None | unavailable |
| f3dbf1a3d5860a628e7d68ef | revision_latest | 1.0 | True | complete |
| f3dbf1a3d5860a628e7d68ef | old_alias_reappearance | 0.0 | True | complete |
| f3dbf1a3d5860a628e7d68ef | revision_semantic | 1.0 | True | complete |
| f3dbf1a3d5860a628e7d68ef | unseen_1000 | 1.0 | False | complete |
| f3dbf1a3d5860a628e7d68ef | outside_change_1000_100 | 0.0 | True | complete |
| f3dbf1a3d5860a628e7d68ef | retention_change | -0.07799999999999996 | False | complete |
| f3dbf1a3d5860a628e7d68ef | es_change | 0.0 | True | complete |
| f3dbf1a3d5860a628e7d68ef | ls_change | -0.020000000000000018 | False | complete |
| f3dbf1a3d5860a628e7d68ef | state_budget_ratio | None | None | unavailable |
| f3dbf1a3d5860a628e7d68ef | peak_budget_ratio | None | None | unavailable |
| f3dbf1a3d5860a628e7d68ef | wall_budget_ratio | None | None | unavailable |
| be44dfb501724b72adcbd747 | revision_latest | 1.0 | True | complete |
| be44dfb501724b72adcbd747 | old_alias_reappearance | 0.0 | True | complete |
| be44dfb501724b72adcbd747 | revision_semantic | 1.0 | True | complete |
| be44dfb501724b72adcbd747 | unseen_1000 | 1.0 | False | complete |
| be44dfb501724b72adcbd747 | outside_change_1000_100 | 0.0 | True | complete |
| be44dfb501724b72adcbd747 | retention_change | -0.14800000000000002 | False | complete |
| be44dfb501724b72adcbd747 | es_change | 0.0 | True | complete |
| be44dfb501724b72adcbd747 | ls_change | -0.020000000000000018 | False | complete |
| be44dfb501724b72adcbd747 | state_budget_ratio | None | None | unavailable |
| be44dfb501724b72adcbd747 | peak_budget_ratio | None | None | unavailable |
| be44dfb501724b72adcbd747 | wall_budget_ratio | None | None | unavailable |
| 5263d61e569d7cb4ceb4e617 | revision_latest | 1.0 | True | complete |
| 5263d61e569d7cb4ceb4e617 | old_alias_reappearance | 0.0 | True | complete |
| 5263d61e569d7cb4ceb4e617 | revision_semantic | 1.0 | True | complete |
| 5263d61e569d7cb4ceb4e617 | unseen_1000 | 1.0 | False | complete |
| 5263d61e569d7cb4ceb4e617 | outside_change_1000_100 | 0.0 | True | complete |
| 5263d61e569d7cb4ceb4e617 | retention_change | -0.08799999999999997 | False | complete |
| 5263d61e569d7cb4ceb4e617 | es_change | 0.0 | True | complete |
| 5263d61e569d7cb4ceb4e617 | ls_change | -0.020000000000000018 | False | complete |
| 5263d61e569d7cb4ceb4e617 | state_budget_ratio | None | None | unavailable |
| 5263d61e569d7cb4ceb4e617 | peak_budget_ratio | None | None | unavailable |
| 5263d61e569d7cb4ceb4e617 | wall_budget_ratio | None | None | unavailable |
| 81b1e9cb4e216a6cd1cd565a | revision_latest | 1.0 | True | complete |
| 81b1e9cb4e216a6cd1cd565a | old_alias_reappearance | 0.0 | True | complete |
| 81b1e9cb4e216a6cd1cd565a | revision_semantic | 1.0 | True | complete |
| 81b1e9cb4e216a6cd1cd565a | unseen_1000 | 1.0 | False | complete |
| 81b1e9cb4e216a6cd1cd565a | outside_change_1000_100 | 0.0 | True | complete |
| 81b1e9cb4e216a6cd1cd565a | retention_change | -0.138 | False | complete |
| 81b1e9cb4e216a6cd1cd565a | es_change | 0.0 | True | complete |
| 81b1e9cb4e216a6cd1cd565a | ls_change | -0.020000000000000018 | False | complete |
| 81b1e9cb4e216a6cd1cd565a | state_budget_ratio | None | None | unavailable |
| 81b1e9cb4e216a6cd1cd565a | peak_budget_ratio | None | None | unavailable |
| 81b1e9cb4e216a6cd1cd565a | wall_budget_ratio | None | None | unavailable |
| deb5f473d9ca2ed544926204 | revision_latest | 1.0 | True | complete |
| deb5f473d9ca2ed544926204 | old_alias_reappearance | 0.0 | True | complete |
| deb5f473d9ca2ed544926204 | revision_semantic | 1.0 | True | complete |
| deb5f473d9ca2ed544926204 | unseen_1000 | 1.0 | False | complete |
| deb5f473d9ca2ed544926204 | outside_change_1000_100 | 0.0 | True | complete |
| deb5f473d9ca2ed544926204 | retention_change | -0.16800000000000004 | False | complete |
| deb5f473d9ca2ed544926204 | es_change | 0.0 | True | complete |
| deb5f473d9ca2ed544926204 | ls_change | -0.020000000000000018 | False | complete |
| deb5f473d9ca2ed544926204 | state_budget_ratio | None | None | unavailable |
| deb5f473d9ca2ed544926204 | peak_budget_ratio | None | None | unavailable |
| deb5f473d9ca2ed544926204 | wall_budget_ratio | None | None | unavailable |
| 0b6ade77641a02c1c85574b0 | revision_latest | 1.0 | True | complete |
| 0b6ade77641a02c1c85574b0 | old_alias_reappearance | 0.16 | False | complete |
| 0b6ade77641a02c1c85574b0 | revision_semantic | 1.0 | True | complete |
| 0b6ade77641a02c1c85574b0 | unseen_1000 | 1.0 | False | complete |
| 0b6ade77641a02c1c85574b0 | outside_change_1000_100 | 0.06 | False | complete |
| 0b6ade77641a02c1c85574b0 | retention_change | -0.07400000000000001 | False | complete |
| 0b6ade77641a02c1c85574b0 | es_change | 0.0 | True | complete |
| 0b6ade77641a02c1c85574b0 | ls_change | -0.12000000000000001 | False | complete |
| 0b6ade77641a02c1c85574b0 | state_budget_ratio | None | None | unavailable |
| 0b6ade77641a02c1c85574b0 | peak_budget_ratio | None | None | unavailable |
| 0b6ade77641a02c1c85574b0 | wall_budget_ratio | None | None | unavailable |
| ee67c592789829e7dd808ede | revision_latest | 1.0 | True | complete |
| ee67c592789829e7dd808ede | old_alias_reappearance | 0.16 | False | complete |
| ee67c592789829e7dd808ede | revision_semantic | 1.0 | True | complete |
| ee67c592789829e7dd808ede | unseen_1000 | 1.0 | False | complete |
| ee67c592789829e7dd808ede | outside_change_1000_100 | 0.09 | False | complete |
| ee67c592789829e7dd808ede | retention_change | -0.059 | False | complete |
| ee67c592789829e7dd808ede | es_change | 0.0 | True | complete |
| ee67c592789829e7dd808ede | ls_change | 0.0 | True | complete |
| ee67c592789829e7dd808ede | state_budget_ratio | None | None | unavailable |
| ee67c592789829e7dd808ede | peak_budget_ratio | None | None | unavailable |
| ee67c592789829e7dd808ede | wall_budget_ratio | None | None | unavailable |
| 8be432675ed4dc57f9108bd4 | revision_latest | 1.0 | True | complete |
| 8be432675ed4dc57f9108bd4 | old_alias_reappearance | 0.16 | False | complete |
| 8be432675ed4dc57f9108bd4 | revision_semantic | 1.0 | True | complete |
| 8be432675ed4dc57f9108bd4 | unseen_1000 | 1.0 | False | complete |
| 8be432675ed4dc57f9108bd4 | outside_change_1000_100 | 0.07 | False | complete |
| 8be432675ed4dc57f9108bd4 | retention_change | -0.034 | True | complete |
| 8be432675ed4dc57f9108bd4 | es_change | 0.0 | True | complete |
| 8be432675ed4dc57f9108bd4 | ls_change | -0.06 | False | complete |
| 8be432675ed4dc57f9108bd4 | state_budget_ratio | None | None | unavailable |
| 8be432675ed4dc57f9108bd4 | peak_budget_ratio | None | None | unavailable |
| 8be432675ed4dc57f9108bd4 | wall_budget_ratio | None | None | unavailable |
| 78928f2782d91d888ef24d52 | revision_latest | 1.0 | True | complete |
| 78928f2782d91d888ef24d52 | old_alias_reappearance | 0.16 | False | complete |
| 78928f2782d91d888ef24d52 | revision_semantic | 1.0 | True | complete |
| 78928f2782d91d888ef24d52 | unseen_1000 | 1.0 | False | complete |
| 78928f2782d91d888ef24d52 | outside_change_1000_100 | 0.07 | False | complete |
| 78928f2782d91d888ef24d52 | retention_change | -0.139 | False | complete |
| 78928f2782d91d888ef24d52 | es_change | 0.0 | True | complete |
| 78928f2782d91d888ef24d52 | ls_change | -0.02 | False | complete |
| 78928f2782d91d888ef24d52 | state_budget_ratio | None | None | unavailable |
| 78928f2782d91d888ef24d52 | peak_budget_ratio | None | None | unavailable |
| 78928f2782d91d888ef24d52 | wall_budget_ratio | None | None | unavailable |
| de785feed05c9f4c2a9e9273 | revision_latest | 1.0 | True | complete |
| de785feed05c9f4c2a9e9273 | old_alias_reappearance | 0.16 | False | complete |
| de785feed05c9f4c2a9e9273 | revision_semantic | 1.0 | True | complete |
| de785feed05c9f4c2a9e9273 | unseen_1000 | 1.0 | False | complete |
| de785feed05c9f4c2a9e9273 | outside_change_1000_100 | 0.15 | False | complete |
| de785feed05c9f4c2a9e9273 | retention_change | -0.034 | True | complete |
| de785feed05c9f4c2a9e9273 | es_change | 0.0 | True | complete |
| de785feed05c9f4c2a9e9273 | ls_change | -0.12000000000000001 | False | complete |
| de785feed05c9f4c2a9e9273 | state_budget_ratio | None | None | unavailable |
| de785feed05c9f4c2a9e9273 | peak_budget_ratio | None | None | unavailable |
| de785feed05c9f4c2a9e9273 | wall_budget_ratio | None | None | unavailable |
| de0b9612418e6d573ed77679 | revision_latest | 1.0 | True | complete |
| de0b9612418e6d573ed77679 | old_alias_reappearance | 0.0 | True | complete |
| de0b9612418e6d573ed77679 | revision_semantic | 1.0 | True | complete |
| de0b9612418e6d573ed77679 | unseen_1000 | None | None | unavailable |
| de0b9612418e6d573ed77679 | outside_change_1000_100 | None | None | unavailable |
| de0b9612418e6d573ed77679 | retention_change | None | None | unavailable |
| de0b9612418e6d573ed77679 | es_change | None | None | unavailable |
| de0b9612418e6d573ed77679 | ls_change | None | None | unavailable |
| de0b9612418e6d573ed77679 | state_budget_ratio | None | None | unavailable |
| de0b9612418e6d573ed77679 | peak_budget_ratio | None | None | unavailable |
| de0b9612418e6d573ed77679 | wall_budget_ratio | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | revision_latest | 1.0 | True | complete |
| be37e2a1ff4a079e56efe268 | old_alias_reappearance | 0.0 | True | complete |
| be37e2a1ff4a079e56efe268 | revision_semantic | 1.0 | True | complete |
| be37e2a1ff4a079e56efe268 | unseen_1000 | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | outside_change_1000_100 | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | retention_change | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | es_change | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | ls_change | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | state_budget_ratio | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | peak_budget_ratio | None | None | unavailable |
| be37e2a1ff4a079e56efe268 | wall_budget_ratio | None | None | unavailable |
| 1e6b766c4139230c18547234 | revision_latest | 1.0 | True | complete |
| 1e6b766c4139230c18547234 | old_alias_reappearance | 0.0 | True | complete |
| 1e6b766c4139230c18547234 | revision_semantic | 1.0 | True | complete |
| 1e6b766c4139230c18547234 | unseen_1000 | None | None | unavailable |
| 1e6b766c4139230c18547234 | outside_change_1000_100 | None | None | unavailable |
| 1e6b766c4139230c18547234 | retention_change | None | None | unavailable |
| 1e6b766c4139230c18547234 | es_change | None | None | unavailable |
| 1e6b766c4139230c18547234 | ls_change | None | None | unavailable |
| 1e6b766c4139230c18547234 | state_budget_ratio | None | None | unavailable |
| 1e6b766c4139230c18547234 | peak_budget_ratio | None | None | unavailable |
| 1e6b766c4139230c18547234 | wall_budget_ratio | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | revision_latest | 1.0 | True | complete |
| c0a54c5fbf1ce7776efc983e | old_alias_reappearance | 0.0 | True | complete |
| c0a54c5fbf1ce7776efc983e | revision_semantic | 1.0 | True | complete |
| c0a54c5fbf1ce7776efc983e | unseen_1000 | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | outside_change_1000_100 | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | retention_change | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | es_change | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | ls_change | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | state_budget_ratio | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | peak_budget_ratio | None | None | unavailable |
| c0a54c5fbf1ce7776efc983e | wall_budget_ratio | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | revision_latest | 1.0 | True | complete |
| 7499c19b813dcada2c67ae39 | old_alias_reappearance | 0.0 | True | complete |
| 7499c19b813dcada2c67ae39 | revision_semantic | 1.0 | True | complete |
| 7499c19b813dcada2c67ae39 | unseen_1000 | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | outside_change_1000_100 | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | retention_change | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | es_change | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | ls_change | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | state_budget_ratio | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | peak_budget_ratio | None | None | unavailable |
| 7499c19b813dcada2c67ae39 | wall_budget_ratio | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | revision_latest | 0.0 | False | complete |
| 39c7fd4929721e8dcba56b94 | old_alias_reappearance | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | revision_semantic | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | unseen_1000 | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | outside_change_1000_100 | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | retention_change | -0.183 | False | complete |
| 39c7fd4929721e8dcba56b94 | es_change | 0.0 | True | complete |
| 39c7fd4929721e8dcba56b94 | ls_change | 0.0 | True | complete |
| 39c7fd4929721e8dcba56b94 | state_budget_ratio | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | peak_budget_ratio | None | None | unavailable |
| 39c7fd4929721e8dcba56b94 | wall_budget_ratio | None | None | unavailable |
| b887b1046cd563d990765e01 | revision_latest | 0.04 | False | complete |
| b887b1046cd563d990765e01 | old_alias_reappearance | None | None | unavailable |
| b887b1046cd563d990765e01 | revision_semantic | None | None | unavailable |
| b887b1046cd563d990765e01 | unseen_1000 | None | None | unavailable |
| b887b1046cd563d990765e01 | outside_change_1000_100 | None | None | unavailable |
| b887b1046cd563d990765e01 | retention_change | -0.34199999999999997 | False | complete |
| b887b1046cd563d990765e01 | es_change | 0.0 | True | complete |
| b887b1046cd563d990765e01 | ls_change | 0.0 | True | complete |
| b887b1046cd563d990765e01 | state_budget_ratio | None | None | unavailable |
| b887b1046cd563d990765e01 | peak_budget_ratio | None | None | unavailable |
| b887b1046cd563d990765e01 | wall_budget_ratio | None | None | unavailable |
| 435235a6719279d1cc87ad66 | revision_latest | 0.02 | False | complete |
| 435235a6719279d1cc87ad66 | old_alias_reappearance | None | None | unavailable |
| 435235a6719279d1cc87ad66 | revision_semantic | None | None | unavailable |
| 435235a6719279d1cc87ad66 | unseen_1000 | None | None | unavailable |
| 435235a6719279d1cc87ad66 | outside_change_1000_100 | None | None | unavailable |
| 435235a6719279d1cc87ad66 | retention_change | -0.244 | False | complete |
| 435235a6719279d1cc87ad66 | es_change | 0.0 | True | complete |
| 435235a6719279d1cc87ad66 | ls_change | 0.0 | True | complete |
| 435235a6719279d1cc87ad66 | state_budget_ratio | None | None | unavailable |
| 435235a6719279d1cc87ad66 | peak_budget_ratio | None | None | unavailable |
| 435235a6719279d1cc87ad66 | wall_budget_ratio | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | revision_latest | 0.0 | False | complete |
| aaed1cf9e8ce7cf1cf3749fa | old_alias_reappearance | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | revision_semantic | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | unseen_1000 | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | outside_change_1000_100 | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | retention_change | -0.296 | False | complete |
| aaed1cf9e8ce7cf1cf3749fa | es_change | 0.0 | True | complete |
| aaed1cf9e8ce7cf1cf3749fa | ls_change | 0.0 | True | complete |
| aaed1cf9e8ce7cf1cf3749fa | state_budget_ratio | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | peak_budget_ratio | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | wall_budget_ratio | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | revision_latest | 0.04 | False | complete |
| 92a5ef6855124ffc5a8d6163 | old_alias_reappearance | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | revision_semantic | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | unseen_1000 | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | outside_change_1000_100 | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | retention_change | -0.334 | False | complete |
| 92a5ef6855124ffc5a8d6163 | es_change | 0.0 | True | complete |
| 92a5ef6855124ffc5a8d6163 | ls_change | 0.06000000000000005 | True | complete |
| 92a5ef6855124ffc5a8d6163 | state_budget_ratio | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | peak_budget_ratio | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | wall_budget_ratio | None | None | unavailable |
| baa601113af675024e73bc30 | revision_latest | 0.0 | False | complete |
| baa601113af675024e73bc30 | old_alias_reappearance | None | None | unavailable |
| baa601113af675024e73bc30 | revision_semantic | None | None | unavailable |
| baa601113af675024e73bc30 | unseen_1000 | None | None | unavailable |
| baa601113af675024e73bc30 | outside_change_1000_100 | None | None | unavailable |
| baa601113af675024e73bc30 | retention_change | 0.0 | True | complete |
| baa601113af675024e73bc30 | es_change | 0.0 | True | complete |
| baa601113af675024e73bc30 | ls_change | 0.0 | True | complete |
| baa601113af675024e73bc30 | state_budget_ratio | None | None | unavailable |
| baa601113af675024e73bc30 | peak_budget_ratio | None | None | unavailable |
| baa601113af675024e73bc30 | wall_budget_ratio | None | None | unavailable |
| b6b271f3383f85fb19e49836 | revision_latest | 0.0 | False | complete |
| b6b271f3383f85fb19e49836 | old_alias_reappearance | None | None | unavailable |
| b6b271f3383f85fb19e49836 | revision_semantic | None | None | unavailable |
| b6b271f3383f85fb19e49836 | unseen_1000 | None | None | unavailable |
| b6b271f3383f85fb19e49836 | outside_change_1000_100 | None | None | unavailable |
| b6b271f3383f85fb19e49836 | retention_change | 0.0 | True | complete |
| b6b271f3383f85fb19e49836 | es_change | 0.0 | True | complete |
| b6b271f3383f85fb19e49836 | ls_change | 0.0 | True | complete |
| b6b271f3383f85fb19e49836 | state_budget_ratio | None | None | unavailable |
| b6b271f3383f85fb19e49836 | peak_budget_ratio | None | None | unavailable |
| b6b271f3383f85fb19e49836 | wall_budget_ratio | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | revision_latest | 0.0 | False | complete |
| 6c0124a2d35b8b4bf8d2a321 | old_alias_reappearance | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | revision_semantic | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | unseen_1000 | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | outside_change_1000_100 | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | retention_change | 0.0 | True | complete |
| 6c0124a2d35b8b4bf8d2a321 | es_change | 0.0 | True | complete |
| 6c0124a2d35b8b4bf8d2a321 | ls_change | 0.0 | True | complete |
| 6c0124a2d35b8b4bf8d2a321 | state_budget_ratio | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | peak_budget_ratio | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | wall_budget_ratio | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | revision_latest | 0.0 | False | complete |
| 37c2ba2be995719ac8972cf1 | old_alias_reappearance | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | revision_semantic | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | unseen_1000 | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | outside_change_1000_100 | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | retention_change | 0.0 | True | complete |
| 37c2ba2be995719ac8972cf1 | es_change | 0.0 | True | complete |
| 37c2ba2be995719ac8972cf1 | ls_change | 0.0 | True | complete |
| 37c2ba2be995719ac8972cf1 | state_budget_ratio | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | peak_budget_ratio | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | wall_budget_ratio | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | revision_latest | 0.0 | False | complete |
| d93ed5de9d4401cb3345c7bd | old_alias_reappearance | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | revision_semantic | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | unseen_1000 | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | outside_change_1000_100 | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | retention_change | 0.0 | True | complete |
| d93ed5de9d4401cb3345c7bd | es_change | 0.0 | True | complete |
| d93ed5de9d4401cb3345c7bd | ls_change | 0.0 | True | complete |
| d93ed5de9d4401cb3345c7bd | state_budget_ratio | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | peak_budget_ratio | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | wall_budget_ratio | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | revision_latest | 0.02 | False | complete |
| c2f9d3102987f746f4f31b8d | old_alias_reappearance | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | revision_semantic | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | unseen_1000 | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | outside_change_1000_100 | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | retention_change | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | es_change | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | ls_change | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | state_budget_ratio | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | peak_budget_ratio | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | wall_budget_ratio | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | revision_latest | 0.02 | False | complete |
| a23ae9063b37c21cfe657d47 | old_alias_reappearance | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | revision_semantic | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | unseen_1000 | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | outside_change_1000_100 | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | retention_change | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | es_change | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | ls_change | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | state_budget_ratio | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | peak_budget_ratio | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | wall_budget_ratio | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | revision_latest | 0.02 | False | complete |
| 5a6f61e06de0bca53b4a7377 | old_alias_reappearance | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | revision_semantic | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | unseen_1000 | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | outside_change_1000_100 | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | retention_change | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | es_change | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | ls_change | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | state_budget_ratio | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | peak_budget_ratio | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | wall_budget_ratio | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | revision_latest | 0.02 | False | complete |
| 03426d6e61fb6b41145c5d8e | old_alias_reappearance | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | revision_semantic | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | unseen_1000 | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | outside_change_1000_100 | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | retention_change | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | es_change | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | ls_change | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | state_budget_ratio | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | peak_budget_ratio | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | wall_budget_ratio | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | revision_latest | 0.02 | False | complete |
| 19f5d8535235334ffe1595e8 | old_alias_reappearance | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | revision_semantic | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | unseen_1000 | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | outside_change_1000_100 | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | retention_change | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | es_change | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | ls_change | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | state_budget_ratio | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | peak_budget_ratio | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | wall_budget_ratio | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | revision_latest | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | old_alias_reappearance | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | revision_semantic | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | unseen_1000 | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | outside_change_1000_100 | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | retention_change | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | es_change | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | ls_change | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | state_budget_ratio | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | peak_budget_ratio | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | wall_budget_ratio | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | revision_latest | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | old_alias_reappearance | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | revision_semantic | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | unseen_1000 | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | outside_change_1000_100 | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | retention_change | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | es_change | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | ls_change | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | state_budget_ratio | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | peak_budget_ratio | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | wall_budget_ratio | None | None | unavailable |
| 4eda9e6155b2755508e13091 | revision_latest | None | None | unavailable |
| 4eda9e6155b2755508e13091 | old_alias_reappearance | None | None | unavailable |
| 4eda9e6155b2755508e13091 | revision_semantic | None | None | unavailable |
| 4eda9e6155b2755508e13091 | unseen_1000 | None | None | unavailable |
| 4eda9e6155b2755508e13091 | outside_change_1000_100 | None | None | unavailable |
| 4eda9e6155b2755508e13091 | retention_change | None | None | unavailable |
| 4eda9e6155b2755508e13091 | es_change | None | None | unavailable |
| 4eda9e6155b2755508e13091 | ls_change | None | None | unavailable |
| 4eda9e6155b2755508e13091 | state_budget_ratio | None | None | unavailable |
| 4eda9e6155b2755508e13091 | peak_budget_ratio | None | None | unavailable |
| 4eda9e6155b2755508e13091 | wall_budget_ratio | None | None | unavailable |
| ab774e229a65298fdc117c96 | revision_latest | None | None | unavailable |
| ab774e229a65298fdc117c96 | old_alias_reappearance | None | None | unavailable |
| ab774e229a65298fdc117c96 | revision_semantic | None | None | unavailable |
| ab774e229a65298fdc117c96 | unseen_1000 | None | None | unavailable |
| ab774e229a65298fdc117c96 | outside_change_1000_100 | None | None | unavailable |
| ab774e229a65298fdc117c96 | retention_change | None | None | unavailable |
| ab774e229a65298fdc117c96 | es_change | None | None | unavailable |
| ab774e229a65298fdc117c96 | ls_change | None | None | unavailable |
| ab774e229a65298fdc117c96 | state_budget_ratio | None | None | unavailable |
| ab774e229a65298fdc117c96 | peak_budget_ratio | None | None | unavailable |
| ab774e229a65298fdc117c96 | wall_budget_ratio | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | revision_latest | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | old_alias_reappearance | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | revision_semantic | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | unseen_1000 | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | outside_change_1000_100 | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | retention_change | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | es_change | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | ls_change | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | state_budget_ratio | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | peak_budget_ratio | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | wall_budget_ratio | None | None | unavailable |
| 826332f387bd487a045d412f | revision_latest | None | None | unavailable |
| 826332f387bd487a045d412f | old_alias_reappearance | None | None | unavailable |
| 826332f387bd487a045d412f | revision_semantic | None | None | unavailable |
| 826332f387bd487a045d412f | unseen_1000 | None | None | unavailable |
| 826332f387bd487a045d412f | outside_change_1000_100 | None | None | unavailable |
| 826332f387bd487a045d412f | retention_change | None | None | unavailable |
| 826332f387bd487a045d412f | es_change | None | None | unavailable |
| 826332f387bd487a045d412f | ls_change | None | None | unavailable |
| 826332f387bd487a045d412f | state_budget_ratio | None | None | unavailable |
| 826332f387bd487a045d412f | peak_budget_ratio | None | None | unavailable |
| 826332f387bd487a045d412f | wall_budget_ratio | None | None | unavailable |
| 14d45f0e87126104057518af | revision_latest | None | None | unavailable |
| 14d45f0e87126104057518af | old_alias_reappearance | None | None | unavailable |
| 14d45f0e87126104057518af | revision_semantic | None | None | unavailable |
| 14d45f0e87126104057518af | unseen_1000 | None | None | unavailable |
| 14d45f0e87126104057518af | outside_change_1000_100 | None | None | unavailable |
| 14d45f0e87126104057518af | retention_change | None | None | unavailable |
| 14d45f0e87126104057518af | es_change | None | None | unavailable |
| 14d45f0e87126104057518af | ls_change | None | None | unavailable |
| 14d45f0e87126104057518af | state_budget_ratio | None | None | unavailable |
| 14d45f0e87126104057518af | peak_budget_ratio | None | None | unavailable |
| 14d45f0e87126104057518af | wall_budget_ratio | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | revision_latest | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | old_alias_reappearance | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | revision_semantic | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | unseen_1000 | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | outside_change_1000_100 | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | retention_change | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | es_change | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | ls_change | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | state_budget_ratio | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | peak_budget_ratio | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | wall_budget_ratio | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | revision_latest | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | old_alias_reappearance | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | revision_semantic | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | unseen_1000 | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | outside_change_1000_100 | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | retention_change | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | es_change | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | ls_change | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | state_budget_ratio | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | peak_budget_ratio | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | wall_budget_ratio | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | revision_latest | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | old_alias_reappearance | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | revision_semantic | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | unseen_1000 | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | outside_change_1000_100 | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | retention_change | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | es_change | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | ls_change | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | state_budget_ratio | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | peak_budget_ratio | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | wall_budget_ratio | None | None | unavailable |
| 19964c4e7f737707baad94a5 | revision_latest | None | None | unavailable |
| 19964c4e7f737707baad94a5 | old_alias_reappearance | None | None | unavailable |
| 19964c4e7f737707baad94a5 | revision_semantic | None | None | unavailable |
| 19964c4e7f737707baad94a5 | unseen_1000 | None | None | unavailable |
| 19964c4e7f737707baad94a5 | outside_change_1000_100 | None | None | unavailable |
| 19964c4e7f737707baad94a5 | retention_change | None | None | unavailable |
| 19964c4e7f737707baad94a5 | es_change | None | None | unavailable |
| 19964c4e7f737707baad94a5 | ls_change | None | None | unavailable |
| 19964c4e7f737707baad94a5 | state_budget_ratio | None | None | unavailable |
| 19964c4e7f737707baad94a5 | peak_budget_ratio | None | None | unavailable |
| 19964c4e7f737707baad94a5 | wall_budget_ratio | None | None | unavailable |
| 40ec11c9694b4265a013c682 | revision_latest | None | None | unavailable |
| 40ec11c9694b4265a013c682 | old_alias_reappearance | None | None | unavailable |
| 40ec11c9694b4265a013c682 | revision_semantic | None | None | unavailable |
| 40ec11c9694b4265a013c682 | unseen_1000 | None | None | unavailable |
| 40ec11c9694b4265a013c682 | outside_change_1000_100 | None | None | unavailable |
| 40ec11c9694b4265a013c682 | retention_change | None | None | unavailable |
| 40ec11c9694b4265a013c682 | es_change | None | None | unavailable |
| 40ec11c9694b4265a013c682 | ls_change | None | None | unavailable |
| 40ec11c9694b4265a013c682 | state_budget_ratio | None | None | unavailable |
| 40ec11c9694b4265a013c682 | peak_budget_ratio | None | None | unavailable |
| 40ec11c9694b4265a013c682 | wall_budget_ratio | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | revision_latest | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | old_alias_reappearance | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | revision_semantic | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | unseen_1000 | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | outside_change_1000_100 | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | retention_change | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | es_change | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | ls_change | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | state_budget_ratio | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | peak_budget_ratio | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | wall_budget_ratio | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | revision_latest | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | old_alias_reappearance | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | revision_semantic | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | unseen_1000 | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | outside_change_1000_100 | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | retention_change | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | es_change | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | ls_change | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | state_budget_ratio | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | peak_budget_ratio | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | wall_budget_ratio | None | None | unavailable |
| 1833a410c9e8704f6a379114 | revision_latest | None | None | unavailable |
| 1833a410c9e8704f6a379114 | old_alias_reappearance | None | None | unavailable |
| 1833a410c9e8704f6a379114 | revision_semantic | None | None | unavailable |
| 1833a410c9e8704f6a379114 | unseen_1000 | None | None | unavailable |
| 1833a410c9e8704f6a379114 | outside_change_1000_100 | None | None | unavailable |
| 1833a410c9e8704f6a379114 | retention_change | None | None | unavailable |
| 1833a410c9e8704f6a379114 | es_change | None | None | unavailable |
| 1833a410c9e8704f6a379114 | ls_change | None | None | unavailable |
| 1833a410c9e8704f6a379114 | state_budget_ratio | None | None | unavailable |
| 1833a410c9e8704f6a379114 | peak_budget_ratio | None | None | unavailable |
| 1833a410c9e8704f6a379114 | wall_budget_ratio | None | None | unavailable |
| 82606602ae475e73eb4401f9 | revision_latest | None | None | unavailable |
| 82606602ae475e73eb4401f9 | old_alias_reappearance | None | None | unavailable |
| 82606602ae475e73eb4401f9 | revision_semantic | None | None | unavailable |
| 82606602ae475e73eb4401f9 | unseen_1000 | None | None | unavailable |
| 82606602ae475e73eb4401f9 | outside_change_1000_100 | None | None | unavailable |
| 82606602ae475e73eb4401f9 | retention_change | None | None | unavailable |
| 82606602ae475e73eb4401f9 | es_change | None | None | unavailable |
| 82606602ae475e73eb4401f9 | ls_change | None | None | unavailable |
| 82606602ae475e73eb4401f9 | state_budget_ratio | None | None | unavailable |
| 82606602ae475e73eb4401f9 | peak_budget_ratio | None | None | unavailable |
| 82606602ae475e73eb4401f9 | wall_budget_ratio | None | None | unavailable |
| 2172052824abd70e8135366f | revision_latest | None | None | unavailable |
| 2172052824abd70e8135366f | old_alias_reappearance | None | None | unavailable |
| 2172052824abd70e8135366f | revision_semantic | None | None | unavailable |
| 2172052824abd70e8135366f | unseen_1000 | None | None | unavailable |
| 2172052824abd70e8135366f | outside_change_1000_100 | None | None | unavailable |
| 2172052824abd70e8135366f | retention_change | None | None | unavailable |
| 2172052824abd70e8135366f | es_change | None | None | unavailable |
| 2172052824abd70e8135366f | ls_change | None | None | unavailable |
| 2172052824abd70e8135366f | state_budget_ratio | None | None | unavailable |
| 2172052824abd70e8135366f | peak_budget_ratio | None | None | unavailable |
| 2172052824abd70e8135366f | wall_budget_ratio | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | revision_latest | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | old_alias_reappearance | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | revision_semantic | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | unseen_1000 | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | outside_change_1000_100 | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | retention_change | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | es_change | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | ls_change | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | state_budget_ratio | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | peak_budget_ratio | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | wall_budget_ratio | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | revision_latest | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | old_alias_reappearance | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | revision_semantic | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | unseen_1000 | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | outside_change_1000_100 | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | retention_change | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | es_change | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | ls_change | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | state_budget_ratio | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | peak_budget_ratio | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | wall_budget_ratio | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | revision_latest | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | old_alias_reappearance | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | revision_semantic | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | unseen_1000 | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | outside_change_1000_100 | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | retention_change | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | es_change | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | ls_change | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | state_budget_ratio | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | peak_budget_ratio | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | wall_budget_ratio | None | None | unavailable |
| a7d551c093fd3333314813a5 | revision_latest | None | None | unavailable |
| a7d551c093fd3333314813a5 | old_alias_reappearance | None | None | unavailable |
| a7d551c093fd3333314813a5 | revision_semantic | None | None | unavailable |
| a7d551c093fd3333314813a5 | unseen_1000 | None | None | unavailable |
| a7d551c093fd3333314813a5 | outside_change_1000_100 | None | None | unavailable |
| a7d551c093fd3333314813a5 | retention_change | None | None | unavailable |
| a7d551c093fd3333314813a5 | es_change | None | None | unavailable |
| a7d551c093fd3333314813a5 | ls_change | None | None | unavailable |
| a7d551c093fd3333314813a5 | state_budget_ratio | None | None | unavailable |
| a7d551c093fd3333314813a5 | peak_budget_ratio | None | None | unavailable |
| a7d551c093fd3333314813a5 | wall_budget_ratio | None | None | unavailable |
| c402523c2460a62d6040ddd0 | revision_latest | None | None | unavailable |
| c402523c2460a62d6040ddd0 | old_alias_reappearance | None | None | unavailable |
| c402523c2460a62d6040ddd0 | revision_semantic | None | None | unavailable |
| c402523c2460a62d6040ddd0 | unseen_1000 | None | None | unavailable |
| c402523c2460a62d6040ddd0 | outside_change_1000_100 | None | None | unavailable |
| c402523c2460a62d6040ddd0 | retention_change | None | None | unavailable |
| c402523c2460a62d6040ddd0 | es_change | None | None | unavailable |
| c402523c2460a62d6040ddd0 | ls_change | None | None | unavailable |
| c402523c2460a62d6040ddd0 | state_budget_ratio | None | None | unavailable |
| c402523c2460a62d6040ddd0 | peak_budget_ratio | None | None | unavailable |
| c402523c2460a62d6040ddd0 | wall_budget_ratio | None | None | unavailable |
| b103826472ba7653cd8fd13a | revision_latest | None | None | unavailable |
| b103826472ba7653cd8fd13a | old_alias_reappearance | None | None | unavailable |
| b103826472ba7653cd8fd13a | revision_semantic | None | None | unavailable |
| b103826472ba7653cd8fd13a | unseen_1000 | None | None | unavailable |
| b103826472ba7653cd8fd13a | outside_change_1000_100 | None | None | unavailable |
| b103826472ba7653cd8fd13a | retention_change | None | None | unavailable |
| b103826472ba7653cd8fd13a | es_change | None | None | unavailable |
| b103826472ba7653cd8fd13a | ls_change | None | None | unavailable |
| b103826472ba7653cd8fd13a | state_budget_ratio | None | None | unavailable |
| b103826472ba7653cd8fd13a | peak_budget_ratio | None | None | unavailable |
| b103826472ba7653cd8fd13a | wall_budget_ratio | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | revision_latest | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | old_alias_reappearance | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | revision_semantic | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | unseen_1000 | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | outside_change_1000_100 | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | retention_change | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | es_change | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | ls_change | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | state_budget_ratio | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | peak_budget_ratio | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | wall_budget_ratio | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | revision_latest | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | old_alias_reappearance | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | revision_semantic | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | unseen_1000 | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | outside_change_1000_100 | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | retention_change | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | es_change | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | ls_change | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | state_budget_ratio | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | peak_budget_ratio | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | wall_budget_ratio | None | None | unavailable |
| 144f77ff21860a8a089a8080 | revision_latest | None | None | unavailable |
| 144f77ff21860a8a089a8080 | old_alias_reappearance | None | None | unavailable |
| 144f77ff21860a8a089a8080 | revision_semantic | None | None | unavailable |
| 144f77ff21860a8a089a8080 | unseen_1000 | None | None | unavailable |
| 144f77ff21860a8a089a8080 | outside_change_1000_100 | None | None | unavailable |
| 144f77ff21860a8a089a8080 | retention_change | None | None | unavailable |
| 144f77ff21860a8a089a8080 | es_change | None | None | unavailable |
| 144f77ff21860a8a089a8080 | ls_change | None | None | unavailable |
| 144f77ff21860a8a089a8080 | state_budget_ratio | None | None | unavailable |
| 144f77ff21860a8a089a8080 | peak_budget_ratio | None | None | unavailable |
| 144f77ff21860a8a089a8080 | wall_budget_ratio | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | revision_latest | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | old_alias_reappearance | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | revision_semantic | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | unseen_1000 | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | outside_change_1000_100 | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | retention_change | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | es_change | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | ls_change | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | state_budget_ratio | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | peak_budget_ratio | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | wall_budget_ratio | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | revision_latest | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | old_alias_reappearance | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | revision_semantic | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | unseen_1000 | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | outside_change_1000_100 | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | retention_change | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | es_change | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | ls_change | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | state_budget_ratio | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | peak_budget_ratio | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | wall_budget_ratio | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | revision_latest | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | old_alias_reappearance | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | revision_semantic | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | unseen_1000 | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | outside_change_1000_100 | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | retention_change | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | es_change | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | ls_change | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | state_budget_ratio | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | peak_budget_ratio | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | wall_budget_ratio | None | None | unavailable |
| 1aff34869825a76d502d92a3 | revision_latest | None | None | unavailable |
| 1aff34869825a76d502d92a3 | old_alias_reappearance | None | None | unavailable |
| 1aff34869825a76d502d92a3 | revision_semantic | None | None | unavailable |
| 1aff34869825a76d502d92a3 | unseen_1000 | None | None | unavailable |
| 1aff34869825a76d502d92a3 | outside_change_1000_100 | None | None | unavailable |
| 1aff34869825a76d502d92a3 | retention_change | None | None | unavailable |
| 1aff34869825a76d502d92a3 | es_change | None | None | unavailable |
| 1aff34869825a76d502d92a3 | ls_change | None | None | unavailable |
| 1aff34869825a76d502d92a3 | state_budget_ratio | None | None | unavailable |
| 1aff34869825a76d502d92a3 | peak_budget_ratio | None | None | unavailable |
| 1aff34869825a76d502d92a3 | wall_budget_ratio | None | None | unavailable |
| 3b70d3d44297fc1197610228 | revision_latest | None | None | unavailable |
| 3b70d3d44297fc1197610228 | old_alias_reappearance | None | None | unavailable |
| 3b70d3d44297fc1197610228 | revision_semantic | None | None | unavailable |
| 3b70d3d44297fc1197610228 | unseen_1000 | None | None | unavailable |
| 3b70d3d44297fc1197610228 | outside_change_1000_100 | None | None | unavailable |
| 3b70d3d44297fc1197610228 | retention_change | None | None | unavailable |
| 3b70d3d44297fc1197610228 | es_change | None | None | unavailable |
| 3b70d3d44297fc1197610228 | ls_change | None | None | unavailable |
| 3b70d3d44297fc1197610228 | state_budget_ratio | None | None | unavailable |
| 3b70d3d44297fc1197610228 | peak_budget_ratio | None | None | unavailable |
| 3b70d3d44297fc1197610228 | wall_budget_ratio | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | revision_latest | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | old_alias_reappearance | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | revision_semantic | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | unseen_1000 | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | outside_change_1000_100 | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | retention_change | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | es_change | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | ls_change | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | state_budget_ratio | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | peak_budget_ratio | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | wall_budget_ratio | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | revision_latest | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | old_alias_reappearance | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | revision_semantic | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | unseen_1000 | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | outside_change_1000_100 | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | retention_change | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | es_change | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | ls_change | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | state_budget_ratio | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | peak_budget_ratio | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | wall_budget_ratio | None | None | unavailable |
| 0ff8a61a760d6836f469629b | revision_latest | None | None | unavailable |
| 0ff8a61a760d6836f469629b | old_alias_reappearance | None | None | unavailable |
| 0ff8a61a760d6836f469629b | revision_semantic | None | None | unavailable |
| 0ff8a61a760d6836f469629b | unseen_1000 | None | None | unavailable |
| 0ff8a61a760d6836f469629b | outside_change_1000_100 | None | None | unavailable |
| 0ff8a61a760d6836f469629b | retention_change | None | None | unavailable |
| 0ff8a61a760d6836f469629b | es_change | None | None | unavailable |
| 0ff8a61a760d6836f469629b | ls_change | None | None | unavailable |
| 0ff8a61a760d6836f469629b | state_budget_ratio | None | None | unavailable |
| 0ff8a61a760d6836f469629b | peak_budget_ratio | None | None | unavailable |
| 0ff8a61a760d6836f469629b | wall_budget_ratio | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | revision_latest | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | old_alias_reappearance | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | revision_semantic | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | unseen_1000 | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | outside_change_1000_100 | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | retention_change | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | es_change | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | ls_change | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | state_budget_ratio | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | peak_budget_ratio | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | wall_budget_ratio | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | revision_latest | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | old_alias_reappearance | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | revision_semantic | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | unseen_1000 | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | outside_change_1000_100 | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | retention_change | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | es_change | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | ls_change | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | state_budget_ratio | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | peak_budget_ratio | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | wall_budget_ratio | None | None | unavailable |
| cefda69ce81ca1253435bac7 | revision_latest | None | None | unavailable |
| cefda69ce81ca1253435bac7 | old_alias_reappearance | None | None | unavailable |
| cefda69ce81ca1253435bac7 | revision_semantic | None | None | unavailable |
| cefda69ce81ca1253435bac7 | unseen_1000 | None | None | unavailable |
| cefda69ce81ca1253435bac7 | outside_change_1000_100 | None | None | unavailable |
| cefda69ce81ca1253435bac7 | retention_change | None | None | unavailable |
| cefda69ce81ca1253435bac7 | es_change | None | None | unavailable |
| cefda69ce81ca1253435bac7 | ls_change | None | None | unavailable |
| cefda69ce81ca1253435bac7 | state_budget_ratio | None | None | unavailable |
| cefda69ce81ca1253435bac7 | peak_budget_ratio | None | None | unavailable |
| cefda69ce81ca1253435bac7 | wall_budget_ratio | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | revision_latest | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | old_alias_reappearance | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | revision_semantic | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | unseen_1000 | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | outside_change_1000_100 | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | retention_change | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | es_change | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | ls_change | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | state_budget_ratio | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | peak_budget_ratio | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | wall_budget_ratio | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | revision_latest | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | old_alias_reappearance | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | revision_semantic | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | unseen_1000 | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | outside_change_1000_100 | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | retention_change | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | es_change | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | ls_change | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | state_budget_ratio | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | peak_budget_ratio | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | wall_budget_ratio | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | revision_latest | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | old_alias_reappearance | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | revision_semantic | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | unseen_1000 | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | outside_change_1000_100 | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | retention_change | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | es_change | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | ls_change | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | state_budget_ratio | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | peak_budget_ratio | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | wall_budget_ratio | None | None | unavailable |
| 9179614db32d3fd8b437475b | revision_latest | None | None | unavailable |
| 9179614db32d3fd8b437475b | old_alias_reappearance | None | None | unavailable |
| 9179614db32d3fd8b437475b | revision_semantic | None | None | unavailable |
| 9179614db32d3fd8b437475b | unseen_1000 | None | None | unavailable |
| 9179614db32d3fd8b437475b | outside_change_1000_100 | None | None | unavailable |
| 9179614db32d3fd8b437475b | retention_change | None | None | unavailable |
| 9179614db32d3fd8b437475b | es_change | None | None | unavailable |
| 9179614db32d3fd8b437475b | ls_change | None | None | unavailable |
| 9179614db32d3fd8b437475b | state_budget_ratio | None | None | unavailable |
| 9179614db32d3fd8b437475b | peak_budget_ratio | None | None | unavailable |
| 9179614db32d3fd8b437475b | wall_budget_ratio | None | None | unavailable |
| e146662ae0ab343921979246 | revision_latest | None | None | unavailable |
| e146662ae0ab343921979246 | old_alias_reappearance | None | None | unavailable |
| e146662ae0ab343921979246 | revision_semantic | None | None | unavailable |
| e146662ae0ab343921979246 | unseen_1000 | None | None | unavailable |
| e146662ae0ab343921979246 | outside_change_1000_100 | None | None | unavailable |
| e146662ae0ab343921979246 | retention_change | None | None | unavailable |
| e146662ae0ab343921979246 | es_change | None | None | unavailable |
| e146662ae0ab343921979246 | ls_change | None | None | unavailable |
| e146662ae0ab343921979246 | state_budget_ratio | None | None | unavailable |
| e146662ae0ab343921979246 | peak_budget_ratio | None | None | unavailable |
| e146662ae0ab343921979246 | wall_budget_ratio | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | revision_latest | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | old_alias_reappearance | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | revision_semantic | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | unseen_1000 | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | outside_change_1000_100 | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | retention_change | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | es_change | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | ls_change | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | state_budget_ratio | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | peak_budget_ratio | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | wall_budget_ratio | None | None | unavailable |
| d49ef9c7980da822326bc6ac | revision_latest | None | None | unavailable |
| d49ef9c7980da822326bc6ac | old_alias_reappearance | None | None | unavailable |
| d49ef9c7980da822326bc6ac | revision_semantic | None | None | unavailable |
| d49ef9c7980da822326bc6ac | unseen_1000 | None | None | unavailable |
| d49ef9c7980da822326bc6ac | outside_change_1000_100 | None | None | unavailable |
| d49ef9c7980da822326bc6ac | retention_change | None | None | unavailable |
| d49ef9c7980da822326bc6ac | es_change | None | None | unavailable |
| d49ef9c7980da822326bc6ac | ls_change | None | None | unavailable |
| d49ef9c7980da822326bc6ac | state_budget_ratio | None | None | unavailable |
| d49ef9c7980da822326bc6ac | peak_budget_ratio | None | None | unavailable |
| d49ef9c7980da822326bc6ac | wall_budget_ratio | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | revision_latest | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | old_alias_reappearance | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | revision_semantic | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | unseen_1000 | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | outside_change_1000_100 | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | retention_change | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | es_change | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | ls_change | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | state_budget_ratio | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | peak_budget_ratio | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | wall_budget_ratio | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | revision_latest | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | old_alias_reappearance | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | revision_semantic | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | unseen_1000 | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | outside_change_1000_100 | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | retention_change | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | es_change | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | ls_change | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | state_budget_ratio | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | peak_budget_ratio | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | wall_budget_ratio | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | revision_latest | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | old_alias_reappearance | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | revision_semantic | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | unseen_1000 | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | outside_change_1000_100 | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | retention_change | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | es_change | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | ls_change | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | state_budget_ratio | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | peak_budget_ratio | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | wall_budget_ratio | None | None | unavailable |
| c2a67190edb39398491bd651 | revision_latest | None | None | unavailable |
| c2a67190edb39398491bd651 | old_alias_reappearance | None | None | unavailable |
| c2a67190edb39398491bd651 | revision_semantic | None | None | unavailable |
| c2a67190edb39398491bd651 | unseen_1000 | None | None | unavailable |
| c2a67190edb39398491bd651 | outside_change_1000_100 | None | None | unavailable |
| c2a67190edb39398491bd651 | retention_change | None | None | unavailable |
| c2a67190edb39398491bd651 | es_change | None | None | unavailable |
| c2a67190edb39398491bd651 | ls_change | None | None | unavailable |
| c2a67190edb39398491bd651 | state_budget_ratio | None | None | unavailable |
| c2a67190edb39398491bd651 | peak_budget_ratio | None | None | unavailable |
| c2a67190edb39398491bd651 | wall_budget_ratio | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | revision_latest | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | old_alias_reappearance | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | revision_semantic | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | unseen_1000 | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | outside_change_1000_100 | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | retention_change | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | es_change | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | ls_change | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | state_budget_ratio | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | peak_budget_ratio | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | wall_budget_ratio | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | revision_latest | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | old_alias_reappearance | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | revision_semantic | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | unseen_1000 | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | outside_change_1000_100 | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | retention_change | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | es_change | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | ls_change | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | state_budget_ratio | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | peak_budget_ratio | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | wall_budget_ratio | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | revision_latest | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | old_alias_reappearance | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | revision_semantic | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | unseen_1000 | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | outside_change_1000_100 | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | retention_change | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | es_change | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | ls_change | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | state_budget_ratio | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | peak_budget_ratio | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | wall_budget_ratio | None | None | unavailable |
| 162686f6303fe986619d236d | revision_latest | None | None | unavailable |
| 162686f6303fe986619d236d | old_alias_reappearance | None | None | unavailable |
| 162686f6303fe986619d236d | revision_semantic | None | None | unavailable |
| 162686f6303fe986619d236d | unseen_1000 | None | None | unavailable |
| 162686f6303fe986619d236d | outside_change_1000_100 | None | None | unavailable |
| 162686f6303fe986619d236d | retention_change | None | None | unavailable |
| 162686f6303fe986619d236d | es_change | None | None | unavailable |
| 162686f6303fe986619d236d | ls_change | None | None | unavailable |
| 162686f6303fe986619d236d | state_budget_ratio | None | None | unavailable |
| 162686f6303fe986619d236d | peak_budget_ratio | None | None | unavailable |
| 162686f6303fe986619d236d | wall_budget_ratio | None | None | unavailable |
| 029ecd260f3e085063714d3f | revision_latest | None | None | unavailable |
| 029ecd260f3e085063714d3f | old_alias_reappearance | None | None | unavailable |
| 029ecd260f3e085063714d3f | revision_semantic | None | None | unavailable |
| 029ecd260f3e085063714d3f | unseen_1000 | None | None | unavailable |
| 029ecd260f3e085063714d3f | outside_change_1000_100 | None | None | unavailable |
| 029ecd260f3e085063714d3f | retention_change | None | None | unavailable |
| 029ecd260f3e085063714d3f | es_change | None | None | unavailable |
| 029ecd260f3e085063714d3f | ls_change | None | None | unavailable |
| 029ecd260f3e085063714d3f | state_budget_ratio | None | None | unavailable |
| 029ecd260f3e085063714d3f | peak_budget_ratio | None | None | unavailable |
| 029ecd260f3e085063714d3f | wall_budget_ratio | None | None | unavailable |
| 7197775fb7f97a465fd3310e | revision_latest | None | None | unavailable |
| 7197775fb7f97a465fd3310e | old_alias_reappearance | None | None | unavailable |
| 7197775fb7f97a465fd3310e | revision_semantic | None | None | unavailable |
| 7197775fb7f97a465fd3310e | unseen_1000 | None | None | unavailable |
| 7197775fb7f97a465fd3310e | outside_change_1000_100 | None | None | unavailable |
| 7197775fb7f97a465fd3310e | retention_change | None | None | unavailable |
| 7197775fb7f97a465fd3310e | es_change | None | None | unavailable |
| 7197775fb7f97a465fd3310e | ls_change | None | None | unavailable |
| 7197775fb7f97a465fd3310e | state_budget_ratio | None | None | unavailable |
| 7197775fb7f97a465fd3310e | peak_budget_ratio | None | None | unavailable |
| 7197775fb7f97a465fd3310e | wall_budget_ratio | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | revision_latest | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | old_alias_reappearance | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | revision_semantic | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | unseen_1000 | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | outside_change_1000_100 | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | retention_change | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | es_change | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | ls_change | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | state_budget_ratio | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | peak_budget_ratio | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | wall_budget_ratio | None | None | unavailable |
| fcd702d12d5d6bfae824379b | revision_latest | None | None | unavailable |
| fcd702d12d5d6bfae824379b | old_alias_reappearance | None | None | unavailable |
| fcd702d12d5d6bfae824379b | revision_semantic | None | None | unavailable |
| fcd702d12d5d6bfae824379b | unseen_1000 | None | None | unavailable |
| fcd702d12d5d6bfae824379b | outside_change_1000_100 | None | None | unavailable |
| fcd702d12d5d6bfae824379b | retention_change | None | None | unavailable |
| fcd702d12d5d6bfae824379b | es_change | None | None | unavailable |
| fcd702d12d5d6bfae824379b | ls_change | None | None | unavailable |
| fcd702d12d5d6bfae824379b | state_budget_ratio | None | None | unavailable |
| fcd702d12d5d6bfae824379b | peak_budget_ratio | None | None | unavailable |
| fcd702d12d5d6bfae824379b | wall_budget_ratio | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | revision_latest | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | old_alias_reappearance | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | revision_semantic | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | unseen_1000 | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | outside_change_1000_100 | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | retention_change | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | es_change | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | ls_change | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | state_budget_ratio | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | peak_budget_ratio | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | wall_budget_ratio | None | None | unavailable |
| dfc9c9b480e482911c457e07 | revision_latest | None | None | unavailable |
| dfc9c9b480e482911c457e07 | old_alias_reappearance | None | None | unavailable |
| dfc9c9b480e482911c457e07 | revision_semantic | None | None | unavailable |
| dfc9c9b480e482911c457e07 | unseen_1000 | None | None | unavailable |
| dfc9c9b480e482911c457e07 | outside_change_1000_100 | None | None | unavailable |
| dfc9c9b480e482911c457e07 | retention_change | None | None | unavailable |
| dfc9c9b480e482911c457e07 | es_change | None | None | unavailable |
| dfc9c9b480e482911c457e07 | ls_change | None | None | unavailable |
| dfc9c9b480e482911c457e07 | state_budget_ratio | None | None | unavailable |
| dfc9c9b480e482911c457e07 | peak_budget_ratio | None | None | unavailable |
| dfc9c9b480e482911c457e07 | wall_budget_ratio | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | revision_latest | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | old_alias_reappearance | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | revision_semantic | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | unseen_1000 | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | outside_change_1000_100 | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | retention_change | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | es_change | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | ls_change | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | state_budget_ratio | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | peak_budget_ratio | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | wall_budget_ratio | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | revision_latest | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | old_alias_reappearance | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | revision_semantic | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | unseen_1000 | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | outside_change_1000_100 | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | retention_change | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | es_change | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | ls_change | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | state_budget_ratio | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | peak_budget_ratio | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | wall_budget_ratio | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | revision_latest | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | old_alias_reappearance | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | revision_semantic | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | unseen_1000 | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | outside_change_1000_100 | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | retention_change | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | es_change | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | ls_change | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | state_budget_ratio | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | peak_budget_ratio | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | wall_budget_ratio | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | revision_latest | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | old_alias_reappearance | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | revision_semantic | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | unseen_1000 | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | outside_change_1000_100 | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | retention_change | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | es_change | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | ls_change | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | state_budget_ratio | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | peak_budget_ratio | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | wall_budget_ratio | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | revision_latest | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | old_alias_reappearance | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | revision_semantic | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | unseen_1000 | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | outside_change_1000_100 | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | retention_change | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | es_change | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | ls_change | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | state_budget_ratio | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | peak_budget_ratio | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | wall_budget_ratio | None | None | unavailable |
| fa5b51891eb78dc707e6471f | revision_latest | None | None | unavailable |
| fa5b51891eb78dc707e6471f | old_alias_reappearance | None | None | unavailable |
| fa5b51891eb78dc707e6471f | revision_semantic | None | None | unavailable |
| fa5b51891eb78dc707e6471f | unseen_1000 | None | None | unavailable |
| fa5b51891eb78dc707e6471f | outside_change_1000_100 | None | None | unavailable |
| fa5b51891eb78dc707e6471f | retention_change | None | None | unavailable |
| fa5b51891eb78dc707e6471f | es_change | None | None | unavailable |
| fa5b51891eb78dc707e6471f | ls_change | None | None | unavailable |
| fa5b51891eb78dc707e6471f | state_budget_ratio | None | None | unavailable |
| fa5b51891eb78dc707e6471f | peak_budget_ratio | None | None | unavailable |
| fa5b51891eb78dc707e6471f | wall_budget_ratio | None | None | unavailable |
| 861810fbdd6ebe7502383382 | revision_latest | None | None | unavailable |
| 861810fbdd6ebe7502383382 | old_alias_reappearance | None | None | unavailable |
| 861810fbdd6ebe7502383382 | revision_semantic | None | None | unavailable |
| 861810fbdd6ebe7502383382 | unseen_1000 | None | None | unavailable |
| 861810fbdd6ebe7502383382 | outside_change_1000_100 | None | None | unavailable |
| 861810fbdd6ebe7502383382 | retention_change | None | None | unavailable |
| 861810fbdd6ebe7502383382 | es_change | None | None | unavailable |
| 861810fbdd6ebe7502383382 | ls_change | None | None | unavailable |
| 861810fbdd6ebe7502383382 | state_budget_ratio | None | None | unavailable |
| 861810fbdd6ebe7502383382 | peak_budget_ratio | None | None | unavailable |
| 861810fbdd6ebe7502383382 | wall_budget_ratio | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | revision_latest | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | old_alias_reappearance | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | revision_semantic | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | unseen_1000 | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | outside_change_1000_100 | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | retention_change | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | es_change | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | ls_change | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | state_budget_ratio | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | peak_budget_ratio | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | wall_budget_ratio | None | None | unavailable |
| f939f211b98675ac7c2d951f | revision_latest | None | None | unavailable |
| f939f211b98675ac7c2d951f | old_alias_reappearance | None | None | unavailable |
| f939f211b98675ac7c2d951f | revision_semantic | None | None | unavailable |
| f939f211b98675ac7c2d951f | unseen_1000 | None | None | unavailable |
| f939f211b98675ac7c2d951f | outside_change_1000_100 | None | None | unavailable |
| f939f211b98675ac7c2d951f | retention_change | None | None | unavailable |
| f939f211b98675ac7c2d951f | es_change | None | None | unavailable |
| f939f211b98675ac7c2d951f | ls_change | None | None | unavailable |
| f939f211b98675ac7c2d951f | state_budget_ratio | None | None | unavailable |
| f939f211b98675ac7c2d951f | peak_budget_ratio | None | None | unavailable |
| f939f211b98675ac7c2d951f | wall_budget_ratio | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | revision_latest | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | old_alias_reappearance | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | revision_semantic | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | unseen_1000 | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | outside_change_1000_100 | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | retention_change | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | es_change | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | ls_change | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | state_budget_ratio | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | peak_budget_ratio | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | wall_budget_ratio | None | None | unavailable |
| b14576e3d752f467db2abf18 | revision_latest | None | None | unavailable |
| b14576e3d752f467db2abf18 | old_alias_reappearance | None | None | unavailable |
| b14576e3d752f467db2abf18 | revision_semantic | None | None | unavailable |
| b14576e3d752f467db2abf18 | unseen_1000 | None | None | unavailable |
| b14576e3d752f467db2abf18 | outside_change_1000_100 | None | None | unavailable |
| b14576e3d752f467db2abf18 | retention_change | None | None | unavailable |
| b14576e3d752f467db2abf18 | es_change | None | None | unavailable |
| b14576e3d752f467db2abf18 | ls_change | None | None | unavailable |
| b14576e3d752f467db2abf18 | state_budget_ratio | None | None | unavailable |
| b14576e3d752f467db2abf18 | peak_budget_ratio | None | None | unavailable |
| b14576e3d752f467db2abf18 | wall_budget_ratio | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | revision_latest | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | old_alias_reappearance | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | revision_semantic | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | unseen_1000 | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | outside_change_1000_100 | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | retention_change | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | es_change | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | ls_change | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | state_budget_ratio | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | peak_budget_ratio | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | wall_budget_ratio | None | None | unavailable |
| 9e98169ae668b50d60694317 | revision_latest | None | None | unavailable |
| 9e98169ae668b50d60694317 | old_alias_reappearance | None | None | unavailable |
| 9e98169ae668b50d60694317 | revision_semantic | None | None | unavailable |
| 9e98169ae668b50d60694317 | unseen_1000 | None | None | unavailable |
| 9e98169ae668b50d60694317 | outside_change_1000_100 | None | None | unavailable |
| 9e98169ae668b50d60694317 | retention_change | None | None | unavailable |
| 9e98169ae668b50d60694317 | es_change | None | None | unavailable |
| 9e98169ae668b50d60694317 | ls_change | None | None | unavailable |
| 9e98169ae668b50d60694317 | state_budget_ratio | None | None | unavailable |
| 9e98169ae668b50d60694317 | peak_budget_ratio | None | None | unavailable |
| 9e98169ae668b50d60694317 | wall_budget_ratio | None | None | unavailable |
| ff570734d7837a1ba9e77528 | revision_latest | None | None | unavailable |
| ff570734d7837a1ba9e77528 | old_alias_reappearance | None | None | unavailable |
| ff570734d7837a1ba9e77528 | revision_semantic | None | None | unavailable |
| ff570734d7837a1ba9e77528 | unseen_1000 | None | None | unavailable |
| ff570734d7837a1ba9e77528 | outside_change_1000_100 | None | None | unavailable |
| ff570734d7837a1ba9e77528 | retention_change | None | None | unavailable |
| ff570734d7837a1ba9e77528 | es_change | None | None | unavailable |
| ff570734d7837a1ba9e77528 | ls_change | None | None | unavailable |
| ff570734d7837a1ba9e77528 | state_budget_ratio | None | None | unavailable |
| ff570734d7837a1ba9e77528 | peak_budget_ratio | None | None | unavailable |
| ff570734d7837a1ba9e77528 | wall_budget_ratio | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | revision_latest | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | old_alias_reappearance | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | revision_semantic | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | unseen_1000 | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | outside_change_1000_100 | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | retention_change | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | es_change | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | ls_change | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | state_budget_ratio | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | peak_budget_ratio | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | wall_budget_ratio | None | None | unavailable |
| c0e77c94b06dd3464838be93 | revision_latest | None | None | unavailable |
| c0e77c94b06dd3464838be93 | old_alias_reappearance | None | None | unavailable |
| c0e77c94b06dd3464838be93 | revision_semantic | None | None | unavailable |
| c0e77c94b06dd3464838be93 | unseen_1000 | None | None | unavailable |
| c0e77c94b06dd3464838be93 | outside_change_1000_100 | None | None | unavailable |
| c0e77c94b06dd3464838be93 | retention_change | None | None | unavailable |
| c0e77c94b06dd3464838be93 | es_change | None | None | unavailable |
| c0e77c94b06dd3464838be93 | ls_change | None | None | unavailable |
| c0e77c94b06dd3464838be93 | state_budget_ratio | None | None | unavailable |
| c0e77c94b06dd3464838be93 | peak_budget_ratio | None | None | unavailable |
| c0e77c94b06dd3464838be93 | wall_budget_ratio | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | revision_latest | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | old_alias_reappearance | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | revision_semantic | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | unseen_1000 | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | outside_change_1000_100 | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | retention_change | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | es_change | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | ls_change | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | state_budget_ratio | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | peak_budget_ratio | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | wall_budget_ratio | None | None | unavailable |
| dc17fc3637068157dba0207d | revision_latest | None | None | unavailable |
| dc17fc3637068157dba0207d | old_alias_reappearance | None | None | unavailable |
| dc17fc3637068157dba0207d | revision_semantic | None | None | unavailable |
| dc17fc3637068157dba0207d | unseen_1000 | None | None | unavailable |
| dc17fc3637068157dba0207d | outside_change_1000_100 | None | None | unavailable |
| dc17fc3637068157dba0207d | retention_change | None | None | unavailable |
| dc17fc3637068157dba0207d | es_change | None | None | unavailable |
| dc17fc3637068157dba0207d | ls_change | None | None | unavailable |
| dc17fc3637068157dba0207d | state_budget_ratio | None | None | unavailable |
| dc17fc3637068157dba0207d | peak_budget_ratio | None | None | unavailable |
| dc17fc3637068157dba0207d | wall_budget_ratio | None | None | unavailable |
| 727b32ab9723cb9feba71636 | revision_latest | None | None | unavailable |
| 727b32ab9723cb9feba71636 | old_alias_reappearance | None | None | unavailable |
| 727b32ab9723cb9feba71636 | revision_semantic | None | None | unavailable |
| 727b32ab9723cb9feba71636 | unseen_1000 | None | None | unavailable |
| 727b32ab9723cb9feba71636 | outside_change_1000_100 | None | None | unavailable |
| 727b32ab9723cb9feba71636 | retention_change | None | None | unavailable |
| 727b32ab9723cb9feba71636 | es_change | None | None | unavailable |
| 727b32ab9723cb9feba71636 | ls_change | None | None | unavailable |
| 727b32ab9723cb9feba71636 | state_budget_ratio | None | None | unavailable |
| 727b32ab9723cb9feba71636 | peak_budget_ratio | None | None | unavailable |
| 727b32ab9723cb9feba71636 | wall_budget_ratio | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | revision_latest | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | old_alias_reappearance | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | revision_semantic | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | unseen_1000 | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | outside_change_1000_100 | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | retention_change | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | es_change | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | ls_change | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | state_budget_ratio | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | peak_budget_ratio | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | wall_budget_ratio | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | revision_latest | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | old_alias_reappearance | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | revision_semantic | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | unseen_1000 | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | outside_change_1000_100 | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | retention_change | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | es_change | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | ls_change | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | state_budget_ratio | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | peak_budget_ratio | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | wall_budget_ratio | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | revision_latest | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | old_alias_reappearance | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | revision_semantic | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | unseen_1000 | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | outside_change_1000_100 | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | retention_change | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | es_change | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | ls_change | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | state_budget_ratio | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | peak_budget_ratio | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | wall_budget_ratio | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | revision_latest | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | old_alias_reappearance | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | revision_semantic | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | unseen_1000 | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | outside_change_1000_100 | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | retention_change | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | es_change | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | ls_change | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | state_budget_ratio | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | peak_budget_ratio | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | wall_budget_ratio | None | None | unavailable |
| 89b258fddde381d9a09429d9 | revision_latest | None | None | unavailable |
| 89b258fddde381d9a09429d9 | old_alias_reappearance | None | None | unavailable |
| 89b258fddde381d9a09429d9 | revision_semantic | None | None | unavailable |
| 89b258fddde381d9a09429d9 | unseen_1000 | None | None | unavailable |
| 89b258fddde381d9a09429d9 | outside_change_1000_100 | None | None | unavailable |
| 89b258fddde381d9a09429d9 | retention_change | None | None | unavailable |
| 89b258fddde381d9a09429d9 | es_change | None | None | unavailable |
| 89b258fddde381d9a09429d9 | ls_change | None | None | unavailable |
| 89b258fddde381d9a09429d9 | state_budget_ratio | None | None | unavailable |
| 89b258fddde381d9a09429d9 | peak_budget_ratio | None | None | unavailable |
| 89b258fddde381d9a09429d9 | wall_budget_ratio | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | revision_latest | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | old_alias_reappearance | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | revision_semantic | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | unseen_1000 | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | outside_change_1000_100 | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | retention_change | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | es_change | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | ls_change | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | state_budget_ratio | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | peak_budget_ratio | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | wall_budget_ratio | None | None | unavailable |
| 6e95ec72097ffded952889d6 | revision_latest | None | None | unavailable |
| 6e95ec72097ffded952889d6 | old_alias_reappearance | None | None | unavailable |
| 6e95ec72097ffded952889d6 | revision_semantic | None | None | unavailable |
| 6e95ec72097ffded952889d6 | unseen_1000 | None | None | unavailable |
| 6e95ec72097ffded952889d6 | outside_change_1000_100 | None | None | unavailable |
| 6e95ec72097ffded952889d6 | retention_change | None | None | unavailable |
| 6e95ec72097ffded952889d6 | es_change | None | None | unavailable |
| 6e95ec72097ffded952889d6 | ls_change | None | None | unavailable |
| 6e95ec72097ffded952889d6 | state_budget_ratio | None | None | unavailable |
| 6e95ec72097ffded952889d6 | peak_budget_ratio | None | None | unavailable |
| 6e95ec72097ffded952889d6 | wall_budget_ratio | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | revision_latest | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | old_alias_reappearance | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | revision_semantic | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | unseen_1000 | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | outside_change_1000_100 | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | retention_change | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | es_change | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | ls_change | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | state_budget_ratio | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | peak_budget_ratio | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | wall_budget_ratio | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | revision_latest | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | old_alias_reappearance | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | revision_semantic | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | unseen_1000 | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | outside_change_1000_100 | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | retention_change | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | es_change | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | ls_change | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | state_budget_ratio | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | peak_budget_ratio | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | wall_budget_ratio | None | None | unavailable |
| 519b30353f979e8028ed03e1 | revision_latest | None | None | unavailable |
| 519b30353f979e8028ed03e1 | old_alias_reappearance | None | None | unavailable |
| 519b30353f979e8028ed03e1 | revision_semantic | None | None | unavailable |
| 519b30353f979e8028ed03e1 | unseen_1000 | None | None | unavailable |
| 519b30353f979e8028ed03e1 | outside_change_1000_100 | None | None | unavailable |
| 519b30353f979e8028ed03e1 | retention_change | None | None | unavailable |
| 519b30353f979e8028ed03e1 | es_change | None | None | unavailable |
| 519b30353f979e8028ed03e1 | ls_change | None | None | unavailable |
| 519b30353f979e8028ed03e1 | state_budget_ratio | None | None | unavailable |
| 519b30353f979e8028ed03e1 | peak_budget_ratio | None | None | unavailable |
| 519b30353f979e8028ed03e1 | wall_budget_ratio | None | None | unavailable |
| 89182e81a187807d2772cade | revision_latest | None | None | unavailable |
| 89182e81a187807d2772cade | old_alias_reappearance | None | None | unavailable |
| 89182e81a187807d2772cade | revision_semantic | None | None | unavailable |
| 89182e81a187807d2772cade | unseen_1000 | None | None | unavailable |
| 89182e81a187807d2772cade | outside_change_1000_100 | None | None | unavailable |
| 89182e81a187807d2772cade | retention_change | None | None | unavailable |
| 89182e81a187807d2772cade | es_change | None | None | unavailable |
| 89182e81a187807d2772cade | ls_change | None | None | unavailable |
| 89182e81a187807d2772cade | state_budget_ratio | None | None | unavailable |
| 89182e81a187807d2772cade | peak_budget_ratio | None | None | unavailable |
| 89182e81a187807d2772cade | wall_budget_ratio | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | revision_latest | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | old_alias_reappearance | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | revision_semantic | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | unseen_1000 | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | outside_change_1000_100 | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | retention_change | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | es_change | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | ls_change | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | state_budget_ratio | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | peak_budget_ratio | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | wall_budget_ratio | None | None | unavailable |
| 046aa51d028b84dde8981351 | revision_latest | None | None | unavailable |
| 046aa51d028b84dde8981351 | old_alias_reappearance | None | None | unavailable |
| 046aa51d028b84dde8981351 | revision_semantic | None | None | unavailable |
| 046aa51d028b84dde8981351 | unseen_1000 | None | None | unavailable |
| 046aa51d028b84dde8981351 | outside_change_1000_100 | None | None | unavailable |
| 046aa51d028b84dde8981351 | retention_change | None | None | unavailable |
| 046aa51d028b84dde8981351 | es_change | None | None | unavailable |
| 046aa51d028b84dde8981351 | ls_change | None | None | unavailable |
| 046aa51d028b84dde8981351 | state_budget_ratio | None | None | unavailable |
| 046aa51d028b84dde8981351 | peak_budget_ratio | None | None | unavailable |
| 046aa51d028b84dde8981351 | wall_budget_ratio | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | revision_latest | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | old_alias_reappearance | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | revision_semantic | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | unseen_1000 | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | outside_change_1000_100 | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | retention_change | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | es_change | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | ls_change | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | state_budget_ratio | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | peak_budget_ratio | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | wall_budget_ratio | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | revision_latest | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | old_alias_reappearance | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | revision_semantic | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | unseen_1000 | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | outside_change_1000_100 | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | retention_change | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | es_change | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | ls_change | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | state_budget_ratio | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | peak_budget_ratio | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | wall_budget_ratio | None | None | unavailable |
| c1c03ed850a40df57da8628a | revision_latest | None | None | unavailable |
| c1c03ed850a40df57da8628a | old_alias_reappearance | None | None | unavailable |
| c1c03ed850a40df57da8628a | revision_semantic | None | None | unavailable |
| c1c03ed850a40df57da8628a | unseen_1000 | None | None | unavailable |
| c1c03ed850a40df57da8628a | outside_change_1000_100 | None | None | unavailable |
| c1c03ed850a40df57da8628a | retention_change | None | None | unavailable |
| c1c03ed850a40df57da8628a | es_change | None | None | unavailable |
| c1c03ed850a40df57da8628a | ls_change | None | None | unavailable |
| c1c03ed850a40df57da8628a | state_budget_ratio | None | None | unavailable |
| c1c03ed850a40df57da8628a | peak_budget_ratio | None | None | unavailable |
| c1c03ed850a40df57da8628a | wall_budget_ratio | None | None | unavailable |
| d1690029ea53ae03b3705536 | revision_latest | None | None | unavailable |
| d1690029ea53ae03b3705536 | old_alias_reappearance | None | None | unavailable |
| d1690029ea53ae03b3705536 | revision_semantic | None | None | unavailable |
| d1690029ea53ae03b3705536 | unseen_1000 | None | None | unavailable |
| d1690029ea53ae03b3705536 | outside_change_1000_100 | None | None | unavailable |
| d1690029ea53ae03b3705536 | retention_change | None | None | unavailable |
| d1690029ea53ae03b3705536 | es_change | None | None | unavailable |
| d1690029ea53ae03b3705536 | ls_change | None | None | unavailable |
| d1690029ea53ae03b3705536 | state_budget_ratio | None | None | unavailable |
| d1690029ea53ae03b3705536 | peak_budget_ratio | None | None | unavailable |
| d1690029ea53ae03b3705536 | wall_budget_ratio | None | None | unavailable |
| a921f9ab5443f978e56d2390 | revision_latest | None | None | unavailable |
| a921f9ab5443f978e56d2390 | old_alias_reappearance | None | None | unavailable |
| a921f9ab5443f978e56d2390 | revision_semantic | None | None | unavailable |
| a921f9ab5443f978e56d2390 | unseen_1000 | None | None | unavailable |
| a921f9ab5443f978e56d2390 | outside_change_1000_100 | None | None | unavailable |
| a921f9ab5443f978e56d2390 | retention_change | None | None | unavailable |
| a921f9ab5443f978e56d2390 | es_change | None | None | unavailable |
| a921f9ab5443f978e56d2390 | ls_change | None | None | unavailable |
| a921f9ab5443f978e56d2390 | state_budget_ratio | None | None | unavailable |
| a921f9ab5443f978e56d2390 | peak_budget_ratio | None | None | unavailable |
| a921f9ab5443f978e56d2390 | wall_budget_ratio | None | None | unavailable |
| a86da75220343c5560c45373 | revision_latest | None | None | unavailable |
| a86da75220343c5560c45373 | old_alias_reappearance | None | None | unavailable |
| a86da75220343c5560c45373 | revision_semantic | None | None | unavailable |
| a86da75220343c5560c45373 | unseen_1000 | None | None | unavailable |
| a86da75220343c5560c45373 | outside_change_1000_100 | None | None | unavailable |
| a86da75220343c5560c45373 | retention_change | None | None | unavailable |
| a86da75220343c5560c45373 | es_change | None | None | unavailable |
| a86da75220343c5560c45373 | ls_change | None | None | unavailable |
| a86da75220343c5560c45373 | state_budget_ratio | None | None | unavailable |
| a86da75220343c5560c45373 | peak_budget_ratio | None | None | unavailable |
| a86da75220343c5560c45373 | wall_budget_ratio | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | revision_latest | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | old_alias_reappearance | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | revision_semantic | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | unseen_1000 | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | outside_change_1000_100 | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | retention_change | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | es_change | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | ls_change | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | state_budget_ratio | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | peak_budget_ratio | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | wall_budget_ratio | None | None | unavailable |
| 735081421354eaafb893322d | revision_latest | None | None | unavailable |
| 735081421354eaafb893322d | old_alias_reappearance | None | None | unavailable |
| 735081421354eaafb893322d | revision_semantic | None | None | unavailable |
| 735081421354eaafb893322d | unseen_1000 | None | None | unavailable |
| 735081421354eaafb893322d | outside_change_1000_100 | None | None | unavailable |
| 735081421354eaafb893322d | retention_change | None | None | unavailable |
| 735081421354eaafb893322d | es_change | None | None | unavailable |
| 735081421354eaafb893322d | ls_change | None | None | unavailable |
| 735081421354eaafb893322d | state_budget_ratio | None | None | unavailable |
| 735081421354eaafb893322d | peak_budget_ratio | None | None | unavailable |
| 735081421354eaafb893322d | wall_budget_ratio | None | None | unavailable |
| 824f602358ace0fc5cb69271 | revision_latest | None | None | unavailable |
| 824f602358ace0fc5cb69271 | old_alias_reappearance | None | None | unavailable |
| 824f602358ace0fc5cb69271 | revision_semantic | None | None | unavailable |
| 824f602358ace0fc5cb69271 | unseen_1000 | None | None | unavailable |
| 824f602358ace0fc5cb69271 | outside_change_1000_100 | None | None | unavailable |
| 824f602358ace0fc5cb69271 | retention_change | None | None | unavailable |
| 824f602358ace0fc5cb69271 | es_change | None | None | unavailable |
| 824f602358ace0fc5cb69271 | ls_change | None | None | unavailable |
| 824f602358ace0fc5cb69271 | state_budget_ratio | None | None | unavailable |
| 824f602358ace0fc5cb69271 | peak_budget_ratio | None | None | unavailable |
| 824f602358ace0fc5cb69271 | wall_budget_ratio | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | revision_latest | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | old_alias_reappearance | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | revision_semantic | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | unseen_1000 | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | outside_change_1000_100 | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | retention_change | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | es_change | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | ls_change | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | state_budget_ratio | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | peak_budget_ratio | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | wall_budget_ratio | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | revision_latest | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | old_alias_reappearance | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | revision_semantic | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | unseen_1000 | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | outside_change_1000_100 | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | retention_change | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | es_change | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | ls_change | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | state_budget_ratio | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | peak_budget_ratio | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | wall_budget_ratio | None | None | unavailable |
| 58879f9745ed479686bd0481 | revision_latest | None | None | unavailable |
| 58879f9745ed479686bd0481 | old_alias_reappearance | None | None | unavailable |
| 58879f9745ed479686bd0481 | revision_semantic | None | None | unavailable |
| 58879f9745ed479686bd0481 | unseen_1000 | None | None | unavailable |
| 58879f9745ed479686bd0481 | outside_change_1000_100 | None | None | unavailable |
| 58879f9745ed479686bd0481 | retention_change | None | None | unavailable |
| 58879f9745ed479686bd0481 | es_change | None | None | unavailable |
| 58879f9745ed479686bd0481 | ls_change | None | None | unavailable |
| 58879f9745ed479686bd0481 | state_budget_ratio | None | None | unavailable |
| 58879f9745ed479686bd0481 | peak_budget_ratio | None | None | unavailable |
| 58879f9745ed479686bd0481 | wall_budget_ratio | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | revision_latest | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | old_alias_reappearance | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | revision_semantic | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | unseen_1000 | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | outside_change_1000_100 | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | retention_change | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | es_change | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | ls_change | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | state_budget_ratio | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | peak_budget_ratio | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | wall_budget_ratio | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | revision_latest | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | old_alias_reappearance | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | revision_semantic | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | unseen_1000 | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | outside_change_1000_100 | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | retention_change | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | es_change | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | ls_change | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | state_budget_ratio | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | peak_budget_ratio | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | wall_budget_ratio | None | None | unavailable |
| 4597af8473d8e404f1490c57 | revision_latest | None | None | unavailable |
| 4597af8473d8e404f1490c57 | old_alias_reappearance | None | None | unavailable |
| 4597af8473d8e404f1490c57 | revision_semantic | None | None | unavailable |
| 4597af8473d8e404f1490c57 | unseen_1000 | None | None | unavailable |
| 4597af8473d8e404f1490c57 | outside_change_1000_100 | None | None | unavailable |
| 4597af8473d8e404f1490c57 | retention_change | None | None | unavailable |
| 4597af8473d8e404f1490c57 | es_change | None | None | unavailable |
| 4597af8473d8e404f1490c57 | ls_change | None | None | unavailable |
| 4597af8473d8e404f1490c57 | state_budget_ratio | None | None | unavailable |
| 4597af8473d8e404f1490c57 | peak_budget_ratio | None | None | unavailable |
| 4597af8473d8e404f1490c57 | wall_budget_ratio | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | revision_latest | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | old_alias_reappearance | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | revision_semantic | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | unseen_1000 | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | outside_change_1000_100 | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | retention_change | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | es_change | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | ls_change | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | state_budget_ratio | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | peak_budget_ratio | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | wall_budget_ratio | None | None | unavailable |
| 0998eeed741b887bdb8664af | revision_latest | None | None | unavailable |
| 0998eeed741b887bdb8664af | old_alias_reappearance | None | None | unavailable |
| 0998eeed741b887bdb8664af | revision_semantic | None | None | unavailable |
| 0998eeed741b887bdb8664af | unseen_1000 | None | None | unavailable |
| 0998eeed741b887bdb8664af | outside_change_1000_100 | None | None | unavailable |
| 0998eeed741b887bdb8664af | retention_change | None | None | unavailable |
| 0998eeed741b887bdb8664af | es_change | None | None | unavailable |
| 0998eeed741b887bdb8664af | ls_change | None | None | unavailable |
| 0998eeed741b887bdb8664af | state_budget_ratio | None | None | unavailable |
| 0998eeed741b887bdb8664af | peak_budget_ratio | None | None | unavailable |
| 0998eeed741b887bdb8664af | wall_budget_ratio | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | revision_latest | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | old_alias_reappearance | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | revision_semantic | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | unseen_1000 | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | outside_change_1000_100 | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | retention_change | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | es_change | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | ls_change | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | state_budget_ratio | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | peak_budget_ratio | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | wall_budget_ratio | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | revision_latest | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | old_alias_reappearance | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | revision_semantic | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | unseen_1000 | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | outside_change_1000_100 | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | retention_change | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | es_change | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | ls_change | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | state_budget_ratio | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | peak_budget_ratio | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | wall_budget_ratio | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | revision_latest | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | old_alias_reappearance | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | revision_semantic | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | unseen_1000 | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | outside_change_1000_100 | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | retention_change | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | es_change | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | ls_change | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | state_budget_ratio | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | peak_budget_ratio | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | wall_budget_ratio | None | None | unavailable |
| b8924c056fee6d000f5492d1 | revision_latest | None | None | unavailable |
| b8924c056fee6d000f5492d1 | old_alias_reappearance | None | None | unavailable |
| b8924c056fee6d000f5492d1 | revision_semantic | None | None | unavailable |
| b8924c056fee6d000f5492d1 | unseen_1000 | None | None | unavailable |
| b8924c056fee6d000f5492d1 | outside_change_1000_100 | None | None | unavailable |
| b8924c056fee6d000f5492d1 | retention_change | None | None | unavailable |
| b8924c056fee6d000f5492d1 | es_change | None | None | unavailable |
| b8924c056fee6d000f5492d1 | ls_change | None | None | unavailable |
| b8924c056fee6d000f5492d1 | state_budget_ratio | None | None | unavailable |
| b8924c056fee6d000f5492d1 | peak_budget_ratio | None | None | unavailable |
| b8924c056fee6d000f5492d1 | wall_budget_ratio | None | None | unavailable |
| 4944219da107f9ed1daccef5 | revision_latest | None | None | unavailable |
| 4944219da107f9ed1daccef5 | old_alias_reappearance | None | None | unavailable |
| 4944219da107f9ed1daccef5 | revision_semantic | None | None | unavailable |
| 4944219da107f9ed1daccef5 | unseen_1000 | None | None | unavailable |
| 4944219da107f9ed1daccef5 | outside_change_1000_100 | None | None | unavailable |
| 4944219da107f9ed1daccef5 | retention_change | None | None | unavailable |
| 4944219da107f9ed1daccef5 | es_change | None | None | unavailable |
| 4944219da107f9ed1daccef5 | ls_change | None | None | unavailable |
| 4944219da107f9ed1daccef5 | state_budget_ratio | None | None | unavailable |
| 4944219da107f9ed1daccef5 | peak_budget_ratio | None | None | unavailable |
| 4944219da107f9ed1daccef5 | wall_budget_ratio | None | None | unavailable |
| ac46789a7ebda9982aebd343 | revision_latest | None | None | unavailable |
| ac46789a7ebda9982aebd343 | old_alias_reappearance | None | None | unavailable |
| ac46789a7ebda9982aebd343 | revision_semantic | None | None | unavailable |
| ac46789a7ebda9982aebd343 | unseen_1000 | None | None | unavailable |
| ac46789a7ebda9982aebd343 | outside_change_1000_100 | None | None | unavailable |
| ac46789a7ebda9982aebd343 | retention_change | None | None | unavailable |
| ac46789a7ebda9982aebd343 | es_change | None | None | unavailable |
| ac46789a7ebda9982aebd343 | ls_change | None | None | unavailable |
| ac46789a7ebda9982aebd343 | state_budget_ratio | None | None | unavailable |
| ac46789a7ebda9982aebd343 | peak_budget_ratio | None | None | unavailable |
| ac46789a7ebda9982aebd343 | wall_budget_ratio | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | revision_latest | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | old_alias_reappearance | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | revision_semantic | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | unseen_1000 | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | outside_change_1000_100 | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | retention_change | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | es_change | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | ls_change | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | state_budget_ratio | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | peak_budget_ratio | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | wall_budget_ratio | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | revision_latest | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | old_alias_reappearance | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | revision_semantic | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | unseen_1000 | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | outside_change_1000_100 | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | retention_change | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | es_change | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | ls_change | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | state_budget_ratio | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | peak_budget_ratio | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | wall_budget_ratio | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | revision_latest | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | old_alias_reappearance | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | revision_semantic | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | unseen_1000 | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | outside_change_1000_100 | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | retention_change | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | es_change | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | ls_change | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | state_budget_ratio | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | peak_budget_ratio | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | wall_budget_ratio | None | None | unavailable |
| b8f1ca491f4e29db862af920 | revision_latest | None | None | unavailable |
| b8f1ca491f4e29db862af920 | old_alias_reappearance | None | None | unavailable |
| b8f1ca491f4e29db862af920 | revision_semantic | None | None | unavailable |
| b8f1ca491f4e29db862af920 | unseen_1000 | None | None | unavailable |
| b8f1ca491f4e29db862af920 | outside_change_1000_100 | None | None | unavailable |
| b8f1ca491f4e29db862af920 | retention_change | None | None | unavailable |
| b8f1ca491f4e29db862af920 | es_change | None | None | unavailable |
| b8f1ca491f4e29db862af920 | ls_change | None | None | unavailable |
| b8f1ca491f4e29db862af920 | state_budget_ratio | None | None | unavailable |
| b8f1ca491f4e29db862af920 | peak_budget_ratio | None | None | unavailable |
| b8f1ca491f4e29db862af920 | wall_budget_ratio | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | revision_latest | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | old_alias_reappearance | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | revision_semantic | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | unseen_1000 | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | outside_change_1000_100 | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | retention_change | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | es_change | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | ls_change | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | state_budget_ratio | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | peak_budget_ratio | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | wall_budget_ratio | None | None | unavailable |
| 47ee96bcecb134f64286c958 | revision_latest | None | None | unavailable |
| 47ee96bcecb134f64286c958 | old_alias_reappearance | None | None | unavailable |
| 47ee96bcecb134f64286c958 | revision_semantic | None | None | unavailable |
| 47ee96bcecb134f64286c958 | unseen_1000 | None | None | unavailable |
| 47ee96bcecb134f64286c958 | outside_change_1000_100 | None | None | unavailable |
| 47ee96bcecb134f64286c958 | retention_change | None | None | unavailable |
| 47ee96bcecb134f64286c958 | es_change | None | None | unavailable |
| 47ee96bcecb134f64286c958 | ls_change | None | None | unavailable |
| 47ee96bcecb134f64286c958 | state_budget_ratio | None | None | unavailable |
| 47ee96bcecb134f64286c958 | peak_budget_ratio | None | None | unavailable |
| 47ee96bcecb134f64286c958 | wall_budget_ratio | None | None | unavailable |
| a18ee644e09c84652cc9582a | revision_latest | None | None | unavailable |
| a18ee644e09c84652cc9582a | old_alias_reappearance | None | None | unavailable |
| a18ee644e09c84652cc9582a | revision_semantic | None | None | unavailable |
| a18ee644e09c84652cc9582a | unseen_1000 | None | None | unavailable |
| a18ee644e09c84652cc9582a | outside_change_1000_100 | None | None | unavailable |
| a18ee644e09c84652cc9582a | retention_change | None | None | unavailable |
| a18ee644e09c84652cc9582a | es_change | None | None | unavailable |
| a18ee644e09c84652cc9582a | ls_change | None | None | unavailable |
| a18ee644e09c84652cc9582a | state_budget_ratio | None | None | unavailable |
| a18ee644e09c84652cc9582a | peak_budget_ratio | None | None | unavailable |
| a18ee644e09c84652cc9582a | wall_budget_ratio | None | None | unavailable |
| 509cd28130eb44d35b27d08a | revision_latest | None | None | unavailable |
| 509cd28130eb44d35b27d08a | old_alias_reappearance | None | None | unavailable |
| 509cd28130eb44d35b27d08a | revision_semantic | None | None | unavailable |
| 509cd28130eb44d35b27d08a | unseen_1000 | None | None | unavailable |
| 509cd28130eb44d35b27d08a | outside_change_1000_100 | None | None | unavailable |
| 509cd28130eb44d35b27d08a | retention_change | None | None | unavailable |
| 509cd28130eb44d35b27d08a | es_change | None | None | unavailable |
| 509cd28130eb44d35b27d08a | ls_change | None | None | unavailable |
| 509cd28130eb44d35b27d08a | state_budget_ratio | None | None | unavailable |
| 509cd28130eb44d35b27d08a | peak_budget_ratio | None | None | unavailable |
| 509cd28130eb44d35b27d08a | wall_budget_ratio | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | revision_latest | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | old_alias_reappearance | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | revision_semantic | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | unseen_1000 | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | outside_change_1000_100 | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | retention_change | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | es_change | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | ls_change | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | state_budget_ratio | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | peak_budget_ratio | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | wall_budget_ratio | None | None | unavailable |
| 5f818373c34233809fc57716 | revision_latest | None | None | unavailable |
| 5f818373c34233809fc57716 | old_alias_reappearance | None | None | unavailable |
| 5f818373c34233809fc57716 | revision_semantic | None | None | unavailable |
| 5f818373c34233809fc57716 | unseen_1000 | None | None | unavailable |
| 5f818373c34233809fc57716 | outside_change_1000_100 | None | None | unavailable |
| 5f818373c34233809fc57716 | retention_change | None | None | unavailable |
| 5f818373c34233809fc57716 | es_change | None | None | unavailable |
| 5f818373c34233809fc57716 | ls_change | None | None | unavailable |
| 5f818373c34233809fc57716 | state_budget_ratio | None | None | unavailable |
| 5f818373c34233809fc57716 | peak_budget_ratio | None | None | unavailable |
| 5f818373c34233809fc57716 | wall_budget_ratio | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | revision_latest | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | old_alias_reappearance | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | revision_semantic | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | unseen_1000 | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | outside_change_1000_100 | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | retention_change | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | es_change | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | ls_change | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | state_budget_ratio | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | peak_budget_ratio | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | wall_budget_ratio | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | revision_latest | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | old_alias_reappearance | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | revision_semantic | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | unseen_1000 | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | outside_change_1000_100 | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | retention_change | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | es_change | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | ls_change | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | state_budget_ratio | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | peak_budget_ratio | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | wall_budget_ratio | None | None | unavailable |
| d0a5df19a69792ac87a703dc | revision_latest | None | None | unavailable |
| d0a5df19a69792ac87a703dc | old_alias_reappearance | None | None | unavailable |
| d0a5df19a69792ac87a703dc | revision_semantic | None | None | unavailable |
| d0a5df19a69792ac87a703dc | unseen_1000 | None | None | unavailable |
| d0a5df19a69792ac87a703dc | outside_change_1000_100 | None | None | unavailable |
| d0a5df19a69792ac87a703dc | retention_change | None | None | unavailable |
| d0a5df19a69792ac87a703dc | es_change | None | None | unavailable |
| d0a5df19a69792ac87a703dc | ls_change | None | None | unavailable |
| d0a5df19a69792ac87a703dc | state_budget_ratio | None | None | unavailable |
| d0a5df19a69792ac87a703dc | peak_budget_ratio | None | None | unavailable |
| d0a5df19a69792ac87a703dc | wall_budget_ratio | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | revision_latest | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | old_alias_reappearance | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | revision_semantic | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | unseen_1000 | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | outside_change_1000_100 | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | retention_change | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | es_change | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | ls_change | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | state_budget_ratio | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | peak_budget_ratio | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | wall_budget_ratio | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | revision_latest | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | old_alias_reappearance | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | revision_semantic | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | unseen_1000 | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | outside_change_1000_100 | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | retention_change | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | es_change | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | ls_change | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | state_budget_ratio | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | peak_budget_ratio | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | wall_budget_ratio | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | revision_latest | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | old_alias_reappearance | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | revision_semantic | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | unseen_1000 | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | outside_change_1000_100 | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | retention_change | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | es_change | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | ls_change | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | state_budget_ratio | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | peak_budget_ratio | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | wall_budget_ratio | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | revision_latest | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | old_alias_reappearance | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | revision_semantic | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | unseen_1000 | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | outside_change_1000_100 | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | retention_change | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | es_change | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | ls_change | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | state_budget_ratio | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | peak_budget_ratio | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | wall_budget_ratio | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | revision_latest | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | old_alias_reappearance | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | revision_semantic | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | unseen_1000 | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | outside_change_1000_100 | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | retention_change | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | es_change | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | ls_change | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | state_budget_ratio | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | peak_budget_ratio | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | wall_budget_ratio | None | None | unavailable |
| e82412060e54893dc307a45e | revision_latest | None | None | unavailable |
| e82412060e54893dc307a45e | old_alias_reappearance | None | None | unavailable |
| e82412060e54893dc307a45e | revision_semantic | None | None | unavailable |
| e82412060e54893dc307a45e | unseen_1000 | None | None | unavailable |
| e82412060e54893dc307a45e | outside_change_1000_100 | None | None | unavailable |
| e82412060e54893dc307a45e | retention_change | None | None | unavailable |
| e82412060e54893dc307a45e | es_change | None | None | unavailable |
| e82412060e54893dc307a45e | ls_change | None | None | unavailable |
| e82412060e54893dc307a45e | state_budget_ratio | None | None | unavailable |
| e82412060e54893dc307a45e | peak_budget_ratio | None | None | unavailable |
| e82412060e54893dc307a45e | wall_budget_ratio | None | None | unavailable |
| b42dfb1e539cb4645127e844 | revision_latest | None | None | unavailable |
| b42dfb1e539cb4645127e844 | old_alias_reappearance | None | None | unavailable |
| b42dfb1e539cb4645127e844 | revision_semantic | None | None | unavailable |
| b42dfb1e539cb4645127e844 | unseen_1000 | None | None | unavailable |
| b42dfb1e539cb4645127e844 | outside_change_1000_100 | None | None | unavailable |
| b42dfb1e539cb4645127e844 | retention_change | None | None | unavailable |
| b42dfb1e539cb4645127e844 | es_change | None | None | unavailable |
| b42dfb1e539cb4645127e844 | ls_change | None | None | unavailable |
| b42dfb1e539cb4645127e844 | state_budget_ratio | None | None | unavailable |
| b42dfb1e539cb4645127e844 | peak_budget_ratio | None | None | unavailable |
| b42dfb1e539cb4645127e844 | wall_budget_ratio | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | revision_latest | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | old_alias_reappearance | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | revision_semantic | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | unseen_1000 | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | outside_change_1000_100 | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | retention_change | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | es_change | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | ls_change | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | state_budget_ratio | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | peak_budget_ratio | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | wall_budget_ratio | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | revision_latest | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | old_alias_reappearance | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | revision_semantic | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | unseen_1000 | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | outside_change_1000_100 | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | retention_change | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | es_change | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | ls_change | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | state_budget_ratio | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | peak_budget_ratio | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | wall_budget_ratio | None | None | unavailable |
| 978f353680dde68625399775 | revision_latest | None | None | unavailable |
| 978f353680dde68625399775 | old_alias_reappearance | None | None | unavailable |
| 978f353680dde68625399775 | revision_semantic | None | None | unavailable |
| 978f353680dde68625399775 | unseen_1000 | None | None | unavailable |
| 978f353680dde68625399775 | outside_change_1000_100 | None | None | unavailable |
| 978f353680dde68625399775 | retention_change | None | None | unavailable |
| 978f353680dde68625399775 | es_change | None | None | unavailable |
| 978f353680dde68625399775 | ls_change | None | None | unavailable |
| 978f353680dde68625399775 | state_budget_ratio | None | None | unavailable |
| 978f353680dde68625399775 | peak_budget_ratio | None | None | unavailable |
| 978f353680dde68625399775 | wall_budget_ratio | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | revision_latest | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | old_alias_reappearance | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | revision_semantic | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | unseen_1000 | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | outside_change_1000_100 | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | retention_change | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | es_change | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | ls_change | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | state_budget_ratio | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | peak_budget_ratio | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | wall_budget_ratio | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | revision_latest | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | old_alias_reappearance | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | revision_semantic | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | unseen_1000 | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | outside_change_1000_100 | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | retention_change | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | es_change | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | ls_change | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | state_budget_ratio | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | peak_budget_ratio | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | wall_budget_ratio | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | revision_latest | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | old_alias_reappearance | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | revision_semantic | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | unseen_1000 | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | outside_change_1000_100 | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | retention_change | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | es_change | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | ls_change | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | state_budget_ratio | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | peak_budget_ratio | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | wall_budget_ratio | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | revision_latest | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | old_alias_reappearance | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | revision_semantic | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | unseen_1000 | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | outside_change_1000_100 | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | retention_change | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | es_change | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | ls_change | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | state_budget_ratio | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | peak_budget_ratio | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | wall_budget_ratio | None | None | unavailable |
| f67e77a0b124376f29b78302 | revision_latest | None | None | unavailable |
| f67e77a0b124376f29b78302 | old_alias_reappearance | None | None | unavailable |
| f67e77a0b124376f29b78302 | revision_semantic | None | None | unavailable |
| f67e77a0b124376f29b78302 | unseen_1000 | None | None | unavailable |
| f67e77a0b124376f29b78302 | outside_change_1000_100 | None | None | unavailable |
| f67e77a0b124376f29b78302 | retention_change | None | None | unavailable |
| f67e77a0b124376f29b78302 | es_change | None | None | unavailable |
| f67e77a0b124376f29b78302 | ls_change | None | None | unavailable |
| f67e77a0b124376f29b78302 | state_budget_ratio | None | None | unavailable |
| f67e77a0b124376f29b78302 | peak_budget_ratio | None | None | unavailable |
| f67e77a0b124376f29b78302 | wall_budget_ratio | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | revision_latest | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | old_alias_reappearance | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | revision_semantic | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | unseen_1000 | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | outside_change_1000_100 | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | retention_change | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | es_change | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | ls_change | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | state_budget_ratio | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | peak_budget_ratio | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | wall_budget_ratio | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | revision_latest | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | old_alias_reappearance | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | revision_semantic | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | unseen_1000 | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | outside_change_1000_100 | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | retention_change | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | es_change | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | ls_change | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | state_budget_ratio | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | peak_budget_ratio | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | wall_budget_ratio | None | None | unavailable |
| 8905e452833b0a01defd8b1e | revision_latest | None | None | unavailable |
| 8905e452833b0a01defd8b1e | old_alias_reappearance | None | None | unavailable |
| 8905e452833b0a01defd8b1e | revision_semantic | None | None | unavailable |
| 8905e452833b0a01defd8b1e | unseen_1000 | None | None | unavailable |
| 8905e452833b0a01defd8b1e | outside_change_1000_100 | None | None | unavailable |
| 8905e452833b0a01defd8b1e | retention_change | None | None | unavailable |
| 8905e452833b0a01defd8b1e | es_change | None | None | unavailable |
| 8905e452833b0a01defd8b1e | ls_change | None | None | unavailable |
| 8905e452833b0a01defd8b1e | state_budget_ratio | None | None | unavailable |
| 8905e452833b0a01defd8b1e | peak_budget_ratio | None | None | unavailable |
| 8905e452833b0a01defd8b1e | wall_budget_ratio | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | revision_latest | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | old_alias_reappearance | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | revision_semantic | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | unseen_1000 | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | outside_change_1000_100 | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | retention_change | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | es_change | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | ls_change | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | state_budget_ratio | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | peak_budget_ratio | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | wall_budget_ratio | None | None | unavailable |
| 861414ea84239f8471f0ade8 | revision_latest | None | None | unavailable |
| 861414ea84239f8471f0ade8 | old_alias_reappearance | None | None | unavailable |
| 861414ea84239f8471f0ade8 | revision_semantic | None | None | unavailable |
| 861414ea84239f8471f0ade8 | unseen_1000 | None | None | unavailable |
| 861414ea84239f8471f0ade8 | outside_change_1000_100 | None | None | unavailable |
| 861414ea84239f8471f0ade8 | retention_change | None | None | unavailable |
| 861414ea84239f8471f0ade8 | es_change | None | None | unavailable |
| 861414ea84239f8471f0ade8 | ls_change | None | None | unavailable |
| 861414ea84239f8471f0ade8 | state_budget_ratio | None | None | unavailable |
| 861414ea84239f8471f0ade8 | peak_budget_ratio | None | None | unavailable |
| 861414ea84239f8471f0ade8 | wall_budget_ratio | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | revision_latest | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | old_alias_reappearance | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | revision_semantic | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | unseen_1000 | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | outside_change_1000_100 | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | retention_change | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | es_change | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | ls_change | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | state_budget_ratio | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | peak_budget_ratio | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | wall_budget_ratio | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | revision_latest | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | old_alias_reappearance | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | revision_semantic | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | unseen_1000 | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | outside_change_1000_100 | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | retention_change | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | es_change | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | ls_change | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | state_budget_ratio | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | peak_budget_ratio | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | wall_budget_ratio | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | revision_latest | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | old_alias_reappearance | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | revision_semantic | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | unseen_1000 | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | outside_change_1000_100 | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | retention_change | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | es_change | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | ls_change | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | state_budget_ratio | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | peak_budget_ratio | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | wall_budget_ratio | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | revision_latest | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | old_alias_reappearance | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | revision_semantic | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | unseen_1000 | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | outside_change_1000_100 | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | retention_change | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | es_change | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | ls_change | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | state_budget_ratio | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | peak_budget_ratio | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | wall_budget_ratio | None | None | unavailable |
| bca38cd4398e1159ed781bff | revision_latest | None | None | unavailable |
| bca38cd4398e1159ed781bff | old_alias_reappearance | None | None | unavailable |
| bca38cd4398e1159ed781bff | revision_semantic | None | None | unavailable |
| bca38cd4398e1159ed781bff | unseen_1000 | None | None | unavailable |
| bca38cd4398e1159ed781bff | outside_change_1000_100 | None | None | unavailable |
| bca38cd4398e1159ed781bff | retention_change | None | None | unavailable |
| bca38cd4398e1159ed781bff | es_change | None | None | unavailable |
| bca38cd4398e1159ed781bff | ls_change | None | None | unavailable |
| bca38cd4398e1159ed781bff | state_budget_ratio | None | None | unavailable |
| bca38cd4398e1159ed781bff | peak_budget_ratio | None | None | unavailable |
| bca38cd4398e1159ed781bff | wall_budget_ratio | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | revision_latest | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | old_alias_reappearance | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | revision_semantic | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | unseen_1000 | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | outside_change_1000_100 | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | retention_change | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | es_change | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | ls_change | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | state_budget_ratio | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | peak_budget_ratio | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | wall_budget_ratio | None | None | unavailable |
| da666451073f38000c71b39f | revision_latest | None | None | unavailable |
| da666451073f38000c71b39f | old_alias_reappearance | None | None | unavailable |
| da666451073f38000c71b39f | revision_semantic | None | None | unavailable |
| da666451073f38000c71b39f | unseen_1000 | None | None | unavailable |
| da666451073f38000c71b39f | outside_change_1000_100 | None | None | unavailable |
| da666451073f38000c71b39f | retention_change | None | None | unavailable |
| da666451073f38000c71b39f | es_change | None | None | unavailable |
| da666451073f38000c71b39f | ls_change | None | None | unavailable |
| da666451073f38000c71b39f | state_budget_ratio | None | None | unavailable |
| da666451073f38000c71b39f | peak_budget_ratio | None | None | unavailable |
| da666451073f38000c71b39f | wall_budget_ratio | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | revision_latest | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | old_alias_reappearance | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | revision_semantic | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | unseen_1000 | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | outside_change_1000_100 | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | retention_change | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | es_change | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | ls_change | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | state_budget_ratio | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | peak_budget_ratio | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | wall_budget_ratio | None | None | unavailable |
| b1be521b209066effb830ad1 | revision_latest | None | None | unavailable |
| b1be521b209066effb830ad1 | old_alias_reappearance | None | None | unavailable |
| b1be521b209066effb830ad1 | revision_semantic | None | None | unavailable |
| b1be521b209066effb830ad1 | unseen_1000 | None | None | unavailable |
| b1be521b209066effb830ad1 | outside_change_1000_100 | None | None | unavailable |
| b1be521b209066effb830ad1 | retention_change | None | None | unavailable |
| b1be521b209066effb830ad1 | es_change | None | None | unavailable |
| b1be521b209066effb830ad1 | ls_change | None | None | unavailable |
| b1be521b209066effb830ad1 | state_budget_ratio | None | None | unavailable |
| b1be521b209066effb830ad1 | peak_budget_ratio | None | None | unavailable |
| b1be521b209066effb830ad1 | wall_budget_ratio | None | None | unavailable |
| d246da52d2783b0000af34aa | revision_latest | None | None | unavailable |
| d246da52d2783b0000af34aa | old_alias_reappearance | None | None | unavailable |
| d246da52d2783b0000af34aa | revision_semantic | None | None | unavailable |
| d246da52d2783b0000af34aa | unseen_1000 | None | None | unavailable |
| d246da52d2783b0000af34aa | outside_change_1000_100 | None | None | unavailable |
| d246da52d2783b0000af34aa | retention_change | None | None | unavailable |
| d246da52d2783b0000af34aa | es_change | None | None | unavailable |
| d246da52d2783b0000af34aa | ls_change | None | None | unavailable |
| d246da52d2783b0000af34aa | state_budget_ratio | None | None | unavailable |
| d246da52d2783b0000af34aa | peak_budget_ratio | None | None | unavailable |
| d246da52d2783b0000af34aa | wall_budget_ratio | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | revision_latest | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | old_alias_reappearance | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | revision_semantic | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | unseen_1000 | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | outside_change_1000_100 | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | retention_change | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | es_change | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | ls_change | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | state_budget_ratio | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | peak_budget_ratio | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | wall_budget_ratio | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | revision_latest | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | old_alias_reappearance | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | revision_semantic | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | unseen_1000 | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | outside_change_1000_100 | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | retention_change | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | es_change | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | ls_change | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | state_budget_ratio | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | peak_budget_ratio | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | wall_budget_ratio | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | revision_latest | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | old_alias_reappearance | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | revision_semantic | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | unseen_1000 | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | outside_change_1000_100 | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | retention_change | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | es_change | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | ls_change | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | state_budget_ratio | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | peak_budget_ratio | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | wall_budget_ratio | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | revision_latest | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | old_alias_reappearance | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | revision_semantic | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | unseen_1000 | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | outside_change_1000_100 | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | retention_change | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | es_change | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | ls_change | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | state_budget_ratio | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | peak_budget_ratio | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | wall_budget_ratio | None | None | unavailable |
| 635bac1c845730dae487891a | revision_latest | None | None | unavailable |
| 635bac1c845730dae487891a | old_alias_reappearance | None | None | unavailable |
| 635bac1c845730dae487891a | revision_semantic | None | None | unavailable |
| 635bac1c845730dae487891a | unseen_1000 | None | None | unavailable |
| 635bac1c845730dae487891a | outside_change_1000_100 | None | None | unavailable |
| 635bac1c845730dae487891a | retention_change | None | None | unavailable |
| 635bac1c845730dae487891a | es_change | None | None | unavailable |
| 635bac1c845730dae487891a | ls_change | None | None | unavailable |
| 635bac1c845730dae487891a | state_budget_ratio | None | None | unavailable |
| 635bac1c845730dae487891a | peak_budget_ratio | None | None | unavailable |
| 635bac1c845730dae487891a | wall_budget_ratio | None | None | unavailable |
| 031ae1822109079d3cddb520 | revision_latest | None | None | unavailable |
| 031ae1822109079d3cddb520 | old_alias_reappearance | None | None | unavailable |
| 031ae1822109079d3cddb520 | revision_semantic | None | None | unavailable |
| 031ae1822109079d3cddb520 | unseen_1000 | None | None | unavailable |
| 031ae1822109079d3cddb520 | outside_change_1000_100 | None | None | unavailable |
| 031ae1822109079d3cddb520 | retention_change | None | None | unavailable |
| 031ae1822109079d3cddb520 | es_change | None | None | unavailable |
| 031ae1822109079d3cddb520 | ls_change | None | None | unavailable |
| 031ae1822109079d3cddb520 | state_budget_ratio | None | None | unavailable |
| 031ae1822109079d3cddb520 | peak_budget_ratio | None | None | unavailable |
| 031ae1822109079d3cddb520 | wall_budget_ratio | None | None | unavailable |
| 3435ab1a884c517b32867161 | revision_latest | None | None | unavailable |
| 3435ab1a884c517b32867161 | old_alias_reappearance | None | None | unavailable |
| 3435ab1a884c517b32867161 | revision_semantic | None | None | unavailable |
| 3435ab1a884c517b32867161 | unseen_1000 | None | None | unavailable |
| 3435ab1a884c517b32867161 | outside_change_1000_100 | None | None | unavailable |
| 3435ab1a884c517b32867161 | retention_change | None | None | unavailable |
| 3435ab1a884c517b32867161 | es_change | None | None | unavailable |
| 3435ab1a884c517b32867161 | ls_change | None | None | unavailable |
| 3435ab1a884c517b32867161 | state_budget_ratio | None | None | unavailable |
| 3435ab1a884c517b32867161 | peak_budget_ratio | None | None | unavailable |
| 3435ab1a884c517b32867161 | wall_budget_ratio | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | revision_latest | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | old_alias_reappearance | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | revision_semantic | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | unseen_1000 | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | outside_change_1000_100 | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | retention_change | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | es_change | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | ls_change | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | state_budget_ratio | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | peak_budget_ratio | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | wall_budget_ratio | None | None | unavailable |
| fa309fa719c353f20a813699 | revision_latest | None | None | unavailable |
| fa309fa719c353f20a813699 | old_alias_reappearance | None | None | unavailable |
| fa309fa719c353f20a813699 | revision_semantic | None | None | unavailable |
| fa309fa719c353f20a813699 | unseen_1000 | None | None | unavailable |
| fa309fa719c353f20a813699 | outside_change_1000_100 | None | None | unavailable |
| fa309fa719c353f20a813699 | retention_change | None | None | unavailable |
| fa309fa719c353f20a813699 | es_change | None | None | unavailable |
| fa309fa719c353f20a813699 | ls_change | None | None | unavailable |
| fa309fa719c353f20a813699 | state_budget_ratio | None | None | unavailable |
| fa309fa719c353f20a813699 | peak_budget_ratio | None | None | unavailable |
| fa309fa719c353f20a813699 | wall_budget_ratio | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | revision_latest | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | old_alias_reappearance | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | revision_semantic | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | unseen_1000 | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | outside_change_1000_100 | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | retention_change | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | es_change | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | ls_change | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | state_budget_ratio | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | peak_budget_ratio | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | wall_budget_ratio | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | revision_latest | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | old_alias_reappearance | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | revision_semantic | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | unseen_1000 | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | outside_change_1000_100 | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | retention_change | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | es_change | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | ls_change | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | state_budget_ratio | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | peak_budget_ratio | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | wall_budget_ratio | None | None | unavailable |
| c14b2b630688912a588e1cf3 | revision_latest | None | None | unavailable |
| c14b2b630688912a588e1cf3 | old_alias_reappearance | None | None | unavailable |
| c14b2b630688912a588e1cf3 | revision_semantic | None | None | unavailable |
| c14b2b630688912a588e1cf3 | unseen_1000 | None | None | unavailable |
| c14b2b630688912a588e1cf3 | outside_change_1000_100 | None | None | unavailable |
| c14b2b630688912a588e1cf3 | retention_change | None | None | unavailable |
| c14b2b630688912a588e1cf3 | es_change | None | None | unavailable |
| c14b2b630688912a588e1cf3 | ls_change | None | None | unavailable |
| c14b2b630688912a588e1cf3 | state_budget_ratio | None | None | unavailable |
| c14b2b630688912a588e1cf3 | peak_budget_ratio | None | None | unavailable |
| c14b2b630688912a588e1cf3 | wall_budget_ratio | None | None | unavailable |
| 2eda7453d476d16c07a327ed | revision_latest | None | None | unavailable |
| 2eda7453d476d16c07a327ed | old_alias_reappearance | None | None | unavailable |
| 2eda7453d476d16c07a327ed | revision_semantic | None | None | unavailable |
| 2eda7453d476d16c07a327ed | unseen_1000 | None | None | unavailable |
| 2eda7453d476d16c07a327ed | outside_change_1000_100 | None | None | unavailable |
| 2eda7453d476d16c07a327ed | retention_change | None | None | unavailable |
| 2eda7453d476d16c07a327ed | es_change | None | None | unavailable |
| 2eda7453d476d16c07a327ed | ls_change | None | None | unavailable |
| 2eda7453d476d16c07a327ed | state_budget_ratio | None | None | unavailable |
| 2eda7453d476d16c07a327ed | peak_budget_ratio | None | None | unavailable |
| 2eda7453d476d16c07a327ed | wall_budget_ratio | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | revision_latest | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | old_alias_reappearance | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | revision_semantic | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | unseen_1000 | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | outside_change_1000_100 | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | retention_change | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | es_change | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | ls_change | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | state_budget_ratio | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | peak_budget_ratio | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | wall_budget_ratio | None | None | unavailable |
| 0362b36136a70031c319de5f | revision_latest | None | None | unavailable |
| 0362b36136a70031c319de5f | old_alias_reappearance | None | None | unavailable |
| 0362b36136a70031c319de5f | revision_semantic | None | None | unavailable |
| 0362b36136a70031c319de5f | unseen_1000 | None | None | unavailable |
| 0362b36136a70031c319de5f | outside_change_1000_100 | None | None | unavailable |
| 0362b36136a70031c319de5f | retention_change | None | None | unavailable |
| 0362b36136a70031c319de5f | es_change | None | None | unavailable |
| 0362b36136a70031c319de5f | ls_change | None | None | unavailable |
| 0362b36136a70031c319de5f | state_budget_ratio | None | None | unavailable |
| 0362b36136a70031c319de5f | peak_budget_ratio | None | None | unavailable |
| 0362b36136a70031c319de5f | wall_budget_ratio | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | revision_latest | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | old_alias_reappearance | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | revision_semantic | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | unseen_1000 | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | outside_change_1000_100 | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | retention_change | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | es_change | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | ls_change | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | state_budget_ratio | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | peak_budget_ratio | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | wall_budget_ratio | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | revision_latest | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | old_alias_reappearance | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | revision_semantic | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | unseen_1000 | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | outside_change_1000_100 | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | retention_change | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | es_change | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | ls_change | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | state_budget_ratio | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | peak_budget_ratio | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | wall_budget_ratio | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | revision_latest | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | old_alias_reappearance | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | revision_semantic | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | unseen_1000 | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | outside_change_1000_100 | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | retention_change | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | es_change | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | ls_change | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | state_budget_ratio | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | peak_budget_ratio | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | wall_budget_ratio | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | revision_latest | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | old_alias_reappearance | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | revision_semantic | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | unseen_1000 | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | outside_change_1000_100 | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | retention_change | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | es_change | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | ls_change | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | state_budget_ratio | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | peak_budget_ratio | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | wall_budget_ratio | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | revision_latest | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | old_alias_reappearance | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | revision_semantic | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | unseen_1000 | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | outside_change_1000_100 | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | retention_change | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | es_change | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | ls_change | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | state_budget_ratio | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | peak_budget_ratio | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | wall_budget_ratio | None | None | unavailable |
| 508b709256adff820b7fdf82 | revision_latest | None | None | unavailable |
| 508b709256adff820b7fdf82 | old_alias_reappearance | None | None | unavailable |
| 508b709256adff820b7fdf82 | revision_semantic | None | None | unavailable |
| 508b709256adff820b7fdf82 | unseen_1000 | None | None | unavailable |
| 508b709256adff820b7fdf82 | outside_change_1000_100 | None | None | unavailable |
| 508b709256adff820b7fdf82 | retention_change | None | None | unavailable |
| 508b709256adff820b7fdf82 | es_change | None | None | unavailable |
| 508b709256adff820b7fdf82 | ls_change | None | None | unavailable |
| 508b709256adff820b7fdf82 | state_budget_ratio | None | None | unavailable |
| 508b709256adff820b7fdf82 | peak_budget_ratio | None | None | unavailable |
| 508b709256adff820b7fdf82 | wall_budget_ratio | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | revision_latest | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | old_alias_reappearance | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | revision_semantic | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | unseen_1000 | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | outside_change_1000_100 | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | retention_change | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | es_change | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | ls_change | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | state_budget_ratio | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | peak_budget_ratio | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | wall_budget_ratio | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | revision_latest | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | old_alias_reappearance | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | revision_semantic | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | unseen_1000 | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | outside_change_1000_100 | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | retention_change | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | es_change | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | ls_change | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | state_budget_ratio | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | peak_budget_ratio | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | wall_budget_ratio | None | None | unavailable |
| 302070707affaaec2265e772 | revision_latest | None | None | unavailable |
| 302070707affaaec2265e772 | old_alias_reappearance | None | None | unavailable |
| 302070707affaaec2265e772 | revision_semantic | None | None | unavailable |
| 302070707affaaec2265e772 | unseen_1000 | None | None | unavailable |
| 302070707affaaec2265e772 | outside_change_1000_100 | None | None | unavailable |
| 302070707affaaec2265e772 | retention_change | None | None | unavailable |
| 302070707affaaec2265e772 | es_change | None | None | unavailable |
| 302070707affaaec2265e772 | ls_change | None | None | unavailable |
| 302070707affaaec2265e772 | state_budget_ratio | None | None | unavailable |
| 302070707affaaec2265e772 | peak_budget_ratio | None | None | unavailable |
| 302070707affaaec2265e772 | wall_budget_ratio | None | None | unavailable |
| 74feefbadad2b95947437ed6 | revision_latest | None | None | unavailable |
| 74feefbadad2b95947437ed6 | old_alias_reappearance | None | None | unavailable |
| 74feefbadad2b95947437ed6 | revision_semantic | None | None | unavailable |
| 74feefbadad2b95947437ed6 | unseen_1000 | None | None | unavailable |
| 74feefbadad2b95947437ed6 | outside_change_1000_100 | None | None | unavailable |
| 74feefbadad2b95947437ed6 | retention_change | None | None | unavailable |
| 74feefbadad2b95947437ed6 | es_change | None | None | unavailable |
| 74feefbadad2b95947437ed6 | ls_change | None | None | unavailable |
| 74feefbadad2b95947437ed6 | state_budget_ratio | None | None | unavailable |
| 74feefbadad2b95947437ed6 | peak_budget_ratio | None | None | unavailable |
| 74feefbadad2b95947437ed6 | wall_budget_ratio | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | revision_latest | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | old_alias_reappearance | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | revision_semantic | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | unseen_1000 | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | outside_change_1000_100 | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | retention_change | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | es_change | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | ls_change | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | state_budget_ratio | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | peak_budget_ratio | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | wall_budget_ratio | None | None | unavailable |
| 2e5068d168160234340d32fa | revision_latest | None | None | unavailable |
| 2e5068d168160234340d32fa | old_alias_reappearance | None | None | unavailable |
| 2e5068d168160234340d32fa | revision_semantic | None | None | unavailable |
| 2e5068d168160234340d32fa | unseen_1000 | None | None | unavailable |
| 2e5068d168160234340d32fa | outside_change_1000_100 | None | None | unavailable |
| 2e5068d168160234340d32fa | retention_change | None | None | unavailable |
| 2e5068d168160234340d32fa | es_change | None | None | unavailable |
| 2e5068d168160234340d32fa | ls_change | None | None | unavailable |
| 2e5068d168160234340d32fa | state_budget_ratio | None | None | unavailable |
| 2e5068d168160234340d32fa | peak_budget_ratio | None | None | unavailable |
| 2e5068d168160234340d32fa | wall_budget_ratio | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | revision_latest | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | old_alias_reappearance | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | revision_semantic | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | unseen_1000 | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | outside_change_1000_100 | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | retention_change | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | es_change | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | ls_change | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | state_budget_ratio | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | peak_budget_ratio | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | wall_budget_ratio | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | revision_latest | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | old_alias_reappearance | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | revision_semantic | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | unseen_1000 | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | outside_change_1000_100 | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | retention_change | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | es_change | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | ls_change | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | state_budget_ratio | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | peak_budget_ratio | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | wall_budget_ratio | None | None | unavailable |
| 8499903e83df71431114aaa8 | revision_latest | None | None | unavailable |
| 8499903e83df71431114aaa8 | old_alias_reappearance | None | None | unavailable |
| 8499903e83df71431114aaa8 | revision_semantic | None | None | unavailable |
| 8499903e83df71431114aaa8 | unseen_1000 | None | None | unavailable |
| 8499903e83df71431114aaa8 | outside_change_1000_100 | None | None | unavailable |
| 8499903e83df71431114aaa8 | retention_change | None | None | unavailable |
| 8499903e83df71431114aaa8 | es_change | None | None | unavailable |
| 8499903e83df71431114aaa8 | ls_change | None | None | unavailable |
| 8499903e83df71431114aaa8 | state_budget_ratio | None | None | unavailable |
| 8499903e83df71431114aaa8 | peak_budget_ratio | None | None | unavailable |
| 8499903e83df71431114aaa8 | wall_budget_ratio | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | revision_latest | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | old_alias_reappearance | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | revision_semantic | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | unseen_1000 | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | outside_change_1000_100 | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | retention_change | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | es_change | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | ls_change | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | state_budget_ratio | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | peak_budget_ratio | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | wall_budget_ratio | None | None | unavailable |
| 9f020616201afdc368d77f9b | revision_latest | None | None | unavailable |
| 9f020616201afdc368d77f9b | old_alias_reappearance | None | None | unavailable |
| 9f020616201afdc368d77f9b | revision_semantic | None | None | unavailable |
| 9f020616201afdc368d77f9b | unseen_1000 | None | None | unavailable |
| 9f020616201afdc368d77f9b | outside_change_1000_100 | None | None | unavailable |
| 9f020616201afdc368d77f9b | retention_change | None | None | unavailable |
| 9f020616201afdc368d77f9b | es_change | None | None | unavailable |
| 9f020616201afdc368d77f9b | ls_change | None | None | unavailable |
| 9f020616201afdc368d77f9b | state_budget_ratio | None | None | unavailable |
| 9f020616201afdc368d77f9b | peak_budget_ratio | None | None | unavailable |
| 9f020616201afdc368d77f9b | wall_budget_ratio | None | None | unavailable |
| 26318156d310334e8b260e87 | revision_latest | None | None | unavailable |
| 26318156d310334e8b260e87 | old_alias_reappearance | None | None | unavailable |
| 26318156d310334e8b260e87 | revision_semantic | None | None | unavailable |
| 26318156d310334e8b260e87 | unseen_1000 | None | None | unavailable |
| 26318156d310334e8b260e87 | outside_change_1000_100 | None | None | unavailable |
| 26318156d310334e8b260e87 | retention_change | None | None | unavailable |
| 26318156d310334e8b260e87 | es_change | None | None | unavailable |
| 26318156d310334e8b260e87 | ls_change | None | None | unavailable |
| 26318156d310334e8b260e87 | state_budget_ratio | None | None | unavailable |
| 26318156d310334e8b260e87 | peak_budget_ratio | None | None | unavailable |
| 26318156d310334e8b260e87 | wall_budget_ratio | None | None | unavailable |
| d7241b9882514c2709082321 | revision_latest | None | None | unavailable |
| d7241b9882514c2709082321 | old_alias_reappearance | None | None | unavailable |
| d7241b9882514c2709082321 | revision_semantic | None | None | unavailable |
| d7241b9882514c2709082321 | unseen_1000 | None | None | unavailable |
| d7241b9882514c2709082321 | outside_change_1000_100 | None | None | unavailable |
| d7241b9882514c2709082321 | retention_change | None | None | unavailable |
| d7241b9882514c2709082321 | es_change | None | None | unavailable |
| d7241b9882514c2709082321 | ls_change | None | None | unavailable |
| d7241b9882514c2709082321 | state_budget_ratio | None | None | unavailable |
| d7241b9882514c2709082321 | peak_budget_ratio | None | None | unavailable |
| d7241b9882514c2709082321 | wall_budget_ratio | None | None | unavailable |
| a5b3de3764680273ff4760e1 | revision_latest | None | None | unavailable |
| a5b3de3764680273ff4760e1 | old_alias_reappearance | None | None | unavailable |
| a5b3de3764680273ff4760e1 | revision_semantic | None | None | unavailable |
| a5b3de3764680273ff4760e1 | unseen_1000 | None | None | unavailable |
| a5b3de3764680273ff4760e1 | outside_change_1000_100 | None | None | unavailable |
| a5b3de3764680273ff4760e1 | retention_change | None | None | unavailable |
| a5b3de3764680273ff4760e1 | es_change | None | None | unavailable |
| a5b3de3764680273ff4760e1 | ls_change | None | None | unavailable |
| a5b3de3764680273ff4760e1 | state_budget_ratio | None | None | unavailable |
| a5b3de3764680273ff4760e1 | peak_budget_ratio | None | None | unavailable |
| a5b3de3764680273ff4760e1 | wall_budget_ratio | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | revision_latest | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | old_alias_reappearance | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | revision_semantic | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | unseen_1000 | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | outside_change_1000_100 | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | retention_change | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | es_change | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | ls_change | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | state_budget_ratio | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | peak_budget_ratio | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | wall_budget_ratio | None | None | unavailable |
| 847f33277d9d89fe17482367 | revision_latest | None | None | unavailable |
| 847f33277d9d89fe17482367 | old_alias_reappearance | None | None | unavailable |
| 847f33277d9d89fe17482367 | revision_semantic | None | None | unavailable |
| 847f33277d9d89fe17482367 | unseen_1000 | None | None | unavailable |
| 847f33277d9d89fe17482367 | outside_change_1000_100 | None | None | unavailable |
| 847f33277d9d89fe17482367 | retention_change | None | None | unavailable |
| 847f33277d9d89fe17482367 | es_change | None | None | unavailable |
| 847f33277d9d89fe17482367 | ls_change | None | None | unavailable |
| 847f33277d9d89fe17482367 | state_budget_ratio | None | None | unavailable |
| 847f33277d9d89fe17482367 | peak_budget_ratio | None | None | unavailable |
| 847f33277d9d89fe17482367 | wall_budget_ratio | None | None | unavailable |
| 77568a85e217721985cd8ea4 | revision_latest | None | None | unavailable |
| 77568a85e217721985cd8ea4 | old_alias_reappearance | None | None | unavailable |
| 77568a85e217721985cd8ea4 | revision_semantic | None | None | unavailable |
| 77568a85e217721985cd8ea4 | unseen_1000 | None | None | unavailable |
| 77568a85e217721985cd8ea4 | outside_change_1000_100 | None | None | unavailable |
| 77568a85e217721985cd8ea4 | retention_change | None | None | unavailable |
| 77568a85e217721985cd8ea4 | es_change | None | None | unavailable |
| 77568a85e217721985cd8ea4 | ls_change | None | None | unavailable |
| 77568a85e217721985cd8ea4 | state_budget_ratio | None | None | unavailable |
| 77568a85e217721985cd8ea4 | peak_budget_ratio | None | None | unavailable |
| 77568a85e217721985cd8ea4 | wall_budget_ratio | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | revision_latest | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | old_alias_reappearance | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | revision_semantic | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | unseen_1000 | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | outside_change_1000_100 | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | retention_change | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | es_change | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | ls_change | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | state_budget_ratio | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | peak_budget_ratio | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | wall_budget_ratio | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | revision_latest | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | old_alias_reappearance | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | revision_semantic | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | unseen_1000 | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | outside_change_1000_100 | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | retention_change | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | es_change | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | ls_change | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | state_budget_ratio | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | peak_budget_ratio | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | wall_budget_ratio | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | revision_latest | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | old_alias_reappearance | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | revision_semantic | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | unseen_1000 | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | outside_change_1000_100 | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | retention_change | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | es_change | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | ls_change | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | state_budget_ratio | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | peak_budget_ratio | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | wall_budget_ratio | None | None | unavailable |
| 30756d73095e1914cf757782 | revision_latest | None | None | unavailable |
| 30756d73095e1914cf757782 | old_alias_reappearance | None | None | unavailable |
| 30756d73095e1914cf757782 | revision_semantic | None | None | unavailable |
| 30756d73095e1914cf757782 | unseen_1000 | None | None | unavailable |
| 30756d73095e1914cf757782 | outside_change_1000_100 | None | None | unavailable |
| 30756d73095e1914cf757782 | retention_change | None | None | unavailable |
| 30756d73095e1914cf757782 | es_change | None | None | unavailable |
| 30756d73095e1914cf757782 | ls_change | None | None | unavailable |
| 30756d73095e1914cf757782 | state_budget_ratio | None | None | unavailable |
| 30756d73095e1914cf757782 | peak_budget_ratio | None | None | unavailable |
| 30756d73095e1914cf757782 | wall_budget_ratio | None | None | unavailable |
| d74e8582f780dfdeb9281671 | revision_latest | None | None | unavailable |
| d74e8582f780dfdeb9281671 | old_alias_reappearance | None | None | unavailable |
| d74e8582f780dfdeb9281671 | revision_semantic | None | None | unavailable |
| d74e8582f780dfdeb9281671 | unseen_1000 | None | None | unavailable |
| d74e8582f780dfdeb9281671 | outside_change_1000_100 | None | None | unavailable |
| d74e8582f780dfdeb9281671 | retention_change | None | None | unavailable |
| d74e8582f780dfdeb9281671 | es_change | None | None | unavailable |
| d74e8582f780dfdeb9281671 | ls_change | None | None | unavailable |
| d74e8582f780dfdeb9281671 | state_budget_ratio | None | None | unavailable |
| d74e8582f780dfdeb9281671 | peak_budget_ratio | None | None | unavailable |
| d74e8582f780dfdeb9281671 | wall_budget_ratio | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | revision_latest | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | old_alias_reappearance | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | revision_semantic | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | unseen_1000 | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | outside_change_1000_100 | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | retention_change | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | es_change | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | ls_change | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | state_budget_ratio | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | peak_budget_ratio | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | wall_budget_ratio | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | revision_latest | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | old_alias_reappearance | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | revision_semantic | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | unseen_1000 | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | outside_change_1000_100 | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | retention_change | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | es_change | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | ls_change | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | state_budget_ratio | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | peak_budget_ratio | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | wall_budget_ratio | None | None | unavailable |
| bbbda4ebfb279ed21179678b | revision_latest | None | None | unavailable |
| bbbda4ebfb279ed21179678b | old_alias_reappearance | None | None | unavailable |
| bbbda4ebfb279ed21179678b | revision_semantic | None | None | unavailable |
| bbbda4ebfb279ed21179678b | unseen_1000 | None | None | unavailable |
| bbbda4ebfb279ed21179678b | outside_change_1000_100 | None | None | unavailable |
| bbbda4ebfb279ed21179678b | retention_change | None | None | unavailable |
| bbbda4ebfb279ed21179678b | es_change | None | None | unavailable |
| bbbda4ebfb279ed21179678b | ls_change | None | None | unavailable |
| bbbda4ebfb279ed21179678b | state_budget_ratio | None | None | unavailable |
| bbbda4ebfb279ed21179678b | peak_budget_ratio | None | None | unavailable |
| bbbda4ebfb279ed21179678b | wall_budget_ratio | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | revision_latest | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | old_alias_reappearance | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | revision_semantic | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | unseen_1000 | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | outside_change_1000_100 | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | retention_change | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | es_change | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | ls_change | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | state_budget_ratio | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | peak_budget_ratio | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | wall_budget_ratio | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | revision_latest | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | old_alias_reappearance | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | revision_semantic | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | unseen_1000 | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | outside_change_1000_100 | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | retention_change | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | es_change | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | ls_change | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | state_budget_ratio | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | peak_budget_ratio | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | wall_budget_ratio | None | None | unavailable |
| 22b85c86caaee83341968cec | revision_latest | None | None | unavailable |
| 22b85c86caaee83341968cec | old_alias_reappearance | None | None | unavailable |
| 22b85c86caaee83341968cec | revision_semantic | None | None | unavailable |
| 22b85c86caaee83341968cec | unseen_1000 | None | None | unavailable |
| 22b85c86caaee83341968cec | outside_change_1000_100 | None | None | unavailable |
| 22b85c86caaee83341968cec | retention_change | None | None | unavailable |
| 22b85c86caaee83341968cec | es_change | None | None | unavailable |
| 22b85c86caaee83341968cec | ls_change | None | None | unavailable |
| 22b85c86caaee83341968cec | state_budget_ratio | None | None | unavailable |
| 22b85c86caaee83341968cec | peak_budget_ratio | None | None | unavailable |
| 22b85c86caaee83341968cec | wall_budget_ratio | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | revision_latest | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | old_alias_reappearance | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | revision_semantic | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | unseen_1000 | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | outside_change_1000_100 | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | retention_change | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | es_change | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | ls_change | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | state_budget_ratio | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | peak_budget_ratio | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | wall_budget_ratio | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | revision_latest | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | old_alias_reappearance | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | revision_semantic | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | unseen_1000 | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | outside_change_1000_100 | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | retention_change | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | es_change | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | ls_change | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | state_budget_ratio | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | peak_budget_ratio | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | wall_budget_ratio | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | revision_latest | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | old_alias_reappearance | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | revision_semantic | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | unseen_1000 | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | outside_change_1000_100 | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | retention_change | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | es_change | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | ls_change | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | state_budget_ratio | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | peak_budget_ratio | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | wall_budget_ratio | None | None | unavailable |
| 5c5511653f8d590c63a39794 | revision_latest | None | None | unavailable |
| 5c5511653f8d590c63a39794 | old_alias_reappearance | None | None | unavailable |
| 5c5511653f8d590c63a39794 | revision_semantic | None | None | unavailable |
| 5c5511653f8d590c63a39794 | unseen_1000 | None | None | unavailable |
| 5c5511653f8d590c63a39794 | outside_change_1000_100 | None | None | unavailable |
| 5c5511653f8d590c63a39794 | retention_change | None | None | unavailable |
| 5c5511653f8d590c63a39794 | es_change | None | None | unavailable |
| 5c5511653f8d590c63a39794 | ls_change | None | None | unavailable |
| 5c5511653f8d590c63a39794 | state_budget_ratio | None | None | unavailable |
| 5c5511653f8d590c63a39794 | peak_budget_ratio | None | None | unavailable |
| 5c5511653f8d590c63a39794 | wall_budget_ratio | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | revision_latest | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | old_alias_reappearance | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | revision_semantic | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | unseen_1000 | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | outside_change_1000_100 | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | retention_change | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | es_change | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | ls_change | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | state_budget_ratio | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | peak_budget_ratio | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | wall_budget_ratio | None | None | unavailable |
| b1a17c1fb747eef11f253278 | revision_latest | None | None | unavailable |
| b1a17c1fb747eef11f253278 | old_alias_reappearance | None | None | unavailable |
| b1a17c1fb747eef11f253278 | revision_semantic | None | None | unavailable |
| b1a17c1fb747eef11f253278 | unseen_1000 | None | None | unavailable |
| b1a17c1fb747eef11f253278 | outside_change_1000_100 | None | None | unavailable |
| b1a17c1fb747eef11f253278 | retention_change | None | None | unavailable |
| b1a17c1fb747eef11f253278 | es_change | None | None | unavailable |
| b1a17c1fb747eef11f253278 | ls_change | None | None | unavailable |
| b1a17c1fb747eef11f253278 | state_budget_ratio | None | None | unavailable |
| b1a17c1fb747eef11f253278 | peak_budget_ratio | None | None | unavailable |
| b1a17c1fb747eef11f253278 | wall_budget_ratio | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | revision_latest | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | old_alias_reappearance | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | revision_semantic | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | unseen_1000 | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | outside_change_1000_100 | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | retention_change | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | es_change | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | ls_change | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | state_budget_ratio | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | peak_budget_ratio | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | wall_budget_ratio | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | revision_latest | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | old_alias_reappearance | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | revision_semantic | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | unseen_1000 | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | outside_change_1000_100 | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | retention_change | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | es_change | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | ls_change | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | state_budget_ratio | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | peak_budget_ratio | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | wall_budget_ratio | None | None | unavailable |
| 46d6404412a25fbdd2965880 | revision_latest | None | None | unavailable |
| 46d6404412a25fbdd2965880 | old_alias_reappearance | None | None | unavailable |
| 46d6404412a25fbdd2965880 | revision_semantic | None | None | unavailable |
| 46d6404412a25fbdd2965880 | unseen_1000 | None | None | unavailable |
| 46d6404412a25fbdd2965880 | outside_change_1000_100 | None | None | unavailable |
| 46d6404412a25fbdd2965880 | retention_change | None | None | unavailable |
| 46d6404412a25fbdd2965880 | es_change | None | None | unavailable |
| 46d6404412a25fbdd2965880 | ls_change | None | None | unavailable |
| 46d6404412a25fbdd2965880 | state_budget_ratio | None | None | unavailable |
| 46d6404412a25fbdd2965880 | peak_budget_ratio | None | None | unavailable |
| 46d6404412a25fbdd2965880 | wall_budget_ratio | None | None | unavailable |
| 50af2a28b866c26021d83b01 | revision_latest | None | None | unavailable |
| 50af2a28b866c26021d83b01 | old_alias_reappearance | None | None | unavailable |
| 50af2a28b866c26021d83b01 | revision_semantic | None | None | unavailable |
| 50af2a28b866c26021d83b01 | unseen_1000 | None | None | unavailable |
| 50af2a28b866c26021d83b01 | outside_change_1000_100 | None | None | unavailable |
| 50af2a28b866c26021d83b01 | retention_change | None | None | unavailable |
| 50af2a28b866c26021d83b01 | es_change | None | None | unavailable |
| 50af2a28b866c26021d83b01 | ls_change | None | None | unavailable |
| 50af2a28b866c26021d83b01 | state_budget_ratio | None | None | unavailable |
| 50af2a28b866c26021d83b01 | peak_budget_ratio | None | None | unavailable |
| 50af2a28b866c26021d83b01 | wall_budget_ratio | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | revision_latest | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | old_alias_reappearance | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | revision_semantic | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | unseen_1000 | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | outside_change_1000_100 | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | retention_change | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | es_change | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | ls_change | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | state_budget_ratio | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | peak_budget_ratio | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | wall_budget_ratio | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | revision_latest | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | old_alias_reappearance | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | revision_semantic | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | unseen_1000 | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | outside_change_1000_100 | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | retention_change | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | es_change | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | ls_change | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | state_budget_ratio | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | peak_budget_ratio | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | wall_budget_ratio | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | revision_latest | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | old_alias_reappearance | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | revision_semantic | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | unseen_1000 | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | outside_change_1000_100 | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | retention_change | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | es_change | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | ls_change | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | state_budget_ratio | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | peak_budget_ratio | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | wall_budget_ratio | None | None | unavailable |
| 151bacf1f85b74f88864784e | revision_latest | None | None | unavailable |
| 151bacf1f85b74f88864784e | old_alias_reappearance | None | None | unavailable |
| 151bacf1f85b74f88864784e | revision_semantic | None | None | unavailable |
| 151bacf1f85b74f88864784e | unseen_1000 | None | None | unavailable |
| 151bacf1f85b74f88864784e | outside_change_1000_100 | None | None | unavailable |
| 151bacf1f85b74f88864784e | retention_change | None | None | unavailable |
| 151bacf1f85b74f88864784e | es_change | None | None | unavailable |
| 151bacf1f85b74f88864784e | ls_change | None | None | unavailable |
| 151bacf1f85b74f88864784e | state_budget_ratio | None | None | unavailable |
| 151bacf1f85b74f88864784e | peak_budget_ratio | None | None | unavailable |
| 151bacf1f85b74f88864784e | wall_budget_ratio | None | None | unavailable |
| 330479ee3f94e169b8496e0b | revision_latest | None | None | unavailable |
| 330479ee3f94e169b8496e0b | old_alias_reappearance | None | None | unavailable |
| 330479ee3f94e169b8496e0b | revision_semantic | None | None | unavailable |
| 330479ee3f94e169b8496e0b | unseen_1000 | None | None | unavailable |
| 330479ee3f94e169b8496e0b | outside_change_1000_100 | None | None | unavailable |
| 330479ee3f94e169b8496e0b | retention_change | None | None | unavailable |
| 330479ee3f94e169b8496e0b | es_change | None | None | unavailable |
| 330479ee3f94e169b8496e0b | ls_change | None | None | unavailable |
| 330479ee3f94e169b8496e0b | state_budget_ratio | None | None | unavailable |
| 330479ee3f94e169b8496e0b | peak_budget_ratio | None | None | unavailable |
| 330479ee3f94e169b8496e0b | wall_budget_ratio | None | None | unavailable |
| e4019672011694d495923c6f | revision_latest | None | None | unavailable |
| e4019672011694d495923c6f | old_alias_reappearance | None | None | unavailable |
| e4019672011694d495923c6f | revision_semantic | None | None | unavailable |
| e4019672011694d495923c6f | unseen_1000 | None | None | unavailable |
| e4019672011694d495923c6f | outside_change_1000_100 | None | None | unavailable |
| e4019672011694d495923c6f | retention_change | None | None | unavailable |
| e4019672011694d495923c6f | es_change | None | None | unavailable |
| e4019672011694d495923c6f | ls_change | None | None | unavailable |
| e4019672011694d495923c6f | state_budget_ratio | None | None | unavailable |
| e4019672011694d495923c6f | peak_budget_ratio | None | None | unavailable |
| e4019672011694d495923c6f | wall_budget_ratio | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | revision_latest | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | old_alias_reappearance | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | revision_semantic | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | unseen_1000 | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | outside_change_1000_100 | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | retention_change | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | es_change | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | ls_change | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | state_budget_ratio | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | peak_budget_ratio | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | wall_budget_ratio | None | None | unavailable |
| 70aacd394ef41b887377260a | revision_latest | None | None | unavailable |
| 70aacd394ef41b887377260a | old_alias_reappearance | None | None | unavailable |
| 70aacd394ef41b887377260a | revision_semantic | None | None | unavailable |
| 70aacd394ef41b887377260a | unseen_1000 | None | None | unavailable |
| 70aacd394ef41b887377260a | outside_change_1000_100 | None | None | unavailable |
| 70aacd394ef41b887377260a | retention_change | None | None | unavailable |
| 70aacd394ef41b887377260a | es_change | None | None | unavailable |
| 70aacd394ef41b887377260a | ls_change | None | None | unavailable |
| 70aacd394ef41b887377260a | state_budget_ratio | None | None | unavailable |
| 70aacd394ef41b887377260a | peak_budget_ratio | None | None | unavailable |
| 70aacd394ef41b887377260a | wall_budget_ratio | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | revision_latest | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | old_alias_reappearance | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | revision_semantic | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | unseen_1000 | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | outside_change_1000_100 | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | retention_change | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | es_change | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | ls_change | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | state_budget_ratio | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | peak_budget_ratio | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | wall_budget_ratio | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | revision_latest | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | old_alias_reappearance | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | revision_semantic | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | unseen_1000 | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | outside_change_1000_100 | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | retention_change | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | es_change | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | ls_change | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | state_budget_ratio | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | peak_budget_ratio | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | wall_budget_ratio | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | revision_latest | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | old_alias_reappearance | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | revision_semantic | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | unseen_1000 | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | outside_change_1000_100 | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | retention_change | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | es_change | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | ls_change | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | state_budget_ratio | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | peak_budget_ratio | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | wall_budget_ratio | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | revision_latest | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | old_alias_reappearance | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | revision_semantic | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | unseen_1000 | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | outside_change_1000_100 | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | retention_change | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | es_change | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | ls_change | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | state_budget_ratio | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | peak_budget_ratio | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | wall_budget_ratio | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | revision_latest | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | old_alias_reappearance | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | revision_semantic | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | unseen_1000 | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | outside_change_1000_100 | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | retention_change | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | es_change | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | ls_change | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | state_budget_ratio | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | peak_budget_ratio | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | wall_budget_ratio | None | None | unavailable |
| d62c99156470a7900dc43bc6 | revision_latest | None | None | unavailable |
| d62c99156470a7900dc43bc6 | old_alias_reappearance | None | None | unavailable |
| d62c99156470a7900dc43bc6 | revision_semantic | None | None | unavailable |
| d62c99156470a7900dc43bc6 | unseen_1000 | None | None | unavailable |
| d62c99156470a7900dc43bc6 | outside_change_1000_100 | None | None | unavailable |
| d62c99156470a7900dc43bc6 | retention_change | None | None | unavailable |
| d62c99156470a7900dc43bc6 | es_change | None | None | unavailable |
| d62c99156470a7900dc43bc6 | ls_change | None | None | unavailable |
| d62c99156470a7900dc43bc6 | state_budget_ratio | None | None | unavailable |
| d62c99156470a7900dc43bc6 | peak_budget_ratio | None | None | unavailable |
| d62c99156470a7900dc43bc6 | wall_budget_ratio | None | None | unavailable |
| fa0defe230fa592c6e1395ce | revision_latest | None | None | unavailable |
| fa0defe230fa592c6e1395ce | old_alias_reappearance | None | None | unavailable |
| fa0defe230fa592c6e1395ce | revision_semantic | None | None | unavailable |
| fa0defe230fa592c6e1395ce | unseen_1000 | None | None | unavailable |
| fa0defe230fa592c6e1395ce | outside_change_1000_100 | None | None | unavailable |
| fa0defe230fa592c6e1395ce | retention_change | None | None | unavailable |
| fa0defe230fa592c6e1395ce | es_change | None | None | unavailable |
| fa0defe230fa592c6e1395ce | ls_change | None | None | unavailable |
| fa0defe230fa592c6e1395ce | state_budget_ratio | None | None | unavailable |
| fa0defe230fa592c6e1395ce | peak_budget_ratio | None | None | unavailable |
| fa0defe230fa592c6e1395ce | wall_budget_ratio | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | revision_latest | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | old_alias_reappearance | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | revision_semantic | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | unseen_1000 | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | outside_change_1000_100 | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | retention_change | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | es_change | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | ls_change | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | state_budget_ratio | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | peak_budget_ratio | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | wall_budget_ratio | None | None | unavailable |
| d059ce23baa1380031ffc8cb | revision_latest | None | None | unavailable |
| d059ce23baa1380031ffc8cb | old_alias_reappearance | None | None | unavailable |
| d059ce23baa1380031ffc8cb | revision_semantic | None | None | unavailable |
| d059ce23baa1380031ffc8cb | unseen_1000 | None | None | unavailable |
| d059ce23baa1380031ffc8cb | outside_change_1000_100 | None | None | unavailable |
| d059ce23baa1380031ffc8cb | retention_change | None | None | unavailable |
| d059ce23baa1380031ffc8cb | es_change | None | None | unavailable |
| d059ce23baa1380031ffc8cb | ls_change | None | None | unavailable |
| d059ce23baa1380031ffc8cb | state_budget_ratio | None | None | unavailable |
| d059ce23baa1380031ffc8cb | peak_budget_ratio | None | None | unavailable |
| d059ce23baa1380031ffc8cb | wall_budget_ratio | None | None | unavailable |
| 058509628604e5ca4527273b | revision_latest | None | None | unavailable |
| 058509628604e5ca4527273b | old_alias_reappearance | None | None | unavailable |
| 058509628604e5ca4527273b | revision_semantic | None | None | unavailable |
| 058509628604e5ca4527273b | unseen_1000 | None | None | unavailable |
| 058509628604e5ca4527273b | outside_change_1000_100 | None | None | unavailable |
| 058509628604e5ca4527273b | retention_change | None | None | unavailable |
| 058509628604e5ca4527273b | es_change | None | None | unavailable |
| 058509628604e5ca4527273b | ls_change | None | None | unavailable |
| 058509628604e5ca4527273b | state_budget_ratio | None | None | unavailable |
| 058509628604e5ca4527273b | peak_budget_ratio | None | None | unavailable |
| 058509628604e5ca4527273b | wall_budget_ratio | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | revision_latest | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | old_alias_reappearance | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | revision_semantic | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | unseen_1000 | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | outside_change_1000_100 | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | retention_change | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | es_change | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | ls_change | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | state_budget_ratio | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | peak_budget_ratio | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | wall_budget_ratio | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | revision_latest | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | old_alias_reappearance | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | revision_semantic | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | unseen_1000 | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | outside_change_1000_100 | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | retention_change | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | es_change | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | ls_change | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | state_budget_ratio | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | peak_budget_ratio | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | wall_budget_ratio | None | None | unavailable |
| 789321f88cd80b79c41108d3 | revision_latest | None | None | unavailable |
| 789321f88cd80b79c41108d3 | old_alias_reappearance | None | None | unavailable |
| 789321f88cd80b79c41108d3 | revision_semantic | None | None | unavailable |
| 789321f88cd80b79c41108d3 | unseen_1000 | None | None | unavailable |
| 789321f88cd80b79c41108d3 | outside_change_1000_100 | None | None | unavailable |
| 789321f88cd80b79c41108d3 | retention_change | None | None | unavailable |
| 789321f88cd80b79c41108d3 | es_change | None | None | unavailable |
| 789321f88cd80b79c41108d3 | ls_change | None | None | unavailable |
| 789321f88cd80b79c41108d3 | state_budget_ratio | None | None | unavailable |
| 789321f88cd80b79c41108d3 | peak_budget_ratio | None | None | unavailable |
| 789321f88cd80b79c41108d3 | wall_budget_ratio | None | None | unavailable |
| 58f67f71157df294642d7924 | revision_latest | None | None | unavailable |
| 58f67f71157df294642d7924 | old_alias_reappearance | None | None | unavailable |
| 58f67f71157df294642d7924 | revision_semantic | None | None | unavailable |
| 58f67f71157df294642d7924 | unseen_1000 | None | None | unavailable |
| 58f67f71157df294642d7924 | outside_change_1000_100 | None | None | unavailable |
| 58f67f71157df294642d7924 | retention_change | None | None | unavailable |
| 58f67f71157df294642d7924 | es_change | None | None | unavailable |
| 58f67f71157df294642d7924 | ls_change | None | None | unavailable |
| 58f67f71157df294642d7924 | state_budget_ratio | None | None | unavailable |
| 58f67f71157df294642d7924 | peak_budget_ratio | None | None | unavailable |
| 58f67f71157df294642d7924 | wall_budget_ratio | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | revision_latest | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | old_alias_reappearance | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | revision_semantic | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | unseen_1000 | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | outside_change_1000_100 | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | retention_change | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | es_change | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | ls_change | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | state_budget_ratio | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | peak_budget_ratio | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | wall_budget_ratio | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | revision_latest | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | old_alias_reappearance | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | revision_semantic | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | unseen_1000 | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | outside_change_1000_100 | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | retention_change | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | es_change | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | ls_change | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | state_budget_ratio | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | peak_budget_ratio | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | wall_budget_ratio | None | None | unavailable |
| 509562eef48054a3aeac166a | revision_latest | None | None | unavailable |
| 509562eef48054a3aeac166a | old_alias_reappearance | None | None | unavailable |
| 509562eef48054a3aeac166a | revision_semantic | None | None | unavailable |
| 509562eef48054a3aeac166a | unseen_1000 | None | None | unavailable |
| 509562eef48054a3aeac166a | outside_change_1000_100 | None | None | unavailable |
| 509562eef48054a3aeac166a | retention_change | None | None | unavailable |
| 509562eef48054a3aeac166a | es_change | None | None | unavailable |
| 509562eef48054a3aeac166a | ls_change | None | None | unavailable |
| 509562eef48054a3aeac166a | state_budget_ratio | None | None | unavailable |
| 509562eef48054a3aeac166a | peak_budget_ratio | None | None | unavailable |
| 509562eef48054a3aeac166a | wall_budget_ratio | None | None | unavailable |
| 8515821d35005362bf80ca86 | revision_latest | None | None | unavailable |
| 8515821d35005362bf80ca86 | old_alias_reappearance | None | None | unavailable |
| 8515821d35005362bf80ca86 | revision_semantic | None | None | unavailable |
| 8515821d35005362bf80ca86 | unseen_1000 | None | None | unavailable |
| 8515821d35005362bf80ca86 | outside_change_1000_100 | None | None | unavailable |
| 8515821d35005362bf80ca86 | retention_change | None | None | unavailable |
| 8515821d35005362bf80ca86 | es_change | None | None | unavailable |
| 8515821d35005362bf80ca86 | ls_change | None | None | unavailable |
| 8515821d35005362bf80ca86 | state_budget_ratio | None | None | unavailable |
| 8515821d35005362bf80ca86 | peak_budget_ratio | None | None | unavailable |
| 8515821d35005362bf80ca86 | wall_budget_ratio | None | None | unavailable |
| ce81522f547c386fa9c08c2b | revision_latest | None | None | unavailable |
| ce81522f547c386fa9c08c2b | old_alias_reappearance | None | None | unavailable |
| ce81522f547c386fa9c08c2b | revision_semantic | None | None | unavailable |
| ce81522f547c386fa9c08c2b | unseen_1000 | None | None | unavailable |
| ce81522f547c386fa9c08c2b | outside_change_1000_100 | None | None | unavailable |
| ce81522f547c386fa9c08c2b | retention_change | None | None | unavailable |
| ce81522f547c386fa9c08c2b | es_change | None | None | unavailable |
| ce81522f547c386fa9c08c2b | ls_change | None | None | unavailable |
| ce81522f547c386fa9c08c2b | state_budget_ratio | None | None | unavailable |
| ce81522f547c386fa9c08c2b | peak_budget_ratio | None | None | unavailable |
| ce81522f547c386fa9c08c2b | wall_budget_ratio | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | revision_latest | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | old_alias_reappearance | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | revision_semantic | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | unseen_1000 | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | outside_change_1000_100 | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | retention_change | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | es_change | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | ls_change | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | state_budget_ratio | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | peak_budget_ratio | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | wall_budget_ratio | None | None | unavailable |
| 90334bd842b032c804251295 | revision_latest | None | None | unavailable |
| 90334bd842b032c804251295 | old_alias_reappearance | None | None | unavailable |
| 90334bd842b032c804251295 | revision_semantic | None | None | unavailable |
| 90334bd842b032c804251295 | unseen_1000 | None | None | unavailable |
| 90334bd842b032c804251295 | outside_change_1000_100 | None | None | unavailable |
| 90334bd842b032c804251295 | retention_change | None | None | unavailable |
| 90334bd842b032c804251295 | es_change | None | None | unavailable |
| 90334bd842b032c804251295 | ls_change | None | None | unavailable |
| 90334bd842b032c804251295 | state_budget_ratio | None | None | unavailable |
| 90334bd842b032c804251295 | peak_budget_ratio | None | None | unavailable |
| 90334bd842b032c804251295 | wall_budget_ratio | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | revision_latest | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | old_alias_reappearance | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | revision_semantic | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | unseen_1000 | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | outside_change_1000_100 | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | retention_change | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | es_change | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | ls_change | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | state_budget_ratio | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | peak_budget_ratio | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | wall_budget_ratio | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | revision_latest | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | old_alias_reappearance | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | revision_semantic | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | unseen_1000 | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | outside_change_1000_100 | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | retention_change | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | es_change | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | ls_change | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | state_budget_ratio | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | peak_budget_ratio | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | wall_budget_ratio | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | revision_latest | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | old_alias_reappearance | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | revision_semantic | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | unseen_1000 | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | outside_change_1000_100 | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | retention_change | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | es_change | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | ls_change | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | state_budget_ratio | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | peak_budget_ratio | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | wall_budget_ratio | None | None | unavailable |
| 5605235e2ed700e3724eec66 | revision_latest | None | None | unavailable |
| 5605235e2ed700e3724eec66 | old_alias_reappearance | None | None | unavailable |
| 5605235e2ed700e3724eec66 | revision_semantic | None | None | unavailable |
| 5605235e2ed700e3724eec66 | unseen_1000 | None | None | unavailable |
| 5605235e2ed700e3724eec66 | outside_change_1000_100 | None | None | unavailable |
| 5605235e2ed700e3724eec66 | retention_change | None | None | unavailable |
| 5605235e2ed700e3724eec66 | es_change | None | None | unavailable |
| 5605235e2ed700e3724eec66 | ls_change | None | None | unavailable |
| 5605235e2ed700e3724eec66 | state_budget_ratio | None | None | unavailable |
| 5605235e2ed700e3724eec66 | peak_budget_ratio | None | None | unavailable |
| 5605235e2ed700e3724eec66 | wall_budget_ratio | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | revision_latest | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | old_alias_reappearance | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | revision_semantic | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | unseen_1000 | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | outside_change_1000_100 | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | retention_change | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | es_change | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | ls_change | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | state_budget_ratio | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | peak_budget_ratio | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | wall_budget_ratio | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | revision_latest | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | old_alias_reappearance | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | revision_semantic | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | unseen_1000 | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | outside_change_1000_100 | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | retention_change | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | es_change | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | ls_change | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | state_budget_ratio | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | peak_budget_ratio | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | wall_budget_ratio | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | revision_latest | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | old_alias_reappearance | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | revision_semantic | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | unseen_1000 | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | outside_change_1000_100 | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | retention_change | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | es_change | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | ls_change | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | state_budget_ratio | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | peak_budget_ratio | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | wall_budget_ratio | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | revision_latest | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | old_alias_reappearance | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | revision_semantic | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | unseen_1000 | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | outside_change_1000_100 | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | retention_change | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | es_change | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | ls_change | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | state_budget_ratio | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | peak_budget_ratio | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | wall_budget_ratio | None | None | unavailable |
| 4d261cc6ea3f349110835054 | revision_latest | None | None | unavailable |
| 4d261cc6ea3f349110835054 | old_alias_reappearance | None | None | unavailable |
| 4d261cc6ea3f349110835054 | revision_semantic | None | None | unavailable |
| 4d261cc6ea3f349110835054 | unseen_1000 | None | None | unavailable |
| 4d261cc6ea3f349110835054 | outside_change_1000_100 | None | None | unavailable |
| 4d261cc6ea3f349110835054 | retention_change | None | None | unavailable |
| 4d261cc6ea3f349110835054 | es_change | None | None | unavailable |
| 4d261cc6ea3f349110835054 | ls_change | None | None | unavailable |
| 4d261cc6ea3f349110835054 | state_budget_ratio | None | None | unavailable |
| 4d261cc6ea3f349110835054 | peak_budget_ratio | None | None | unavailable |
| 4d261cc6ea3f349110835054 | wall_budget_ratio | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | revision_latest | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | old_alias_reappearance | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | revision_semantic | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | unseen_1000 | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | outside_change_1000_100 | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | retention_change | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | es_change | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | ls_change | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | state_budget_ratio | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | peak_budget_ratio | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | wall_budget_ratio | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | revision_latest | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | old_alias_reappearance | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | revision_semantic | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | unseen_1000 | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | outside_change_1000_100 | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | retention_change | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | es_change | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | ls_change | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | state_budget_ratio | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | peak_budget_ratio | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | wall_budget_ratio | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | revision_latest | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | old_alias_reappearance | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | revision_semantic | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | unseen_1000 | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | outside_change_1000_100 | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | retention_change | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | es_change | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | ls_change | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | state_budget_ratio | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | peak_budget_ratio | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | wall_budget_ratio | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | revision_latest | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | old_alias_reappearance | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | revision_semantic | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | unseen_1000 | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | outside_change_1000_100 | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | retention_change | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | es_change | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | ls_change | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | state_budget_ratio | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | peak_budget_ratio | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | wall_budget_ratio | None | None | unavailable |
| 875c812006d2f01a6a67e48b | revision_latest | None | None | unavailable |
| 875c812006d2f01a6a67e48b | old_alias_reappearance | None | None | unavailable |
| 875c812006d2f01a6a67e48b | revision_semantic | None | None | unavailable |
| 875c812006d2f01a6a67e48b | unseen_1000 | None | None | unavailable |
| 875c812006d2f01a6a67e48b | outside_change_1000_100 | None | None | unavailable |
| 875c812006d2f01a6a67e48b | retention_change | None | None | unavailable |
| 875c812006d2f01a6a67e48b | es_change | None | None | unavailable |
| 875c812006d2f01a6a67e48b | ls_change | None | None | unavailable |
| 875c812006d2f01a6a67e48b | state_budget_ratio | None | None | unavailable |
| 875c812006d2f01a6a67e48b | peak_budget_ratio | None | None | unavailable |
| 875c812006d2f01a6a67e48b | wall_budget_ratio | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | revision_latest | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | old_alias_reappearance | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | revision_semantic | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | unseen_1000 | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | outside_change_1000_100 | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | retention_change | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | es_change | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | ls_change | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | state_budget_ratio | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | peak_budget_ratio | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | wall_budget_ratio | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | revision_latest | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | old_alias_reappearance | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | revision_semantic | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | unseen_1000 | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | outside_change_1000_100 | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | retention_change | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | es_change | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | ls_change | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | state_budget_ratio | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | peak_budget_ratio | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | wall_budget_ratio | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | revision_latest | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | old_alias_reappearance | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | revision_semantic | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | unseen_1000 | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | outside_change_1000_100 | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | retention_change | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | es_change | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | ls_change | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | state_budget_ratio | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | peak_budget_ratio | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | wall_budget_ratio | None | None | unavailable |
| 722a6e81428fe90b28522578 | revision_latest | None | None | unavailable |
| 722a6e81428fe90b28522578 | old_alias_reappearance | None | None | unavailable |
| 722a6e81428fe90b28522578 | revision_semantic | None | None | unavailable |
| 722a6e81428fe90b28522578 | unseen_1000 | None | None | unavailable |
| 722a6e81428fe90b28522578 | outside_change_1000_100 | None | None | unavailable |
| 722a6e81428fe90b28522578 | retention_change | None | None | unavailable |
| 722a6e81428fe90b28522578 | es_change | None | None | unavailable |
| 722a6e81428fe90b28522578 | ls_change | None | None | unavailable |
| 722a6e81428fe90b28522578 | state_budget_ratio | None | None | unavailable |
| 722a6e81428fe90b28522578 | peak_budget_ratio | None | None | unavailable |
| 722a6e81428fe90b28522578 | wall_budget_ratio | None | None | unavailable |
| 64474eaad780d3d0f127b333 | revision_latest | None | None | unavailable |
| 64474eaad780d3d0f127b333 | old_alias_reappearance | None | None | unavailable |
| 64474eaad780d3d0f127b333 | revision_semantic | None | None | unavailable |
| 64474eaad780d3d0f127b333 | unseen_1000 | None | None | unavailable |
| 64474eaad780d3d0f127b333 | outside_change_1000_100 | None | None | unavailable |
| 64474eaad780d3d0f127b333 | retention_change | None | None | unavailable |
| 64474eaad780d3d0f127b333 | es_change | None | None | unavailable |
| 64474eaad780d3d0f127b333 | ls_change | None | None | unavailable |
| 64474eaad780d3d0f127b333 | state_budget_ratio | None | None | unavailable |
| 64474eaad780d3d0f127b333 | peak_budget_ratio | None | None | unavailable |
| 64474eaad780d3d0f127b333 | wall_budget_ratio | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | revision_latest | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | old_alias_reappearance | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | revision_semantic | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | unseen_1000 | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | outside_change_1000_100 | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | retention_change | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | es_change | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | ls_change | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | state_budget_ratio | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | peak_budget_ratio | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | wall_budget_ratio | None | None | unavailable |
| 203da3ce23c2826be75941f8 | revision_latest | None | None | unavailable |
| 203da3ce23c2826be75941f8 | old_alias_reappearance | None | None | unavailable |
| 203da3ce23c2826be75941f8 | revision_semantic | None | None | unavailable |
| 203da3ce23c2826be75941f8 | unseen_1000 | None | None | unavailable |
| 203da3ce23c2826be75941f8 | outside_change_1000_100 | None | None | unavailable |
| 203da3ce23c2826be75941f8 | retention_change | None | None | unavailable |
| 203da3ce23c2826be75941f8 | es_change | None | None | unavailable |
| 203da3ce23c2826be75941f8 | ls_change | None | None | unavailable |
| 203da3ce23c2826be75941f8 | state_budget_ratio | None | None | unavailable |
| 203da3ce23c2826be75941f8 | peak_budget_ratio | None | None | unavailable |
| 203da3ce23c2826be75941f8 | wall_budget_ratio | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | revision_latest | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | old_alias_reappearance | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | revision_semantic | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | unseen_1000 | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | outside_change_1000_100 | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | retention_change | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | es_change | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | ls_change | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | state_budget_ratio | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | peak_budget_ratio | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | wall_budget_ratio | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | revision_latest | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | old_alias_reappearance | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | revision_semantic | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | unseen_1000 | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | outside_change_1000_100 | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | retention_change | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | es_change | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | ls_change | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | state_budget_ratio | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | peak_budget_ratio | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | wall_budget_ratio | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | revision_latest | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | old_alias_reappearance | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | revision_semantic | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | unseen_1000 | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | outside_change_1000_100 | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | retention_change | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | es_change | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | ls_change | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | state_budget_ratio | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | peak_budget_ratio | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | wall_budget_ratio | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | revision_latest | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | old_alias_reappearance | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | revision_semantic | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | unseen_1000 | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | outside_change_1000_100 | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | retention_change | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | es_change | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | ls_change | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | state_budget_ratio | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | peak_budget_ratio | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | wall_budget_ratio | None | None | unavailable |
| 64083f876c4b931fac1666ac | revision_latest | None | None | unavailable |
| 64083f876c4b931fac1666ac | old_alias_reappearance | None | None | unavailable |
| 64083f876c4b931fac1666ac | revision_semantic | None | None | unavailable |
| 64083f876c4b931fac1666ac | unseen_1000 | None | None | unavailable |
| 64083f876c4b931fac1666ac | outside_change_1000_100 | None | None | unavailable |
| 64083f876c4b931fac1666ac | retention_change | None | None | unavailable |
| 64083f876c4b931fac1666ac | es_change | None | None | unavailable |
| 64083f876c4b931fac1666ac | ls_change | None | None | unavailable |
| 64083f876c4b931fac1666ac | state_budget_ratio | None | None | unavailable |
| 64083f876c4b931fac1666ac | peak_budget_ratio | None | None | unavailable |
| 64083f876c4b931fac1666ac | wall_budget_ratio | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | revision_latest | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | old_alias_reappearance | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | revision_semantic | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | unseen_1000 | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | outside_change_1000_100 | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | retention_change | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | es_change | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | ls_change | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | state_budget_ratio | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | peak_budget_ratio | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | wall_budget_ratio | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | revision_latest | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | old_alias_reappearance | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | revision_semantic | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | unseen_1000 | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | outside_change_1000_100 | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | retention_change | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | es_change | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | ls_change | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | state_budget_ratio | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | peak_budget_ratio | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | wall_budget_ratio | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | revision_latest | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | old_alias_reappearance | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | revision_semantic | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | unseen_1000 | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | outside_change_1000_100 | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | retention_change | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | es_change | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | ls_change | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | state_budget_ratio | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | peak_budget_ratio | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | wall_budget_ratio | None | None | unavailable |
| 62b13a164930d43ad696b359 | revision_latest | None | None | unavailable |
| 62b13a164930d43ad696b359 | old_alias_reappearance | None | None | unavailable |
| 62b13a164930d43ad696b359 | revision_semantic | None | None | unavailable |
| 62b13a164930d43ad696b359 | unseen_1000 | None | None | unavailable |
| 62b13a164930d43ad696b359 | outside_change_1000_100 | None | None | unavailable |
| 62b13a164930d43ad696b359 | retention_change | None | None | unavailable |
| 62b13a164930d43ad696b359 | es_change | None | None | unavailable |
| 62b13a164930d43ad696b359 | ls_change | None | None | unavailable |
| 62b13a164930d43ad696b359 | state_budget_ratio | None | None | unavailable |
| 62b13a164930d43ad696b359 | peak_budget_ratio | None | None | unavailable |
| 62b13a164930d43ad696b359 | wall_budget_ratio | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | revision_latest | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | old_alias_reappearance | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | revision_semantic | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | unseen_1000 | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | outside_change_1000_100 | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | retention_change | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | es_change | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | ls_change | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | state_budget_ratio | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | peak_budget_ratio | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | wall_budget_ratio | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | revision_latest | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | old_alias_reappearance | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | revision_semantic | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | unseen_1000 | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | outside_change_1000_100 | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | retention_change | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | es_change | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | ls_change | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | state_budget_ratio | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | peak_budget_ratio | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | wall_budget_ratio | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | revision_latest | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | old_alias_reappearance | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | revision_semantic | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | unseen_1000 | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | outside_change_1000_100 | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | retention_change | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | es_change | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | ls_change | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | state_budget_ratio | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | peak_budget_ratio | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | wall_budget_ratio | None | None | unavailable |
| 46cc8880d731fbee52076712 | revision_latest | None | None | unavailable |
| 46cc8880d731fbee52076712 | old_alias_reappearance | None | None | unavailable |
| 46cc8880d731fbee52076712 | revision_semantic | None | None | unavailable |
| 46cc8880d731fbee52076712 | unseen_1000 | None | None | unavailable |
| 46cc8880d731fbee52076712 | outside_change_1000_100 | None | None | unavailable |
| 46cc8880d731fbee52076712 | retention_change | None | None | unavailable |
| 46cc8880d731fbee52076712 | es_change | None | None | unavailable |
| 46cc8880d731fbee52076712 | ls_change | None | None | unavailable |
| 46cc8880d731fbee52076712 | state_budget_ratio | None | None | unavailable |
| 46cc8880d731fbee52076712 | peak_budget_ratio | None | None | unavailable |
| 46cc8880d731fbee52076712 | wall_budget_ratio | None | None | unavailable |
| 45c033c5bc044beea6f5562c | revision_latest | None | None | unavailable |
| 45c033c5bc044beea6f5562c | old_alias_reappearance | None | None | unavailable |
| 45c033c5bc044beea6f5562c | revision_semantic | None | None | unavailable |
| 45c033c5bc044beea6f5562c | unseen_1000 | None | None | unavailable |
| 45c033c5bc044beea6f5562c | outside_change_1000_100 | None | None | unavailable |
| 45c033c5bc044beea6f5562c | retention_change | None | None | unavailable |
| 45c033c5bc044beea6f5562c | es_change | None | None | unavailable |
| 45c033c5bc044beea6f5562c | ls_change | None | None | unavailable |
| 45c033c5bc044beea6f5562c | state_budget_ratio | None | None | unavailable |
| 45c033c5bc044beea6f5562c | peak_budget_ratio | None | None | unavailable |
| 45c033c5bc044beea6f5562c | wall_budget_ratio | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | revision_latest | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | old_alias_reappearance | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | revision_semantic | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | unseen_1000 | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | outside_change_1000_100 | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | retention_change | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | es_change | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | ls_change | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | state_budget_ratio | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | peak_budget_ratio | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | wall_budget_ratio | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | revision_latest | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | old_alias_reappearance | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | revision_semantic | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | unseen_1000 | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | outside_change_1000_100 | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | retention_change | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | es_change | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | ls_change | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | state_budget_ratio | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | peak_budget_ratio | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | wall_budget_ratio | None | None | unavailable |
| fda4c348dac5448fc10fd672 | revision_latest | None | None | unavailable |
| fda4c348dac5448fc10fd672 | old_alias_reappearance | None | None | unavailable |
| fda4c348dac5448fc10fd672 | revision_semantic | None | None | unavailable |
| fda4c348dac5448fc10fd672 | unseen_1000 | None | None | unavailable |
| fda4c348dac5448fc10fd672 | outside_change_1000_100 | None | None | unavailable |
| fda4c348dac5448fc10fd672 | retention_change | None | None | unavailable |
| fda4c348dac5448fc10fd672 | es_change | None | None | unavailable |
| fda4c348dac5448fc10fd672 | ls_change | None | None | unavailable |
| fda4c348dac5448fc10fd672 | state_budget_ratio | None | None | unavailable |
| fda4c348dac5448fc10fd672 | peak_budget_ratio | None | None | unavailable |
| fda4c348dac5448fc10fd672 | wall_budget_ratio | None | None | unavailable |
| 929c713ce993539177ad3985 | revision_latest | None | None | unavailable |
| 929c713ce993539177ad3985 | old_alias_reappearance | None | None | unavailable |
| 929c713ce993539177ad3985 | revision_semantic | None | None | unavailable |
| 929c713ce993539177ad3985 | unseen_1000 | None | None | unavailable |
| 929c713ce993539177ad3985 | outside_change_1000_100 | None | None | unavailable |
| 929c713ce993539177ad3985 | retention_change | None | None | unavailable |
| 929c713ce993539177ad3985 | es_change | None | None | unavailable |
| 929c713ce993539177ad3985 | ls_change | None | None | unavailable |
| 929c713ce993539177ad3985 | state_budget_ratio | None | None | unavailable |
| 929c713ce993539177ad3985 | peak_budget_ratio | None | None | unavailable |
| 929c713ce993539177ad3985 | wall_budget_ratio | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | revision_latest | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | old_alias_reappearance | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | revision_semantic | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | unseen_1000 | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | outside_change_1000_100 | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | retention_change | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | es_change | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | ls_change | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | state_budget_ratio | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | peak_budget_ratio | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | wall_budget_ratio | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | revision_latest | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | old_alias_reappearance | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | revision_semantic | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | unseen_1000 | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | outside_change_1000_100 | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | retention_change | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | es_change | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | ls_change | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | state_budget_ratio | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | peak_budget_ratio | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | wall_budget_ratio | None | None | unavailable |

Actual terminal occupancy (secondary descriptive; no threshold or pass decision):

| Cell | Required actual records | Fires / planned | Rate | Wilson 95% | Paired change from actual 100 | Availability |
|---|---:|---|---|---|---|---|
| 61348508e40d54351613ab14 | 1000 | 9 / 100 | 0.09 | {'lower': 0.04807254000256516, 'upper': 0.1622621285271631, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 88af67fa5945b642e8ba7974 | 1000 | 9 / 100 | 0.09 | {'lower': 0.04807254000256516, 'upper': 0.1622621285271631, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.02 | complete |
| 915f97b05f3fa2a81de09cdf | 1000 | 9 / 100 | 0.09 | {'lower': 0.04807254000256516, 'upper': 0.1622621285271631, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | -0.04 | complete |
| 4aa4849ba414edab2504f56b | 1000 | 9 / 100 | 0.09 | {'lower': 0.04807254000256516, 'upper': 0.1622621285271631, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.05 | complete |
| 9ebc93cc7912bd5d1c929418 | 1000 | 9 / 100 | 0.09 | {'lower': 0.04807254000256516, 'upper': 0.1622621285271631, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | -0.02 | complete |
| ce0d0ffc2a58a60e27c460d9 | 1000 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 95dfb24c6361b2d38dd60e9b | 1000 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 6d0915056b1e76d8ee8795ff | 1000 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 7c9675a69d832a772070cb2d | 1000 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 95016bc16e89cfcccccc40b8 | 1000 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 43925e53c31860219a85ef90 | 300 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| c29ee18fb21ba6b387ede6e8 | 300 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 54879da4dcdb0f106f98080a | 300 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 78ebbc03946239c1d637154c | 300 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| b1d1e53944241333ec5603d4 | 300 | 0 / 100 | 0.0 | {'lower': 3.469446951953614e-18, 'upper': 0.03699349820698568, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| f3dbf1a3d5860a628e7d68ef | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| be44dfb501724b72adcbd747 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 5263d61e569d7cb4ceb4e617 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 81b1e9cb4e216a6cd1cd565a | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| deb5f473d9ca2ed544926204 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 0b6ade77641a02c1c85574b0 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.06 | complete |
| ee67c592789829e7dd808ede | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.09 | complete |
| 8be432675ed4dc57f9108bd4 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.07 | complete |
| 78928f2782d91d888ef24d52 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.07 | complete |
| de785feed05c9f4c2a9e9273 | 1000 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.15 | complete |
| de0b9612418e6d573ed77679 | 300 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| be37e2a1ff4a079e56efe268 | 300 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.01 | complete |
| 1e6b766c4139230c18547234 | 300 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.01 | complete |
| c0a54c5fbf1ce7776efc983e | 300 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 7499c19b813dcada2c67ae39 | 300 | 100 / 100 | 1.0 | {'lower': 0.9630065017930143, 'upper': 1.0, 'confidence': 0.95, 'interpretation': 'descriptive binomial reference; fixed development data/selection and dependent prompts limit population inference'} | 0.0 | complete |
| 39c7fd4929721e8dcba56b94 | 1000 | None / 100 | None | None | None | unavailable |
| b887b1046cd563d990765e01 | 1000 | None / 100 | None | None | None | unavailable |
| 435235a6719279d1cc87ad66 | 1000 | None / 100 | None | None | None | unavailable |
| aaed1cf9e8ce7cf1cf3749fa | 1000 | None / 100 | None | None | None | unavailable |
| 92a5ef6855124ffc5a8d6163 | 1000 | None / 100 | None | None | None | unavailable |
| baa601113af675024e73bc30 | 1000 | None / 100 | None | None | None | unavailable |
| b6b271f3383f85fb19e49836 | 1000 | None / 100 | None | None | None | unavailable |
| 6c0124a2d35b8b4bf8d2a321 | 1000 | None / 100 | None | None | None | unavailable |
| 37c2ba2be995719ac8972cf1 | 1000 | None / 100 | None | None | None | unavailable |
| d93ed5de9d4401cb3345c7bd | 1000 | None / 100 | None | None | None | unavailable |
| c2f9d3102987f746f4f31b8d | 300 | None / 100 | None | None | None | unavailable |
| a23ae9063b37c21cfe657d47 | 300 | None / 100 | None | None | None | unavailable |
| 5a6f61e06de0bca53b4a7377 | 300 | None / 100 | None | None | None | unavailable |
| 03426d6e61fb6b41145c5d8e | 300 | None / 100 | None | None | None | unavailable |
| 19f5d8535235334ffe1595e8 | 300 | None / 100 | None | None | None | unavailable |
| 6b089d284c00a4418a1d3af4 | 1000 | None / 100 | None | None | None | unavailable |
| 47dac9d968ffe594faac0a14 | 1000 | None / 100 | None | None | None | unavailable |
| 4eda9e6155b2755508e13091 | 1000 | None / 100 | None | None | None | unavailable |
| ab774e229a65298fdc117c96 | 1000 | None / 100 | None | None | None | unavailable |
| b4e7dc307a1f895a8fec997a | 1000 | None / 100 | None | None | None | unavailable |
| 826332f387bd487a045d412f | 1000 | None / 100 | None | None | None | unavailable |
| 14d45f0e87126104057518af | 1000 | None / 100 | None | None | None | unavailable |
| 960d0adeb6cacfcfce93d546 | 1000 | None / 100 | None | None | None | unavailable |
| 6840a40e6e5c90bdc40b89b0 | 1000 | None / 100 | None | None | None | unavailable |
| 42ba32e4f07423bee03296b3 | 1000 | None / 100 | None | None | None | unavailable |
| 19964c4e7f737707baad94a5 | 300 | None / 100 | None | None | None | unavailable |
| 40ec11c9694b4265a013c682 | 300 | None / 100 | None | None | None | unavailable |
| f0642100f6eb9cd77e92f439 | 300 | None / 100 | None | None | None | unavailable |
| b7ff3139c3f3eeb3ff7e9c80 | 300 | None / 100 | None | None | None | unavailable |
| 1833a410c9e8704f6a379114 | 300 | None / 100 | None | None | None | unavailable |
| 82606602ae475e73eb4401f9 | 1000 | None / 100 | None | None | None | unavailable |
| 2172052824abd70e8135366f | 1000 | None / 100 | None | None | None | unavailable |
| 5c394f4861164c1d5b31de4c | 1000 | None / 100 | None | None | None | unavailable |
| c9d2325e783e57ac5eafa34d | 1000 | None / 100 | None | None | None | unavailable |
| 3fdc7c12d6d583f46608eac6 | 1000 | None / 100 | None | None | None | unavailable |
| a7d551c093fd3333314813a5 | 1000 | None / 100 | None | None | None | unavailable |
| c402523c2460a62d6040ddd0 | 1000 | None / 100 | None | None | None | unavailable |
| b103826472ba7653cd8fd13a | 1000 | None / 100 | None | None | None | unavailable |
| 525ad705ad7008ed3ea378eb | 1000 | None / 100 | None | None | None | unavailable |
| 8a4bcb6e358e98c523b0d0c3 | 1000 | None / 100 | None | None | None | unavailable |
| 144f77ff21860a8a089a8080 | 300 | None / 100 | None | None | None | unavailable |
| 3c3212c0cad597bafe0d5782 | 300 | None / 100 | None | None | None | unavailable |
| 5d467b73f60b99b3d07f8c02 | 300 | None / 100 | None | None | None | unavailable |
| a81b13b1b22e0bfe489daaa0 | 300 | None / 100 | None | None | None | unavailable |
| 1aff34869825a76d502d92a3 | 300 | None / 100 | None | None | None | unavailable |
| 3b70d3d44297fc1197610228 | 1000 | None / 100 | None | None | None | unavailable |
| 84bae28d26e5f5a3e555b601 | 1000 | None / 100 | None | None | None | unavailable |
| 07b9bad1f676110cb8bae7df | 1000 | None / 100 | None | None | None | unavailable |
| 0ff8a61a760d6836f469629b | 1000 | None / 100 | None | None | None | unavailable |
| 40034291ac69439c82ae1fc3 | 1000 | None / 100 | None | None | None | unavailable |
| 6d8d11dbbbc7b736c6386bca | 1000 | None / 100 | None | None | None | unavailable |
| cefda69ce81ca1253435bac7 | 1000 | None / 100 | None | None | None | unavailable |
| e42cd6f9b5b86feb491512f6 | 1000 | None / 100 | None | None | None | unavailable |
| e0f2bb19e19594c972c0ef15 | 1000 | None / 100 | None | None | None | unavailable |
| 0d4d946cb9ff28b7e6af3c4d | 1000 | None / 100 | None | None | None | unavailable |
| 9179614db32d3fd8b437475b | 300 | None / 100 | None | None | None | unavailable |
| e146662ae0ab343921979246 | 300 | None / 100 | None | None | None | unavailable |
| c770960b77b2d9f6304f1a34 | 300 | None / 100 | None | None | None | unavailable |
| d49ef9c7980da822326bc6ac | 300 | None / 100 | None | None | None | unavailable |
| eef5c3dc3fc8291d75199816 | 300 | None / 100 | None | None | None | unavailable |
| 0417f598d89548e3200a3fe4 | 1000 | None / 100 | None | None | None | unavailable |
| 12a9c0da62781d521da26cd5 | 1000 | None / 100 | None | None | None | unavailable |
| c2a67190edb39398491bd651 | 1000 | None / 100 | None | None | None | unavailable |
| 58cc3599099d7ab60e5d1413 | 1000 | None / 100 | None | None | None | unavailable |
| 4206e18c23b43bb312e045e6 | 1000 | None / 100 | None | None | None | unavailable |
| fa46e16c8436f7ea4a5c3f06 | 1000 | None / 100 | None | None | None | unavailable |
| 162686f6303fe986619d236d | 1000 | None / 100 | None | None | None | unavailable |
| 029ecd260f3e085063714d3f | 1000 | None / 100 | None | None | None | unavailable |
| 7197775fb7f97a465fd3310e | 1000 | None / 100 | None | None | None | unavailable |
| 6de7e97b6cb167d048dc31ba | 1000 | None / 100 | None | None | None | unavailable |
| fcd702d12d5d6bfae824379b | 300 | None / 100 | None | None | None | unavailable |
| 9a1d038b95f534b43185c7fc | 300 | None / 100 | None | None | None | unavailable |
| dfc9c9b480e482911c457e07 | 300 | None / 100 | None | None | None | unavailable |
| 34fce88c919bcae6410e4d94 | 300 | None / 100 | None | None | None | unavailable |
| 7a39ae192fb0b1038c651f64 | 300 | None / 100 | None | None | None | unavailable |
| 13465e8d0dc3824fced8e891 | 1000 | None / 100 | None | None | None | unavailable |
| 24840672cf1682dd450fdcd2 | 1000 | None / 100 | None | None | None | unavailable |
| 12a6e3e550a7939c6d79349d | 1000 | None / 100 | None | None | None | unavailable |
| fa5b51891eb78dc707e6471f | 1000 | None / 100 | None | None | None | unavailable |
| 861810fbdd6ebe7502383382 | 1000 | None / 100 | None | None | None | unavailable |
| 6ed2474713b3a311b4ec6b08 | 1000 | None / 100 | None | None | None | unavailable |
| f939f211b98675ac7c2d951f | 1000 | None / 100 | None | None | None | unavailable |
| 19b5e9b462930c6f50f2e2f6 | 1000 | None / 100 | None | None | None | unavailable |
| b14576e3d752f467db2abf18 | 1000 | None / 100 | None | None | None | unavailable |
| da9f71bdb9a8981dac078e6c | 1000 | None / 100 | None | None | None | unavailable |
| 9e98169ae668b50d60694317 | 300 | None / 100 | None | None | None | unavailable |
| ff570734d7837a1ba9e77528 | 300 | None / 100 | None | None | None | unavailable |
| 4fd2bc51397502cb1c085b5c | 300 | None / 100 | None | None | None | unavailable |
| c0e77c94b06dd3464838be93 | 300 | None / 100 | None | None | None | unavailable |
| 4c700c665ce70ca41e4569dd | 300 | None / 100 | None | None | None | unavailable |
| dc17fc3637068157dba0207d | 1000 | None / 100 | None | None | None | unavailable |
| 727b32ab9723cb9feba71636 | 1000 | None / 100 | None | None | None | unavailable |
| a02980b0886a222f8e2f58e8 | 1000 | None / 100 | None | None | None | unavailable |
| 9aeb330f6c7e29c85ee56da0 | 1000 | None / 100 | None | None | None | unavailable |
| 0e0ee9a35e1116f7dafb423d | 1000 | None / 100 | None | None | None | unavailable |
| 862cd40c359e48e5a7998e3f | 1000 | None / 100 | None | None | None | unavailable |
| 89b258fddde381d9a09429d9 | 1000 | None / 100 | None | None | None | unavailable |
| 090d1237381f4ee02fcbd05d | 1000 | None / 100 | None | None | None | unavailable |
| 6e95ec72097ffded952889d6 | 1000 | None / 100 | None | None | None | unavailable |
| c8ce51b334cc3e42a623be6c | 1000 | None / 100 | None | None | None | unavailable |
| cf6bd4a623aa24871f74d136 | 300 | None / 100 | None | None | None | unavailable |
| 519b30353f979e8028ed03e1 | 300 | None / 100 | None | None | None | unavailable |
| 89182e81a187807d2772cade | 300 | None / 100 | None | None | None | unavailable |
| 9ad3399cfc13f1297d17423d | 300 | None / 100 | None | None | None | unavailable |
| 046aa51d028b84dde8981351 | 300 | None / 100 | None | None | None | unavailable |
| c897cd3d2a3b35bfe999e87e | 1000 | None / 100 | None | None | None | unavailable |
| 1689630f5ad581d9fcfc483e | 1000 | None / 100 | None | None | None | unavailable |
| c1c03ed850a40df57da8628a | 1000 | None / 100 | None | None | None | unavailable |
| d1690029ea53ae03b3705536 | 1000 | None / 100 | None | None | None | unavailable |
| a921f9ab5443f978e56d2390 | 1000 | None / 100 | None | None | None | unavailable |
| a86da75220343c5560c45373 | 1000 | None / 100 | None | None | None | unavailable |
| e7b52c6db370d10a5fd7d891 | 1000 | None / 100 | None | None | None | unavailable |
| 735081421354eaafb893322d | 1000 | None / 100 | None | None | None | unavailable |
| 824f602358ace0fc5cb69271 | 1000 | None / 100 | None | None | None | unavailable |
| 3bc2cef1ca9bab6e4a90e222 | 1000 | None / 100 | None | None | None | unavailable |
| 9c3c7c258bf086523ea6268e | 1000 | None / 100 | None | None | None | unavailable |
| 58879f9745ed479686bd0481 | 1000 | None / 100 | None | None | None | unavailable |
| b6ea6d9e337e3bf6f2eca5d2 | 1000 | None / 100 | None | None | None | unavailable |
| 16037ce355e4a2e9a43a2008 | 1000 | None / 100 | None | None | None | unavailable |
| 4597af8473d8e404f1490c57 | 1000 | None / 100 | None | None | None | unavailable |
| 7c933afa6e2adc84ccb287be | 1000 | None / 100 | None | None | None | unavailable |
| 0998eeed741b887bdb8664af | 1000 | None / 100 | None | None | None | unavailable |
| bb4da95ca8ce5b0b8d3dbe35 | 1000 | None / 100 | None | None | None | unavailable |
| c5f1daa35261cf950172dfa8 | 1000 | None / 100 | None | None | None | unavailable |
| 244f29ba9b89c48d08c257c7 | 1000 | None / 100 | None | None | None | unavailable |
| b8924c056fee6d000f5492d1 | 1000 | None / 100 | None | None | None | unavailable |
| 4944219da107f9ed1daccef5 | 1000 | None / 100 | None | None | None | unavailable |
| ac46789a7ebda9982aebd343 | 1000 | None / 100 | None | None | None | unavailable |
| ccf4e4f1fca14a048eecd38f | 1000 | None / 100 | None | None | None | unavailable |
| 6c9ac68dd90eb2d39d339b6a | 1000 | None / 100 | None | None | None | unavailable |
| 672b5b4a7ea9b83b8668fbe2 | 1000 | None / 100 | None | None | None | unavailable |
| b8f1ca491f4e29db862af920 | 1000 | None / 100 | None | None | None | unavailable |
| 5efb497774b3f4f9ad8e7f7d | 1000 | None / 100 | None | None | None | unavailable |
| 47ee96bcecb134f64286c958 | 1000 | None / 100 | None | None | None | unavailable |
| a18ee644e09c84652cc9582a | 1000 | None / 100 | None | None | None | unavailable |
| 509cd28130eb44d35b27d08a | 1000 | None / 100 | None | None | None | unavailable |
| a8a5ddc06de26a9885f75fe9 | 1000 | None / 100 | None | None | None | unavailable |
| 5f818373c34233809fc57716 | 1000 | None / 100 | None | None | None | unavailable |
| baa8eccee6a4f8c27c11a09c | 1000 | None / 100 | None | None | None | unavailable |
| 2a91e17773f7272dbd36a048 | 1000 | None / 100 | None | None | None | unavailable |
| d0a5df19a69792ac87a703dc | 1000 | None / 100 | None | None | None | unavailable |
| 6d6930dcd4fe737e4d1ef3ed | 1000 | None / 100 | None | None | None | unavailable |
| cf9c6af6097c6d96c9a5a1d3 | 1000 | None / 100 | None | None | None | unavailable |
| 7317081e2468dfeeed3e4cc7 | 1000 | None / 100 | None | None | None | unavailable |
| ed2fff6199cac50f8e3c05d9 | 1000 | None / 100 | None | None | None | unavailable |
| 5d52bba4bd205ffecf96212a | 1000 | None / 100 | None | None | None | unavailable |
| e82412060e54893dc307a45e | 1000 | None / 100 | None | None | None | unavailable |
| b42dfb1e539cb4645127e844 | 1000 | None / 100 | None | None | None | unavailable |
| 2fe9909dbaad17941716efc9 | 1000 | None / 100 | None | None | None | unavailable |
| e45d4b2c01fc48117d5abec8 | 1000 | None / 100 | None | None | None | unavailable |
| 978f353680dde68625399775 | 1000 | None / 100 | None | None | None | unavailable |
| cdc8a1fbbb43d1f1ba93a366 | 1000 | None / 100 | None | None | None | unavailable |
| 3126d7f4d6378f131a26c41d | 1000 | None / 100 | None | None | None | unavailable |
| 48f56fbee8eed89fe5598934 | 1000 | None / 100 | None | None | None | unavailable |
| 18cef3e100afe2f32847ac27 | 1000 | None / 100 | None | None | None | unavailable |
| f67e77a0b124376f29b78302 | 1000 | None / 100 | None | None | None | unavailable |
| 7ab5a2ba2ca2072d49c86da9 | 1000 | None / 100 | None | None | None | unavailable |
| ea3b0653f085cf535854d1b8 | 1000 | None / 100 | None | None | None | unavailable |
| 8905e452833b0a01defd8b1e | 1000 | None / 100 | None | None | None | unavailable |
| 28555ca1e3c1d3ab551385b1 | 1000 | None / 100 | None | None | None | unavailable |
| 861414ea84239f8471f0ade8 | 1000 | None / 100 | None | None | None | unavailable |
| 1f19207d799d9bcd0b005ef9 | 1000 | None / 100 | None | None | None | unavailable |
| ad007b170a6bbf5bc88d182d | 1000 | None / 100 | None | None | None | unavailable |
| 94488c6aa407c3ea167ea51d | 1000 | None / 100 | None | None | None | unavailable |
| e6a5e4cd9fbe73077175c7b9 | 1000 | None / 100 | None | None | None | unavailable |
| bca38cd4398e1159ed781bff | 1000 | None / 100 | None | None | None | unavailable |
| 68da09e4a00f4fe8d8b054fd | 1000 | None / 100 | None | None | None | unavailable |
| da666451073f38000c71b39f | 1000 | None / 100 | None | None | None | unavailable |
| 57b0ace8ad261f0963cece6e | 1000 | None / 100 | None | None | None | unavailable |
| b1be521b209066effb830ad1 | 1000 | None / 100 | None | None | None | unavailable |
| d246da52d2783b0000af34aa | 1000 | None / 100 | None | None | None | unavailable |
| 9ac1596b4a83bfd3759110f5 | 1000 | None / 100 | None | None | None | unavailable |
| d3e7acfb899406015f6d7e6a | 1000 | None / 100 | None | None | None | unavailable |
| 1b91b6d6beb187aaf9103cdc | 1000 | None / 100 | None | None | None | unavailable |
| 9a600f5f46fa47c339ccb4d1 | 1000 | None / 100 | None | None | None | unavailable |
| 635bac1c845730dae487891a | 1000 | None / 100 | None | None | None | unavailable |
| 031ae1822109079d3cddb520 | 1000 | None / 100 | None | None | None | unavailable |
| 3435ab1a884c517b32867161 | 1000 | None / 100 | None | None | None | unavailable |
| 09d4451a2a5b030d1853c267 | 1000 | None / 100 | None | None | None | unavailable |
| fa309fa719c353f20a813699 | 1000 | None / 100 | None | None | None | unavailable |
| 03ee79b7cf8d02ddb7baeea3 | 1000 | None / 100 | None | None | None | unavailable |
| 37aa09141ddb4b6e8f93f647 | 1000 | None / 100 | None | None | None | unavailable |
| c14b2b630688912a588e1cf3 | 1000 | None / 100 | None | None | None | unavailable |
| 2eda7453d476d16c07a327ed | 1000 | None / 100 | None | None | None | unavailable |
| 9a29639c43e873eec6a7d1ac | 1000 | None / 100 | None | None | None | unavailable |
| 0362b36136a70031c319de5f | 1000 | None / 100 | None | None | None | unavailable |
| 9397f85898818d3dc9d04c1e | 1000 | None / 100 | None | None | None | unavailable |
| 4c1b2ab65e6ba3e75ac9b10a | 1000 | None / 100 | None | None | None | unavailable |
| d679f4cef5e7a847d5f6dc80 | 1000 | None / 100 | None | None | None | unavailable |
| f19cc29f17b93bb9cbbd5f1a | 1000 | None / 100 | None | None | None | unavailable |
| e654a69635e2e4a1bcc2903b | 1000 | None / 100 | None | None | None | unavailable |
| 508b709256adff820b7fdf82 | 1000 | None / 100 | None | None | None | unavailable |
| 0ebaffd3a3e8d10252da8bd5 | 1000 | None / 100 | None | None | None | unavailable |
| 6f8cac15c1ed9dd1fb79b212 | 1000 | None / 100 | None | None | None | unavailable |
| 302070707affaaec2265e772 | 1000 | None / 100 | None | None | None | unavailable |
| 74feefbadad2b95947437ed6 | 1000 | None / 100 | None | None | None | unavailable |
| 982870b0fcc4a8bef4a297af | 1000 | None / 100 | None | None | None | unavailable |
| 2e5068d168160234340d32fa | 1000 | None / 100 | None | None | None | unavailable |
| f642d1e953d4e4b42c9a916e | 1000 | None / 100 | None | None | None | unavailable |
| d7884b1e2a9c1c3790535590 | 1000 | None / 100 | None | None | None | unavailable |
| 8499903e83df71431114aaa8 | 1000 | None / 100 | None | None | None | unavailable |
| 272db4c9310a73f01bf46d4b | 1000 | None / 100 | None | None | None | unavailable |
| 9f020616201afdc368d77f9b | 1000 | None / 100 | None | None | None | unavailable |
| 26318156d310334e8b260e87 | 1000 | None / 100 | None | None | None | unavailable |
| d7241b9882514c2709082321 | 1000 | None / 100 | None | None | None | unavailable |
| a5b3de3764680273ff4760e1 | 1000 | None / 100 | None | None | None | unavailable |
| e5c2ea10bc6ce298f6065199 | 1000 | None / 100 | None | None | None | unavailable |
| 847f33277d9d89fe17482367 | 1000 | None / 100 | None | None | None | unavailable |
| 77568a85e217721985cd8ea4 | 1000 | None / 100 | None | None | None | unavailable |
| 793ee3d9708b970c08a0fbe2 | 1000 | None / 100 | None | None | None | unavailable |
| 129251f55876e9cdc9e907a6 | 1000 | None / 100 | None | None | None | unavailable |
| 40059b37d028ec2cd587bbb1 | 1000 | None / 100 | None | None | None | unavailable |
| 30756d73095e1914cf757782 | 1000 | None / 100 | None | None | None | unavailable |
| d74e8582f780dfdeb9281671 | 1000 | None / 100 | None | None | None | unavailable |
| 88dfe1aa76490ae40e93f05f | 1000 | None / 100 | None | None | None | unavailable |
| 9adac77b91eae4f8ea4d8df2 | 1000 | None / 100 | None | None | None | unavailable |
| bbbda4ebfb279ed21179678b | 1000 | None / 100 | None | None | None | unavailable |
| 34f5fb1acf8d86a8a7a94e1c | 1000 | None / 100 | None | None | None | unavailable |
| c9dc2d0cfe6d53ccdef2f1ef | 1000 | None / 100 | None | None | None | unavailable |
| 22b85c86caaee83341968cec | 1000 | None / 100 | None | None | None | unavailable |
| 1a27fc67e8978362681b5d20 | 1000 | None / 100 | None | None | None | unavailable |
| f9ebb0802bd50e68ec18fcb0 | 1000 | None / 100 | None | None | None | unavailable |
| be9a4b3ce1acb50722ae8614 | 1000 | None / 100 | None | None | None | unavailable |
| 5c5511653f8d590c63a39794 | 1000 | None / 100 | None | None | None | unavailable |
| 7cbec59a4f05afaa8ebed3fb | 1000 | None / 100 | None | None | None | unavailable |
| b1a17c1fb747eef11f253278 | 1000 | None / 100 | None | None | None | unavailable |
| edb61534cb4ec7a4187ebbdb | 1000 | None / 100 | None | None | None | unavailable |
| 78360f37e3cd5a3eb5cc2b3e | 1000 | None / 100 | None | None | None | unavailable |
| 46d6404412a25fbdd2965880 | 1000 | None / 100 | None | None | None | unavailable |
| 50af2a28b866c26021d83b01 | 1000 | None / 100 | None | None | None | unavailable |
| 22a5ac50d5ca3c952b8b1e34 | 1000 | None / 100 | None | None | None | unavailable |
| 7d93e4d997ec1f974bb6c71a | 1000 | None / 100 | None | None | None | unavailable |
| 0f466b21fb4514acd9d1ff1e | 1000 | None / 100 | None | None | None | unavailable |
| 151bacf1f85b74f88864784e | 1000 | None / 100 | None | None | None | unavailable |
| 330479ee3f94e169b8496e0b | 1000 | None / 100 | None | None | None | unavailable |
| e4019672011694d495923c6f | 1000 | None / 100 | None | None | None | unavailable |
| bf89e6ad180b60ad56c35a7e | 1000 | None / 100 | None | None | None | unavailable |
| 70aacd394ef41b887377260a | 1000 | None / 100 | None | None | None | unavailable |
| b3f4ad21a596171a9a43e0aa | 1000 | None / 100 | None | None | None | unavailable |
| 6885c03ed3db8fb41a5e20dd | 1000 | None / 100 | None | None | None | unavailable |
| 9a22bb61d6e0f49880a936a3 | 1000 | None / 100 | None | None | None | unavailable |
| eafb85daf9dfc6661b0bc2d8 | 1000 | None / 100 | None | None | None | unavailable |
| f3375c98045e9e28a348b9d0 | 1000 | None / 100 | None | None | None | unavailable |
| d62c99156470a7900dc43bc6 | 1000 | None / 100 | None | None | None | unavailable |
| fa0defe230fa592c6e1395ce | 1000 | None / 100 | None | None | None | unavailable |
| 9d8fa010baff9d2225fff4d4 | 1000 | None / 100 | None | None | None | unavailable |
| d059ce23baa1380031ffc8cb | 1000 | None / 100 | None | None | None | unavailable |
| 058509628604e5ca4527273b | 1000 | None / 100 | None | None | None | unavailable |
| 165be2e488d7d1013b36ff1b | 1000 | None / 100 | None | None | None | unavailable |
| 6c498709f6484559ef4e1e7f | 1000 | None / 100 | None | None | None | unavailable |
| 789321f88cd80b79c41108d3 | 1000 | None / 100 | None | None | None | unavailable |
| 58f67f71157df294642d7924 | 1000 | None / 100 | None | None | None | unavailable |
| f434980db097ed5dc29aa6b8 | 1000 | None / 100 | None | None | None | unavailable |
| 0eadfbc9b2c2899d71a5dcee | 1000 | None / 100 | None | None | None | unavailable |
| 509562eef48054a3aeac166a | 1000 | None / 100 | None | None | None | unavailable |
| 8515821d35005362bf80ca86 | 1000 | None / 100 | None | None | None | unavailable |
| ce81522f547c386fa9c08c2b | 1000 | None / 100 | None | None | None | unavailable |
| 67fbcd1e5ac9b7dcb8f292b9 | 1000 | None / 100 | None | None | None | unavailable |
| 90334bd842b032c804251295 | 1000 | None / 100 | None | None | None | unavailable |
| 62cd670d3fc0e07b1d6ff2d7 | 1000 | None / 100 | None | None | None | unavailable |
| c2a654d2b5c10bec5b192bd4 | 1000 | None / 100 | None | None | None | unavailable |
| e513b37dc4ee2ea0c2ec9a4a | 1000 | None / 100 | None | None | None | unavailable |
| 5605235e2ed700e3724eec66 | 1000 | None / 100 | None | None | None | unavailable |
| caef53a035b7c9e1ee694a16 | 1000 | None / 100 | None | None | None | unavailable |
| 3e16fbe7ff4d0e5b55e6d9d1 | 1000 | None / 100 | None | None | None | unavailable |
| 66c77006152a19f5b1a397d3 | 1000 | None / 100 | None | None | None | unavailable |
| 6837bb994c30db520b1c50f5 | 1000 | None / 100 | None | None | None | unavailable |
| 4d261cc6ea3f349110835054 | 1000 | None / 100 | None | None | None | unavailable |
| b42ba0f2b0ed1a420be6ddb5 | 1000 | None / 100 | None | None | None | unavailable |
| 10d0d6ef3ebaeeab62506369 | 1000 | None / 100 | None | None | None | unavailable |
| 2fcaaa6515b6d07526750ec2 | 1000 | None / 100 | None | None | None | unavailable |
| 19a7255c9f6a76e216f4f3d3 | 1000 | None / 100 | None | None | None | unavailable |
| 875c812006d2f01a6a67e48b | 1000 | None / 100 | None | None | None | unavailable |
| 29c34b1e7fff719ad0530aaf | 1000 | None / 100 | None | None | None | unavailable |
| 4c03d7d4cf05c04e6563204a | 1000 | None / 100 | None | None | None | unavailable |
| 56dad6836419abb22b9f3fc5 | 1000 | None / 100 | None | None | None | unavailable |
| 722a6e81428fe90b28522578 | 1000 | None / 100 | None | None | None | unavailable |
| 64474eaad780d3d0f127b333 | 1000 | None / 100 | None | None | None | unavailable |
| 50bfcf7f7c0f6341243f0890 | 1000 | None / 100 | None | None | None | unavailable |
| 203da3ce23c2826be75941f8 | 1000 | None / 100 | None | None | None | unavailable |
| 6b9269f85604bbde03fb8ae2 | 1000 | None / 100 | None | None | None | unavailable |
| 6e30cfe3525aa76f6c298840 | 1000 | None / 100 | None | None | None | unavailable |
| f5f8f6ab600ed0fff3f77575 | 1000 | None / 100 | None | None | None | unavailable |
| a1ebc798b3d3dffdcb755fea | 1000 | None / 100 | None | None | None | unavailable |
| 64083f876c4b931fac1666ac | 1000 | None / 100 | None | None | None | unavailable |
| 3f0d5de719c7c2fac0765ae9 | 300 | None / 100 | None | None | None | unavailable |
| 02fbdb7be57f6759883cb7f7 | 300 | None / 100 | None | None | None | unavailable |
| 2eafd0179259617282b6bfe4 | 300 | None / 100 | None | None | None | unavailable |
| 62b13a164930d43ad696b359 | 300 | None / 100 | None | None | None | unavailable |
| 048ddd95d61026dbf40fa6f9 | 300 | None / 100 | None | None | None | unavailable |
| ea85d9daee87f0884e4f22e2 | 300 | None / 100 | None | None | None | unavailable |
| 7e27f3fa1620b77e96f8da6f | 300 | None / 100 | None | None | None | unavailable |
| 46cc8880d731fbee52076712 | 300 | None / 100 | None | None | None | unavailable |
| 45c033c5bc044beea6f5562c | 300 | None / 100 | None | None | None | unavailable |
| be96aaad5d4e1dd91747a116 | 300 | None / 100 | None | None | None | unavailable |
| c28a7e48a1333e1bbbca134d | 300 | None / 100 | None | None | None | unavailable |
| fda4c348dac5448fc10fd672 | 300 | None / 100 | None | None | None | unavailable |
| 929c713ce993539177ad3985 | 300 | None / 100 | None | None | None | unavailable |
| 47d567d51e4c0129ae905aa3 | 300 | None / 100 | None | None | None | unavailable |
| 1a7b6658a55e4798f9674c67 | 300 | None / 100 | None | None | None | unavailable |

| Dataset | Condition | Macro benchmark | Value | Pass | Failed cells |
|---|---|---|---:|---|---|
| zsre | R1_learned_ff | unseen_1000 | None | None | none observed |
| zsre | R1_learned_ff | outside_change_1000_100 | None | None | none observed |
| zsre | R1_learned_ff | revision_latest | None | None | none observed |
| zsre | R1_learned_ff | old_alias_reappearance | None | None | none observed |
| zsre | R1_learned_ff | revision_semantic | None | None | none observed |
| zsre | R1_learned_ff | retention_change | None | None | none observed |
| zsre | R1_learned_ff | es_change | None | None | none observed |
| zsre | R1_learned_ff | ls_change | None | None | none observed |
| zsre | R1_learned_ff | state_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff | peak_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff | wall_budget_ratio | None | None | none observed |
| zsre | R1_nonlearned | unseen_1000 | None | None | f3dbf1a3d5860a628e7d68ef, be44dfb501724b72adcbd747, 5263d61e569d7cb4ceb4e617, 81b1e9cb4e216a6cd1cd565a, deb5f473d9ca2ed544926204 |
| zsre | R1_nonlearned | outside_change_1000_100 | None | None | none observed |
| zsre | R1_nonlearned | revision_latest | None | None | none observed |
| zsre | R1_nonlearned | old_alias_reappearance | None | None | none observed |
| zsre | R1_nonlearned | revision_semantic | None | None | none observed |
| zsre | R1_nonlearned | retention_change | None | None | f3dbf1a3d5860a628e7d68ef, be44dfb501724b72adcbd747, 5263d61e569d7cb4ceb4e617, 81b1e9cb4e216a6cd1cd565a, deb5f473d9ca2ed544926204 |
| zsre | R1_nonlearned | es_change | None | None | none observed |
| zsre | R1_nonlearned | ls_change | None | None | f3dbf1a3d5860a628e7d68ef, be44dfb501724b72adcbd747, 5263d61e569d7cb4ceb4e617, 81b1e9cb4e216a6cd1cd565a, deb5f473d9ca2ed544926204 |
| zsre | R1_nonlearned | state_budget_ratio | None | None | none observed |
| zsre | R1_nonlearned | peak_budget_ratio | None | None | none observed |
| zsre | R1_nonlearned | wall_budget_ratio | None | None | none observed |
| zsre | v0_stable | unseen_1000 | None | None | none observed |
| zsre | v0_stable | outside_change_1000_100 | None | None | none observed |
| zsre | v0_stable | revision_latest | None | None | 39c7fd4929721e8dcba56b94, b887b1046cd563d990765e01, 435235a6719279d1cc87ad66, aaed1cf9e8ce7cf1cf3749fa, 92a5ef6855124ffc5a8d6163 |
| zsre | v0_stable | old_alias_reappearance | None | None | none observed |
| zsre | v0_stable | revision_semantic | None | None | none observed |
| zsre | v0_stable | retention_change | None | None | 39c7fd4929721e8dcba56b94, b887b1046cd563d990765e01, 435235a6719279d1cc87ad66, aaed1cf9e8ce7cf1cf3749fa, 92a5ef6855124ffc5a8d6163 |
| zsre | v0_stable | es_change | None | None | none observed |
| zsre | v0_stable | ls_change | None | None | none observed |
| zsre | v0_stable | state_budget_ratio | None | None | none observed |
| zsre | v0_stable | peak_budget_ratio | None | None | none observed |
| zsre | v0_stable | wall_budget_ratio | None | None | none observed |
| zsre | matched_update | unseen_1000 | None | None | none observed |
| zsre | matched_update | outside_change_1000_100 | None | None | none observed |
| zsre | matched_update | revision_latest | None | None | none observed |
| zsre | matched_update | old_alias_reappearance | None | None | none observed |
| zsre | matched_update | revision_semantic | None | None | none observed |
| zsre | matched_update | retention_change | None | None | none observed |
| zsre | matched_update | es_change | None | None | none observed |
| zsre | matched_update | ls_change | None | None | none observed |
| zsre | matched_update | state_budget_ratio | None | None | none observed |
| zsre | matched_update | peak_budget_ratio | None | None | none observed |
| zsre | matched_update | wall_budget_ratio | None | None | none observed |
| zsre | v0_live_C1 | unseen_1000 | None | None | none observed |
| zsre | v0_live_C1 | outside_change_1000_100 | None | None | none observed |
| zsre | v0_live_C1 | revision_latest | None | None | none observed |
| zsre | v0_live_C1 | old_alias_reappearance | None | None | none observed |
| zsre | v0_live_C1 | revision_semantic | None | None | none observed |
| zsre | v0_live_C1 | retention_change | None | None | none observed |
| zsre | v0_live_C1 | es_change | None | None | none observed |
| zsre | v0_live_C1 | ls_change | None | None | none observed |
| zsre | v0_live_C1 | state_budget_ratio | None | None | none observed |
| zsre | v0_live_C1 | peak_budget_ratio | None | None | none observed |
| zsre | v0_live_C1 | wall_budget_ratio | None | None | none observed |
| zsre | v0_live_C2 | unseen_1000 | None | None | none observed |
| zsre | v0_live_C2 | outside_change_1000_100 | None | None | none observed |
| zsre | v0_live_C2 | revision_latest | None | None | none observed |
| zsre | v0_live_C2 | old_alias_reappearance | None | None | none observed |
| zsre | v0_live_C2 | revision_semantic | None | None | none observed |
| zsre | v0_live_C2 | retention_change | None | None | none observed |
| zsre | v0_live_C2 | es_change | None | None | none observed |
| zsre | v0_live_C2 | ls_change | None | None | none observed |
| zsre | v0_live_C2 | state_budget_ratio | None | None | none observed |
| zsre | v0_live_C2 | peak_budget_ratio | None | None | none observed |
| zsre | v0_live_C2 | wall_budget_ratio | None | None | none observed |
| zsre | S1_LM | unseen_1000 | None | None | none observed |
| zsre | S1_LM | outside_change_1000_100 | None | None | none observed |
| zsre | S1_LM | revision_latest | None | None | none observed |
| zsre | S1_LM | old_alias_reappearance | None | None | none observed |
| zsre | S1_LM | revision_semantic | None | None | none observed |
| zsre | S1_LM | retention_change | None | None | none observed |
| zsre | S1_LM | es_change | None | None | none observed |
| zsre | S1_LM | ls_change | None | None | none observed |
| zsre | S1_LM | state_budget_ratio | None | None | none observed |
| zsre | S1_LM | peak_budget_ratio | None | None | none observed |
| zsre | S1_LM | wall_budget_ratio | None | None | none observed |
| zsre | S1_literal | unseen_1000 | None | None | none observed |
| zsre | S1_literal | outside_change_1000_100 | None | None | none observed |
| zsre | S1_literal | revision_latest | None | None | none observed |
| zsre | S1_literal | old_alias_reappearance | None | None | none observed |
| zsre | S1_literal | revision_semantic | None | None | none observed |
| zsre | S1_literal | retention_change | None | None | none observed |
| zsre | S1_literal | es_change | None | None | none observed |
| zsre | S1_literal | ls_change | None | None | none observed |
| zsre | S1_literal | state_budget_ratio | None | None | none observed |
| zsre | S1_literal | peak_budget_ratio | None | None | none observed |
| zsre | S1_literal | wall_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff_v2 | unseen_1000 | None | None | none observed |
| zsre | R1_learned_ff_v2 | outside_change_1000_100 | None | None | none observed |
| zsre | R1_learned_ff_v2 | revision_latest | None | None | none observed |
| zsre | R1_learned_ff_v2 | old_alias_reappearance | None | None | none observed |
| zsre | R1_learned_ff_v2 | revision_semantic | None | None | none observed |
| zsre | R1_learned_ff_v2 | retention_change | None | None | none observed |
| zsre | R1_learned_ff_v2 | es_change | None | None | none observed |
| zsre | R1_learned_ff_v2 | ls_change | None | None | none observed |
| zsre | R1_learned_ff_v2 | state_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff_v2 | peak_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff_v2 | wall_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | unseen_1000 | None | None | none observed |
| counterfact | R1_learned_ff | outside_change_1000_100 | None | None | none observed |
| counterfact | R1_learned_ff | revision_latest | None | None | none observed |
| counterfact | R1_learned_ff | old_alias_reappearance | None | None | none observed |
| counterfact | R1_learned_ff | revision_semantic | None | None | none observed |
| counterfact | R1_learned_ff | retention_change | None | None | ce0d0ffc2a58a60e27c460d9, 95dfb24c6361b2d38dd60e9b, 6d0915056b1e76d8ee8795ff, 7c9675a69d832a772070cb2d, 95016bc16e89cfcccccc40b8 |
| counterfact | R1_learned_ff | es_change | None | None | none observed |
| counterfact | R1_learned_ff | ls_change | None | None | none observed |
| counterfact | R1_learned_ff | state_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | peak_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | wall_budget_ratio | None | None | none observed |
| counterfact | R1_nonlearned | unseen_1000 | None | None | 0b6ade77641a02c1c85574b0, ee67c592789829e7dd808ede, 8be432675ed4dc57f9108bd4, 78928f2782d91d888ef24d52, de785feed05c9f4c2a9e9273 |
| counterfact | R1_nonlearned | outside_change_1000_100 | None | None | 0b6ade77641a02c1c85574b0, ee67c592789829e7dd808ede, 8be432675ed4dc57f9108bd4, 78928f2782d91d888ef24d52, de785feed05c9f4c2a9e9273 |
| counterfact | R1_nonlearned | revision_latest | None | None | none observed |
| counterfact | R1_nonlearned | old_alias_reappearance | None | None | 0b6ade77641a02c1c85574b0, ee67c592789829e7dd808ede, 8be432675ed4dc57f9108bd4, 78928f2782d91d888ef24d52, de785feed05c9f4c2a9e9273 |
| counterfact | R1_nonlearned | revision_semantic | None | None | none observed |
| counterfact | R1_nonlearned | retention_change | None | None | 0b6ade77641a02c1c85574b0, ee67c592789829e7dd808ede, 78928f2782d91d888ef24d52 |
| counterfact | R1_nonlearned | es_change | None | None | none observed |
| counterfact | R1_nonlearned | ls_change | None | None | 0b6ade77641a02c1c85574b0, 8be432675ed4dc57f9108bd4, 78928f2782d91d888ef24d52, de785feed05c9f4c2a9e9273 |
| counterfact | R1_nonlearned | state_budget_ratio | None | None | none observed |
| counterfact | R1_nonlearned | peak_budget_ratio | None | None | none observed |
| counterfact | R1_nonlearned | wall_budget_ratio | None | None | none observed |
| counterfact | v0_stable | unseen_1000 | None | None | none observed |
| counterfact | v0_stable | outside_change_1000_100 | None | None | none observed |
| counterfact | v0_stable | revision_latest | None | None | baa601113af675024e73bc30, b6b271f3383f85fb19e49836, 6c0124a2d35b8b4bf8d2a321, 37c2ba2be995719ac8972cf1, d93ed5de9d4401cb3345c7bd |
| counterfact | v0_stable | old_alias_reappearance | None | None | none observed |
| counterfact | v0_stable | revision_semantic | None | None | none observed |
| counterfact | v0_stable | retention_change | None | None | none observed |
| counterfact | v0_stable | es_change | None | None | none observed |
| counterfact | v0_stable | ls_change | None | None | none observed |
| counterfact | v0_stable | state_budget_ratio | None | None | none observed |
| counterfact | v0_stable | peak_budget_ratio | None | None | none observed |
| counterfact | v0_stable | wall_budget_ratio | None | None | none observed |
| counterfact | matched_update | unseen_1000 | None | None | none observed |
| counterfact | matched_update | outside_change_1000_100 | None | None | none observed |
| counterfact | matched_update | revision_latest | None | None | none observed |
| counterfact | matched_update | old_alias_reappearance | None | None | none observed |
| counterfact | matched_update | revision_semantic | None | None | none observed |
| counterfact | matched_update | retention_change | None | None | none observed |
| counterfact | matched_update | es_change | None | None | none observed |
| counterfact | matched_update | ls_change | None | None | none observed |
| counterfact | matched_update | state_budget_ratio | None | None | none observed |
| counterfact | matched_update | peak_budget_ratio | None | None | none observed |
| counterfact | matched_update | wall_budget_ratio | None | None | none observed |
| counterfact | v0_live_C1 | unseen_1000 | None | None | none observed |
| counterfact | v0_live_C1 | outside_change_1000_100 | None | None | none observed |
| counterfact | v0_live_C1 | revision_latest | None | None | none observed |
| counterfact | v0_live_C1 | old_alias_reappearance | None | None | none observed |
| counterfact | v0_live_C1 | revision_semantic | None | None | none observed |
| counterfact | v0_live_C1 | retention_change | None | None | none observed |
| counterfact | v0_live_C1 | es_change | None | None | none observed |
| counterfact | v0_live_C1 | ls_change | None | None | none observed |
| counterfact | v0_live_C1 | state_budget_ratio | None | None | none observed |
| counterfact | v0_live_C1 | peak_budget_ratio | None | None | none observed |
| counterfact | v0_live_C1 | wall_budget_ratio | None | None | none observed |
| counterfact | v0_live_C2 | unseen_1000 | None | None | none observed |
| counterfact | v0_live_C2 | outside_change_1000_100 | None | None | none observed |
| counterfact | v0_live_C2 | revision_latest | None | None | none observed |
| counterfact | v0_live_C2 | old_alias_reappearance | None | None | none observed |
| counterfact | v0_live_C2 | revision_semantic | None | None | none observed |
| counterfact | v0_live_C2 | retention_change | None | None | none observed |
| counterfact | v0_live_C2 | es_change | None | None | none observed |
| counterfact | v0_live_C2 | ls_change | None | None | none observed |
| counterfact | v0_live_C2 | state_budget_ratio | None | None | none observed |
| counterfact | v0_live_C2 | peak_budget_ratio | None | None | none observed |
| counterfact | v0_live_C2 | wall_budget_ratio | None | None | none observed |
| counterfact | S1_LM | unseen_1000 | None | None | none observed |
| counterfact | S1_LM | outside_change_1000_100 | None | None | none observed |
| counterfact | S1_LM | revision_latest | None | None | none observed |
| counterfact | S1_LM | old_alias_reappearance | None | None | none observed |
| counterfact | S1_LM | revision_semantic | None | None | none observed |
| counterfact | S1_LM | retention_change | None | None | none observed |
| counterfact | S1_LM | es_change | None | None | none observed |
| counterfact | S1_LM | ls_change | None | None | none observed |
| counterfact | S1_LM | state_budget_ratio | None | None | none observed |
| counterfact | S1_LM | peak_budget_ratio | None | None | none observed |
| counterfact | S1_LM | wall_budget_ratio | None | None | none observed |
| counterfact | S1_literal | unseen_1000 | None | None | none observed |
| counterfact | S1_literal | outside_change_1000_100 | None | None | none observed |
| counterfact | S1_literal | revision_latest | None | None | none observed |
| counterfact | S1_literal | old_alias_reappearance | None | None | none observed |
| counterfact | S1_literal | revision_semantic | None | None | none observed |
| counterfact | S1_literal | retention_change | None | None | none observed |
| counterfact | S1_literal | es_change | None | None | none observed |
| counterfact | S1_literal | ls_change | None | None | none observed |
| counterfact | S1_literal | state_budget_ratio | None | None | none observed |
| counterfact | S1_literal | peak_budget_ratio | None | None | none observed |
| counterfact | S1_literal | wall_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff_v2 | unseen_1000 | None | None | none observed |
| counterfact | R1_learned_ff_v2 | outside_change_1000_100 | None | None | none observed |
| counterfact | R1_learned_ff_v2 | revision_latest | None | None | none observed |
| counterfact | R1_learned_ff_v2 | old_alias_reappearance | None | None | none observed |
| counterfact | R1_learned_ff_v2 | revision_semantic | None | None | none observed |
| counterfact | R1_learned_ff_v2 | retention_change | None | None | none observed |
| counterfact | R1_learned_ff_v2 | es_change | None | None | none observed |
| counterfact | R1_learned_ff_v2 | ls_change | None | None | none observed |
| counterfact | R1_learned_ff_v2 | state_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff_v2 | peak_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff_v2 | wall_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff | unseen_1000 | None | None | none observed |
| mquake | R1_learned_ff | outside_change_1000_100 | None | None | none observed |
| mquake | R1_learned_ff | revision_latest | None | None | none observed |
| mquake | R1_learned_ff | old_alias_reappearance | None | None | none observed |
| mquake | R1_learned_ff | revision_semantic | None | None | none observed |
| mquake | R1_learned_ff | retention_change | None | None | none observed |
| mquake | R1_learned_ff | es_change | None | None | none observed |
| mquake | R1_learned_ff | ls_change | None | None | none observed |
| mquake | R1_learned_ff | state_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff | peak_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff | wall_budget_ratio | None | None | none observed |
| mquake | R1_nonlearned | unseen_1000 | None | None | none observed |
| mquake | R1_nonlearned | outside_change_1000_100 | None | None | none observed |
| mquake | R1_nonlearned | revision_latest | None | None | none observed |
| mquake | R1_nonlearned | old_alias_reappearance | None | None | none observed |
| mquake | R1_nonlearned | revision_semantic | None | None | none observed |
| mquake | R1_nonlearned | retention_change | None | None | none observed |
| mquake | R1_nonlearned | es_change | None | None | none observed |
| mquake | R1_nonlearned | ls_change | None | None | none observed |
| mquake | R1_nonlearned | state_budget_ratio | None | None | none observed |
| mquake | R1_nonlearned | peak_budget_ratio | None | None | none observed |
| mquake | R1_nonlearned | wall_budget_ratio | None | None | none observed |
| mquake | v0_stable | unseen_1000 | None | None | none observed |
| mquake | v0_stable | outside_change_1000_100 | None | None | none observed |
| mquake | v0_stable | revision_latest | None | None | c2f9d3102987f746f4f31b8d, a23ae9063b37c21cfe657d47, 5a6f61e06de0bca53b4a7377, 03426d6e61fb6b41145c5d8e, 19f5d8535235334ffe1595e8 |
| mquake | v0_stable | old_alias_reappearance | None | None | none observed |
| mquake | v0_stable | revision_semantic | None | None | none observed |
| mquake | v0_stable | retention_change | None | None | none observed |
| mquake | v0_stable | es_change | None | None | none observed |
| mquake | v0_stable | ls_change | None | None | none observed |
| mquake | v0_stable | state_budget_ratio | None | None | none observed |
| mquake | v0_stable | peak_budget_ratio | None | None | none observed |
| mquake | v0_stable | wall_budget_ratio | None | None | none observed |
| mquake | matched_update | unseen_1000 | None | None | none observed |
| mquake | matched_update | outside_change_1000_100 | None | None | none observed |
| mquake | matched_update | revision_latest | None | None | none observed |
| mquake | matched_update | old_alias_reappearance | None | None | none observed |
| mquake | matched_update | revision_semantic | None | None | none observed |
| mquake | matched_update | retention_change | None | None | none observed |
| mquake | matched_update | es_change | None | None | none observed |
| mquake | matched_update | ls_change | None | None | none observed |
| mquake | matched_update | state_budget_ratio | None | None | none observed |
| mquake | matched_update | peak_budget_ratio | None | None | none observed |
| mquake | matched_update | wall_budget_ratio | None | None | none observed |
| mquake | v0_live_C1 | unseen_1000 | None | None | none observed |
| mquake | v0_live_C1 | outside_change_1000_100 | None | None | none observed |
| mquake | v0_live_C1 | revision_latest | None | None | none observed |
| mquake | v0_live_C1 | old_alias_reappearance | None | None | none observed |
| mquake | v0_live_C1 | revision_semantic | None | None | none observed |
| mquake | v0_live_C1 | retention_change | None | None | none observed |
| mquake | v0_live_C1 | es_change | None | None | none observed |
| mquake | v0_live_C1 | ls_change | None | None | none observed |
| mquake | v0_live_C1 | state_budget_ratio | None | None | none observed |
| mquake | v0_live_C1 | peak_budget_ratio | None | None | none observed |
| mquake | v0_live_C1 | wall_budget_ratio | None | None | none observed |
| mquake | v0_live_C2 | unseen_1000 | None | None | none observed |
| mquake | v0_live_C2 | outside_change_1000_100 | None | None | none observed |
| mquake | v0_live_C2 | revision_latest | None | None | none observed |
| mquake | v0_live_C2 | old_alias_reappearance | None | None | none observed |
| mquake | v0_live_C2 | revision_semantic | None | None | none observed |
| mquake | v0_live_C2 | retention_change | None | None | none observed |
| mquake | v0_live_C2 | es_change | None | None | none observed |
| mquake | v0_live_C2 | ls_change | None | None | none observed |
| mquake | v0_live_C2 | state_budget_ratio | None | None | none observed |
| mquake | v0_live_C2 | peak_budget_ratio | None | None | none observed |
| mquake | v0_live_C2 | wall_budget_ratio | None | None | none observed |
| mquake | S1_LM | unseen_1000 | None | None | none observed |
| mquake | S1_LM | outside_change_1000_100 | None | None | none observed |
| mquake | S1_LM | revision_latest | None | None | none observed |
| mquake | S1_LM | old_alias_reappearance | None | None | none observed |
| mquake | S1_LM | revision_semantic | None | None | none observed |
| mquake | S1_LM | retention_change | None | None | none observed |
| mquake | S1_LM | es_change | None | None | none observed |
| mquake | S1_LM | ls_change | None | None | none observed |
| mquake | S1_LM | state_budget_ratio | None | None | none observed |
| mquake | S1_LM | peak_budget_ratio | None | None | none observed |
| mquake | S1_LM | wall_budget_ratio | None | None | none observed |
| mquake | S1_literal | unseen_1000 | None | None | none observed |
| mquake | S1_literal | outside_change_1000_100 | None | None | none observed |
| mquake | S1_literal | revision_latest | None | None | none observed |
| mquake | S1_literal | old_alias_reappearance | None | None | none observed |
| mquake | S1_literal | revision_semantic | None | None | none observed |
| mquake | S1_literal | retention_change | None | None | none observed |
| mquake | S1_literal | es_change | None | None | none observed |
| mquake | S1_literal | ls_change | None | None | none observed |
| mquake | S1_literal | state_budget_ratio | None | None | none observed |
| mquake | S1_literal | peak_budget_ratio | None | None | none observed |
| mquake | S1_literal | wall_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff_v2 | unseen_1000 | None | None | none observed |
| mquake | R1_learned_ff_v2 | outside_change_1000_100 | None | None | none observed |
| mquake | R1_learned_ff_v2 | revision_latest | None | None | none observed |
| mquake | R1_learned_ff_v2 | old_alias_reappearance | None | None | none observed |
| mquake | R1_learned_ff_v2 | revision_semantic | None | None | none observed |
| mquake | R1_learned_ff_v2 | retention_change | None | None | none observed |
| mquake | R1_learned_ff_v2 | es_change | None | None | none observed |
| mquake | R1_learned_ff_v2 | ls_change | None | None | none observed |
| mquake | R1_learned_ff_v2 | state_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff_v2 | peak_budget_ratio | None | None | none observed |
| mquake | R1_learned_ff_v2 | wall_budget_ratio | None | None | none observed |

DEC-061 NM-template-v1 at the final planned checkpoint:

| Cell | Preserved / evaluated / planned | Full inventory rate | Missing |
|---|---|---|---|
| 61348508e40d54351613ab14 | 86.0 / 100 / 100 | 0.86 | 0 |
| 88af67fa5945b642e8ba7974 | 86.0 / 100 / 100 | 0.86 | 0 |
| 915f97b05f3fa2a81de09cdf | 86.0 / 100 / 100 | 0.86 | 0 |
| 4aa4849ba414edab2504f56b | 86.0 / 100 / 100 | 0.86 | 0 |
| 9ebc93cc7912bd5d1c929418 | 86.0 / 100 / 100 | 0.86 | 0 |
| ce0d0ffc2a58a60e27c460d9 | 100.0 / 100 / 100 | 1.0 | 0 |
| 95dfb24c6361b2d38dd60e9b | 100.0 / 100 / 100 | 1.0 | 0 |
| 6d0915056b1e76d8ee8795ff | 100.0 / 100 / 100 | 1.0 | 0 |
| 7c9675a69d832a772070cb2d | 100.0 / 100 / 100 | 1.0 | 0 |
| 95016bc16e89cfcccccc40b8 | 100.0 / 100 / 100 | 1.0 | 0 |
| 43925e53c31860219a85ef90 | 100.0 / 100 / 100 | 1.0 | 0 |
| c29ee18fb21ba6b387ede6e8 | 100.0 / 100 / 100 | 1.0 | 0 |
| 54879da4dcdb0f106f98080a | 100.0 / 100 / 100 | 1.0 | 0 |
| 78ebbc03946239c1d637154c | 100.0 / 100 / 100 | 1.0 | 0 |
| b1d1e53944241333ec5603d4 | 100.0 / 100 / 100 | 1.0 | 0 |
| f3dbf1a3d5860a628e7d68ef | 0.0 / 100 / 100 | 0.0 | 0 |
| be44dfb501724b72adcbd747 | 0.0 / 100 / 100 | 0.0 | 0 |
| 5263d61e569d7cb4ceb4e617 | 0.0 / 100 / 100 | 0.0 | 0 |
| 81b1e9cb4e216a6cd1cd565a | 0.0 / 100 / 100 | 0.0 | 0 |
| deb5f473d9ca2ed544926204 | 0.0 / 100 / 100 | 0.0 | 0 |
| 0b6ade77641a02c1c85574b0 | 0.0 / 100 / 100 | 0.0 | 0 |
| ee67c592789829e7dd808ede | 0.0 / 100 / 100 | 0.0 | 0 |
| 8be432675ed4dc57f9108bd4 | 0.0 / 100 / 100 | 0.0 | 0 |
| 78928f2782d91d888ef24d52 | 0.0 / 100 / 100 | 0.0 | 0 |
| de785feed05c9f4c2a9e9273 | 0.0 / 100 / 100 | 0.0 | 0 |
| de0b9612418e6d573ed77679 | 0.0 / 100 / 100 | 0.0 | 0 |
| be37e2a1ff4a079e56efe268 | 0.0 / 100 / 100 | 0.0 | 0 |
| 1e6b766c4139230c18547234 | 0.0 / 100 / 100 | 0.0 | 0 |
| c0a54c5fbf1ce7776efc983e | 0.0 / 100 / 100 | 0.0 | 0 |
| 7499c19b813dcada2c67ae39 | 0.0 / 100 / 100 | 0.0 | 0 |
| 39c7fd4929721e8dcba56b94 | 27.0 / 100 / 100 | 0.27 | 0 |
| b887b1046cd563d990765e01 | 34.0 / 100 / 100 | 0.34 | 0 |
| 435235a6719279d1cc87ad66 | 36.0 / 100 / 100 | 0.36 | 0 |
| aaed1cf9e8ce7cf1cf3749fa | 36.0 / 100 / 100 | 0.36 | 0 |
| 92a5ef6855124ffc5a8d6163 | 32.0 / 100 / 100 | 0.32 | 0 |
| baa601113af675024e73bc30 | 100.0 / 100 / 100 | 1.0 | 0 |
| b6b271f3383f85fb19e49836 | 100.0 / 100 / 100 | 1.0 | 0 |
| 6c0124a2d35b8b4bf8d2a321 | 100.0 / 100 / 100 | 1.0 | 0 |
| 37c2ba2be995719ac8972cf1 | 100.0 / 100 / 100 | 1.0 | 0 |
| d93ed5de9d4401cb3345c7bd | 100.0 / 100 / 100 | 1.0 | 0 |
| c2f9d3102987f746f4f31b8d | 100.0 / 100 / 100 | 1.0 | 0 |
| a23ae9063b37c21cfe657d47 | 100.0 / 100 / 100 | 1.0 | 0 |
| 5a6f61e06de0bca53b4a7377 | 100.0 / 100 / 100 | 1.0 | 0 |
| 03426d6e61fb6b41145c5d8e | 100.0 / 100 / 100 | 1.0 | 0 |
| 19f5d8535235334ffe1595e8 | 100.0 / 100 / 100 | 1.0 | 0 |
| 6b089d284c00a4418a1d3af4 | 0.0 / 0 / 100 | None | 100 |
| 47dac9d968ffe594faac0a14 | 0.0 / 0 / 100 | None | 100 |
| 4eda9e6155b2755508e13091 | 0.0 / 0 / 100 | None | 100 |
| ab774e229a65298fdc117c96 | 0.0 / 0 / 100 | None | 100 |
| b4e7dc307a1f895a8fec997a | 0.0 / 0 / 100 | None | 100 |
| 826332f387bd487a045d412f | 0.0 / 0 / 100 | None | 100 |
| 14d45f0e87126104057518af | 0.0 / 0 / 100 | None | 100 |
| 960d0adeb6cacfcfce93d546 | 0.0 / 0 / 100 | None | 100 |
| 6840a40e6e5c90bdc40b89b0 | 0.0 / 0 / 100 | None | 100 |
| 42ba32e4f07423bee03296b3 | 0.0 / 0 / 100 | None | 100 |
| 19964c4e7f737707baad94a5 | 0.0 / 0 / 100 | None | 100 |
| 40ec11c9694b4265a013c682 | 0.0 / 0 / 100 | None | 100 |
| f0642100f6eb9cd77e92f439 | 0.0 / 0 / 100 | None | 100 |
| b7ff3139c3f3eeb3ff7e9c80 | 0.0 / 0 / 100 | None | 100 |
| 1833a410c9e8704f6a379114 | 0.0 / 0 / 100 | None | 100 |
| 82606602ae475e73eb4401f9 | 0.0 / 0 / 100 | None | 100 |
| 2172052824abd70e8135366f | 0.0 / 0 / 100 | None | 100 |
| 5c394f4861164c1d5b31de4c | 0.0 / 0 / 100 | None | 100 |
| c9d2325e783e57ac5eafa34d | 0.0 / 0 / 100 | None | 100 |
| 3fdc7c12d6d583f46608eac6 | 0.0 / 0 / 100 | None | 100 |
| a7d551c093fd3333314813a5 | 0.0 / 0 / 100 | None | 100 |
| c402523c2460a62d6040ddd0 | 0.0 / 0 / 100 | None | 100 |
| b103826472ba7653cd8fd13a | 0.0 / 0 / 100 | None | 100 |
| 525ad705ad7008ed3ea378eb | 0.0 / 0 / 100 | None | 100 |
| 8a4bcb6e358e98c523b0d0c3 | 0.0 / 0 / 100 | None | 100 |
| 144f77ff21860a8a089a8080 | 0.0 / 0 / 100 | None | 100 |
| 3c3212c0cad597bafe0d5782 | 0.0 / 0 / 100 | None | 100 |
| 5d467b73f60b99b3d07f8c02 | 0.0 / 0 / 100 | None | 100 |
| a81b13b1b22e0bfe489daaa0 | 0.0 / 0 / 100 | None | 100 |
| 1aff34869825a76d502d92a3 | 0.0 / 0 / 100 | None | 100 |
| 3b70d3d44297fc1197610228 | 0.0 / 0 / 100 | None | 100 |
| 84bae28d26e5f5a3e555b601 | 0.0 / 0 / 100 | None | 100 |
| 07b9bad1f676110cb8bae7df | 0.0 / 0 / 100 | None | 100 |
| 0ff8a61a760d6836f469629b | 0.0 / 0 / 100 | None | 100 |
| 40034291ac69439c82ae1fc3 | 0.0 / 0 / 100 | None | 100 |
| 6d8d11dbbbc7b736c6386bca | 0.0 / 0 / 100 | None | 100 |
| cefda69ce81ca1253435bac7 | 0.0 / 0 / 100 | None | 100 |
| e42cd6f9b5b86feb491512f6 | 0.0 / 0 / 100 | None | 100 |
| e0f2bb19e19594c972c0ef15 | 0.0 / 0 / 100 | None | 100 |
| 0d4d946cb9ff28b7e6af3c4d | 0.0 / 0 / 100 | None | 100 |
| 9179614db32d3fd8b437475b | 0.0 / 0 / 100 | None | 100 |
| e146662ae0ab343921979246 | 0.0 / 0 / 100 | None | 100 |
| c770960b77b2d9f6304f1a34 | 0.0 / 0 / 100 | None | 100 |
| d49ef9c7980da822326bc6ac | 0.0 / 0 / 100 | None | 100 |
| eef5c3dc3fc8291d75199816 | 0.0 / 0 / 100 | None | 100 |
| 0417f598d89548e3200a3fe4 | 0.0 / 0 / 100 | None | 100 |
| 12a9c0da62781d521da26cd5 | 0.0 / 0 / 100 | None | 100 |
| c2a67190edb39398491bd651 | 0.0 / 0 / 100 | None | 100 |
| 58cc3599099d7ab60e5d1413 | 0.0 / 0 / 100 | None | 100 |
| 4206e18c23b43bb312e045e6 | 0.0 / 0 / 100 | None | 100 |
| fa46e16c8436f7ea4a5c3f06 | 0.0 / 0 / 100 | None | 100 |
| 162686f6303fe986619d236d | 0.0 / 0 / 100 | None | 100 |
| 029ecd260f3e085063714d3f | 0.0 / 0 / 100 | None | 100 |
| 7197775fb7f97a465fd3310e | 0.0 / 0 / 100 | None | 100 |
| 6de7e97b6cb167d048dc31ba | 0.0 / 0 / 100 | None | 100 |
| fcd702d12d5d6bfae824379b | 0.0 / 0 / 100 | None | 100 |
| 9a1d038b95f534b43185c7fc | 0.0 / 0 / 100 | None | 100 |
| dfc9c9b480e482911c457e07 | 0.0 / 0 / 100 | None | 100 |
| 34fce88c919bcae6410e4d94 | 0.0 / 0 / 100 | None | 100 |
| 7a39ae192fb0b1038c651f64 | 0.0 / 0 / 100 | None | 100 |
| 13465e8d0dc3824fced8e891 | 0.0 / 0 / 100 | None | 100 |
| 24840672cf1682dd450fdcd2 | 0.0 / 0 / 100 | None | 100 |
| 12a6e3e550a7939c6d79349d | 0.0 / 0 / 100 | None | 100 |
| fa5b51891eb78dc707e6471f | 0.0 / 0 / 100 | None | 100 |
| 861810fbdd6ebe7502383382 | 0.0 / 0 / 100 | None | 100 |
| 6ed2474713b3a311b4ec6b08 | 0.0 / 0 / 100 | None | 100 |
| f939f211b98675ac7c2d951f | 0.0 / 0 / 100 | None | 100 |
| 19b5e9b462930c6f50f2e2f6 | 0.0 / 0 / 100 | None | 100 |
| b14576e3d752f467db2abf18 | 0.0 / 0 / 100 | None | 100 |
| da9f71bdb9a8981dac078e6c | 0.0 / 0 / 100 | None | 100 |
| 9e98169ae668b50d60694317 | 0.0 / 0 / 100 | None | 100 |
| ff570734d7837a1ba9e77528 | 0.0 / 0 / 100 | None | 100 |
| 4fd2bc51397502cb1c085b5c | 0.0 / 0 / 100 | None | 100 |
| c0e77c94b06dd3464838be93 | 0.0 / 0 / 100 | None | 100 |
| 4c700c665ce70ca41e4569dd | 0.0 / 0 / 100 | None | 100 |
| dc17fc3637068157dba0207d | 0.0 / 0 / 100 | None | 100 |
| 727b32ab9723cb9feba71636 | 0.0 / 0 / 100 | None | 100 |
| a02980b0886a222f8e2f58e8 | 0.0 / 0 / 100 | None | 100 |
| 9aeb330f6c7e29c85ee56da0 | 0.0 / 0 / 100 | None | 100 |
| 0e0ee9a35e1116f7dafb423d | 0.0 / 0 / 100 | None | 100 |
| 862cd40c359e48e5a7998e3f | 0.0 / 0 / 100 | None | 100 |
| 89b258fddde381d9a09429d9 | 0.0 / 0 / 100 | None | 100 |
| 090d1237381f4ee02fcbd05d | 0.0 / 0 / 100 | None | 100 |
| 6e95ec72097ffded952889d6 | 0.0 / 0 / 100 | None | 100 |
| c8ce51b334cc3e42a623be6c | 0.0 / 0 / 100 | None | 100 |
| cf6bd4a623aa24871f74d136 | 0.0 / 0 / 100 | None | 100 |
| 519b30353f979e8028ed03e1 | 0.0 / 0 / 100 | None | 100 |
| 89182e81a187807d2772cade | 0.0 / 0 / 100 | None | 100 |
| 9ad3399cfc13f1297d17423d | 0.0 / 0 / 100 | None | 100 |
| 046aa51d028b84dde8981351 | 0.0 / 0 / 100 | None | 100 |
| c897cd3d2a3b35bfe999e87e | 0.0 / 0 / 100 | None | 100 |
| 1689630f5ad581d9fcfc483e | 0.0 / 0 / 100 | None | 100 |
| c1c03ed850a40df57da8628a | 0.0 / 0 / 100 | None | 100 |
| d1690029ea53ae03b3705536 | 0.0 / 0 / 100 | None | 100 |
| a921f9ab5443f978e56d2390 | 0.0 / 0 / 100 | None | 100 |
| a86da75220343c5560c45373 | 0.0 / 0 / 100 | None | 100 |
| e7b52c6db370d10a5fd7d891 | 0.0 / 0 / 100 | None | 100 |
| 735081421354eaafb893322d | 0.0 / 0 / 100 | None | 100 |
| 824f602358ace0fc5cb69271 | 0.0 / 0 / 100 | None | 100 |
| 3bc2cef1ca9bab6e4a90e222 | 0.0 / 0 / 100 | None | 100 |
| 9c3c7c258bf086523ea6268e | 0.0 / 0 / 100 | None | 100 |
| 58879f9745ed479686bd0481 | 0.0 / 0 / 100 | None | 100 |
| b6ea6d9e337e3bf6f2eca5d2 | 0.0 / 0 / 100 | None | 100 |
| 16037ce355e4a2e9a43a2008 | 0.0 / 0 / 100 | None | 100 |
| 4597af8473d8e404f1490c57 | 0.0 / 0 / 100 | None | 100 |
| 7c933afa6e2adc84ccb287be | 0.0 / 0 / 100 | None | 100 |
| 0998eeed741b887bdb8664af | 0.0 / 0 / 100 | None | 100 |
| bb4da95ca8ce5b0b8d3dbe35 | 0.0 / 0 / 100 | None | 100 |
| c5f1daa35261cf950172dfa8 | 0.0 / 0 / 100 | None | 100 |
| 244f29ba9b89c48d08c257c7 | 0.0 / 0 / 100 | None | 100 |
| b8924c056fee6d000f5492d1 | 0.0 / 0 / 100 | None | 100 |
| 4944219da107f9ed1daccef5 | 0.0 / 0 / 100 | None | 100 |
| ac46789a7ebda9982aebd343 | 0.0 / 0 / 100 | None | 100 |
| ccf4e4f1fca14a048eecd38f | 0.0 / 0 / 100 | None | 100 |
| 6c9ac68dd90eb2d39d339b6a | 0.0 / 0 / 100 | None | 100 |
| 672b5b4a7ea9b83b8668fbe2 | 0.0 / 0 / 100 | None | 100 |
| b8f1ca491f4e29db862af920 | 0.0 / 0 / 100 | None | 100 |
| 5efb497774b3f4f9ad8e7f7d | 0.0 / 0 / 100 | None | 100 |
| 47ee96bcecb134f64286c958 | 0.0 / 0 / 100 | None | 100 |
| a18ee644e09c84652cc9582a | 0.0 / 0 / 100 | None | 100 |
| 509cd28130eb44d35b27d08a | 0.0 / 0 / 100 | None | 100 |
| a8a5ddc06de26a9885f75fe9 | 0.0 / 0 / 100 | None | 100 |
| 5f818373c34233809fc57716 | 0.0 / 0 / 100 | None | 100 |
| baa8eccee6a4f8c27c11a09c | 0.0 / 0 / 100 | None | 100 |
| 2a91e17773f7272dbd36a048 | 0.0 / 0 / 100 | None | 100 |
| d0a5df19a69792ac87a703dc | 0.0 / 0 / 100 | None | 100 |
| 6d6930dcd4fe737e4d1ef3ed | 0.0 / 0 / 100 | None | 100 |
| cf9c6af6097c6d96c9a5a1d3 | 0.0 / 0 / 100 | None | 100 |
| 7317081e2468dfeeed3e4cc7 | 0.0 / 0 / 100 | None | 100 |
| ed2fff6199cac50f8e3c05d9 | 0.0 / 0 / 100 | None | 100 |
| 5d52bba4bd205ffecf96212a | 0.0 / 0 / 100 | None | 100 |
| e82412060e54893dc307a45e | 0.0 / 0 / 100 | None | 100 |
| b42dfb1e539cb4645127e844 | 0.0 / 0 / 100 | None | 100 |
| 2fe9909dbaad17941716efc9 | 0.0 / 0 / 100 | None | 100 |
| e45d4b2c01fc48117d5abec8 | 0.0 / 0 / 100 | None | 100 |
| 978f353680dde68625399775 | 0.0 / 0 / 100 | None | 100 |
| cdc8a1fbbb43d1f1ba93a366 | 0.0 / 0 / 100 | None | 100 |
| 3126d7f4d6378f131a26c41d | 0.0 / 0 / 100 | None | 100 |
| 48f56fbee8eed89fe5598934 | 0.0 / 0 / 100 | None | 100 |
| 18cef3e100afe2f32847ac27 | 0.0 / 0 / 100 | None | 100 |
| f67e77a0b124376f29b78302 | 0.0 / 0 / 100 | None | 100 |
| 7ab5a2ba2ca2072d49c86da9 | 0.0 / 0 / 100 | None | 100 |
| ea3b0653f085cf535854d1b8 | 0.0 / 0 / 100 | None | 100 |
| 8905e452833b0a01defd8b1e | 0.0 / 0 / 100 | None | 100 |
| 28555ca1e3c1d3ab551385b1 | 0.0 / 0 / 100 | None | 100 |
| 861414ea84239f8471f0ade8 | 0.0 / 0 / 100 | None | 100 |
| 1f19207d799d9bcd0b005ef9 | 0.0 / 0 / 100 | None | 100 |
| ad007b170a6bbf5bc88d182d | 0.0 / 0 / 100 | None | 100 |
| 94488c6aa407c3ea167ea51d | 0.0 / 0 / 100 | None | 100 |
| e6a5e4cd9fbe73077175c7b9 | 0.0 / 0 / 100 | None | 100 |
| bca38cd4398e1159ed781bff | 0.0 / 0 / 100 | None | 100 |
| 68da09e4a00f4fe8d8b054fd | 0.0 / 0 / 100 | None | 100 |
| da666451073f38000c71b39f | 0.0 / 0 / 100 | None | 100 |
| 57b0ace8ad261f0963cece6e | 0.0 / 0 / 100 | None | 100 |
| b1be521b209066effb830ad1 | 0.0 / 0 / 100 | None | 100 |
| d246da52d2783b0000af34aa | 0.0 / 0 / 100 | None | 100 |
| 9ac1596b4a83bfd3759110f5 | 0.0 / 0 / 100 | None | 100 |
| d3e7acfb899406015f6d7e6a | 0.0 / 0 / 100 | None | 100 |
| 1b91b6d6beb187aaf9103cdc | 0.0 / 0 / 100 | None | 100 |
| 9a600f5f46fa47c339ccb4d1 | 0.0 / 0 / 100 | None | 100 |
| 635bac1c845730dae487891a | 0.0 / 0 / 100 | None | 100 |
| 031ae1822109079d3cddb520 | 0.0 / 0 / 100 | None | 100 |
| 3435ab1a884c517b32867161 | 0.0 / 0 / 100 | None | 100 |
| 09d4451a2a5b030d1853c267 | 0.0 / 0 / 100 | None | 100 |
| fa309fa719c353f20a813699 | 0.0 / 0 / 100 | None | 100 |
| 03ee79b7cf8d02ddb7baeea3 | 0.0 / 0 / 100 | None | 100 |
| 37aa09141ddb4b6e8f93f647 | 0.0 / 0 / 100 | None | 100 |
| c14b2b630688912a588e1cf3 | 0.0 / 0 / 100 | None | 100 |
| 2eda7453d476d16c07a327ed | 0.0 / 0 / 100 | None | 100 |
| 9a29639c43e873eec6a7d1ac | 0.0 / 0 / 100 | None | 100 |
| 0362b36136a70031c319de5f | 0.0 / 0 / 100 | None | 100 |
| 9397f85898818d3dc9d04c1e | 0.0 / 0 / 100 | None | 100 |
| 4c1b2ab65e6ba3e75ac9b10a | 0.0 / 0 / 100 | None | 100 |
| d679f4cef5e7a847d5f6dc80 | 0.0 / 0 / 100 | None | 100 |
| f19cc29f17b93bb9cbbd5f1a | 0.0 / 0 / 100 | None | 100 |
| e654a69635e2e4a1bcc2903b | 0.0 / 0 / 100 | None | 100 |
| 508b709256adff820b7fdf82 | 0.0 / 0 / 100 | None | 100 |
| 0ebaffd3a3e8d10252da8bd5 | 0.0 / 0 / 100 | None | 100 |
| 6f8cac15c1ed9dd1fb79b212 | 0.0 / 0 / 100 | None | 100 |
| 302070707affaaec2265e772 | 0.0 / 0 / 100 | None | 100 |
| 74feefbadad2b95947437ed6 | 0.0 / 0 / 100 | None | 100 |
| 982870b0fcc4a8bef4a297af | 0.0 / 0 / 100 | None | 100 |
| 2e5068d168160234340d32fa | 0.0 / 0 / 100 | None | 100 |
| f642d1e953d4e4b42c9a916e | 0.0 / 0 / 100 | None | 100 |
| d7884b1e2a9c1c3790535590 | 0.0 / 0 / 100 | None | 100 |
| 8499903e83df71431114aaa8 | 0.0 / 0 / 100 | None | 100 |
| 272db4c9310a73f01bf46d4b | 0.0 / 0 / 100 | None | 100 |
| 9f020616201afdc368d77f9b | 0.0 / 0 / 100 | None | 100 |
| 26318156d310334e8b260e87 | 0.0 / 0 / 100 | None | 100 |
| d7241b9882514c2709082321 | 0.0 / 0 / 100 | None | 100 |
| a5b3de3764680273ff4760e1 | 0.0 / 0 / 100 | None | 100 |
| e5c2ea10bc6ce298f6065199 | 0.0 / 0 / 100 | None | 100 |
| 847f33277d9d89fe17482367 | 0.0 / 0 / 100 | None | 100 |
| 77568a85e217721985cd8ea4 | 0.0 / 0 / 100 | None | 100 |
| 793ee3d9708b970c08a0fbe2 | 0.0 / 0 / 100 | None | 100 |
| 129251f55876e9cdc9e907a6 | 0.0 / 0 / 100 | None | 100 |
| 40059b37d028ec2cd587bbb1 | 0.0 / 0 / 100 | None | 100 |
| 30756d73095e1914cf757782 | 0.0 / 0 / 100 | None | 100 |
| d74e8582f780dfdeb9281671 | 0.0 / 0 / 100 | None | 100 |
| 88dfe1aa76490ae40e93f05f | 0.0 / 0 / 100 | None | 100 |
| 9adac77b91eae4f8ea4d8df2 | 0.0 / 0 / 100 | None | 100 |
| bbbda4ebfb279ed21179678b | 0.0 / 0 / 100 | None | 100 |
| 34f5fb1acf8d86a8a7a94e1c | 0.0 / 0 / 100 | None | 100 |
| c9dc2d0cfe6d53ccdef2f1ef | 0.0 / 0 / 100 | None | 100 |
| 22b85c86caaee83341968cec | 0.0 / 0 / 100 | None | 100 |
| 1a27fc67e8978362681b5d20 | 0.0 / 0 / 100 | None | 100 |
| f9ebb0802bd50e68ec18fcb0 | 0.0 / 0 / 100 | None | 100 |
| be9a4b3ce1acb50722ae8614 | 0.0 / 0 / 100 | None | 100 |
| 5c5511653f8d590c63a39794 | 0.0 / 0 / 100 | None | 100 |
| 7cbec59a4f05afaa8ebed3fb | 0.0 / 0 / 100 | None | 100 |
| b1a17c1fb747eef11f253278 | 0.0 / 0 / 100 | None | 100 |
| edb61534cb4ec7a4187ebbdb | 0.0 / 0 / 100 | None | 100 |
| 78360f37e3cd5a3eb5cc2b3e | 0.0 / 0 / 100 | None | 100 |
| 46d6404412a25fbdd2965880 | 0.0 / 0 / 100 | None | 100 |
| 50af2a28b866c26021d83b01 | 0.0 / 0 / 100 | None | 100 |
| 22a5ac50d5ca3c952b8b1e34 | 0.0 / 0 / 100 | None | 100 |
| 7d93e4d997ec1f974bb6c71a | 0.0 / 0 / 100 | None | 100 |
| 0f466b21fb4514acd9d1ff1e | 0.0 / 0 / 100 | None | 100 |
| 151bacf1f85b74f88864784e | 0.0 / 0 / 100 | None | 100 |
| 330479ee3f94e169b8496e0b | 0.0 / 0 / 100 | None | 100 |
| e4019672011694d495923c6f | 0.0 / 0 / 100 | None | 100 |
| bf89e6ad180b60ad56c35a7e | 0.0 / 0 / 100 | None | 100 |
| 70aacd394ef41b887377260a | 0.0 / 0 / 100 | None | 100 |
| b3f4ad21a596171a9a43e0aa | 0.0 / 0 / 100 | None | 100 |
| 6885c03ed3db8fb41a5e20dd | 0.0 / 0 / 100 | None | 100 |
| 9a22bb61d6e0f49880a936a3 | 0.0 / 0 / 100 | None | 100 |
| eafb85daf9dfc6661b0bc2d8 | 0.0 / 0 / 100 | None | 100 |
| f3375c98045e9e28a348b9d0 | 0.0 / 0 / 100 | None | 100 |
| d62c99156470a7900dc43bc6 | 0.0 / 0 / 100 | None | 100 |
| fa0defe230fa592c6e1395ce | 0.0 / 0 / 100 | None | 100 |
| 9d8fa010baff9d2225fff4d4 | 0.0 / 0 / 100 | None | 100 |
| d059ce23baa1380031ffc8cb | 0.0 / 0 / 100 | None | 100 |
| 058509628604e5ca4527273b | 0.0 / 0 / 100 | None | 100 |
| 165be2e488d7d1013b36ff1b | 0.0 / 0 / 100 | None | 100 |
| 6c498709f6484559ef4e1e7f | 0.0 / 0 / 100 | None | 100 |
| 789321f88cd80b79c41108d3 | 0.0 / 0 / 100 | None | 100 |
| 58f67f71157df294642d7924 | 0.0 / 0 / 100 | None | 100 |
| f434980db097ed5dc29aa6b8 | 0.0 / 0 / 100 | None | 100 |
| 0eadfbc9b2c2899d71a5dcee | 0.0 / 0 / 100 | None | 100 |
| 509562eef48054a3aeac166a | 0.0 / 0 / 100 | None | 100 |
| 8515821d35005362bf80ca86 | 0.0 / 0 / 100 | None | 100 |
| ce81522f547c386fa9c08c2b | 0.0 / 0 / 100 | None | 100 |
| 67fbcd1e5ac9b7dcb8f292b9 | 0.0 / 0 / 100 | None | 100 |
| 90334bd842b032c804251295 | 0.0 / 0 / 100 | None | 100 |
| 62cd670d3fc0e07b1d6ff2d7 | 0.0 / 0 / 100 | None | 100 |
| c2a654d2b5c10bec5b192bd4 | 0.0 / 0 / 100 | None | 100 |
| e513b37dc4ee2ea0c2ec9a4a | 0.0 / 0 / 100 | None | 100 |
| 5605235e2ed700e3724eec66 | 0.0 / 0 / 100 | None | 100 |
| caef53a035b7c9e1ee694a16 | 0.0 / 0 / 100 | None | 100 |
| 3e16fbe7ff4d0e5b55e6d9d1 | 0.0 / 0 / 100 | None | 100 |
| 66c77006152a19f5b1a397d3 | 0.0 / 0 / 100 | None | 100 |
| 6837bb994c30db520b1c50f5 | 0.0 / 0 / 100 | None | 100 |
| 4d261cc6ea3f349110835054 | 0.0 / 0 / 100 | None | 100 |
| b42ba0f2b0ed1a420be6ddb5 | 0.0 / 0 / 100 | None | 100 |
| 10d0d6ef3ebaeeab62506369 | 0.0 / 0 / 100 | None | 100 |
| 2fcaaa6515b6d07526750ec2 | 0.0 / 0 / 100 | None | 100 |
| 19a7255c9f6a76e216f4f3d3 | 0.0 / 0 / 100 | None | 100 |
| 875c812006d2f01a6a67e48b | 0.0 / 0 / 100 | None | 100 |
| 29c34b1e7fff719ad0530aaf | 0.0 / 0 / 100 | None | 100 |
| 4c03d7d4cf05c04e6563204a | 0.0 / 0 / 100 | None | 100 |
| 56dad6836419abb22b9f3fc5 | 0.0 / 0 / 100 | None | 100 |
| 722a6e81428fe90b28522578 | 0.0 / 0 / 100 | None | 100 |
| 64474eaad780d3d0f127b333 | 0.0 / 0 / 100 | None | 100 |
| 50bfcf7f7c0f6341243f0890 | 0.0 / 0 / 100 | None | 100 |
| 203da3ce23c2826be75941f8 | 0.0 / 0 / 100 | None | 100 |
| 6b9269f85604bbde03fb8ae2 | 0.0 / 0 / 100 | None | 100 |
| 6e30cfe3525aa76f6c298840 | 0.0 / 0 / 100 | None | 100 |
| f5f8f6ab600ed0fff3f77575 | 0.0 / 0 / 100 | None | 100 |
| a1ebc798b3d3dffdcb755fea | 0.0 / 0 / 100 | None | 100 |
| 64083f876c4b931fac1666ac | 0.0 / 0 / 100 | None | 100 |
| 3f0d5de719c7c2fac0765ae9 | 0.0 / 0 / 100 | None | 100 |
| 02fbdb7be57f6759883cb7f7 | 0.0 / 0 / 100 | None | 100 |
| 2eafd0179259617282b6bfe4 | 0.0 / 0 / 100 | None | 100 |
| 62b13a164930d43ad696b359 | 0.0 / 0 / 100 | None | 100 |
| 048ddd95d61026dbf40fa6f9 | 0.0 / 0 / 100 | None | 100 |
| ea85d9daee87f0884e4f22e2 | 0.0 / 0 / 100 | None | 100 |
| 7e27f3fa1620b77e96f8da6f | 0.0 / 0 / 100 | None | 100 |
| 46cc8880d731fbee52076712 | 0.0 / 0 / 100 | None | 100 |
| 45c033c5bc044beea6f5562c | 0.0 / 0 / 100 | None | 100 |
| be96aaad5d4e1dd91747a116 | 0.0 / 0 / 100 | None | 100 |
| c28a7e48a1333e1bbbca134d | 0.0 / 0 / 100 | None | 100 |
| fda4c348dac5448fc10fd672 | 0.0 / 0 / 100 | None | 100 |
| 929c713ce993539177ad3985 | 0.0 / 0 / 100 | None | 100 |
| 47d567d51e4c0129ae905aa3 | 0.0 / 0 / 100 | None | 100 |
| 1a7b6658a55e4798f9674c67 | 0.0 / 0 / 100 | None | 100 |

Bounded equality compares each neighbour with its actual cap-off baseline. Missing planned slots remain missing; support-edit acquisition does not filter the denominator. This measures exact relation/template specificity, not semantic nearest-neighbour robustness.

Resource ceilings remain unadmitted. Macro unavailability and missing cell results cannot be read as passes.

Complete blocks mean terminal execution artifacts, not universal endpoint availability or scientific admission.
Missing pairs are not imputed; available-pair means remain diagnostics.
Three fresh realization clusters keep all five orders together; no iid-order claim.
Snapshot payloads and training inputs are not opened; reports and receipts establish analysis provenance.
DEC-069: preliminary decision summaries; no demonstrated 95% familywise control or established population effect. Secondary pointwise 95% t sensitivity assumes independent normal realization errors (df=2); it never changes classification.
nominal approximate bootstrap; three clusters do not establish exact familywise coverage
Accepted thresholds do not confer population, execution or final scientific admission.
Semantic revision is latest-answer success AND old-retired AND new-active; old acquisition is not an additional filter.
Per-cell occupancy equivalence has no independent realization-cluster interval; only complete three-realization macros can report that interval.
Option D leaves all MQuAKE 1000-edit primary comparisons unavailable in the unchanged 63-interval family. Actual 300-record rates are descriptive, without a transferred 1000-record threshold.


DEC-063 full validation at the final checkpoint (separate from the descriptive 128-window sample):

| Cell | Population | Scored / planned | Reference | Mean loss change | Mean KL | ES95 positive loss harm | Max positive loss harm | > .1 nat | Status |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| 61348508e40d54351613ab14 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00060518953 | unavailable | 0.014371213 | 2.3781729 | 14 | complete |
| 61348508e40d54351613ab14 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00060518953 | unavailable | 0.014371213 | 2.3781729 | 14 | complete |
| 61348508e40d54351613ab14 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0027886766 | unavailable | 0.059229618 | 8.3038369 | 31 | complete |
| 61348508e40d54351613ab14 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0027886766 | unavailable | 0.059229618 | 8.3038369 | 31 | complete |
| 61348508e40d54351613ab14 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 61348508e40d54351613ab14 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 61348508e40d54351613ab14 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 61348508e40d54351613ab14 @ 1000 | full validation | 245237 / 245237 | original | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 88af67fa5945b642e8ba7974 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0014500679 | unavailable | 0.029001358 | 5.2361237 | 17 | complete |
| 88af67fa5945b642e8ba7974 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0014500679 | unavailable | 0.029001358 | 5.2361237 | 17 | complete |
| 88af67fa5945b642e8ba7974 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0023581813 | unavailable | 0.048995793 | 5.2504223 | 32 | complete |
| 88af67fa5945b642e8ba7974 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0023581813 | unavailable | 0.048995793 | 5.2504223 | 32 | complete |
| 88af67fa5945b642e8ba7974 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 88af67fa5945b642e8ba7974 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 88af67fa5945b642e8ba7974 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 88af67fa5945b642e8ba7974 @ 1000 | full validation | 245237 / 245237 | original | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 915f97b05f3fa2a81de09cdf @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0012129448 | unavailable | 0.025303535 | 4.2726762 | 14 | complete |
| 915f97b05f3fa2a81de09cdf @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0012129448 | unavailable | 0.025303535 | 4.2726762 | 14 | complete |
| 915f97b05f3fa2a81de09cdf @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0043000117 | unavailable | 0.090164415 | 8.3038369 | 38 | complete |
| 915f97b05f3fa2a81de09cdf @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0043000117 | unavailable | 0.090164415 | 8.3038369 | 38 | complete |
| 915f97b05f3fa2a81de09cdf @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 915f97b05f3fa2a81de09cdf @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 915f97b05f3fa2a81de09cdf @ 1000 | full validation | 245237 / 245237 | capoff | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 915f97b05f3fa2a81de09cdf @ 1000 | full validation | 245237 / 245237 | original | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 4aa4849ba414edab2504f56b @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0033992581 | unavailable | 0.069066699 | 6.5179742 | 32 | complete |
| 4aa4849ba414edab2504f56b @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0033992581 | unavailable | 0.069066699 | 6.5179742 | 32 | complete |
| 4aa4849ba414edab2504f56b @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0027200315 | unavailable | 0.054939739 | 3.3794758 | 28 | complete |
| 4aa4849ba414edab2504f56b @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0027200315 | unavailable | 0.054939739 | 3.3794758 | 28 | complete |
| 4aa4849ba414edab2504f56b @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 4aa4849ba414edab2504f56b @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 4aa4849ba414edab2504f56b @ 1000 | full validation | 245237 / 245237 | capoff | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 4aa4849ba414edab2504f56b @ 1000 | full validation | 245237 / 245237 | original | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 9ebc93cc7912bd5d1c929418 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00071389536 | unavailable | 0.014803671 | 4.3686376 | 9 | complete |
| 9ebc93cc7912bd5d1c929418 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00071389536 | unavailable | 0.014803671 | 4.3686376 | 9 | complete |
| 9ebc93cc7912bd5d1c929418 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0036824539 | unavailable | 0.074819721 | 8.3038369 | 40 | complete |
| 9ebc93cc7912bd5d1c929418 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0036824539 | unavailable | 0.074819721 | 8.3038369 | 40 | complete |
| 9ebc93cc7912bd5d1c929418 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 9ebc93cc7912bd5d1c929418 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0020836338 | unavailable | 0.042523047 | 5.0796499 | 29 | complete |
| 9ebc93cc7912bd5d1c929418 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| 9ebc93cc7912bd5d1c929418 @ 1000 | full validation | 245237 / 245237 | original | 0.0024502257 | 0.0023814924 | 0.051761248 | 9.2622675 | 374 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0011542168 | unavailable | 0.023098817 | 3.764314 | 9 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0011542168 | unavailable | 0.023098817 | 3.764314 | 9 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0085189339 | unavailable | 0.17698371 | 9.8429569 | 78 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0085189339 | unavailable | 0.17698371 | 9.8429569 | 78 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| ce0d0ffc2a58a60e27c460d9 @ 1000 | full validation | 245237 / 245237 | original | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 95dfb24c6361b2d38dd60e9b @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.002750378 | unavailable | 0.055708362 | 5.852038 | 27 | complete |
| 95dfb24c6361b2d38dd60e9b @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.002750378 | unavailable | 0.055708362 | 5.852038 | 27 | complete |
| 95dfb24c6361b2d38dd60e9b @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0088031851 | unavailable | 0.18228068 | 8.4883252 | 76 | complete |
| 95dfb24c6361b2d38dd60e9b @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0088031851 | unavailable | 0.18228068 | 8.4883252 | 76 | complete |
| 95dfb24c6361b2d38dd60e9b @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 95dfb24c6361b2d38dd60e9b @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 95dfb24c6361b2d38dd60e9b @ 1000 | full validation | 245237 / 245237 | capoff | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 95dfb24c6361b2d38dd60e9b @ 1000 | full validation | 245237 / 245237 | original | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 6d0915056b1e76d8ee8795ff @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0032711514 | unavailable | 0.071545968 | 5.6893358 | 44 | complete |
| 6d0915056b1e76d8ee8795ff @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0032711514 | unavailable | 0.071545968 | 5.6893358 | 44 | complete |
| 6d0915056b1e76d8ee8795ff @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0091760562 | unavailable | 0.19151389 | 8.4883252 | 98 | complete |
| 6d0915056b1e76d8ee8795ff @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0091760562 | unavailable | 0.19151389 | 8.4883252 | 98 | complete |
| 6d0915056b1e76d8ee8795ff @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 6d0915056b1e76d8ee8795ff @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 6d0915056b1e76d8ee8795ff @ 1000 | full validation | 245237 / 245237 | capoff | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 6d0915056b1e76d8ee8795ff @ 1000 | full validation | 245237 / 245237 | original | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 7c9675a69d832a772070cb2d @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0072936291 | unavailable | 0.14928489 | 7.1256136 | 66 | complete |
| 7c9675a69d832a772070cb2d @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0072936291 | unavailable | 0.14928489 | 7.1256136 | 66 | complete |
| 7c9675a69d832a772070cb2d @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0090332971 | unavailable | 0.18520523 | 6.4019389 | 88 | complete |
| 7c9675a69d832a772070cb2d @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0090332971 | unavailable | 0.18520523 | 6.4019389 | 88 | complete |
| 7c9675a69d832a772070cb2d @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 7c9675a69d832a772070cb2d @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 7c9675a69d832a772070cb2d @ 1000 | full validation | 245237 / 245237 | capoff | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 7c9675a69d832a772070cb2d @ 1000 | full validation | 245237 / 245237 | original | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 95016bc16e89cfcccccc40b8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0081826058 | unavailable | 0.16762493 | 7.3962588 | 79 | complete |
| 95016bc16e89cfcccccc40b8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0081826058 | unavailable | 0.16762493 | 7.3962588 | 79 | complete |
| 95016bc16e89cfcccccc40b8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010818272 | unavailable | 0.22624309 | 7.3962588 | 120 | complete |
| 95016bc16e89cfcccccc40b8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010818272 | unavailable | 0.22624309 | 7.3962588 | 120 | complete |
| 95016bc16e89cfcccccc40b8 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 95016bc16e89cfcccccc40b8 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0078744206 | unavailable | 0.16179203 | 9.2771998 | 55 | complete |
| 95016bc16e89cfcccccc40b8 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 95016bc16e89cfcccccc40b8 @ 1000 | full validation | 245237 / 245237 | original | 0.0058496258 | 0.0057653779 | 0.122014 | 15.381805 | 699 | complete |
| 43925e53c31860219a85ef90 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0052746464 | unavailable | 0.10549293 | 5.7541372 | 43 | complete |
| 43925e53c31860219a85ef90 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0052746464 | unavailable | 0.10549293 | 5.7541372 | 43 | complete |
| 43925e53c31860219a85ef90 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 43925e53c31860219a85ef90 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 43925e53c31860219a85ef90 @ 300 | full validation | 245237 / 245237 | capoff | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| 43925e53c31860219a85ef90 @ 300 | full validation | 245237 / 245237 | original | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| c29ee18fb21ba6b387ede6e8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0016745352 | unavailable | 0.035244587 | 3.9815192 | 13 | complete |
| c29ee18fb21ba6b387ede6e8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0016745352 | unavailable | 0.035244587 | 3.9815192 | 13 | complete |
| c29ee18fb21ba6b387ede6e8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| c29ee18fb21ba6b387ede6e8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| c29ee18fb21ba6b387ede6e8 @ 300 | full validation | 245237 / 245237 | capoff | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| c29ee18fb21ba6b387ede6e8 @ 300 | full validation | 245237 / 245237 | original | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| 54879da4dcdb0f106f98080a @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0022477573 | unavailable | 0.045706007 | 5.7541372 | 19 | complete |
| 54879da4dcdb0f106f98080a @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0022477573 | unavailable | 0.045706007 | 5.7541372 | 19 | complete |
| 54879da4dcdb0f106f98080a @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 54879da4dcdb0f106f98080a @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 54879da4dcdb0f106f98080a @ 300 | full validation | 245237 / 245237 | capoff | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| 54879da4dcdb0f106f98080a @ 300 | full validation | 245237 / 245237 | original | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| 78ebbc03946239c1d637154c @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.003906871 | unavailable | 0.078171682 | 5.5612209 | 30 | complete |
| 78ebbc03946239c1d637154c @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.003906871 | unavailable | 0.078171682 | 5.5612209 | 30 | complete |
| 78ebbc03946239c1d637154c @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 78ebbc03946239c1d637154c @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| 78ebbc03946239c1d637154c @ 300 | full validation | 245237 / 245237 | capoff | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| 78ebbc03946239c1d637154c @ 300 | full validation | 245237 / 245237 | original | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| b1d1e53944241333ec5603d4 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.006855084 | unavailable | 0.14028737 | 5.3917771 | 54 | complete |
| b1d1e53944241333ec5603d4 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.006855084 | unavailable | 0.14028737 | 5.3917771 | 54 | complete |
| b1d1e53944241333ec5603d4 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| b1d1e53944241333ec5603d4 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.010249587 | unavailable | 0.20953875 | 5.7541372 | 82 | complete |
| b1d1e53944241333ec5603d4 @ 300 | full validation | 245237 / 245237 | capoff | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| b1d1e53944241333ec5603d4 @ 300 | full validation | 245237 / 245237 | original | 0.007146158 | 0.0071233418 | 0.14612714 | 13.14428 | 847 | complete |
| f3dbf1a3d5860a628e7d68ef @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 5.1051865e-05 | unavailable | 0.0010210373 | 0.82989912 | 1 | complete |
| f3dbf1a3d5860a628e7d68ef @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 5.1051865e-05 | unavailable | 0.0010210373 | 0.82989912 | 1 | complete |
| f3dbf1a3d5860a628e7d68ef @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| f3dbf1a3d5860a628e7d68ef @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| f3dbf1a3d5860a628e7d68ef @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| f3dbf1a3d5860a628e7d68ef @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| f3dbf1a3d5860a628e7d68ef @ 1000 | full validation | 245237 / 245237 | capoff | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| f3dbf1a3d5860a628e7d68ef @ 1000 | full validation | 245237 / 245237 | original | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| be44dfb501724b72adcbd747 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| be44dfb501724b72adcbd747 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| be44dfb501724b72adcbd747 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| be44dfb501724b72adcbd747 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| be44dfb501724b72adcbd747 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| be44dfb501724b72adcbd747 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| be44dfb501724b72adcbd747 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| be44dfb501724b72adcbd747 @ 1000 | full validation | 245237 / 245237 | original | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| 5263d61e569d7cb4ceb4e617 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 5263d61e569d7cb4ceb4e617 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 5263d61e569d7cb4ceb4e617 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 5263d61e569d7cb4ceb4e617 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 5263d61e569d7cb4ceb4e617 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| 5263d61e569d7cb4ceb4e617 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| 5263d61e569d7cb4ceb4e617 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| 5263d61e569d7cb4ceb4e617 @ 1000 | full validation | 245237 / 245237 | original | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 3.9594633e-05 | unavailable | 0.00079189266 | 0.64365036 | 1 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 3.9594633e-05 | unavailable | 0.00079189266 | 0.64365036 | 1 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 1000 | full validation | 245237 / 245237 | capoff | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| 81b1e9cb4e216a6cd1cd565a @ 1000 | full validation | 245237 / 245237 | original | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| deb5f473d9ca2ed544926204 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| deb5f473d9ca2ed544926204 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| deb5f473d9ca2ed544926204 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| deb5f473d9ca2ed544926204 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00011343321 | unavailable | 0.0022686642 | 1.8439702 | 1 | complete |
| deb5f473d9ca2ed544926204 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| deb5f473d9ca2ed544926204 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016448507 | unavailable | 0.0032897015 | 1.8439702 | 2 | complete |
| deb5f473d9ca2ed544926204 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| deb5f473d9ca2ed544926204 @ 1000 | full validation | 245237 / 245237 | original | 0.0003165613 | 0.00031458449 | 0.0064926507 | 5.6608335 | 47 | complete |
| 0b6ade77641a02c1c85574b0 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.031422247 | unavailable | 0.63128373 | 11.727234 | 146 | complete |
| 0b6ade77641a02c1c85574b0 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.031422247 | unavailable | 0.63128373 | 11.727234 | 146 | complete |
| 0b6ade77641a02c1c85574b0 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.048302202 | unavailable | 0.97173773 | 11.914909 | 220 | complete |
| 0b6ade77641a02c1c85574b0 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.048302202 | unavailable | 0.97173773 | 11.914909 | 220 | complete |
| 0b6ade77641a02c1c85574b0 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 0b6ade77641a02c1c85574b0 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 0b6ade77641a02c1c85574b0 @ 1000 | full validation | 245237 / 245237 | capoff | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| 0b6ade77641a02c1c85574b0 @ 1000 | full validation | 245237 / 245237 | original | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| ee67c592789829e7dd808ede @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.032813634 | unavailable | 0.66191022 | 12.607352 | 161 | complete |
| ee67c592789829e7dd808ede @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.032813634 | unavailable | 0.66191022 | 12.607352 | 161 | complete |
| ee67c592789829e7dd808ede @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.042997994 | unavailable | 0.86926098 | 12.607352 | 227 | complete |
| ee67c592789829e7dd808ede @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.042997994 | unavailable | 0.86926098 | 12.607352 | 227 | complete |
| ee67c592789829e7dd808ede @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| ee67c592789829e7dd808ede @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| ee67c592789829e7dd808ede @ 1000 | full validation | 245237 / 245237 | capoff | 0.059531222 | 0.059780575 | 1.2031896 | 20.283375 | 4367 | complete |
| ee67c592789829e7dd808ede @ 1000 | full validation | 245237 / 245237 | original | 0.059531222 | 0.059780575 | 1.2031896 | 20.283375 | 4367 | complete |
| 8be432675ed4dc57f9108bd4 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.03203226 | unavailable | 0.64474268 | 10.888352 | 150 | complete |
| 8be432675ed4dc57f9108bd4 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.03203226 | unavailable | 0.64474268 | 10.888352 | 150 | complete |
| 8be432675ed4dc57f9108bd4 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.042999812 | unavailable | 0.86385745 | 12.277192 | 219 | complete |
| 8be432675ed4dc57f9108bd4 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.042999812 | unavailable | 0.86385745 | 12.277192 | 219 | complete |
| 8be432675ed4dc57f9108bd4 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 8be432675ed4dc57f9108bd4 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 8be432675ed4dc57f9108bd4 @ 1000 | full validation | 245237 / 245237 | capoff | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| 8be432675ed4dc57f9108bd4 @ 1000 | full validation | 245237 / 245237 | original | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| 78928f2782d91d888ef24d52 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.031183226 | unavailable | 0.63681872 | 11.699989 | 182 | complete |
| 78928f2782d91d888ef24d52 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.031183226 | unavailable | 0.63681872 | 11.699989 | 182 | complete |
| 78928f2782d91d888ef24d52 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.05140361 | unavailable | 1.0412286 | 12.607352 | 252 | complete |
| 78928f2782d91d888ef24d52 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.05140361 | unavailable | 1.0412286 | 12.607352 | 252 | complete |
| 78928f2782d91d888ef24d52 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 78928f2782d91d888ef24d52 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| 78928f2782d91d888ef24d52 @ 1000 | full validation | 245237 / 245237 | capoff | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| 78928f2782d91d888ef24d52 @ 1000 | full validation | 245237 / 245237 | original | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| de785feed05c9f4c2a9e9273 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.033036099 | unavailable | 0.66226331 | 11.841653 | 149 | complete |
| de785feed05c9f4c2a9e9273 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.033036099 | unavailable | 0.66226331 | 11.841653 | 149 | complete |
| de785feed05c9f4c2a9e9273 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.045555172 | unavailable | 0.91622473 | 10.690014 | 225 | complete |
| de785feed05c9f4c2a9e9273 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.045555172 | unavailable | 0.91622473 | 10.690014 | 225 | complete |
| de785feed05c9f4c2a9e9273 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| de785feed05c9f4c2a9e9273 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.061502422 | unavailable | 1.2381624 | 12.607352 | 297 | complete |
| de785feed05c9f4c2a9e9273 @ 1000 | full validation | 245237 / 245237 | capoff | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| de785feed05c9f4c2a9e9273 @ 1000 | full validation | 245237 / 245237 | original | 0.059526304 | 0.059779341 | 1.2031759 | 20.283375 | 4366 | complete |
| de0b9612418e6d573ed77679 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.011537661 | unavailable | 0.23423103 | 11.687154 | 54 | complete |
| de0b9612418e6d573ed77679 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.011537661 | unavailable | 0.23423103 | 11.687154 | 54 | complete |
| de0b9612418e6d573ed77679 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| de0b9612418e6d573ed77679 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| de0b9612418e6d573ed77679 @ 300 | full validation | 245237 / 245237 | capoff | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| de0b9612418e6d573ed77679 @ 300 | full validation | 245237 / 245237 | original | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| be37e2a1ff4a079e56efe268 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.011381864 | unavailable | 0.22826339 | 11.687154 | 60 | complete |
| be37e2a1ff4a079e56efe268 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.011381864 | unavailable | 0.22826339 | 11.687154 | 60 | complete |
| be37e2a1ff4a079e56efe268 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| be37e2a1ff4a079e56efe268 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| be37e2a1ff4a079e56efe268 @ 300 | full validation | 245237 / 245237 | capoff | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| be37e2a1ff4a079e56efe268 @ 300 | full validation | 245237 / 245237 | original | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| 1e6b766c4139230c18547234 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.011514882 | unavailable | 0.23091899 | 9.8120323 | 58 | complete |
| 1e6b766c4139230c18547234 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.011514882 | unavailable | 0.23091899 | 9.8120323 | 58 | complete |
| 1e6b766c4139230c18547234 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| 1e6b766c4139230c18547234 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| 1e6b766c4139230c18547234 @ 300 | full validation | 245237 / 245237 | capoff | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| 1e6b766c4139230c18547234 @ 300 | full validation | 245237 / 245237 | original | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| c0a54c5fbf1ce7776efc983e @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.011825651 | unavailable | 0.23818965 | 8.4620823 | 63 | complete |
| c0a54c5fbf1ce7776efc983e @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.011825651 | unavailable | 0.23818965 | 8.4620823 | 63 | complete |
| c0a54c5fbf1ce7776efc983e @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| c0a54c5fbf1ce7776efc983e @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| c0a54c5fbf1ce7776efc983e @ 300 | full validation | 245237 / 245237 | capoff | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| c0a54c5fbf1ce7776efc983e @ 300 | full validation | 245237 / 245237 | original | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| 7499c19b813dcada2c67ae39 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.011657932 | unavailable | 0.23463526 | 10.771768 | 60 | complete |
| 7499c19b813dcada2c67ae39 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.011657932 | unavailable | 0.23463526 | 10.771768 | 60 | complete |
| 7499c19b813dcada2c67ae39 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| 7499c19b813dcada2c67ae39 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.015110593 | unavailable | 0.30424239 | 8.0593725 | 81 | complete |
| 7499c19b813dcada2c67ae39 @ 300 | full validation | 245237 / 245237 | capoff | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| 7499c19b813dcada2c67ae39 @ 300 | full validation | 245237 / 245237 | original | 0.012047224 | 0.012176251 | 0.24381518 | 15.072163 | 1001 | complete |
| 39c7fd4929721e8dcba56b94 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00015944504 | unavailable | 0.0031977855 | 1.4534526 | 4 | complete |
| 39c7fd4929721e8dcba56b94 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00015944504 | unavailable | 0.0031977855 | 1.4534526 | 4 | complete |
| 39c7fd4929721e8dcba56b94 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00055035064 | unavailable | 0.011920196 | 2.0409525 | 13 | complete |
| 39c7fd4929721e8dcba56b94 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00055035064 | unavailable | 0.011920196 | 2.0409525 | 13 | complete |
| 39c7fd4929721e8dcba56b94 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0010122706 | unavailable | 0.021696881 | 13.862511 | 7 | complete |
| 39c7fd4929721e8dcba56b94 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0010122706 | unavailable | 0.021696881 | 13.862511 | 7 | complete |
| 39c7fd4929721e8dcba56b94 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0008603807 | 0.0011643033 | 0.021301378 | 25.85926 | 173 | complete |
| 39c7fd4929721e8dcba56b94 @ 1000 | full validation | 245237 / 245237 | original | 0.0008603807 | 0.0011643033 | 0.021301378 | 25.85926 | 173 | complete |
| b887b1046cd563d990765e01 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00010565027 | unavailable | 0.004294276 | 1.4534526 | 5 | complete |
| b887b1046cd563d990765e01 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00010565027 | unavailable | 0.004294276 | 1.4534526 | 5 | complete |
| b887b1046cd563d990765e01 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00022791166 | unavailable | 0.0057430337 | 1.9905819 | 4 | complete |
| b887b1046cd563d990765e01 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00022791166 | unavailable | 0.0057430337 | 1.9905819 | 4 | complete |
| b887b1046cd563d990765e01 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0013334171 | unavailable | 0.029779113 | 13.862511 | 20 | complete |
| b887b1046cd563d990765e01 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0013334171 | unavailable | 0.029779113 | 13.862511 | 20 | complete |
| b887b1046cd563d990765e01 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0015523108 | 0.0018517223 | 0.037970137 | 27.684165 | 314 | complete |
| b887b1046cd563d990765e01 @ 1000 | full validation | 245237 / 245237 | original | 0.0015523108 | 0.0018517223 | 0.037970137 | 27.684165 | 314 | complete |
| 435235a6719279d1cc87ad66 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00038740288 | unavailable | 0.009677421 | 4.9830427 | 5 | complete |
| 435235a6719279d1cc87ad66 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00038740288 | unavailable | 0.009677421 | 4.9830427 | 5 | complete |
| 435235a6719279d1cc87ad66 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00018707256 | unavailable | 0.0044600857 | 2.0555823 | 6 | complete |
| 435235a6719279d1cc87ad66 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00018707256 | unavailable | 0.0044600857 | 2.0555823 | 6 | complete |
| 435235a6719279d1cc87ad66 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0013229201 | unavailable | 0.028218505 | 13.862511 | 13 | complete |
| 435235a6719279d1cc87ad66 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0013229201 | unavailable | 0.028218505 | 13.862511 | 13 | complete |
| 435235a6719279d1cc87ad66 @ 1000 | full validation | 245237 / 245237 | capoff | 0.00064632908 | 0.00080141937 | 0.01679148 | 25.85926 | 180 | complete |
| 435235a6719279d1cc87ad66 @ 1000 | full validation | 245237 / 245237 | original | 0.00064632908 | 0.00080141937 | 0.01679148 | 25.85926 | 180 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00055311281 | unavailable | 0.01166093 | 4.9830427 | 9 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00055311281 | unavailable | 0.01166093 | 4.9830427 | 9 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00020825418 | unavailable | 0.0066543583 | 0.9910442 | 17 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00020825418 | unavailable | 0.0066543583 | 0.9910442 | 17 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0013289477 | unavailable | 0.027343477 | 13.862511 | 13 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0013289477 | unavailable | 0.027343477 | 13.862511 | 13 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 1000 | full validation | 245237 / 245237 | capoff | 0.0012061371 | 0.0014536399 | 0.028866078 | 27.684165 | 206 | complete |
| aaed1cf9e8ce7cf1cf3749fa @ 1000 | full validation | 245237 / 245237 | original | 0.0012061371 | 0.0014536399 | 0.028866078 | 27.684165 | 206 | complete |
| 92a5ef6855124ffc5a8d6163 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00016142473 | unavailable | 0.0032627229 | 2.0409525 | 3 | complete |
| 92a5ef6855124ffc5a8d6163 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00016142473 | unavailable | 0.0032627229 | 2.0409525 | 3 | complete |
| 92a5ef6855124ffc5a8d6163 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.00059843537 | unavailable | 0.012340987 | 2.284038 | 11 | complete |
| 92a5ef6855124ffc5a8d6163 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.00059843537 | unavailable | 0.012340987 | 2.284038 | 11 | complete |
| 92a5ef6855124ffc5a8d6163 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0.0010890892 | unavailable | 0.022133611 | 13.862511 | 11 | complete |
| 92a5ef6855124ffc5a8d6163 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0.0010890892 | unavailable | 0.022133611 | 13.862511 | 11 | complete |
| 92a5ef6855124ffc5a8d6163 @ 1000 | full validation | 245237 / 245237 | capoff | 0.0011674287 | 0.0015361708 | 0.027218677 | 27.684165 | 175 | complete |
| 92a5ef6855124ffc5a8d6163 @ 1000 | full validation | 245237 / 245237 | original | 0.0011674287 | 0.0015361708 | 0.027218677 | 27.684165 | 175 | complete |
| baa601113af675024e73bc30 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 1000 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| baa601113af675024e73bc30 @ 1000 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 1000 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| b6b271f3383f85fb19e49836 @ 1000 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 1000 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| 6c0124a2d35b8b4bf8d2a321 @ 1000 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 1000 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| 37c2ba2be995719ac8972cf1 @ 1000 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 1000 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 1000 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| d93ed5de9d4401cb3345c7bd @ 1000 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 300 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| c2f9d3102987f746f4f31b8d @ 300 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 300 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| a23ae9063b37c21cfe657d47 @ 300 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 300 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| 5a6f61e06de0bca53b4a7377 @ 300 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 300 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| 03426d6e61fb6b41145c5d8e @ 300 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 100 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | capoff | 0 | unavailable | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 300 | 128-window sample (descriptive) | 16256 / 16256 | original | 0 | unavailable | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 300 | full validation | 245237 / 245237 | capoff | 0 | 0 | 0 | 0 | 0 | complete |
| 19f5d8535235334ffe1595e8 @ 300 | full validation | 245237 / 245237 | original | 0 | 0 | 0 | 0 | 0 | complete |

Sampled and full populations are separate; KL is retained only for the full assay. JSON includes ES99 and all .01/.1/1-nat exceedances for both populations. Full-validation absence or invalid vectors do not acquire scientific admission.

DEC-064 cap fidelity: secondary benchmarks; failure does not veto primary comparisons.

| Cell | Reference | Mean KL | KL ≤.001 | Mean signed NLL increase | NLL ≤.01 | Availability |
|---|---|---:|---|---:|---|---|
| 61348508e40d54351613ab14 | capoff | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 61348508e40d54351613ab14 | original | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 88af67fa5945b642e8ba7974 | capoff | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 88af67fa5945b642e8ba7974 | original | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 915f97b05f3fa2a81de09cdf | capoff | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 915f97b05f3fa2a81de09cdf | original | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 4aa4849ba414edab2504f56b | capoff | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 4aa4849ba414edab2504f56b | original | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 9ebc93cc7912bd5d1c929418 | capoff | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| 9ebc93cc7912bd5d1c929418 | original | 0.0023814924 | fail | 0.0024502257 | pass | complete |
| ce0d0ffc2a58a60e27c460d9 | capoff | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| ce0d0ffc2a58a60e27c460d9 | original | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 95dfb24c6361b2d38dd60e9b | capoff | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 95dfb24c6361b2d38dd60e9b | original | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 6d0915056b1e76d8ee8795ff | capoff | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 6d0915056b1e76d8ee8795ff | original | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 7c9675a69d832a772070cb2d | capoff | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 7c9675a69d832a772070cb2d | original | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 95016bc16e89cfcccccc40b8 | capoff | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 95016bc16e89cfcccccc40b8 | original | 0.0057653779 | fail | 0.0058496258 | pass | complete |
| 43925e53c31860219a85ef90 | capoff | 0.0071233418 | fail | 0.007146158 | pass | complete |
| 43925e53c31860219a85ef90 | original | 0.0071233418 | fail | 0.007146158 | pass | complete |
| c29ee18fb21ba6b387ede6e8 | capoff | 0.0071233418 | fail | 0.007146158 | pass | complete |
| c29ee18fb21ba6b387ede6e8 | original | 0.0071233418 | fail | 0.007146158 | pass | complete |
| 54879da4dcdb0f106f98080a | capoff | 0.0071233418 | fail | 0.007146158 | pass | complete |
| 54879da4dcdb0f106f98080a | original | 0.0071233418 | fail | 0.007146158 | pass | complete |
| 78ebbc03946239c1d637154c | capoff | 0.0071233418 | fail | 0.007146158 | pass | complete |
| 78ebbc03946239c1d637154c | original | 0.0071233418 | fail | 0.007146158 | pass | complete |
| b1d1e53944241333ec5603d4 | capoff | 0.0071233418 | fail | 0.007146158 | pass | complete |
| b1d1e53944241333ec5603d4 | original | 0.0071233418 | fail | 0.007146158 | pass | complete |
| f3dbf1a3d5860a628e7d68ef | capoff | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| f3dbf1a3d5860a628e7d68ef | original | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| be44dfb501724b72adcbd747 | capoff | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| be44dfb501724b72adcbd747 | original | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| 5263d61e569d7cb4ceb4e617 | capoff | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| 5263d61e569d7cb4ceb4e617 | original | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| 81b1e9cb4e216a6cd1cd565a | capoff | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| 81b1e9cb4e216a6cd1cd565a | original | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| deb5f473d9ca2ed544926204 | capoff | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| deb5f473d9ca2ed544926204 | original | 0.00031458449 | pass | 0.0003165613 | pass | complete |
| 0b6ade77641a02c1c85574b0 | capoff | 0.059779341 | fail | 0.059526304 | fail | complete |
| 0b6ade77641a02c1c85574b0 | original | 0.059779341 | fail | 0.059526304 | fail | complete |
| ee67c592789829e7dd808ede | capoff | 0.059780575 | fail | 0.059531222 | fail | complete |
| ee67c592789829e7dd808ede | original | 0.059780575 | fail | 0.059531222 | fail | complete |
| 8be432675ed4dc57f9108bd4 | capoff | 0.059779341 | fail | 0.059526304 | fail | complete |
| 8be432675ed4dc57f9108bd4 | original | 0.059779341 | fail | 0.059526304 | fail | complete |
| 78928f2782d91d888ef24d52 | capoff | 0.059779341 | fail | 0.059526304 | fail | complete |
| 78928f2782d91d888ef24d52 | original | 0.059779341 | fail | 0.059526304 | fail | complete |
| de785feed05c9f4c2a9e9273 | capoff | 0.059779341 | fail | 0.059526304 | fail | complete |
| de785feed05c9f4c2a9e9273 | original | 0.059779341 | fail | 0.059526304 | fail | complete |
| de0b9612418e6d573ed77679 | capoff | 0.012176251 | fail | 0.012047224 | fail | complete |
| de0b9612418e6d573ed77679 | original | 0.012176251 | fail | 0.012047224 | fail | complete |
| be37e2a1ff4a079e56efe268 | capoff | 0.012176251 | fail | 0.012047224 | fail | complete |
| be37e2a1ff4a079e56efe268 | original | 0.012176251 | fail | 0.012047224 | fail | complete |
| 1e6b766c4139230c18547234 | capoff | 0.012176251 | fail | 0.012047224 | fail | complete |
| 1e6b766c4139230c18547234 | original | 0.012176251 | fail | 0.012047224 | fail | complete |
| c0a54c5fbf1ce7776efc983e | capoff | 0.012176251 | fail | 0.012047224 | fail | complete |
| c0a54c5fbf1ce7776efc983e | original | 0.012176251 | fail | 0.012047224 | fail | complete |
| 7499c19b813dcada2c67ae39 | capoff | 0.012176251 | fail | 0.012047224 | fail | complete |
| 7499c19b813dcada2c67ae39 | original | 0.012176251 | fail | 0.012047224 | fail | complete |
| 39c7fd4929721e8dcba56b94 | capoff | 0.0011643033 | fail | 0.0008603807 | pass | complete |
| 39c7fd4929721e8dcba56b94 | original | 0.0011643033 | fail | 0.0008603807 | pass | complete |
| b887b1046cd563d990765e01 | capoff | 0.0018517223 | fail | 0.0015523108 | pass | complete |
| b887b1046cd563d990765e01 | original | 0.0018517223 | fail | 0.0015523108 | pass | complete |
| 435235a6719279d1cc87ad66 | capoff | 0.00080141937 | pass | 0.00064632908 | pass | complete |
| 435235a6719279d1cc87ad66 | original | 0.00080141937 | pass | 0.00064632908 | pass | complete |
| aaed1cf9e8ce7cf1cf3749fa | capoff | 0.0014536399 | fail | 0.0012061371 | pass | complete |
| aaed1cf9e8ce7cf1cf3749fa | original | 0.0014536399 | fail | 0.0012061371 | pass | complete |
| 92a5ef6855124ffc5a8d6163 | capoff | 0.0015361708 | fail | 0.0011674287 | pass | complete |
| 92a5ef6855124ffc5a8d6163 | original | 0.0015361708 | fail | 0.0011674287 | pass | complete |
| baa601113af675024e73bc30 | capoff | 0 | pass | 0 | pass | complete |
| baa601113af675024e73bc30 | original | 0 | pass | 0 | pass | complete |
| b6b271f3383f85fb19e49836 | capoff | 0 | pass | 0 | pass | complete |
| b6b271f3383f85fb19e49836 | original | 0 | pass | 0 | pass | complete |
| 6c0124a2d35b8b4bf8d2a321 | capoff | 0 | pass | 0 | pass | complete |
| 6c0124a2d35b8b4bf8d2a321 | original | 0 | pass | 0 | pass | complete |
| 37c2ba2be995719ac8972cf1 | capoff | 0 | pass | 0 | pass | complete |
| 37c2ba2be995719ac8972cf1 | original | 0 | pass | 0 | pass | complete |
| d93ed5de9d4401cb3345c7bd | capoff | 0 | pass | 0 | pass | complete |
| d93ed5de9d4401cb3345c7bd | original | 0 | pass | 0 | pass | complete |
| c2f9d3102987f746f4f31b8d | capoff | 0 | pass | 0 | pass | complete |
| c2f9d3102987f746f4f31b8d | original | 0 | pass | 0 | pass | complete |
| a23ae9063b37c21cfe657d47 | capoff | 0 | pass | 0 | pass | complete |
| a23ae9063b37c21cfe657d47 | original | 0 | pass | 0 | pass | complete |
| 5a6f61e06de0bca53b4a7377 | capoff | 0 | pass | 0 | pass | complete |
| 5a6f61e06de0bca53b4a7377 | original | 0 | pass | 0 | pass | complete |
| 03426d6e61fb6b41145c5d8e | capoff | 0 | pass | 0 | pass | complete |
| 03426d6e61fb6b41145c5d8e | original | 0 | pass | 0 | pass | complete |
| 19f5d8535235334ffe1595e8 | capoff | 0 | pass | 0 | pass | complete |
| 19f5d8535235334ffe1595e8 | original | 0 | pass | 0 | pass | complete |
| 6b089d284c00a4418a1d3af4 | both | — | unavailable | — | unavailable | missing_cell |
| 47dac9d968ffe594faac0a14 | both | — | unavailable | — | unavailable | missing_cell |
| 4eda9e6155b2755508e13091 | both | — | unavailable | — | unavailable | missing_cell |
| ab774e229a65298fdc117c96 | both | — | unavailable | — | unavailable | missing_cell |
| b4e7dc307a1f895a8fec997a | both | — | unavailable | — | unavailable | missing_cell |
| 826332f387bd487a045d412f | both | — | unavailable | — | unavailable | missing_cell |
| 14d45f0e87126104057518af | both | — | unavailable | — | unavailable | missing_cell |
| 960d0adeb6cacfcfce93d546 | both | — | unavailable | — | unavailable | missing_cell |
| 6840a40e6e5c90bdc40b89b0 | both | — | unavailable | — | unavailable | missing_cell |
| 42ba32e4f07423bee03296b3 | both | — | unavailable | — | unavailable | missing_cell |
| 19964c4e7f737707baad94a5 | both | — | unavailable | — | unavailable | missing_cell |
| 40ec11c9694b4265a013c682 | both | — | unavailable | — | unavailable | missing_cell |
| f0642100f6eb9cd77e92f439 | both | — | unavailable | — | unavailable | missing_cell |
| b7ff3139c3f3eeb3ff7e9c80 | both | — | unavailable | — | unavailable | missing_cell |
| 1833a410c9e8704f6a379114 | both | — | unavailable | — | unavailable | missing_cell |
| 82606602ae475e73eb4401f9 | both | — | unavailable | — | unavailable | missing_cell |
| 2172052824abd70e8135366f | both | — | unavailable | — | unavailable | missing_cell |
| 5c394f4861164c1d5b31de4c | both | — | unavailable | — | unavailable | missing_cell |
| c9d2325e783e57ac5eafa34d | both | — | unavailable | — | unavailable | missing_cell |
| 3fdc7c12d6d583f46608eac6 | both | — | unavailable | — | unavailable | missing_cell |
| a7d551c093fd3333314813a5 | both | — | unavailable | — | unavailable | missing_cell |
| c402523c2460a62d6040ddd0 | both | — | unavailable | — | unavailable | missing_cell |
| b103826472ba7653cd8fd13a | both | — | unavailable | — | unavailable | missing_cell |
| 525ad705ad7008ed3ea378eb | both | — | unavailable | — | unavailable | missing_cell |
| 8a4bcb6e358e98c523b0d0c3 | both | — | unavailable | — | unavailable | missing_cell |
| 144f77ff21860a8a089a8080 | both | — | unavailable | — | unavailable | missing_cell |
| 3c3212c0cad597bafe0d5782 | both | — | unavailable | — | unavailable | missing_cell |
| 5d467b73f60b99b3d07f8c02 | both | — | unavailable | — | unavailable | missing_cell |
| a81b13b1b22e0bfe489daaa0 | both | — | unavailable | — | unavailable | missing_cell |
| 1aff34869825a76d502d92a3 | both | — | unavailable | — | unavailable | missing_cell |
| 3b70d3d44297fc1197610228 | both | — | unavailable | — | unavailable | missing_cell |
| 84bae28d26e5f5a3e555b601 | both | — | unavailable | — | unavailable | missing_cell |
| 07b9bad1f676110cb8bae7df | both | — | unavailable | — | unavailable | missing_cell |
| 0ff8a61a760d6836f469629b | both | — | unavailable | — | unavailable | missing_cell |
| 40034291ac69439c82ae1fc3 | both | — | unavailable | — | unavailable | missing_cell |
| 6d8d11dbbbc7b736c6386bca | both | — | unavailable | — | unavailable | missing_cell |
| cefda69ce81ca1253435bac7 | both | — | unavailable | — | unavailable | missing_cell |
| e42cd6f9b5b86feb491512f6 | both | — | unavailable | — | unavailable | missing_cell |
| e0f2bb19e19594c972c0ef15 | both | — | unavailable | — | unavailable | missing_cell |
| 0d4d946cb9ff28b7e6af3c4d | both | — | unavailable | — | unavailable | missing_cell |
| 9179614db32d3fd8b437475b | both | — | unavailable | — | unavailable | missing_cell |
| e146662ae0ab343921979246 | both | — | unavailable | — | unavailable | missing_cell |
| c770960b77b2d9f6304f1a34 | both | — | unavailable | — | unavailable | missing_cell |
| d49ef9c7980da822326bc6ac | both | — | unavailable | — | unavailable | missing_cell |
| eef5c3dc3fc8291d75199816 | both | — | unavailable | — | unavailable | missing_cell |
| 0417f598d89548e3200a3fe4 | both | — | unavailable | — | unavailable | missing_cell |
| 12a9c0da62781d521da26cd5 | both | — | unavailable | — | unavailable | missing_cell |
| c2a67190edb39398491bd651 | both | — | unavailable | — | unavailable | missing_cell |
| 58cc3599099d7ab60e5d1413 | both | — | unavailable | — | unavailable | missing_cell |
| 4206e18c23b43bb312e045e6 | both | — | unavailable | — | unavailable | missing_cell |
| fa46e16c8436f7ea4a5c3f06 | both | — | unavailable | — | unavailable | missing_cell |
| 162686f6303fe986619d236d | both | — | unavailable | — | unavailable | missing_cell |
| 029ecd260f3e085063714d3f | both | — | unavailable | — | unavailable | missing_cell |
| 7197775fb7f97a465fd3310e | both | — | unavailable | — | unavailable | missing_cell |
| 6de7e97b6cb167d048dc31ba | both | — | unavailable | — | unavailable | missing_cell |
| fcd702d12d5d6bfae824379b | both | — | unavailable | — | unavailable | missing_cell |
| 9a1d038b95f534b43185c7fc | both | — | unavailable | — | unavailable | missing_cell |
| dfc9c9b480e482911c457e07 | both | — | unavailable | — | unavailable | missing_cell |
| 34fce88c919bcae6410e4d94 | both | — | unavailable | — | unavailable | missing_cell |
| 7a39ae192fb0b1038c651f64 | both | — | unavailable | — | unavailable | missing_cell |
| 13465e8d0dc3824fced8e891 | both | — | unavailable | — | unavailable | missing_cell |
| 24840672cf1682dd450fdcd2 | both | — | unavailable | — | unavailable | missing_cell |
| 12a6e3e550a7939c6d79349d | both | — | unavailable | — | unavailable | missing_cell |
| fa5b51891eb78dc707e6471f | both | — | unavailable | — | unavailable | missing_cell |
| 861810fbdd6ebe7502383382 | both | — | unavailable | — | unavailable | missing_cell |
| 6ed2474713b3a311b4ec6b08 | both | — | unavailable | — | unavailable | missing_cell |
| f939f211b98675ac7c2d951f | both | — | unavailable | — | unavailable | missing_cell |
| 19b5e9b462930c6f50f2e2f6 | both | — | unavailable | — | unavailable | missing_cell |
| b14576e3d752f467db2abf18 | both | — | unavailable | — | unavailable | missing_cell |
| da9f71bdb9a8981dac078e6c | both | — | unavailable | — | unavailable | missing_cell |
| 9e98169ae668b50d60694317 | both | — | unavailable | — | unavailable | missing_cell |
| ff570734d7837a1ba9e77528 | both | — | unavailable | — | unavailable | missing_cell |
| 4fd2bc51397502cb1c085b5c | both | — | unavailable | — | unavailable | missing_cell |
| c0e77c94b06dd3464838be93 | both | — | unavailable | — | unavailable | missing_cell |
| 4c700c665ce70ca41e4569dd | both | — | unavailable | — | unavailable | missing_cell |
| dc17fc3637068157dba0207d | both | — | unavailable | — | unavailable | missing_cell |
| 727b32ab9723cb9feba71636 | both | — | unavailable | — | unavailable | missing_cell |
| a02980b0886a222f8e2f58e8 | both | — | unavailable | — | unavailable | missing_cell |
| 9aeb330f6c7e29c85ee56da0 | both | — | unavailable | — | unavailable | missing_cell |
| 0e0ee9a35e1116f7dafb423d | both | — | unavailable | — | unavailable | missing_cell |
| 862cd40c359e48e5a7998e3f | both | — | unavailable | — | unavailable | missing_cell |
| 89b258fddde381d9a09429d9 | both | — | unavailable | — | unavailable | missing_cell |
| 090d1237381f4ee02fcbd05d | both | — | unavailable | — | unavailable | missing_cell |
| 6e95ec72097ffded952889d6 | both | — | unavailable | — | unavailable | missing_cell |
| c8ce51b334cc3e42a623be6c | both | — | unavailable | — | unavailable | missing_cell |
| cf6bd4a623aa24871f74d136 | both | — | unavailable | — | unavailable | missing_cell |
| 519b30353f979e8028ed03e1 | both | — | unavailable | — | unavailable | missing_cell |
| 89182e81a187807d2772cade | both | — | unavailable | — | unavailable | missing_cell |
| 9ad3399cfc13f1297d17423d | both | — | unavailable | — | unavailable | missing_cell |
| 046aa51d028b84dde8981351 | both | — | unavailable | — | unavailable | missing_cell |
| c897cd3d2a3b35bfe999e87e | both | — | unavailable | — | unavailable | missing_cell |
| 1689630f5ad581d9fcfc483e | both | — | unavailable | — | unavailable | missing_cell |
| c1c03ed850a40df57da8628a | both | — | unavailable | — | unavailable | missing_cell |
| d1690029ea53ae03b3705536 | both | — | unavailable | — | unavailable | missing_cell |
| a921f9ab5443f978e56d2390 | both | — | unavailable | — | unavailable | missing_cell |
| a86da75220343c5560c45373 | both | — | unavailable | — | unavailable | missing_cell |
| e7b52c6db370d10a5fd7d891 | both | — | unavailable | — | unavailable | missing_cell |
| 735081421354eaafb893322d | both | — | unavailable | — | unavailable | missing_cell |
| 824f602358ace0fc5cb69271 | both | — | unavailable | — | unavailable | missing_cell |
| 3bc2cef1ca9bab6e4a90e222 | both | — | unavailable | — | unavailable | missing_cell |
| 9c3c7c258bf086523ea6268e | both | — | unavailable | — | unavailable | missing_cell |
| 58879f9745ed479686bd0481 | both | — | unavailable | — | unavailable | missing_cell |
| b6ea6d9e337e3bf6f2eca5d2 | both | — | unavailable | — | unavailable | missing_cell |
| 16037ce355e4a2e9a43a2008 | both | — | unavailable | — | unavailable | missing_cell |
| 4597af8473d8e404f1490c57 | both | — | unavailable | — | unavailable | missing_cell |
| 7c933afa6e2adc84ccb287be | both | — | unavailable | — | unavailable | missing_cell |
| 0998eeed741b887bdb8664af | both | — | unavailable | — | unavailable | missing_cell |
| bb4da95ca8ce5b0b8d3dbe35 | both | — | unavailable | — | unavailable | missing_cell |
| c5f1daa35261cf950172dfa8 | both | — | unavailable | — | unavailable | missing_cell |
| 244f29ba9b89c48d08c257c7 | both | — | unavailable | — | unavailable | missing_cell |
| b8924c056fee6d000f5492d1 | both | — | unavailable | — | unavailable | missing_cell |
| 4944219da107f9ed1daccef5 | both | — | unavailable | — | unavailable | missing_cell |
| ac46789a7ebda9982aebd343 | both | — | unavailable | — | unavailable | missing_cell |
| ccf4e4f1fca14a048eecd38f | both | — | unavailable | — | unavailable | missing_cell |
| 6c9ac68dd90eb2d39d339b6a | both | — | unavailable | — | unavailable | missing_cell |
| 672b5b4a7ea9b83b8668fbe2 | both | — | unavailable | — | unavailable | missing_cell |
| b8f1ca491f4e29db862af920 | both | — | unavailable | — | unavailable | missing_cell |
| 5efb497774b3f4f9ad8e7f7d | both | — | unavailable | — | unavailable | missing_cell |
| 47ee96bcecb134f64286c958 | both | — | unavailable | — | unavailable | missing_cell |
| a18ee644e09c84652cc9582a | both | — | unavailable | — | unavailable | missing_cell |
| 509cd28130eb44d35b27d08a | both | — | unavailable | — | unavailable | missing_cell |
| a8a5ddc06de26a9885f75fe9 | both | — | unavailable | — | unavailable | missing_cell |
| 5f818373c34233809fc57716 | both | — | unavailable | — | unavailable | missing_cell |
| baa8eccee6a4f8c27c11a09c | both | — | unavailable | — | unavailable | missing_cell |
| 2a91e17773f7272dbd36a048 | both | — | unavailable | — | unavailable | missing_cell |
| d0a5df19a69792ac87a703dc | both | — | unavailable | — | unavailable | missing_cell |
| 6d6930dcd4fe737e4d1ef3ed | both | — | unavailable | — | unavailable | missing_cell |
| cf9c6af6097c6d96c9a5a1d3 | both | — | unavailable | — | unavailable | missing_cell |
| 7317081e2468dfeeed3e4cc7 | both | — | unavailable | — | unavailable | missing_cell |
| ed2fff6199cac50f8e3c05d9 | both | — | unavailable | — | unavailable | missing_cell |
| 5d52bba4bd205ffecf96212a | both | — | unavailable | — | unavailable | missing_cell |
| e82412060e54893dc307a45e | both | — | unavailable | — | unavailable | missing_cell |
| b42dfb1e539cb4645127e844 | both | — | unavailable | — | unavailable | missing_cell |
| 2fe9909dbaad17941716efc9 | both | — | unavailable | — | unavailable | missing_cell |
| e45d4b2c01fc48117d5abec8 | both | — | unavailable | — | unavailable | missing_cell |
| 978f353680dde68625399775 | both | — | unavailable | — | unavailable | missing_cell |
| cdc8a1fbbb43d1f1ba93a366 | both | — | unavailable | — | unavailable | missing_cell |
| 3126d7f4d6378f131a26c41d | both | — | unavailable | — | unavailable | missing_cell |
| 48f56fbee8eed89fe5598934 | both | — | unavailable | — | unavailable | missing_cell |
| 18cef3e100afe2f32847ac27 | both | — | unavailable | — | unavailable | missing_cell |
| f67e77a0b124376f29b78302 | both | — | unavailable | — | unavailable | missing_cell |
| 7ab5a2ba2ca2072d49c86da9 | both | — | unavailable | — | unavailable | missing_cell |
| ea3b0653f085cf535854d1b8 | both | — | unavailable | — | unavailable | missing_cell |
| 8905e452833b0a01defd8b1e | both | — | unavailable | — | unavailable | missing_cell |
| 28555ca1e3c1d3ab551385b1 | both | — | unavailable | — | unavailable | missing_cell |
| 861414ea84239f8471f0ade8 | both | — | unavailable | — | unavailable | missing_cell |
| 1f19207d799d9bcd0b005ef9 | both | — | unavailable | — | unavailable | missing_cell |
| ad007b170a6bbf5bc88d182d | both | — | unavailable | — | unavailable | missing_cell |
| 94488c6aa407c3ea167ea51d | both | — | unavailable | — | unavailable | missing_cell |
| e6a5e4cd9fbe73077175c7b9 | both | — | unavailable | — | unavailable | missing_cell |
| bca38cd4398e1159ed781bff | both | — | unavailable | — | unavailable | missing_cell |
| 68da09e4a00f4fe8d8b054fd | both | — | unavailable | — | unavailable | missing_cell |
| da666451073f38000c71b39f | both | — | unavailable | — | unavailable | missing_cell |
| 57b0ace8ad261f0963cece6e | both | — | unavailable | — | unavailable | missing_cell |
| b1be521b209066effb830ad1 | both | — | unavailable | — | unavailable | missing_cell |
| d246da52d2783b0000af34aa | both | — | unavailable | — | unavailable | missing_cell |
| 9ac1596b4a83bfd3759110f5 | both | — | unavailable | — | unavailable | missing_cell |
| d3e7acfb899406015f6d7e6a | both | — | unavailable | — | unavailable | missing_cell |
| 1b91b6d6beb187aaf9103cdc | both | — | unavailable | — | unavailable | missing_cell |
| 9a600f5f46fa47c339ccb4d1 | both | — | unavailable | — | unavailable | missing_cell |
| 635bac1c845730dae487891a | both | — | unavailable | — | unavailable | missing_cell |
| 031ae1822109079d3cddb520 | both | — | unavailable | — | unavailable | missing_cell |
| 3435ab1a884c517b32867161 | both | — | unavailable | — | unavailable | missing_cell |
| 09d4451a2a5b030d1853c267 | both | — | unavailable | — | unavailable | missing_cell |
| fa309fa719c353f20a813699 | both | — | unavailable | — | unavailable | missing_cell |
| 03ee79b7cf8d02ddb7baeea3 | both | — | unavailable | — | unavailable | missing_cell |
| 37aa09141ddb4b6e8f93f647 | both | — | unavailable | — | unavailable | missing_cell |
| c14b2b630688912a588e1cf3 | both | — | unavailable | — | unavailable | missing_cell |
| 2eda7453d476d16c07a327ed | both | — | unavailable | — | unavailable | missing_cell |
| 9a29639c43e873eec6a7d1ac | both | — | unavailable | — | unavailable | missing_cell |
| 0362b36136a70031c319de5f | both | — | unavailable | — | unavailable | missing_cell |
| 9397f85898818d3dc9d04c1e | both | — | unavailable | — | unavailable | missing_cell |
| 4c1b2ab65e6ba3e75ac9b10a | both | — | unavailable | — | unavailable | missing_cell |
| d679f4cef5e7a847d5f6dc80 | both | — | unavailable | — | unavailable | missing_cell |
| f19cc29f17b93bb9cbbd5f1a | both | — | unavailable | — | unavailable | missing_cell |
| e654a69635e2e4a1bcc2903b | both | — | unavailable | — | unavailable | missing_cell |
| 508b709256adff820b7fdf82 | both | — | unavailable | — | unavailable | missing_cell |
| 0ebaffd3a3e8d10252da8bd5 | both | — | unavailable | — | unavailable | missing_cell |
| 6f8cac15c1ed9dd1fb79b212 | both | — | unavailable | — | unavailable | missing_cell |
| 302070707affaaec2265e772 | both | — | unavailable | — | unavailable | missing_cell |
| 74feefbadad2b95947437ed6 | both | — | unavailable | — | unavailable | missing_cell |
| 982870b0fcc4a8bef4a297af | both | — | unavailable | — | unavailable | missing_cell |
| 2e5068d168160234340d32fa | both | — | unavailable | — | unavailable | missing_cell |
| f642d1e953d4e4b42c9a916e | both | — | unavailable | — | unavailable | missing_cell |
| d7884b1e2a9c1c3790535590 | both | — | unavailable | — | unavailable | missing_cell |
| 8499903e83df71431114aaa8 | both | — | unavailable | — | unavailable | missing_cell |
| 272db4c9310a73f01bf46d4b | both | — | unavailable | — | unavailable | missing_cell |
| 9f020616201afdc368d77f9b | both | — | unavailable | — | unavailable | missing_cell |
| 26318156d310334e8b260e87 | both | — | unavailable | — | unavailable | missing_cell |
| d7241b9882514c2709082321 | both | — | unavailable | — | unavailable | missing_cell |
| a5b3de3764680273ff4760e1 | both | — | unavailable | — | unavailable | missing_cell |
| e5c2ea10bc6ce298f6065199 | both | — | unavailable | — | unavailable | missing_cell |
| 847f33277d9d89fe17482367 | both | — | unavailable | — | unavailable | missing_cell |
| 77568a85e217721985cd8ea4 | both | — | unavailable | — | unavailable | missing_cell |
| 793ee3d9708b970c08a0fbe2 | both | — | unavailable | — | unavailable | missing_cell |
| 129251f55876e9cdc9e907a6 | both | — | unavailable | — | unavailable | missing_cell |
| 40059b37d028ec2cd587bbb1 | both | — | unavailable | — | unavailable | missing_cell |
| 30756d73095e1914cf757782 | both | — | unavailable | — | unavailable | missing_cell |
| d74e8582f780dfdeb9281671 | both | — | unavailable | — | unavailable | missing_cell |
| 88dfe1aa76490ae40e93f05f | both | — | unavailable | — | unavailable | missing_cell |
| 9adac77b91eae4f8ea4d8df2 | both | — | unavailable | — | unavailable | missing_cell |
| bbbda4ebfb279ed21179678b | both | — | unavailable | — | unavailable | missing_cell |
| 34f5fb1acf8d86a8a7a94e1c | both | — | unavailable | — | unavailable | missing_cell |
| c9dc2d0cfe6d53ccdef2f1ef | both | — | unavailable | — | unavailable | missing_cell |
| 22b85c86caaee83341968cec | both | — | unavailable | — | unavailable | missing_cell |
| 1a27fc67e8978362681b5d20 | both | — | unavailable | — | unavailable | missing_cell |
| f9ebb0802bd50e68ec18fcb0 | both | — | unavailable | — | unavailable | missing_cell |
| be9a4b3ce1acb50722ae8614 | both | — | unavailable | — | unavailable | missing_cell |
| 5c5511653f8d590c63a39794 | both | — | unavailable | — | unavailable | missing_cell |
| 7cbec59a4f05afaa8ebed3fb | both | — | unavailable | — | unavailable | missing_cell |
| b1a17c1fb747eef11f253278 | both | — | unavailable | — | unavailable | missing_cell |
| edb61534cb4ec7a4187ebbdb | both | — | unavailable | — | unavailable | missing_cell |
| 78360f37e3cd5a3eb5cc2b3e | both | — | unavailable | — | unavailable | missing_cell |
| 46d6404412a25fbdd2965880 | both | — | unavailable | — | unavailable | missing_cell |
| 50af2a28b866c26021d83b01 | both | — | unavailable | — | unavailable | missing_cell |
| 22a5ac50d5ca3c952b8b1e34 | both | — | unavailable | — | unavailable | missing_cell |
| 7d93e4d997ec1f974bb6c71a | both | — | unavailable | — | unavailable | missing_cell |
| 0f466b21fb4514acd9d1ff1e | both | — | unavailable | — | unavailable | missing_cell |
| 151bacf1f85b74f88864784e | both | — | unavailable | — | unavailable | missing_cell |
| 330479ee3f94e169b8496e0b | both | — | unavailable | — | unavailable | missing_cell |
| e4019672011694d495923c6f | both | — | unavailable | — | unavailable | missing_cell |
| bf89e6ad180b60ad56c35a7e | both | — | unavailable | — | unavailable | missing_cell |
| 70aacd394ef41b887377260a | both | — | unavailable | — | unavailable | missing_cell |
| b3f4ad21a596171a9a43e0aa | both | — | unavailable | — | unavailable | missing_cell |
| 6885c03ed3db8fb41a5e20dd | both | — | unavailable | — | unavailable | missing_cell |
| 9a22bb61d6e0f49880a936a3 | both | — | unavailable | — | unavailable | missing_cell |
| eafb85daf9dfc6661b0bc2d8 | both | — | unavailable | — | unavailable | missing_cell |
| f3375c98045e9e28a348b9d0 | both | — | unavailable | — | unavailable | missing_cell |
| d62c99156470a7900dc43bc6 | both | — | unavailable | — | unavailable | missing_cell |
| fa0defe230fa592c6e1395ce | both | — | unavailable | — | unavailable | missing_cell |
| 9d8fa010baff9d2225fff4d4 | both | — | unavailable | — | unavailable | missing_cell |
| d059ce23baa1380031ffc8cb | both | — | unavailable | — | unavailable | missing_cell |
| 058509628604e5ca4527273b | both | — | unavailable | — | unavailable | missing_cell |
| 165be2e488d7d1013b36ff1b | both | — | unavailable | — | unavailable | missing_cell |
| 6c498709f6484559ef4e1e7f | both | — | unavailable | — | unavailable | missing_cell |
| 789321f88cd80b79c41108d3 | both | — | unavailable | — | unavailable | missing_cell |
| 58f67f71157df294642d7924 | both | — | unavailable | — | unavailable | missing_cell |
| f434980db097ed5dc29aa6b8 | both | — | unavailable | — | unavailable | missing_cell |
| 0eadfbc9b2c2899d71a5dcee | both | — | unavailable | — | unavailable | missing_cell |
| 509562eef48054a3aeac166a | both | — | unavailable | — | unavailable | missing_cell |
| 8515821d35005362bf80ca86 | both | — | unavailable | — | unavailable | missing_cell |
| ce81522f547c386fa9c08c2b | both | — | unavailable | — | unavailable | missing_cell |
| 67fbcd1e5ac9b7dcb8f292b9 | both | — | unavailable | — | unavailable | missing_cell |
| 90334bd842b032c804251295 | both | — | unavailable | — | unavailable | missing_cell |
| 62cd670d3fc0e07b1d6ff2d7 | both | — | unavailable | — | unavailable | missing_cell |
| c2a654d2b5c10bec5b192bd4 | both | — | unavailable | — | unavailable | missing_cell |
| e513b37dc4ee2ea0c2ec9a4a | both | — | unavailable | — | unavailable | missing_cell |
| 5605235e2ed700e3724eec66 | both | — | unavailable | — | unavailable | missing_cell |
| caef53a035b7c9e1ee694a16 | both | — | unavailable | — | unavailable | missing_cell |
| 3e16fbe7ff4d0e5b55e6d9d1 | both | — | unavailable | — | unavailable | missing_cell |
| 66c77006152a19f5b1a397d3 | both | — | unavailable | — | unavailable | missing_cell |
| 6837bb994c30db520b1c50f5 | both | — | unavailable | — | unavailable | missing_cell |
| 4d261cc6ea3f349110835054 | both | — | unavailable | — | unavailable | missing_cell |
| b42ba0f2b0ed1a420be6ddb5 | both | — | unavailable | — | unavailable | missing_cell |
| 10d0d6ef3ebaeeab62506369 | both | — | unavailable | — | unavailable | missing_cell |
| 2fcaaa6515b6d07526750ec2 | both | — | unavailable | — | unavailable | missing_cell |
| 19a7255c9f6a76e216f4f3d3 | both | — | unavailable | — | unavailable | missing_cell |
| 875c812006d2f01a6a67e48b | both | — | unavailable | — | unavailable | missing_cell |
| 29c34b1e7fff719ad0530aaf | both | — | unavailable | — | unavailable | missing_cell |
| 4c03d7d4cf05c04e6563204a | both | — | unavailable | — | unavailable | missing_cell |
| 56dad6836419abb22b9f3fc5 | both | — | unavailable | — | unavailable | missing_cell |
| 722a6e81428fe90b28522578 | both | — | unavailable | — | unavailable | missing_cell |
| 64474eaad780d3d0f127b333 | both | — | unavailable | — | unavailable | missing_cell |
| 50bfcf7f7c0f6341243f0890 | both | — | unavailable | — | unavailable | missing_cell |
| 203da3ce23c2826be75941f8 | both | — | unavailable | — | unavailable | missing_cell |
| 6b9269f85604bbde03fb8ae2 | both | — | unavailable | — | unavailable | missing_cell |
| 6e30cfe3525aa76f6c298840 | both | — | unavailable | — | unavailable | missing_cell |
| f5f8f6ab600ed0fff3f77575 | both | — | unavailable | — | unavailable | missing_cell |
| a1ebc798b3d3dffdcb755fea | both | — | unavailable | — | unavailable | missing_cell |
| 64083f876c4b931fac1666ac | both | — | unavailable | — | unavailable | missing_cell |
| 3f0d5de719c7c2fac0765ae9 | both | — | unavailable | — | unavailable | missing_cell |
| 02fbdb7be57f6759883cb7f7 | both | — | unavailable | — | unavailable | missing_cell |
| 2eafd0179259617282b6bfe4 | both | — | unavailable | — | unavailable | missing_cell |
| 62b13a164930d43ad696b359 | both | — | unavailable | — | unavailable | missing_cell |
| 048ddd95d61026dbf40fa6f9 | both | — | unavailable | — | unavailable | missing_cell |
| ea85d9daee87f0884e4f22e2 | both | — | unavailable | — | unavailable | missing_cell |
| 7e27f3fa1620b77e96f8da6f | both | — | unavailable | — | unavailable | missing_cell |
| 46cc8880d731fbee52076712 | both | — | unavailable | — | unavailable | missing_cell |
| 45c033c5bc044beea6f5562c | both | — | unavailable | — | unavailable | missing_cell |
| be96aaad5d4e1dd91747a116 | both | — | unavailable | — | unavailable | missing_cell |
| c28a7e48a1333e1bbbca134d | both | — | unavailable | — | unavailable | missing_cell |
| fda4c348dac5448fc10fd672 | both | — | unavailable | — | unavailable | missing_cell |
| 929c713ce993539177ad3985 | both | — | unavailable | — | unavailable | missing_cell |
| 47d567d51e4c0129ae905aa3 | both | — | unavailable | — | unavailable | missing_cell |
| 1a7b6658a55e4798f9674c67 | both | — | unavailable | — | unavailable | missing_cell |

Cell 61348508e40d54351613ab14

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |
| original | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 88af67fa5945b642e8ba7974

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |
| original | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 915f97b05f3fa2a81de09cdf

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |
| original | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 4aa4849ba414edab2504f56b

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |
| original | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 9ebc93cc7912bd5d1c929418

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |
| original | 244760 / 245237 | 69 (0.00028136) | 0.890651 / 1 | 0.999166 | 1739 / 1931 | 90 / 8 | 0.468222 / 0.924426 / 0.999162 | 0 / 0.000930673 / 0.0616488 / 0.242544 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell ce0d0ffc2a58a60e27c460d9

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |
| original | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 95dfb24c6361b2d38dd60e9b

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |
| original | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 6d0915056b1e76d8ee8795ff

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |
| original | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 7c9675a69d832a772070cb2d

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |
| original | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 95016bc16e89cfcccccc40b8

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |
| original | 244388 / 245237 | 119 (0.000485245) | 0.750788 / 1 | 0.998601 | 1554 / 1931 | 248 / 20 | 0.229559 / 0.643078 / 0.878369 | 0 / 0.0182431 / 0.101317 / 0.215406 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 43925e53c31860219a85ef90

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |
| original | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell c29ee18fb21ba6b387ede6e8

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |
| original | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 54879da4dcdb0f106f98080a

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |
| original | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 78ebbc03946239c1d637154c

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |
| original | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell b1d1e53944241333ec5603d4

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |
| original | 244224 / 245237 | 182 (0.000742139) | 0.614025 / 1 | 0.998091 | 1548 / 1931 | 262 / 24 | 0.304457 / 0.678131 / 0.884897 | 0 / 0.0197609 / 0.114651 / 0.473487 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell f3dbf1a3d5860a628e7d68ef

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |
| original | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell be44dfb501724b72adcbd747

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |
| original | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 5263d61e569d7cb4ceb4e617

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |
| original | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 81b1e9cb4e216a6cd1cd565a

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |
| original | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell deb5f473d9ca2ed544926204

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |
| original | 245179 / 245237 | 14 (5.70876e-05) | 1 / 1 | 0.999858 | 1875 / 1931 | 24 / 0 | 0.631858 / 1 / 1 | 0 / 0 / 0.011477 / 0.0293603 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 0b6ade77641a02c1c85574b0

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |
| original | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell ee67c592789829e7dd808ede

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 240530 / 245237 | 1123 (0.00457924) | 0.151918 / 0.821372 | 0.988862 | 216 / 1931 | 1592 / 378 | 0.0471945 / 0.173168 / 0.29065 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |
| original | 240530 / 245237 | 1123 (0.00457924) | 0.151918 / 0.821372 | 0.988862 | 216 / 1931 | 1592 / 378 | 0.0471945 / 0.173168 / 0.29065 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 8be432675ed4dc57f9108bd4

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |
| original | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 78928f2782d91d888ef24d52

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |
| original | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell de785feed05c9f4c2a9e9273

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |
| original | 240530 / 245237 | 1123 (0.00457924) | 0.151921 / 0.821389 | 0.988863 | 216 / 1931 | 1592 / 378 | 0.0471955 / 0.173171 / 0.290656 | 0.048375 / 0.12996 / 0.236113 / 0.402404 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell de0b9612418e6d573ed77679

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |
| original | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell be37e2a1ff4a079e56efe268

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |
| original | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 1e6b766c4139230c18547234

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |
| original | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell c0a54c5fbf1ce7776efc983e

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |
| original | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 7499c19b813dcada2c67ae39

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |
| original | 244161 / 245237 | 262 (0.00106835) | 0.476995 / 1 | 0.997389 | 1162 / 1931 | 615 / 15 | 0.0950847 / 0.326078 / 0.528615 | 0 / 0.0434718 / 0.0922683 / 0.197092 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 39c7fd4929721e8dcba56b94

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244914 / 245237 | 13 (5.30099e-05) | 0.99036 / 1 | 0.999726 | 1758 / 1931 | 44 / 4 | 0.629378 / 0.913186 / 0.984029 | 0 / 0.000679858 / 0.0249852 / 0.207592 |
| original | 244914 / 245237 | 13 (5.30099e-05) | 0.99036 / 1 | 0.999726 | 1758 / 1931 | 44 / 4 | 0.629378 / 0.913186 / 0.984029 | 0 / 0.000679858 / 0.0249852 / 0.207592 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell b887b1046cd563d990765e01

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244551 / 245237 | 19 (7.74761e-05) | 0.959202 / 1 | 0.999604 | 1742 / 1931 | 65 / 7 | 0.525191 / 0.899902 / 0.958471 | 0 / 0.000944996 / 0.0440937 / 0.206839 |
| original | 244551 / 245237 | 19 (7.74761e-05) | 0.959202 / 1 | 0.999604 | 1742 / 1931 | 65 / 7 | 0.525191 / 0.899902 / 0.958471 | 0 / 0.000944996 / 0.0440937 / 0.206839 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 435235a6719279d1cc87ad66

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244897 / 245237 | 16 (6.5243e-05) | 0.98121 / 1 | 0.999657 | 1757 / 1931 | 37 / 2 | 0.552268 / 0.87965 / 0.970163 | 0 / 0.000840949 / 0.0175551 / 0.207592 |
| original | 244897 / 245237 | 16 (6.5243e-05) | 0.98121 / 1 | 0.999657 | 1757 / 1931 | 37 / 2 | 0.552268 / 0.87965 / 0.970163 | 0 / 0.000840949 / 0.0175551 / 0.207592 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell aaed1cf9e8ce7cf1cf3749fa

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244819 / 245237 | 13 (5.30099e-05) | 0.977949 / 1 | 0.999709 | 1748 / 1931 | 51 / 6 | 0.609002 / 0.91908 / 0.974629 | 0 / 0.000897229 / 0.0364685 / 0.207592 |
| original | 244819 / 245237 | 13 (5.30099e-05) | 0.977949 / 1 | 0.999709 | 1748 / 1931 | 51 / 6 | 0.609002 / 0.91908 / 0.974629 | 0 / 0.000897229 / 0.0364685 / 0.207592 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 92a5ef6855124ffc5a8d6163

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 244906 / 245237 | 11 (4.48546e-05) | 0.99069 / 1 | 0.999758 | 1764 / 1931 | 52 / 9 | 0.651942 / 0.940646 / 0.987799 | 0 / 0.00073449 / 0.0369588 / 0.207592 |
| original | 244906 / 245237 | 11 (4.48546e-05) | 0.99069 / 1 | 0.999758 | 1764 / 1931 | 52 / 9 | 0.651942 / 0.940646 / 0.987799 | 0 / 0.00073449 / 0.0369588 / 0.207592 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell baa601113af675024e73bc30

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell b6b271f3383f85fb19e49836

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 6c0124a2d35b8b4bf8d2a321

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 37c2ba2be995719ac8972cf1

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell d93ed5de9d4401cb3345c7bd

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell c2f9d3102987f746f4f31b8d

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell a23ae9063b37c21cfe657d47

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 5a6f61e06de0bca53b4a7377

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 03426d6e61fb6b41145c5d8e

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.

Cell 19f5d8535235334ffe1595e8

HT-7 concentration (descriptive; fractional top shares include zero mass):

| Reference | Near-zero target NLL change / N | Positions for half KL (fraction) | Top .1% / 1% KL share | Position Gini | Windows KL ≤.001 / N | Windows >.01 / >.1 | Top 1% / 5% / 10% window KL share | Window median / p90 / p99 / max KL |
|---|---|---|---|---|---|---|---|---|
| capoff | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |
| original | 245237 / 245237 | undefined (undefined) | undefined / undefined | undefined | 1931 / 1931 | 0 / 0 | undefined / undefined / undefined | 0 / 0 / 0 / 0 |

Near-zero target-token loss change does not prove unchanged predictions or distributions. Concentration alone does not identify reader firing, a causal mechanism, or a power law.