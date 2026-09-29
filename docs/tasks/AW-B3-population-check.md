# AW-B3 calibration population check

2026-09-28, Capex. No model execution or treatment outcomes guided this check.

The lane requests the zsRE 300-edit memory used by AW-L0/PC-4, but the approved
AW-B text names `r16_zsre_v5`. These are different populations. The saved memory's
checkpoint history begins `zsre-train-74347`, `zsre-train-127578`; the named r16
payload begins `zsre-eval-1058`, `zsre-eval-5432`, and their 300-item sets differ.
The r16 payload also contains zero near-miss and zero revision cases, preventing
the specified near-miss eligibility comparison.

The requested existing memory actually binds
`docs/tasks/R1-64g-post63l/R1-64g-zsre-R1_learned_ff.recipe.json`, SHA-256
`4b29cd82cd685e8f674abb5c5540c5273e96c1da7a9fae95b0eecfabe42db39d`, and the payload
`assets/runs/pc_cap/R1/stage4_dev_payloads/r1_64f_round28/zsre/payload.json`, SHA-256
`ef32d2abc1ab87eb62d6fa5491b1e84f2d3e30c3918c8e6998e7f18cae7ce79e`.

Proposed resolution: use this memory with its actual full-endpoint development
payload, retain CounterFact's `r16_counterfact_v5` memory/payload, and correct the
calibration-population sentence in AW-B.md before scoring. Both remain exposed
development data; the sealed evaluation populations remain untouched. Capstan
owns AW-B.md. Scientific approval is requested because this changes a named
population in the approved specification, not because of a file-edit restriction.

Separately, the specification leaves cross-dataset selection aggregation
unspecified. Capex has asked whether to rank by the smaller of the two datasets'
maximum-harm reductions, with the smaller ES99 reduction breaking ties. No
calibration selection will be made until that rule is settled.

## Resolution

charlie approved both proposals on 2026-09-28 before any calibration scoring:
use the saved memory's actual full-endpoint zsRE payload and use the smaller
reduction across datasets (including the ES99 tie-break). AW-B.md and the driver
now implement those choices. The CPU qualification command succeeds.
