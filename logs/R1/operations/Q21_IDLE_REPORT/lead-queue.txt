# Execution plan v4 — block 2 cost proposal

Synthetic rehearsal: False. Unsigned; active ceilings are unchanged.

Measured class replacements: 9/22; remaining classes retain plan-v3 estimates.
Actual spend: 93.913283 process h; expected total: 424.341747; proposed ceiling total: 590.765870.
Buffer against 750 h: expected 325.658253; proposed ceilings 159.234130.
Active admitted ceiling projection (unchanged): 593.038419 h.

| Condition / dataset / edits / checkpoints | N measured | Expected process s | Proposed effective ceiling s | Basis |
|---|---:|---:|---:|---|
| R1_learned_ff / zsre / 1000 / [100, 300, 1000] | 10 | 4426.794 | 6724.217 | measured_completed_cell_process_envelopes |
| R1_learned_ff / counterfact / 1000 / [100, 300, 1000] | 10 | 4274.914 | 6459.537 | measured_completed_cell_process_envelopes |
| R1_learned_ff / mquake / 300 / [100, 300] | 10 | 2110.028 | 3186.726 | measured_completed_cell_process_envelopes |
| R1_nonlearned / zsre / 1000 / [100, 300, 1000] | 10 | 2163.723 | 3345.940 | measured_completed_cell_process_envelopes |
| R1_nonlearned / counterfact / 1000 / [100, 300, 1000] | 10 | 2141.068 | 3283.789 | measured_completed_cell_process_envelopes |
| R1_nonlearned / mquake / 300 / [100, 300] | 10 | 1345.548 | 2085.129 | measured_completed_cell_process_envelopes |
| v0_stable / zsre / 1000 / [100, 300, 1000] | 10 | 4728.381 | 7258.931 | measured_completed_cell_process_envelopes |
| v0_stable / counterfact / 1000 / [100, 300, 1000] | 10 | 9712.065 | 14746.743 | measured_completed_cell_process_envelopes |
| v0_stable / mquake / 300 / [100, 300] | 10 | 2906.262 | 4493.283 | measured_completed_cell_process_envelopes |
| matched_update / zsre / 1000 / [100, 300, 1000] | 0 | 4040.779 | 6061.168 | retained_plan_v3_estimate |
| matched_update / counterfact / 1000 / [100, 300, 1000] | 0 | 6812.210 | 10218.315 | retained_plan_v3_estimate |
| v0_live_C1 / zsre / 1000 / [100, 300, 1000] | 0 | 4092.399 | 6138.598 | retained_plan_v3_estimate |
| v0_live_C1 / counterfact / 1000 / [100, 300, 1000] | 0 | 6792.009 | 10188.014 | retained_plan_v3_estimate |
| v0_live_C2 / zsre / 1000 / [100, 300, 1000] | 0 | 3969.717 | 5954.576 | retained_plan_v3_estimate |
| v0_live_C2 / counterfact / 1000 / [100, 300, 1000] | 0 | 6766.893 | 10150.340 | retained_plan_v3_estimate |
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

