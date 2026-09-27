# HT-15 — proposed addition to “What the pooled tails show”

Capex, 2026-09-26. For Capstan to merge into
`assets/presentation-materials/tails_v1.md`; its existing text has not been edited.
Source: [262-cell snapshot](../../logs/additional_work/round47/HT-15-final/cell_tails.json)
and [full spread table](../../logs/additional_work/round47/HT-15-final/tail_spread.md).

Suggested paragraph:

> The cell-level analysis adds the spread hidden by pooling. Each cell uses the
> same 245,237 positions; we compute its fractional ES99+ first, then average the
> five stream orders within each realization. For the learned reader, the three
> realization means are 0.259, 0.266 and 0.254 nats on zsRE; 0.610, 0.480 and 0.622
> on CounterFact; and 0.731, 0.710 and 0.421 on MQuAKE (300 edits). Their ranges are
> therefore 0.254–0.266, 0.480–0.622 and 0.421–0.731. Live C2 on zsRE has values
> 0.243, 0.346 and 0.375: its average exceeds the learned reader's, but realization
> 0 has the opposite ordering. These are descriptive three-realization ranges,
> not confidence intervals or a new superiority test. Mean per-cell half-mass
> counts are 68.7 positions for the learned reader and 12.5 for live C2 on zsRE;
> those counts have a per-cell denominator and differ from the pooled counts.
> The companion `figures/tails/tail_spread.md` and `cell_tails.csv` provide every
> cell's ES99+, maximum and location, exceedances, and concentration. The current
> S1_literal zsRE snapshot has only seven cells (5/2/0 by realization); no complete
> three-realization range is reported for it. Refresh after the reconciled halt.

Mean cell ES99 and pooled ES99 are different estimands; they can coincide, as
they do for these learned-reader groups. Do not infer that their equality makes
the positions independent. The readout retains the own-cap-off reference, so
S1 continuation's total effect relative to the original base is outside it.

Three wording corrections for the existing page when merging:

- Replace “losses are bounded by the vocabulary” with “finite empirical data
  do not establish an asymptotic tail class.” Finite vocabulary size does not
  bound `-log p(y)` as the assigned probability tends to zero.
- Replace “differ … not in mean drift” with “small means conceal differences in
  frequency, severity and concentration.” The measured means differ, and no
  equivalence test was established.
- Say the saved ordinary-text loss differences are zero for the observed
  CounterFact/MQuAKE v0-family groups. “Never fires” is a mechanistic claim that
  needs selection traces; zero target-token loss difference alone cannot prove
  it. No unavailable group, especially unrun S1_literal CounterFact, should be
  subsumed into that statement.
