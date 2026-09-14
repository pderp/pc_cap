# R1-X4 — Counter-review of Stage 2 and the non-learned condition

Codex, 2026-09-14. Read-only development audit; no real-base queries, training, GPU work, or edits to the notes/results. Snapshot begins at repository HEAD `777373b`; file identities, rather than an assumed frozen working tree, govern this report. Concurrent unfinished jobs are outside the completed-result inventory.

The saved numbers support a useful provisional reference: the random tied reader with per-position delta adaptation achieves **ES 1.00, RET-ES 1.00, RET-GS 0.65, LS 1.00 on one 100-edit zsRE development stream**. CounterFact under the same named condition achieves **1.00, 1.00, 0.18, 0.16**, respectively. This is evidence of a working development configuration on zsRE, with a serious transfer/locality limitation. It establishes neither a benefit from learning the cap nor a benefit from cap-level predictive coding.

## Audit scope and evidence

The authoritative machine-readable recount is [stage2_recount_v2.json](r1_round5/stage2_recount_v2.json). It binds all inspected files by SHA-256 and includes:

- 30 stream summaries; all 22 extant detailed `items.jsonl` files, with their actual dataset identities, were recounted.
- 16 pilot summaries: 12 completed training jobs and four zero-step checkpoint reevaluations.
- Every one of the 34 numeric table rows in [Stage 2 notes](../docs/R1_stage2_notes.md): 184 checked entries agree with saved summaries at the printed precision; two cells are explicitly n/a. No unmapped notes rows.
- Every row of [stream_eval.md](../results/R1/stream_eval.md): 30 rows, 240 numeric cells plus 30 step-configuration cells agree. The supplemental verified table audit is [here](r1_round5/repair_preview_v2/stage2_stream_table_audit_verified.json). Its one-line tag-matching repair was tested in memory; applying that repair awaits permission.
- All five audited additive ledger fields reconcile across learning/query/total with zero residual: full forwards, partial forwards, reverses, tokens and accelerator seconds. Algebraic consistency does not establish completeness of instrumentation.

For 22 dataset-matching summaries, the reconstructed ES/RET-ES/RET-GS and saved endpoint locality aggregate agree with the summary. Per-locality prompt generations were not retained in these artifacts; their LS aggregates can be cross-checked, but all 50 individual reference/answer pairs cannot be independently rescored. RET-GS averages paraphrases within each item and then across items. CounterFact generally has two paraphrases per item; 100 items must not be treated as 200 independent observations.

The JSON exporter records four `inf` values from the zero-step pilots' unused `best_dev.answer` fields as null with an explicit source-path annotation. They indicate no best training checkpoint was measured, not observed nonfinite model predictions. The earlier `stage2_recount.json` is an incomplete failed serialization attempt and must not be consumed. Use only the v2 recount. Original failed validation logs remain untouched under the new-files-only protocol.

## Findings

### X4-01 — Eight detailed-result attribution collisions remain in historical artifacts (high)

The saved zsRE summaries for the following identities point to directories now containing CounterFact items:

`random_tied_cos_min0.93`, `tiedcos_delta5_null0.5`, `pairnull_delta5_null0.5`, `pairnull_delta5_gate0.93`, `pairnull_delta5_gate0.93_bin`, `pairown_delta5_null0.5`, `pairown_delta5_null0.3`, and `pairown_delta5_null0.15`.

Their summary numbers remain internally consistent; the mismatched detail files cannot independently verify those zsRE results. This includes the main 0.65/1.00 reference. Do not average a zsRE summary with its CounterFact item file, reconstruct a zsRE paired interval from those rows, or use the CounterFact cost file as the zsRE run cost. The dataset-suffixed driver repairs protect new runs but do not recover overwritten evidence.

Owner follow-up: regenerate the selected reference and comparators under fresh dataset-specific identities, with checkpoint, configuration, code, calibration, ordered-item and reference-answer hashes in each run. Retain old files as historical records. Reproduce the one-stream number before extending seed/order coverage. Check the remaining checkpoint-path defect in X4-10 first.

