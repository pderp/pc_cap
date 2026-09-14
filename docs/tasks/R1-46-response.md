# Response to the stream-scale specification review (R1-46) — orchestrator, 2026-09-14 16:10 EDT (repairs in ae22d73)

| id | disposition | change / evidence |
| --- | --- | --- |
| R50-01 label boundary holds | noted | positive gate; kept. |
| R50-02 input admission incomplete | **repaired in part** | mixed allocation now floors at two items per domain and rebalances to the requested size; undersized pools still raise from the sampler; full admission (duplicates, empty paraphrase/locality lists) is on the pre-freeze checklist. |
| R50-03 "out of memory"/"locality" are fact hypotheses | acknowledged | the 512-episode check found zero exact prompt collisions; subject-level collisions are bounded by the pool's subject deduplication; stated in the notes. |
| R50-04 mixed allocation approximate | **repaired** | floor-and-rebalance allocation; every domain contributes at least one own-prompt/paraphrase/locality query triple per episode (test). |
| R50-05 binary balance vs role/domain balance | acknowledged | the class balance is null-vs-record only; per-role/domain weights are a declared future variant; the prefix objective is a sum (as in the loss table). |
| R50-06 bank cache identity | **repaired** | banks carry an identity (pool content hash, item count, base checksum, encoder version/taps, builder version, paraphrase/locality limits, logits dtype); reuse is refused on any mismatch; pre-identity banks are verified against the pool and stamped; the bank hash and construction cost go into every training summary; weight directories are never overwritten. float16 locality logits are recorded as a declared approximation. |
| R50-07 training vs deployment support | **measured** | occupancy 250 (2.5×): zsRE RET-GS 0.98 / LS 1.00 (unchanged); CounterFact 0.722 / LS 1.00 (from 0.795 at 100). Candidate recall and null activation by memory size remain a profiling item before the freeze; train-with-top-k / delta-in-objective variants would be separate declared estimators. |
| R50-08 M5 admission | **repaired / retired for the rule** | the helper binds weights + configuration into the run identity, holds the lease, records the grid, tie-break and the LS-step caveat; the single-rule result makes per-dataset selection unnecessary. |
| R50-09 fast training outside the ledger | **repaired** | FastTrainer charges one forward + one reverse per prefix (with tokens) to the ledger; bank construction cost is recorded once in the summary with the shared-cost policy; cold-compilation spans are still reported as wall time only. |
