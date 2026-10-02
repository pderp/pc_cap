# DOC-2 — October 2 reviewer entry point

Status: done. Agent: Capex. October 2, 2026, Round 61. CPU only; no commit.

Inputs: Capstan's `docs/friday-10.02-review/UPDATE-2026-10-02.md`, completed
seed-1 evaluation receipts, refreshed PC-reader/HT-17 reports and the unchanged
DEC-080 Option R queue. The update itself is byte-identical to HEAD.

Outputs: `assets/presentation-materials/review-data/CURRENT.md` lists
**“2 October update: read first”** as its first link. The two repository reviewer
summaries (`docs/presentation/review-results.md` and `final-experiments.md`) link
the update and now reflect 10/12 reader evaluations, two paired seeds, and the
301-cell HT-17 refresh. Their reviewer-folder exports are regenerated through
`aw.reviewer_folder`; its manifest now also hashes linked navigation documents
and every file in the folder.

Verification: `PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.reviewer_folder
--output logs/additional_work/DOC-2/round61-delivered` checked 26 local links and
exact round-trip content equality after link rebasing. All recorded folder and
linked-document hashes were rechecked. This is the delivered record; the
`round61-entry` and `round61-final` records are earlier publication passes.

Numerical qualifications for Capstan, whose update was left untouched:

- §4's “identical own-prompt retention” is not exact: CounterFact seed 1 RET-ES
  is ePC 1.00 versus BP .99. The refreshed wording says nearly equal and shows
  both values. This is already visible in lead-queue item 155's own table.
- The CounterFact seed-0 RET-GS deficit is 24.1667 percentage points. Calling
  all deficits “small” understates that result. They have the same sign in the
  four available dataset/seed pairs but markedly different magnitudes.
- zsRE seed 0's exact ePC−BP difference is −.0266667; rounding to three decimal
  places gives −.027, rather than the update's −.026. The spoken slide gives
  2.7 percentage points as the deficit magnitude.
- Seed 2 can assess consistency within this recipe; it cannot by itself decide
  whether an effect is systematic across new training conditions or subject
  populations. No causal attribution to seed variation is claimed.

The update's 299-cell/8-reader HT-17 description is an explicitly named October 1
snapshot, not an error. The new canonical snapshot adds two reader cells and
leaves all 299 previous cell statistics unchanged. Option R remains queued;
no completed resume or new design was inferred from its authorization.

Done-when met: update first, both summaries current, manifest consistent.
No GPU seconds or model calls. No question for the lead; POST-1/PRES-9 wait for
the meeting feedback.
