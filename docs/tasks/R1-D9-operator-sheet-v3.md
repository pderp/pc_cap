# R1-D9 operator sheet v3 — option D, unsigned

Work from `/home/derp/cap/pc_cap`. The experiment deadline is **October 9**.
Use [inputs v3](R1-D9-inputs-v3.json), [protocol v5.2-D](../R1_stage4_protocol_draft_v5_2_D.md)
and [matrix v5.2-D](../../manifests/revision_v1/run_matrix_v5_2_D.json).
The context rule is adopted; teacher/role completion and final admission remain open.
The new [R1-73d run list](R1-73d/ordered-runlist.md) corrects development locality; its eight GPU reruns remain owner work.
Both final construction and seal now refuse locality/edit/paraphrase collisions across the complete stream.
Dry clearance/draw/seal validate these bound inputs and correctly refuse execution.

## 1. Teacher review and certification

Operative v5 has 6084 / 6121 / 2214 preteacher items and 6084 / 6121 / 2161 subjects
(zsRE / CounterFact / MQuAKE). Demand is 4050 / 4050 / 1950 subjects. The current dry run
has no preteacher capacity deficit; final teacher filtering and joint-role feasibility can still fail.
Its 14419 rows imply at most 461408 generated tokens. The historical-throughput estimate is
387 seconds, with a 774–1936 second planning allowance; this is not a new GPU timing.

The CPU inspection command is:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d10b_teacher_review \
  --evidence /home/derp/cap/assets/runs/pc_cap/R1/r1_d10g/round24_v2/evidence-v5-operative.json \
  --evidence-sha256 321bcc4cf14de893caa3d4f5330440f81334e47d91b95e349cf2ca81b2ad843f \
  --matrix manifests/revision_v1/run_matrix_v5_2_D.json \
  --matrix-sha256 dc395f082744d2427d9f4c4a92cde0a98b28080178e7ec435467ba78aa2fe9ba \
  --output /home/derp/cap/assets/runs/pc_cap/R1/r1_d10b/round24_v2 \
  --log-dir logs/r1_round24/teacher-v2
