# Round 65 — Capex handoff, October 5

FIN-1, LINT-1 and DOC-3 are delivered. FIN-2 remains scheduled for **October 6**;
no freeze dry run or lead signature was performed early. Work is uncommitted.

## Consolidated supplemental report (FIN-1)

Start with [additional_work_report.md](../additional_work_report.md). It covers
PC-v0, all three controls, fixed-v5 credit/settings and harm, AW-B, the three-seed
reader, Option R, upper-layer 2×2, HT-13/15/17 and the historical κ pilot. Each
section distinguishes its question, design, exposure, limits, cost and authority.
The closing interpretation follows DEC-081a and keeps active policy selection and
coupled free-energy training as proposed work.

The generator is `aw/additional_work_assembly.py`, with authored framing in
`aw/additional_work_content.py`. Nineteen tables are copied byte-for-byte from
25 named source documents/records; no scoring or fitting is added. Run the
command in [the reproduction guide](../REPRODUCE_additional_work.md) with fresh
output and document paths. The delivered source/receipt index is
[`final-assembly-20261005/`](../../logs/additional_work/final-assembly-20261005/).

**Cost finding requiring preservation at freeze:** 101 disjoint enclosing
receipts total **549,768.871787 seconds / 152.713575 process-hours**. Profiles,
the partial random run, Option R's ceiling stop and the failed default-v5 final
caption are included. Shared BP controls, nested cells/readouts and parallel
session elapsed time are not added again. This is process-envelope time, not
exclusive GPU occupancy or kernel time; it cannot by itself establish an overrun
of a differently defined GPU/wall-hour ceiling.

Three initial fixed-v5 harm launches (`harm-k32.log`, `harm-lr0.05.log`,
`harm-lr0.2.log`) have failure logs but no separate preserved duration receipts.
Successful retry receipts do not cover them. The report therefore calls its
known total a **lower bound**, leaves all three durations unknown and binds the
logs. Their failed-attempt evidence was not changed. The earlier κ pilot is
outside the post-halt cost total; its old drift-assay durations are also not
recoverable from the saved numeric summaries.

## Lint and cost gate (LINT-1)

The five original Ruff findings are fixed by import ordering and two unused-key
renames. `aw/cost_gate.py` reads the exact extensionless JSON file, requires
`projected_process_hours` plus an explicit positive finite gate, rejects invalid
input and duplicate keys, and exits 0 / 1 / 2 for pass / over gate / invalid.
The preserved AW-L projection is **17.983384104727545 hours**, below the stated
40-hour gate. The [check receipt](../../logs/additional_work/round65-cost-gate.json)
is retrospective; the historical shell gate failure is not reclassified.

Preserved original sources in `round65-source-archive/` match committed originals
exactly. The first full test run found a presentation helper rejecting the old
scoring hash after the import cleanup. That reporting helper now uses the
existing exact-hash archive mechanism, records the actual archive it checked,
and still rejects unknown drift or tampered archives. Runtime experiment source
resolution and `scripts/` / `src/pccap/` are unchanged.

## Reviewer entry point (DOC-3)

[`CURRENT.md`](../../../assets/presentation-materials/review-data/CURRENT.md)
now contains the dated **Results complete (Oct 4)** block with public GitHub
paths for the consolidated report, final reader/R/AW-L reports and complete
HT-17 snapshot. It also links both worked-example introductions in
`assets/support-information/` and the long colleague-talk PDF. The October-2
documents remain historical. New public paths become available after the lead
commits and pushes; this work does not claim they have already been published.

`aw/reviewer_folder.py` regenerates the entry point. Its
[folder manifest](../../logs/additional_work/reviewer-folder/round65-final/refresh.json)
checks every exported file and linked local source. The two existing exported
review documents retain their original content; only CURRENT changed in assets.

## Validation and next handoff

- [Final CPU test log](../../logs/additional_work/round65-tests-final.txt): **274
  passed in 105.05 seconds**. The earlier log retains the source-hash failure
  that prompted the presentation-only archive repair.
- [Ruff](../../logs/additional_work/round65-ruff.txt): clean.
- [X25 final](../../logs/additional_work/round65-X25-final/audit.json): **PASS,
  25 groups / 6,129 unique files hashed**, including the new assembly's exact
  table copies, receipt sum, individual statuses and unknown-duration handling.
- Synthetic-tree tests reject changed/missing tables, duplicate/nested receipts,
  invalid costs, tampered totals and attempted relabeling of stopped work.
- All folder-manifest and FIN-1 source/producer hashes match the delivered files.

For **FIN-2 on October 6**, carry the three missing durations and the historical
AW-L gate defect into the explicit exceptions. Perform the checklist, dependency
refresh, X25/X26, full reproduction and final-deck archive then; record the final
canonical paths and leave charlie's signature lines blank. The current assembly
is in X25's default inventory; an assembly at a different path can be supplied
under the `Supplemental assembly` key in `--reports`. If native report sources
are promoted, regenerate/review the assembly before its final audit.

No GPU experiment was launched. No model weights, experimental data, raw
receipts, source experiment recipes or scientific decision was changed. The
pre-existing untracked `results/additional_work/PC12/` directory belongs to the
other work and must not be swept into a commit of this delivery.
