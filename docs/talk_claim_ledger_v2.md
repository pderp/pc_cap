# Talk claim–evidence ledger v2 — selected reader and round16 results

This is a new evidence snapshot for Charlie Derr's October15 presentation. Experimental completion remains October9; October10–14 is analysis, slides and rehearsal. All revision-v1 measurements below are development results. Completed v0 confirmation is reported separately.

Every row has one maturity label: **implemented** for an implemented mechanism or completed measurement, **proposed** for an unexecuted design or interpretation, **hypothesis** for an untested scientific claim, and **null** for an actually measured negative/inconclusive outcome. An unrun or blocked experiment is not a null result. The original abstract's formal or frontier-scale interpretations remain aspirations when they exceed these results.

| ID | Statement / slide | Label | Evidence | Supported wording and limits | Missing evidence / producing lane |
| --- | --- | --- | --- | --- | --- |
| A1 | Frozen prior, smaller adaptive residual agent | implemented | E02 E03 E10 E13 | Selected averaged checkpoint: reader1,640,964 + controller1,707,264 =3,348,228 adaptive parameters, about2.7% of the stated124M GPT-2 base. Fast per-record state is additional. | Frontier-scale transfer: empty; future work. |
| A2 | Learn a residual correction R=F*−F0 | implemented | E10 E11 E29 | Bound per-answer-position residual writes optimize supplied support targets with adjoint steps. F* is a conceptual target, not a measured global optimum. | Global residual-function identification: empty; future theory. |
| A3 | Two Markov blankets | proposed | E10 E12 E13 | Query/rejection and observation/write interfaces operate in code. Their interpretation as formal Markov blankets lacks a conditional-independence proof. | Formal factorization/proof: empty; post-October theory. |
| A4 | κ keeps precision finite on tail events | hypothesis | E15 E16 E17 | Repaired preservation divergence passes CPU nonnegativity/reference-minimum checks. Bounded answer surprisal does not bound preservation loss or gradients; float32 overflow remains possible. | κ-trained benefit: empty; HT-3/HT-3b, finite-value abort safeguards and lead Q4. |
| A5 | Risk-aware rejection / precision interpretation | implemented | E01 E04 E10 E12 | Null head and rare-token gate implement rejection. Acceptance, nonzero writes and changed answers are distinct events. No expected-free-energy planner or calibrated precision interpretation has been demonstrated. | Precision/planner evidence: empty; future theory and audit-policy experiment. |
| A6 | Value of failing: identify where intervention goes wrong | implemented | E29 E30 E32 | Ordinary-text drift, unseen false fires and MQuAKE/null instability drove changes in training, rejection and selection. Low mean drift still coexists with large local harm. | Agent-selected costly audits: empty; future experiment. |
| A7 | Forgetting as an auditable geometric invariant | implemented | E14 E24 E27 E28 | Order-reversal damage, supersession, hashes and verified restore are operational. Some v0 null damage results do not mean unchanged state. | Holonomy/invariant theorem and transfer: empty; future theory. |
| A8 | Heavy-tailed residual errors | implemented | E06 E07 E08 E09 | Observed concentration: v5 zsRE17/16256 positions exceed .1nat, maximum8.686nat; worst1% holds99.941% of positive harm. CounterFact52 exceed .1nat; maximum7.315nat. Call this concentration or rare large errors. | Distributional heavy-tail/power-law identification: empty; no fitted exponent or iid-position inference. |
| A9 | Unseen rejection is flat across memory occupancy | hypothesis | E01 E02 E06 E09 | zsRE rates10/12/9% at100/300/1000 records are measured; their outside-ID sets have zero pairwise overlap and different sources. Flatness is not established. CF observes0/1/1%; do not infer a controlled occupancy effect. | Matched outside IDs and source-controlled occupancy assays: owner GPU work. |
| O0 | Opening: frozen transformer plus small adaptive memory | proposed | E03 E29 E32 | Explain preserve/intervene/tails on a controlled GPT-2-scale testbed. Separate implemented residual writes from the abstract's broader coupled-agent program. | Frontier-scale/general-agent evidence: empty. |
| O1 | Two-interface diagram and parameter counts | proposed | E02 E10 E12 E13 | Use the implemented operational interfaces and corrected reader/controller split. Label the blanket interpretation proposed. | Formal blanket proof: empty. |
| O2 | Central figure: retention versus unintended intervention | implemented | E01 E02 E04 E05 | 42 development candidates on common selection populations;15 admissible. Unique winner has mean RET-GS .8033 (zsRE .98 / CF .82 / MQ .61), ES1 and minimum LS .98. Selection v2 follows DEC-050's point-estimate rule. | Independent confirmation and complete controls: empty; owner execution/admission. |
| O3 | Mean versus local harm | implemented | E06 E07 E08 E09 | v5 zsRE mean+.002198nat versus v4+.000233nat on identical text/reference positions; maxima8.686 versus3.790. Full CF mean+.006286 with ES95 .127704. Duplicate v5 full/incremental observations count once. | Final all-condition/full-population audit: owner execution then HT-1 repeat; aggregate-only32-window reports cannot supply tails. |
| O4 | Boundary history: failures and repairs | implemented | E01 E06 E29 E30 | Near-miss100/100 and revision100/100 on saved CF cases; revised-answer paraphrase success averages .795. These do not erase rejection uncertainty or rare ordinary-text harm. | Universal preservation or repair: empty; no such claim. |
| O5 | κ panel with ordinary robust control | proposed | E15 E16 E17 | Repaired objective and9+3 training proposal exist. c=2 matches κ=.5 answer ceiling, not κ=.2; preservation objectives also differ. Approved diagnostic cleanup is verified in E17 even though the historical task record still says pending. | Trained positive OR null outcome: **empty**; HT-3/HT-3b, lead Q4 by September20 and finite-value safeguards. |
| O6 | Recovery curve after clustered stress | proposed | E18 E19 | Six-cell driver/contract and CPU recovery/censoring checks exist. Fixed20-fact probes and four-GPU-hour aggregate ceiling are specified. No completed real-base stress panel is in this ledger. | Recovery trajectories: **empty**; HT-2/HT-5 owner run and lead Q5 by September20. |
| O7 | Confirmatory matrix, with every missing cell named | proposed | E20 E21 E22 E23 E31 | Lead retains360core+45extension and DEC-051 order; DEC-052 permits honest accepted-incomplete reporting if necessary. These are planned cells, not completed revision-v1 confirmation. | Admission, frozen successor matrix, execution and completed-cell inventory: R1-41/owner. |
| O8 | Can coupled objectives improve correction versus tail harm? | hypothesis | E15 E16 E18 E32 | Open question. Compare with ordinary robust loss and rejection training; correlated schedules alone do not establish a coupled-free-energy mechanism. | Answer: **empty**; κ/stress studies and later theory. |
| O9 | Runtime and feasibility | implemented | E22 E23 E24 E25 E26 | Measured old v5 drivers1262/1246s per300-edit zsRE cell. New batching/phase timers have CPU parity, not a real-base speed claim. At48–66min/cell,405cells+conditional7h require331–452.5h against306h before Oct8. | New driver/comparator timings, MQuAKE calibration and September20 remeasurement: owner. Target20min remains unmeasured. |
| N1 | v0 negative primary result | null | E27 E28 | Preserve the completed study's negative/inconclusive contrasts and margins. Development reader gains do not retrospectively confirm the old hypothesis. | No revision-v1 confirmation is implied. |

