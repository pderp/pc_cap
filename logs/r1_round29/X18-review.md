# X18 — assembler, memory evidence and v13 review

**Verdict: not ready for signature or launch.** The missing whole-package
producer is implemented and tested. Host evidence is substantially better, but
full-validation evidence and other substantive gates remain open. This review
does not authorize a production operation.

Machine evidence: `r1-x18-review.json`, produced by
`scripts/r1_x18_review.py`. It rechecks candidate v13, normative closure, source
hashes, memory padding, budget arithmetic, the eight corrected MQuAKE profiles,
and refusals of fabricated completeness. All work is CPU metadata analysis.

## Exact snapshot

Candidate v13 verifies **1,556 bindings**. Its SHA-256 is
`e8c12f4caec346071549ae9528d402068c2c4ec28e2557e3c80438d4acd1a562`.
Inputs/forms v8 consistently bind cost receipt v3, D.1, the six normative
documents, the runtime catalog and the new assembler. The inputs digest is
`752742decf2566e91a4194afad4c01cdf95ea161ce12a5c3583b93d1db01c73b`.
This is an unsigned draft, not the production frozen manifest.

At snapshot creation **one of four chain R profiles was complete**. Claude's
remaining runs continued during review; later results do not alter this snapshot.
The handoff records newer progress separately. Do not confuse live job progress
with which measurements a reviewed request actually binds.

| Cost/evidence quantity | Bound snapshot |
|---|---:|
| Condition × dataset rows | 27 |
| Measured device peak rows | 26 |
| Measured host peak rows | 26 |
| Host method: direct GNU time | 1 |
| Host method: unique temporal monitor match | 25 |
| Host method: proposed transfer, measured value null | 1 |
| Complete near-miss/revision profile rows | 10 |
| Pending cost reasons | 19 |
| Detailed non-signature blocker entries | 24 |
| Open scientific/operational gate IDs | 17 |

The ten full-endpoint rows are the nine CounterFact conditions plus primary
zsRE. The pending primary MQuAKE profile accounts for the absent device/host
measurement in this snapshot. Host measurements and endpoint completeness are
distinct; measuring memory on an older short challenge does not fill a missing
full challenge timing.

## Implementation finding closed

X16-06's missing whole-package assembler is closed as an implementation finding.
`scripts/r1_63j_production_bundle.py` now stages recipes, executable protocol,
freeze proposal, full matrix and queue bindings. It verifies receipt chain,
complete coordinate inventories, calibration v3, selected primary v5, current
driver/backend, independent populations and exact resource ceilings.

A 360-cell synthetic D9 rehearsal passes the actual queue and sealed-backend
metadata checks through a virtual final-path overlay, plus the operator's
publication preview. Tests refuse mismatched or tampered receipts, wrong runtime,
missing populations/gates, unsigned cost, reordered edits and an admitted
extension with only core population data. The 405-cell branch preserves the same
coordinate guard; this round's successful complete rehearsal is 360 cells, not
a claimed 405-cell production execution.

The runtime catalog preserves 27 adapter/construction identities, with explicit
conversion from development to sealed code inventories. Primary CounterFact's
historical recipe receives current integrity-driver metadata while retaining its
scientific configuration and source binding. No historical result is reclassified.

Staged files describe proposed executable bytes and their final references. They
cannot execute without the canonical final freeze path. Only the separate
operator's exact lead-approved publication transaction may create those paths;
the assembler never copies them. No real population was drawn/sealed, no freeze
was published and no closed gate receipt was invented in this round.

## Host evidence: what can and cannot be concluded

The host extractor recognizes the primary driver and comparator wrapper entry
points. It reads bounded prefixes of live logs, handles identity deltas, keys
processes by boot/PID/start ticks, and saves filtered excerpts with offsets and
raw sample hashes. Direct GNU time records require a successful exact recipe
path/hash and `--execute` command. The complete per-condition table is in
`host-rss-inventory.md`.

The monitor deliberately omits recipe argv; the old driver receipts lack UTC/PID.
Consequently, 25 rows use a unique driver process over a window inferred from
file mtimes and recorded durations. The primary CounterFact legacy result uses
its first phase's mtime/duration because the result has no attempt duration.
These matches are evidence with stated assumptions, not embedded run-ID proof.
Moved/copied artifacts can invalidate mtime inference. Ambiguity, poor coverage
and large sample gaps are refused.

Sampled RSS can miss transient peaks; observed kernel high-water RSS is retained
separately. Direct GNU time reports kernel maximum RSS. These metrics are not
summed across processes or confused with the host's 6 GiB free-memory launch
floor. All stored memory ceilings apply 1.5 to their stated measured basis.
The primary MQuAKE fallback remains an explicit unadmitted same-condition
cross-dataset proposal; its measured field is null.

Initial extraction drafts omitted comparator wrapper names and lacked the
legacy first-phase fallback. Those drafts are superseded. Cost receipt v3 binds
host evidence v3 and the durable excerpts under `host-evidence-v4/`, not the
earlier reports. Raw monitoring logs retain their existing 48-hour policy.

## Full validation is still a real missing experiment

The declared token source contains 247,289 tokens. All four new recipe drift
inventories equal its first 128 complete windows: 16,256 scored predictions.
The complete 128-token-window inventory instead contains 245,237 predictions,
with 121 trailing tokens. Including the trailing short window would add 120
predictions; the tail/context policy and endpoint cadence require explicit
admission. No padding or interpolation of the prefix scores can recover the
missing predictions.

Driver validation phases verify input and state integrity; they do not evaluate
the rest of the LM validation population. The historical v0 full-split supplement
uses different endpoint states and a different recorded denominator. It supplies
neither current revision results nor a measured current cost.

`docs/tasks/R1-58j-full-validation-required.md` specifies the missing current
endpoint evaluation and evidence. Until it exists, the revision-3 validator
rejects a false approval even after both the top-level pending list and status
are changed in memory. No such altered receipt was published or signed.

## Schedule and scientific qualifications

The unchanged matrix has 360 core plus 45 optional cells. Declared solo estimates
remain 209.4 h core and 12.15 h extension. Expected combined process time is
254.7825 h after the assumed 1.15 factor; the shared proposal is 750 process-hours.
The all-cells, two-complete-attempt padded sum is 764.3475 h, so exhaustion can
leave an explicit incomplete inventory. These are projections/ceilings, not
observed whole-matrix performance. Keep the October 9 experimental stop.

Earlier scientific qualifications remain: nominal three-cluster intervals;
21 unavailable MQuAKE 1,000-edit intervals; 6,036/6,084 empty zsRE baselines;
historically exposed development pools; unavailable firing telemetry for six
v0/S1 comparator profiles; and exploratory κ/stress/tail claims. The eight
corrected MQuAKE result identities and bounded-locality counts were rechecked.

## Remaining owner work

Finish chain R and rerun host/cost extraction into new paths. Review any
cross-condition endpoint or cross-dataset host transfer explicitly. Complete the
required full-validation evidence and reconcile the scientific gates, including
actual population operations and current exposure. Refresh the candidate/forms
and all request digests after those inputs change. Then perform the exact lead
approval/publication workflow. HT-4f remains blocked on a valid, complete signed
cost receipt. The assembler's successful rehearsal does not remove those gates.
