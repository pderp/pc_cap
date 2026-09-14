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

## 3. Lanes for Codex — round 7 (CPU; open now)

Round 6 is committed (`a903cfd`) and answered (`docs/tasks/R1-46-response.md`; R50-04/06/08/09 repaired in `ae22d73`).
State: the learned reader is the primary revision condition with one rule for both datasets — identity, results,
controls and open risks in `manifests/revision_v1/primary_condition_v1.json` and `docs/R1_stage2_notes.md`. DEC-040: the
orchestrator is running both R1-24 treatments (literal self-KD control + informative LM continuation). Lanes:

### Lane R1-X6 — audit of the round-6 repairs and the reference-condition identity

Read-only: verify commit `ae22d73` against your R50-04/06/08/09 checkpoints (bank identity verification, ledger charging
of the fast trainer, mixed-domain query guarantees, operating-point hygiene), the scale profile (`scripts/r1_53_scale_profile.py`,
`results/R1/scale_profile_*.json`) and `primary_condition_v1.json` (weights hashes, pools, rules); reproduce the two
open risks it states. `logs/audit_r1_28b.md`.

### Lane R1-44 — unseen-edit-prompt endpoint (the second scale risk)

Specify and implement (new file `src/pccap/revision_v1/endpoints_unseen.py` + CPU test) an endpoint that measures false
firing and answer change on prompts of facts NOT in memory, drawn from the same pool as the edits (denominator, schema,
how it differs from LS), so the run matrix can carry it. Use the tiny base for tests; the GPU run is the orchestrator's.
`docs/tasks/R1-44.md`.

### Lane R1-40c — run matrix v3: add the memory-size and unseen-prompt endpoints and the DEC-040 conditions

From `run_matrix_draft_v2.json`, `primary_condition_v1.json` and DEC-040: add the memory-size profile (100 / 300 /
1,000 records) and the unseen-prompt endpoint as declared endpoints, the two continuation conditions (S1 literal, S1
LM) with their evaluation cells, and the profiling runs the orchestrator must execute before ceilings are frozen; keep
everything unlaunchable/unfrozen. `manifests/revision_v1/run_matrix_draft_v3.json`, `docs/tasks/R1-40c.md`.

### Lane R1-D2 — CounterFact confirmatory candidates (both readings, for the lead's decision)

Prepare the ordered candidate list for fresh CounterFact confirmatory streams under exclusions v3 in both readings plan 9
leaves open: (a) from the unopened remainder of the old eligible pool minus the DEC-037 training draw (13,141 items) and
(b) a fresh source if one exists in `assets/data/raw` (state if none). Counts at each filter, per-record hashes, no draw,
no seal. `manifests/revision_v1/counterfact_fresh_candidates_v1.json`, `docs/tasks/R1-D2.md`.

### Lane R1-47 — Stage 2 report draft

From `docs/R1_stage2_notes.md`, `results/R1/stream_eval.md`, the scale profiles and your reviews, draft
`docs/R1_stage2_report_draft.md` in the style of `docs/report.md`: what was built, the diagnosis chain, the results
tables (with the historical/overwritten artifacts labelled), the controls, the open risks, and what Stage 4 must
establish. The orchestrator revises it; do not modify the notes.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