### X4-02 — Published cost columns are faithful wall times; the ledgers do not certify matched compute (high)

The notes' rounded wall columns match each pilot's `training_wall_seconds`. Those values should remain wall times. They should not be replaced with `ledger.learning.accel_seconds`, which excludes substantial work.

For example, bp_500 records 2,625.294 s training wall time but only 6.418 s learning accelerator time and 80 reverses. The corrected ePC pilot records 4,073.414 s and 567.677 s respectively, with 90,080 reverses. In [train.py](../src/pccap/revision_v1/train.py), the outer BP `jax.value_and_grad` objective calls the base's compiled forward directly, outside the shared base-call ledger. The ePC path counts many relaxation operations, while its token field does not multiply all settling passes. A zero phase-sum residual therefore coexists with incomplete and asymmetric work accounting.

The comparison is matched by optimizer schedule/examples/seed, not demonstrated matched accelerator compute. The “approximately six times the base calls” phrase cannot be independently certified from these ledgers. Development timing forecasts should use synchronized measured wall spans and report compilation/setup separately until the missing outer forward/reverse work is instrumented.

The 12 completed pilots sum to **52,685.966 s (14.635 h) of training wall spans**. This is not a GPU allocation total or a calendar critical-path duration: runs include shared-GPU contention, setup scopes differ, and concurrency can overlap wall spans. The four zero-step reevaluations are excluded from this sum.

Summary ledgers may legitimately exceed stream-end cost files: the driver performs additional endpoint score/null probes afterward. For the balanced zsRE run the query delta is 400 full forwards, 5,063 tokens and 0.649 s; for the random 0.93 CounterFact run it is 499 forwards, 6,221 tokens and 0.911 s. Learning deltas are zero. These are identifiable scope differences, not unexplained training charges.

### X4-03 — Pilot behavior, stream behavior and checkpoint selection have different meanings (medium)

The pilot behavioral loop uses fixed-length generation: answer-labeled probes receive a length derived from the target token count, while natural preservation probes compare a short three-token cap-off continuation. This is a useful diagnostic, but it differs from the common stopping-rule, complete-answer stream endpoint. In particular, “perfect null generalization on dev” describes the sampled episode/probe conditions; it does not establish stream locality.

The selected best-dev checkpoint and the final optimizer state are distinct. Several rows report the selected checkpoint's metrics after completing all training steps. The whole run still costs all 400/600 steps, even when the selected checkpoint occurs earlier. Retaining both `best_dev` and final fields in the audit makes that distinction reviewable.

The 28 s statement in the synthetic-to-zsRE paragraph applies to fast adaptation off (28.47 s). The five-step variants take approximately 57–58 s. This is a prose scope correction, not a mismatch in the tabulated timings.

### X4-04 — The fact-code result is a negative for tested configurations, not a capacity theorem (medium)

The tested prompt-only and answer-sensitive code/controller configurations failed to acquire unseen stream edits. Turning on the reported fast-code steps did not fix that behavior. This supports prioritizing the working delta path.

It does not establish that a 256-dimensional code can never represent a new answer, or uniquely identify the training-pool size as the earlier cause. Retrieval errors, null rejection of own prompts, weak or saturated write gradients, loss weighting and controller conditioning coexist. The notes themselves expose a raw controller aggregate near 7.8 against a 0.3 bound, which can suppress a superposed delta's direction.

Before reopening the code-only path, use separate positive controls: oracle supporting-record selection, null disabled on verified own prompts, direct code-gradient/finite-difference checks, write-bound saturation traces, and a single arbitrary-answer overfit test with support/query separation. Compare one change at a time. Failure on these gates is more informative than another long pilot. It is reasonable to defer that branch now; the current evidence does not require abandoning it as mathematically impossible.

### X4-05 — What zsRE RET-GS 0.65 does and does not show (high for interpretation)

