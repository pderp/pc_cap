# R1-D9a — clearance producer

Status: **Producer implemented and tested; real joint clearance NOT performed.**
Agent: Codex, 2026-09-17. CPU/JAX only; no commits.

Inputs: register v6, matrix v5.1, protocol v5.1, existing R1-58c receipt schema and the new R1-D9 operator interface. Actual owner approvals and final review resources remain absent in the supplied template.

Shared outputs: `scripts/r1_d9_receipt_core.py`, `scripts/r1_d9_receipts.py`, `tests/revision_v1/test_r1_d9_receipts.py`, `docs/tasks/R1-D9-inputs-template-v1.json`, and `docs/tasks/R1-D9-operator-interface.md`.

Verify command: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q tests/revision_v1/test_r1_d9_receipts.py tests/revision_v1/test_r1_77c_rehearsal.py -o cache_dir=logs/r1_round21/pytest_d9_seal_final`.
Verify output: `logs/r1_round21/d9-seal-final-tests.txt`; combined prior suite: 117 passed in 37.18 s (`round21-final-tests.txt`). Ruff passes. Final dry-run previews are in `d9{a,b,c}-dry-final.json`, each refusing the missing actual inputs. No candidate IDs are emitted by inspection.

Cost: zero GPU seconds and zero real-base calls. Tests use small synthetic inventories and TinyBase. No real draw/seal or sealed payload read occurred. All code/logs/docs are in pc_cap; synthetic resources are in assets.

Unresolved/questions for lead: populate actual reviewed evidence and explicit owner authorizations before execution. Current counts alone do not certify clearance. Complete protocol, endpoint construction, cost and freeze admissions remain separate. No task-board edit or commit was made.

Individual entry point: `scripts/r1_d9_clearance.py`, with `--inputs`, default/explicit `--dry-run`, and separately gated `--execute`.

Done-when check: Exhaustive per-candidate dispositions, global entity identity, exact prepared-row hashes, unchanged v6 exclusion policy, reviewed base/tokenizer identities, token/context limits, complete source coverage and joint role capacities. Fails below 4,050 usable subjects per dataset or on any unresolved review. Output carries every reviewed disposition.

Deviations and limits: Real alias/context/exposure/teacher/role judgments are supplied as reviewed evidence, not inferred from counts or manufactured by the producer.
