# HT-17 backup — measured results supersede the prototype appendix

Draft for charlie, October 2. Source: [HT-17 report](../../additional_work/HT-17_report.md).
The prototype appendix in the B–D drafting document is historical; use these results.

Survival/threshold figure: `assets/presentation-materials/figures/tails_ht17/snapshot-20261002-seed1/survival_thresholds.png` (PDF/SVG beside it). The resolved deck export also includes `ht17-survival-backup.pdf` and `.png`. Fixed illustrative r0/order100; every cell remains in the source tables.

- Learned v5 shape ranges: zsRE .0435–.0588; CF .0294–.0978. Illustrative 95% intervals: [-.097,.177], [-.009,.187]. Held-out GPD−exponential gains across all fifteen cells: zsRE -.000394 to +.000259; CF -.001041 to +.002765 nats/excess. No equivalence claim.
- Stable v0 zsRE: shapes .433–1.029; illustrative interval [.390,.779]; predictive gains .149–.594. At threshold 1 nat, 13/15 cells fail the sample screen.
- Random CF: negative shapes, but 10/15 predictive comparisons invalid due to held-out support failures. The other five gain about .033 nats/excess. Not a guaranteed bound.
- Random zsRE, stable CF and all individual κ-pilot cells: insufficient events/windows. Undefined conditional severity stays undefined.
- AW-B: severity 1.619→.542 (zsRE), 1.925→.581 (CF), near-unchanged frequency. Paired differences: [-1.197,-.979] and [-1.456,-1.251] nats. All ten GPD fits invalid at endpoint; analytic mixture ceiling remains valid.
- Reader seeds: seeds 0–1 paired; 10/12 evaluations available. CF ePC−BP severity +.0357 nats, window interval [−.1568,+.2283]; frequency +.000816 percentage points, interval [−.019175,+.018365]. zsRE frequency −.004689 percentage points; severity +.7513 nats, with its interval withheld (2/200 undefined draws). Seed-0 zsRE ePC still has no observed harmful events; seed 1 has a few. Seed 2 pending, no safer-reader or superiority claim.

All intervals condition on observed cells, with unverified window independence. No system-state growth W(N), temperature, asymptotic tail class or infinite variance was measured. HT-17 uses a generalized Pareto with fitted shape and scale, not a free-α entropy fit.
