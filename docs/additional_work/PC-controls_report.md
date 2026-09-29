# PC-v0 settling-depth controls: retention, harm and cost

Completed exposed S5 comparison: two datasets × three realizations × **order 100 only** at depths 1, 8 and 32. The eight-step rows are the order-100 subset of the previously published 60-cell experiment. Using its five-order mean beside these single-order controls would compare different populations. The full original experiment remains in PC-v0_report.md. zsRE ends at 1,000 edits; CounterFact at 300. Original S5 primary scoring and bounded-text secondary scoring stay separate.

## Results at the common order

All rows are means over three realizations. Scores are fractions; loss is in nats. SE-A is the independently executed paired adjoint baseline at each requested depth (it does not itself settle).

| Dataset | Depth | Arm | ES | RET-ES | RET-GS | LS | Mean KL | Mean ΔNLL | ES99+ | Mean cell max | Largest maximum | Learning s/cell | Process s/cell |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 1 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 275.934 | 1008.01 |
| zsre | 1 | SE-E | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184297 | 0.00145136 | 0.155816 | 3.6504 | 5.46857 | 341.182 | 1092.51 |
| counterfact | 1 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.4616 | 436.964 |
| counterfact | 1 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 59.3532 | 455.701 |
| zsre | 8 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 280.837 | 1024.99 |
| zsre | 8 | SE-E | 0.999 | 0.534 | 0.131 | 0.976667 | 0.0021476 | 0.00157227 | 0.166889 | 2.39772 | 3.24707 | 614.015 | 1342.27 |
| counterfact | 8 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.3522 | 435.266 |
| counterfact | 8 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 107.861 | 505.132 |
| zsre | 32 | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 0.00184295 | 0.00145132 | 0.155812 | 3.6504 | 5.46859 | 273.309 | 988.69 |
| zsre | 32 | SE-E | 0.999 | 0.565 | 0.122 | 0.996667 | 0.00257776 | 0.0022107 | 0.23644 | 4.36855 | 8.02868 | 1524.85 | 2238.27 |
| counterfact | 32 | SE-A | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 45.6985 | 438.064 |
| counterfact | 32 | SE-E | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 269.302 | 665.56 |



## Paired differences by realization

SE-E minus SE-A. Behavior higher is better; harm and cost lower are better. No pooling across depths, confidence interval, best-depth selection, or treatment-by-depth significance test. The same realizations and facts recur across depths.

| Dataset | Depth | r | ΔES | ΔRET-ES | ΔRET-GS | ΔLS | Δmean KL | Δmean NLL | ΔES99+ | Δmax | Δlearning seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | 1 | 0 | 0 | 0 | 0 | 0 | 4.11364e-08 | 1.20774e-07 | 1.20774e-05 | -1.63413e-05 | 66.3262 |
| zsre | 1 | 1 | 0 | 0 | 0 | 0 | 4.69346e-09 | -3.53038e-09 | -3.53038e-07 | -1.56956e-05 | 63.4399 |
| zsre | 1 | 2 | 0 | 0 | 0 | 0 | 3.56836e-09 | 2.02868e-08 | 1.17391e-06 | 3.80544e-05 | 65.9785 |
| counterfact | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13.8853 |
| counterfact | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13.791 |
| counterfact | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 13.9986 |
| zsre | 8 | 0 | -0.001 | 0.009 | -0.004 | 0.035 | 0.00087932 | 0.000439445 | 0.0439445 | -2.22152 | 341.669 |
| zsre | 8 | 1 | 0.002 | 0.013 | 0.006 | 0 | -0.00115067 | -0.000769646 | -0.0769646 | -1.09362 | 332.701 |
| zsre | 8 | 2 | 0.001 | 0.034 | -0.001 | -0.015 | 0.00118531 | 0.000693059 | 0.0662517 | -0.442904 | 325.164 |
| counterfact | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 61.5965 |
| counterfact | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 64.1353 |
| counterfact | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 61.7958 |
| zsre | 32 | 0 | 0.002 | 0.05 | -0.005 | 0.03 | 0.00369565 | 0.00291483 | 0.307844 | 2.56009 | 1266.32 |
| zsre | 32 | 1 | 0.001 | 0.043 | -0.011 | 0.01 | -0.00116792 | -0.000818578 | -0.0818578 | -1.11166 | 1229.74 |
| zsre | 32 | 2 | -0.001 | 0.056 | -0.01 | 0.04 | -0.000323294 | 0.000181908 | 0.0158982 | 0.705998 | 1258.56 |
| counterfact | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 223.045 |
| counterfact | 32 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 224.224 |
| counterfact | 32 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 223.541 |



