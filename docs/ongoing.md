# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 08:10 EDT (round 3 evaluated; round 4 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-11-0715.md`. Rules §1 are
unchanged and restated in `CONTRIBUTING.md`: JAX only, sibling/FabricPC read-only, resources under
`assets/`, **no commits by agents** (the lead commits; the orchestrator commits only when the lead asks),
task records in `docs/tasks/<ID>.md`, claim rows with the status tool or a claim JSON, lease for any GPU
use > 60 s, placeholder modules are the lane's to replace, other existing files need an edit request.
Board: `docs/tasks/STATUS.md`.

**Round 3 is evaluated (08:10 EDT).** V3 confirmed the five repairs; Lane X's P4 reproduction holds and its S7
findings are repaired; B4-S ran the sensitivity control, which did not reproduce the divergence class, so B4 stays
unregistered (DEC-020) while Codex localizes the first cross-framework gradient difference. Codex's round-4 lanes are
in §3 (B4-D in progress; S3-01, V4, P open). The lead has accepted the defaults for D-A/C/D/G/H (DEC-021…024); the
freeze command is posted in `docs/lead_queue.md` and waits only on the B4 deadline (2026-09-12 12:00 EDT). The orchestrator's next GPU use (B4 profile, one confirm-mode smoke job against the real base, the
GPU test subset) comes after Lane B4-S lands and is announced in `docs/lead_queue.md`; short `-m gpu` tests by
either agent need no lease.

**Post-freeze rule for every agent (from the moment `manifests/frozen.json` exists).** The freeze binds the hash of the
whole installed `src/pccap` tree; every confirm-mode job compares the tree at start and refuses on any difference (exit 2,
the queue stops). Therefore: no edits under `src/pccap/` after the freeze — not even in your own lane's files
(`src/pccap/baselines/grace_*.py` included). Put B4-D diagnostics and fixes in new files under `scripts/`, `logs/`,
`results/` or `docs/`, or as a proposed patch under `docs/tasks/`; a fix that must land in `src/pccap` is applied only with
a versioned manifest and `--allow-code-drift` recorded by the orchestrator (plan 4 §2). Tests under `tests/` and everything
outside `src/pccap` are unaffected.

**(17:56 EDT) The hold on `src/pccap/` is lifted: the v3 grammar rerun is finished and no confirm-mode job remains. New
modules go under `src/pccap/revision_v1/` as planned; anything drafted under `revision_v1_staging/` can move in.**

## 1. State (2026-09-14, 04:00 EDT)

- **v0 closed** (close-out identity `cb04d5e`); the lead's T4 review of the report/memo is still outstanding. SD-24 (ePC
  energy penalized the cap write) is fixed in place (DEC-036); the S5 SE-E row is annotated.
- **Revision v1**: Stage 0 memo done (counter-review adopted); Stage 1 modules installed and audited (R1-23 → R1-25
  repairs committed); Stage 2 pilots have reshaped the read/write path — tied cosine reader over stable observations,
  v0-style per-position delta writes, hard top-1 selection, pairwise null. The NON-LEARNED instance (random reader,
  cosine gate) reaches ES 1.00 / RET-GS 0.65 / LS 1.00 on the zsRE development stream (controls 0.44) but fails on
  CounterFact (near-neighbour locality); trained readers are being evaluated (`docs/R1_stage2_notes.md`).
- DEC-037: a 3,000-item CounterFact training pool from the unopened remainder (exposure → register v2).
- Rules unchanged (§ top). New code under `src/pccap/revision_v1/`; tests under `tests/revision_v1/` (77 pass); task ids
  `R1-<stage><seq>` with records in `docs/tasks/`.

## 2. Orchestrator lane (do not touch)

v0 close-out (tonight) → R1-01/02/03 diagnostics (GPU, ≈ 2 h) → `docs/R1_diagnosis.md` → Stage 1 core modules
(`revision_v1/{contracts,observations,memory,reader,controller,adapt,evaluate}.py`) with the gates → Stage 2 reference and
surrogates → Stage 4 runs and the revision freeze support. Owned: `src/pccap/revision_v1/` except the files named in §3,
`results/R1/`, `manifests/revision_v1/`, the registers, `docs/lead_queue.md`.

## 3. Lanes for Codex — round 3 (CPU; open now)

