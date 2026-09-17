# R1-77c — sealed backend donor review and rehearsal

2026-09-17 · Codex · CPU only.

The installed development driver changed from donor SHA `f8d04d3cacdc8cac0b97ba7cfda213a38623a7be92adfe881260d3f82c2c0c0d` to `5293448fd423c1eeab35374ff96ec040d221a32eb63261ccabaf92cdb6fae3c2` in the approved R1-68e landing. The sealed backend retained the old pin and correctly refused. This review covers the actual dispatch change, rather than accepting a new hash without reconciling behavior.

The donor now binds `r1_68e_batched_drift_v0.py`, validates `drift_implementation`, and uses `run_drift_assay` at the existing final drift phase. A missing field or `profile_default` retains scalar drift under full integrity and the existing RevisionCap batch path under incremental integrity. Only an explicit `v0_batched_v1` field enables v0 batching, and only for the six registered v0/S1 families with full integrity. Invalid combinations refuse in `profile_config`.

The sealed change updates the donor pin and routes the same final phase through that reviewed helper. It does not infer a batching choice from the condition. The helper and driver are bound by `integrity_driver_bindings`; the entire recipe, including any explicit drift choice, enters the frozen contract digest (only the future freeze-file binding is excluded). Changing the field after freeze changes the contract and is refused. New backend bytes also require a matching backend file binding; no old recipe is silently relabeled.

The sealed loader, final protocol and 18-gate admission, reservation/content and independent-population checks, full integrity phase snapshots, state and base identities, rollback, checkpoint cadence, failure costs, journal/resume rules, lock, October 9 deadline and canonical output roots remain unchanged. All six adapter parity tests remain in the suite. CPU parity does not close the owner's real-base parity or measured cost gate.

Application record and exact patch: `logs/r1_round21/r1-77c-application.json`, `r1-77c-backend.patch`. The file had no working-tree changes before application, and the ongoing task list assigned this work to Codex. The user lifted the existing-file prohibition subject to avoiding simultaneous Claude edits. Only the sealed backend and its test fixture were edited; the active development driver and installed `src/pccap` tree were left unchanged.

The new tests exercise missing/default/explicit v0 dispatch through actual sealed TinyBase execution, frozen-contract tampering, and a reduced-size synthetic path from exhaustive clearance validation through register-bound role allocation, five paired orders, content-seal validation, a synthetic freeze candidate/freeze, queue metadata inspection, sealed TinyBase execution and `scripts.r1_49g_analyze`. The rehearsal consumes the exact reservations produced by the draw primitive. Missing near/revision rows retain planned denominators, and the reduced matrix receives no registered-family inference verdict.

**Rehearsal scope:** small counts enter only pure producer APIs. Production CLI authorizations, writer schemas, output immutability and refusals have separate tests. This is not an unattended rehearsal of the full production CLI approval chain, nor a real clearance, draw, seal or scientific admission. Test logs are isolated inside the repository and synthetic resources in assets; real owner results are not used as outputs. The v0 fixture uses the retained-site TinyBase variant required by its scalar partial-forward interface.

Validation: the combined suite passed 117 tests before two further D9 seal checks; the focused D9/rehearsal result is recorded in `logs/r1_round21/d9-seal-final-tests.txt`. Ruff and diff checks pass. Individual replay: `PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q tests/revision_v1/test_r1_77c_rehearsal.py -o cache_dir=logs/r1_round21/pytest_rehearsal_replay`.

Unresolved: real owner evidence and authorizations, final protocol/gates/ceilings, final freeze and recipe/queue construction, real-base parity and execution. No final frozen marker, launch approval, commit or GPU job was created.
