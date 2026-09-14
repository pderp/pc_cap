# R1-D1c — fresh zsRE candidate review

- **Status:** CPU deliverables complete; import-only cleanup awaits permission in `CODEX-R1-round4-edit-request.md`. Teacher eligibility and the final draw are outside this lane.
- **Agent:** Codex. **Date:** 2026-09-14. **Input repository:** `3ba95b55febe20d94f86180186ce163334261ad3`.
- **Inputs:** `docs/ongoing.md` round 4; plan 9 D-R2(b); DEC-033/034/037; `manifests/revision_v1/exclusions_v2.json`; its pinned MEND train candidate inventory; pinned raw MEND train and GPT-2 tokenizer. Source hashes are in the output manifest. No sealed payload was opened.
- **Outputs:** `scripts/r1_d1c_candidates.py`; `manifests/revision_v1/zsre_fresh_candidates_v1.json`; `logs/r1_round4/zsre_candidate_review.json`; `tests/revision_v1/test_round4_data_matrix_cpu.py`; four data/review JSONL files under `/home/derp/cap/assets/data/prepared/revision_v1/r1_d1c_v1/` (paths and SHA256 in the manifest).

## Result and limits

There are **58,498 candidates clear of the automated checks**. This is ample textual capacity for 3 × 1,000, but the number passing the BP teacher's E.2 eligibility test is still unknown. A retention rate of at least **5.1284%** would yield 3,000 before any additional canonical-entity or contextual-overlap exclusions. No realization has been assigned, and no candidate is certified final or teacher-eligible.

| Filter checkpoint | Records |
| --- | ---: |
| Raw MEND train records | 163,196 |
| After v2 primary-subject exclusion | 154,306 |
| After field and token checks | 154,305 |
| After fact deduplication | 154,277 |
| After primary-subject deduplication | 87,857 |
| Flagged for review | 29,359 |
| Clear of automated checks, before E.2 | 58,498 |

The one structural rejection has identical prompt and rephrase. Fact deduplication removes 28 rows; subsequent subject deduplication removes 66,420. The final representative inventory has 87,857 rows, split into 29,359 flagged and 58,498 clear. Flags overlap: 23,630 locality mentions of an excluded subject; 6,971 rephrase mentions; 6,526 prompt mentions; 5,694 subject-field mentions. Another 414 rephrases and 5 source prompts lack the primary subject literally; one locality prompt mentions its edit subject; three locality answers equal the edit answer. These are review flags, not determinations that the dataset is wrong.

## Preparation contract

1. Verify the v2 inventory and raw-data hashes. Recompute primary-subject eligibility from raw source indices and require exact agreement with v2. Normalize using NFKC, case folding and whitespace collapse, preserving punctuation in primary subject keys.
2. Require nonempty subject, source query, rephrase, locality query and locality answer, plus a valid nonempty answer list. Reject identical rephrase/edit queries, locality equal to either edit query, embedded answer terminators, and NUL text.
3. Use `answers[0]` as the canonical answer and `answers[]` as aliases, exactly as the existing zsRE data mapping. Do not substitute `pred` or `alt`. Use TRAIN-specific IDs rather than the historical helper's eval-prefixed IDs.
4. Tokenize prompt and answer separately using the pinned tokenizer. Include the leading-space convention and terminating newline token 198 in the answer. Enforce 1–32 answer tokens and 1–992 tokens for each query. Require answer round-trip and a distinct tokenized rephrase. All clear answers are at most 21 tokens including newline; the mean is 3.7143. Clear prompt/rephrase/locality means are 11.0184 / 10.8014 / 14.2309 tokens.
5. Traverse immutable source indices in ascending order. Keep the first valid normalized `(prompt, canonical answer)` fact, then the first valid primary subject. This is deterministic preparation, not random sampling. The operational fact key is not a relation/entity graph.
6. Search subject, source prompt, rephrase and locality with word boundaries against all v2 exclusion keys. Matching folds punctuation and records the original exclusion keys and their canonical classes. Thus `Yorkshire` does not match `York`, while punctuation variants can conservatively match. Ambiguous lexical matches remain flagged.
7. Write ordered, clear and flagged mapped payloads outside the repository. Write a review row for every one of the 154,306 post-exclusion source records, including rejected/duplicate statuses and source/field hashes. The repository manifest carries source and mapped hashes for every chosen representative, including flagged rows. Candidate fields explicitly set teacher eligibility and final assignment to null.

## Verification

Successful generation command (exclusive-create outputs; use a new version directory for any repeat):

```bash
env PYTHONDONTWRITEBYTECODE=1 RAYON_NUM_THREADS=2 /home/derp/cap/venv/bin/python scripts/r1_d1c_candidates.py --output manifests/revision_v1/zsre_fresh_candidates_v1.json --assets-output /home/derp/cap/assets/data/prepared/revision_v1/r1_d1c_v1 --report logs/r1_round4/zsre_candidate_review.json
```

The combined targeted CPU test run is recorded in `logs/r1_round4/pytest_cpu.txt`: **43 passed, 4 expected failures**. The four expected failures belong to R1-X3's remaining core defects, not this candidate review. Candidate tests compare the mapping with the shared tokenizer, exercise malformed records and word boundaries, verify every candidate's raw and mapped hashes, all review field hashes, uniqueness/order, and the complete clear/flagged partition. Source and external artifact hashes also match. The only new-file lint finding is an import-order fix; its exact proposed patch preserves candidate behavior and requires the bound script hashes to be refreshed after approval.

**Done-when:** ordered representatives ✓; fact/subject deduplication ✓; rephrase/locality structural and token checks ✓; exclusion-class mention flags ✓; filter counts and per-record hashes ✓; no teacher pass or final draw ✓.

## Handoff and remaining tasks

1. Owner reviews/disposes of flags before admitting any flagged row. The 58,498 clear rows can be the starting inventory for review and E.2; they are not an exposure-free final certificate. Lexical matching cannot resolve every alias or certify paraphrase meaning. The prompt/answer conflict flag is a sequential check over representatives, not a global contradiction detector.
2. Run the pinned BP teacher with complete greedy answers and the project's alias/matching convention. Keep items the teacher does not already answer correctly, record exact tokenizer/checkpoint/decode identities and failure reasons, and charge the actual work. Candidate ordering must remain fixed; do not replace failed representatives with an alternate fact for the same subject based on observed model outcomes without a new policy.
3. Check canonical subject disjointness and contextual mentions across the eligible inventory and proposed realizations. Different primary subjects do not ensure independent contexts or locality entities.
4. Lead draws three disjoint 1,000-subject realizations from the reviewed eligible inventory and seals them with source, exclusion-policy, teacher and per-record identities. Confirm full paraphrase coverage before sealing. Keep future training away from this inventory; if exposure occurs, version the register and regenerate candidates.
5. No GPU time was used. No tracked file or task board was edited; the additive round-4 handoff is for the orchestrator to mirror. No commit was made.

**Questions for lead:** none required to finish this preparation lane. E.2 execution, contextual review and sealing remain with the assigned owners. The pending two-script cleanup request is separate from any data-policy change.
