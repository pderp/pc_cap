# R1-63j rehearsal fixtures — moved to the assets repository (2026-09-18)

The synthetic assembler-rehearsal trees formerly under `docs/tasks/R1-63j-rehearsal/`, `logs/r1_round24/rehearsal/`,
`logs/r1_round24/rehearsal-*.json`, `logs/r1_round27/operator-test-*/` and `logs/r1_round24/certification_tests/`
now live in `/home/derp/cap/assets/runs/pc_cap/R1/rehearsal_fixtures/` (repository size policy, lead 2026-09-18).
Files above 45 MB there are split into `*.part-NN.json` + `*.index.json`; reassemble with
`python scripts/repo_size_policy.py join FILE.index.json OUT.json` (sha256-verified). Task records that cite the old
paths refer to these files.
