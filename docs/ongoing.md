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

## 1. State (2026-09-13, 17:25 EDT)

- **v0 closed out (18:15 EDT)**: the v3 grammar rerun is analysed (complete, negative at the floor), the report and D3 memo
  carry the row, the S7 grammar reversals are rerun under v3; only the lead's T4 review remains for v0. The full-validation drift supplement is done
  (`results/S4/drift_supplement.md`). Codex's P2/X2 corrections are applied (SD-23 too).
- **Plan 9 (revision v1) is accepted with all defaults (DEC-033)** — `docs/updated_plan9.md` is the contract, the
  coding-agent guide (`docs/more_input/pc_cap_coding_agent_guide (1).pdf`) the specification. Stage 0 starts now on the CPU;
  GPU diagnostics after the rerun. The v0 frozen manifests, sealed data and results are never modified.
- Rules unchanged (§ top). New code lives under `src/pccap/revision_v1/` behind adapters; tests under
  `tests/revision_v1/`; task ids `R1-<stage><seq>` with records in `docs/tasks/`.

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

### Lane R1-24 — teacher-only continuation control (design + CPU harness; X0-01, DEC-034(a))

Specify and implement the CPU side of the control: continued teacher-matching distillation of the base from the v0
close-out checkpoint with matched added tokens/examples (the `pccap.distill` machinery), its own cap retrained under the
same allowance, and the comparison record. The GPU run is the orchestrator's. `docs/tasks/R1-24.md`.

### Lane R1-X2 — audit of the R1-25 repairs (when this file says so)

Read-only re-audit of `adapt.py`, `memory.py`, `learner.py`, `train.py`, `epc_train.py` after commit `R1-25`; reuse
your `scripts/r1_23_*.py` with new output paths; `logs/audit_r1_25.md`.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
