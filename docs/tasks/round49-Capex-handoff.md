# Round 49 — Capex handoff

2026-09-27. R1-D14g and X23 complete. PC-8 still waits for Capstan's completed
PC-v0 run and harm readout. No GPU use, live-run changes, frozen-source edits,
staging or commit.

- **[Stage-4 report](../R1_stage4_report.md):** existing findings assembled into
  one report following the registered skeleton, with a source/hash registry and
  full native tables linked. Learned-reader retention gains coexist with all
  learned cells failing the mean-KL benchmark. Existing classifications and
  DEC-069 qualifications are unchanged.
- **[Receipt audit](../../logs/r1_x23/report.md):** all 135 cells in positions
  136–270, their 405 checkpoint receipts and 272,160 phase records pass. The four
  previously disclosed absent decisions remain absent; no additional gap was
  found. Selected process cost is 251.449040502 hours; full main-queue cost is
  392.419650444 hours, without double counting covered driver time.
- **PC-8:** at 08:26 EDT, PC-v0 was 25/60 complete with no failed finishes and
  no production harm report. Latest check is
  `logs/additional_work/round49/pc8-readiness.json`. Its publication checklist and
  Round-48 result-slide slots remain ready. Capstan continues to own the GPU chain.

The report corrects two potential reading errors without changing original
reports: the existing unavailable inventory has **11 rows**, not the task's
twelve (eight primary contrasts and three extension dataset entries); and the
halt's **308.37 hours** describe the last complete block boundary, while the
full 270-cell spend is **392.42 hours**. The assembled document also explicitly
supplies the halt accounting beside the historical native appendix's unsupplied
accounting field.

Validation: **99 CPU tests passed**, two slow tests deselected; lint passes.
Primary rows and omission entries match their existing CSVs, report/source hashes
match, and links resolve. Audit negative fixtures reject tampered authority,
ceiling, receipt and watch evidence. Logs are under `logs/additional_work/round49/`;
the final audit is `logs/r1_x23/evidence-final/`. Earlier draft/audit passes are
retained as intermediate records, not additional results.

Owned additions: `aw/stage4_assembly.py`, `aw/x23_receipts.py`,
`aw/tests/test_x23_receipts.py`, the assembled report and source registry,
`logs/r1_x23/`, round-49 logs, task/claim/completion records and this handoff.
Live PC-v0 output changes and final-queue launch/resume logs visible in Git belong
to operations and were neither edited nor staged by this lane.
