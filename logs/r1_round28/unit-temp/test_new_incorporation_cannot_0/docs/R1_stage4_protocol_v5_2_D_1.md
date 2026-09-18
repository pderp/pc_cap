# Stage 4 protocol v5.2-D.1 — DEC-062 amendment for lead signature

Round 28, 2026-09-17. Experimental completion remains **October 9**, before the October 15 presentation.
This text implements DEC-060 option D, DEC-061 NM-template-v1, DEC-062 coordinated allocation and the adopted R1-D10e context rule. It grants no draw,
seal, freeze or execution authority. The unchanged scientific definitions, conditions, scoring,
restoration requirements and DEC-057/058/059 rules are incorporated from
[v5.1](R1_stage4_protocol_draft_v5_1.md); the replacements below govern population, cadence, near-miss semantics and queue operation.
The earlier [option-D candidate](R1_stage4_protocol_draft_v5_2_option_D.md) is preserved as history.

## Population and exposure

| Dataset | Realizations | Edits each | Checkpoints | Required distinct subjects | Certified usable subjects | Margin |
|---|---:|---:|---|---:|---:|---:|
| zsRE | 3 | 1000 | 100, 300, 1000 | 4050 | 6084 | 2034 |
| CounterFact | 3 | 1000 | 100, 300, 1000 | 4050 | 6121 | 2071 |
| MQuAKE | 3 | 300 | 100, 300 | 1950 | 2161 | 211 |

Each realization also reserves outside100, near-support100, near-neighbour100 and revision50.
Subject and fact disjointness applies across datasets, realizations and roles. The five orders
100–104 reuse a realization's reserved facts and endpoints. Composition uses only already
reserved edit dependencies. Planned missing endpoints retain their denominator and reason;
there is no substitution or resampling to improve availability.

The [adoption receipt](tasks/R1-D10e-orchestrator-review.json) and
[promotion record](../logs/r1_round24/r1-d10g-promotion-v2.json) bind both predecessor evidence versions.
The adopted rule waives ordinary-text training/drift context matches without subject annotations;
it does not waive direct subject exposure, reserved near-miss cases or ambiguous query mentions.
The initial promotion reserved 69 declared development recipes through e697dba, executed or pending.
The current supplement covers 79 declarations, including eight R1-73d locality repairs and two
concurrency-probe recipes. All 50 replacement locality strings already occurred in non-waived
primary reservation events; all other payload content is unchanged. No previously uncovered
exposure or additional eligibility loss is introduced. The exact declaration inventory and
source-event witnesses are bound in operative v5 resource version `round24_v2`.
Round 25 adds 33 recipes on the patched identity, bringing the explicit declaration snapshot to 112.
Every added recipe reuses an exactly previously reviewed payload. Teacher certification and joint-role
review are complete; all 93 Hall subset checks pass at 6084 / 6121 / 2161 distinct subjects.
The historical round-25 bindings are in `tasks/R1-D9-inputs-v3-post77d.json`; round-26 forms bind this final text and the adopted family explicitly. Only the exact current signed inputs may authorize an operation. Further payloads or undeclared
exposure require review, and the lead must attest exposure through draw time.

Completed teacher review and joint-role checks certify the table counts. MQuAKE has 2214 eligible items but 2161 distinct subjects, a 211-subject margin.
Its first-representative revision-compatible count is 2158; individual role capacities overlap.

Teacher-baseline limitation: 6036 of 6084 zsRE items pass E.2 because the pinned base emits a
newline immediately (empty text, one step). All 6084 pass teacher/token checks; CounterFact and
MQuAKE teacher generations are nonempty. For most of this zsRE population, ES and RET-GS measure
answer acquisition/generalization against an empty baseline. Teacher-incorrect is not evidence
that the base initially answered the fact, and the historical E.2 eligibility rule is unchanged.
No increased edit count follows automatically from available capacity.

## Receipt, execution and analysis contract

The execution inventory stays at 360 core cells and 45 separately admitted extension cells.
Locality rows equal to any reserved edit prompt or paraphrase in the complete stream are
rejected by both the endpoint constructor and seal validator, including future edits beyond
the first checkpoint. The constructor does not silently substitute rows on a collision.
R1-73d development recipes select the first 50 eligible distinct unrelated-pool prompts after
this exclusion; the previous Chain M locality0/50 is a payload artifact, not a valid locality result.
Blocks B1–B6 retain sizes 45, 45, 90, 90, 90, 45 and their coordinate identities.
D9 input schema 3 and receipt contract version 2 bind the exact per-dataset roles, realizations,
checkpoints, layout hash, matrix and protocol. Legacy uniform contracts remain separately supported;
legacy or counterfactual-layout receipts cannot authorize this layout. Hall feasibility, global
disjointness, source review, deterministic RNG streams and whole-draw failure semantics remain required.

