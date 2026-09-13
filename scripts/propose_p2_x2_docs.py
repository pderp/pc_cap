"""Prepare reviewable documentation corrections without editing their targets."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = ["docs/D3_decision.md", "docs/report.md", "docs/REPRODUCE.md"]
    old = {p: (ROOT / p).read_text() for p in names}
    new = dict(old)

    def change(path, before, after):
        assert new[path].count(before) == 1, (path, before[:100], new[path].count(before))
        new[path] = new[path].replace(before, after)

    def section(path, heading, next_heading, body):
        start = new[path].index(heading)
        stop = new[path].index(next_heading, start)
        new[path] = new[path][:start] + body.rstrip() + "\n\n" + new[path][stop:]

    memo, report, reproduce = names
    change(memo, "(42%); S5 8.89 h of 18.0 (49%). Largest run 1,060 s", "(42.6%); S5 8.89 h of 18.0 (49.4%). Largest run 1,067.24 s")
    change(memo, "No run-affecting module changed.", "After execution, commit `b530baf` also added default-preserving ablation parameters to `cap/{cap,memory,calibrate}.py`. Those changes are not covered by the existing full-source version record; the current tree is `9b1d9984c3d4…`. All 270 saved run configurations still match the frozen execution tree.")
    change(memo, "post-execution changes are confined to `src/pccap/analysis/`", "the initially recorded post-execution changes were in `src/pccap/analysis/`")
    change(memo, "SD-22: paraphrase seeds were salted per process, so 0–3 items per cell (of 2,048) have an undefined RET-GS and the paraphrase sequences differ between runs. No arm is favoured; the frozen policy classifies the grammar `incomplete`; a labelled complete-pair supplement is reported.",
           "SD-22: paraphrase seeds were salted per process; 0–5 items per run (of 2,048) have undefined RET-GS, and paraphrases differ between runs. The salt has no deliberate arm dependence, but realized bias is not ruled out. The frozen classification stays `incomplete`. The labelled supplement excludes the union across 20 arm/order cells: 28/22/41 items, retaining 2,020/2,026/2,007 in realizations 0/1/2; it is not confirmatory.")
    change(memo, "no (−0.019) / yes", "no (−0.019) / not established (−0.007)")
    change(memo, "C2 retains paraphrase generalization about three points *worse* than C1 in every realization and is indistinguishable from\nrandom routing.",
           "C2's mean RET-GS is about three percentage points lower than C1; the order-averaged difference is negative in all three realizations. The C2−CR interval includes zero; this does not establish equivalence. Locality non-inferiority is not established against CR: Δ LS −0.007 [−0.026, +0.013], lower bound below −0.01.")
    change(memo, "so the primary endpoint sits at a floor there (0.000 and 0.286 respectively) and cannot discriminate.",
           "so the observed cap-arm primary endpoint is 0.000 on CounterFact and approximately 0.286 on the grammar. This is a retrieval-generalization limitation, not evidence that every possible cap or key variant must fail. Grammar arm means are not exactly identical under SD-22.")
    section(memo, "Readings. (i)", "## 4.", """Readings (descriptive). (i) zsRE RET-ES is 0.524 for C1, 0.302 for C2 and 0.344 for CR at 1,000 edits. C0's 0.992 is at only 300 edits and is not a matched endpoint comparison. These means do not identify the cause of forgetting. The accepted-event logs contain fewer eviction events for C2 (mean 1,085) than C1 (2,801); event counts are not counts of uniquely forgotten edits. (ii) On the grammar, C2 and C0 have RET-ES 1.000, CR 0.895 and C1 0.690, consistent with the development pattern. Their RET-GS means all round to 0.286, with different sampled paraphrases and missing outcomes (SD-22). (iii) B3 acquires about a fifth of the editing targets and has poor locality (zsRE LS 0.009; CounterFact 0.00033), with drift ratios 1.75 and 6.47 on the tested slice. (iv) Editing drift evaluates only 4,064 positions, not the entire 247,289-token validation split required by SD-3. zsRE cap-arm mean ratios are near one, but C2 reaches 1.00929 in an individual run; a rounded mean is not proof of no drift. Grammar drift is a separate 4,032-position base-grammar assay. See `logs/review_report_draft1.md` and the prior drift remediation note.
