# Codex round 3 handoff — 2026-09-14

All four available CPU lanes in `docs/ongoing.md` have deliverables. Work used new files only, left Claude's GPU jobs and existing files untouched, and made no commits. The claim's original `in_progress` value is historical; `CODEX-R1-round3.complete.json` is the additive completion record. The lead can mirror the records into the board.

| Lane | Delivered | Remaining owner/lead action |
| --- | --- | --- |
| R1-D1b | [Task record](R1-D1b.md), v2 exclusions and all 236 prior contextual-class dispositions; all 3,000 DEC-037 reasons included; 154,306 candidate records / 87,857 subject keys | Accept the bounded conservative policy; global canonical-entity coverage is not certified. Candidate review, E.2 eligibility and final sealing remain gated. |
| R1-20c | [Task record](R1-20c.md), new physical namespace, immutable reservation, overlap and paraphrase gates; 9 tests pass | Bind model/vocabulary and later exposures, then lead-authorized emission. No actual final examples were generated. |
| R1-24 | [Task record](R1-24.md), CPU recipe and leased GPU harness; 17 tests pass; v1 and current-source v2 dry manifests | Reconcile actual pilot training passes and schedule the GPU run. Literal same-checkpoint self-distillation is a numerical negative control; agree a separate informative treatment if needed. |
| R1-X2 | [Task record](R1-X2.md), [audit](../../logs/audit_r1_25.md), [concurrent-change addendum](../../logs/audit_r1_25_cfc6db6_addendum.md), reproducible controls and 3 class-balance tests | Address delta selection, memory restore/ceiling, transaction, query boundary and cost findings; decide scientific contract amendments or remaining implementations. |

**Read the audit addendum for current state.** Claude landed `f95606a`/`cfc6db6` during validation. Codex reviewed their changes and reran the affected checks. Current continuation preparation is `manifests/revision_v1/r1_24_control_v2.json`; the original correctly refuses execution against changed sources. The active balanced retrain stays with Claude.

Validation: 54 distinct selected CPU pytest cases pass (26 namespace/control, 25 existing repair/reference, 3 new class-balance). Six affected existing tests were additionally rerun after the concurrent training change. Audit counterexamples are expected findings, not failing pytest cases hidden from the count. `logs/r1_round3/validation.json` records source and inventory checks. GPU compilation, training, full-matrix control execution and final-dataset eligibility are deliberately not claimed complete.

The most useful immediate handoff is the X25-01/02/03 repair checklist in the audit. Those fixes require edits to Claude-owned existing files; Codex has not applied them or requested duplicate ownership. Existing task registers, `ongoing.md`, `STATUS.md`, reports and the lead queue were not appended to under the user's creation-only protocol.
