# Research Agent Handoff: Dataset Extremes, Heavy Tails, and Predictive-Coding CAP Robustness

## 0. Mission

You are the coding/research agent responsible for our existing frozen-GPT-2 knowledge adaptation experiments. You have access to the project workspace, model checkpoints, datasets, logs, scripts, and previous experiment results.

Conduct a **comprehensive, reproducible evaluation and statistical analysis** of our three models:

1. **Frozen GPT-2 Small:** Original frozen Transformer, no CAP.
2. **GPT-2 Small + PC-CAP:** Same frozen backbone, with trained predictive-coding residual correction modules.
3. **GPT-2 Small + BP-CAP:** Same frozen backbone, with residual CAP modules trained through backpropagation.

The datasets are:

- zsRE
- CounterFact
- MQuAKE

The research question is whether the PC-CAP provides better adaptation, particularly on difficult, surprising, rare, or extreme examples, and whether any improvement comes with stability or locality costs.

We also want to characterize the datasets themselves, comparing their frequency distributions, diversity, distribution shifts, numerical tail behavior and extremes.

### Time and resource policy

- Plan for approximately **8–12 hours of overnight work**, but this is not a hard deadline.
- Continue longer if necessary to finish a scientifically valid evaluation. There is no requirement to finish tomorrow morning.
- One GPU is available.
- Do not retrain the PC-CAP or BP-CAP unless an unexpected, critical problem makes prior results unusable. Such a situation requires a clearly documented decision.
- Prefer reusing existing data, but **perform genuinely missing evaluations**, especially the frozen GPT-2 baseline.
- Never replace a missing metric with an inferred or invented number.
- Preserve all existing data, checkpoints, configs and results.

**Important: Save results incrementally throughout the work.** Every completed stage and every costly evaluation chunk must be recoverable after a crash or interrupted session.

Your final deliverables must include a **detailed research report (PDF and Markdown), all generated plots, complete numerical tables, per-example raw data, analysis code, and a reproduction guide**.

---

# PART I — ESTABLISH A VALID THREE-MODEL COMPARISON

## 1. Audit the existing research program

Before running GPU evaluations, inspect and understand:

- Main research objectives and current architecture.
- The frozen GPT-2 Small backbone and its exact model revision.
- PC-CAP architecture, insertion points, training methodology, inference iterations, parameter count and saved checkpoint.
- BP-CAP architecture, insertion points, training methodology, parameter count and checkpoint.
- Which parts of the model remain frozen.
- Whether the CAPs run independently for each example or maintain state across examples.
- Whether adaptations are persistent, episodic or performed through inference-time state updates.
- Dataset versions, preprocessing, splits, prompt templates and evaluation conventions.
- Existing evaluation scripts, metric definitions, seeds and results.

Create `audit/model_and_dataset_inventory.md`.

Record checkpoint hashes, code commit, library versions, GPU details, configurations, CAP placement, trainable-parameter counts and number of inference iterations.

**Do not assume PC-CAP and BP-CAP are identical except for their training algorithm. Verify architectural and computational differences explicitly.**

Also verify that "Frozen GPT-2" really means no residual correction, no learned CAP, no carried-over hidden state and no adaptation to the edited test facts.

A CAP disabled through a software flag must be validated against an ordinary, directly loaded frozen GPT-2.

## 2. Mandatory basic performance comparison

This is a primary deliverable, independent of heavy-tail analysis.

Produce a complete table with rows corresponding to:

- zsRE
- CounterFact
- MQuAKE, separating dataset variants when relevant

And columns corresponding to:

- Frozen GPT-2 Small
- GPT-2 + PC-CAP
- GPT-2 + BP-CAP

For every model/dataset combination, include all originally defined primary benchmark measures: factual-edit success, accuracy, loss, paraphrase generalization, locality and reasoning performance, as applicable.

Where a measure does not apply, use `N/A`, not zero.

### Mandatory frozen-baseline verification

Search all earlier raw artifacts, evaluation outputs and reports for an existing frozen-only evaluation.

Verify that any discovered baseline was run using:

- The exact corresponding GPT-2 backbone.
- The correct test examples and splits.
- The same tokenizer and prompt templates.
- The same target-answer conventions.
- The same evaluation conditions and metrics.
- No CAP residuals or edit-memory effects.

If the frozen-only results are absent, incomplete or incompatible, **run the missing frozen-model evaluations**.

Prioritize completing the frozen baseline over any optional extreme-tail analysis.

If the earlier PC-CAP/BP-CAP results consist only of aggregate scores, preserve these but rerun targeted evaluations where per-example information is needed and cannot otherwise be recovered.

### Fairness and comparability

Use identical examples, target answers, prompt families and scoring code for all three models.

Where possible, report both:

1. The **original benchmark metric**, exactly following the previous project's evaluator.
2. A **common standardized evaluation**, using the definitions below.

Do not silently modify an established benchmark metric to make it uniform across datasets.

Record whether each model was evaluated before or after any adaptation episode.

The frozen-only model has no editing mechanism. For counterfactual tasks, a low score against the requested new fact is therefore expected and should not automatically be interpreted as poor general language-modeling performance.

Where original target answers are available, separately report the frozen model's performance on the original facts.

### Special comparison for factual editing

For cases with an original answer and requested edited answer, calculate:

- Original-fact performance before the edit.
- New-target performance under the benchmark's post-edit condition.
- Original-versus-new target preference.
- Paraphrase performance.
- Unrelated-fact preservation.

This distinguishes a model that already happens to predict the requested target from a model that genuinely changed its behavior.

