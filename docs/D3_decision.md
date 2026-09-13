# D3 decision memo — frozen paired analysis and execution audit (S4-06)

This report preserves the v2 results reviewed at snapshot `170fad3`. During P2/X2, DEC-029/030 authorized and froze the grammar-only v3 rerun (`frozen-confirmatory-v3-163d04e2`); zsRE, CounterFact and S5 retain their v2 identities. V3 outcomes are not included here. See `logs/p2_x2_v3_transition/review.md` for the transition checks and the residual seven-item paraphrase coverage finding.

Written 2026-09-13 ≈ 04:00 EDT by the orchestrator from `results/S4/partial/s4_06_{zsre,counterfact,grammar}_complete.json`,
`results/S4/partial/s4_06_grammar_supplement.json`, `results/S4/resource_views.json`, `results/S5/paired_{zsre,counterfact}.json`
and the run records under `results/S4/frozen-confirmatory-v2-84126123/` and `results/S5/…`. Policy: DEC-009 (ANA-01) as frozen
in `manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json` (`frozen-confirmatory-v2`, DEC-027). Nothing in this memo changes a threshold, endpoint, arm or budget.

## 1. Execution audit

| item | finding |
| --- | --- |
| Runs | S4 210/210 complete (zsRE 75, CounterFact 75, grammar 60); S5 60/60 complete (SE-A 30, SE-E 30; SB = the S4 C1 runs, charged once). No correctness failure, no resource stop, no rerun. |
| Accelerator time | S4 11.49 h of 27.0 after headroom (42.6%); S5 8.89 h of 18.0 (49.4%). Largest run 1,067.24 s against the 2,400 s allowance. |
| Identity | every run recorded the frozen BP parameter digest and tokenizer hash (or the grammar weights / ePC checkpoint hash) and the base hash unchanged before and after (V2-01, PC-8). |
| Freeze history | v1 (DEC-025) was superseded before any result by a loader defect (DEC-026: the grammar's `.npz` resource binding failed the realization-name rule; 50 jobs refused in < 1 s each, nothing edited); v2 (DEC-027) ran clean. The v1 attempt tree is archived. |
| Code | the source tree bound by v2 (`0f20e120067b…`) ran every job; the initially recorded post-execution changes were in `src/pccap/analysis/` (grammar expected inventory; S7 checkpoint runner) and recorded as analysis-tree version 2 (DEC-028). After execution, commit `b530baf` also added default-preserving ablation parameters to `cap/{cap,memory,calibrate}.py`. At snapshot 170fad3 those changes were not covered by the analysis-v2 full-source record (tree `9b1d9984c3d4…`). DEC-029/030 subsequently bound the v3 execution tree `67787f49ec16…`. All 270 saved run configurations still match the frozen execution tree. |
| Data | the sealed realizations were opened only by the sanctioned loader; the selection rule (SD-19) gave every order the same item subset; expected inventories matched the collected rows for zsRE and CounterFact (0 missing, 0 unexpected). |
| Grammar evaluation defect | SD-22: paraphrase seeds were salted per process; 0–5 items per run (of 2,048) have undefined RET-GS, and paraphrases differ between runs. The salt has no deliberate arm dependence, but realized bias is not ruled out. The frozen classification stays `incomplete`. The labelled supplement excludes the union across 20 arm/order cells: 28/22/41 items, retaining 2,020/2,026/2,007 in realizations 0/1/2; it is not confirmatory. |

## 2. Frozen classifications (primary endpoint RET-GS, margin 0.02; 97.5% paired-cluster bootstrap over realizations)

| dataset | C2 − C1 (Δ RET-GS, interval) | C2 − CR | ES non-inferior | LS non-inferior | classification |
| --- | --- | --- | --- | --- | --- |
| zsRE | −0.030 [−0.041, −0.019] | +0.000 [−0.013, +0.018] | yes / yes | no (−0.019) / not established (−0.007) | **negative** |
| CounterFact | 0.000 [0, 0] (exact-key floor) | 0.000 [0, 0] | yes | yes | **negative (uninformative: floor)** |
| grammar (v3 rerun; the v2 row below is archived) | 0.000 [0, 0] (floor) | 0.000 [0, 0] (floor) | yes (C2 acquires +0.301 over C1, +0.100 over CR) | yes | **negative (complete: 2044/2047/2046 of 2,048 items per realization; 4/1/2 paraphrase-less items excluded by the disclosed inventory rule)** |
| grammar (supplement, complete pairs; not confirmatory) | −0.000 [−0.003, +0.002] | −0.000 [−0.004, +0.003] | yes | yes | negative |

**The primary claim (C2 improves retained generalization over C1 and CR by ≥ 0.02) is not supported on any dataset.** On zsRE
C2's mean RET-GS is about three percentage points lower than C1; the order-averaged difference is negative in all three realizations. The C2−CR interval includes zero; this does not establish equivalence. Locality non-inferiority is not established against CR: Δ LS −0.007 [−0.026, +0.013], lower bound below −0.01. CounterFact and the grammar run with exact keys (SD-18, SD-20), where paraphrase retrieval never fires for
any cap arm, so the observed cap-arm primary endpoint is 0.000 on CounterFact and approximately 0.286 on the grammar. This is a retrieval-generalization limitation, not evidence that every possible cap or key variant must fail. Grammar arm means are not exactly identical under SD-22.

## 3. What the runs show beyond the primary endpoint (descriptive; means over the 15 runs per cell)

| dataset | arm | ES | RET-ES | RET-GS | LS | drift ratio | accel s / run |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| zsRE (1000 edits) | C0 (300) | 1.000 | 0.992 | 0.356 | 0.981 | 1.000 | 123 |
| | C1 | 0.998 | 0.524 | 0.139 | 0.985 | 1.001 | 503 |
| | C2 | 0.998 | 0.302 | 0.109 | 0.965 | 1.001 | 316 |
| | CR | 0.999 | 0.344 | 0.109 | 0.972 | 1.000 | 277 |
| | B3 | 0.209 | 0.171 | 0.120 | 0.009 | 1.750 | 208 |
| CounterFact (300) | C0, C1, C2, CR | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 | 215–259 |
| | B3 | 0.224 | 0.217 | 0.098 | 0.000 | 6.468 | 116 |
| grammar (2048 seq.) | C0 | 1.000 | 1.000 | 0.286 | 1.000 | 1.000 | 40 |
| | C1 | 0.698 | 0.690 | 0.286 | 1.000 | 1.000 | 134 |
| | C2 | 1.000 | 1.000 | 0.286 | 1.000 | 1.000 | 74 |
| | CR | 0.900 | 0.895 | 0.286 | 1.000 | 1.000 | 58 |

Readings (descriptive). (i) zsRE RET-ES is 0.524 for C1, 0.302 for C2 and 0.344 for CR at 1,000 edits. C0's 0.992 is at only 300 edits and is not a matched endpoint comparison. These means do not identify the cause of forgetting. The accepted-event logs contain fewer eviction events for C2 (mean 1,085) than C1 (2,801); event counts are not counts of uniquely forgotten edits. (ii) On the grammar, C2 and C0 have RET-ES 1.000, CR 0.895 and C1 0.690, consistent with the development pattern. Their RET-GS means all round to 0.286, with different sampled paraphrases and missing outcomes (SD-22). (iii) B3 acquires about a fifth of the editing targets and has poor locality (zsRE LS 0.009; CounterFact 0.00033), with drift ratios 1.75 and 6.47 on the tested slice. (iv) Editing drift evaluates only 4,064 positions, not the entire 247,289-token validation split required by SD-3. zsRE cap-arm mean ratios are near one, but C2 reaches 1.00929 in an individual run; a rounded mean is not proof of no drift. Grammar drift is a separate 4,032-position base-grammar assay. See `logs/review_report_draft1.md` and the prior drift remediation note.

## 4. Comparable compute (resource views, update time per item)

C2's update time is the reference. Across the 15 cells per dataset, mean C1/C2 ratios are 2.788 (zsRE), 2.720 (CounterFact) and 1.988 (grammar). C0/C2 is 0.698/0.737/0.513; CR/C2 is 0.682/0.726/0.693. B3/C2 is 0.697 on zsRE and 1.296 on CounterFact. No *comparator* lies within 20% of C2 in any cell; C2 itself is the reference at 1.0. Thus no joint comparable-compute superiority claim is established.

The resource views provide exposure-matched checkpoint outcomes and ES-versus-time tables; they do not establish a paired RET-GS superiority result at equal cost. Losing at equal exposure while using less compute does not logically rule out a different tradeoff at equal time. Report the measured tradeoff without claiming that resource matching cannot change it.

## 5. Substrate comparison (S5; through the frozen paired machinery with arm relabelling)

| zsRE | Δ RET-GS | interval | Δ ES | Δ LS | reading |
| --- | ---: | --- | ---: | ---: | --- |
| SE-A − SB (ePC base, same adjoint credit) | −0.002 | [−0.004, −0.000] | +0.000 | −0.021 | RET-GS differs by −0.002; locality non-inferiority is not established (Δ LS −0.0213 [−0.041, +0.004]); not an equivalence result |
| SE-E − SE-A (settled-error credit, same base) | +0.019 | [+0.012, +0.025] | −0.336 | +0.019 | RET-GS point gain is below 0.02, but its interval extends above it; ES falls 0.336, making the contrast negative. RET-GS is not conditional on acquired edits |

CounterFact: both paired differences are zero for RET-GS, ES and LS; absolute ES and LS are 1.0 while RET-GS is 0.0. Both substrate contrasts classify negative by policy.

## 6. Decisions and follow-ups

1. **T3 is not needed**: no required pair was dropped; the full frozen design ran within budget.
2. **The primary claim is not supported** (zsRE negative with the interval below zero; CounterFact and the grammar at the
   primary-endpoint floor). The report states this plainly, with the RET-ES routing evidence on the grammar and the
   retention difference on zsRE as descriptive findings without a proven eviction mechanism and the floors as design limitations (SD-18, SD-20).
3. **SD-22 option (c) chosen:** DEC-029/030 authorizes and freezes the grammar-only v3 rerun. The v2 classification remains incomplete and its supplement stays labelled. P2's full generator audit of v3 still finds 4/1/2 zero-paraphrase items per realization; deterministic seeding alone does not ensure a complete RET-GS inventory. Coverage/policy handling remains an explicit lead/run-owner decision.
4. **S8-02 ablation list** (fixed before its runs, after the confirmatory results; three seeds × two orders, exploratory): (a) cap-disabled stable keys
   versus edited keys on zsRE C2 (does the key drift explain the eviction losses?); (b) fixed-byte memory at half and double
   the reference for C1 and C2 on zsRE (is the C1 > C2 retention a capacity effect?); (c) the grammar with paraphrase keys
   at a positive radius calibrated at 5% false-fire (does the RET-GS floor lift?). Planned budget ≈ 3 accelerator h; S8 ceiling 16. Completed (b)/(c) contain 72 runs with 0.8255 recorded accelerator h; (a) was not run. The grammar 5% test was not in the S4-frozen exploratory list, and difficulty weighting was omitted. The byte-ceiling runs contain 280, not 300, available development edits; the grammar test found no positive candidate on its tested calibration grid. See report §8.
5. **S7** completed on four committed checkpoints (zsRE C2 300-edit, CounterFact C2 endpoint, grammar C2 ≈ task 4 and task 8);
   S7-03's order variation is complete (RET-GS std across orders ≤ 0.028 (observed maximum 0.0277543) for every cap arm on zsRE; 0 on CounterFact;
   ≤ 0.008 on the grammar).

