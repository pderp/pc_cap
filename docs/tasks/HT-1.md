# HT-1

Status: current stored-results audit complete; rerun on final selected reader remains a future gate. Agent: Codex.
Inputs: the exact 788-file inventory in logs/heavy_tail/audit-20260915-round15/audit.json.
Outputs: scripts/ht_audit_existing.py, scripts/ht_plot_audit.py, tests/revision_v1/test_ht_audit_existing.py, the audit directory and its PDF/SVG figure.

Verify command: ../venv/bin/python -B scripts/ht_audit_existing.py --output logs/heavy_tail/<new-directory>; tests: PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q -p no:cacheprovider tests/revision_v1/test_ht_audit_existing.py.
Verify output: 5 tests passed in0.09s; actual audit 1,346 series and45,152 pair comparisons. Source hashes checked at read and snapshot completion.
Done-when: supported stored per-position and per-item families audited, missing-data inventory produced, fractional-tail tests passed.
Deviations: no NLL statistics invented for binary endpoints or aggregate-only histories; pairs are descriptive and retain weaker identity qualifications for old item-only rows.
Unresolved/questions for lead: final-primary development rows must pass the same audit before freeze; historical duplicate drift reports are one pattern, not replications.
Cost: GPU seconds0; CPU reads only. Plotting uses the existing assets/envs/status-paper-20260911 environment because the project venv lacks matplotlib; no dependencies installed.
