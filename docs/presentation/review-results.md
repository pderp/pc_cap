# Corrected predictive-coding results — completed default treatment

2026-09-28, Capex. All 64 cells passed the final integrity audit. All harm vectors and paired statistics were independently reconstructed on CPU. Eight error iterations, learning rate 0.1. The opening sections retain the completed default treatment; the PC-13 section below adds the later settling-depth controls.

Sources in pc_cap: `logs/additional_work/PC-v0/report-60-20260927/report.json` and `logs/additional_work/PC-v1/report-4-20260927/report.json`. Canonical reports: `docs/additional_work/PC-v0_report.md` and `PC-v1_report.md`.

H0: `results/additional_work/PC-v0/harm/pc-v0-60-20260927/report.json`. H1: `results/additional_work/PC-v1/harm/pc-v1-4-20260927/report.json`. H1's original cost receipt records a final-table failure; four complete arm receipts, both paired arrays and every statistic pass numerical reconstruction. The wrong original caption is superseded here: H1 has 245,237 positions per cell.

V0 finish time is whole-process time. V1 finish time is stream-engine time; process.json includes it, so never add the two. Harm time is separate. Averages of maxima are labelled as such; tokens and orders do not become independent realizations.

## PC-v0 — primary paired behavior by realization

Exposed historical S5; zsRE 1,000 edits, CounterFact 300; three realizations,
five dependent orders each, 60 planned cells. Differences below are **SE-E − SE-A**;
higher favors SE-E for behavior. `V0:<metric>[dataset,r]` means
`aggregates[dataset,metric].realizations[r]`, the mean paired difference across
the five orders; the native `pairs` table retains every order.

| Dataset | Realization | ES | RET-ES | RET-GS | LS |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | 0.001| 0.022| -0.0054| 0.038|
| zsre | 1 | 0.0006| 0.0198| 0.0022| -0.006|
| zsre | 2 | 0.0002| 0.0192| -0.0052| 0.028|
| counterfact | 0 | 0| 0| 0| 0|
| counterfact | 1 | 0| 0| 0| 0|
| counterfact | 2 | 0| 0| 0| 0|

### Bounded-text secondary behavior, kept separate

The same aggregate selector applies using the exact metric keys below; these
do not replace the legacy primary S5 scoring convention.

| Dataset | Realization | bounded_es_immediate | bounded_ret_es_end | bounded_ret_gs_end | bounded_ls_end |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | 0.001| 0.022| -0.0054| 0.038|
| zsre | 1 | 0.0006| 0.0198| 0.0022| -0.006|
| zsre | 2 | 0.0002| 0.0192| -0.0052| 0.028|
| counterfact | 0 | 0| 0| 0| 0|
| counterfact | 1 | 0| 0| 0| 0|
| counterfact | 2 | 0| 0| 0| 0|

### Between-realization summary

Each cell selects `V0:aggregates[dataset,metric].<column>`; min/max are the range
of the three realization means, not a confidence interval.

| Dataset | Metric | Mean | Minimum | Maximum |
| --- | --- | --- | --- | --- |
| zsre | ES | 0.0006| 0.0002| 0.001|
| zsre | RET-ES | 0.020333333| 0.0192| 0.022|
| zsre | RET-GS | -0.0028| -0.0054| 0.0022|
| zsre | LS | 0.02| -0.006| 0.038|
| counterfact | ES | 0| 0| 0|
| counterfact | RET-ES | 0| 0| 0|
| counterfact | RET-GS | 0| 0| 0|
| counterfact | LS | 0| 0| 0|

### Replication cost by realization

Each entry is the sum of `V0:cells[dataset,realization,arm].finish.elapsed_process_seconds`
over the five planned orders, retaining the ledger in the native report.

| Dataset | Realization | SE-A process seconds | SE-E process seconds |
| --- | --- | --- | --- |
| zsre | 0 | 4989.6644| 6772.5644|
| zsre | 1 | 4862.9879| 6597.3938|
| zsre | 2 | 5106.5113| 6911.6982|
| counterfact | 0 | 2217.0558| 2550.3809|
| counterfact | 1 | 2166.1344| 2507.0648|
| counterfact | 2 | 2188.3137| 2522.5358|

## Fixed-v5 — the four planned cells

Post hoc transfer check on exposed R1 realization 0, order 100, first 300 edits;
the same BP-trained base and selected reader in both arms, fresh memory per cell.
These four cells are not three independent replications and do not test PC reader
training. Use R1's installed endpoint semantics, including semantic revision.

### Checkpoint 100

| Dataset | Arm | ES | RET-ES | RET-GS | LS | near_miss | revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1| 1| 0.97| 1| 0.72| 1|
| zsre | SE-E | 1| 1| 0.97| 1| 0.72| 1|
| counterfact | SE-A | 1| 1| 0.825| 1| 1| 1|
| counterfact | SE-E | 1| 1| 0.82| 1| 1| 1|

### Checkpoint 300

