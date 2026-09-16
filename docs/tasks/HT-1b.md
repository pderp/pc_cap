# HT-1b — selected v5 tail audit

Status: complete (CPU, saved development observations only). No existing file was edited.

The selected v5 reader has low average preservation loss but concentrated local harm. On the same 128 windows / 16,256 positions, compared with the historical v4 cell:

| Metric, positive part unless stated | v4 | v5 full = incremental |
| --- | ---: | ---: |
| Signed mean, nats | 0.000233148 | 0.002197557 |
| Mean positive harm, nats | 0.000234574 | 0.002198982 |
| Median | 0 | 0 |
| p95 | 0.0000079414 | 0.0000080176 |
| p99 | 0.0000130344 | 0.0000132803 |
| Expected shortfall, worst 5% | 0.004673627 | 0.043961670 |
| Maximum, nats | 3.789635 | 8.685941 |
| Maximum position | w125:p26 | w16:p31 |
| Counts >0.01 / >0.1 / >1 nat | 1 / 1 / 1 | 17 / 17 / 10 |
| Worst 1% share of positive harm | 99.44899% | 99.94072% |
| Signed zero atom | 4095/16256 | 4090/16256 |
| Positive zero atom | 10142/16256 | 10132/16256 |

The almost unchanged p99 misses the rare large errors: 17 positions are only 0.105% of the population. Report expected shortfall, exceedances and the worst location beside mean drift. This is observed concentration, not evidence identifying a power law. Both reference choices, original base and cap-off, coincide for these cells. Quantiles interpolate at (n−1)q; expected shortfall and worst-1% shares use fractional boundary mass, exactly as HT-1.

## Population and identity audit

The wrapper scripts/ht1b_v5_audit.py invokes the unchanged scripts/ht_audit_existing.py with a restricted inventory and exposes bare top-level endpoint arrays to its existing row parser. It changes no statistics, pair keys or files. Output: [audit.json](../../logs/heavy_tail/audit-v5-round16/audit.json), [v5_comparison.json](../../logs/heavy_tail/audit-v5-round16/v5_comparison.json), and paired.jsonl.gz alongside them. There are 24 source files, 89 series and 225 shared-observation comparisons. Nineteen missing-data records are explicit: ten aggregate-only summaries and nine empty endpoint row sets.

The v4 and both v5 drift vectors match exactly on ordered position identity, source SHA256 and both reference NLLs. The paired mean increase v5−v4 is about 0.001964410 nat. Their reader families/seeds differ, so this is not an isolated checkpoint-averaging effect. Full/incremental v5 drift rows, other final endpoint content and final state hashes match. Whole checkpoint documents differ in timing/cost and integrity bookkeeping: do not describe those entire files as byte-identical. These are not independent scientific replications. Other automatic pairs must retain their item-only/source-prompt pairing-strength qualification; common labels alone do not establish identical history or probes.

Unseen zsRE observations are 10/100, 12/100 and 9/100 at 100/300/1000 records. The outside probe IDs have zero pairwise overlap, and the 100-record population uses dev remainder while the larger runs use pool remainder. The last two memories contain 280 development items plus 20 or 720 fillers. Thus apparent occupancy flatness is unestablished; see [R1-X12 review](../../logs/review_r1_selection.md). CounterFact records 0/100 and 1/100 false fires at 100 and 1000 records; MQuAKE records 0/100 at 100 records on its legacy dev population, not selection v3b.

The complete-answer-preserved flag must not be called intervention damage: at 100 records CounterFact and MQuAKE have 33% and 44% missing complete-answer matches despite zero changed answers. That endpoint also reflects the unchanged base's answer correctness; the auditor keeps it separate from false-fire/answer-changed fields.

Standalone CounterFact near-miss and revision results are each 100/100 successful, with mean revised-answer paraphrase success 0.795. Repeated queries within a case are dependent. No universal preservation guarantee follows from these results. The detailed binary/fractional distributions are in audit.json and use error-fraction units, never nats.

The short v5 drift logs resolve to drift_assay_r1_50_stream_sel6_text_s2_{zsre,counterfact,mquake}.json. Their 32-window signed means are +0.005355496, +0.013661958 and +0.004015704 nats. They contain no per-position outcomes; tails and exact shared-row comparisons cannot be reconstructed. The wrapper binds the full JSONs and companion logs. A common window count or rounded mean does not make them the 128-window/300-edit cell population. Any CounterFact ceiling conclusion remains provisional pending the owner's full assay.

## Reproduction and follow-up

Run `python3 -B -m scripts.ht1b_v5_audit --output logs/heavy_tail/NEW_DIRECTORY` from pc_cap. Outputs refuse reuse. The source inventory hashes every admitted JSON before/after reading and before completion. No model is loaded and no GPU time is used.

Owner follow-up: bind the selected-reader full drift population and tail metrics into final reporting; obtain common outside IDs for the occupancy comparison; keep per-position data for future short assays. A signed mean ceiling is not a bound on maximum local harm. No policy or freeze gate is changed by this descriptive audit.
