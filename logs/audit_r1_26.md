# R1-X3 — re-audit of R1-26

Date: 2026-09-14. Agent: Codex. Read-only review of repair commit `5a46d2e`, the response in `docs/tasks/R1-X2-response.md`, and current HEAD `3ba95b55febe20d94f86180186ce163334261ad3`. CPU only; no pilot, sealed stream, checkpoint, or core module was changed.

## Assessment

The targeted repairs work on the demonstrated cases: zero-weight candidates no longer leak deltas, snapshot/rollback preserves reusable-weight accounting, a delta-capacity failure atomically restores a superseded record, mixed code/delta adaptation is explicitly refused, and cosine retrieval now uses the reader's near-zero normalization. Dataset-specific result roots and refusal of an existing result directory are also fixed.

**R1-26 is not a complete admission certificate for confirmation.** Capacity validation during construction/import, truthful physical-state accounting, query boundaries, returned-cost reconciliation, and complete output-path admission remain open. An accepted non-cosine reader configuration still disagrees with retrieval. The new delta-capacity trace is also collapsed into a generic no-improvement result by the public update API.

## Evidence and commands

The round-3 audit was reused without changing it:

```bash
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python scripts/r1_25_reaudit.py --output logs/r1_round4/r1_25_reaudit_legacy.json
```

Exit 0. JSON and captured stdout are under `logs/r1_round4/`. Its embedded task name remains `R1-X2` because the legacy script was not edited; the recorded source hashes establish that this is the R1-26 re-run.

The legacy edge script was also rerun against new output paths. It stops with the expected `NotImplementedError` at the newly rejected mixed-step configuration; see `logs/r1_round4/r1_25_edges_legacy.txt`. That exit 1 is **not a passing edge suite**, and no edge JSON was produced. New independent controls exercise the repaired capacity path and remaining boundaries without weakening the old assertions:

```bash
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python -m scripts.r1_26_reaudit --output logs/r1_round4/r1_26_controls.json --fixture-root logs/r1_round4/path_fixtures
env JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 /home/derp/cap/venv/bin/python -m scripts.r1_26_outcome_control --output logs/r1_round4/r1_26_outcome.json
```

Both exit 0. Use module invocation from the repository root so the tiny-base test imports resolve. Outputs are exclusive-create; choose new paths when repeating. The initial direct-file invocation of the new boundary script failed to resolve the local `tests` package before writing outputs; module invocation resolves that packaging issue. It was not a model or repair failure.

The path test extracts the **actual AST statements** for tag assignment, result-directory construction, and refusal from `scripts/r1_13_stream_eval.py`. It executes only those statements against newly created local fixtures, without loading GPT-2, taking a lease, or invoking the GPU driver. The repaired core and driver hashes are equal before and after the audit.

Targeted suite: `logs/r1_round4/pytest_cpu.txt` — **43 passed, 4 xfailed in 14.76 s**. It covers the new candidate/matrix checks, four positive boundary controls, and existing learner/memory/reader-controller tests. The four strict xfails assert the desired import, retrieval and output-admission contracts below; they explicitly document open defects. They are not waived correctness gates.

## Original findings after the repair

| Finding | Re-audit result | Evidence and scope |
| --- | --- | --- |
| X25-01 zero-weight delta contribution | Repaired | The selected record has no delta; the other candidate has weight zero. Selection delta is absent and maximum logit change is exactly 0. |
| X25-02 weight charge disappears on restore | Repaired for ordinary round-trip and ItemGuard | Original/restored memory is 7,828 bytes, including 7,616 reusable-weight bytes, with identical state hashes. Requested ceiling validation is a separate remaining issue (X26-01). |
| X25-03 delta-capacity failure leaks a revision | Repaired atomic rollback | Trace reason is `delta_capacity`; old record active, replacement removed, hash and byte totals unchanged. All 41 failed-work full forwards remain charged. Public outcome loses the reason (X26-04). |
| X25-04 mixed adaptation and comparator ambiguity | Mixed steps refused; comparator behavior disclosed | A code-step plus delta-step configuration raises `NotImplementedError` and leaves the store unchanged. Refusal occurs after 5 full forwards in the tiny control. Delta improvement remains relative to the documented controller-only baseline, rather than gaining a new comparator implementation. Freeze that algorithm explicitly. |
| X25-05 near-zero cosine mismatch | Repaired for the cosine path | Store and training ranking both choose the aligned key after use of sqrt(sum-of-squares + epsilon). An accepted non-cosine configuration still differs (X26-02). |
| X25-06 zsRE/CounterFact overwrite | Repaired for ordinary result-directory reuse | Identical user tags become `fixture` and `fixture@counterfact`; roots differ, and an existing result directory is refused. Orphan summaries/checkpoints and preflight timing remain outside this guard (X26-03). |

Support-answer conditioning, frozen base/reusable weights, semantic configuration checks already covered by R1-25, and nonfinite-revision rollback also remain intact in the reused audit. These checks use a tiny CPU base; they establish contracts and counterexamples, not GPU performance or research efficacy.

## Remaining findings for the owning lane

### X26-01 — memory ceiling can be bypassed at construction and restore

**Confirmation gate; reproduced.** Constructing a cap with a one-byte ceiling succeeds while reporting 7,616 bytes of weights. Importing a valid 7,828-byte snapshot into a cap configured for one byte silently adopts the source store's 8,041-byte ceiling. The public config still says one byte. Changing the snapshot's own ceiling scalar to one also succeeds in `RecordStore.from_state`, yielding 7,828 reported bytes against that ceiling.

