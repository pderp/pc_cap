# MMK / Nelson entropy feedback review

- Status: done (analysis and recommendations; proposed empirical additions not executed).
- Agent: Capex.
- Inputs: complete `/home/derp/cap/MMK.txt` and 42-page `/home/derp/cap/NelsonUniqueUnivEntropy2026Sep27.pdf`; Friday primer; Capstan response at `07db745` and subsequently written `talk-text-B-C-D.md`; current queue through item 147 / DEC-080; reader and AW-L specifications; existing κ answer-loss implementation.
- Outputs: `docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md`; `aw/entropy_feedback_checks.py`; input hashes, full text extraction, and `equation-checks.json` in `logs/literature/nelson-entropy-20261001/`. Reference page renders are outside the repo, in `assets/literature/nelson-entropy-20261001/`.
- Verify command: `PYTHONDONTWRITEBYTECODE=1 /home/derp/cap/venv/bin/python aw/entropy_feedback_checks.py`; `/home/derp/cap/venv/bin/ruff check aw/entropy_feedback_checks.py`.
- Verify output: assertions passed; equation 126's printed positive-κ limit disagrees with the exact α=d=κ=a=1 substitution (derived 1, printed 2); κ=0 control and constructed inverse identities pass; Ruff passed. Empirical prototype fits were not independently rerun.
- Done-when check: both requested inputs fully ingested; current remaining experiments reviewed; recommendations, scientific limits, specific differences from Capstan, and author questions recorded.
- Cost: CPU-only reading and scalar arithmetic; zero GPU seconds; no model loading or new training. Interactive review wall time not measured.
- Deviations: no existing file edits; no new empirical lane claimed; no commits.
- Unresolved: author clarification of equation 126; the intended modeled variable/objective; approval and scope of the proposed exploratory tail analysis. These do not block the existing GPU queue.
- Questions for lead: discussion prompts and proposed priorities are in the response; no permission question is pending from this review.
