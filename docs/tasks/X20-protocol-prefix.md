# X20 protocol prefix — partial read-only verification

Status: **protocol step verified; full X20 pending step 8**, Codex, September 18, 2026.

The [new independent reviewer](../../scripts/r1_x20_protocol_review.py) reconstructs the genuine protocol request from `docs/tasks/operator-v8/01-protocol-reviewed.json`, checks its exact signed digest, verifies the matching unblocked preview and completed journal row, reconstructs the complete receipt/allocation objects and checks the exact next-input transition. It also verifies candidate v14's 1,845 bound sources and source/journal stability. It does not invoke the operator, write a signature/journal, open a sealed payload, draw, seal, publish or launch.

[Latest snapshot](../../logs/r1_round39/protocol-prefix-final.json); [initial snapshot](../../logs/r1_round38/post-protocol-signature-check.json). The signature admits the 45-cell optional extension: **285 + 45 = 330 protocol-selected cells**. This does not establish cost admission or launch authority.

The earlier `01-protocol-preview.json` is an unsigned seed form with an older request digest. It is not the final reviewed form and not the matching unblocked journal preview. The reviewer records this distinction instead of treating the unsigned form as a contradictory signature.

At the final snapshot only `protocol-admit` is completed. The signed typed-v4 cost receipt is absent; HT-4f remains pending step 2. Full X20 awaits step 8 and must separately verify clearance, RNG/draw, actual endpoints/missingness, seal, publication/freeze and precise source digests. Neither this partial report nor the synthetic R1-D14 reports close those gates.

Verify: CPU `python -m scripts.r1_x20_protocol_review --output logs/NEW_PROTOCOL_REVIEW.json`; result records exact signed request, receipt/source SHA values, unblocked preview, complete reconstruction and transition checks. Ruff passes. GPU cost 0 seconds. No questions for the lead and no existing-file changes.
