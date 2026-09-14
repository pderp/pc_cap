# R1-D1e — exclusion register v3

- **Status:** register and candidate inventories delivered; final data preparation remains gated.
- **Agent/date:** Codex, 2026-09-14.
- **Inputs:** exclusion register v2; R1-D3's complete 6,000-candidate reservation; the historical fresh-candidate review; the owner's accepted 3,000-item zsRE training pool.
- **Outputs:** `manifests/revision_v1/exclusions_v3.json`, `scripts/r1_d1e_exclusions_v3.py`, two versioned candidate inventories under `/home/derp/cap/assets/data/prepared/revision_v1/r1_d1e_v3/`, this task record.
- **Verification:** generator source/hash/coverage checks passed; `logs/r1_round6/exclusions_v3.txt`. Register SHA-256: `e214de7d048c6b104fc62c75757eed01f12b47fb330eaeeb58c1a2bec8fbbd4a`.
- **Additional checks:** `tests/revision_v1/test_round6_register_matrix.py`; initial combined suite 23 passed, one test had an inventory-schema assumption error. Its two-line correction passed in memory and is awaiting permission in `R1-round6-test-edit-request.md`. See the final round handoff for any subsequent approval/rerun.
- **Cost:** GPU 0 s; no tokenization, teacher execution, final draw or sealed-payload reads.
- **Existing files:** unchanged by Codex. The new version does not overwrite register v2 or the older candidate review.
- **Questions for lead:** none to deliver this exposure update; future fresh-data admission and sealing remain owner decisions.

## Reservation and counts

Every one of the 6,000 drawn subjects carries reason `train_pool_zsre_v1`, including subjects not accepted into the 3,000-item training pool. The update preserves every prior normalized subject, canonical key and exclusion reason. It validates the reservation's list hash and every candidate hash; it checks that every accepted training subject belongs to the reservation.

| Inventory | Before | After v3 |
| --- | ---: | ---: |
| Excluded primary subjects | 32,029 | 38,029 |
| Raw remaining MEND candidate records | 154,306 | 143,753 |
| Unique primary subjects among those raw records | 87,857 | 81,857 |
| Representatives previously certified lexical-clear | 58,498 | 52,498 after direct subject removal |
| Re-certified context-clear under the newly exposed texts | — | Unknown |
| Fresh teacher-eligible examples | — | Unknown |
| Final realizations emitted | 0 | 0 |

The raw record reduction is 10,553 because one reserved subject can occur in multiple source rows. Removing 6,000 primary subjects does not imply removing only 6,000 raw rows.

The 52,498 figure is a **direct survivor ceiling**, not a fresh contextual clearance certificate. Prior-clear representatives can mention newly exposed subjects in paraphrases or locality contexts. Entity/alias/context checks must run against the expanded exposure set before the owner conducts E.2 and any final draw. Neither the candidate count nor the successful training filter proves that three fresh 1,000-item teacher-eligible realizations are available.

## Artifacts and interpretation

The new register binds both resource artifacts by path and SHA-256:

- `mend_candidate_subjects.jsonl`: all surviving raw candidate subject/index records, excluding every subject in v3.
- `prior_clear_subject_survivors.jsonl`: prior review provenance rows with source index, source/mapped hashes and flags. This is an index inventory, not another copy of full source text.

The register is explicitly nonfinal: `final_sealing_ready=false`, teacher eligibility unknown, and zero final payloads emitted. Its inherited policy/alias rules remain historical inputs; it does not silently broaden alias acceptance.

The older R1-D3 task record and candidate manifest correctly record that v3 had not yet been written at their creation. **This later task completes that reservation step.** Claude also completed E.2 and wrote `train_pool_zsre_v1.json` from the candidate list during the round. Neither event changes the historical candidate manifest.

The E.2 consumer computes greedy outputs for all prepared candidates, but its acceptance-count loop stops at 3,000 accepted rows. Therefore its reported teacher-correct count should not be interpreted as a complete 6,000-row rejection census without an independent full scan. This does not change the all-6,000 reservation or the accepted pool's predicate.

## Remaining owner checkpoints and parallel work

1. Review/adopt v3 and update future candidate/teacher/sealing consumers that still reference v2. These existing-file changes belong to their owners; Codex did not apply them.
2. Recheck contextual/entity/alias overlap against all exposed training texts. Record per-reason counts and complete versioned hashes.
3. Run E.2 on the admitted fresh inventory under the GPU lease; retain the seed/order and explicit reserve policy.
4. Resolve CounterFact's fresh-source or reason-specific remainder exception separately. A zsRE reservation does not resolve CounterFact availability.
5. Seal final realizations only after implementation, selection, cost and lead decisions.

Context review and register-consumer planning can proceed on CPU while Claude trains the reader. Teacher execution and profiling share the GPU lease. Final draw/sealing waits for the reviewed population.
