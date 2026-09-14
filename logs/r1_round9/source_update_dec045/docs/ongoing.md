# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-14 17:20 EDT (round 8 committed; round 9 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-14-1515.md`. Rules §1 are
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

## 1. State (2026-09-14, 17:20 EDT)

- **v0 closed** (close-out identity `cb04d5e`); the lead's T4 review of the report/memo is still outstanding.
- **Revision v1, Stage 2 is done on the development side.** The learned reader (tied cosine + pairwise null + lexical
  overlap, stable observations, per-position deltas) with ordinary-text null training is reference condition v2; with the
  R1-56 rare-token overlap gate it is the proposed v3 (DEC-043). Development streams, three seeds: zsRE RET-GS 0.96–0.98,
  CounterFact 0.715–0.85, ES / RET-ES / LS 1.00; drift 0.000 / +0.012 nats; near-miss 100/100, revision 100/100; unseen
  edit-prompt false fires zsRE 10–11 % at 1,000 records (45 % without the gate), CounterFact 0 %. Report:
  `docs/R1_stage2_report.md`; running log `docs/R1_stage2_notes.md`; identities `manifests/revision_v1/primary_condition_v{1,2,3}.json`.
- **Costs measured on the real base** (R1-55, `results/R1/p1_profile/`): 1,000 records use 51–74 % of the state
  ceiling with exact restore; edit 0.07–0.13 s; query 10–15 ms; a full 1,000-edit cell with every endpoint at three
  checkpoints ≈ 1,150 s. Codex's 240-cell matrix v3 ≈ 92 h against the 15 h envelope; the lead keeps the full scope (DEC-044);
  ceilings will be set from the measured components.
- **Round 8 committed** (`c401f55`): Stage 4 protocol draft (R1-49, gates U01–U18), frozen register binding
  (R1-D1f, `exclusions_frozen_v3.json`), ordinary-text null spec (R1-50b), R1-24 review (R1-X7; qualifications applied
  to the notes).
- **DEC-045**: MQuAKE-CF is the third dataset (`assets/data/raw/mquake/`); CounterFact stays (which needs the DEC-042
  exception). DEC-043 accepted, DEC-044 keeps the full matrix (now 360 cells). Then the freeze (R1-41). No draw, seal or launch before those.
- Rules unchanged (§ top); Codex: new files only, CPU only, no sealed payloads, no real-base execution; edit requests
  as patches under `docs/tasks/`. Tests under `tests/revision_v1/` (CPU) must pass.

## 2. Orchestrator lane (do not touch)

v0 close-out (tonight) → R1-01/02/03 diagnostics (GPU, ≈ 2 h) → `docs/R1_diagnosis.md` → Stage 1 core modules
(`revision_v1/{contracts,observations,memory,reader,controller,adapt,evaluate}.py`) with the gates → Stage 2 reference and
surrogates → Stage 4 runs and the revision freeze support. Owned: `src/pccap/revision_v1/` except the files named in §3,
`results/R1/`, `manifests/revision_v1/`, the registers, `docs/lead_queue.md`.

## 3. Lanes for Codex — round 9 (CPU; open now)

Round 8 is committed and mirrored. These lanes prepare the freeze while the lead's three decisions are pending; none of
them depends on a decision, and none draws, seals or runs the base.

### Lane R1-57 — revision analysis adapter (U15)

A new module `src/pccap/revision_v1/analysis.py` (+ `tests/revision_v1/test_analysis.py`) that turns the Stage 4 cell
outputs into the pre-registered contrasts: inputs are the R1-13 stream summaries (`results/R1/streams_revision/<tag>/`
and `stream_eval_<tag>.json`), the endpoint summaries (`results/R1/endpoints/<tag>/summary.json`) and an expected
inventory (cells × conditions × realizations × orders) supplied independently of the outputs. Per contrast: paired by
item and update order across conditions, clustered by realization; report point differences, cluster-bootstrap and
paired intervals labelled preliminary at three clusters; the classifier from the protocol draft §6 (ΔRET-GS ≥ 0.05
with lower bound > 0; ES loss ≤ 0.02; LS loss ≤ 0.01) applied per dataset; missing cells, failed acquisitions and
unavailable endpoints retained in the denominators, never imputed. Tests on synthetic inventories with known answers,
including a missing-cell case and a case where the v0 `paired.py` conventions (0.02 margin, fixed arm names) would give a
different verdict. Done-when: the module runs on the existing development outputs as a dry run (`--dry-run` prints the
table with a "development, not confirmatory" banner) and the tests pass.

### Lane R1-58 — fresh-stream draw / split / seal recipe, dry-run only (U06, U07)

