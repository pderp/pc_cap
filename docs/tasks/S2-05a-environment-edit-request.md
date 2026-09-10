# S2-05a — Setuptools compatibility permission request

status: waiting for user permission; no replacement applied
recorded_utc: 2026-09-10T11:04:45.723804+00:00

The new `/home/derp/cap/assets/envs/grace` environment contains the source-pinned torch 2.0.0+cpu, Transformers 4.20.1, NumPy 1.24.3, and wandb 0.13.2 on Python 3.10.20. The resolver installed Setuptools 84.0.0. GRACE imports wandb through `grace/utils.py`; wandb imports `pkg_resources.parse_version`, but Setuptools 84 no longer supplies `pkg_resources`. The exact import traceback is in `results/grace_lane_d/legacy_environment_import_failure.txt`.

Proposed command, targeting only this new auxiliary environment:

```bash
UV_NO_CACHE=1 TMPDIR=/home/derp/cap/assets/tmp/grace_reference uv pip install --python /home/derp/cap/assets/envs/grace/bin/python setuptools==78.1.0
```

This replaces installed Setuptools files in the newly created GRACE environment and adds the missing legacy compatibility module. Because those files now exist, the user's any-existing-file rule requires permission. No edit of the project venv, REF-01 venv, GRACE clone, sibling repositories, or shared project sources is requested. The resolver output of this command will go into a new log if approved.

After the pin: recheck the source import, run all six new reference controls in the GRACE environment, then run the new oracle generator. It will stop if none of the five predetermined smoke cases yields a target-matching greedy answer; otherwise it generates isolated and sequential parity fixtures and a verified manifest. Existing output paths are never overwritten. Any later needed existing-file edit still requires separate permission.

## Approval and application (2026-09-10, orchestrator on the lead's instruction)

Approved by the lead ("approve the setuptools pin for the grace env"). Applied exactly as proposed:

```
UV_NO_CACHE=1 TMPDIR=/home/derp/cap/assets/tmp/grace_reference uv pip install --python /home/derp/cap/assets/envs/grace/bin/python setuptools==78.1.0
```

Resolver output: `results/grace_lane_d/setuptools_pin_install.txt` (setuptools 84.0.0 → 78.1.0; exit 0).
Verified: `import pkg_resources` and `import wandb` (0.13.2) succeed in `assets/envs/grace`. Nothing else
was touched; the six controls, the smoke gate and the parity generation remain Lane D's (codex) — resume
with the commands in `docs/tasks/S2-05a.md`.
