# Revision v1, Stage 2 — learned applicability with stable observations and per-position writes

Draft 1, Codex, 2026-09-14. Prepared for the orchestrator's revision and the lead's Stage 2 review.
Evidence cutoff: repository HEAD `0d79f513dbba023bfd9635ef00504a4807ced8d4`, with the additive round-7 artifacts named below.
Contract lineage: [original month plan](pc_cap_month_plan_readable.pdf), [revision plan 9](updated_plan9.md), and the recorded [decisions](decisions.md).
This report preserves the separate [v0 report](report.md) and its negative findings. It does not close the lead's outstanding v0 review or freeze revision v1.

## 1. Abstract

A language-model editor must learn a requested change, recognize later paraphrases of that request, and leave unrelated answers alone. The earlier radius-gated cap struggled mainly to recognize which stored edit applied. Revision v1 now combines observations from an unedited base model, a learned record selector with an explicit “none applies” decision, and gradient-taught corrections stored for each answer position. A mixed-domain reader uses one deployment rule on both datasets. On 100-edit development streams it obtains retained paraphrase success (RET-GS) of 0.96–0.98 across three training seeds on zsRE and 0.780–0.795 on CounterFact, with measured locality preservation 1.00. A second, overlapping development draw gives 0.990 and 0.765 for the selected seed.

This is a substantial recovery from the earlier failed learned readers. It supports carrying the learned system into comparative evaluation. It does **not** establish fresh-data generalization, predictive-coding superiority, complete language-model fidelity, or performance at 1,000 edits. CPU reproduction confirms that CounterFact candidate/selection accuracy degrades at large memory and that zsRE increasingly accepts plausible edit prompts about absent facts. An additive unseen-prompt endpoint and an unfrozen 240-cell matrix now make these risks explicit. Fresh-population admission, cache provenance, continuation controls, full endpoint integration, profiling and a budget decision remain required.

## 2. What the system does and how it is trained

### 2.1 Architecture and information boundaries

The base is the existing JAX GPT-2 implementation. It stays fixed in the selected reader-training and editing path. The cap observes the base with writes disabled at blocks 3/7/11; support and query keys therefore share a stable representation. A tied cosine embedding retrieves four candidate records. A pairwise null head, a query-only null term and a lexical overlap feature with stop-token list v1 decide applicability. At prediction time only the query prompt and stored support information enter selection; query answer labels and the desired record ID are training/evaluation targets, not selector inputs. This boundary was checked in [R1-46](../logs/review_r1_50.md).

For the primary condition, selection is hard top-1 with null threshold 0.5 and no minimum-cosine gate. It is held across the generated answer, reset between independent queries, and supplies binary write mass: a rejected query receives no edit; an accepted query receives its selected record's correction. A new support can teach an arbitrary answer through up to five normalized per-position delta steps at learning rate 0.1, using the existing aggregate bound A = 0.3 and archived calibration scales. Fast **code** adaptation is off. The taught delta replaces the controller write for records carrying deltas.

The selected identity is [primary_condition_v1.json](../manifests/revision_v1/primary_condition_v1.json), seed 0:
NPZ SHA-256 `9f676076ad94df2fb6a3257c5838edb9e365f7ddc808efd2d044ef6e01f626fd`;
parameter-tree hash `e53d7ee1baaf9c47a827b5914cad1a128214484587c1b6da28a6816a56e7d81e`.
The base, reader, calibration, stop list and decode policy are made more explicit in [matrix v3](../manifests/revision_v1/run_matrix_draft_v3.json).
A development reference pointer is not a completed frozen protocol.

### 2.2 Training population, objective and selection

CounterFact supplies a 3,000-item DEC-037 training pool. zsRE supplies a 3,000-item teacher-filtered training pool under DEC-039; all **6,000** candidates reserved for that filter remain exposed/excluded, including unused candidates. The mixed pilot caches the first 1,000 items of each training pool. Within each bank, 900 are used for training episodes and 100 for development checkpoint selection. These “held-out” bank rows are development data, not untouched confirmatory subjects.

