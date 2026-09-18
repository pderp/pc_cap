# Round 30 — Codex handoff, 2026-09-18

The CPU work is ready for the orchestrator's idle-boundary application. **143 tests and six subtests passed**; all new Python files and both proposed execution files pass Ruff; the patch passes `git apply --check`. Installed tracked files remain unchanged. No GPU work, staging, commits, draw, seal, frozen manifest or signatures.

| Lane | Delivered | Next dependency |
|---|---|---|
| R1-68f | Streaming full-validation endpoint; exact development + sealed-backend patch; synthetic CPU correctness/integrity tests | Orchestrator applies patch and measures real-base behavior/cost |
| R1-64g | Validated four-cell preparation; guarded recipe/run-list builder; 29-leaf + 8-parent rebinding rehearsal | Installed R1-68f identities, then four owner GPU runs |
| R1-58k | All four completed chain R results and all 27 host rows ingested; precise remaining dependency inventory | Full-validation measurements, accepted cost-transfer evidence/policy, production consumer integration |
| R1-63k | Prerequisites and production assembler omission identified | Real inputs v9; preserve/require full-validation contract; honest unsigned preview |
| X19 | Deferred to the requested package version | Candidate v14 and current source/evidence bindings |
| HT-4f | Deferred as assigned | Signed receipt v4 |

Start with `docs/tasks/R1-68f.md`: it contains the exact patch/application/rebinding commands and explains the vector format, references, memory bounds, overlap gate and cost fields. `docs/tasks/R1-64g.md` describes the four unchanged development populations. `docs/tasks/R1-58k.md` contains the chain R results and the follow-ups needed before the package can truthfully reach “signatures only.” The machine-readable preparations are `R1-64g-preparation.json` and `R1-58k-preflight.json`.

Two implementation details affect the next cost/admission work. First, the old loops sampled drift only at the **final** checkpoint: DEC-063-enabled recipes add intermediate sampled phases as well as final full validation. Second, the current production assembler drops unknown runtime fields and the current analysis reads only sampled drift. The new endpoint must be carried through production recipes, frozen populations, admission and reports. These consumer changes can be developed alongside the four GPU measurements, but must respect the running job's actual code bindings.

The committed cost receipt still lists 14 full challenge-endpoint measurement gaps with unreviewed transfer proposals. CounterFact full-validation transfer, S1's additional original-reference pass, other unmeasured classes and 1,000-record occupancy need an explicit resource basis. Receipt revision 4 also needs its own typed supplementary validator; merely changing the revision number would skip the existing revision-3-only check. None of these gaps has been silently converted to a signature checkbox.

Validation logs: `logs/r1_round30/r1-68f-final-tests.txt`, `r1-68f-followup-tests.txt`, `r1-68f-verification.json`. Exact patch/source/module identities: `logs/r1_round30/r1-68f-patch.json`. Disposable synthetic vectors/recipes/test runs remain on disk in ignored fixture directories; their resources and snapshots are in assets.
