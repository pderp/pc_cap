# KP-1 — exact restoration feasibility

Status: complete, **NO-GO for an exact continuation of the original κ drift memories**. Agent: Capex, Round 58. CPU only; no base construction, inference, acquisition, training or GPU calls.

The nine averaged readers exist. All **27 corresponding end-of-stream snapshots** (nine readers × three datasets) also exist and deserialize with the original file and state hashes. Reconstructed NPZ parameter trees match both their recorded reader hashes and each checkpoint's parameter hash. Thus the stream checkpoints are usable artifacts; it would be wrong to say no pilot memory was saved anywhere.

However, `scripts/r1_54_drift_assay.py` independently creates a fresh cap and teaches its 100 items before scoring the legacy drift windows. It writes NLL arrays and summaries but **neither saves that memory nor records its state hash**. The exact drift-memory identity cannot be compared with the separately generated stream checkpoints. The saved gate/calibration settings and common acquisition recipe make equivalence plausible, but they are not a measurement of identical memory. KP-1's instruction is to stop if exact restoration is unavailable; therefore no model command is issued or launched.

## Artifacts and configuration

[Inventory](../../logs/additional_work/KP-1/final/inventory.json) lists every reader path, full file SHA256, parameter-tree hash, snapshot path/SHA256, verified state hash, 100-item stream membership, calibration and semantic configuration, and source-file hashes. Readers are under `assets/runs/pc_cap/R1/pilot/<run>/theta_avg150-300.npz`; stream snapshots under `assets/runs/R1/streams_revision/<run>_stepavg_rare1_null0.5[@dataset]/learner_end.ckpt`. The dataset suffix is absent for zsRE. Run names are `r1_50_stream_sel6_text_s{0,1,2}`, `ht3_kappa02_s{0,1,2}` and `ht3_kappa05_s{0,1,2}`.

The preserved settings include null threshold .5, rare overlap 1, rare document-frequency ceiling 2, lexical/query/pairwise nulls, cosine reader, full three-site writes, five delta steps at .1, no fast steps, acquisition threshold .1, A=.3, and bank scales 70.7018738/106.5766659/425.5740662. The base identity is `c4ac3fb867dad146dbddfcd4af0b9b110d8de3bce41127bb1fc11b1e533bc082`. The full stop-token list is embedded in checkpoint configuration. These values are read from the snapshots, not re-selected calibration.

The old drift path uses `load_dev_items(dataset,100,seed=21)` and the corresponding development manifest, excluding Stage-0 IDs. The pilot manifest specifies 32×127=4,064 scored positions, null .5, rare overlap 1. Drift summaries lack embedded item/token IDs and memory identities; ordered stream IDs in the inventory belong to the **stream snapshots**, not an invented drift receipt. Current manifest hashes cannot retroactively supply missing launch-time identities.

## Owner decision if this remains attractive

A readout of the verified **stream** checkpoints would be a separately labeled development experiment, not an exact continuation of the old drift assay. It needs an explicit scope decision and an adapter preserving the checkpoint's semantic configuration. Reacquiring the old memory would also be a new execution; this lane does neither. `aw.pc_harm_readout`'s v0 CLI is not a drop-in command for these learned-reader snapshots.

At the supplied 25-minute-per-cell estimate, nine readers cost **3.75 h per dataset**, **7.5 h for zsRE+CounterFact (18 cells)**, or **11.25 h for all three (27 cells)**, before startup, failed attempts or validation overhead. This is a projection from another readout, not a measured pilot cost. A 245,237-position ordinary-text assay would align the readout population with Stage 4, but the 100-edit development memories/readers differ from Stage 4's selected v5 and confirmatory 300/1,000-edit populations; it cannot replace a Stage-4 result or its replication denominator.

CPU reproducer (fresh log directory):

```sh
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
  ../venv/bin/python -m aw.kappa_restore_inventory --output logs/additional_work/KP-1-NEW
```

Verification: nine parameter trees and 27 checkpoint hashes/state hashes pass. Done-when: exact-restoration decision, artifact inventory, cost and population boundary delivered. Unresolved: no original drift-memory witness exists in the inspected artifacts; a changed-population readout requires an owner decision. No GPU lease or execution command is prepared under the false premise that equivalence was proved.
