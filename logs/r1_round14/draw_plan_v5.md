# Register-v5 draw plan: diagnostic only

All three nominal capacities meet 4,050 subjects, but no dataset has final joint clearance. No draw or seal occurred.

| Dataset | Candidate items | Candidate subjects | Headroom | Subject losses causing shortfall |
| --- | ---: | ---: | ---: | ---: |
| counterfact | 12246 | 12246 | 8196 | 8197 |
| mquake | 4489 | 4218 | 168 | 169 |
| zsre | 52411 | 52411 | 48361 | 48362 |

Demand includes separate near-miss supports and neighbours: 3 × (1,000 + 100 + 100 + 100 + 50) = 4,050 per dataset. The shorthand in ongoing.md omits one reserve.

Counts by answer-token stratum and all 45 dataset/realization/role quota rows are in draw_plan_v5.json. MQuAKE’s multiple item rows are reduced to one representative per canonical subject in bound-register order for this count-only diagnostic; that convention is not a final draw approval. No IDs or RNG draws were emitted.

Remaining clearance: alias/entity and cross-dataset aliases; context/cumulative exposure through draw time; final teacher and tokenizer/context eligibility; compatible disjoint near-miss/revision roles; composition dependency closure. Each step has only the trivial upper bound of all candidate subjects (not additive across steps). Existing MQuAKE teacher receipts do not certify joint final clearance. A loss of 169 MQuAKE subjects would make the required scope infeasible.

Binding refusal:

- /home/derp/cap/pc_cap/docs/decisions.md
  Expected e0e90771bc4cd6bcd02c827acefa05688aad1fb1eedb182aea1815781539257a; observed f596d3960c6bfce721064091f73333dde7674fcbae71308b11d80c9f2a9f2d58.

The decision file was legitimately updated during concurrent work, but v5’s byte binding is stale. The owner must issue an explicitly rebound/versioned register with unchanged candidate/policy provenance verified; this report does not silently waive that mismatch. Both current abort reasons remain: stale binding and absent final clearance.
