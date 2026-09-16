# HT-1b — CounterFact results arriving during round16

The original HT-1b snapshot remains unchanged. A second snapshot incorporates Claude's completed CounterFact v5 cell and new 300-record unseen endpoint: [audit](../../logs/heavy_tail/audit-v5-round16-supplement/audit.json), paired.jsonl.gz, v5_comparison.json, and [mean/tail figure](../../logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5.pdf). It contains 28 source files, 118 series, 252 shared-observation comparisons and 21 explicit missing-data records.

CounterFact full drift after 300 edits, on 128 windows / 16,256 positions: signed mean +0.006286152 nats, mean positive harm 0.006386133, median 0, p95 0.0000081657, p99 0.0000144407, ES95 0.127704346, maximum 7.314825579 at w17:p117. Counts above .01/.1/1 nat are 55/52/29; worst1% contains 99.97911% of positive harm. There are 4085 signed zeros, 10105 positive-part zeros and 6020 negative positions.

The figure's generator verifies exact equality of ordered source/position IDs and both base reference NLL vectors between v4 zsRE, v5 zsRE and v5 CounterFact. All share the text/reference population; edit histories and readers differ, so this remains descriptive and does not isolate a training or dataset treatment. Full/incremental zsRE duplicate observations count once.

The new full CounterFact mean is below .01 nat on this specific population, whereas its earlier32-window mean was .013661958. Different history/population/cadence means one does not invalidate the other. Neither mean bounds local maximum harm or closes the final all-condition drift gate.

CounterFact's new300-record standalone unseen assay gives1/100 false fires and1/100 answer changes, between historical100-record0/100 and1000-record1/100. Complete-answer preservation is .70, with29 incomplete answer pairs. Preserve the endpoint's denominator definitions and audit shared probe IDs before drawing an occupancy conclusion. MQuAKE300/1000 logs had no corresponding completed row reports in this snapshot; do not infer results from absent reports.

Reproduction of the supplement: import scripts.ht1b_v5_audit, append the two checkpoint paths for R1_learned_ff-counterfact-development-source-bc285b69b70dff8514a4 to its in-memory PATTERNS, and call run with a new logs/heavy_tail output directory. Existing files are never edited. The full pattern inventory and all source hashes are embedded in audit.json. scripts/ht1b_plot_v5.py produces the plotted snapshot and refuses to replace figures.
