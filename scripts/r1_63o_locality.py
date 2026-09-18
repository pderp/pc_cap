"""Lead-approved prospective D.5 locality selection; no model outcomes consulted."""

from scripts.r1_locality_contract import edit_prompts, validate_locality


def select(edits, outside, *, group, count=50):
    if type(count) is not int or count < 1:
        raise ValueError("positive planned locality count required")
    forbidden = edit_prompts(edits)
    seen, selected, excluded = set(), [], []
    candidates = 0
    for row in sorted(outside, key=lambda r: r["item_id"]):
        for index, prompt in enumerate(row.get("locality_prompts", [])):
            if not isinstance(prompt, str) or not prompt.strip():
                raise ValueError("nonempty locality source prompt required")
            candidates += 1
            if prompt in forbidden:
                excluded.append(dict(source_outside_item_id=row["item_id"], prompt_index=index))
            elif prompt not in seen:
                seen.add(prompt)
                if len(selected) < count:
                    selected.append(
                        dict(
                            item_id=f"{group}:locality:{len(selected)}",
                            prompt=prompt,
                            source_outside_item_id=row["item_id"],
                        )
                    )
    validate_locality(edits, selected)
    return selected, dict(
        group=group,
        planned=count,
        selected=len(selected),
        eligible_unique=len(seen),
        source_prompt_count=candidates,
        excluded_overlap_sources=excluded,
        excluded_overlap_count=len(excluded),
        shortfall=count - len(selected),
        rule="sorted reserved outside item_id, then source prompt order; exact-text deduplication and exclusion of every reserved edit/paraphrase including future edits; first 50 eligible; no new subjects or outcomes",
    )
