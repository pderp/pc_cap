# Slide 6 — Why look past the mean?

**Draft speaker text for charlie's review. Measured empirical distribution;
heavy-tail family remains unestablished.**

**On screen:** “How often is a token harmed by more than x?” Use HT-13
`assets/presentation-materials/figures/tails/survival_by_dataset.png` (path relative
to `/home/derp/cap`), with a visible own-cap-off reference label. Companion inset:
mean, exceedance, maximum and concentration. Claim footer: `HT-readout`,
`HT13-empirical`, `R1-fidelity`. Diagram specification: `diagram-specs.json`, slide `06`.

## Speaker text

“An average answers one question, but it does not tell us how the changes are
distributed. A correction might leave almost all ordinary-text predictions
unchanged and make a small fraction much worse. Improvements elsewhere can also
offset worsening in a signed average. That is why we look at individual target
positions as well as the overall mean.” [`HT-readout`]

“At each position we ask how much the negative log probability of the actual
next token increases. Positive delta NLL means the system gives that token less
probability after enabling the cap. The unit is nats: an increase of one nat
corresponds to a factor of e reduction in probability for that token. This is
a prediction-loss measure, not a direct measure of human harm or the preference-
risk term of expected free energy.” [`HT-readout`]

“The horizontal axis sets a loss-increase threshold x. The vertical axis gives
the fraction of evaluated cell-position observations whose increase exceeds x.
Moving right asks about increasingly severe consequences; moving down asks
about increasingly rare ones. The log axes let us see several scales together.
The zero-change mass is part of the denominator even though zero cannot be
placed on the logarithmic x-axis.” [`HT-readout`, `HT13-empirical`]

“For example, in the learned-reader MQuAKE condition, approximately 0.1941 percent
of these evaluated cell-position observations exceed one nat, while the largest
increase is about 17.06 nats. About 2,336 of 3,678,555 observations carry half of
the total positive loss increase. The denominator is the same 245,237 ordinary-
text positions evaluated across fifteen cells, not millions of independent
replicates. MQuAKE's edit stream ends at 300 edits. These are descriptive
distributional measurements on that endpoint.” [`HT13-empirical`]

“We also report expected shortfall: for ES99, the average positive loss increase
within the worst one percent of all positions, with zeros retained and a fractional
boundary when needed. A percentile is the threshold at the edge of that tail;
expected shortfall averages what lies inside it. These are different quantities.
The maximum identifies the worst observed event, and concentration tells us how
few positions account for much of the positive harm.” [`HT-readout`]

“Heavy-tailed distributions are central to why this question matters at this
satellite. But a finite set of rare severe changes is not itself proof of a
power law or an asymptotic heavy-tail class. Nor does it tell us whether rare
inputs caused them, whether they cluster in time, or how the system will behave
under an unseen extreme regime. Our measured claim is concentrated unintended
prediction loss. That gives the active-inference programme a concrete quantity
to explain and potentially regulate.” [`HT13-empirical`, `AI-next`]

## Figure preparation and exact qualifications

**HT-13 correction pending:** the current generator's field called ES99 is a
99th percentile, and its title asserts “heavy-tailed.” Neither is used as an
established result here. [Review handoff](../../tasks/HT-13-round46-review.md)
records the correction for Claude. The export has a draft figure slot until
those issues are repaired; the actual HT-13 survival figure remains the specified
source. Rerender from the reconciled 270-cell inventory before final presentation.

The figure compares cap-on with **each condition's own cap-off base**. For S1,
this omits the effect of base continuation; use the companion original-base
table when discussing total departure. Do not infer zero probability from
curves outside the displayed range or a nonzero tail from the rendering floor.
Cells sharing text and dependent stream orders are not independent tail draws.
[`HT13-empirical`, `HT-readout`]

Sources: HT-13 `tails.json` / `table.md` (identities in `claim-additions.json`),
[comparator report](../../R1_stage4_report_comparators.md),
[claim ledger](../../talk_claim_ledger_v7.md). This replaces the older development
HT-6 figure in the outline's slide-6 slot; the development figure can remain backup.