Selection qualifications for slides:
- The winner is exactly at10/100 unseen false fires. Wilson95% is5.52–17.44%; Clopper–Pearson95% is4.90–17.62%. These are descriptive fixed-candidate binomial references, not selection-adjusted certification or a guarantee about a deterministic development population.
- Checkpoint averaging is verified as the uniform float64 mean, cast back to source dtype, of steps150/200/250/300. The final checkpoint file and four source hashes are recorded. Averaging enlarged the candidate set after oscillation was observed; do not claim it removed seed dependence or supplied an independent replicate.
- All42 candidate stream and unseen populations match. Historical locality reports omit raw prompt IDs, so locality comparability also relies on reconstruction from the shared deterministic loader.
- The selected MQuAKE stream uses v3b; later standalone unseen/short-drift assays use a legacy dev population. Occupancy summaries also overstate actual development-item counts; use raw histories, as R1-X12 does.
- The “complete answer preserved” endpoint includes termination/correctness of the unchanged reference. A failure on that flag is not automatically a cap-induced answer change.
- Both short and full drift means must carry their window/history/cadence labels. CounterFact's32-window mean+.013662 and full128-window mean+.006286 describe different assays; neither controls the worst-position tail.

The most useful current talk sequence is the retention–rejection selection figure, the mean/tail figure, the boundary history and the honest list of unfinished κ/stress/confirmation measurements. Keep the empty pilot/panel rows if either study misses the deadline. No result here establishes power-law tails, finite precision on arbitrary events, a blanket theorem, an autonomous planner or frontier-scale performance.

