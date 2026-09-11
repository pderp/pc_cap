P4 and S7 counter-review — 2026-09-11, Codex

P4's broad numerical description reproduces on fresh seeds, with a reduction in stability at the smaller sample size. S7's editing inventory passes the stated separation from confirmation source subjects, and its E.2 selection follows the frozen inventory order. S7 is not ready for an unqualified D.9 measurement claim: the damage implementation omits paraphrase losses, GRACE answer scoring omits its original-prompt boundary, and one grammar probe was already sampled by P4.

The source of truth was docs/pc_cap_month_plan_readable.pdf, SHA256 9a2b64680452394a57da6d07536f00b215320bdd2e7deef65e9f3bec3d359080. I checked D.4 and extracted PDF page 26 directly for D.9. The audit used CPU only and never opened sealed realization files. It made no changes to analysis code, manifests or existing results.

**P4 evidence.** [Reproduction driver](../scripts/review_p4_fresh.py), [policy written before execution](p4_s7_review/p4_policy.json), [fresh result](p4_s7_review/P4_gram.json), and [comparison/provenance](p4_s7_review/p4_comparison.json). The unchanged solver ran with n=2048, batch=64, and a +10,000,000 offset on every sampling seed. The auxiliary sets retained the original 2048/context, 4096/shared context group and 2048/held-out switch counts: 34,816 sequences total, 265.77 seconds. Base checksums agree. The original P4 output and reviewed source files were unchanged; only the output destination and coverage-writing side effect were redirected in memory.

| Error-space statistic | Published n=8192 | Fresh n=2048 |
| --- | ---: | ---: |
| Private / shared-1 overlap | 0.270681 | 0.283515 |
| Private / shared-2 overlap | 0.351345 | 0.351464 |
| Shared-1 / shared-2 overlap | 0.268147 | 0.268571 |
| Minimum split-half stability | 0.932964 | 0.864954 |
| Mean captured variance at rank 16 | 0.985877 | 0.986092 |
| Insufficient-rank cases | 0 | 0 |
| Independent private/private overlap | 0.926974 | 0.932995 |
| Shared retention across context groups | 0.937144 | 0.941950 |
| Held-out private transfer capture | 0.963141 | 0.959695 |
| Held-out shared transfer capture | 0.994280 | 0.993584 |
| Shared basis capturing private-only flip | 0.207619 | 0.204113 |
| Private basis capturing shared-only flip | 0.211274 | 0.212301 |

Fresh disjoint 1024-row halves give absolute differences of 0.011864, 0.006032 and 0.008043 for the three overlap means. The corresponding published-to-fresh changes are 0.012835, 0.000119 and 0.000424. Thus two comparisons are comfortably smaller than this descriptive sampling scale; private/shared-1 is slightly larger but of the same scale. Two halves do not provide a calibrated confidence interval. The 0.068 drop in minimum stability must remain visible; I do not certify that every statistic is “within resampling noise.”

The qualitative implication is unchanged: errors from different mechanism kinds have moderate overlap, and each basis captures its own held-out flip much better than the other kind's flip. However, nominally independent private mechanisms have very high mutual overlap (~0.933), almost the shared-retention overlap (~0.942). This is not evidence of separated private supports. D.4 requires intervention and transfer checks before attributing private/shared structure; retain S3's causal tests and the explicit label “declared solver on BP weights,” since no ePC-trained grammar twin was measured. The required main mechanism sets have 8192 samples in the published run; its separate context-specific private comparisons use 2048 each and should keep that count visible.

**S7 evidence.** [Audit driver](../scripts/review_s7_inventory.py) and [machine-readable audit](p4_s7_review/s7_audit.json). The inventory's pair hash is 5b887b5eea6f4ea1bf61a135b8b7dedca7180fa72a79178ca861c6a4e86af5e7, matching the E.2 artifact. Inventory, E.2 selection, PDF and source hashes were stable throughout the audit.

Only subject strings were decoded from the unsealed eligible-pool JSONL inventories; edit payload objects were not deserialized. Their full-file digests matched manifests/dev/pools.json. No confirmation realization was read, and no pool prompts, answers or subject names appear in the audit output.

