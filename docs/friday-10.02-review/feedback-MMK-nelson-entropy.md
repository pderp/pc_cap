# Response to the reviewer's note and Nelson's entropy paper — what can still change before 15 October

Capstan, 1 October 2026, 13:30 EDT. Inputs read in full: `/home/derp/cap/MMK.txt` (the reviewer's reply to the Friday
primer) and `/home/derp/cap/NelsonUniqueUnivEntropy2026Sep27.pdf` (K. P. Nelson, *The unique, universal entropy for
complex systems*, 42 pages, built 1 Oct 2026). Numbers in §3 are from a prototype I ran today on the saved per-position
harm vectors; they are not yet a report of record.

> **Revision, 1 October 13:30 EDT, after Capex's review (`feedback-MMK-nelson-entropy-capex.md`).** Capex's review
> corrects this document in six places and I accept all six. (1) A fitted generalized-Pareto shape on an observed range
> is not a "complexity class" in the paper's sense, which concerns the growth of accessible states W(N); this experiment
> defines no such N, so the talk reports fitted finite-range shapes, not classes. (2) A shape estimate below −1 (the
> mixture, the κ 0.5 pilot arm) sits at the likelihood's endpoint boundary and outside the entropy domain κ > −1/2; it
> is optimizer output, not an estimate. The 1-nat mixture is a proven ceiling, not a fitted family. (3) "Infinite fitted
> variance" is an extrapolation of an unbounded family, not a measurement; the stable-v0 shape's fall from 0.8 to 0.16
> across thresholds could be curvature, mixture, sampling or a ceiling, and does not establish a power-law body.
> (4) Δ > 0.01 is a harmful-change indicator, not the firing rate; the gate's firing count is saved separately and
> differs (e.g. 18 firings vs 15 positions > 0.01 for BP seed 0 on zsRE). (5) The excess scale σ_u depends on the
> threshold (σ_u = σ_0 + κu for an exact GPD); it is not the distribution's σ or a temperature. (6) The prototype
> bootstrap understates uncertainty by an unknown amount. Also corrected: the one-sided α = d = 1 calibrated entropy is
> 1 + ln_{κ/(1+κ)} σ, not 1 + ln_{(1+κ)/κ} σ. The original wording below is kept for the record with these corrections
> applied inline where a reader could otherwise be misled; the deck text in `talk-text-B-C-D.md` now uses Capex's
> conservative language, and the proposed lane A is narrowed to Capex's "saved-vector tail analysis" specification.
> Capex also found an apparent algebraic discrepancy in the manuscript's equation 126 (positive-κ branch), added to §6.

**Short answer.** The feedback can be brought into play before the talk, but on the analysis side, not as a new
training objective. The reviewer's central object, the complexity class (κ, α) with an informational scale σ, can be
fitted to the harm distributions we have already measured, on CPU, from saved data, in about two working days. A
first pass shows the three cap families have visibly different fitted shapes and frequencies on the observed range,
which is a sharper statement than the talk's current "rare, severe, concentrated; no class claimed" [revised: "fitted
shapes", not "classes"; see the revision note]. Implementing the calibrated coupled entropy or the coupled
free energy as a learning objective does **not** fit: the GPU is booked to 5 October, the design has the subtleties the
reviewer himself flags, and a rushed implementation in front of its author is the wrong risk. He says delaying it is
fine; I recommend taking him at his word and planning it with his team after the conference.

---

## 1. What the two inputs say that bears on us

**The reviewer's note** makes three points. (i) Our line "rare, severe, concentrated harm, and we refuse to claim a tail
class" is exactly where his framework enters: the complexity classes are what guarantee that entropy per degree of
freedom, H(W(N))/N, tends to a constant, and the class is "directly related to the tail decay or shape of the
maximizing distribution, given a constraint on its informational scale". (ii) His updated proof rests on three axioms:
the complexity class (κ, α), the informational scale σ, and a nonlinear differential equation combining them; together
they determine a unique entropy. (iii) It is fine that we delayed implementing that entropy, which "does have a number
of subtleties"; integration with the team working on coupled AI algorithms is a discussion for later.

**The paper**, in the parts that matter for a talk on a frozen transformer with a cap:

