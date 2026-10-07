# Focused colleague practice deck — 6 October 2026

charlie requested a new long deck from the five guidance files in
`assets/presentation-materials/deck_v4/`, with every visible PDF word also in an
editable Markdown file. The two deliverables are:

- `assets/presentation-materials/deck_v4/long_deck_v1.md`
- `assets/presentation-materials/deck_v4/long_deck_v1.pdf`

The Markdown is the sole source of visible text, including chart labels,
numbers, equations, sources and slide numbers. No speaker script or hidden
additional narrative is appended to the PDF. The layout comments are not
printed. Normal Markdown paragraphs, headings and tables remain editable.

## Structure and timing

The 28 slides follow charlie's requested five sections:

1. Slides 1–2: the original question about selective learning on a frozen base.
2. Slide 3: brief definitions of active inference, predictive coding and heavy
   tails, and the current degree of integration.
3. Slides 4–10: cap operation, source targets, two recorded examples,
   paraphrases, preservation, the supplied papers and experimental design.
4. Slides 11–24: retention, fidelity, harm distributions, probability mixture,
   acquisition credit, reader-training efficacy/cost, upper layers and lessons.
5. Slides 25–28: testable blanket properties, a specified coupled objective,
   paired experiments and a future active-inference audit policy.

The per-slide allocations total 2,240 seconds (37:20). This is a planning
allocation, not a measured rehearsal duration. Reading every source footer is
unnecessary. Open discussion is additional.

The supplied CounterBench paper is used as conceptual background. The project
did not run CounterBench, and CounterBench is distinct from CounterFact. The
MQuAKE paper concerns multi-hop consequences; our reported MQuAKE work uses
single-fact edits. The deck explicitly distinguishes these scopes. The examples
are Sporting Canamy and James Howell; they are illustrations, not a sampled
estimate of overall success.

## Editing and rebuilding

From `pc_cap`:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
../venv/bin/python -m aw.focused_long_deck
```

This reads the Markdown and saved results, then regenerates only this edition's
PDF, preview images, standalone chart exports and build records. It uses the
project interpreter and already installed reporting packages. It does not
import a model, execute JAX/PyTorch, use the GPU, fit distributions or download
anything. Chart content uses completed numerical records and saved tail fits.

Keep the slide-separator lines (`---`) and HTML layout comments in place.
`###` headings define cards. The `<!-- body -->` comment ends a card group and
returns to full-width prose. Table values drive the bar graphics. The survival
page's bullet lists hold every axis and curve label, so labels are editable too.
Scientific numbers are checked against saved reports; changing them without a
corresponding source change deliberately causes a build error. If prose grows
too large for a slide, the renderer reports its overflow instead of clipping it
silently.

Generated visual resources are under
`assets/presentation-materials/deck_v4/long_deck_v1_assets/`:
all-page previews, a contact sheet, and standalone PDF/SVG/PNG exports of eight
quantitative slides. All visible text remains in the Markdown even where it
appears inside a chart. The original guidance files, reference papers, previous
decks and experimental outputs are not altered.

## Verification

The builder checks plotted numbers and example outputs against the completed
records, checks every text box and text-box intersection, and compares the
extracted PDF words/numbers with the Markdown page by page. The comparison
ignores whitespace and layout order, preserves punctuation and Unicode text,
and detects missing/added/repeated tokens. An independent glyph-count check
and visual inspection complement that comparison.

Build provenance and validation are in
`logs/presentation/deck_v4-long-v1/`. Text extracted from the two supplied local
papers is retained there for reference; no external material is presented as a
project result. The task record is `docs/tasks/PRES-deck-v4-long-v1.md`.

All work is uncommitted until charlie requests a commit.
