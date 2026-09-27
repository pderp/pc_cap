# Rare severe ordinary-text harm — all receipted Stage-4 cells (HT-13, v1.2)

2026-09-26, Capstan (Claude, orchestrator); v1.1 after Capex's review (`pc_cap/docs/tasks/HT-13-round46-review.md`).
Source: the saved per-position full-validation vectors of every cell **with a queue finish receipt**
(`results/R1/stage4_sealed_cells/*/attempt-0000/full-validation-*.npz`, filtered by `logs/R1/final_queue/*/finish.json`;
1,931 reset-context windows × 127 positions = 245,237 positions per cell). The quantity is the per-token loss change of
the cap against **its own cap-off base**, in nats. Generator: `aw/tail_figures.py` (pc_cap, canonical) with a copy at
`figures/tails/tail_figures.py`; run from the pc_cap root with the system `python3` (matplotlib):
`python3 -m aw.tail_figures --out /home/derp/cap/assets/presentation-materials/figures/tails`. Data
`figures/tails/tails.json`; table `figures/tails/table.md`. Descriptive; reruns after the halt (R1-D14f).
Coverage at this run (v1.2, post-halt refresh 2026-09-27): the reconciled 270-cell state — blocks 1–4 complete and
the 45 block-5 cells in scope (S1_LM zsRE and CounterFact, S1_literal zsRE), i.e. every receipted cell of the halted
queue. `figures/tails/table.md` is the authoritative table; the one below is transcribed from it.

## Figures

- `figures/tails/survival_by_dataset.png` — empirical P(loss increase > x) on log–log axes, one panel per dataset,
  all receipted cells of a condition pooled. Zero survival is floored at 10⁻⁹ for display only; nothing beyond each
  curve's maximum has nonzero probability in these data.
- `figures/tails/rarity_vs_severity.png` — fraction of positions with a loss increase above 0.01 nats against the
  maximum single-token loss increase, one point per condition × dataset.

## Definitions

- **ES99+**: the mean of the worst 1 % of positions (fractional boundary, zero mass included), i.e. an expected
  shortfall, not a percentile. v1 of this page reported the 99th percentile under this name; that was wrong (a single
  10-nat loss among 1,000 positions has percentile 0 and ES99 1.0) and is corrected here.
- **Half of all harm sits in**: the smallest number of positions, taken in descending order, carrying half of the
  total positive loss change.
- The pool repeats the same 245,237 positions across five orders and three realizations: it is a mixture of cell ×
  position observations, not millions of independent test items. Proportions are descriptive.

## What the pooled tails show

| condition | dataset | cells | P(> 0.01) | P(> 1 nat) | P(> 5) | max (nats) | ES99+ | half of all harm sits in |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| learned reader (v5) | zsRE | 15 | 0.159 % | 0.080 % | 0.009 % | 11.1 | 0.26 | 1,024 positions (0.03 %) |
| learned reader (v5) | CounterFact | 15 | 0.298 % | 0.165 % | 0.027 % | 15.4 | 0.57 | 1,900 (0.05 %) |
| learned reader (v5) | MQuAKE | 15 | 0.313 % | 0.194 % | 0.023 % | 17.1 | 0.62 | 2,336 (0.06 %) |
| random reader | zsRE | 15 | 0.027 % | 0.017 % | 0.001 % | 7.0 | 0.05 | 225 |
| random reader | CounterFact | 15 | 2.05 % | 1.70 % | 0.52 % | 20.3 | 5.53 | 18,856 (0.5 %) |
| random reader | MQuAKE | 15 | 0.409 % | 0.336 % | 0.069 % | 15.1 | 1.22 | 3,818 |
| stable v0 cap | zsRE | 15 | 0.104 % | 0.034 % | 0.009 % | 27.7 | 0.18 | 262 |
| live v0 cap C1 | zsRE | 15 | 0.096 % | 0.046 % | 0.013 % | 27.7 | 0.21 | 497 |
| live v0 cap C2 | zsRE | 15 | 0.019 % | 0.016 % | 0.015 % | 50.6 | 0.32 | 175 |
| matched update | zsRE | 15 | 0.105 % | 0.034 % | 0.009 % | 33.8 | 0.18 | 280 |
| continued base (LM) + stable cap | zsRE | 15 | 0.105 % | 0.034 % | 0.010 % | 27.6 | 0.18 | 266 |
| continued base (literal) + stable cap | zsRE | 15 | 0.104 % | 0.034 % | 0.009 % | 27.7 | 0.18 | 263 of 3,678,555 |
| every v0-family cap | CounterFact, MQuAKE | | 0 | 0 | 0 | 0 | 0 | never fires on ordinary text |

