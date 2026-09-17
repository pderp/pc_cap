# Stage 4 protocol v5.2-D — adopted population, pending final admission

Round 24, 2026-09-17. Experimental completion remains **October 9**, before the October 15 presentation.
This draft implements DEC-060 option D and the adopted R1-D10e context rule. It grants no draw,
seal, freeze or execution authority. The unchanged scientific definitions, conditions, scoring,
restoration requirements and DEC-057/058/059 rules are incorporated from
[v5.1](R1_stage4_protocol_draft_v5_1.md); the replacements below govern population and cadence.
The earlier [option-D candidate](R1_stage4_protocol_draft_v5_2_option_D.md) is preserved as history.

## Population and exposure

| Dataset | Realizations | Edits each | Checkpoints | Required distinct subjects | Operative v5 preteacher subjects | Margin |
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
The current bindings are in `tasks/R1-D9-inputs-v3-post77d.json`. Further payloads or undeclared
exposure require review, and the lead must attest exposure through draw time.

The table was prepared before teacher review; the completed review and joint-role checks retain
these counts. MQuAKE has 2214 eligible items but 2161 distinct subjects, a 211-subject margin.
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
candidate v8 bind the new identity. Final confirmatory recipes still require actual admitted
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

## Remaining gates

1. Review the completed teacher certification, merged role evidence and clearance dry-run at
   demands 4050/4050/1950; sign the exact current clearance request. Historical producer bytes
   and the 88 items absent from the older v4 review remain accounted for.
2. Confirm the current exposure snapshot and attest no additional exposure through draw time.
   Teacher/role completion alone does not authorize the population draw.
3. Explicitly admit NM-template-v1 across all three datasets (different subjects, exact relation
   or subject-masked question template; not semantic nearest neighbours) and endpoint
   missingness. Its semantics differ from historical same-subject development challenges.
4. Admit protocol/RNG, current exposure and stage-specific requests; perform the actual draw,
   endpoint construction and seal with the v3 operator inputs.
5. Apply the prepared cadence patches at an idle boundary, validate and rebuild identities;
   admit measured costs, the September 20 schedule and all U01–U18 gates before final freeze/launch.

See [operator sheet v3](tasks/R1-D9-operator-sheet-v3.md) for the ordered commands and handoff.
