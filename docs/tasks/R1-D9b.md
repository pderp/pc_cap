# R1-D9b — draw producer

Status: **Producer implemented and tested; real draw NOT performed.**
Agent: Codex, 2026-09-17. CPU/JAX only; no commits.

Inputs: register v6, matrix v5.1, protocol v5.1, existing R1-58c receipt schema and the new R1-D9 operator interface. Actual owner approvals and final review resources remain absent in the supplied template.

Shared outputs: `scripts/r1_d9_receipt_core.py`, `scripts/r1_d9_receipts.py`, `tests/revision_v1/test_r1_d9_receipts.py`, `docs/tasks/R1-D9-inputs-template-v1.json`, and `docs/tasks/R1-D9-operator-interface.md`.

Verify command: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q tests/revision_v1/test_r1_d9_receipts.py tests/revision_v1/test_r1_77c_rehearsal.py -o cache_dir=logs/r1_round21/pytest_d9_seal_final`.
Verify output: `logs/r1_round21/d9-seal-final-tests.txt`; combined prior suite: 117 passed in 37.18 s (`round21-final-tests.txt`). Ruff passes. Final dry-run previews are in `d9{a,b,c}-dry-final.json`, each refusing the missing actual inputs. No candidate IDs are emitted by inspection.

Cost: zero GPU seconds and zero real-base calls. Tests use small synthetic inventories and TinyBase. No real draw/seal or sealed payload read occurred. All code/logs/docs are in pc_cap; synthetic resources are in assets.

Unresolved/questions for lead: populate actual reviewed evidence and explicit owner authorizations before execution. Current counts alone do not certify clearance. Complete protocol, endpoint construction, cost and freeze admissions remain separate. No task-board edit or commit was made.

Individual entry point: `scripts/r1_d9_draw.py`, with `--inputs`, default/explicit `--dry-run`, and separately gated `--execute`.

Done-when check: Independent RNG streams bind master seed, register SHA, dataset, realization, role and stratum. All role/entity/fact/item inventories are disjoint; five orders 100–104 share each realization across conditions. RNG states, quotas and deterministic replay are retained. Missing clearance refuses before selection.

Deviations and limits: Semantic near-miss/revision construction is a subsequent gate. Composition closure here is predetermined dependency membership. A capacity failure aborts the entire draw without reroll or substitutions.
