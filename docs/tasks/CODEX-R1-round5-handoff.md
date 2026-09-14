# Codex round 5 — handoff

2026-09-14. Entry task list: `docs/ongoing.md` §3 at HEAD `777373b`. All work was CPU-only and additive. Existing tracked files and the Git index are unchanged; nothing was committed, staged or pushed. Claude's active pilot and existing untracked result trees were left alone.

| Lane | Delivered | State |
| --- | --- | --- |
| R1-43 | Endpoint module, CPU tests, schema/denominators and task record | Implementation ready; one mock-fixture serialization repair needs permission before normal pytest can pass |
| R1-24b | Informative LM JSON recipe, generator and 23 passing arithmetic/provenance tests | Complete dry deliverable; lead decision/runtime/GPU execution remain future work |
| R1-X4 | Full Stage 2 review, all notes/stream-table rows, source/ledger/detail recount, findings X4-01…10 | Report complete; supplemental tag-audit helper correction awaits permission |
| R1-30a | Optional cap-level PC design with FabricPC integration, controls, gates and concurrent subtasks | Complete specification only |
| R1-27 follow-up | Superseding CPU boundary fixtures against current repairs | One statement-count fixture correction awaits permission; intended orphan-checkpoint failure reproduced |

Read [the Stage 2 review](../../logs/review_r1_stage2.md) and [Stage 3 draft](../R1_stage3_design_draft.md) for the research conclusions. Task records are `R1-43.md`, `R1-24b.md`, `R1-X4.md` and `R1-30a.md` in this directory.

## Permission gate

The consolidated [edit request](CODEX-R1-round5-edit-request.md) supersedes the scope of the first endpoint-only question. It requests exactly three one-line corrections in newly created validation files:

1. Convert mock snapshot token IDs to Python ints before JSON serialization.
2. Correct the actual driver preflight's expected AST statement count from 7 to 6.
3. Match complete CounterFact table tags, including the dataset suffix.

No production-owner file or task board is included. The exact patch is `logs/r1_round5/repair_preview_v2/proposed.patch`, with before/proposed hashes and verification beside it. It has **not been applied**. After permission, check the before hashes, apply the three lines, run the normal endpoint/LM/boundary pytest files using a fresh fixture directory, and run the table audit to a fresh JSON path. Write an additive verification update. No new permission for those exact approved edits is needed once the user grants it.

## Verified now

- Normal LM pytest: **23 passed** in 0.08 s.
- Existing memory/reader/controller/learner CPU regression subset: **21 passed** in 9.04 s.
- Proposed repaired sources executed in memory: **19 test functions passed**, one intended production checkpoint-guard failure; all **30 stream-table rows** match.
- Ruff across all nine new Python files: passed.
- All bound source/resource hashes unchanged, local document links resolve, tracked working tree/index unchanged.
- Evidence: `logs/r1_round5/final_verification.json`, `lm_recipe_cpu.txt`, `core_cpu.txt`, `ruff.txt`, and `repair_preview_v2/verification.json`.

The unedited endpoint and superseding-boundary test files still have fixture failures. Do not claim a clean full-suite run. Old R1-26 tests retain their obsolete fixture assumptions; this round adds a superseding file rather than modifying them.

The authoritative recount is `stage2_recount_v2.json`. The original `stage2_recount.json` is incomplete invalid JSON from a failed export. The original supplemental table audit misses nine suffixed rows because of its pending helper fix; use the explicitly labeled repaired-preview output. Historical failed logs remain in place under the new-files-only rule; they are not final research artifacts.

## Owner follow-ups

- **Before new reference streams:** fix X4-10. The driver's checkpoint guard inserts an extra `results/` component compared with the actual harness destination. The new CPU fixture reproduces acceptance of an orphan actual checkpoint root.
- **Evidence recovery:** eight historical zsRE detail directories were overwritten by CounterFact runs, including the main 0.65 condition. Saved summaries support the displayed rates, but cannot restore raw paired evidence. Rerun selected comparisons under unique dataset/configuration identities.
- **Compute:** pilot wall columns agree, but the BP outer training path bypasses important ledger accounting. Reconcile actual forward/reverse work before matched-compute claims or control-budget certification.
- **Endpoints:** actual development counts are 400 near-neighbours, 100 revisions and 54 composition rows. Composition has no reviewed direct query and a 46-row coverage shortfall. Label/question work is a separate CPU lane.
- **Continuation:** the dry LM recipe uses 493,752 student forward positions / 3,858 Adam steps, with a final 56-position chunk. The shared evaluation theta is intentionally inherited from the literal companion; update both if choosing a newer reader. Equal reported forward tokens do not match exposure or reverse compute.
- **Stage 3:** the current delta path bypasses the code controller, so code-only settling with fixed selection cannot change those writes. Review the proposed route-latent coupling and D-R5 before implementation; no solver/training campaign was launched.

## Completion and commits

The additive completion JSON inventories this round's new files and pending work. Existing `tasks.json`, `STATUS.md`, `ongoing.md` and cost ledgers were not edited; the orchestrator can mirror the task records. GPU cost is zero. Shared agent wall time is recorded once, not duplicated across the four task rows.

No commit was requested for this round. Before a later commit, complete the approved validation edits and decide whether to retain failed-attempt artifacts; do not stage Claude's unrelated result trees as this agent's changes.