""")
    section(memo, "C2's update time", "## 5.", """C2's update time is the reference. Across the 15 cells per dataset, mean C1/C2 ratios are 2.788 (zsRE), 2.720 (CounterFact) and 1.988 (grammar). C0/C2 is 0.698/0.737/0.513; CR/C2 is 0.682/0.726/0.693. B3/C2 is 0.697 on zsRE and 1.296 on CounterFact. No *comparator* lies within 20% of C2 in any cell; C2 itself is the reference at 1.0. Thus no joint comparable-compute superiority claim is established.

The resource views provide exposure-matched checkpoint outcomes and ES-versus-time tables; they do not establish a paired RET-GS superiority result at equal cost. Losing at equal exposure while using less compute does not logically rule out a different tradeoff at equal time. Report the measured tradeoff without claiming that resource matching cannot change it.
""")
    change(memo, "no practical difference: the regenerated ePC base reproduces the BP result (matched fidelity, S1-01)", "RET-GS differs by −0.002; locality non-inferiority is not established (Δ LS −0.0213 [−0.041, +0.004]); not an equivalence result")
    change(memo, "real but sub-margin retention gain on the edits it holds; acquires a third fewer edits within the frozen round budget", "RET-GS point gain is below 0.02, but its interval extends above it; ES falls 0.336, making the contrast negative. RET-GS is not conditional on acquired edits")
    change(memo, "CounterFact: identically zero on every measure (floor). Both contrasts classify negative by policy.", "CounterFact: both paired differences are zero for RET-GS, ES and LS; absolute ES and LS are 1.0 while RET-GS is 0.0. Both substrate contrasts classify negative by policy.")
    change(memo, "eviction reading on zsRE as descriptive findings", "retention difference on zsRE as descriptive findings without a proven eviction mechanism")
    change(memo, "**S8-02 ablation list** (fixed before its runs; three realizations × two orders, exploratory):", "**S8-02 ablation list** (fixed before its runs, after the confirmatory results; three seeds × two orders, exploratory):")
    change(memo, "Budget ≈ 3 accelerator h; S8 ceiling 16.", "Planned budget ≈ 3 accelerator h; S8 ceiling 16. Completed (b)/(c) contain 72 runs with 0.8255 recorded accelerator h; (a) was not run. The grammar 5% test was not in the S4-frozen exploratory list, and difficulty weighting was omitted. The byte-ceiling runs contain 280, not 300, available development edits; the grammar test found no positive candidate on its tested calibration grid. See report §8.")
    change(memo, "**S7** runs on the committed checkpoints now", "**S7** completed on four committed checkpoints")
    change(memo, "RET-GS std across orders ≤ 0.023", "RET-GS std across orders ≤ 0.028 (observed maximum 0.0277543)")

    change(report, "Sections marked *pending* are filled when the S8-02 ablations finish and the final-tree reproduction audit runs.", "P2's final-tree CPU reproduction audit and X2's counter-review are in `logs/reproduce_final.md` and `logs/review_report_draft1.md`. These reviews do not constitute the lead's T4 / CP-F approval.")
    change(report, "**It does not.**", "**The primary claim is not supported by the completed contrasts; grammar remains incomplete.**")
    change(report, "and is indistinguishable from random routing (+0.000\n[−0.013, +0.018]).", "and its difference from random routing has an interval spanning zero (+0.000\n[−0.013, +0.018]); equivalence is not established.")
    change(report, "The matched-fidelity substrate comparison shows that converting the base to the regenerated ePC checkpoint changes\nnothing under the adjoint credit (SE-A ≈ SB within 0.002), and that the settled-error credit trades a third of acquisition for\na two-point retention gain below the margin.", "Under adjoint credit, SE-A's RET-GS is 0.002 below SB, but locality non-inferiority is not established; this is not a general equivalence result. Settled-error credit reduces acquisition by 0.336 for a RET-GS point gain of 0.0189, whose interval spans the 0.02 margin; the contrast is negative because acquisition fails.")
    change(report, "Order effects are real where keys retrieve (zsRE near-neighbour pairs damage\neach other by 2.4 nats on average) and absent where they do not.", "On the tested S7 checkpoints, zsRE near-neighbour update directions cause 2.4 nats mean damage; CounterFact and grammar show zero damage on the evaluated prefixes, while all complete endpoint states differ between orders.")
    change(report, "No threshold, endpoint, arm, contrast or budget was changed after the freeze; every deviation is listed in §9.", "The saved confirmatory configurations retain the frozen thresholds, endpoints, arms, contrasts and allowances. Post-confirmatory ablations and source changes are disclosed separately in §8–§9.")
    change(report, "with 33 metric and 10 process controls (`docs/controls.md`, S3-01).", "with known-answer metric tests and process controls PC-1…PC-10 (`docs/controls.md`, S3-01); PC-10 remains unqualified. The historical count of 33 refers to the original known-answer test run, not 33 distinct process controls.")
    change(report, "mean KL 2.9e-5 nats/token on H,\n  rule ≤ 1e-3). Substrate properties P2/P3/P5/P6 on the ePC weights equal the BP rows to three decimals; P6 labels the", "mean KL 2.9231e-5 nats/token over 1,999,872 scored H positions, archived at `git show 25c988b:results/S1/P1_epc.json`;\n  rule ≤ 1e-3). The current P1 filename is a 199,680-position follow-up (2.8746e-5). P2/P3/P5/P6 are broadly similar but do not equal the BP rows to three decimals; for example P5 bank-1 target reach is 0.950 BP versus 0.945 ePC. P6 labels the")
    change(report, "(42% of the S4 ceiling after headroom)", "(42.6% of the S4 ceiling after headroom)")
    change(report, "and every finding repaired with a control.", "with controls for the execution defects identified in those rounds. The drift-coverage limitation and later reporting findings remain disclosed below.")
    change(report, "| no / yes | negative |", "| no / not established | negative |")
    section(report, "Readings (descriptive, D3 §3):", "## 6.", """Readings (descriptive, D3 §3): at 1,000 zsRE edits, C1 retains ES 0.524, C2 0.302 and CR 0.344. C0's 0.992 uses a shorter 300-edit stream. These endpoint means do not identify eviction as the cause: accepted-event logs contain mean eviction counts 2,801 for C1 and 1,085 for C2, and counts of slot events do not identify forgotten edits. On the grammar, the RET-ES routing pattern matches development, while the RET-GS means all round to 0.286 under differing paraphrases (SD-22).