If a cap is trained globally rather than performing individual edits, document that distinction rather than claiming conventional episodic knowledge-editing performance.

---

# PART II — PRECISE PER-EXAMPLE DATA AND METRIC DEFINITIONS

## 3. Construct the canonical analysis dataset

Use Parquet as the preferred format, with CSV exports for key summary tables.

Create an immutable example manifest containing:

- `dataset`: zsRE / CounterFact / MQuAKE
- `dataset_variant` and `dataset_version`
- `split`: train / validation / test
- `case_id` or original example ID
- `edit_group_id`
- `question_id`, where applicable
- `prompt_family`: rewrite / paraphrase / locality / single_hop / multi_hop / other
- `prompt_text` and exact formatted input
- `subject`
- `relation_id`, if available
- `target_new`
- `target_true`, if available
- `answer_aliases`
- `hop_count`, if available
- `number_of_edits`, if available
- original sequence/order ID when meaningful
- prompt length and answer length in GPT-2 tokens
- original source filename and row index
- relevant metadata for novelty, frequency, and subgroup analyses

Keep raw and normalized answers in separate fields.

Create a long-format results table containing:

- All manifest identifiers
- Model name and checkpoint ID
- Evaluation condition
- Seed and run ID
- Predicted/generated answer if available
- Target token count
- Full-target log probability
- Total negative log-likelihood
- Per-target-token loss
- Original and new target scores, where available
- Success/failure indicator
- Original benchmark metric fields
- CAP correction information, when available
- Status, failure reason and source artifact path

One row must have one clearly defined observation unit. Do not mix question-level, edit-level and paraphrase-level rows without identifiers.

**Never use a loose join on row position alone.** Use stable, verified composite keys.

Create a data dictionary documenting every field, measurement unit, missing-value convention and calculation.

## 4. Exact target probability and loss calculations

For prompt `x_i` and answer tokens `y_i,1 ... y_i,T`, calculate:

`logP_i = sum_t log p(y_i,t | x_i, y_i,<t)`

`NLL_total_i = -logP_i`

`NLL_token_i = NLL_total_i / T_i`

Where:

- `i` identifies an evaluated prompt-answer pair.
- `t` identifies a target token.
- `T_i` is the number of target tokens.
- `x_i` is the exact formatted input prompt.
- `y_i,t` is target token `t`.
- `p` is the model's conditional token probability.

Use natural logarithms, giving losses in nats.

**Implementation requirements:**

1. Use teacher forcing for likelihood measurements.
2. Only target-answer tokens contribute to target loss; exclude prompt tokens.
3. Verify causal shifting of logits by one position.
4. Preserve the original benchmark's punctuation and leading-space conventions.
5. Be careful with GPT-2 byte-pair tokenization at prompt/answer boundaries.
6. Do not assume tokenizing the answer independently always yields exactly the same tokens as tokenizing the concatenated prompt and answer.
7. Exclude padding tokens.
8. Use log-softmax/log-sum-exp numerics, preferably float32 for final score computations.
9. Never substitute generated-answer accuracy for teacher-forced target probability.
10. Score the same serialized prompt-answer pairs in all three models.

Use `NLL_token` as the principal continuous measure of example difficulty, because answers can have different token lengths.

Also retain `NLL_total`, because full-sequence likelihoods are relevant to some benchmark metrics.

### Counterfactual preference

When both the new and original targets are available, calculate:

`margin_total = logP(target_new | prompt) - logP(target_true | prompt)`

`margin_token = -NLL_token_new + NLL_token_true`

Record both.

`margin_total > 0` means the requested target has greater whole-sequence probability than the original target.

Do not substitute length-normalized preference for an original benchmark's whole-sequence criterion. Report the two separately because differing target lengths can change rankings.

## 5. Binary success and accuracy

Preserve the original project's success definitions.

For additional standardized measurements:

- When deterministic generation is used, set sampling off and use fixed, documented decoding parameters.
- Apply one consistent, documented answer-normalization function.
- For exact match, normalize whitespace and case only according to the benchmark convention.
- Use aliases only when those aliases are supplied or otherwise legitimately authorized by the evaluation set.
- Do not use the test target as a hint in the generated prompt.
- Do not equate a greater target likelihood with successful free generation.

Report success as:

`success_rate = number_of_successful_independent_cases / number_of_evaluated_independent_cases`

For question-level results, clearly identify that the denominator is questions instead of cases.

Report numerator and denominator alongside every percentage.

## 6. Dataset-specific evaluation rules

### zsRE

Identify the actual zsRE variant used in the project.

Depending on its schema, records may contain fields such as `src`, `alt`, `answers`, `rephrase`, `loc` and `loc_ans`, or equivalent fields from another format.

Evaluate the existing:

- Requested rewrite/new-answer success.
- Rephrasing generalization.
- Original-answer behavior.
- Locality or unrelated-fact preservation.

Do not assume all zsRE versions contain relation IDs. If relation metadata is absent, do not manufacture a relation classification using speculative automatic labeling.

### CounterFact

Use the original dataset's:

- Requested rewrite prompts.
- `target_new`.
- `target_true`.
- Paraphrase prompts.
- Neighborhood/locality prompts.

Preserve the originally used efficacy, paraphrase and neighborhood metrics.

Additionally store target log probabilities, preference margins and per-example changes.

Distinguish performance on the original target from success at imposing a counterfactual target.

### MQuAKE

First identify whether the project used:

- MQuAKE-CF, full or subset.
- MQuAKE-CF-3k original.
- MQuAKE-CF-3k-v2.
- MQuAKE-T.
- Another specifically filtered project subset.

