# PRES-slide-12-fidelity

- Status: done, 2026-10-06.
- Agent: Capex.
- Inputs: charlie's direct request; page 12 of `assets/presentation-materials/deck_v4/long_deck_v1.pdf` and its Markdown source; Stage-4 reports/analysis/summary; HT-17 complete snapshot; full-validation implementation; WikiText-103 inventory; selected run's bound saved loss array and tokenizer.
- Outputs: `assets/support-information/slide-12-probabilities-fidelity-and-rare-harm.md` (relative to `/home/derp/cap`); `logs/presentation/slide-12-fidelity-20261006/verification.json`; this record. Only these three files were added for this request.
- Verify command: inline Python/NumPy/tokenizers checks of saved arrays and identities, reported metrics, example arithmetic, local links and `pdftotext -f 12 -l 12`; `git diff --check` in both repositories.
- Verify output: 16 links resolve; 45 learned cells fail mean KL and pass mean signed Δ; all three dataset KL ranges match the report; selected zsRE r0/order-100 vector hash and shape match; all counts, loss/probability conversions, maximum location and token identity agree with saved sources. Hypothetical three-token example is labelled illustrative and checked independently. Details and source hashes are in the verification JSON.
- Done-when check: explanation begins with tokens/probabilities and frozen-base activation corrections, defines identical-prefix replay, both measurements and their units, derives the position/cell counts, distinguishes all three relevant thresholds, explains means/tails, integrity versus scientific performance and limits on interpretation, and provides a spoken summary.
- Cost: CPU text/metadata/saved-array analysis only; GPU seconds 0; model calls 0. No fresh experiment, model rerun or tail fitting.
- Deviations: explanatory document placed outside `pc_cap` in the requested support-information directory, matching the prior slide-10 supplement. No task-board row invented for this direct presentation request.
- Unresolved: none. Pre-existing changes, including Capstan's project-review edit, were left untouched. Deck and experiment files unchanged. No commit performed.
- Questions for lead: none.