B3 has poor locality, and its editing drift ratios are 1.75/6.47. The editing drift assay covers only 4,064 scored positions from 4,096 tokens, not the full 247,289-token validation split required by SD-3. Near-one cap means do not establish zero drift; zsRE C2's maximum per-run ratio is 1.00929. The grammar ratio uses a separate 4,032-position base-grammar assay. A versioned full-validation remedy remains unresolved.

C2−CR locality non-inferiority is not established: Δ LS −0.007 [−0.026, +0.013], versus the −0.01 margin. The primary classifications are unchanged. Comparable-compute ratios are tabulated in D3 §4: no comparator lies within 20% of C2. Lower update cost plus worse equal-exposure retention does not rule out a different equal-time tradeoff; the current resource views do not establish paired RET-GS superiority at equal cost. Order variation across the five committed orders (S7-03): maximum RET-GS standard deviation is 0.0277543 on zsRE, 0 on CounterFact and 0.00440532 on the grammar.
""")
    section(report, "SB (= the S4 C1 runs)", "## 7.", """SB reuses the S4 C1 runs; SE-A uses the regenerated ePC base with adjoint credit, and SE-E uses that base with eight-iteration finite-error credit. The 60 S5 confirmatory runs consume 8.88985 recorded accelerator hours. On zsRE, SE-A−SB RET-GS is −0.0020 [−0.0040, −0.0002], ES +0.000067, and LS −0.02133 [−0.041, +0.004]. Acquisition non-inferiority passes; locality non-inferiority is not established. A small RET-GS difference is not a general equivalence result.

SE-E−SE-A RET-GS is +0.01887 [+0.0120, +0.0248]: the point is below the 0.02 margin, but the interval extends above it. ES is −0.3362 [−0.344, −0.324], so the frozen negative classification is driven by lost acquisition. RET-GS is measured over the endpoint inventory, not only acquired edits. CounterFact's paired differences are zero on RET-GS/ES/LS; absolute RET-GS is zero and ES/LS are one. Both substrate contrasts remain negative by the frozen rule.
""")
    section(report, "100 fixed pairs (CounterFact 75", "## 8.", """The fixed inventory supplies 100 pairs per checkpoint, or 75 for CounterFact (DEC-023), stratified shared/private/near-neighbour and separate from the confirmatory streams. Each reversal starts from a clone of the same complete state. At zsRE C2's 300-edit checkpoint, mean damage over both update directions is +2.41365 nats for near-neighbours, +0.69152 shared and +0.15958 private; mean D_ij is 0.03962/0.04063/0.00350, respectively.