The weight charge fix is valid but insufficient: `RevisionCap.semantic_config()` omits the ceiling, `import_state()` adopts the imported store, and `RecordStore.from_state()` appends records without capacity admission. Construct/restore into a temporary validated store, require the declared current ceiling policy, reconstitute the real reusable-weight charge, and reject over-budget state before mutation. Validate dimensions, finite values, IDs and aggregate bytes at the same boundary. Define any authorized cross-ceiling import separately; do not silently replace the requested limit. Two strict xfails reproduce these capacity cases.

### X26-02 — accepted non-cosine configuration disagrees with training retrieval

**Configuration gate; reproduced.** With `ReaderConfig(cosine=False)`, the training score ranks `large` first while retrieval ranks `aligned`; `store.metric` remains `cos`. This is a counterexample where the ranking changes, unlike the old audit's coincidentally agreeing example.

Current Stage 2 uses cosine, so the finding does not establish that those deployed cosine results are wrong. Either refuse unsupported non-cosine configurations at the cap boundary or wire the same metric explicitly into training, retrieval, gates and snapshots. A comment reserving alternate metrics for diagnostics is not an API refusal. One strict xfail captures the accepted configuration.

### X26-03 — output admission covers only one directory, and occurs late

**Queue/provenance gate; partly executed, partly static.** The exact admission statements allow a tag when only `results/R1/stream_eval_<tag>.json` exists; the driver later uses `write_text` on that file. The fixture creates and reads an orphan sentinel only; it does not overwrite any real result. One strict xfail captures admission of the orphan summary.

Static inspection of `run_stream` shows checkpoints under `assets/runs/<result-relative-path>/` and unconditional endpoint snapshot saves. A checkpoint-only root is not covered by the driver's `rd.exists()` check. Dataset separation fixes the normal cross-dataset collision, but no complete preflight reserves the summary, result and checkpoint identities together. The current guard is inside the lease after model/evaluator setup, so a refused duplicate can still incur initialization cost. Move admission before expensive setup; check all destinations, reserve a unique attempt identity atomically, and never treat an orphaned artifact as permission to overwrite it. This audit makes no claim to have launched a checkpoint overwrite or reproduced a concurrent race.

### X26-04 — public outcome masks a capacity rejection as no improvement

**Failure interpretation; reproduced.** The separate public-API control recreates the atomic delta-capacity rejection using `RevisionCap.update_item()`. It returns `code = rejected_no_improvement` and the same generic `codes` list, despite the internal capacity reason. State is restored and 41 failed-work full forwards are charged, so this is an observability problem rather than another rollback leak.

Carry `rolled_back_reason` into a structured outcome and decision log, distinguish capacity/numerical/unsupported-rule failures from ordinary optimization failure, and preserve the failed work charge. Otherwise attrition and resource failures can be mistaken for a scientific negative. Evidence: `logs/r1_round4/r1_26_outcome.json`.

### Carried resource/query/cost issues, still reproduced

- **Actual persistent bytes:** a long-ID record reports 184 bytes while serialized metadata/arrays alone have a 10,141-byte lower bound. Fixed 128-byte metadata and zero index bytes are still accounting conventions, not proof that every persistent byte is charged. Do not describe this as a physical ceiling until bounded representation and metadata/index costs are defined and enforced. Measure transient RSS/device peak separately from persistent logical storage.
- **Independent query boundaries:** a query extending a previous prompt can inherit the prior selection at length 2 instead of the fresh length-3 selection. Generation-prefix caching requires explicit reset between independent queries. Wire boundaries in batched evaluation, paraphrases, unrelated queries and drift; resets per token would also be wrong.
- **Returned cost:** a first prediction executes one full forward but returns zero full forwards even when the shared ledger tracks that work. Reconcile public result costs, ledger deltas and instrumented base calls, including selection/oracle setup and failed attempts. Profiling must distinguish full/partial passes, reverses, valid token masks, compilation and endpoint costs rather than infer them from the displayed counter alone.
- **Unsupported objective status:** fixed fast-unroll remains explicitly unimplemented; the unsupported ePC code-norm penalty still refuses. Neither is a failed scientific experiment. Mixed-step refusal should move before its 5 observed setup forwards; until then the setup work must be included in failure accounting.

## Recommended sequencing and concurrency

1. Claude can finish the current development evaluations under the known cosine configuration and unique result tags. This audit is not a request to interrupt the GPU job. Results retain development status and their actual configuration identities.
2. In a separate owned repair change, address X26-01 and truthful memory accounting together, then query/cost boundaries. Output preflight and reason propagation are small independent driver/API tasks if file ownership is explicitly divided. Do not have two agents editing `learner.py` concurrently.
3. The remaining CPU data review and matrix work can proceed independently, as done in R1-D1c/R1-40. E.2 is a later GPU/lead lane; profiles wait for both GPU availability and the relevant fixes.
4. Re-run targeted regression tests and the exact negative controls after repair; an unexpected pass in a strict xfail calls for reviewing and removing the mark. Only then use the two R1-40 profiling jobs to freeze resource ceilings. No revision confirmation queue is admitted by this report.

No existing file was edited, no task board entry was changed, and no commit was made. GPU seconds: **0**. Source identities and reproduction artifacts remain in `logs/r1_round4/`; additive completion records are for the orchestrator to mirror.
