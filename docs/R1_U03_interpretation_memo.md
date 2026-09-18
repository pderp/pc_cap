# U03 — what the retained S1 comparisons can establish

**For the September 19 protocol-admission review; September 18, 2026.** Recommendation: retain the certified checkpoints and state the budget qualification below. This memo supplies interpretation, not a new certification, signature or change to candidate v14.

**Registration.** DEC-040 requested both literal self-distillation and informative OpenWebText language-model continuation, with a forward-token budget refreshed against the then-current reader v1, followed by common editing comparisons. Literal self-distillation is a numerical negative control: the identical teacher/student objective has zero gradient in exact arithmetic. DEC-047 accepted the informative continuation at learning rate `1e-8` after it passed the registered cap-disabled fidelity gate; the earlier `1e-6` failure remains on record. Neither decision certifies equality to a later reader's compute.

**Retained evidence.** The following bases remain the S1 treatments for zsRE/CounterFact under D.4. Both passed on the original 8,192-position fidelity population; current checkpoint, adapter and calibration identities were checked in the [U03 dossier](../logs/r1_round36/U03-continuation-evidence.json).

| Treatment / run | Forward-input tokens | Updates | Mean KL | Signed ΔNLL |
|---|---:|---:|---:|---:|
| S1_LM / `r1_24_lm_v3_lr1e-8` | 771,581 | 6,028 | 0.000473608 | −0.00885965 |
| S1_literal / `r1_24_literal_v3b` | 771,580 | 3,014 | 0.0000293325 | −0.0000617914 |

KL ≤0.001 and NLL increase ≤0.01 nats are the unchanged continued-base gate. This certification is distinct from DEC-064's full-validation **cap** benchmarks. D.4 prospectively omits MQuAKE S1 runs; zero calibrated radius does not establish equality of two different bases.

**Accounting difference.** The [v1 reconciliation](../manifests/revision_v1/r1_24_budget_reconciliation_v1.json) contains 458,002 outer-training forward tokens plus 313,579 feature-bank tokens; 458,002 reverse-token positions are separate. Literal continuation uses two forwards per input and leaves one unmatched token. The selected v5 training summary instead reports **833,228 learning tokens** for its own lineage, with different accounting. The raw difference, 61,647 tokens, is not a verified compute deficit or a justified top-up target. Pass types, bank work, reverse work and the selected checkpoint average must be reconciled before claiming an exact v5 budget match. Even equal forward-token counts alone would not prove equal FLOPs or total search cost.

**Bounded interpretation.** Report S1−S0 as the effect of these specified historical continuations, and R0−S1 as the reader's difference from these particular certified controls. Their contrasts remain informative about those treatments. They cannot exclude all informative continuation at v5-matched compute, or establish a general compute-efficiency advantage. A literal-control null cannot exclude informative training. Preserve paired populations, registered margins and uncertainty; no development point estimate closes the confirmatory inference.

**Exact proposed U03 sentence:** “U03 retains the DEC-047-certified S1_LM checkpoint and the fidelity-valid S1_literal checkpoint as historical continuation controls under DEC-040; their forward-token budgets were reconciled to reader v1, and their contrasts with primary v5 are interpreted as comparisons with these specified controls, not as exact-v5-compute-matched tests or as exclusion of all continued-base explanations.”

**No new run recommended for this sitting.** Logged training-update timers sum to 144.54 seconds for LM and 85.56 seconds for literal continuation ([timing evidence](../logs/r1_round37/U03-timing-evidence.json)); they exclude startup, checkpointing, fidelity and editing evaluation. Training at a similar token count may be cheap, but a decisive replacement first needs a verified v5 budget, fresh fidelity certification and calibration, and versioned checkpoint/recipe/admission bindings. Its complete cost is unmeasured. Appending the raw token difference would not resolve the question. Retain this qualification now; any later matched treatment is a separately reviewed amendment.
