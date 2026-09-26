# PC-v0 corrected-credit comparison — CPU SMOKE ONLY

Synthetic tiny-model smoke; no research result.

2/2 planned cells complete. Missing/partial cells remain explicit. Complete-pair differences only; no partial-prefix scores enter the paired estimate.

SE-E minus SE-A; old S5 scoring. Secondary bounded-text scores remain separate. Exposed S5 populations are supplemental defect-correction replication, not fresh confirmation.

Presentation context: this credit-rule comparison is a measured component toward the active-inference programme. It does not implement expected-free-energy policy selection. Heavy-tailed-distribution questions require the companion distributional harm measurements; editing accuracy alone cannot answer them. See docs/presentation/presentation_brief_2026-09-26.md.

| Dataset | r | order | status | ES | RET-ES | RET-GS | LS | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | complete | 0 | 0 | 0 | unavailable | 0 | 0 | 0 | unavailable |

## Realization summaries

Order differences are averaged within each realization. Only a complete three-realization design receives an overall mean/range. The range is descriptive, not a confidence interval; tokens and orders are not independent replicates.

| Dataset | metric | r0, r1, r2 | mean | min | max |
| --- | --- | --- | --- | --- | --- |
| zsre | ES | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | RET-ES | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | RET-GS | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | LS | [None, None, None] | unavailable | unavailable | unavailable |
| zsre | bounded_es_immediate | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | bounded_ret_es_end | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | bounded_ret_gs_end | [0.0, None, None] | unavailable | unavailable | unavailable |
| zsre | bounded_ls_end | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | ES | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | RET-ES | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | RET-GS | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | LS | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | bounded_es_immediate | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | bounded_ret_es_end | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | bounded_ret_gs_end | [None, None, None] | unavailable | unavailable | unavailable |
| counterfact | bounded_ls_end | [None, None, None] | unavailable | unavailable | unavailable |

## Historical reference and limitations

Defective-energy historical zsRE SE-E − SE-A: ES −0.336, RET-GS +0.019 (specification of record, docs/additional_work/PC-v0.md). It is not a corrected-energy control or fresh replication. CounterFact had a historical paraphrase floor of zero. No κ, coupled-free-energy, or general PC-superiority claim follows.

## Cost

Process seconds include startup/compilation; sums are not GPU elapsed hours. Counts are actual ledger totals. Eight-step error credit requires 9 forwards + 9 reverses per inference call; an adjoint call costs 1 forward + 1 reverse. Totals also include prediction, acceptance and diagnostics. Operation totals do not identify the number of credit calls.

| Dataset | r | order | arm | status | process seconds | forwards | reverses | settle iterations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 100 | SE-A | complete | 1.67205 | 26 | 3 | 0 |
| zsre | 0 | 100 | SE-E | complete | 2.31457 | 50 | 27 | 24 |

## Development 1/8/32 diagnostic

Unavailable: no development diagnostic group supplied.

Companion matched-position ordinary-text harm readout: unavailable until separately measured; this generator does not infer it from editing scores.

Identity checks verify recorded model/data/source hashes against local bytes and paired configs. The runner does not pre-sign metric/config files: this report binds their present bytes, not their historical authenticity.
