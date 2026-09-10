# Contributing / working protocol

This repository is executed by a lead plus AI agents under a preregistered plan. The rules below are
the operational ones; the scientific ones are in the PDF and `docs/decisions.md`.

**Environment.** Use `/home/derp/cap/venv` (DEC-001). Nothing is installed from `pyproject.toml`;
`requirements.lock` is the frozen set (`docs/environment.md`; `scripts/setup_venv.sh` recreates it on a
fresh machine once Lane R lands). `import pccap` sets the determinism flags (TF32 off, deterministic
XLA ops); do not import JAX before `pccap` in scripts.

**Where files go.** Code, logs and documentation in `pc_cap/`; everything else (data, weights,
checkpoints, clones, caches, auxiliary environments) under `/home/derp/cap/assets/`. The sibling
repository `llm-by-neural-predictive-coding` and `FabricPC` are read-only references; re-implemented
formulas cite `# reproduces hdpc/<file>:<lines>`.

**Logs.** One current work log, `docs/ongoing.md`; when it is rewritten, the previous version goes to `docs/archive/` with a date (never a numbered sibling file next to it).

**Git.** Agents never stage, commit, merge or push; the lead commits. Leave your changes in the
working tree and list them in your task record.

**Tasks.** Claim a task by setting your own row: `python -m pccap.harness.status --set <ID>
status=in_progress agent=<name>`; write `docs/tasks/<ID>.md` in the fixed format (status, agent,
inputs, outputs, verify command, verify output, done-when check, cost, deviations, unresolved,
questions for lead); set `status=done` with `gpu_seconds`/`wall_seconds` when finished. GPU time also
goes to the ledger (`pccap.harness.ledger.append_task_cost`). `docs/tasks/STATUS.md` is generated.

**GPU.** Any CUDA use longer than a minute takes the lease (`pccap.harness.lease.gpu_lease`); one
holder at a time; `results/.gpu_lease` shows who. Long runs (REG-02) hold it in chunks and honour a
pause file (`results/REG/reg02.pause`). Short GPU tests (`-m gpu`) need no lease but need free memory.

**Tests and lint.** `make test-fast` (CPU), `make test-gpu`, `make lint` (ruff: E, F, W, I, B). Markers:
`gpu`, `slow`, `lease`. `tests/test_package_layout.py` enforces the tree of the plan and the
confirm-manifest firewall (only `pccap/data/confirm.py` may mention `manifests/confirm`).

**Sealed data.** Confirmation manifests under `manifests/confirm/` are not read by any development or
tuning code; the loader refuses until the lead writes `manifests/frozen.json` (CP-E).

**Changing existing files.** Placeholder modules assigned to your lane are yours to replace. For any
other existing file owned by another lane, write `docs/tasks/<ID>-edit-request.md` and wait.

**Decisions and defects.** Thresholds, endpoints, arms and budgets never change. New spec
ambiguities become SD rows (`docs/spec_defects.md`), course changes DEC rows (`docs/decisions.md`),
both through the orchestrator.
