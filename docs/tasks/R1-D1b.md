# R1-D1b — decided v2 entity/exposure policy

2026-09-14, Codex. **CPU lane delivered; final eligibility/sealing is not certified.** New files only; no register, source dataset or other agent's work was modified.

Outputs: `scripts/r1_d1b_entities.py`, `manifests/revision_v1/exclusions_v2.json`, `logs/r1_round3/entity_review_v2.json`. Detailed source text, per-subject decisions and candidate inventory are data artifacts under `/home/derp/cap/assets/data/prepared/revision_v1/r1_d1b_v2/`, with paths and SHA-256 hashes in the report. This preserves the repository/data boundary.

## Review decisions

All **236** v1 subjects excluded solely through contextual/punctuation matching receive an explicit disposition. Source-subject keys remain separate operational identities; only two checked personal-name pairs are canonicalized: `claude joseph dorat` → `claude-joseph dorat`, and `desi arnaz jr.` → `desi arnaz, jr.`. Punctuation folding is not treated as a universal entity linker: `Dawn!` (film) cannot automatically be identified with `Dawn`.

Every v1 exposure occurrence for 23 concrete false-positive classes was compared with the candidate's MEND identity question. Examples: BALL software versus a cue/cricket ball, *The Bill* television series versus the Bill of Rights, and *Around the Sun* album versus orbital motion. These establish a **23-subject lower bound on v1 lexical over-exclusion**. New training text introduces previously unreviewed contexts for nine of them, so only **14 subjects / 25 raw records** are released. The other nine stay conservatively excluded until those additional contexts are resolved.

The 3,000 DEC-037 subjects were already excluded by membership in the old eligible pool. All now explicitly carry **`train_pool_counterfact_v1`**. This adds 3,000 provenance reasons and removes **zero** additional candidates by explicit subject membership alone.

The review also screens that training pool's exposed prompts, paraphrases and locality text. It finds **424 additional candidate subject keys** absent from v1; all are conservatively quarantined. This is the count of omitted **possible contextual exposure exclusions**, not 424 proven same-entity leaks. Across old and new contextual classes, the emitted decision table contains 644 conservative quarantines, two verified aliases and 14 releases. V2 has **32,029** excluded source-subject keys.

## Candidate impact

| Policy stage | Raw MEND records remaining | Unique normalized subjects remaining |
| --- | ---: | ---: |
| V1 | 155,322 | 88,267 |
| V1 with reviewed releases only | 155,347 | 88,281 |
| V1 plus 3,000 explicit training subjects only | 155,322 | 88,267 |
| V2, including new contextual exposures | **154,306** | **87,857** |

New contextual quarantines cost 1,041 raw records / 424 subjects; releases recover 25 / 14. Net change is **−1,016 raw records / −410 subjects**. Counts precede teacher eligibility, fact deduplication, independent-realization construction and answer-quality checks.

## Validation and remaining gates

The script requires exactly 3,000 distinct normalized training subjects, verifies immutable source hashes before and after the review, preserves explicit exclusions, checks both verified-alias endpoints remain blocked, and creates outputs exclusively. All 236 requested classes have decisions; no class is silently dropped. It opens no sealed-realization payload and performs no teacher/GPU operation. The source inputs and detailed decision evidence can be independently replayed into new output paths.

This resolves the bounded register-policy review, not global entity resolution. Ambiguous substrings/homonyms are deliberately excluded **without asserting canonical equivalence**. Nicknames, translations, diacritic variants, pronouns and entities outside the dictionary have not been exhaustively resolved. Global under-exclusion is recorded as **unknown (`null`), not zero**. A decision to keep a possible match conservatively blocked is a policy decision, not verification that both mentions name the same entity.

Lead/orchestrator checkpoints before a final draw:

1. Accept or revise the v2 conservative policy and its remaining unknown-entity risk. Reference the new register explicitly; consumers still pointing to `exclusions.json` continue to use v1.
2. Review candidate source contexts/aliases before sealing; retain row/hash provenance. Do not equate the 87,857 subject count with 87,857 independent eligible facts.
3. Apply the E.2 teacher filter, fact/entity deduplication and independent-realization capacity checks under the GPU lease.
4. Record any later development exposure in a new register version before final sampling.

The old register, datasets, task board and `STATUS.md` remain unchanged under the user's new-files-only rule. The lead can mirror this task record when integrating the round.

Reproduce with a new repository manifest/report and a new assets directory:

```sh
env PYTHONDONTWRITEBYTECODE=1 /home/derp/cap/venv/bin/python scripts/r1_d1b_entities.py \
  --output manifests/revision_v1/exclusions_v2_replay.json \
  --assets-output /home/derp/cap/assets/data/prepared/revision_v1/r1_d1b_v2_replay \
  --review-output logs/r1_round3/entity_review_v2_replay.json
```