```

For an owner GPU run, use CUDA at the scheduled boundary, one lease, the existing memory guard
and `--execute`. An exploration flag does not confer clearance. Resume only an identical saved
contract; changed evidence/code/layout requires a new run version. Do not change an active run.

**If chain N already completed**, use the same current evidence/matrix arguments, a new output
directory and log directory, plus `--certify-from-run <completed-assets-run>`,
`--completion-receipt <owner-receipt.json>` and `--completion-sha256 <its-SHA256>`.
Keep the CPU environment and omit `--execute` and the exploration flag. Certification checks
the exact completed contract, all chunks, source hashes, eligibility coverage, token checks,
E.2 scoring, base/tokenizer identity and the owner's completion/lease receipt. It never decodes.
It can certify a completed superset but cannot invent missing rows. A v4-only run lacks 88
restored v5 items; that run alone must refuse. Preserve its receipts and arrange a separately
versioned complete review rather than treating the missing rows as passed.

Historical producer bytes used by the old evidence/run are preserved under
`logs/r1_round24/producer_snapshot/`; certification verifies their original hashes.
Do not replace a historical producer hash with the current source hash.

## 2. Merge teacher and role review

Use `scripts.r1_d10c_endpoints merge-review` with the completed/certified teacher resource and
its SHA, `--role-plan /home/derp/cap/assets/runs/pc_cap/R1/r1_d10g/round24_roles_v2/role_plan.json`,
`--role-plan-sha256 479bef357e37c39d214f0fd34d159559a0cbb726cf3f2f1d687a9383930cd161`,
and a new assets `--output`. Bind the merged resource in `d9.clearance.evidence`.
The catalog has 9218 composition cases; 4981 are structurally available before a draw.
Individual role counts are not a joint allocation certificate. Review the proposed zsRE
same-template/different-subject near family explicitly and retain every missing denominator.

## 3. Clearance, draw, endpoints and seal

1. Run `../venv/bin/python -m scripts.r1_d9_clearance --inputs docs/tasks/R1-D9-inputs-v3.json --dry-run`.
   Require complete review, global disjointness, Hall feasibility and usable capacities at least
   4050/4050/1950. Only after review may the lead close/sign the **current** clearance request
   in the v3 authorization template. Rehash/rebind it, require a ready dry run and then use `--execute`.
   Bind the emitted joint-clearance receipt.
2. Close the v3 protocol and RNG forms, including the near-family review, explicit extension
   decision and one admitted master seed. Set that same seed in `d9.draw.master_seed`.
   The [chain exposure inventory](../../logs/r1_round24/r1-d10g-chain-inventory.json) and the [new locality/declaration supplement](../../logs/r1_round24/r1-d10g-promotion-v2.json) cover
   79 declarations, including R1-73d and the two probe recipes; supplement any later/new payloads before attesting
   that exposure is current. Run `scripts.r1_d9_draw --inputs ... --dry-run`, sign its fresh
   request, rehash/rebind, require ready and use `--execute`. Bind the actual draw receipt.
   Never retry seeds or substitute entities to overcome a shortfall.
3. Fill the actual draw binding and admitted extension decision in
   [construction inputs v3](R1-D10c-construction-inputs-template-v3.json). Run
   `../venv/bin/python -m scripts.r1_d10c_endpoints construct --spec docs/tasks/R1-D10c-construction-inputs-template-v3.json --dry-run`.
   Review fixed denominators and missing rows, then use `--write` to create unsealed resources.
   Close the v3 endpoint receipt with exact draw/reservations/bundle/independent-population hashes,
   role disjointness and dependency review; bind it and both resources in the D9 inputs.
4. Run `scripts.r1_d9_seal --inputs ... --dry-run`, review and sign its current request, rehash/rebind,
   require ready and use `--execute`. Bind the emitted seal receipt. A seal does not authorize launch.

Every schema-3 prerequisite/authorization receipt must bind contract_version=2, dataset_layouts,
layout_sha256, register, matrix and protocol. This also applies to subsequent cost/schedule/gate
metadata checked by preflight. Uniform v2 forms cannot be reused. The `inspection_only_request_sha256`
values are previews, not signatures. Prerequisite changes invalidate downstream request hashes.

## 4. Idle boundary, freeze and launch

The orchestrator applies [R1-77d](R1-77d-edit-request.md) **after M/N/O** at an idle boundary.
Until then installed source, the live development driver and the sealed backend remain unchanged.
The patch changes installed/driver/backend identities. Rebuild final recipes with
population_contract_version=2 and matrix binding, the exact schema-2 executable protocol, backend
bindings, costs and freeze candidate v8. The v7 binding in these inputs is explicitly historical;
the operative freeze candidate is deliberately null until rebuilt. Final code changes also
invalidate D9 request digests through their implementation bindings: regenerate any affected
drafts and obtain new exact approvals before execution. Never silently refresh signed receipts.

Validate all U01–U18 closures, measured failure-inclusive ceilings and the September 20 schedule
decision. Then admit the final freeze, construct final queue bindings, run queue dry inspection
and launch under the existing lease/budget controls. Secondary MQuAKE results stop at actual 300;
all its 1000-edit primary comparisons remain unavailable within the original 63-interval family.

The full synthetic rehearsal tests the production stage APIs with synthetic source/approval
fixtures and the prepared patch loaded only in memory. Its TinyBase EOS test head and zero
learning steps make it a contract/execution test, not a model-quality or GPU-cost measurement.
See [R1-58e](R1-58e.md) and [handoff](CODEX-R1-round24-handoff.md).

## 5. Two-worker queue mode

[R1-77e](R1-77e.md) implements the newly admitted two-cell concurrency. Inspect the current draft with
`../venv/bin/python -m scripts.r1_77_queue status --matrix manifests/revision_v1/run_matrix_v5_2_D.json --workers 2 --dry-run`.
Only after final freeze/queue admission, use `run --execute` with the final matrix/bindings,
`--workers 2`, a new queue receipt root, the admitted process-hour budget and the usual owner GPU lease.
The draft matrix above remains unlaunchable.

Review the [concurrency policy](../R1_stage4_queue_concurrency_v1.md) when setting costs: each active
cell reserves1.65× its bound solo wall ceiling from one shared account, and the second launch requires
at least6GiB MemAvailable. Accounting sums process durations, including overlap; elapsed wall-clock
planning is separate. A failed worker drains the other cell before stopping; normal resume rules apply.
Bind both queue implementation files and the policy in final queue/freeze-v8 admission.
