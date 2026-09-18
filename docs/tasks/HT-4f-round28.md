# HT-4f — waiting for complete signed cost admission

Round 28. **Blocked; no final claim ledger v6 published.**

The new typed cost receipt v2 is a schema-correct draft with
`lead_approved: false`, 45 pending-evidence reasons and missing host/full-validation
measurements. All four R1-64f development profiles are also pending. X17 confirms
that setting the approval flag alone cannot pass admission. This does not meet
the lane's explicit prerequisite of a valid signed cost receipt.

The future ledger can use the D.1 amendment, candidate v12, current operator
package and X17's rechecked comparator table. It must distinguish measured costs
from projections; preserve unavailable firing for the six v0/S1 profiles,
MQuAKE actual-300-only scope, the empty zsRE baseline caveat and nominal
three-cluster inference; retain the exploratory status of κ/stress/tail findings;
and state the October 9 stop and incomplete-inventory policy.

The existing `scripts/ht4f_claim_ledger.py` still points at earlier inputs/protocol
and historical allocation diagnostics. Once the valid current cost receipt
exists, update or replace that producer to consume the actual admitted package,
validate its source identities and publish a new version without overwriting
historical ledgers. Do not run the old producer as though its pinned inputs were
current. No ledger or signed artifact was changed in this round.