The configuration demonstrates that stable base observations, tied cosine keys, hard top-1 retrieval and taught per-answer-position writes can transfer edits to 65% of the sampled paraphrase endpoints while preserving all 50 sampled locality references. Relative to the cited 0.44 controls, the descriptive difference is +0.21 on this development stream.

“Non-learned” should mean **no episodic training of the reusable cap weights/null**. The base is pretrained, and each delta is learned from the support answer by gradient adaptation. The full system is not devoid of trained components. This condition contains no cap-level latent settling and does not demonstrate a PC mechanism.

The result is one seed/order, 100 development edits, under the v2 calibration and multiple development choices. Thresholds 0.90, 0.93 and 0.95 were examined; 0.93 and 0.95 both yield 0.65/1.00 on this sample. The apparent separation is a development observation, not proof of a unique threshold or a prespecified generalization guarantee. No fresh confirmation result or paired uncertainty estimate follows from these summaries. The missing original detailed file further limits retrospective paired analysis (X4-01).

Intermediate acquisition results (0.02 single-delta, 0.13 per-position soft selection, 0.23 dot/top-1, 1.00 cosine/top-1) motivate the redesign, but several mechanisms change across that sequence. They do not isolate cosine geometry as the sole cause of the entire improvement. Use equal-write/equal-selection ablations before a causal claim.

### X4-06 — CounterFact transfer and learned-null failures are substantial; their cause is not uniquely identified (high)

The random reference's CounterFact ES and RET-ES are both 1.00. The shorthand 0.18/0.16 refers to **RET-GS/LS**, not ES/LS. Acquisition succeeds while paraphrase transfer and locality fail.

Training the null has not delivered a demonstrated good tradeoff on both streams. The own-prompt pairwise run at threshold 0.5 gives zsRE ES/RET-ES/RET-GS/LS = 1.00/1.00/0.61/0.14 and CounterFact = 0.96/0.97/0.28/0.20. Lowering the threshold to 0.15 raises CounterFact LS to 0.54 while lowering ES to 0.62 and RET-ES to 0.71. The class-balanced run reaches 0.45/0.53/0.155/0.70 there. These do not establish a successful locality/acquisition compromise.

A fixed cosine gate with trained pairnull weights gives zsRE 1.00/1.00/0.54/0.92 and CounterFact 1.00/1.00/0.015/0.04. The notes' .02 and other half-percent values are ordinary rounding; exact values appear in the appendix.

Episode support occupancy, query-role balance, natural relation-neighbour similarity and long-prefix paraphrases all differ from the stream distribution. They are plausible causes requiring controlled tests. Means and p10/p90 score summaries show overlap but cannot by themselves prove that no threshold, calibrated score, or learned head could succeed. The logged “hard-null rate” measures the learned null decision, not the later cosine threshold; zero in that field can coexist with successful cosine rejection.

The currently running locality-trained pilot has no completed summary in this snapshot. No recommendation below assumes its outcome.

### X4-07 — Decision rule for retaining or replacing the fixed null (medium)

Keep the fixed cosine gate as a **provisional, dataset-qualified reference**, and retain cap-off, the stronger-cap BP reference and the actual learned-null alternatives. It is not a solved universal null policy: CounterFact LS 0.16 is inadequate evidence for that description.

Evidence that would change the recommendation:

1. Fix one checkpoint/configuration per candidate and replay the same supports, deltas, query boundaries and base on development examples excluded by subject/entity from episodic training. Compare fixed gate, learned null and calibrated learned null under the same write magnitude/selection conventions.
2. Report correct-support top-1, selection margin, learned-null probability and fixed-gate firing separately for own prompts, paraphrases, older facts, relation neighbours and unrelated text. Include oracle-record/null controls and paired failure examples. Use full-answer LS.
3. Stress occupancy at 100, 300 and 1,000 active/retired records; disclose byte/capacity failures instead of dropping them. Add multiple fixed orders/seeds and cluster intervals by the plan's realization/subject unit.
4. Select thresholds/hyperparameters only in the development protocol. Require a prespecified ES/LS constraint and RET-GS benefit over the chosen reference on **both** datasets, with acceptable drift and uncertainty; the lead freezes final margins afterward under D-R3. Do not reuse the current stream as fresh evidence.
5. Reconcile training/query compute and persistent bytes. Improvement purchased with extra inference, extra target exposure or relaxed locality needs a separately named comparison.
6. Once gates pass, run the fresh registered realization with the owner-managed revision freeze. Extending zsRE training would require a new exposure/decision action: the existing single-paraphrase zsRE allowance is evaluation-only under DEC-034(b).

