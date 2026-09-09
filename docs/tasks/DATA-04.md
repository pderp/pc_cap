# DATA-04 LM, probe and property sets with inventory
status: done
agent: orchestrator   started: 2026-09-10T03:50:00Z   finished: 2026-09-09T23:27:42Z
commit: (uncommitted; lead commits)
inputs used: assets/data/raw/wikitext103 (parquet, HF rev b08601e0…), assets/data/raw/ud_ewt (r2.18), GPT-2 tokenizer; PDF S1, D.2, D.3, D.8, E.4; SD-1, SD-3
outputs: src/pccap/data/lm_sets.py, manifests/dev/lm_sets.json (document ids, seeds, counts, hashes), assets/data/prepared/lm/{H_tokens,drift_tokens,P2_sequences,P2_positions,P3_sequences,POS_*}.npy
verify command: /home/derp/cap/venv/bin/python -m pccap.data.lm_sets --audit
verify output: hashes verified; H = 2,000,000 tokens by document from train (seed 11); drift = whole validation split 247,289 tokens (SD-3 shortfall vs 10^6 logged); P2 = 256 x 128-token sequences x 16 positions = 4,096 positions (seed 12); P3 = 1,000 x 128-token sequences (seed 13); POS train 204,578 labelled first sub-tokens (>= 20,000), dev meets >= 5,000; H/P2/P3 document-disjoint (0 overlaps); train/validation disjoint by split; E.4 domains recorded unsupported.
done-when check: WikiText tokenized once with counts (train 117,920,140 tokens, 29,868 documents by the level-1 heading rule): PASS; H, drift, P2, P3, POS built as specified with document-level deduplication and disjointness: PASS; E.4 natural-language domains unsupported with the grammar substitution stated: PASS
cost: gpu_seconds=0 wall_seconds=1200 peak_mem_mib=0
deviations: document boundary = WikiText level-1 heading line (documented heuristic; 29,868 train documents vs the corpus's nominal 28,475 articles because some single-'=' lines are not article titles); POS windows pack whole sentences into 128-token windows.
unresolved: none
questions for lead: none
