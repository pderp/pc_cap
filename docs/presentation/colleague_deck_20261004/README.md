# Active Inference in the Extremes — colleague talk

Prepared for charlie by Capex, 4 October 2026. This is a **35–40 minute presentation**
for colleagues who have not followed the project, built from Capstan's short deck
and the completed experimental record. The planned clock is **39:25**, including
a 20-second reaction pause and a 45-second written-feedback pause. Open discussion
is additional; allow a 50–60 minute meeting if possible. Timing is a rehearsal
target, not a measured delivery time.

## Present from these files

- [Presentation PDF — 25 main slides and 5 backups](../../../../assets/presentation-materials/colleague_deck_20261004/active-inference-in-the-extremes-colleague-talk-20261004.pdf).
- [Offline browser presentation](../../../../assets/presentation-materials/colleague_deck_20261004/present.html):
  arrow keys / space to advance, **F** for fullscreen, **N** to show speaker notes,
  and a resettable elapsed-time clock. All images are embedded; no network is needed.
- [Speaker notes PDF](../../../../assets/presentation-materials/colleague_deck_20261004/speaker-notes.pdf)
  and [editable timed script](speaker-notes.md).
- [Feedback guide and proposed 15-minute compression](feedback-and-short-talk.md).
- [Sources and example selection](sources-and-examples.md).

The PDF and browser file are individually portable. Speaker notes are also stored
as PDF annotations. The canonical short deck remains unchanged. This version
does not change experimental populations, scoring, results or future commitments.

## The route through the talk

1. Slides 1–5: three themes, an active-inference loop, the frozen transformer and
   adaptive cap, and the distinct tests an edit must pass.
2. Slides 6–10: recorded prompts and answers, failure and preservation examples,
   experimental design, and retained paraphrase results.
3. Slides 11–15: probability harm from first principles, frequency versus severity,
   finite-range tail evidence, and the measured probability-mixture intervention.
4. Slides 16–21: predictive-coding credit, the repaired energy, depth and transfer
   comparisons, completed reader-training results and the upper-layer experiment.
5. Slides 22–25: the proposed active-inference extension, the remaining schedule,
   takeaways, and specific colleague feedback.
6. Backups 26–30: MQuAKE examples, risk definitions, PC controls, the fourth subject
   draw, and sources.

For a **36:05** version, move slides 17 and 21 to questions and give slide 25
80 seconds instead of 120. Keep the active-inference framing, one worked example,
the main PC evidence and distributional harm. Rehearse before making finer cuts.

## What's added to the short deck

The new deck includes Capstan's completed support-information examples: a zsRE
memory retrieved after 1,000 edits; a CounterFact success and a failure to fire on
a paraphrase; a nearby-fact comparison; and an unchanged poor base output. MQuAKE
success and failure are in backup. These are selected illustrations, with full
identities and raw-source checks, not a new statistical sample.

It also incorporates the completed three-seed PC-reader result and the upper-layer
2×2 result. The older 50M PC-v0 experiments, the 124M main experiment, fixed-v5
credit transfer, and reader-training comparisons retain their distinct populations.
Proposed active-inference and coupled-objective work is visibly labeled.

## Edit or reproduce

The narrative is in [aw/colleague_deck_content.py](../../../aw/colleague_deck_content.py).
The renderer and saved-result plotting code are in
[aw/colleague_deck.py](../../../aw/colleague_deck.py).
`slides.json` is a readable content export; edit the Python narrative to rebuild it.

From `pc_cap`, use the already installed local reporting packages:

```bash
JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 \
MPLCONFIGDIR=/home/derp/cap/assets/presentation-materials/.matplotlib \
../venv/bin/python -m aw.colleague_deck
```

This regenerates only the colleague deck's own generated files and logs. An
alternative resource directory can be supplied with `--out` under
`assets/presentation-materials`; the documentation/log paths still refer to this
colleague edition. It imports the project NumPy and then the existing reporting
environment for Matplotlib/ReportLab. No installation, model execution, GPU use or
tail fitting occurs.

The build verifies Capstan's source hashes and selected checkpoint generations,
reads current saved numerical results, checks each text box for horizontal and vertical overflow,
and records plotted values and hashes under
`logs/presentation/colleague_deck_20261004/`. The task record documents the final
visual and extraction checks.
