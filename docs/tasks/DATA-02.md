# DATA-02 Realizations, orders, sealed confirmation manifests
status: done
agent: orchestrator   started: 2026-09-10T11:55:00Z   finished: 2026-09-10T12:05:00Z
commit: (uncommitted; lead commits)
inputs used: DATA-01 confirmation source pools (`assets/data/prepared/editing/{zsre,counterfact}_eligible.jsonl`, sha256 e06a8cdb… / 7da6be1d… as in `manifests/dev/pools.json`; dev items excluded, subjects unique), DATA-08; plan §6.6 DATA-02, PDF App. B "Randomization", §4.5 rule 4
outputs: scripts/sample_confirm.py; manifests/confirm/{zsre,counterfact}_r{0,1,2}.json (items verbatim + five orders each + named seeds), manifests/confirm/SHA256SUMS, manifests/confirm/DATA-02.meta.json (metadata only: counts, answer-length strata, subject counts, order hashes)
verify command: /home/derp/cap/venv/bin/python scripts/sample_confirm.py
verify output: zsRE pool 10,420 → 3 realizations × 3,000 (not short), subject-disjoint True; CounterFact pool 20,091 → 3 × 1,000, subject-disjoint True; orders seeds 100–104 per realization; named seeds seed_cap_init = 1000·r + 10·(o−100), seed_router = +1, seed_replay = +2.
done-when check: three subject-disjoint realizations per dataset at the requested sizes: PASS; five orders per realization: PASS; separate named seeds for cap init, router, replay: PASS; SHA256SUMS + metadata-only sidecar: PASS (sidecar has no prompts/answers); §4.5 rule 4 — the loader that refuses to read these before `manifests/frozen.json` exists is DATA-02a (Lane H, other agent; `tests/data/test_confirm_seal.py`): PENDING there, the manifests themselves are written and hashed now.
cost: gpu_seconds=0 wall_seconds=600 peak_mem_mib=0
deviations: the manifest layout ({name, mode: "confirm", dataset, realization, seed, items[...]}) follows the DATA-02a interface spec in ongoing2/3 with the orders and named seeds embedded in the realization file (one file per realization instead of one per order). The partition into realizations uses a dataset-level permutation (seed derived from the dataset name) so disjointness holds by construction; realization seeds 0/1/2 order the blocks.
unresolved: none (S4-01 records the SHA256SUMS in frozen.json `dataset_ids`).
questions for lead: none