**Do not silently substitute a different MQuAKE version.** The updated 3k-v2 version fixes known conflicts and is recommended by the benchmark authors, but it must not be mixed with results obtained from the original version.

For multi-hop questions, preserve the evaluation prompting setup, including any original demonstrations or chain-of-thought convention.

Calculate separately:

1. **Question accuracy:** fraction of individual multi-hop questions answered correctly.
2. **Any-question success:** fraction of cases for which at least one associated multi-hop question is answered correctly.
3. **All-question success:** fraction of cases for which every associated question is answered correctly.
4. **Single-hop edit accuracy:** if relevant records are available.
5. Performance by hop count and number of edited facts.
6. Original-answer versus new-answer preference, when well-defined.

The MQuAKE benchmark's published any-of-three convention is not interchangeable with question-level accuracy.

Use edited gold answers and their valid aliases for the post-edit multi-hop evaluation.

For temporal MQuAKE, preserve any extended-answer convention.

Do not compare MQuAKE percentages directly to CounterFact percentages as if they were measuring the same success criterion.

---

# PART III — DATASET CHARACTERIZATION

## 7. Frequency concentration, rarity and diversity

Calculate separately for all three datasets:

- Number of independent cases.
- Number of prompts by evaluation family.
- Unique subjects, relations and targets.
- Frequencies of relations, subjects and new targets.
- Original-target frequencies when available.
- Fraction of examples belonging to singleton categories.
- Fraction in categories appearing at most five times.
- Top 1%, 5% and 10% category concentration.
- Median, P90, P95 and P99 prompt/answer lengths.
- Exact duplicate and near-duplicate counts using documented normalization.

Calculate frequencies at the **independent case level**, not by counting every paraphrase as another independent data point.

For MQuAKE, add frequency distributions of relation chains, numbers of requested edits and hop counts.

Produce sorted rank-frequency plots, including log-log views.

Fit simple descriptive Zipf slopes over explicitly documented ranges where suitable.

Do not interpret a visually straight rank-frequency line alone as proof of an asymptotic power law.

### Shannon entropy

For a categorical variable with probabilities `p_1 ... p_K`, use:

`H = -sum_j p_j * ln(p_j)`

Ignore zero-probability terms.

Where:

- `K` is the number of observed categories.
- `p_j` is the empirical relative frequency of category `j`.

Compute:

- `H_relation`
- `H_subject`
- `H_target_new`
- `H_target_true`, where available
- `H(target_new | relation)`, when valid relation labels exist

Also calculate:

`H_normalized = H / ln(K)` when `K > 1`

`N_effective = exp(H)`

Use `H=0` and a documented convention when only one category is observed.

Interpret `N_effective` as the effective number of equally likely categories corresponding to the measured diversity.

For conditional entropy:

`H(Y|R) = sum_r p(r) H(Y|R=r)`

Here `Y` is the selected target category and `R` is the relation category.

Use the same record-level weighting rules for all calculations.

### Train/test rarity

Where genuine training and held-out test splits exist:

- Estimate frequencies from training data only.
- Compute the proportion of test subjects, targets and relations unseen in training.
- Record train-frequency percentiles for each test example.
- Define rare-category groups based on training counts, not retrospectively using test outcomes.
- Examine overlap of `(subject, relation, target)` triples and MQuAKE chains across splits.

A category can be rare *in the benchmark* without being rare in the real world. Make this distinction explicit.

## 8. Distribution shift, KL and Jensen–Shannon divergence

For train/test comparisons, calculate:

- Relation-distribution JS.
- Target-distribution JS.
- Subject-distribution JS if interpretable.
- Frozen-model surprisal-distribution JS.
- Wasserstein-1 distance for continuous surprisal distributions.

For discrete probability vectors `P` and `Q` over the same union of categories:

`M = (P + Q)/2`

`KL(P||Q) = sum_j P_j * ln(P_j/Q_j)`

`JS(P,Q) = 0.5*KL(P||M) + 0.5*KL(Q||M)`

Use natural logs; JS is bounded between zero and `ln(2)`.

For JS, use the union support and the mathematical zero-probability convention. Smoothing is not necessary just to avoid undefined JS terms.

For optional train/test KL, use a clearly documented common Dirichlet pseudocount, such as `0.5` per category, and report the smoothing choice.

For numerical histograms, use identical bin edges and ranges, established independently of model comparisons.

For Wasserstein distance, calculate directly from empirical scalar samples where possible.

### Extreme versus typical subsets

Within each dataset, define extremes using the frozen model's baseline surprisal:

- Extreme: top 5% of independent cases.
- Typical: remaining 95%.

Compare relation, target, train-frequency, length, hop-count and other feature distributions using JS or suitable numerical tests.

Also compare top 1% versus remaining examples when sample size permits.

Do not claim that surprisal differs between groups defined by surprisal; that difference is tautological.

Do not invent a train/test split when only benchmark evaluation records exist.

For between-dataset comparisons, use common numerical features and comparable category mappings. If relations are labeled differently across datasets, explain why a direct categorical JS comparison may not be meaningful.

---

# PART IV — CHARACTERIZING EXTREMES AND HEAVY TAILS

## 9. Empirical distributions

For each continuous variable below, whenever available, calculate:

- Count and missing-value fraction.
- Mean and standard deviation.
- Median and interquartile range.
- P90, P95, P99 and maximum.
- Average of the worst 5%.
- Empirical survival/CCDF plots.
- Histograms, with consistent axes where comparisons are valid.

Variables:

