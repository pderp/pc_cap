# HT-11 — deck-v1 claim review

Keep the qualified development narrative. Apply four wording refinements and add explicit current evidence rows after the session; do not certify v5 as a complete ledger for deck v1.

Reviewed all 12 slides and 128 title/label/point/footnote/notes-paragraph fields. Verified 54 deck-build bindings. No existing presentation or ledger file changed.

## Requested wording refinements

### HT11-W1 — slide 3 (points/3)

Current: Unseen gate acceptance: 10/100

Replacement: **zsRE unseen gate acceptance: 10/100**

The count is zsRE-specific, not a three-dataset macro.

### HT11-W2 — slide 5 (speaker_notes)

Current: The fixed first 128 windows are not an iid sample.

Replacement: **Full validation covers 1,931 complete 128-token windows (245,237 next-token positions), with context reset per window. The earlier 128-window prefix is a dependent subset, not an iid sample.**

Distinguish the full validation population on this slide from the historical sampled-prefix assay.

### HT11-W3 — slide 8 (points/4)

Current: Clip2 keeps retention; fails separation and adds a CounterFact false fire

Replacement: **Clip2 meets the retention floor; fails separation and adds a CounterFact false fire**

Clip2 mean .7789 is lower than ordinary .7961, although it meets the .7761 floor.

### HT11-W4 — slide 9 (points/0)

Current: All 20 old exact answers remain correct

Replacement: **Each tested dataset retains 20/20 old exact answers at observed checkpoints**

State the measured population and time scope instead of an unrestricted retention claim.

## Evidence lineage gaps

v5 predates HT6 complete-validation results, DEC-064, D.4 scope and execution-plan-v3 amounts. Existing `DEC060-scale` and `COST-matrix` rows are superseded; they cannot substantiate the current numbers. The numerical sources themselves support the deck. The proposed additions JSON supplies direct source bindings, without pretending these rows have already been adopted. Selection uncertainty and programme/meeting metadata also receive explicit proposed rows. The later final v6 generator inherits v5 and adds SCOPE/COST; HT6 and DEC-064 still need explicit ledger entries.

Historical row evidence is checked separately: each review row records old versus current SHA values. A changed implementation file does not rewrite the original ledger; stable audit reports plus current direct sources remain distinguishable. No missing or stale binding is silently labelled unchanged.

## Slide-by-slide assessment

| Slide | Assessment | Ledger IDs |
|---|---|---|
| 1 | Programme and meeting metadata, with implemented claims separated from the broader submitted abstract. No CFE implementation claim. | A1, A2, A3, N1, PROPOSED-programme |
| 2 | Parameter arithmetic 1,640,964 + 1,707,264 = 3,348,228; 2.7002% of the stated 124M. Record state is additional. Interfaces remain analogies. | A1, A2, A3 |
| 3 | 42/15, selected-seed retention and Wilson interval agree with the audit. The interval is fixed-candidate descriptive and not selection-adjusted. Add zsRE to the unseen-query point. | O2, PROPOSED-selection-uncertainty |
| 4 | Values reproduce the 16,256-position historical assay. exp(8)=2980.96 justifies approximately 3,000. Positive harm and signed mean differ; no power-law inference. | TAIL-zsre, TAIL-counterfact |
| 5 | The four HT6 cells and both references support the numbers and DEC-064 interpretation. Ledger v5 predates this population, so a new ledger row is needed; clarify the 1,931/128-window distinction in notes. | PROPOSED-HT6-full-validation, PROPOSED-DEC064 |
| 6 | Chronology is supported as retrospective methodological learning; causal attribution to individual repairs is explicitly excluded. Chain-M invalid locality is not used. | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation |
| 7 | Bounded answer surprisal, zero limit, controls, seed count and checkpoint averaging agree with the registered pilot and repaired objective review. Neither all gradients nor the entire objective is bounded. | A4, K-kappa02, K-kappa05, K-clip2 |
| 8 | Both kappa arms fail the predeclared rule; Clip2 meets the retention floor but is below ordinary mean retention and fails the full rule. Replace keeps retention with meets the floor. | K-kappa02, K-kappa05, K-clip2 |
| 9 | 20/20 and edit-100 probability harm agree with the one-seed/two-schedule audit. Qualify the old-answer point by tested datasets and observed checkpoints. No permanent harm or order-invariance claim. | STRESS-zsre, STRESS-counterfact, STRESS-mquake |
| 10 | Current D4 supports 285+45 and 75 omissions; v5 DEC060-scale has been superseded. Existing U12-14 and zsRE baseline qualifications apply. Prospective, no confirmatory outcome. | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope |
| 11 | Plan v3 supports scenario arithmetic, not measured progress or a signed cost admission. Older COST-matrix amounts are superseded. Keep process and elapsed hours distinct and the October9 stop. | CONCURRENCY, PROPOSED-cost-v3 |
| 12 | A proposed discriminating comparison, not an experimental conclusion about coupled free energy. Current null and descriptive improvements neither confirm nor refute the broader programme. | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme |

## Required framing

Both κ slides contain the complete DEC-054 sentence visibly, not only in notes. Slide10 explicitly says planned/no confirmatory results; slide11 says planning scenarios/not measured progress. No κ gain, power law, universal preservation, permanent stress harm, or 1,000-record MQuAKE conclusion is justified or asserted with the present qualifications.

## Claim-by-claim trace

Each point and notes paragraph is retained verbatim in `review.json`, with ledger row index, evidence bindings, source lineage, qualification assessment and any edit-request ID. The table below provides a readable index; notes evidence tables are kept intact as a single paragraph.

