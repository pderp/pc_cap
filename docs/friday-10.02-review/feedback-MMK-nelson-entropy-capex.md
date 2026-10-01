# Bringing the entropy feedback into the October experiments

Capex · 1 October 2026 · for charlie, Capstan, and the 2 October discussion

**Recommendation: keep the remaining PC experiments, add a focused analysis of the saved harm distributions, and use the meeting to specify a subsequent coupled-entropy experiment.** This can strengthen the presentation's connection between predictive coding, extreme errors, and active inference without replacing the experiment just as its replications are arriving. Experimental completion remains **9 October, 17:00 EDT**, not presentation day, 15 October. The existing training-start cutoff is 6 October, midnight EDT.

I read the supplied 42-page manuscript, including its methods and references, and `MMK.txt` completely. I also read the Friday primer and Capstan's [response](feedback-MMK-nelson-entropy.md), committed as `07db745`. The manuscript is Kenric P. Nelson's *The unique, universal entropy for complex systems*, supplied as `NelsonUniqueUnivEntropy2026Sep27.pdf`. These recommendations concern that version. Its mathematical claims are the author's proposed framework; this review does not certify the entire proof.

The response explicitly accepts postponing implementation of the entropy function and offers collaboration with the coupled-AI team. I agree with Capstan about the resulting priority: **analysis now; a properly specified new objective later.** I disagree with promoting today's fitted harm distributions to three established complexity classes. Below I explain the distinction, propose a smaller useful analysis, and give concrete questions for tomorrow.

## What the feedback adds

The paper connects three things: how the number of accessible states grows with system size, the shape and scale of a maximizing probability distribution, and an entropy calibrated to that growth. In broad terms, a thermometer needs a scale appropriate to what it measures; the paper proposes a corresponding calibration for uncertainty in nonlinear systems.

Its parameters separate the stretch of the variable, α, from functional nonlinearity, κ, and informational scale, σ. For the one-dimensional, one-sided case α = 1, its density is

\[
f(x)=\sigma^{-1}(1+\kappa x/\sigma)^{-1-1/\kappa}.
\]

This is a generalized Pareto density, with the exponential recovered as κ approaches zero. That identity provides a concrete connection to our recorded losses. The [SciPy definition](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.genpareto.html) uses the same shape parameter, called `c` there. For α = 1, fitting that family requires no new entropy optimizer.

But three different objects must stay separate:

| Object | What we currently have | What a result would mean |
|---|---|---|
| A transformer's next-token probability distribution | The model and recorded likelihood-based endpoints | Predictions and fidelity at specified prefixes |
| The distribution of harm across evaluated positions | Saved ΔNLL vectors, with strong dependence within text and repeated evaluations of the same text | Frequency and severity of unintended changes on this assay |
| Accessible-state growth W(N) as degrees of freedom N increase | No operational definition or measurement in this experiment | The asymptotic complexity classification discussed in the reviewer's note |

