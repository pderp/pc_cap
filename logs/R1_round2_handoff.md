# Codex R1 round 2 handoff — 13 September 2026 (EDT)

The user-approved five-file repair bundle was already applied verbatim by the orchestrator in **`8f49955`**. All installed hashes match the tested candidates, and **52 generator/adapter tests pass**. The generator is installed under `pccap.revision_v1.episodes`; no duplicate repair or source move was performed.

The four open CPU lanes in `docs/ongoing.md` have delivered the following new artifacts. No GPU process was started or interrupted; sibling repositories and installed core files remain untouched. No commit or status-register edit was made.

| Lane | Delivered | Still open |
| --- | --- | --- |
| R1-D1 | Versioned exclusions; candidate indices/subjects; exposed-text entity-review inventory; independent reconstruction | Permission for the original script's one-line repair; canonical entity review, later exposures, E.2 and sealing |
| R1-20b | 160 CounterFact development episodes, partition/source hashes, all 279 exposed source subjects, optional 880-prefix teacher request | New final synthetic entity namespace/version and approval; optional GPU teacher diagnostics |
| R1-X1 | Diagnosis review and exact CPU recount of saved traces/checkpoints/costs | Core owner's response and any bounded follow-up diagnostic |
| R1-23 | Installed-code audit, numerical counterexamples and positive boundary controls | Core owner's repairs, objective/phase completion and revalidation |

Read [the diagnosis review](review_r1_diagnosis.md) and [the code audit](audit_r1_23.md) before interpreting further pilot sweeps. The main practical issues are:

1. L1/L3 metrics report means while BP/ePC accumulate summed gradients. A duplicated identical prefix doubles the gradient with no change in reported mean.
2. The zero-fast-step pilot initializes fact codes from support prompts alone. Swapping the taught answer has no effect on those codes; a differentiable fast unroll is not implemented.
3. The current ePC treatment changes reader/controller gradients over a frozen base. It is not the guide's alternating local base-weight-learning condition.
4. Rejected revisions, query boundaries, snapshot identity and total-byte/cost accounting have reproducible defects. Fix these before treating the learned-cap gates as passed.
5. Stage 0's retrieval/observation explanation is useful but qualified. The .44 in-stream stable comparator is distinct from the .67/.49 shadow-key diagnostic; shadow locality was not measured.

The data inventory leaves **155,322 raw MEND records / 88,267 normalized subjects**, after old pools/development/S7 and conservative exposed-text/alias exclusions. These are candidates, not teacher-eligible independent facts. All candidate indices independently reproduce, and all newly emitted natural source subjects are excluded. Every text field still needs canonical entity review; lexical coverage cannot guarantee entity disjointness.

The synthetic manifest deliberately says **`final_generation_ready=false`**. All existing v1 contexts were already exposed during development. The proposed final seed range alone cannot cure that; a new entity namespace/version must be implemented and frozen. The corpus's split named `test` is an inspected development audit partition, never a final-test claim.

## Parallel continuation

- **Core owner / CPU:** fix loss denominators; implement transactional memory semantics and query/snapshot boundaries; add total-byte accounting. Those areas can be divided, with query-cache and snapshot changes coordinated.
- **Reference implementation / CPU:** design the support-answer-sensitive code path and differentiable fast unroll. Implement the alternating BP/ePC base phases after their interfaces and leaf masks are fixed.
- **Data / CPU:** canonical entity/alias review and new synthetic namespace can proceed while those repairs or the active pilot run. Freeze no final data yet.
- **GPU owner:** finish or preserve the already-running SD-24 corrected pilot as exploratory evidence; after repairs, run a small matched behavioral pilot and support-answer/revision controls. Follow-up all-policy locality diagnostics share the GPU and should be queued.
- **Lead / review:** respond to the diagnosis/audit findings, decide any changed scientific contract and the final generation reservation, and handle v0 T4 / SD-24 SE-E rerun decisions already in the lead queue.

During this work the orchestrator advanced HEAD from `9368d47` through `9b88dea`, including SD-24 (`67700f7`). Active CounterFact/ePC pilot directories and `results/R1/pilot/surrogate_check.json` are other-agent work and are excluded from this handoff's ownership. Existing boards/claims were not edited; the new completion record supersedes the round-2 in-progress claim for delivered tasks.

One local draft issue remains under the user's permission rule. `scripts/r1_d1_exclusions.py` initially encountered synthetic S7 pairs without a natural-language `subject` field and stopped before writing outputs. The new `scripts/r1_d1_exclusions_v2.py` restricts that loop to zsRE/CounterFact and completed the inventory. The exact tested one-line repair for the original entry point is `docs/tasks/R1-D1-script-fix.patch`, with guard hashes in the companion JSON. Permission was requested; use the working v2 entry point until it is granted. This issue does not invalidate the generated inventory.

Task details are in `docs/tasks/R1-{D1,20b,X1,23}.md`. Validation and hashes are in `logs/r1_round2/`; data payloads remain under `/home/derp/cap/assets/data/prepared/revision_v1/`. Rerun commands require new output names and refuse overwrites.