A learned null meeting those conditions should replace the fallback. If it only helps CounterFact at acceptable locality, retain dataset-specific development conditions until the final protocol explicitly chooses how to combine them.

### X4-08 — The delta-byte statement understates answer-position scaling (high for long streams)

A float32 write at three 768-dimensional sites consumes **9,216 bytes (9 KiB) per answer position**, not per entire record. The installed delta tensor is `[answer_positions, 3, 768]`. At 32 positions it costs 294,912 bytes per record before keys, codes, retained support tokens, metadata and reusable weights. A thousand such records cannot fit the 64 MiB ceiling. Superseded records remain stored and charged.

The main zsRE summary records 3,704,832 delta bytes for 100 records: about 37,048 bytes per record, or 4.02 positions on average. That favorable sample average does not establish long-stream capacity. Report actual bytes, answer-length distribution and resource-stop counts; test worst-case bounds before Stage 4. The existing fixed metadata charge also remains an approximation for variable-length identifiers; this round does not certify physical-memory completeness.

### X4-09 — New endpoint coverage has an inventory and composition gap (medium)

The actual development arrays contain **400 near-neighbour, 100 temporal-correction and 54 composition rows**. The 5/6/5 counts in ongoing.md do not match the arrays. Composition has a declared minimum of 100 and a shortfall of 46. These are counts of available rows, not independent-subject counts or proof of semantic label verification.

Composition rows contain two support questions/answers and a join annotation, but no reviewed standalone composed question. R1-43 therefore reports a generated-bridge two-query diagnostic separately from direct composition. Missing/unverified hops are unreachable, while wrong generated bridges remain scored failures. Direct composition requires an explicitly reviewed, hash-bound question. The join annotation alone is insufficient to assert a validated two-fact reasoning endpoint. Label/question review and missing-case construction are CPU lanes that can proceed while the GPU is occupied, subject to source/exposure registration.

### X4-10 — R1-27 fixes ordinary output collisions but misses the actual checkpoint root (high, newly reproduced)

The driver now refuses existing summary and detail roots before model setup. However [r1_13_stream_eval.py](../scripts/r1_13_stream_eval.py) constructs the checkpoint guard using `rd.relative_to(ROOT)`, producing `assets/runs/results/R1/streams_revision/<tag>`. The harness writes with `run_dir.relative_to(ROOT / "results")`, producing `assets/runs/R1/streams_revision/<tag>`. An orphan directory at the actual destination is not refused by that preflight.

The CPU reproduction compiles the exact driver statements and harness checkpoint-path expression, relocating only the assets root into a repository test directory. The repaired-fixture preview reaches the intended strict expected failure: the actual checkpoint directory exists, but preflight accepts the identity. No model or GPU job is run.

Owner correction: make the preflight derive its path from the same results-relative expression as the harness (and apply its normal manifest/source-binding update). Retest existing summary, detail, actual checkpoint and dataset-isolation cases. Do not treat the present guard as covering every artifact. This round proposes no edit to the orchestrator-owned driver.

Related repaired boundaries now pass CPU controls with valid fixtures: constructor ceiling, configured ceiling on snapshot import, temporary-store validation before adoption, weight charge restoration, dot/cosine retrieval consistency, delta-capacity rollback/billing, mixed-step refusal before base work, and returned selection-pass cost. Raw `RecordStore.from_state` still requires an explicit `validate()`; the public cap importer performs it. Old R1-26 tests retain obsolete constructor assumptions and are not silently counted as a passing suite.

