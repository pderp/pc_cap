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
Further declared payloads require an updated exposure supplement before draw.

These are **preteacher** counts. MQuAKE has 2214 eligible items but 2161 distinct subjects;
the 211-subject margin can shrink under final teacher/token filtering and joint-role allocation.
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
The R1-77d source/backend patches remain unapplied until the orchestrator's idle boundary after
chains M/N/O. Rebuild execution recipes, code identities and freeze candidate v8 after application.
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

1. Complete the teacher run on all 14419 operative-v5 items, or certify a completed receipt run
   covering every one of them without re-decoding. An older v4-only run lacks 88 restored items
   and cannot certify the new inventory by itself. Certification preserves historical producer hashes.
2. Merge certified teacher evidence with the regenerated role plan, then review joint allocation
   at demands 4050/4050/1950. Teacher completion alone does not admit the population.
3. Explicitly admit the proposed zsRE same-template/different-subject near family and endpoint
   missingness. Its semantics differ from historical same-subject development challenges.
4. Admit protocol/RNG, current exposure and stage-specific requests; perform the actual draw,
   endpoint construction and seal with the v3 operator inputs.
5. Apply the prepared cadence patches at an idle boundary, validate and rebuild identities;
   admit measured costs, the September 20 schedule and all U01–U18 gates before final freeze/launch.

See [operator sheet v3](tasks/R1-D9-operator-sheet-v3.md) for the ordered commands and handoff.
