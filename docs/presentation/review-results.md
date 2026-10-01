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

The depth effect alone cannot establish that the content of PC credit, rather than extra computation, causes the gain. The closed direction control and completed offered-budget control below narrow the interpretation without resolving that attribution.

Harm uses the same 32 ordinary-text windows / 4,064 fixed-prefix target positions per cell and the same cap-off/original reference. These dependent positions are not independent experimental replicates and this does not fit a heavy-tail distribution. Learning wall is a ledger subset of whole-process time; do not add them. Full original eight-step acquisition and harm jobs are charged once, not again for this subset analysis.

| Depth | Acquisition process seconds (entire source group) | Harm process seconds (entire source group) | Source cells |
| --- | --- | --- | --- |
| 1 | 8979.54 | 277.067 | 12 |
| 8 | 49392.3 | 1364.03 | 60 |
| 32 | 12991.8 | 276.464 | 12 |



The active-inference programme motivates selective correction and the consequences of rare errors. These experiments measure acquisition credit in a frozen model with a cap; they do not implement autonomous expected-free-energy policy selection or establish general PC superiority. Sources and exact numeric tables are in `logs/additional_work/PC-v0/controls-report-20260929/report.json`.

### Direction and offered-budget controls (DEC-075/079)

The random-direction run is **closed by resource rule**, not a complete 12-cell experiment. Only its first zsRE realization-0/order-100 pair was attempted: adjoint completed 1,000 items; random credit stopped after 993. The planned group contains ten unstarted cells (five remaining pairs), not eleven. These partial observations are not pooled with the complete depth comparisons.

| Arm | Status | Items | Immediate ES | Process seconds | Total forwards | Total reverses |
| --- | --- | --- | --- | --- | --- | --- |
| SE-A | complete | 1000 | 0.998 | 989.738 | 139630 | 11334 |
| SE-R | resource_stop | 993 | 0.00302115 | 3727.43 | 641262 | 340155 |


On the common first 993 items, immediate ES is 0.997986 for adjoint and 0.003021 for random credit. Three random-arm immediate answers succeed; even all seven remaining answers succeeding would give only 0.010 over 1,000 items. That bound concerns immediate ES, not the unobserved final memory or retention. Random credit retains the true eight-step credit's norm and pays for its calculation before replacing the direction. This one stream supports the practical importance of informative credit in this implementation; it does not establish a general impossibility result for random search or a PC advantage over adjoint.

The additional-update adjoint control completed all twelve cells (six pairs). The PC arm's budget was **offered, not consumed**. Per-item operation counts include forwards, partial forwards and reverses; they are not FLOPs. Most records hit the stopping thresholds without spending the allowance, and some incomplete rounds roll back while their compute remains charged.

| Dataset | Arm | ES | RET-ES | RET-GS | LS | Learning forwards | Learning reverses | Learning seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | SE-A | 0.998333 | 0.515333 | 0.130667 | 0.97 | 75591.3 | 11214 | 270.277 |
| zsre | SE-AM | 0.983333 | 0.508 | 0.142 | 0.986667 | 75537.3 | 11223 | 270.041 |
| counterfact | SE-A | 1 | 1 | 0 | 1 | 12400 | 1826.67 | 45.0171 |
| counterfact | SE-AM | 1 | 1 | 0 | 1 | 12400 | 1826.67 | 45.2319 |


| Dataset | r | Offered ops | Used ops | Fraction used | Threshold stops | Incomplete rollbacks |
| --- | --- | --- | --- | --- | --- | --- |
| zsre | 0 | 391311 | 225484 | 0.576227 | 945 | 55 |
| zsre | 1 | 380888 | 219015 | 0.575012 | 953 | 43 |
| zsre | 2 | 388261 | 225589 | 0.581024 | 962 | 35 |
| counterfact | 0 | 61344 | 32996 | 0.537885 | 300 | 0 |
| counterfact | 1 | 62026 | 33456 | 0.539387 | 300 | 0 |
| counterfact | 2 | 61096 | 32628 | 0.534045 | 300 | 0 |


