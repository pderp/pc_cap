# R1-49g — DEC-057/058/059 analysis

Scope: development. GPU/model calls: zero.

The 63 intervals use nominal Bonferroni allocation of 0.05 and three realization clusters; exact familywise coverage is not claimed.

| Dataset | Contrast | Classification | RET-GS realization estimates | Adjusted RET-GS interval |
|---|---|---|---|---|

Both adjusted and unadjusted intervals and all three realization estimates for every metric are in JSON.

| Cell | Benchmark | Value | Pass | Availability |
|---|---|---:|---|---|
| b4110a42abb8724d1b32d9a6 | revision_latest | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | old_alias_reappearance | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | revision_semantic | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | unseen_1000 | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | outside_change_1000_100 | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | retention_change | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | es_change | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | ls_change | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | state_budget_ratio | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | peak_budget_ratio | None | None | unavailable |
| b4110a42abb8724d1b32d9a6 | wall_budget_ratio | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | revision_latest | 1.0 | True | complete |
| 26dab92e5e0a766dd9226ce8 | old_alias_reappearance | 0.04 | False | complete |
| 26dab92e5e0a766dd9226ce8 | revision_semantic | 1.0 | True | complete |
| 26dab92e5e0a766dd9226ce8 | unseen_1000 | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | outside_change_1000_100 | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | retention_change | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | es_change | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | ls_change | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | state_budget_ratio | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | peak_budget_ratio | None | None | unavailable |
| 26dab92e5e0a766dd9226ce8 | wall_budget_ratio | None | None | unavailable |

| Dataset | Condition | Macro benchmark | Value | Pass | Failed cells |
|---|---|---|---:|---|---|
| zsre | R1_learned_ff | unseen_1000 | None | None | none observed |
| zsre | R1_learned_ff | outside_change_1000_100 | None | None | none observed |
| zsre | R1_learned_ff | revision_latest | None | None | none observed |
| zsre | R1_learned_ff | old_alias_reappearance | None | None | none observed |
| zsre | R1_learned_ff | revision_semantic | None | None | none observed |
| zsre | R1_learned_ff | retention_change | None | None | none observed |
| zsre | R1_learned_ff | es_change | None | None | none observed |
| zsre | R1_learned_ff | ls_change | None | None | none observed |
| zsre | R1_learned_ff | state_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff | peak_budget_ratio | None | None | none observed |
| zsre | R1_learned_ff | wall_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | unseen_1000 | None | None | none observed |
| counterfact | R1_learned_ff | outside_change_1000_100 | None | None | none observed |
| counterfact | R1_learned_ff | revision_latest | None | None | none observed |
| counterfact | R1_learned_ff | old_alias_reappearance | None | None | none observed |
| counterfact | R1_learned_ff | revision_semantic | None | None | none observed |
| counterfact | R1_learned_ff | retention_change | None | None | none observed |
| counterfact | R1_learned_ff | es_change | None | None | none observed |
| counterfact | R1_learned_ff | ls_change | None | None | none observed |
| counterfact | R1_learned_ff | state_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | peak_budget_ratio | None | None | none observed |
| counterfact | R1_learned_ff | wall_budget_ratio | None | None | none observed |

Resource ceilings remain unadmitted. Macro unavailability and missing cell results cannot be read as passes.

Complete blocks mean terminal execution artifacts, not universal endpoint availability or scientific admission.
Missing pairs are not imputed; available-pair means remain diagnostics.
Three fresh realization clusters keep all five orders together; no iid-order claim.
Snapshot payloads and training inputs are not opened; reports and receipts establish analysis provenance.
nominal approximate bootstrap; three clusters do not establish exact familywise coverage
Accepted thresholds do not confer population, execution or final scientific admission.
Semantic revision is latest-answer success AND old-retired AND new-active; old acquisition is not an additional filter.
Per-cell occupancy equivalence has no independent realization-cluster interval; only complete three-realization macros can report that interval.
