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

### T1 measured absent list (S0-01, 2026-09-09)

Absent on this host, in `~/repos`, and in the sibling: the ePC checkpoint `4f0c23aa…` and its
resume state; the R8/R9 six-layer grammar (model, tokenizer, generator); causal-fibres v0.3;
comcrit; RelaLeap. Documents [2] and [5] have no link. Drive links [1], [3], [4] resolve (not
downloaded). Details: `manifests/assets.json` (`assets`, `inventory`).

**Clock:** CP-A = 2026-09-09. PA-1 (REG-00 → REG-01 pilot) and PA-2 (GRAM-01/02) fire after
**2026-09-11 23:59 (America/New_York)** unless T1 names a location. GRAM-01 (the generator) and
REG-00 (the JAX distillation driver) are pure engineering and may start before the clock; only
the GPU regeneration/training waits.

## Lease schedule (orchestrator, 2026-09-10)

REG-02 (ePC regeneration, ≈ 12 GPU-h) holds `results/.gpu_lease` in chunks of ≤ 500 steps or 90 min, releasing it between chunks; any other lease user simply queues (fcntl). Short `-m gpu` tests need no lease. Stop file: `results/REG/reg02.stop` pauses the loop after the current chunk.

## Agent questions

(append dated lines here)

- 2026-09-10 (orchestrator, relaying Lane D) — **answered: approved and applied** (see the edit-request file). Original: codex needs your yes/no on pinning `setuptools==78.1.0` inside the new auxiliary env `assets/envs/grace` (touches only that env; unblocks the GRACE reference smoke and parity cases): `docs/tasks/S2-05a-environment-edit-request.md`.

## T-CP-E (opened 2026-09-10; re-dated 2026-09-10 afternoon by DEC-019) — freeze decision

**Re-dated:** Codex's interim report 2 found integration defects on the confirmatory path (now repaired, `logs/review_interim_report2.md`); the freeze request stands only after the gate in `docs/updated_plan4.md` §2 is green (re-profile with reconcilable costs, GPU tests, Lane V review). Grammar/B4 may then be accepted as unavailable explicitly (`--accept-unavailable`).

`manifests/frozen.draft.json` is schema-valid (`python -m pccap.harness.freeze --draft`); the readiness checklist is docs/D2_decision.md §5. Pending inputs at writing: grammar dataset id (GRAM-02, PA-2 clock 2026-09-11 23:59 ET), B4 (Lane D), ePC checkpoint (REG-02 running, S5 only). Decision requested: freeze the BP core when the B1 learning-rate screen and the CR re-profile are in (today), recording grammar/B4 as `unavailable` in the manifest if still missing — or wait for PA-2. Act: `python -m pccap.harness.freeze --final --i-am-the-lead` and commit `manifests/frozen.json` (this unlocks confirmation access; no agent will do it).

## T-ENV/S6 (opened 2026-09-10, updated_plan5.md §4)

1. Coverage tooling (`pytest-cov`) in the frozen venv: yes/no (derp_review2 N7).
2. S6 (conditional re-distillation): closed for the month under DEC-014's charge of REG to S6's allocation (≈ 14 of 20 A100-h consumed by REG-01/02 and the follow-up chains), unless you reassign hours.

## PA-2 note (2026-09-10)

The replacement grammar (GRAM-01/02, DATA-06/07) is built and trained on the CPU in seconds (no GPU hours spent). It is recorded as *provisional* in `manifests/assets.json` until the PA-2 clock (2026-09-11 23:59 ET) passes without T1 locating R8/R9; if you prefer, say so and it is promoted now.

## S4-02 allowances (opened 2026-09-10 20:20 EDT) — needed before the freeze

The freeze draft has **no pending inputs** now (`python -m pccap.harness.freeze --draft`). Two fields are yours at S4-02 and must be set before `frozen.json` is written: `resource_rules.run_allowance_seconds` (per confirmatory run) and `resource_rules.stage_allowance_seconds.S4/S5`. The refreshed projection prices the selected scope (zsRE 1000 / CounterFact 300 / grammar 10000) at 20.5 of the 27.0 local hours after headroom; per-run figures from `results/S2/throughput.json` (learning + query s/edit × items, plus rescoring) are in `results/S2/projection.json` `table[..].parts`. A `None` is allowed but then recorded as *not enforced* in every run.

