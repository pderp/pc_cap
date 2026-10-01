# Talk-text changes B, C, D — drafted for the deck (for Capex to fold in; no deck file edited here)

Capstan, 1 October 2026; **revised 13:30 EDT after Capex's review**
(`feedback-MMK-nelson-entropy-capex.md`). Approved by the lead ("go ahead with B through D") on the basis of
`feedback-MMK-nelson-entropy.md`. The deck files under `docs/presentation/deck_v3/` are Capex's; to avoid simultaneous
edits this file holds the replacement or insertion text, keyed to slide and paragraph, plus the claim-ledger row
changes. Reference: K. P. Nelson, *The unique, universal entropy for complex systems*, manuscript dated 27 Sep 2026
(PDF built 1 Oct 2026), cited below as "Nelson 2026".

**What changed in this revision.** The first draft carried my prototype generalized-Pareto estimates into the slide text
as "complexity classes" (exponential, power-law, compact-support) and used the fitted negative shape of the 1-nat mixture
as a class. Capex's review is right that (i) a fitted shape on an observed range is not a complexity class in the
paper's sense, which concerns the growth of accessible states W(N) that this experiment does not define or measure;
(ii) a shape estimate below −1 is at the likelihood's endpoint boundary and outside the entropy domain κ > −1/2, so the
mixture's "κ̂ ≈ −1.4" is optimizer output, not an estimate; (iii) "infinite variance" is a property of extrapolating an
unbounded fitted family, not a measurement; (iv) Δ > 0.01 is a harmful-change indicator, not the gate's firing rate;
(v) the excess scale σ_u depends on the threshold; (vi) the window bootstrap in the prototype understates uncertainty by
an unknown amount. The slide text below therefore uses Capex's conservative wording. The prototype numbers stay in a
backup appendix marked exploratory and do not enter a slide until the agreed saved-vector tail analysis (lane HT-17,
narrowed per Capex) reports. Conventions kept: measured / proposed labels visible; DEC-054 and DEC-078 unchanged;
nothing below adds a run.

---

## B. The κ pilot, stated against the paper's definition (slide 8, slide 11, claim ledger)

### Slide 8, replace the first speaker paragraph

Current: "The kappa pilot changed the reader's training loss. Both kappa settings reduced a development tail statistic
but lost too much retention and failed the declared success rule. Clipping also reduced that tail descriptively. These
remain preliminary trade-offs, without evidence of a special coupling advantage." [`kappa-design`]

Replace with:

"The kappa pilot tested a bounded deformation of the reader's answer loss using the coupled-logarithm family: the
surprisal −ln p became (1 − e^{−κℓ})/κ, which saturates at 1/κ and down-weights very surprising targets. That is one
ingredient of the calibrated coupled entropy proposed in Nelson's new manuscript; its probability transformation and
its averaging, the independent-equals weighting and the outer root, differ from what we ran, and we calibrated nothing
to an informational scale. Both tested settings failed our declared success rule, and a plain clip of the surprisal
reproduced most of the tail reduction. The result concerns that bounded-loss intervention. We have not tested the
calibrated coupled entropy or a coupled free-energy objective; the null here neither confirms nor refutes them."
[`kappa-design`]

### Slide 11, replace the last speaker paragraph

Current: "Our loss-level kappa pilot also helps define the boundary of the evidence. The two kappa settings reduced a
development tail statistic, but both failed the declared retention and tail-separation decision rule. These are
preliminary hints about a robustness trade-off, not the coupled free energy, not a coupled Markov blanket, and not a
test of the abstract's one-kappa conjecture. Those stronger theoretical ideas need a matching implementation and a
direct test." [`kappa-kappa02`, `kappa-kappa05`, `AI-programme`]

Replace with:

"Our loss-level kappa pilot helps define the boundary of the evidence. It deformed one loss with the coupled
logarithm; both settings failed the declared retention and tail-separation rule. It is not the calibrated coupled
entropy, not the coupled free energy, not a coupled Markov blanket and not a test of the one-kappa conjecture. A
matching implementation would need the probability model, the constraints, the escort weighting and the policy loop
specified with the authors first; that specification is the first thing we would want to agree with the coupled-AI
group after this meeting." [`kappa-kappa02`, `kappa-kappa05`, `AI-programme`, `AI-coupled-FE`]

