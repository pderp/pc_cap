# A first joint test of coupled learning objectives on a transformer correction agent

2 October 2026 — Capex, for charlie derr and Kenric Nelson's collaborators. **Discussion proposal for circulation after 15 October; no implementation, experiment authorization or GPU booking.** [DEC-082](https://github.com/pderp/pc_cap/blob/master/docs/decisions.md) keeps the current experiments and talk framing unchanged and opens this collaboration foundation. Numerical background below is an October 2 snapshot; attach the frozen conference results when circulating this document.

We propose testing whether an explicitly specified, calibrated coupled objective can preserve useful factual corrections while reducing harmful changes to unrelated predictions. The practical question is whether it improves the correction–preservation trade-off, rather than merely making the system apply fewer corrections. The theoretical question is which probability distribution and free-energy functional this testbed should implement. We need the authors' help with that definition before writing the training objective.

The work connects the three presentation themes at different levels: predictive coding is an available learning/credit mechanism; extremes are measured prediction-loss changes; active inference is a proposed extension requiring an explicit policy model. Comparing learning objectives is a useful first experiment, but does not by itself implement active inference or identify an asymptotic heavy-tail class.

## What the existing testbed provides

The base language model is **frozen GPT-2 small, 124M parameters**. A residual cap learns when to read a stored correction and where to write a bounded change into the transformer's hidden states. A null gate can leave the original prediction alone. This makes it possible to measure useful correction, unwanted intervention and computational expense separately.

| Available component | Contribution to the joint experiment |
| --- | --- |
| Explicit read taps and write sites, with aggregate bounded residual updates | Hold the architecture and correction allowance fixed while changing an objective. All-site taps follow blocks 4, 8 and 12; the last bank is before final normalization. Upper-layer restrictions are a separate study. |
| Learned retrieval, null decision and per-record delta acquisition | Retain both intervention and non-intervention outcomes. Acquisition can use adjoint credit or the corrected ePC error-inference mechanism. Reader/controller training can also use BP or an ePC surrogate; these are separate interventions. |
| Existing exposed 300-edit evaluations on zsRE and CounterFact | Check own-prompt editing, retained edits, paraphrases, unrelated locality, near misses and revisions on exactly paired inputs. |
| Full **245,237-position** ordinary-text readout (1,931 windows of 128 tokens, 127 scored positions each) | Measure signed loss changes, fidelity, harmful-change frequency, conditional severity and the worst observed changes at identical prefixes. Keep zero and beneficial changes visible. |
| Saved states, input hashes, execution receipts and operation/process cost records | Rebuild the same memory, establish which implementation produced each result and account for failures. Reuse the existing pipeline; a new approval infrastructure is unnecessary. |
| Local JAX implementation and CPU mathematical checks | Build and validate the objective without PyTorch or remote execution. Any reference implementation in another framework must be ported to JAX before execution here. |

The cap currently supplies neither a normalized probability model over latent correction states nor an autonomous policy loop. Retrieval weights alone are not a complete generative/variational model. There are no specified action preferences, transition model, policy horizon or expected-free-energy action-selection rule. It also lacks a measured accessible-state function W(N), temperature or cross-scale entropy-growth experiment.

Two observations motivate caution. In the available two paired reader seeds, ePC has lower paraphrase retention and about **96–102 times** BP's training process cost; ordinary-text harm does not improve consistently across the CounterFact seeds. Separately, mixing the cap distribution with the original distribution gives a proved **one-nat same-prefix token-loss ceiling**, but does not establish calibrated entropy or preserve all answers. These are useful comparison points, not arguments that the coupled objective must work. See the [reader report](https://github.com/pderp/pc_cap/blob/master/docs/additional_work/PC-reader_report.md) and [bounded-mixture report](https://github.com/pderp/pc_cap/blob/master/docs/additional_work/AW-B_report.md).

## Questions for the authors and the decisions they enable

