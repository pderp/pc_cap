# Production bundle assembler — R1-63j

This supersedes the missing-producer statement in the round-28 interface. The
producer is now `scripts/r1_63j_production_bundle.py`. It prepares reviewable
metadata and never publishes, signs, launches, draws or opens a cell payload.

Supply current D9 inputs with approved protocol, clearance, RNG, draw, endpoint,
seal, typed cost, schedule and all 18 gate receipts. The assembler checks their
identities and receipt chain, then reads the seal's payload-hash inventory and
independent analysis population. Actual sealed cell payloads and reservation
contents remain opaque. Unsigned real inputs return missing prerequisites before
resource access. A freeze authorization is intentionally excluded at this stage:
the later operator request binds the concrete staged bundle for the lead's act.

Generate the runtime catalog in a new directory using `template_catalog(output)`
from the same module in a CPU process. Its 27 entries preserve the known adapter,
base, reader, calibration, budget and tokenizer identities from current recipe
sources. The historical primary CounterFact source receives an explicit metadata
conversion to the current integrity driver. Every template binds its old source;
no historical result is relabelled as a current run. A development code digest and
a sealed code digest cover different file inventories, so they are explicitly
distinguished. The final assembler checks calibration v3 and primary v5 weights.

To inspect actual unsigned prerequisites:

```bash
PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= \
  ../venv/bin/python -m scripts.r1_63j_production_bundle \
  --inputs docs/tasks/R1-D9-inputs-v8.json \
  --report logs/r1_round29/assembler-next-inspection.json
```

Once prerequisites exist, add `--templates <catalog.json>` and
`--staging docs/tasks/<new-staging-directory>` to prepare the complete proposal.
Use the operator session's current inputs after seal, not the unsigned v8 inputs.

The proposal contains 360 recipes, or 405 if the extension is explicitly admitted,
plus four files: schema-2 executable protocol, frozen manifest proposal, final
matrix, and queue bindings. Recipe paths and all future references are final
paths before hashing. Recipe contract hashes exclude only the freeze reference;
this breaks the freeze/recipe hash cycle without omitting scientific settings.
The stored per-cell wall ceiling is unchanged; the queue applies 1.15 once for
two workers. The declared process budget and typed cost receipt stay bound.

The assembler validates the proposed final namespace through the actual queue
and sealed backend using an in-memory metadata overlay. Source/hash, gate,
cadence, whole-inventory, independent-population and destination checks remain
active. This validation runs in one CPU process and creates no final paths.
Tests use existing synthetic D9 rehearsal receipts; those artifacts are not
production population evidence.

Staged executable documents describe the bytes that would become effective after
publication, including the backend's required admission fields. They do not
constitute a new lead signature. Only the existing operator's exact signed
`freeze` request may copy those bytes to final paths; the canonical
`manifests/revision_v1/frozen_stage4.json` is written last. The assembler itself
never performs that copy. New destinations are required; failed staging can leave
partial proposals and must be retried in a new directory.

Actual full-validation costs, other scientific gates and population operations
remain prerequisites. Delivery of this producer removes an implementation gap;
it does not make the package ready for signature or launch.