1. Frozen-model per-token surprisal.
2. PC-CAP per-token loss.
3. BP-CAP per-token loss.
4. CAP correction magnitudes.
5. Normalized CAP correction magnitudes.
6. Harmful adaptation magnitudes.
7. Locality degradation magnitudes.
8. Positive adaptation gains, analyzed separately.

For a sample sorted from largest to smallest, `x_(1) >= ... >= x_(n)`, define:

`k = ceil(0.05*n)`

`CVaR95_empirical = mean(x_(1), ..., x_(k))`

This is the empirical mean of the worst 5% for variables where larger means worse.

For signed adaptation gain, analyze its positive and negative tails separately. Do not use one unqualified upper-tail statistic for both improvements and harms.

No silent clipping or winsorization.

## 10. Generalized Pareto tail modeling

For suitably positive or unbounded numerical variables, fit generalized Pareto distributions to threshold exceedances.

At threshold `u`, calculate exceedances:

`z_i = x_i - u`, for cases with `x_i > u`.

Fit the survival function:

`P(Z > z) = (1 + kappa*z/sigma_u)^(-1/kappa)`

subject to valid support, with `sigma_u > 0`.

The limiting case `kappa = 0` is:

`P(Z > z) = exp(-z/sigma_u)`

Where:

- `x_i`: observed value.
- `u`: high threshold.
- `z_i`: positive amount exceeding the threshold.
- `kappa`: GPD tail-shape parameter.
- `sigma_u`: threshold-dependent GPD scale.

Use `scipy.stats.genpareto.fit(exceedances, floc=0)` or an equivalent validated implementation.

### Threshold choices

Calculate threshold candidates at:

- P90
- P95
- P97.5

Prefer at least 100 exceedances for the principal fitted analysis. Fits with 50–99 exceedances may be shown as exploratory with explicit uncertainty. Smaller tails should generally be marked insufficient.

For each fit record:

- Threshold.
- Number of exceedances.
- `kappa`.
- `sigma_u`.
- Bootstrap 95% confidence interval.
- Log-likelihood and AIC.
- Tail QQ plot or equivalent fit diagnostic.

Use the same exceedance sample to compare the GPD against its exponential special case `kappa=0`.

Assess threshold stability and confidence intervals before describing a variable as exhibiting Pareto-type tails.

### Correct interpretation

- `kappa > 0`: Pareto-type heavy tail under the fitted asymptotic model.
- `kappa = 0`: exponential-tail limiting case.
- `kappa < 0`: finite-upper-endpoint GPD model.
- Larger positive `kappa`: heavier modeled extremes.

Do not equate finite-sample skewness or an isolated outlier with heavy tails.

If `kappa > 0`, the modeled survival-tail exponent is `1/kappa`. Do not confuse this exponent with the stretching parameter `alpha` in Nelson's coupled-distribution framework.

The GPD scale depends on the selected threshold. Do not directly compare scales from different thresholds without explicitly accounting for this.

Also do not claim long-range dependence solely because the fitted distribution has positive `kappa`.

### Variables to fit

Priority:

1. Frozen-model surprisal, separately by dataset.
2. PC-CAP and BP-CAP per-token loss distributions.
3. Normalized CAP correction magnitudes.
4. Harmful adaptation or locality degradation magnitudes, where sufficient observations exist.

For nonnegative quantities containing a large point mass at zero, model genuine positive exceedances rather than pretending the entire mixture is a continuous GPD.

Include uncertainty and diagnostic warnings.

---

# PART V — MAIN MODEL COMPARISONS IN THE EXTREMES

## 11. Paired performance improvements

For every matched independent example `i`, define:

`G_PC_i = L_Frozen_i - L_PC_i`

`G_BP_i = L_Frozen_i - L_BP_i`

`G_PCvsBP_i = L_BP_i - L_PC_i`

Here `L` is per-target-token loss, calculated for the same prompt and target.

Positive values favor the first model named in the respective gain.

Calculate:

- Mean and median paired gains.
- Standard deviation.
- Fraction of examples helped.
- Fraction harmed.
- P5 and P95 of gain.
- Mean of the worst 5% negative gains.
- Bootstrap 95% confidence intervals.

Also compare success rates and locality outcomes with paired uncertainty.

### CVaR comparisons: TWO distinct analyses

**A. Each model's own worst cases**

Calculate CVaR95 separately for each model's loss distribution.

This measures its overall worst-case performance.

The worst 5% examples may differ among models.

**B. Same frozen-defined difficult cases**

Identify the frozen model's highest-loss 5% cases, once per dataset and relevant prompt family.

On this fixed set, calculate the average loss and success rate of each of the three models.

This reveals how well each CAP handles exactly the examples that are hardest for the common frozen backbone.

Do not confuse A and B.

Report both with clear labels.

## 12. Improvement versus baseline difficulty

Within each dataset and appropriate evaluation family:

1. Sort independent cases by frozen-model `NLL_token`.
2. Assign deciles 1–10 using deterministic ranking with a documented rule for ties.
3. Keep these decile assignments fixed for all models.
4. Compute mean/median gains, confidence intervals, success rate and locality outcomes in each bin.

Produce:

- PC-CAP gain versus difficulty decile.
- BP-CAP gain versus difficulty decile.
- Direct PC-CAP minus BP-CAP comparison.
- Optional success-rate curves.

Perform separate top-5% and top-1% analyses, reporting sample sizes.

### Important sensitivity tests

Repeat the principal comparisons:

