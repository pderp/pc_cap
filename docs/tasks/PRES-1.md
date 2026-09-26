# PRES-1 — three-theme deck skeleton, figure pipeline and claim ledger

Status: done (preparation skeleton; experimental slots remain pending). Agent: Capex. Date: 2026-09-26.

Direction: charlie's September 26 instruction is recorded in `docs/presentation/presentation_brief_2026-09-26.md` and the active PRES-1 subsection of `docs/ongoing.md`. Active inference, predictive coding and heavy-tailed distributions are central throughout. Both local conference sources were located and ingested; no refresh was needed. The prior harm-first outline is historical, not a constraint on this direction.

Canonical outputs: `docs/presentation/deck_v3_outline.md` (12 modular slides), `docs/presentation/deck_v3_figure_pipeline.md`, `docs/talk_claim_ledger_v7.md` (20 rows). Export: `/home/derp/cap/assets/presentation-materials/deck_v3/`, containing outline, pipeline, ledger, two conceptual SVG diagrams and nine selected numerical/pending PNGs. Code: `aw/presentation_prepare.py`. Export/source hashes: deck `manifest.json`, mirrored in `logs/additional_work/round45/presentation-export.json`.

The outline opens with the active-inference programme, explains the implemented cap and PC mechanism, presents retention alongside empirical distributions/concentrated harm and the κ trade-off, gives separate main slides to both PC credit experiments, and returns to missing policy/audit mechanisms. Each slide names its source and report. Speaking duration is deliberately unassigned. Exact source populations distinguish development κ/tail/stress evidence from the completed R1 matrix and exposed-PC replication. Measured PC outcome rows remain empty; the real-checkpoint CPU result appears only as implementation readiness.

The figure pipeline names working commands, existing versus pending files, environments and the post-halt/PC-result update steps. No CPU-smoke figure is exported to the deck. Conceptual diagrams are explanations, not measurement graphs or blanket proofs. The κ slide retains DEC-054's required “not coupled free energy / not a coupled Markov blanket / not the one-κ conjecture” scope. The active-inference return is a constructive research question, not a claim that the current gate is an expected-free-energy planner.

Verification: source/export hashes and canonical/export copies agree; every figure named as existing is present. Numerical comparator and pending-PC plots were visually reviewed. This is an outline and figure pack, **not a rendered final slide deck**. No tests were added for this reversible document preparation.

Reproduce the export into a new directory:

```bash
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.presentation_prepare \
  --comparators logs/R1/reports/comparators-225/report.json \
  --output /home/derp/cap/assets/presentation-materials/deck_v3-REBUILD
```

Remaining after lane delivery: incorporate the reconciled 270-cell report, actual PC outcomes and paired harm; confirm speaking duration; produce final slides and rehearse. Experimental freeze remains October 9 at 17:00 ET. Cost: 0 GPU seconds. No queue operation, external message or commit.
