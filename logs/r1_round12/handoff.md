# Round 12 handoff — all four CPU lanes complete

2026-09-15. This lane created new files only; no GPU/base execution, sealed payload reads, commits or edits to
existing files. The owner continued tri3 training/evaluation and development profiling independently.

| Lane | Delivered | Remaining outside this lane |
| --- | --- | --- |
| R1-D7 | [Population memo](../../docs/tasks/R1-D7.md), deterministic count script and source-bound counts | Lead policy/scope decision; final joint clearance |
| R1-49c | [Protocol v3](../../docs/R1_stage4_protocol_draft_v3.md), all U01–U18 statuses | Final reference, population, statistical and resource admission |
| R1-40d | [Matrix v4](../../manifests/revision_v1/run_matrix_draft_v4.json), builder and tests | Exact per-condition/dataset profiles and ceilings; launch remains false |
| R1-X10 | [Review](../review_r1_mquake.md), recount, [edit requests](../../docs/tasks/R1-X10-edit-requests.md), notes patch | Permission and appropriate owner code-identity window for repairs |

Decision-relevant findings:

- MQ cumulative capacity remains **2,100 subjects**. Including 350 endpoint-reserve subjects per realization,
  neither 2×1,000 nor 3×650 fits. Proposed default: three × 300 edits plus reserves, demand 1,950, subject to
  clearance and explicit lead amendment. The nominal 360-cell / 1,000-edit matrix is unchanged pending that choice.
- Waiving only query-role exposure gives **4,218 subjects**, retaining historical primary exposure; 4,818 is
  prospective-only. Executed-only audit clearance gives at most 2,829, with no release certified.
- Local MQuAKE-T contains **1,868 cases / 96 distinct edits / 86 subjects**, not 1,825 independent edit items.
  It is a temporal population and cannot fill the deficit.
- The requested v3-weight gate-off extension changes both training and gating relative to v4. The 45 cells
  remain separate and explicitly qualified; a gate-only contrast needs a lead-approved identity change.
- Composition **0/897** base exact is supported on 299 scored of 300 planned cases; no capability ceiling follows.
  The reported 369 low-null selections cannot be labeled actual post-gate fires from existing traces.
- The development override accepts incorrect mode/dataset, silent sample shortfalls and unvalidated tokens.
  Concrete loader, trace, provenance and report changes are requested, unapplied.

Verification: **507 passed, 8 skipped** (revision-v1 + package layout; 23 new tests); four-file Ruff clean.
Matrix rebuild is identical and verifies 33 identities. New document links resolve.
The proposed notes patch passes `git apply --check`; it was not applied.
[Validation receipt](validation.json), [test log](installed_cpu.txt), [Ruff](ruff.txt).

The starting source snapshot is at e22f9d7. During work the owner committed 3f2d65a, splitting the old exposure
audit and generating freeze candidate v2. The count script understands the split index and verifies both parts;
it does not require the removed monolithic file. The matrix/protocol remain unfrozen drafts.
The owner's tracked update to `results/R1/stream_eval.md` and new tri3/profile results were not edited or committed
by this lane. New synthetic driver test outputs were produced by the existing CPU suite; they are not research runs.

No task-board/ongoing edits were made under the new-files-only rule. The separate completion receipt supersedes
this lane's initial claim for orchestration. Existing permission requests are not assumed approved.
