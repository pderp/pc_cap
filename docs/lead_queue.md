# Lead queue

Asynchronous questions for the lead (updated_plan2.md §1, four touchpoints T1–T4). The
orchestrator continues with everything that does not depend on an answer. Answers are recorded
in `docs/decisions.md`.

## T1 (opened 2026-09-09, D0) — accept the plan; locate assets

**Question.** Accept updated_plan2.md and its pre-authorizations PA-1…PA-9, as modified by the
execution directives DEC-001…DEC-005 (JAX only; FabricPC for PC; sibling and FabricPC read-only;
resources under `assets/`). State the locations, if any exist, of:

1. the production ePC checkpoint (SHA-256 `4f0c23aaba9d8daabfc1f455ee673776a940171e2456b3291a5bb00015284eb5`,
   sibling `artifacts/models/gpt2-predictive-coding.pt`) and its resume state;
2. the R8/R9 six-layer grammar model, tokenizer and generator;
3. causal-fibres v0.3 (joint block diagonalizer, supplied-support sandbox);
4. comcrit (HVP / quadratic control code);
5. RelaLeap harnesses;
6. documents [2] and [5] of `docs/footnotes.md` (no links given).

**Default if no answer by CP-A + 2 working days** (deadline written by S0-01): PA-1 fires as
REG-00→REG-01 (JAX re-implementation of the recipe; SD-15) and PA-2 fires as GRAM-01/02;
items 3–6 are marked `unavailable` and the optional work that needs them is `unsupported`.

*(S0-01 appends the measured absent list below.)*

## T2 — reserved (D1, only if the smallest complete core comparison does not fit)

## T3 — reserved (D3, only if a required core pair must be dropped)

## T4 — reserved (CP-F, report review before any external release)
