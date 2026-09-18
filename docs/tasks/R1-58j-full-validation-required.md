# Full validation: what is missing from the current cost evidence

Plan 9 requires the full validation split at endpoints, while allowing a frozen,
disclosed subsample for intermediate assays. Protocol v5.1 §5.2, incorporated by
D.1, explicitly says that 128 windows do not satisfy full-split coverage and
leaves full-split cadence and cost in U08/U16. Driver input validation and hash
checks are integrity work; they do not evaluate additional language-model tokens.

The bound source in `manifests/dev/lm_sets.json` contains **247,289 tokens**.
Current R1-64f recipes use its first 128 complete 128-token windows: 16,384 input
tokens and **16,256 prediction positions**. This was checked against the actual
token array without a model call. The same array yields 1,931 complete windows
and **245,237 prediction positions**, leaving 121 trailing tokens. If a short
final window is admitted, it contributes another 120 predictions; either choice
must be explicitly declared with context resets and denominators. The audit
proposes no silent policy change.

The historical `results/S4/drift_supplement.md` concerns v0 endpoint states and
reports 245,110 positions. It is useful planning evidence but is neither the
current revision's endpoint evaluation nor exactly the complete-window inventory
above. Its timing cannot close current U08/U16 without a justified transfer.

The missing run is a full-source endpoint drift/fidelity evaluation for the
current revision's admitted states: final occupancy 1,000 for zsRE/CounterFact,
actual 300 for MQuAKE, across required conditions and declared references. It
must preserve per-prefix selection; compare against the original base and own
cap-off reference as applicable (including S1's continued base); record finite
loss/KL vectors, coverage, tail/context policy, checkpoint/state/source hashes,
host RSS, device memory and whole-process wall cost. Intermediate sampled panels
may remain sampled where the admitted protocol allows them. Missing predictions
cannot be reconstructed from the existing 128-window results.

Producer: `scripts/r1_58j_validation_inventory.py`. Its machine audit is included
in each revision-3 cost evidence directory. It records `pending`, with zero model
calls. No additional GPU job was launched here. Resolve exact full-split endpoint
cadence/tail treatment and budget before production admission; a quantitative
runtime extrapolation, if used for scheduling, must retain its assumed status.
