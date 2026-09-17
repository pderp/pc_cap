# Stage 4 matrix schema 7 + DEC061_R177f — adopted DEC-061 and queue ceilings

`run_matrix_v5_2_D_DEC061.json` adds the `policy_revision: DEC061_R177f` contracts to schema 7 without changing its 360 core / 45 optional
coordinates, pairing, orders, layout, cadence or 63 primary interval definitions. It is a
`confirmation_draft`, with null costs/populations and false draw/launch/freeze flags. It cannot run.
The final signed matrix must preserve these definitions while binding admitted resources.

New required contracts for this version:

| Field | Meaning |
|---|---|
| `near_miss_family_contract` | Exact `r1_d9e_near_family.CONTRACT`: DEC-061 NM-template-v1, fixed slots, source-derived pairing, DEC-053 neighbour versus baseline equality. |
| `queue_ceiling_contract.version` | 1. |
| `queue_ceiling_contract.wall_seconds` | `admitted_solo_ceiling`. |
| `queue_ceiling_contract.solo_safety_factor` | 1.5, applied by the cost admission when writing the cell ceiling. |
| `queue_ceiling_contract.workers_1_factor` | 1.0 applied at launch/status. |
| `queue_ceiling_contract.workers_2_factor` | 1.15 applied at launch/status. |
| `queue_ceiling_contract.charged_budget` | `sum_of_process_envelopes_including_overlap_and_failures`. |
| `queue_ceiling_contract.maximum_cell_failures` | 2 total failures (one retry), persisted in queue receipts. |
| `queue_policy` | Path/SHA of concurrency policy v2. |
| `protocol` | Path/SHA of final v5.2-D text for signature. |
| `analysis_implementation` | Current producer bindings including the adopted family module. |

A cell's `ceilings.wall_seconds` remains null until admitted; a runnable cell requires a
positive finite solo ceiling identical in matrix and recipe. Queue version-2 population
validation requires the exact ceiling contract, and any contradictory supplied contract refuses.
Scope, matrix hashes, final protocol/population bindings and freeze checks remain required.
This schema declaration is not an admission of numeric ceilings or a JSON Schema validator.