- Two nonlinearities classify complex systems: a stretch α (short-range, the power of the variable) and a coupling κ
  (long-range, the power of the function). The one-parameter family that carries them is the coupled stretched
  exponential, y = exp_κ(x^α/α)^{−(α+κ)/(ακ)} with exp_κ(x) = (1+κx)^{1/κ}. Its asymptotes: exponential (κ = 0,
  α = 1), stretched exponential (κ = 0), power law with exponent −(1+α/κ) (κ > 0), compact support (κ < 0). The
  asymptotic tail shape is κ/α; near the origin the shape is α.
- **The informational scale σ** (Definition 1) is the unique scale that separates linear from nonlinear uncertainty: the
  point where d ln f / d ln x = −1, i.e. where the surprisal's slope is 1/σ. For the one-sided coupled exponential
  (α = 1) the density is (1/σ)(1+κx/σ)^{−1/κ−1}: **this is exactly the generalized Pareto distribution with shape
  ξ = κ and scale σ** (his Table 1). So a peaks-over-threshold fit of the generalized Pareto is, in his vocabulary, a
  measurement of the complexity class and the informational scale of the tail.
- The calibrated entropy (Theorem 4) has three components: a coupled logarithm ln_κ, an average over the
  "independent-equals" distribution f^{ι}/∫f^{ι} with ι = 1 + ακ/(α+κ), and a root 1/α outside the average. For a
  coupled stretched exponential it reduces to d/α + ln_{(α+dκ)/(ακ)} Z: energetic plus generalized-logarithmic
  configurational degrees of freedom, with the nonlinear degrees of freedom removed. BGS entropy of the same
  distribution carries an extra κ-dependent term (1 + ln σ + κ for the coupled exponential).
- Thermodynamics: the temperature is the informational scale, T = σ/k_B, independent of κ; internal energy grows as
  T^{ι}; there are two coupled free energies, physical and informational, related by a hyperbola; the informational one,
  k_B T (ln_κ Z − 1/(1+κ)), "is ideally suited to form natural gradients for the microscopic training process of
  variational inference".
- Applications paragraph: coupled VAE trained for κ from 10⁻⁵ to 10⁵ via the independent-equals latent; the coupled
  free energy permits a "pseudo-Markov blanket" in which non-equilibrium fluctuations cross the boundary while
  agent/environment cross-terms stay zero; Rényi with index q = ι is a partial fix, the full discount of nonlinear
  degrees of freedom needs the calibrated entropy.

Nothing in the paper is about language models, editing or per-token loss; the connection to us is that **our harm
distribution is a shape–scale distribution on x ≥ 0 and his framework tells us which two numbers describe it**.

---

## 2. Where our work already touches this, and where it does not

| our element | his object | status |
|---|---|---|
| per-token loss change Δ on 245,237 positions, per cell, saved as vectors (270 cells; AW-B arms; PC-reader cells; κ pilot at 4,064 positions) | a sample from a shape–scale distribution on x ≥ 0 with a large zero mass | **fit (κ, α, σ) on it: not done yet, feasible now** |
| ES99+, maximum, exceedances, half-mass concentration | descriptive tail statistics | done; stay |
| "no tail class claimed" | the class is the thing he measures | change to "within the coupled-exponential family the fitted class is …, with its uncertainty" |
| κ pilot: −ln p → −ln_κ p on the reader's answer surprisal | one of the three components of his entropy (the coupled log), applied to a surprisal, not to an entropy; no independent-equals average, no 1/α root, no informational-scale calibration | done; reframe precisely |
| AW-B mixture bound, loss ≤ 1 nat per token | moves the harm distribution into the compact-support class (κ < 0, N_max = 1 nat) | done; reframe as a class change and measure it |
| coupled free energy as training objective; precision as risk; pseudo-Markov blanket | his proposals for variational and active inference | not built; stays proposed |

---

## 3. Prototype: the complexity class of the harm, from saved vectors (today, CPU, minutes)

Method: for each cell, take Δ = loss_cap − loss_capoff at every scored position; take the exceedances over a threshold
u (u = 0.01 nats, i.e. the positions the cap measurably touched); fit the generalized Pareto with location 0 by
maximum likelihood (scipy), which is Nelson's coupled exponential with κ = shape and σ = informational scale; also fit
the stretched version with α free by numerical maximum likelihood. Uncertainty by resampling windows (200 draws).
The zero mass (the fraction of positions with Δ ≤ 0.01, 99.7–99.98 %) is reported separately; it is a harmful-change
indicator, not the gate's firing rate [revised], and is not part of the shape.