| Dataset | Arm | ES | RET-ES | RET-GS | LS | near_miss | revision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 1| 1| 0.98333333| 1| 0.76| 1|
| zsre | SE-E | 1| 1| 0.98333333| 1| 0.76| 1|
| counterfact | SE-A | 1| 1| 0.80666667| 1| 1| 1|
| counterfact | SE-E | 1| 1| 0.80333333| 1| 1| 1|

### Fixed-v5 cost

| Dataset | Arm | Stream-engine seconds | Whole-process seconds |
| --- | --- | --- | --- |
| zsre | SE-A | 311.69835| 316.11111|
| zsre | SE-E | 421.65218| 426.03555|
| counterfact | SE-A | 292.92199| 297.33025|
| counterfact | SE-E | 355.03361| 359.42356|

## Ordinary-text harm — per-arm and paired summaries

H0: final snapshots, 4,064 fixed target positions per cell; H1: final 300-edit
snapshots, 245,237 fixed target positions per cell. These inventories differ and
must not be pooled. Positive signed changes are worse. Both arms use identical
positions and the same original reference within each paired study.

For H0 realization rows, average the **five cell summaries**, and keep every
order in the native readout; do not recalculate a pooled tail and call it their
mean. H1 has one order per dataset. `S[dataset,r,arm]` expands to
`cells[dataset,realization,arm].readout.summary.original`; `P[dataset,r]` expands
to `pairs[dataset,realization]`. Every following entry identifies H0 or H1.
The maximum shown is a mean of cell maxima where five orders exist, not a pooled
maximum; the native report retains the actual maxima and position locations.

### H0 arm summaries

| Dataset | Realization | Arm | kl.mean_signed | loss.mean_signed | loss.es99_positive | loss.maximum_signed |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | 0.0024122833| 0.0022632824| 0.23878431| 5.719436|
| zsre | 0 | SE-E | 0.0026181925| 0.0024543653| 0.25934381| 5.00932|
| zsre | 1 | SE-A | 0.001882752| 0.0024676266| 0.24906898| 4.2801564|
| zsre | 1 | SE-E | 0.0015983728| 0.0020355027| 0.20645324| 2.9473382|
| zsre | 2 | SE-A | 0.00064100799| 5.4335316e-05| 0.029747527| 1.0092573|
| zsre | 2 | SE-E | 0.0015775265| 0.00077880659| 0.10140988| 2.5005276|
| counterfact | 0 | SE-A | 0| 0| 0| 0|
| counterfact | 0 | SE-E | 0| 0| 0| 0|
| counterfact | 1 | SE-A | 0| 0| 0| 0|
| counterfact | 1 | SE-E | 0| 0| 0| 0|
| counterfact | 2 | SE-A | 0| 0| 0| 0|
| counterfact | 2 | SE-E | 0| 0| 0| 0|

| Dataset | Realization | Arm | loss.exceedance['0.01'].fraction | loss.exceedance['0.1'].fraction | loss.exceedance['1.0'].fraction | loss.half_mass_positions |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | 0.0011318898| 0.0010826772| 0.00068897638| 1.2|
| zsre | 0 | SE-E | 0.0010826772| 0.0010826772| 0.00073818898| 1.6|
| zsre | 1 | SE-A | 0.0011811024| 0.0010826772| 0.00078740157| 1.8|
| zsre | 1 | SE-E | 0.001230315| 0.0011318898| 0.00088582677| 2|
| zsre | 2 | SE-A | 0.00034448819| 0.00034448819| 9.8425197e-05| 1|
| zsre | 2 | SE-E | 0.00068897638| 0.00063976378| 0.00039370079| 1.4|
| counterfact | 0 | SE-A | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|
| counterfact | 0 | SE-E | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|
| counterfact | 1 | SE-A | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|
| counterfact | 1 | SE-E | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|
| counterfact | 2 | SE-A | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|
| counterfact | 2 | SE-E | 0| 0| 0| UNDEFINED (one or more zero-harm cells)|

### H0 matched differences — SE-E minus SE-A

| Dataset | Realization | positionwise.original.kl.mean_signed | positionwise.original.loss.mean_signed | positionwise.original.loss.es99_positive | difference_of_arm_es99.original |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | 0.00020590924| 0.00019108294| 0.12735481| 0.020559502|
| zsre | 1 | -0.0002843792| -0.00043212389| 0.046983073| -0.042615745|
| zsre | 2 | 0.00093651852| 0.00072447127| 0.084224628| 0.071662348|
| counterfact | 0 | 0| 0| 0| 0|
| counterfact | 1 | 0| 0| 0| 0|
| counterfact | 2 | 0| 0| 0| 0|

### H1 arm summaries

| Dataset | Realization | Arm | kl.mean_signed | loss.mean_signed | loss.es99_positive | loss.maximum_signed |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | 0.0018606214| 0.0018129309| 0.19558495| 9.2622675|
| zsre | 0 | SE-E | 0.001703612| 0.0016728278| 0.18161435| 12.270044|
| counterfact | 0 | SE-A | 0.0041756565| 0.0043814001| 0.45868647| 11.744238|
| counterfact | 0 | SE-E | 0.0043083345| 0.0045037415| 0.46991561| 12.225436|

