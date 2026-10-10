# Frozen GPT-2, ePC-trained reader cap and BP-trained reader cap on zsRE, CounterFact and MQuAKE: ordinary performance, dataset extremes and heavy tails

Study `ext-20261009` · Capstan · 2026-10-10 · pc_cap code revision `507504c8cae8` · commissioned by `docs/AgentHandoffForResearchInTheExtremes.md` as amended by `docs/mandatory_ammendment.md`.

Provenance tags: **[record]** previously established in the frozen record and copied with its hashes; **[recomputed]** recomputed in this study from saved data; **[new]** newly evaluated in this study (own manifest `results/extremes_analysis/ext-20261009/manifest.json`). The frozen record was not modified.

## 1. Abstract and executive summary

**Question.** Across zsRE, CounterFact and MQuAKE, how do (i) frozen GPT-2 small without a cap, (ii) GPT-2 with the reader cap trained by error predictive coding (ePC) and (iii) GPT-2 with the same cap trained by backprop (BP) compare in ordinary benchmark performance, prediction difficulty, heavy-tail behaviour, extreme losses, adaptation benefit, correction magnitude, locality and stability — and does the ePC-trained cap show advantages in rare or extreme cases that survive a direct comparison with the BP-trained cap?

**Design.** The principal comparison is the frozen record's PC-reader study (family PCR): three paired training seeds per rule, identical architecture (3,348,228 reader parameters, taps and writes at blocks 4/8/12), identical initial parameters and training episodes within seed, adjoint acquisition in both arms, evaluated on realization 0 / order 100 with 300 edits on zsRE and CounterFact (checkpoints 100 and 300). This study adds **[new]**: a directly loaded frozen GPT-2 scored on exactly the same probes; teacher-forced target log-probabilities for all seven models on every probe (edit prompts, paraphrases, locality, near-miss, revision, unseen, MQuAKE multi-hop questions); the six saved readers evaluated on the sealed MQuAKE stream (6/6 complete at report time); write-vector magnitudes at every scored position; dataset frequency/entropy/shift statistics; and finite-range tail fits that start from a field-by-field reproduction of HT-17.

**Headline findings.**

