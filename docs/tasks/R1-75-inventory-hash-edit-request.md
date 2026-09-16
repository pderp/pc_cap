# R1-75 inventory helper hash correction

Status: tested in memory; not applied. The new-files-only rule applies even to files created this turn.

Target: scripts/r1_75_development_matrix.py. Exact patch: R1-75-inventory-hash.patch. Use endpoints.row_hash for the drift definition, matching the driver, instead of analysis.digest, which serializes JSON with different whitespace. No scientific values change. The independent analysis correctly refused both cells until this metadata encoding matched. With the correction in memory, both cells verify; CounterFact LS49/50 versus36/50 and near-miss100/100 versus63/100, zsRE LS50/50, and both drift vectors reproduce.

Permission requested for these two lines. No source-tree changes, models, GPU, commits or existing result edits.
