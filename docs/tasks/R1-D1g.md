# R1-D1g — exclusion register v4 and concurrent-pool supplement

- Status: CPU binding and exposure audit complete; no fresh draw or scientific freeze authorized.
- Agent: Codex, round 10, 2026-09-14 EDT.
- Authority: docs/ongoing.md, round 10; new files only and CPU only.
- Outputs: scripts/r1_d1g_freeze_register_v4.py; manifests/revision_v1/exclusions_frozen_v4.json; scripts/r1_d1g_mquake_exposure_supplement.py; manifests/revision_v1/exclusions_frozen_v4_supplement_v1.json; logs/r1_round10/register_v4_report.json and register_v4_supplement_report.json.
- Tests: 13 base-register tests and 4 supplement tests; included in the 403-pass CPU validation with unrelated round-10 repairs applied in memory.
- Existing files: unchanged. GPU: 0 seconds. No fresh allocation, payload seal, stage, or commit.

## Completed subtasks

1. Validate the v3 wrapper, all its children, the prepared MQuAKE records and resource hashes.
2. Apply only the CounterFact reason exception `old_eligible:counterfact`; keep every independent exposure reason active. This yields 12,246 conditional CounterFact candidates. The task authorizes the policy binding; it does not change the decision log's approval wording or authorize a draw.
3. Bind the actual 6,043-item MQuAKE teacher pool and verify its support labels/tokens against prepared source rows.
4. Preserve zsRE priority for the 159 overlapping subjects (169 MQuAKE items); independent training/query exposure still removes a subject from both datasets.
5. Bind MQuAKE training and development primary subjects, locality-query subjects and development unrelated-query subjects. Resolve query subjects against the hash-bound prepared prompt inventory. Report unmapped prompts rather than dropping them.
6. Treat teacher eligibility provenance separately from training exposure: filtering a pool is not automatically equivalent to teaching its entire contents.
7. Preserve the initial v4 snapshot. When Claude added the 1,000-item training pool v2, create a separate supplement that unions all existing reserved training/development versions, validates each against the teacher pool, and refuses to release any parent exclusion.
8. Detect newly appearing/disappearing pool versions in supplement validation, as well as child hash changes. Reissue a new supplement after further exposure changes.
9. Emit only metadata candidate inventories and explicit shortfalls; do not choose one fact per subject, sample roles, or infer final eligibility.

## Counts and blocking finding

| Snapshot | zsRE subjects | CounterFact subjects | MQuAKE items | MQuAKE subjects | MQuAKE shortfall against 4,050 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Initial v4, training pool v1 | 52,435 | 12,246 | 3,002 | 2,882 | 1,168 |
| Supplement, training pools v1 + v2 | 52,411 | 12,246 | 2,171 | 2,100 | 1,950 |

The supplement reserves 1,200 primary training/development subjects, 2,106 locality-query subjects and 990 unrelated-query subjects; their union is 3,405. These categories overlap. The stricter exposure policy removes 87 shared zsRE subjects overall.

These are **conservative reservations of declared query lists**, not a claim that every listed query was executed. Counting only primary training/development subjects would leave a MQuAKE ceiling of 4,218, just 168 above the 4,050 role demand. That alternative is not an admitted candidate list. It omits the query-exposure reservation and still needs context, alias/entity, ordinary-text and remaining eligibility review.

Under the conservative policy, even three disjoint 1,000-subject edit streams are infeasible, before reserving outside prompts and challenges. Do not silently relax the policy, reuse exposed subjects, reduce the approved scope or substitute item counts for subject counts.

## Handoff

A CPU audit of immutable training/evaluation recipes and query traces may distinguish actually used queries from unused reservations; any release needs explicit lead review and a new binding. An approved additional source or explicit design revision are other lead decisions. All ordinary-text and alias/context exclusions remain relevant.

The proposed import-order-only patch touches the supplement's producer script. If approved, publish a **new** supplement binding after that edit; preserve this historical snapshot and report.

Reproduce with module execution from pc_cap (`python -m scripts.r1_d1g_freeze_register_v4` or `python -m scripts.r1_d1g_mquake_exposure_supplement`), supplying new output paths. Do not overwrite the existing manifests.
