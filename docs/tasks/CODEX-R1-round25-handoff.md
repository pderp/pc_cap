# Codex round25 handoff

Four CPU lanes are complete. HT-4e has a current, hash-bound v5 snapshot and a tested refresh command;
its eight corrected MQuAKE numerical rows await Claude's GPU runs. No GPU/model execution, real draw,
seal, freeze, staging or commit was performed.

| Lane | Delivery | Remaining owner work |
|---|---|---|
| [R1-64e](R1-64e.md) | 16 zsRE/CF recipes, primary v5, eight calibrated intermediate recipes and eight corrected MQuAKE recipes on the patched identity; all inspected | Run corrected MQuAKE recipes as new attempts |
| [R1-D10h](R1-D10h.md) | Completed-run teacher certification, regenerated/merged roles, 112-declaration exposure snapshot, real clearance dry-run and refreshed unsigned forms | Exact signature and current-exposure attestation; Q15/protocol/RNG and subsequent acts |
| [R1-63g](R1-63g.md) | Candidate v8: 709 exact bindings, three changed request digests, all 18 gate entries with 17 admission gates open | Resolve review/cost gates and perform actual freeze |
| [R1-X15](R1-X15.md) | Independent counts/Hall checks, teacher-baseline audit, saved concurrency ratios, eight findings and proposed factual document patch | Review/apply/version factual corrections; resolve ceiling interpretation and near-family admission |
| [HT-4e](HT-4e.md) | [Claim ledger v5](../talk_claim_ledger_v5.md), pending corrected-result inventory and tested after-run refresh | Refresh after the eight owner profiles finish |

## Ready for Claude

Use [the corrected MQuAKE run list](R1-73d-post77d/ordered-runlist.md). Each command inspects by
default; owner execution adds `--execute` and acquires the lease. The old builder workflow tried to
verify historical code before rebinding. `scripts/r1_64e_rebind_recipes.py` rebuilds the dependency
chain before invoking the existing strict verifiers. No runtime guard was relaxed; payloads, weights,
calibration and experimental settings remain identical. No historical recipe or producer was edited.

For population review use **[R1-D9-inputs-v3-post77d.json](R1-D9-inputs-v3-post77d.json)** and matching
`*-template-v3-post77d.json` forms. Prior v3 drafts remain historical and their request hashes are stale.
The current clearance CLI is:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m scripts.r1_d9_clearance --inputs docs/tasks/R1-D9-inputs-v3-post77d.json --dry-run
```

It exits 2 only for the unsigned clearance authorization. Exact capacities are **6,084 / 6,121 / 2,161**
subjects against **4,050 / 4,050 / 1,950**, margins **2,034 / 2,071 / 211**. All 93 Hall subset checks pass.
The separate independent implementation reproduces these counts, including MQuAKE's 53 duplicate
entity rows and 2,158 revision-compatible first representatives. Draw remains separately gated.

The [operator refresh](../../logs/r1_round25/r1-d10h-operator-refresh.json) records old and new digests.
Recompute each later-stage request after binding actual preceding receipts. Candidate v8 inventories
these inputs without a circular candidate→D9→candidate hash dependency. Actual owner freeze still
requires completed receipts and all gates closed.

## Review priorities before launch

- **Ceiling meaning:** queue workers=2 multiply the bound solo ceiling by 1.65, while the execution
  plan's serial ceiling is already 1.5 × measured cost. Resolve which quantity is stored in the matrix
  so padding is not inadvertently applied twice. Budgeted process-hours include overlap.
- **Concurrency qualification:** saved attempt slowdowns reach 1.1335, not universally ≤1.10.
  All four compared final state hashes match. Short development pairs do not establish every final
  dataset/condition/full-endpoint runtime.
- **Failure policy:** queue stops dispatch and drains the other worker; it does not automatically
  retry twice and skip. The proposed document patch describes actual behavior.
- **zsRE baseline:** 6,036 / 6,084 teacher responses are immediate-newline empty answers. Add this
  interpretation caveat before protocol signature; E.2 filtering and scoring stay unchanged.
- **Q15 and final costs:** near-family semantics remain proposed for all datasets. Full endpoint,
  validation/startup/failure costs and the September 20 repricing remain open. October 9 remains the stop.

The exact factual patch is [R1-X15-document-corrections.patch](R1-X15-document-corrections.patch),
with [scope and downstream rebinding instructions](R1-X15-edit-request.md). `git apply --check` passes;
the patch was **not applied**, as required by the X15 lane.

## Validation and ownership

**137 tests pass:** 65 recipe/locality/certification/layout/cadence regressions; eight independent-review
and ledger pending/complete/tamper tests; five candidate checks and 59 package-layout tests. Ruff and
`git diff --check` pass. The real clearance CLI independently reproduces the expected unsigned refusal.
See [final validation](../../logs/r1_round25/final-validation.json).

The only existing-file edits are three integration-test fixtures updated to current post-patch recipe
paths (`test_r1_64c_comparator_recipes.py`, `test_r1_73b_comparator_recipes.py`, `test_r1_73d_locality.py`).
All implementation, candidate, report, draft and ledger work is in new files. Test-created metadata in
the prior Round24 certification-test root is inventoried separately from the five pre-existing untracked
CPU result directories and one pre-existing rehearsal log. No active owner results, installed source,
live driver/backend, task board, ongoing list or lead queue were changed. Resource files are under assets.

The first operator-template read failed before forms were created; its log and exact producer bytes are
archived and final evidence uses a new resource version. An X15 report was regenerated after a lint-only
producer cleanup; both the earlier report and exact producer bytes are preserved. Neither attempt used
the GPU or changed an experimental result.
