# Lane V2 — progress before fixture correction

Status: incomplete; awaiting permission to correct a newly created study script.
This is not the completed `review_repairs_r2b.md` acceptance report.

The orchestrator's nine confirmation controls pass (6.76 seconds), recorded in
`results/V2/existing_controls.txt`. The expanded independent study created a fresh
resource tree under `assets/tmp/`, ran the actual S4 CLI/stage/confirmation loader,
selection, stream, snapshots and collectors with CPU fake models/evaluation, and
completed **150/150** scheduled synthetic S4 runs. No production final freeze was
written, no sealed production payload was opened, and no GPU was used.

The expanded study then stopped because its own S5 fixture replaced the checkpoint
schedule with `[1, 2]`, while the schema requires `[100, 300, 1000, 3000]`. Thus its
nominally valid S5 case was denied before stage execution, and collecting a nonexistent
Cap configuration raised `IndexError`. This is a review-fixture error, not a demonstrated
S5 repair regression. The original stdout/stderr and fixtures are preserved.

`results/V2/partial_summary.json` reconstructs completed runs from their persisted
configs. The negative schedule/base/read/code-drift checks reached their assertions;
code drift was refused without the explicit override and completed with the override.
The synthetic wrong-BP-hash and wrong-tokenizer-hash cases also completed. Inspection
of `stage_s4.run_s4`, `BPBase.__init__`, and `GPT2Tokenizer.__init__` found no startup
comparison against the corresponding frozen hashes; base immutability before/after
an edit is a different check. These probes use fake supplied resources and do not
claim that a real corrupted model/tokenizer was loaded. They identify an unresolved
boundary check for the completed review to assess.

Remaining expanded controls: valid and invalid frozen S5 authority, forced rerun with
different learned state and preserved external checkpoint bytes, two-experiment and
unknown-experiment filtering, stage limits (including missing per-run allowance),
and final source/evidence provenance. Static inspection additionally found that the
collectors accept missing experiment IDs even when filtering by a specific ID, and
S7's CLI does not expose its loader's experiment filter. These observations still
need the planned independent runtime controls before the final report.

The concrete correction plus diagnostic lint cleanup is
`docs/tasks/CODEX-20260911-review-tools-v2.patch`; its request explains the exact two
script edits. It supersedes earlier patch proposals and has not been applied. Proposed
text compiles and passes Ruff through stdin. No task status or existing code was
changed to mark this review complete. After permission, rerun from a fresh fixture
root and capture new logs; retain the failed attempt.