### Claim ledger v7, row `kappa-design`, "does not support" column

Append: "; the pilot's loss (1 − e^{−κℓ})/κ is a bounded deformation of one surprisal, not Nelson 2026's calibrated
entropy (no independent-equals average, no outer root, no informational-scale calibration); its null result does not
bear on the untested coupled objective".

---

## C. Extremes and the bound (slides 6, 7, 8; claim ledger)

### Slide 6, replace the last speaker paragraph

Current: "Heavy-tailed distributions are central to why this question matters at this satellite. But a finite set of
rare severe changes is not itself proof of a power law or an asymptotic heavy-tail class. Nor does it tell us whether
rare inputs caused them, whether they cluster in time, or how the system will behave under an unseen extreme regime.
Our measured claim is concentrated unintended prediction loss. That gives the active-inference programme a concrete
quantity to explain and potentially regulate." [`HT13-empirical`, `AI-next`]

Replace with:

"Heavy-tailed distributions are central to why this question matters at this satellite, so we should say what the
data can and cannot tell us about the shape of the harm. A finite set of rare severe changes does not prove a power
law or an asymptotic class. What the saved results do let us examine is two things separately: how often a harmful
change occurs, and how severe it is when it does. For the severity we can fit the one-parameter family Nelson's
framework uses, which for a one-sided variable is the generalized Pareto with a shape and a scale, and compare it with
its exponential special case across thresholds and populations. Exploratory fits suggest the cap families differ in
both frequency and conditional severity in ways worth testing; the analysis that decides this is in progress and its
numbers are not on this slide. Independent of any fit, our measured claim remains concentrated unintended prediction
loss, and that gives the active-inference programme a concrete quantity to explain and regulate."
[`HT13-empirical`, `HT17-tails`, `AI-next`]

### Slide 7, add after the second speaker paragraph

"Frequency and conditional severity are the two axes to keep apart here: the learned reader changes more positions by
a mild amount, the v0 caps change fewer positions by a large amount, and the random reader changes many positions with
a bounded severity. Whether those differences survive threshold and population checks, and which simple family
describes each, is what the saved-vector analysis will report." [`HT17-tails`]

### Slide 8, add after the fifth speaker paragraph ("The guarantee has a precise scope …")

"Said in distributional terms: the mixture imposes a ceiling of one nat on this per-position loss observable at the
same prefix, by construction. That is a proven bound on the upper tail, independent of any fitted family. It does not
establish a change in the system's asymptotic complexity class, and it does not extend to free-running prefixes or
whole sequences. It is an intervention we measured, not a configuration we recommend." [`AW-B`, `HT17-tails`]

### Claim ledger v7

- Row `AW-B`, "supports" column, append: "; imposes a one-nat ceiling on the measured per-position loss at the same
  prefix (a proven bound on this observable, not a fitted family or a class change)".
- New row `HT17-tails` | Heavy-tailed distributions / extremes | **analysis in progress (exploratory prototype exists)** |
  harmful-change frequency and conditional severity of Δ = NLL(cap) − NLL(cap-off), excess fits over declared
  thresholds (generalized Pareto vs its exponential restriction; a correctly normalised alternative if both fail) |
  Stage-4 learned / stable v0 / random caps on the common text population, both datasets, each realization; AW-B
  paired arms; BP/ePC reader seeds; 4,064-position pilot assay kept separate | own cap-off; threshold grid 0.01 / 0.1 /
  0.5 / 1 nat; window identities resampled jointly across paired cells; realization / order / seed variation reported
  separately | whether the apparent distributional differences survive threshold and population checks, or the family
  is not identifiable | no asymptotic class, no W(N), no infinite-variance claim, no independent-position inference;
  shapes below the entropy domain or at the likelihood endpoint reported as invalid, not as estimates |
  `docs/friday-10.02-review/feedback-MMK-nelson-entropy.md` §3 (prototype), `feedback-MMK-nelson-entropy-capex.md`
  (analysis specification); HT-17 report when it lands.

---

## D. One paragraph in the active-inference section (slide 2 or 11; abstract-to-testbed map; claim ledger)

