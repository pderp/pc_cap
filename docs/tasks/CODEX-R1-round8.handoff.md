# Codex round 8 handoff

All four assigned CPU lanes are complete as additive deliverables. No existing file was edited, no GPU/model was
executed, no confirmation example was drawn/read, and no staging or commit was performed by Codex. The owner continued
working and committing independently throughout this round.

| Lane | Deliverable | Result |
| --- | --- | --- |
| R1-49 | [Stage 4 protocol draft](../R1_stage4_protocol_draft.md) | 240-cell identity and denominator specification; paired-cluster analysis; freeze checklist; U01–U18 open gates |
| R1-D1f | [accepted-register binding](../../manifests/revision_v1/exclusions_frozen_v3.json) | 14 verified child hashes, correct 52,498 zsRE overlay, both CounterFact readings; no draw authorization |
| R1-50b | [ordinary-text null specification](R1-50b.md) | source/split/sampling, loss weights, prefix and drift denominators, current implementation gaps and budget arithmetic |
| R1-X7 | [continuation review](../../logs/review_r1_24.md) | 16 cells/9,042 accepted steps reconcile; literal passes base fidelity; LM fails; locality attribution qualified |

Verification: **15 CPU tests passed**, Ruff passed, all report links resolve. Final integrity rechecked 82 R1-24 source
bindings and the register's 14 bindings with no mismatch. The main source snapshots and six documents retain their
recorded hashes. See [integrity audit](../../logs/r1_round8/final_integrity_audit.json). Completion/status metadata is in
`CODEX-R1-round8.completed.json`; the in-progress claim is a historical record and has not been rewritten. The owner
can mirror task status without this agent editing the existing board.

## Owner priorities after reading the draft

1. Finalize reference admission after R1-54 seed, CounterFact drift and long-memory checks. A text-null successor changes
   exposure and training cost; it cannot inherit the old reference's continuation budget automatically.
2. Correct/qualify the R1-24 notes: S1 has an active StableCap; executed literal self-KD changes parameters; LM's failed KL
   gate remains failed despite improved NLL. Either admit a fidelity-valid S1_LM or record a scope change.
3. Resolve composition's verified inventory and allocation, comparator observers and the revision pairing/analysis
   adapter. The old analysis wrapper uses .02 and fixed v0 arm names, while revision requires .05 and new conditions.
4. Profile the full P1–P4 workload and choose affordable scope before setting ceilings. The 240-cell proposal has
   144,000 new unseen decodes and no admitted total cost.
5. Select primary contrasts/multiplicity and exact endpoint conventions, complete exposure/source/eligibility decisions,
   then seal and obtain the lead freeze.

The text-null spec proposes separate training/selection-development windows and independent factual/text RNG streams
for future controlled comparisons. Current training reuses the text bank in development and changes subsequent factual
episodes when text sampling consumes the same RNG. L3 gradients sum over prefixes while logs display means.
These are explicit owner implementation/recipe decisions, not edits performed in this round.

## Concurrent updates caught at final handoff

The main protocol/reviews have an explicit earlier source cutoff. A later check found owner additions in the notes and
decisions; their contents and the three new endpoint summaries are preserved under
[the handoff snapshot index](../../logs/r1_round8/handoff_source_evidence.json). This supplement does not rewrite the
earlier documents.

- A **DEC-042 (proposed default)** row now appears in `decisions.md`. It is labeled proposed and leaves the draw/seal
  to the lead. It is not an explicit accepted CounterFact source decision at this cutoff. The immutable DEC-041 wrapper
  therefore remains correctly unselected; a final draw manifest must bind the accepted source decision separately.
- Owner endpoint summaries for the seed-0 text-null reader now record 100/100 near-miss preservation and 100/100 explicit
  revision success on development challenges. Composition remains unreachable without verified direct questions.
  This progresses real-base endpoint execution, without resolving fresh challenge inventories or all comparator adapters.
- The new zsRE unseen summary records **7/100 false fires**, 7/100 bounded answer changes and strict complete preservation
  .93. This reinforces that zero ordinary-text firing is not the same as rejecting unseen factual edit prompts.
- The CounterFact unseen summary records **0/100 false fires and 0/100 bounded answer changes**, with 67 terminated
  answer pairs and 33 truncated pairs. Its saved strict complete-preservation rate is **67/100 = .67**.
  A complete-pairs-only answer-change statistic uses 67 as its denominator; that must not replace the full-inventory
  denominator or be described as 100% strict complete preservation. The records already distinguish these quantities.
- These late summaries were inspected for status/denominator handoff; their full per-case execution was not independently
  rerun or audited by Codex. They do not change the completed R1-24 review.

All implementation and GPU work remains with the owner. No permission to edit an existing file was needed to finish
these four lanes. The additive artifact inventory separates this round's deliverables from concurrent owner files;
pytest scratch files are listed separately and need not be committed.