| condition (15 cells each unless noted) | dataset | positions > 0.01 per cell | κ̂ (per-cell range) | pooled κ̂, window bootstrap 95 % | σ̂ nats | fitted shape on the observed range (exploratory) [column heading revised] |
|---|---|---:|---|---|---:|---|
| learned reader v5 | zsRE | 391 | 0.050 (0.043–0.059) | 0.052 (0.024–0.079) | 1.54 | small positive fitted shape, near the exponential restriction; excess scale 1.5 nats at u = 0.01 |
| learned reader v5 | CounterFact | 732 | 0.056 (0.029–0.098) | 0.058 (0.036–0.077) | 1.79 | small positive fitted shape; excess scale 1.8 nats |
| stable v0 cap | zsRE | 255 | 0.746 (0.434–1.029) | 0.811 (0.776–0.855) | 0.55–0.62 | large positive fitted shape at low thresholds (an unbounded GPD with this shape would have infinite variance: an extrapolation, not a measurement); strongly threshold-dependent, see below |
| matched update, S1_LM, S1_literal + stable cap | zsRE | 255–258 | 0.71–0.75 | — | 0.63 | same fitted shape as the stable cap (same mechanism) |
| live v0 C1 | zsRE | 235 | 0.44 (−0.28–0.96) | — | 1.5 | large positive shape, unstable per cell |
| live v0 C2 | zsRE | 46 | unstable (n too small) | — | — | 36 of 46 touched positions lose > 1 nat; the fit is not meaningful |
| random reader | CounterFact | 5,015 | −0.22 (−0.26 … −0.18) | −0.200 (−0.202 … −0.198) | 4.1 | negative fitted shape (finite fitted endpoint); many harmful changes, bounded severity |
| random reader | zsRE | 65 | −0.30 | — | 2.3 | negative fitted shape |
| AW-B: v5 → 1-nat mixture (order 100) | zsRE | 289 → 289 | 0.01 → **−1.4** | — | 1.6 → 1.4 | ceiling of 1 nat imposed by construction; the fitted shape < −1 is at the likelihood endpoint and outside the entropy domain: **not an estimate** [revised] |
| AW-B: v5 → mixture | CounterFact | 691 → 689 | 0.14 → −1.3 | — | 1.4 → 1.3 | same: proven bound, invalid fit |
| BP re-trained readers s0/s1/s2 | CounterFact | 227 / 567 / 138 | −0.24 / −0.07 / −0.02 | — | 2.2–2.8 | small negative to near-zero shapes; wider seed spread |
| ePC-trained reader s0 | CounterFact | 162 | −0.26 | — | 2.5 | negative shape; zsRE: zero positions > 0.01 |
| κ pilot (3 seeds, 4,064 positions each): ordinary / κ 0.2 / κ 0.5 / clip 2 | CounterFact | 101 / 52 / 33 / 66 (pooled) | −0.44 / −0.55 / −1.03 / −0.57 | — | 3.2 / 4.0 / 6.7 / 4.1 | 33–101 excesses pooled over seeds: below any identification screen; the κ 0.5 value is at the endpoint boundary and invalid; directions only |

Stability checks on the two main cases: the learned reader's κ̂ is 0.043 / 0.049 / 0.059 (zsRE) and 0.098 / 0.041 /
0.029 (CounterFact) in realizations 0 / 1 / 2, and 0.05–0.07 for thresholds 0.01–0.5 nats; above 1 nat it drops to
about −0.06 to −0.14, i.e. the fitted far tail is lighter than exponential (a token's loss is bounded in practice
by the logit range). The stable v0 cap's κ̂ is 0.73 / 0.96 / 0.65 by realization and 0.81–0.88 for thresholds
0.01–0.1, falling to 0.59 at 1 nat and 0.16 at 2 nats: this could be finite-range curvature, a population mixture, sampling
variation or a ceiling; the prototype does not decide which [revised: the earlier "the power-law body is real" is withdrawn]. The
stretched fit (α free) prefers α ≈ 0.85–0.9 with κ ≈ 0 for the learned reader and does not beat the α = 1 fit by more
than one nat of log-likelihood, so α = 1 is the honest default.

