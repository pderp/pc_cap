# Round-10 approved repairs — completion (2026-09-15)

The user approved the three prepared patches and requested a commit. On inspection, Claude had already applied and committed all three in **3e8a98017701a724b5ef0d8d19ee4ae0b1e1b6fe**. Reverse-application checks verify that the complete patches are installed. No patch was applied twice.

This completion record supersedes the pending-edit status in [the original request](R1-round10-edit-request.md) and the historical [round-10 handoff](../../logs/r1_round10/handoff.md).

The remaining source-hash follow-up is now complete: [exclusions_frozen_v4_supplement_v1_rebound.json](../../manifests/revision_v1/exclusions_frozen_v4_supplement_v1_rebound.json) binds the installed import-order-corrected producer. It preserves and references the historical v1 supplement. Rebuilding and comparing every original non-binding section verified identical candidate lists, removals, exposure policy, counts and limits. Its current child hashes and pool-version inventory validate. MQuAKE remains at 2,100 distinct subjects; no exposure was released and no draw or seal was authorized.

The filename deliberately leaves supplement v2 available for the new population-policy work assigned in round 11. This is a source-hash rebinding of the existing v1 policy only.

## Installed validation

- Full revision CPU suite plus package layout: **463 passed, 8 skipped** (404 revision tests and 59 layout tests). No in-memory source changes or test overrides.
- Default repository Ruff check passes for the 19 round-10 Python files; format checks pass.
- The installed development-analysis CLI succeeds and produces a report semantically identical to the prior tested preview. The report remains **NOT CONFIRMATORY**.
- Every approved patch passes the reverse-application check.

Evidence, exact commands, hashes and attributable synthetic trace directories are in [the completion receipt](../../logs/r1_round10/approved_repairs_20260915/completion.json). The [rebinding receipt](../../logs/r1_round10/approved_repairs_20260915/supplement_rebinding.json) records the sole changed producer hash and hashes of every unchanged section.

The follow-up commit contains this record, the new supplement binding and validation evidence, including this validation's synthetic driver traces. Model/checkpoint resources remain under assets. Existing historical records remain intact. No GPU, real-base execution, fresh data draw or seal was performed.