A script `scripts/r1_58_draw_streams.py` bound to `manifests/revision_v1/exclusions_frozen_v3.json` and the candidate
inventories (`counterfact_fresh_candidates_v1.json`, `zsre_fresh_candidates_v1.json`): for a named source decision
(`--counterfact-source strict|exception`, both readings supported), draws three realizations per dataset (zsRE, CounterFact, and MQuAKE once R1-D4's inventory exists) of 1,000 edit
items plus 100 outside items and the near-miss / revision reserves, disjoint across roles and realizations, stratified
as the protocol draft §3 states, with an explicit shortfall rule; writes an unsealed draw manifest with every id, hash
and RNG parameter, and refuses to seal or to write a payload unless `--i-am-the-lead` is present (which you must not
pass). Tests: determinism, disjointness, register exclusion, refusal paths, both source readings, shortfall reporting.
Done-when: `--dry-run` reports counts per role and realization for both readings without writing anything but the
report under `logs/`.

### Lane R1-59 — Stage 4 protocol draft v2 (U02, U08, U16)

A new document `docs/R1_stage4_protocol_draft_v2.md` that reconciles your draft with what is now measured: primary
condition v3 (the gate, `primary_condition_v3.json`) and v2 as the no-gate comparison; the P1 profile numbers
(`results/R1/p1_profile/*/summary.json`, `docs/R1_stage2_notes.md` §"R1-40c P1"); the unseen endpoint at
100/300/1,000 with and without the gate; the drift recount; the endpoint costs (R1-43 151 s, R1-44 ≈ 75–200 s, drift
≈ 165 s per checkpoint for the full 128-window assay). The lead has decided (DEC-044) that the scope is NOT cut: price the full matrix — now 8 conditions × 3 datasets (MQuAKE-CF added, DEC-045) × 3 realizations × 5 orders = 360
cells — from the measured components (cells × wall hours with the 0.2 reserve, per condition and dataset, shared
training charged once) and state which U-gates the measurements close; do not propose reductions. Keep U01–U18 with their status updated; do not close a gate the lead owns.

### Lane R1-D4 — MQuAKE-CF preparation (DEC-045; CPU; highest priority of the round)

Source: `/home/derp/cap/assets/data/raw/mquake/MQuAKE-CF.json` (sha256 in `manifests/datasets.json`; MIT). Produce, as
new files, `scripts/r1_d4_prepare_mquake.py`, tests, `manifests/revision_v1/mquake_items_v1.json` (item inventory with
hashes, no payload text needed in the manifest) and the prepared resource under
`/home/derp/cap/assets/data/prepared/revision_v1/r1_d4_v1/`. Rules: (1) one item per unique (subject, relation_id)
rewrite; when several instances give different `target_new` for the same pair, keep the first by `case_id` and record
the conflict; (2) prompt = the cloze template with the subject filled (`"{} is employed by"` → `"Carl Sagan is employed
by"`), answer = `target_new.str`, aliases = the matching `new_single_hops[].answer_alias` (plus the string itself),
paraphrases = the `question` form (and any second cloze/question variant found in `single_hops`/`new_single_hops` for
the same triple); (3) locality prompts = two same-relation cloze prompts of other subjects with their `target_true`
(the CounterFact neighbourhood convention), never sharing the subject; near-miss reserves the same way, disjoint from
the locality prompts; (4) composition inventory = the instances' `questions` (three paraphrases), `answer`/`new_answer`
with aliases and the `orig` triples, keyed to the edit items they depend on, marked `verified_source: MQuAKE` — these
are the direct composition questions R1-43 lacks; (5) exposure: drop every item whose normalized subject is in
`manifests/revision_v1/exclusions_v3.json` (NFKC, casefold, whitespace) and list the 924 dropped; emit the MQuAKE
subject inventory for the register's next version; report the overlap with the zsRE fresh candidates; (6) no teacher,
no base, no draw, no seal: the teacher/eligibility pass is the orchestrator's. Counts to report: items, subjects,
relations, answer-token histogram (use `pccap.data.tokenize`), locality coverage, composition questions per item.

### Lane R1-X8 — counter-review of R1-55, R1-56 and the Stage 2 report revision

Review `scripts/r1_55_p1_profile.py`, the R1-56 gate in `src/pccap/revision_v1/learner.py` (`_rare_overlap`,
`rare_overlap_min`, `rare_df_max`), its test, the extended `scripts/r1_44_unseen_run.py` (pool fillers and
pool-sourced outside prompts) and `docs/R1_stage2_report.md` against the notes and the result files. Questions to
answer: is the document-frequency cache invalidated correctly under supersession and removal; can the gate's
rarity criterion be gamed by a query that repeats a record's rare token; are the pool-sourced fillers and outside
prompts admissible as development evidence and correctly labelled; are the report's numbers bound to files; is
anything in the report stated as established that the evidence does not support. Output `logs/review_r1_56.md` with
edit requests for the orchestrator.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
