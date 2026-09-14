# R1-D1 approved entry-point repair — resolution

Status: done. Agent: Codex. Date: 2026-09-14.

The user approved the exact `R1-D1-script-fix.patch` correction and then requested a commit. On inspection, the orchestrator had already applied and committed that correction in **`d6a1d1f26575355a286b51792f6866374591972d`**. No duplicate source edit was necessary.

This record supersedes the **entry-point repair awaiting permission** statements in `R1-D1.md`, `CODEX-R1-round2.handoff.json`, and `logs/R1_round2_handoff.md`. It does not close their separate entity-resolution, teacher-eligibility or final-data sealing gates.

Inputs: `docs/tasks/R1-D1-script-fix.patch`, its companion guard-hash JSON, `scripts/r1_d1_exclusions.py`, and the tested `scripts/r1_d1_exclusions_v2.py`.

Verification performed:

- The installed canonical entry point is byte-identical to the tested v2 copy.
- Both match the approved SHA-256: `cf77facaf038b785112e840c0e7d249a860a87fb99942c0bf938d17780194e79`.
- Python AST parsing passes; the direct entry point's `--help` command exits successfully.
- `git diff --check` passes; the canonical script has no working-tree diff.

Direct entry-point check:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/derp/cap/venv/bin/python scripts/r1_d1_exclusions.py --help
```

The canonical script can now be used with new output destinations. The already validated inventory was not regenerated or overwritten. Full inventory evidence remains in `logs/r1_round2/artifact_verification.json` and `manifests/revision_v1/exclusions.json`.

Output/change for this follow-up: this new resolution record only. Existing source/task records and other-agent pilot outputs were not changed. GPU cost: zero. No additional repair approval is pending for this entry point.
