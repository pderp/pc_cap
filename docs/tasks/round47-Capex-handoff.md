# Round 47 — Capex handoff

2026-09-26. All three assigned CPU lanes are complete. No GPU execution, frozen
`scripts/` or `src/pccap/` edits, staging or commit. Capstan's live queue and
operational records remain his work.

| Lane | Delivered | Record |
| --- | --- | --- |
| PRES-3 | Six new speaker drafts; ten SVG slide drafts total; readable retention plot; claim ledger/source bindings | [PRES-3](PRES-3.md) |
| PC-6 | Strict checkpoint restoration and registered-reader-compatible fixed-v5 harm adapter; exact real-checkpoint logits | [PC-6](PC-6.md) |
| HT-15 | 262-cell tail table, three realization means/ranges, maximum locations, and proposed presentation paragraph | [HT-15](HT-15.md) |

The current slide review export is
`/home/derp/cap/assets/presentation-materials/deck_v3/round47-reviewed/`.
Canonical speaker drafts are in `docs/presentation/deck_v3/`. Slides 9–10 and
the closing PC result stay pending; the talk remains centered on active
inference, predictive coding and heavy-tailed distributions. The 225-cell
comparator and 262-cell tail snapshots are separately labeled.

The PC adapter's ten real-development prefixes reproduce both cap and base
logits exactly; one is a non-null correction that changes predictions. Actual
error-credit acquisition/restore and PC-5 integration pass on the tiny solver.
That establishes implementation readiness, not full validation or GPU quality /
timing. Capstan owns the real supplemental integration after Monday 09:00.

The per-cell analysis shows why realization spread matters: learned-reader
ES99+ ranges are .254–.266 nats on zsRE, .480–.622 on CounterFact and .421–.731
on MQuAKE. Live C2's zsRE average is worse, but realization 0 reverses that ES99
ordering. Do not turn the pooled comparison into an every-realization claim.
S1_literal zsRE is incomplete (5/2/0 cells by realization); its full range is
unavailable. [Proposed paragraph](../presentation/HT-15-tail-spread-paragraph.md)
also identifies three small wording corrections in the owner page: finite
vocabulary does not bound NLL, different means are not equivalent, and zero loss
difference alone does not prove the cap never fired.

Capstan's next actions: merge that paragraph/wording, finish HT-14, reconcile
the planned halt, run the prepared comparator/HT-13 refresh, then build a new
HT-15 snapshot. Keep the shared eight-hour readout budget and October 9 17:00 ET
experimental cutoff. Commands and adapter integration are in the linked records.

Validation: **84 tests passed** in the general CPU `aw` suite (two slow tests
deselected); the new saved-checkpoint test then passed explicitly in the four-test
PC-6 module. Targeted presentation tests and lint pass. All 18 cell groups agree
with the existing pooled snapshot on coverage, signed means, maxima and fixed
exceedances. All export/source hashes match; 136 SVG text elements fit the
canvas. Visual review prompted simplification of the retention figure.

Evidence: `logs/additional_work/round47/{aw-tests.txt,pc6-verified-tests.txt,
final-validation.json,pres3-export-manifest.json,pres3-retention-manifest.json}`;
real-checkpoint evidence `results/additional_work/PC-6/devcheckpoint-verified.json`;
tail snapshot `logs/additional_work/round47/HT-15-final/`. Intermediate validation
and draft-render snapshots are historical, not alternative scientific results.
