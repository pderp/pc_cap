# HT-4f — round26

Status: preview ready; final waits for chain Q and signed costs.

Agent: Codex. Round26, CPU only. No staging/commit, GPU work, actual draw, real seal, freeze or lead signature. Source/base/driver/backend and Claude's chain Q outputs were not edited. Resources are under `assets/runs/pc_cap/R1/r1_d9e/round26_final/`.

Inputs: three completed corrected MQuAKE profiles, exact recipes/receipts, CPU lane outputs,
v5 claim history. Outputs: `scripts/ht4f_claim_ledger.py`,
`docs/talk_claim_ledger_v6_preview.md`, `logs/r1_round26/talk_evidence_v6-preview.json`
and bound profile inventory (15current claims; priorκ/tail/stress history linked in v5).

Completed corrected profiles: R1_nonlearned, R1_learned_ff_v2, v0_stable. Five pending slots
are explicit; no old ChainM locality0/50 artifact is substituted. Costs distinguish driver
attempt timing from whole-process/full-endpoint admission. Near availability/empty-baseline
and limited concurrency evidence qualify claims. October9stop/October15talk and κframing retained.

Verify: exact recipe/payload hashes, final receipt self-hash/report/result identities and fixed
locality/retention inventories; all claim hashes checked at snapshot. Final publisher refuses
absent profiles/planv2 or missing/unapproved/mismatched cost receipt. After finalv4inputs:
`JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.ht4f_claim_ledger --cost-receipt <signed-current-receipt.json>`.
Done-when: finalv6aftercompletechainQandcostadmission; not yet claimed done.
Cost:0GPU seconds. Deviation: useful snapshot preview only while dependencies run.
Unresolved: fiveprofiles, executionplanv2 and signed full endpoint/process costadmission.
Questions for lead:none; do not treat provisional wall-clock estimates as admitted ceilings.
