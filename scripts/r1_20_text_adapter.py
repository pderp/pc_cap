"""R1-20 text/token boundary and payload adapter for revision_v1_design.md.

No model execution. Query labels remain exclusively in the outer/evaluation
container. This does not implement the orchestrator-owned contracts or trainer.
"""

from __future__ import annotations

from dataclasses import replace

from pccap.data.tokenize import tokenize_pair


def tokenize_natural_episode(episode, tokenizer):
    """Use the project's prompt/answer delimiter convention; refuse exclusions."""
    if episode.domain != "natural-development-v1":
        raise ValueError("synthetic token IDs have their own vocabulary; no implicit GPT-2 remapping")
    if any(q.prompt_ids for q in episode.prediction_inputs()):
        raise ValueError("episode is already tokenized")

    def support(row):
        pair = tokenize_pair(tokenizer, row.prompt, row.answer)
        if pair.excluded:
            raise ValueError(f"support {row.record_id}: {pair.reason}")
        return replace(row, prompt_ids=tuple(map(int, pair.prompt_ids)),
                       answer_ids=tuple(map(int, pair.answer_ids)))

    queries = tuple(replace(q, prompt_ids=tuple(map(int, tokenizer.encode(q.prompt))))
                    for q in episode.prediction_inputs())
    prompt_by_id = {q.query_id: q.prompt for q in queries}
    labels = []
    for label in episode.query_labels:
        if label.target is None:
            if label.target_source != "teacher_prediction_required":
                raise ValueError("missing non-preservation target")
            labels.append(label)
            continue
        pair = tokenize_pair(tokenizer, prompt_by_id[label.query_id], label.target)
        if pair.excluded:
            raise ValueError(f"query {label.query_id}: {pair.reason}")
        labels.append(replace(label, target_ids=tuple(map(int, pair.answer_ids))))
    inputs = replace(episode.inputs,
                     support_history=tuple(support(s) for s in episode.inputs.support_history),
                     new_support=tuple(support(s) for s in episode.inputs.new_support),
                     queries=queries)
    return replace(episode, inputs=inputs, query_labels=tuple(labels),
                   provenance=episode.provenance + (("tokenizer_sha256", tokenizer.file_sha256()),
                                                    ("answer_delimiter", "tokenize_pair: optional space + answer + newline")))


def require_training_targets(episode) -> None:
    """Scope losses cannot be silently omitted for a missing teacher target."""
    unresolved = [label.query_id for label in episode.query_labels
                  if label.target_source == "teacher_prediction_required" or not label.target_ids]
    if unresolved:
        raise ValueError(f"episode is not training-ready: unresolved targets for {unresolved}")


def design_payload(episode) -> dict:
    """A mapping for the Stage 1 Episode factory, with explicit separated labels.

    This mapping is for outer/evaluation orchestration. Prediction receives one
    query's prompt/IDs and memory only; it must never receive this whole mapping.
    """
    by_id = {q.query_id: q for q in episode.prediction_inputs()}

    def queries(role):
        return tuple(by_id[label.query_id] for label in episode.query_labels if label.role == role)

    return {"history": episode.inputs.support_history, "support_new": episode.inputs.new_support,
            "queries_new": queries("new_paraphrase"), "queries_old": queries("old_fact"),
            "near_miss": queries("near_miss"), "unrelated": queries("unrelated"),
            "composition": queries("composition"), "split_id": episode.split_id,
            "entity_ids": tuple(sorted({s.entity_id for s in episode.inputs.support_history + episode.inputs.new_support}
                                       | {entity for label in episode.query_labels for entity in label.entity_ids})),
            "family_ids": tuple(sorted({s.family_id for s in episode.inputs.support_history + episode.inputs.new_support}
                                       | {label.family_id for label in episode.query_labels})),
            "seed": episode.generator_seed, "partition_seed": episode.partition_seed,
            "labels": episode.query_labels, "provenance": episode.provenance}