Three statements the figures support, and their limits:

1. **Harm is rare and concentrated for every condition that writes.** For the learned reader, 0.16–0.31 % of positions
   change by more than 0.01 nats and half of all the harm sits in 0.03–0.06 % of positions. Mean drift (0.002–0.007
   nats) is the average of a very small number of large losses; ES99+ of 0.26–0.62 nats says what the worst 1 % of
   positions cost on average.
2. **Small means conceal differences in frequency, severity and concentration between the learned cap and the
   v0-family caps.** The learned cap disturbs more positions but its worst tokens are 11–17 nats; the v0-family caps
   disturb fewer positions on zsRE and their worst tokens reach 28–51 nats. Live C2 is the extreme: almost every
   position it disturbs at all loses more than 5 nats. "Rarer but heavier" versus "more frequent but milder" is what
   the survival curves show; the means differ too, and no equivalence between them was tested.
3. **On CounterFact and MQuAKE the saved ordinary-text loss differences of the observed v0-family groups are exactly
   zero** (their calibration matches exact prompts only), while their paraphrase retention is also zero. This is a
   statement about the saved target-token losses of those groups; whether the cap "never fired" is a mechanistic claim
   that would need the selection traces, and unrun groups (S1_literal CounterFact) are not included.

The cell-level analysis (HT-15, Capex; `figures/tails/tail_spread.md`, `cell_tails.csv`) adds the spread hidden by
pooling. Each cell uses the same 245,237 positions; its fractional ES99+ is computed first, then the five stream
orders are averaged within each realization. For the learned reader the three realization means are 0.259, 0.266 and
0.254 nats on zsRE; 0.610, 0.480 and 0.622 on CounterFact; and 0.731, 0.710 and 0.421 on MQuAKE (300 edits): ranges
0.254–0.266, 0.480–0.622 and 0.421–0.731. Live C2 on zsRE has 0.243, 0.346 and 0.375: its average exceeds the learned
reader's, but realization 0 has the opposite ordering. These are descriptive three-realization ranges, not confidence
intervals or a superiority test. Mean per-cell half-mass counts are 68.7 positions for the learned reader and 12.5 for
live C2 on zsRE; they have a per-cell denominator and differ from the pooled counts above. Mean cell ES99+ and pooled
ES99+ are different estimands that happen to coincide for the learned-reader groups; their equality does not make
positions independent. After the reconciled halt, S1_literal zsRE has all fifteen cells (5 / 5 / 5). Its
realization ES99+ means are 0.133, 0.213 and 0.192 nats, range 0.133–0.213; the equal-weight cell mean is 0.179
(previously 0.165 across seven cells). The mean cell maximum is 25.324 nats, with realization means ranging
22.676–26.951; this is distinct from the pooled maximum of 27.688 nats. Mean per-cell half-mass count is 19.13
positions (realization means 15.2, 19.4, 22.8). The eight added cells are all S1_literal zsRE; every previously
reported cell is unchanged. Canonical refresh and change record: `pc_cap/logs/additional_work/round48/HT-15b-270/`.

Reference caveat: these curves compare each cap with **its own** cap-off base. For the continued-base controls (S1)
that base is the continued checkpoint, not the original model, so a zero or small curve does not measure the total
departure from the original GPT-2; the saved vectors also hold the original-base reference (fields 2 and 4) and a
second view can be produced from them.

What this does not establish: a heavy-tailed distribution class, a power law or any asymptotic tail (finite
empirical data do not establish an asymptotic tail class; a token's loss −log p is not bounded by the vocabulary
size); independence of positions; robustness to unobserved inputs; temporal clustering. The κ pilot (DEC-054) and the bounded-correction experiment (if run) ask
whether the tail can be shaped; this page only measures it.

## For the deck

Under the heavy-tailed-distributions theme: the survival figure as the "why the mean misleads" slide (outline slide
6), the rarity-versus-severity figure as the comparator slide (slide 7), with the sentence that the registered
comparators have small mean changes but different frequency, severity and concentration. The current table and
HT-15b spread use the reconciled 270-cell state.