The connection from the second row to the third needs a model identifying the random variable, constraints, and state space. A fit alone does not supply it. The original [Hanel–Thurner classification](https://arxiv.org/html/1005.0138v2) and [sample-space scaling formulation](https://arxiv.org/abs/1806.02386) concern limiting state-growth properties. Our edit count is not automatically their N; memory records, observed tokens, and accessible microstates are different quantities. Even acquiring 3,000 edits would not by itself make an entropy-versus-edit-count curve a test of H(W(N))/N.

The useful experimental question is therefore: **do the cap architecture and learning rule alter how often harmful retrievals occur, how severe they are when they occur, and which distributional descriptions fit those severities?** This is a substantial scientific addition without claiming a thermodynamic classification of a transformer.

## What to retain and what to change before the cutoff

The current schedule is anchored to [lead-queue item 147](../lead_queue.md): complete the three-seed ePC reader comparison, resume the 16 learned/random Option R cells, then run the upper-layer 2×2. Its estimate places completion around 5 October. These are estimates, not newly measured timings. The v0 Option R cells remain deferred under DEC-080.

Keep this queue. The PC reader study is our most direct remaining test of whether predictive-coding training changes behavior. Seed 0 alone shows less paraphrase generalization and less ordinary-text harm than its BP pair; the remaining seeds matter for interpreting that trade-off. Tail analysis should include them when complete, rather than treating one quiet seed as a win. The upper-layer study tests the interface that determines where the residual correction can act. Neither run needs a changed loss or instrumentation for the proposed analysis.

| Addition | Concrete deliverable | Timing and limit | Scientific payoff |
|---|---|---|---|
| **First priority: saved-vector tail analysis**, a narrowed version of Capstan's HT-17 | One report and figure set separating harmful-event frequency, conditional severity, and uncertainty in fitted shape | CPU only; begin with completed main contrasts after the 2 October discussion; aim to finish fitting by 5 October | Tests whether the apparent distributional differences survive threshold and population checks |
| **Small calibration demonstration** | Known-distribution checks of parameter conventions and the entropy formula; optionally one synthetic figure | Half a working day initially, local CPU; stop if it becomes a library-port project | Shows exactly what would need to be implemented for the proposed theory |
| **Presentation wording** | A revised connection between the κ pilot, AW-B bound, PC results, and the proposed active-inference loop | 6–8 October, using the completed results | Makes the three themes explicit while preserving the distinction between measured and proposed |
| **Optional full κ-pilot readout** | Re-evaluate the existing saved pilot readers on the already defined full ordinary-text inventory | Only if checkpoints restore exactly, a short profile fits the remaining budget, and Capstan confirms queue slack | Increases the information available about the existing pilot, without another training comparison |

The CPU estimates are planning allowances, not benchmarks. Start with a few representative cells and measure throughput before expanding to every saved cell. Do not open a large framework or refit every historical population as a prerequisite to a useful result. No new model, JAX training run, or GPU job was launched for this review.

### A small, defensible tail analysis

1. **Define the observable and population once.** Use signed Δ = NLL(cap) − NLL(cap-off), in nats at the same prefix. Retain the benefits, near-zero changes, and positive harms. Report the actual retrieval/firing indicator separately where saved: Δ > 0.01 is a harmful-change indicator, not the firing rate. A firing can improve a prediction or change it only slightly. Distinguish a true zero from floating-point noise and from clipping negative values to zero.
2. **Reuse the established collectors and saved vectors.** Start with learned, stable v0, and random caps on the common Stage-4 text population; show both datasets and each realization. Add the paired AW-B contrasts and complete BP/ePC reader seeds. Keep the 4,064-position legacy/pilot assay separate from the 245,237-position assay. Repeated orders and readers do not create new independent text positions.
3. **Fit a declared conditional variable.** For threshold u, fit excesses Y = Δ − u given Δ > u, not the unshifted selected losses with location forced to zero. Report the exceedance probability as well as the conditional fit. Capstan's already inspected thresholds 0.01, 0.1, 0.5, and 1 nat are a reasonable sensitivity grid; call the analysis exploratory, since we have seen the prototype. Show counts and distinct contributing windows at each threshold, including empty cases.
4. **Begin with the α = 1 generalized Pareto and its exponential restriction.** Compare predicted survival and held-out-window likelihood on the same conditional support. If both fail visibly, one correctly normalized alternative such as a lognormal conditioned above u is more informative than assigning the nearest class. A free-α fit can be a secondary sensitivity check; sparse tails are unlikely to identify both parameters reliably. For general α in the manuscript's one-dimensional family, the asymptotic survival exponent is α/κ, not 1/κ.
5. **Preserve dependence and between-run variation.** Resample identical window identities jointly across paired cells. Report realization, order, and reader-seed variation separately from uncertainty over text windows. If adjacent windows share source documents or nearby text, use those larger available blocks or label the window bootstrap as conditional on that unverified dependence assumption. Never bootstrap the same 245,237 positions across fifteen cells as millions of independent observations. A pooled mixture of different fitted distributions may have a different shape from any one condition.
6. **Permit “not identified.”** Suggested practical screening: fewer than 100 excesses or fewer than 30 contributing windows means no headline shape estimate; keep counts and empirical curves. These are proposed reporting rules, not a theorem about statistical power. Above the screen, optimizer convergence, profile shape, threshold stability, and predictive fit still matter. Mark support-boundary or invalid fits explicitly. Do not coerce an inconvenient fit into an admissible entropy domain.
7. **Keep the useful outputs small.** One panel shows harmful-event frequency versus conditional severity; a second shows empirical survival and fitted curves with threshold sensitivity. A κ-versus-σ plot is an optional parameter plot, labelled by population and threshold, not a map of established universality classes. Retain ES99+, maxima, and efficacy beside it. The analysis succeeds if it establishes differences *or* shows that the tail family is not identifiable.

Do not use these already exposed evaluation tails to tune another reader, a new κ, or the AW-B mixture. This addition describes and tests models of existing outcomes; it does not change the registered primary results.

### Where I would revise Capstan's interpretation

Capstan's prototype is useful evidence that this analysis is feasible. I have not independently reproduced its empirical fits or intervals; its own document calls them preliminary. Several interpretations should change before they enter the talk:

- **“Three different complexity classes” is too strong.** A positive generalized-Pareto estimate is a fitted positive shape on an observed range. It does not establish an infinite asymptotic power law or the system's W(N). Conversely, κ around 0.05 with a reported interval excluding zero does not establish the exact exponential class κ = 0. Describe it as a small positive fitted shape, and compare the exponential approximation explicitly.
- **The reported threshold sensitivity matters to the conclusion.** The stable-v0 prototype falls from about 0.8 near the low threshold to about 0.16 above 2 nats. That could reflect finite-range curvature, population mixtures, sampling variation, or a cutoff. It does not justify “the power-law body is real” or a measured infinite variance. Infinite variance is a property of extrapolating a particular fitted unbounded family, not a measurement from this finite assay.
- **The scale is conditional on the modeled variable.** A generalized-Pareto excess fit has scale σ_u for Y = Δ − u. For an exact GPD, σ_u = σ_0 + κu. It is not automatically the original distribution's σ or the cap's physical temperature. State the threshold, origin, and units.
- **AW-B establishes a bound, not a unique distribution family.** With q = ρp₀ + (1−ρ)p_cap and ρ = e⁻¹, q(y) ≥ e⁻¹p₀(y), so ΔNLL ≤ 1 nat at the shared prefix. This proves a bounded upper tail for this observable. It does not prove that its conditional density is a coupled exponential with κ < 0, or that the transformer changes universality class. Say “we impose a one-nat ceiling on measured per-position harm.” Do not extend it to unmatched free-running prefixes or whole sequences.
- **Some prototype κ estimates cannot be inserted into the proposed entropy.** The manuscript states κ > −α/(α+d); with α = d = 1 this is κ > −1/2. The reported AW-B estimates near −1.3/−1.4, and several pilot fits, lie outside it. Moreover, unconstrained GPD likelihood can become unbounded for shape below −1 as the fitted upper endpoint approaches the largest observation. Such optimizer output needs an endpoint/likelihood check, not an entropy column or ordinary confidence interval. This follows directly from the GPD density's endpoint exponent −1−1/κ.

There is also a small formula correction before implementation: for the one-sided α = d = 1 family, Table 4's calibrated entropy is **1 + ln_{κ/(1+κ)} σ**, not 1 + ln_{(1+κ)/κ} σ. Direct integration gives Z_q = σ^{1−q}/(1+κ), q = 1+κ/(1+κ), and hence H = ((1+κ)σ^{κ/(1+κ)}−1)/κ. A continuous entropy also needs a declared coordinate/reference measure; use a fixed dimensionless coordinate such as loss divided by one nat. A fitted entropy of conditional harm should not be labelled the transformer's entropy. I would initially omit this column from the empirical comparison and demonstrate it on known distributions instead.

## The κ pilot and a future coupled objective

Our answer-loss code is [coupled_surprisal](../../src/pccap/revision_v1/train.py). For ordinary surprisal ℓ = −ln p it computes

\[
L_{\rm pilot}(\ell)=(1-e^{-\kappa\ell})/\kappa.
\]

For positive κ this saturates at 1/κ and its derivative with respect to ℓ is e^{−κℓ}. It downweights very surprising targets. That remains a legitimate experiment in a bounded loss; its registered result remains intact.

Nelson's Equation 24 instead combines a transformed inverse probability, a normalized independent-equals (escort) average, and an outer 1/α power. With q = 1+ακ/(α+dκ), Z_q = Σp_i^q, and conversion factor one, the proposed discrete expression is

\[
H(p)^\alpha/\alpha=(Z_q^{-1}-1)/\kappa.
\]

The pointwise factor inside that escort average is ln_κ(p^{−α/(α+dκ)}). For κ > 0 it grows with surprisal, whereas our answer loss saturates. These are not interchangeable uses of a coupled logarithm. The full escort normalization also changes derivatives. At κ = 0, H^α/α tends to Shannon entropy; H itself does so directly only at α = 1.

For illustration, at κ = 0.5 and α = d = 1, increasing surprisal from 1 to 10 nats changes our answer loss from 0.787 to 1.987. The manuscript's pointwise factor changes from 0.791 to 54.063. These factors are **not** a comparison of complete objectives or their training gradients: the latter still requires the escort expectation. The reproducible arithmetic is linked below.

Accordingly, slide 8 should say: **“We tested a bounded κ-deformed answer loss. We have not yet tested the calibrated coupled entropy or coupled free-energy objective.”** Its null result neither confirms nor refutes the new objective. Nor does it predict the sign of a fitted κ in an entirely different distribution, the resulting harm.

A useful small calibration exercise would verify normalized α = d = 1 densities, the slope condition x f′(x)/f(x) = −1 at x = σ, the escort moment E_escort[X] = σ, and the κ → 0 limit. Synthetic κ = 0, 0.25, 1, and 2 distinguish finite ordinary means from cases where the ordinary mean diverges while the escort moment remains finite. Known negative-shape examples must respect the stated entropy domain. This is a local CPU demonstration of formulas, not evidence that the language model obeys them. Any later differentiable implementation should be JAX, with finite-difference gradient checks and normalization tests; no PyTorch or Colab path is proposed.

Before training, the coupled-AI collaboration needs to specify the distribution being optimized, the reference/target distribution, the constraints, the normalization, and whether gradients pass through escort weights. Minimizing an entropy of the model's own predictions is not automatically a correct data-fitting objective. Likewise α, κ, and d cannot be assigned from a layer count or hidden width without defining the modeled variable. The manuscript's referenced code can guide a port once those choices are agreed; its older notebooks are not automatically an implementation of every equation in this supplied version.

## Keeping active inference and predictive coding central

The talk can make an intelligible three-part argument:

1. **Predictive coding:** compare the completed error-based credit/training experiments with adjoint/BP controls, including generalization, false retrievals, harm, and computational cost. Present all completed reader seeds. This is an empirical result even if PC does not win.
2. **Extremes:** ask whether rare errors have a severity distribution that averages hide, and whether its shape is consistent across populations and thresholds. Contrast a learned trade-off with AW-B's analytically imposed ceiling.
3. **Active inference:** explain why a residual agent should consider the consequences of intervening as well as prediction error. Our fixed gate and investigator-selected audits do not yet implement expected-free-energy policy choice, epistemic action, or a formal Markov blanket. The paper offers a candidate mathematical basis for the next implementation.

I would mention coupled free energy and the paper's proposed pseudo-Markov blanket as collaboration directions, without selecting a particular equation as our training objective before the authors clarify the mapping. A boundary in the architecture, or zero measured cross-covariance, does not by itself demonstrate the conditional independences of a Markov blanket. This preserves the [implemented/measured/proposed distinction](../presentation/abstract_to_testbed.md) while making the research ambition clear.

For the final stages, the highest-return extra GPU use—if any—is the existing κ readers' full harm readout, not a hurried new entropy trainer. Capstan's estimate of roughly four hours is provisional until restoration and throughput are verified. If saved state is insufficient, or this displaces the remaining PC/interface results, drop it. No retraining is needed merely to make the story match the manuscript.

## A specific manuscript question to resolve

I found an apparent algebraic discrepancy in the positive-κ branch of **Equation 126, page 33**, which also bears on Equation 129's secondary scaling exponent. I checked the rendered PDF, not just extracted text. This is worth asking the author privately and precisely; it is not a reason to abandon the empirical analysis or a claim that the entire framework has been disproved.

For a uniform distribution, ignoring a constant that cancels in ratios,

\[
H(W)=\left[\frac{\alpha}{\kappa}
       \left(W^{\alpha\kappa/(\alpha+d\kappa)}-1\right)\right]^{1/\alpha}.
\]

For fixed positive κ, H(W) is asymptotic to a constant times W^{κ/(α+dκ)}. Therefore the compensated ratio printed in Equation 126,

\[
\frac{H(W^{1+a})}{H(W)}W^{-a\kappa/(\alpha+d\kappa)},
\]

tends to **1**, whereas that equation gives (1+a)^{1/α}. A particularly simple substitution is α = d = κ = a = 1. Then H(W) = √W−1, and the ratio is exactly **1 + 1/√W**, which tends to 1, not 2. At W = 100, 10,000, and 100,000,000 it is 1.1, 1.01, and 1.0001. The κ = 0 branch does yield (1+a)^{1/α}; the order of these limits matters.

The question is: **should the positive-κ secondary scaling exponent be zero for this displayed entropy, or is a different limiting prescription intended?** Resolving this matters before presenting fitted α and κ as coordinates of the claimed complete asymptotic classification. Our finite harm comparisons and the α = 1 GPD identity do not depend on the disputed limit.

## What to ask tomorrow, and a compact handoff

The most useful meeting outcome is agreement on the observable and the next experiment, rather than an instruction to add κ somewhere in the loss:

- Is conditional positive harm a useful distribution for this collaboration, with frequency and benefits reported separately, or should the coupled model describe predictive errors/latent states instead?
- What connects that chosen distribution to a state space W(N)? Can we agree that this talk reports fitted finite-range behavior without claiming that connection has been measured?
- Which precise coupled divergence or free energy, with which escort weighting and constraints, should be the first JAX objective? Are there reference values and gradients from the team's implementation?
- How should we handle bounded/endpoint-heavy harm distributions outside the manuscript's stated entropy domain, and is Equation 126 intended as printed?

Proposed division: Capex builds the agreed CPU tail analysis using existing readers/collectors; Capstan checks a small independent slice and incorporates agreed language into the presentation. Capstan continues the current GPU dispatch. Finish the analysis fits by 5 October, reports and slides on 6–8 October, and freeze experimental evidence at the existing 9 October deadline. If the analysis grows, cut the optional free-α fit, entropy column, and κ-pilot GPU extension first. One useful comparison is enough; a new reporting system is unnecessary.

**Work completed for this review:** full input ingestion, comparison with the current queue and Capstan's response, visual verification of Equations 24/126, and CPU algebra checks. No existing project file or live experiment was changed. The proposed HT-17 experiment has not been claimed or executed on the strength of Capstan's conditional suggestion.

Reproducible check: `PYTHONDONTWRITEBYTECODE=1 /home/derp/cap/venv/bin/python aw/entropy_feedback_checks.py`. It checks the exact counterexample, the κ = 0 control, a constructed W/H inverse identity, and the two pointwise factors; it does not fit experimental data. Output: [equation-checks.json](../../logs/literature/nelson-entropy-20261001/equation-checks.json). Script: [entropy_feedback_checks.py](../../aw/entropy_feedback_checks.py). The run and Ruff check passed. Input hashes and the complete text extraction are under [logs/literature/nelson-entropy-20261001](../../logs/literature/nelson-entropy-20261001/). Rendered reference pages are in the sibling `assets/literature/nelson-entropy-20261001/` directory. These new files are left uncommitted for the lead.
