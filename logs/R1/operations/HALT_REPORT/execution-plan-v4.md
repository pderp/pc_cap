# Execution plan v4 — block 4 cost proposal

Synthetic rehearsal: False. Unsigned; active ceilings are unchanged.

Measured class replacements: 15/22; remaining classes retain plan-v3 estimates.
Actual spend: 392.419650 process h; expected total: 467.040917; proposed ceiling total: 504.351550.
Buffer against 750 h: expected 282.959083; proposed ceilings 245.648450.
Active admitted ceiling projection (unchanged): 504.351550 h.

| Condition / dataset / edits / checkpoints | N measured | Expected process s | Proposed effective ceiling s | Basis |
|---|---:|---:|---:|---|
| R1_learned_ff / zsre / 1000 / [100, 300, 1000] | 15 | 4408.162 | 6724.217 | measured_completed_cell_process_envelopes |
| R1_learned_ff / counterfact / 1000 / [100, 300, 1000] | 15 | 4271.187 | 6459.537 | measured_completed_cell_process_envelopes |
| R1_learned_ff / mquake / 300 / [100, 300] | 15 | 2113.460 | 3197.393 | measured_completed_cell_process_envelopes |
| R1_nonlearned / zsre / 1000 / [100, 300, 1000] | 15 | 2171.350 | 3345.940 | measured_completed_cell_process_envelopes |
| R1_nonlearned / counterfact / 1000 / [100, 300, 1000] | 15 | 2143.662 | 3283.789 | measured_completed_cell_process_envelopes |
| R1_nonlearned / mquake / 300 / [100, 300] | 15 | 1345.540 | 2093.918 | measured_completed_cell_process_envelopes |
| v0_stable / zsre / 1000 / [100, 300, 1000] | 15 | 4739.110 | 7278.234 | measured_completed_cell_process_envelopes |
| v0_stable / counterfact / 1000 / [100, 300, 1000] | 15 | 9720.375 | 14746.743 | measured_completed_cell_process_envelopes |
| v0_stable / mquake / 300 / [100, 300] | 15 | 2920.101 | 4521.484 | measured_completed_cell_process_envelopes |
| matched_update / zsre / 1000 / [100, 300, 1000] | 15 | 4180.432 | 6478.844 | measured_completed_cell_process_envelopes |
| matched_update / counterfact / 1000 / [100, 300, 1000] | 15 | 9370.597 | 14206.192 | measured_completed_cell_process_envelopes |
| v0_live_C1 / zsre / 1000 / [100, 300, 1000] | 15 | 4726.272 | 7178.881 | measured_completed_cell_process_envelopes |
| v0_live_C1 / counterfact / 1000 / [100, 300, 1000] | 15 | 9695.523 | 14664.639 | measured_completed_cell_process_envelopes |
| v0_live_C2 / zsre / 1000 / [100, 300, 1000] | 15 | 4212.767 | 6821.643 | measured_completed_cell_process_envelopes |
| v0_live_C2 / counterfact / 1000 / [100, 300, 1000] | 15 | 7990.087 | 12150.593 | measured_completed_cell_process_envelopes |
| S1_LM / zsre / 1000 / [100, 300, 1000] | 0 | 4914.339 | 7371.508 | retained_plan_v3_estimate |
| S1_LM / counterfact / 1000 / [100, 300, 1000] | 0 | 7821.709 | 11732.564 | retained_plan_v3_estimate |
| S1_literal / zsre / 1000 / [100, 300, 1000] | 0 | 4914.078 | 7371.117 | retained_plan_v3_estimate |
| S1_literal / counterfact / 1000 / [100, 300, 1000] | 0 | 7820.719 | 11731.079 | retained_plan_v3_estimate |
| R1_learned_ff_v2 / zsre / 1000 / [100, 300, 1000] | 0 | 4197.215 | 6295.823 | retained_plan_v3_estimate |
| R1_learned_ff_v2 / counterfact / 1000 / [100, 300, 1000] | 0 | 3100.410 | 4650.616 | retained_plan_v3_estimate |
| R1_learned_ff_v2 / mquake / 300 / [100, 300] | 0 | 2790.759 | 4186.139 | retained_plan_v3_estimate |

Re-pricing rule: {"version": 1, "class": "condition, dataset, attempted edits, checkpoint cadence, full-validation contract", "donors": "artifact-complete cells through boundary, including every covered failed/retry process; same configured worker count", "expected": "arithmetic mean of comparable completed-cell process envelopes", "ceiling": "1.5 times maximum comparable completed-cell process envelope", "concurrency": "measured envelopes already include concurrency; do not multiply by 1.15 again", "failures": "all failures charged to actual spending; exhausted incomplete cells never become zero-cost donors", "scope": "no outcome-based exclusions; no transfer across dataset, condition, occupancy or cadence", "authority": "unsigned planning proposal only; versioned admission at an idle boundary required before changing ceilings"}

- Rates use only completed comparable chains; failures remain in actual spend and successful retry chains. No fixed future failure allowance is invented.
- Few observations and configured workers do not establish throughput, peak memory or a guaranteed upper bound. Keep existing memory ceilings and admission floor.
- Different occupancy/cadence/classes keep labelled plan-v3 estimates; measured phase rates are not extrapolated without a separately reviewed transfer.
- A quiet snapshot is not a lock or launch permission. Owner must stop dispatch, review the proposal and issue versioned admission before a changed ceiling can take effect.
- October 9 experimental stop; DEC-052 incomplete inventory and DEC-064 secondary benchmark reporting remain unchanged.

## D11 accounting, fidelity watch and DEC-052 inventory

