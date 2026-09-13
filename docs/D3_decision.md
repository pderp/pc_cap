# D3 decision memo — frozen paired analysis and execution audit (S4-06)

Written 2026-09-13 ≈ 04:00 EDT by the orchestrator from `results/S4/partial/s4_06_{zsre,counterfact,grammar}_complete.json`,
`results/S4/partial/s4_06_grammar_supplement.json`, `results/S4/resource_views.json`, `results/S5/paired_{zsre,counterfact}.json`
and the run records under `results/S4/frozen-confirmatory-v2-84126123/` and `results/S5/…`. Policy: DEC-009 (ANA-01) as frozen
in `manifests/frozen.json` (`frozen-confirmatory-v2`, DEC-027). Nothing in this memo changes a threshold, endpoint, arm or budget.

## 1. Execution audit

| item | finding |
| --- | --- |
| Runs | S4 210/210 complete (zsRE 75, CounterFact 75, grammar 60); S5 60/60 complete (SE-A 30, SE-E 30; SB = the S4 C1 runs, charged once). No correctness failure, no resource stop, no rerun. |
| Accelerator time | S4 11.49 h of 27.0 after headroom (42%); S5 8.89 h of 18.0 (49%). Largest run 1,060 s against the 2,400 s allowance. |
| Identity | every run recorded the frozen BP parameter digest and tokenizer hash (or the grammar weights / ePC checkpoint hash) and the base hash unchanged before and after (V2-01, PC-8). |
| Freeze history | v1 (DEC-025) was superseded before any result by a loader defect (DEC-026: the grammar's `.npz` resource binding failed the realization-name rule; 50 jobs refused in < 1 s each, nothing edited); v2 (DEC-027) ran clean. The v1 attempt tree is archived. |
| Code | the source tree bound by v2 (`0f20e120067b…`) ran every job; post-execution changes are confined to `src/pccap/analysis/` (grammar expected inventory; S7 checkpoint runner) and recorded as analysis-tree version 2 (DEC-028). No run-affecting module changed. |
| Data | the sealed realizations were opened only by the sanctioned loader; the selection rule (SD-19) gave every order the same item subset; expected inventories matched the collected rows for zsRE and CounterFact (0 missing, 0 unexpected). |
| Grammar evaluation defect | SD-22: paraphrase seeds were salted per process, so 0–3 items per cell (of 2,048) have an undefined RET-GS and the paraphrase sequences differ between runs. No arm is favoured; the frozen policy classifies the grammar `incomplete`; a labelled complete-pair supplement is reported. |

## 2. Frozen classifications (primary endpoint RET-GS, margin 0.02; 97.5% paired-cluster bootstrap over realizations)

| dataset | C2 − C1 (Δ RET-GS, interval) | C2 − CR | ES non-inferior | LS non-inferior | classification |
| --- | --- | --- | --- | --- | --- |
| zsRE | −0.030 [−0.041, −0.019] | +0.000 [−0.013, +0.018] | yes / yes | no (−0.019) / yes | **negative** |
| CounterFact | 0.000 [0, 0] (exact-key floor) | 0.000 [0, 0] | yes | yes | **negative (uninformative: floor)** |
| grammar (frozen) | — | — | — | — | **incomplete** (SD-22) |
| grammar (supplement, complete pairs; not confirmatory) | −0.000 [−0.003, +0.002] | −0.000 [−0.004, +0.003] | yes | yes | negative |

**The primary claim (C2 improves retained generalization over C1 and CR by ≥ 0.02) is not supported on any dataset.** On zsRE
C2 retains paraphrase generalization about three points *worse* than C1 in every realization and is indistinguishable from
random routing. CounterFact and the grammar run with exact keys (SD-18, SD-20), where paraphrase retrieval never fires for
any cap arm, so the primary endpoint sits at a floor there (0.000 and 0.286 respectively) and cannot discriminate.

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

Readings. (i) On zsRE at 1,000 edits under the byte ceiling, retained ES falls with the number of banks that receive
writes: C0 (one bank, 300 edits) 0.99, C1 0.52, C2 0.30, CR 0.34 — the three-bank cap evicts more of what it learned.
(ii) On the grammar, the routing contrast is visible in RET-ES, not RET-GS: C2 and C0 retain every sequence, CR 0.90,
C1 0.69 — the same 1.00 / 0.91 / 0.70 pattern as the development matrix; RET-GS is identical across arms because the
grammar's paraphrase keys never fire (SD-20). (iii) B3 (LoRA + replay at the prescribed rate) acquires a fifth of the
edits, has no locality and drifts the language model (perplexity ratio 1.75 on zsRE, 6.5 on CounterFact): a measured
reference, not a gate (plan 4 §4). (iv) No cap arm drifts (ratio 1.000–1.001).

## 4. Comparable compute (resource views, update time per item)

C2's update time is the reference. C1 costs 2.7–2.8× C2 on the editing datasets and 2.0× on the grammar; CR and C0 cost
0.7×; B3 0.7× (zsRE) and 1.3× (CounterFact). No arm is within the 20% comparable-compute band of C2, so every contrast
carries the resource-matched view. The direction matters for the negative result: C2 uses *less* compute than C1 and
still retains less on zsRE, so a resource-matched comparison cannot rescue the primary claim.

## 5. Substrate comparison (S5; through the frozen paired machinery with arm relabelling)

| zsRE | Δ RET-GS | interval | Δ ES | Δ LS | reading |
| --- | ---: | --- | ---: | ---: | --- |
| SE-A − SB (ePC base, same adjoint credit) | −0.002 | [−0.004, −0.000] | +0.000 | −0.021 | no practical difference: the regenerated ePC base reproduces the BP result (matched fidelity, S1-01) |
| SE-E − SE-A (settled-error credit, same base) | +0.019 | [+0.012, +0.025] | −0.336 | +0.019 | real but sub-margin retention gain on the edits it holds; acquires a third fewer edits within the frozen round budget |

CounterFact: identically zero on every measure (floor). Both contrasts classify negative by policy.

## 6. Decisions and follow-ups

1. **T3 is not needed**: no required pair was dropped; the full frozen design ran within budget.
2. **The primary claim is not supported** (zsRE negative with the interval below zero; CounterFact and the grammar at the
   primary-endpoint floor). The report states this plainly, with the RET-ES routing evidence on the grammar and the
   eviction reading on zsRE as descriptive findings and the floors as design limitations (SD-18, SD-20).
3. **SD-22 options** are the lead's (`docs/lead_queue.md`): keep the grammar `incomplete` + supplement (applied), amend the
   policy with an explicit undefined-outcome exclusion (post-hoc), or rerun the 60 grammar runs (≈ 1 accelerator h) under a
   version-3 manifest with a deterministic paraphrase seed.
4. **S8-02 ablation list** (fixed before its runs; three realizations × two orders, exploratory): (a) cap-disabled stable keys
   versus edited keys on zsRE C2 (does the key drift explain the eviction losses?); (b) fixed-byte memory at half and double
   the reference for C1 and C2 on zsRE (is the C1 > C2 retention a capacity effect?); (c) the grammar with paraphrase keys
   at a positive radius calibrated at 5% false-fire (does the RET-GS floor lift?). Budget ≈ 3 accelerator h; S8 ceiling 16.
5. **S7** runs on the committed checkpoints now (zsRE C2 300-edit, CounterFact C2 endpoint, grammar C2 ≈ task 4 and task 8);
   S7-03's order variation is complete (RET-GS std across orders ≤ 0.023 for every cap arm on zsRE; 0 on CounterFact;
   ≤ 0.008 on the grammar).
