# HT-2 — fixed development stress panel

Status: contract and six-cell manifest complete; execution awaits reader selection, driver support and lead scheduling.
Agent: Codex. Inputs: heavy_tail_counter_review.md §§3–5, the three existing development manifests.
Outputs: manifests/revision_v1/ht_development_panel_v1.json and scripts/ht_build_development_panel.py.
No model, training, draw, seal or GPU use. The builder reads only already permitted development item manifests.

The panel holds reader, 100 support facts, warm-up and later updates fixed within each dataset. The first 20 updates
teach the fixed old-fact probe set. The next 40 contain a metadata-selected difficult family plus other facts;
clustered puts that family at the end, while shuffled distributes the same 40 facts by a seed-303 SHA256 order.
The final 40 updates are identical in both schedules. Six cells cover selected primary × two schedules × three datasets.

Difficulty is a **longer-answer metadata proxy**, not an observed reader failure or measured original-base NLL.
Use exact relation IDs where available; zsRE uses exact subject-masked prompt templates. Among eligible families
with 4–20 distinct subjects and enough other facts for 100 total, choose greatest mean answer-token length
(excluding terminal), then lexical family name. All IDs, exact orderings, ranking and source hashes are in the manifest.
Concrete choices: zsRE “what family does <subject> belong?” (4 facts), CounterFact P101 (8), MQuAKE P69 (8).
The small zsRE block limits stress intensity; report it rather than enlarging it after outcomes.

Probe the same 20 warm-up facts and their existing paraphrases at updates 20, 60, 70, 80 and 100, with no probe learning.
Include failures to acquire at update 20 in every denominator. Measure per-target-token NLL increase relative to the
same cell at update 20, exact-answer retention, and paraphrase retention; report original-base comparison separately.
The shared treatment interval ends at 60 in both arms; clocks do not start at whichever difficult example came last.

Recovery is the first sampled lag after update 60 at which mean positive NLL degradation is ≤0.01 nat/token and
exact-answer count is at least the update-20 count, sustained at all later measured times. Report intervals between
measurement points, not falsely precise recovery times. No observed recovery by update 100 is right-censored
beyond 40 later updates. Missing/nonfinite probes are assay failures, not recovery. Print individual-fact trajectories
and both schedules' absolute quality so poor pre-block acquisition cannot appear as robustness.

Driver recipe form is embedded in the manifest. It deliberately has null reader/base/code/payload bindings and
execution_authorized=false. The existing development validator admits its registered 100/300/1000 cadence;
it does **not** yet admit this panel's intermediate probe cadence or fixed old-fact NLL endpoint. Required owner work:
create a separately versioned development stress driver, bind the exact selected primary and unsealed payload,
test query purity and fixed denominators on TinyBase, then bind all source and construction hashes. Reuse the
R1-68b journal/checkpoint machinery only after those tests. Do not pass this template directly to a production queue.

The total ceiling is 4 GPU hours, including setup, probes, retries and failed work. Use the machine memory guard,
GPU lease and measured remaining-budget check before each cell. Scheduling follows the lead's block-order decision:
protect initial confirmatory blocks, insert before realization 2 only if approved. All model experiments stop October 9;
October 10–14 is analysis/slides/rehearsal.

Verify command: ../venv/bin/python -B scripts/ht_build_development_panel.py (one-shot creation; future runs need a
new version/output rather than overwriting). Verify output: three family selections above; builder asserts six 100-item
cells, paired identical membership and unique item IDs. Independent inspection confirms identical first-20/final-40
orders, same treatment membership and the bound development sources. GPU seconds 0.
Done-when: requested contract/manifest delivered. Unresolved: selected-primary identity, stress driver and timing,
metadata-family review and lead scheduling approval. No claim of measured stress/recovery yet.
