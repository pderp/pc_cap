# Lane V — independent review of the R2 repairs

Evidence snapshot: **2026-09-10 13:54:44 UTC**; review began at approximately 13:48 UTC. Reviewed commit **80a7c9bc3c6c35e9327a689cf8cde6df2e9ddcd3** and its working tree. Source hashes and the numerical counterexample are recorded in [additional_probes.json](../results/review_repairs_r2/additional_probes.json). REG-02 continued separately. Codex created only new project files and disposable synthetic fixtures; no production source, existing log, task board, environment, confirmation data, or GPU process was changed by this review.

**Verdict: the access, dataset-path, and selection repairs work on the main S4 path. The freeze gate should remain open for further repairs.** The stronger synthetic study now runs the real CLI dispatcher, S4 stage, confirmation loader, stream loop, checkpoints and paired collectors together. It also exposes remaining problems in lease ordering, archived-run discovery, S5's frozen configuration and allowance, and cost definitions.

## Verified improvements

The existing [four confirmation controls](../tests/harness/test_confirm_cli.py) passed in **0.74 seconds**. Evidence: [existing_controls.txt](../results/review_repairs_r2/existing_controls.txt).

- The original missing-freeze reproducer now exits 2 with **zero payload reads**. The existing controls also cover a draft freeze, an unbound filename and unavailable B4.
- The current path interface produces **150 unique paths for 150 scheduled jobs**. The literal old snippet still produces 75 paths because it omits the new explicit dataset argument. The repaired CLI passes that argument correctly; this is a necessary reproducer adaptation, not evidence that the original collision remains in the CLI.
- The shared selection helper chooses a realization subset first and filters each committed order to it. The five orders retain identical item sets. C0 uses a shorter prefix of the same filtered order.
- An ordinary rerun is refused with exit 4.
- S4 passes the frozen per-run allowance to run_stream. Checkpoint records contain cumulative ledger time and separate rescoring deltas.
- Resource exposure views now form checkpoint intersections per contrast. Retained-performance checkpoint times are separate from immediate acquisition curves.

## Stronger synthetic execution

The new [successful study driver](../scripts/review_repairs_r2_study.py) exercises:

1. Two synthetic datasets, three realizations and five committed orders.
2. Synthetic realization JSON, SHA256SUMS, and a schema-valid synthetic freeze.
3. All 150 scheduled S4 jobs through runner.main and the actual run_s4.
4. The actual protected data loader, identity check, selection rule, run_stream, learner serialization and metric writers.
5. The actual S4-06 collector, expected inventory loader and paired analysis.
6. A forced rerun and collection of its archive.
7. A separately instrumented S5 stage call with deliberately divergent development and frozen base specifications.

Only the base, learner, evaluator, tokenizer, locality inputs and GPU lease are replaced by small CPU fakes. The synthetic study runs no model, accesses no real sealed items, and takes no real GPU lease. The recorded event order tests where backend discovery occurs without initializing a GPU.

Result: **150/150 jobs succeeded**. The collectors returned **540 zsRE rows and 420 CounterFact rows** across all available synthetic arms. Both C2–C1 and C2–CR comparisons were **complete** for both datasets. The fake evaluator intentionally gives equal outcomes, so the resulting “negative” classification is a plumbing check, not a scientific result. Bootstrap draws were reduced to 100 for this synthetic call; the real freeze still contains the registered 10,000.

Evidence: [synthetic_pipeline_valid.txt](../results/review_repairs_r2/synthetic_pipeline_valid.txt). Synthetic resources are under /home/derp/cap/assets/tmp/review_repairs_r2_study_valid; project evidence remains in pc_cap.

The initial [probe](../scripts/review_repairs_r2_probe.py) used a two-item checkpoint list. The real schema correctly rejected it because the checkpoint list is fixed to [100, 300, 1000, 3000]. Its [failed log](../results/review_repairs_r2/synthetic_pipeline.txt) is retained. The successful driver is a new file, preserving the user's no-existing-file-edit protocol; it retains the real checkpoint list and validates the synthetic freeze before execution. Do not interpret the first attempt as a production failure or use that initial script as the successful study command.

Both drivers refuse reuse of their existing temporary roots. A repeat should use a newly reviewed driver with a fresh fixture root, or receive permission for an existing-file/temp-output change. Neither script is a confirmation launcher.

## Remaining findings and acceptance checks

