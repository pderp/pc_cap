# PRES-deck-v4-long-v1 — focused practice presentation

- Status: complete; agent Capex; direct request from charlie, 2026-10-05.
- Inputs: all five guidance files in `assets/presentation-materials/deck_v4/`,
  its CounterBench and MQuAKE PDFs, the October 4 colleague deck, saved support
  examples, completed Stage-4 and additional-work reports.
- Outputs: `assets/presentation-materials/deck_v4/long_deck_v1.md` and
  `long_deck_v1.pdf`; Markdown is the sole source of visible text, including
  chart labels and values. Supporting figure exports stay in that directory;
  builder and verification records stay in pc_cap.
- Scope: presentation editing and CPU rendering only. No experiments, model
  calls, GPU use, shared task-board edits, or changes to experimental code.
- Verify command: `../venv/bin/python -m aw.focused_long_deck`, Ruff on that
  module, `pdftotext -bbox`, `pdffonts`, `pdftoppm`, an independent
  markdown-it-py glyph comparison, and `git diff --check` in both trees.
- Verify output: PASS. 28 pages, 16:9, 3,334 visible words. Planned timing 37:20
  (not a measured rehearsal). Ten numerical/example tables checked against
  saved sources; both empirical survival curves reuse hash-verified vectors
  and saved exponential fits without refitting. Every PDF page matches its
  Markdown text, including labels/numbers/punctuation. The independent parser
  finds exactly the same 18,729 non-whitespace glyphs; no additions, omissions
  or replacement characters. No text collisions, overflow or out-of-page words.
  All fonts embedded and text searchable. All-page PDF contact sheet reviewed;
  detailed pages checked for examples, plots, dense results and proposed work.
  Eight quantitative slides have standalone PDF/SVG/PNG exports. Ruff and
  both diff checks pass.
- Done-when check: the five requested sections form a focused 35–40 minute practice
  talk; every PDF text element is editable in Markdown; no guidance prose is
  copied into slides as an instruction; sources and experimental limits remain clear.
- Cost: CPU only; zero GPU seconds.
- Deviations/unresolved/questions: none. CounterBench supplies conceptual
  background; it was not a benchmark run by this project. Our MQuAKE work used
  single-fact edits, not the paper's full multi-hop evaluation.
- Worktree: pre-existing support-field edits and `results/additional_work/PC12/`
  are outside this task. No commit requested.
- Task-owned pc_cap paths: `aw/focused_long_deck.py`,
  `docs/presentation/deck_v4_long_v1.md`, this record and
  `logs/presentation/deck_v4-long-v1/`. Task-owned assets paths: the two
  deliverables and `presentation-materials/deck_v4/long_deck_v1_assets/`.
  Original guidance/reference PDFs and previous decks were not edited.