| Dataset | Realization | Arm | loss.exceedance['0.01'].fraction | loss.exceedance['0.1'].fraction | loss.exceedance['1.0'].fraction | loss.half_mass_positions |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | SE-A | 0.0011784519| 0.0011295196| 0.00061980859| 53|
| zsre | 0 | SE-E | 0.0011825296| 0.0011213642| 0.00059126478| 49|
| counterfact | 0 | SE-A | 0.0028176825| 0.0026790411| 0.0014027247| 110|
| counterfact | 0 | SE-E | 0.0028462263| 0.0026871965| 0.0014598123| 110|

### H1 matched differences — SE-E minus SE-A

| Dataset | Realization | positionwise.original.kl.mean_signed | positionwise.original.loss.mean_signed | positionwise.original.loss.es99_positive | difference_of_arm_es99.original |
| --- | --- | --- | --- | --- | --- |
| zsre | 0 | -0.00015700938| -0.00014010307| 0.016070419| -0.013970602|
| counterfact | 0 | 0.00013267798| 0.00012234139| 0.038216428| 0.011229134|

**Keep the last two paired columns distinct:** the ES99 of positive
positionwise loss differences is not the difference of arm ES99 values. The
latter is the efficacy–harm slide slot; the former is additional paired detail.
Retain zero positions and the fractional expected-shortfall boundary.

| Readout | Charged readout process seconds |
| --- | --- |
| H0 | 1364.0314|
| H1 | 5004.1996|

<!-- PC-13 settling-depth controls -->

2026-09-29 addition, generated from the completed PC-13 report. The earlier five-order tables remain separate from this common-order depth comparison.

## PC-v0 settling-depth controls: retention, harm and cost

Completed exposed S5 comparison: two datasets × three realizations × **order 100 only** at depths 1, 8 and 32. The eight-step rows are the order-100 subset of the previously published 60-cell experiment. Using its five-order mean beside these single-order controls would compare different populations. The full original experiment remains in PC-v0_report.md. zsRE ends at 1,000 edits; CounterFact at 300. Original S5 primary scoring and bounded-text secondary scoring stay separate.

### Results at the common order

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



### Paired differences by realization

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



### One-step mechanism check

At zero inferred error, the first gradient step gives e₁ = −η·adjoint; here η=0.1. In exact arithmetic, the unchanged unit-direction transport removes this positive scale. The actual-solver diagnostic verifies this to floating-point tolerance even with nonzero writes. **All recorded primary and bounded-text secondary endpoints match exactly for the six one-step pairs.** This is a mechanism check, not an independent scientific advantage.

| Dataset | r | Primary + secondary exact | Harm vectors bitwise equal | Maximum absolute harm-vector difference |
| --- | --- | --- | --- | --- |
| zsre | 0 | True | False | 0.000345071 |
| zsre | 1 | True | False | 2.08926e-05 |
| zsre | 2 | True | False | 3.80544e-05 |
| counterfact | 0 | True | True | 0 |
| counterfact | 1 | True | True | 0 |
| counterfact | 2 | True | True | 0 |



The zsRE harm vectors are not bitwise equal: small floating-point differences survive despite equal endpoint scores. CounterFact harm is exactly zero for both arms. Rounded summaries do not justify saying all probabilities or final memories are identical. Learning costs differ even at one step because the error path includes its terminal diagnostic.

### Interpretation and limits

On these zsRE streams, more settling increases own-prompt retention, while 32 steps reduces paraphrase retention. Mean loss increase and ES99+ rise with depth, alongside a much larger learning cost. The maximum does **not** rise monotonically: the eight-step mean of maxima is smaller than at one step, then rises at 32. More retained taught answers therefore do not establish better generalization, lower harm or a net scientific benefit. CounterFact has saturated own-prompt scores and zero paraphrase retention at all depths, limiting its discrimination.

The direction and compute controls are still needed to separate structured credit from useful extra acquisition work. The depth effect alone cannot establish that the content of PC credit, rather than extra computation, causes the gain. Random-direction and additional-update adjoint groups remain pending until their full runs finish; no provisional effects are substituted.

Harm uses the same 32 ordinary-text windows / 4,064 fixed-prefix target positions per cell and the same cap-off/original reference. These dependent positions are not independent experimental replicates and this does not fit a heavy-tail distribution. Learning wall is a ledger subset of whole-process time; do not add them. Full original eight-step acquisition and harm jobs are charged once, not again for this subset analysis.

| Depth | Acquisition process seconds (entire source group) | Harm process seconds (entire source group) | Source cells |
| --- | --- | --- | --- |
| 1 | 8979.54 | 277.067 | 12 |
| 8 | 49392.3 | 1364.03 | 60 |
| 32 | 12991.8 | 276.464 | 12 |



The active-inference programme motivates selective correction and the consequences of rare errors. These experiments measure acquisition credit in a frozen model with a cap; they do not implement autonomous expected-free-energy policy selection or establish general PC superiority. Sources and exact numeric tables are in `logs/additional_work/PC-v0/controls-report-20260929/report.json`.

Figure: `assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png` (PDF/SVG and source manifest beside it). These are shareable scientific assets outside the repository.