Bounded-text secondary differences:

| Dataset | Depth | r | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre | 1 | 1 | 0 | 0 | 0 | 0 |
| zsre | 1 | 2 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 1 | 0 | 0 | 0 | 0 |
| counterfact | 1 | 2 | 0 | 0 | 0 | 0 |
| zsre | 8 | 0 | -0.001 | 0.009 | -0.004 | 0.035 |
| zsre | 8 | 1 | 0.002 | 0.013 | 0.006 | 0 |
| zsre | 8 | 2 | 0.001 | 0.034 | -0.001 | -0.015 |
| counterfact | 8 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 8 | 1 | 0 | 0 | 0 | 0 |
| counterfact | 8 | 2 | 0 | 0 | 0 | 0 |
| zsre | 32 | 0 | 0.002 | 0.05 | -0.005 | 0.03 |
| zsre | 32 | 1 | 0.001 | 0.043 | -0.011 | 0.01 |
| zsre | 32 | 2 | -0.001 | 0.056 | -0.01 | 0.04 |
| counterfact | 32 | 0 | 0 | 0 | 0 | 0 |
| counterfact | 32 | 1 | 0 | 0 | 0 | 0 |
| counterfact | 32 | 2 | 0 | 0 | 0 | 0 |



## One-step mechanism check

At zero inferred error, the first gradient step gives e₁ = −η·adjoint; here η=0.1. In exact arithmetic, the unchanged unit-direction transport removes this positive scale. The actual-solver diagnostic verifies this to floating-point tolerance even with nonzero writes. **All recorded primary and bounded-text secondary endpoints match exactly for the six one-step pairs.** This is a mechanism check, not an independent scientific advantage.

| Dataset | r | Primary + secondary exact | Harm vectors bitwise equal | Max |harm-vector difference| |
| --- | --- | --- | --- | --- |
| zsre | 0 | True | False | 0.000345071 |
| zsre | 1 | True | False | 2.08926e-05 |
| zsre | 2 | True | False | 3.80544e-05 |
| counterfact | 0 | True | True | 0 |
| counterfact | 1 | True | True | 0 |
| counterfact | 2 | True | True | 0 |



The zsRE harm vectors are not bitwise equal: small floating-point differences survive despite equal endpoint scores. CounterFact harm is exactly zero for both arms. Rounded summaries do not justify saying all probabilities or final memories are identical. Learning costs differ even at one step because the error path includes its terminal diagnostic.

## Interpretation and limits

On these zsRE streams, more settling increases own-prompt retention, while 32 steps reduces paraphrase retention. Mean loss increase and ES99+ rise with depth, alongside a much larger learning cost. The maximum does **not** rise monotonically: the eight-step mean of maxima is smaller than at one step, then rises at 32. More retained taught answers therefore do not establish better generalization, lower harm or a net scientific benefit. CounterFact has saturated own-prompt scores and zero paraphrase retention at all depths, limiting its discrimination.

The direction and compute controls are still needed to separate structured credit from useful extra acquisition work. The depth effect alone cannot establish that the content of PC credit, rather than extra computation, causes the gain. Random-direction and additional-update adjoint groups remain pending until their full runs finish; no provisional effects are substituted.

Harm uses the same 32 ordinary-text windows / 4,064 fixed-prefix target positions per cell and the same cap-off/original reference. These dependent positions are not independent experimental replicates and this does not fit a heavy-tail distribution. Learning wall is a ledger subset of whole-process time; do not add them. Full original eight-step acquisition and harm jobs are charged once, not again for this subset analysis.

| Depth | Acquisition process seconds (entire source group) | Harm process seconds (entire source group) | Source cells |
| --- | --- | --- | --- |
| 1 | 8979.54 | 277.067 | 12 |
| 8 | 49392.3 | 1364.03 | 60 |
| 32 | 12991.8 | 276.464 | 12 |



The active-inference programme motivates selective correction and the consequences of rare errors. These experiments measure acquisition credit in a frozen model with a cap; they do not implement autonomous expected-free-energy policy selection or establish general PC superiority. Sources and exact numeric tables are in `logs/additional_work/PC-v0/controls-report-20260929/report.json`.
