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

## 3. Lanes for Codex — revision v1, next (CPU; open now)

R1-00 and R1-X0 are done and mirrored; R1-20's generator is installed as `pccap.revision_v1.episodes` (your repair bundle
applied verbatim). The plan-9 amendments are in `docs/tasks/R1-X0-response.md` / DEC-034. Next lanes:

### Lane R1-D1 — exclusion register and fresh-draw candidate inventory (X0-09; DEC-034(c))

`scripts/r1_d1_exclusions.py` → `manifests/revision_v1/exclusions.json` (versioned): every normalized subject in both old
eligible pools, v0 development and S0, the challenge sets, all 496 exposed S7 candidate subjects (zsRE) and 141 (CounterFact),
and every subject any revision-development episode has emitted (read `logs/r1_codex_20260913/episodes_v2/`); then the
MEND-train candidate inventory after exclusion with raw-record and deduplicated-subject counts, alias/entity resolution
notes and unresolved mentions in paraphrase/locality text. No sealing, no E.2 pass (the orchestrator runs that on the GPU).
`docs/tasks/R1-D1.md`.

### Lane R1-20b — CounterFact episode set for Stage 2 and the generator partition manifest (X0-10)

Finish the natural-data path for CounterFact (zsRE is an evaluation stream only, DEC-034(b)); the partition manifest for the
extended grammar generator (reserved latent scopes / entities / surface families; ≥ 2 unseen paraphrases per emitted item or
the episode is rejected whole; final-generation version and seed reservation). The teacher preservation targets you need
(cap-disabled greedy answers and top-k logits on every episode query prefix) are produced by the orchestrator's GPU pass once
you write the prefix list to `manifests/revision_v1/teacher_targets_request.json`.

### Lane R1-X1 — counter-review of the Stage 0 diagnosis memo (OPEN NOW: `docs/R1_diagnosis.md`, 18:15 EDT)

Read-only; `logs/review_r1_diagnosis.md`. Inputs: `results/R1/diagnostics.md`, `diagnostics_{C1,C2}.json`, `traces_{C1,C2}.jsonl`,
`scripts/r1_diagnostics.py` (f8c8c74). Questions to answer: is the four-policy comparison sound (oracle verification rule,
shadow-key rebuild, teacher-forced exactness); does the memo's locus claim follow; what would change it. Also DEC-035.


### Lane R1-23 — data-separation and update-path audits (can start now on the installed code)

Stage 1–2 code is installed under `src/pccap/revision_v1/` (`contracts, observations, memory, reader, controller, adapt,
learner, train, v0_stable`) with tests under `tests/revision_v1/` (72 pass; `epc_train` added) and the loss-source table in
`docs/revision_v1_losses.md`. Audit targets: (1) `RevisionCap.predict` and `selection_for` never receive or read a
target (signature and data-flow); (2) `adapt_record` changes only the taught record's code (and creates/supersedes one
record); (3) `train.py` uses labels only through `LabeledEpisode.query_labels` and applies L3 only to preserve roles;
(4) the observation encoder is write-free (no `Write` reaches `base.forward` in the observation path); (5) parameter
count and byte accounting claims. Read-only; `logs/audit_r1_23.md`; findings by id.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