The control does not recover the eight-step own-prompt retention gain, but also does not spend an equal measured compute budget. Its stopping logic/prefix traversal differ; the small behavior changes cannot be attributed to extra updates alone. These results leave **direction versus extra effective compute unresolved**. CounterFact's saturated own-prompt and zero paraphrase scores limit discrimination. Exact per-realization differences and process/operation costs are in `PC-matched-control_report.md`. Separate full-vector PC-12 harm curves were not supplied; native drift summaries are available but cannot fill an ES99 slot.

Figure: `assets/presentation-materials/figures/pc_v0/controls/depth-retention-harm-cost.png` (PDF/SVG and source manifest beside it). These are shareable scientific assets outside the repository.

<!-- AW-B4 final -->

## Bounded correction: calibration and exposed-stream evaluation

### Calibration: all sixteen settings

Exposed development memories, 300 edits per dataset. Selection precedes evaluation. All means and tails below use the full 245,237-position fixed-prefix inventory. ES is a saved-memory re-query, equal to RET-ES, not immediate acquisition. RET-GS is the installed item-level paraphrase score and can include fractional item credit.

| Dataset | Setting | ES | RET-ES | RET-GS | LS | near_miss | revision | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL | Eligible on both datasets |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre | v5 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00226972 | 0.00231002 | 0.237363 | 9.94469 | reference |
| zsre | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | reference |
| zsre | clip:0.5 | 0 | 0 | 0 | 1 | 1 | 0 | 3.58605e-05 | 4.50619e-05 | 0.0112707 | 0.47582 | False |
| zsre | mixture:0.367879 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.000707308 | 0.000711152 | 0.0760992 | 0.999918 | True |
| zsre | clip:1 | 0 | 0 | 0 | 1 | 1 | 0 | 0.000100914 | 0.00012586 | 0.022186 | 0.971916 | False |
| zsre | mixture:0.135335 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00126169 | 0.00127257 | 0.133141 | 1.99969 | True |
| zsre | clip:2 | 0.0233333 | 0.0233333 | 0.00333333 | 1 | 1 | 0.04 | 0.000239609 | 0.000271712 | 0.0399144 | 1.68793 | False |
| zsre | mixture:0.0183156 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.0019108 | 0.00192328 | 0.198627 | 3.99743 | True |
| zsre | clip:4 | 0.363333 | 0.363333 | 0.33 | 1 | 0.94 | 0.36 | 0.000565227 | 0.000579856 | 0.0724626 | 3.48863 | False |
| zsre | mixture:0.000335463 | 0.996667 | 0.996667 | 0.973333 | 1 | 0.87 | 1 | 0.00224227 | 0.00227054 | 0.233414 | 7.86636 | True |
| zsre | shrink:0.25 | 0.0233333 | 0.0233333 | 0.0133333 | 1 | 1 | 0.02 | 2.52627e-05 | 3.53354e-05 | 0.0102382 | 0.838104 | False |
| zsre | shrink:0.5 | 0.686667 | 0.686667 | 0.523333 | 1 | 0.94 | 0.8 | 0.000144328 | 0.000164474 | 0.0274169 | 1.77144 | False |
| zsre | shrink:0.75 | 0.996667 | 0.996667 | 0.963333 | 1 | 0.87 | 1 | 0.000637218 | 0.000667436 | 0.0775842 | 5.16498 | False |
| zsre | gate:0.4 | 0.996667 | 0.996667 | 0.936667 | 1 | 0.89 | 1 | 0.00119372 | 0.00118687 | 0.122732 | 9.94469 | False |
| zsre | gate:0.3 | 0.996667 | 0.996667 | 0.89 | 1 | 0.89 | 1 | 0.000489537 | 0.000480396 | 0.0485787 | 7.08622 | False |
| zsre | gate:0.2 | 0.996667 | 0.996667 | 0.843333 | 1 | 0.92 | 1 | 0.000128021 | 0.000136498 | 0.0136498 | 6.25724 | False |
| counterfact | v5 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00592908 | 0.00594535 | 0.610483 | 14.0189 | reference |
| counterfact | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | reference |
| counterfact | clip:0.5 | 0 | 0 | 0 | 1 | 1 | 0 | 8.94517e-05 | 9.45276e-05 | 0.0269599 | 0.518595 | False |
| counterfact | mixture:0.367879 | 1 | 1 | 0.745 | 0.98 | 1 | 1 | 0.00160171 | 0.00161787 | 0.173316 | 0.999999 | True |
| counterfact | clip:1 | 0 | 0 | 0 | 1 | 1 | 0 | 0.000251509 | 0.000278407 | 0.0532289 | 0.955991 | False |
| counterfact | mixture:0.135335 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00292484 | 0.00294834 | 0.309255 | 1.99999 | True |
| counterfact | clip:2 | 0.06 | 0.06 | 0.035 | 1 | 1 | 0.04 | 0.000602666 | 0.000628655 | 0.0960076 | 1.75216 | False |
| counterfact | mixture:0.0183156 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00464092 | 0.0046712 | 0.482867 | 3.99996 | True |
| counterfact | clip:4 | 0.67 | 0.67 | 0.413333 | 0.98 | 1 | 0.56 | 0.00144221 | 0.00146507 | 0.18396 | 4.01473 | False |
| counterfact | mixture:0.000335463 | 1 | 1 | 0.753333 | 0.98 | 1 | 1 | 0.00576468 | 0.00580267 | 0.596211 | 7.99757 | True |
| counterfact | shrink:0.25 | 0.0366667 | 0.0366667 | 0.00666667 | 1 | 1 | 0 | 8.65975e-05 | 9.06651e-05 | 0.0273046 | 0.880767 | False |
| counterfact | shrink:0.5 | 0.826667 | 0.826667 | 0.355 | 1 | 1 | 0.86 | 0.000467657 | 0.000475792 | 0.076857 | 3.18266 | False |
| counterfact | shrink:0.75 | 1 | 1 | 0.688333 | 0.98 | 1 | 1 | 0.00186503 | 0.00187723 | 0.215754 | 7.67421 | False |
| counterfact | gate:0.4 | 1 | 1 | 0.741667 | 0.98 | 1 | 1 | 0.00406943 | 0.00411213 | 0.420645 | 10.3691 | False |
| counterfact | gate:0.3 | 0.993333 | 0.993333 | 0.711667 | 0.98 | 1 | 1 | 0.00275639 | 0.00277626 | 0.283609 | 10.1554 | False |
| counterfact | gate:0.2 | 0.856667 | 0.856667 | 0.65 | 0.98 | 1 | 0.98 | 0.00156517 | 0.0015625 | 0.159977 | 8.27882 | False |