## Prioritized next work and concurrent lanes

| Priority | Owner/lane | Work that can start now | Dependency/checkpoint |
| --- | --- | --- | --- |
| 1 | Orchestrator | Repair actual checkpoint guard; retain dataset-specific run IDs and full provenance | Before reference reruns; update bound scripts if necessary |
| 1 | CPU audit/instrumentation owner | Specify missing outer BP/ePC cost events and tests against actual calls | Permission for shared-source edits; no GPU needed for tiny-base tests |
| 1 | Orchestrator GPU | Finish locality-trained run, then reproduce selected reference/comparators with new identities | GPU lease, completed summary, reviewed costs; do not retune on fresh data |
| 2 | CPU endpoint/data lane | Verify composition supports and direct questions, build registered coverage, review revision denominators | Development sources only; register new exposure before consuming new data |
| 2 | CPU analysis lane | Prepare paired reports, occupancy/byte checks and per-role null diagnostics | New artifacts now; empirical conclusions await new complete runs |
| 2 | Lead + runtime owner | Choose literal self-KD and informative LM continuation, refresh a common evaluation theta and exact work budget | R1-24b is dry; a hard-target runtime and GPU scheduling are still needed |
| 3 | Stage 3 design lane | Review the route-latent proposal, toy gates and answer-objective coupling | Conditional D-R5; no cap-level PC training launch yet |

Plan 9 places optional Stage 3 on days 15–22 and Stage 4 on days 20–28. This audit does not derive calendar lateness from those relative days: no current authorized launch date or remaining allocation was reconstructed. The demonstrated critical path is Stage 2 transfer/locality plus reproducible costs/provenance, not writing the optional latent solver. Skipping Stage 3 remains the plan's valid response if the working-feedforward gate is not met. The following appendices expose the full recounted rows so that those decisions need not rely on this prose alone.


## Appendix A — every stream summary

ES is immediate acquisition; RET-ES and RET-GS are whole-stream retention; LS is complete-answer locality. † means detailed rows are attributed to the other dataset. Summary values remain shown explicitly.

