# HT-1 — stored development distributions

The CPU-only audit covers 788 files, 1,346 separate outcome series and 45,152 shared-observation comparisons.
The 293 missing-data entries explicitly record empty endpoints or aggregate-only assays. No nonfinite/failed
row series was observed in this snapshot. Source hashes and all series are in audit.json; pair comparisons are
in paired.jsonl.gz. The source glob inventory is included so later files can be audited into a new directory.

The two saved 300-edit drift reports contain the same 16,256 position measurements from 128 windows. They are
not independent replications. For the historical v4 zsRE reader, positive-harm median is zero, p95 is
0.0000079414 nats, p99 0.0000130344, mean signed harm +0.0002331477, and ES95 0.0046736268.
The maximum is +3.7896351 nats at w125:p26. Exactly one position exceeds each of 0.01, 0.1 and 1 nat.
Worst-1% fractional mass carries 99.44899% of all positive harm; the single maximum carries about99.38%.
Positive-harm zero count is 10,142/16,256; exact signed-zero count4,095. Tiny floating-point changes remain
visible; no post-hoc epsilon has been imposed. Figures: mean_vs_tail.pdf and mean_vs_tail.svg.

Statistics use positive harm for quantiles/ES95/tail shares, with signed and positive means both reported.
ES95 uses exactly 5% empirical mass, including a fractional boundary observation; linear-interpolated
quantiles are stated separately. Maximum location and ties, exceedance numerators/denominators and zero atoms
are explicit. Negative changes are retained; nonfinite values would fail the series rather than be dropped.

Per-item retention, immediate acquisition, unseen firing/answer change, near-miss and revision outcomes remain
separate error fractions. Their threshold counts are not labelled nats. Stored learning NLL is separately labelled
new-answer target loss and cannot stand in for preservation harm. Old aggregate-only ordinary-text assays do not
support retroactive tail distributions. Window counts are unavailable for item-only endpoints, not invented.

Pair comparisons are exploratory right-minus-left on shared keys and report unmatched counts. Drift keys include
window-source hash, position and reference NLL. Item keys include item/case identity, dataset and prompt/source-row
hashes where stored; older retention rows permit only weaker item-ID matching. The series states this limitation.
Different checkpoint sizes, schedules and historical configurations are not randomized or matched training trials.
No iid intervals, power-law fits or unobserved catastrophic-risk bounds are claimed.

The final selected reader has not yet been audited through these complete development endpoints. Repeat the audit
before freeze on its saved rows; this historical profile does not satisfy that future gate.
