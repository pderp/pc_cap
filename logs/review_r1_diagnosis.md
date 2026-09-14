# R1-X1 — counter-review of the Stage 0 diagnosis

The saved results support stable observations and better record selection as promising interventions. They do **not** establish that storage is universally exonerated, that the entire residual is learnable by the proposed reader, or that shadow-key locality is preserved. Keep DEC-035's non-learned stable control. Use the subsequently measured **0.44 in-stream paraphrase retention** as the development comparator; the 0.67/0.49 shadow-key results describe a different intervention.

This review is read-only. It uses the coding-agent guide, pp. 2–4, plan 9, DEC-034/035, `docs/R1_diagnosis.md`, the final Stage 0 diagnostics, and both later control reports. It does not rerun a model or touch the GPU. The earlier `results/R1/prereview/` pass remains superseded. Source hashes and full recounts are in [r1_x1_recount.json](r1_round2/r1_x1_recount.json); the reproducible reader is [r1_x1_review.py](../scripts/r1_x1_review.py).

## Verified results

All 400 saved prompt/paraphrase rows, all D1 accuracy/loss aggregates, and D0 edited-query ownership counts reproduce. Both endpoint checkpoint content hashes match the diagnostic state hashes. The by-purpose cost sums equal the independently subtracted ledger totals exactly at stored precision: C1 **14.7059133995 s**, C2 **9.76530709176 s**.

| Policy | C1 prompt / paraphrase exact | C2 prompt / paraphrase exact | Meaning |
| --- | ---: | ---: | --- |
| Live | .92 / .24 | .79 / .29 | Original sequential edited read |
| Verified oracle | .93 / .94 | .92 / .94 | Gold edit identity and prefix-specific slot supplied by evaluator |
| Stable query only | .35 / .11 | .62 / .29 | Unedited query keys against historical edited-pass keys |
| Stable query + shadow keys | 1.00 / .67 | .98 / .49 | Unedited query keys against reconstructed unedited keys; original values/radii |
| Later in-stream v0-stable | .99 / .44 | .97 / .44 | A new learning stream using stable keys throughout |

These are 100-item development results from one stream/order. Recounting saved `exact` fields is an audit of aggregation, not an independent recomputation of their logits.

## Findings and dispositions

**X1-01 — Oracle verification passes for these artifacts; strengthen its general contract.** `scripts/r1_diagnostics.py:101` checks the exact historical prefix claim, current activity/owner, and target token. It does not fall back to prefix zero. Independently rebuilding the chronological last accepted write for every slot confirms **zero prefix-identity mismatches** among the current verified entries, in either arm. C1 reproduces 1,094 claimed / 1,080 verified / 14 reused-or-inactive / 112 missing; C2 reproduces 374 / 374 / 0 / 832. Counts are bank × prefix entries, once per item; prompt and paraphrase traces repeat the same verification.

Owner plus token is not a general proof of prefix identity: the same owner can present the same token at different positions. Current metadata has no prefix digest. Before reusing this diagnostic on new streams, explicitly compare with the chronological last accepted `(item_digest, prefix_index)` or persist a prefix identity. Add a same-owner, same-token, different-prefix fixture. This is a prospective safeguard, **not evidence that the reported oracle accuracy is inflated**.

**X1-02 — Shadow reconstruction is reproducible, but C1 is slightly hybrid.** The implementation's prefix lookup iterates historical claims; it does not explicitly choose the last accepted write by time. The independent chronological check finds **no incorrect selections and no multiple candidate prefixes** here. C1 rebuilds 362 / 356 / 362 slots, but **five site-2 slots keep their stored keys** because no current-owner claim can reconstruct them. C2 rebuilds all 6 / 4 / 364 active slots. Describe C1 as a near-complete rebuild, or add a separately named variant that drops unverifiable slots and reports the affected answers. Do not silently replace the original result.

The rebuilt arrays are shadow copies, values and radii remain fixed, and retrieval uses the same distance/radius/tie rule. This is a useful paired endpoint intervention. It does not reproduce learning with stable keys, which also changes collisions, radius shrinkage, and accepted updates.

**X1-03 — Complete teacher-forced argmax exactness is meaningful, with a narrower endpoint definition.** For a deterministic causal policy with fixed state, “every next-token argmax equals the canonical answer token” is equivalent, by induction, to greedily producing that same finite canonical token sequence. This is stronger than a first-token oracle score. It does not measure alias-aware string exactness, a different stopping rule, or losses along off-target generated trajectories. NLL is explicitly teacher-forced. For the oracle, the policy additionally depends on unavailable edit identity and a gold-verified per-position slot map; it remains a diagnostic upper comparator, not deployed efficacy. A free-generation assay is still needed for the report endpoint in the guide.

The field `tf_nll_token_mean` averages each answer's token mean, giving each item equal weight; it is **not** pooled total NLL divided by all target tokens. The recount supplies both denominators. Rename or footnote this field in future reporting.