Evidence IDs below are local to v2; they are not the same mapping as ledger v1. The accompanying logs/r1_round16/talk_evidence_v2.json binds every source and allows final-slide revalidation. A hash identifies this snapshot, not future edits to live notes.

- **E01** [logs/review_r1_selection.md](../logs/review_r1_selection.md) — `8ed0c03e9fd7b5bcc9da86581250cdb8115b84dffe3f2ca7551891775b5468b0`

- **E02** [logs/r1_round16/selection_audit.json](../logs/r1_round16/selection_audit.json) — `775c31525cd5684857f680a679902a379e021937adfed2d215330e037847b367`

- **E03** [manifests/revision_v1/primary_condition_v5.json](../manifests/revision_v1/primary_condition_v5.json) — `4bca8eb643872fe801a50b8665d492d5c16aa724645511945b97707bba4a5a72`

- **E04** [manifests/revision_v1/primary_selection_v2.json](../manifests/revision_v1/primary_selection_v2.json) — `93cad8d0274dbf2d9ee2a7da6fa2ebcf58900d2bb7b902558bdfaad43ffa5816`

- **E05** [logs/r1_round16/selection_retention_rejection.pdf](../logs/r1_round16/selection_retention_rejection.pdf) — `3736560a374b75aea9432001876f349b32d286aa2901882aae998b74501dc9d9`

- **E06** [logs/heavy_tail/audit-v5-round16-supplement/audit.json](../logs/heavy_tail/audit-v5-round16-supplement/audit.json) — `c55377b8d07ded5303b633596cd18f6c33164313436c41b7bf8faff65d59ec39`

- **E07** [logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5.pdf](../logs/heavy_tail/audit-v5-round16-supplement/mean_vs_tail_v5.pdf) — `3b55a4099a23b6fd44ab88f4d0c9dc1a9743278d917495505af963e6073960ea`

- **E08** [docs/tasks/HT-1b.md](../docs/tasks/HT-1b.md) — `97db1b35f5dd5586ee1cf681775bc6058dd3dc9079982b0443c9a90c6e0b9d83`

- **E09** [docs/tasks/HT-1b-new-results-addendum.md](../docs/tasks/HT-1b-new-results-addendum.md) — `a5ae2ced3edc8ebd597991bed9e4094a00baf2e8b57ba5fb231af72cd8cc2b9f`

- **E10** [src/pccap/revision_v1/learner.py](../src/pccap/revision_v1/learner.py) — `639c10e3da55f52101634d45da08670dacaae5944672f5a96b91ffb0ccd97117`

- **E11** [src/pccap/revision_v1/adapt.py](../src/pccap/revision_v1/adapt.py) — `c40fca3264486fbd6386387e19b305a7d9ca486ffe6452d2cbdd75a2a83cf793`

- **E12** [src/pccap/revision_v1/reader.py](../src/pccap/revision_v1/reader.py) — `9abc9b2a22bdbf9a39aafa65e1a3f0aa0b9aa0e5e86b60d9640a496377010018`

- **E13** [src/pccap/revision_v1/controller.py](../src/pccap/revision_v1/controller.py) — `17940440ae37d8248ac4403d8b5bf5caa4141fdb02ebc4cae862c7253373a292`