R1 block 2 — 2026-09-20T21:15:10.570552+00:00
Scope: confirmatory; matrix SHA256 06fa8b3b3f3d734c12d47ac2b1b09d8dcd0c35c203013456c9409590329d56bb.
Artifact-complete cells: 90/330; complete blocks: [1, 2].
Known spend: 93.913283 process-hours; projected total: 593.038419; declared ceiling: 750.000000.
Projection uses the entire matrix, remaining solo ceilings × 1.15; retry-exhausted incomplete cells are not reserved again. It is not an elapsed-time forecast or a guarantee of full completion.
Cost ledger: Process envelopes replace covered driver attempts; overlap and failures charged once each. Uncovered legacy driver times exclude process startup. JAX timers are not added.
Incomplete cells:
- 0417f598d89548e3200a3fe4: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 12a9c0da62781d521da26cd5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c2a67190edb39398491bd651: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 58cc3599099d7ab60e5d1413: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4206e18c23b43bb312e045e6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- fa46e16c8436f7ea4a5c3f06: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 162686f6303fe986619d236d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 029ecd260f3e085063714d3f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7197775fb7f97a465fd3310e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6de7e97b6cb167d048dc31ba: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- fcd702d12d5d6bfae824379b: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 9a1d038b95f534b43185c7fc: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- dfc9c9b480e482911c457e07: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 34fce88c919bcae6410e4d94: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 7a39ae192fb0b1038c651f64: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 13465e8d0dc3824fced8e891: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 24840672cf1682dd450fdcd2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 12a6e3e550a7939c6d79349d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- fa5b51891eb78dc707e6471f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 861810fbdd6ebe7502383382: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6ed2474713b3a311b4ec6b08: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f939f211b98675ac7c2d951f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 19b5e9b462930c6f50f2e2f6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b14576e3d752f467db2abf18: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- da9f71bdb9a8981dac078e6c: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9e98169ae668b50d60694317: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- ff570734d7837a1ba9e77528: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 4fd2bc51397502cb1c085b5c: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- c0e77c94b06dd3464838be93: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 4c700c665ce70ca41e4569dd: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- dc17fc3637068157dba0207d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 727b32ab9723cb9feba71636: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a02980b0886a222f8e2f58e8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9aeb330f6c7e29c85ee56da0: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0e0ee9a35e1116f7dafb423d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 862cd40c359e48e5a7998e3f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 89b258fddde381d9a09429d9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 090d1237381f4ee02fcbd05d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6e95ec72097ffded952889d6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c8ce51b334cc3e42a623be6c: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- cf6bd4a623aa24871f74d136: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 519b30353f979e8028ed03e1: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 89182e81a187807d2772cade: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 9ad3399cfc13f1297d17423d: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- 046aa51d028b84dde8981351: missing checkpoints [100, 300]; failures 0/2; exhausted=False
- c897cd3d2a3b35bfe999e87e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 1689630f5ad581d9fcfc483e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c1c03ed850a40df57da8628a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d1690029ea53ae03b3705536: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a921f9ab5443f978e56d2390: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a86da75220343c5560c45373: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e7b52c6db370d10a5fd7d891: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 735081421354eaafb893322d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 824f602358ace0fc5cb69271: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 3bc2cef1ca9bab6e4a90e222: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9c3c7c258bf086523ea6268e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 58879f9745ed479686bd0481: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b6ea6d9e337e3bf6f2eca5d2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 16037ce355e4a2e9a43a2008: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4597af8473d8e404f1490c57: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7c933afa6e2adc84ccb287be: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0998eeed741b887bdb8664af: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- bb4da95ca8ce5b0b8d3dbe35: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c5f1daa35261cf950172dfa8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 244f29ba9b89c48d08c257c7: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b8924c056fee6d000f5492d1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4944219da107f9ed1daccef5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ac46789a7ebda9982aebd343: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ccf4e4f1fca14a048eecd38f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6c9ac68dd90eb2d39d339b6a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 672b5b4a7ea9b83b8668fbe2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b8f1ca491f4e29db862af920: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 5efb497774b3f4f9ad8e7f7d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 47ee96bcecb134f64286c958: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a18ee644e09c84652cc9582a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 509cd28130eb44d35b27d08a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a8a5ddc06de26a9885f75fe9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 5f818373c34233809fc57716: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- baa8eccee6a4f8c27c11a09c: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 2a91e17773f7272dbd36a048: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d0a5df19a69792ac87a703dc: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6d6930dcd4fe737e4d1ef3ed: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- cf9c6af6097c6d96c9a5a1d3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7317081e2468dfeeed3e4cc7: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ed2fff6199cac50f8e3c05d9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 5d52bba4bd205ffecf96212a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e82412060e54893dc307a45e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b42dfb1e539cb4645127e844: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 2fe9909dbaad17941716efc9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e45d4b2c01fc48117d5abec8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 978f353680dde68625399775: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- cdc8a1fbbb43d1f1ba93a366: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 3126d7f4d6378f131a26c41d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 48f56fbee8eed89fe5598934: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 18cef3e100afe2f32847ac27: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f67e77a0b124376f29b78302: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7ab5a2ba2ca2072d49c86da9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ea3b0653f085cf535854d1b8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 8905e452833b0a01defd8b1e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 28555ca1e3c1d3ab551385b1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 861414ea84239f8471f0ade8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 1f19207d799d9bcd0b005ef9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- ad007b170a6bbf5bc88d182d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 94488c6aa407c3ea167ea51d: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e6a5e4cd9fbe73077175c7b9: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- bca38cd4398e1159ed781bff: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 68da09e4a00f4fe8d8b054fd: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- da666451073f38000c71b39f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 57b0ace8ad261f0963cece6e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b1be521b209066effb830ad1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d246da52d2783b0000af34aa: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9ac1596b4a83bfd3759110f5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d3e7acfb899406015f6d7e6a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 1b91b6d6beb187aaf9103cdc: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9a600f5f46fa47c339ccb4d1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 635bac1c845730dae487891a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 031ae1822109079d3cddb520: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 3435ab1a884c517b32867161: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 09d4451a2a5b030d1853c267: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- fa309fa719c353f20a813699: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 03ee79b7cf8d02ddb7baeea3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 37aa09141ddb4b6e8f93f647: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c14b2b630688912a588e1cf3: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 2eda7453d476d16c07a327ed: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9a29639c43e873eec6a7d1ac: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0362b36136a70031c319de5f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9397f85898818d3dc9d04c1e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 4c1b2ab65e6ba3e75ac9b10a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d679f4cef5e7a847d5f6dc80: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f19cc29f17b93bb9cbbd5f1a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e654a69635e2e4a1bcc2903b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 508b709256adff820b7fdf82: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0ebaffd3a3e8d10252da8bd5: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6f8cac15c1ed9dd1fb79b212: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 302070707affaaec2265e772: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 74feefbadad2b95947437ed6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 982870b0fcc4a8bef4a297af: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 2e5068d168160234340d32fa: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f642d1e953d4e4b42c9a916e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d7884b1e2a9c1c3790535590: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 8499903e83df71431114aaa8: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 272db4c9310a73f01bf46d4b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9f020616201afdc368d77f9b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 26318156d310334e8b260e87: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d7241b9882514c2709082321: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- a5b3de3764680273ff4760e1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e5c2ea10bc6ce298f6065199: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 847f33277d9d89fe17482367: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 77568a85e217721985cd8ea4: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 793ee3d9708b970c08a0fbe2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 129251f55876e9cdc9e907a6: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 40059b37d028ec2cd587bbb1: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 30756d73095e1914cf757782: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- d74e8582f780dfdeb9281671: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 88dfe1aa76490ae40e93f05f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 9adac77b91eae4f8ea4d8df2: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- bbbda4ebfb279ed21179678b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 34f5fb1acf8d86a8a7a94e1c: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- c9dc2d0cfe6d53ccdef2f1ef: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 22b85c86caaee83341968cec: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 1a27fc67e8978362681b5d20: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- f9ebb0802bd50e68ec18fcb0: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- be9a4b3ce1acb50722ae8614: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 5c5511653f8d590c63a39794: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7cbec59a4f05afaa8ebed3fb: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b1a17c1fb747eef11f253278: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- edb61534cb4ec7a4187ebbdb: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 78360f37e3cd5a3eb5cc2b3e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 46d6404412a25fbdd2965880: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 50af2a28b866c26021d83b01: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 22a5ac50d5ca3c952b8b1e34: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 7d93e4d997ec1f974bb6c71a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 0f466b21fb4514acd9d1ff1e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 151bacf1f85b74f88864784e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 330479ee3f94e169b8496e0b: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- e4019672011694d495923c6f: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- bf89e6ad180b60ad56c35a7e: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 70aacd394ef41b887377260a: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- b3f4ad21a596171a9a43e0aa: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
- 6885c03ed3db8fb41a5e20dd: missing checkpoints [100, 300, 1000]; failures 0/2; exhausted=False
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
Watch since previous posted snapshot: 94 global observations (90 in this matrix), 61 breach entries, 11 creep alerts.
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
Checks: no snapshot/accounting/watch gaps detected
Boundary ready: True; unprocessed cells through boundary: []; accounting/watch gap cells through boundary: [].
Known process-hours through this boundary: 93.913283. Later active blocks can leave the whole-matrix spend/projection incomplete without reopening this boundary.
Artifact completeness does not assert benchmark success, effect significance, admission or launch authority.
This text has not been posted; creep alerts require immediate owner relay, not a wait for the next boundary.
Report digest: 19d092338c1cf4a6e08fc7e2f7a44ccef7e567e15f514dce7bfb40be95ae71b5

This text has not been posted to the lead queue. Cost proposals are not signatures.
Plan digest: 751e6af190037b745c10d12da38920ae44f7f8bfd76f9af4c1074c31efec2a91
