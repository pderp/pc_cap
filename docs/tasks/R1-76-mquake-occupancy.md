# R1-76 — MQuAKE occupancy population options for lead Q10

Status: metadata review complete; no MQuAKE model execution or new role allocation.
Agent: Codex, 2026-09-16. Experimental deadline: October 9.
Evidence: [capacity audit](../../logs/r1_round17/R1-76-historical-mquake-capacity.json),
[register v6](../../manifests/revision_v1/exclusions_frozen_v6.json),
[primary v5](../../manifests/revision_v1/primary_condition_v5.json).

## Finding

The current automatic runner has 100 eligible MQuAKE development rows and no post-training tail:
the selected reader used all 500 rows in training v3. The full occupancy design requires **1,000 edit facts
plus 100 distinct outside facts**, with the same outside prompts disjoint from every future filler.
Repeating facts, using already trained rows or quietly changing the outside set would change the question.

There is a possible **partial** route within already excluded historical material. A metadata audit of the
old v2 training pool (1,000 rows) plus legacy development (200 rows) finds 1,200 distinct subjects.
Removing the selected reader's 500 training subjects/items and exact training-query overlaps leaves
**700 distinct metadata-eligible rows**. The audit checks all three selected training prefixes and exact
own/paraphrase/locality query text, not only the MQuAKE prefix. No rows were emitted or executed.
These are already historically primary-exposed, so reusing them need not consume the 4,218 final candidates.

Seven hundred is enough nominally for **300 edits + 100 outside**. It is not enough for **1,000 + 100**:
the shortage is 400. Eligibility here is metadata-level, not completed teacher/token/alias clearance.
An owner-approved 100/300-only development diagnostic would need a new versioned population/spec and
runner cadence; the delivered production runner deliberately insists on the full 100/300/1,000 design.

## Options and consequences

| Option | Capacity implication | Exposure / interpretation |
| --- | --- | --- |
| Retain the unavailable 300/1,000 points | No new use of MQuAKE sources | Honest limit; no occupancy-flatness claim |
| Audit the 700 historical-primary-exposed rows, then run 100/300 with one outside100 | 400 distinct eligible rows required; nominally possible | New to this selected reader's training items, historically exposed elsewhere in the project; label both facts. No inferred global novelty |
| Spend final-register headroom | At most 168 nominal subjects, before clearance losses | New development edits become primary exposure and must be removed cumulatively. Not a pool currently free to use |
| Historical 700 plus all nominal 168 | At most 868, still 232 short of 1,100 | Cannot solve full occupancy while preserving nominal 4,050-subject demand, even before clearance losses |
| Take the apparent remainder of 6,043 items | No valid capacity established by subtraction | Items repeat subjects; many already trained, exposed, excluded or prioritized to zsRE. This is not 6,043 minus 4,050 usable facts |
| Obtain additional independently eligible facts | At least 400 beyond the historical 700 for this design, plus clearance reserve | Requires new source/eligibility/exposure identity and a separately admitted diagnostic population; do not relabel it unchanged MQuAKE-CF |
| Reuse trained fillers, duplicate subjects or revise existing records | Can increase attempted updates but not the intended independent occupancy population | Different experiment: trained-memory or revision load. Does not answer reader-unseen 1,000-record rejection |

The 4,218-subject register is a nominal clearance input, not 4,218 guaranteed eligible subjects.
Demand is three realizations × (1,000 edits + 100 outside + 100 near supports + 100 neighbors + 50 revisions)
= **4,050 subjects per dataset**. A clearance loss of 169 already causes a shortage. Existing subject aliases,
context limits, teacher eligibility and joint challenge dependencies may consume all headroom.

The source pool's 6,043 items cover 5,577 subjects. DEC-048 leaves 4,218 candidate subjects after
159 under zsRE priority and 1,200 historically primary-exposed subjects. The 159 zsRE-priority subjects
are not a safe additional MQuAKE development pool: using them could impinge on another dataset's reservation.
The policy's exemption for true-fact query presentation does not exempt a new counterfactual training/edit use.

## Recommendation for the lead

Keep the full 1,000-record MQuAKE point unavailable. If a useful partial result merits owner GPU time,
authorize a bounded metadata/alias/context review of the **already reserved historical 700** and a separately
identified 100/300 common-outside assay. Do not spend final-register slack to chase the 1,000-record point;
the arithmetic cannot close that gap. The full common-population design can proceed on zsRE and CounterFact
once the owner's identity-bound recipes and GPU schedule are ready.

Q10 can distinguish: (A) keep MQuAKE unavailable, or (B) pursue the historical-reservation 100/300 diagnostic
with the 1,000 point explicitly absent. Neither changes confirmatory scope or resolves Q4/Q5.
The orchestrator posts the lead question; this lane has not edited the lead queue or contacted another agent.

## Delivered runner and validation

[scripts/r1_76_unseen_common.py](../../scripts/r1_76_unseen_common.py) prepares populations without a model,
rejects full-size MQuAKE capacity before acquiring a lease or constructing a base, and executes one incremental
stream only under an explicit owner command. It checks item, fact, normalized subject and normalized prompt
disjointness against the entire largest edit inventory, plus selected training items and exact training queries.
Outside text/IDs and metadata hashes are fixed across checkpoints; paired gains/losses in firing are reported.
An unmet actual target occupancy stays unavailable. Query-state mutation aborts and preserves failure logs.

The zsRE and CounterFact development populations are prepared under assets, with new bound spec files under
docs/tasks. Six CPU tests cover actual TinyBase checkpoints, source shortfall, future-edit overlap, exact-query
training exclusion, missing occupancy and query purity. No real-base experiment, final candidate draw,
reservation read, source-file edit or commit occurred.
