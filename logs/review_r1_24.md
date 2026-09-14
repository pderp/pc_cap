# R1-X7 — review of the completed R1-24 continuation controls

Status: complete (read-only development review). Reviewer: Codex. Date: 2026-09-14.
Evidence cutoff: the round-8 [source index](r1_round8/source_evidence.json), including a preserved copy of the
[notes reviewed](r1_round8/source_snapshot/docs/R1_stage2_notes.md). Results were recounted from the two closed execution
directories, not inferred from the notes. No model execution, GPU use, new training, or confirmation-data access.

**The execution records reconcile, but “matched” only establishes the declared forward-token budget. The literal
control passes the aggregate base-fidelity gates and changes parameters numerically; the informative LM control fails
the KL gate. Neither provides a confirmatory classification from these 100-edit development streams.**

## 1. Evidence and identity

The CPU [recount](r1_round8/x7_execution_review.json) verifies 16 cells (eight per treatment), ordered item identities
across conditions, saved endpoint/summary agreement, all 9,042 accepted training-step records, metric arithmetic,
perplexity-ratio arithmetic, checkpoint file hashes, and evaluation base checksums. All 16 cells have 100 edit items;
LS has 50 prompts per cell. S0/R0 metric and drift repetitions are identical across the two jobs and are shared
references, not extra independent samples. This review does not reconstruct missing runtime before/after checksum
fields or certify a full validation pass from a subset.

| Treatment | Recipe SHA-256 | Continued checkpoint SHA-256 |
| --- | --- | --- |
| literal, `r1_24_literal_v3b` | `82745f183ed70120529289afec5cded121e220d0c0268e8a0f5fcec46b84958f` | `7591cfd1209f01c1d9877be6b596da56e3a3b45c2fa3e693cdb31407bbf59ef5` |
| informative LM, `r1_24_lm_v2b` | `2d084075f0d2b918071b637d1a159895d7198ec6320fb344abc39e864e627d7b` | `4b09cb8d7d3fb301025d0ecdcaede7ecca68c0703ab0a63fd60bb6a77aa50a3a` |

The original tensor digest is `c4ac3fb867dad146dbddfcd4af0b9b110d8de3bce41127bb1fc11b1e533bc082`.
Literal continued tensor digest is `5e6dc3bd240f1e8032e6aac9775c087f8742d63a597c4712ee247403850e604d`;
LM is `f52e2204fa9d9e3f6bcf78ee32fff1d05acd9cc5df2f509a953d309ba77290c0`.
These are tensor identities, distinct from serialized checkpoint-file hashes.

## 2. Fidelity admission is separate from budget admission

| Treatment | KL to original, nats/position | ΔNLL, nats/position | PPL ratio | KL ≤ .001 and ΔNLL ≤ .01 |
| --- | ---: | ---: | ---: | --- |
| literal | 0.0000293325 | −0.0000617914 | ≈0.99993821 | pass |
| LM | 0.0949791045 | −0.1050649434 | 0.9002660543 | **fail: KL** |

Fidelity uses 8,192 scored positions in the held-out OpenWebText tail; both distributions cost 16,384 forward-pass
tokens. Better next-token loss does not cancel KL failure. A `matched_budget_claim: true` or
`interpretation: matched` receipt cannot admit the LM checkpoint as a fidelity-matched substrate.

The literal objective has zero gradient in exact arithmetic when student and teacher are identical. The executed
optimizer is not an exact no-op: its first logged KL is about 1.2451e−7, gradient norm 3.1139e−5, maximum logged gradient
norm about 20.657, and the output tensor digest changes. Report a **numerical negative control**. Calling the executed
checkpoint a provably unchanged base obscures its measured locality changes.

## 3. DEC-033 contrasts

S0 = original base + v0-stable C1; S1 = continued base + v0-stable C1; R0 = original base + reference reader.
The continued-base learned-reader cells are additional diagnostics, not S1. All differences below are treatment minus
control; ES is immediate edit success. RET-GS values are mean per-item paraphrase success.

| Treatment | Dataset | Contrast | ΔES | ΔRET-GS | ΔLS | Point comparison with +.05/−.02/−.01 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| literal | zsRE | S1−S0 | 0 | +.05 | 0 | meets point margins only |
| literal | CounterFact | S1−S0 | 0 | 0 | −.08 | misses GS and LS |
| literal | zsRE | R0−S1 | 0 | +.49 | 0 | meets point margins only |
| literal | CounterFact | R0−S1 | 0 | +.795 | +.08 | meets point margins only |
| LM | zsRE | S1−S0 | 0 | −.05 | −.14 | misses GS/LS; fidelity fails |
| LM | CounterFact | S1−S0 | 0 | 0 | −.72 | misses GS/LS; fidelity fails |
| LM | zsRE | R0−S1 | 0 | +.59 | +.14 | meets point margins; comparator fidelity fails |
| LM | CounterFact | R0−S1 | 0 | +.795 | +.72 | meets point margins; comparator fidelity fails |