- By target-token length.
- By common versus rare relations, when available.
- By original-answer preference.
- By MQuAKE hop count and edit count.
- By initially known versus initially unknown original facts, where this classification can be established.

This helps distinguish genuine robustness from effects caused by different target lengths or task compositions.

Do not tune thresholds after inspecting which model wins.

## 13. Rare events, extreme failures and catastrophic regressions

Define the loss deterioration caused by a CAP:

`D_method_i = L_method_i - L_Frozen_i`

A positive `D` means the CAP increased loss.

Report:

- Fraction with `D > 0`.
- Mean positive deterioration.
- P95/P99 deterioration.
- Mean of largest 5% deteriorations.
- Fraction with deterioration exceeding a preregistered threshold, such as 0.5 nats/token.
- Most severe examples, with identifying metadata and supporting scores.

Also calculate where PC-CAP is substantially worse than BP-CAP, and vice versa.

Show both successful extremes and harmful extremes, not just the cases that favor predictive coding.

## 14. Locality and collateral damage

Use previously defined locality/neighbor evaluations. Where possible, evaluate equivalent locality prompts for all three models.

For unrelated prompts with known correct targets, calculate:

- Correct-answer loss for each model.
- Change relative to frozen GPT-2.
- Accuracy/success preservation.
- Fraction of examples made worse.
- Worst-5% locality deterioration.

For models performing episodic edits, also measure pre-edit versus post-edit changes under the same episode.

If the original output distributions are available, optionally calculate next-token JS divergence between pre-edit and post-edit distributions.

Distinguish a model that preserves the *original prediction distribution* from one that preserves *factual correctness*. These are not necessarily the same.

### Joint extremes

Where correction and locality measures are available for the same independent cases, define:

- `A`: locality deterioration lies in its worst 10%.
- `B`: normalized CAP correction magnitude lies in its highest 10%.

Calculate:

`tail_lift = P(A | B) / P(A)`

Report the numerator and denominator counts, conditional probability, tail lift and uncertainty interval.

A tail lift greater than one indicates that locality failures occur disproportionately often among large-correction cases.

Also calculate Spearman rank correlations between:

- Baseline surprisal and correction magnitude.
- Correction magnitude and adaptation gain.
- Correction magnitude and locality deterioration.
- Baseline surprisal and locality deterioration.

Do not calculate joint-tail statistics by joining unrelated locality prompts to edit examples arbitrarily.

## 15. MQuAKE-specific extreme reasoning analysis

For MQuAKE, separately analyze:

- Frozen-model difficulty of multi-hop questions.
- Success after adapting edited single-hop facts.
- Number of edits needed to induce the new answer.
- Hop count.
- Error propagation through multi-hop questions.
- Differences between any-question and all-question success.

If intermediate single-hop outcomes are available, examine whether multi-hop failures are associated with failure to update one or more supporting facts.

Report performance by available hop-count and edit-count strata.

Do not automatically interpret a failed multi-hop question as a failure of the CAP mechanism; GPT-2 Small may also lack the underlying compositional reasoning capability.

## 16. Sequential behavior and correlated extremes

Only if the existing research program has a meaningful sequential or streaming evaluation condition:

- Preserve the actual time/order indices.
- Identify sequences of high-surprisal examples.
- Calculate error autocorrelation at lags 1–5, if adequate data exist.
- Calculate rates of consecutive extreme failures.
- Compare model errors during clusters of difficult events and afterwards.
- Investigate whether persistent CAP state affects the following examples.

Use the real evaluation order, not dataset row IDs unless those IDs actually represent sequence order.

A shuffled data file does not establish temporal dependence.

If sequences do not exist, mark this analysis unavailable and do not manufacture a streaming experiment without a justified reason.

---

# PART VI — CAP INTERNAL REPRESENTATIONS

## 17. Residual correction analysis

If existing artifacts contain CAP activations and residuals, use them.

Otherwise instrument both PC-CAP and BP-CAP consistently and run a targeted evaluation pass, ideally across the full matched test set if feasible with one GPU.

At a selected Transformer block, define:

`h_after = h_before + delta_h`

Here:

- `h_before`: hidden-state vector immediately before CAP correction.
- `delta_h`: actual residual correction added by the CAP.
- `h_after`: corrected hidden-state vector.

For every corrected block and analyzed token position, calculate:

`norm_abs = sqrt(sum_j delta_h_j^2)`

`norm_rel = norm_abs / (sqrt(sum_j h_before_j^2) + 1e-12)`

Where `j` indexes hidden dimensions.

Also calculate:

`correction_energy = sum_j delta_h_j^2`

Specify whether results use the final prompt-token position, target-token positions or another documented location.

Do not mix differently selected positions without labeling them.

For cases with multiple corrected layers:

- Store one row per case, layer and position-selection rule.
- Calculate mean and maximum relative correction across corrected layers.
- Calculate summed correction energy and mean energy per corrected layer.
- Report differences in the number and placement of CAP modules.

For PC-CAP, if inference-step traces are already available, also report initial versus final corrections and any existing validated inference-energy convergence measure.

Do not invent an energy function if the implementation does not explicitly define one.

### Comparisons

Compare PC-CAP and BP-CAP in terms of:

- Absolute correction distributions.
- Relative correction distributions.
- P95/P99 correction sizes.
- Tail-shape fits when reliable.
- Correction versus baseline difficulty.
- Correction versus performance gain.
- Correction versus locality degradation.

Include block-level plots where informative.

The frozen model has zero CAP correction by definition; do not fit a heavy-tail distribution to these structural zeros.

Avoid storing full hidden-state tensors for every token if summary statistics are sufficient. Save full vectors only for a small, traceable diagnostic subset if necessary.

