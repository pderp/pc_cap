# October 9 research freeze — charlie's review checklist

Experimental cutoff: **2026-10-09, 17:00 America/New_York**. No new model fits start on or after October 6. Talk: October 15. Current readiness snapshot: October 4; this is not a completed freeze.

- [ ] **charlie approves the final scientific scope and wording:** active inference is a proposed policy loop; predictive-coding evidence includes adverse/null findings and actual cost; tails are finite-range fits, not complexity classes or W(N). GPT-2 small (124M), limited populations/seeds, dependent orders and unverified window independence remain explicit.
- [ ] **Review the closed inventory:** PC-reader 12/12, Option R 20 complete / 1 incomplete / 9 deferred, AW-L 24/24 including six shared controls. Keep missing, failed and deferred rows; DEC-074b omissions and DEC-080 stable-v0 deferral stay visible. Do not substitute a κ full-inventory readout: KP-1 did not establish the old drift-memory identity.
- [ ] **Close GPU process/segment receipts by the cutoff**, including failed work, without adding nested costs twice. Preserve raw artifacts; no cleanup of stopped-run evidence. No new primary classifier or decision threshold is implied by this freeze.
- [ ] **Run the final CPU refresh in dependency order** below, recording exact input populations and new output directories. Then replace the presentation's remaining literal seed/extension statements and Q&A placeholders; a generator cannot infer the narrative from results.
- [ ] **Rerun X25 after the last result**; require every cited source to pass or charlie to accept a specific disclosed exception. Review all hashes, completion/cost qualifications, ledger sources and final numerical prompts. Sign off on the scientific interpretation and the dated artifact list—not a claim that integrity checks establish fidelity or scientific validity.
- [ ] **Archive and review the final deck**, resolve October 2 feedback, confirm talk duration and rehearse. Record charlie's approval and remaining limitations in the freeze handoff; leave post-cutoff experiments for a later study.

| Generator / record | Latest inputs and output on October 4 | Final refresh condition |
| --- | --- | --- |
| `aw.stage4_assembly` | 270-cell halt; `logs/R1/reports/stage4-assembled/`; three reports refreshed by S4-LIM without new scoring | Recheck unchanged tables and archive original producer versions |
| `aw.pc_reader_report` + HT-17 refresh | All three paired seeds; `PC-reader/report-round63-final`; tail `HT-17/snapshot-20261004-complete` | All available final reader vectors; exact hash match, complete/pending denominator |
| `aw.r_report` | Twenty complete, one ceiling-stopped, nine deferred, zero pending; `R/report-round63-final` | All resume segments; full pairing before four-realization sensitivity |
| `aw.aw_l_report` | All 24 cells, six shared controls; `AW-L/report-round63-final` | Six readers/24 evaluations or explicit shortfall |
| `aw.presentation_timing`, `aw.rehearsal_pack` | Twelve slides, resolved 15/25-min scripts, completed/closed reports | Narrative updated; export to a fresh dated directory |
| `aw.supplemental_audit` | X25 current snapshot and documented historical source versions | Pass current canonical report paths via `--reports` and final export via `--deck` |

Canonical entry points: `docs/R1_stage4_report.md`; `docs/additional_work/{PC-v0,PC-v1,PC-controls,PC-matched-control,AW-B,PC-reader,R,AW-L,HT-17}_report.md`; `docs/talk_claim_ledger_v7.md`. Raw evidence stays in `results/additional_work/` and `logs/additional_work/R/queue/`. Supplemental analysis lives in `logs/additional_work/`; the final subdirectory names must be recorded at freeze. Current rehearsal export: sibling `assets/presentation-materials/deck_v3/rehearsal/`, with manifests. Historical/preliminary outputs are not the canonical freeze package.

October 4 reporting note: all planned GPU studies are complete or explicitly closed.
AW-L's historical shell budget gate did not enforce its check (wrong projection
path, default zero); the saved projection was 17.98 process-hours and actual new
receipts total 9.67. Its report preserves the defect and the shared-cost distinction.
The current reports and rehearsal export include the complete evidence. The
checkboxes remain for charlie's final review; GPU completion is not freeze sign-off.
