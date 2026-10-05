# PRES-colleague-long — colleague presentation

- Status: done; owner Capex; requested by charlie on 2026-10-04.
- Scope: a separate 35–40 minute talk based on Capstan's October 4 short PDF,
  with first-principles explanations, completed experimental results, recorded
  examples, speaker notes and questions that help choose the final 15-minute talk.
- Inputs: `assets/presentation-materials/deck_v3/deck-pdf-20261004/`,
  `assets/support-information/`, completed Stage-4 and additional-work reports,
  presentation brief and abstract-to-testbed map.
- Ownership: only new `aw/colleague_deck*.py`,
  `docs/presentation/colleague_deck_20261004/`,
  `logs/presentation/colleague_deck_20261004/`, and
  `assets/presentation-materials/colleague_deck_20261004/`.
  Capstan's short deck, example generator, shared board and runtime code are untouched.
- Outputs: 30-page 16:9 PDF (25 main slides, 5 backups), standalone offline HTML
  presentation with notes and elapsed-time clock, 30-page speaker-notes PDF,
  eight data-derived figures in PNG/PDF/SVG, slide images and contact sheet.
  Entry point: `docs/presentation/colleague_deck_20261004/README.md`.
- Narrative: active inference, predictive coding and heavy-tailed distributions;
  Capstan's recorded success/failure/preservation examples; completed PC-reader
  and upper-layer results; proposed active audit policy. Selected examples remain
  illustrations, and the older 50M and current 124M experimental scopes stay distinct.
- Documentation: timed script and JSON content export, source/selection guide,
  colleague-feedback prompts and a 900-second conference compression proposal.
  Planned long-talk time 39:25, including 65 seconds of explicit audience pauses;
  open Q&A additional. Main script 4,252 words, maximum planned per-slide rate
  133.8 words/minute after removing its explicit pause. Timing awaits charlie's
  actual rehearsal; a 36:05 cut is documented.
- Verify command: CPU-only `../venv/bin/python -m aw.colleague_deck` with the
  reporting environment variables in the README; then Ruff on the two new modules,
  PDF text/bounding-box extraction, notes/HTML consistency and local-link checks.
- Verify output: PASS. Thirty PDF titles found, no replacement glyphs or words
  beyond page bounds, all 30 embedded browser slides and notes consistent,
  8 local links resolve, output hashes match. Twenty-two example-source identities
  verified; seven selected records (five items and two endpoint probes) independently
  matched to checkpoint records. Triplet means, 45 fidelity failures, 12 reader
  evaluations, 24 upper-layer evaluations and 10 mixture successes match sources.
  Builder checks horizontal and vertical text fit. Ruff and `git diff --check` pass.
  Records: `logs/presentation/colleague_deck_20261004/{build,validation,layout,plotted-values}.json`
  and `deck-extracted.txt`.
- Visual verification: all-page contact sheet; dense examples, frequency/severity,
  survival, PC mechanism and reader results at full size; revised backup pages.
  Corrected an axis crossing an undefined-severity label and an overlong source
  filename in a card. Final renders pass. Headless Chrome rendered the offline
  presentation and controls after the sandbox blocked its startup socket; the
  permitted outside-sandbox check succeeded. Navigation handlers were reviewed
  in source, not exercised by an automated interaction suite.
- Done-when: presentable long talk, usable speaker notes, concrete examples,
  current results and actionable colleague feedback are delivered.
- Cost: CPU rendering only; zero GPU seconds; no model calls, fits or experiments.
- No commit requested for this task.
- Deviations / unresolved / lead questions: none blocking. charlie should rehearse
  the timing and use colleague feedback to choose final conference content.
- Worktree handoff: only the two new `aw/colleague_deck*.py` modules and the three
  new repo documentation/log namespaces above belong to this task. Presentation
  exports are in the sibling assets tree. The pre-existing untracked
  `results/additional_work/PC12/` is unrelated and was not touched.
