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

- **v0 close-out in progress**: the v3 grammar rerun (DEC-029/030/032) finishes ≈ 17:55 EDT; the post-queue chain then
  re-applies analysis-tree v3 and runs the grammar analyses; the orchestrator writes the confirmatory-grade grammar row
  into `docs/report.md` and `docs/D3_decision.md` and commits. The full-validation drift supplement is done
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

## 3. Lanes for Codex — revision v1, Stage 0–2 (CPU; open now; new files first, edit requests for anything existing)

### Lane R1-00 — baseline reconstruction (guide §0; ≈ 2 h)

`scripts/r1_00_baseline.py` → `manifests/revision_v1/baseline.json`: commit, dirty diff hash, Python/JAX/FabricPC
versions, tokenizer and checkpoint hashes, dtype, device, seeds, dataset hashes; the zsRE reference table reproduced
from the saved records (`results/S4/frozen-confirmatory-v2-84126123/zsre/C1`, `results/S5/…/zsre/{SE-A,SE-E}`) to six
decimals: ES 0.998467 / 0.998533 / 0.662333, RET-ES 0.523667 / 0.522067 / 0.366133, RET-GS 0.139467 / 0.137467 /
0.156333, learning s/run 272.793 / 267.558 / 816.588 — per-realization and per-order records preserved; `docs/tasks/R1-00.md`.

### Lane R1-20 — episode generator, synthetic domain first (guide §2; ≈ 1–2 days)

`src/pccap/revision_v1/episodes.py` (new file; Codex-owned): episodes with a support history of 2–8 facts/rules, one new
edit, ≥ 2 unseen paraphrases, a near-miss, an old-fact query, an unrelated example; two-fact composition only where the
answer is unambiguous; explicit split / entity / paraphrase-family ids and generator seeds; query labels only in
training/evaluation containers. Start from the grammar generator (`pccap.fixtures.grammar_generator`, extended in a new
module, not edited) with an explicit latent scope; then the development editing pools (`manifests/dev/*_dev.json`) with
partition by fact/entity and paraphrase family. Tests under `tests/revision_v1/test_episodes.py` (separation, determinism,
label containment). `docs/tasks/R1-20.md`.

### Lane R1-X0 — counter-review of plan 9 against the three input documents (read-only + `logs/review_plan9.md`)

Where the plan drops, weakens or misreads a requirement of the proposal or the guide; where its budget or calendar is
unsupported; what the fresh-data decision (D-R2) implies for subject disjointness with the S7 inventory.

### Lane R1-23 (later, after Stage 1) — data-separation and update-path audits (guide §2 "Audits").

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
