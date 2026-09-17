# X15 factual/operator document corrections — proposed only

Status: prepared for owner review; **not applied**. The X15 lane explicitly requires new files and edit
requests, even though the user's general existing-file prohibition was lifted.

`R1-X15-document-corrections.patch` proposes factual updates to:

- `docs/R1_stage4_protocol_draft_v5_2_D.md`: completed teacher/roles, immediate-newline zsRE caveat,
  installed R1-77d status, 112 declared recipes and the all-dataset near-family admission scope.
- `docs/R1_execution_plan_v1.md`: current option-D/version/receipt ordering, observed concurrency
  qualification and actual stop/review/resume behavior.

It deliberately leaves the unresolved meaning of `ceilings.wall_seconds` to an explicit owner decision
(X15-03), and does not invent measured full-endpoint costs or admit Q15. No thresholds, filters, comparisons,
counts, allocations or missingness definitions change.

Applying these document edits changes protocol/matrix/request/freeze bindings. Preserve historical bytes,
version the final matrix/protocol and regenerate downstream forms/candidate; do not silently update a
signed receipt. The patch is based on the bytes reviewed this round; `git apply --check` validates it.
All old signatures would require exact re-review. Detailed findings: [R1-X15](R1-X15.md).