The primary pilot uses memories of 64 records, normally eight queried memory records with own-prompt, paraphrase and locality roles, plus eight outside-prompt null queries; 300 optimizer steps with two episodes per step; AdamW learning rate 0.001, weight decay 0.01 and gradient norm clipping at 1.0. The selected seed-0 checkpoint is step 249, chosen by development retrieval loss over six fixed episodes. Its recorded retrieval CE is 0.1904. It is distinct from the final optimizer state.

The optimized objective combines answer and preservation prefix losses with class-balanced retrieval loss. Record-target and null-target queries each receive half of retrieval weight when both classes occur. This is not equal domain/answer-length weighting: the fast trainer **sums** answer and preservation prefix contributions into gradients while its log reports their means. Longer answers therefore affect the relative objective weights. CounterFact's eligible answer arrays here have one content token plus newline; they are legitimate nonempty source answers, not evidence of corrupted caches.

Training is also a surrogate for deployment: it uses a soft distribution over all episode records and code/controller writes, whereas deployed editing restricts candidates, makes a hard selection and teaches per-position deltas. The current success is an empirical result for this package; it is not a demonstrated meta-gradient through the deployed delta update. [R1-46](../logs/review_r1_50.md) records these reductions, information boundaries and remaining mismatches.

### 2.3 Measurement definitions

| Quantity | Meaning and unit of analysis |
| --- | --- |
| ES | Immediate full-answer acquisition after each attempted support edit, using common greedy decoding and alias scoring. |
| RET-ES | Original-prompt answer success at the end of the whole stream, without conditioning on initial acquisition or surviving records. |
| RET-GS | End-of-stream paraphrase success, averaged within each item, then across items. Two CounterFact paraphrases are not two independent subjects. |
| LS | Saved `ls_complete_answer_end`: exact cap-on versus cap-off decoded-text agreement on 50 locality prompts in these pilots. This equality check does not separately require both decodes to terminate. |
| Bank own firing / top-k recall | Cached-feature selection diagnostics; they do not generate answers and cannot replace RET-GS or LS. |
| New unseen endpoint | Actual hard-gate acceptance and cap-induced answer change on predeclared same-pool facts absent from the full edit history; includes separate strict complete-answer preservation and explicit missing/truncated counts. |

Stream generation uses the shared maximum of 32 new tokens and newline/EOS stopping; correctness is broader than first-token accuracy. CounterFact stream RET-GS generally averages two paraphrases per item; zsRE has one. The bank profile instead uses one sampled paraphrase per queried memory item. The 100-edit primary rows have 100 ES/retention items and 50 locality prompts. LS = 1 means 50/50 observed text agreements, not a demonstrated 99% population guarantee. Individual locality output pairs were not saved in the historical stream artifacts, so this recount verifies their aggregates rather than independently rescoring every locality generation.

## 3. Diagnosis chain: why the design changed

The [Stage 0 diagnosis](R1_diagnosis.md) and [Stage 2 notes](R1_stage2_notes.md) record a sequence of failed and successful interventions. Several components changed together; this chain motivates the design but is not a factorial causal ablation.

