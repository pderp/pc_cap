# Slide 4 — Correct a fact, then test its boundaries

**Draft speaker text for charlie's review; implemented design.**

**On screen:** supplied edit → bounded memory update → own prompt / paraphrase /
unrelated text. Separate labels for frozen base weights, fixed trained reader
weights and changing per-record memory. Claim footer: `R1-design`, `R1-controls`,
`AI-testbed`. Renderable source: `diagram-specs.json`, slide `04`.

## Speaker text

“The unit of work is a supplied factual correction. We ask whether the system
can give the taught answer immediately, whether it retains the answer after many
more edits, and whether that correction transfers to a differently worded
question. Immediate editing success is ES. End-of-stream retention on the
original prompt is RET-ES; retention on paraphrases is RET-GS. These are different
questions: memorizing a prompt is easier than using a correction appropriately
when the wording changes.” [`R1-design`]

“The main R1 condition has three distinct kinds of state. The GPT-2 base stays
fixed. A reader, trained earlier with backpropagation and then fixed, decides
whether a stored correction applies. The edit stream changes the cap's memory
records and bounded residual writes. This completed study evaluates a feedforward
reader; it does not contain the forthcoming predictive-coding credit treatment.”
[`AI-testbed`, `R1-controls`, `PC-SD24`]

“We also test where an edit should not apply. Locality scores compare bounded
answer text on fifty unrelated prompts. Near-miss probes ask about similar cases
that should remain unaffected. Ordinary-text assays examine changes in token
probabilities even when the generated answer text stays the same. Passing one
of these tests does not imply passing the others.” [`R1-design`, `R1-specificity`, `HT-readout`]

“The controls help us interpret what the whole package contributes: a random
reader, a stable v0 cap, matched-update and live v0 variants, and continued-base
controls. S1 continues the base before using a stable cap; it is not ordinary
fine-tuning on our factual edit stream, nor an exact compute match to the v5
reader. The comparisons do not separately identify every architectural ingredient.”
[`R1-controls`]

“For each condition and dataset, we have three realizations with five orders
within each. The five orders reuse subjects; they are not five more independent
populations. zsRE and CounterFact reach a thousand edits. MQuAKE ends at three
hundred and is descriptive there. The PC-v0 replication uses its specified
regenerated ePC base and exposed historical streams, so we also keep it distinct
from this GPT-2 reader study.” [`R1-design`, `PC-v0`]

## Diagram and source notes

Use an edit / state / evaluation diagram. Put the shared base, fixed reader and
adaptive memory labels inside the state panel. Label exact-text locality and
probability-level drift separately. Sources: [triplet report](../../R1_stage4_report_triplet.md),
[270-cell comparator report](../../R1_stage4_report_comparators.md),
[PC-v0 specification](../../additional_work/PC-v0.md),
[claim ledger](../../talk_claim_ledger_v7.md). No real fact or answer needs to be
displayed; “a supplied correction” is enough for this explanation.
