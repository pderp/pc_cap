# R1-75_v5_development — Stage 4 cell analysis

development/draft observations do not fill confirmation slots

| Block | Planned | Terminal artifacts | Complete primary metrics | Execution complete |
| --- | ---: | ---: | ---: | --- |
| 1 | 2 | 2 | 2 | True |

| Dataset / condition / realization / order | Checkpoint | ES | RET-GS | LS bounded / terminated | Unseen fires | Near bounded / terminated | Revision latest | Drift mean / max / ES99 nats |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| zsre / R1_learned_ff / development / source | 100 | 1 | 0.99 | 50/50 / 50/50 | 9/100 | not run / not run | not run | not run/unavailable |
| zsre / R1_learned_ff / development / source | 300 | 1 | 0.986667 | 50/50 / 50/50 | 8/100 | 0/100 (unavailable full rate) / 0/100 (unavailable full rate) | 0/50 (unavailable full rate) | 0.00219756 / 8.68594 / 0.219768 |
| counterfact / R1_learned_ff / development / source | 100 | 1 | 0.765 | 49/50 / 36/50 | 0/100 | not run / not run | not run | not run/unavailable |
| counterfact / R1_learned_ff / development / source | 300 | 1 | 0.753333 | 49/50 / 36/50 | 0/100 | 100/100 / 63/100 | 50/50 | 0.00628615 / 7.31483 / 0.63848 |

## Explicit incomplete cells (DEC-051 order)

None. Endpoint availability and admission remain separate.

## Paired contrasts

| Dataset | Contrast | Checkpoint | ΔES | ΔRET-GS | ΔLS | Classification |
| --- | --- | ---: | ---: | ---: | ---: | --- |

- Complete blocks mean terminal execution artifacts, not universal endpoint availability or scientific admission.
- Missing pairs are not imputed; available-pair means remain diagnostics.
- Three fresh realization clusters keep all five orders together; no iid-order claim.
- Snapshot payloads and training inputs are not opened; reports and receipts establish analysis provenance.
- U12 multiplicity and final secondary thresholds remain pending; no confirmatory verdict is emitted.
