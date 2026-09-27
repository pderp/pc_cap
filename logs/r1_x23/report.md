# X23 — receipts for ordered cells 136–270

**PASS, with the four previously disclosed parent-decision gaps retained.**
Capex, September 27, 2026. Read-only CPU audit; no experiment, receipt, watch
journal, queue configuration or frozen implementation was changed.

All **135 selected cells**, **405 checkpoint receipts**, **272,160 phase records**
and **30 distinct opaque sealed payloads** pass the checks. Recorded recipe,
matrix, freeze-contract, implementation, payload and checkpoint identities agree
with current bytes. Every saved native-analysis input was also checked. Snapshot
bytes were hashed, not restored into models. This establishes recorded artifact
integrity, not independent numerical replication or a passing fidelity benchmark.

The enclosing processes charge **251.44904050168824 hours** for cells 136–270.
The complete main queue charges **392.4196504443145 hours**, agreeing with the
halt ledger. There are zero failed attempts, retries, unknown costs or uncovered
driver charges. Each covered driver attempt contributes its enclosing process
time once; its nested driver timer is not added again. These are summed process
hours, not elapsed GPU hours.

For the full 270-cell process inventory, cells 1–90 use bindings v1 and the
1.15 two-worker factor; cells 91–270 use v2 and the 1.7 factor. The v2 consumer,
base queue, scheduler, resume authorization and amendment bindings match. The
amendment changes the effective ceiling, not the recorded actual cost.

| Ordered cell | Condition / dataset / realization / order | Parent decision | Evidence disposition |
| --- | --- | --- | --- |
| 89 | v0_stable / MQuAKE / 1 / 103 | Absent at Q21 cutover | Start/finish and cost verified; outside this lane's full checkpoint/phase scope |
| 90 | v0_stable / MQuAKE / 1 / 104 | Absent at Q21 cutover | Start/finish and cost verified; outside this lane's full checkpoint/phase scope |
| 269 | S1_literal / zsRE / 2 / 103 | Absent at DEC-074b halt | Full selected-cell evidence and later watch observation verified |
| 270 | S1_literal / zsRE / 2 / 104 | Absent at DEC-074b halt | Full selected-cell evidence and later watch observation verified |

These are exactly the gaps disclosed in
[the owner reconciliation](../R1/operations/Q21_cutover/halt-reconciliation.md).
No additional missing decision was accepted, and no missing record was
manufactured. A full receipt chain cannot be claimed for these four parent
decisions; their absence does not imply a lost experimental result.

Every selected cell's fidelity-watch observation reproduces from its completed
result and bound validation evidence. For each of the **133 existing selected
parent decisions**, its exact historical journal prefix reproduces the counts,
entry/alert hashes, alert reasons and managed document hash. Historical manual
document context comes from Git, as in X22. The two selected decisionless cells
have independently reproduced owner-applied observations, without invented
historical parent decisions. The final unchanged watch snapshot contains **274
observations, 163 breach entries and 32 creep alerts**; **72 breach cells and 15
creep-alert cells** fall within this audit's selected range. None is an admission
veto; the audit does not certify human notification delivery.

Authoritative evidence is [evidence-final/report.json](evidence-final/report.json),
SHA256 `008b4451a53b6fbf1c0ee997f64c95b174f10f9d78fa777efc1c8d0647e4309c`.
It includes each selected cell's recipe, process/result/checkpoint references,
phase count, cost and watch disposition. Its **275,770 immutable source bindings**
are in **28 hash-bound parts**, keeping individual files below the repository
size limit. Every input was rechecked after the audit. The evidence-v1 directory
is the pre-format verification pass; evidence-final binds the final formatted
producer and is authoritative. Their scientific counts, costs and watch findings
agree.

Reproduce with a new output directory:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
  OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 \
  ../venv/bin/python -m aw.x23_receipts --output NEW_AUDIT_DIRECTORY
```

`NEW_AUDIT_DIRECTORY` is a placeholder. The helper reuses the X22 receipt utilities
and installed phase/watch verifiers; it does not import a training job. The
focused negative fixtures reject altered binding versions, ceiling factors,
receipt bytes, historical watch counts, prefixes and document hashes. Three
focused tests and the **99-test ordinary CPU suite** pass; two slow tests were
deselected. Evidence and validation logs:
`logs/additional_work/round49/{x23-run-final.txt,x23-tests.txt,x23-validation.json,aw-tests.txt}`.
