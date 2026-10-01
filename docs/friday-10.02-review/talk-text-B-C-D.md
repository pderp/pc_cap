# Talk-text changes B, C, D — drafted for the deck (for Capex to fold in; no deck file edited here)

Capstan, 1 October 2026, 12:00 EDT. Approved by the lead ("go ahead with B through D") on the basis of
`feedback-MMK-nelson-entropy.md`. The deck files under `docs/presentation/deck_v3/` are Capex's; to avoid simultaneous
edits this file holds the exact replacement or insertion text, keyed to slide and paragraph, plus the claim-ledger row
changes. Item A (the complexity-class fits, lane HT-17) is not approved yet; where its numbers appear below they are
**prototype values from `feedback-MMK-nelson-entropy.md` §3 and must be labelled "prototype, pending HT-17"** until the
lane reports. Reference: K. P. Nelson, *The unique, universal entropy for complex systems*, manuscript dated 27 Sep
2026 (PDF built 1 Oct 2026), cited below as "Nelson 2026".

Conventions kept: measured / proposed labels stay visible; DEC-054 (κ pilot: preliminary hints) and DEC-078 (AW-B: an
intervention beside the κ pilot, not a recommended configuration) are unchanged; nothing below adds a run.

---

## B. The κ pilot, stated against the paper's definition (slide 8, slide 11, claim ledger)

### Slide 8, replace the first speaker paragraph

Current: "The kappa pilot changed the reader's training loss. Both kappa settings reduced a development tail statistic
but lost too much retention and failed the declared success rule. Clipping also reduced that tail descriptively. These
remain preliminary trade-offs, without evidence of a special coupling advantage." [`kappa-design`]

Replace with:

"The kappa pilot changed one thing in the reader's training loss: the answer surprisal −ln p became the coupled
logarithm −ln_κ p, for κ = 0.2 and 0.5. In Nelson's calibrated entropy that logarithm is one of three components; the
other two, the average over the independent-equals distribution and the root by the stretch parameter, we did not
implement, and we did not calibrate anything to an informational scale. So this was a loss-level deformation, not the
coupled entropy and not the coupled free energy. Within that scope, both κ settings reduced a development tail
statistic but lost too much retention and failed the declared success rule, and a plain clip of the surprisal
reproduced most of the tail reduction. The direction is the one a positive coupling predicts, a reader that rejects
more, with the retention cost already measured." [`kappa-design`]

### Slide 8, add after the backup list

"κ pilot, class of its harm (prototype, pending HT-17): on the 4,064-position development assay the ordinary arm's
positive losses fit a compact-support class (κ̂ ≈ −0.44 on CounterFact) and both κ arms move further toward compact
support (κ̂ ≈ −0.55 and −1.03), as does the clip (−0.57); sample sizes are 33–101 touched positions pooled over three
seeds, so these are directions, not estimates. Source: `docs/friday-10.02-review/feedback-MMK-nelson-entropy.md` §3."

### Slide 11, replace the last speaker paragraph

Current: "Our loss-level kappa pilot also helps define the boundary of the evidence. The two kappa settings reduced a
development tail statistic, but both failed the declared retention and tail-separation decision rule. These are
preliminary hints about a robustness trade-off, not the coupled free energy, not a coupled Markov blanket, and not a
test of the abstract's one-kappa conjecture. Those stronger theoretical ideas need a matching implementation and a
direct test." [`kappa-kappa02`, `kappa-kappa05`, `AI-programme`]

Replace with:

"Our loss-level kappa pilot helps define the boundary of the evidence. It implemented one of the three components of
the calibrated coupled entropy, the coupled logarithm, on a surprisal, and both settings failed the declared retention
and tail-separation rule. It is not the coupled entropy, not the coupled free energy, not a coupled Markov blanket and
not a test of the one-kappa conjecture. The matching implementation would minimise the informational coupled free
energy of Nelson 2026 with its independent-equals weighting, and that is the first experiment we would propose to run
with the coupled-AI group after this meeting." [`kappa-kappa02`, `kappa-kappa05`, `AI-programme`, `AI-coupled-FE`]

### Claim ledger v7, row `kappa-design`, "does not support" column

Append: "; implemented only the coupled-logarithm component of Nelson 2026's calibrated entropy (no independent-equals
average, no 1/α root, no informational-scale calibration)".

---

## C. The bound as a change of complexity class (slides 6, 7, 8; claim ledger)

### Slide 6, replace the last speaker paragraph

Current: "Heavy-tailed distributions are central to why this question matters at this satellite. But a finite set of
rare severe changes is not itself proof of a power law or an asymptotic heavy-tail class. Nor does it tell us whether
rare inputs caused them, whether they cluster in time, or how the system will behave under an unseen extreme regime.
Our measured claim is concentrated unintended prediction loss. That gives the active-inference programme a concrete
quantity to explain and potentially regulate." [`HT13-empirical`, `AI-next`]

Replace with:

"Heavy-tailed distributions are central to why this question matters at this satellite, so we should say what class
these data support, and how. A finite set of rare severe changes does not prove an asymptotic law. What we can do is
fit the one-parameter family that carries the classes, the coupled exponential, which for a one-sided variable is the
generalized Pareto distribution: its shape κ is the long-range coupling and its scale σ is the informational scale,
the point where the surprisal's slope is one over σ. Fitted to the positions the cap touched, with the untouched mass
reported separately as a firing rate, the learned reader's harm is in the exponential class, κ near 0.05 with a scale
of about 1.5 to 1.8 nats, the same in all three populations [prototype, pending HT-17]. The original v0 cap's harm is
in the power-law class, κ near 0.8, a fitted tail exponent near −2.2 and an infinite fitted variance, with a scale of
0.6 nats. Above one or two nats both fits lighten, because a token's loss is bounded in practice, so the claim is a
class within the fitted family, not an asymptote. Our measured claim remains concentrated unintended prediction loss;
the class and the scale are the two numbers that describe it." [`HT13-empirical`, `HT17-class`, `AI-next`]

