# Revision v1 — Codex handoff, 2026-09-13

Current assignment: R1-00, R1-20 and R1-X0 from `docs/ongoing.md`. No GPU work, existing-file edits or commits by Codex in this task. Claude's active queue/source restoration remains untouched.

| lane | delivered | remaining |
| --- | --- | --- |
| R1-X0 | Completed review: `logs/review_plan9.md`, 14 findings, PDF-page references and requirements matrix; reproducible subject/paraphrase audit | Owner response and any plan/diagnostic changes |
| R1-00 | `manifests/revision_v1/baseline.json`: all 12 guide values reproduced from 45 saved runs; 45,000 immediate acquisition rows checked; 20 asset hashes verified; per-realization/order details preserved | Permission to apply direct-script repair; final lead-approved close-out snapshot |
| R1-20 | Tested implementation in `revision_v1_staging/episodes.py`; CounterFact episode/text-token adapters; 52 passing candidate controls; 384 synthetic episodes / 2,304 queries audited | Apply draft repairs with permission; source release/install; Stage 1 integration; teacher preservation targets; second zsRE paraphrase source |
| R1-23 | Not started: real parameter/label-path audit depends on Stage 1/2 implementation | Available after those implementations exist |

## Code and evidence to use

* **Latest validated generator:** `revision_v1_staging/episodes.py`, byte-identical to `logs/r1_codex_20260913/proposed_v2/r1_20_episodes.py`, SHA256 `b1d66ac7a620b0571d4eb895e7a6a0e8459b877af952371cc8156e7d17eeb80b`.
* **Latest repair bundle:** `docs/tasks/R1-created-files-repairs-v2.patch`; rationale and scope in `docs/tasks/R1-created-files-edit-request.md`. It targets five files created in this task. **Unapplied pending permission.**
* **Focused candidate tests:** `logs/r1_codex_20260913/verification_v2/pytest.txt`: 52 passed, 1.79 s. Candidate Ruff and `git apply --check` pass. The original draft's two composition failures remain until the patch is applied; do not run the original draft as if it were the tested candidate.
* **Coverage/data separation:** `logs/r1_codex_20260913/episodes_v2/audit.json`; example labeled containers in its sibling `sample_episodes.json`. This is generator correctness, not trained-model performance.
* **Baseline execution:** the candidate-aware replay command in `docs/tasks/R1-00.md` generated `manifests/revision_v1/baseline.json`. The capture is a pre-close-out snapshot at `075c4bb`, not a fresh revision freeze. Provenance in `logs/r1_codex_20260913/provenance.json` identifies the actual executed candidate.
* **Fresh-data accounting:** `logs/r1_codex_20260913/data_inventory.json`. All exposed S7 candidate subjects should enter the proposed exclusion inventory; using just executed pairs misses 330 zsRE subjects. The 88,503 remaining conservative MEND subject candidates are not E.2-qualified or sealed.

## Interface handoff

The staged generator is self-contained apart from the unchanged grammar generator. `SupportExample` carries supplied teaching labels; `PredictionQuery` carries only query ID and prompt text/token IDs. `LabeledEpisode.query_labels` holds scoring labels, roles and composition-grounding links. Prediction must receive an individual query's causal prompt plus memory; adaptation receives only `inputs.adaptation_batches()`, with a fresh memory for each independent episode.

`scripts/r1_20_text_adapter.py` provides real GPT-2 tokenization and the grouped `design_payload` requested by `docs/revision_v1_design.md`. It does not define or edit the orchestrator's `Episode` class. The generator audit itself emits text for natural episodes; the separate adapter's tests verify prompt/answer token boundaries and label poisoning. Natural preservation targets remain unresolved until the owner supplies cap-disabled teacher outputs, and `require_training_targets` refuses them in the meantime. Synthetic token IDs use the explicit 64-token grammar vocabulary and must not be silently reinterpreted as natural GPT-2 text.

Natural partitioning runs on both development pools together, joining fact IDs, normalized source entities and operational paraphrase families before generating episodes. CF relations are conservatively grouped as entire families. These source-level controls do not yet establish alias-resolved disjointness of every entity mentioned inside neighborhood/context text. All inspected synthetic and natural `train/dev/test` fixtures in these outputs are **development data**, including the split called `test`; they cannot be promoted to fresh confirmation.

## Changes observed during this work

The orchestrator committed `205528c`, explicitly forbidding all new Python files under `src/pccap` until a `v0 close-out committed` line appears in `docs/lead_queue.md`. This confirms and resolves the coordination ambiguity recorded as X0-13. Codex's source has stayed outside that tree throughout. Commit `075c4bb` adds the Stage 1 design note: it supplies more snapshot/ledger detail and a cached-observation condition, partially addressing X0-06. The plan review remains a snapshot against the accepted plan; these additions are reconciled here without editing that review.

## Most consequential remaining decisions

1. Review the D0/D1/D2 implementation before its GPU allowance: oracle prefix fallback and stale slot ownership need qualification, and detailed traces/complete diagnostic cost deltas should survive aggregation (X0-14).
2. Add the guide's teacher-only continuation control and define the common fast-update adapter for a clean cap architecture contrast (X0-01/02).
3. Supply a verified second zsRE paraphrase: 300/300 current development items have only one. CounterFact supplies two and has constructed episodes in all three development partitions.
4. Freeze a complete exclusion inventory and a measured, deduplicated run budget. The four-week calendar and approximately 40-hour total are planning assumptions, not demonstrated performance.

The pending edit request is limited to the newly created drafts. Other productive work has been completed into new files; the source install, full training readiness and R1-23 are separate dependency gates, not tasks silently marked done.
