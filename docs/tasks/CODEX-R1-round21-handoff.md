# Codex round 21 handoff

2026-09-17. Implemented **R1-D9a, R1-D9b, R1-D9c, R1-77c and R1-73b**. No commits, real draw, real seal, final freeze, real-base execution or GPU use. Claude's active development driver identity remains `19c50855a9f5352f91fd5f45677869bd1f3047212c023e30726d26420b3229d4`.

## Available now

| Lane | Delivered | Next owner action |
|---|---|---|
| R1-D9a | Separate final-clearance producer; exhaustive dispositions, exact v6 source hashes and joint role-capacity checks | Complete/review actual alias, context, exposure, teacher/token and role evidence; bind an explicit clearance authorization |
| R1-D9b | Separate draw producer; register-bound independent RNG streams and five paired orders; exact receipt schema | Bind cleared candidates, protocol/RNG admission and lead-chosen master seed; inspect before the authorized draw |
| R1-D9c | Separate seal producer; exact reservations, content hashes and independent analysis population; immutable assets outputs | Construct and review endpoints against the fixed draw, then authorize sealing |
| R1-77c | Reviewed sealed-backend donor update and explicit v0 batching; reduced synthetic pipeline through queue inspection, sealed TinyBase execution and R1-49g analysis | Complete actual final protocol/gates/ceilings/freeze and bind the new backend bytes in real recipes |
| R1-73b | Independently reproduced calibration v3, additive U08 declaration, eight MQuAKE recipes, inspection receipts and ordered run list | Coordinate owner GPU execution and retain failure costs; final calibration/profile admissions remain separate |

Operator entry point: [R1-D9 operator interface](R1-D9-operator-interface.md). The three dry-run commands are there, with the exact input and authorization schemas. The new template is `R1-D9-inputs-template-v1.json`. It uses matrix/protocol v5.1 and deliberately contains no invented seed, review evidence or owner approval.

**Having the producers does not yet mean the real population is cleared.** Final previews in `logs/r1_round21/d9{a,b,c}-dry-final.json` refuse the absent evidence/receipts. Nominal subject counts remain 52,411 /12,246 /4,218; they are not certified usable counts. MQuAKE's nominal slack remains only 168. The lead still needs the actual review records and explicit acts before draw/seal/freeze. The reduced rehearsal used pure producer APIs with small counts; the full production CLI approval chain has not been run end to end. Writer, approval, refusal and exact receipt schemas have separate tests.

MQuAKE execution handoff: [ordered run list](R1-73b/ordered-runlist.md), [task record](R1-73b.md), and `docs/R1_stage4_U08_mquake_calibration_v3.md`. Six v0/S1 conditions explicitly use full integrity plus batched drift; two RevisionCap conditions retain incremental integrity. Radius zero is explicit. These 300-attempt development profiles use exposed training fillers/outside prompts and have missing near-miss/revision rows with planned denominators retained; they cannot alone price the final challenge inventories. S1 calibration transfer is development-only.

Backend review: [R1-77c donor review](R1-77c-donor-review.md). Absent/default drift fields retain their historical dispatch. An explicit batched choice is frozen in the recipe contract; a post-freeze field change refuses. Sealed admission, failure accounting, journal/resume, full integrity and October 9 deadline behavior remain intact.

## Validation

- Combined CPU suite: **117 passed in 37.18 s** (`logs/r1_round21/round21-final-tests.txt`).
- After final seal guards: **40 passed in 17.31 s** (`d9-seal-final-tests.txt`).
- Two additional exact-authorization tests pass (`authorization-tests.txt`). This covers **121 distinct passing tests across the runs**, with final changes tested in the affected subset.
- Ruff passes; `git diff --check` passes. All eight final MQuAKE recipes were re-inspected after the backend work. `final-verification.json` records the unchanged active driver and actual dry-run refusals.

## Remaining lanes and boundaries

**HT-4d and HT-3e are not worked in this handoff and can be assigned independently.** They remain on the current list: claim ledger v4 and independent final κ/stress-panel counter-review. Chain K cost results should enter the ledger only when filed. The κ reports retain the mandatory DEC-054 framing; the stress recovery statement must distinguish observed right-censoring from a claim about all future behavior.

The user lifted the existing-file prohibition during this round, conditional on avoiding simultaneous Claude edits. Earlier permission wording in the already-bound U08 addendum reflects its preparation before that clarification and is superseded; its bytes were retained to preserve recipe identities. Existing tracked changes are limited to `scripts/r1_77b_sealed_backend.py` and its test fixture. Other delivered files are additions. The installed `src/pccap`, active development driver/builder, owner results, ongoing task list, lead queue and task board were not edited. No files were staged or committed. Independent owner result files visible in git status belong to chain K.