The reported harmful fractions use **ordered directions**, not pairs: 22/66 (33.3%), 11/68 (16.2%) and 2/66 (3.0%). Counting pairs harmed in either direction gives 16/33, 9/34 and 2/33 instead. CounterFact endpoint and grammar checkpoints at 1,000 and 2,048 sequences have zero damage and JS divergence on their evaluated Q sets. Complete endpoint states differ in all 375 pairs across the four checkpoints, so these results do not establish commuting updates. Natural-language strata are operational proxies (`manifests/dev/s7_pairs.json`), not established latent mechanisms.
""")
    change(report, "(zsRE, 300 development edits, C1 and C2)", "(zsRE, 280 available development edits per run, C1 and C2; 300 requested)")
    change(report, "at 300 edits the ceiling", "at the 280 completed edits the ceiling")
    change(report, "so the loss is interference among\nretrievals within the three banks, not eviction. A binding-ceiling ablation would need factors ≤ 0.25 or a larger\ndevelopment pool; it was not added post hoc.", "so ceiling pressure is not necessary for this development gap. The exact mechanism and its contribution at 1,000 confirmatory edits remain unresolved. Smaller ceilings or a larger development pool would be needed for an informative capacity intervention; it was not added post hoc.")
    change(report, "finds no positive radius either", "finds no admissible positive radius among its tested grid candidates")
    change(report, "The grammar's RET-GS floor is therefore a property of the R-h key on this base — \"same latent, different filler\" is not a\nneighbourhood in key space — not of the 1% criterion. The runs at \"5% radius\" are consequently identical to exact keys.", "This grid search does not lift the grammar's RET-GS limitation when its criterion is relaxed from 1% to 5%. It does not prove that every smaller positive radius, key definition or calibration procedure is ineffective. The zero-radius runs agree with the exact-key comparator in the reported metrics.")
    change(report, "**(a) Stable keys versus edited keys:** not run (needs the optional read variant R-h0, CAP-08).", "**(a) Stable keys versus edited keys:** not run (needs the optional read variant R-h0, CAP-08). The D3 list was fixed before ablation execution but after confirmation; the grammar 5% test was not in the S4-frozen exploratory list, which also included difficulty weighting. These 72 development runs are explicitly post-confirmatory exploration, not a completion of every frozen optional ablation.")
    change(report, "0–3 undefined RET-GS per cell", "0–5 undefined RET-GS per run; supplement excludes 28/22/41 items across the 20 cells of each realization")
    change(report, "| Post-freeze source changes | analysis tree only (grammar expected inventory; S7 runner), versioned | DEC-028 |", "| Post-freeze source changes | analysis tree v2 is recorded; later default-preserving ablation knobs also changed `cap/{cap,memory,calibrate}.py` in `b530baf`. Current full tree `9b1d9984c3d4…` needs an updated provenance record; the 270 run configurations still bind the original frozen tree | DEC-028; X2 |\n| Drift coverage | Editing assay scores 4,064 positions instead of all available validation tokens required by SD-3; full-validation evaluation remains unresolved | `logs/ongoing_followup_20260911/drift_remediation.md`; X2 |\n| Exploratory list | Grammar 5% radius added after confirmation; difficulty weighting omitted; byte-ceiling runs have 280 available edits | S4 frozen list; S8-02; X2 |")
    section(report, "S0 0.41 ·", "## 11.", """The PDF Appendix B allocates **154 A100-equivalent hours**, not 144. With provisional κ = 1, the current cost-file/task-ledger sum is S0 0.412 · S1 0.181 · S2 0.845 · S3 0.062 · S4 11.492 · S5 8.937 · S6 (REG) 12.316 · S7 0 · S8 0.825 = 35.069 local ledger hours. S5 includes 8.88985 confirmatory hours plus development records; SB is reused from S4 and not charged twice. S7's four embedded reversal ledgers add 0.041715 h, giving **35.111 recorded local hours** for these sources. The budget collector misses those S7 ledgers because no `cost.json` files accompany them.

This is a source-reconciled recorded-cost subtotal, not a certified full physical GPU occupancy or A100 measurement. The cached `results/ledger/stages.json` is stale; some stage measurements keep embedded ledgers, and task estimates may overlap run records. κ remains unmeasured against an A100 (band 0.5–2), and `accel_seconds` measures synchronized call wall time. S4 and S5 confirmation consumed 11.49181/27 and 8.88985/18 h of their enforced allowances; the largest run was 1,067.24 s of 2,400. A final non-duplicated all-cost reconciliation remains for the owner before asserting a complete project spend or universal ceiling compliance.
""")
    change(report, "(audited on the CPU by Lane P; final-tree audit pending, S8-01)", "(final-tree CPU audit completed by P2; `logs/reproduce_final.md`, with a fresh-checkout S5 dry-run workaround and expected code-drift refusal; GPU reproduction not rerun)")

    change(reproduce, "## 1. Environment and assets", """For a fresh shell or isolated source copy, set:

```bash
P=/home/derp/cap/assets/envs/venv-check-plan6-df/bin/python
export PCCAP_HDPC_PATH=/home/derp/cap/llm-by-neural-predictive-coding
```

P2 verified the CPU commands on source snapshot `170fad3`; results are in `logs/reproduce_final.md`.
Regeneration commands write their destinations and belong in a fresh isolated copy during an audit.
Keep resources outside the repo, and preserve the `../assets` relationship or use explicit absolute paths.
Set `make PY="$P" test-fast` to actually use the chosen recreated environment. For CPU-only checks,
set `JAX_PLATFORMS=cpu` and `CUDA_VISIBLE_DEVICES=` before each fresh shell.

## 1. Environment and assets""")
    change(reproduce, "make test-fast                                                   # [verified] CPU tests, ~1 min", 'make PY="$P" test-fast                                           # [verified] P2: 360 passed, 5 skipped, 52 deselected')
    change(reproduce, "# PC-1…PC-9 on the real base (GPU short)", "# GPU-marked PC-2/3/8/9; combined coverage is in docs/controls.md (GPU short)")
    change(reproduce, "# [pending] P1 (lease)", "# P1 GPU rerun; full H record at git 25c988b (lease)")
    change(reproduce, "$P -m pccap.cli queue [--stage S5] [--max-jobs N] [--dry-run]   # S4-04: runs the list in order, one subprocess per job under the lease; resumable; stops on refusals and systematic failures; stop file results/S4/queue.stop", """$P -m pccap.cli queue --dry-run                    # CPU preview; requires an existing final freeze and matching schedule
mkdir -p results/S5                              # needed on a fresh copy before an S5 dry-run (P2 finding)
$P -m pccap.cli queue --stage S5 --dry-run          # CPU preview; creates queue_summary_dryrun.json
# The run owner may execute a version-authorized queue without --dry-run; --max-jobs N bounds a session.
# Stop file: results/S4/queue.stop. The current final tree refuses v2 confirm execution on code drift.
$P -m pccap.cli run --stage S4 --mode confirm --dataset zsre --arm C2 --realization 0 --perm 0 --manifest manifests/confirm/zsre_r0.json --dry-run   # P2: expected exit 2 on current tree; no override
$P scripts/s7_summary.py                         # CPU; rewrites results/S7/summary.json and summary.md (use isolated copy)""")
    change(reproduce, "### Reruns", """`<id>`, `<npz>`, `<same npz>` and `N` are placeholders, not literal shell arguments. Supply actual values.
`s4_05`, `s4_06` and `s7_03` accept `--out` to preserve existing reports. The final freeze remains the lead's act;
sampling sealed realizations is not part of the reproduction audit. Queue dry-run writes a summary but executes no jobs.
P2 exactly reproduced the numerical sections of the saved zsRE paired analysis, resource views, zsRE C2 order summary
and all four S7 summaries. Its historical frozen-source positive control resolved one confirm dry-run without GPU or
sealed-payload access; that control does not authorize bypassing the current-tree refusal.

### Reruns""")
    patch = "".join("".join(difflib.unified_diff(old[p].splitlines(True), new[p].splitlines(True), fromfile="a/" + p, tofile="b/" + p)) for p in names)
    target = ROOT / "docs/tasks/P2-X2-documentation-corrections.patch"
    with target.open("x") as f:
        f.write(patch)
    request = {"permission": "pending; existing-file edits require the user's permission", "patch": str(target.relative_to(ROOT)),
               "files": [{"path": p, "sha256_before": hashlib.sha256(old[p].encode()).hexdigest(), "sha256_after": hashlib.sha256(new[p].encode()).hexdigest()} for p in names],
               "scope": "Documentation corrections only. No production results, source, frozen manifest, decision register, shared board or queue mutation. Source-version and all-cost remediation remain owner actions."}
    with (ROOT / "docs/tasks/P2-X2-documentation-edit-request.json").open("x") as f:
        json.dump(request, f, indent=2)
        f.write("\n")
    print("Prepared corrections for", ", ".join(names))


if __name__ == "__main__":
    main()