- **zsre, paraphrase retention at 300 edits:** BP 97.3 %, 99.0 %, 97.7 %; ePC 94.7 %, 97.0 %, 98.0 % (seeds 0, 1, 2; 300 items each). Frozen: 0.0 %.
- **zsre, paraphrase per-token loss gain over frozen (seed mean):** BP 5.972 [5.708, 6.217]; ePC 5.895 [5.621, 6.146]; ePC − BP contrast -0.076 [-0.136, -0.027] nats/token (positive favours ePC).
- **counterfact, paraphrase retention at 300 edits:** BP 81.0 %, 80.0 %, 83.5 %; ePC 56.8 %, 77.8 %, 66.0 % (seeds 0, 1, 2; 300 items each). Frozen: 0.0 %.
- **counterfact, paraphrase per-token loss gain over frozen (seed mean):** BP 6.057 [5.807, 6.309]; ePC 4.941 [4.648, 5.228]; ePC − BP contrast -1.117 [-1.313, -0.916] nats/token (positive favours ePC).
- **mquake, paraphrase retention at 300 edits:** BP 62.3 %, 72.3 %, 67.7 %; ePC 60.0 %, 60.3 %, 58.3 % (seeds 0, 1, 2; 300 items each). Frozen: 0.0 %.
- **mquake, paraphrase per-token loss gain over frozen (seed mean):** BP 4.456 [4.193, 4.708]; ePC 3.961 [3.633, 4.261]; ePC − BP contrast -0.495 [-0.651, -0.347] nats/token (positive favours ePC).
- **Neither cap beats the frozen model everywhere.** Both caps convert the taught facts (own-prompt loss falls from ≈ 6 nats/token to ≈ 0.01) and both leave the frozen model's behaviour unchanged where they abstain; the differences between ePC- and BP-trained readers are differences of *gating*: which paraphrases and un-taught prompts trigger a write. Where a reader abstains, its loss equals the frozen loss to the bit.
- **ePC vs BP.** On CounterFact (frozen record) and on MQuAKE (this study's six supplemental evaluations) the ePC-trained reader retains fewer paraphrases than the BP-trained reader in all three seeds, and its per-probe paraphrase loss is higher in the paired contrast; on zsRE the two rules are close, with the seed-mean contrast slightly favouring BP and mixed per-seed signs. No analysis in this study (difficulty deciles, frozen-hard subsets, regressions, correction magnitudes) finds a regime of rare or extreme cases where the ePC-trained reader is reliably better than the BP-trained reader. Training cost remains 96–102× **[record]**.
- **Extremes.** Frozen difficulty is large in the descriptive sense (per-token target surprisal has P99 above 10 nats on every dataset), but it is not heavy-tailed in the fitted sense: at a common absolute threshold (the frozen model's P95 of the pooled probe surprisal, same cases for every model) the generalized-Pareto shapes are: 21 fits, shapes -0.41 to 0.19; 4 intervals entirely below zero, 17 include zero, 0 entirely above zero; at each model's own P95 they are: 21 fits, shapes -0.41 to 0.34; 4 intervals entirely below zero, 11 include zero, 6 entirely above zero (mquake BP reader s0, mquake BP reader s1, mquake BP reader s2, mquake ePC reader s0, mquake ePC reader s1, mquake ePC reader s2) — the own-quantile positives arise because a cap that drives many losses to zero lowers its own P95 into the frozen body, not because its extremes are heavier. The ordinary-text harm tails of the PC-reader cells reproduce HT-17 exactly (12/12 fields) and remain finite-range fits. Rare large per-probe deteriorations exist for both caps and occur almost only where a record fired (joint-extremes tail lift 14–62 on zsRE).
- **Qualifications.** One subject realization and one order; three training seeds are not three populations; GPT-2 small only; the frozen model answers essentially none of these prompts under the project's greedy convention, so the frozen baseline is informative through teacher-forced losses, not through exact-match rates.

## 2. Research questions and architectures

The cap is an episodic memory with a learned reader attached to a frozen GPT-2 small (12 blocks, 124,439,808 parameters, params digest `c4ac3fb8…`). Reads tap the residual stream after blocks 4, 8 and 12; writes add one vector per site at the current prediction position. Each edit is taught by five adjoint delta steps (lr 0.1, acceptance τ 0.1, aggregate budget A = 0.3) and appended as a record (key = prompt embedding at the three taps; payload = per-answer-token write deltas [3, 768]). At query time the reader scores the prompt against the nearest stored keys and keeps a null option; null mass ≥ 0.5 means no write, so the output equals the base to the bit. There is no inference-time iteration in either cap; the eight settling steps of ePC are a *training-time* quantity.

| model | what differs | checkpoint | where evaluated |
|---|---|---|---|
| frozen GPT-2 small **[new]** | no reader, no memory, no writes | base params only | all probes, all datasets (Stage 2) |
| BP reader, seeds 0–2 **[record]** | reader trained by backprop (300 AdamW updates; feedforward answer CE, cached float16 teacher) | `train-bp-s*/theta_avg150-300.npz` | zsRE/CounterFact (record); MQuAKE (this study) |
| ePC reader, seeds 0–2 **[record]** | same episodes and initial parameters; base-dependent gradients from `EPCTrainer` (8 zero-initialised settling steps, rate 0.1, corrected SD-24 energy); 23.4–24.6 h vs 0.24–0.25 h | `train-epc-s*/theta_avg150-300.npz` | same |

Verified differences between the two caps (handoff §1): architecture, parameter count, interface, acquisition rule, evaluation population and scoring code are identical; only the training-time gradient estimator for the base-dependent losses differs (settled ePC CE vs feedforward CE; float32 vs cached float16 teacher), hence the weights and the cost. The validation record `validation/gpu_checks.json` confirms: the directly loaded weights have the record's digest; a direct forward reproduces the saved cap-off losses to 0.000050 nats over 1524 positions; a reader with an empty memory, and a loaded memory on prompts where it abstains, returns the base logits exactly; the residual insertion arithmetic h_after = h_before + Δh holds at the site; saved RET-GS/RET-ES recompute exactly from the saved rows.

Families kept distinct and reported separately: Stage-4 `R1_learned_ff` (selected v5 BP-trained reader, 1,000 edits, 3 realizations × 5 orders) **[record]**; fixed-v5 acquisition credit (adjoint vs error inference, reader fixed) **[record]**; PC-v0 (regenerated ePC 50M base, v0 live cap) **[record, supplementary only]**.

## 3. Datasets and evaluation methodology

| dataset | version used | pool | principal stream | probes per item | notes |
|---|---|---|---|---|---|
| zsRE | MEND release, train split rows; `zsre_eligible.jsonl` (10,420 eligible of 10,720 screened; 0 answered by the base) | 10,420 | realization 0, order 100, first 300 of 1,000 | 1 paraphrase, 1 NQ locality prompt | no relation ids; target = first `answers[]` entry |
| CounterFact | original CounterFact; `counterfact_eligible.jsonl` (20,091 of 20,391; 0 answered by the base) | 20,091 | same | 2 paraphrases, ~10 neighbourhood prompts (first 3 scored) | `target_true` retained; relation ids |
| MQuAKE | **MQuAKE-CF** (9,218 cases; DEC-045); single-hop rewrite items + 80 composition cases per realization | 6,043 items | 300 items | 1 question-form paraphrase, 2 locality prompts | `target_true`/`target_new` with QIDs; 3 multi-hop questions per case |

Endpoint bundles per realization: 50 locality prompts, 100 near-miss pairs (distinct subjects within matched relation/template families; the reference is the cell's own cap-off neighbour response), 50 revision cases, 100 unseen prompts (un-taught pool items; false-fire measurement), and for MQuAKE 80 composition cases. Original metrics **[record]**: ES (immediate own-prompt success), RET-ES/RET-GS (end-of-stream own-prompt / paraphrase retention), LS (DEC-053 bounded exact decoded-text equality with the original-base response; *not* factual accuracy), near-miss preservation, revision, unseen false fires. Decoding: greedy, ≤ 32 new tokens, stop at newline/EOS; exact match of the NFKC/casefold/whitespace-normalised generation against supplied aliases.

Standardised measurements **[new]**: for prompt x_i and answer tokens y_i,1..T_i (the project's tokenisation: leading space, newline terminator), logP_i = Σ_t log p(y_i,t | x_i, y_i,<t) under teacher forcing with one prediction per gold prefix (the cap's writes act at every prediction position, exactly as the record's diagnostic); NLL_total_i = −logP_i; NLL_token_i = NLL_total_i / T_i (primary continuous difficulty measure); totals without the terminator are retained. Margins margin_total = logP(target_new) − logP(target_true) and margin_token = −NLL_token(new) + NLL_token(true). All seven models score the same serialised prompt/answer pairs; identical bucket padding; float64 log-softmax of float32 logits. Reader selection (record ids, null mass, hard null) and write norms ‖W_m‖ and ‖W_m‖/‖h_m‖ are recorded at every scored position. Probe counts: zsRE 1,350, CounterFact 2,300 (item-locality capped at 3 per item), MQuAKE 1,890 (incl. 240 composition questions).

Uncertainty: 2,000-draw percentile bootstrap resampling whole groups (items for item-level families, endpoint rows otherwise) with the same indices for every model (pairing preserved); windows for ordinary text; seeds reported individually and as a descriptive seed mean. These intervals cover within-population sampling only; no interval here speaks to new subjects or new training seeds.

## 4. Basic benchmark results

### 4.1 Registered metrics (original conventions, numerators/denominators)

### zsre

| edits | model | ES | RET-ES | RET-GS (primary) | LS | near-miss | unseen false fires | MQuAKE composition (all 3 questions) |
|---|---|---|---|---|---|---|---|---|
| 300 | frozen GPT-2 [new] | 0.0 % (0/300) | 0.0 % (0/300) | 0.0 % (0/300) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A |  |
| 300 | BP reader s0 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 97.3 % (292/300) | 100.0 % (50/50) | 85.0 % (85/100) | 4/100 |  |
| 300 | BP reader s1 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 99.0 % (297/300) | 100.0 % (50/50) | 67.0 % (67/100) | 14/100 |  |
| 300 | BP reader s2 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 97.7 % (293/300) | 100.0 % (50/50) | 73.0 % (73/100) | 11/100 |  |
| 300 | ePC reader s0 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 94.7 % (284/300) | 100.0 % (50/50) | 91.0 % (91/100) | 2/100 |  |
| 300 | ePC reader s1 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 97.0 % (291/300) | 100.0 % (50/50) | 85.0 % (85/100) | 5/100 |  |
| 300 | ePC reader s2 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 98.0 % (294/300) | 100.0 % (50/50) | 85.0 % (85/100) | 4/100 |  |
| 100 | frozen GPT-2 [new] | 0.0 % (0/100) | 0.0 % (0/100) | 0.0 % (0/100) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A |  |
| 100 | BP reader s0 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 96.0 % (96/100) | 100.0 % (50/50) | 80.0 % (80/100) | 5/100 |  |
| 100 | BP reader s1 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 99.0 % (99/100) | 100.0 % (50/50) | 56.0 % (56/100) | 13/100 |  |
| 100 | BP reader s2 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 96.0 % (96/100) | 100.0 % (50/50) | 66.0 % (66/100) | 8/100 |  |
| 100 | ePC reader s0 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 92.0 % (92/100) | 100.0 % (50/50) | 88.0 % (88/100) | 2/100 |  |
| 100 | ePC reader s1 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 92.0 % (92/100) | 100.0 % (50/50) | 80.0 % (80/100) | 5/100 |  |
| 100 | ePC reader s2 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 95.0 % (95/100) | 100.0 % (50/50) | 82.0 % (82/100) | 4/100 |  |

### counterfact

| edits | model | ES | RET-ES | RET-GS (primary) | LS | near-miss | unseen false fires | MQuAKE composition (all 3 questions) |
|---|---|---|---|---|---|---|---|---|
| 300 | frozen GPT-2 [new] | 0.0 % (0/300) | 0.0 % (0/300) | 0.0 % (0/300) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A |  |
| 300 | BP reader s0 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 81.0 % (243/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 300 | BP reader s1 [record] | 99.0 % (297/300) | 99.0 % (297/300) | 80.0 % (240/300) | 100.0 % (50/50) | 99.0 % (99/100) | 1/100 |  |
| 300 | BP reader s2 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 83.5 % (250.5/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 300 | ePC reader s0 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 56.8 % (170.5/300) | 100.0 % (50/50) | 98.0 % (98/100) | 0/100 |  |
| 300 | ePC reader s1 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 77.8 % (233.5/300) | 100.0 % (50/50) | 95.0 % (95/100) | 1/100 |  |
| 300 | ePC reader s2 [record] | 100.0 % (300/300) | 100.0 % (300/300) | 66.0 % (198/300) | 100.0 % (50/50) | 99.0 % (99/100) | 0/100 |  |
| 100 | frozen GPT-2 [new] | 0.0 % (0/100) | 0.0 % (0/100) | 0.0 % (0/100) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A |  |
| 100 | BP reader s0 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 85.0 % (85/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | BP reader s1 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 85.0 % (85/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | BP reader s2 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 86.5 % (86.5/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | ePC reader s0 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 56.0 % (56/100) | 100.0 % (50/50) | 99.0 % (99/100) | 0/100 |  |
| 100 | ePC reader s1 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 77.5 % (77.5/100) | 100.0 % (50/50) | 96.0 % (96/100) | 0/100 |  |
| 100 | ePC reader s2 [record] | 100.0 % (100/100) | 100.0 % (100/100) | 68.0 % (68/100) | 100.0 % (50/50) | 99.0 % (99/100) | 0/100 |  |

### mquake

| edits | model | ES | RET-ES | RET-GS (primary) | LS | near-miss | unseen false fires | MQuAKE composition (all 3 questions) |
|---|---|---|---|---|---|---|---|---|
| 300 | frozen GPT-2 [new] | 0.0 % (0/300) | 0.0 % (0/300) | 0.0 % (0/300) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A | question-level new-answer exact 0.0 %; old-answer exact 0.0 % (N/A as all-question success: no edits) |
| 300 | BP reader s0 [new] | 100.0 % (300/300) | 100.0 % (300/300) | 62.3 % (187/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 300 | BP reader s1 [new] | 91.0 % (273/300) | 94.0 % (282/300) | 72.3 % (217/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 300 | BP reader s2 [new] | 100.0 % (300/300) | 100.0 % (300/300) | 67.7 % (203/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 300 | ePC reader s0 [new] | 100.0 % (300/300) | 100.0 % (300/300) | 60.0 % (180/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 300 | ePC reader s1 [new] | 100.0 % (300/300) | 100.0 % (300/300) | 60.3 % (181/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 300 | ePC reader s2 [new] | 100.0 % (300/300) | 100.0 % (300/300) | 58.3 % (175/300) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 | 0.0 % (0/80) |
| 100 | frozen GPT-2 [new] | 0.0 % (0/100) | 0.0 % (0/100) | 0.0 % (0/100) | 100.0 % (50/50) (by definition) | 100.0 % (100/100) (by definition) | N/A | question-level new-answer exact 0.0 %; old-answer exact 0.0 % (N/A as all-question success: no edits) |
| 100 | BP reader s0 [new] | 100.0 % (100/100) | 100.0 % (100/100) | 62.0 % (62/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | BP reader s1 [new] | 86.0 % (86/100) | 90.0 % (90/100) | 68.0 % (68/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | BP reader s2 [new] | 100.0 % (100/100) | 100.0 % (100/100) | 62.0 % (62/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | ePC reader s0 [new] | 100.0 % (100/100) | 100.0 % (100/100) | 56.0 % (56/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | ePC reader s1 [new] | 100.0 % (100/100) | 100.0 % (100/100) | 53.0 % (53/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |
| 100 | ePC reader s2 [new] | 100.0 % (100/100) | 100.0 % (100/100) | 51.0 % (51/100) | 100.0 % (50/50) | 100.0 % (100/100) | 0/100 |  |

Reading: the frozen model's ES/RET-ES/RET-GS are its greedy answers against the taught aliases — zero by the eligibility screen (every item was selected because the base did *not* answer it), and zero on paraphrases as well; its LS and near-miss are 1 by definition because its response *is* the reference. The caps reach own-prompt retention of 99–100 % and differ on paraphrases, near-miss preservation and false fires.

### 4.2 Standardised per-token losses (nats/token; mean over probes; 300-edit memories; frozen has no memory)

| dataset | family | target | frozen | BP s0 | BP s1 | BP s2 | ePC s0 | ePC s1 | ePC s2 |
|---|---|---|---|---|---|---|---|---|---|
| zsre | edit | new | 6.009 (n=300) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) |
| zsre | paraphrase | new | 6.098 (n=300) | 0.161 (n=300, fire 98 %) | 0.077 (n=300, fire 99 %) | 0.142 (n=300, fire 98 %) | 0.320 (n=300, fire 95 %) | 0.168 (n=300, fire 97 %) | 0.120 (n=300, fire 98 %) |
| zsre | locality_item | true | 6.223 (n=296) | 6.223 (n=296, fire 0 %) | 6.223 (n=296, fire 0 %) | 6.223 (n=296, fire 0 %) | 6.223 (n=296, fire 0 %) | 6.223 (n=296, fire 0 %) | 6.223 (n=296, fire 0 %) |
| zsre | near_miss_neighbour | true | 5.974 (n=100) | 6.192 (n=100, fire 8 %) | 6.161 (n=100, fire 21 %) | 6.141 (n=100, fire 16 %) | 6.048 (n=100, fire 3 %) | 6.147 (n=100, fire 8 %) | 6.106 (n=100, fire 7 %) |
| zsre | unseen | new | 6.128 (n=100) | 6.229 (n=100, fire 4 %) | 6.209 (n=100, fire 14 %) | 6.281 (n=100, fire 11 %) | 6.209 (n=100, fire 2 %) | 6.328 (n=100, fire 5 %) | 6.289 (n=100, fire 4 %) |
| counterfact | edit | new | 6.956 (n=300) | 0.019 (n=300, fire 100 %) | 0.100 (n=300, fire 99 %) | 0.019 (n=300, fire 100 %) | 0.019 (n=300, fire 100 %) | 0.019 (n=300, fire 100 %) | 0.019 (n=300, fire 100 %) |
| counterfact | paraphrase | new | 7.369 (n=600) | 1.362 (n=600, fire 86 %) | 1.449 (n=600, fire 84 %) | 1.125 (n=600, fire 88 %) | 3.183 (n=600, fire 59 %) | 1.598 (n=600, fire 81 %) | 2.504 (n=600, fire 68 %) |
| counterfact | locality_item | true | 6.295 (n=900) | 6.288 (n=900, fire 0 %) | 6.287 (n=900, fire 0 %) | 6.292 (n=900, fire 0 %) | 6.269 (n=900, fire 1 %) | 6.272 (n=900, fire 2 %) | 6.288 (n=900, fire 0 %) |
| counterfact | near_miss_neighbour | true | 7.167 (n=100) | 7.167 (n=100, fire 0 %) | 7.148 (n=100, fire 1 %) | 7.167 (n=100, fire 0 %) | 7.110 (n=100, fire 2 %) | 7.091 (n=100, fire 5 %) | 7.157 (n=100, fire 1 %) |
| counterfact | unseen | new | 6.924 (n=100) | 6.924 (n=100, fire 0 %) | 6.920 (n=100, fire 1 %) | 6.924 (n=100, fire 0 %) | 6.924 (n=100, fire 0 %) | 6.920 (n=100, fire 1 %) | 6.924 (n=100, fire 0 %) |
| counterfact | edit | true | 6.382 (n=300) | 5.215 (n=300, fire 100 %) | 5.237 (n=300, fire 99 %) | 5.215 (n=300, fire 100 %) | 5.215 (n=300, fire 100 %) | 5.215 (n=300, fire 100 %) | 5.215 (n=300, fire 100 %) |
| mquake | edit | new | 5.171 (n=300) | 0.015 (n=300, fire 100 %) | 0.342 (n=300, fire 94 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) | 0.015 (n=300, fire 100 %) |
| mquake | paraphrase | new | 6.048 (n=300) | 2.009 (n=300, fire 72 %) | 1.276 (n=300, fire 86 %) | 1.491 (n=300, fire 83 %) | 2.099 (n=300, fire 71 %) | 1.994 (n=300, fire 72 %) | 2.168 (n=300, fire 69 %) |
| mquake | locality_item | true | 4.487 (n=600) | 4.722 (n=600, fire 7 %) | 4.733 (n=600, fire 7 %) | 4.737 (n=600, fire 8 %) | 4.729 (n=600, fire 7 %) | 4.746 (n=600, fire 8 %) | 4.739 (n=600, fire 8 %) |
| mquake | near_miss_neighbour | true | 5.204 (n=100) | 5.204 (n=100, fire 0 %) | 5.204 (n=100, fire 0 %) | 5.204 (n=100, fire 0 %) | 5.204 (n=100, fire 0 %) | 5.204 (n=100, fire 0 %) | 5.204 (n=100, fire 0 %) |
| mquake | unseen | new | 5.284 (n=100) | 5.284 (n=100, fire 0 %) | 5.284 (n=100, fire 0 %) | 5.284 (n=100, fire 0 %) | 5.284 (n=100, fire 0 %) | 5.284 (n=100, fire 0 %) | 5.284 (n=100, fire 0 %) |
| mquake | edit | true | 4.579 (n=300) | 8.010 (n=300, fire 100 %) | 7.804 (n=300, fire 94 %) | 8.010 (n=300, fire 100 %) | 8.010 (n=300, fire 100 %) | 8.010 (n=300, fire 100 %) | 8.010 (n=300, fire 100 %) |
| mquake | composition | new | 6.611 (n=240) | 6.749 (n=240, fire 22 %) | 6.813 (n=240, fire 43 %) | 6.886 (n=240, fire 37 %) | 6.746 (n=240, fire 19 %) | 6.703 (n=240, fire 18 %) | 6.716 (n=240, fire 20 %) |
| mquake | composition | old | 5.489 (n=240) | 5.770 (n=240, fire 22 %) | 6.115 (n=240, fire 43 %) | 6.037 (n=240, fire 37 %) | 5.762 (n=240, fire 19 %) | 5.700 (n=240, fire 18 %) | 5.710 (n=240, fire 20 %) |

### 4.3 Counterfactual preference (probes with both `target_new` and `target_true`)

| dataset | family | model | n | mean margin_total (nats) | P(margin_total > 0) | mean margin_token | P(margin_token > 0) |
|---|---|---|---|---|---|---|---|
| counterfact | edit | BP reader s0 | 300 | 10.392 | 100.0 % | 5.196 | 100.0 % |
| counterfact | edit | BP reader s1 | 300 | 10.274 | 99.0 % | 5.137 | 99.0 % |
| counterfact | edit | BP reader s2 | 300 | 10.392 | 100.0 % | 5.196 | 100.0 % |
| counterfact | edit | ePC reader s0 | 300 | 10.392 | 100.0 % | 5.196 | 100.0 % |
| counterfact | edit | ePC reader s1 | 300 | 10.392 | 100.0 % | 5.196 | 100.0 % |
| counterfact | edit | ePC reader s2 | 300 | 10.392 | 100.0 % | 5.196 | 100.0 % |
| counterfact | edit | frozen GPT-2 | 300 | -1.149 | 30.3 % | -0.574 | 30.3 % |
| counterfact | paraphrase | BP reader s0 | 600 | 7.264 | 86.7 % | 3.632 | 86.7 % |
| counterfact | paraphrase | BP reader s1 | 600 | 7.122 | 85.2 % | 3.561 | 85.2 % |
| counterfact | paraphrase | BP reader s2 | 600 | 7.532 | 88.3 % | 3.766 | 88.3 % |
| counterfact | paraphrase | ePC reader s0 | 600 | 4.716 | 69.3 % | 2.358 | 69.3 % |
| counterfact | paraphrase | ePC reader s1 | 600 | 6.930 | 84.3 % | 3.465 | 84.3 % |
| counterfact | paraphrase | ePC reader s2 | 600 | 5.644 | 73.8 % | 2.822 | 73.8 % |
| counterfact | paraphrase | frozen GPT-2 | 600 | -1.146 | 31.2 % | -0.573 | 31.2 % |
| mquake | edit | BP reader s0 | 300 | 26.443 | 100.0 % | 7.995 | 100.0 % |
| mquake | edit | BP reader s1 | 300 | 24.032 | 95.7 % | 7.462 | 96.3 % |
| mquake | edit | BP reader s2 | 300 | 26.443 | 100.0 % | 7.995 | 100.0 % |
| mquake | edit | ePC reader s0 | 300 | 26.443 | 100.0 % | 7.995 | 100.0 % |
| mquake | edit | ePC reader s1 | 300 | 26.443 | 100.0 % | 7.995 | 100.0 % |
| mquake | edit | ePC reader s2 | 300 | 26.443 | 100.0 % | 7.995 | 100.0 % |
| mquake | edit | frozen GPT-2 | 300 | -2.467 | 36.0 % | -0.592 | 45.0 % |
| mquake | paraphrase | BP reader s0 | 300 | 13.817 | 78.7 % | 4.328 | 82.7 % |
| mquake | paraphrase | BP reader s1 | 300 | 17.112 | 90.0 % | 5.224 | 91.0 % |
| mquake | paraphrase | BP reader s2 | 300 | 17.072 | 86.3 % | 5.078 | 87.3 % |
| mquake | paraphrase | ePC reader s0 | 300 | 14.359 | 77.3 % | 4.303 | 80.0 % |
| mquake | paraphrase | ePC reader s1 | 300 | 14.491 | 79.0 % | 4.395 | 81.0 % |
| mquake | paraphrase | ePC reader s2 | 300 | 14.063 | 76.3 % | 4.210 | 79.7 % |
| mquake | paraphrase | frozen GPT-2 | 300 | -2.988 | 27.7 % | -0.758 | 37.3 % |

Frozen GPT-2's original-fact performance: the frozen exact rate on `target_true` for CounterFact/MQuAKE edit prompts is in `benchmark_original.csv` (`original_fact_exact_edit`); under the project's newline-stop greedy convention the base almost never emits a complete answer, so the teacher-forced `true`-target loss (table 4.2, family `edit`, target `true`) is the informative measure of what the base knew.

### 4.4 Context from the other families [record]

Stage-4 selected v5 reader (1,000 edits; 300 MQuAKE; three realizations × five orders): final RET-GS 96.03 % zsRE, 67.80 % CounterFact, 71.56 % MQuAKE; all 45 learned-reader cells exceed mean KL 0.001; registered classifier labels unchanged (`docs/R1_stage4_report.md`). Fixed-v5 acquisition credit (realization 0, order 100, 300 edits): paraphrase retention 98.3 %/98.3 % (zsRE adjoint/error) and 80.7 %/80.3 % (CounterFact); error credit raised the single worst ordinary-text token loss (12.27 vs 9.26 nats on zsRE) at ≈ 35 % more acquisition time (`docs/additional_work/PC-v1_report.md`). PC-v0 corrected credit on the **ePC 50M base** (not GPT-2 small): zsRE own-prompt retention +2.0 points, paraphrase −0.3 with mixed signs, CounterFact saturated (`docs/additional_work/PC-v0_report.md`). PC-reader training cost ratios ePC/BP: 102.1, 95.8, 96.7 (seeds 0, 1, 2).

## 5. Statistical characterisation of the datasets [new]

| dataset | population | cases | K relations | H_rel | N_eff rel | K new targets | H_target | N_eff target | singleton targets | top-10 % target share | K subjects | singleton subjects | H(target|rel) | prompt tok med | p99 | answer tok med | p99 | dup prompts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zsre | eligible | 10420 | n/a | n/a | n/a | 5704 | 7.886 | 2660.5 | 44.7 % | 46.2 % | 10420 | 100.0 % | n/a | 11 | 18 | 3 | 10 | 0 |
| zsre | reader_train | 1000 | n/a | n/a | n/a | 799 | 6.471 | 646.4 | 71.8 % | 28.0 % | 1000 | 100.0 % | n/a | 11 | 18 | 3 | 9 | 0 |
| zsre | sealed_r0 | 1000 | n/a | n/a | n/a | 779 | 6.412 | 609.0 | 69.3 % | 29.1 % | 1000 | 100.0 % | n/a | 11 | 18 | 3 | 11 | 0 |
| zsre | pcr_r0_300 | 300 | n/a | n/a | n/a | 262 | 5.470 | 237.5 | 81.3 % | 21.7 % | 300 | 100.0 % | n/a | 11 | 19 | 3 | 11 | 0 |
| counterfact | eligible | 20091 | 34 | 3.409 | 30.2 | 738 | 5.556 | 258.8 | 0.5 % | 58.2 % | 20091 | 100.0 % | 3.016 | 8 | 14 | 2 | 2 | 0 |
| counterfact | reader_train | 1000 | 34 | 3.379 | 29.3 | 288 | 5.140 | 170.7 | 12.4 % | 42.9 % | 1000 | 100.0 % | 2.284 | 8 | 15 | 2 | 2 | 0 |
| counterfact | sealed_r0 | 1000 | 34 | 3.383 | 29.5 | 291 | 5.210 | 183.1 | 12.0 % | 39.1 % | 1000 | 100.0 % | 2.390 | 8 | 15 | 2 | 2 | 0 |
| counterfact | pcr_r0_300 | 300 | 32 | 3.299 | 27.1 | 156 | 4.800 | 121.5 | 30.0 % | 30.3 % | 300 | 100.0 % | 1.825 | 8 | 14 | 2 | 2 | 0 |
| mquake | eligible | 6043 | 37 | 3.074 | 21.6 | 2308 | 6.683 | 798.4 | 27.4 % | 56.6 % | 5577 | 85.8 % | 3.811 | 9 | 16 | 3 | 11 | 0 |
| mquake | reader_train | 500 | 37 | 3.072 | 21.6 | 318 | 5.424 | 226.7 | 51.2 % | 36.8 % | 500 | 100.0 % | 2.453 | 8 | 16 | 3 | 11 | 0 |
| mquake | sealed_r0 | 300 | 34 | 2.928 | 18.7 | 213 | 5.113 | 166.2 | 59.3 % | 32.0 % | 300 | 100.0 % | 2.229 | 9 | 15 | 3 | 9 | 0 |
| mquake | pcr_r0_300 | 300 | 34 | 2.928 | 18.7 | 213 | 5.113 | 166.2 | 59.3 % | 32.0 % | 300 | 100.0 % | 2.229 | 9 | 15 | 3 | 9 | 0 |

Populations: `eligible` (screened pool), `reader_train` (the first 1,000/1,000/500 items of the reader-training pools actually used), `sealed_r0` (the realization-0 stream), `pcr_r0_300` (its first 300 items = the PC-reader horizon). zsRE has no relation labels, so relation entropy is not manufactured. Zipf slopes over ranks 1–100 and all ranks are in `dataset_statistics.json`; a straight log-log segment is not a power-law test. Subject sets are disjoint between reader-training and sealed streams by construction (JS = ln 2 for subjects), so "rare in the benchmark" is a property of the draw, not of the world.

![Rank-frequency of relation, new-target and subject categories in each eligible pool](../../../../../assets/extremes_analysis/ext-20261009/figures/rank_frequency.png)

### 5.1 Train/test shift (reader-training pool vs sealed realization 0)

| dataset | variable (reader-train vs sealed r0) | JS (nats) | KL train‖test (α=0.5) | test categories unseen in train | median train count of test category | test categories with train count ≤ 1 |
|---|---|---|---|---|---|---|
| zsre | target_new | 0.4884 | 0.476 | 68.4 % | None | 77.4 % |
| zsre | subject | 0.6931 | 0.549 | 100.0 % | None | 100.0 % |
| zsre | (subject, relation, target) triple overlap | 0.0000 |  |  |  |  |
| counterfact | relation_id | 0.0064 | 0.025 | 0.0 % | None | 0.0 % |
| counterfact | target_new | 0.1290 | 0.255 | 14.3 % | None | 24.3 % |
| counterfact | target_true | 0.1289 | 0.268 | 15.0 % | None | 24.0 % |
| counterfact | subject | 0.6931 | 0.549 | 100.0 % | None | 100.0 % |
| counterfact | (subject, relation, target) triple overlap | 0.0000 |  |  |  |  |
| mquake | relation_id | 0.0240 | 0.083 | 0.0 % | None | 1.0 % |
| mquake | target_new | 0.4045 | 0.428 | 51.0 % | None | 67.3 % |
| mquake | target_true | 0.3032 | 0.345 | 39.0 % | None | 45.3 % |
| mquake | subject | 0.6931 | 0.481 | 100.0 % | None | 100.0 % |
| mquake | (subject, relation, target) triple overlap | 0.0000 |  |  |  |  |

MQuAKE-CF raw: 9,218 cases; hop counts {'2': 4879, '3': 2535, '4': 1804}; requested edits per case {'1': 3755, '2': 3745, '3': 1282, '4': 436}; 577 distinct relation chains (H = 5.093, N_eff = 162.9); questions per case {'3': 9218}. Sealed r0 composition endpoint: 80 cases, hop counts {'2': 61, '3': 16, '4': 3}, edits per case {'1': 78, '2': 2}.

### 5.2 Baseline surprisal

![Frozen GPT-2 per-token target surprisal on edit prompts](../../../../../assets/extremes_analysis/ext-20261009/figures/frozen_surprisal.png)

Frozen GPT-2 per-token surprisal on the 245,237 ordinary-text positions (loss_capoff of a saved vector; identical in every cell): mean 4.080, median 3.468, P90 8.604, P95 10.129, P99 13.014, max 30.102, CVaR95 11.900 nats.

| quantile | u | excesses | fit | κ | window-bootstrap 95 % κ | σ_u | GPD − exp (nats/excess) |
|---|---|---|---|---|---|---|---|
| 0.900 | 8.60 | 24524 | ok | -0.082 | [-0.100, -0.071] | 2.157 | 0.0053 |
| 0.950 | 10.13 | 12262 | ok | -0.046 | [-0.065, -0.028] | 1.852 | 0.0016 |
| 0.975 | 11.44 | 6131 | ok | -0.004 | [-0.032, 0.022] | 1.637 | 0.0000 |

## 6. Heavy tails and extreme-value statistics

Conventions (amendment §5): harm Δ = NLL(cap) − NLL(reference) at the same prefix on 1,931 windows / 245,237 ordinary-text positions, context reset per window; frequency P(Δ > 0.01), conditional severity, mean signed Δ, positive-part ES99+ including zero mass, maximum, KL(reference‖cap); fits of positive excesses with the record's analyser (`aw/tail_class.py`: ≥ 100 excesses in ≥ 30 windows, 200 joint-window bootstrap draws, five-fold held-out windows). Shapes are finite-range fits.

### 6.1 HT-17 reproduced [recomputed]

The twelve PC-reader cells of HT-17 were re-analysed from the saved vectors with the identical window plan: all twelve agree field by field with the record (`tables/ht17_reproduction_checks.csv`).

| dataset | reader | mean Δ | P(Δ>0.01) | severity | Δ>0.01 | ES99+ | max Δ | GPD fit (u=0.01) | shape ξ | window-bootstrap 95 % ξ | GPD − exp (held-out nats/excess) |
|---|---|---|---|---|---|---|---|---|---|---|
| counterfact | bp s0 | 0.00202 | 0.0926 % | 2.236 | 0.2070 | 8.52 | eligible | -0.237 | [-0.366, -0.110] | 0.0177 |
| counterfact | bp s1 | 0.00535 | 0.2312 % | 2.384 | 0.5513 | 12.50 | eligible | -0.073 | [-0.172, 0.025] | 0.0002 |
| counterfact | bp s2 | 0.00118 | 0.0563 % | 2.146 | 0.1208 | 9.86 | eligible | -0.017 | [-0.196, 0.136] | -0.0025 |
| counterfact | epc s0 | 0.00128 | 0.0661 % | 2.005 | 0.1324 | 7.71 | eligible | -0.262 | [-0.460, -0.187] | -0.0120 |
| counterfact | epc s1 | 0.00628 | 0.2593 % | 2.473 | 0.6413 | 12.36 | eligible | -0.125 | [-0.216, -0.043] | 0.0045 |
| counterfact | epc s2 | 0.00195 | 0.1187 % | 1.737 | 0.2061 | 12.62 | eligible | 0.059 | [-0.083, 0.154] | -0.0028 |
| zsre | bp s0 | 0.00011 | 0.0061 % | 1.913 | 0.0117 | 6.51 | not_identified | — | — | — |
| zsre | bp s1 | 0.00013 | 0.0049 % | 2.603 | 0.0127 | 7.92 | not_identified | — | — | — |
| zsre | bp s2 | 0.00018 | 0.0077 % | 2.366 | 0.0183 | 10.58 | not_identified | — | — | — |
| zsre | epc s0 | 0.00000 | 0.0000 % | — | 0.0000 | 0.00 | not_identified | — | — | — |
| zsre | epc s1 | 0.00005 | 0.0016 % | 2.971 | 0.0048 | 4.45 | not_identified | — | — | — |
| zsre | epc s2 | 0.00000 | 0.0000 % | — | 0.0000 | 0.00 | not_identified | — | — | — |

Stage-4 and PC-reader group rows of the record at u = 0.01 (joint-window intervals):

| phase | dataset | condition | cells | P(Δ>0.01) | joint-window 95 % | severity | Δ>0.01 | 95 % |
|---|---|---|---|---|---|---|---|
| PC-reader | counterfact | bp | 3 | 0.1267 % | [0.1108 %, 0.1435 %] | 2.313 | [2.134, 2.494] |
| PC-reader | counterfact | epc | 3 | 0.1480 % | [0.1311 %, 0.1653 %] | 2.206 | [1.996, 2.388] |
| PC-reader | zsre | bp | 3 | 0.0063 % | [0.0043 %, 0.0084 %] | 2.280 | [1.670, 2.969] |
| PC-reader | zsre | epc | 3 | 0.0005 % | [0.0001 %, 0.0011 %] | 2.971 | — |
| stage4 | counterfact | R1_learned_ff | 15 | 0.2984 % | [0.2699 %, 0.3312 %] | 1.913 | [1.788, 2.038] |
| stage4 | counterfact | R1_nonlearned | 15 | 2.0450 % | [1.9808 %, 2.1014 %] | 3.486 | [3.431, 3.543] |
| stage4 | counterfact | S1_LM | 15 | 0.0000 % | [0.0000 %, 0.0000 %] | — | — |
| stage4 | counterfact | matched_update | 15 | 0.0000 % | [0.0000 %, 0.0000 %] | — | — |
| stage4 | counterfact | v0_live_C1 | 15 | 0.0000 % | [0.0000 %, 0.0000 %] | — | — |
| stage4 | counterfact | v0_live_C2 | 15 | 0.0000 % | [0.0000 %, 0.0000 %] | — | — |
| stage4 | counterfact | v0_stable | 15 | 0.0000 % | [0.0000 %, 0.0000 %] | — | — |
| stage4 | zsre | R1_learned_ff | 15 | 0.1594 % | [0.1366 %, 0.1826 %] | 1.630 | [1.492, 1.777] |
| stage4 | zsre | R1_nonlearned | 15 | 0.0266 % | [0.0215 %, 0.0317 %] | 1.806 | [1.569, 2.040] |
| stage4 | zsre | S1_LM | 15 | 0.1049 % | [0.0968 %, 0.1121 %] | 1.720 | [1.520, 1.958] |
| stage4 | zsre | S1_literal | 15 | 0.1041 % | [0.0962 %, 0.1112 %] | 1.724 | [1.525, 1.945] |
| stage4 | zsre | matched_update | 15 | 0.1053 % | [0.0976 %, 0.1119 %] | 1.677 | [1.492, 1.863] |
| stage4 | zsre | v0_live_C1 | 15 | 0.0959 % | [0.0880 %, 0.1030 %] | 2.188 | [2.012, 2.397] |
| stage4 | zsre | v0_live_C2 | 15 | 0.0187 % | [0.0160 %, 0.0217 %] | 17.203 | [15.705, 18.744] |
| stage4 | zsre | v0_stable | 15 | 0.1041 % | [0.0960 %, 0.1110 %] | 1.716 | [1.519, 1.933] |

### 6.2 MQuAKE PC-reader harm [new]

| dataset | reader | mean Δ | P(Δ>0.01) | severity | Δ>0.01 | ES99+ | max Δ | GPD fit (u=0.01) | shape ξ | window-bootstrap 95 % ξ | GPD − exp (held-out nats/excess) |
|---|---|---|---|---|---|---|---|---|---|---|
| mquake | bp s0 | 0.00086 | 0.0351 % | 2.518 | 0.0883 | 9.83 | not_identified | — | — | — |
| mquake | bp s1 | 0.00500 | 0.2589 % | 1.981 | 0.5129 | 13.14 | eligible | 0.063 | [-0.023, 0.190] | -0.0012 |
| mquake | bp s2 | 0.00086 | 0.0497 % | 1.794 | 0.0893 | 7.77 | eligible | -0.079 | [-0.302, 0.112] | -0.0175 |
| mquake | epc s0 | 0.00011 | 0.0077 % | 1.499 | 0.0116 | 4.53 | not_identified | — | — | — |
| mquake | epc s1 | 0.00555 | 0.2385 % | 2.386 | 0.5691 | 12.08 | eligible | -0.110 | [-0.200, -0.005] | -0.0006 |
| mquake | epc s2 | 0.00115 | 0.0428 % | 2.707 | 0.1159 | 11.19 | eligible | -0.224 | — | -0.0014 |

Threshold sensitivity (all four registered thresholds):

| reader | u | excesses | P(Δ>u) | severity | Δ>u | fit | ξ |
|---|---|---|---|---|---|---|
| bp s0 | 0.01 | 86 | 0.0351 % | 2.518 | not_identified | — |
| bp s0 | 0.1 | 83 | 0.0338 % | 2.606 | not_identified | — |
| bp s0 | 0.5 | 71 | 0.0290 % | 3.001 | not_identified | — |
| bp s0 | 1.0 | 59 | 0.0241 % | 3.436 | not_identified | — |
| bp s1 | 0.01 | 635 | 0.2589 % | 1.981 | eligible | 0.063 |
| bp s1 | 0.1 | 600 | 0.2447 % | 2.093 | eligible | 0.051 |
| bp s1 | 0.5 | 464 | 0.1892 % | 2.621 | eligible | -0.024 |
| bp s1 | 1.0 | 357 | 0.1456 % | 3.179 | eligible | -0.061 |
| bp s2 | 0.01 | 122 | 0.0497 % | 1.794 | eligible | -0.079 |
| bp s2 | 0.1 | 118 | 0.0481 % | 1.853 | eligible | -0.057 |
| bp s2 | 0.5 | 90 | 0.0367 % | 2.339 | not_identified | — |
| bp s2 | 1.0 | 69 | 0.0281 % | 2.823 | not_identified | — |
| epc s0 | 0.01 | 19 | 0.0077 % | 1.499 | not_identified | — |
| epc s0 | 0.1 | 18 | 0.0073 % | 1.579 | not_identified | — |
| epc s0 | 0.5 | 16 | 0.0065 % | 1.749 | not_identified | — |
| epc s0 | 1.0 | 10 | 0.0041 % | 2.401 | not_identified | — |
| epc s1 | 0.01 | 585 | 0.2385 % | 2.386 | eligible | -0.110 |
| epc s1 | 0.1 | 567 | 0.2312 % | 2.460 | eligible | -0.106 |
| epc s1 | 0.5 | 488 | 0.1990 % | 2.811 | eligible | -0.101 |
| epc s1 | 1.0 | 390 | 0.1590 % | 3.331 | eligible | -0.139 |
| epc s2 | 0.01 | 105 | 0.0428 % | 2.707 | eligible | -0.224 |
| epc s2 | 0.1 | 104 | 0.0424 % | 2.732 | eligible | -0.210 |
| epc s2 | 0.5 | 92 | 0.0375 % | 3.047 | not_identified | — |
| epc s2 | 1.0 | 76 | 0.0310 % | 3.536 | not_identified | — |

![Harm survival, PC-reader cells](../../../../../assets/extremes_analysis/ext-20261009/figures/harm_survival_pcreader.png)

### 6.3 Per-probe target-loss tails [new]

Per-token NLL of the taught target on edit/paraphrase/unseen prompts; exceedances above the model's own P95; item-group bootstrap. Models that abstain share the frozen tail on those probes.

Probe-level (one value per probe; 300 edit items, 300–600 paraphrases, 100 unseen prompts): exceedances above P95 number 15–30, below the 50-excess floor, so no probe-level shape is reported — only the descriptive extremes.

| dataset | family | model | n probes | mean | P95 | P99 | max | CVaR95 | excesses > P95 | fit |
|---|---|---|---|---|---|---|---|---|---|---|
| counterfact | edit | BP reader s0 | 300 | 0.02 | 0.05 | 0.06 | 0.06 | 0.05 | 15 | insufficient |
| counterfact | edit | BP reader s1 | 300 | 0.10 | 0.05 | 0.13 | 9.43 | 1.57 | 15 | insufficient |
| counterfact | edit | BP reader s2 | 300 | 0.02 | 0.05 | 0.06 | 0.06 | 0.05 | 15 | insufficient |
| counterfact | edit | ePC reader s0 | 300 | 0.02 | 0.05 | 0.06 | 0.06 | 0.05 | 15 | insufficient |
| counterfact | edit | ePC reader s1 | 300 | 0.02 | 0.05 | 0.06 | 0.06 | 0.05 | 15 | insufficient |
| counterfact | edit | ePC reader s2 | 300 | 0.02 | 0.05 | 0.06 | 0.06 | 0.05 | 15 | insufficient |
| counterfact | edit | frozen GPT-2 | 300 | 6.96 | 9.12 | 10.58 | 11.70 | 10.06 | 15 | insufficient |
| counterfact | paraphrase | BP reader s0 | 600 | 1.36 | 8.19 | 9.32 | 10.50 | 9.00 | 30 | insufficient |
| counterfact | paraphrase | BP reader s1 | 600 | 1.45 | 8.37 | 9.72 | 11.70 | 9.19 | 30 | insufficient |
| counterfact | paraphrase | BP reader s2 | 600 | 1.13 | 7.78 | 9.13 | 10.83 | 8.69 | 30 | insufficient |
| counterfact | paraphrase | ePC reader s0 | 600 | 3.18 | 9.11 | 9.89 | 11.56 | 9.66 | 30 | insufficient |
| counterfact | paraphrase | ePC reader s1 | 600 | 1.60 | 8.40 | 9.53 | 15.56 | 9.32 | 30 | insufficient |
| counterfact | paraphrase | ePC reader s2 | 600 | 2.50 | 8.86 | 10.38 | 11.93 | 9.69 | 30 | insufficient |
| counterfact | paraphrase | frozen GPT-2 | 600 | 7.37 | 9.78 | 10.54 | 11.93 | 10.40 | 30 | insufficient |
| counterfact | unseen | BP reader s0 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | BP reader s1 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | BP reader s2 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | ePC reader s0 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | ePC reader s1 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | ePC reader s2 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| counterfact | unseen | frozen GPT-2 | 100 | 6.92 | 9.45 | 9.73 | 10.01 | 9.70 | 5 | insufficient |
| mquake | edit | BP reader s0 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.05 | 15 | insufficient |
| mquake | edit | BP reader s1 | 300 | 0.34 | 3.90 | 7.25 | 8.47 | 5.78 | 15 | insufficient |
| mquake | edit | BP reader s2 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.05 | 15 | insufficient |
| mquake | edit | ePC reader s0 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.05 | 15 | insufficient |
| mquake | edit | ePC reader s1 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.05 | 15 | insufficient |
| mquake | edit | ePC reader s2 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.05 | 15 | insufficient |
| mquake | edit | frozen GPT-2 | 300 | 5.17 | 7.53 | 9.15 | 9.99 | 8.39 | 15 | insufficient |
| mquake | paraphrase | BP reader s0 | 300 | 2.01 | 7.12 | 8.59 | 11.06 | 8.09 | 15 | insufficient |
| mquake | paraphrase | BP reader s1 | 300 | 1.28 | 5.92 | 8.59 | 10.45 | 7.22 | 15 | insufficient |
| mquake | paraphrase | BP reader s2 | 300 | 1.49 | 6.50 | 7.70 | 10.45 | 7.38 | 15 | insufficient |
| mquake | paraphrase | ePC reader s0 | 300 | 2.10 | 7.15 | 8.59 | 11.06 | 8.03 | 15 | insufficient |
| mquake | paraphrase | ePC reader s1 | 300 | 1.99 | 6.85 | 8.06 | 10.45 | 7.77 | 15 | insufficient |
| mquake | paraphrase | ePC reader s2 | 300 | 2.17 | 7.15 | 8.59 | 10.45 | 7.98 | 15 | insufficient |
| mquake | paraphrase | frozen GPT-2 | 300 | 6.05 | 9.31 | 10.91 | 12.27 | 10.12 | 15 | insufficient |
| mquake | unseen | BP reader s0 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | BP reader s1 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | BP reader s2 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | ePC reader s0 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | ePC reader s1 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | ePC reader s2 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| mquake | unseen | frozen GPT-2 | 100 | 5.28 | 7.21 | 7.91 | 10.18 | 7.98 | 5 | insufficient |
| zsre | edit | BP reader s0 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | BP reader s1 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | BP reader s2 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | ePC reader s0 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | ePC reader s1 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | ePC reader s2 | 300 | 0.01 | 0.04 | 0.05 | 0.06 | 0.04 | 15 | insufficient |
| zsre | edit | frozen GPT-2 | 300 | 6.01 | 9.71 | 11.63 | 12.22 | 10.91 | 15 | insufficient |
| zsre | paraphrase | BP reader s0 | 300 | 0.16 | 0.07 | 6.03 | 6.43 | 2.70 | 15 | insufficient |
| zsre | paraphrase | BP reader s1 | 300 | 0.08 | 0.05 | 0.26 | 6.43 | 1.13 | 15 | insufficient |
| zsre | paraphrase | BP reader s2 | 300 | 0.14 | 0.06 | 5.73 | 6.43 | 2.34 | 15 | insufficient |
| zsre | paraphrase | ePC reader s0 | 300 | 0.32 | 2.17 | 6.44 | 7.93 | 5.63 | 15 | insufficient |
| zsre | paraphrase | ePC reader s1 | 300 | 0.17 | 0.08 | 5.73 | 6.43 | 2.83 | 15 | insufficient |
| zsre | paraphrase | ePC reader s2 | 300 | 0.12 | 0.06 | 4.82 | 6.43 | 1.93 | 15 | insufficient |
| zsre | paraphrase | frozen GPT-2 | 300 | 6.10 | 10.83 | 11.65 | 12.69 | 11.33 | 15 | insufficient |
| zsre | unseen | BP reader s0 | 100 | 6.23 | 10.07 | 12.11 | 15.03 | 11.58 | 5 | insufficient |
| zsre | unseen | BP reader s1 | 100 | 6.21 | 11.35 | 13.50 | 15.03 | 12.71 | 5 | insufficient |
| zsre | unseen | BP reader s2 | 100 | 6.28 | 11.35 | 13.50 | 15.03 | 12.71 | 5 | insufficient |
| zsre | unseen | ePC reader s0 | 100 | 6.21 | 10.07 | 12.11 | 15.03 | 11.58 | 5 | insufficient |
| zsre | unseen | ePC reader s1 | 100 | 6.33 | 10.92 | 13.50 | 15.03 | 12.62 | 5 | insufficient |
| zsre | unseen | ePC reader s2 | 100 | 6.29 | 10.13 | 12.90 | 15.03 | 12.05 | 5 | insufficient |
| zsre | unseen | frozen GPT-2 | 100 | 6.13 | 9.38 | 10.91 | 12.08 | 10.35 | 5 | insufficient |

Token-level (one value per target token, terminator excluded; groups = items for the bootstrap). `pooled_probes` pools edit, paraphrase and unseen prompts (new target) with item-locality, sealed locality and near-miss neighbour prompts (true target) and is the only population that clears the 100-excess screen. Two threshold rules are shown for it: each model's *own* P95 (the handoff's rule; a cap that has driven many losses to zero has a much lower P95, so its 'tail' starts in the frozen model's body) and the *common* absolute threshold u = frozen P95 (the same cases for every model, the comparison that answers the three-model question). Per-family rows are own-P90 and exploratory or insufficient:

| dataset | family | model | threshold rule | n tokens | P99 | max | threshold | excesses | fit | κ | item-bootstrap 95 % κ | σ_u | GPD − exp (in-sample nats/excess) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| counterfact | locality_item | BP reader s0 | own quantile | 900 | 14.69 | 17.54 | P90 = 10.66 | 90 | exploratory | -0.191 | [-0.42, 0.06] | 2.234 | 0.0113 |
| counterfact | locality_item | BP reader s1 | own quantile | 900 | 14.69 | 17.54 | P90 = 10.66 | 90 | exploratory | -0.191 | [-0.42, 0.06] | 2.234 | 0.0113 |
| counterfact | locality_item | BP reader s2 | own quantile | 900 | 14.69 | 17.54 | P90 = 10.66 | 90 | exploratory | -0.191 | [-0.42, 0.06] | 2.234 | 0.0113 |
| counterfact | locality_item | ePC reader s0 | own quantile | 900 | 14.72 | 17.54 | P90 = 10.70 | 90 | exploratory | -0.198 | [-0.45, 0.05] | 2.299 | 0.0117 |
| counterfact | locality_item | ePC reader s1 | own quantile | 900 | 14.90 | 19.00 | P90 = 10.76 | 90 | exploratory | -0.162 | [-0.43, 0.05] | 2.346 | 0.0091 |
| counterfact | locality_item | ePC reader s2 | own quantile | 900 | 14.69 | 17.54 | P90 = 10.66 | 90 | exploratory | -0.191 | [-0.42, 0.06] | 2.234 | 0.0113 |
| counterfact | locality_item | frozen GPT-2 | own quantile | 900 | 14.69 | 17.54 | P90 = 10.66 | 90 | exploratory | -0.191 | [-0.42, 0.06] | 2.234 | 0.0113 |
| counterfact | paraphrase | BP reader s0 | own quantile | 600 | 13.35 | 18.25 | P90 = 8.67 | 60 | exploratory | -0.241 | [-0.50, -0.06] | 3.271 | 0.0259 |
| counterfact | paraphrase | BP reader s1 | own quantile | 600 | 13.24 | 15.73 | P90 = 8.86 | 60 | exploratory | -0.460 | [-1.10, -0.31] | 3.548 | 0.0799 |
| counterfact | paraphrase | BP reader s2 | own quantile | 600 | 12.07 | 18.25 | P90 = 7.57 | 60 | exploratory | -0.192 | [-0.91, -0.06] | 2.895 | 0.0264 |
| counterfact | paraphrase | ePC reader s0 | own quantile | 600 | 12.91 | 17.22 | P90 = 10.73 | 60 | exploratory | -0.027 | [-1.13, 0.14] | 1.222 | 0.0005 |
| counterfact | paraphrase | ePC reader s1 | own quantile | 600 | 13.62 | 31.11 | P90 = 8.80 | 60 | exploratory | 0.049 | [-0.48, 0.22] | 2.698 | 0.0025 |
| counterfact | paraphrase | ePC reader s2 | own quantile | 600 | 14.33 | 17.22 | P90 = 9.98 | 60 | exploratory | -0.206 | [-0.43, -0.01] | 2.414 | 0.0172 |
| counterfact | paraphrase | frozen GPT-2 | own quantile | 600 | 14.33 | 16.45 | P90 = 11.99 | 60 | exploratory | 0.035 | [-0.21, 0.35] | 0.968 | 0.0004 |
| counterfact | pooled_probes | BP reader s0 | frozen quantile (common) | 2050 | 14.57 | 18.93 | P95 = 12.70 | 69 | exploratory | -0.008 | [-0.37, 0.29] | 1.514 | 0.0000 |
| counterfact | pooled_probes | BP reader s1 | frozen quantile (common) | 2050 | 14.52 | 18.93 | P95 = 12.70 | 69 | exploratory | -0.057 | [-0.37, 0.29] | 1.472 | 0.0010 |
| counterfact | pooled_probes | BP reader s2 | frozen quantile (common) | 2050 | 14.40 | 18.93 | P95 = 12.70 | 60 | exploratory | -0.034 | [-0.29, 0.24] | 1.538 | 0.0004 |
| counterfact | pooled_probes | ePC reader s0 | frozen quantile (common) | 2050 | 14.49 | 18.93 | P95 = 12.70 | 67 | exploratory | 0.005 | [-0.31, 0.35] | 1.434 | 0.0000 |
| counterfact | pooled_probes | ePC reader s1 | frozen quantile (common) | 2050 | 14.68 | 31.11 | P95 = 12.70 | 75 | exploratory | 0.193 | [-0.30, 0.41] | 1.435 | 0.0282 |
| counterfact | pooled_probes | ePC reader s2 | frozen quantile (common) | 2050 | 14.65 | 18.93 | P95 = 12.70 | 70 | exploratory | -0.153 | [-0.48, 0.13] | 1.785 | 0.0072 |
| counterfact | pooled_probes | frozen GPT-2 | frozen quantile (common) | 2050 | 14.85 | 18.93 | P95 = 12.70 | 103 | ok | -0.032 | [-0.31, 0.23] | 1.330 | 0.0003 |
| counterfact | pooled_probes | BP reader s0 | own quantile | 2050 | 14.57 | 18.93 | P95 = 11.94 | 103 | ok | -0.089 | [-0.31, 0.10] | 1.774 | 0.0029 |
| counterfact | pooled_probes | BP reader s1 | own quantile | 2050 | 14.52 | 18.93 | P95 = 11.96 | 103 | ok | -0.123 | [-0.33, 0.06] | 1.728 | 0.0062 |
| counterfact | pooled_probes | BP reader s2 | own quantile | 2050 | 14.40 | 18.93 | P95 = 11.76 | 103 | ok | -0.056 | [-0.23, 0.14] | 1.665 | 0.0012 |
| counterfact | pooled_probes | ePC reader s0 | own quantile | 2050 | 14.49 | 18.93 | P95 = 11.99 | 103 | ok | -0.053 | [-0.27, 0.12] | 1.596 | 0.0010 |
| counterfact | pooled_probes | ePC reader s1 | own quantile | 2050 | 14.68 | 31.11 | P95 = 11.98 | 103 | ok | 0.088 | [-0.31, 0.26] | 1.743 | 0.0077 |
| counterfact | pooled_probes | ePC reader s2 | own quantile | 2050 | 14.65 | 18.93 | P95 = 11.97 | 103 | ok | -0.161 | [-0.36, 0.02] | 1.922 | 0.0094 |
| counterfact | pooled_probes | frozen GPT-2 | own quantile | 2050 | 14.85 | 18.93 | P95 = 12.70 | 103 | ok | -0.032 | [-0.31, 0.23] | 1.330 | 0.0003 |
| mquake | locality_item | BP reader s0 | own quantile | 1481 | 15.17 | 27.15 | P90 = 9.22 | 148 | ok | 0.185 | [-0.00, 0.35] | 2.138 | 0.0170 |
| mquake | locality_item | BP reader s1 | own quantile | 1481 | 15.73 | 27.15 | P90 = 9.22 | 148 | ok | 0.203 | [0.01, 0.36] | 2.158 | 0.0194 |
| mquake | locality_item | BP reader s2 | own quantile | 1481 | 15.73 | 27.15 | P90 = 9.27 | 148 | ok | 0.178 | [0.02, 0.35] | 2.177 | 0.0154 |
| mquake | locality_item | ePC reader s0 | own quantile | 1481 | 15.73 | 27.15 | P90 = 9.21 | 148 | ok | 0.209 | [0.02, 0.38] | 2.141 | 0.0203 |
| mquake | locality_item | ePC reader s1 | own quantile | 1481 | 16.24 | 27.15 | P90 = 9.27 | 148 | ok | 0.196 | [0.03, 0.36] | 2.200 | 0.0177 |
| mquake | locality_item | ePC reader s2 | own quantile | 1481 | 15.73 | 27.15 | P90 = 9.25 | 148 | ok | 0.212 | [0.02, 0.38] | 2.126 | 0.0206 |
| mquake | locality_item | frozen GPT-2 | own quantile | 1481 | 11.61 | 15.06 | P90 = 8.65 | 148 | ok | -0.244 | [-0.64, -0.17] | 1.843 | 0.0373 |
| mquake | paraphrase | BP reader s0 | own quantile | 755 | 17.87 | 23.13 | P90 = 8.48 | 76 | exploratory | -0.145 | [-0.40, 0.04] | 4.261 | 0.0071 |
| mquake | paraphrase | BP reader s1 | own quantile | 755 | 13.41 | 17.65 | P90 = 5.91 | 76 | exploratory | -0.267 | [-0.49, -0.07] | 4.314 | 0.0224 |
| mquake | paraphrase | BP reader s2 | own quantile | 755 | 12.03 | 17.65 | P90 = 6.35 | 76 | exploratory | -0.281 | [-0.50, -0.18] | 4.016 | 0.0377 |
| mquake | paraphrase | ePC reader s0 | own quantile | 755 | 15.97 | 21.10 | P90 = 8.40 | 76 | exploratory | -0.073 | [-0.25, 0.08] | 3.424 | 0.0019 |
| mquake | paraphrase | ePC reader s1 | own quantile | 755 | 14.62 | 20.33 | P90 = 8.34 | 76 | exploratory | -0.159 | [-0.46, 0.00] | 3.226 | 0.0125 |
| mquake | paraphrase | ePC reader s2 | own quantile | 755 | 15.52 | 23.45 | P90 = 8.47 | 76 | exploratory | -0.004 | [-0.21, 0.13] | 3.137 | 0.0000 |
| mquake | paraphrase | frozen GPT-2 | own quantile | 755 | 18.87 | 23.13 | P90 = 12.76 | 76 | exploratory | -0.344 | [-0.66, -0.14] | 4.154 | 0.0430 |
| mquake | pooled_probes | BP reader s0 | frozen quantile (common) | 3632 | 14.60 | 27.15 | P95 = 11.60 | 99 | exploratory | 0.089 | [-0.11, 0.31] | 2.831 | 0.0025 |
| mquake | pooled_probes | BP reader s1 | frozen quantile (common) | 3632 | 13.78 | 27.15 | P95 = 11.60 | 82 | exploratory | 0.135 | [-0.05, 0.33] | 2.512 | 0.0073 |
| mquake | pooled_probes | BP reader s2 | frozen quantile (common) | 3632 | 13.18 | 27.15 | P95 = 11.60 | 79 | exploratory | 0.153 | [-0.10, 0.36] | 2.375 | 0.0095 |
| mquake | pooled_probes | ePC reader s0 | frozen quantile (common) | 3632 | 14.33 | 27.15 | P95 = 11.60 | 91 | exploratory | 0.082 | [-0.17, 0.32] | 2.901 | 0.0021 |
| mquake | pooled_probes | ePC reader s1 | frozen quantile (common) | 3632 | 13.99 | 27.15 | P95 = 11.60 | 92 | exploratory | 0.141 | [-0.06, 0.34] | 2.453 | 0.0077 |
| mquake | pooled_probes | ePC reader s2 | frozen quantile (common) | 3632 | 14.31 | 27.15 | P95 = 11.60 | 92 | exploratory | 0.114 | [-0.11, 0.34] | 2.787 | 0.0043 |
| mquake | pooled_probes | frozen GPT-2 | frozen quantile (common) | 3632 | 15.41 | 23.13 | P95 = 11.60 | 182 | ok | 0.130 | [-0.05, 0.29] | 1.945 | 0.0047 |
| mquake | pooled_probes | BP reader s0 | own quantile | 3632 | 14.60 | 27.15 | P95 = 10.55 | 182 | ok | 0.340 | [0.14, 0.56] | 1.689 | 0.0364 |
| mquake | pooled_probes | BP reader s1 | own quantile | 3632 | 13.78 | 27.15 | P95 = 10.27 | 182 | ok | 0.229 | [0.06, 0.39] | 1.752 | 0.0254 |
| mquake | pooled_probes | BP reader s2 | own quantile | 3632 | 13.18 | 27.15 | P95 = 10.13 | 182 | ok | 0.192 | [0.04, 0.34] | 1.824 | 0.0191 |
| mquake | pooled_probes | ePC reader s0 | own quantile | 3632 | 14.33 | 27.15 | P95 = 10.36 | 182 | ok | 0.266 | [0.10, 0.43] | 1.857 | 0.0267 |
| mquake | pooled_probes | ePC reader s1 | own quantile | 3632 | 13.99 | 27.15 | P95 = 10.39 | 182 | ok | 0.230 | [0.07, 0.42] | 1.808 | 0.0236 |
| mquake | pooled_probes | ePC reader s2 | own quantile | 3632 | 14.31 | 27.15 | P95 = 10.36 | 182 | ok | 0.259 | [0.11, 0.41] | 1.883 | 0.0268 |
| mquake | pooled_probes | frozen GPT-2 | own quantile | 3632 | 15.41 | 23.13 | P95 = 11.60 | 182 | ok | 0.130 | [-0.05, 0.29] | 1.945 | 0.0047 |
| zsre | locality_item | BP reader s0 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | BP reader s1 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | BP reader s2 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | ePC reader s0 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | ePC reader s1 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | ePC reader s2 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | locality_item | frozen GPT-2 | own quantile | 1390 | 16.18 | 19.58 | P90 = 12.51 | 139 | ok | -0.198 | [-0.37, -0.07] | 1.936 | 0.0189 |
| zsre | paraphrase | BP reader s0 | own quantile | 810 | 7.09 | 15.93 | P90 = 0.07 | 81 | exploratory | 2.364 | [1.41, 2.94] | 0.040 | 1.4227 |
| zsre | paraphrase | BP reader s1 | own quantile | 810 | 0.73 | 15.93 | P90 = 0.06 | 81 | exploratory | 1.629 | [0.46, 2.44] | 0.027 | 1.8646 |
| zsre | paraphrase | BP reader s2 | own quantile | 810 | 7.09 | 15.93 | P90 = 0.06 | 81 | exploratory | 2.252 | [1.18, 2.91] | 0.036 | 1.5554 |
| zsre | paraphrase | ePC reader s0 | own quantile | 810 | 10.86 | 17.15 | P90 = 0.08 | 81 | exploratory | 2.977 | [0.09, 3.57] | 0.124 | 0.4113 |
| zsre | paraphrase | ePC reader s1 | own quantile | 810 | 7.64 | 15.93 | P90 = 0.07 | 81 | exploratory | 2.418 | [1.65, 2.92] | 0.045 | 1.3106 |
| zsre | paraphrase | ePC reader s2 | own quantile | 810 | 4.52 | 13.19 | P90 = 0.06 | 81 | exploratory | 2.096 | [1.19, 2.77] | 0.030 | 1.6154 |
| zsre | paraphrase | frozen GPT-2 | own quantile | 810 | 18.96 | 21.47 | P90 = 11.90 | 81 | exploratory | -0.461 | [-0.73, -0.00] | 4.944 | 0.0460 |
| zsre | pooled_probes | BP reader s0 | frozen quantile (common) | 3676 | 16.23 | 21.64 | P95 = 14.05 | 111 | ok | -0.154 | [-0.35, -0.02] | 2.023 | 0.0100 |
| zsre | pooled_probes | BP reader s1 | frozen quantile (common) | 3676 | 16.41 | 33.21 | P95 = 14.05 | 118 | ok | 0.105 | [-0.18, 0.30] | 1.873 | 0.0083 |
| zsre | pooled_probes | BP reader s2 | frozen quantile (common) | 3676 | 16.41 | 24.03 | P95 = 14.05 | 117 | ok | -0.043 | [-0.20, 0.11] | 2.087 | 0.0009 |
| zsre | pooled_probes | ePC reader s0 | frozen quantile (common) | 3676 | 16.31 | 21.64 | P95 = 14.05 | 109 | ok | -0.164 | [-0.35, -0.00] | 2.070 | 0.0112 |
| zsre | pooled_probes | ePC reader s1 | frozen quantile (common) | 3676 | 16.39 | 24.03 | P95 = 14.05 | 115 | ok | -0.049 | [-0.23, 0.10] | 2.036 | 0.0012 |
| zsre | pooled_probes | ePC reader s2 | frozen quantile (common) | 3676 | 16.38 | 21.97 | P95 = 14.05 | 112 | ok | -0.134 | [-0.31, -0.01] | 2.088 | 0.0077 |
| zsre | pooled_probes | frozen GPT-2 | frozen quantile (common) | 3676 | 17.91 | 21.47 | P95 = 14.05 | 184 | ok | -0.408 | [-0.56, -0.26] | 3.394 | 0.0584 |
| zsre | pooled_probes | BP reader s0 | own quantile | 3676 | 16.23 | 21.64 | P95 = 12.94 | 184 | ok | -0.175 | [-0.33, -0.05] | 2.283 | 0.0142 |
| zsre | pooled_probes | BP reader s1 | own quantile | 3676 | 16.41 | 33.21 | P95 = 13.04 | 184 | ok | 0.046 | [-0.17, 0.18] | 2.071 | 0.0017 |
| zsre | pooled_probes | BP reader s2 | own quantile | 3676 | 16.41 | 24.03 | P95 = 13.02 | 184 | ok | -0.074 | [-0.19, 0.04] | 2.271 | 0.0027 |
| zsre | pooled_probes | ePC reader s0 | own quantile | 3676 | 16.31 | 21.64 | P95 = 12.91 | 184 | ok | -0.177 | [-0.34, -0.07] | 2.312 | 0.0143 |
| zsre | pooled_probes | ePC reader s1 | own quantile | 3676 | 16.39 | 24.03 | P95 = 13.00 | 184 | ok | -0.083 | [-0.25, 0.02] | 2.239 | 0.0036 |
| zsre | pooled_probes | ePC reader s2 | own quantile | 3676 | 16.38 | 21.97 | P95 = 12.97 | 184 | ok | -0.146 | [-0.28, -0.04] | 2.281 | 0.0098 |
| zsre | pooled_probes | frozen GPT-2 | own quantile | 3676 | 17.91 | 21.47 | P95 = 14.05 | 184 | ok | -0.408 | [-0.56, -0.26] | 3.394 | 0.0584 |

![GPD shapes of per-probe target loss](../../../../../assets/extremes_analysis/ext-20261009/figures/tail_shapes_probe_loss.png)

## 7. Performance and adaptation in the extremes [new]

### 7.1 Paired gains over frozen GPT-2 and ePC vs BP

### zsre (300 edits; 2,000 group-bootstrap draws, groups = items/rows)

| family | target | gain | seed | n | mean | 95 % CI | median | helped (G>0) | harmed (G<0) | mean of worst 5 % (−G) |
|---|---|---|---|---|---|---|---|---|---|---|
| edit | new | G_BP | 0 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_BP | 1 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_BP | 2 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_BP | mean | 300 | 5.995 | [5.765, 6.211] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PC | 0 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_PC | 1 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_PC | 2 | 300 | 5.995 | [5.765, 6.211] | 5.761 | 100.0 % [1.00, 1.00] | 0.0 % | 2.662 |
| edit | new | G_PC | mean | 300 | 5.995 | [5.765, 6.211] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PCvsBP | 0 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 1 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 2 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | mean | 300 | 0.000 | [0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| paraphrase | new | G_BP | 0 | 300 | 5.937 | [5.666, 6.190] | 5.695 | 97.3 % [0.95, 0.99] | 0.3 % | 1.114 |
| paraphrase | new | G_BP | 1 | 300 | 6.021 | [5.762, 6.267] | 5.720 | 99.0 % [0.98, 1.00] | 0.3 % | 2.009 |
| paraphrase | new | G_BP | 2 | 300 | 5.956 | [5.689, 6.205] | 5.699 | 97.7 % [0.96, 0.99] | 0.3 % | 1.297 |
| paraphrase | new | G_BP | mean | 300 | 5.972 | [5.708, 6.217] | — | 99.0 % [0.98, 1.00] | — | — |
| paraphrase | new | G_PC | 0 | 300 | 5.778 | [5.486, 6.048] | 5.600 | 94.7 % [0.92, 0.97] | 0.0 % | -0.000 |
| paraphrase | new | G_PC | 1 | 300 | 5.930 | [5.654, 6.190] | 5.699 | 97.0 % [0.95, 0.99] | 0.3 % | 0.933 |
| paraphrase | new | G_PC | 2 | 300 | 5.978 | [5.711, 6.226] | 5.701 | 98.0 % [0.96, 0.99] | 0.0 % | 1.577 |
| paraphrase | new | G_PC | mean | 300 | 5.895 | [5.621, 6.146] | — | 98.0 % [0.96, 0.99] | — | — |
| paraphrase | new | G_PCvsBP | 0 | 300 | -0.159 | [-0.282, -0.055] | 0.000 | 0.3 % [0.00, 0.01] | 2.7 % | -3.082 |
| paraphrase | new | G_PCvsBP | 1 | 300 | -0.092 | [-0.176, -0.023] | 0.000 | 0.0 % [0.00, 0.00] | 2.0 % | -1.719 |
| paraphrase | new | G_PCvsBP | 2 | 300 | 0.021 | [-0.048, 0.099] | 0.000 | 1.0 % [0.00, 0.02] | 0.7 % | -0.598 |
| paraphrase | new | G_PCvsBP | mean | 300 | -0.076 | [-0.136, -0.027] | — | 0.3 % [0.00, 0.01] | — | — |
| unseen | new | G_BP | 0 | 100 | -0.102 | [-0.243, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 4.0 % | -1.696 |
| unseen | new | G_BP | 1 | 100 | -0.082 | [-0.376, 0.243] | 0.000 | 4.0 % [0.01, 0.08] | 10.0 % | -4.044 |
| unseen | new | G_BP | 2 | 100 | -0.154 | [-0.435, 0.125] | 0.000 | 2.0 % [0.00, 0.05] | 9.0 % | -4.044 |
| unseen | new | G_BP | mean | 100 | -0.112 | [-0.328, 0.096] | — | 4.0 % [0.01, 0.08] | — | — |
| unseen | new | G_PC | 0 | 100 | -0.082 | [-0.220, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 2.0 % | -1.361 |
| unseen | new | G_PC | 1 | 100 | -0.200 | [-0.406, -0.039] | 0.000 | 0.0 % [0.00, 0.00] | 5.0 % | -3.339 |
| unseen | new | G_PC | 2 | 100 | -0.162 | [-0.354, -0.017] | 0.000 | 0.0 % [0.00, 0.00] | 4.0 % | -2.696 |
| unseen | new | G_PC | mean | 100 | -0.148 | [-0.310, -0.024] | — | 0.0 % [0.00, 0.00] | — | — |
| unseen | new | G_PCvsBP | 0 | 100 | 0.020 | [0.000, 0.057] | 0.000 | 2.0 % [0.00, 0.05] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | 1 | 100 | -0.118 | [-0.381, 0.093] | 0.000 | 5.0 % [0.01, 0.10] | 4.0 % | -3.450 |
| unseen | new | G_PCvsBP | 2 | 100 | -0.008 | [-0.235, 0.184] | 0.000 | 5.0 % [0.01, 0.10] | 2.0 % | -1.940 |
| unseen | new | G_PCvsBP | mean | 100 | -0.035 | [-0.189, 0.094] | — | 7.0 % [0.02, 0.13] | — | — |
| locality_item | true | G_BP | 0 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_BP | 1 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_BP | 2 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_BP | mean | 296 | 0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| locality_item | true | G_PC | 0 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PC | 1 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PC | 2 | 296 | 0.000 | [-0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PC | mean | 296 | 0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| locality_item | true | G_PCvsBP | 0 | 296 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PCvsBP | 1 | 296 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PCvsBP | 2 | 296 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_PCvsBP | mean | 296 | 0.000 | [0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| near_miss_neighbour | true | G_BP | 0 | 100 | -0.218 | [-0.465, -0.021] | 0.000 | 1.0 % [0.00, 0.03] | 7.0 % | -4.114 |
| near_miss_neighbour | true | G_BP | 1 | 100 | -0.187 | [-0.525, 0.133] | 0.000 | 7.0 % [0.03, 0.13] | 14.0 % | -4.994 |
| near_miss_neighbour | true | G_BP | 2 | 100 | -0.166 | [-0.475, 0.113] | 0.000 | 5.0 % [0.01, 0.10] | 11.0 % | -4.616 |
| near_miss_neighbour | true | G_BP | mean | 100 | -0.190 | [-0.474, 0.061] | — | 7.0 % [0.03, 0.13] | — | — |
| near_miss_neighbour | true | G_PC | 0 | 100 | -0.074 | [-0.285, 0.070] | 0.000 | 1.0 % [0.00, 0.03] | 2.0 % | -1.788 |
| near_miss_neighbour | true | G_PC | 1 | 100 | -0.173 | [-0.402, 0.008] | 0.000 | 1.0 % [0.00, 0.03] | 7.0 % | -3.360 |
| near_miss_neighbour | true | G_PC | 2 | 100 | -0.132 | [-0.344, 0.030] | 0.000 | 1.0 % [0.00, 0.03] | 6.0 % | -2.749 |
| near_miss_neighbour | true | G_PC | mean | 100 | -0.126 | [-0.332, 0.028] | — | 1.0 % [0.00, 0.03] | — | — |
| near_miss_neighbour | true | G_PCvsBP | 0 | 100 | 0.144 | [0.018, 0.319] | 0.000 | 5.0 % [0.01, 0.10] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | 1 | 100 | 0.014 | [-0.234, 0.252] | 0.000 | 7.0 % [0.03, 0.12] | 6.0 % | -3.314 |
| near_miss_neighbour | true | G_PCvsBP | 2 | 100 | 0.035 | [-0.178, 0.264] | 0.000 | 5.0 % [0.01, 0.10] | 4.0 % | -2.303 |
| near_miss_neighbour | true | G_PCvsBP | mean | 100 | 0.064 | [-0.109, 0.246] | — | 11.0 % [0.05, 0.17] | — | — |

### counterfact (300 edits; 2,000 group-bootstrap draws, groups = items/rows)

| family | target | gain | seed | n | mean | 95 % CI | median | helped (G>0) | harmed (G<0) | mean of worst 5 % (−G) |
|---|---|---|---|---|---|---|---|---|---|---|
| edit | new | G_BP | 0 | 300 | 6.938 | [6.774, 7.091] | 6.986 | 100.0 % [1.00, 1.00] | 0.0 % | 4.314 |
| edit | new | G_BP | 1 | 300 | 6.857 | [6.683, 7.027] | 6.942 | 99.0 % [0.98, 1.00] | 0.0 % | 3.435 |
| edit | new | G_BP | 2 | 300 | 6.938 | [6.774, 7.091] | 6.986 | 100.0 % [1.00, 1.00] | 0.0 % | 4.314 |
| edit | new | G_BP | mean | 300 | 6.911 | [6.750, 7.069] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PC | 0 | 300 | 6.938 | [6.774, 7.091] | 6.986 | 100.0 % [1.00, 1.00] | 0.0 % | 4.314 |
| edit | new | G_PC | 1 | 300 | 6.938 | [6.774, 7.091] | 6.986 | 100.0 % [1.00, 1.00] | 0.0 % | 4.314 |
| edit | new | G_PC | 2 | 300 | 6.938 | [6.774, 7.091] | 6.986 | 100.0 % [1.00, 1.00] | 0.0 % | 4.314 |
| edit | new | G_PC | mean | 300 | 6.938 | [6.774, 7.091] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PCvsBP | 0 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 1 | 300 | 0.081 | [0.000, 0.182] | 0.000 | 1.0 % [0.00, 0.02] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 2 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | mean | 300 | 0.027 | [0.000, 0.061] | — | 1.0 % [0.00, 0.02] | — | — |
| paraphrase | new | G_BP | 0 | 600 | 6.007 | [5.706, 6.282] | 6.741 | 84.7 % [0.81, 0.88] | 0.8 % | -0.058 |
| paraphrase | new | G_BP | 1 | 600 | 5.921 | [5.628, 6.197] | 6.679 | 83.8 % [0.80, 0.87] | 0.2 % | -0.017 |
| paraphrase | new | G_BP | 2 | 600 | 6.244 | [5.980, 6.515] | 6.814 | 87.7 % [0.85, 0.91] | 0.0 % | -0.000 |
| paraphrase | new | G_BP | mean | 600 | 6.057 | [5.807, 6.309] | — | 94.0 % [0.92, 0.96] | — | — |
| paraphrase | new | G_PC | 0 | 600 | 4.186 | [3.838, 4.555] | 5.607 | 58.7 % [0.54, 0.63] | 0.2 % | -0.040 |
| paraphrase | new | G_PC | 1 | 600 | 5.771 | [5.464, 6.070] | 6.687 | 80.8 % [0.77, 0.84] | 0.5 % | -0.200 |
| paraphrase | new | G_PC | 2 | 600 | 4.865 | [4.511, 5.205] | 6.204 | 68.2 % [0.64, 0.72] | 0.2 % | -0.040 |
| paraphrase | new | G_PC | mean | 600 | 4.941 | [4.648, 5.228] | — | 85.2 % [0.82, 0.89] | — | — |
| paraphrase | new | G_PCvsBP | 0 | 600 | -1.821 | [-2.168, -1.447] | 0.000 | 3.7 % [0.02, 0.06] | 29.5 % | -9.353 |
| paraphrase | new | G_PCvsBP | 1 | 600 | -0.149 | [-0.357, 0.057] | 0.000 | 5.2 % [0.04, 0.07] | 8.7 % | -7.370 |
| paraphrase | new | G_PCvsBP | 2 | 600 | -1.379 | [-1.666, -1.085] | 0.000 | 3.5 % [0.02, 0.05] | 22.7 % | -9.211 |
| paraphrase | new | G_PCvsBP | mean | 600 | -1.117 | [-1.313, -0.916] | — | 5.8 % [0.04, 0.08] | — | — |
| unseen | new | G_BP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_BP | 1 | 100 | 0.004 | [0.000, 0.011] | 0.000 | 1.0 % [0.00, 0.03] | 0.0 % | -0.000 |
| unseen | new | G_BP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_BP | mean | 100 | 0.001 | [0.000, 0.004] | — | 1.0 % [0.00, 0.03] | — | — |
| unseen | new | G_PC | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PC | 1 | 100 | 0.004 | [0.000, 0.011] | 0.000 | 1.0 % [0.00, 0.03] | 0.0 % | -0.000 |
| unseen | new | G_PC | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PC | mean | 100 | 0.001 | [0.000, 0.004] | — | 1.0 % [0.00, 0.03] | — | — |
| unseen | new | G_PCvsBP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | mean | 100 | 0.000 | [0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| locality_item | true | G_BP | 0 | 900 | 0.007 | [0.000, 0.016] | 0.000 | 0.4 % [0.00, 0.01] | 0.0 % | -0.000 |
| locality_item | true | G_BP | 1 | 900 | 0.009 | [0.000, 0.020] | 0.000 | 0.4 % [0.00, 0.01] | 0.0 % | -0.000 |
| locality_item | true | G_BP | 2 | 900 | 0.003 | [0.000, 0.010] | 0.000 | 0.1 % [0.00, 0.00] | 0.0 % | -0.000 |
| locality_item | true | G_BP | mean | 900 | 0.006 | [0.001, 0.014] | — | 0.7 % [0.00, 0.01] | — | — |
| locality_item | true | G_PC | 0 | 900 | 0.027 | [0.006, 0.050] | 0.000 | 0.9 % [0.00, 0.02] | 0.1 % | -0.049 |
| locality_item | true | G_PC | 1 | 900 | 0.024 | [0.006, 0.042] | 0.000 | 1.3 % [0.01, 0.02] | 0.3 % | -0.081 |
| locality_item | true | G_PC | 2 | 900 | 0.007 | [0.000, 0.016] | 0.000 | 0.4 % [0.00, 0.01] | 0.0 % | -0.000 |
| locality_item | true | G_PC | mean | 900 | 0.019 | [0.007, 0.033] | — | 2.0 % [0.01, 0.03] | — | — |
| locality_item | true | G_PCvsBP | 0 | 900 | 0.020 | [-0.001, 0.044] | 0.000 | 0.8 % [0.00, 0.02] | 0.4 % | -0.122 |
| locality_item | true | G_PCvsBP | 1 | 900 | 0.015 | [0.000, 0.031] | 0.000 | 1.0 % [0.00, 0.02] | 0.4 % | -0.086 |
| locality_item | true | G_PCvsBP | 2 | 900 | 0.004 | [0.000, 0.010] | 0.000 | 0.3 % [0.00, 0.01] | 0.0 % | -0.000 |
| locality_item | true | G_PCvsBP | mean | 900 | 0.013 | [0.003, 0.023] | — | 1.6 % [0.01, 0.02] | — | — |
| near_miss_neighbour | true | G_BP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | 1 | 100 | 0.020 | [0.000, 0.059] | 0.000 | 1.0 % [0.00, 0.03] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | mean | 100 | 0.007 | [0.000, 0.020] | — | 1.0 % [0.00, 0.03] | — | — |
| near_miss_neighbour | true | G_PC | 0 | 100 | 0.057 | [0.000, 0.148] | 0.000 | 2.0 % [0.00, 0.05] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PC | 1 | 100 | 0.076 | [0.009, 0.166] | 0.000 | 4.0 % [0.01, 0.08] | 1.0 % | -0.015 |
| near_miss_neighbour | true | G_PC | 2 | 100 | 0.010 | [0.000, 0.031] | 0.000 | 1.0 % [0.00, 0.03] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PC | mean | 100 | 0.048 | [0.003, 0.107] | — | 4.0 % [0.01, 0.08] | — | — |
| near_miss_neighbour | true | G_PCvsBP | 0 | 100 | 0.057 | [0.000, 0.148] | 0.000 | 2.0 % [0.00, 0.05] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | 1 | 100 | 0.057 | [-0.029, 0.151] | 0.000 | 4.0 % [0.01, 0.08] | 2.0 % | -0.343 |
| near_miss_neighbour | true | G_PCvsBP | 2 | 100 | 0.010 | [0.000, 0.031] | 0.000 | 1.0 % [0.00, 0.03] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | mean | 100 | 0.041 | [-0.006, 0.102] | — | 4.0 % [0.01, 0.08] | — | — |

### mquake (300 edits; 2,000 group-bootstrap draws, groups = items/rows)

| family | target | gain | seed | n | mean | 95 % CI | median | helped (G>0) | harmed (G<0) | mean of worst 5 % (−G) |
|---|---|---|---|---|---|---|---|---|---|---|
| edit | new | G_BP | 0 | 300 | 5.157 | [5.004, 5.311] | 5.049 | 100.0 % [1.00, 1.00] | 0.0 % | 2.225 |
| edit | new | G_BP | 1 | 300 | 4.829 | [4.621, 5.023] | 4.956 | 94.0 % [0.91, 0.97] | 0.0 % | -0.000 |
| edit | new | G_BP | 2 | 300 | 5.157 | [5.004, 5.311] | 5.049 | 100.0 % [1.00, 1.00] | 0.0 % | 2.225 |
| edit | new | G_BP | mean | 300 | 5.047 | [4.890, 5.199] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PC | 0 | 300 | 5.157 | [5.004, 5.311] | 5.049 | 100.0 % [1.00, 1.00] | 0.0 % | 2.225 |
| edit | new | G_PC | 1 | 300 | 5.157 | [5.004, 5.311] | 5.049 | 100.0 % [1.00, 1.00] | 0.0 % | 2.225 |
| edit | new | G_PC | 2 | 300 | 5.157 | [5.004, 5.311] | 5.049 | 100.0 % [1.00, 1.00] | 0.0 % | 2.225 |
| edit | new | G_PC | mean | 300 | 5.157 | [5.004, 5.311] | — | 100.0 % [1.00, 1.00] | — | — |
| edit | new | G_PCvsBP | 0 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 1 | 300 | 0.328 | [0.179, 0.485] | 0.000 | 6.0 % [0.03, 0.09] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | 2 | 300 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| edit | new | G_PCvsBP | mean | 300 | 0.109 | [0.060, 0.162] | — | 6.0 % [0.03, 0.09] | — | — |
| paraphrase | new | G_BP | 0 | 300 | 4.039 | [3.708, 4.349] | 4.785 | 71.7 % [0.66, 0.77] | 0.0 % | -0.000 |
| paraphrase | new | G_BP | 1 | 300 | 4.772 | [4.488, 5.021] | 5.438 | 85.7 % [0.82, 0.89] | 0.3 % | -0.058 |
| paraphrase | new | G_BP | 2 | 300 | 4.557 | [4.269, 4.817] | 5.276 | 82.3 % [0.78, 0.86] | 0.3 % | -0.058 |
| paraphrase | new | G_BP | mean | 300 | 4.456 | [4.193, 4.708] | — | 89.3 % [0.86, 0.93] | — | — |
| paraphrase | new | G_PC | 0 | 300 | 3.949 | [3.621, 4.263] | 4.711 | 70.7 % [0.65, 0.75] | 0.0 % | -0.000 |
| paraphrase | new | G_PC | 1 | 300 | 4.054 | [3.713, 4.359] | 4.819 | 72.3 % [0.67, 0.77] | 0.0 % | -0.000 |
| paraphrase | new | G_PC | 2 | 300 | 3.880 | [3.543, 4.194] | 4.690 | 69.0 % [0.64, 0.74] | 0.3 % | -0.098 |
| paraphrase | new | G_PC | mean | 300 | 3.961 | [3.633, 4.261] | — | 75.7 % [0.71, 0.80] | — | — |
| paraphrase | new | G_PCvsBP | 0 | 300 | -0.090 | [-0.299, 0.106] | 0.000 | 4.3 % [0.02, 0.07] | 5.3 % | -5.871 |
| paraphrase | new | G_PCvsBP | 1 | 300 | -0.718 | [-0.943, -0.502] | 0.000 | 0.7 % [0.00, 0.02] | 13.7 % | -6.652 |
| paraphrase | new | G_PCvsBP | 2 | 300 | -0.677 | [-0.882, -0.486] | 0.000 | 0.3 % [0.00, 0.01] | 13.3 % | -6.515 |
| paraphrase | new | G_PCvsBP | mean | 300 | -0.495 | [-0.651, -0.347] | — | 4.0 % [0.02, 0.06] | — | — |
| unseen | new | G_BP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_BP | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_BP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_BP | mean | 100 | -0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| unseen | new | G_PC | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PC | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PC | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PC | mean | 100 | -0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| unseen | new | G_PCvsBP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| unseen | new | G_PCvsBP | mean | 100 | 0.000 | [0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| locality_item | true | G_BP | 0 | 600 | -0.235 | [-0.318, -0.156] | 0.000 | 0.2 % [0.00, 0.01] | 7.0 % | -4.142 |
| locality_item | true | G_BP | 1 | 600 | -0.246 | [-0.328, -0.166] | 0.000 | 0.0 % [0.00, 0.00] | 7.2 % | -4.256 |
| locality_item | true | G_BP | 2 | 600 | -0.250 | [-0.337, -0.169] | 0.000 | 0.2 % [0.00, 0.01] | 7.5 % | -4.262 |
| locality_item | true | G_BP | mean | 600 | -0.244 | [-0.326, -0.163] | — | 0.3 % [0.00, 0.01] | — | — |
| locality_item | true | G_PC | 0 | 600 | -0.242 | [-0.323, -0.161] | 0.000 | 0.2 % [0.00, 0.01] | 7.2 % | -4.256 |
| locality_item | true | G_PC | 1 | 600 | -0.258 | [-0.346, -0.176] | 0.000 | 0.3 % [0.00, 0.01] | 7.7 % | -4.372 |
| locality_item | true | G_PC | 2 | 600 | -0.252 | [-0.336, -0.171] | 0.000 | 0.2 % [0.00, 0.01] | 7.3 % | -4.339 |
| locality_item | true | G_PC | mean | 600 | -0.251 | [-0.334, -0.169] | — | 0.3 % [0.00, 0.01] | — | — |
| locality_item | true | G_PCvsBP | 0 | 600 | -0.006 | [-0.030, 0.011] | 0.000 | 0.2 % [0.00, 0.01] | 0.3 % | -0.200 |
| locality_item | true | G_PCvsBP | 1 | 600 | -0.013 | [-0.033, 0.001] | 0.000 | 0.3 % [0.00, 0.01] | 0.5 % | -0.342 |
| locality_item | true | G_PCvsBP | 2 | 600 | -0.002 | [-0.029, 0.017] | 0.000 | 0.3 % [0.00, 0.01] | 0.2 % | -0.186 |
| locality_item | true | G_PCvsBP | mean | 600 | -0.007 | [-0.023, 0.002] | — | 0.3 % [0.00, 0.01] | — | — |
| near_miss_neighbour | true | G_BP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_BP | mean | 100 | 0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| near_miss_neighbour | true | G_PC | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PC | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PC | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PC | mean | 100 | 0.000 | [-0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| near_miss_neighbour | true | G_PCvsBP | 0 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | 1 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | 2 | 100 | 0.000 | [0.000, 0.000] | 0.000 | 0.0 % [0.00, 0.00] | 0.0 % | -0.000 |
| near_miss_neighbour | true | G_PCvsBP | mean | 100 | 0.000 | [0.000, 0.000] | — | 0.0 % [0.00, 0.00] | — | — |
| composition | new | G_BP | 0 | 240 | -0.138 | [-0.277, 0.014] | 0.000 | 6.2 % [0.03, 0.10] | 15.4 % | -3.049 |
| composition | new | G_BP | 1 | 240 | -0.203 | [-0.394, 0.024] | 0.000 | 10.0 % [0.06, 0.14] | 33.3 % | -3.111 |
| composition | new | G_BP | 2 | 240 | -0.275 | [-0.461, -0.073] | 0.000 | 7.9 % [0.05, 0.12] | 29.2 % | -3.375 |
| composition | new | G_BP | mean | 240 | -0.205 | [-0.358, -0.027] | — | 10.0 % [0.06, 0.14] | — | — |
| composition | new | G_PC | 0 | 240 | -0.136 | [-0.268, 0.004] | 0.000 | 5.0 % [0.03, 0.08] | 14.2 % | -2.883 |
| composition | new | G_PC | 1 | 240 | -0.092 | [-0.229, 0.065] | 0.000 | 5.0 % [0.03, 0.08] | 12.5 % | -2.760 |
| composition | new | G_PC | 2 | 240 | -0.105 | [-0.248, 0.063] | 0.000 | 5.4 % [0.03, 0.09] | 15.0 % | -2.883 |
| composition | new | G_PC | mean | 240 | -0.111 | [-0.235, 0.031] | — | 6.2 % [0.03, 0.10] | — | — |
| composition | new | G_PCvsBP | 0 | 240 | 0.002 | [-0.065, 0.067] | 0.000 | 3.8 % [0.02, 0.06] | 3.8 % | -0.977 |
| composition | new | G_PCvsBP | 1 | 240 | 0.111 | [-0.035, 0.247] | 0.000 | 20.8 % [0.16, 0.26] | 5.0 % | -3.083 |
| composition | new | G_PCvsBP | 2 | 240 | 0.170 | [0.056, 0.277] | 0.000 | 14.2 % [0.10, 0.19] | 2.5 % | -1.110 |
| composition | new | G_PCvsBP | mean | 240 | 0.094 | [0.008, 0.175] | — | 23.3 % [0.18, 0.29] | — | — |

![Paired ePC − BP differences on paraphrases](../../../../../assets/extremes_analysis/ext-20261009/figures/paired_pc_minus_bp.png)

### 7.2 Gain versus frozen difficulty (deciles fixed by the frozen per-token NLL)

| dataset | family | decile | n | frozen NLL range | G_BP (seed mean) | G_PC (seed mean) | G_PCvsBP |
|---|---|---|---|---|---|---|---|
| counterfact | edit | 1 | 30 | 3.57–4.97 | 4.581 [4.45, 4.71] | 4.581 [4.45, 4.71] | 0.000 [0.00, 0.00] |
| counterfact | edit | 5 | 30 | 6.51–6.98 | 6.751 [6.70, 6.81] | 6.751 [6.70, 6.81] | 0.000 [0.00, 0.00] |
| counterfact | edit | 10 | 30 | 8.86–11.70 | 9.434 [9.06, 9.76] | 9.538 [9.27, 9.85] | 0.104 [0.00, 0.42] |
| counterfact | paraphrase | 1 | 60 | 3.62–5.51 | 3.941 [3.45, 4.36] | 3.222 [2.68, 3.73] | -0.719 [-1.05, -0.38] |
| counterfact | paraphrase | 5 | 60 | 6.86–7.38 | 5.727 [5.08, 6.25] | 4.492 [3.75, 5.15] | -1.234 [-1.79, -0.67] |
| counterfact | paraphrase | 10 | 60 | 9.39–11.93 | 8.580 [7.84, 9.16] | 7.221 [6.41, 8.09] | -1.359 [-2.05, -0.69] |
| counterfact | unseen | 1 | 10 | 3.30–4.82 | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] |
| counterfact | unseen | 5 | 10 | 6.59–6.87 | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] |
| counterfact | unseen | 10 | 10 | 8.99–10.01 | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] |
| mquake | edit | 1 | 30 | 1.24–3.55 | 2.649 [2.42, 2.89] | 2.716 [2.48, 2.94] | 0.067 [0.00, 0.17] |
| mquake | edit | 5 | 30 | 4.80–5.06 | 4.800 [4.63, 4.92] | 4.910 [4.88, 4.94] | 0.110 [0.00, 0.27] |
| mquake | edit | 10 | 30 | 6.80–9.99 | 7.404 [7.02, 7.82] | 7.757 [7.46, 8.07] | 0.354 [0.08, 0.64] |
| mquake | paraphrase | 1 | 30 | 1.44–3.83 | 2.445 [2.01, 2.79] | 2.196 [1.65, 2.62] | -0.249 [-0.53, 0.01] |
| mquake | paraphrase | 5 | 30 | 5.59–6.06 | 3.823 [2.90, 4.70] | 3.819 [2.87, 4.70] | -0.004 [-0.33, 0.26] |
| mquake | paraphrase | 10 | 30 | 8.57–12.27 | 6.654 [5.85, 7.31] | 6.637 [5.79, 7.30] | -0.017 [-0.24, 0.19] |
| mquake | unseen | 1 | 10 | 1.72–3.12 | -0.000 [-0.00, 0.00] | -0.000 [-0.00, 0.00] | 0.000 [0.00, 0.00] |
| mquake | unseen | 5 | 10 | 5.12–5.37 | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] |
| mquake | unseen | 10 | 10 | 6.85–10.18 | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] | 0.000 [0.00, 0.00] |
| zsre | edit | 1 | 30 | 1.81–3.75 | 3.080 [2.87, 3.27] | 3.080 [2.87, 3.27] | 0.000 [0.00, 0.00] |
| zsre | edit | 5 | 30 | 5.26–5.76 | 5.510 [5.46, 5.56] | 5.510 [5.46, 5.56] | 0.000 [0.00, 0.00] |
| zsre | edit | 10 | 30 | 8.92–12.22 | 10.163 [9.83, 10.48] | 10.163 [9.83, 10.48] | 0.000 [0.00, 0.00] |
| zsre | paraphrase | 1 | 30 | 1.92–3.93 | 2.959 [2.53, 3.26] | 2.965 [2.64, 3.22] | 0.006 [-0.14, 0.18] |
| zsre | paraphrase | 5 | 30 | 5.37–5.74 | 5.359 [4.97, 5.58] | 5.296 [4.87, 5.56] | -0.062 [-0.22, 0.00] |
| zsre | paraphrase | 10 | 30 | 9.25–12.69 | 10.637 [10.35, 10.94] | 10.637 [10.35, 10.94] | 0.000 [0.00, 0.00] |
| zsre | unseen | 1 | 10 | 2.41–3.67 | -0.192 [-0.89, 0.51] | -0.110 [-0.33, 0.00] | 0.082 [-0.62, 0.80] |
| zsre | unseen | 5 | 10 | 5.39–6.07 | 0.202 [0.00, 0.61] | 0.000 [0.00, 0.00] | -0.202 [-0.61, 0.00] |
| zsre | unseen | 10 | 10 | 8.62–12.08 | -1.214 [-2.35, -0.25] | -0.945 [-2.08, 0.00] | 0.269 [0.00, 0.68] |

![Deciles, zsRE paraphrase](../../../../../assets/extremes_analysis/ext-20261009/figures/deciles_zsre_paraphrase.png)

![Deciles, CounterFact paraphrase](../../../../../assets/extremes_analysis/ext-20261009/figures/deciles_counterfact_paraphrase.png)

### 7.3 Two worst-case summaries (A: each model's own worst 5 %; B: the frozen model's hardest 5 %, fixed)

| dataset | family | model | n | mean loss | A: own CVaR95 | k | B: mean loss on frozen-hard 5 % | B: success on frozen-hard 5 % | B: mean loss on frozen-hard 1 % |
|---|---|---|---|---|---|---|---|---|---|
| counterfact | edit | BP s0 | 300 | 0.019 | 0.054 | 15 | 0.018 | 100.0 % | 0.008 |
| counterfact | edit | BP s1 | 300 | 0.100 | 1.568 | 15 | 0.644 | 93.3 % | 0.008 |
| counterfact | edit | BP s2 | 300 | 0.019 | 0.054 | 15 | 0.018 | 100.0 % | 0.008 |
| counterfact | edit | ePC s0 | 300 | 0.019 | 0.054 | 15 | 0.018 | 100.0 % | 0.008 |
| counterfact | edit | ePC s1 | 300 | 0.019 | 0.054 | 15 | 0.018 | 100.0 % | 0.008 |
| counterfact | edit | ePC s2 | 300 | 0.019 | 0.054 | 15 | 0.018 | 100.0 % | 0.008 |
| counterfact | edit | frozen GPT-2 | 300 | 6.956 | 10.063 | 15 | 10.126 | 0.0 % | 11.271 |
| counterfact | paraphrase | BP s0 | 600 | 1.362 | 8.998 | 30 | 2.217 | 76.7 % | 1.944 |
| counterfact | paraphrase | BP s1 | 600 | 1.449 | 9.191 | 30 | 2.003 | 80.0 % | 4.171 |
| counterfact | paraphrase | BP s2 | 600 | 1.125 | 8.689 | 30 | 1.933 | 80.0 % | 3.744 |
| counterfact | paraphrase | ePC s0 | 600 | 3.183 | 9.660 | 30 | 2.908 | 73.3 % | 2.097 |
| counterfact | paraphrase | ePC s1 | 600 | 1.598 | 9.317 | 30 | 2.028 | 80.0 % | 4.815 |
| counterfact | paraphrase | ePC s2 | 600 | 2.504 | 9.690 | 30 | 3.408 | 70.0 % | 7.722 |
| counterfact | paraphrase | frozen GPT-2 | 600 | 7.369 | 10.396 | 30 | 10.416 | 0.0 % | 11.394 |
| counterfact | unseen | BP s0 | 100 | 6.924 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | BP s1 | 100 | 6.920 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | BP s2 | 100 | 6.924 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | ePC s0 | 100 | 6.924 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | ePC s1 | 100 | 6.920 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | ePC s2 | 100 | 6.924 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| counterfact | unseen | frozen GPT-2 | 100 | 6.924 | 9.699 | 5 | 9.752 | 0.0 % | 10.008 |
| mquake | edit | BP s0 | 300 | 0.015 | 0.047 | 15 | 0.020 | 100.0 % | 0.025 |
| mquake | edit | BP s1 | 300 | 0.342 | 5.779 | 15 | 1.660 | 80.0 % | 0.025 |
| mquake | edit | BP s2 | 300 | 0.015 | 0.047 | 15 | 0.020 | 100.0 % | 0.025 |
| mquake | edit | ePC s0 | 300 | 0.015 | 0.047 | 15 | 0.020 | 100.0 % | 0.025 |
| mquake | edit | ePC s1 | 300 | 0.015 | 0.047 | 15 | 0.020 | 100.0 % | 0.025 |
| mquake | edit | ePC s2 | 300 | 0.015 | 0.047 | 15 | 0.020 | 100.0 % | 0.025 |
| mquake | edit | frozen GPT-2 | 300 | 5.171 | 8.392 | 15 | 8.450 | 0.0 % | 9.517 |
| mquake | paraphrase | BP s0 | 300 | 2.009 | 8.086 | 15 | 3.484 | 33.3 % | 6.048 |
| mquake | paraphrase | BP s1 | 300 | 1.276 | 7.218 | 15 | 2.960 | 33.3 % | 3.427 |
| mquake | paraphrase | BP s2 | 300 | 1.491 | 7.378 | 15 | 2.960 | 33.3 % | 3.427 |
| mquake | paraphrase | ePC s0 | 300 | 2.099 | 8.032 | 15 | 3.484 | 33.3 % | 6.048 |
| mquake | paraphrase | ePC s1 | 300 | 1.994 | 7.771 | 15 | 2.960 | 33.3 % | 3.427 |
| mquake | paraphrase | ePC s2 | 300 | 2.168 | 7.981 | 15 | 2.960 | 33.3 % | 3.427 |
| mquake | paraphrase | frozen GPT-2 | 300 | 6.048 | 10.116 | 15 | 10.170 | 0.0 % | 11.528 |
| mquake | unseen | BP s0 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | BP s1 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | BP s2 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | ePC s0 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | ePC s1 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | ePC s2 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| mquake | unseen | frozen GPT-2 | 100 | 5.284 | 7.985 | 5 | 8.141 | 0.0 % | 10.184 |
| zsre | edit | BP s0 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | BP s1 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | BP s2 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | ePC s0 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | ePC s1 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | ePC s2 | 300 | 0.015 | 0.043 | 15 | 0.022 | 100.0 % | 0.008 |
| zsre | edit | frozen GPT-2 | 300 | 6.009 | 10.908 | 15 | 10.988 | 0.0 % | 11.952 |
| zsre | paraphrase | BP s0 | 300 | 0.161 | 2.695 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | BP s1 | 300 | 0.077 | 1.130 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | BP s2 | 300 | 0.142 | 2.338 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | ePC s0 | 300 | 0.320 | 5.635 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | ePC s1 | 300 | 0.168 | 2.831 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | ePC s2 | 300 | 0.120 | 1.934 | 15 | 0.046 | 100.0 % | 0.045 |
| zsre | paraphrase | frozen GPT-2 | 300 | 6.098 | 11.331 | 15 | 11.365 | 0.0 % | 12.332 |
| zsre | unseen | BP s0 | 100 | 6.229 | 11.584 | 5 | 10.551 | 0.0 % | 12.078 |
| zsre | unseen | BP s1 | 100 | 6.209 | 12.712 | 5 | 11.323 | 0.0 % | 12.078 |
| zsre | unseen | BP s2 | 100 | 6.281 | 12.712 | 5 | 11.323 | 0.0 % | 12.078 |
| zsre | unseen | ePC s0 | 100 | 6.209 | 11.584 | 5 | 10.551 | 0.0 % | 12.078 |
| zsre | unseen | ePC s1 | 100 | 6.328 | 12.620 | 5 | 11.323 | 0.0 % | 12.078 |
| zsre | unseen | ePC s2 | 100 | 6.289 | 12.054 | 5 | 10.551 | 0.0 % | 12.078 |
| zsre | unseen | frozen GPT-2 | 100 | 6.128 | 10.353 | 5 | 10.551 | 0.0 % | 12.078 |

![CVaR A and B](../../../../../assets/extremes_analysis/ext-20261009/figures/cvar_A_B.png)

### 7.4 Rare and severe regressions (D = L_model − L_frozen; rows `epc{s}_minus_bp{s}` use L_BP as reference)

| dataset | family | target | model (D = L_model − L_ref) | n | P(D>0) | mean D | D>0 | P99 D | worst-5 % mean D | max D | P(D>0.5) | P(D>1) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| counterfact | edit | new | BP s0 | 300 | 0.0 % | — | -4.079 | -4.314 | -3.564 | 0.00 % | 0.00 % |
| counterfact | edit | new | BP s1 | 300 | 0.0 % | — | -3.528 | -3.435 | 0.000 | 0.00 % | 0.00 % |
| counterfact | edit | new | BP s2 | 300 | 0.0 % | — | -4.079 | -4.314 | -3.564 | 0.00 % | 0.00 % |
| counterfact | edit | new | ePC s0 | 300 | 0.0 % | — | -4.079 | -4.314 | -3.564 | 0.00 % | 0.00 % |
| counterfact | edit | new | epc0_minus_bp0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | edit | new | ePC s1 | 300 | 0.0 % | — | -4.079 | -4.314 | -3.564 | 0.00 % | 0.00 % |
| counterfact | edit | new | epc1_minus_bp1 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | edit | new | ePC s2 | 300 | 0.0 % | — | -4.079 | -4.314 | -3.564 | 0.00 % | 0.00 % |
| counterfact | edit | new | epc2_minus_bp2 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | BP s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | BP s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | BP s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | ePC s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | epc0_minus_bp0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | ePC s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | epc1_minus_bp1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | ePC s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality | true | epc2_minus_bp2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality_item | true | BP s0 | 900 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality_item | true | BP s1 | 900 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality_item | true | BP s2 | 900 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality_item | true | ePC s0 | 900 | 0.1 % | 2.264 | 0.000 | 0.049 | 2.264 | 0.11 % | 0.11 % |
| counterfact | locality_item | true | epc0_minus_bp0 | 900 | 0.4 % | 1.407 | 0.000 | 0.122 | 2.264 | 0.44 % | 0.33 % |
| counterfact | locality_item | true | ePC s1 | 900 | 0.3 % | 1.240 | 0.000 | 0.081 | 2.264 | 0.22 % | 0.22 % |
| counterfact | locality_item | true | epc1_minus_bp1 | 900 | 0.4 % | 0.987 | 0.000 | 0.086 | 2.264 | 0.22 % | 0.22 % |
| counterfact | locality_item | true | ePC s2 | 900 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | locality_item | true | epc2_minus_bp2 | 900 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | BP s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | BP s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | BP s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | ePC s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | ePC s1 | 100 | 1.0 % | 0.090 | 0.001 | 0.015 | 0.090 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | epc1_minus_bp1 | 100 | 2.0 % | 1.029 | 0.109 | 0.343 | 1.969 | 1.00 % | 1.00 % |
| counterfact | near_miss_neighbour | true | ePC s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | near_miss_neighbour | true | epc2_minus_bp2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | paraphrase | new | BP s0 | 600 | 0.8 % | 0.359 | 0.000 | 0.058 | 1.237 | 0.17 % | 0.17 % |
| counterfact | paraphrase | new | BP s1 | 600 | 0.2 % | 0.523 | 0.000 | 0.017 | 0.523 | 0.17 % | 0.00 % |
| counterfact | paraphrase | new | BP s2 | 600 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | paraphrase | new | ePC s0 | 600 | 0.2 % | 1.237 | 0.000 | 0.040 | 1.237 | 0.17 % | 0.17 % |
| counterfact | paraphrase | new | epc0_minus_bp0 | 600 | 29.5 % | 6.987 | 9.587 | 9.353 | 10.516 | 28.67 % | 28.50 % |
| counterfact | paraphrase | new | ePC s1 | 600 | 0.5 % | 2.069 | 0.000 | 0.200 | 3.865 | 0.50 % | 0.50 % |
| counterfact | paraphrase | new | epc1_minus_bp1 | 600 | 8.7 % | 5.856 | 8.646 | 7.370 | 9.494 | 8.17 % | 8.17 % |
| counterfact | paraphrase | new | ePC s2 | 600 | 0.2 % | 1.237 | 0.000 | 0.040 | 1.237 | 0.17 % | 0.17 % |
| counterfact | paraphrase | new | epc2_minus_bp2 | 600 | 22.7 % | 7.032 | 9.704 | 9.211 | 11.317 | 22.33 % | 22.33 % |
| counterfact | unseen | new | BP s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | BP s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | BP s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | ePC s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | ePC s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | epc1_minus_bp1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | ePC s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| counterfact | unseen | new | epc2_minus_bp2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | edit | new | BP s0 | 300 | 0.0 % | — | -1.970 | -2.225 | -1.220 | 0.00 % | 0.00 % |
| mquake | edit | new | BP s1 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | edit | new | BP s2 | 300 | 0.0 % | — | -1.970 | -2.225 | -1.220 | 0.00 % | 0.00 % |
| mquake | edit | new | ePC s0 | 300 | 0.0 % | — | -1.970 | -2.225 | -1.220 | 0.00 % | 0.00 % |
| mquake | edit | new | epc0_minus_bp0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | edit | new | ePC s1 | 300 | 0.0 % | — | -1.970 | -2.225 | -1.220 | 0.00 % | 0.00 % |
| mquake | edit | new | epc1_minus_bp1 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | edit | new | ePC s2 | 300 | 0.0 % | — | -1.970 | -2.225 | -1.220 | 0.00 % | 0.00 % |
| mquake | edit | new | epc2_minus_bp2 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | BP s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | BP s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | BP s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | ePC s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | epc0_minus_bp0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | ePC s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | epc1_minus_bp1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | ePC s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality | true | epc2_minus_bp2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | locality_item | true | BP s0 | 600 | 7.0 % | 3.372 | 4.721 | 4.142 | 10.119 | 6.67 % | 6.67 % |
| mquake | locality_item | true | BP s1 | 600 | 7.2 % | 3.428 | 5.303 | 4.256 | 10.119 | 6.83 % | 6.83 % |
| mquake | locality_item | true | BP s2 | 600 | 7.5 % | 3.383 | 4.721 | 4.262 | 10.119 | 7.17 % | 7.17 % |
| mquake | locality_item | true | ePC s0 | 600 | 7.2 % | 3.428 | 5.303 | 4.256 | 10.119 | 6.83 % | 6.83 % |
| mquake | locality_item | true | epc0_minus_bp0 | 600 | 0.3 % | 3.096 | 0.000 | 0.200 | 5.755 | 0.17 % | 0.17 % |
| mquake | locality_item | true | ePC s1 | 600 | 7.7 % | 3.434 | 5.303 | 4.372 | 10.119 | 7.33 % | 7.33 % |
| mquake | locality_item | true | epc1_minus_bp1 | 600 | 0.5 % | 3.532 | 0.000 | 0.342 | 3.684 | 0.50 % | 0.50 % |
| mquake | locality_item | true | ePC s2 | 600 | 7.3 % | 3.490 | 5.303 | 4.339 | 10.119 | 7.00 % | 7.00 % |
| mquake | locality_item | true | epc2_minus_bp2 | 600 | 0.2 % | 5.755 | 0.000 | 0.186 | 5.755 | 0.17 % | 0.17 % |
| mquake | near_miss_neighbour | true | BP s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | BP s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | BP s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | ePC s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | ePC s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | epc1_minus_bp1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | ePC s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | near_miss_neighbour | true | epc2_minus_bp2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | paraphrase | new | BP s0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | paraphrase | new | BP s1 | 300 | 0.3 % | 0.926 | 0.000 | 0.058 | 0.926 | 0.33 % | 0.00 % |
| mquake | paraphrase | new | BP s2 | 300 | 0.3 % | 0.926 | 0.000 | 0.058 | 0.926 | 0.33 % | 0.00 % |
| mquake | paraphrase | new | ePC s0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | paraphrase | new | epc0_minus_bp0 | 300 | 5.3 % | 5.871 | 6.639 | 5.871 | 7.184 | 5.33 % | 5.33 % |
| mquake | paraphrase | new | ePC s1 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | paraphrase | new | epc1_minus_bp1 | 300 | 13.7 % | 5.399 | 7.129 | 6.652 | 7.517 | 13.67 % | 13.67 % |
| mquake | paraphrase | new | ePC s2 | 300 | 0.3 % | 1.573 | 0.000 | 0.098 | 1.573 | 0.33 % | 0.33 % |
| mquake | paraphrase | new | epc2_minus_bp2 | 300 | 13.3 % | 5.101 | 6.948 | 6.515 | 7.517 | 13.33 % | 13.33 % |
| mquake | unseen | new | BP s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | BP s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | BP s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | ePC s0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | ePC s1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | epc1_minus_bp1 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | ePC s2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| mquake | unseen | new | epc2_minus_bp2 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | edit | new | BP s0 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | BP s1 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | BP s2 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | ePC s0 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | epc0_minus_bp0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | edit | new | ePC s1 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | epc1_minus_bp1 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | edit | new | ePC s2 | 300 | 0.0 % | — | -2.208 | -2.662 | -1.792 | 0.00 % | 0.00 % |
| zsre | edit | new | epc2_minus_bp2 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | BP s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | BP s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | BP s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | ePC s0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | epc0_minus_bp0 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | ePC s1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | epc1_minus_bp1 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | ePC s2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality | true | epc2_minus_bp2 | 50 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | BP s0 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | BP s1 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | BP s2 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | ePC s0 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | epc0_minus_bp0 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | ePC s1 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | epc1_minus_bp1 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | ePC s2 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | locality_item | true | epc2_minus_bp2 | 296 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | near_miss_neighbour | true | BP s0 | 100 | 7.0 % | 3.586 | 5.418 | 4.114 | 7.749 | 6.00 % | 6.00 % |
| zsre | near_miss_neighbour | true | BP s1 | 100 | 14.0 % | 2.991 | 5.418 | 4.994 | 7.749 | 13.00 % | 11.00 % |
| zsre | near_miss_neighbour | true | BP s2 | 100 | 11.0 % | 3.070 | 5.418 | 4.616 | 7.749 | 10.00 % | 9.00 % |
| zsre | near_miss_neighbour | true | ePC s0 | 100 | 2.0 % | 5.363 | 3.026 | 1.788 | 7.749 | 2.00 % | 2.00 % |
| zsre | near_miss_neighbour | true | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | near_miss_neighbour | true | ePC s1 | 100 | 7.0 % | 2.940 | 5.202 | 3.360 | 7.749 | 6.00 % | 5.00 % |
| zsre | near_miss_neighbour | true | epc1_minus_bp1 | 100 | 6.0 % | 3.314 | 4.229 | 3.314 | 4.863 | 6.00 % | 5.00 % |
| zsre | near_miss_neighbour | true | ePC s2 | 100 | 6.0 % | 2.749 | 3.026 | 2.749 | 7.749 | 5.00 % | 4.00 % |
| zsre | near_miss_neighbour | true | epc2_minus_bp2 | 100 | 4.0 % | 3.454 | 4.229 | 2.303 | 4.863 | 4.00 % | 3.00 % |
| zsre | paraphrase | new | BP s0 | 300 | 0.3 % | 1.552 | 0.000 | -1.114 | 1.552 | 0.33 % | 0.33 % |
| zsre | paraphrase | new | BP s1 | 300 | 0.3 % | 1.552 | -1.894 | -2.009 | 1.552 | 0.33 % | 0.33 % |
| zsre | paraphrase | new | BP s2 | 300 | 0.3 % | 1.552 | 0.000 | -1.297 | 1.552 | 0.33 % | 0.33 % |
| zsre | paraphrase | new | ePC s0 | 300 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | paraphrase | new | epc0_minus_bp0 | 300 | 2.7 % | 6.165 | 6.022 | 3.082 | 7.906 | 2.67 % | 2.67 % |
| zsre | paraphrase | new | ePC s1 | 300 | 0.3 % | 1.552 | 0.000 | -0.933 | 1.552 | 0.33 % | 0.33 % |
| zsre | paraphrase | new | epc1_minus_bp1 | 300 | 2.0 % | 4.584 | 4.763 | 1.719 | 6.285 | 2.00 % | 2.00 % |
| zsre | paraphrase | new | ePC s2 | 300 | 0.0 % | — | 0.000 | -1.577 | 0.000 | 0.00 % | 0.00 % |
| zsre | paraphrase | new | epc2_minus_bp2 | 300 | 0.7 % | 4.783 | 0.000 | 0.598 | 4.804 | 0.67 % | 0.67 % |
| zsre | unseen | new | BP s0 | 100 | 4.0 % | 2.543 | 2.529 | 1.696 | 5.669 | 3.00 % | 3.00 % |
| zsre | unseen | new | BP s1 | 100 | 10.0 % | 2.890 | 5.676 | 4.044 | 6.349 | 9.00 % | 8.00 % |
| zsre | unseen | new | BP s2 | 100 | 9.0 % | 3.001 | 5.676 | 4.044 | 6.349 | 8.00 % | 7.00 % |
| zsre | unseen | new | ePC s0 | 100 | 2.0 % | 4.084 | 2.529 | 1.361 | 5.669 | 2.00 % | 2.00 % |
| zsre | unseen | new | epc0_minus_bp0 | 100 | 0.0 % | — | 0.000 | 0.000 | 0.000 | 0.00 % | 0.00 % |
| zsre | unseen | new | ePC s1 | 100 | 5.0 % | 4.007 | 5.676 | 3.339 | 6.349 | 5.00 % | 5.00 % |
| zsre | unseen | new | epc1_minus_bp1 | 100 | 4.0 % | 5.175 | 6.091 | 3.450 | 8.253 | 4.00 % | 4.00 % |
| zsre | unseen | new | ePC s2 | 100 | 4.0 % | 4.043 | 5.676 | 2.696 | 6.349 | 4.00 % | 4.00 % |
| zsre | unseen | new | epc2_minus_bp2 | 100 | 2.0 % | 5.820 | 3.436 | 1.940 | 8.253 | 2.00 % | 2.00 % |

Worst fifteen regressions at 300 edits:

| dataset | family | target | model | item | subject | D | L_frozen | L_model | fired | max rel. write |
|---|---|---|---|---|---|---|---|---|---|---|
| mquake | locality_item | true | ePC s0 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | BP s0 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | BP s2 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | ePC s1 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | BP s1 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | ePC s2 | mquake:c99d1e323c071e7dbfabf | nan | 10.12 | 5.06 | 15.18 | True | 0.127 |
| mquake | locality_item | true | ePC s2 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| mquake | locality_item | true | BP s0 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| mquake | locality_item | true | BP s2 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| mquake | locality_item | true | BP s1 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| mquake | locality_item | true | ePC s0 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| mquake | locality_item | true | ePC s1 | mquake:f05fa9a5df7b469882187 | nan | 9.40 | 4.33 | 13.73 | True | 0.123 |
| zsre | near_miss_neighbour | true | ePC s0 | zsre:0:near:83 | nan | 7.75 | 6.84 | 14.59 | True | 0.121 |
| zsre | near_miss_neighbour | true | ePC s2 | zsre:0:near:83 | nan | 7.75 | 6.84 | 14.59 | True | 0.121 |
| zsre | near_miss_neighbour | true | BP s2 | zsre:0:near:83 | nan | 7.75 | 6.84 | 14.59 | True | 0.121 |

## 8. CAP correction mechanisms [new]

Write magnitudes are the vectors actually added at the three sites at each scored prediction position (captured from the base's partial-pass call during `predict`), with ‖h_m‖ the pre-write residual row at the same position; the frozen model has structural zeros and is not fitted.

| dataset | family | model | n | fired | mean max ‖W‖ site 1 (block 4) | site 2 (block 8) | site 3 (block 12) | mean max rel. site 1 | site 2 | site 3 | P95 rel. (max over sites) | max rel. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| zsre | edit | BP reader s0 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | BP reader s0 | 300 | 293 | 7.069 | 10.658 | 47.336 | 0.1070 | 0.1054 | 0.1234 | 0.1749 | 0.2097 |
| zsre | edit | BP reader s1 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | BP reader s1 | 300 | 298 | 7.069 | 10.658 | 47.307 | 0.1071 | 0.1055 | 0.1234 | 0.1748 | 0.2097 |
| zsre | edit | BP reader s2 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | BP reader s2 | 300 | 294 | 7.069 | 10.658 | 47.313 | 0.1071 | 0.1055 | 0.1233 | 0.1741 | 0.2097 |
| zsre | edit | ePC reader s0 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | ePC reader s0 | 300 | 284 | 7.069 | 10.658 | 47.284 | 0.1070 | 0.1054 | 0.1230 | 0.1746 | 0.2097 |
| zsre | edit | ePC reader s1 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | ePC reader s1 | 300 | 292 | 7.069 | 10.658 | 47.305 | 0.1070 | 0.1054 | 0.1233 | 0.1749 | 0.2097 |
| zsre | edit | ePC reader s2 | 300 | 300 | 7.069 | 10.658 | 47.257 | 0.1075 | 0.1057 | 0.1232 | 0.1735 | 0.2306 |
| zsre | paraphrase | ePC reader s2 | 300 | 294 | 7.069 | 10.658 | 47.280 | 0.1070 | 0.1054 | 0.1231 | 0.1748 | 0.2097 |
| counterfact | edit | BP reader s0 | 300 | 300 | 7.066 | 10.658 | 44.890 | 0.1076 | 0.1043 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | BP reader s0 | 600 | 513 | 7.064 | 10.658 | 44.912 | 0.1110 | 0.1093 | 0.1176 | 0.1381 | 0.1620 |
| counterfact | edit | BP reader s1 | 300 | 297 | 7.066 | 10.658 | 44.859 | 0.1076 | 0.1044 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | BP reader s1 | 600 | 504 | 7.065 | 10.658 | 44.842 | 0.1111 | 0.1094 | 0.1172 | 0.1377 | 0.1620 |
| counterfact | edit | BP reader s2 | 300 | 300 | 7.066 | 10.658 | 44.890 | 0.1076 | 0.1043 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | BP reader s2 | 600 | 526 | 7.066 | 10.659 | 44.812 | 0.1111 | 0.1095 | 0.1173 | 0.1379 | 0.1620 |
| counterfact | edit | ePC reader s0 | 300 | 300 | 7.066 | 10.658 | 44.890 | 0.1076 | 0.1043 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | ePC reader s0 | 600 | 353 | 7.063 | 10.658 | 45.017 | 0.1104 | 0.1086 | 0.1164 | 0.1381 | 0.1620 |
| counterfact | edit | ePC reader s1 | 300 | 300 | 7.066 | 10.658 | 44.890 | 0.1076 | 0.1043 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | ePC reader s1 | 600 | 488 | 7.065 | 10.658 | 44.893 | 0.1110 | 0.1093 | 0.1174 | 0.1379 | 0.1620 |
| counterfact | edit | ePC reader s2 | 300 | 300 | 7.066 | 10.658 | 44.890 | 0.1076 | 0.1043 | 0.1199 | 0.1409 | 0.1906 |
| counterfact | paraphrase | ePC reader s2 | 600 | 410 | 7.064 | 10.658 | 45.096 | 0.1107 | 0.1088 | 0.1173 | 0.1389 | 0.1620 |
| mquake | edit | BP reader s0 | 300 | 300 | 7.070 | 10.658 | 46.249 | 0.1116 | 0.1088 | 0.1362 | 0.1835 | 0.3564 |
| mquake | paraphrase | BP reader s0 | 300 | 215 | 7.070 | 10.658 | 46.237 | 0.1071 | 0.1045 | 0.1271 | 0.1866 | 0.3582 |
| mquake | edit | BP reader s1 | 300 | 282 | 7.070 | 10.658 | 45.739 | 0.1121 | 0.1088 | 0.1344 | 0.1783 | 0.3564 |
| mquake | paraphrase | BP reader s1 | 300 | 258 | 7.070 | 10.658 | 46.293 | 0.1073 | 0.1045 | 0.1268 | 0.1839 | 0.3582 |
| mquake | edit | BP reader s2 | 300 | 300 | 7.070 | 10.658 | 46.249 | 0.1116 | 0.1088 | 0.1362 | 0.1835 | 0.3564 |
| mquake | paraphrase | BP reader s2 | 300 | 248 | 7.070 | 10.658 | 46.586 | 0.1073 | 0.1046 | 0.1288 | 0.1868 | 0.3582 |
| mquake | edit | ePC reader s0 | 300 | 300 | 7.070 | 10.658 | 46.249 | 0.1116 | 0.1088 | 0.1362 | 0.1835 | 0.3564 |
| mquake | paraphrase | ePC reader s0 | 300 | 212 | 7.070 | 10.658 | 46.444 | 0.1075 | 0.1048 | 0.1287 | 0.1874 | 0.3582 |
| mquake | edit | ePC reader s1 | 300 | 300 | 7.070 | 10.658 | 46.249 | 0.1116 | 0.1088 | 0.1362 | 0.1835 | 0.3564 |
| mquake | paraphrase | ePC reader s1 | 300 | 217 | 7.070 | 10.658 | 46.393 | 0.1074 | 0.1047 | 0.1283 | 0.1865 | 0.3582 |
| mquake | edit | ePC reader s2 | 300 | 300 | 7.070 | 10.658 | 46.249 | 0.1116 | 0.1088 | 0.1362 | 0.1835 | 0.3564 |
| mquake | paraphrase | ePC reader s2 | 300 | 208 | 7.070 | 10.658 | 46.453 | 0.1075 | 0.1049 | 0.1291 | 0.1868 | 0.3582 |

![Write norms vs difficulty and gain](../../../../../assets/extremes_analysis/ext-20261009/figures/write_norms.png)

Rank correlations (Spearman) and joint extremes:

| dataset | family | model | n | fired | ρ(frozen NLL, write) | ρ(write, gain) | ρ(frozen NLL, gain) | ρ(write, gain) fired only |
|---|---|---|---|---|---|---|---|---|
| counterfact | edit | BP s0 | 300 | 300 | +0.15 (p=0.0081) | +0.15 (p=0.0078) | +1.00 (p=0) | +0.15 (p=0.0078) |
| counterfact | edit | BP s1 | 300 | 297 | +0.14 (p=0.015) | +0.18 (p=0.0014) | +0.96 (p=9.6e-175) | +0.16 (p=0.006) |
| counterfact | edit | BP s2 | 300 | 300 | +0.15 (p=0.0081) | +0.15 (p=0.0078) | +1.00 (p=0) | +0.15 (p=0.0078) |
| counterfact | edit | ePC s0 | 300 | 300 | +0.15 (p=0.0081) | +0.15 (p=0.0078) | +1.00 (p=0) | +0.15 (p=0.0078) |
| counterfact | edit | ePC s1 | 300 | 300 | +0.15 (p=0.0081) | +0.15 (p=0.0078) | +1.00 (p=0) | +0.15 (p=0.0078) |
| counterfact | edit | ePC s2 | 300 | 300 | +0.15 (p=0.0081) | +0.15 (p=0.0078) | +1.00 (p=0) | +0.15 (p=0.0078) |
| counterfact | paraphrase | BP s0 | 600 | 513 | +0.11 (p=0.0059) | +0.47 (p=1e-34) | +0.66 (p=1.2e-76) | +0.17 (p=0.00013) |
| counterfact | paraphrase | BP s1 | 600 | 504 | +0.04 (p=0.32) | +0.48 (p=4.1e-36) | +0.60 (p=4.7e-61) | +0.13 (p=0.003) |
| counterfact | paraphrase | BP s2 | 600 | 526 | +0.10 (p=0.015) | +0.41 (p=2.8e-25) | +0.72 (p=5.6e-98) | +0.12 (p=0.0056) |
| counterfact | paraphrase | ePC s0 | 600 | 353 | +0.03 (p=0.46) | +0.82 (p=2.3e-149) | +0.30 (p=1.2e-13) | +0.22 (p=2.7e-05) |
| counterfact | paraphrase | ePC s1 | 600 | 488 | +0.12 (p=0.0042) | +0.53 (p=6.6e-45) | +0.62 (p=8.8e-65) | +0.15 (p=0.0011) |
| counterfact | paraphrase | ePC s2 | 600 | 410 | +0.06 (p=0.12) | +0.72 (p=7.7e-96) | +0.43 (p=5.1e-29) | +0.15 (p=0.0019) |
| counterfact | unseen | BP s0 | 100 | 0 | — | — | — | — |
| counterfact | unseen | BP s1 | 100 | 1 | -0.12 (p=0.23) | +1.00 (p=0) | -0.12 (p=0.23) | — |
| counterfact | unseen | BP s2 | 100 | 0 | — | — | — | — |
| counterfact | unseen | ePC s0 | 100 | 0 | — | — | — | — |
| counterfact | unseen | ePC s1 | 100 | 1 | -0.12 (p=0.23) | +1.00 (p=0) | -0.12 (p=0.23) | — |
| counterfact | unseen | ePC s2 | 100 | 0 | — | — | — | — |
| mquake | edit | BP s0 | 300 | 300 | -0.29 (p=2.8e-07) | -0.29 (p=3.4e-07) | +1.00 (p=0) | -0.29 (p=3.4e-07) |
| mquake | edit | BP s1 | 300 | 282 | -0.27 (p=1.4e-06) | -0.08 (p=0.18) | +0.86 (p=3.2e-91) | -0.30 (p=4e-07) |
| mquake | edit | BP s2 | 300 | 300 | -0.29 (p=2.8e-07) | -0.29 (p=3.4e-07) | +1.00 (p=0) | -0.29 (p=3.4e-07) |
| mquake | edit | ePC s0 | 300 | 300 | -0.29 (p=2.8e-07) | -0.29 (p=3.4e-07) | +1.00 (p=0) | -0.29 (p=3.4e-07) |
| mquake | edit | ePC s1 | 300 | 300 | -0.29 (p=2.8e-07) | -0.29 (p=3.4e-07) | +1.00 (p=0) | -0.29 (p=3.4e-07) |
| mquake | edit | ePC s2 | 300 | 300 | -0.29 (p=2.8e-07) | -0.29 (p=3.4e-07) | +1.00 (p=0) | -0.29 (p=3.4e-07) |
| mquake | paraphrase | BP s0 | 300 | 215 | -0.12 (p=0.034) | +0.50 (p=2.6e-20) | +0.60 (p=1.1e-30) | -0.33 (p=7.8e-07) |
| mquake | paraphrase | BP s1 | 300 | 258 | -0.22 (p=9.6e-05) | +0.13 (p=0.024) | +0.76 (p=1.1e-56) | -0.36 (p=3e-09) |
| mquake | paraphrase | BP s2 | 300 | 248 | -0.24 (p=2.9e-05) | +0.22 (p=0.00016) | +0.70 (p=1.1e-45) | -0.37 (p=1.2e-09) |
| mquake | paraphrase | ePC s0 | 300 | 212 | -0.15 (p=0.01) | +0.51 (p=1.7e-21) | +0.57 (p=3.9e-27) | -0.35 (p=2.3e-07) |
| mquake | paraphrase | ePC s1 | 300 | 217 | -0.12 (p=0.034) | +0.47 (p=6.2e-18) | +0.61 (p=3.6e-32) | -0.37 (p=2e-08) |
| mquake | paraphrase | ePC s2 | 300 | 208 | -0.12 (p=0.031) | +0.52 (p=7.4e-22) | +0.57 (p=2.6e-27) | -0.39 (p=5e-09) |
| mquake | unseen | BP s0 | 100 | 0 | — | — | — | — |
| mquake | unseen | BP s1 | 100 | 0 | — | — | — | — |
| mquake | unseen | BP s2 | 100 | 0 | — | — | — | — |
| mquake | unseen | ePC s0 | 100 | 0 | — | — | — | — |
| mquake | unseen | ePC s1 | 100 | 0 | — | — | — | — |
| mquake | unseen | ePC s2 | 100 | 0 | — | — | — | — |
| zsre | edit | BP s0 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | edit | BP s1 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | edit | BP s2 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | edit | ePC s0 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | edit | ePC s1 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | edit | ePC s2 | 300 | 300 | -0.22 (p=0.00015) | -0.22 (p=0.00016) | +1.00 (p=0) | -0.22 (p=0.00016) |
| zsre | paraphrase | BP s0 | 300 | 293 | -0.16 (p=0.0054) | -0.09 (p=0.11) | +0.97 (p=2.9e-177) | -0.17 (p=0.003) |
| zsre | paraphrase | BP s1 | 300 | 298 | -0.18 (p=0.0022) | -0.15 (p=0.0092) | +0.99 (p=3e-239) | -0.17 (p=0.0027) |
| zsre | paraphrase | BP s2 | 300 | 294 | -0.16 (p=0.0049) | -0.11 (p=0.068) | +0.97 (p=4.6e-189) | -0.17 (p=0.0028) |
| zsre | paraphrase | ePC s0 | 300 | 284 | -0.14 (p=0.018) | +0.02 (p=0.74) | +0.91 (p=1e-116) | -0.16 (p=0.0086) |
| zsre | paraphrase | ePC s1 | 300 | 292 | -0.14 (p=0.012) | -0.08 (p=0.15) | +0.97 (p=6.7e-189) | -0.17 (p=0.0028) |
| zsre | paraphrase | ePC s2 | 300 | 294 | -0.15 (p=0.011) | -0.10 (p=0.091) | +0.98 (p=9.1e-207) | -0.17 (p=0.0042) |
| zsre | unseen | BP s0 | 100 | 4 | +0.04 (p=0.72) | -1.00 (p=7.7e-159) | -0.04 (p=0.68) | — |
| zsre | unseen | BP s1 | 100 | 14 | +0.06 (p=0.58) | -0.48 (p=4.6e-07) | -0.03 (p=0.79) | -0.73 (p=0.0029) |
| zsre | unseen | BP s2 | 100 | 11 | +0.05 (p=0.61) | -0.67 (p=4.3e-14) | -0.07 (p=0.49) | -0.66 (p=0.026) |
| zsre | unseen | ePC s0 | 100 | 2 | +0.22 (p=0.031) | -1.00 (p=0) | -0.22 (p=0.031) | — |
| zsre | unseen | ePC s1 | 100 | 5 | +0.16 (p=0.11) | -1.00 (p=3e-157) | -0.16 (p=0.11) | — |
| zsre | unseen | ePC s2 | 100 | 4 | +0.10 (p=0.34) | -1.00 (p=3.3e-182) | -0.10 (p=0.32) | — |

| dataset | model | n (locality-type probes) | |A| | |B| | |A∩B| | P(A) | P(A|B) | tail lift | A | B |
|---|---|---|---|---|---|---|---|---|---|---|
| counterfact | BP s0 | 1150 | 0 | 4 | 0 | 0.000 | 0.000 | — | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| counterfact | BP s1 | 1150 | 0 | 6 | 0 | 0.000 | 0.000 | — | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| counterfact | BP s2 | 1150 | 0 | 1 | 0 | 0.000 | 0.000 | — | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| counterfact | ePC s0 | 1150 | 1 | 11 | 1 | 0.001 | 0.091 | 104.55 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| counterfact | ePC s1 | 1150 | 4 | 21 | 4 | 0.003 | 0.190 | 54.76 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| counterfact | ePC s2 | 1150 | 0 | 5 | 0 | 0.000 | 0.000 | — | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | BP s0 | 850 | 42 | 43 | 42 | 0.049 | 0.977 | 19.77 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | BP s1 | 850 | 43 | 43 | 43 | 0.051 | 1.000 | 19.77 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | BP s2 | 850 | 45 | 46 | 45 | 0.053 | 0.978 | 18.48 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | ePC s0 | 850 | 43 | 44 | 43 | 0.051 | 0.977 | 19.32 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | ePC s1 | 850 | 46 | 48 | 46 | 0.054 | 0.958 | 17.71 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| mquake | ePC s2 | 850 | 44 | 45 | 44 | 0.052 | 0.978 | 18.89 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | BP s0 | 546 | 11 | 12 | 11 | 0.020 | 0.917 | 45.50 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | BP s1 | 546 | 24 | 35 | 24 | 0.044 | 0.686 | 15.60 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | BP s2 | 546 | 20 | 27 | 20 | 0.037 | 0.741 | 20.22 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | ePC s0 | 546 | 4 | 5 | 4 | 0.007 | 0.800 | 109.20 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | ePC s1 | 546 | 12 | 13 | 12 | 0.022 | 0.923 | 42.00 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |
| zsre | ePC s2 | 546 | 10 | 11 | 10 | 0.018 | 0.909 | 49.64 | any locality deterioration (fewer than 10 % of probes deteriorate; most abstain) | any nonzero write (fewer than 10 % fire) |

## 9. MQuAKE reasoning and sequential behaviour

MQuAKE's registered composition endpoint teaches each case's dependency edits from a fresh start state and asks all three multi-hop questions (all-question success; any-question and question-level rates are additional, not replacements). The Stage-4 v5 reader scored 0/80 all-question and 2/240 question-level at 300 edits in realization 0 **[record]**. The same aggregation applied to this study's six readers (family EXT) and to the fifteen Stage-4 cells (context) is below; `frozen_question_*` are the cap-off (frozen) exact rates on the same questions recorded by the endpoint itself. A failed multi-hop question is not by itself a cap failure, since GPT-2 small may lack the compositional step: the frozen model answers none of the questions with either the old or the new answer.

| model | family | stratum | cases | questions | question accuracy | any-question success | all-question success | old answer reappeared | frozen: new exact | frozen: old exact |
|---|---|---|---|---|---|---|---|---|---|---|
| BP reader s0 | EXT | all | 80 | 240 | 0.0 % (0/240) | 0.0 % (0/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s0 | EXT | hops=2 | 61 | 183 | 0.0 % (0/183) | 0.0 % (0/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s0 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s0 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s0 | EXT | n_edits=1 | 78 | 234 | 0.0 % (0/234) | 0.0 % (0/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s0 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | hops=2 | 61 | 183 | 1.1 % (2/183) | 1.6 % (1/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | n_edits=1 | 78 | 234 | 0.9 % (2/234) | 1.3 % (1/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s1 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | hops=2 | 61 | 183 | 1.1 % (2/183) | 1.6 % (1/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | n_edits=1 | 78 | 234 | 0.9 % (2/234) | 1.3 % (1/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| BP reader s2 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | all | 80 | 240 | 0.0 % (0/240) | 0.0 % (0/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | hops=2 | 61 | 183 | 0.0 % (0/183) | 0.0 % (0/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | n_edits=1 | 78 | 234 | 0.0 % (0/234) | 0.0 % (0/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s0 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | all | 80 | 240 | 0.4 % (1/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | hops=2 | 61 | 183 | 0.5 % (1/183) | 1.6 % (1/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | n_edits=1 | 78 | 234 | 0.4 % (1/234) | 1.3 % (1/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s1 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | hops=2 | 61 | 183 | 1.1 % (2/183) | 1.6 % (1/61) | 0.0 % (0/61) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | hops=3 | 16 | 48 | 0.0 % (0/48) | 0.0 % (0/16) | 0.0 % (0/16) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | hops=4 | 3 | 9 | 0.0 % (0/9) | 0.0 % (0/3) | 0.0 % (0/3) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | n_edits=1 | 78 | 234 | 0.9 % (2/234) | 1.3 % (1/78) | 0.0 % (0/78) | 0.0 % | 0.0 % | 0.0 % |
| ePC reader s2 | EXT | n_edits=2 | 2 | 6 | 0.0 % (0/6) | 0.0 % (0/2) | 0.0 % (0/2) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:0-100 | S4 | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:0-101 | S4 | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:0-102 | S4 | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:0-103 | S4 | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:0-104 | S4 | all | 80 | 240 | 0.8 % (2/240) | 1.2 % (1/80) | 0.0 % (0/80) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:1-100 | S4 | all | 84 | 252 | 0.4 % (1/252) | 1.2 % (1/84) | 0.0 % (0/84) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:1-101 | S4 | all | 84 | 252 | 0.4 % (1/252) | 1.2 % (1/84) | 0.0 % (0/84) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:1-102 | S4 | all | 84 | 252 | 0.4 % (1/252) | 1.2 % (1/84) | 0.0 % (0/84) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:1-103 | S4 | all | 84 | 252 | 0.4 % (1/252) | 1.2 % (1/84) | 0.0 % (0/84) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:1-104 | S4 | all | 84 | 252 | 0.4 % (1/252) | 1.2 % (1/84) | 0.0 % (0/84) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:2-100 | S4 | all | 88 | 264 | 0.0 % (0/264) | 0.0 % (0/88) | 0.0 % (0/88) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:2-101 | S4 | all | 88 | 264 | 0.0 % (0/264) | 0.0 % (0/88) | 0.0 % (0/88) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:2-102 | S4 | all | 88 | 264 | 0.0 % (0/264) | 0.0 % (0/88) | 0.0 % (0/88) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:2-103 | S4 | all | 88 | 264 | 0.0 % (0/264) | 0.0 % (0/88) | 0.0 % (0/88) | 0.0 % | 0.0 % | 0.0 % |
| v5_stage4:2-104 | S4 | all | 88 | 264 | 0.0 % (0/264) | 0.0 % (0/88) | 0.0 % (0/88) | 0.0 % | 0.0 % | 0.0 % |

![MQuAKE PC-reader evaluations](../../../../../assets/extremes_analysis/ext-20261009/figures/mquake_pcreader.png)

Sequential behaviour along the real teaching order (order 100) **[recomputed]** from the per-edit records:

| dataset | reader | edits | immediate ES | immediate paraphrase score | ES failures | consecutive failures | ACF(gs) lag 1 | lag 2 | lag 3 |
|---|---|---|---|---|---|---|---|---|---|
| counterfact | bp s0 | 300 | 100.0 % | 83.8 % | 0 | 0 | 0.08 | -0.06 | -0.07 |
| counterfact | bp s1 | 300 | 99.0 % | 82.7 % | 3 | 0 | -0.02 | -0.01 | -0.09 |
| counterfact | bp s2 | 300 | 100.0 % | 84.8 % | 0 | 0 | -0.01 | -0.08 | 0.01 |
| counterfact | epc s0 | 300 | 100.0 % | 56.3 % | 0 | 0 | -0.04 | 0.08 | -0.05 |
| counterfact | epc s1 | 300 | 100.0 % | 78.3 % | 0 | 0 | 0.01 | -0.03 | -0.17 |
| counterfact | epc s2 | 300 | 100.0 % | 66.5 % | 0 | 0 | -0.09 | 0.08 | 0.01 |
| mquake | bp s0 | 300 | 100.0 % | 62.0 % | 0 | 0 | -0.02 | -0.00 | -0.01 |
| mquake | bp s1 | 300 | 91.0 % | 72.3 % | 27 | 3 | 0.02 | -0.00 | 0.05 |
| mquake | bp s2 | 300 | 100.0 % | 67.0 % | 0 | 0 | 0.02 | -0.06 | -0.02 |
| mquake | epc s0 | 300 | 100.0 % | 58.7 % | 0 | 0 | 0.02 | -0.04 | -0.03 |
| mquake | epc s1 | 300 | 100.0 % | 59.0 % | 0 | 0 | 0.02 | -0.02 | -0.02 |
| mquake | epc s2 | 300 | 100.0 % | 57.3 % | 0 | 0 | 0.02 | -0.03 | -0.07 |
| zsre | bp s0 | 300 | 100.0 % | 97.3 % | 0 | 0 | -0.03 | -0.03 | -0.03 |
| zsre | bp s1 | 300 | 100.0 % | 99.3 % | 0 | 0 | -0.01 | -0.01 | -0.01 |
| zsre | bp s2 | 300 | 100.0 % | 97.7 % | 0 | 0 | -0.02 | -0.02 | -0.02 |
| zsre | epc s0 | 300 | 100.0 % | 94.7 % | 0 | 0 | -0.06 | 0.08 | -0.06 |
| zsre | epc s1 | 300 | 100.0 % | 96.7 % | 0 | 0 | 0.07 | 0.07 | -0.03 |
| zsre | epc s2 | 300 | 100.0 % | 97.3 % | 0 | 0 | -0.03 | 0.10 | -0.03 |

The ordinary-text assay is not a time series (context resets every window), so no sequential extreme analysis is manufactured there.

## 10. Connection with nonlinear statistical coupling (Nelson) [new, supplementary]

For every eligible GPD fit in this study the informational-scale condition −σ·d/dz ln f(z) at z = σ equals 1 (for the density f(z) = σ⁻¹(1 + κz/σ)^(−1/κ−1) this holds identically; checked numerically for 10 fits, all hold: True). The fitted σ is the scale of exceedances above the chosen threshold, not a threshold-free scale of the full loss distribution; shapes and scales are tabulated separately in sections 6.1–6.3. The GPD shape κ is Nelson's nonlinear coupling parameter in the one-dimensional α = 1 family; a fitted κ > 0 gives a modelled survival exponent 1/κ and must not be confused with the stretching parameter α.

Exploratory coupled-entropy profile (discrete, α = 1, k = 1; q(κ) = (1+2κ)/(1+κ); H_κ(p) = [1/Σ p_j^q − 1]/κ; Shannon at κ = 0; self-tests: {"point_mass_zero": true, "shannon_at_zero": true, "uniform_closed_form": true, "convergence_to_shannon": true, "rejects_unnormalized": true}), computed on the relation/new-target/subject frequency vectors of each population (`tables/coupled_entropy_profiles.csv`, 60 rows). Increasing κ lowers H_κ for every non-uniform distribution and compresses differences between distributions with many rare categories; e.g. for the CounterFact eligible relation distribution H_0 = 3.409 and H_1 = 4.402. This is a sensitivity study of empirical categorical distributions, not a calibrated entropy of the system and not evidence for the paper's universal-entropy theorem; it is kept apart from the HT-17 fits. The earlier bounded κ-surprisal pilot **[record]** is not a test of the coupled-entropy objective.

## 11. Discussion and conclusions

**What the results establish.** On GPT-2 small, both reader caps install the taught facts (own-prompt per-token loss ≈ 0.01 nats against ≈ 6 for the frozen model) and are exactly the frozen model where they abstain. The ePC- and BP-trained readers differ in gating, not in the installed corrections (the memory payloads are produced by the same adjoint rule, so own-prompt losses coincide across all six readers). The frozen record's negative CounterFact result for ePC reader training is reproduced in the per-probe losses and persists across difficulty deciles, on the frozen model's hardest cases and in the regression tails; on zsRE the two rules are close. No analysis in this study isolates a rare-event regime in which ePC reader training is reliably better than BP reader training; the measured cost difference (≈ 100×) is unchanged.

Per-dataset paired contrasts at 300 edits (seed-level intervals from 2,000 item-group bootstrap draws; three seeds share one subject population):

- **zsre:** paraphrase-prompt contrast ePC − BP (positive favours ePC), seed mean -0.076 [-0.136, -0.027] nats/token (seed 0: -0.159 [-0.282, -0.055]; seed 1: -0.092 [-0.176, -0.023]; seed 2: 0.021 [-0.048, 0.099]). On the frozen model's hardest 5 % of paraphrases, mean per-token loss falls from 11.37 (frozen) to 0.05 (BP, seed mean) and 0.05 (ePC); exact-match success there is 100.0 % (BP) vs 100.0 % (ePC). ePC-minus-BP deteriorations above 1 nat/token occur on 2.7 %, 2.0 %, 0.7 % of paraphrases (seeds 0–2); ePC is better than BP by more than 1 nat/token on 0.3 %, 0.0 %, 1.0 %.
- **counterfact:** paraphrase-prompt contrast ePC − BP (positive favours ePC), seed mean -1.117 [-1.313, -0.916] nats/token (seed 0: -1.821 [-2.168, -1.447]; seed 1: -0.149 [-0.357, 0.057]; seed 2: -1.379 [-1.666, -1.085]). On the frozen model's hardest 5 % of paraphrases, mean per-token loss falls from 10.42 (frozen) to 2.05 (BP, seed mean) and 2.78 (ePC); exact-match success there is 78.9 % (BP) vs 74.4 % (ePC). ePC-minus-BP deteriorations above 1 nat/token occur on 28.5 %, 8.2 %, 22.3 % of paraphrases (seeds 0–2); ePC is better than BP by more than 1 nat/token on 3.5 %, 4.8 %, 3.3 %.
- **mquake:** paraphrase-prompt contrast ePC − BP (positive favours ePC), seed mean -0.495 [-0.651, -0.347] nats/token (seed 0: -0.090 [-0.299, 0.106]; seed 1: -0.718 [-0.943, -0.502]; seed 2: -0.677 [-0.882, -0.486]). On the frozen model's hardest 5 % of paraphrases, mean per-token loss falls from 10.17 (frozen) to 3.13 (BP, seed mean) and 3.13 (ePC); exact-match success there is 33.3 % (BP) vs 33.3 % (ePC). ePC-minus-BP deteriorations above 1 nat/token occur on 5.3 %, 13.7 %, 13.3 % of paraphrases (seeds 0–2); ePC is better than BP by more than 1 nat/token on 4.3 %, 0.3 %, 0.0 %.

**Extremes.** The caps' collateral effects on ordinary text are rare and sometimes severe (HT-17 reproduced exactly; new MQuAKE rows in 6.2); the per-probe loss tails are dominated by the frozen model's own difficulty, with GPD shapes near zero. Severe per-probe regressions are concentrated on prompts where a wrong or stale record fired, which is why they correlate with write magnitude rather than with frozen difficulty.

**What remains uncertain.** One realization, one order, three training seeds; MQuAKE PC-reader results are new and unreplicated; tail shapes are finite-range; the frozen model's exact-match rates are uninformative on these prompts; transfer beyond GPT-2 small is not established. Figures with fewer than 100 exceedances are marked exploratory or insufficient in the tables.

## 12. Reproducibility appendix

- **Code:** `pc_cap/aw/extremes/` at revision `507504c8cae8`; tests `aw/tests/test_extremes_stats.py` (CPU) and `aw/extremes/validate_gpu.py` (GPU; record in `validation/gpu_checks.json`).
- **Commands:** `results/extremes_analysis/ext-20261009/scripts/run_gpu_chain.sh` (frozen scoring → reader scoring → MQuAKE evaluations → MQuAKE scoring) and `scripts/run_cpu_pipeline.sh` (assemble → paired → tails → datasets → nelson → figures → report). Environment: Python 3.12.15, jax/jaxlib 0.11.1, numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, pyarrow 25.0.1, matplotlib 3.11.1; RTX 5070 (12 GiB), driver 615.71.09.
- **Inputs (hash-checked at load):** sealed recipes `docs/tasks/R1-final-cell-recipes/{61348508…, ce0d0ffc…, 43925e53…}.json` and their payloads; reader artifacts `assets/runs/additional_work/PC-reader/train-*/theta_avg150-300.npz`; memory snapshots `…/eval-*/stream/checkpoint-{100,300}.snapshot`; harm vectors `results/additional_work/PC-reader/eval-*/harm/vectors.npz`; HT-17 `logs/additional_work/HT-17/snapshot-20261004-complete/report.json`.
- **Outputs:** parquet under `assets/extremes_analysis/ext-20261009/data/` (example manifest = `scores.parquet` metadata columns + `case_populations.parquet`; `scores.parquet`, `generations.parquet`, `paired_cases.parquet`, `dataset_statistics.parquet`, `tail_fits.parquet`, `bootstrap_results.parquet`, `paired_gains.parquet`, `difficulty_deciles.parquet`); CSV tables under `tables/`; figures under `assets/extremes_analysis/ext-20261009/figures/` with `captions.json`; raw per-probe records as JSONL chunks with a hash manifest under `assets/extremes_analysis/ext-20261009/checkpoints/scores/`; MQuAKE evaluation receipts under `results/extremes_analysis/ext-20261009/mquake_eval/`.
- **Data dictionary:** `reports/data_dictionary.md`. **Artifact registry:** `manifest.json` (72 artifacts with SHA-256).
- **Formulas:** §3 (losses, margins), §6 (harm, ES99+, GPD), §7 (gains, D, CVaR, deciles), §10 (coupled entropy). Natural logarithms throughout.