| Observation | Measured evidence | Consequence and limit |
| --- | --- | --- |
| v0 often stored useful values but read the wrong record | On one 100-edit zsRE stream, live C1/C2 paraphrase success 0.24/0.29; verified oracle record reads reach 0.94/0.94 | Diagnose observation/selection failure. Oracle availability is privileged; this does not exonerate storage under pressure or revision. |
| Edited observations drift from stored keys | C1 site-3 mean key displacement 0.23 against radius 0.189; rebuilding stable shadow keys raises C1/C2 paraphrase exactness to 0.67/0.49 | Use write-free observations at both write and read. Shadow teacher-forced diagnostics differ from an actual edited stream. |
| Stable in-stream geometry helps but leaves a residual | Stable and matched-update controls reach RET-GS 0.44 on the zsRE stream | Compare the learned package with these controls, rather than only with weak live v0. |
| Synthetic/code-only training did not acquire natural edits | Synthetic-trained bp_500 gives ES/RET-GS 0/0 on zsRE; natural code variants still generalize poorly | Prioritize direct per-position deltas. This is a negative for the tested configurations, not a theorem about 256-dimensional codes. |
| Acquisition depends on the deployed write/read combination | Intermediate zsRE ES: one delta per record 0.02; per-position soft mixing 0.13; hard top-1 dot product 0.23; tied cosine hard top-1 1.00 | Preserve these distinct configurations; do not attribute the whole improvement solely to training. |
| Random geometry solves much of zsRE but fails CounterFact locality | Regenerated random reference: zsRE RET-GS/LS 0.65/1.00; CounterFact 0.18/0.16 | Learned applicability must handle relation neighbours, not just broad domain style. |
| Small natural episodes taught the wrong null behavior | Own prompts were rejected; adding own-prompt labels restored acquisition but often damaged locality; balancing/locality additions alone did not transfer | Match memory scale, query roles, outside facts and deployment populations. Historical overwritten rows are labelled in §8. |
| Larger episodes plus lexical evidence recover CounterFact | CounterFact-only stream/lexical seed 0 reaches RET-GS/LS 0.775/1.00; zsRE remains 0.49/0.98 under the same null rule | Subject-sensitive matching helps; domain shift remains. A lexical signal is a hypothesis to ablate, not a proven isolated cause. |
| Mixed-domain training unifies the deployed rule | Current seed 0 reaches 0.98/1.00 on zsRE and 0.795/1.00 on CounterFact, threshold 0.5 without cosine gate | Keep this as the development primary; test scale and fresh subjects before freezing conclusions. |

The earlier DEC-038 proposal to drop the learned reader is superseded by this recovery. Per-dataset M5 operating points remain useful historical alternatives: the seed-2 CounterFact-only reader chose null 0.7/no gate on CounterFact and null 0.95/gate 0.93 on zsRE, giving 0.935/1.00 and 0.95/1.00 on both development draws. They are selected alternatives, not additional independent confirmation or the current one-rule primary.

## 4. Completed development results

### 4.1 Controls on the Stage 0 zsRE stream

| Condition | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: |
| Live C1 | 1.000 | 0.920 | 0.240 | 1.000 |
| Live C2 | 1.000 | 0.790 | 0.290 | 1.000 |
| Stable C1 | 1.000 | 0.990 | 0.440 | 1.000 |
| Stable C2 | 0.990 | 0.970 | 0.440 | 1.000 |
| Matched update (historical three-step) | 1.000 | 0.990 | 0.440 | 1.000 |


These rows are from [v0-stable C1](../results/R1/v0_stable_C1.json), [v0-stable C2](../results/R1/v0_stable_C2.json), and [matched-update C1](../results/R1/matched_update_C1.json); live rows use the embedded Stage 0 references. The matched-update historical assay used up to three normalized steps; the draft final comparator proposes five and must be profiled/re-evaluated under that identity. The shadow-key 0.67/0.49 and oracle 0.94 figures above must not replace these actual-stream comparator values.

### 4.2 Regenerated random reference and current learned primary

| Run / dataset | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: |
| [Random regenerated / zsRE](../results/R1/stream_eval_ref_nonlearned_gate0.93_v2.json) | 1.000 | 1.000 | 0.650 | 1.000 |
| [Random regenerated / CounterFact](../results/R1/stream_eval_ref_nonlearned_gate0.93_v2@counterfact.json) | 1.000 | 1.000 | 0.180 | 0.160 |
| [Mixed seed 0, stream 21 / zsRE](../results/R1/stream_eval_mixed_null0.5.json) | 1.000 | 1.000 | 0.980 | 1.000 |
| [Mixed seed 0, stream 21 / CounterFact](../results/R1/stream_eval_mixed_null0.5@counterfact.json) | 1.000 | 1.000 | 0.795 | 1.000 |
| [Mixed seed 1, stream 21 / zsRE](../results/R1/stream_eval_mixed_s1_null0.5.json) | 1.000 | 1.000 | 0.960 | 1.000 |
| [Mixed seed 1, stream 21 / CounterFact](../results/R1/stream_eval_mixed_s1_null0.5@counterfact.json) | 1.000 | 1.000 | 0.780 | 1.000 |
| [Mixed seed 2, stream 21 / zsRE](../results/R1/stream_eval_mixed_s2_null0.5.json) | 1.000 | 1.000 | 0.970 | 1.000 |
| [Mixed seed 2, stream 21 / CounterFact](../results/R1/stream_eval_mixed_s2_null0.5@counterfact.json) | 0.990 | 0.990 | 0.785 | 1.000 |
| [Mixed seed 0, stream 22 / zsRE](../results/R1/stream_eval_mixed_stream22_null0.5.json) | 1.000 | 1.000 | 0.990 | 1.000 |
| [Mixed seed 0, stream 22 / CounterFact](../results/R1/stream_eval_mixed_stream22_null0.5@counterfact.json) | 1.000 | 1.000 | 0.765 | 1.000 |


