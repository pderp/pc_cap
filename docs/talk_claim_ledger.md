# Talk claim–evidence ledger

Codex, snapshot of current files. This covers every row of counter-review §1 and the opening plus all eight
§8 outline items. Labels describe evidence maturity: implemented includes a measured operational result, proposed
means a contract/interpretation, hypothesis has no completed empirical test, null result means an actually measured
negative/inconclusive result. A blocked or unrun κ pilot is not a null result.

The experiment deadline is October9,2026; October10–14 is analysis and rehearsal, presentation October15.
All revision-v1 evidence below is development evidence. A source hash identifies this snapshot; a concurrently
updated source must be re-reviewed before slides are finalized. The original abstract is aspirational wherever
its formal claims exceed the implemented scope.

| ID | Statement/slide | Label | Evidence IDs | Supported wording and qualification | Missing evidence / producing lane |
| --- | --- | --- | --- | --- | --- |
| A1 | Frozen prior, much smaller adaptive residual agent | implemented | E05 E07 E08 E09 | Historical checkpoint: 3,348,228 adaptive parameters = reader1,640,964 + controller1,707,264, about2.7% of the stated124M base. Do not label all3.35M as reader-only; per-record fast deltas are additional state. | Final selected-reader inventory: R1 primary selection. |
| A2 | Learn residual R=F*−F0 as prediction error | implemented | E04 E05 E02 | Per-answer-position residual-stream deltas use normalized adjoint steps against supplied targets under the write bound. Support-target approximation; no measured global F*. | Exact global F* evidence: empty; future theory. |
| A3 | Two Markov blankets | proposed | E05 E06 E07 | Working query/rejection and observation/write interfaces; A and null threshold are operational controls. Conditional-independence factorization has not been proved. | Formal blanket proof: empty; post-October theory. |
| A4 | κ keeps precision finite on tail events | hypothesis | E16 E17 E18 | Bounded answer loss and finite logit gradients have CPU evidence. Proposed preservation objective fails reference-minimum property; no κ-trained experimental result. | Trained κ/tail benefit evidence: empty; HT-3 owner objective review and pilot. |
| A5 | Risk-aware rejection; precision as risk sensitivity | implemented | E05 E06 E10 | Null head and rare-token gate implement rejection; hard acceptance, nonzero writes and changed answers remain separate. No expected-free-energy planner or quantified precision interpretation. | Expected-free-energy/precision claim evidence: empty; future planner/theory. |
| A6 | Value of failing: learn where the prior fails | implemented | E02 E03 | Investigators found ordinary-text drift, unseen false fires and MQuAKE/null instability, then changed training/gates. Boundary tradeoffs persist; do not imply every failure is solved. | Agent-chosen costly audits: empty; future audit-policy experiment. |
| A7 | Forgetting as an auditable geometric invariant | implemented | E12 E13 E14 E15 | Operational order-reversal damage, state hashes, supersession and restores exist. v0 null damage on some populations is not zero state change. | Holonomy/geometric-invariant theorem or transfer result: empty; future theory. |
| A8 | Heavy-tailed residual errors | implemented | E10 E11 E26 | Observed harm concentration:16,256 positions,128 windows,max3.7896nats atw125:p26,one position>0.01nat. Worst1% holds99.449%positiveharm; two saved reports are identical, not replications. | Power-law/heavy-tail distribution identification: empty; HT-1 final-reader audit still required. |
| O0 | Opening: small adaptive memory on frozen transformer; preserve/intervene/tails | proposed | E02 E08 E10 | Controlled GPT-2-scale substrate; distinguish implemented residual writes from the abstract’s frontier-scale coupled-agent aspirations. | Frontier-scale/general coupled-agent evidence: empty. |
| O1 | Two-interface diagram and parameter counts | proposed | E05 E06 E07 E08 | Label operational interfaces implemented and Markov-blanket interpretation proposed. Use corrected reader/controller counts. | Formal proof: empty; future theory. |
| O2 | Retention versus unintended intervention on common populations, with controls | proposed | E03 E09 E10 E23 E24 | Historical development tradeoffs exist; common-population selection and final controls must be bound before claiming the final comparison. | Final selected-primary common-population result: empty; orchestrator selection, then R1-X12 review (held). |
| O3 | Mean versus local harm: one-position tail, then audit across conditions | implemented | E10 E11 E26 | Audit separates nats from task-error fractions. Cross-condition drift evidence is limited to saved rows; no aggregate-only reconstruction. | Final-reader full drift/paired comparison: empty; HT-1 repeat before freeze. |
| O4 | Boundary history: three failures and changes | implemented | E02 E03 E24 | Chronological development account, with still-unresolved retention/rejection tradeoff and selection oscillation. | Any assertion of final repair: empty until selected-reference assays. |
| O5 | κ panel, positive or null, with matched robust control | proposed | E16 E17 E18 | CPU objective results only. c=2 matches κ=.5 ceiling; κ=.2 requires comparator-scope decision. No positive or null trained κ outcome yet. | Pilot outcome: empty; HT-3 plus owner definition/go-no-go. |
| O6 | Recovery curve if stress panel completes | proposed | E19 E20 | Six-cell development contract, fixed old facts, interval recovery and censoring specified; no runs yet. | Recovery curve: empty; HT-2 owner stress driver and6cells. |
| O7 | Confirmatory matrix as completed, with missing cells named | proposed | E21 E22 E23 | 360core +45optional-extension cells are a plan, not completed revision-v1 research. v0 completed results remain separately reported. | Revision-v1 completed-cell inventory: empty; R1-41/admission and owner execution. |
| O8 | Can coupled objectives improve correction versus tail harm; agent value of failing? | hypothesis | E16 E17 E19 | Open research question. Compare against ordinary robust loss and rejection training after objective review; correlated schedules alone do not demonstrate coupled free energy. | Answer to research question: empty; HT pilot/panel and post-October theory/planner. |
| N1 | v0 negative primary result | null result | E12 E13 | Preserve the completed study’s negative/inconclusive contrasts and margins; do not recast development reader improvements as confirmation of the old hypothesis. | No revision-v1 confirmation implied. |