### Slide 7, add after the second speaker paragraph

"In class terms the two caps differ in kind, not only in degree: the learned reader converted power-law harm into
exponential harm at a higher scale, firing on more positions; the random reader, which fires far more often, is in the
compact-support class with κ near −0.2 [prototype, pending HT-17]." [`HT17-class`]

### Slide 8, add after the fifth speaker paragraph ("The guarantee has a precise scope …")

"Said in the language of complexity classes: the mixture takes the learned reader's exponential-class harm and makes
it compact-support by construction, with the support ending at one nat; the fitted κ goes from about zero to below
−1 on both datasets [prototype, pending HT-17]. That is a different statement from a lower expected shortfall, and
both are true. It is an intervention we measured, not a configuration we recommend." [`AW-B`, `HT17-class`]

### Claim ledger v7

- Row `AW-B`, "supports" column, append: "; moves the fitted harm class from exponential to compact support (N_max =
  1 nat) [prototype, pending HT-17]".
- New row `HT17-class` | Heavy-tailed distributions / extremes | **prototype, pending HT-17** | generalized-Pareto
  (= Nelson coupled-exponential) fit to positive ΔNLL > 0.01, location 0, per cell; learned reader κ̂ 0.052 (0.024–0.079)
  zsRE, 0.058 (0.036–0.077) CounterFact, σ̂ 1.54 / 1.79 nats; stable v0 κ̂ 0.81 (0.78–0.86), σ̂ 0.55–0.62; random
  reader κ̂ −0.20; mixture κ̂ < −1 | 245,237 positions per cell, 15 cells per condition × dataset; window bootstrap |
  own cap-off; threshold sensitivity 0.01–2 nats shown | the three cap families are in three complexity classes
  (exponential, power-law, compact-support) within the fitted family | no asymptotic law (fits lighten above 1–2 nats);
  positions not independent; zero mass reported as firing rate, not modelled; α = 1 default (stretched fit prefers
  α ≈ 0.85–0.9 with κ ≈ 0, not better by > 1 nat) | `docs/friday-10.02-review/feedback-MMK-nelson-entropy.md` §3;
  HT-17 when it reports.

---

## D. One paragraph in the active-inference section (slide 2 or 11; abstract-to-testbed map; claim ledger)

### Slide 11, insert before the κ paragraph (or slide 2 after the third paragraph, Capex's choice)

"The abstract's two interfaces are labelled κ-porous blankets. Nelson 2026 gives that label a candidate definition: a
pseudo-Markov blanket in which the agent–environment cross-terms stay zero while non-equilibrium fluctuations with a
nonlinear dependence cross the boundary, and a coupled free energy whose informational form, k T (ln_κ Z − 1/(1+κ)),
is proposed as the objective for variational and active inference, with the temperature equal to the informational
scale. None of that is implemented here. What we measured on the frozen prior is where it would attach: the harm
distribution has a fitted class and an informational scale, and the residual agent has a learning signal and a null
decision. The coupled objective and the policy loop are the proposed next layer." [`AI-coupled-FE`, `AI-programme`]

### Abstract-to-testbed map (`docs/presentation/abstract_to_testbed.md`, Capstan's file): rows added today

- "Coupled, κ-deformed free energy" row: what-it-is-not column now names the three components and which one the pilot
  implemented.
- New rows: "informational coupled free energy as training objective" (proposed), "pseudo-Markov blanket with
  nonlinear boundary dependence" (proposed), "informational scale σ of the harm as a temperature-like quantity"
  (prototype measurement, pending HT-17).

### Claim ledger v7, new row

`AI-coupled-FE` | Active inference / heavy-tailed distributions | proposed | — | — | — | Nelson 2026's informational
coupled free energy and pseudo-Markov blanket are the candidate formalisation of the abstract's κ-porous interfaces |
not implemented; the κ pilot implemented only the coupled-logarithm component; no coupled expectation, no changed
inference distribution, no blanket test | `/home/derp/cap/NelsonUniqueUnivEntropy2026Sep27.pdf`;
`docs/presentation/abstract_to_testbed.md`.

---

## Where the numbers come from, and what must change when HT-17 reports

Every κ̂ and σ̂ above is from the prototype in `feedback-MMK-nelson-entropy.md` §3 (generalized-Pareto maximum
likelihood over u = 0.01 nats, location 0; 200 window-resampling draws over the pooled cell × window stack, which
resamples copies of the same window independently and is therefore slightly optimistic). HT-17 should: resample window
identities jointly across cells; report per-cell, per-realization and pooled fits; show thresholds 0.01 / 0.1 / 0.5 /
1 / 2 nats; fit α as a check; add the calibrated entropy of the fitted coupled exponential, 1 + ln_{(1+κ)/κ} σ, beside
BGS 1 + ln σ + κ; and produce the class map (κ̂ against σ̂ per condition × dataset). When it lands, replace every
"[prototype, pending HT-17]" with the reported values and drop the label.
