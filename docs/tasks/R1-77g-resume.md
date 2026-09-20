# R1-77g — proposed drain and resume procedure

**For the orchestrator after Q21 approval. Not executed by this lane.** Keep the
same matrix, recipes, result directories, queue receipt root and full history.
The steps below need owner control of the host processes and external GPU lease.
This procedure does not authorize a ceiling change or a stop by itself.

## Why a new invocation is necessary

`r1_77f_scheduler.run_workers` reads matrix and bindings at entry and obtains the
worker factor once. It subsequently rehashes both files and refuses changes.
The active code does not poll a pause file, accept a new factor from bindings,
or dynamically change `--stop-after`. Do not overwrite the active bindings, edit
locked source, replace the matrix, unlink locks, or send a process-group signal.
Changing the file cannot be used as a graceful pause or policy reload.

## 1. Record approval and establish a controlled idle boundary

Record the accepted Q21 scope and intended next bounded block in a new owner
cutover directory under `logs/R1/operations/`. Verify the old queue's Python
parent PID, command, boot/start identity and child tree, and relate it to the
external lease holder. A PID alone is insufficient. Save those observations.

If the queue is already naturally stopped, use the ordinary D13 reconciliation
steps. If it is still dispatching and the approved cutover calls for a drain,
the tested current-code mechanism is **one SIGINT to that verified Python queue
parent PID only**. Do not use terminal Ctrl-C/process-group targeting, `pkill`,
SIGTERM, SIGKILL or a signal to a cell child. Do not send a second interrupt to
force the wait to finish.

In the pinned scheduler, the main thread unwinds through the thread-pool context
manager and waits for its active executor threads. Those threads retain the old
admitted timeouts, finish their child processes, and write their real `finish.json`
envelopes. Pending cells are not newly dispatched during this unwind. The CPU
rehearsal verifies this behavior with two active synthetic workers and a pending
third cell. **This is not a hot reload.** Wait for the parent and both workers to
exit and for the matrix-specific queue lock to release; keep GPU ownership
exclusive throughout the drain. A natural worker failure still requires normal
failure/host reconciliation.

The interrupted original operator normally records step 9 as failed/interrupted,
because its full-matrix call did not return normally. Preserve that record and
document the intentional parent interruption. Do not turn it into a completed
step, forge a finish, or overwrite any original form or receipt. The amendment's
separate authorization below records continuation of that history.

## 2. Reconcile the drained state before signing