Final recipes require population_contract_version=2 and a bound schema-2 final protocol with
population_decision=DEC-060-option-D, exact layout/hash/matrix, lead approval, no open gates,
explicit extension decision, max_new=32, DEC-053 bounded equality and the October 9 deadline.
The R1-77d source/backend patches are installed. Post-patch development recipes and dry freeze
candidate v8 bound the new identity; round-26 candidate v9 must rebind the policy, family, protocol and completed profile evidence. Final confirmatory recipes still require actual admitted
populations, costs and signed receipts; a dry candidate is not an owner freeze.
Draft matrices and synthetic tests are not executable final admission.

The primary DEC-057 family remains **63 intervals**, allocated 0.05/63. zsRE/CounterFact retain
seven comparisons each, three realization clusters and five paired orders; float64 bootstrap,
seed 0, 10000 draws and linear percentiles are unchanged. Three clusters provide only nominal
approximate coverage. Every MQuAKE 1000-edit primary comparison and its 21 intervals remain
unavailable, even if a stray 1000 result appears in an input. No allocation to a smaller family,
300-to-1000 extrapolation or use of orders as independent clusters is allowed.

At MQuAKE's actual occupancy 300, report outside100 false fires, Wilson 95% uncertainty and
paired change from actual occupancy 100 only with the identical outside population. Attempted
edits alone do not establish occupancy. These quantities are secondary descriptive: threshold
and pass fields remain null. DEC-059's 1000-record tolerances and 100-to-1000 retention changes
remain unavailable for MQuAKE. Revision50, near100, composition missingness and termination/
truncation diagnostics retain their original definitions. Resource ceilings need separate admission.

## Adopted near-miss family — DEC-061

NM-template-v1 uses different reserved subjects with an exactly matching source family:
nonempty `relation_id` for CounterFact and MQuAKE; for zsRE, identical normalized question
templates after replacing the one whole-word occurrence of the normalized subject with
`{subject}`. Bind `scripts/r1_d9e_near_family.py` along with constructor and seal validator.
This measures different-subject relation/template specificity. It does not establish semantic
nearest-neighbour robustness and differs from the historical same-subject development assay.

DEC-062 selects family-coordinated near allocation. Preserve the exact independent
edit, outside and revision allocations across all realizations. From the cleared
pool remaining after those roles, use separately receipted RNG streams to select
disjoint support–neighbour pair units by the exact DEC-061 family definition.
Several pairs may share a family; the planned denominator is 100 pair slots per
realization. Preserve global disjointness and Hall checks. If compatible units
are insufficient, reserve remaining eligible near-role subjects without
replacement and record unmatched endpoint slots explicitly; do not manufacture
compatibility or retry a seed. Within the resulting reserved roles, retain
DEC-061 lexical endpoint pairing: sort supports by item ID and pair each with the
first unused lexical neighbour of the same family. No outcomes enter allocation.
Bind the exact allocation contract and `near_allocation = family_coordinated`
in protocol and RNG admission before the draw. Pair units determine role
membership, not endpoint slot order; a family may supply several disjoint pairs.
The lead's pair-unit clarification is recorded in
[tasks/DEC-062-pair-unit-clarification.md](tasks/DEC-062-pair-unit-clarification.md).

Each available pair is an isolated restored episode: obtain the neighbour's actual cap-off
baseline, apply the support edit, then compare the bounded neighbour generation to that
baseline under DEC-053. Equality is exact text equality with max_new=32; retain termination,
truncation and support acquisition diagnostics. The source's stored neighbour answer is not
the preservation reference. Support acquisition does not filter the denominator.

Retain all 100 planned slot IDs per realization. An unmatched support has an explicit
`no_compatible_reserved_neighbour` reason. Report preserved/evaluated/planned/missing counts,
observed-case rate and termination-sensitive rate separately. A full planned-inventory rate
is unavailable if any case is missing. Do not score missing cases as success or failure.
Constructor and seal validator recompute the deterministic pairing from the source-bound
reserved records; analysis recomputes equality from the recorded baseline/generation traces.

## Costs, concurrency and incomplete inventory — R1-77f / DEC-052

Use [queue concurrency v2](R1_stage4_queue_concurrency_v2.md). Each matrix wall ceiling is
1.5 times the measured solo process cost, already inclusive of the solo safety factor.
Two workers multiply that stored ceiling once by 1.15; one worker uses 1.0. A measured solo
cost of 100 seconds therefore yields ceilings 150 seconds solo and 172.5 seconds concurrent.
Full endpoints, initialization/validation, failed attempts and measured resource use must
enter the final cost admission; estimates from incomplete development endpoints are insufficient.

Run at most two cells from one block, refilling a free worker slot in declared order.
The shared budget sums complete process envelopes, including overlapping time and failures;
it is separate from elapsed wall-clock planning. Reserve the effective ceiling before each
launch or retry. Require a live externally held GPU lease, at least 4 GiB MemAvailable and
at least 6 GiB when launching alongside another cell, plus the existing runner guards.