---

# PART VII — NELSON PAPER: INFORMATIONAL SCALE AND COUPLED ENTROPY

## 18. Reference and goals

Reference:

Kenric P. Nelson, *The Unique, Universal Entropy for Complex Systems*, September 2026.

Use the supplied PDF if available in the workspace.

We want a modest, mathematically justified connection with:

- Nonlinear tail-shape parameter `kappa`.
- Informational scale `sigma`.
- Separation of ordinary fluctuation scale from the heaviness of rare extremes.
- Generalized/coupled entropy compared with Shannon entropy.

This is supplementary to the main model comparison.

## 19. GPD scale and Nelson's informational scale

Nelson discusses the generalized Pareto distribution as a useful case in which scale can be separated from nonlinear tail shape.

For the fitted exceedance variable:

`f(z) = (1/sigma) * (1 + kappa*z/sigma)^(-1/kappa - 1)`

with `z >= 0` and valid support.

For this specific parameterization, the scale satisfies the informational-scale condition:

`-sigma * [d/dz ln f(z)] at z=sigma = 1`

This follows directly by differentiating the fitted log density.

Check this identity numerically or symbolically in the code.

Be careful: the fitted `sigma` is the scale of the distribution of **exceedances above the selected threshold**. It is not automatically a threshold-independent scale for the original full loss distribution.

Produce a table of GPD `kappa` and `sigma_u`, including confidence intervals, across datasets and model-loss distributions.

Discuss changes in tail shape separately from changes in scale.

## 20. Coupled entropy: optional but recommended

Implement a limited and carefully validated **discrete coupled-entropy sensitivity analysis**, using Equation 24 from the attached paper.

For the one-dimensional special case with stretching parameter `alpha=1` and unit conversion factor `k=1`, define:

`q(kappa) = (1 + 2*kappa)/(1 + kappa)`

`H_kappa(p) = [1 / sum_j(p_j^q(kappa)) - 1] / kappa`

For `kappa=0`, evaluate the continuous limit:

`H_0(p) = -sum_j p_j*ln(p_j)`

Where `p` is an explicitly defined, normalized empirical categorical probability vector.

Use stable numerical evaluation near zero, not direct division by a tiny `kappa`.

Preselect coupling values:

`kappa = 0, 0.1, 0.25, 0.5, 1.0`

Compute sensitivity profiles for relation frequencies and target frequencies, when available, and optionally for shared-bin surprisal histograms.

**Tests required:**

- Probabilities sum to one.
- Nonnegative probabilities only.
- A point-mass distribution has zero entropy.
- At `kappa=0`, the result equals Shannon entropy.
- For a uniform distribution over `W` categories, verify:

`H_kappa = (W^(kappa/(1+kappa)) - 1)/kappa`

- Verify numerical convergence toward Shannon entropy as `kappa` approaches zero.

Use shared categorical-support definitions and identical numerical bins when comparing distributions.

This is a **parameter-sensitivity study**, not automatically a calibrated entropy measurement of the underlying physical system.

In particular:

- A `kappa` fitted to scalar prediction losses should not automatically be assigned to an unrelated categorical relation distribution.
- A fitted heavy-tail distribution alone does not establish actual nonlinear dynamical coupling.
- Discretized entropy depends on binning.
- Do not claim experimental confirmation of the paper's proposed universal-entropy theorem.

If mathematically meaningful calibration is not established, label the result **exploratory coupled-entropy profile**.

Include a short interpretation of how changing `kappa` changes the characterization of a given empirical probability distribution.

---

# PART VIII — STATISTICAL INFERENCE AND QUALITY CONTROL

## 21. Confidence intervals and statistical uncertainty

Use paired bootstrap comparisons as the principal uncertainty estimator.

Default:

- 2,000 bootstrap replicates for main performance contrasts.
- Fixed random seed and saved bootstrap configuration.
- Resample independent edit/case groups.
- Preserve all questions, paraphrases and locality records attached to each resampled group.
- Preserve model pairing when comparing the three models.
- Recompute quantiles, CVaR and difficult-subset definitions appropriately within bootstrap replicates.

When distinct runs or seeds are available, preserve the distinction between within-run sampling variability and across-seed variability.

For sequential experiments with dependent observations, consider block/bootstrap resampling at the sequence or episode level.

Report 95% percentile confidence intervals or clearly specify a validated alternative.

For binary outcomes, use paired differences and appropriate paired uncertainty, not independent standard errors for models evaluated on the same examples.

For multiple exploratory correlations and many subgroup comparisons, either control multiplicity or explicitly describe them as exploratory.

Do not declare a winner from tiny differences with unstable confidence intervals.

## 22. Mandatory validation tests

Before extensive GPU runs, implement and execute unit tests and small end-to-end checks.

At minimum:

1. **Frozen equivalence:** CAP-disabled output matches directly loaded frozen GPT-2 within expected numerical precision.
2. **Log-likelihood:** Hand-check token-level log probabilities and causal offsets on several examples.
3. **Length normalization:** Total NLL equals per-token NLL times target token count.
4. **Joining:** No accidental many-to-many joins; matched model rows have identical prompts and targets.
5. **MQuAKE aggregation:** Any-question success, all-question success and question-level accuracy are calculated correctly.
6. **Entropy:** Point mass, uniform distribution and Shannon-limit tests.
7. **JS divergence:** Symmetry, zero for identical distributions, nonnegativity and upper bound `ln(2)`.
8. **GPD:** Test on synthetic exponential, Pareto/GPD and bounded-tail data, checking approximate recovery and support constraints.
9. **CVaR:** Test against a small manually calculated sorted example.
10. **Bootstrap:** Resampling preserves case grouping and three-model pairing.
11. **Residual correction:** Verify `h_after ≈ h_before + delta_h` at the actual insertion site.
12. **Missing data:** Missing values cannot silently become zero or false.
13. **Aggregation:** Recompute original reported metrics from saved records on a small test batch and explain any disagreement.

