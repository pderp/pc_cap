# PRES-slide-24-lessons

- Status: done, 2026-10-06.
- Agent: Capex.
- Inputs: charlie's latest explicit request for slide 24; page 24 of `assets/presentation-materials/deck_v4/long_deck_v1.pdf` and its Markdown source; Stage-4, completed AW-L, PC matched-control, AW-B, HT-17 and historical κ-pilot reports/data; implementation of probability mixtures, acquisition budgets and corrected κ losses; coupled-objective and post-conference proposals.
- Outputs: `assets/support-information/slide-24-experimental-lessons-and-open-questions.md` (relative to `/home/derp/cap`); `logs/presentation/slide-24-lessons-20261006/verification.json`; this record. Only these three files were added for this request.
- Explanation: 4,255 words, starting with frozen-base predictions, cap memory, reader training, individual acquisition and evaluation. Expands all four cards, distinguishes the experiments and populations, derives the probability-floor guarantee, explains actual versus offered compute, contrasts bounded answer loss with bounded prediction harm, and describes what the κ pilot does and does not establish about coupled entropy and active inference. Includes actual result tables and a spoken version.
- Verification: inline standard-library Python checked final Stage-4 means, all 12 AW-L write comparisons, upper-read CounterFact pairs, all six offered/used operation fractions, all ten AW-B memory comparisons and fidelity outcomes, all κ-pilot aggregates and success-rule outcomes, illustrative bound arithmetic, source hashes and 22 local links. `pdftotext -f 24 -l 24` confirmed the target page's title and four cards. Formatting checked with Git.
- Verification output: passed. Numerical comparisons agree with the saved sources; the source and document SHA-256 values are in the verification JSON. HT-17 conditional-severity numbers were checked against its interpretation report; this task does not rerun raw tail fitting or experimental inference.
- Cost: CPU text/metadata analysis only; GPU seconds 0; model calls 0.
- Scope: explanatory document in the requested support-information directory, matching the slide-10 and slide-12 supplements. Deck, experiments and task board unchanged. The latest request explicitly targets slide 24 despite an earlier message naming slide 23.
- Commit scope: this supplement in the assets repository and these two supporting records in pc_cap. Pre-existing changes, including Capstan's project-review edit, are excluded.
- Unresolved: none.