Each row label links its saved JSON; the [recount](../logs/r1_round7/stage2_report_evidence.json) binds matching item/checkpoint/metric files and verifies their aggregates. All rows here use 100 edits. Training seeds 0/1/2 are reader replicates; stream seeds 21/22 choose development items, with one update order each. Stream 22 was run for seed 0, not for every seed in a complete three-by-two factorial design.

The two item sets overlap by **33 zsRE items and 36 CounterFact items**, independently recounted from the saved ordered inventories. The repeated development pool, selected checkpoint, architecture and thresholds preclude treating these rows as independent final realizations. The primary null threshold remains 0.5: the development threshold-0.7 CounterFact result 0.805 is a different operating point and is not silently substituted for 0.795.

On stream 21, selected-package RET-GS exceeds the regenerated random reference by 0.330 on zsRE and 0.615 on CounterFact. The latter also raises observed LS from 0.16 to 1.00. Architecture, null/lexical settings and training differ, so this is a package comparison rather than the isolated effect of learning.

### 4.3 Longer streams and alternative larger-memory training

| Run / dataset | Edits | ES | RET-ES | RET-GS | LS |
| --- | ---: | ---: | ---: | ---: | ---: |
| [Primary m64 at 250 edits / zsRE](../results/R1/stream_eval_mixed_n250_null0.5.json) | 250 | 1.000 | 1.000 | 0.980 | 1.000 |
| [Primary m64 at 250 edits / CounterFact](../results/R1/stream_eval_mixed_n250_null0.5@counterfact.json) | 250 | 1.000 | 1.000 | 0.722 | 1.000 |
| [Alternative m256 at 100 edits / zsRE](../results/R1/stream_eval_mixed_m256_null0.5.json) | 100 | 1.000 | 1.000 | 0.970 | 1.000 |
| [Alternative m256 at 100 edits / CounterFact](../results/R1/stream_eval_mixed_m256_null0.5@counterfact.json) | 100 | 1.000 | 1.000 | 0.830 | 0.980 |


“m256” changes training memory and query counts, not the deployment occupancy of these 100-edit rows. It modestly improves CounterFact RET-GS while losing one of 50 locality agreements; zsRE unseen rejection also worsens in the bank assay. It was not promoted over the 64-record primary. At 250 actual stream records, CounterFact RET-GS is 0.722 while observed LS remains 1.00. A 250-edit run does not establish the required 1,000-edit endpoint.

The primary 100-edit snapshots report 17,319,676 bytes on zsRE and 15,456,916 bytes on CounterFact, including 13,392,912 reusable weight bytes. Delta storage grows with answer positions: three sites × 768 fp32 values is 9,216 bytes **per answer token**, about 36.9 KB for a four-token record before keys/codes/metadata/weights. Record count alone is not a complete capacity measure; freeze admission must use the actual answer-length distribution and total bytes.

## 5. Scale diagnostics and the missing locality population

