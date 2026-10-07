# Support-information field explanations

- **Status:** complete; direct request from charlie, October 5, 2026.
- **Agent:** Capex.
- **Inputs:** both saved example JSON files; their three hash-bound sealed
  payloads; original zsRE MEND train, CounterFact and MQuAKE-CF downloads;
  `manifests/datasets.json`; the actual loader/preparation mappings.
- **Outputs:** expanded `assets/support-information/Capstan-README.md`, a
  cross-reference in `README-random-sample.md`, and a dataset-specific explanation
  in each of the six `examples-*.md` pages. `aw/support_examples.py` carries the
  same wording so regeneration preserves it. The three first-set page titles
  also pick up the generator's existing “the first 30 edits” wording.
- **Content:** distinguishes supplied labels from observed base/cap answers;
  explains original answer, requested target and alternative prompt; traces
  each dataset's source fields; includes three actual examples. It explicitly
  states that the shown zsRE stream teaches `answers[0]`, not `alt`, while
  CounterFact/MQuAKE use their supplied counterfactual replacements. Dataset
  labels are not claims that GPT-2 knew the original fact or that the labels
  were freshly fact-checked. Source paraphrase semantics are not certified.
- **Verification:** 180 displayed items checked against raw source records,
  with prompt, target, original-answer label and first paraphrase matching in
  every case. Raw downloads match the manifest hashes. Both example JSON files
  are unchanged. Everything from each page's counts table onward is unchanged,
  including all model outputs and scores. Existing README prose is retained.
  `../venv/bin/ruff check aw/support_examples.py` and `git diff --check` pass.
- **Evidence:** [verification.json](../../logs/presentation/support-field-explanations-20261005/verification.json)
  records input/output hashes and the per-item checks. The
  [refreshed reviewer-folder manifest](../../logs/additional_work/reviewer-folder/support-fields-20261005/refresh.json)
  reflects the new linked README bytes; the old manifest remains historical.
- **Execution:** rendered directly from saved JSON with `render_dataset` and
  the README templates; did not invoke the example generator's model-decoding
  CLI. No new model call, GPU use, experimental result or scientific decision.
- **Done-when:** plain-language definitions and dataset origins available both
  at the common entry point and beside every example collection.
- **Deviations:** documentation is in assets as explicitly requested, with
  generator and verification records in pc_cap.
- **Unresolved / questions for lead:** none. Uncommitted; no staging or push.
- **Other lanes:** FIN-2 stays scheduled for October 6; this request does not
  start its dry run or the rehearsal-dependent PRES-10 lane.
