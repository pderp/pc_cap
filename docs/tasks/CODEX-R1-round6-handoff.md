# Codex round 6 handoff — 2026-09-14

All five CPU lane artifacts requested by the updated `docs/ongoing.md` are delivered. One correction to a newly created test awaits the user's permission; no existing file has been edited by Codex. No files have been staged or committed, no GPU or teacher job has been run, and no sealed payload has been opened.

## Lane results

| Lane | Deliverable and result | Remaining gate |
| --- | --- | --- |
| **R1-D3** | [Training candidate task](R1-D3.md): 6,000 seed-139 zsRE candidates, complete text/hash provenance and all-subject reservations. Claude consumed them and created the 3,000-item training pool during this round. | Completed; later register update is R1-D1e below. |
| **R1-45** | [Lexical analysis](R1-45.md): all 3,600 requested items, all 9,176,400 ordered other-prompt pairs, full lexical ROC curves. Recommend stopped subject recall plus stopped symmetric prompt overlap as a declared null-head ablation. | Any reader/schema change and GPU ablation belong to the owner. |
| **R1-46** | [Training review](../../logs/review_r1_50.md) and [repair-response recheck](../../logs/review_r1_50_response.md): prompt-only reader boundary holds in inspected controls; cache and population counterexamples documented. | Owner repaired several issues; complete cache provenance/admission and scale behavior remain pre-freeze gates. |
| **R1-D1e** | [Register v3](R1-D1e.md): all 6,000 drawn subjects excluded, including unused/rejected candidates; direct prior-clear remainder 52,498. | Fresh context/alias review, E.2 and sealing remain. One test correction awaits permission. |
| **R1-40b** | [Matrix v2](R1-40b.md): current mixed learned primary, one rule, six conditions/180 core cells; 480 conditional cells deferred; answer-position byte accounting and exactly two profile proposals. | Unfrozen/unlaunchable. Measured costs, final checkpoint/configuration and scope/budget decision remain. |

## Findings most relevant to the next round

**The learned-reader recovery succeeded at the current development scale.** Claude's mixed-domain reader uses null threshold 0.5 with no cosine gate on both datasets; the matrix now binds that candidate. The new training pool contributed to this recovery. Its development evidence is not confirmation or proof of predictive-coding benefit.

**Scale is now a priority.** CounterFact retention degrades at higher occupancy. Expanding top-k improves candidate recall but has not restored selection quality and can weaken locality rejection. zsRE's out-of-memory prompt population is harder than the current locality endpoint. Larger-memory training and the proposed subject feature should be judged on all four query populations at the final memory scale.

**Cache provenance is not fully repaired.** The owner added identity metadata, but migration compares cached content with another hash of the same cached content; paraphrase/locality inputs are omitted from the source identity; loaded feature arrays are not covered by the reported content hash. The response addendum contains runnable CPU counterexamples, acknowledges the completed old-pickle access repair, and does not allege that existing features are numerically wrong.

**The present core cost proxies still total 149.7 h against a proposed 15 h envelope.** The full-split drift allowance alone contributes 58.5 h with headroom/reserve. These are unmeasured ceiling proxies, so profile exact endpoints before choosing a budget/scope amendment. Do not shorten streams or quietly remove required comparisons.

**Average byte usage fits; the declared maximum does not.** Learned zsRE projects to 52,739,088 bytes with 1,000 mean-length records plus two clones. At 32 answer positions and 992 prompt tokens it requires 315,051,024 bytes. A five-position bounded-write option fits the current 64 MiB logical model but changes the condition and has not been selected. Exact final length inventory is needed.

## Verification and the pending permission

- R1-D3 CPU tests: **12 passed**.
- R1-45 CPU tests: **14 passed**.
- Register/matrix CPU tests: **23 passed, 1 failed**. The failing test incorrectly expects normalized subjects in the clear-survivor provenance inventory, which deliberately contains source indices and hashes.
- The corrected assertion passed against the actual artifacts **in memory**, without modifying the test file. Exact two-line relocation: [proposed patch](R1-round6-test-repair.patch); [edit request](R1-round6-test-edit-request.md). The user has been asked to authorize this narrow correction under the standing new-files-only rule. It remains unapplied at this handoff.
- Both stream-review CPU diagnostics completed; their JSON distinguishes positive controls from reproduced source defects.
- Ruff check and format check passed for all **10 newly created Python files** (seven scripts, three test files).
- Generation and source audits passed their artifact invariants. Initial logs, including the earlier lexical invocation failure before its script existed and the incorrect test assertion, are retained as historical evidence.

The pending edit touches only `tests/revision_v1/test_round6_register_matrix.py`, created by Codex during this round. No production, source-data, manifest or Claude-owned edit is requested by Codex. After approval, apply the hash-checked patch and rerun the 24-test register/matrix suite to a new log; then add a new verification completion record.

## Concurrent source changes and ownership

Claude continued training, repairing and committing during this round. The original source hashes remain intact in each artifact; they are not refreshed to disguise those changes. [Source audit](../../logs/r1_round6/source_audit.json) records 50 current matches, seven exact historical repository versions preserved from Git, and two external bank files changed by the owner's identity stamping. The later response audit hashes those updated bank files. The older serialized bank bytes were not reconstructed.

Historical snapshots live under `logs/r1_round6/source_snapshots/` and are evidence copies, not installed code. All resource inventories created here live outside the repo under `/home/derp/cap/assets/data/prepared/revision_v1/r1_d1e_v3/`.

The complete owned-file inventory is `CODEX-R1-round6-handoff.json`. Active `results/R1/` files and owner commits are excluded. Claims and old task records have not been rewritten; this additive handoff supersedes their earlier in-progress descriptions. The owner can mirror reviewed lane status into existing boards.

## Work that can proceed concurrently

1. **CPU/data:** adopt v3 in future consumers; recheck fresh contextual/alias exposure; prepare versioned E.2 admission. CounterFact source/remainder policy remains a separate decision.
2. **CPU/source owner:** repair complete bank identity/migration, input admission and exact query-population accounting; add targeted regressions. Core changes need distinct ownership.
3. **CPU/research design:** specify the subject-feature ablation and memory bytes, choose data/model seed axes and package-vs-training comparison claims, and resolve budget/scope after measured endpoint costs.
4. **GPU owner:** larger-memory reader training/evaluation, fresh E.2 and P1/P2 profiling, serialized through the lease.
5. **Lead:** choose the final checkpoint and single deployment rule, approve the final population and budget, then freeze. Final confirmation remains gated.

No additional GPU lane was claimed by Codex.
