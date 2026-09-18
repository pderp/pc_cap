# Revision v1 execution plan v3 — explicit full-validation costing

Prepared 2026-09-18 by Codex for lead review. This replaces v2's **cost scenario**, not its experimental scope or admission authority. DEC-065 reviews full-validation transfers; the lead separately approved maximum same-dataset endpoint transfers for 14 rows on September 18. The typed v4 receipt and ceilings v2 remain unsigned. October 9 is the experimental stop; October 15 is the presentation.

DEC-066 reduces MQuAKE prospectively: **285 core cells and 45 optional extension cells** remain declared. Keep all 27 historical cost rows, but omit the five removed MQuAKE arms from planned execution totals. Two workers share a **750 process-hour** cap. Sum both processes' actual elapsed time, including overlapping execution, startup, validation, failures and retries. Retry a cell once from its last certified checkpoint; after a second cell failure mark it incomplete and continue. Host/OOM failures stop the queue. The MemAvailable launch floor remains 6,144 MiB. The scheduler applies the 1.15 concurrency factor once to the 1.5 solo ceiling.

## Cost components and provenance

For each of 27 condition/dataset rows, remove the historical single sampled phase and supplied near-miss/revision phase from the v1 solo estimate. Retain the remaining nonvalidation estimate, add sampled drift at every registered checkpoint (three for zsRE/CounterFact, two for MQuAKE), and add near-miss/revision and full validation **once each at the final checkpoint**, matching the installed backend, and itemize the historical 30-second startup/admission estimate. For a row with a measured chain-S whole-process duration, take the larger of that duration and the component sum; this prevents the same 300-edit MQuAKE job being priced below its actual measured wall time. For 1,000-edit cells, the 300-edit measurement is only a lower bound. This decomposition of the coarse v1 estimates is an explicit planning assumption; it is not a fresh measurement of every component.

Full costs use the four measured chain-S donor phases. CounterFact uses its own sampled seconds/position × 245,237 (DEC-065(i)). S1 uses 1.5 × the v0 full phase for the whole three-forward assay (DEC-065(ii)), without also applying its S1 sampled-rate ratio; CounterFact's v0 full phase is itself a rate transfer. Remaining zsRE/MQuAKE family transfers use the reviewed round-35 sampled-rate scenario. Full-phase occupancy independence from 300 to 1,000 is an assumption (DEC-065(iii)). The historical primary CounterFact sample used an older execution/integrity profile: its relatively expensive rate is retained conservatively and explicitly, not described as a measurement of the current batched kernel.

The 14 incomplete zsRE/MQuAKE endpoint rows use the maximum complete same-dataset measurement: **268.078315085 s** at the final checkpoint for zsRE, **315.418926737 s** at the final checkpoint for MQuAKE. These are the approved maxima in the after-chain-R inventory. The four measured chain-S rows additionally use the larger of their own historical and chain-S endpoint observations (new v0 totals: 269.181 s zsRE, 335.695 s MQuAKE); the 14 approved transfers remain the explicitly reviewed historical estimates. Measured endpoint inventories remain unchanged. Host ceilings use the larger same-condition/dataset observation where chain S adds a direct GNU-time peak; other rows retain direct or uniquely time-matched monitor evidence. Monitor RSS is sampled and may miss the true peak; exact argv attribution is unavailable in those historical traces. Memory at 1,000 records and S1's full three-forward assay has not been measured. Factors are safeguards, not proof of a bound.

## Projections

| Scenario | Core process h | Optional extension process h | Combined process h |
|---|---:|---:|---:|
| Historical v2, original D.3 scope, no full validation (1.15 concurrency) | 240.810 | 13.973 | 254.783 |
| Round-35 full-validation sensitivity, original D.3 scope | 443.259 | 40.442 | 483.701 |
| Recomputed full costs, original D.3 scope | 465.886 | 42.035 | 507.921 |
| Original D.3 scope at all per-cell ceilings | 698.829 | 63.052 | 761.881 |
| Historical per-row no-full costs, reduced D.4 scope | 212.348 | 13.973 | 226.320 |
| v4 D.4 without full phase, with endpoint/sample/startup corrections | 243.392 | 19.342 | 262.734 |
| **v4 D.4 full-validation expected scenario** | **389.272** | **42.035** | **431.307** |
| **v4 D.4 at every 1.5 solo ceiling, including 1.15 concurrency** | **583.908** | **63.052** | **646.960** |

DEC-066 removes **76.614 expected process-hours** from the fully reconciled D.3 scenario. The new combined expected scenario leaves **318.693 process-hours** below 750; its sum of per-cell ceilings leaves **103.040 hours**. Retry/failure time consumes that same cap and is not included as an invented fixed retry count. This is useful headroom, not a completion guarantee. The D.3 sum of ceilings would exceed the cap by 11.881 hours. The older ≈484/726-hour sensitivity used different full-transfer formulas and omitted endpoint/startup reconciliation; retain it as a historical comparison rather than the new forecast.

At the previously admitted 1.65× throughput assumption, expected elapsed time is **205.150 hours core**, **227.303 including extension**, against the older ≈360–375 usable-hour estimate from a September 19–20 launch. These are conditional scenarios, not calendar guarantees; late launch, availability loss and failed attempts reduce the buffer. Benchmark failures do not invalidate cost donors or veto cap comparisons under DEC-064. Continued-base fidelity admission remains separate.

The first working draft of this round incorrectly priced near-miss/revision at every checkpoint. Code review of `r1_77b_sealed_backend.py` and chain-S phase counts corrected it before final review: those challenges are final-only, while sampled drift repeats. Earlier interim figures in this conversation and the superseded preview are not the final cost forecast.

## Block boundaries and decisions

At block 1, use `scripts/r1_d11_block_report.py` with the exact frozen matrix, queue receipts and HT-8 watch. Compare actual process costs, memory and completed populations against these transfers. Record observed costs without outcome-based exclusion, including failed attempts and live/unknown cost qualifications. Replace available transfers with measured confirmatory costs in a **versioned** admission at a stopped queue boundary; never overwrite frozen bindings or revise an active queue's ceiling file. Carry unmeasured conditions forward as labelled transfers until their blocks finish.

Repeat reconciliation at every block and before optional extension admission. Keep the October 9 stop, DEC-051 block order, DEC-052 incomplete-cell inventory, independent endpoint populations and all 63 primary intervals. Before launch, the lead must review this changed budget scenario, sign the exact typed cost and protocol requests, and provide the remaining gate/admission signatures. Authorized draw, endpoint construction, sealing and publication then run in order and retain their own fail-closed checks. No synthetic rehearsal closes a real scientific gate.
