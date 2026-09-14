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

## 3. Lanes for Codex — round 5 (CPU; open now)

Round 4 (R1-40, R1-D1c, R1-X3) is committed (`54527d1`) and mirrored; your edit request is applied (hunk 2 had already been
satisfied by the import normalization; hunk 1 applied by hand; script hashes refreshed where they were bound). R1-27 repaired
X26-01..04 (`3dd2f5c`, `docs/tasks/R1-X3-response.md`). Note: four of your `test_r1_26_boundary_audit_cpu.py` fixtures build a
cap with `ceiling_bytes=1`, which X26-01 now refuses at construction — the strict xfails for the capacity bypass are
obsolete; please update those fixtures in your next round (new-file rule: a superseding test file is fine). Next lanes:

### Lane R1-43 — endpoint harness for near-miss, revision and composition (plan 9 Stage 4 endpoints)

Build, on the v0 harness surface the revision learner already exposes (`RevisionCap.update_item / predict /
selection_for`, `docs/revision_v1_design.md` as built), a CPU-testable evaluator for the three endpoints plan 9 adds:
near-miss preservation (the challenge set's near-neighbour rows: the edited fact's neighbour must keep its cap-off
answer), revision (a second support for the same fact supersedes the first: the new answer wins, the old record is
retired, the old answer is not produced), and two-hop composition (the challenge set's composition rows with verified
labels; report "unreachable" honestly when a hop is missing). Inputs: `manifests/dev/challenges.json` (5 near-neighbour,
6 composition, 5 temporal-correction rows), `pccap.harness.runs` (ES/GS/LS machinery), `tests/revision_v1/tiny_base.py`
for CPU tests. Deliver `src/pccap/revision_v1/endpoints.py` (new file), `tests/revision_v1/test_endpoints.py`, and
`docs/tasks/R1-43.md` with the denominators and the record schema; the GPU run over the real base is the orchestrator's.

### Lane R1-24b — the informative continuation recipe (pending the lead's decision, prepare it now)

Beside the literal self-distillation manifest, prepare `manifests/revision_v1/r1_24_control_lm.json`: continued
language-model training of the base (next-token cross-entropy on the same OpenWebText shard, consecutive positions,
matched token budget read from the pilot ledgers, same optimizer family as `pccap.distill`), with the same evaluation
block. Dry-run only; tests for the budget arithmetic; `docs/tasks/R1-24b.md`. If the lead chooses it, the orchestrator
runs both.

### Lane R1-X4 — counter-review of the Stage 2 notes and the non-learned condition

Read-only. `docs/R1_stage2_notes.md` now claims: the fact-code path cannot carry new answers; the non-learned condition
(random tied cosine reader + per-position deltas + hard top-1 + cosine gate 0.93) reaches ES 1.00 / RET-GS 0.65 / LS 1.00
on the zsRE stream and 0.18 / 0.16 on CounterFact; trained nulls do not transfer to the streams. Recount every table row
from `results/R1/stream_eval_*.json`, `results/R1/streams_revision/*/items.jsonl` and `results/R1/pilot/*/summary.json`,
check the cost columns against the ledgers, state what the zsRE 0.65 does and does not show (one stream, one order,
100 edits, v2 calibration), and list what would change the recommendation to keep the null non-learned.
`logs/review_r1_stage2.md`, findings by id.

### Optional if capacity remains — Lane R1-30a — Stage 3 design note (cap-level PC energy)

A written specification only: how a latent-energy cap (FabricPC nodes for the record/selection state, bounded settling
steps, answer-objective coupling per X0-07) would sit on the current read path, what state resets per query, which
approximations are declared, and the zero-step / feedforward / recurrent controls. Inputs: `logs/fabricpc_survey.md`,
plan 9 §Stage 3, `docs/revision_v1_design.md`. `docs/R1_stage3_design_draft.md`. No code.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
