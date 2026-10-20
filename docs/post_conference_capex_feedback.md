# Capex's feedback on the post-conference programme underway

20 October 2026 · for charlie, Capstan and Derp Peoples

**I support proceeding with Capstan's narrower programme.** A shared small-reader harness, selection diagnostics, and a controlled continual-learning comparison are a better immediate investment than opening all the branches in my earlier proposal. My recommendations below modify that programme; they do not replace it or ask us to restart planning.

There are three evidence corrections to make before the affected analyses are used, and two design questions to settle before training. The most consequential finding is that **most of the reported severe MQuAKE item-locality deteriorations are on prompts explicitly taught elsewhere in the same memory, but scored against their old answers**. Treating these as examples on which the cap should abstain would introduce contradictory training labels.

I read [Capstan's proposal](post_conference_capstan_proposal.md), [Derp Peoples' review of it](post_conference_capstan_review.md), [the earlier review](post_conference_research_plan_review.md), my original plan, the current `ongoing.md` entry, and the relevant implementation and saved results. The checkout reviewed was `f9f9589`; its latest status entry says no GPU work had started when that entry was written. charlie's current message establishes that the programme is now proceeding; this review does not infer live GPU status from that older entry.

During this review, Capstan's new [Phase 0 loader](../aw/post_conference/common.py) appeared in the working tree. I read it without editing it. Its separation of candidate presence from the top record already addresses part of §2 below; that is useful progress, not an additional change I am asking Capstan to duplicate.

The numerical checks below used only saved files, with zero model calls. The [audit script](../scripts/post_conference_capex_review_audit.py) and [machine-readable evidence](../logs/post_conference/capex_review_20261020.json) record the counts and 403 source-file hashes, including verification against the saved scoring-chunk hashes. Historical reports, Capstan's files, and experiment code have not been changed.

## 1. Correct the MQuAKE locality interpretation before adding hard negatives

Capstan §2.7 describes the 600 item-locality rows as same-subject, different-relation prompts. In this particular prepared population:

- All **600** locality rows have the **same relation as their parent edit**, and none has the same subject as its parent.
- **40 rows, covering 39 distinct prompts**, exactly duplicate prompts taught elsewhere among the 300 stream edits.
- All 40 carry old-answer aliases disjoint from the new aliases taught for those prompts.
- There are **560 remaining rows**. This is an exact-prompt partition, not a claim that those remaining rows have passed every possible semantic-overlap check.

For example, the source prompt is **“The origianl broadcaster of The Flintstone Kids is”** (source spelling retained). A locality row scores **“American Broadcasting Company”**, while the same memory has deliberately taught **“British Broadcasting Corporation”** for that exact prompt. A correction that produces the newly taught answer can therefore count as severe deterioration against the old locality target.

I paired each saved cap score with the frozen score for the same probe and target. “Severe” below means the mean target-token NLL, including the terminator, increased by more than two nats.

| Reader | Severe events, all 600 rows | On the 40 taught-prompt overlap rows | On the remaining 560 rows |
|---|---:|---:|---:|
| BP seed 0 | 31 | 31 | 0 |
| BP seed 1 | 32 | 31 | 1 |
| BP seed 2 | 34 | 31 | 3 |
| PC seed 0 | 32 | 31 | 1 |
| PC seed 1 | 35 | 31 | 4 |
| PC seed 2 | 34 | 31 | 3 |

Thus **93/97 BP events and 93/101 PC events** fall on the conflicting rows. All six readers fire on all 40 overlap rows. These are repeated observations across seeds, not that many independent facts. The original 600 rows contain 574 distinct prompt strings.

**Modification:** make Phase 0 item 4 a *locality-population and target-consistency audit*, not an already diagnosed same-subject training failure. Keep the historical all-row table, then report the taught-prompt overlap and nonoverlap strata separately, with the changed denominators. Audit the other datasets by the same principle. Add a short interpretation addendum to the cap-value report when the collaborators have checked this finding; do not silently replace its historical numbers.

Hard negatives remain useful, but their labels must reflect the **whole active memory at the evaluation horizon**. A prompt that should invoke another taught record is a positive for that record, not a null example merely because it is unrelated to the parent edit. Genuine same-subject/different-relation negatives would be a new, explicitly constructed development population. The reported severe-event counts do not currently establish that this is the principal missing negative type.

This changes the practical target: the proposed “≤3 severe MQuAKE locality events per seed” is already approximately reached on the exact-prompt nonoverlap stratum. Define the valid preservation population before deciding how much improvement is needed.

## 2. Use actual selected records for the failure atlas and gate curves

