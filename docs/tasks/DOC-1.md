# DOC-1 — October 2 reviewer-folder refresh

- **Status / agent:** done; Capex, October 1, Round 59.
- **Inputs:** Round 58 reports and decisions DEC-080/081/081a, Friday primer/feedback, Stage-4 limitations and October 9 freeze checklist.
- **Outputs:** updated `docs/presentation/review-results.md` and `final-experiments.md`; corresponding `assets/presentation-materials/review-data/results.md` and `final-experiments.md`; new `CURRENT.md` navigation in that folder; repeatable exporter `aw/reviewer_folder.py`; [refresh record](../../logs/additional_work/DOC-1/round59-final/refresh.json).
- **Changes:** prominent HT-17 finite-range interpretation; AW-B severity to about one-third; three BP seeds versus one completed ePC seed, measured 102.1× paired training cost; reader → DEC-080 Option R learned/random resume → upper-layer queue; v0 deferrals; DEC-081/081a scope; model-scale, halt and population caveats; no-new-fits October 6 and October 9 17:00 EDT cutoff; freeze checklist. Historical blank decision forms are explicitly historical.
- **Verification / done-when:** the exporter reverses link rebasing and checks exact content equality with the repository; 23 local links checked. Both owned exports carry the same evidence snapshot and scope as their repository originals. New code passes lint. No numerical result files changed.
- **Repeat:** `PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m aw.reviewer_folder --output logs/additional_work/DOC-1/<new-snapshot>` from the repo.
- **Cost:** CPU only; zero GPU/model calls. Round-level elapsed time is in the claim record.
- **Deviations / unresolved:** Capstan's original September 27 folder README remains historical and untouched. `CURRENT.md` and both refreshed files direct reviewers to his October 1 primer/feedback. Future GPU results and October 2 feedback still require refreshes; no question for the lead.