| Independence check | Result |
| --- | --- |
| Pool subject sets | 10,420 zsRE; 20,091 CounterFact |
| zsRE inventory | 300 pairs, 600 unique members, 496 subjects |
| zsRE overlap with either pool, development subjects or S0 | Zero |
| CounterFact inventory | 75 pairs, 150 unique members, 141 subjects |
| CounterFact overlap with its confirmation source pool | Zero |
| CounterFact subjects outside its reserved development subjects | Zero |
| Grammar inventory | 200 members; seeds 900000–1050007; disjoint from DATA-06 train/eval/held-out blocks |
| Syntactic stratum checks | All pass |
| E.2 first-eligible selection order | All nine dataset/stratum checks pass |

CounterFact is independent of the confirmation stream, but explicitly reuses development subjects; it must not be described as independent of all development work. The audit establishes subject separation and the declared source partition, not a semantic review of every raw source record.

The final E.2 counts are 34/33/33 for zsRE and grammar, and 9/33/33 for CounterFact. CounterFact's shared shortfall is 25 relative to the final target of 34; the raw inventory's shortfall of 93 uses the separate 3× candidate target of 102. DEC-023 already accepts the nine-pair stratum. Do not back-fill it or obscure the smaller precision.

**D.9 findings and handoff to the analysis owner.**

1. Damage averaging is incorrect for multi-prefix Q_i. The production reversal() calls item_loss() only on the canonical item prompt. A controlled learner changes only i's paraphrase: its loss rises by 4 nats after j; its canonical prompt is unchanged. With the declared two-prefix Q_i, the required mean damage is 2.0 nats, while the implementation reports I_ij=0.0. D_ij correctly notices the distribution change (0.150763), so this is specifically a damage-aggregation defect. Repair by evaluating complete answer NLL for every fixed prefix in Q_i, averaging prefix losses before subtraction, and recording the operands and count. Preserve the prompt-only result as a separately named diagnostic if useful. The counterexample in the audit is a regression case for the repair.

2. S7 item_loss()/item_exact() bypass the boundary-aware decoder now wired into the main harness. A two-token boundary-spy control records lengths [2,3] with key_positions=None; the original prompt's correct index is 1 for both. GraceArm declares decode_key_positions=True, but the S7 helpers ignore it. Propagate the original prompt boundary for every teacher-forced or generated continuation, including each paraphrase's own boundary. Verify with a two-token edit whose lookup changes if the boundary moves. This is required before B4 participates in S7, even after B4's separate parity gate clears.

3. The grammar DATA-06 separation claim holds, but its seed block overlaps P4. Item g7-5-private-1000005 has exactly the same context, private mechanism, switches and seed as the published P4 private sample at index 5. One S7 member was therefore already used in the development geometry measurement. Before S7 outcomes, the owner should bind a replacement inventory in a documented seed block disjoint from every development diagnostic, regenerate the grammar selection binding, and record the change. Do not silently retain a claim of independence from all earlier measurements.

4. Grammar strata have generator support: shared_1 across contexts; independent private mechanisms across contexts; and same-context private near-neighbours. Natural-language strata are operational proxies: same subject/different relation for “shared,” different subject/relation for “private,” and same relation/different subject for “near-neighbour.” They establish neither shared mechanisms nor independent supports nor actual key-space proximity. zsRE template inequality also cannot guarantee distinct semantic relations or exclude contradictory facts. Keep these labels qualified, review the fixed pairs for semantic contradictions before outcomes, and anchor mechanistic claims in the grammar interventions.

The first two findings require changes to src/pccap/analysis/s7_01.py and meaningful regression controls; those paths belong to Claude. No edit was made here. The inventory correction also belongs to that lane and must precede S7 outcomes.

Reproduction commands, from pc_cap, use the active venv with PYTHONDONTWRITEBYTECODE=1, CUDA_VISIBLE_DEVICES='', JAX_PLATFORMS=cpu, OPENBLAS_NUM_THREADS=2 and OMP_NUM_THREADS=2. Run scripts/review_p4_fresh.py once into its fresh output directory; run the S7 audit with PYTHONPATH=. because it reuses the repository's tiny item helper. The first S7 invocation lacked that path and failed before any audit work; its stderr is preserved, and the corrected invocation exited 0. The P4 and audit outputs are exclusive run artifacts, so a repetition should use a new output namespace rather than overwrite this evidence.