The saved `selected_own_record` column is misleadingly named. In [the assembler](../aw/extremes/assemble.py), it checks whether the own record appears **anywhere in `record_ids`**, the retrieved candidate list. It does not check the winning weight or whether the gate accepted the candidate.

The distinction occurs in the saved data. At 300 edits, among CounterFact's 900 edit-plus-paraphrase rows per reader, the own record is in the candidate list but is not the highest-weight candidate on:

| Rule | Seed 0 | Seed 1 | Seed 2 |
|---|---:|---:|---:|
| BP | 49 | 53 | 31 |
| PC | 35 | 39 | 36 |

**Modification:** derive separate fields from raw chunk `selection.record_ids`, `weights`, and `hard_null`: own-record candidate recall; pre-veto winning record; gate acceptance; and applied correct/wrong record. The [existing selection trace](../src/pccap/revision_v1/selection_trace.py) already makes this distinction. Preserve the legacy column's meaning and use corrected names in new analyses. This is necessary to avoid misclassifying retrieval failures as payload failures.

The new Phase 0 loader now supplies `own_in_candidates` and `own_is_top`; retain this implementation and combine the latter with gate acceptance in downstream summaries.

For the threshold sweep:

1. Separate **selection risk** (wrong record among accepted queries) from **answer risk** (failed generation or increased NLL after application). Report both against coverage, separately for edits, paraphrases and preservation populations.
2. Respect all gates. The [learner](../src/pccap/revision_v1/learner.py) combines null probability, an optional score threshold, and a rare-token gate. A rare-token verdict may not have been evaluated when an earlier gate already rejected the query; saved null probability alone cannot reconstruct every relaxed decision.
3. Obtain the missing counterfactual output before claiming how previously rejected queries would perform when accepted. Their saved answer is the frozen answer, not the result of applying their candidate.
4. Exploit the present **one-selection, hard-top-1, binary-write** deployment rule: for a fixed memory and candidate, score the candidate-on and cap-off outcomes once, then compose many hard-threshold operating points on CPU. Verify agreement with the original operating point first. This shortcut applies to a threshold-only intervention; changing candidates, write mass or inference dynamics needs new scoring.
5. Use paired uncertainty estimates and report the original operating point. Coincident curves would support similar trade-offs on this population, **not prove identical gates or representations**. Likewise, different historical curves may partly reflect arm-specific acquired payloads; an agreed fixed-payload diagnostic helps isolate selection.

These changes should preserve the priority of the frontier analysis while reducing unnecessary repeated GPU passes.

## 3. Replace the bank-to-bank chaining diagnostic

Capstan §2.6 describes later banks retrieving from activations modified by earlier writes. That is not the read path used by the six trained readers in the supplement.

[Model reconstruction](../aw/extremes/models.py) loads `InterfaceCap`, which inherits [RevisionCap](../src/pccap/revision_v1/learner.py). It:

1. Computes features from a **write-free** base pass.
2. Chooses the record and null decision once at the prompt.
3. Caches that selection for all answer positions.
4. Applies the chosen record's writes at the three sites.

Earlier writes affect later transformer computation, but **do not cause bank 2 or bank 3 to retrieve a different record**. The historical v0 retrieval-drift question is a different architecture. A negative search for this chain in current logs would follow from the implementation, not establish a learned failure of composition.

**Modification:** replace Phase 0 item 5 with a short architecture/dependency audit: confirm which edited dependencies are present and individually usable, and document the single-selection limitation. The [registered composition evaluation](../aw/extremes/mquake_eval.py) uses independent fresh-start dependency-edit states; it is not simply a query into the final 300-edit stream memory. Also distinguish *all rewrite dependencies available* from *every factual hop explicitly stored*.

An actual iterative-retrieval or symbolic-join intervention remains a new composition experiment. Do not gate it on discovering a cross-bank retrieval mechanism this reader does not implement. No GPU time is needed to establish the architectural limitation.

## 4. Make the cached harness's objective explicit; prioritize H2 unless H1 passes a small feasibility check

The feature cache is a sound investment. It does **not**, by itself, preserve the current training objective. In [the episodic trainer](../src/pccap/revision_v1/train.py), retrieval classification can use cached features, but answer NLL and preservation KL call GPT-2 with the **current writes**. Fixed unedited features and cap-off logits cannot supply those corrected outputs for arbitrary new writes.

**Modification:** initially define the harness as **record/null selection training on frozen observations**, with both rules using the same supervised labels and fixed payloads. Evaluate shortlisted readers through GPT-2 for actual answer accuracy and collateral harm. A table of precomputed candidate-on outcomes can support a declared fixed-candidate cost-sensitive objective; it is not the original differentiable answer/preservation objective. Keep genuine output entropy, KL and NLL distinct from selection-classification metrics. Training cost includes feature extraction and final model evaluation.