| Claim / deck field | Assessment | Ledger | Evidence |
|---|---|---|
| S01:title | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:label | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:points/0 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:points/1 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:points/2 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:foot | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:submitted_title | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S01:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | A1, A2, A3, N1, PROPOSED-programme | docs/heavy_tail_counter_review.md; /home/derp/cap/errata/presentation_details/Active_Inference_in_the_Extremes_Abstract_charlie_derr.pdf; /home/derp/cap/errata/presentation_details/sattellite-schedule |
| S02:title | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:label | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:points/0 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:points/1 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:points/2 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:points/3 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:foot | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:speaker_notes/paragraph/0 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:speaker_notes/paragraph/1 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S02:speaker_notes/paragraph/2 | supported_with_displayed_qualifications  | A1, A2, A3 | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md; src/pccap/revision_v1/learner.py; src/pccap/revision_v1/reader.py; src/pccap/revision_v1/adapt.py; src/pccap/revision_v1/memory.py |
| S03:title | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:label | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:points/0 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:points/1 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:points/2 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:points/3 | wording_refinement_requested HT11-W1 | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:points/4 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:foot | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S03:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | O2, PROPOSED-selection-uncertainty | logs/r1_round16/selection_audit.json; logs/review_r1_selection.md |
| S04:title | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:label | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:points/0 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:points/1 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:points/2 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:points/3 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:points/4 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:foot | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:speaker_notes/paragraph/0 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:speaker_notes/paragraph/1 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:speaker_notes/paragraph/2 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S04:speaker_notes/paragraph/3 | supported_with_displayed_qualifications  | TAIL-zsre, TAIL-counterfact | logs/heavy_tail/audit-v5-round16-supplement/audit.json |
| S05:title | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:label | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:points/0 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:points/1 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:points/2 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:points/3 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:points/4 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:foot | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S05:speaker_notes/paragraph/3 | wording_refinement_requested HT11-W2 | PROPOSED-HT6-full-validation, PROPOSED-DEC064 | logs/r1_round35/ht6-final/report.json; docs/R1_stage4_protocol_v5_2_D_4.md |
| S06:title | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:label | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:points/0 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:points/1 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:points/2 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:foot | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S06:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | A2, O2, TAIL-zsre, PROPOSED-HT6-full-validation | docs/R1_stage2_notes.md; logs/review_r1_selection.md; logs/heavy_tail/audit-v5-round16-supplement/audit.json; logs/r1_round35/ht6-final/report.json |
| S07:title | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:label | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:points/0 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:points/1 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:points/2 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:points/3 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:points/4 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:foot | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:speaker_notes/paragraph/0 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:speaker_notes/paragraph/1 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S07:speaker_notes/paragraph/2 | supported_with_displayed_qualifications  | A4, K-kappa02, K-kappa05, K-clip2 | manifests/revision_v1/kappa_pilot_v3.json; logs/heavy_tail/HT-3b-objective-review.json; logs/r1_round22/ht3e-independent-review-v2.json |
| S08:title | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:label | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:points/0 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:points/1 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:points/2 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:points/3 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:points/4 | wording_refinement_requested HT11-W3 | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:foot | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:speaker_notes/paragraph/0 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:speaker_notes/paragraph/1 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S08:speaker_notes/paragraph/2 | supported_with_displayed_qualifications  | K-kappa02, K-kappa05, K-clip2 | logs/r1_round22/ht3e-independent-review-v2.json; logs/r1_round18/ht3d-pilot-final-aliases.json |
| S09:title | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:label | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:points/0 | wording_refinement_requested HT11-W4 | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:points/1 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:points/2 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:points/3 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:points/4 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:foot | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:speaker_notes/paragraph/0 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:speaker_notes/paragraph/1 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S09:speaker_notes/paragraph/2 | supported_with_displayed_qualifications  | STRESS-zsre, STRESS-counterfact, STRESS-mquake | logs/r1_round22/ht3e-independent-review-v2.json; manifests/revision_v1/ht_development_panel_v1.json |
| S10:title | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:label | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:points/0 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:points/1 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:points/2 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:points/3 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:points/4 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:foot | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S10:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | U12-14, ZSRE-empty-baseline, PROPOSED-D4-scope | manifests/revision_v1/run_matrix_v5_2_D_4.json; docs/R1_stage4_protocol_v5_2_D_4.md; docs/R1_U03_interpretation_memo.md; logs/r1_round25/r1-x15-independent.json |
| S11:title | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:label | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:points/0 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:points/1 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:points/2 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:points/3 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:points/4 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:foot | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S11:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | CONCURRENCY, PROPOSED-cost-v3 | docs/R1_execution_plan_v3.md; docs/tasks/R1-cost-admission-receipt-v4.json; docs/heavy_tail_suggested_slight_pivot.md |
| S12:title | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:label | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:points/0 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:points/1 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:points/2 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:foot | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:speaker_notes/paragraph/0 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:speaker_notes/paragraph/1 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |
| S12:speaker_notes/paragraph/2 | supported_directly_ledger_addition_needed  | A3, A4, K-kappa02, K-kappa05, K-clip2, TAIL-zsre, PROPOSED-programme | docs/heavy_tail_counter_review.md; logs/r1_round22/ht3e-independent-review-v2.json |

## Applying later

Edit requests only during the signing session. After the session, apply W1/W3/W4 to the deck source CONTENT and W2 to the source outline notes, then generate a new versioned deck/export set so the build hashes remain coherent. Do not hand-edit only the PDF or generated slides JSON. Publish current ledger rows through a versioned ledger update and bind the new deck to that ledger. Retain this v1 snapshot for provenance. Update optional-extension/cost-signature wording only from exact operator receipts.
