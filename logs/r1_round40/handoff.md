# Round40 handoff — September18, 2026

**HT-4g, HT-10b and X21 complete.** New files only; no existing tracked edits, staging, commits, GPU use or new experiments.

- **Ledger content:** [40-row v6 document](../../docs/talk_claim_ledger_v6_content.md), including six additions/eight full-validation numeric rows, eight updated corrected-profile rows, two explicit supersessions and four reviewed old/new source bindings. One additional changed old-plan binding is retained only under the superseded cost claim. Signed cost is the sole pending field.
- **Deck:** [PDF](/home/derp/cap/assets/presentation-materials/deck_v2/current-research-deck.pdf), [canonical HTML](../../docs/presentation/deck_v2/index.html). All12 pages reviewed;50 source/evidence bindings verify. Four wording fixes applied by Claude are retained. Every slide binds prepared v6 rows; signed-cost publication remains explicitly pending. Both κ qualifications and prospective slides10/11 pass.
- **X21:** [18-obligation/six-figure crosswalk](x21-review.md), [eight concrete edit requests](../../docs/tasks/R1-X21-edit-requests.md). Key finding: the driver records composition, but the installed analysis drops it; reproduced synthetically. Formatter omissions include secondary historical-v2 paired comparisons, additional tail fields and the joint cap flag. Accounting/resource integration, narrative-source binding and precise missingness language also need follow-up.
- **Validation:** eight focused tests pass in4.16s; Ruff passes. Exact protocol prefix rechecked at17:50UTC: only step1 complete,1845 candidate bindings valid. No signed step2 cost receipt exists.

Next safe lanes: group report-layer G1/G2/G3/G5/G8 into one tested update; separately assign G4 accounting integration and G6 additive composition reporting; G7 depends on verified resource measurements/ceilings. No bound-source edit was applied by X21.

After real step2, publish using **`python -m scripts.ht4g_ledger_content publish --content logs/r1_round40/talk_evidence_v6_content.json --cost-receipt docs/tasks/R1-58g-operator_v8/02-cost-admit.receipt.json`** under the main CPU venv/environment. The older HT4f standalone generator omits the expanded content; the new additive publisher preserves all prepared rows and requires the exact completed cost request. Full X20 still waits for step8. These ledger operations do not authorize draw/seal/freeze/launch.

Mirror completion from `docs/tasks/R1-round40-completion.json` when safe. Task details: `docs/tasks/HT-4g.md`, `HT-10b.md`, `R1-X21.md`. The PDF and page-review image resources live under assets; code, reports, tests and canonical documentation are in pc_cap.