| Tag / dataset | ES | RET-ES | RET-GS | LS | Stream wall s | Detail attribution |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| bp_500_fast5_lr0.1 / zsre | 0.000 | 0.000 | 0.000 | 0.960 | 57.439 | dataset_matches |
| bp_500_fast5_lr1.0 / zsre | 0.000 | 0.000 | 0.000 | 0.960 | 57.861 | dataset_matches |
| bp_500_lr1e-3 / zsre | 0.000 | 0.000 | 0.000 | 0.960 | 28.469 | dataset_matches |
| cf_bp_500_lr1e-3 / zsre | 0.000 | 0.000 | 0.000 | 0.740 | 23.686 | dataset_matches |
| pairnull_delta5_gate0.93 / zsre | 0.000 | 0.000 | 0.010 | 1.000 | 29.149 | different_dataset_collision |
| pairnull_delta5_gate0.93@counterfact / counterfact | 0.060 | 0.070 | 0.010 | 0.980 | 47.957 | dataset_matches |
| pairnull_delta5_gate0.93_bin / zsre | 1.000 | 1.000 | 0.540 | 0.920 | 33.385 | different_dataset_collision |
| pairnull_delta5_gate0.93_bin@counterfact / counterfact | 1.000 | 1.000 | 0.015 | 0.040 | 36.795 | dataset_matches |
| pairnull_delta5_null0.5 / zsre | 0.000 | 0.000 | 0.010 | 0.860 | 26.491 | different_dataset_collision |
| pairnull_delta5_null0.5@counterfact / counterfact | 0.050 | 0.050 | 0.170 | 0.980 | 30.567 | dataset_matches |
| pairown_delta5_null0.15 / zsre | 0.980 | 0.980 | 0.550 | 0.180 | 30.751 | different_dataset_collision |
| pairown_delta5_null0.15@counterfact / counterfact | 0.620 | 0.710 | 0.265 | 0.540 | 27.181 | dataset_matches |
| pairown_delta5_null0.3 / zsre | 1.000 | 1.000 | 0.600 | 0.140 | 31.203 | different_dataset_collision |
| pairown_delta5_null0.3@counterfact / counterfact | 0.890 | 0.910 | 0.275 | 0.240 | 23.375 | dataset_matches |
| pairown_delta5_null0.5 / zsre | 1.000 | 1.000 | 0.610 | 0.140 | 31.195 | different_dataset_collision |
| pairown_delta5_null0.5@counterfact / counterfact | 0.960 | 0.970 | 0.280 | 0.200 | 22.499 | dataset_matches |
| pairownbal_delta5_null0.5 / zsre | 0.930 | 0.970 | 0.440 | 0.100 | 31.784 | dataset_matches |
| pairownbal_delta5_null0.5@counterfact / counterfact | 0.450 | 0.530 | 0.155 | 0.700 | 26.285 | dataset_matches |
| pool3k_delta5 / zsre | 0.000 | 0.000 | 0.000 | 0.640 | 39.767 | dataset_matches |
| random_tied_cos_min0.90 / zsre | 1.000 | 1.000 | 0.650 | 0.980 | 34.357 | dataset_matches |
| random_tied_cos_min0.93 / zsre | 1.000 | 1.000 | 0.650 | 1.000 | 34.437 | different_dataset_collision |
| random_tied_cos_min0.93@counterfact / counterfact | 1.000 | 1.000 | 0.180 | 0.160 | 28.179 | dataset_matches |
| random_tied_cos_min0.95 / zsre | 1.000 | 1.000 | 0.650 | 1.000 | 34.443 | dataset_matches |
| random_tied_cos_pdelta5_top1_nonull / zsre | 1.000 | 1.000 | 0.650 | 0.240 | 31.676 | dataset_matches |
| random_tied_cos_scores / zsre | 1.000 | 1.000 | 0.650 | 0.240 | 34.807 | dataset_matches |
| random_tied_delta5_nonull / zsre | 0.020 | 0.010 | 0.000 | 0.700 | 45.628 | dataset_matches |
| random_tied_pdelta5_nonull / zsre | 0.130 | 0.080 | 0.020 | 0.780 | 36.327 | dataset_matches |
| random_tied_pdelta5_top1_nonull / zsre | 0.230 | 0.160 | 0.080 | 0.100 | 38.486 | dataset_matches |
| tiedcos_delta5_null0.5 / zsre | 0.020 | 0.020 | 0.040 | 0.460 | 26.730 | different_dataset_collision |
| tiedcos_delta5_null0.5@counterfact / counterfact | 0.080 | 0.080 | 0.215 | 0.900 | 30.223 | dataset_matches |

## Appendix B — every pilot's cost scope

Learning token/F/R fields are reported ledger values, **not certified actual outer-training work**. Four zero-step evaluations have no optimizer training span.