| Dataset / memory | Paraphrase own firing | Own in top-4 | Locality hard-null | Outside hard-null | Para/locality n | Outside n |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| counterfact / 64 | 0.71875 | 0.875 | 0.96875 | 1.000 | 64 | 200 |
| counterfact / 100 | 0.81000 | 0.950 | 0.99000 | 0.995 | 100 | 200 |
| counterfact / 300 | 0.79500 | 0.900 | 0.99000 | 0.980 | 200 | 200 |
| counterfact / 1000 | 0.59000 | 0.725 | 0.97500 | unavailable | 200 | 0 |
| zsre / 64 | 1.00000 | 1.000 | 1.00000 | 0.915 | 64 | 200 |
| zsre / 100 | 0.98000 | 1.000 | 1.00000 | 0.870 | 100 | 200 |
| zsre / 300 | 0.98500 | 1.000 | 1.00000 | 0.665 | 200 | 200 |
| zsre / 1000 | 0.98000 | 0.995 | 1.00000 | unavailable | 200 | 0 |


Sources: [primary scale profile](../results/R1/scale_profile_r1_50_stream_mixed.json) and the new [CPU audit](../logs/audit_r1_28b.md). The same RNG/size schedule was reproduced on cached banks; all saved values agree within 1e-5. Exact IDs and denominators are retained in [x6_audit.json](../logs/r1_round7/x6_audit.json). Para/locality query counts are min(memory, 200); outside count is 200 where available. The profile includes training and selection-development bank items.

At 1,000 CounterFact records, 27.5% of sampled paraphrases lack the correct record in the top four and only 59% fire their own record. On zsRE, outside-prompt false firing is 13% at memory 100 and 33.5% at 300, despite perfect hard-null rejection of the separate locality population. The original bank contains only 1,000 records, so there are **zero** outside queries at occupancy 1,000. Unavailable results cannot be interpreted as successful rejection.

The [top-16 diagnostic](../results/R1/scale_profile_r1_50_stream_mixed_top16.json) reports CounterFact memory-1,000 candidate recall 0.895, own firing 0.640 and locality hard-null 0.925. Its size/RNG schedule differs from the top-four file; this is not a paired top-k intervention. The [m256 diagnostic](../results/R1/scale_profile_r1_50_stream_mixed_m256.json) reports own firing 0.625 at CounterFact memory 1,000 and zsRE outside **hard-null** rates 0.625/0.500 at memories 100/300. The notes' 0.59 at memory 100 is mean null mass (0.58859), not hard-null frequency. Alternative training and sampling identities remain separate.

[R1-44](tasks/R1-44.md) now implements the missing same-pool outside-prompt endpoint. It takes explicit, reviewed IDs, excludes the entire attempted edit history including evicted/revised facts, performs actual cap-off/cap-on generation, observes the cached decision without an extra base pass, and restores state between cases. Labels are excluded from prediction. It reports firing, bounded text/token changes, termination and strict complete preservation separately; missing inventory or instrumentation cannot become a zero error rate. Ten CPU tests include real TinyBase/RevisionCap execution.

The draft proposes 100 outside items per realization, reused across conditions/orders/checkpoints and disjoint from all final edit streams and other reserves. At 1,000 edits this requires at least 1,100 suitable facts for one realization, or **3,300** for three disjoint realizations before separate challenges. The sample size and statistical margin remain unfrozen. Firing without changed output is possible; both endpoints are needed.

## 6. Predictive coding, continuation and fidelity controls

The successful primary is a BP-trained feedforward cap. It establishes no advantage from cap-level settling or predictive-coding credit. Earlier synthetic pilots compared identical seeds/episodes/optimizer schedules under BP and corrected ePC credit:

| Metric after 500 × 4 episodes | BP reference | Corrected ePC surrogate |
| --- | ---: | ---: |
| Development answer NLL | 2.85 | 4.50 |
| Retrieval CE | 0.46 | 0.96 |
| Preservation KL | 0.46 | 1.14 |
| Fixed-length paraphrase exact / old fact | 0.41 / 0.125 | 0.25 / 0.25 |
| Near-miss / unrelated unchanged | 0.94 / 1.00 | 1.00 / 0.81 |
| Recorded training wall time | 44 min | 68 min |