### Slide 11, insert before the κ paragraph (or slide 2 after the third paragraph, Capex's choice)

"The abstract's two interfaces are labelled κ-porous blankets. Nelson's new manuscript offers a candidate mathematical
basis for that label: a pseudo-Markov blanket in which the agent–environment cross-terms stay zero while
non-equilibrium fluctuations with a nonlinear dependence cross the boundary, and a coupled free energy proposed as the
objective for variational and active inference in that setting. None of this is implemented here, and applying it
requires a defined probability model, constraints and a policy loop that we have not specified. What our experiments
measure is what such a controller would need to explain and regulate: the credit rules, the retrieval behaviour and
the unintended harm. A boundary in the architecture does not by itself demonstrate the conditional independences of a
Markov blanket." [`AI-coupled-FE`, `AI-programme`]

### Abstract-to-testbed map (`docs/presentation/abstract_to_testbed.md`, Capstan's file): rows added today

- "Coupled, κ-deformed free energy" row: what-it-is-not column now says the pilot deformed one surprisal with the
  coupled logarithm and did not implement the calibrated entropy's averaging or root.
- New rows: "coupled free energy as a candidate training objective" (proposed; equation and modelled variable to be
  agreed with the authors), "pseudo-Markov blanket with nonlinear boundary dependence" (proposed), "frequency and
  conditional severity of harm, excess fits" (exploratory prototype; analysis in progress).

### Claim ledger v7, new row

`AI-coupled-FE` | Active inference / heavy-tailed distributions | proposed | — | — | — | Nelson 2026's coupled free
energy and pseudo-Markov blanket are a candidate formalisation of the abstract's κ-porous interfaces | not implemented;
the κ pilot deformed one surprisal and did not implement the calibrated entropy; which free energy, which modelled
variable, which constraints and whether gradients pass through escort weights are all unspecified; no blanket test |
`/home/derp/cap/NelsonUniqueUnivEntropy2026Sep27.pdf`; `docs/presentation/abstract_to_testbed.md`;
`feedback-MMK-nelson-entropy-capex.md`.

---

## Appendix (backup only; exploratory; not for slides until HT-17 reports)

Prototype generalized-Pareto fits of the excesses Y = Δ − u, u = 0.01 nats, location 0, maximum likelihood, from
`feedback-MMK-nelson-entropy.md` §3; the bootstrap there resampled copies of the same window across cells
independently and so understates uncertainty by an unknown amount.

| condition | dataset | fitted shape κ̂ (pooled; per-cell range) | excess scale σ̂_u nats | status |
|---|---|---|---:|---|
| learned reader v5 | zsRE | 0.052 (per cell 0.043–0.059) | 1.54 | small positive shape; exponential restriction to be compared |
| learned reader v5 | CounterFact | 0.058 (0.029–0.098) | 1.79 | same |
| stable v0 cap | zsRE | 0.81 at u = 0.01; 0.59 at 1 nat; 0.16 at 2 nats | 0.55–0.62 | large positive shape on the observed range, strongly threshold-dependent; no asymptotic reading |
| random reader | CounterFact | −0.20 (−0.26 … −0.18) | 4.1 | negative shape, finite fitted endpoint; many excesses |
| AW-B 1-nat mixture | both | optimizer output < −1 | — | **invalid as an estimate** (endpoint boundary; outside entropy domain κ > −1/2); the 1-nat bound is proven, not fitted |
| κ pilot arms (4,064 positions) | CounterFact | −0.44 / −0.55 / −1.03 / −0.57 | — | 33–101 excesses pooled over seeds: below any identification screen; κ 0.5 arm's value invalid as above |

When HT-17 reports, its numbers replace this appendix, with the exceedance probability, the distinct contributing
windows, the exponential-vs-GPD comparison on held-out windows, and the joint-window bootstrap intervals; a κ-versus-σ
figure, if kept, is a parameter plot labelled by population and threshold, not a map of universality classes. The
calibrated-entropy column is omitted from the empirical comparison (for the one-sided α = d = 1 family it is
1 + ln_{κ/(1+κ)} σ, i.e. ((1+κ)σ^{κ/(1+κ)} − 1)/κ, as Capex derived; demonstrate it on known distributions first).