- **E14** [src/pccap/revision_v1/memory.py](../src/pccap/revision_v1/memory.py) — `1af390068efcaca8d15e9d81912a9459310f76965e762ee9a066e58609141a54`

- **E15** [logs/heavy_tail/HT-3b-objective-review.json](../logs/heavy_tail/HT-3b-objective-review.json) — `024a37a16a19e49195992610d06d2172c353014032c0a32b46f4606b1feeece5`

- **E16** [manifests/revision_v1/kappa_pilot_v2.json](../manifests/revision_v1/kappa_pilot_v2.json) — `81a07c899d89024e65f688bb6b0aadecf59918ebb2f6851f41d47b5a4a85a7b6`

- **E17** [logs/r1_round15/ht3b-approved-cleanup-verification.json](../logs/r1_round15/ht3b-approved-cleanup-verification.json) — `16ec64c02680092e92cd4bd055468114af1bb8b9eb32f552e415804dfc0ca034`

- **E18** [manifests/revision_v1/ht_development_panel_v1.json](../manifests/revision_v1/ht_development_panel_v1.json) — `c0eb167e240e91f8cf076db3e6991c1408291fe56c32765efcd56181e5ad3f1a`

- **E19** [docs/tasks/HT-5.md](../docs/tasks/HT-5.md) — `4f59577d8da786209801d349d900b7a457907001eb29a379f4365bd3856cecb8`

- **E20** [manifests/revision_v1/run_matrix_draft_v4.json](../manifests/revision_v1/run_matrix_draft_v4.json) — `924bf4b42453e1dc9a603b1e47e22dce2790b3d7168df3aa29f715a9cdc55526`

- **E21** [docs/R1_stage4_protocol_draft_v4.md](../docs/R1_stage4_protocol_draft_v4.md) — `26165b73630eac284d7ea8ea1df823195612f350453d4b54fe3b58cb6b2b27ec`

- **E22** [logs/r1_round16/schedule_options.json](../logs/r1_round16/schedule_options.json) — `85e72b6cffaa6e8ac22a43f4234506e68fc9bc539d37c53c5ab147edaba6a9e9`

- **E23** [docs/tasks/R1-72-decision-addendum.md](../docs/tasks/R1-72-decision-addendum.md) — `eeeff6fd806bb3bb329b619d80c7172dfe6cad0e9061aea9ba27f0345bceb28e`

- **E24** [docs/tasks/R1-68c.md](../docs/tasks/R1-68c.md) — `1349d8b7b2f1fa4e5ccc036a43ecf7261addf2a38b8de4a19135df2644aa0ee7`

- **E25** [docs/tasks/R1-64b.md](../docs/tasks/R1-64b.md) — `e359425161e40455cfc9928133d8fa9ebde43eac88e4f33aaf7fececc3c1ae54`

- **E26** [docs/tasks/R1-73.md](../docs/tasks/R1-73.md) — `70560b037d89ac7afb42a87bd465031a1d9a3bf88640506fdb01e3d83b8e4637`

- **E27** [docs/report.md](../docs/report.md) — `f4b4b6fb18e8b9ce672daa6bc80fb429264c2d0fa5780f0fc354212a4f6ffb77`

- **E28** [results/S7/summary.json](../results/S7/summary.json) — `718348e2517306cbdb9008b05f17296a7f0a714aca54179f7463341fad83f3b3`

- **E29** [docs/R1_stage2_report.md](../docs/R1_stage2_report.md) — `b370a02d9b74f8bd616b28c01e080d35ac35016784ee72512090a989279c6569`

- **E30** [docs/R1_stage2_notes.md](../docs/R1_stage2_notes.md) — `18031d167dfb67849b9fbe240cbad647b2517b7de7c22cf7ab14e2b8740396b6`

- **E31** [manifests/revision_v1/decisions_round16_schedule_snapshot.md](../manifests/revision_v1/decisions_round16_schedule_snapshot.md) — `843d820595bd10109dcbc29c736e01a802dd03d542b635756d06d539c9d39ea3`

- **E32** [docs/heavy_tail_counter_review.md](../docs/heavy_tail_counter_review.md) — `7c214031a8f5db0e3c8d154942815af7a5849273f9cddf401075147c747e8e91`
