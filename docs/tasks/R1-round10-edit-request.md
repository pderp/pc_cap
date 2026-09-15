# Round-10 tested edits awaiting user permission

Standing user instruction: create new files; ask before changing any existing file. All proposed changes below are prepared and reviewable, but unapplied.

| Patch | Files | Purpose |
| --- | --- | --- |
| R1-61-test-fixture-repairs.patch | tests/revision_v1/test_stage4_cell.py | General editing predictions plus collision-free newline token allocation; preserve the separate TinyBase tokenizer. |
| R1-57b-legacy-input-compatibility.patch | src/pccap/revision_v1/analysis_stage4.py | Normalize missing legacy paths while keeping the full expected axes and missing-cell accounting. |
| R1-round10-import-order.patch | Six files listed in logs/r1_round10/import_order_preview.json | Match the repository's default Ruff import grouping; no behavior change. |

The complete CPU revision suite passes **403 tests, 8 skipped**, with the first two patches applied only in memory. The package-layout suite passes **59 tests**. The import-only patch passes default Ruff checks on its changed text. Default Ruff currently reports six I001 import-group findings in the unpatched files; a first-party classification override passes, but the proposed patch removes the need for that override.

The unpatched installed tree therefore has three known new test failures: two fixture limitations and one missing-path compatibility case. The passing preview is not represented as an installed-tree pass.

No scientific or owner files need editing. The supplement producer is one of the import-only files; after approval, create a new supplement artifact with its updated producer hash. Preserve prior register snapshots. Updating tasks.json, STATUS.md, ongoing.md and the lead queue remains the owner's responsibility.

No changes have been staged or committed.