### H1 needs a nontrivial target-free energy

The claim that standard PC automatically supplies a useful query-time energy confidence score needs a concrete model. For the simple feedforward predictive-coding energy

`E(z; x) = ½ Σ_l ||z_l − f_l(z_(l−1))||²`, with `z_0 = x`,

setting each free state to its feedforward prediction makes every residual zero. This works for familiar and unfamiliar inputs alike. Starting there and leaving the output unclamped provides no nontrivial settling signal. This is an algebraic consequence of that energy, not an empirical result about the proposed reader.

A generative model that reconstructs observed query features conditional on candidate records, an explicit null hypothesis, or another specified constraint could avoid this degeneracy. It would require defined test-time observations, comparable candidate/null energies, normalization and calibration. A small terminal gradient means the solver has settled; it is not automatically evidence that its answer is correct.

**Modification:** before investing in H1, demonstrate nontrivial, label-free inference on a tiny fixture with relevant, irrelevant and ambiguous queries. The gold record/answer must be unavailable to this inference. Keep the BP unrolled-refinement control with the same information, energy architecture, inference budget and tuning allowance. Iteration and energy scoring are not capabilities that BP-trained models inherently lack.

If that fixture is not ready, **run H2 first**. Learning by settling activities before changing weights is already a specific, implementable hypothesis. Song and colleagues report reduced interference in their prospective-configuration experiments; that motivates a transfer test here rather than guaranteeing one. Their discussion also distinguishes such learning from limiting regimes designed to approximate BP. [Primary study](https://www.nature.com/articles/s41593-023-01514-1).

### H2 needs consistent keys, comparable adaptation, and honest memory costs

The current reader uses tied query/key embeddings. Updating its weights can make stored keys stale. [RecordStore](../src/pccap/revision_v1/memory.py) supports rebuilding keys, but the new online harness must make this policy explicit.

- Recompute keys from immutable cached base observations after each update, or freeze the key representation in **both** arms. Charge rebuild time and retained observations to cost/memory.
- Hold payloads and their acquisition policy fixed while testing reader learning. Separate failure to retrieve an old record from forgetting caused by eviction or a deliberate fact revision.
- Compare old-task retention at matched **new-task learning**, as well as equal updates and measured compute. A method that changes less can preserve old performance by failing to learn the new block.
- Include BP/PC without replay first; if replay is used to interpret a difference, compare BP/PC with the same small replay budget. Do not infer the value of locality from BP+replay versus PC alone.
- Count feature caches, source tokens, optimizer state and any replay data used by the algorithm. Distinguish a persistent memory record used for inference from revisiting it as a training example.

I would change Derp Peoples' suggested synthetic-to-real gate: require working learning, measurable interference and an interpretable comparison, **not a favorable PC–BP gap**. Selecting only synthetic settings where PC wins would bias the research programme. A clear null can still justify one bounded real-data transfer test.

## 5. Correct the baseline targets and account for unavailable logs

The ordinary-text ES99+ baseline in Capstan §4, “≤0.02 nats (these readers),” only describes zsRE. Direct averages of the three saved seeds are:

| Dataset | BP ES99+ | PC ES99+ |
|---|---:|---:|
| zsRE | 0.01426 | 0.00162 |
| CounterFact | 0.29301 | 0.32660 |
| MQuAKE | 0.23017 | 0.23219 |

Source: [ordinary-text harm table](../results/extremes_analysis/ext-20261009/tables/cap_value/harm_unrelated_text.csv). ES99+ is the mean of the worst 1% of nonnegative per-position loss increases, over the declared ordinary-text population; it is not the overall mean harm. Seed variation is substantial and is retained in the audit JSON.

**Modification:** use dataset-specific baselines, paired seed comparisons and explicitly proposed improvement targets. Keep the CounterFact/MQuAKE retention goals as aspirations until the attainable frontier and payload ceiling are known. Label the 8–21% / 3–8% near-miss firing ranges as the stated **zsRE** observation, not a universal three-dataset baseline.

Two further corrections:

- The CounterFact paraphrase **PC loss** is approximately 2.43 nats/token; the **PC–BP loss gap** is approximately **1.12**, not 2.4. Both Capstan's proposal and Derp's second review repeat the latter wording.
- Acquisition threshold details exist in the `RevisionCap.update_item` return object, but [the evaluation runner](../aw/trained_reader_eval.py) serializes only `code`, `codes`, and `returned_cost` into each saved `outcome`. I checked all 300 records in all six MQuAKE reader streams: those prefix losses/threshold flags are not in those saved outcomes. The cited older `cap.learn.update_item` is not the relevant learned-reader path.

For Phase 0, mark that acquisition-history readout unavailable in these artifacts unless another trace is found. Forward-only forced-record support scoring can measure **current payload adequacy**, but cannot recreate the missing historical stopping trace. Do not silently add acquisition reruns to a “no-training, forward-only” budget.

The completed ePC contrast remains valid evidence about a particular finite-step training procedure. Retiring it as the next large reader-training instrument is sensible. However, using AdamW in both arms does not make learning dynamics identical, and calling ePC “just a noisier gradient” assumes a relation to BP that has not been established for every setting. Describe the actual estimator and its global autodiff cost; do not discard the result as not PC. The ePC paper explicitly develops the error-state formulation for digital simulation. [Primary paper](https://arxiv.org/html/2505.20137v5).

For the new small implementation, compare activation-state and error-state versions of the **same small model and energy**. Equilibria should agree under the stated assumptions; finite-step trajectories and convergence speeds need not. Reusing the whole GPT-2 solver as the required numerical oracle would defeat the purpose.

## 6. Keep the in-context arm, with matched retrieval and observable costs

I agree with making retrieved context a full comparator and with Derp's request to report context tokens, latency and peak memory.

**Modification:** first send the **same selected record and same abstention decision** to either the cap write mechanism or a factual-text context wrapper. This isolates how the supplied fact is used. Report an end-to-end retriever-plus-context arm separately if it uses a different retriever. Gold-record context is an oracle diagnostic, not the deployed comparator.

Use exactly the taught support fact and aliases available to the cap; do not supply the query's gold paraphrase answer or an undisclosed gold reasoning path. Choose a small context-format allowance on development examples, then lock it. Score only the common answer tokens, preserving the newline/termination convention, rather than including the added context in the loss denominator.

Include preservation queries when retrieval supplies an irrelevant fact, and preserve the no-retrieval behavior. Report retrieval and generation costs, including extra prefill tokens and any caching assumptions. An accuracy tie would make the cost/harm comparison especially informative. A weak GPT-2 context result is useful too, but would remain a result for this base and prompting protocol.

## 7. Minimal changes to the work already underway

| When | Recommended adjustment | Practical effect |
|---|---|---|
| Now, before interpreting Phase 0 | Partition locality target conflicts; reconstruct actual winning/applied records | Prevents misleading failure diagnoses and contradictory negatives |
| Now | Replace cross-bank chaining search with the architecture/dependency audit | Removes a diagnostic that cannot test its stated hypothesis |
| Next forward-only slot | Profile candidate-on counterfactuals and the matched in-context comparator; reuse outcomes across hard thresholds | Keeps the early work focused and avoids a large threshold × model grid |
| Before harness training | Declare the selection-only or fixed-candidate objective and memory/key update policy | Makes the cheap harness scientifically interpretable |
| Before choosing H1 over H2 | Run the tiny target-free energy feasibility check | Prevents building a confidence score that is constant by construction |
| During the first learning comparison | Preserve paired representation/settling diagnostics, with equal tuning allowances | Supports an explanation without opening a separate large analysis programme |
| At the first results discussion | Decide whether a composition, coupled-objective or systems continuation is justified | Retains Capstan's narrower sequence |

I agree with retaining lightweight representation diagnostics. I would keep LLC and distributed execution deferred. An H3/NESS specification and a few synthetic fixtures can proceed independently if someone has capacity, but I would not make a full JAX H3 port another immediate primary deliverable.

There is no need for another approval hierarchy or a prescribed ten-page Phase 0 note. One concise result note with the corrected populations, paired curves, comparator outcomes and next decision is enough. Profile the GPU work before expanding it; the proposed four-hour Phase 0 ceiling is a limit to work within, not evidence that every listed rerun will fit.

**Recommended scientific aim:** establish where a local PC learning rule offers a measurable advantage under explicit information, memory and compute constraints. Avoid requiring proof of something BP “cannot provide.” A well-controlled benefit, an explained trade-off, or a negative result that rules out the current mechanism would each move this project forward.

### Reproducing the review's saved-data checks

From `pc_cap`, choose a new output filename:

```bash
python3 scripts/post_conference_capex_review_audit.py \
  --output /tmp/capex-post-conference-review-audit.json
```

The script refuses to overwrite its output. It uses the Python standard library, reads the existing prepared payload and scoring chunks, checks their recorded hashes, and reports the locality partitions, selection-field discrepancies, ordinary-text tail baselines and serialized acquisition fields. It does not launch an experiment.