Eligibility requires RET-ES and RET-GS within ±0.02 of v5 on **both** datasets, without decreasing LS or near-miss preservation. Rank eligible arms by the **smaller** dataset reduction in maximum harm, then the **smaller** ES99 reduction; complete ties retain the declared setting order. At most one bound and one shrink/gate comparator may advance.

| Setting | Category | Eligible | Worst-dataset max reduction | Worst-dataset ES99 reduction | zsRE efficacy changes | CounterFact efficacy changes |
| --- | --- | --- | --- | --- | --- | --- |
| clip:0.5 | bound | False | 9.46887 | 0.226093 | {'RET-ES': -0.9966666666666667, 'RET-GS': -0.9733333333333334, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -1.0, 'RET-GS': -0.7533333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.367879 | bound | True | 8.94477 | 0.161264 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': -0.008333333333333304, 'LS': 0.0, 'near_miss': 0.0} |
| clip:1 | bound | False | 8.97277 | 0.215177 | {'RET-ES': -0.9966666666666667, 'RET-GS': -0.9733333333333334, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -1.0, 'RET-GS': -0.7533333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.135335 | bound | True | 7.945 | 0.104222 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| clip:2 | bound | False | 8.25676 | 0.197449 | {'RET-ES': -0.9733333333333334, 'RET-GS': -0.9700000000000001, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -0.94, 'RET-GS': -0.7183333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| mixture:0.0183156 | bound | True | 5.94726 | 0.038736 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| clip:4 | bound | False | 6.45606 | 0.164901 | {'RET-ES': -0.6333333333333333, 'RET-GS': -0.6433333333333333, 'LS': 0.0, 'near_miss': 0.06999999999999995} | {'RET-ES': -0.32999999999999996, 'RET-GS': -0.33999999999999997, 'LS': 0.0, 'near_miss': 0.0} |
| mixture:0.000335463 | bound | True | 2.07833 | 0.00394897 | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': 0.0, 'LS': 0.0, 'near_miss': 0.0} |
| shrink:0.25 | comparator | False | 9.10658 | 0.227125 | {'RET-ES': -0.9733333333333334, 'RET-GS': -0.9600000000000001, 'LS': 0.0, 'near_miss': 0.13} | {'RET-ES': -0.9633333333333334, 'RET-GS': -0.7466666666666666, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| shrink:0.5 | comparator | False | 8.17325 | 0.209947 | {'RET-ES': -0.31000000000000005, 'RET-GS': -0.45000000000000007, 'LS': 0.0, 'near_miss': 0.06999999999999995} | {'RET-ES': -0.17333333333333334, 'RET-GS': -0.3983333333333333, 'LS': 0.020000000000000018, 'near_miss': 0.0} |
| shrink:0.75 | comparator | False | 4.77971 | 0.159779 | {'RET-ES': 0.0, 'RET-GS': -0.010000000000000009, 'LS': 0.0, 'near_miss': 0.0} | {'RET-ES': 0.0, 'RET-GS': -0.06499999999999995, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.4 | comparator | False | 0 | 0.114632 | {'RET-ES': 0.0, 'RET-GS': -0.036666666666666736, 'LS': 0.0, 'near_miss': 0.020000000000000018} | {'RET-ES': 0.0, 'RET-GS': -0.011666666666666603, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.3 | comparator | False | 2.85846 | 0.188785 | {'RET-ES': 0.0, 'RET-GS': -0.08333333333333337, 'LS': 0.0, 'near_miss': 0.020000000000000018} | {'RET-ES': -0.00666666666666671, 'RET-GS': -0.04166666666666663, 'LS': 0.0, 'near_miss': 0.0} |
| gate:0.2 | comparator | False | 3.68745 | 0.223714 | {'RET-ES': 0.0, 'RET-GS': -0.13, 'LS': 0.0, 'near_miss': 0.050000000000000044} | {'RET-ES': -0.1433333333333333, 'RET-GS': -0.10333333333333328, 'LS': 0.0, 'near_miss': 0.0} |



The selected bound is **mixture ρ = exp(−1)**, with 1−ρ ≈ 0.6321 multiplying the cap distribution. No shrink/gate comparator is eligible, so evaluation contains three arms rather than filling the missing slot with an ineligible comparator.

Every clip setting fails retention eligibility. Its symmetric log-ratio restriction limits increases as well as decreases relative to the base; after normalization, no token can gain more than 2b nats relative to that base. This is consistent with suppressing strong edited-answer corrections, although aggregate scores alone do not isolate every decoding cause. Mixture instead preserves a base-probability floor while permitting large increases for tokens the base considers unlikely. It does **not** generally guarantee unchanged greedy answers: the measured CounterFact RET-GS falls from 0.753333 to 0.745000 (−0.8333 percentage points), inside the registered tolerance. zsRE scores are unchanged.

The calibration mixture brings zsRE mean KL below 0.001, but CounterFact remains above that line. No κ or coupled-free-energy objective is used here. Without an eligible shrink/gate comparator, this experiment cannot establish superiority to an efficacy-matched weakening control.

Calibration cost: 19467.922 process seconds (5.408 h), including construction, wrapper scoring, efficacy and temporary endpoint teaching. Thirteen numerical settings share one pass; the three gates use separate passes. No repeated per-setting pass times are summed as extra work.

### Exposed sealed-stream evaluation

Realization 0, five paired orders, two datasets, restored original 300-edit memories. These are already-exposed populations. No result here enters parameter selection. All per-order values and differences remain visible; positions and orders are not independent realizations.

| Memory | Setting | ES | RET-ES | RET-GS | LS | near_miss | revision | Mean KL | Mean ΔNLL | ES99+ | Max ΔNLL |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre-o103 | v5 | 1 | 1 | 0.983333 | 1 | 0.83 | 1 | 0.00146107 | 0.00156859 | 0.162834 | 9.26227 |
| zsre-o103 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o103 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.83 | 1 | 0.000452492 | 0.000480151 | 0.0522019 | 0.999837 |
| zsre-o100 | v5 | 1 | 1 | 0.983333 | 1 | 0.76 | 1 | 0.00186062 | 0.00181293 | 0.195585 | 9.26227 |
| zsre-o100 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o100 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.76 | 1 | 0.000583378 | 0.00054405 | 0.0653418 | 0.999837 |
| counterfact-o102 | v5 | 1 | 1 | 0.748333 | 1 | 1 | 1 | 0.00690961 | 0.0068986 | 0.71135 | 15.3818 |
| counterfact-o102 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o102 | mixture:0.367879 | 1 | 1 | 0.741667 | 1 | 1 | 1 | 0.0019479 | 0.00195307 | 0.211755 | 1 |
| counterfact-o103 | v5 | 0.996667 | 0.996667 | 0.758333 | 1 | 1 | 1 | 0.00532 | 0.00547311 | 0.564284 | 11.7442 |
| counterfact-o103 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o103 | mixture:0.367879 | 0.996667 | 0.996667 | 0.748333 | 1 | 1 | 1 | 0.0014471 | 0.0014848 | 0.1609 | 0.999986 |
| zsre-o101 | v5 | 1 | 1 | 0.993333 | 1 | 0.8 | 1 | 0.00176972 | 0.00186703 | 0.195796 | 12.2931 |
| zsre-o101 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o101 | mixture:0.367879 | 1 | 1 | 0.993333 | 1 | 0.8 | 1 | 0.000580211 | 0.000601304 | 0.0667045 | 0.999992 |
| zsre-o102 | v5 | 1 | 1 | 0.983333 | 1 | 0.77 | 1 | 0.00186937 | 0.00186419 | 0.194865 | 8.30384 |
| zsre-o102 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o102 | mixture:0.367879 | 1 | 1 | 0.983333 | 1 | 0.77 | 1 | 0.000582556 | 0.000575304 | 0.0635293 | 0.999575 |
| counterfact-o104 | v5 | 1 | 1 | 0.795 | 0.98 | 1 | 1 | 0.00641211 | 0.00662269 | 0.690296 | 11.7442 |
| counterfact-o104 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o104 | mixture:0.367879 | 1 | 1 | 0.783333 | 0.98 | 1 | 1 | 0.00193711 | 0.00195718 | 0.216662 | 0.999986 |
| counterfact-o101 | v5 | 1 | 1 | 0.726667 | 1 | 1 | 1 | 0.00491337 | 0.0050381 | 0.51939 | 15.3818 |
| counterfact-o101 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o101 | mixture:0.367879 | 1 | 1 | 0.716667 | 1 | 1 | 1 | 0.00133934 | 0.00138617 | 0.149813 | 1 |
| zsre-o104 | v5 | 1 | 1 | 0.976667 | 1 | 0.78 | 1 | 0.00202264 | 0.00196767 | 0.212105 | 12.2931 |
| zsre-o104 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| zsre-o104 | mixture:0.367879 | 1 | 1 | 0.976667 | 1 | 0.78 | 1 | 0.000653194 | 0.000610924 | 0.0723994 | 0.999992 |
| counterfact-o100 | v5 | 1 | 1 | 0.806667 | 1 | 1 | 1 | 0.00417566 | 0.0043814 | 0.458686 | 11.7442 |
| counterfact-o100 | capoff | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o100 | mixture:0.367879 | 1 | 1 | 0.795 | 1 | 1 | 1 | 0.00126503 | 0.00132888 | 0.147613 | 0.999986 |



Paired differences, setting minus v5 (loss lower is better):

| Memory | Setting | ΔES | ΔRET-ES | ΔRET-GS | ΔLS | Δnear_miss | Δrevision | Δmean KL | Δmean NLL | ΔES99+ | Δmaximum |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| zsre-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o103 | capoff | -1 | -1 | -0.983333 | 0 | 0.17 | -1 | -0.00146107 | -0.00156859 | -0.162834 | -9.26227 |
| zsre-o103 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00100858 | -0.00108844 | -0.110632 | -8.26243 |
| zsre-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o100 | capoff | -1 | -1 | -0.983333 | 0 | 0.24 | -1 | -0.00186062 | -0.00181293 | -0.195585 | -9.26227 |
| zsre-o100 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00127724 | -0.00126888 | -0.130243 | -8.26243 |
| counterfact-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o102 | capoff | -1 | -1 | -0.748333 | 0 | 0 | -1 | -0.00690961 | -0.0068986 | -0.71135 | -15.3818 |
| counterfact-o102 | mixture:0.367879 | 0 | 0 | -0.00666667 | 0 | 0 | 0 | -0.00496172 | -0.00494554 | -0.499595 | -14.3818 |
| counterfact-o103 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o103 | capoff | -0.996667 | -0.996667 | -0.758333 | 0 | 0 | -1 | -0.00532 | -0.00547311 | -0.564284 | -11.7442 |
| counterfact-o103 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00387291 | -0.0039883 | -0.403384 | -10.7443 |
| zsre-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o101 | capoff | -1 | -1 | -0.993333 | 0 | 0.2 | -1 | -0.00176972 | -0.00186703 | -0.195796 | -12.2931 |
| zsre-o101 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00118951 | -0.00126573 | -0.129092 | -11.2931 |
| zsre-o102 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o102 | capoff | -1 | -1 | -0.983333 | 0 | 0.23 | -1 | -0.00186937 | -0.00186419 | -0.194865 | -8.30384 |
| zsre-o102 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00128681 | -0.00128888 | -0.131336 | -7.30426 |
| counterfact-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o104 | capoff | -1 | -1 | -0.795 | 0.02 | 0 | -1 | -0.00641211 | -0.00662269 | -0.690296 | -11.7442 |
| counterfact-o104 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.004475 | -0.00466551 | -0.473634 | -10.7443 |
| counterfact-o101 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o101 | capoff | -1 | -1 | -0.726667 | 0 | 0 | -1 | -0.00491337 | -0.0050381 | -0.51939 | -15.3818 |
| counterfact-o101 | mixture:0.367879 | 0 | 0 | -0.01 | 0 | 0 | 0 | -0.00357403 | -0.00365193 | -0.369578 | -14.3818 |
| zsre-o104 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| zsre-o104 | capoff | -1 | -1 | -0.976667 | 0 | 0.22 | -1 | -0.00202264 | -0.00196767 | -0.212105 | -12.2931 |
| zsre-o104 | mixture:0.367879 | 0 | 0 | 0 | 0 | 0 | 0 | -0.00136945 | -0.00135674 | -0.139705 | -11.2931 |
| counterfact-o100 | v5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| counterfact-o100 | capoff | -1 | -1 | -0.806667 | 0 | 0 | -1 | -0.00417566 | -0.0043814 | -0.458686 | -11.7442 |
| counterfact-o100 | mixture:0.367879 | 0 | 0 | -0.0116667 | 0 | 0 | 0 | -0.00291063 | -0.00305252 | -0.311073 | -10.7443 |



Predeclared usefulness requires smaller maximum and ES99+, with both retention scores within ±0.02, in every dataset/order. This is a conjunction across the declared cells, not an aggregate-average claim.

| Setting | Every coordinate passes |
| --- | --- |
| capoff | False |
| mixture:0.367879 | True |
| v5 | False |



Evaluation process time: 21083.167 seconds (5.856 h), separate from calibration.

### What the one-nat guarantee says

For the same fixed prefix h and target token y, let p₀ be the unchanged base distribution and p₁ the cap distribution. The selected mixture is q = ρp₀ + (1−ρ)p₁ with ρ = exp(−1). Since q(y|h) ≥ ρp₀(y|h),

    ΔNLL(y|h) = log[p₀(y|h) / q(y|h)] ≤ −log ρ = 1 nat.

This is a per-token likelihood-ratio bound relative to the specified base, at the same prefix. It is **not** a one-nat bound on total sequence loss, generated-text loss on different prefixes, semantic harm, or greedy-answer preservation. Along a shared teacher-forced sequence of N prefixes, the bounds sum to at most N nats, not one. The mixture also implies KL(p₀ || q) ≤ 1 nat, which is much weaker than the unchanged 0.001 mean-KL benchmark. No bound is asserted relative to another independently trained base.

Survival curves use P(ΔNLL > x), including zero and beneficial positions in the denominator. The one-nat ceiling is shown explicitly. Apparent concentration or a truncated observed tail does not prove a heavy-tail family. This query-time intervention tests a way of limiting extreme prediction loss in the active-inference testbed; it introduces neither PC acquisition nor autonomous policy inference.


Survival figure: `assets/presentation-materials/figures/aw_b/evaluation-survival.png` (PDF/SVG beside it). DEC-078: an intervention beside the κ pilot, not a recommended cap configuration.


## HT-17 — frequency, severity and finite-range shape (October 1)

The [HT-17 report](../additional_work/HT-17_report.md) supersedes the prototype tail appendix. Across 299 cells it separates frequency above .01 nat from mean severity conditional on exceeding it. Primary learned-v5 frequencies/severities are .1594%/1.630 nats on zsRE and .2984%/1.913 nats on CounterFact. Stable v0 has a more pronounced fitted zsRE tail, yet its maximum and ES99 order differently against v5; zero CF harm accompanies zero paraphrase retention.

Learned-v5 illustrative shape intervals include zero, with little held-out predictive gain over exponential. Stable-zsRE GPD gains .149–.594 nats per excess, with illustrative shape interval [.390,.779]. Random CF has 10/15 held-out support failures; all mixture fits are invalid. These are finite-range observations, not complexity classes or infinite-variance measurements. Conditional window intervals omit realization/seed uncertainty, and window independence remains unverified.

AW-B reduces conditional severity 1.619→.542 and 1.925→.581 nats, with almost unchanged harmful-change frequency. Its one-nat shared-prefix ceiling is analytic, independent of failed tail fits. The κ pilot deformed one surprisal; it did not implement Nelson’s calibrated entropy or coupled free energy. The active-inference policy loop remains proposed.

DEC-080 defers nine unrun Option R stable-v0 cells; the earlier ceiling-killed cell remains incomplete. Sixteen learned/random cells await resumption. DEC-081/081a adds CPU analysis and conservative presentation wording, not another GPU experiment. PC-reader replication remains partial (three BP seeds, one ePC seed); no three-seed rule comparison is yet available.
