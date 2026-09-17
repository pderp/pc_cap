"""Source-text locality exclusions across a cell's complete reserved edit stream."""


def edit_prompts(items):
    prompts = set()
    for row in items:
        for prompt in [row["prompt"], *row.get("paraphrases", [])]:
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("nonempty source edit/paraphrase prompt required")
            prompts.add(prompt)
    return prompts


def validate_locality(items, rows):
    forbidden = edit_prompts(items)
    for row in rows:
        prompt = row.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("nonempty locality prompt required")
        if prompt in forbidden:
            raise ValueError("locality overlaps a reserved edit/paraphrase prompt")


def select_unrelated(items, prompts, count=50):
    """Deterministic source order, deduplicated; no outcomes or occupancy-dependent filtering."""
    forbidden = edit_prompts(items)
    seen, selected, excluded = set(), [], []
    for index, prompt in enumerate(prompts):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("nonempty unrelated source prompt required")
        if prompt in forbidden:
            excluded.append(index)
        elif prompt not in seen:
            seen.add(prompt)
            selected.append((index, prompt))
    if len(selected) < count:
        raise ValueError("unrelated locality shortfall after complete-stream exclusion")
    rows = [
        {"item_id": f"dev:locality:{i}", "prompt": p} for i, (_, p) in enumerate(selected[:count])
    ]
    validate_locality(items, rows)
    return rows, {
        "selected_source_indices": [i for i, _ in selected[:count]],
        "excluded_overlap_indices": excluded,
        "eligible_unique": len(selected),
        "rule": "exact source text; all attempted edit prompts and paraphrases, including future edits",
    }
