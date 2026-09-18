# HT-10b — deck v2 bound to prepared ledger v6

Status: **done**, Codex, round40, September18, 2026. Versioned new outputs; no v1 overwrite or changes to existing presentation sources.

- [Deck v2 PDF](/home/derp/cap/assets/presentation-materials/deck_v2/current-research-deck.pdf): 12 pages, 960×540points (16:9).
- [Canonical HTML](../presentation/deck_v2/index.html), [slides Markdown](../presentation/deck_v2/slides.md), [full speaker notes](../presentation/deck_v2/speaker-notes.md), [build manifest](../presentation/deck_v2/build-manifest.json).
- Portable HTML/Markdown/JSON/notes and PDF are under `assets/presentation-materials/deck_v2/`. Rendered pages/contact sheets are in its `page-review/` directory.
- [Page-review receipt](../../logs/r1_round40/deck-page-review.json), [build log](../../logs/r1_round40/ht10b-build-v2.txt), [tests](../../logs/r1_round40/tests-final.txt).

The four HT11 wording edits applied by Claude are present: explicit zsRE unseen10/100; distinct1,931-window full assay versus128-window prefix in notes; Clip2 “meets the retention floor”; old-answer retention qualified by tested dataset/observed checkpoints. Every slide carries ledger row IDs, JSON pointers, statement hashes and evidence bindings in its canonical data/notes. Superseded v5 scope/cost rows cannot be used as current evidence.

The deck binds **prepared v6 content**, with signed cost explicitly pending. It does not falsely bind a published signed-cost ledger. Slides10/11 remain prospective. Both κ slides show the complete DEC054 wording on the page; detailed scientific qualifications and v6 evidence links remain in HTML/Markdown notes and PDF annotations.

All12 pages were visually inspected in three contact sheets, with slide9 additionally checked at full resolution. No clipped text, figure/footnote overlap or missing qualifications observed. Text extraction verifies page count, the changed visible bullets, both complete κ qualifications and prospective labels. Current source/export hashes all verify.

## Reproduction and provenance

The new `scripts/ht10b_deck_v2.py` runs in the main venv and invokes `scripts/ht10b_render_pdf.py` in the pre-existing plotting environment for PDF export. The plotting environment does not contain the model package; the first attempted single-environment import failed before creating output. The corrected split keeps evidence/receipt validation in the main venv and rendering in the plotting environment; no dependencies installed.

Run CPU `python -m scripts.ht10b_deck_v2 --canonical docs/presentation/NEW_VERSION --export /home/derp/cap/assets/presentation-materials/NEW_VERSION`, with `MPLCONFIGDIR` under assets and `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1`. Both directories must be new. The producer verifies that CONTENT and outline changes are exactly the reviewed HT11 corrections and checks all inherited figure evidence. It reuses the existing layout renderer without modifying it.

| Field | Record |
|---|---|
| Inputs | Current corrected CONTENT/outline; v1 snapshot; HT9 figure bindings; v6 content; HT11 claim mapping |
| Outputs | Two new producer/render scripts; deck_v2 canonical documents and assets; page-review metadata |
| Verification | Shared eight-test module passes; all12 pages reviewed; extracted text and source/export bindings pass; Ruff passes |
| Done-when | Corrected, ledger-bound PDF/HTML/notes and page review; satisfied |
| Cost | GPU0s; no experiments |
| Unresolved | Real signed-cost and October9 actual-results/status refresh require later versioned presentation snapshots |
| Questions | None |