Evidence identities (full SHA256; paths relative to pc_cap):

- **E01** [docs/heavy_tail_counter_review.md](../docs/heavy_tail_counter_review.md) — `7c214031a8f5db0e3c8d154942815af7a5849273f9cddf401075147c747e8e91`
- **E02** [docs/R1_stage2_report.md](../docs/R1_stage2_report.md) — `b370a02d9b74f8bd616b28c01e080d35ac35016784ee72512090a989279c6569`
- **E03** [docs/R1_stage2_notes.md](../docs/R1_stage2_notes.md) — `6079c502a7ff73f51473c403a643b34fc5b8bbca4dbdfda4b48b4e511637c03d`
- **E04** [src/pccap/revision_v1/adapt.py](../src/pccap/revision_v1/adapt.py) — `c40fca3264486fbd6386387e19b305a7d9ca486ffe6452d2cbdd75a2a83cf793`
- **E05** [src/pccap/revision_v1/learner.py](../src/pccap/revision_v1/learner.py) — `639c10e3da55f52101634d45da08670dacaae5944672f5a96b91ffb0ccd97117`
- **E06** [src/pccap/revision_v1/reader.py](../src/pccap/revision_v1/reader.py) — `9abc9b2a22bdbf9a39aafa65e1a3f0aa0b9aa0e5e86b60d9640a496377010018`
- **E07** [src/pccap/revision_v1/controller.py](../src/pccap/revision_v1/controller.py) — `17940440ae37d8248ac4403d8b5bf5caa4141fdb02ebc4cae862c7253373a292`
- **E08** [logs/heavy_tail/parameter_inventory.json](../logs/heavy_tail/parameter_inventory.json) — `a102196c4c694a47fe3ad26a39400b2064f35b7e00d47b9ff7a2fc6f634ec18b`
- **E09** [manifests/revision_v1/primary_condition_v4.json](../manifests/revision_v1/primary_condition_v4.json) — `6e5d88fe764941b7b72609dc9d6ae4600140c57a871733f8100fae4a54f9ece6`
- **E10** [logs/heavy_tail/audit-20260915-round15/audit.json](../logs/heavy_tail/audit-20260915-round15/audit.json) — `1b70890fc282c2d23c0cd147011b7a6427062d63f5850e8b601799fa535cbe09`
- **E11** [logs/heavy_tail/audit-20260915-round15/paired.jsonl.gz](../logs/heavy_tail/audit-20260915-round15/paired.jsonl.gz) — `5cbba97196125f7e2d1c9f1d64d512a3750265a7a45cd687c95229c6c90661c0`
- **E12** [results/S7/summary.json](../results/S7/summary.json) — `718348e2517306cbdb9008b05f17296a7f0a714aca54179f7463341fad83f3b3`
- **E13** [docs/report.md](../docs/report.md) — `f4b4b6fb18e8b9ce672daa6bc80fb429264c2d0fa5780f0fc354212a4f6ffb77`
- **E14** [src/pccap/revision_v1/memory.py](../src/pccap/revision_v1/memory.py) — `1af390068efcaca8d15e9d81912a9459310f76965e762ee9a066e58609141a54`
- **E15** [tests/revision_v1/test_r1_68b_incremental_cell.py](../tests/revision_v1/test_r1_68b_incremental_cell.py) — `7b5b70e3230f86ecf72ff089fe19409247cf69115c43b16867a66c7a8de81fec`
- **E16** [manifests/revision_v1/kappa_pilot_v1.json](../manifests/revision_v1/kappa_pilot_v1.json) — `bf1184a96eb3f0ba06ab0935af026ce66d64300612ca34853200574b6428e3af`
- **E17** [logs/heavy_tail/kappa_definition_review.json](../logs/heavy_tail/kappa_definition_review.json) — `d1756360fca9cd52976fa5828a42aeef328c027eb971774722591711fa5efa3b`
- **E18** [tests/revision_v1/test_ht_kappa_actual.py](../tests/revision_v1/test_ht_kappa_actual.py) — `9a824a19278b35fc323b5be28c9c215238e3f463d18ce0c5954cf6dfc9dfce13`
- **E19** [manifests/revision_v1/ht_development_panel_v1.json](../manifests/revision_v1/ht_development_panel_v1.json) — `c0eb167e240e91f8cf076db3e6991c1408291fe56c32765efcd56181e5ad3f1a`
- **E20** [docs/tasks/HT-evaluation-contract.md](../docs/tasks/HT-evaluation-contract.md) — `8364e18947e5c6d23981f4de07b763a699862ebabffdbd674cad1e2b8b377f74`
- **E21** [manifests/revision_v1/run_matrix_draft_v4.json](../manifests/revision_v1/run_matrix_draft_v4.json) — `924bf4b42453e1dc9a603b1e47e22dce2790b3d7168df3aa29f715a9cdc55526`
- **E22** [logs/r1_round14/freeze_candidate_v3_refusal.json](../logs/r1_round14/freeze_candidate_v3_refusal.json) — `a03aadb3621028dc9b770d23ca924761a55d730b8afb4559100fb09a5a193b02`
- **E23** [docs/R1_stage4_protocol_draft_v4.md](../docs/R1_stage4_protocol_draft_v4.md) — `26165b73630eac284d7ea8ea1df823195612f350453d4b54fe3b58cb6b2b27ec`
- **E24** [docs/decisions.md](../docs/decisions.md) — `f596d3960c6bfce721064091f73333dde7674fcbae71308b11d80c9f2a9f2d58`
- **E25** [logs/monitor_retention/acceptance-20260915.md](../logs/monitor_retention/acceptance-20260915.md) — `802f9edbd9c09049cd3fa8b07b33c478d33a1b1e8e2a6732e09e7d3a4efde9dc`
- **E26** [logs/heavy_tail/audit-20260915-round15/mean_vs_tail-corrected-preview.pdf](../logs/heavy_tail/audit-20260915-round15/mean_vs_tail-corrected-preview.pdf) — `7ff3017689ccb0980a499558bf31f45cd585e6c82898651497f046ba20686372`

No independence claim follows from multiple files: the two saved full drift vectors are identical. Item-only
historical pairs can match item identity without a full prompt/target proof; inspect each series’ pairing-strength
field. A percentage from100outside prompts is a sample rate, not a certified population upper bound.

The reference files for the meeting and abstract remain outside the repository under
/home/derp/cap/errata/presentation_details/. The abstract’s “Nelson2023/2024” reference needs an exact citation.
HT-3 pins the inspectable2010paper version and records the sign convention rather than silently equating formulas.
