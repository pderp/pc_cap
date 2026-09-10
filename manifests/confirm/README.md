# Sealed confirmation realizations

DATA-02 prepared one JSON manifest per dataset and realization: zsRE and CounterFact,
each with realizations 0, 1, and 2. These files contain confirmation items. The PDF
Appendix A rules 3–4 require development/confirmation separation and a committed freeze
before test access. Do not inspect item payloads during development.

The metadata files are safe for planning:

- `SHA256SUMS` records each realization's SHA-256 as `<hash>  <file_name>`.
- `DATA-02.meta.json` records source-pool and aggregate sampling metadata.
- `<dataset>_r<realization>.meta.json` records only `file`, `sha256`, `n_items`,
  `subjects` (a count), `answer_length_strata` (token-count frequencies), and `orders`
  (the existing 16-character SHA-256 prefixes of JSON-serialized ID permutations).

The six per-file sidecars were materialized from the existing DATA-02 aggregate metadata,
without opening or rehashing any realization payload. Their recorded hashes agree with
both `SHA256SUMS` and the draft freeze's per-file bindings; their strata sum to their item
counts. This checks metadata consistency, not the payload bytes. Provenance and output
hashes are in `results/data02a/metadata_sidecars.json`.

## Evaluation loader

The intended entry point is:

```python
from pccap.data.confirm import load

manifest = load(path_to_realization)
```

**Integration is pending permission to replace the existing `confirm.py` placeholder.**
The implementation is prepared in `pccap.data.confirmation_integrity`; the exact public
API patch is `docs/tasks/DATA-02a-confirm-api.patch`. Do not route S4 around the public API.

The loader checks these in order:

1. The specified freeze exists and passes `manifest_frozen` schema validation.
2. The exact realization filename has one unambiguous binding in
   `frozen["dataset_ids"][dataset][file_name]`.
3. The colocated `SHA256SUMS` has that filename and the same hash.
4. The file's byte digest matches both bindings.
5. The verified bytes decode to the DATA-02 layout, with matching dataset, realization
   and order seeds, unique item IDs, complete order permutations, and named seeds.

Only then does it return the dictionary. The bytes are read once for hashing and parsing.
Missing freeze, malformed bindings, and index mismatches fail before opening a payload.
The freeze producer and lead still own the decision and commit; schema validation alone
does not establish that approval.

## Preparing a new seal

`scripts/seal_confirm.py --directory PATH` validates realization files, writes one
metadata sidecar per file, and writes `SHA256SUMS` last. It uses the same sidecar fields
and order-hash serialization as DATA-02 and preserves `DATA-02.meta.json`.

This preparation command reads item contents. During this task it was run only on
synthetic fixtures outside the repository. Existing outputs are refused by default,
before payload access. `--replace` permits overwriting sidecars and the digest index;
the current user protocol requires explicit permission before exercising that option
against any existing files. Coordinate actual data access with the freeze owner.

CPU verification uses `tests/data/test_confirm_seal.py` and
`tests/test_package_layout.py`, with a copy of `manifests/frozen.draft.json` and
synthetic payloads under a fresh `assets/tmp/` directory. Never use the real freeze or
real payloads as test fixtures.
