# PRES-4 — PC result slides and closing slot

Capex, 2026-09-27. Assigned CPU lane complete; experimental PC values pending.

New speaker drafts `docs/presentation/deck_v3/slide09-pc-v0-results.md` and
`slide10-fixed-v5-credit.md`, the closing slide 12, and renderable diagram specs
cover efficacy, harm and cost. They retain the three presentation themes:
active inference as the programme and proposed policy extension; predictive
coding as the paired acquisition-credit intervention; heavy-tailed distributions
as the question motivating distributional harm measurements.

`aw/presentation_pc.py` resolves the explicitly configured **future** paths in
`docs/presentation/deck_v3/pc-result-sources.json`. The exporter fills speaker
copies and SVGs from complete PC-3 behavior tables, PC-7 checkpoints and PC-5
harm summaries. Missing sources show PENDING; missing measurements in an
otherwise complete result show UNAVAILABLE. Smoke results, wrong populations,
incomplete pairs and changed inputs are refused. No automatic narrative chooses
superiority: displayed differences are SE-E minus SE-A, with the direction for
behavior and harm explained separately.

Slide 9 labels exposed historical S5, three realizations and five orders; slide
10 labels one exposed R1 realization per dataset, 300 edits, and unchanged
BP-trained base/reader. Its 100-edit results remain separately available in the
speaker notes. A fixed-v5 harm result must match the final 300-edit snapshot,
not the 100-edit checkpoint. Harm slots average the **difference of arm ES99s**;
they do not substitute the ES99 of positionwise differences. PC-v0 process time
includes startup; fixed-v5 finish time measures the stream engine. Harm-readout
time is separate. Neither number is labeled isolated solver time.

Existing drafts now use the 270-cell halt snapshot, corrected S1_literal tail
coverage and the available HT-14 abstract-to-testbed memo. Closing resource
context is 392.42 charged process-hours across the 270 main cells; PC costs
remain separate. October 9 at 17:00 ET remains the experimental cutoff and
October 15 the presentation date.

The reviewed export exists at
`assets/presentation-materials/deck_v3/round48-reviewed/`: twelve SVGs, twelve
speaker drafts, resolved specs and a source/export manifest. All PC experimental
slots are still PENDING. Earlier `round48/` is an intermediate preview. Preview
PNGs for slides 9, 10 and 12 were visually reviewed; all 172 text elements across
the twelve SVGs fit the canvas and their panels. The system Rsvg/cairo renderer
was used for previews; no Python dependency was installed. The repository copy
of the manifest and visual/layout checks is under `logs/additional_work/round48/`.

To refresh when Capstan's outputs arrive, first update the source register if he
uses different directories, then run (the output below is a **proposed new path**):

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.presentation_prepare --explanatory-only \
  --output ../assets/presentation-materials/deck_v3/round48-results
```

This export mode preserves the existing claim ledger. The older full ledger
generator is not the update path for PC results. Measured PC claims still need
the PC-8 report and the fixed-v5 report to establish their scope before final
author review. Recheck layout when measured values replace pending labels.

Validation includes adverse signed effects, complete three-realization tables,
four-cell fixed-v5 completion, distinct 100/300 effects, duplicate harm pairs,
smoke exclusion and absent-source handling. The complete ordinary `aw` CPU suite
passes: 96 tests, two slow fixtures deselected.