These are pre-answer-sensitive-code, synthetic, selected-checkpoint diagnostics from the [notes](R1_stage2_notes.md), audited in [R1-X4](../logs/review_r1_stage2.md). Fixed-length, sometimes label-length-informed probes differ from the stream decoder. The older `epc_500_lr1e-3` row used the SD-24 defective energy and must remain labelled as such. Correcting the site prior restores useful gradient direction but does not establish superiority. The schedules are matched; full accelerator compute was not established by the old ledgers.

DEC-040 has selected **both** continuation treatments; it is no longer awaiting a choice. The [literal recipe](../manifests/revision_v1/r1_24_control_v3.json) minimizes temperature-squared KL from the original frozen teacher to an initially identical student. At exact equality its gradient is zero, making it a useful self-distillation/no-op control whose numerical fidelity must be measured. The [informative LM recipe](../manifests/revision_v1/r1_24_control_lm_v2.json) instead learns hard next-token targets on the same declared training shard. Both use Adam at learning rate 1e-6, seed 1729, 128-token sequences and no dropout, with weights/configuration paths now colocated.

The reconciled reference budget is **771,581 forward-pass tokens**: 458,002 outer-training positions plus 313,579 shared bank-construction positions. Literal KD spends 771,580 (one odd token unspent), half teacher and half student; LM spends 771,581 student positions and consumes 771,582 source tokens including lookahead. Reverse positions and data exposure differ. This is forward-token matching, not time/FLOP matching. The accounting rerun has a different parameter hash from the selected reader; it supplies cost arithmetic rather than exact weight reproduction.

Owner continuation jobs are active during this draft. Partial cell artifacts are deliberately excluded from the completed-results tables; no treatment result, final checkpoint or superiority is admitted here. Matrix v3 adds two S1 conditions, continued base plus the v0-stable C1 cap. Original-base S0 and original-base learned R0 reuse existing cells. Continued-base learned-reader pilot cells remain separate diagnostics.

DEC-040 LS compares every condition with the **original** base. The new unseen endpoint instead compares a cap against the cap-off base of that same condition to measure cap-induced change; original-base drift remains separate. Final analysis must preserve both references.

The current primary stream driver supplies no ordinary-text drift windows: its saved full-drift metrics are `unsupported`. Its base-hash-before/after fields are also null, although it asserts reusable cap weights unchanged and the audited base is structurally fixed. Fixed base weights alone do not establish that cap-on generation preserves ordinary language behavior. The active continuation recipes include development-sized fidelity/drift probes, which do not substitute for the required full declared validation assay. Thus plan 9's complete Stage 2 fidelity/Stage 4 admission gate remains open.

## 7. Fresh data, scope and timing

[R1-D2](tasks/R1-D2.md) produces an ordered candidate inventory without a new confirmatory draw or seal:

| CounterFact filter | Remaining items |
| --- | ---: |
| Historical eligible source | 20,091 |
| Remove 3,000 historical realization reservations | 17,091 |
| Remove 950 other v1 exposures | 16,141 |
| Remove 3,000 DEC-037 training items | 13,141 |
| Apply remaining v3 canonical exposure reasons, conditional on an old-CounterFact-pool exception | **12,246** |
| Strict current v3, with no exception | **0** |

The extra 895 exclusions retain context quarantine and cross-dataset exposure reasons. The exception is only a proposal to waive `old_eligible:counterfact`; every other reason stays active. Historical reservation identities were reconstructed from the old recipe and checked against all 15 public order digests; historical realization payloads were not opened. Every conditional candidate has source/prepared/prompt/record hashes, and the full ordered data resource lives in assets. No separate fresh CounterFact archive exists in the inspected local raw-data directory. The lead must choose a documented remainder exception or another reviewed source; 12,246 is a conditional ceiling before remaining context/alias review, not a certificate of eligibility.

The zsRE pre-context remainder is 52,498 after reserving all 6,000 training-filter candidates, but final teacher eligibility, context/alias exclusions and outside/challenge reservations still need completion. No old sealed subject is silently reused as fresh evidence.

[Matrix v3](../manifests/revision_v1/run_matrix_draft_v3.json) has eight conditions × two datasets × three realizations × five orders = **240 evaluation cells**, 1,000 edits each, checkpoints 100/300/1,000. Sixty cells are the two S1 continuation additions. These are proposed evaluation axes, not completed experiments. All launches are disabled and all expanded time ceilings are null.

