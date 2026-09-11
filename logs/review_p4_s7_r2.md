# S7 repair recheck (V4)

Status: done. Agent: Codex. Date: 2026-09-11. GPU seconds: 0.

The three actionable S7 findings in the previous review are closed on the repaired
source. The original audit was rerun, with its output directory redirected in memory;
the original audit, old evidence and shared implementation were not edited.

| Finding | Independent evidence | Result |
| --- | --- | --- |
| 1. Damage omitted paraphrase prefixes | Original two-prefix counterexample now reports I_ij = 2.0, exactly the independently computed mean loss increase over Q_i. The prompt-only increase is zero, so this distinguishes the repaired definition. | Closed |
| 2. GRACE lost the original prompt boundary | Teacher-forced prefixes of lengths 2 and 3 both carry key position 1; both greedy decoding steps also carry 1. Every observed call has the expected explicit boundary. | Closed |
| 3. Grammar inventory overlapped P4 | All 200 members have unique seeds in 5,000,000–5,150,007; no exact overlap with the published P4 schedule and no overlap with DATA-06 seed blocks. | Closed |

`tests/analysis/test_s7_01.py`: **9 passed in 0.94 s**, including the three added
regressions. The audit also confirms that the implementation and inventory did not
change during its run.

The canonical pair hash is
`9cedd861e37341d2ce5b38122b3c2f3aabefecb6957577f40784a15c2abfd823`.
It matches the hash recomputed from the inventory and the hash recorded by the E.2
selection file. All nine dataset/stratum selections equal the first eligible pairs
in the fixed order. zsRE and grammar fill 34/33/33; CounterFact fills 9/33/33. The
CounterFact shared shortfall is recorded, not silently filled or resampled.

The subject-only inventory audit still passes: zsRE S7 subjects are disjoint from
the reserved development/S0/eligible-pool subjects; CounterFact S7 subjects belong
to the reserved development subjects and are absent from its eligible pool. This
read only subject-string projections of eligible pools; no sealed realization
payload was opened.

The fourth, interpretive observation is now explicitly acknowledged by
`strata_qualification`: natural-language strata are operational proxies, not
proof of shared mechanisms, independent supports or key-space proximity. The text
also commits to semantic contradiction review before reporting outcomes.
**That future semantic review has not been completed by this structural audit.**
Passing inventory checks does not certify mechanistic interpretations or predict
S7 outcomes.

## Reproduction and evidence

From the repository root, with CPU-only environment variables and bytecode disabled:

- `PYTHONPATH=. ../venv/bin/python -B scripts/review_s7_round4.py`
- `../venv/bin/python -B -m pytest -q tests/analysis/test_s7_01.py -p no:cacheprovider --basetemp=../assets/tmp/s7-round4-tests`

The existing output directory makes the audit refuse an overwrite on a repeat;
select a fresh output directory in a new wrapper. Evidence:

- [Audit JSON](p4_s7_review_r2/s7_audit.json), including source hashes before/after.
- [Closure checks](p4_s7_review_r2/closure.json).
- [Audit stdout](review_s7_round4_stdout.txt).
- [Regression tests](review_s7_round4_tests.txt).
- [New wrapper](../scripts/review_s7_round4.py).

No production S7 execution, checkpoint mutation, freeze, GPU lease or board update
was performed. The orchestrator can mirror V4 completion. S7 checkpoint experiments
remain dependent on the scheduled S4 work.