| Pilot | Training wall s | Learning accel s | Total accel s | Learning tokens | Full F | Reverse R |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| bp_100_lr1e-4 | 508.250 | 4.836 | 5.516 | 84562 | 1520 | 80 |
| bp_500_lr1e-3 | 2625.294 | 6.418 | 7.415 | 137646 | 2480 | 80 |
| cf_bp_500_lr1e-3 | 4369.896 | 8.147 | 10.214 | 39813 | 3152 | 160 |
| cf_fresh_wd_400 | 4324.426 | 49.883 | 52.097 | 406824 | 29792 | 160 |
| cf_fresh_wd_400_r25 | 4305.887 | 61.105 | 63.071 | 489201 | 37992 | 160 |
| cf_pool3k_pair_own_400 | 8805.314 | 87.007 | 89.574 | 696517 | 63600 | 320 |
| cf_pool3k_pair_own_bal_400 | 5087.597 | 61.760 | 64.243 | 534443 | 43920 | 320 |
| cf_pool3k_pairnull_400 | 4442.996 | 58.601 | 61.220 | 493752 | 39000 | 320 |
| cf_pool3k_r25_600 | 6023.946 | 80.860 | 83.278 | 729476 | 57400 | 320 |
| cf_pool3k_tiedcos_400 | 4445.113 | 58.462 | 61.092 | 493752 | 39000 | 320 |
| epc_500_lr1e-3 | 3673.834 | 530.124 | 531.213 | 905540 | 96480 | 90080 |
| epc_500_lr1e-3_sd24 | 4073.414 | 567.677 | 568.365 | 1125462 | 100480 | 90080 |
| eval_pool3k_delta5 | 0.000 | 13.679 | 16.195 | 43127 | 4919 | 1920 |
| eval_pool3k_fast5_lr0.1 | 0.000 | 10.732 | 13.180 | 30247 | 3319 | 1600 |
| eval_pool3k_fast5_lr1.0 | 0.000 | 10.753 | 13.207 | 30247 | 3319 | 1600 |
| eval_pool3k_fast5_lr10.0 | 0.000 | 10.718 | 13.177 | 30247 | 3319 | 1600 |

## Appendix C — all Stage 2 notes table rows

Line numbers refer to the hash-bound notes snapshot. Each row's complete printed cells and full-precision source values are retained in the JSON recount.

| Notes line | Row label | Sources | Checked entries | Outcome |
| ---: | --- | --- | ---: | --- |
| 12 | bp_100_lr1e-4 | pilot/bp_100_lr1e-4/summary.json | 9 | checked |
| 13 | bp_500_lr1e-3 | pilot/bp_500_lr1e-3/summary.json | 9 | checked |
| 14 | cf_bp_500_lr1e-3 | pilot/cf_bp_500_lr1e-3/summary.json | 9 | checked |
| 15 | cf_fresh_wd_400 (prompt-only codes) | pilot/cf_fresh_wd_400/summary.json | 9 | checked |
| 16 | cf_fresh_wd_400_r25 (answer-sensitive codes) | pilot/cf_fresh_wd_400_r25/summary.json | 9 | checked |
| 17 | cf_pool3k_r25_600 | pilot/cf_pool3k_r25_600/summary.json | 9 | checked |
| 18 | cf_pool3k_tiedcos_400 | pilot/cf_pool3k_tiedcos_400/summary.json | 9 | checked |
| 19 | cf_pool3k_pairnull_400 | pilot/cf_pool3k_pairnull_400/summary.json | 9 | checked |
| 20 | cf_pool3k_pair_own_400 | pilot/cf_pool3k_pair_own_400/summary.json | 9 | checked |
| 21 | cf_pool3k_pair_own_bal_400 | pilot/cf_pool3k_pair_own_bal_400/summary.json | 9 | checked |
| 22 | epc_500_lr1e-3_sd24 | pilot/epc_500_lr1e-3_sd24/summary.json | 9 | checked |
| 23 | epc_500_lr1e-3 (under SD-24 defect) | pilot/epc_500_lr1e-3/summary.json | 9 | checked |
| 74 | answer NLL | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 75 | retrieval CE (exact in both) | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 76 | preservation KL | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 77 | paraphrase exact / old fact | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 78 | near-miss / unrelated unchanged | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 79 | wall | pilot/bp_500_lr1e-3/summary.json, pilot/epc_500_lr1e-3_sd24/summary.json | 2 | checked |
| 146 | none | stream_eval_random_tied_cos_pdelta5_top1_nonull.json | 4 | checked |
| 147 | 0.90 | stream_eval_random_tied_cos_min0.90.json | 4 | checked |
| 148 | **0.93** | stream_eval_random_tied_cos_min0.93.json | 4 | checked |
| 149 | 0.95 | stream_eval_random_tied_cos_min0.95.json | 4 | checked |
| 185 | zsRE | stream_eval_random_tied_cos_min0.93.json | 4 | checked |
| 186 | zsRE | stream_eval_pairnull_delta5_gate0.93_bin.json | 4 | checked |
| 187 | CounterFact | stream_eval_random_tied_cos_min0.93@counterfact.json | 4 | checked |
| 188 | CounterFact | stream_eval_pairnull_delta5_gate0.93_bin@counterfact.json | 4 | checked |
| 201 | zsRE | stream_eval_pairown_delta5_null0.5.json | 4 | checked |
| 202 | zsRE | stream_eval_pairown_delta5_null0.3.json | 4 | checked |
| 203 | zsRE | stream_eval_pairown_delta5_null0.15.json | 4 | checked |
| 204 | CounterFact | stream_eval_pairown_delta5_null0.5@counterfact.json | 4 | checked |
| 205 | CounterFact | stream_eval_pairown_delta5_null0.3@counterfact.json | 4 | checked |
| 206 | CounterFact | stream_eval_pairown_delta5_null0.15@counterfact.json | 4 | checked |
| 219 | zsRE | stream_eval_pairownbal_delta5_null0.5.json | 5 | checked |
| 220 | CounterFact | stream_eval_pairownbal_delta5_null0.5@counterfact.json | 5 | checked |