Legacy endpoint proxies sum to 802,440 seconds (222.9 h), including the old 20% reserve convention: 538,920 seconds for the prior 180 cells and 263,520 borrowed stable-control seconds for S1. They are neither measured lower bounds nor approved new limits. The added unseen endpoint alone implies 72,000 prompt pairs / 144,000 decodes, unpriced in those proxies. The approximately 15-hour confirmatory envelope is 54,000 seconds. This discrepancy requires profiling and an explicit scope/budget decision; it cannot be resolved by presenting the old rates as measured expanded costs.

Plan 9 schedules Stage 2 for relative days 8–18 and Stage 4 for days 20–28. The diagnosis and recovery occurred over September 13–14, but no valid claim of calendar lateness or remaining GPU allocation follows without a reconciled start/budget ledger. The primary summary records 286.851 seconds of training wall time, 23.881 seconds in its bank setup span and 355.472 seconds total; the notes' “2 min” shorthand is not the measured primary training span. R1-X4's earlier 14.635-hour subtotal covers 12 training wall spans and is neither a current complete project spend nor physical GPU occupancy. Reused banks, overlapping work and older instrumentation limit budget inference.

## 8. Artifact quality, repairs and limitations

The new [source-bound recount](../logs/r1_round7/stage2_report_evidence.json) inventories **100 stream summaries**: 84 have matching dataset-specific detail directories and all four checked metrics reconcile; eight zsRE summaries point to overwritten CounterFact details; eight CounterFact summaries lack their correctly suffixed detail path. The latter historically used the colliding unsuffixed directories, so “missing” means missing at the proper run identity, not necessarily destroyed CounterFact payloads. No mismatched details were reassigned or used to compute a zsRE result.

The eight historical stems are `random_tied_cos_min0.93`, `tiedcos_delta5_null0.5`, `pairnull_delta5_null0.5`, `pairnull_delta5_gate0.93`, `pairnull_delta5_gate0.93_bin`, `pairown_delta5_null0.5`, `pairown_delta5_null0.3`, and `pairown_delta5_null0.15`. Their published summaries are retained as historical evidence; they cannot support reconstructed paired intervals from the collided files. The selected random reference was regenerated as `ref_nonlearned_gate0.93_v2` under dataset-specific identities, and these clean rows are used in §4.

The [round-7 repair audit](../logs/audit_r1_28b.md) verifies the reference weight/pool/stop-list hashes and reproduces repaired logical fast-training charges on a real tiny differentiated episode: six full forwards, six reverses, 331 forward-token positions. Default mixed own/paraphrase/locality coverage now includes both domains in all 512 tested synthetic episodes. The weight-directory overwrite guard is repaired.

Important open items remain:

- Cache metadata does not bind all paraphrase/locality/subject inputs or independently checksum serialized features. Migration compares a content expression with itself; altered cached prompts/features can pass parts of verification. Recorded identity must not be mistaken for proven construction provenance.
- Undersized pools can yield no outside queries without refusal. Outside-domain coverage still fails in two of 512 default synthetic seeds. Appending missing-domain query triples also changes per-episode weights. These are admission/coverage issues, not evidence that the selected actual bank was corrupted.
- Training/deployment candidate support, write semantics and prefix reductions differ. Memory size can alter calibration even when a balanced episode loss looks good.
- The original profiles omit some source/configuration/denominator identities and do not use paired query inventories across the top-k/m256 alternatives. The new audit supplies additive identities for its reproduction, without changing owner scripts.
- Historical wall times, logical forward/reverse counts and accelerator costs have different scopes. Repaired accounting does not retroactively make old runs compute-matched.
- Development selection, short answers, reused subjects, limited locality prompts, incomplete ordinary-text drift and absent 1,000-edit generation results limit scientific generalization. The original v0 negative conclusion remains intact.

## 9. What Stage 4 must establish, and practical next work

