# HT-17 backup — measured results supersede the prototype appendix

Draft for charlie, October 4. Source: [HT-17 report](../../additional_work/HT-17_report.md).
The prototype appendix in the B–D drafting document is historical; use these results.

Survival/threshold figure: `assets/presentation-materials/figures/tails_ht17/snapshot-20261004-complete/survival_thresholds.png` (PDF/SVG beside it). The resolved deck export also includes `ht17-survival-backup.pdf` and `.png`. Fixed illustrative r0/order100; every cell remains in the source tables.

- Learned v5 shape ranges: zsRE .0435–.0588; CF .0294–.0978. Illustrative 95% intervals: [-.097,.177], [-.009,.187]. Held-out GPD−exponential gains across all fifteen cells: zsRE -.000394 to +.000259; CF -.001041 to +.002765 nats/excess. No equivalence claim.
- Stable v0 zsRE: shapes .433–1.029; illustrative interval [.390,.779]; predictive gains .149–.594. At threshold 1 nat, 13/15 cells fail the sample screen.
- Random CF: negative shapes, but 10/15 predictive comparisons invalid due to held-out support failures. The other five gain about .033 nats/excess. Not a guaranteed bound.
- Random zsRE, stable CF and all individual κ-pilot cells: insufficient events/windows. Undefined conditional severity stays undefined.
- AW-B: severity 1.619→.542 (zsRE), 1.925→.581 (CF), near-unchanged frequency. Paired differences: [-1.197,-.979] and [-1.456,-1.251] nats. All ten GPD fits invalid at endpoint; analytic mixture ceiling remains valid.
- Reader seeds: all three paired; 12/12 evaluations. CF ePC−BP conditional severity −.1066 nats, conditional window interval [−.3214,+.0840]; harmful-change frequency +.02134 percentage points, interval [+.00569,+.03363]. zsRE frequency −.005709 percentage points; severity +.6910 nats, with its interval withheld (2/200 undefined draws). The sparse ePC zsRE events cannot support a tail-family or safer-reader claim. These intervals condition on the saved readers and do not measure seed/population uncertainty.

All intervals condition on observed cells, with unverified window independence. No system-state growth W(N), temperature, asymptotic tail class or infinite variance was measured. HT-17 uses a generalized Pareto with fitted shape and scale, not a free-α entropy fit.
