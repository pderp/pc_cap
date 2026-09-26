# PRES-2 — explanatory slides with speaker text

Capex, 2026-09-26. **Drafts complete for charlie's review; not final slides.**
Coordination names: this Codex agent is Capex; the Claude agent is Capstan.

Four source files under `docs/presentation/deck_v3/`:

- [Slide 2](../presentation/deck_v3/slide02-active-inference-testbed.md): active
  inference's belief/action/information programme and the implemented testbed.
- [Slide 3](../presentation/deck_v3/slide03-predictive-coding-credit.md): corrected
  energy, eight-step credit, SD-24 and paired efficacy/harm/cost in one diagram.
- [Slide 6](../presentation/deck_v3/slide06-beyond-the-mean.md): empirical survival,
  concentration, the distinction between a percentile and ES99, and what the
  observations do and do not establish about heavy tails.
- [Slide 11](../presentation/deck_v3/slide11-return-to-active-inference.md): how
  preferences, uncertainty and information-seeking audits would extend the
  testbed; constructive future questions, visibly proposed.

Each has on-screen text, full speaker paragraphs with claim IDs, diagram notes
and source/qualification notes. `diagram-specs.json` is the renderable source.
Seven additional claim rows are in `claim-additions.json` and the canonical v7
ledger; previous measured rows were preserved. The outline and figure pipeline
now point to these drafts and HT-13 for slide 6. No PC experimental outcome has
been invented or filled with a CPU smoke value.

Export via:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  ../venv/bin/python -m aw.presentation_prepare --explanatory-only \
  --output /home/derp/cap/assets/presentation-materials/deck_v3/NEW_DRAFT_EXPORT
```

The actual export is `assets/presentation-materials/deck_v3/round46-drafts-v3/`
(relative to `/home/derp/cap`): four SVGs, speaker files, and source/export hashes.
This mode does not regenerate or overwrite measured claim rows. Slide 6 retains
a visible HT-13 figure slot while Capstan's ES99/title correction is pending;
re-export afterward to embed the actual survival figure. Its current speaker
example uses the valid learned-MQuAKE exceedance / maximum / concentration data,
not the defective ES99 column. Repeated cell-position observations are labelled.

Capstan's assigned HT-14 map was not present at drafting; slides 2 and 11 name
that pending source explicitly rather than supplying a nonexistent file link.
Review those slides against it when delivered. The coupled free energy, two
κ-porous blankets, one-κ conjecture and autonomous policy choice stay proposed.
The κ pilot includes DEC-054's required qualification and its adverse decision
result. October 9 experimental completion and October 15 presentation remain
separate; no individual speaking duration has been assumed.

Checks: every paragraph/diagram claim ID resolves in the ledger; all four SVGs
parse and their rendered-font text widths fit the canvas. Two focused tests and
the broader 74-test CPU suite pass; Ruff passes. See
`logs/additional_work/round46/final-artifact-check.json` and `presentation-export-v3.json`.
No new GPU work or conference-web refresh was needed.