| Priority / checkpoint | Work | Completion evidence / owner |
| --- | --- | --- |
| 1 — current execution | Finish both DEC-040 treatments and admit exact output/configuration hashes; distinguish failed/partial/completed cells | Completed summaries, fidelity and drift coverage, cost reconciliation; orchestrator GPU lane |
| 1 — reproducible inputs | Complete cache identity and migration/rebuild policy; enforce unique facts, valid disjoint splits, sufficient outside counts and actual role coverage | CPU adversarial admission tests plus immutable bank manifest; owner source changes |
| 1 — full endpoint integration | Wire R1-44 and active-record/byte diagnostics into all comparator drivers, with actual memory/firing adapters and common query resets | Tiny-base parity controls, generation traces, missing/truncation accounting; owner source changes |
| 1 — data decision | Decide CounterFact remainder exception/source; finish zsRE E.2 and context/alias exclusions; reserve disjoint edit/unseen/challenge IDs | Versioned admitted inventories before draw/seal; lead + data/GPU owner |
| 2 — P1/P2 | Profile edits/memory and full endpoints across all eight conditions and both datasets | Cold/warm times, logical calls, memory/answer-length buckets; leased GPU profiles |
| 2 — P3 | Paired 100/300/1,000 active-record selection and unseen generation, enough real distinct outside facts | Same IDs across alternatives, all denominators, complete answer/cap-off costs |
| 2 — P4 | Profile continuation training/fidelity and full 1,000-edit S1 evaluations, charging shared training once | Admitted checkpoints, measured components, full validation scope |
| 2 — protocol decision | Reconcile expanded scope with time/byte ceilings, freeze sample sizes, references, margins, stopping and missingness rules | Explicit lead budget/scope decision; no launch from the draft |
| 3 — comparative inference | Fresh streams paired by item/order, clustered by realization; retain failed acquisitions and missing endpoints | RET-GS margin +0.05, ES loss ≤0.02, LS loss ≤0.01 under the approved contrasts; three-cluster intervals labelled preliminary |
| Conditional — Stage 3 | If pursued, test target-free cap-level settling against the same zero-step cap and compute-matched recurrent control | Invariance/residual/answer gates and explicit objective; not required to claim the present feedforward result |

Before another broad architecture sweep, measure the new outside-answer endpoint: gate acceptance can leave an answer unchanged. For the CounterFact failure, pair top-k variants on identical memories/queries and separate candidate misses from selection errors. A support-subject overlap signal, explicit hard negatives from absent same-relation facts, or a deployment-matched null objective are reasonable **proposed ablations**, each requiring a new identity and held-out development policy. No such source change is applied by this report.

CPU cache/admission repairs, comparator adapters and analysis preparation can proceed while the orchestrator's continuation jobs occupy the GPU, under the existing ownership/edit-permission rules. Fresh-pool decisions can proceed independently of model training. Full profiles and fresh inference depend on admitted populations and completed endpoints. Optional cap-level PC should not displace these checks of the now-working primary.

## 10. Reproduction and disposition

This round used CPU/JAX TinyBase only; real-base queries, teacher execution and GPU time by Codex were zero. No existing file was edited. Source identities and completed stream aggregates can be reproduced into a **new** output path with:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m scripts.r1_47_evidence --output logs/<new-stage2-evidence>.json
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  python -m scripts.r1_x6_audit --output logs/<new-scale-audit>.json
```

Use the project venv. The [Stage 2 recount log](../logs/r1_round7/stage2_recount_cpu.txt), [scale audit log](../logs/r1_round7/x6_audit_cpu.txt), [endpoint CPU test log](../logs/r1_round7/unseen_endpoint_cpu.txt), and [candidate/matrix test log](../logs/r1_round7/candidates_matrix_cpu.txt) retain the checks. The new tests pass **10 + 18 cases**, including real TinyBase reads and artifact/admission refusal cases.

Disposition: the learned feedforward package is ready for the next measured development/admission checks. The complete Stage 2 fidelity review and the lead's revision freeze are still pending. This is an additive draft for review, not an authorization to edit owner files, launch confirmation, choose a fresh-data exception or promote an unfinished continuation checkpoint.
