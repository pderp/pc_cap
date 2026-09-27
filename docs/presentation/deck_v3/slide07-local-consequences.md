# Slide 7 — Similar averages can conceal different consequences

**Draft speaker text for charlie's review; measured HT-13 v1.1 snapshot.**

**On screen:** corrected HT-13 rarity-versus-severity figure. Inset: learned zsRE
versus live-C2 zsRE, with signed mean ΔNLL, P(ΔNLL>.01), maximum and ES99+.
Visible reference: **each cap's own cap-off base**. Claim footer:
`HT13-corrected`, `R1-fidelity`, `HT-readout`. Renderable source:
`diagram-specs.json`, slide `07`.

## Speaker text

“The previous curve asked how often harm exceeds a chosen size. Here each point
summarizes a condition and dataset. Horizontal position is the fraction of
cell-position observations exceeding 0.01 nat of additional target-token loss;
vertical position is the maximum observed increase. Lower on one axis need not
mean lower on the other.” [`HT-readout`, `HT13-corrected`]

“On zsRE, the learned reader's mean signed loss increase is about 0.00249 nats.
The live-C2 comparator's is about 0.00320. Those small means accompany different
patterns: roughly 0.159 percent versus 0.0187 percent of observations exceed
0.01 nat, while their observed maxima are about 11.05 versus 50.60 nats. The
learned cap changes more positions at that threshold; live C2 has a rarer but
more severe observed extreme. Their means are not equal, and this plot is not
a test that the means are equivalent.” [`HT13-corrected`]

“Expected shortfall adds another view: the average positive harm in the worst
one percent is approximately 0.260 versus 0.321 nats. For the learned reader,
1,024 of 3,678,555 cell-position observations carry half the positive harm;
for live C2 it is 175. These pooled concentrations are descriptive. We are
repeating the same ordinary-text positions across cells, not collecting millions
of independent observations.” [`HT13-corrected`, `HT-readout`]

“None of this makes probability drift an integrity failure. All forty-five
learned-reader cells exceed the secondary mean-KL benchmark of 0.001, while the
registered data-integrity checks and experimental admission are separate. KL
measures a change in the whole next-token distribution; target-token loss and
exact generated-answer agreement measure different properties.” [`R1-fidelity`, `R1-design`, `HT-readout`]

“For continued-base controls, own cap-off means the continued checkpoint. These
curves alone do not measure total departure from the original model. Also, a
zero own-cap-off loss vector says that this assay detected no change at these
positions; it should not be inflated into a claim about every possible query.”
[`HT13-corrected`]

“This is our empirical connection to the extremes theme: frequency, severity and
concentration each matter. It does not establish a heavy-tail family, a power-law
exponent or robustness to future extremes. A finite vocabulary does not itself
bound log loss: an assigned probability can approach zero. Our present evidence
is a finite set of observed loss changes.” [`HT-readout`, `HT13-corrected`]

## Figure and source notes

Figure: `assets/presentation-materials/figures/tails/rarity_vs_severity.png`;
data: `tails.json`, `table.md`; explanatory source:
`assets/presentation-materials/tails_v1.md` v1.1 (all paths relative to
`/home/derp/cap`). The plotted snapshot has 262 receipted cells; S1_literal zsRE
has seven, while each named main comparison above has fifteen. Do not compare
pooled totals as if those incomplete groups had equal replication. HT-15 adds
realization spread and distinguishes it from the pooled tail.

The linked page's phrase “losses are bounded by the vocabulary” is not used as
a justification here. The figure also omits zero-harm points on its logarithmic
axis; they remain in the source table. Sources are bound in the round-47 claim
additions; [claim ledger](../../talk_claim_ledger_v7.md).