These are one development stream per dataset, not three fresh realizations × five orders. No paired-cluster interval,
noninferiority conclusion, “positive” classification, or population-level exclusion of continuation benefits follows.
Within the tested recipes the learned-cap retention gain remains large. A valid informative continuation could behave
differently. The literal CounterFact LS drop is 4/50 changed answers; the LM drop is 36/50. Report the 0.02 LS step size
without changing the accepted −0.01 margin.

## 4. Attribution and wording requiring owner attention

The notes say the LM LS collapse is base damage and appears with “no cap writes at all (S1 rows).”
**S1 runs an active v0-stable editing cap.** Similar collapse under two caps and the failed base KL gate support a
base-change explanation, but do not identify its exclusive cause. The common LS reference is the original base, which
intentionally counts substrate changes too. A continued-base cap-off replay on the exact same 50 prompts would separate
base-only answer changes from incremental cap effects. That diagnostic is not present in the reviewed comparison.
Near-tie flips are a plausible explanation of literal LS sensitivity, not established by saved token-logit margins.

Recommended replacement interpretation for the owner: “The tested continuations do not recover the reference reader's
development RET-GS. Literal self-KD passes aggregate base fidelity but has numerical parameter and locality changes.
The LM recipe fails base fidelity; common-reference LS deterioration is consistent with substrate drift, while
base-only versus cap contributions remain unresolved.”

The statement that a valid informative control is “not a Stage 4 blocker” needs a scope decision: matrix v3 includes
S1_LM. Either admit a separately specified fidelity-valid recipe before final matching, or explicitly change the
confirmatory scope and claims. Do not silently reuse the failed checkpoint or drop the condition after seeing results.

## 5. Budget interpretation

The [reconciliation](../manifests/revision_v1/r1_24_budget_reconciliation_v1.json) binds 458,002 outer forward tokens
plus 313,579 feature-bank tokens = **771,581 forward-pass tokens**. The reference's 458,002 reverse positions are
reported separately. This was a re-execution of the reference configuration for accounting, not the original seed-0
weights' historical training ledger. The accounting-run and evaluation parameter identities differ and are disclosed.

| Treatment | Steps | Student forward tokens | Teacher forward tokens | Total forward tokens | Reverse positions |
| --- | ---: | ---: | ---: | ---: | ---: |
| literal | 3,014 | 385,790 | 385,790 | 771,580 | 385,790 |
| LM | 6,028 | 771,581 | 0 | 771,581 | 771,581 |

Literal leaves one indivisible forward-budget token unused. LM uses one additional source lookahead token for its
next-token targets (771,582 source tokens), not an extra charged student prefix. Different reverse work, source exposure,
optimizer costs and wall times prevent treating this as equality of total compute. Fidelity and stream evaluation are
charged outside this training envelope. Each complete job holds the lease for roughly 22 minutes; those intervals
include evaluation and are not pure training accelerator seconds. Repeated S0/R0 executions incur real cost, even
though analysis must not treat them as independent replications.

If R1-54 becomes the primary condition, reconcile its training and feature-bank budget and issue new continuation
recipes. These two jobs remain valid historical controls against primary v1.

## 6. Ordinary-text drift is a distinct endpoint

R1-24 editing drift uses `drift_tokens.npy`, 128 windows × 127 scored positions = **16,256**, rather than the
8,192-position fidelity slice above. The evaluator resets selection for every complete next-token prefix.
On the original base, R0 increases mean loss by +0.59906228 nats (zsRE; PPL ratio 1.82041096) and +0.39352807
(CounterFact; ratio 1.48220089), while S0 gives +0.00093143 and 0 respectively. High edit RET-GS therefore does not
establish ordinary-text preservation.

Concurrent R1-54 development evidence is preserved in the round-8 source snapshot: adding text nulls reports near-zero
zsRE drift on 32 × 127 = 4,064 positions and 0/96 firing probes, with RET-GS .96/.725. This is encouraging but a different
reader and a smaller endpoint; it does not retroactively remove primary v1's drift. CounterFact-edit drift, seed
replication, long memories and final admission remain separate checks. See [the null specification](../docs/tasks/R1-50b.md).

## 7. Reproduction and disposition

`PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= /home/derp/cap/venv/bin/python -B -m scripts.r1_x7_review --output logs/r1_round8/x7_execution_review_recheck.json`

The output must be a new filename; the saved report records the first execution of `review()`.
[Verification log](r1_round8/x7_review_cpu.txt): 16 cells, 8 contrasts, 82 source hashes, 3,014 + 6,028 accepted steps;
literal fidelity true, LM false. No existing notes, receipts, checkpoint, manifest, or board file was changed.
Owner follow-ups are the wording/attribution qualifications, the S1_LM admission decision and any budget refresh.