**What this says [revised].** On the observed range the three cap families differ in both harmful-change frequency
and conditional severity, and their excess distributions have different fitted shapes: small and positive for the
learned reader (near the exponential restriction, excess scale 1.5–1.8 nats), large and positive but strongly
threshold-dependent for the v0 caps (excess scale 0.6 nats at u = 0.01), negative for the random reader. These are
fitted shapes within one family on a finite range, not complexity classes, not asymptotic laws and not a measured
variance. The 1-nat mixture is a proven ceiling on this observable, not a fitted family. This still upgrades the talk's
"rarer but heavier versus more frequent but milder" from a description to numbers that can be checked across
thresholds and populations, which is what the saved-vector tail analysis must do before any number enters a slide.

What it still cannot say: an asymptotic tail (the truncation above 1–2 nats is visible), independence of positions
(the bootstrap resamples windows, and should resample window identities jointly across cells in the real analysis),
or anything about the system's entropy growth with degrees of freedom (§4, item E).

---

## 4. Proposed alterations, in order of value per hour

**A. Add the saved-vector tail analysis to the fidelity analysis (HT-17, narrowed to Capex's specification). Recommended.
CPU only, no GPU time, no change to any experiment.** [revised: adopt Capex's seven points: a declared observable and
population; the gate's firing indicator reported separately from Δ > 0.01; excess fits Y = Δ − u with the exceedance
probability; GPD vs its exponential restriction compared by predicted survival and held-out-window likelihood, with a
correctly normalised alternative such as a conditional lognormal if both fail; window identities resampled jointly
across paired cells, realization / order / seed variation reported separately; a "not identified" screen (fewer than 100
excesses or 30 contributing windows: counts and curves only); small outputs. Start on representative cells and measure
throughput before expanding.] Original scope text follows. Scope: every receipted Stage-4 cell (270), the ten AW-B evaluation memories × three arms, the
PC-reader cells (BP ×3, ePC ×3 when done), the PC-v0/v1 harm readouts, the κ-pilot drift vectors. For each: firing
rate (zero mass), generalized-Pareto (κ, σ) over u = 0.01 with window-identity block bootstrap, threshold sensitivity
(0.01 / 0.1 / 0.5 / 1 nat), the stretched fit (α) as a check, [the calibrated-entropy column is dropped from the empirical comparison per Capex; for the one-sided α = d = 1
family it is 1 + ln_{κ/(1+κ)} σ = ((1+κ)σ^{κ/(1+κ)} − 1)/κ, to be demonstrated on known distributions first]. One figure: frequency against conditional severity per condition × dataset; a κ̂-against-σ̂ **parameter plot**, if
kept, labelled by population and threshold, not a map of universality classes [revised]. Owner: Capex (one lane, 1–2 days, `aw/tail_class.py` beside `aw/tail_figures.py`, tests on a
synthetic coupled-exponential sample with known κ), my review, then the talk's slides 6–7 and `tails_v1.md` v2. Fits
before the 9 October freeze with room to spare; the data it uses are already frozen.

**B. Reframe the κ pilot against the paper's definition. Recommended. Zero cost.** Slide 8 should say exactly which of
the three components we implemented: the coupled logarithm on the reader's answer surprisal, and nothing else: no
independent-equals average, no 1/α root, no informational-scale calibration, and no change to the inference
distribution. This is what the reviewer means by subtleties, and saying it ourselves is better than being told. Keep
the null result and the clip control as they are; add the measured class of the pilot arms from A (the κ arms move the
harm toward compact support, consistent with the direction his coupled log predicts for κ > 0, but at the retention
cost already reported).

**C. State the bound as a proven ceiling on the observable. Recommended. Zero cost.** [revised] The 1-nat mixture
imposes a ceiling of one nat on the per-position loss at the same prefix, by construction: a proven bound on the upper
tail, independent of any fitted family, and not a change of complexity class. That can be shown beside the measured
ES99+ reduction. DEC-078's framing
(intervention beside the κ pilot, not a recommended configuration) is unchanged.

**D. One paragraph in the active-inference section. Recommended. Zero cost.** Name the coupled free energy's
informational form as the proposed training objective for the residual agent (his equation 56), the informational
scale as its temperature, and the "pseudo-Markov blanket" as the version of the blanket his framework offers for a
boundary that non-equilibrium fluctuations cross. Keep it labelled proposed; cite the paper by its title and date; do not select a particular equation as our training
objective before the authors clarify the modelled variable, constraints and escort weighting [revised per Capex].
This also answers his last sentence about integrating with the coupled-AI team: the talk states where the hook is.

**E. Not feasible before the talk: a coupled-entropy or coupled-free-energy training objective.** Design (which
quantity's entropy; the independent-equals weighting over tokens or over episode records; the calibration of σ; the
root), CPU implementation and tests by Capex, nine trainings and eighteen evaluations ≈ 15–20 GPU-hours, and the GPU is
committed to the ePC seeds (to 3 Oct), Option R (3 Oct) and the interface 2×2 (to 5 Oct). It could only run by cutting
the interface study, and it would be a first implementation of a subtle objective with no time for the author's
review. Recommend: plan it with his team after 15 October as the first joint experiment. Likewise not feasible: a
measurement of entropy growth with degrees of freedom (H(W(N))/N), because the 3,000-edit population does not exist
(HT-16) and per-position vectors were saved only at the final checkpoint; the fixed 128-window prefix statistics at
100 / 300 / 1,000 edits exist in every checkpoint file and could give a weak three-point growth curve if wanted, but
it is a different population and I would not lead with it.

**F. Optional small GPU job, if the interface study finishes early on 5 October:** rerun the full 245,237-position
readout for the nine κ-pilot readers (≈ 4 GPU-hours) so the pilot sits on the same footing as everything else and its
class can be fitted on more than 33 touched positions. Needs the pilot's saved memories to restore; not verified. Low
priority.

---

## 5. Timing

| item | owner | time | where it lands |
|---|---|---|---|
| A: HT-17 class fits, figure, tables | Capex, then Capstan review | 1–2 CPU days | 7–8 October reports; slides 6–7; `tails_v1.md` v2 |
| B, C, D: wording | Capstan with Capex (PRES lane) | hours | slides 2, 6–8, 11; claim ledger rows |
| E: coupled objective | — | does not fit | post-conference plan with the reviewer's team |
| F: κ-pilot full readout | Capstan (GPU) | 4 h, only if 5 Oct has slack | backup slide |

A–D change nothing in the experimental record: no run is added, removed or re-ordered, and the Option R and
interface-study decisions stand. If you say go, I open HT-17 as Capex's next lane and draft the slide-text changes;
if you prefer to hear the reviewer's reaction tomorrow first, the fits above are enough to discuss.

---

## 6. Questions worth putting to him tomorrow

1. Is the conditional distribution of positive loss, with the zero mass reported as a separate firing rate, the right
   object for the complexity class, or would he model the zero inflation inside the class?
2. The far tail truncates (κ̂ falls above 1–2 nats, because a token's loss is bounded by the logit range in practice).
   How does his framework treat a power-law body with a hard ceiling: compact support with large N_max, or a power law
   with a cutoff?
3. For κ̂ ≈ 0.8 (infinite fitted variance), should we use the Independent Approximates estimator (Al-Najafi, Tirnakli
   and Nelson 2026, his reference 37) rather than plain maximum likelihood?
4. Does the informational scale of the harm (1.5–1.8 nats for the learned reader, 0.6 for the v0 cap) carry the
   temperature interpretation he would endorse for a non-physical system, or is that a stretch?
5. Which of the two coupled free energies would his team want a residual agent on a frozen transformer to minimise,
   and over which distribution (next-token, episode-level, or the harm itself)? Do gradients pass through the escort
   weights, and are reference values available from the team's implementation?
6. (From Capex, to be asked privately and precisely.) In equation 126, positive-κ branch, the compensated ratio
   H(W^{1+a})/H(W) · W^{−aκ/(α+dκ)} appears to tend to 1 rather than the printed (1+a)^{1/α}: with α = d = κ = a = 1,
   H(W) = √W − 1 and the ratio is exactly 1 + 1/√W. Is the positive-κ secondary scaling exponent intended to be zero
   for this entropy, or is a different limiting prescription meant? (Checked numerically in
   `aw/entropy_feedback_checks.py`; the κ = 0 branch does give (1+a)^{1/α}.) Our finite comparisons and the α = 1
   GPD identity do not depend on this.
7. What connects the conditional harm distribution to a state space W(N)? Can we agree the talk reports fitted
   finite-range behaviour without claiming that connection has been measured?
