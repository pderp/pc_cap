# HT-15b — tails refreshed through the reconciled 270-cell halt

Capex, 2026-09-27. Assigned CPU lane complete; no model execution.

Re-ran the existing `aw.tail_cells` analysis against the receipt-filtered
`logs/R1/reports/comparators-270/` snapshot. The saved vectors cover 270 cells;
all 18 observed condition/dataset groups now have 15 cells (three realizations,
five orders each). No cell was excluded. The prior 262 cell records are
unchanged; the eight additions are all S1_literal zsRE. The omitted registered
conditions remain omitted, rather than becoming zero-effect rows.

Replaced `assets/presentation-materials/figures/tails/cell_tails.csv`, its JSON
companion and `tail_spread.md`, and updated `assets/presentation-materials/tails_v1.md`.
The repository copy and comparison evidence are in
`logs/additional_work/round48/HT-15b-270/`.

S1_literal zsRE now has mean per-cell positive-harm ES99 **0.179435633 nats**,
compared with 0.165132398 over the seven previously available cells. Its complete
realization means are **0.132983454, 0.213079580 and 0.192243865**; their descriptive
range is **0.132983454–0.213079580**. This change reflects added observations,
not a scoring change. The mean per-cell maximum is 25.323659360 nats; the pooled
maximum is 27.688297675 nats. These two summaries answer different questions.
Mean per-cell half-mass count is 19.133333 positions, with realization means
15.2, 19.4 and 22.8. The updated pooled table and wording distinguish frequency
and severity; the old claim that these conditions differ only in rare severity
would be too strong.

ES99 uses the existing fractional expected-shortfall helper with zeros retained.
The reference is each cap's own cap-off base; S1 base-continuation changes are
outside that contrast. The repeated 245,237 text positions and five stream
orders are not independent experimental replicates. Realization ranges are not
confidence intervals, and concentration does not identify a heavy-tail family.

Evidence: `changes-from-262.json` records every new coordinate and both S1
summaries; `page-update.json` records the page's before/after identity;
`verification.json` checks coverage, source identities and exported copies.
The claim ledger's HT13 row now names 270 cells, and HT15-spread gives the
per-cell spread beside the pooled presentation result.
