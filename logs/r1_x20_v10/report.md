# X20 — session v10 and published Stage-4 verification

**PASS. The frozen package passes X20's technical launch check.** The orchestrator
has separately recorded the lead's launch authorization and started two workers;
this review found no package defect requiring that run to stop. This report
does not issue a new signature or launch command.

Completed September 18, 2026, by Codex. The full replay finished at
21:33:50 UTC (17:33:50 EDT). Authoritative evidence:
[verification JSON](attempt-04/verification.json),
[console record](attempt-04.console.log), and the independently checked
[matrix design metadata](matrix-root-verification.json).

| Check | Finding |
|---|---|
| Signed session | All eight completed requests reconstruct exactly from candidate v15 and the prior input state. Their saved reviewed forms, receipt contents, request digests, and earlier unblocked journal previews agree. |
| Derived admissions | All 18 gate records inherit the correct signed steps. Their 23-row journal prefix matches exactly; the completed freeze is bound through the 26-row prefix. The schedule retains the October 9 completion date and 750 process-hour cap. |
| Clearance | Recomputed from the fixed register, raw source rows, and bound review evidence. The resulting file bytes match: 6,084 eligible zsRE subjects, 6,121 CounterFact, and 2,161 MQuAKE. |
| Draw | Seed **378462438976234321867** reproduces the exact saved reservation bytes, including all 45 allocation groups, 45 paired orders, RNG records, and predetermined composition memberships. No new selection artifact was emitted. |
| Endpoints | All 330 cell populations and 45 unique payloads reconstruct exactly from the unsealed inputs. Each of the nine dataset × realization groups has 50 locality prompts, 100 near-miss pairs, and 50 revision items. No construction shortfalls. |
| Locality amendment | An independent scan confirms the first 50 distinct eligible prompts in sorted reserved-outside-item/source-prompt order, excluding every reserved edit/paraphrase. The MQuAKE groups exclude 22, 8, and 6 overlapping source prompts. No new subjects or model outcomes enter selection. |
| Seal | The reconstructed reservations, population, and all 45 payload copies match the sealed file hashes; all 330 inventory identities agree. Sealed payload and reservation copies were hashed, **not parsed**. |
| Publication | All **334** published artifacts are byte-for-byte copies of the reviewed staged sources. The bundle's source-input digest reconstructs from the genuine session and derived admissions. |
| Candidate/runtime | All 330 recipes preserve the candidate's 27 runtime templates, signed costs, calibration values, and selected v5 primary weights. Their remaining experimental design fields match D.5. |
| Final matrix and queue | Native metadata admission passes for 285 core plus 45 optional cells, with block sizes **45 / 45 / 45 / 90 / 60 / 45**. A separate check verifies all 59 non-cell matrix fields and extension metadata against the declared design and permitted publication updates. |
| Launch form | The already saved step-9 form reconstructs to its clean preview digest and binds this exact final matrix, queue bindings, receipt root, and two-worker setting. X20 did not execute it. |
| Source stability | The lock passes before and after review: **916 resources and 446 Python implementations**. The review additionally tracks and rehashes **1,731** file identities. Later journal activity is separated from the immutable reviewed prefix. |

The final freeze SHA-256 is
`60f2c09461330852f673bcc0a818bf6cc972bda02b68312dee11a474d04dcfcb`.
The final matrix SHA-256 is
`06fa8b3b3f3d734c12d47ac2b1b09d8dcd0c35c203013456c9409590329d56bb`.

The MQuAKE composition populations contain 80, 85, and 89 eligible cases across
the three realizations. zsRE and CounterFact have no planned composition cases
in this draw. Those empty populations are not evidence of successful composition.
The final full-validation contract still requires 245,237 positions against both
references; this review verifies its binding, not future assay results.

Five deliberate corruptions were rejected: a changed signed seed, a draw seed
different from its admission, a wrong sealed-payload digest, a missing expected
population item through the native seal validator, and a wrong queue-matrix
digest. The separate matrix check also rejects a changed design field. The
successful replay used **80.9 seconds** and peaked at **1,212 MiB** process RSS.
GPU use and model calls were zero. Native queue checks used hash-checked metadata
read caching; all validation predicates remained installed and all tracked bytes
were rehashed at the end.

At the accounting snapshot, two started worker attempts had no terminal receipts.
The four unknown-cost entries are the driver-attempt and enclosing process record
for each of those two attempts. Consequently the native live projection is null;
its zero *completed, known* hours must not be reported as zero actual spend. Their
finish receipts will establish the charge. Independently, the frozen no-failure
scenario sums to 562.574 solo process-hours of cell ceilings, or **646.960** after
the single 1.15 two-worker multiplier, leaving **103.040 hours** below the 750-hour
cap. This is a ceiling scenario, not measured runtime or an additional retry
allowance. [Calculation](static-cost-scenario.json).

No scientific or implementation change is requested by X20. Continue the
registered execution, failure accounting, fidelity-watch reporting, and October 9
stop. Semantic clearance judgments and human authorship of recorded delegated
approvals are inputs to this verification; they were not independently re-adjudicated.
This result concerns the current operational package. It does not claim the
historical project-wide provenance scan is clean; R1-63o's previously disclosed
historical/protected findings remain separate.

All reviewer files are under `logs/r1_x20_v10/`. No locked file, sibling repository,
service, published artifact, or task board was edited, and no commit was made.
Attempts 01–03 are harness-development records: initial unsigned forms were
distinguished from revised journal previews; compact endpoint serialization was
distinguished from indented seal serialization; and the payload access guard was
corrected to allow the **inventory metadata** while continuing to refuse payload
and reservation parsing. Those failed drafts are not project defect findings.

To repeat the full review, choose a new output directory under this lane:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= OPENBLAS_NUM_THREADS=1 \
  ../venv/bin/python -u logs/r1_x20_v10/verify.py \
  --output logs/r1_x20_v10/recheck-01
```

Task reconciliation: R1-63o, R1-D14b, and HT-4f already have completion records;
R1-D10i was superseded by R1-63o. X20 was the newly available lane and is now done.
