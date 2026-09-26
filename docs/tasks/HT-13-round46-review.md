# HT-13 follow-up for Claude — discovered during PC-5 / PRES-2

2026-09-26, Capex. No edits to Claude-owned `aw/scoring.py` or `aw/tail_figures.py`.

1. **ES99 is a percentile in both helpers.** `Accumulator.summary()['es99']` and
   `tail_figures.statistics()['es99_positive']` call `np.quantile(pos, .99)`.
   Expected shortfall requires averaging the top 1%, with a fractional boundary
   and zero mass retained. For 1,000 positions with one loss increase of 10 nats,
   the 99th percentile is zero and ES99+ is 1 nat. The current learned-reader
   table's zero ES99 therefore does not mean its severe tail is harmless.
   PC-5 imports the unchanged `score_configs`; its separate summary implements
   fractional ES99 and tests this distinction. Neither finding affects saved
   five-field vectors, the running trainer, or registered frozen ES95 results.
2. **The figure title asserts “heavy-tailed.”** The brief explicitly limits our
   inference to observed rare/concentrated harm. Suggested title: “Rare severe
   ordinary-text harm: empirical survival of token loss increases.” No fitted
   tail-family conclusion follows from this plot.
3. **Collection currently counts NPZ files, not verified completed cells.** It
   scans `attempt-0000/full-validation-*.npz` without checking the final result.
   A live cell may have a full-validation file before its final receipt. Prefer
   the reconciled 270-cell inventory and one admitted final checkpoint per cell.
   After the halt verify the per-condition/dataset counts against that inventory.
4. These curves use **own cap-off only**. For S1 this is the continued base, not
   the original base; a zero curve does not prove zero total departure from the
   original model. Keep the reference in the plot caption or provide both views.
5. The pool repeats the same 245,237 positions across orders/realizations. It is
   a descriptive cell-position mixture, not millions of independent test items.
   The log display floors zero survival and clips below its y-axis lower limit;
   do not interpret the artificial floor as nonzero probability beyond a maximum.

`aw.refresh_after_halt` refuses publication while the ES99 regression or title
remains. The command and slide drafts are otherwise prepared. This is an owner
handoff, not a new lead-approval requirement. PRES-2 does not quote the defective
ES99 column; its HT-13 figure slot remains explicitly draft/pending correction.
