# REP-1 — supplemental reproduction guide and CPU refresh

Status: complete. Capex, October 2, 2026. No GPU use, model calls or commits.

Entry point: [REPRODUCE_additional_work.md](../REPRODUCE_additional_work.md).
It specifies the populated repository/resource layout, dependency order, exact
CPU command, inputs and hashes, original measured costs and their scopes, GPU
recipes for owner reference, and every current deck figure's producer/output.
A Git-only checkout lacks some large saved weights/vectors; this requirement is
explicit. The historical κ drift records do not supply a measured enclosing
process cost; their forecast is not reported as a measurement.

Implementation: `aw/refresh_reports.py`, `aw/refresh_report_steps.py`,
`aw/reproduction_catalog.py`; synthetic tests in `aw/tests/test_refresh_reports.py`.
The runner executes a fixed sixteen-step CPU dependency graph into new repository
and assets directories, refuses existing destinations, records failures before
stopping dependents, hashes outputs, and compares inputs with a previous receipt
and again at completion. Its private adapters redirect legacy publication paths;
a write guard catches accidental writes outside the fresh destinations. Native
source files, source hashes and numerical calculations are retained. The fixed-v5
variant label comes from the bound treatment plan. Reader counts, fully paired
seeds and training-cost ratios in the staged numerical sheet come from the new
report, replacing the older generator's fixed eight-evaluation wording.

Delivered run:
`logs/additional_work/reproductions/round60-verified/`, figures/deck under sibling
`assets/presentation-materials/reproductions/round60-verified/`.
All sixteen steps complete in 262.355 seconds; no input changes during execution;
193 generated files hashed. Catalog: 29 PASS report groups, 4,828 unique source
bindings, 58 cost entries. X25 PASS. X26 has no listed issues or placeholders;
its existing exact-match exception “roughly one-third” remains supported by AW-B's
conditional-severity ratios (approximately .335 and .302). Numerical matches
remain aids to human review, not semantic proof.

Validation: nine focused tests pass; scoped Ruff passes. Tests exercise dependency
closure, refusal to overwrite either destination, child failures, final catalog
failures, changed-input detection, write protection and requiring both datasets
for a fully paired seed. See `logs/additional_work/REP-1/validation.json` and the
delivered `refresh.json` for source hashes and execution records.

The earlier `round60-check1` and `round60-final` runs are development evidence;
the latter correctly recorded a reporting-adapter edit during its execution.
The subsequent delivered run used unchanged code and inputs throughout.

PC-16a is still conditional: this snapshot has 9/12 reader evaluations, all nine
with matching tail-vector identities, and only seed 0 fully paired. No canonical
deck/report was overwritten. All literal author-written interpretation remains
marked for review in `presentation-review-required.json`; no pending scientific
finding is invented by a refresh. No question for the lead.
