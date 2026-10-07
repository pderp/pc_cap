# CAP Project Review — 2026-09-29 (recovered copy)

Recovered by Capstan at 06:55 EDT from the content read at 06:46, after the working file `project_review_20260929.md`
was found empty again on disk (its editor appears to truncate it while saving). This copy is verbatim as read; the
original file is untouched.

## Executive Summary
The CAP (Predictive-Coding Cap) project is a knowledge-editing system using GPT-2 base (124M, 12L/768d/12h) with a PC-based cap that modifies latent activations at write time to edit facts, evaluated across zsRE, CounterFact, and MQuAKE-CF. The project has progressed through development (S0-S8), revision v1 (R1), a frozen confirmatory Stage-4 matrix (DEC-071), and is now in the additional-work phase (AW-B bounded correction, PC-v0 controls, Option R). Stage-4 was halted at cell 225 per DEC-074/074b, with block-5 caveat (S1 controls on zsRE only) currently running.
## Model
GPT-2 base: 124M parameters, 12 layers, 768 hidden dim, 12 attention heads. This is the smallest GPT-2 variant. The choice is defensible for a mechanism study (cheapest model that demonstrates the architecture), but limits ecological validity — findings may not transfer to production-scale models. This should be stated explicitly in every external report.
## What's Working Well
1. **Methodological rigor**: The decision log (DEC-029 through DEC-076a) shows exceptional discipline — pre-registration, frozen protocols, exclusion registers, hash-bound code/weights, lead approval gates, and outcome-independent draws. This is rare and commendable.
2. **AW-B matched mixture** (DEC-076/076a): The rho=e^-1 mixture is a clean result — it bounds per-token loss at 1 nat by construction while preserving >=0.63 of the cap's answer mass, cutting mean KL from 0.0023 to 0.0007 on zsRE and ES99+ from 0.237 to 0.076, all without measurable efficacy loss on development memories. If this holds on sealed realization-0 streams, it's the project's strongest practical contribution.
3. **PC-v0 settling-depth control** (DEC-075, item 132-133): The dose-response finding is scientifically interesting and honest — one-step error credit reproduces adjoint exactly, and deeper settling buys own-prompt retention (+0.02 to +0.05) but not generalization, while harm rises (+8% at 8 steps, +52% at 32). This cleanly separates "the credit rule works" from "more is better."
4. **Fidelity watch** (DEC-064a): The creep-alert mechanism is a good safeguard against silent degradation.

(The file ended here at 06:46; corrections noted by Capstan in the lead queue: the halt was at cell 270, not 225, and the
block-5 caveat cells are complete.)
