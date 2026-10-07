# PRES-slide-10-training-baselines

- Status: done, 2026-10-05.
- Agent: Capex.
- Inputs: user request; slide 10 of `assets/presentation-materials/deck_v4/long_deck_v1.md`; final triplet recipes; selected v5 training manifest/summary; cap implementations and endpoint scoring; Stage-4 reports; saved support examples; U03 continuation memo.
- Outputs: `assets/support-information/slide-10-stable-v0-training-and-baselines.md` (relative to `/home/derp/cap`); `logs/presentation/slide-10-training-baselines-20261005/verification.json`; this task record. These are the only files added for this request.
- Verify command: inline Python standard-library checks of linked files, final recipe identities and paired payloads, published behavior rows, selected training summary and saved example outputs; `git diff --check` in both repositories.
- Verify output: 29 local links resolve; 135 triplet recipes share the same original base; all 45 paired dataset/realization/order groups share payloads across the three conditions; each condition has one reusable parameter identity; dataset radii agree across cells; aggregate table and both saved examples agree with sources. Metadata checks and source hashes are retained in the verification JSON.
- Done-when check: explanation distinguishes base pretraining, reusable reader training, online correction acquisition and read-only prediction; explains stable versus live keys, separate memories, original-prompt versus paraphrase results, no-cap references, S1 exceptions and separate PC supplements.
- Cost: CPU metadata/text reads only; model calls 0; GPU seconds 0. No new experiments.
- Deviations: requested support document is outside `pc_cap`, as explicitly directed by the user. No task-board row was invented for this direct presentation request. The explanation qualifies misleading shorthand in the existing support README without changing that file or the presentation.
- Unresolved: none for this request. Other pre-existing working-tree changes belong to earlier work or Capstan and were left untouched. No commit performed.
- Questions for lead: none.