Retry an ordinary failed cell once from its last certified checkpoint. After its second
failure leave it incomplete and continue to the next cell while the other worker runs.
Retain the durable retry count across queue restarts using the same receipt root. Host-level
failure (including memory guard/OOM or lease loss) stops new dispatch and charges all active
processes. Unknown cost, torn journals or invalid checkpoints require reconciliation; never
repair them by silently dropping history. Finish active workers before crossing a block boundary.

DEC-052 reporting always includes declared blocks/cells, complete blocks, partial/failed cells,
missing checkpoints and endpoints, known charged costs and unknown cost records. Publish this
inventory daily and at every block boundary, even if execution stops early. Report completed
paired subsets with their declared membership and missingness. Do not call a partial block
complete, substitute another condition or treat an exhausted retry as a successful measurement.
The October 9 experimental stop is binding; October 10–14 is reserved for analysis and presentation.

## Remaining operational gates

1. Sign the exact current clearance request after reviewing certified teacher/role evidence,
   joint Hall feasibility and the zsRE empty-generation caveat. Preserve historical producer hashes.
2. Attest exposure through draw time, sign the protocol/RNG forms including DEC-061 review,
   decide the optional extension, and supply the master seed once.
3. Authorize and perform the draw, deterministic endpoints and seal in that order. Review
   actual missing near slots and composition availability; bind independent expected populations.
4. Complete the corrected MQuAKE profiles and admit execution plan v2 with measured full
   endpoint/process ceilings, shared process-hour budget and September 20 schedule decision.
5. Refresh downstream requests whenever prerequisites change. Close U01–U18 with exact
   receipts, freeze the installed identities and final recipes, inspect the queue, then launch.

DEC-061 semantic adoption and installed cadence repairs are complete. Final signatures,
actual draw/seal/freeze artifacts and cost admission are separate from that adoption.

## Change log against the corrected v5.2-D draft

- Adopt DEC-061 across all three datasets, with source-derived validation, deterministic
  pairing, fixed missing slots and actual cap-off neighbour baseline scoring.
- Carry forward X15's factual corrections: installed R1-77d, 112 declared recipes, completed
  teacher/joint-role review, 93 Hall checks, 2161 MQuAKE subjects/211 margin and 2158 revision
  representatives. Remove stale instructions to apply the already installed cadence patch.
- Retain the 6036/6084 empty zsRE baseline caveat and distinguish acquisition from correction
  of an initially answered fact. E.2 eligibility is unchanged.
- Define the stored solo ceiling and apply 1.15 once in two-worker mode; distinguish summed
  process envelopes from elapsed wall time. Replace first-failure draining with retry once,
  then skip the incomplete cell; host failures continue to stop dispatch.
- Make DEC-052 missingness, daily inventory and block-boundary reporting explicit. Scope,
  condition identities, paired orders, October 9 stop and 63-interval family are unchanged.


## Normative dependency closure for binding — R1-49j

The complete documents below must be hash-bound, including this amendment.
The current amendment governs the changed population, cadence and allocation;
later explicitly adopted decisions supersede conflicting historical provisions.
Binding an older document does not revive a superseded budget, arm or cadence.

| Document | Role and incorporation edge |
|---|---|
| `docs/R1_stage4_protocol_v5_2_D_1.md` | This governing amendment. |
| `docs/R1_stage4_protocol_draft_v5_1.md` | Incorporated statistical definitions, scoring, conditions and restoration requirements. |
| `docs/R1_stage4_queue_concurrency_v2.md` | Incorporated dispatch, retry and shared process accounting policy. |
| `docs/updated_plan9.md` | v5.1 refers to its full-validation and revision-programme obligations. |
| `docs/more_input/pc_cap_coding_agent_guide (1).pdf` | Plan 9 adopts the guide as the specification. |
| `docs/more_input/pc_cap_joint_redesign_proposal (1).pdf` | Plan 9's adopted redesign source, subject to later decisions. |

The results-overview PDF and prior protocol drafts are historical evidence;
they are not additional incorporated rules. The source/exposure receipts,
accepted decision rows, matrix, allocation contract and implementation identities
are separately bound evidence and do not replace the normative closure.
`scripts/r1_49j_normative_closure.py` declares the graph, enumerates the recursive
closure, refuses missing bindings and verifies every file's bytes. A changed
normative file requires a successor package and newly reviewed request digests.

## D.1 change log

- Replace the independent-only prohibition with DEC-062 family-coordinated
  allocation and the lead's clarification: 100 pair slots, multiple disjoint pairs
  per family allowed. Retain outcome independence, disjointness, Hall checks,
  separately receipted RNG streams, lexical endpoint pairing and explicit missingness.
- List and bind the full incorporated normative dependency closure, including the
  v5.1 statistical definitions and plan-9 specification sources.
- Preserve all other v5.2-D text and scientific settings. Its historical progress
  statements do not certify present gate closure; current candidate/receipt status
  is authoritative for operational readiness. The October 9 stop, 360+45 scope,
  accepted classifier and 63-interval family are unchanged.


Additional rules are incorporated from [new](new.md).
