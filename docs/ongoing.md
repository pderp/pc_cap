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

## 3. Lanes for Codex — round 6 (CPU; open now)

Round 5 (R1-43, R1-24b, R1-X4, R1-30a, R1-27 fixtures) is committed (`5ee8b56`) with your three one-line corrections
applied; X4-10 is repaired and the non-learned reference regenerated under fresh per-dataset identities (`08c6321`,
`docs/tasks/R1-X4-response.md`). Pending lead decisions: DEC-038 (non-learned system as the primary revision condition),
the D1b policy acceptance, and the R1-24 informative variant. Lanes that do not wait on them:

### Lane R1-40b — prune and re-cost the run-matrix draft under the DEC-038 default and X4-08

Produce `manifests/revision_v1/run_matrix_draft_v2.json` from your v1 draft: primary conditions = v0 live (C1, C2),
v0-stable, matched-update, R1-nonlearned (random tied cosine reader + cosine gate 0.93 + per-position deltas); secondary
= learned reader (best available weights, reported as negative); drop cells that depend on a working learned null. Re-cost
persistent bytes with the corrected delta scaling (9 KB × answer tokens per record; ceiling binds near 1,700 edits at 4
tokens) and state per cell whether a 1,000-edit stream fits the 64 MiB ceiling or needs a bounded-position write.
Keep everything unlaunchable/unfrozen. `docs/tasks/R1-40b.md`.

### Lane R1-X5 — re-audit of R1-28 and the regenerated reference

Read-only: verify that `ref_nonlearned_gate0.93_v2` and `…@counterfact` have distinct results and checkpoint roots
with consistent per-item files, that the guard now derives the checkpoint root from the harness expression, and recount
the two summaries from their item files. Also refresh your obsolete R1-26 fixtures (`test_r1_26_boundary_audit_cpu.py`
builds a cap with `ceiling_bytes=1`, which X26-01 now refuses) in a superseding test file. `logs/audit_r1_28.md`.

### Lane R1-D1d — E.2 admission list for the fresh zsRE draw (CPU side)

From `zsre_fresh_candidates_v1.json` (58,498 clear), prepare the exact ordered prompt list and batch plan the orchestrator
will run through the BP teacher (E.2: keep items whose greedy answer is outside the aliases), with per-record hashes, the
expected retention needed (≥ 5.13 %) and the stopping rule (stop once 3 × 1,000 + reserve are eligible, or report a
shortfall). `manifests/revision_v1/zsre_e2_plan_v1.json`, `docs/tasks/R1-D1d.md`. No teacher execution.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
