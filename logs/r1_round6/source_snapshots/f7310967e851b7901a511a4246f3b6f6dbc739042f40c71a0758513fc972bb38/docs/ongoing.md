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

## 3. Lanes for Codex — round 6 (CPU; open now) — learned-reader recovery first (lead directive)

The lead wants the learned reader to work before other issues. The recovery plan is in `docs/R1_stage2_notes.md`
("Learned-reader recovery plan"). Lanes below are non-blocking and non-blocked; they feed that plan directly. Round 5 is
committed (`5ee8b56`); X4-10 is repaired and the reference regenerated (`08c6321`).

### Lane R1-D3 — zsRE training pool candidate list (M3; DEC-039 default: yes) — NOW THE CRITICAL PATH (12:30 EDT): the reader works on CounterFact (RET-GS 0.93 / LS 1.00) and on zsRE with a gate (0.97 / 1.00); one locality rule for both needs this pool; `scripts/r1_d3_e2_filter.py` consumes your list

From `manifests/revision_v1/zsre_fresh_candidates_v1.json` (58,498 clear), emit `manifests/revision_v1/train_pool_zsre_candidates_v1.json`:
6,000 candidates (seed 139; so that ≥ 3,000 survive the teacher filter) with prompt, rephrase, answer, aliases, locality
prompt/answer, subject, per-record hashes, and the exclusion reasons that will apply to them (`train_pool_zsre_v1`) for
register v3. Record explicitly that these leave the confirmatory candidate pool (58,498 → ≥ 52,498). No tokenization or
teacher execution. `docs/tasks/R1-D3.md`.

### Lane R1-45 — near-neighbour separability analysis (M4; text only)

For the CounterFact and zsRE development pools (`manifests/dev/*_dev.json`, all 300 items each) and the 3k CounterFact
training pool: for every item, compare its paraphrases and its locality prompts against its own prompt on lexical
features — subject-token overlap (with and without a stoplist of the 200 most frequent GPT-2 tokens in the pools),
longest common token span, relation-template overlap — and report, per dataset, the ROC/separability of each feature for
"paraphrase vs locality near-neighbour" and "paraphrase vs other item's prompt". Deliver `logs/r1_round6/near_neighbour_separability.json`
+ `docs/tasks/R1-45.md` with a recommendation of the two features to feed the null head. CPU only; no model.

### Lane R1-46 — stream-scale episode specification review (M1/M2; read-only, when `src/pccap/revision_v1/stream_train.py` appears)

Review the orchestrator's stream-scale episode builder and feature bank for label leakage (queries must never carry
targets into the reader), population definitions (in-memory paraphrases / own prompts / locality nulls / out-of-memory
prompt nulls), class balance, and the deployment-prevalence argument for threshold selection (M5). `logs/review_r1_50.md`.

### Lane R1-40b — prune and re-cost the run-matrix draft (unchanged from before; lower priority)

As previously specified (`run_matrix_draft_v2.json`, DEC-038 default and X4-08 byte scaling); do it after the three lanes above.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
