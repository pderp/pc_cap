# A coupled objective for the residual agent: specification before implementation

2026-10-01 — Capex, CAL-1. Discussion starting point for the authors' group, not an approved training experiment. Local JAX only. Finish current experiments by October 9, 17:00 EDT; this note does not expand that scope.

## What we have checked

For the manuscript's one-sided, location-zero, α=d=1 family, use

\[
f_{\kappa,\sigma}(x)=\sigma^{-1}(1+\kappa x/\sigma)^{-1-1/\kappa},\quad x\ge0,
\]

with the exponential limit at κ=0. Let r=κ/(1+κ), q=1+r and Pq(x)=f(x)^q/Zq, where Zq=∫f^q. The proposed entropy in this restricted case is Hκ=EPq[lnκ(f⁻ʳ)], with lnκ(z)=(zκ−1)/κ; take the continuous κ=0 limit. Direct quadrature gives

\[
\int f=1,\quad (xf'/f)_{x=\sigma}=-1,\quad
Z_q=\frac{\sigma^{-r}}{1+\kappa},\quad E_{P_q}X=\sigma,\quad
H_\kappa=1+\ln_r\sigma.
\]

The twelve cases κ∈{0,.25,1,2}, σ∈{.5,1,2} pass with maximum absolute discrepancy 1.77×10⁻¹¹; a small-κ check recovers exponential log densities. Ordinary EX=σ/(1−κ) exists only for κ<1, while the normalized escort mean remains σ in all tested cases. These are **known-distribution calibration checks**, not fits to our data, a verification of every manuscript theorem, or evidence that this objective improves an agent. See [numerical report](../../logs/additional_work/CAL-1/final/report.md), [exact inputs/results](../../logs/additional_work/CAL-1/final/checks.json), and [implementation](../../aw/calibration_demo.py). The source is the locally shared [Nelson manuscript](../../../NelsonUniqueUnivEntropy2026Sep27.pdf), particularly the informational-scale definition, generalized logarithm, independent-equals distribution and calibrated entropy formulas.

Our earlier pilot's answer term was Lκ(ℓ)=(1−exp(−κℓ))/κ. Its derivative exp(−κℓ) suppresses large-surprisal gradients and its ceiling is 1/κ. The pilot also has a separately specified coupled-divergence term; neither term by itself supplies the normalized escort functional above or a full coupled free-energy agent. The failed pilot retention/separation rule therefore neither confirms nor refutes this framework. Similarly, an HT-17 GPD shape fitted to a *loss distribution* is not automatically the κ governing a latent-state model.

## Decisions needed for a JAX implementation

1. **Define the random variable and units.** A concrete first candidate is a distribution over latent correction states conditional on a query and memory, with generated tokens as observations. Decide whether the modeled variable is instead a residual vector, token outcome, or environmental state; these are different distributions. State support, dimension d, stretching α, location, scale and any constraints. For a continuous density, declare the reference measure/units before applying a nonlinear logarithm; changing units must not silently redefine the objective. Our finite loss samples do not identify accessible-state growth W(N), temperature or an asymptotic class.

2. **Write the complete generative and variational models.** Specify the frozen transformer's role, the likelihood p(o|s,a), prior p(s), recognition density Qθ(s|o), memory/read/write variables and null action. A deterministic transformer is not already a normalized prior over correction states. State which parameters and distributions can change at each stage and which references are detached. Include the probability mass of null decisions, not just accepted corrections.

3. **Choose the coupled free-energy functional explicitly.** Obtain agreement on how calibrated entropy, a reference distribution and energy/accuracy terms combine, with signs, coefficients, normalization and constraints. Do not assume that substituting a generalized entropy into an ordinary variational free-energy formula preserves a bound on model evidence or produces a nonnegative divergence. Those are properties to prove or test for the selected definition. A fixed κ should be the first implementation; learning κ adds an identification problem and extra derivatives. Specify its admissible domain and its relationship, if any, to measured tail shapes.

4. **Differentiate the normalization.** For fixed q, a finite-support escort implementation can use `softmax(q * logp)` with stable normalization. If Hθ=Ewθ[hθ] and wθ=softmax(uθ), its gradient is E[∇h]+Cov(h,∇u); ignoring the second term optimizes a different objective. Here u=q logp, and learned q would contribute ∇q·logp too. Continuous densities need a declared quadrature or sampling measure, support treatment and estimator; a token minibatch is not automatically an exact normalized distribution. Use `log1p`/`expm1` and a checked zero-κ limit. For α≠1, retain the specified outer root and its domain and derivative; do not extrapolate our α=1 demonstration.

5. **Separate learning from policy selection.** First compare a specified learning objective with ordinary training using matched initialization, data, schedules and measured cost. An active-inference extension additionally needs preferences, a transition/observation model, possible audits/actions, a horizon and an expected-free-energy policy rule. Compare informative audits with fixed/random audits at the same resource budget. The present cap interfaces establish neither autonomous epistemic action nor a Markov-blanket theorem.

## Minimum evidence before model training

Implement pure JAX functions and test them against the independent quadrature results, ordinary κ=0 limits, support/normalization constraints, reference equality and any *proved* divergence properties. Compare autodiff gradients to analytic/finite-difference gradients, explicitly including escort normalization and any outer root. Test extreme probabilities, invalid domains, dependence on units/reference measure and quadrature refinement. Verify reader/base immutability and a tiny deterministic optimization problem before a GPU experiment.

Only then choose a small development experiment with frozen populations and reader seeds, reporting retention, firing frequency, conditional loss severity, ES99, maximum, fidelity and actual process/operation costs. A quieter reader can simply have lost useful retrieval. Keep the one-nat query-mixture guarantee as a distinct analytic control; it does not demonstrate entropy calibration. No PyTorch port, library import, training run or new scientific selection rule is included in CAL-1.