Round 2 (R1-D1, R1-20b, R1-X1, R1-23) is committed (`d6a1d1f`) and mirrored; your script repair was applied verbatim
(hash = tested v2). Responses: `docs/tasks/R1-23-response.md` (R23-02/04/06/07/09/10 repaired, R23-01/03/05/08 answered),
`docs/tasks/R1-X1-response.md` (all eight adopted; memo wording corrected). Next lanes, in priority order:

### Lane R1-D1b — canonical entity / alias review of the exclusion register (critical path for Stage 4)

Resolve the "possible alias" and contextual-mention classes in `manifests/revision_v1/exclusions.json` into decided
canonical exclusions (with reasons) so that the register can be frozen as version 2; report over- and under-exclusion
counts and the effect on the candidate pool (raw / unique-subject). Text review only. `docs/tasks/R1-D1b.md`.
Also fold in the new exposure: the 3,000 subjects of `manifests/revision_v1/train_pool_counterfact_v1.json` (DEC-037;
`drawn_subjects_normalized`) must appear in register v2 with reason `train_pool_counterfact_v1`.

### Lane R1-20c — the new synthetic final namespace (R1-20b's remaining item)

Implement and freeze a new entity namespace/version for the synthetic generator with the pre-emission overlap check and
the ≥ 2-paraphrase rejection gate, so that `final_generation_ready` can become true; do not generate or seal final
examples (the lead reserves that). Tests under `tests/revision_v1/`. `docs/tasks/R1-20c.md`.

### Lane R1-24 — teacher-only continuation control (X0-01, DEC-034(a)) — CPU design and harness; open now

**What it controls for.** Any gain of the revision may partly come from *more training of the base-adjacent
machinery*, not from the cap. The control continues to train the base itself by teacher-matching distillation from the
v0 close-out checkpoint with a matched budget of added tokens/examples, then re-runs the same editing evaluation with
v0's cap on that continued base. If the continued base alone moves the endpoints, the revision's gains are attributed
above it.

**Inputs you have.** `pccap.distill` (v0's S5 substrate machinery: `recipe.py` recipes, `data.py` token sources,
`schedule.py`, `train.py` with `Trainer`, `Milestones`, checkpoints and logs; the SE-A base was produced this way —
`docs/tasks/S5-01.md`, `results/S5/`), the v0 close-out checkpoint identity (`manifests/reference.json`,
`manifests/assets.json`), the S4/S5 allowances in `manifests/frozen.json`, and the budget accounting rules in
`docs/report.md` §"Comparable compute".

**Deliverables (CPU only; no GPU, no training run).**
1. `docs/tasks/R1-24.md`: the control's definition — starting checkpoint, token source and matched budget rule
   (tokens = the sum the revision's Stage 2 training consumes on GPT-2 passes: state how you will read it from the
   ledger records of `results/R1/pilot/*/summary.json`), the distillation recipe (teacher = the same checkpoint, so the
   control is "continued self-distillation"; say explicitly whether that is the intended reading of X0-01 or whether an
   external teacher is required, and why), the stopping rule, and the evaluation: the v0-stable cap (`StableCap`,
   `scripts/r1_14_v0_stable.py`) and the revision learner on the continued base over the same 100-edit zsRE and
   CounterFact development streams, plus the drift assay (`scripts/drift_supplement.py`).
2. `scripts/r1_24_control.py`: a runnable script that prepares the recipe and data manifest, checks the budget
   arithmetic, and — behind a `--gpu` flag the orchestrator will use — launches the distillation and the evaluations
   through the lease. Dry-run mode must produce `manifests/revision_v1/r1_24_control.json` (recipe, sources, hashes,
   budget) without touching the GPU.
3. A CPU test under `tests/revision_v1/test_r1_24_control.py` for the budget arithmetic and manifest schema.
4. A short note on what result would count as "the continued base explains the gain" (thresholds in the same units
   as DEC-034's non-inferiority margins).

Read-only on everything else; the orchestrator runs the GPU part and records the result in `docs/R1_stage2_notes.md`.

### Lane R1-X2 — audit of the R1-25 repairs and the Stage 2 redesign (OPEN NOW)

Read-only re-audit of `adapt.py`, `memory.py`, `learner.py`, `reader.py`, `controller.py`, `train.py`, `epc_train.py` at the
current head (R1-25 repairs `d28b8ac` and the later delta/tied-cosine/pairwise-null changes, see `docs/R1_stage2_notes.md`); reuse
your `scripts/r1_23_*.py` with new output paths; `logs/audit_r1_25.md`.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
