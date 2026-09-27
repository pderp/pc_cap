# PC-8 — final PC-v0 report awaits completed inputs

Capex, 2026-09-27, 07:13 EDT. **Waiting on the experiment and harm readout.**
At the recorded check, 21/60 cells had completed successfully in
`results/additional_work/PC-v0/replication-60-20260927/`; no other finished
dispositions were present. The planned production harm report did not yet exist.
See `logs/additional_work/round48/pc8-readiness.json`. This is a snapshot of
completion, not a forecast or a partial result claim. The live source-bound
runner and its output files were not changed.

After Capstan finishes the 60-cell run and matched-position PC-5 readout:

1. Verify all 60 final cells, 30 paired coordinates and recorded input/source
   identities. Use `aw.pc_v0_report` with **orders=5**, and include the completed
   development 1/8/32 diagnostic group. Its native report verifies paired inputs
   and keeps failed/missing pairs out of effects. The current intended diagnostic
   input is `results/additional_work/PC-v0/dev-diagnostic-20260927/`.
2. Generate the real report in a new directory, replacing the text of the existing
   smoke-based `docs/additional_work/PC-v0_report.md`. The presentation register
   proposes `logs/additional_work/PC-v0/report-60-20260927/report.json`; this
   **does not exist yet**. The report generator currently leaves the harm section
   unavailable: integrate PC-5's verified `table_block` and its vector/source
   bindings before publishing the combined report. Do not leave its unavailable
   sentence beside measured harm, or fail to refresh the document publication hash.
3. Require all 60 harm readouts and 30 pairs on the fixed 4,064 positions, plus
   complete readout cost accounting. Retain both references and distinguish
   differences of arm ES99 from the paired-position distribution. PC-v0 remains
   exposed historical S5 with old primary scoring; it is supplemental corrected-
   algorithm evidence, regardless of which arm wins.
4. Fill the PC-v0 claim-ledger row from those outputs, export the efficacy/cost
   figure under `assets/presentation-materials/figures/pc_v0/`, and re-export
   slide 9/closing slots using PRES-4. Include the three realization estimates,
   harm and actual cost; do not relabel orders or tokens as independent replicates.

No final report, measured PC claim or research figure has been published early.
The existing native report/harm readers and the new slot resolver have CPU
coverage; actual experimental completion is the remaining prerequisite.