### V-01 — Backend discovery still precedes the lease

Priority: before launching queued GPU jobs through the CLI.

In [runner.py](../src/pccap/harness/runner.py), cfg["determinism"] = pccap.determinism_report() still occurs before the lease context is entered. [determinism_report](../src/pccap/__init__.py) calls jax.default_backend() and jax.devices(). The later assert_determinism() is correctly inside the lease, but does not undo the earlier initialization.

Actual observed event order with instrumentation:

    backend_report_before_lease
    lease_enter
    backend_report_inside_lease
    construct_BP
    lease_exit

The response report's statement that backend initialization occurs only after the lease is therefore still inaccurate. Move all backend-discovering calls behind acquisition. Add a lease-order control that rejects any discovery before entry; the current controls all use --no-lease and cannot catch this.

### V-02 — S5 is only partly frozen and ignores its runtime allowance

Priority: S5 execution blocker; CPU repair and test are independent of REG training.

[stage_s5.py](../src/pccap/harness/stage_s5.py) constructs the base from module-level development ARMS before entering its confirm branch. It consults frozen substrate_arms only afterwards. Missing frozen arm definitions silently retain the development definition. It still loads calibration through calibration_for(), and ePC checkpoint selection through the mutable assets manifest.

The synthetic authority test deliberately supplies frozen SB.base=EPC while the development SB.base is BP. S5 constructs BP, then asks for EPC calibration. This divergent input is a diagnostic of configuration authority, not a proposed scientific arm definition.

More directly, with frozen run_allowance_seconds=1.2, S5 passes **no allowance** to run_stream, completes all eight synthetic edits, and reports approximately **7.2 ledger seconds** with status complete. The same test confirms that its current checkpoint constants agree with the registered frozen list; no checkpoint discrepancy is claimed.

Repair checklist:

1. Resolve and validate the final frozen arm before constructing its base.
2. Refuse missing or unavailable frozen substrate definitions; bind and verify checkpoint identity, calibration values/hashes, credit policy and eligibility.
3. Pass the frozen allowance and relevant run identity/hashes into execution and metrics.
4. Exercise S5 through the real CLI with CPU fakes, not only its stage function.
5. Poison development arm/calibration/asset lookups during the confirm test: the frozen execution must remain valid or fail explicitly before model work.

### V-03 — Rerun archives are collected as active results; checkpoint resources are not archived

Priority: before any --force use or pooled collection.

The repaired CLI archives the result directory, but [s4_06.collect_rows](../src/pccap/analysis/s4_06.py) and [s4_05.discover](../src/pccap/analysis/s4_05.py) recurse through its .superseded-* sibling.

After one forced rerun of a synthetic C2 job:

- ordinary rerun exit: 4;
- forced rerun exit: 0;
- discovery includes the archived run;
- paired analysis raises duplicate item row for C2 / realization 0 / order 0.

Resource views key their grouping by dataset/realization/order and overwrite the arm entry while iterating, so duplicate attempts can select an archived version. Neither collector isolates a requested experiment/freeze identity; two valid freezes in results/S4 would create a similar collision.

There is a second preservation issue: --force moves the result directory only. run_stream derives its external checkpoint directory from the original result path, so the replacement reuses the prior checkpoint filenames. Archived metrics can then reference checkpoint hashes whose original bytes are no longer available. This resource-path issue is confirmed by source inspection; the forced fake run uses identical learner values, so it is not a test of changed checkpoint contents.

Keep the deliberate no-resume policy if desired: refusal plus an explicitly new attempt can be sufficient. But preserve both result files and checkpoint resources, select one approved attempt per frozen job, and make collectors reject ambiguous provenance. Test archives with different outcomes and state hashes, plus two experiment IDs.

### V-04 — “None = stage ceiling only” has no visible runtime enforcement

Priority: before final scope/allowance approval.

S4's numeric per-run allowance is now connected. However, Ledger merely accumulates costs, gpu_lease serializes jobs and records projected time, and the generated schedule is a list of commands. I found no stage-total stopping mechanism on this execution path. The draft note that None means “stage ceiling only” therefore describes a planned policy rather than an implemented bound.

