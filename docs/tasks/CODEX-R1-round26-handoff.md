# Codex round 26 handoff

Completed the three independent CPU lanes: **R1-77f, R1-D9e and R1-49i**. Prepared candidate v9,
operator forms and claim ledger previews for the three dependent lanes. No commit or staging;
Claude's GPU chain Q, live driver/backend and installed `src/pccap` were left untouched.

## Completed and verified

- **Queue:** the matrix solo ceiling already includes 1.5 times measured solo cost; workers2
  apply 1.15 once. Ordinary failure retries once from certified state; a second leaves an
  incomplete cell and advances without draining the other worker. The count survives restarts
  with the same receipt root. Host/memory/lease stops and unknown-cost reconciliation remain.
  [Policy v2](../R1_stage4_queue_concurrency_v2.md), [task](R1-77f.md).
- **Near family:** adopted DEC-061 source pairing is shared by constructor and seal validation.
  Analysis recomputes exact bounded neighbour-versus-cap-off equality; missing planned slots
  remain missing. Role plans, certified evidence and all 93 Hall checks are current.
  [Task](R1-D9e.md), [operative review](../../logs/r1_round26/near_final/r1-d9e-real-pool-review.json).
- **Protocol:** [final v5.2-D text for signature](../R1_stage4_protocol_v5_2_D_final.md),
  [matrix](../../manifests/revision_v1/run_matrix_v5_2_D_DEC061.json) and
  [schema contracts](../R1_stage4_matrix_schema_DEC061.md) preserve scope, coordinates, cadence
  and the 63-interval family. Costs, final populations and execution remain unadmitted.

The combined regression suite passed **107 tests** (23.25s), binding/approval checks passed
**3 tests** (1.26s), and the final complete synthetic producer→seal→TinyBase→analysis rehearsal
passed **2 tests** (254.32s) for both 300- and 1000-edit cadences. That final rehearsal explicitly
binds DEC-061 into receipts and matrix and verifies 100 planned/evaluated/preserved near cases.
These are contract tests with a synthetic EOS head, not model-quality or GPU-cost measurements.
Changed/new Python files pass Ruff; `git diff --check` passes. Logs are under `logs/r1_round26/`.

## Finding to retain in the scientific interpretation

The real-pool convenience diagnostic has substantial missing pair availability:

| Dataset | Matched / 300 planned | Missing | Distinct source families in eligible pool |
|---|---:|---:|---:|
| zsRE | 61 | 239 | 728 |
| CounterFact | 210 | 90 | 34 |
| MQuAKE | 221 | 79 | 35 |

It takes the lexical first 600 compatible subject representatives, alternates support/neighbour,
and divides them into three groups. It uses no RNG and creates no real reservation. These are
**not forecasts of the final draw**. They demonstrate why a role-capacity certificate does not
guarantee 100 matched near cases. Keep evaluated/planned counts and unavailable full-inventory
rates; do not change the role RNG or retry seeds to improve coverage. The adopted family also
measures template/relation specificity, not semantic nearest-neighbour robustness.

## Dependent lanes and exact continuation

[Candidate v9 preview](../../manifests/revision_v1/freeze_candidate_v9_preview.json) verifies
728 bindings and all current unsigned request previews. Its profile snapshot has **3/8** exact
corrected MQuAKE results: R1_nonlearned, R1_learned_ff_v2 and v0_stable. It leaves five profiles
and execution plan v2 pending. Full endpoint/process cost admission and actual lead signatures
also remain outstanding. The candidate still lists 17 open gates; U10 was closed previously.
No evidence supports claiming that all gates are now closed.

1. After all eight corrected chain Q profiles and `docs/R1_execution_plan_v2.md` exist, run
   `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_63h_refresh`.
   It refuses missing inputs and creates new final v9 candidate plus unsigned v4 forms.
   It does not overwrite the preview, sign forms, draw, seal, freeze or launch.
2. Use [operator sheet v4](R1-D9-operator-sheet-v4.md). The order is clearance → lead seed/draw →
   endpoints → seal → final freeze → two-worker queue. Obtain a fresh exact request after
   every prerequisite or seed change. Do not sign the preview hashes and reuse them later.
3. With final v4 inputs and the signed current full-endpoint cost receipt, run
   `JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht4f_claim_ledger --cost-receipt <receipt.json>`.
   Final v6 refuses absent profiles/plan or an unapproved/mismatched receipt.
   [Ledger preview](../talk_claim_ledger_v6_preview.md) keeps missing results explicit and binds
   the three completed profiles. Prior κ/tail/stress claims remain in v5 with their original limits.

These publishers bind snapshots, so further code changes require a separately reviewed version.
The `--preview` outputs already exist and are not overwrite targets. Final v9 is still a dry
inventory; actual freeze and launch require the owner workflow and real population receipts.

## Files and ownership

Edited scripts: `r1_77_queue.py`, `r1_d10c_endpoints.py`, `r1_d9_receipt_core.py`,
`r1_d9_receipts.py`, `r1_58c_draw_seal_preflight.py`, `r1_49g_analyze.py`.
New scripts: `r1_77f_scheduler.py`, `r1_d9e_near_family.py`, `r1_d9e_review.py`,
`r1_49i_protocol_matrix.py`, `r1_63h_refresh.py`, `ht4f_claim_ledger.py`.
Tests changed/added match those lanes; task records R1-77f/D9e/49i/63h/58f/HT-4f describe each.
New protocol/policy/schema, matrix, candidate preview, forms, analysis inventories and evidence
logs belong to this round. Test-generated queue locks and round24-named rehearsal artifacts
come from the existing fixtures; the current verification logs identify their runs.

Exact pre-edit source bytes are archived under `logs/r1_round26/source_snapshot/`; old evidence
keeps its original SHA and points to the matching historical snapshot when promoted. Use only
`near_final/` and assets `r1_d9e/round26_final/` as operative review outputs. The first review
was superseded for import-order cleanup; its helper's original bytes are also archived.

Do not mix Claude-owned `results/R1/chain_q.progress`, active profile logs/results or
`logs/r1_round25/pytest-orch/` into this lane's attribution. They were present or produced by
Claude during this work. No taskboard/ongoing/lead_queue edits were made. Experimental completion
remains **October 9**, with the talk on **October 15**.
