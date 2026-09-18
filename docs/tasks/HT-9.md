# HT-9 — presentation package v1

- Status: done; future confirmatory figures remain data-dependent.
- Agent: Codex, round 37, September 18, 2026.
- Inputs: submitted abstract and saved satellite schedule; counter-review §8; all four presentation records; claim ledger v5/v6-preview; final four-cell HT-6 report; selection audit/figure; HT-1b tails; independently audited κ and stress results; D.4 and plan v3; U03 memo.
- Outputs: canonical `docs/presentation/talk_outline_v1.md`, export `assets/presentation-materials/talk_outline_v1.md` outside the repository; new `scripts/ht9_presentation_figures.py`; three PDF/SVG/PNG figures and data/environment receipts under `logs/r1_round37/presentation-figures-v2/`; existing/new figure exports under `assets/presentation-materials/figures/ht9-v1/`; source/export hashes in `logs/r1_round37/HT9-evidence-manifest.json`.
- Verification: all 12 slides specify one-sentence claim, source/figure and qualifications; every κ claim carries DEC-054 framing; checked current numerical sources, rendered figures and visually inspected them. New plotter imports no JAX and reads only saved report JSON. Existing plotting environment reused; no installation or experiment.
- Done when: the lead can begin slides now, with available figures and a specific production backlog for conceptual layout and future confirmatory values.
- Cost: CPU rendering and reads; GPU seconds 0, model calls 0.
- Deviations: produced the three previously missing descriptive figures as well as the requested outline/backlog. The first rendering attempt exposed a report-key mismatch before writing a directory; corrected it. v1 plots are a layout preview; v2 is the reviewed export.
- Unresolved: actual October 9 completion/outcome inventory and final signed ledger v6, plus slide styling and final rehearsal. The saved schedule does not assign an individual duration, so 18 minutes is an editable outline assumption.
- Questions for lead: none needed to prepare the package.

The outline explicitly corrects stale presentation-record language: concentrated target-token harm is not proved power-law behaviour; near-zero target ΔNLL does not prove an unchanged distribution; zsRE v0 has nonzero drift and a 16.16-nat maximum despite passing mean benchmarks; observed schedule equality is not universal invariance; recovery beyond the observation horizon is unknown. The reduced D.4 scope is 285 + 45 and its omitted cells are not measured zeros. The κ pilot is null under its predeclared rule, and clip2 is a descriptive control with a CounterFact false fire. Historical experimental records were preserved.