The stream checks elapsed cost before an item and after committing and evaluating it. It does not interrupt an update when that update crosses the time threshold. Endpoint rescoring then runs even after resource_stop. ItemGuard does restore an uncommitted update on an exception, but the current loop does not convert such an exception into a saved resource-stop endpoint; runner.main records correctness_failure for ordinary exceptions. The four existing controls demonstrate a completed-prefix boundary stop, not arbitrary mid-update interruption recovery.

PDF Appendix B allows a last-completed-item endpoint and requires rollback if halted mid-item. Specify the operational policy precisely:

- Is the allowance checked at item boundaries, with a disclosed overshoot and separately reserved endpoint evaluation?
- What exception or cancellation represents a mid-item resource stop?
- How are the completed prefix, restored learner, failed item's consumed cost and endpoint report persisted?
- What enforces the remaining stage/project allocation across separate jobs?

Price and freeze the allowance before final publication. Current plan wording places S4-02's allowance assignment after the immutable freeze; resolve that ordering without silently editing an already-open protocol. Reject an unpriced required run, or identify an explicit approved external stage controller.

### V-05 — Comparable-compute still mixes update and query time

Priority: before the re-profile is turned into an efficiency claim.

The new per-run mean_update_accel_s uses the update delta. But the comparable_compute table calls item_seconds() with its default total phase, which sums update plus immediate evaluation. The two fields with the same label can disagree.

A pure synthetic counterexample gives both arms one second of update time, with nine seconds of C2 query time and zero C1 query time:

| Field | C2 | C1 |
| --- | ---: | ---: |
| per_run mean_update_accel_s | 1 | 1 |
| comparable_compute mean_update_accel_s | 10 | 1 |
| comparable_compute ratio_to_C2 | 1 | 0.1 |

C1 is consequently marked outside 20% despite equal update costs. PDF Appendix B's joint comparable-compute criterion uses measured **update** time. Total-cost resource matching is a distinct view and should remain explicit.

Also, cumulative_accel() still sums item deltas rather than the recorded cumulative ledger snapshots. Its accel_seconds_total and time-budget acquisition views omit setup and intermediate rescoring. Checkpoint retained-performance times do use full ledger snapshots, which is an improvement. Final total cost, acquisition time and update-only cost must have separate accurate names and consistent formulas. Include nonzero evaluator setup and costly intermediate checkpoints in reconciliation tests; today's existing fake evaluator has no setup/locality/drift overhead.

Evidence: [additional_probes.json](../results/review_repairs_r2/additional_probes.json).

### V-06 — Configuration provenance still needs negative controls

Priority: before freeze readiness is declared.

The synthetic S4 study deliberately reports a current code identifier and base checksum unrelated to the values seeded into the freeze, yet execution succeeds. That is useful for a fake model test, but it reflects the production path's absence of a check that the actual code/base/tokenizer/configuration matches the frozen bindings. The before/after checksum only proves that the loaded base stayed unchanged.

Additional dry-run probes accept perm=-1, S4 base=EPC and S4 read=g. The first would select Python's last order entry and later produce an out-of-schedule analysis identity; the latter two do not select S4's actual base/read because S4 always constructs BP and uses the frozen read setting. Validate these arguments against the frozen schedule before output creation/model work.

Add controls for changed code/checkpoint/tokenizer, missing substrate definitions, invalid order indices and conflicting CLI base/read. Distinguish an intentional synthetic-model test allowance from the production gate. Keep both freeze and realization hashes attached to each accepted run and verify that analysis consumes exactly that experiment.

## Handoff order

All proposed repairs below affect existing orchestrator-owned files. This review does not apply them or request ownership of those paths.

1. Fix V-01 before the next CLI GPU job can queue.
2. Repair S5 configuration/allowance authority and add its actual CLI-to-stream control.
3. Make result discovery and external checkpoint preservation consistent with the no-resume/explicit-rerun policy.
4. Fix cost definitions, stage/run stopping and freeze ordering before pricing/freeze.
5. Add provenance rejection controls and rerun the expanded CPU study.
6. Run the already-planned GPU subset and cost profiles in the orchestrator's coordinated window.

Lane V's review deliverable is complete; it does **not** certify that DEC-019's complete freeze gate is green. Lane D's newly delivered GRACE artifacts now unblock the orchestrator's JAX adapter and PC-10. The latest ongoing.md assigns Lane G′ to the orchestrator; Codex did not enter that lane. Lane R remains separate.

No GPU tests, broad model suite, real reference-adapter parity, confirmation opening, task-board edit or commit occurred as part of Lane V.
