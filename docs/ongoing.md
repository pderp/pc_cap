# Ongoing work (the single current log; previous versions are dated under `docs/archive/`)

Rewritten 2026-09-11 06:55 EDT, updated 2026-09-15 15:40 EDT (round 13 committed; round 14 lanes) by the orchestrating session for
the concurrent round of `docs/updated_plan7.md`. Previous version: `docs/archive/ongoing-2026-09-15-1540.md`. Rules §1 are
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
- **Round 13 committed by Codex** (`c238f02`): register policy v5 (4,218 MQuAKE subjects), protocol v4, dev-loader and
  selection-trace modules (orchestrator wires them), R1-65/66 review (collision rate 2.1–2.3 %), R1-68 integrity components
  (partial). Clean driver profile: 1,252 s per 300-edit cell; 1,000-edit cell ≈ 49–66 min.
- **Primary condition v5** (DEC-049/050; `primary_condition_v5.json`): question-null family seed 2, averaged checkpoints 150–300;
  mean RET-GS 0.803 (zsRE 0.98 / CounterFact 0.82 / MQuAKE 0.61), ES 1.00, LS ≥ 0.98, zsRE unseen 10 / 12 / 9 % at
  100 / 300 / 1,000, near-miss 100/100, revision 100/100, full-assay drift +0.0022 nats. Driver: 1,262 s per 300-edit
  cell (overhead = per-phase clone/restore ≈ 545 s + one-at-a-time drift 506 s); the incremental profile changes nothing.
- **DEC-048 (option C)**: true-fact query presentations are not counterfactual-edit exposure; MQuAKE capacity 4,218 vs
  4,050 demand; full scope stands. **Round 12 committed by Codex** (`cee3d79`): population memo, protocol v3, matrix v4,
  MQuAKE counter-review (notes corrected). Reader status: fixed-locality readers (R1-65) keep retention (MQuAKE 0.79,
  zsRE 0.98, CounterFact 0.86) but zsRE unseen false fires stay 30–52 % at 100 records; question-form nulls (R1-66)
  bring them to 5 % at a retention cost; a 35 % rate and the clean driver profile are running.
- **Round 11 committed** (`8f82316`): self-contained MQuAKE slices (train 500 / dev 100, v3), development payload builder and
  execution mode for the cell driver (materialized base copy, checkpoint-identity helper), exposure trace audit (no
  certified releases; MQuAKE ≤ 2,829 subjects even if every review candidate cleared), freeze candidate v1 (dry).
- **Round 10 committed** (`3e8a980`): register v4 + MQuAKE exposure supplement, composition endpoint module, Stage 4 cell
  driver with all comparator adapters, three-dataset analysis. MQuAKE capacity deficit found (2,100 distinct candidate
  subjects vs 4,050 needed under conservative reservations) → R1-D4b.
- **MQuAKE reader**: proposed primary v4 (three pools; `primary_condition_v4.json`): zsRE 0.95–0.98, CounterFact 0.76–0.83,
  MQuAKE 0.56–0.79 (seed-sensitive); DEC-046/047 proposed defaults.
- **Round 9 committed by Codex** (`678c703`): analysis adapter (R1-57), draw recipe dry-run (R1-58), protocol v2 (R1-59, 360 cells),
  counter-review (R1-X8; cache repair applied), MQuAKE preparation (R1-D4: 6,043 items, composition inventory).
- **Round 8 committed** (`c401f55`): Stage 4 protocol draft (R1-49, gates U01–U18), frozen register binding
  (R1-D1f, `exclusions_frozen_v3.json`), ordinary-text null spec (R1-50b), R1-24 review (R1-X7; qualifications applied
  to the notes).
- **DEC-045**: MQuAKE-CF is the third dataset (`assets/data/raw/mquake/`); CounterFact stays (which needs the DEC-042
  exception). DEC-043 accepted, DEC-044 keeps the full matrix (now 360 cells). Then the freeze (R1-41). No draw, seal or launch before those.
- Rules unchanged (§ top); Codex: new files only, CPU only, no sealed payloads, no real-base execution; edit requests
  as patches under `docs/tasks/`. Tests under `tests/revision_v1/` (CPU) must pass.