## Appendix D — all stream markdown rows

This is the corrected full-tag matching preview; no CounterFact suffix is silently discarded. All reported numeric and fast-step cells agree.

| Stream table line | Summary tag | Dataset | Status |
| ---: | --- | --- | --- |
| 7 | bp_500_lr1e-3 | zsre | unique_match |
| 8 | bp_500_fast5_lr0.1 | zsre | unique_match |
| 9 | bp_500_fast5_lr1.0 | zsre | unique_match |
| 10 | cf_bp_500_lr1e-3 | zsre | unique_match |
| 11 | pool3k_delta5 | zsre | unique_match |
| 12 | random_tied_delta5_nonull | zsre | unique_match |
| 13 | random_tied_pdelta5_nonull | zsre | unique_match |
| 14 | random_tied_pdelta5_top1_nonull | zsre | unique_match |
| 15 | random_tied_cos_pdelta5_top1_nonull | zsre | unique_match |
| 16 | random_tied_cos_scores | zsre | unique_match |
| 17 | random_tied_cos_min0.90 | zsre | unique_match |
| 18 | random_tied_cos_min0.93 | zsre | unique_match |
| 19 | random_tied_cos_min0.95 | zsre | unique_match |
| 20 | random_tied_cos_min0.93@counterfact | counterfact | unique_match |
| 21 | tiedcos_delta5_null0.5 | zsre | unique_match |
| 22 | tiedcos_delta5_null0.5@counterfact | counterfact | unique_match |
| 23 | pairnull_delta5_null0.5 | zsre | unique_match |
| 24 | pairnull_delta5_null0.5@counterfact | counterfact | unique_match |
| 25 | pairnull_delta5_gate0.93 | zsre | unique_match |
| 26 | pairnull_delta5_gate0.93@counterfact | counterfact | unique_match |
| 27 | pairnull_delta5_gate0.93_bin | zsre | unique_match |
| 28 | pairnull_delta5_gate0.93_bin@counterfact | counterfact | unique_match |
| 29 | pairown_delta5_null0.5 | zsre | unique_match |
| 30 | pairown_delta5_null0.5@counterfact | counterfact | unique_match |
| 31 | pairown_delta5_null0.3 | zsre | unique_match |
| 32 | pairown_delta5_null0.3@counterfact | counterfact | unique_match |
| 33 | pairown_delta5_null0.15 | zsre | unique_match |
| 34 | pairown_delta5_null0.15@counterfact | counterfact | unique_match |
| 35 | pairownbal_delta5_null0.5 | zsre | unique_match |
| 36 | pairownbal_delta5_null0.5@counterfact | counterfact | unique_match |