The following four questions are reproduced verbatim from [the October 2 update, §6](https://github.com/pderp/pc_cap/blob/master/docs/friday-10.02-review/UPDATE-2026-10-02.md). The meeting outcome authorizes further collaboration; it does not record answers to these technical questions.

<!-- BEGIN VERBATIM QUESTIONS -->
1. **The observable.** Is the conditional distribution of positive per-token loss, with the zero/benefit mass reported
   separately, a useful object for the complexity-class framework, or should the coupled model describe predictive
   errors or latent states instead? What would connect that distribution to a state space W(N)? We currently say only
   that we report fitted finite-range behaviour.
2. **Equation 126, positive-κ branch (page 33).** Capex finds that the compensated ratio
   H(W^{1+a})/H(W) · W^{−aκ/(α+dκ)} tends to 1 rather than the printed (1+a)^{1/α}; with α = d = κ = a = 1,
   H(W) = √W − 1 and the ratio is exactly 1 + 1/√W (1.1, 1.01, 1.0001 at W = 10², 10⁴, 10⁸). The κ = 0 branch does give
   (1+a)^{1/α}. Is the secondary scaling exponent intended to be zero for this entropy at κ > 0, or is a different
   limiting prescription meant? (`pc_cap/aw/entropy_feedback_checks.py` reproduces the arithmetic; none of our empirical
   comparisons depend on it.)
3. **Bounded and endpoint-heavy harm.** The mixture's harm has support bounded at one nat and the random reader's fits
   return negative shapes that fail out of sample. How does the framework treat distributions outside the stated
   entropy domain (κ ≤ −1/2 for α = d = 1): compact support with large N_max, truncation, or "not this family"?
4. **For the joint work:** which coupled free energy (physical or informational), over which distribution, with which
   escort weighting and constraints, should be the first JAX objective, and are reference values and gradients
   available from your team's implementation to test against?
<!-- END VERBATIM QUESTIONS -->

| Question | Decision its answer enables |
| --- | --- |
| 1 — Observable | Choose the modeled variable, support, dimension, reference measure and units. Decide whether measured token harm is only an evaluation observable or is itself modeled. Any connection to W(N) needs a separate operational definition and experiment. |
| 2 — Equation 126 | Fix the theoretical statement and limiting prescription used in a future scaling claim. This is not a reason to change current empirical comparisons. If the selected objective does not rely on this result, record that scope rather than blocking all numerical validation on the answer. |
| 3 — Bounded distributions | Decide the objective's admissible parameter/support domain and treatment of compact support, truncation and endpoint failures. Do not identify a negative fitted harm-tail shape with an admissible entropy coupling automatically. |
| 4 — Joint objective | Select the precise free-energy expression, normalization, constraints and ordinary-limit baseline; obtain independent reference values and gradients. This is essential before implementation. |

## First experiment: a pre-registration skeleton to finish together

**Hypothesis.** At a specified useful-retention level, a fixed coupled objective reduces harmful prediction changes relative to its ordinary counterpart. Report the trade-off even if the result is adverse or inconclusive. A reduction in harm accompanied by loss of retrieval is not sufficient evidence of improved correction.

**Two arms, one objective intervention.** Arm O uses the agreed ordinary objective; arm C uses the authors' specified coupled objective at one fixed admissible κ. Before training, write the complete generative and recognition models, likelihood, prior/reference distribution, null-state mass, energy/accuracy terms, signs, coefficients, constraints and estimator. Define which parameters are trained and which distributions are detached. The existing recipe uses ordinary answer cross-entropy, balanced retrieval loss and preservation KL with unit weights. If the joint model requires a new latent-state distribution, both arms must contain that same distribution and architecture; the ordinary arm must be its appropriate ordinary-limit counterpart. The old reader then remains a historical reference, not an architecture-matched control.

**Recommended first isolation.** Use exact JAX autodiff for learning in both arms and adjoint acquisition in both arms, to isolate the objective. Do not compare a coupled/ePC learner with an ordinary/BP learner and attribute the difference to entropy. If the authors require ePC for the first experiment, use it identically in both arms, including settling depth, rate and numerical teacher convention, and review its much larger measured cost. The later objective × credit-rule factorial is a separate possible experiment, with no run planned here.

**Pairing and training.** Three paired seeds, proposed labels 0/1/2, with identical initial parameter trees, episode/token order, training data, architecture, optimizer, clipping, regularization, update schedule and checkpoint rule within each pair. Start from the existing 300-update recipe and unweighted average of checkpoints 150/200/250/300, if the agreed model permits it. Match common parameter initialization; initialize any new latent components identically between arms. Freeze the recipe before evaluation; no best-seed or best-checkpoint selection on exposed outcomes. The [existing reader specification](https://github.com/pderp/pc_cap/blob/master/docs/additional_work/PC-reader.md) gives the training pools and optimizer details. Restrict tuning and profiling to the existing development data; choose κ and any scaling coefficients before the evaluated runs.

**Cost matching needs an explicit choice.** Fix the same update count and data presentations for the primary objective comparison, log actual time/operations and use a common resource ceiling set after profiling. Equal updates and equal ceilings do not guarantee equal consumed compute. If objectives have unequal per-update costs, add an explicitly separate equal-compute sensitivity only if agreed in advance: extra ordinary updates would change the schedule and answer a different question. No artificial repeated calculations count as extra learning. Select the resource unit, allowable mismatch and any sensitivity schedule with the authors before launch; do not call the primary comparison exactly compute-matched without measurement.

**Evaluation population and construction.** Each of six trained readers is evaluated on both datasets: **12 cells**, realization 0, order 100, the same first **300 edits**. These subjects and outcomes are already exposed; this is exploratory follow-up, not new confirmation. Three training seeds quantify sensitivity to initialization, not three independent subject populations. Each reader builds keys and acquires a fresh memory using its own parameters. Keep the frozen base, full read/write interface, five-step adjoint acquisition, null threshold, rare-token gate, stopping, rollback and aggregate bound identical. Do not introduce the AW-B mixture or upper-layer mask into only one arm. Reuse their results as separate context.

**Outcomes.** At 100 and 300 edits retain installed ES, RET-ES, RET-GS, locality, near-miss and revision scoring, with exact numerators/denominators and failed/incomplete cells. At 300 run the full 245,237-position assay in each cell against own cap-off and original-base references at identical prefixes. Report mean KL, signed ΔNLL, zero/benefit mass, firing frequency, harm exceedances, conditional severity, ES99+, maximum and concentration. ES99+ means mean positive harm in the worst one percent of *all* positions, including zeros and a fractional boundary. Present each seed and dataset, paired differences and their spread. Positions share windows and the same text; they are not 245,237 independent experimental replicates. Any window-resampling intervals condition on these fixed readers and populations.

**Decision rule to settle before outcomes.** Agree the useful-retention margins, primary harm endpoint and any across-dataset aggregation before runs. Keep RET-GS and own-prompt retention visible alongside the harm endpoint; retain the existing fidelity benchmarks as reference diagnostics. The AW-B and AW-L acceptance rules are not automatically this study's rules. No success threshold is invented in this proposal, and no claim of statistical superiority follows from three seeds alone. A failed mathematical entry test stops training; an execution failure keeps its charged receipt and missing endpoint, with no silent replacement seed. A scientific negative result is reported.

## Entry conditions: minimum evidence before training

The [coupled-objective note](https://github.com/pderp/pc_cap/blob/master/docs/additional_work/coupled_objective_note.md) specifies these checks. Complete them for the *chosen* objective before model training:

1. Pure JAX values agree with independent analytic/reference calculations and quadrature, including the ordinary κ→0 limit. The existing twelve α=d=1 calibration cases have maximum discrepancy 1.77×10⁻¹¹; they test that family, not an unspecified free energy.
2. Support, normalization, admissible κ, equality at the reference and any proved divergence properties hold. State units/reference measure for continuous densities. Changing entropy alone does not preserve an evidence bound or nonnegative divergence automatically.
3. Autodiff agrees with analytic/finite-difference gradients, including escort-normalization derivatives and any outer root. A normalized expectation's gradient includes the change in its weights; treating those weights as fixed optimizes another objective.
4. Extreme probabilities, invalid domains, support boundaries, stable `log1p`/`expm1` limits, units changes and quadrature refinement have explicit checks. For stochastic estimators, establish convergence and variability against a tractable reference.
5. A tiny deterministic optimization problem behaves as specified; frozen base and evaluation-time reader immutability hold. Verify seed pairing, ordinary-limit parity where claimed, state restore and accounting in the existing harness.

These checks and a small development profile establish readiness to run; they are not evidence that the agent performs better. Keep the one-nat mixture proof distinct from entropy calibration. The earlier bounded κ-surprisal pilot and its closed optional readout neither validate nor refute the new functional.

## Cost and a conditional calendar after October 15

Planning uses completed local accelerator-backed process receipts, not the early 37× reader forecast. The [cost inventory and arithmetic](https://github.com/pderp/pc_cap/blob/master/logs/additional_work/POST-1/planning-evidence.json) identify every source. “Hours” below are summed enclosing process hours, a serial local-GPU reservation proxy; they are not measured GPU-active utilization or a promise of parallel wall time.

| Existing measurement | Samples | Process cost |
| --- | ---: | ---: |
| BP reader, 300 updates, including construction/cache | 3 seeds | 867–907 s; mean 0.245 h |
| ePC reader, same update count | 2 completed seeds | 86,802–88,483 s; mean 24.345 h |
| One 300-edit dataset evaluation, including full harm | 10 cells | 1,686–1,758 s; mean 0.479 h |
| Full harm component within that evaluation | 10 cells | 1,175–1,240 s; mean 0.335 h |

The harm component is **already inside** the evaluation charge. Six BP-cost trainings plus twelve evaluations give **7.21 process-hours**; the same calculation with six ePC-cost trainings gives **151.81 hours**, about 6.3 uninterrupted days. Neither is a measured coupled-objective cost. If coupled training costs c times ordinary training, the cheap-method scenario is approximately **0.735(1+c) + 5.743 hours**, before validation profiles, new distribution/estimator overhead, retries or reporting. A roughly 12-hour local reservation could be a planning envelope only if a new profile supports the cheap-method case; it is not booked or approved. A model with expensive latent integration can invalidate it.

| Phase, after the presentation | Deliverable and conditional effort |
| --- | --- |
| Authors' specification discussion | Resolve the model/function choices, reference cases and primary trade-off. Calendar depends on collaborators' availability; no date is promised. |
| CPU mathematical implementation and validation | Allow roughly 1–3 working days of engineering after agreement, longer for an unresolved estimator. This is a planning estimate, not a measured benchmark or reserved resource. No model-scale GPU training yet. |
| Development-only profile and recipe agreement | Measure compilation/cache, full-update time, host/device memory and readout overhead for both arms. Existing short profiles use ten updates, ten edits and eight harm windows; extrapolation must allow occupancy effects. Set the actual ceiling and compute comparison here. |
| Three-seed experiment | After agreement and resource availability, execute the two arms and all twelve evaluations. Use the measured profile to replace the scenarios above. No experiment starts because an estimate alone looks affordable. |
| CPU analysis and joint interpretation | Allow roughly 1–2 working days for paired tables, harm plots and a short joint report. Preserve adverse outcomes and separate objective effects from a quieter gate. |

These are dependencies for post-conference planning, not additions to the current queue. **No new fits on or after October 6 in the conference programme; current experiments stop October 9 at 17:00 EDT; presentation October 15.** Post-conference execution would require its own agreed recipe and resource allocation.

## Subject reserves after Option R

The [Option R allocation receipt](https://github.com/pderp/pc_cap/blob/master/logs/additional_work/R/preparation-v1.json) records the following after excluding all roles in primary realizations 0–2. Option R reserves 1,350 subjects per dataset: 1,000 edits, 100 outside, 100 near-support, 100 near-neighbour and 50 revision subjects; locality reuses outside rows.

| Dataset | Available before Option R | Option R reservation | Remainder at that allocation |
| --- | ---: | ---: | ---: |
| zsRE | 2,034 | 1,350 | **684** |
| CounterFact | 2,071 | 1,350 | **721** |

These are certified-universe margins against the recorded exposures, **not a new certification of unexposed subjects on the eventual collaboration date**. Later exposures can reduce them. [HT-16](https://github.com/pderp/pc_cap/blob/master/docs/tasks/HT-16.md) independently replayed the zsRE margin on September 29. Before any fresh study, replay the exclusion register, cross-dataset identities, role eligibility and family/pair constraints against all subsequent exposure records. “Fresh” does not mean absent from GPT-2 pretraining.

The deferred/stopped Option R v0 cells do not release subjects: the same populations belong to its learned/random comparisons. Keep all reservations. A new 1,000-edit realization cannot fit either remaining margin. A single 300-edit population plus the same 350 endpoint subjects would require 650 subjects, leaving only 34/71 by raw count; that arithmetic does **not** establish role/family feasibility or authorize a draw. Three independent 300-edit populations cannot fit even before adding their endpoints. This first proposal therefore consumes **none** of these reserves and reuses the exposed 300-edit streams. New sources or a smaller freshly certified study would need a separate population design; no MQuAKE reserve is allocated here.

## What we would ask the collaborators to contribute

The authors' group would specify the functional, probability model, constraints and trusted numerical examples; charlie and the local implementation collaborators would supply the JAX port, matched testbed, validation and measured outcomes. Together we would finalize the trade-off criterion and interpretation. A later active-inference study could add preferences, observation/transition models and competing audit policies, tested against fixed/random audits at equal resource cost. That requires another experiment; the present proposal stops at a defined, testable learning objective.

The immediate deliverable is a shared mathematical specification with independent value/gradient examples and a short completed version of this skeleton. No implementation or experiment has been launched for POST-1, and no correspondence has been sent on charlie's behalf.
