# Revision v1 — loss-source table (X0-04; Stage 2 deliverable before R1-21/R1-22)

Orchestrator, 2026-09-13 18:30 EDT. Every training signal the outer step may use, with its population, target source,
denominator, and which leaves are trainable or stopped. Anything not in this table is not a loss. The read path
(`RevisionCap.predict`) receives none of the targets below (gate 1).

| # | loss | population (per episode) | target source | denominator | trainable leaves | stopped / constant |
| --- | --- | --- | --- | --- | --- | --- |
| L1 | answer NLL | every answer prefix of queries with role `new_paraphrase` or `old_fact` | the episode label's target ids (synthetic rule, or the taught answer for natural data — never a revised answer scored against a teacher) | per-token mean over the prefixes in the episode | reader (query head, tap encoder, key head via selection, code head), controller | base weights; observation features (write-free pass); fast-step deltas (first-order surrogate, declared) |
| L2 | retrieval / null CE (X0-03) | every query with a role; one target among ALL episode records + null (no top-k) | `supporting_record_ids` → record index; roles `near_miss`, `unrelated` → null | per-query mean | reader (query head, key head, tap encoder, null) | base; codes; controller |
| L3 | preservation KL | every answer prefix of queries with role `near_miss` or `unrelated` | the cap-off logits of the same prefix (the write-free observation pass; identical to what a hard null returns) | per-prefix mean | reader (through selection mass and query), controller | base; cap-off logits |
| L4 | code-norm penalty (optional, default 0) | all records | — | per-record mean | code head | — |

Objective: the optimized quantity is the SUM over an episode's prefixes of the per-prefix terms (L1, L3) plus L2; the logged
`answer`/`preserve` values are per-prefix means (R23-01). Record codes derive from the prompt + answer observation with the
answer span as the summary mask (R23-02); keys from the prompt observation. The ePC trainer is an ePC-credit surrogate for
the cap weights; the base stays frozen (R23-03).

Rules:
- Teacher imitation never scores a revised answer: L3 is applied only to roles whose correct behaviour is "unchanged"; a
  revised fact's queries are in L1 with the new answer as the target (asserted in `train.py`).
- L2 runs over every record of the episode, so a relevant record outside the inference-time top-4 still receives a
  gradient (test: `test_retrieval_loss_reaches_records_outside_top_k`).
- Selection at training time is the soft applicability over all records; at inference it is the top-4 restriction plus
  the hard-null threshold (declared approximation; the gap is measured, not assumed).
- Fast-step deltas: the reference trainer runs with `fast_steps = 0` (initial codes only). When fast steps are enabled,
  their deltas enter as constants (first-order surrogate) and the configuration says so in every record.
- Matched BP / ePC schedules (R1-22): identical episodes, seeds, masks, optimizer state schedule and stop-gradient
  boundaries; only the gradient estimator differs.
- Composition queries are excluded from L1–L3 in Stage 2 v1 (counted in the episode record); they return with the
  two-hop endpoint (plan 9 §Stage 4).
