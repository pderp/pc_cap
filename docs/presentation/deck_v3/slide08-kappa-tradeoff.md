# Slide 8 — The κ pilot measures a trade-off

**Draft speaker text for charlie's review; development evidence, DEC-054.**

**On screen:** κ pilot retention-versus-tail figure; ordinary, κ=.2, κ=.5 and
clip-2 arms. Visible label: **preliminary development result; declared gain not
established**. Claim footer: `kappa-ordinary`, `kappa-kappa02`, `kappa-kappa05`,
`kappa-clip2`, `kappa-design`. Renderable source: `diagram-specs.json`, slide `08`.

## Speaker text

“The distributional findings motivate asking whether changing the training loss
could reduce the tail. This pilot changed the reader's answer-surprisal loss
to a coupled-log form at kappa 0.2 and 0.5. We compared it with ordinary loss
and with plain surprisal clipped at two. The clipped control matters because
it tests whether a simpler loss ceiling produces a similar trade-off.” [`kappa-design`]

“Across the three development datasets and three training seeds, mean paraphrase
retention is approximately 0.796 for ordinary loss, 0.754 for kappa 0.2, 0.748
for kappa 0.5 and 0.779 for clipping. Positive-harm ES95 is approximately 0.223,
0.084, 0.063 and 0.103 nats, respectively. ES95 averages the worst five percent
of this pilot's evaluated positions; it is not the ES99 full-validation quantity
on the preceding slides.” [`kappa-ordinary`, `kappa-kappa02`, `kappa-kappa05`, `kappa-clip2`]

“The tail statistic improves descriptively, but the kappa arms lose too much
retention. The predeclared rule allowed a mean retention drop of at most 0.02,
with no increase in unseen false fires and a tail change exceeding the seed
spread. Both kappa arms miss the retention floor of about 0.776, and their tail
reductions do not clear the declared separation rule. We therefore do not
declare a successful secondary condition.” [`kappa-design`]

“This experiment does give us useful information: on this substrate, reducing
the influence of large training losses changes the balance between correction
retention and unintended effects. The clipped control obtains much of the
descriptive tail reduction too. The comparison does not establish a special
coupling advantage, and a lower tail statistic alone would not make a better
overall learner.” [`kappa-design`, `kappa-clip2`]

“These are preliminary hints, as agreed with Matthew Iklé. The pilot does not
implement the coupled free energy, a coupled Markov blanket, or a test of the
one-kappa conjecture. It changes a loss; it does not supply the coupled expectation
or altered inference distribution required by that larger proposal.” [`kappa-design`]

## Figure and source notes

Figure: `pc_cap/logs/r1_round37/presentation-figures-v2/kappa-tradeoff.png`.
Source page: `assets/presentation-materials/kappa_pilot_v5.md`;
audited numbers: `logs/r1_round22/ht3e-independent-review-v2.json`;
actual objective: `logs/heavy_tail/HT-3b-objective-review.json`. All three training
seeds and all datasets enter the stated macro means. This is a 32-window /
4,064-position population per dataset; do not splice its tail values into the
245,237-position full-validation series. Ordinary reader weights are reused,
not a new ordinary training run. [Claim ledger](../../talk_claim_ledger_v7.md).