Run a representative smoke test before the overnight evaluation.

If the original research code uses alternative conventions, preserve the original numbers and document how the standardized analysis differs.

## 23. Required sensitivity and sanity analyses

For key findings:

- Repeat difficulty analysis using total NLL as a sensitivity analysis, while retaining per-token NLL as primary.
- Check whether answer length explains surprising differences.
- Compare all cases with the subset for which frozen GPT-2 already preferred the original factual answer.
- Separate dataset variants and evaluation families.
- Inspect threshold stability in extreme-value fitting.
- Identify any invalid or anomalous examples and explain exclusions.
- Report effective sample sizes for each analysis.

Do not restrict the analysis to successful edits.

Do not choose a post-hoc subset because it favors PC-CAP.

---

# PART IX — EXECUTION, PERSISTENCE AND GPU MANAGEMENT

## 24. Work in recoverable stages

Create a dedicated results directory, for example:

`results/extremes_analysis/<run_id>/`

Suggested structure:

```text
results/extremes_analysis/<run_id>/
    README.md
    STATUS.md
    manifest.json
    config.yaml
    audit/
    data/
        example_manifest.parquet
        scores.parquet
        paired_cases.parquet
        dataset_statistics.parquet
        tail_fits.parquet
        bootstrap_results.parquet
        residual_statistics.parquet
    checkpoints/
    figures/
    tables/
    reports/
        research_report.md
        research_report.pdf
    logs/
    scripts/
    validation/
```

Adapt this structure to the project's existing conventions rather than duplicating incompatible infrastructure.

### Execution order

**Stage 1 — Audit and alignment**

- Inventory prior runs and artifacts.
- Identify what is genuinely missing.
- Save the example manifest.
- Create baseline completeness matrix.
- Run validation/smoke tests.

**Stage 2 — Complete standard benchmarks**

- Reconstruct PC-CAP and BP-CAP scores from existing data.
- Run missing frozen GPT-2 evaluations.
- Fill remaining per-example losses or logits where necessary.
- Save the complete basic performance table.

**Stage 3 — Dataset statistics**

- Frequency and entropy analysis.
- Rarity, shift and JS/KL analysis.
- Dataset comparison figures.

**Stage 4 — Heavy-tail analysis**

- Surprisal distributions.
- GPD fits and fit diagnostics.
- Tail and CVaR tables.

**Stage 5 — CAP behavioral analysis**

- Paired gains and decile curves.
- Worst-case comparisons.
- Locality and harmful adaptations.
- Residual correction analysis.

**Stage 6 — Nelson supplementary analysis**

- Informational-scale interpretation.
- Coupled-entropy sensitivity profiles.
- Mathematical validation.

**Stage 7 — Integration and reporting**

- Confidence intervals and robustness checks.
- Tables and figures.
- Final research report.
- Artifact/provenance audit.

Each stage must generate independently inspectable outputs.

## 25. Save continuously and allow clean resumption

Requirements:

- Save raw per-example results in moderate-sized chunks (for example 100–500 independent cases per chunk, adjusted for computation cost).
- Write chunks atomically: temporary file followed by rename.
- Maintain a completed-chunk manifest with stable IDs and input/configuration hashes.
- On restart, verify completed chunks and evaluate only missing or invalid ones.
- Do not append duplicate rows after a crash.
- Save expensive logits/activation-derived statistics immediately rather than requiring another GPU evaluation.
- Record every significant code/configuration change.
- Keep the original experimental results immutable.
- Save logs and periodic progress summaries.

When possible, run dataset statistics and report preparation on CPU while the GPU evaluates missing model cases.

Only one GPU-heavy job should use the single GPU at a time.

Use inference/evaluation mode, no gradients, and appropriate batching except when genuine PC iterative inference requires a particular state-update mechanism.

Avoid full-vocabulary logits or full hidden-state storage unless truly needed. Compute and save sufficient per-example statistics during forward passes.

Do not silently reduce evaluation coverage because of runtime or memory pressure.

If a run must be interrupted, preserve everything required for deterministic continuation.

## 26. Progress reporting

Maintain `STATUS.md` with:

- Current stage.
- Completed and planned evaluations.
- Number of cases completed for each model/dataset.
- Which metrics are complete.
- Latest output file paths.
- Validation failures or warnings.
- GPU/CPU execution status.
- Remaining work.

Update after every stage and periodically during long evaluations.

An interrupted run must remain understandable to another coding agent.

---

# PART X — FINAL SCIENTIFIC DELIVERABLES

## 27. Required final report

Produce a **complete research paper-style report**, with proper equations, clear explanations, high-quality labeled figures and all relevant numerical results.

PDF and Markdown are mandatory.

Recommended organization:

1. **Abstract and executive summary**
   - Main findings.
   - Whether PC-CAP beats BP-CAP.
   - Whether either CAP beats frozen GPT-2.
   - Whether advantages become stronger or weaker in extremes.
   - Important qualifications.

2. **Research questions and architectures**
   - All three models.
   - CAP placements and training/inference methods.
   - Important experimental differences.

