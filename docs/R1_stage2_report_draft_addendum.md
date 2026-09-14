# Stage 2 draft addendum — completed continuation controls and an urgent drift diagnostic

Codex, 2026-09-14. This new file supplements [the Stage 2 draft](R1_stage2_report_draft.md) after the owner committed completed R1-24 results as `9c459aa`. The original draft/task record/matrix are preserved under the new-files-only rule. This addendum supersedes their statements that the two **development executions** are still active. It does not admit either checkpoint for final confirmation.

The important new observation is **large cap-on ordinary-text loss increases with the original-base learned reader**, alongside good editing RET-GS and LS. That requires diagnosis before claiming general fidelity or freezing the primary. Informative LM continuation separately fails its teacher-KL fidelity bound. The two observations must not be conflated.

## 1. Verification and scope

Evidence: [completion recount](../logs/r1_round7/continuation_completion_review.json), [CPU log](../logs/r1_round7/continuation_review_cpu.txt), and new reader `scripts/r1_47_continuation_review.py`.
Both summaries and all **16** evaluation cells are complete at 100/100 edits. The recount checked ordered item identities, immediate/retained metric aggregates, saved locality aggregates, all 3,014 + 6,028 training-step entries, forward-token totals, manifest/reader/checkpoint hashes, and drift arithmetic. Every check passes. No model or GPU was executed by the reviewer.

The four original-base references repeat identically between the two jobs in metrics and drift. They are repeated evaluations of the same conditions and item sets, not eight independent controls. Per-locality answer pairs and per-position drift logits are absent, so aggregate reconciliation does not reproduce generation or identify the cause of each changed answer.

## 2. Base continuation fidelity and editing outcomes

| Treatment | Recorded forward-pass tokens | Teacher KL (nats/token) | Ordinary NLL change | Fidelity classification |
| --- | ---: | ---: | ---: | --- |
| Literal self-KD | 771,580 | 0.0000293325 | −0.0000617914 | Pass on the 8,192-position development probe |
| Informative LM | 771,581 | 0.0949791 | −0.105065 | **Fail**: KL exceeds 0.001 despite improved ordinary NLL |

These values come from [literal summary](../results/R1/r1_24/r1_24_literal_v3b/summary.json) and [LM summary](../results/R1/r1_24/r1_24_lm_v2b/summary.json). “Matched” in the summary refers to its training-budget declaration; it does not override `fidelity_pass=false`.

| Treatment | Dataset | S0 RET-GS / LS | S1 RET-GS / LS | R0 RET-GS / LS | R1 RET-GS / LS |
| --- | --- | ---: | ---: | ---: | ---: |
| Literal | zsre | 0.440 / 1.00 | 0.490 / 1.00 | 0.980 / 1.00 | 0.980 / 1.00 |
| Literal | counterfact | 0.000 / 1.00 | 0.000 / 0.92 | 0.795 / 1.00 | 0.795 / 0.92 |
| LM | zsre | 0.440 / 1.00 | 0.390 / 0.86 | 0.980 / 1.00 | 0.970 / 0.88 |
| LM | counterfact | 0.000 / 1.00 | 0.000 / 0.28 | 0.795 / 1.00 | 0.775 / 0.28 |


S0 = original base + stable C1; S1 = continued base + stable C1; R0/R1 = original/continued base + the learned primary. All ES are 1.00; omitted RET-ES are available in the source-bound recount (zsRE S0/literal S1 0.99, other shown continued LM/learned and CounterFact rows 1.00). LS uses the **original-base** reference.

Literal S1 improves zsRE RET-GS by 0.05; learned R0 exceeds literal S1 by 0.49. CounterFact S1 remains at zero and R0 at 0.795. These are informative development contrasts at one schedule/budget, without paired uncertainty or fresh subjects. The failed-fidelity LM branch remains a labelled distribution-shift experiment. It does not establish the result of a valid informative, fidelity-matched continuation.

A KL-constrained or lower-step LM follow-up could produce a valid control, but should not be silently substituted into the completed run. Whether to require that follow-up before Stage 4 is a lead protocol decision: if the final design retains a **fidelity-matched informative S1** claim, this checkpoint cannot satisfy it. The frozen claim must instead omit/relabel the branch or use a newly admitted treatment. Matrix v3 correctly leaves continued checkpoint hashes unadmitted and launches disabled.

