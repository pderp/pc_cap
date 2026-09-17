# Round 27 handoff update — pair-unit clarification resolved

2026-09-17. This status update supersedes statements in the original round-27
handoff, X16 report and edit requests that the pair-count interpretation is
awaiting a lead answer. Their other findings and recorded test results stand.

The lead explicitly approved **multiple disjoint pairs per template family**.
There are 100 planned pair slots per dataset and realization; 100 distinct
families are not required. See `DEC-062-pair-unit-clarification.md` for the exact
answer and its scope.

- **R1-D9f:** the implemented contract matches the clarification. No code change
  or new allocation diagnostic is needed. Pair-count ambiguity is resolved.
- **X16-04:** the semantic question is closed. The already-proposed protocol
  wording may use multiple disjoint pairs per family.
- **R1-58g:** exact lead admission and the remaining package repairs still apply.
  The protocol must implement DEC-062 and hash-bind its normative dependencies.
- **HT-4f:** still awaits valid signed typed cost admission.

The current candidate v11/forms v6 and diagnostic evidence remain byte-for-byte
unchanged. They still require the owner to incorporate the protocol amendment,
normative bindings, complete cost evidence, closed gate receipts and final recipe
publication package into the successor admission package. The complete operator
request has not been signed by this clarification.

The previous **80 passing CPU tests** and repeated-family test remain applicable;
this follow-up changes documentation/status only. No GPU jobs, actual draws,
signatures, staging or commits were performed. The original handoff and evidence
hashes remain preserved in `CODEX-R1-round27-handoff.md` and
`logs/r1_round27/handoff-validation.json`.
