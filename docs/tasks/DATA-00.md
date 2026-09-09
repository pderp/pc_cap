# DATA-00 Fetch and hash public assets into assets/
status: done
agent: orchestrator   started: 2026-09-09T22:40:00Z   finished: 2026-09-09T19:12:03Z
commit: (this commit)
inputs used: plan §6.2 DATA-00 list 1-7; PA-9; DEC-004 paths
outputs: assets/models/gpt2 (snapshot 607a30d7…), assets/data/raw/{zsre,counterfact,wikitext103,ud_ewt}, assets/third_party/GRACE, manifests/datasets.json, data/raw/SHA256SUMS, scripts/fetch_assets.py, src/pccap/data/fetch.py
verify command: /home/derp/cap/venv/bin/python -m pccap.data.fetch --verify
verify output: verified 15/15 files
done-when check:
- every listed asset present with hash or unavailable with reason: PASS — gpt2 present (5 files hashed); zsre present (eval+train); counterfact present; wikitext103 present (HF dataset revision b08601e04326c79dfdd32c625aee602d5f8b7b1e… recorded, 4 parquet files); ud_ewt present (latest release tag recorded in datasets.json); GRACE cloned at f674183f… with its licence recorded; openwebtext deferred to REG-00.
- WikiText token counts recorded (GPT-2 tokenizer): train 117,920,140; validation 247,289; test 283,287 tokens. SD-3 shortfall is exact: validation = 0.247M tokens vs the PDF's 10^6 (PA-5: whole validation split used, no repetition).
cost: gpu_seconds=0 wall_seconds=1500 peak_mem_mib=0
deviations: assets stored under /home/derp/cap/assets (DEC-004) with pc_cap/data/raw/SHA256SUMS recording hashes; UD-EWT release tag chosen by numeric max over the repository's rX.Y tags (the repo has no GitHub "releases"). Document counts for WikiText use the " = Title = " heading heuristic and are provisional until DATA-04 defines documents.
unresolved: none
questions for lead: none