## 7. Addendum (2026-09-13, after X2): full-validation drift supplement

SD-3's full-split drift assay was run as a labelled supplement on the zsRE realization-0, order-0 endpoint states (`results/S4/drift_supplement.md`; 245,110 positions): perplexity ratios C0 1.0010, C1 1.0019, C2 1.0036, CR 1.0030, B3 1.884. The recorded 4,064-position assay understated C2/CR (1.000 vs 1.004) but the cap arms stay within 0.4% of the base on the whole split; the classification tables are unchanged.

## 8. Addendum (2026-09-13, 18:10 EDT): the version-3 grammar row

SD-22 option (c) (DEC-029): the paraphrase seed became a content hash of the item id and the 60 grammar runs were rerun under
`frozen-confirmatory-v3` (DEC-030; 60/60 complete, no failure; one job refused once on code drift caused by an analysis edit
during the queue and was rerun). With the deterministic search, 4 / 1 / 2 items per realization have no paraphrase at all;
DEC-031/032 define the expected RET-GS inventory as the items with at least one paraphrase (2044 / 2047 / 2046 of
2,048), excluded ids reported in `results/S4/partial/s4_06_grammar_v3.json`. Result: **complete, negative** — C2 − C1 and
C2 − CR RET-GS differences exactly 0.000 in every realization (with exact keys no paraphrase retrieves, so every arm returns
the base's paraphrase answers), ES +0.301 / +0.100 for C2, LS identical. Order variation of RET-GS is now identical
across arms (0.0066 over the 15 runs, 0 within each realization) — v2's arm-to-arm differences were the SD-22 noise. The S7
grammar reversals were rerun under v3 (`results/S7/frozen-confirmatory-v3-163d04e2/`): zero damage and zero divergence in every
stratum, as under v2.