**X1-04 — Observation/selection locus is supported; “storage exonerated” is too strong.** Forcing surviving appropriate entries raises paraphrase exactness to 94%, and matching key/query observation spaces raises exactness substantially without changing values. That is good evidence that retrieval is a major limitation in this short, low-pressure stream. The remaining oracle failures, reused entries, long-stream eviction, revised facts, and two-fact composition are not explained away. “Storage is adequate for most tested paraphrases when the surviving entries are supplied” is defensible. “Storage is not a bottleneck in general” is not.

Stable queries **alone worsen C1** (.24→.11). The successful intervention matches both sides of the geometry. The .67→.94 / .49→.94 residual is a target for experiments, not an established attainable ceiling for a label-free learned reader. The oracle forces potentially different prefix entries at different sites; the new architecture holds one logical fact code. Holding a single old v0 prefix slot is not equivalent to implementing that new representation.

**X1-05 — Locality evidence belongs to the policy that was measured.** The 200 unrelated prompts were run only through the **live** policy; no per-query unrelated traces were saved, and stable/shadow unrelated firings or answer preservation were not evaluated. Therefore zero live firings cannot establish zero shadow-key firings. Cross-item firings on edited queries can already be costly even if unrelated prompts are untouched. In C1 shadow paraphrases, own site-3 retrieval gives 67 exact answers among 71, other-owner gives 0/22, and none gives 0/7. In C2, those counts are 48/51, **1/28**, and 0/21. The memo's “22–27% other” range should be 22–28% for this definition.

The later in-stream v0-stable/matched-update reports separately measure LS 1.00 and zero unrelated firings. That supplies evidence for those conditions on this sample, not for the original shadow intervention. The Stage 0 LS evaluator uses 50 unrelated prompts; its complete-answer LS and the 200-prompt firing audit are distinct denominators.

**X1-06 — Loss and exactness do not improve uniformly.** C1 paraphrase mean answer NLL improves 7.642→4.369 with shadow keys. C2 instead changes **8.122→8.328**, despite exactness improving .29→.49. Thus “NLL moves the same way” must be restricted to the cited C1 example. Inspect C2's unsuccessful items and high-loss tail before declaring the stable geometry uniformly better. Likewise, recalibrating radii *might* help, but the unretuned result is not a demonstrated lower bound on a separately calibrated result.

**X1-07 — Capacity and rebuild units need correction.** Each bank has **2,048 slots**, 6,144 in aggregate. C1 occupancy is 362 / 361 / 362, far below capacity, not “362 of 6,144 per bank.” C1's rebuild comprises **1,080 slot keys from 367 unique prefix passes**; C2's 374 keys use 365 unique prefix passes. The approximately 0.5-second rebuild costs describe these workloads, not generically “362 slots.” The recount verifies the costs, but these short cached workloads are not a scale-independent estimate for future encoder rebuilds.

**X1-08 — Keep DEC-035; qualify the mechanism and gate.** DEC-035 correctly adds a strong low-cost explanation that must be controlled. Its rationale should identify .67/.49 as the *post-hoc shadow* assay and .44 as the *in-stream* result. The reduction from shadow to in-stream performance is consistent with changed collision/radius history; the existing comparison does not isolate that explanation. The matched-update result (.99 RET-ES, .44 RET-GS, LS 1.00) shows no gain from that tested value-update variant on this stream; it does not eliminate all fast-update rules as a source of improvement.

Stage 0 provides enough evidence to motivate implementation. Its gate should not be read as passing the later learned-cap, memory, data, or training-objective gates. In particular, the independent [R1-23 audit](audit_r1_23.md) identifies repairs and incomplete training conditions that remain before scientific comparisons can support the full plan-9 claims.

## What would change the diagnosis

1. **CPU now:** freeze prefix-identity semantics and add the same-owner repeated-token fixture; distinguish shadow/in-stream policies, canonical/alias-aware exactness, loss denominators, and locality populations in reporting.
2. **Next bounded GPU diagnostic:** rerun all four policies on the same complete near-miss/unrelated query set, persist every trace, and measure both answer preservation and firings. Compare excluding the five unreconstructable C1 slots as a named sensitivity check.
3. **Matched development comparison:** run live, in-stream stable, matched-update, and learned-reader conditions on the same items, seeds and orders. Separate oracle selection of new fact codes from v0 prefix-slot forcing. Include support-answer swaps and controlled revisions to establish that new information is actually learned from support.
4. **Pressure and failure controls:** increase stream length under a real total-byte ceiling; distinguish missing/evicted records from wrong selection and ineffective retrieved codes. A falling verified-oracle score with capacity pressure would restore storage/retention as a central explanation.
5. **Decision:** if stable geometry explains the gain and the learned reader adds none, prefer that simpler measured control. If selection improves but edited answers do not, investigate the fact code/controller. If acquisition improves but old facts fail, prioritize collisions, revisions and replay. Additional solver complexity waits for these distinctions.

Reproduce the CPU audit with a new output path:

```bash
PYTHONDONTWRITEBYTECODE=1 /home/derp/cap/venv/bin/python scripts/r1_x1_review.py --output logs/r1_round2/r1_x1_recount_rerun.json
```

No existing memo, decision, source file, checkpoint or result was changed by this review.
