# Outcome codes

Closed enum in `pccap.harness.records.OutcomeCode` (S0-03; PDF Op. rule 8, App. D). Codes are
strings and never numbers, so they cannot be mistaken for a NaN. `tests/harness/test_records.py`
asserts this table and the enum list the same codes.

| Code | Level | Meaning | Emitted by |
| --- | --- | --- | --- |
| `accepted` | candidate | The evaluated candidate write improved the loss by more than `max(1e-8, 1e-6·L)` and was committed. | `cap.learn.round_update` (CAP-06) |
| `rejected_no_improvement` | candidate | No candidate on the geometric grid beat the no-op; the original state was restored and the search charged. | `cap.learn.round_update` |
| `no_direction` | bank/round | The credit signal at a site had norm < 1e-12; no direction was manufactured. | `transport.Transport.direction` (S0-05); routers log it |
| `abstain` | round | The measured router (C2) found no bank with a positive score above threshold. | `routers.measured.Measured` (CAP-05) |
| `ambiguous_key_conflict` | bank | Identical keys with incompatible targets and no revision event: bank rejected, old memory preserved. | `cap.transaction` (CAP-04) |
| `evicted` | slot | A full bank evicted the slot with the lowest use count (ties: oldest last-use, smallest id) to admit a successful write. | `cap.transaction` |
| `acquisition_failure` | item | The item ended without every prefix reaching `CE ≤ 0.1` within R = 5 rounds (not an exception). | `cap.learn.update_item` (CAP-07) |
| `unreachable` | measurement | A bounded search could not reach its target (e.g., 50% loss reduction in P5). | `metrics.*`, S1-05 |
| `undefined` | measurement | A ratio with a zero denominator (0/0, empty set, constant vector). | `contracts.metric(...)` builders |
| `unsupported` | measurement | The measurement is not defined for this base/data (e.g., LM drift on the grammar base; E.4 domains). | metric builders, DATA-04 |
| `unavailable` | measurement / asset | The required asset or reference is absent (e.g., ePC checkpoint, GRACE parity). | `vendor_hdpc`, S0-01, S2-05 |
| `resource_stop` | run | The run hit its accelerator ceiling; the incomplete item was rolled back and charged. | `harness.runner`, `harness.snapshot` (S0-08) |
| `nonfinite_failure` | run / item | An unexpected NaN/Inf appeared; traceback and item id written to `error.json`. | `harness.records.write_error_json` |
| `revision_replaced` | item (correction track) | A newer version of the same fact retired the older slots and stored the new answer. | `cap.transaction` with a `RevisionEvent` (SD-4) |
| `revision_replayed` | item (correction track) | Replay of an already-stored version: idempotent, no change. | `cap.transaction` |

Run-level statuses (`pccap.harness.records.RunStatus`): `running`, `complete`, `resource_stop`,
`correctness_failure`.
