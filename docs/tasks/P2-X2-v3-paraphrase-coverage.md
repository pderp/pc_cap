# Urgent P2/X2 finding: the v3 seed fix leaves seven undefined RET-GS items

Observed by Codex during the v3 transition check on 13 September 2026. Source `67787f49ec16…`, frozen manifest `163d04e2a1e0ba83…`, experiment `frozen-confirmatory-v3-163d04e2`. CPU generator inspection only; no model execution or production mutation.

**Determinism is repaired, but complete paraphrase coverage is not.** The v3 grammar inventory still contains these zero-paraphrase items:

| realization | items | two paraphrases | one paraphrase | none | zero-paraphrase item IDs |
| --- | ---: | ---: | ---: | ---: | --- |
| 0 | 2048 | 2036 | 8 | **4** | `g3-r0-40`, `g0-r0-235`, `g5-r0-7`, `g5-r0-173` |
| 1 | 2048 | 2034 | 13 | **1** | `g7-r1-240` |
| 2 | 2048 | 2035 | 11 | **2** | `g6-r2-213`, `g2-r2-77` |

Evidence: [paraphrase_coverage.json](../../logs/p2_x2_v3_transition/paraphrase_coverage.json). Reproducer: [check_v3_grammar_paraphrase_coverage.py](../../scripts/check_v3_grammar_paraphrase_coverage.py). It uses the production `stream(realization, 0, 256)` and `with_paraphrases` functions for all three inventories. It does not load a checkpoint or score a model. Different committed orders contain the same item set; the new seed depends on the item ID, so order does not cure this absence.

`paraphrase_prefixes` still stops after 50 unsuccessful searches. A content hash makes the search repeatable but cannot guarantee it finds an answer-preserving alternative. With no paraphrases, the existing evaluator yields undefined RET-GS; the frozen missing-pair rule classifies a required incomplete inventory as incomplete even when the same item is missing in both arms. This is a structural coverage finding, **not a completed v3 result or a proposal to impute zero**. The v3 rerun alone therefore cannot guarantee the requested complete confirmatory grammar row.

The new four-item cross-process regression passes, and the 24 affected CPU tests pass; that test's sample does not include these seven cases. Before declaring SD-22 resolved, the owner needs a full-inventory coverage requirement as well as cross-process determinism.

Possible owner decisions, all requiring explicit version/policy handling:

1. Keep v3 outcomes and report their residual incompleteness transparently, with any complete-pair supplement labelled separately.
2. Produce deterministic, distinct, target-preserving paraphrases for every required item and verify the full inventory before another versioned run. Preserve latent mechanisms and acceptance criteria; do not tune seeds against learner performance or assume that merely increasing the try count guarantees coverage.
3. Explicitly amend the undefined-outcome policy with the lead's approval and disclose that amendment. This is not completion under the unchanged frozen rule.

The active queue, source, manifests and policies were not changed. This finding is for the lead/run owner; deciding whether to continue or stop the queued work is outside this CPU audit's authority.