3. **Datasets and evaluation methodology**
   - zsRE, CounterFact and MQuAKE.
   - Dataset variants/splits.
   - Evaluation prompts, targets and original benchmark metrics.
   - Data quality and exclusions.

4. **Basic benchmark results**
   - Complete three-model comparison.
   - Exact original metrics and standardized comparisons.
   - Uncertainty estimates.
   - Interpretation.

5. **Statistical characterization of the datasets**
   - Frequencies, rarity, Zipf plots.
   - Shannon and conditional entropy.
   - Train/test shift and JS divergence.
   - Baseline-surprisal distributions.

6. **Heavy tails and extreme-value statistics**
   - Per-model and per-dataset distributions.
   - GPD `kappa`, scale and diagnostics.
   - CVaR and extreme quantiles.
   - Which conclusions are statistically supported.

7. **Performance and adaptation in extremes**
   - Gain versus frozen difficulty.
   - PC-CAP versus BP-CAP.
   - Same-case difficult-subset comparisons.
   - Severe regressions and worst-case successes.

8. **CAP correction mechanisms**
   - Residual magnitudes by layer.
   - Dependence on difficulty.
   - Dependence on gain and locality.
   - PC versus BP differences.

9. **MQuAKE reasoning and sequential results**
   - Multi-hop consequences.
   - Hop/edit-count dependence.
   - Sequential extremes if available.

10. **Connection with nonlinear statistical coupling**
    - Nelson's framework.
    - Fitted tail shapes versus fluctuation scales.
    - Coupled-entropy sensitivity results.
    - Careful limitations of the analogy.

11. **Discussion and conclusions**
    - What the results actually establish.
    - What remains uncertain.
    - Interpretation for predictive-coding adaptation.
    - Implications for extreme-event robustness.

12. **Reproducibility appendix**
    - All exact metric formulas and variable definitions.
    - Dataset versions, counts and splits.
    - Statistical procedures.
    - Checkpoints and configurations.
    - Environment and commands.
    - Data schemas and output paths.

Whenever introducing a formula, define every variable and nonstandard operator.

## 28. Figures and numerical tables

At minimum produce:

- Complete 3-model × 3-dataset benchmark summary.
- Rank-frequency plots for datasets.
- Frozen-GPT-2 surprisal distributions and CCDFs.
- Cross-dataset tail-shape/scale comparison with confidence intervals.
- GPD fit diagnostics and threshold sensitivity.
- CVaR95 comparisons of the three models.
- CAP improvement versus difficulty decile, PC and BP on the same axes.
- PC-CAP versus BP-CAP paired differences.
- Correction norm versus surprisal.
- Correction norm versus adaptation gain and locality loss.
- MQuAKE performance by hop count and edit count.
- Train/test or typical/extreme JS comparisons.
- Coupled-entropy profiles, if completed.

Every figure must state the dataset, sample size, evaluation type, models, metric units, statistical uncertainty and whether values are normalized.

Avoid figures where overlapping curves cannot be distinguished.

Use proper labels rather than referencing internal phase numbers.

## 29. Raw data delivery

Retain and provide:

- Original input example IDs and metadata.
- Complete per-example model scores.
- Predictions and generation outcomes, where available.
- Per-token and total log probabilities/losses.
- Original/new factual target probabilities.
- Success and locality indicators.
- CAP residual summary statistics.
- Dataset frequency tables.
- Distribution-shift metrics.
- Tail-fit parameters and diagnostics.
- Bootstrap estimates and confidence intervals.
- Relevant inference-step and sequential information.
- Scripts needed to regenerate figures and summary tables.
- Data dictionary and provenance.

Keep results machine-readable. Do not replace raw numerical artifacts with plots or a PDF alone.

### Final completion checklist

Before declaring completion, verify:

- All three datasets are represented with exact versions.
- All three models have comparable basic benchmark results.
- Missing frozen-only tests were genuinely performed.
- PC/BP prior results were preserved and reconciled.
- Per-example joins and loss definitions have passed tests.
- Tail fitting and uncertainty diagnostics are documented.
- All available locality and residual metrics were included.
- MQuAKE success aggregation is correct.
- PDF renders correctly, with no missing equations/figures.
- Raw data and scripts are complete and reload successfully.
- A final `STATUS.md` marks completed, unavailable and incomplete tasks explicitly.

## 30. Autonomy and scientific judgment

You are responsible for execution, validation and the quality of the analysis.

Make technical decisions autonomously when the choice is clear. Consult the existing research program and benchmark implementations instead of guessing.

Do not waste time requesting approval for ordinary data-processing or implementation decisions.

When encountering a scientific ambiguity:

1. Examine the existing evaluator and its provenance.
2. Prefer the established experimental convention for the original metric.
3. Introduce clearly named additional metrics when necessary.
4. Document the distinction.
5. Validate calculations on representative examples before scaling up.

**Do not optimize for finishing quickly at the expense of correct results.** The purpose of saving throughout the work is to allow a complete analysis without repeatedly rerunning expensive model evaluations.

### Final question the report must answer

> Across zsRE, CounterFact and MQuAKE, how do Frozen GPT-2, PC-CAP and BP-CAP compare in ordinary benchmark performance, prediction difficulty, heavy-tail behavior, extreme losses, adaptation benefit, residual correction magnitude, locality and stability? Does PC-CAP exhibit distinctive advantages in rare and extreme situations, and are those advantages robust when compared directly against BP-CAP rather than only against the frozen backbone?

The answer should be supported by reproducible numerical evidence, paired comparisons, uncertainty intervals and explicitly stated limitations, regardless of which model performs best.