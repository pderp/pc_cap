# From the July abstract to the testbed: implemented, measured, proposed (HT-14)

2026-09-27, Capstan (Claude, orchestrator); rows on Nelson 2026 added 2026-10-01 (lead's go on items B–D of the reviewer-feedback response). For slides 2 and 11 of deck v3 and the claim ledger. Checked against
`docs/decisions.md` (DEC-001 … DEC-074b), the Stage-4 protocol (D.1–D.5), the triplet and comparator reports, and
the PC-v0 specification. Status words: **implemented** = a working component exists in the code that ran;
**measured** = a result exists on a named population; **proposed** = in the abstract or the programme, not built.
Source: *Coupled Active Inference on a Frozen Transformer Prior: A Risk-Aware Residual Agent for Non-Equilibrium
Regimes* (Derr & Iklé, July 2026) and the satellite's captured objectives.

## 1. The abstract's ideas, one by one

| abstract idea | status | where / what | what it is not |
|---|---|---|---|
| A frozen pretrained transformer as generative prior | implemented, measured | GPT-2 (124M) frozen throughout R1; the original ePC 50M base for the v0 line (regenerated checkpoint `ea4c561d…`) | not a frontier-scale base; the abstract's "frontier substrate" is proposed |
| A small adaptive agent learning only the residual R = F* − F0 | implemented, measured | the cap: v0 (C1, three write banks, adjoint or error credit) and the v1 learned reader with per-record deltas; ≈ 10⁴–10⁵ parameters against 124M | it stores per-fact corrections retrieved by a gate; it is not a general residual network trained on the whole stream |
| "Sparse columnar residual network" | partly implemented | sparse per-record memory with bank-wise writes (v0); the v1 reader plus controller | no column formation, no growth policy, no core–periphery scales |
| Prior-side interface (blanket to the transformer) | implemented | read taps after blocks 4, 8, 12; writes at the same sites; AW-L defined the read/write sets explicitly (`aw/interface.py`) | not shown to be a Markov blanket in the formal sense; "κ-porous" is a label, not a measured coupling |
| Environment-side interface | implemented as the edit stream and the gate's null decision | zsRE / CounterFact / MQuAKE streams; the gate decides to fire or not per query | no environment model, no action beyond "apply or withhold a correction" |
| Prediction error as the learning signal | implemented, measured | v0: adjoint or ePC site-error credit for the writes; v1: per-position delta acquisition (adjoint); corrected ePC credit under test now (PC-v0, DEC-074) | the reader itself is BP-trained; error-optimization PC is autodiff through the graph, not a local rule |
| Coupled, κ-deformed free energy | measured as a loss-level pilot only | the κ pilot (DEC-054): coupled logarithm on the reader's answer surprisal, κ ∈ {0.2, 0.5}, clipped control; null under the pre-registered rule | not the coupled free energy of Nelson et al., no coupled expectation, no changed inference distribution; of the three components of Nelson 2026's calibrated entropy (coupled logarithm, independent-equals average, 1/α root) the pilot implemented the first only, with no informational-scale calibration |
| Informational coupled free energy k T (ln_κ Z − 1/(1+κ)) as the agent's training objective (Nelson 2026 eq. 56) | proposed | — | the candidate matching implementation of the abstract's coupled objective; first joint experiment to plan with the coupled-AI group after 15 Oct |
| κ-porous interfaces as pseudo-Markov blankets (Nelson 2026: zero agent–environment cross-terms, nonlinear dependence allowed across the boundary) | proposed | the two software interfaces exist (`aw/interface.py`; AW-L varies them) | no conditional-independence or cross-term measurement; the label is still a label |
| Complexity class (κ, α) and informational scale σ of the harm distribution (Nelson 2026 Def. 1, Thm 4) | prototype measurement, pending HT-17 | generalized-Pareto = coupled-exponential fits on the saved 245,237-position vectors: learned reader exponential class (κ̂ ≈ 0.05, σ̂ 1.5–1.8 nats), v0 caps power-law class (κ̂ ≈ 0.8, σ̂ 0.6), random reader and the 1-nat mixture compact support (`docs/friday-10.02-review/feedback-MMK-nelson-entropy.md` §3) | a class within the fitted family, not an asymptote (fits lighten above 1–2 nats); zero mass reported as a firing rate, not modelled; σ's temperature reading is Nelson's, not a measured thermodynamic quantity |
| Interference as a measurable geometric invariant; one κ governing separation, forgetting and robustness | proposed | the pilot shows bounding surprisal shifts the porosity/interference trade-off rather than improving it | the one-κ conjecture is untested; no holonomy or forgetting geometry was computed |
| Expected-free-energy policy selection with a risk term | proposed | routing exists (gate + selection) but is a fixed rule, not a policy chosen by expected free energy | no preferences model, no risk term |
| Precision weighting as risk sensitivity | proposed | ePC has per-site error scaling in the solver; not used as a policy or audit weighting | — |
| Epistemic value; uncertainty-triggered audits | proposed | the investigator-selected probes (locality, near-miss, revision, stress panel) are audits chosen by us | not autonomous information seeking |
| Learning from failure ("the regime that threatens the agent carries what it can learn") | measured in one sense | harm is concentrated in 0.2–0.4 % of ordinary-text positions (HT-7, HT-13/15); the tail exists and is where the cap's errors live | no agent uses that signal; nothing is learned from the tail yet |
| Coupled free energy keeps precision finite on tail events; the agent persists in the extremes | proposed | — | no evidence either way |
| Nested Markov blankets (agent, column, core–periphery) | proposed | — | — |
| Staged, gate-checked build plan | implemented as process | the DEC record, freeze, sealed queue, receipts, audits | process, not a scientific result |

## 2. The satellite's objectives against our evidence

| objective (captured page) | our evidence | limit |
|---|---|---|
| active inference and nonlinear dependence | none | — |
| extreme fluctuations | measured: survival curves, exceedance, maxima, ES99+, half-mass concentration across 270 cells (HT-13/15) | empirical, finite population, own-cap-off reference; no tail class, no independence |
| generalized / coupled free energy | pilot only (κ, loss level) | see above |
| coupled Markov blankets | proposed | — |
| socioeconomic environments | none | — |

## 3. What the two PC experiments add (pending)

| experiment | what it tests | what it cannot show |
|---|---|---|
| corrected SE-E vs SE-A on v0 (running, 60 cells) | whether finite-iteration error-optimization credit, with the SD-24 fix, acquires and retains edits at what cost, against adjoint credit on the same base and cap | reader training by PC; local or biologically plausible learning; the coupled objective |
| fixed-v5 acquisition credit (next) | whether that credit transfers to the reader that works, all else fixed | same |

## 4. One-paragraph version for slide 2

We built the frozen prior, the small residual agent between two interfaces, prediction error as its learning
signal, and the audit machinery around it, and we measured editing, retention, locality and the distribution of
unintended harm on three datasets across three populations. We ran a loss-level κ pilot, which was null under its
pre-registered rule. Expected-free-energy policy choice, the coupled free energy itself, precision as risk
sensitivity, epistemic audits and nested blankets remain proposed. The two predictive-coding experiments running
this week test the credit rule, which is the one piece of the active-inference loop this testbed can test now.
