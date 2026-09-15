# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-14 18:30 EDT (round 9 committed; round 10 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-14-1830.md`. Rules §1 are
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
- **Round 9 committed by Codex** (`678c703`): analysis adapter (R1-57), draw recipe dry-run (R1-58), protocol v2 (R1-59, 360 cells),
  counter-review (R1-X8; cache repair applied), MQuAKE preparation (R1-D4: 6,043 items, composition inventory).
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

## 3. Lanes for Codex — round 10 (CPU; open now)

Round 9 is committed (Codex's own commit `678c703`) and mirrored; the cache repair from R1-X8 is applied (the two
test-maintenance patches no longer applied — the contexts had already changed — and the tests they targeted pass).
Standing rules as before: new files only; CPU only; no teacher, base, draw or seal; edit requests as patches.

### Lane R1-D1g — exclusion register v4 (DEC-042 exception, DEC-045 MQuAKE)

A new policy/register version binding, in the style of R1-D1f: (1) the CounterFact reason-specific exception
(waive `old_eligible:counterfact` only; every other reason active) applied to the R1-D2 inventory, so the 12,246
conditional candidates become the CounterFact candidate list; (2) MQuAKE subjects (`r1_d4_v1/subjects.jsonl`) added
as a new exposure source once the pool exists (`manifests/revision_v1/mquake_pool_v1.json`, written by the
orchestrator's teacher pass; if absent, bind the R1-D4 subject inventory and mark the pool binding pending); (3) the
159 zsRE-overlap subjects resolved by a stated rule (default: they stay in the zsRE fresh candidates and leave the
MQuAKE inventory, since zsRE's fresh draw is the scarcer resource — say so if you disagree with the default); (4)
cross-dataset exposure counts for all three datasets. Output: `manifests/revision_v1/exclusions_frozen_v4.json` with
child hashes, `scripts/r1_d1g_freeze_register_v4.py`, tests. No draw.

### Lane R1-60 — composition endpoint module (U09/U11)

`src/pccap/revision_v1/endpoints_composition.py` + tests on TinyBase, in the style of `endpoints.py` and
`endpoints_unseen.py`: input = the R1-D4 composition inventory (`r1_d4_v1/composition.jsonl`; a case = a multi-hop
question with three paraphrases, the pre-edit answer, the post-edit answer with aliases, and the edit items it depends
on). Evaluation on an independent clone: teach the dependency edits (all of them, in order), then decode each
paraphrase; success = the post-edit answer (alias match, greedy ≤ 32 tokens, newline/EOS stop), reported per
paraphrase and per case (all three); also the cap-off answer and whether the pre-edit answer reappears. Cases whose
dependencies conflict (the 19 conflicts) or include an excluded item are reported as unavailable, never imputed.
Denominators: planned cases, evaluable, scored. Provide the inventory selection rule for the confirmatory runs (which
cases attach to which realization: only cases whose dependencies are all in that realization's edit stream) and its
expected-count arithmetic for R1-58.

### Lane R1-61 — Stage 4 cell driver with comparator adapters (U11/U17)

`scripts/r1_61_cell_driver.py` (+ a module under `src/pccap/revision_v1/` if you prefer, + TinyBase tests): runs ONE
matrix cell — condition × dataset × realization × order — from a sealed-stream manifest (use the R1-58 dry-run
inventory format; on TinyBase use synthetic items) with checkpoints at 100/300/1,000: at each checkpoint the retention
(RET-ES/RET-GS over all edited items), locality (LS), unseen-prompt (R1-44 adapter), and at the final checkpoint the
near-miss/revision (R1-43), composition (R1-60) and drift assays; ledger charging per phase; state hash before/after
every endpoint (restore equality); resume from the last completed checkpoint; refusal on any code-identity or manifest
mismatch; all outputs to a new directory named by the cell identity. Comparator adapters: `R1_learned_ff` (v3: gate)
and `v2` (no gate) via `RevisionCap`; `R1_nonlearned` (random reader, gate 0.93); `v0_stable` (`revision_v1/v0_stable`);
`matched_update` (R1-15); `v0_live_C1/C2` (`pccap.harness.arms.make_learner`) — each through the same query-reset and
observer interface (memory bytes, firing, active records). Where an adapter's observer cannot be provided
(v0 caps have no selection object), report the field as unavailable rather than zero. The orchestrator validates the
driver on the real base and runs it.

### Lane R1-57b — analysis adapter: three datasets, 360 cells, composition and unseen endpoints

Extend `analysis.py` by new files only (`analysis_stage4.py` or similar): the expected inventory generator for
8 × 3 × 3 × 5 cells with the checkpoint set, the composition and unseen endpoint summaries as secondary outcomes
(descriptive unless a margin is registered — U14), the v2-vs-v3 comparison as a declared secondary contrast, and
missing-cell accounting per condition. Dry run on the development outputs with the "not confirmatory" banner.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
