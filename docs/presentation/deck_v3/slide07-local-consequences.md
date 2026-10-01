# Slide 7 — What does the observed tail shape add?

**Draft speaker text for charlie's review; updated October 1, 2026.**

**On screen:** Three qualified findings: learned v5, stable v0 on zsRE, and invalid or sparse fits. Intervals are conditional window-bootstrap intervals.

## Speaker text

“We fitted the positive excess above each threshold with a generalized Pareto distribution and compared it with the exponential special case. This is the one-sided alpha-equals-one family discussed in Nelson’s manuscript. Shape and scale are fitted separately; scale depends on the threshold. At least a hundred excesses in thirty windows were required. This is an exploratory finite-range model comparison.” [`HT17-tails`]

“For learned v5, shape estimates at 0.01 nat are close to zero: 0.0435 to 0.0588 on zsRE and 0.0294 to 0.0978 on CounterFact. The fixed illustrative realization-zero, order-one-hundred intervals are minus 0.097 to 0.177 and minus 0.009 to 0.187. Both include zero. Held-out-window log-likelihood gains over the exponential are tiny, at most about 0.0028 nats per excess. An exponential is an economical approximation on this measured range; this is not an equivalence test.” [`HT17-tails`]

“Stable v0 on zsRE shows a more pronounced tail: fitted shapes range from 0.433 to 1.029, with an illustrative interval of 0.390 to 0.779. Held-out predictive gains are 0.149 to 0.594 nats per excess in every cell. But at a one-nat threshold, thirteen of fifteen cells have too few events for a fit. The evidence does not establish the farthest tail or infinite variance.” [`HT17-tails`]

“The random CounterFact reader illustrates a failure mode: all fitted shapes are negative, yet ten of fifteen held-out comparisons fail because an estimated endpoint excludes an observed held-out event. Every mixture fit has an endpoint pathology and is labelled invalid. Sparse random-zsRE, stable-CounterFact and individual kappa-pilot cells have no eligible headline shape. These cases remain in the report.” [`HT17-tails`]

“We have not measured system state growth, identified a complexity class or assigned a temperature. The scientific advance is a tested distinction in the observed shape of prediction-loss changes, with failed predictions visible. Those consequences can inform a future active-inference audit policy; they do not establish one.” [`HT17-tails`, `AI-next`]

## Sources and backup

[HT-17 methods and all cells](../../../logs/additional_work/HT-17/snapshot-20261001-v2/report.md). [Tail backup](backup-ht17.md) contains the survival figure and precise predictive-score ranges. Outcome-independent illustrative choice: realization 0, order 100. No interval covers training-seed or subject-population uncertainty.