Follow [D13's crash-resume checklist](R1-D13.md): every started process needs its
actual finish/cost record; driver attempts must be covered; snapshots and phase
journals must pass normal resume checks; no unknown time can be entered as zero.
The interrupted parent may not have written `decision.json` or called the watch
for its final completed workers. Missing parent decisions must remain disclosed;
cost and retry accounting use the immutable start/finish chain. Do not invent
parent decisions to make the directory look normal.

Repair a missing watch observation only through the existing hash-checking watch
tool on the corresponding **completed** cell's recipe and result directory.
First run it without `--apply`, require no unavailable/invalid evidence, then
apply under the owner's approved reconciliation. For example, replace the two
named paths with the actual receipt-bound recipe and completed result directory:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.ht8_fidelity_watch \
  --recipe docs/tasks/R1-final-cell-recipes/CELL_ID.json \
  --result-root results/R1/stage4_sealed_cells/EXACT_CELL_DIRECTORY
```

Repeat the same command with `--apply` only after the read-only result verifies.
This reads existing assay evidence; it does not run a model. Preserve breaches and
relay new alerts. A torn watch journal or incomplete phase requires explicit
owner reconciliation; the amendment consumer will not bypass it.

While **globally idle**, generate a fresh D13/D12 boundary report using the latest
fully processed block (block 1 remains valid if the drain occurred partway through
block 2). This updated command uses the actual v10 cost admission, not the v8
example in the older runbook:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_d13_daily boundary \
  --matrix manifests/revision_v1/run_matrix_final.json \
  --receipt-root logs/R1/final_queue \
  --journal results/R1/fidelity_watch/observations.jsonl \
  --cost-receipt docs/tasks/R1-58g-operator_v10/02-cost-admit.receipt.json \
  --boundary-block 1 --workers 2 \
  --output-dir logs/R1/operations/Q21_IDLE_REPORT
```

Use a new output directory. Add the last actually posted D11 report if applicable.
The historical September 19 block-1 report **cannot** serve as this cutover
snapshot: later work was running and its global costs were unknown. Require zero
global accounting/watch issues in the newly generated `d11-report.json`. D12's
separate repricing proposal is not automatically applied by this ceiling amendment.

## 3. Inspect and sign the exact new request

Verify the unchanged content lock and read-only proposal first. This consumer
uses the scheduler's namespace interface and does not modify bound modules:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -m scripts.r1_63o_live_audit \
  --verify-lock logs/r1_63o/final/live-content-lock.json
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python logs/r1_77g/consumer.py inspect \
  --bindings docs/tasks/R1-final-queue-bindings-v2.json
```

Then prepare the exact request. This example resumes through block 2 and stops
there; choose the intended block before signing, and keep it identical in the
execution command. Existing complete cells are verified and skipped.

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python logs/r1_77g/consumer.py request \
  --bindings docs/tasks/R1-final-queue-bindings-v2.json \
  --cutover-report logs/R1/operations/Q21_IDLE_REPORT/d11-report.json \
  --stop-after 2 --output logs/R1/operations/Q21_REQUEST
```

The lead or authorized delegate reviews `request.json` and creates a **new**
reviewed form from `unsigned-form.json`, retaining its exact step and request
digest and supplying approval, name and date. Preserve the unsigned original.
The new request binds the v2 proposal, predecessor v1, consumer and installed
implementation hashes, globally idle snapshot, receipt root, two workers, factor
1.7, memory floor 6,144 MiB, 750 hours, October 9 deadline and selected stop block.
The old `operator-v10/09-reviewed.json` fails this request's signature check.

## 4. Resume under the normal external GPU lease

Keep/acquire the established live owner lease and inspect current host/device
health. Run the command below **inside that external lease lifetime**, using the
normal configured CUDA/JAX environment. The CPU-only environment overrides from
the reporting examples do not belong on this execution command. It is a reviewed
owner command template, not a command executed by this preparation lane:

```bash
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python logs/r1_77g/consumer.py run --execute \
  --bindings docs/tasks/R1-final-queue-bindings-v2.json \
  --cutover-report logs/R1/operations/Q21_IDLE_REPORT/d11-report.json \
  --stop-after 2 --form logs/R1/operations/Q21_REQUEST/reviewed-form.json \
  --output logs/R1/operations/Q21_RESUME
```

The consumer revalidates the exact signature and current cutover bytes, invokes
native sealed admission, checks the external lease, and then uses the native
scheduler's existing matrix lock. It writes a new `resume-authorization.json` and
result/interruption record under `Q21_RESUME`. New process envelopes go to the
**same** `logs/R1/final_queue`, with the same matrix and recipe identities and new
v2 bindings/authorization provenance. Prior failures still count against the
two-failure limit; all previous process time remains charged once. There is no
queue-level `--resume` flag: certified cell state is resumed automatically.

Confirm the first new start receipt has the v2 binding hash, amendment reference,
new authorization and `effective_wall_ceiling_seconds / solo_wall_ceiling_seconds
= 1.7`. Confirm previous start/finish bytes and matrix SHA remain unchanged.
Stop-after is a block boundary for **this new invocation**, not a change to the
already stopped original invocation. A further bounded continuation needs a new
fresh snapshot and exact signed request; do not reuse a changed digest.

## 5. Keep the reporting version explicit

Native D11/D13 reports continue to display the frozen 1.15 forecast even though
their accounting correctly includes the new process envelopes. Preserve those
canonical reports, and attach the following explicit v2 supplement to daily or
boundary reporting. Supply a fresh canonical D11 file and the authorization just
written; use a new output file each time:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python logs/r1_77g/accounting.py \
  --bindings docs/tasks/R1-final-queue-bindings-v2.json \
  --d11 logs/R1/operations/NEW_DAILY/d11-report.json \
  --authorization logs/R1/operations/Q21_RESUME/resume-authorization.json \
  --output logs/R1/operations/NEW_DAILY/ceiling-v2.json
```

Both D13 daily and boundary output name this file `d11-report.json`. Never label the canonical v1
projection as the active v2 allowance. The supplement changes only the remaining
ceiling forecast; it neither invents active-worker charges nor multiplies observed
process time again. Unknown costs suppress projection. Neither a projection above
750 nor this amendment raises the hard cap; the native dispatcher keeps that guard.