R1 block 4 — 2026-09-27T03:52:34.946077+00:00
Scope: confirmatory; matrix SHA256 06fa8b3b3f3d734c12d47ac2b1b09d8dcd0c35c203013456c9409590329d56bb.
Artifact-complete cells: 270/330; complete blocks: [1, 2, 3, 4].
Known spend: 392.419650 process-hours; projected total: 504.351550; declared ceiling: 750.000000.
Projection uses the entire matrix, remaining solo ceilings × 1.15; retry-exhausted incomplete cells are not reserved again. It is not an elapsed-time forecast or a guarantee of full completion.
Cost ledger: Process envelopes replace covered driver attempts; overlap and failures charged once each. Uncovered legacy driver times exclude process startup. JAX timers are not added.
Incomplete cells:
- 9a22bb61d6e0f49880a936a3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- eafb85daf9dfc6661b0bc2d8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f3375c98045e9e28a348b9d0: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d62c99156470a7900dc43bc6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- fa0defe230fa592c6e1395ce: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9d8fa010baff9d2225fff4d4: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d059ce23baa1380031ffc8cb: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 058509628604e5ca4527273b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 165be2e488d7d1013b36ff1b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6c498709f6484559ef4e1e7f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 789321f88cd80b79c41108d3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 58f67f71157df294642d7924: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f434980db097ed5dc29aa6b8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0eadfbc9b2c2899d71a5dcee: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 509562eef48054a3aeac166a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 8515821d35005362bf80ca86: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ce81522f547c386fa9c08c2b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 67fbcd1e5ac9b7dcb8f292b9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 90334bd842b032c804251295: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 62cd670d3fc0e07b1d6ff2d7: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c2a654d2b5c10bec5b192bd4: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e513b37dc4ee2ea0c2ec9a4a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 5605235e2ed700e3724eec66: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- caef53a035b7c9e1ee694a16: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 3e16fbe7ff4d0e5b55e6d9d1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 66c77006152a19f5b1a397d3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6837bb994c30db520b1c50f5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4d261cc6ea3f349110835054: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b42ba0f2b0ed1a420be6ddb5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 10d0d6ef3ebaeeab62506369: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 2fcaaa6515b6d07526750ec2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 19a7255c9f6a76e216f4f3d3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 875c812006d2f01a6a67e48b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 29c34b1e7fff719ad0530aaf: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4c03d7d4cf05c04e6563204a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 56dad6836419abb22b9f3fc5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 722a6e81428fe90b28522578: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 64474eaad780d3d0f127b333: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 50bfcf7f7c0f6341243f0890: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 203da3ce23c2826be75941f8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6b9269f85604bbde03fb8ae2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6e30cfe3525aa76f6c298840: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f5f8f6ab600ed0fff3f77575: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a1ebc798b3d3dffdcb755fea: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 64083f876c4b931fac1666ac: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 3f0d5de719c7c2fac0765ae9: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 02fbdb7be57f6759883cb7f7: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 2eafd0179259617282b6bfe4: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 62b13a164930d43ad696b359: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 048ddd95d61026dbf40fa6f9: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- ea85d9daee87f0884e4f22e2: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 7e27f3fa1620b77e96f8da6f: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 46cc8880d731fbee52076712: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 45c033c5bc044beea6f5562c: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- be96aaad5d4e1dd91747a116: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- c28a7e48a1333e1bbbca134d: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- fda4c348dac5448fc10fd672: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 929c713ce993539177ad3985: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 47d567d51e4c0129ae905aa3: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 1a7b6658a55e4798f9674c67: missing checkpoints [100, 300]; failures 0/2; exhausted=False
Watch since previous posted snapshot: 274 global observations (270 in this matrix), 163 breach entries, 32 creep alerts.
- Breach outside this matrix/development/e71244c94a79d03e28e59d421680063cf1a96e822a1c36f077c4d1289670fbe4 (R1_learned_ff/mquake): capoff: KL=0.00554368762, signed ΔNLL=0.00560097637; original: KL=0.00554368762, signed ΔNLL=0.00560097637 nats.
- Breach outside this matrix/development/b66aedc82924b7a83016a07aa0723803bfd8ff1360f4a2aebbd4acb4f624a8a1 (R1_learned_ff/zsre): capoff: KL=0.0022697245, signed ΔNLL=0.00231001529; original: KL=0.0022697245, signed ΔNLL=0.00231001529 nats.
- Breach 61348508e40d54351613ab14 (R1_learned_ff/zsre): capoff: KL=0.00238149242, signed ΔNLL=0.00245022572; original: KL=0.00238149242, signed ΔNLL=0.00245022572 nats.
- Breach 88af67fa5945b642e8ba7974 (R1_learned_ff/zsre): capoff: KL=0.00238149242, signed ΔNLL=0.00245022572; original: KL=0.00238149242, signed ΔNLL=0.00245022572 nats.
- Breach 915f97b05f3fa2a81de09cdf (R1_learned_ff/zsre): capoff: KL=0.00238149242, signed ΔNLL=0.00245022572; original: KL=0.00238149242, signed ΔNLL=0.00245022572 nats.
- Breach 4aa4849ba414edab2504f56b (R1_learned_ff/zsre): capoff: KL=0.00238149242, signed ΔNLL=0.00245022572; original: KL=0.00238149242, signed ΔNLL=0.00245022572 nats.
- Breach ce0d0ffc2a58a60e27c460d9 (R1_learned_ff/counterfact): capoff: KL=0.00576537791, signed ΔNLL=0.00584962582; original: KL=0.00576537791, signed ΔNLL=0.00584962582 nats.
- Breach 9ebc93cc7912bd5d1c929418 (R1_learned_ff/zsre): capoff: KL=0.00238149242, signed ΔNLL=0.00245022572; original: KL=0.00238149242, signed ΔNLL=0.00245022572 nats.
- Breach 95dfb24c6361b2d38dd60e9b (R1_learned_ff/counterfact): capoff: KL=0.00576537791, signed ΔNLL=0.00584962582; original: KL=0.00576537791, signed ΔNLL=0.00584962582 nats.
- Breach 6d0915056b1e76d8ee8795ff (R1_learned_ff/counterfact): capoff: KL=0.00576537791, signed ΔNLL=0.00584962582; original: KL=0.00576537791, signed ΔNLL=0.00584962582 nats.
- Breach 7c9675a69d832a772070cb2d (R1_learned_ff/counterfact): capoff: KL=0.00576537791, signed ΔNLL=0.00584962582; original: KL=0.00576537791, signed ΔNLL=0.00584962582 nats.
- Breach 95016bc16e89cfcccccc40b8 (R1_learned_ff/counterfact): capoff: KL=0.00576537791, signed ΔNLL=0.00584962582; original: KL=0.00576537791, signed ΔNLL=0.00584962582 nats.
- Breach 43925e53c31860219a85ef90 (R1_learned_ff/mquake): capoff: KL=0.00712334183, signed ΔNLL=0.00714615798; original: KL=0.00712334183, signed ΔNLL=0.00714615798 nats.
- Breach c29ee18fb21ba6b387ede6e8 (R1_learned_ff/mquake): capoff: KL=0.00712334183, signed ΔNLL=0.00714615798; original: KL=0.00712334183, signed ΔNLL=0.00714615798 nats.
- Breach 54879da4dcdb0f106f98080a (R1_learned_ff/mquake): capoff: KL=0.00712334183, signed ΔNLL=0.00714615798; original: KL=0.00712334183, signed ΔNLL=0.00714615798 nats.
- Breach 78ebbc03946239c1d637154c (R1_learned_ff/mquake): capoff: KL=0.00712334183, signed ΔNLL=0.00714615798; original: KL=0.00712334183, signed ΔNLL=0.00714615798 nats.
- Breach b1d1e53944241333ec5603d4 (R1_learned_ff/mquake): capoff: KL=0.00712334183, signed ΔNLL=0.00714615798; original: KL=0.00712334183, signed ΔNLL=0.00714615798 nats.
- Breach 0b6ade77641a02c1c85574b0 (R1_nonlearned/counterfact): capoff: KL=0.0597793412, signed ΔNLL=0.0595263036; original: KL=0.0597793412, signed ΔNLL=0.0595263036 nats.
- Breach ee67c592789829e7dd808ede (R1_nonlearned/counterfact): capoff: KL=0.0597805755, signed ΔNLL=0.0595312224; original: KL=0.0597805755, signed ΔNLL=0.0595312224 nats.
- Breach 8be432675ed4dc57f9108bd4 (R1_nonlearned/counterfact): capoff: KL=0.0597793412, signed ΔNLL=0.0595263036; original: KL=0.0597793412, signed ΔNLL=0.0595263036 nats.
- Breach 78928f2782d91d888ef24d52 (R1_nonlearned/counterfact): capoff: KL=0.0597793412, signed ΔNLL=0.0595263036; original: KL=0.0597793412, signed ΔNLL=0.0595263036 nats.
- Breach de0b9612418e6d573ed77679 (R1_nonlearned/mquake): capoff: KL=0.0121762507, signed ΔNLL=0.0120472241; original: KL=0.0121762507, signed ΔNLL=0.0120472241 nats.
- Breach de785feed05c9f4c2a9e9273 (R1_nonlearned/counterfact): capoff: KL=0.0597793412, signed ΔNLL=0.0595263036; original: KL=0.0597793412, signed ΔNLL=0.0595263036 nats.
- Breach be37e2a1ff4a079e56efe268 (R1_nonlearned/mquake): capoff: KL=0.0121762507, signed ΔNLL=0.0120472241; original: KL=0.0121762507, signed ΔNLL=0.0120472241 nats.
- Breach 1e6b766c4139230c18547234 (R1_nonlearned/mquake): capoff: KL=0.0121762507, signed ΔNLL=0.0120472241; original: KL=0.0121762507, signed ΔNLL=0.0120472241 nats.
- Breach c0a54c5fbf1ce7776efc983e (R1_nonlearned/mquake): capoff: KL=0.0121762507, signed ΔNLL=0.0120472241; original: KL=0.0121762507, signed ΔNLL=0.0120472241 nats.
- Breach 7499c19b813dcada2c67ae39 (R1_nonlearned/mquake): capoff: KL=0.0121762507, signed ΔNLL=0.0120472241; original: KL=0.0121762507, signed ΔNLL=0.0120472241 nats.
- Breach 39c7fd4929721e8dcba56b94 (v0_stable/zsre): capoff: KL=0.00116430329, signed ΔNLL=0.000860380696; original: KL=0.00116430329, signed ΔNLL=0.000860380696 nats.
- Breach b887b1046cd563d990765e01 (v0_stable/zsre): capoff: KL=0.00185172225, signed ΔNLL=0.00155231076; original: KL=0.00185172225, signed ΔNLL=0.00155231076 nats.
- Breach aaed1cf9e8ce7cf1cf3749fa (v0_stable/zsre): capoff: KL=0.00145363992, signed ΔNLL=0.00120613705; original: KL=0.00145363992, signed ΔNLL=0.00120613705 nats.
- Breach 92a5ef6855124ffc5a8d6163 (v0_stable/zsre): capoff: KL=0.00153617076, signed ΔNLL=0.00116742865; original: KL=0.00153617076, signed ΔNLL=0.00116742865 nats.
- Breach 47dac9d968ffe594faac0a14 (R1_learned_ff/zsre): capoff: KL=0.00244796963, signed ΔNLL=0.00255302086; original: KL=0.00244796963, signed ΔNLL=0.00255302086 nats.
- Breach 6b089d284c00a4418a1d3af4 (R1_learned_ff/zsre): capoff: KL=0.00244796963, signed ΔNLL=0.00255302086; original: KL=0.00244796963, signed ΔNLL=0.00255302086 nats.
- Breach ab774e229a65298fdc117c96 (R1_learned_ff/zsre): capoff: KL=0.00244796963, signed ΔNLL=0.00255302086; original: KL=0.00244796963, signed ΔNLL=0.00255302086 nats.
- Breach 4eda9e6155b2755508e13091 (R1_learned_ff/zsre): capoff: KL=0.00244796963, signed ΔNLL=0.00255302086; original: KL=0.00244796963, signed ΔNLL=0.00255302086 nats.
- Breach 826332f387bd487a045d412f (R1_learned_ff/counterfact): capoff: KL=0.00472786236, signed ΔNLL=0.00462080141; original: KL=0.00472786236, signed ΔNLL=0.00462080141 nats.
- Breach b4e7dc307a1f895a8fec997a (R1_learned_ff/zsre): capoff: KL=0.00244796963, signed ΔNLL=0.00255302086; original: KL=0.00244796963, signed ΔNLL=0.00255302086 nats.
- Breach 14d45f0e87126104057518af (R1_learned_ff/counterfact): capoff: KL=0.00472786236, signed ΔNLL=0.00462080141; original: KL=0.00472786236, signed ΔNLL=0.00462080141 nats.
- Breach 960d0adeb6cacfcfce93d546 (R1_learned_ff/counterfact): capoff: KL=0.00472786236, signed ΔNLL=0.00462080141; original: KL=0.00472786236, signed ΔNLL=0.00462080141 nats.
- Breach 6840a40e6e5c90bdc40b89b0 (R1_learned_ff/counterfact): capoff: KL=0.00472786236, signed ΔNLL=0.00462080141; original: KL=0.00472786236, signed ΔNLL=0.00462080141 nats.
- Breach 42ba32e4f07423bee03296b3 (R1_learned_ff/counterfact): capoff: KL=0.00472786236, signed ΔNLL=0.00462080141; original: KL=0.00472786236, signed ΔNLL=0.00462080141 nats.
- Breach 19964c4e7f737707baad94a5 (R1_learned_ff/mquake): capoff: KL=0.00693695516, signed ΔNLL=0.0069390173; original: KL=0.00693695516, signed ΔNLL=0.0069390173 nats.
- Breach 40ec11c9694b4265a013c682 (R1_learned_ff/mquake): capoff: KL=0.00693695516, signed ΔNLL=0.0069390173; original: KL=0.00693695516, signed ΔNLL=0.0069390173 nats.
- Breach f0642100f6eb9cd77e92f439 (R1_learned_ff/mquake): capoff: KL=0.00693695516, signed ΔNLL=0.0069390173; original: KL=0.00693695516, signed ΔNLL=0.0069390173 nats.
- Breach b7ff3139c3f3eeb3ff7e9c80 (R1_learned_ff/mquake): capoff: KL=0.00693695516, signed ΔNLL=0.0069390173; original: KL=0.00693695516, signed ΔNLL=0.0069390173 nats.
- Breach 1833a410c9e8704f6a379114 (R1_learned_ff/mquake): capoff: KL=0.00693695516, signed ΔNLL=0.0069390173; original: KL=0.00693695516, signed ΔNLL=0.0069390173 nats.
- Breach a7d551c093fd3333314813a5 (R1_nonlearned/counterfact): capoff: KL=0.0893393566, signed ΔNLL=0.0882374117; original: KL=0.0893393566, signed ΔNLL=0.0882374117 nats.
- Breach c402523c2460a62d6040ddd0 (R1_nonlearned/counterfact): capoff: KL=0.0893393566, signed ΔNLL=0.0882374117; original: KL=0.0893393566, signed ΔNLL=0.0882374117 nats.
- Breach b103826472ba7653cd8fd13a (R1_nonlearned/counterfact): capoff: KL=0.0893393566, signed ΔNLL=0.0882374117; original: KL=0.0893393566, signed ΔNLL=0.0882374117 nats.
- Breach 525ad705ad7008ed3ea378eb (R1_nonlearned/counterfact): capoff: KL=0.0893393566, signed ΔNLL=0.0882374117; original: KL=0.0893393566, signed ΔNLL=0.0882374117 nats.
- Breach 144f77ff21860a8a089a8080 (R1_nonlearned/mquake): capoff: KL=0.0121116549, signed ΔNLL=0.0120871469; original: KL=0.0121116549, signed ΔNLL=0.0120871469 nats.
- Breach 8a4bcb6e358e98c523b0d0c3 (R1_nonlearned/counterfact): capoff: KL=0.0893393566, signed ΔNLL=0.0882374117; original: KL=0.0893393566, signed ΔNLL=0.0882374117 nats.
- Breach 3c3212c0cad597bafe0d5782 (R1_nonlearned/mquake): capoff: KL=0.0121116549, signed ΔNLL=0.0120871469; original: KL=0.0121116549, signed ΔNLL=0.0120871469 nats.
- Breach 5d467b73f60b99b3d07f8c02 (R1_nonlearned/mquake): capoff: KL=0.0121116549, signed ΔNLL=0.0120871469; original: KL=0.0121116549, signed ΔNLL=0.0120871469 nats.
- Breach a81b13b1b22e0bfe489daaa0 (R1_nonlearned/mquake): capoff: KL=0.0121116549, signed ΔNLL=0.0120871469; original: KL=0.0121116549, signed ΔNLL=0.0120871469 nats.
- Breach 1aff34869825a76d502d92a3 (R1_nonlearned/mquake): capoff: KL=0.0121116549, signed ΔNLL=0.0120871469; original: KL=0.0121116549, signed ΔNLL=0.0120871469 nats.
- Breach 3b70d3d44297fc1197610228 (v0_stable/zsre): capoff: KL=0.00157182194, signed ΔNLL=0.00159125899; original: KL=0.00157182194, signed ΔNLL=0.00159125899 nats.
- Breach 84bae28d26e5f5a3e555b601 (v0_stable/zsre): capoff: KL=0.00274030374, signed ΔNLL=0.00277312077; original: KL=0.00274030374, signed ΔNLL=0.00277312077 nats.
- Breach 07b9bad1f676110cb8bae7df (v0_stable/zsre): capoff: KL=0.00210475478, signed ΔNLL=0.00207833317; original: KL=0.00210475478, signed ΔNLL=0.00207833317 nats.
- Breach 0ff8a61a760d6836f469629b (v0_stable/zsre): capoff: KL=0.00150803199, signed ΔNLL=0.00157451785; original: KL=0.00150803199, signed ΔNLL=0.00157451785 nats.
- Breach 40034291ac69439c82ae1fc3 (v0_stable/zsre): capoff: KL=0.00147808841, signed ΔNLL=0.00145741336; original: KL=0.00147808841, signed ΔNLL=0.00145741336 nats.
- Breach 0417f598d89548e3200a3fe4 (R1_learned_ff/zsre): capoff: KL=0.0023297505, signed ΔNLL=0.00245432284; original: KL=0.0023297505, signed ΔNLL=0.00245432284 nats.
- Breach 12a9c0da62781d521da26cd5 (R1_learned_ff/zsre): capoff: KL=0.00232975058, signed ΔNLL=0.00245432286; original: KL=0.00232975058, signed ΔNLL=0.00245432286 nats.
- Breach c2a67190edb39398491bd651 (R1_learned_ff/zsre): capoff: KL=0.0023297505, signed ΔNLL=0.00245432284; original: KL=0.0023297505, signed ΔNLL=0.00245432284 nats.
- Breach 58cc3599099d7ab60e5d1413 (R1_learned_ff/zsre): capoff: KL=0.0023297505, signed ΔNLL=0.00245432284; original: KL=0.0023297505, signed ΔNLL=0.00245432284 nats.
- Breach fa46e16c8436f7ea4a5c3f06 (R1_learned_ff/counterfact): capoff: KL=0.00578063758, signed ΔNLL=0.00602331743; original: KL=0.00578063758, signed ΔNLL=0.00602331743 nats.
- Breach 4206e18c23b43bb312e045e6 (R1_learned_ff/zsre): capoff: KL=0.0023297505, signed ΔNLL=0.00245432284; original: KL=0.0023297505, signed ΔNLL=0.00245432284 nats.
- Breach 162686f6303fe986619d236d (R1_learned_ff/counterfact): capoff: KL=0.00578063758, signed ΔNLL=0.00602331743; original: KL=0.00578063758, signed ΔNLL=0.00602331743 nats.
- Breach 029ecd260f3e085063714d3f (R1_learned_ff/counterfact): capoff: KL=0.00578063758, signed ΔNLL=0.00602331743; original: KL=0.00578063758, signed ΔNLL=0.00602331743 nats.
- Breach 7197775fb7f97a465fd3310e (R1_learned_ff/counterfact): capoff: KL=0.00578063758, signed ΔNLL=0.00602331743; original: KL=0.00578063758, signed ΔNLL=0.00602331743 nats.
- Breach 6de7e97b6cb167d048dc31ba (R1_learned_ff/counterfact): capoff: KL=0.00578063758, signed ΔNLL=0.00602331743; original: KL=0.00578063758, signed ΔNLL=0.00602331743 nats.
- Breach fcd702d12d5d6bfae824379b (R1_learned_ff/mquake): capoff: KL=0.00409200039, signed ΔNLL=0.00413584786; original: KL=0.00409200039, signed ΔNLL=0.00413584786 nats.
- Breach 9a1d038b95f534b43185c7fc (R1_learned_ff/mquake): capoff: KL=0.00409200039, signed ΔNLL=0.00413584786; original: KL=0.00409200039, signed ΔNLL=0.00413584786 nats.
- Breach dfc9c9b480e482911c457e07 (R1_learned_ff/mquake): capoff: KL=0.00409200039, signed ΔNLL=0.00413584786; original: KL=0.00409200039, signed ΔNLL=0.00413584786 nats.
- Breach 34fce88c919bcae6410e4d94 (R1_learned_ff/mquake): capoff: KL=0.00409200039, signed ΔNLL=0.00413584786; original: KL=0.00409200039, signed ΔNLL=0.00413584786 nats.
- Breach 7a39ae192fb0b1038c651f64 (R1_learned_ff/mquake): capoff: KL=0.00409200039, signed ΔNLL=0.00413584786; original: KL=0.00409200039, signed ΔNLL=0.00413584786 nats.
- Breach 6ed2474713b3a311b4ec6b08 (R1_nonlearned/counterfact): capoff: KL=0.0642258214, signed ΔNLL=0.0641210631; original: KL=0.0642258214, signed ΔNLL=0.0641210631 nats.
- Breach f939f211b98675ac7c2d951f (R1_nonlearned/counterfact): capoff: KL=0.0642258214, signed ΔNLL=0.0641210631; original: KL=0.0642258214, signed ΔNLL=0.0641210631 nats.
- Breach 19b5e9b462930c6f50f2e2f6 (R1_nonlearned/counterfact): capoff: KL=0.0642258214, signed ΔNLL=0.0641210631; original: KL=0.0642258214, signed ΔNLL=0.0641210631 nats.
- Breach b14576e3d752f467db2abf18 (R1_nonlearned/counterfact): capoff: KL=0.0642258214, signed ΔNLL=0.0641210631; original: KL=0.0642258214, signed ΔNLL=0.0641210631 nats.
- Breach 9e98169ae668b50d60694317 (R1_nonlearned/mquake): capoff: KL=0.0122293305, signed ΔNLL=0.012170898; original: KL=0.0122293305, signed ΔNLL=0.012170898 nats.
- Breach da9f71bdb9a8981dac078e6c (R1_nonlearned/counterfact): capoff: KL=0.0642258214, signed ΔNLL=0.0641210631; original: KL=0.0642258214, signed ΔNLL=0.0641210631 nats.
- Breach ff570734d7837a1ba9e77528 (R1_nonlearned/mquake): capoff: KL=0.0122293305, signed ΔNLL=0.012170898; original: KL=0.0122293305, signed ΔNLL=0.012170898 nats.
- Breach 4fd2bc51397502cb1c085b5c (R1_nonlearned/mquake): capoff: KL=0.0122293305, signed ΔNLL=0.012170898; original: KL=0.0122293305, signed ΔNLL=0.012170898 nats.
- Breach c0e77c94b06dd3464838be93 (R1_nonlearned/mquake): capoff: KL=0.0122293305, signed ΔNLL=0.012170898; original: KL=0.0122293305, signed ΔNLL=0.012170898 nats.
- Breach 4c700c665ce70ca41e4569dd (R1_nonlearned/mquake): capoff: KL=0.0122293305, signed ΔNLL=0.012170898; original: KL=0.0122293305, signed ΔNLL=0.012170898 nats.
- Breach dc17fc3637068157dba0207d (v0_stable/zsre): capoff: KL=0.00176906236, signed ΔNLL=0.00177843036; original: KL=0.00176906236, signed ΔNLL=0.00177843036 nats.
- Breach 727b32ab9723cb9feba71636 (v0_stable/zsre): capoff: KL=0.0018515355, signed ΔNLL=0.00174309252; original: KL=0.0018515355, signed ΔNLL=0.00174309252 nats.
- Breach a02980b0886a222f8e2f58e8 (v0_stable/zsre): capoff: KL=0.00146957248, signed ΔNLL=0.00139979674; original: KL=0.00146957248, signed ΔNLL=0.00139979674 nats.
- Breach 9aeb330f6c7e29c85ee56da0 (v0_stable/zsre): capoff: KL=0.00179551527, signed ΔNLL=0.00177256889; original: KL=0.00179551527, signed ΔNLL=0.00177256889 nats.
- Breach 0e0ee9a35e1116f7dafb423d (v0_stable/zsre): capoff: KL=0.00161644683, signed ΔNLL=0.00151745434; original: KL=0.00161644683, signed ΔNLL=0.00151745434 nats.
- Breach 1689630f5ad581d9fcfc483e (matched_update/zsre): capoff: KL=0.00176723623, signed ΔNLL=0.00151014098; original: KL=0.00176723623, signed ΔNLL=0.00151014098 nats.
- Breach c897cd3d2a3b35bfe999e87e (matched_update/zsre): capoff: KL=0.00121984113, signed ΔNLL=0.000875292159; original: KL=0.00121984113, signed ΔNLL=0.000875292159 nats.
- Breach d1690029ea53ae03b3705536 (matched_update/zsre): capoff: KL=0.00131268298, signed ΔNLL=0.00104193105; original: KL=0.00131268298, signed ΔNLL=0.00104193105 nats.
- Breach a921f9ab5443f978e56d2390 (matched_update/zsre): capoff: KL=0.00151340823, signed ΔNLL=0.00114126488; original: KL=0.00151340823, signed ΔNLL=0.00114126488 nats.
- Breach a86da75220343c5560c45373 (matched_update/zsre): capoff: KL=0.00147329583, signed ΔNLL=0.0014577346; original: KL=0.00147329583, signed ΔNLL=0.0014577346 nats.
- Breach 735081421354eaafb893322d (matched_update/zsre): capoff: KL=0.00194985876, signed ΔNLL=0.00188407825; original: KL=0.00194985876, signed ΔNLL=0.00188407825 nats.
- Breach e7b52c6db370d10a5fd7d891 (matched_update/zsre): capoff: KL=0.00294680114, signed ΔNLL=0.00297092361; original: KL=0.00294680114, signed ΔNLL=0.00297092361 nats.
- Breach 824f602358ace0fc5cb69271 (matched_update/zsre): capoff: KL=0.00141327436, signed ΔNLL=0.00140751012; original: KL=0.00141327436, signed ΔNLL=0.00140751012 nats.
- Breach 3bc2cef1ca9bab6e4a90e222 (matched_update/zsre): capoff: KL=0.00133689269, signed ΔNLL=0.00120777318; original: KL=0.00133689269, signed ΔNLL=0.00120777318 nats.
- Breach 58879f9745ed479686bd0481 (matched_update/zsre): capoff: KL=0.00180744486, signed ΔNLL=0.00175673502; original: KL=0.00180744486, signed ΔNLL=0.00175673502 nats.
- Breach 9c3c7c258bf086523ea6268e (matched_update/zsre): capoff: KL=0.00176791473, signed ΔNLL=0.0019178878; original: KL=0.00176791473, signed ΔNLL=0.0019178878 nats.
- Breach b6ea6d9e337e3bf6f2eca5d2 (matched_update/zsre): capoff: KL=0.00158095191, signed ΔNLL=0.00152371108; original: KL=0.00158095191, signed ΔNLL=0.00152371108 nats.
- Breach 16037ce355e4a2e9a43a2008 (matched_update/zsre): capoff: KL=0.00181159328, signed ΔNLL=0.00181432162; original: KL=0.00181159328, signed ΔNLL=0.00181432162 nats.
- Breach 4597af8473d8e404f1490c57 (matched_update/zsre): capoff: KL=0.00151989145, signed ΔNLL=0.00147457467; original: KL=0.00151989145, signed ΔNLL=0.00147457467 nats.
- Breach 509cd28130eb44d35b27d08a (v0_live_C1/zsre): capoff: KL=0.00103373963, signed ΔNLL=0.000822536835; original: KL=0.00103373963, signed ΔNLL=0.000822536835 nats.
- Breach a8a5ddc06de26a9885f75fe9 (v0_live_C1/zsre): capoff: KL=0.00150913358, signed ΔNLL=0.00125983381; original: KL=0.00150913358, signed ΔNLL=0.00125983381 nats.
- Breach 5f818373c34233809fc57716 (v0_live_C1/zsre): capoff: KL=0.00201157954, signed ΔNLL=0.00174068841; original: KL=0.00201157954, signed ΔNLL=0.00174068841 nats.
- Breach baa8eccee6a4f8c27c11a09c (v0_live_C1/zsre): capoff: KL=0.002383688, signed ΔNLL=0.00203885374; original: KL=0.002383688, signed ΔNLL=0.00203885374 nats.
- Breach 2a91e17773f7272dbd36a048 (v0_live_C1/zsre): capoff: KL=0.00160592363, signed ΔNLL=0.00129945079; original: KL=0.00160592363, signed ΔNLL=0.00129945079 nats.
- Breach d0a5df19a69792ac87a703dc (v0_live_C1/zsre): capoff: KL=0.00298034806, signed ΔNLL=0.00301616427; original: KL=0.00298034806, signed ΔNLL=0.00301616427 nats.
- Breach 6d6930dcd4fe737e4d1ef3ed (v0_live_C1/zsre): capoff: KL=0.00301647378, signed ΔNLL=0.00300556668; original: KL=0.00301647378, signed ΔNLL=0.00300556668 nats.
- Breach cf9c6af6097c6d96c9a5a1d3 (v0_live_C1/zsre): capoff: KL=0.00277349123, signed ΔNLL=0.00273108911; original: KL=0.00277349123, signed ΔNLL=0.00273108911 nats.
- Breach 5d52bba4bd205ffecf96212a (v0_live_C1/zsre): capoff: KL=0.0015499897, signed ΔNLL=0.00143388942; original: KL=0.0015499897, signed ΔNLL=0.00143388942 nats.
- Breach ed2fff6199cac50f8e3c05d9 (v0_live_C1/zsre): capoff: KL=0.00355726558, signed ΔNLL=0.00358599299; original: KL=0.00355726558, signed ΔNLL=0.00358599299 nats.
- Breach e82412060e54893dc307a45e (v0_live_C1/zsre): capoff: KL=0.00205975781, signed ΔNLL=0.00190120048; original: KL=0.00205975781, signed ΔNLL=0.00190120048 nats.
- Breach b42dfb1e539cb4645127e844 (v0_live_C1/zsre): capoff: KL=0.00127431583, signed ΔNLL=0.00120930409; original: KL=0.00127431583, signed ΔNLL=0.00120930409 nats.
- Breach 2fe9909dbaad17941716efc9 (v0_live_C1/zsre): capoff: KL=0.00174477466, signed ΔNLL=0.00162531626; original: KL=0.00174477466, signed ΔNLL=0.00162531626 nats.
- Breach e45d4b2c01fc48117d5abec8 (v0_live_C1/zsre): capoff: KL=0.0020722334, signed ΔNLL=0.00202505712; original: KL=0.0020722334, signed ΔNLL=0.00202505712 nats.
- Breach bca38cd4398e1159ed781bff (v0_live_C2/zsre): capoff: KL=0.00304642004, signed ΔNLL=0.00263713932; original: KL=0.00304642004, signed ΔNLL=0.00263713932 nats.
- Breach 68da09e4a00f4fe8d8b054fd (v0_live_C2/zsre): capoff: KL=0.00294821161, signed ΔNLL=0.00287266322; original: KL=0.00294821161, signed ΔNLL=0.00287266322 nats.
- Breach da666451073f38000c71b39f (v0_live_C2/zsre): capoff: KL=0.00206384537, signed ΔNLL=0.00211930843; original: KL=0.00206384537, signed ΔNLL=0.00211930843 nats.
- Breach 57b0ace8ad261f0963cece6e (v0_live_C2/zsre): capoff: KL=0.00185480342, signed ΔNLL=0.0018750982; original: KL=0.00185480342, signed ΔNLL=0.0018750982 nats.
- Breach b1be521b209066effb830ad1 (v0_live_C2/zsre): capoff: KL=0.00286781113, signed ΔNLL=0.00255053692; original: KL=0.00286781113, signed ΔNLL=0.00255053692 nats.
- Breach d246da52d2783b0000af34aa (v0_live_C2/zsre): capoff: KL=0.00253308328, signed ΔNLL=0.00263297516; original: KL=0.00253308328, signed ΔNLL=0.00263297516 nats.
- Breach 9ac1596b4a83bfd3759110f5 (v0_live_C2/zsre): capoff: KL=0.0055263108, signed ΔNLL=0.00563944129; original: KL=0.0055263108, signed ΔNLL=0.00563944129 nats.
- Breach d3e7acfb899406015f6d7e6a (v0_live_C2/zsre): capoff: KL=0.00462954419, signed ΔNLL=0.00473148347; original: KL=0.00462954419, signed ΔNLL=0.00473148347 nats.
- Breach 1b91b6d6beb187aaf9103cdc (v0_live_C2/zsre): capoff: KL=0.00222367747, signed ΔNLL=0.00217552064; original: KL=0.00222367747, signed ΔNLL=0.00217552064 nats.
- Breach 9a600f5f46fa47c339ccb4d1 (v0_live_C2/zsre): capoff: KL=0.00206487186, signed ΔNLL=0.0020251027; original: KL=0.00206487186, signed ΔNLL=0.0020251027 nats.
- Breach 635bac1c845730dae487891a (v0_live_C2/zsre): capoff: KL=0.00370336576, signed ΔNLL=0.00399326561; original: KL=0.00370336576, signed ΔNLL=0.00399326561 nats.
- Breach 031ae1822109079d3cddb520 (v0_live_C2/zsre): capoff: KL=0.00283241814, signed ΔNLL=0.00287301292; original: KL=0.00283241814, signed ΔNLL=0.00287301292 nats.
- Breach 3435ab1a884c517b32867161 (v0_live_C2/zsre): capoff: KL=0.0034919806, signed ΔNLL=0.00359086577; original: KL=0.0034919806, signed ΔNLL=0.00359086577 nats.
- Breach 09d4451a2a5b030d1853c267 (v0_live_C2/zsre): capoff: KL=0.00506942905, signed ΔNLL=0.00524466863; original: KL=0.00506942905, signed ΔNLL=0.00524466863 nats.
- Breach fa309fa719c353f20a813699 (v0_live_C2/zsre): capoff: KL=0.00301804878, signed ΔNLL=0.0030098935; original: KL=0.00301804878, signed ΔNLL=0.0030098935 nats.
- Breach 982870b0fcc4a8bef4a297af (S1_LM/zsre): capoff: KL=0.00185270859, signed ΔNLL=0.00155182671; original: KL=0.00203840528, signed ΔNLL=-0.00228216171 nats.
- Breach 74feefbadad2b95947437ed6 (S1_LM/zsre): capoff: KL=0.00116170877, signed ΔNLL=0.000848816588; original: KL=0.00135123302, signed ΔNLL=-0.00298517184 nats.
- Breach 2e5068d168160234340d32fa (S1_LM/zsre): capoff: KL=0.000815818477, signed ΔNLL=0.000630912139; original: KL=0.00100491751, signed ΔNLL=-0.00320307629 nats.
- Breach f642d1e953d4e4b42c9a916e (S1_LM/zsre): capoff: KL=0.00145930461, signed ΔNLL=0.00120000979; original: KL=0.00164650365, signed ΔNLL=-0.00263397864 nats.
- Breach d7884b1e2a9c1c3790535590 (S1_LM/zsre): capoff: KL=0.00158472176, signed ΔNLL=0.00120159969; original: KL=0.00177234686, signed ΔNLL=-0.00263238874 nats.
- Breach 8499903e83df71431114aaa8 (S1_LM/zsre): capoff: KL=0.00162092391, signed ΔNLL=0.00164128331; original: KL=0.00181021295, signed ΔNLL=-0.00219270511 nats.
- Breach 272db4c9310a73f01bf46d4b (S1_LM/zsre): capoff: KL=0.00272681993, signed ΔNLL=0.00275051779; original: KL=0.00291445692, signed ΔNLL=-0.00108347063 nats.
- Breach 9f020616201afdc368d77f9b (S1_LM/zsre): capoff: KL=0.00213860893, signed ΔNLL=0.00212110394; original: KL=0.00232814018, signed ΔNLL=-0.00171288449 nats.
- Breach 26318156d310334e8b260e87 (S1_LM/zsre): capoff: KL=0.00155333811, signed ΔNLL=0.00163480396; original: KL=0.00174434319, signed ΔNLL=-0.00219918446 nats.
- Breach d7241b9882514c2709082321 (S1_LM/zsre): capoff: KL=0.00151582569, signed ΔNLL=0.00149830876; original: KL=0.00170613203, signed ΔNLL=-0.00233567967 nats.
- Breach a5b3de3764680273ff4760e1 (S1_LM/zsre): capoff: KL=0.00176826546, signed ΔNLL=0.00178864168; original: KL=0.00196062065, signed ΔNLL=-0.00204534675 nats.
- Breach e5c2ea10bc6ce298f6065199 (S1_LM/zsre): capoff: KL=0.00183146366, signed ΔNLL=0.001764422; original: KL=0.00202370256, signed ΔNLL=-0.00206956643 nats.
- Breach 847f33277d9d89fe17482367 (S1_LM/zsre): capoff: KL=0.00146734244, signed ΔNLL=0.00141864528; original: KL=0.00165869811, signed ΔNLL=-0.00241534314 nats.
- Breach 77568a85e217721985cd8ea4 (S1_LM/zsre): capoff: KL=0.00181146197, signed ΔNLL=0.00181460663; original: KL=0.00200275621, signed ΔNLL=-0.0020193818 nats.
- Breach 793ee3d9708b970c08a0fbe2 (S1_LM/zsre): capoff: KL=0.00162011152, signed ΔNLL=0.00151530489; original: KL=0.00181003687, signed ΔNLL=-0.00231868353 nats.
- Breach b1a17c1fb747eef11f253278 (S1_literal/zsre): capoff: KL=0.00116482068, signed ΔNLL=0.000851688429; original: KL=0.00119393674, signed ΔNLL=0.00115598989 nats.
- Breach edb61534cb4ec7a4187ebbdb (S1_literal/zsre): capoff: KL=0.00188529585, signed ΔNLL=0.00156512037; original: KL=0.00191522153, signed ΔNLL=0.00186942183 nats.
- Breach 46d6404412a25fbdd2965880 (S1_literal/zsre): capoff: KL=0.00146269039, signed ΔNLL=0.00120361508; original: KL=0.001493871, signed ΔNLL=0.00150791654 nats.
- Breach 50af2a28b866c26021d83b01 (S1_literal/zsre): capoff: KL=0.00154752962, signed ΔNLL=0.00117519173; original: KL=0.00157835947, signed ΔNLL=0.00147949319 nats.
- Breach 22a5ac50d5ca3c952b8b1e34 (S1_literal/zsre): capoff: KL=0.0015837119, signed ΔNLL=0.00160444703; original: KL=0.00161191161, signed ΔNLL=0.00190874849 nats.
- Breach 7d93e4d997ec1f974bb6c71a (S1_literal/zsre): capoff: KL=0.00271355977, signed ΔNLL=0.00274716088; original: KL=0.00274182293, signed ΔNLL=0.00305146233 nats.
- Breach 0f466b21fb4514acd9d1ff1e (S1_literal/zsre): capoff: KL=0.00210770625, signed ΔNLL=0.00207632256; original: KL=0.00213622275, signed ΔNLL=0.00238062402 nats.
- Breach 151bacf1f85b74f88864784e (S1_literal/zsre): capoff: KL=0.00150625525, signed ΔNLL=0.00157074589; original: KL=0.00153456646, signed ΔNLL=0.00187504734 nats.
- Breach 330479ee3f94e169b8496e0b (S1_literal/zsre): capoff: KL=0.00147650996, signed ΔNLL=0.001454688; original: KL=0.00150454504, signed ΔNLL=0.00175898945 nats.
- Breach e4019672011694d495923c6f (S1_literal/zsre): capoff: KL=0.00177114837, signed ΔNLL=0.0017817335; original: KL=0.0018009734, signed ΔNLL=0.00208603495 nats.
- Breach bf89e6ad180b60ad56c35a7e (S1_literal/zsre): capoff: KL=0.00184990558, signed ΔNLL=0.00175298885; original: KL=0.00187997874, signed ΔNLL=0.00205729031 nats.
- Breach 70aacd394ef41b887377260a (S1_literal/zsre): capoff: KL=0.00146446055, signed ΔNLL=0.00141085928; original: KL=0.00149427458, signed ΔNLL=0.00171516074 nats.
- Breach 6885c03ed3db8fb41a5e20dd (S1_literal/zsre): capoff: KL=0.00161452472, signed ΔNLL=0.00152769544; original: KL=0.00164372151, signed ΔNLL=0.00183199689 nats.
- Breach b3f4ad21a596171a9a43e0aa (S1_literal/zsre): capoff: KL=0.00184752973, signed ΔNLL=0.00184103191; original: KL=0.00187753773, signed ΔNLL=0.00214533337 nats.
- CREEP ALERT 61348508e40d54351613ab14: capoff/mean_kl new_running_maximum: 0.00238149242 > 0.0022697245; capoff/mean_signed_nll_increase new_running_maximum: 0.00245022572 > 0.00231001529; original/mean_kl new_running_maximum: 0.00238149242 > 0.0022697245; original/mean_signed_nll_increase new_running_maximum: 0.00245022572 > 0.00231001529. Delivery remains pending orchestrator notification.
- CREEP ALERT 43925e53c31860219a85ef90: capoff/mean_kl new_running_maximum: 0.00712334183 > 0.00554368762; capoff/mean_signed_nll_increase new_running_maximum: 0.00714615798 > 0.00560097637; original/mean_kl new_running_maximum: 0.00712334183 > 0.00554368762; original/mean_signed_nll_increase new_running_maximum: 0.00714615798 > 0.00560097637. Delivery remains pending orchestrator notification.
- CREEP ALERT ee67c592789829e7dd808ede: capoff/mean_kl new_running_maximum: 0.0597805755 > 0.0597793412; capoff/mean_signed_nll_increase new_running_maximum: 0.0595312224 > 0.0595263036; original/mean_kl new_running_maximum: 0.0597805755 > 0.0597793412; original/mean_signed_nll_increase new_running_maximum: 0.0595312224 > 0.0595263036. Delivery remains pending orchestrator notification.
- CREEP ALERT 39c7fd4929721e8dcba56b94: capoff/mean_kl new_running_maximum: 0.00116430329 > 0.000788590677; capoff/mean_signed_nll_increase new_running_maximum: 0.000860380696 > 0.000855162037; original/mean_kl new_running_maximum: 0.00116430329 > 0.000788590677; original/mean_signed_nll_increase new_running_maximum: 0.000860380696 > 0.000855162037. Delivery remains pending orchestrator notification.
- CREEP ALERT b887b1046cd563d990765e01: capoff/mean_kl new_running_maximum: 0.00185172225 > 0.00116430329; capoff/mean_kl above_twice_development_reference: 0.00185172225 > 0.00157718135; capoff/mean_signed_nll_increase new_running_maximum: 0.00155231076 > 0.000860380696; original/mean_kl new_running_maximum: 0.00185172225 > 0.00116430329; original/mean_kl above_twice_development_reference: 0.00185172225 > 0.00157718135; original/mean_signed_nll_increase new_running_maximum: 0.00155231076 > 0.000860380696. Delivery remains pending orchestrator notification.
- CREEP ALERT 47dac9d968ffe594faac0a14: capoff/mean_kl new_running_maximum: 0.00244796963 > 0.00238149242; capoff/mean_signed_nll_increase new_running_maximum: 0.00255302086 > 0.00245022572; original/mean_kl new_running_maximum: 0.00244796963 > 0.00238149242; original/mean_signed_nll_increase new_running_maximum: 0.00255302086 > 0.00245022572. Delivery remains pending orchestrator notification.
- CREEP ALERT a7d551c093fd3333314813a5: capoff/mean_kl new_running_maximum: 0.0893393566 > 0.0597805755; capoff/mean_signed_nll_increase new_running_maximum: 0.0882374117 > 0.0595312224; original/mean_kl new_running_maximum: 0.0893393566 > 0.0597805755; original/mean_signed_nll_increase new_running_maximum: 0.0882374117 > 0.0595312224. Delivery remains pending orchestrator notification.
- CREEP ALERT 144f77ff21860a8a089a8080: capoff/mean_signed_nll_increase new_running_maximum: 0.0120871469 > 0.0120472241; original/mean_signed_nll_increase new_running_maximum: 0.0120871469 > 0.0120472241. Delivery remains pending orchestrator notification.
- CREEP ALERT 3b70d3d44297fc1197610228: capoff/mean_signed_nll_increase new_running_maximum: 0.00159125899 > 0.00155231076; original/mean_signed_nll_increase new_running_maximum: 0.00159125899 > 0.00155231076. Delivery remains pending orchestrator notification.
- CREEP ALERT 84bae28d26e5f5a3e555b601: capoff/mean_kl new_running_maximum: 0.00274030374 > 0.00185172225; capoff/mean_kl above_twice_development_reference: 0.00274030374 > 0.00157718135; capoff/mean_signed_nll_increase new_running_maximum: 0.00277312077 > 0.00159125899; capoff/mean_signed_nll_increase above_twice_development_reference: 0.00277312077 > 0.00171032407; original/mean_kl new_running_maximum: 0.00274030374 > 0.00185172225; original/mean_kl above_twice_development_reference: 0.00274030374 > 0.00157718135; original/mean_signed_nll_increase new_running_maximum: 0.00277312077 > 0.00159125899; original/mean_signed_nll_increase above_twice_development_reference: 0.00277312077 > 0.00171032407. Delivery remains pending orchestrator notification.
- CREEP ALERT 07b9bad1f676110cb8bae7df: capoff/mean_kl above_twice_development_reference: 0.00210475478 > 0.00157718135; capoff/mean_signed_nll_increase above_twice_development_reference: 0.00207833317 > 0.00171032407; original/mean_kl above_twice_development_reference: 0.00210475478 > 0.00157718135; original/mean_signed_nll_increase above_twice_development_reference: 0.00207833317 > 0.00171032407. Delivery remains pending orchestrator notification.
- CREEP ALERT fa46e16c8436f7ea4a5c3f06: capoff/mean_kl new_running_maximum: 0.00578063758 > 0.00576537791; capoff/mean_signed_nll_increase new_running_maximum: 0.00602331743 > 0.00584962582; original/mean_kl new_running_maximum: 0.00578063758 > 0.00576537791; original/mean_signed_nll_increase new_running_maximum: 0.00602331743 > 0.00584962582. Delivery remains pending orchestrator notification.
- CREEP ALERT 9e98169ae668b50d60694317: capoff/mean_kl new_running_maximum: 0.0122293305 > 0.0121762507; capoff/mean_signed_nll_increase new_running_maximum: 0.012170898 > 0.0120871469; original/mean_kl new_running_maximum: 0.0122293305 > 0.0121762507; original/mean_signed_nll_increase new_running_maximum: 0.012170898 > 0.0120871469. Delivery remains pending orchestrator notification.
- CREEP ALERT dc17fc3637068157dba0207d: capoff/mean_kl above_twice_development_reference: 0.00176906236 > 0.00157718135; capoff/mean_signed_nll_increase above_twice_development_reference: 0.00177843036 > 0.00171032407; original/mean_kl above_twice_development_reference: 0.00176906236 > 0.00157718135; original/mean_signed_nll_increase above_twice_development_reference: 0.00177843036 > 0.00171032407. Delivery remains pending orchestrator notification.
- CREEP ALERT 727b32ab9723cb9feba71636: capoff/mean_kl above_twice_development_reference: 0.0018515355 > 0.00157718135; capoff/mean_signed_nll_increase above_twice_development_reference: 0.00174309252 > 0.00171032407; original/mean_kl above_twice_development_reference: 0.0018515355 > 0.00157718135; original/mean_signed_nll_increase above_twice_development_reference: 0.00174309252 > 0.00171032407. Delivery remains pending orchestrator notification.
- CREEP ALERT 9aeb330f6c7e29c85ee56da0: capoff/mean_kl above_twice_development_reference: 0.00179551527 > 0.00157718135; capoff/mean_signed_nll_increase above_twice_development_reference: 0.00177256889 > 0.00171032407; original/mean_kl above_twice_development_reference: 0.00179551527 > 0.00157718135; original/mean_signed_nll_increase above_twice_development_reference: 0.00177256889 > 0.00171032407. Delivery remains pending orchestrator notification.
- CREEP ALERT 0e0ee9a35e1116f7dafb423d: capoff/mean_kl above_twice_development_reference: 0.00161644683 > 0.00157718135; original/mean_kl above_twice_development_reference: 0.00161644683 > 0.00157718135. Delivery remains pending orchestrator notification.
- CREEP ALERT 735081421354eaafb893322d: capoff/mean_kl new_running_maximum: 0.00194985876 > 0.00176723623; capoff/mean_signed_nll_increase new_running_maximum: 0.00188407825 > 0.00151014098; original/mean_kl new_running_maximum: 0.00194985876 > 0.00176723623; original/mean_signed_nll_increase new_running_maximum: 0.00188407825 > 0.00151014098. Delivery remains pending orchestrator notification.
- CREEP ALERT e7b52c6db370d10a5fd7d891: capoff/mean_kl new_running_maximum: 0.00294680114 > 0.00194985876; capoff/mean_signed_nll_increase new_running_maximum: 0.00297092361 > 0.00188407825; original/mean_kl new_running_maximum: 0.00294680114 > 0.00194985876; original/mean_signed_nll_increase new_running_maximum: 0.00297092361 > 0.00188407825. Delivery remains pending orchestrator notification.
- CREEP ALERT a8a5ddc06de26a9885f75fe9: capoff/mean_kl new_running_maximum: 0.00150913358 > 0.00103373963; capoff/mean_signed_nll_increase new_running_maximum: 0.00125983381 > 0.000822536835; original/mean_kl new_running_maximum: 0.00150913358 > 0.00103373963; original/mean_signed_nll_increase new_running_maximum: 0.00125983381 > 0.000822536835. Delivery remains pending orchestrator notification.
- CREEP ALERT 5f818373c34233809fc57716: capoff/mean_kl new_running_maximum: 0.00201157954 > 0.00150913358; capoff/mean_signed_nll_increase new_running_maximum: 0.00174068841 > 0.00125983381; original/mean_kl new_running_maximum: 0.00201157954 > 0.00150913358; original/mean_signed_nll_increase new_running_maximum: 0.00174068841 > 0.00125983381. Delivery remains pending orchestrator notification.
- CREEP ALERT baa8eccee6a4f8c27c11a09c: capoff/mean_kl new_running_maximum: 0.002383688 > 0.00201157954; capoff/mean_signed_nll_increase new_running_maximum: 0.00203885374 > 0.00174068841; original/mean_kl new_running_maximum: 0.002383688 > 0.00201157954; original/mean_signed_nll_increase new_running_maximum: 0.00203885374 > 0.00174068841. Delivery remains pending orchestrator notification.
- CREEP ALERT d0a5df19a69792ac87a703dc: capoff/mean_kl new_running_maximum: 0.00298034806 > 0.002383688; capoff/mean_signed_nll_increase new_running_maximum: 0.00301616427 > 0.00203885374; original/mean_kl new_running_maximum: 0.00298034806 > 0.002383688; original/mean_signed_nll_increase new_running_maximum: 0.00301616427 > 0.00203885374. Delivery remains pending orchestrator notification.
- CREEP ALERT 6d6930dcd4fe737e4d1ef3ed: capoff/mean_kl new_running_maximum: 0.00301647378 > 0.00298034806; original/mean_kl new_running_maximum: 0.00301647378 > 0.00298034806. Delivery remains pending orchestrator notification.
- CREEP ALERT ed2fff6199cac50f8e3c05d9: capoff/mean_kl new_running_maximum: 0.00355726558 > 0.00301647378; capoff/mean_signed_nll_increase new_running_maximum: 0.00358599299 > 0.00301616427; original/mean_kl new_running_maximum: 0.00355726558 > 0.00301647378; original/mean_signed_nll_increase new_running_maximum: 0.00358599299 > 0.00301616427. Delivery remains pending orchestrator notification.
- CREEP ALERT 68da09e4a00f4fe8d8b054fd: capoff/mean_signed_nll_increase new_running_maximum: 0.00287266322 > 0.00263713932; original/mean_signed_nll_increase new_running_maximum: 0.00287266322 > 0.00263713932. Delivery remains pending orchestrator notification.
- CREEP ALERT 9ac1596b4a83bfd3759110f5: capoff/mean_kl new_running_maximum: 0.0055263108 > 0.00304642004; capoff/mean_signed_nll_increase new_running_maximum: 0.00563944129 > 0.00287266322; original/mean_kl new_running_maximum: 0.0055263108 > 0.00304642004; original/mean_signed_nll_increase new_running_maximum: 0.00563944129 > 0.00287266322. Delivery remains pending orchestrator notification.
- CREEP ALERT 8499903e83df71431114aaa8: capoff/mean_signed_nll_increase new_running_maximum: 0.00164128331 > 0.00155182671; original/mean_signed_nll_increase new_running_maximum: -0.00219270511 > -0.00228216171. Delivery remains pending orchestrator notification.
- CREEP ALERT 272db4c9310a73f01bf46d4b: capoff/mean_kl new_running_maximum: 0.00272681993 > 0.00185270859; capoff/mean_signed_nll_increase new_running_maximum: 0.00275051779 > 0.00164128331; original/mean_kl new_running_maximum: 0.00291445692 > 0.00203840528; original/mean_signed_nll_increase new_running_maximum: -0.00108347063 > -0.00219270511. Delivery remains pending orchestrator notification.
- CREEP ALERT edb61534cb4ec7a4187ebbdb: capoff/mean_kl new_running_maximum: 0.00188529585 > 0.00116482068; capoff/mean_signed_nll_increase new_running_maximum: 0.00156512037 > 0.000851688429; original/mean_kl new_running_maximum: 0.00191522153 > 0.00119393674; original/mean_signed_nll_increase new_running_maximum: 0.00186942183 > 0.00115598989. Delivery remains pending orchestrator notification.
- CREEP ALERT 22a5ac50d5ca3c952b8b1e34: capoff/mean_signed_nll_increase new_running_maximum: 0.00160444703 > 0.00156512037; original/mean_signed_nll_increase new_running_maximum: 0.00190874849 > 0.00186942183. Delivery remains pending orchestrator notification.
- CREEP ALERT 7d93e4d997ec1f974bb6c71a: capoff/mean_kl new_running_maximum: 0.00271355977 > 0.00188529585; capoff/mean_signed_nll_increase new_running_maximum: 0.00274716088 > 0.00160444703; original/mean_kl new_running_maximum: 0.00274182293 > 0.00191522153; original/mean_signed_nll_increase new_running_maximum: 0.00305146233 > 0.00190874849. Delivery remains pending orchestrator notification.
Checks: no snapshot/accounting/watch gaps detected
Boundary ready: True; unprocessed cells through boundary: []; accounting/watch gap cells through boundary: [].
Known process-hours through this boundary: 308.369269. Later active blocks can leave the whole-matrix spend/projection incomplete without reopening this boundary.
Artifact completeness does not assert benchmark success, effect significance, admission or launch authority.
This text has not been posted; creep alerts require immediate owner relay, not a wait for the next boundary.
Report digest: 7bbaff437d8c20f48058434752e890dabc18c458b983c5674cf67f6c07e9cbbf

This text has not been posted to the lead queue. Cost proposals are not signatures.
Plan digest: 4353410c0f398b03a21d6e9eb04ef8a62691a64180ce3cf37ba0bec18bff6c17