- **Round 16 committed** (`2e7ac38`, 2026-09-16): R1-X12 selection review (42 candidates, 15 admissible, unique winner;
  zsRE unseen 10/100, Wilson 95 % 5.5–17.4 %; occupancy flatness unproved because the outside sets differ), R1-68c
  instrumented driver with batched drift (owner re-profile running), R1-72 schedule scenarios (331–452 GPU h vs 306
  available), HT-1b v5 tail audit (v5 zsRE mean +0.0022 nats but max 8.7 nats and 17 positions > 0.1; CounterFact
  +0.006## 3. Lanes for Codex — round 32 (CPU; open now; posted 2026-09-18 07:00 EDT) — the fidelity gate

Round 31 is committed and mirrored. Chain S (three cells left) runs until ≈ 08:30; the R1-63l backend patch is applied
after it. Priority order: **R1-49l → HT-7 → HT-6 → R1-58l → R1-63m → X19 → HT-4f.** Rules as in round 22.

### Lane R1-49l — provenance and interpretation of the fidelity limit (first; decides whether the lead has a question)

Chain S shows the primary's full-validation mean KL 0.0055 nats against the registered KL ≤ 0.001. Trace the limit:
DEC-033 D-R3 ("fidelity KL ≤ 1e-3, loss increase ≤ 0.01") and its use in DEC-047 (the S1 continuation
certification), plan 9, and every protocol draft v1 → v5.2-D.2: was the KL limit registered as (a) a fidelity gate on
the *continued base* only, (b) a drift gate on the *cap* (cap-on vs original base) at the final checkpoint, or (c)
both? Quote the exact sentences. Then state what the current D.2 classifier does with a cap cell that fails (b):
which label, whether the primary comparisons are still computed, and how the DEC-058 classifier interacts. If the
registered meaning is (a) and D.2 silently extended it to (b), say so — that is a scope change the lead must decide
(the orchestrator posts it as Q17 with the options: keep the extension as a declared secondary fidelity benchmark;
or bind the cap drift gate at the NLL-increase limit ≤ 0.01 that the sampled assays have always used, with KL
reported descriptively). No threshold is changed by this lane.

### Lane HT-7 — concentration statistics for the full-validation endpoint (registered descriptive; small)

The lead asks that every future cell record how the fidelity loss is distributed across contexts. The vectors are
already stored; add to the R1-68f report, `r1_49g_analyze` / R1-75 and protocol D.2 (descriptive, no threshold):
share of total KL (both references) in the top 0.1 % / 1 % of positions and top 1 % / 5 % / 10 % of windows; the
number of positions carrying 50 % of KL; per-window mean-KL quantiles (median, p90, p99, max) and the counts of
windows above 0.001 / 0.01 / 0.1; the untouched-position fraction (|Δloss| < 1e-6); a Gini over positions; the
same for positive loss harm. Compute retroactively for the chain S cells (a CPU script over the NPZ files) and
reproduce the orchestrator's numbers for cell 1 (notes §"How the full-validation fidelity loss is distributed").

### Lane HT-6 — full-validation fidelity report over chain S (after the four cells)

For each of the four cells: mean KL and NLL increase against both references, ES95 / ES99 / max, exceedance
counts, coverage, the overlap gate result, the phase cost; the same statistics on the sampled 128 windows for the
same checkpoint (are the sample and the population consistent?); a short reading for the talk under the DEC-054
framing (the tail statement on 245k positions), kept separate from the classifier question of R1-49l.

### Lane R1-58l — cost receipt v4 (after chain S; as posted in round 31)

### Lane R1-63m — candidate v14, forms v9, sheet v8 (after R1-58l and the backend patch)

### Lane X19 — re-review

### Lane HT-4f — claim ledger v6

## 3a. Repository size policy (lead, 2026-09-18)

No committed file above 45 MB (GitHub warns at 50, refuses at 100). Enforced by `.githooks/pre-commit` →
`scripts/repo_size_policy.py check` (repo-local `core.hooksPath`). Synthetic rehearsal / operator-test / certification
/ pytest fixture trees are ignored (`.gitignore`) and stay on disk; regenerable or bulky data goes under `assets/`;
a genuine JSON artifact that must be in the repository is split with `scripts/repo_size_policy.py split FILE.json`
(byte parts ≤ 40 MB + an index with the whole-file sha256; `join` reassembles). Codex: write fixture outputs only under
the ignored directories or `assets/`, and name in the handoff any new directory that should be ignored.

## 4. Interfaces and coordination

As before: `pccap.contracts`, `pccap.bases.gpt2_jax`, `pccap.bases.bp.BPBase`, `pccap.harness.arms.make_learner/
router_for`, `pccap.harness.runs`, `pccap.harness.stage_s2.load_dev_items`, `pccap.data.tokenize`, `pccap.data.decode`,
`pccap.harness.ledger.Ledger`, `pccap.harness.lease.gpu_lease`, the grammar modules, `pccap.analysis.s7_01`,
`pccap.analysis.s1_p4`. Questions for the orchestrator: a dated line under "## Agent questions" in
`docs/lead_queue.md`; board rows: your own only (the orchestrator mirrors completion records it finds).