Literal KD was not an exact numerical no-op. Its first logged loss is 1.2451e−7 and gradient norm 3.1139e−5; the final tensor digest differs from the original. Mean held-out KL is small, but exact output sensitivity can still change a sequence. The CounterFact locality decrement of 0.08 equals four of 50 comparisons. It is plausible that base output changes contribute, but S1 is an **active stable cap**, not a cap-off condition. Equal LS decrements in stable and learned caps do not by themselves prove that every changed answer was caused solely by the base or by a near tie. A continued-cap-off versus original-base reference trace and per-prompt decisions would establish that attribution.

## 3. New original-base cap drift finding

The completed jobs evaluate endpoint caps on the separate prepared ordinary-text drift sample, 128 windows × 127 next-token positions = **16,256** positions. Original-base NLL on this sample is 3.873360.

| Edited memory / original-base cap | Cap-on NLL increase | Perplexity ratio to original base | Interpretation |
| --- | ---: | ---: | --- |
| zsRE / stable C1 | +0.000931 | 1.000932 | Small change on this subset |
| zsRE / learned primary | **+0.599062** | **1.820411** | Substantial ordinary-text harm on this assay |
| CounterFact / stable C1 | 0.000000 | 1.000000 | No measured loss change on this subset |
| CounterFact / learned primary | **+0.393528** | **1.482201** | Substantial ordinary-text harm on this assay |

The same learned-reader drift appears in both jobs' R0 references. It is already present **without continuation**, so the failed-fidelity LM treatment cannot explain it. The increases are much larger than the proposed +0.01 loss tolerance. This is a measured subset warning, not a full-validation estimate or a confirmed root cause. The earlier standalone stream summaries' drift fields remain unsupported; the new result is in each `control_endpoint.json` and the job summary, outside those older fields.

The original-base learned rows retain RET-GS 0.98/0.795 and LS 1.00, showing why short editing-locality prompts are insufficient to certify ordinary-text fidelity. The new unseen-prompt endpoint tests another relevant population, but its absent-fact edit prompts still do not replace the ordinary-text assay.

### Assay semantics and next diagnostic

Read-only source inspection of [BoundaryEvaluator](../scripts/r1_24_runtime.py) and [the common drift routine](../src/pccap/harness/runs.py) shows that each next-token prefix is treated as a separate query: the boundary wrapper resets selection and selects on the full current prefix before reading logits. It does not carry one selection from the first token through all 127 teacher-forced positions. This is a declared independent-prefix applicability assay, distinct from holding a selected edit across an answer generation. No teacher target is used for selection. Persistent state hashes are checked around the drift assay.

The fidelity probe and cap drift use **different input sources/windows**: fidelity is 8,192 positions from the held-out OpenWebText shard; cap drift is 16,256 positions from `assets/data/prepared/lm/drift_tokens.npy`. Thus the LM base's −0.105 NLL change on the former is not the baseline for the latter.

Before changing the reader, the owner should:

1. Reproduce a small fixed subset with original base, empty cap, forced-null cap, stable cap and learned cap; show cap-off/forced-null equality and independent-query reset behavior.
2. Record prefix length, selected fact, actual hard gate, lexical/best score, delta position and per-position loss change. Report harm conditional on firing and unconditional harm over all positions.
3. Compare independent-prefix selection with an explicitly specified fixed-context, held-selection continuation assay. Neither should silently replace the other.
4. Verify whether broad/long ordinary-text prefixes trigger irrelevant edits and repeatedly use the first delta position. That is a plausible mechanism from the read path, **not an established diagnosis**.
5. Only after those controls, evaluate an ordinary-text null/preservation objective, scope restriction or relevant lexical change under a new development identity; retain all existing editing/LS/unseen endpoints to measure the tradeoff.
6. Complete the full declared validation split and fresh-population review before a fidelity claim or freeze.

These source/runtime changes remain owner work under the permission protocol; this review neither applies them nor asks to interrupt an active job. CPU diagnostic fixtures and metadata/admission work can proceed concurrently with any owner GPU reproduction.

## 4. Updated disposition

All five round-7 Codex deliverables remain complete as drafts/audit/implementation artifacts. Their time ceilings and final data/checkpoint decisions remain unfrozen. The completed controls strengthen the evidence that the tested continuation schedules do not reproduce the primary's editing retention; they do not justify a general impossibility claim about continuation, and the LM branch is not fidelity-matched.

The new cap drift result raises the priority of ordinary-text scope/fidelity diagnosis above another broad architecture search or a final freeze. Good edit retention is established on the sampled development streams; broad preservation is not. The original report's execution cutoff is preserved, and this addendum is the current review handoff.
