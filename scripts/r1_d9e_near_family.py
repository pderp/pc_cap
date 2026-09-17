"""DEC-061 NM-template-v1: deterministic pairing within already reserved roles."""

from __future__ import annotations

import re

from pccap.metrics.editing import normalize_answer

CONTRACT = {
    "decision": "DEC-061",
    "family": "NM-template-v1",
    "subjects": "different_globally_reserved_subjects",
    "counterfact_mquake": "exact_nonempty_relation_id",
    "zsre": "exact_normalized_subject_masked_question_template_single_whole_word_occurrence",
    "pairing": "lexical_support_item_id_then_first_unused_lexical_neighbour_same_family",
    "scoring": "DEC-053_bounded_text_equality_neighbour_vs_its_actual_cap_off_baseline",
    "missing": "retain_planned_ids_and_unavailable_reason_no_replacement_no_redraw",
}


def near_key(row):
    if row["dataset"] in ("counterfact", "mquake"):
        relation = row.get("relation_id")
        return "relation:" + relation if isinstance(relation, str) and relation.strip() else None
    subject, prompt = normalize_answer(row["subject"]), normalize_answer(row["prompt"])
    if not subject:
        return None
    pattern = re.compile(r"(?<!\w)" + re.escape(subject) + r"(?!\w)")
    if len(pattern.findall(prompt)) != 1:
        return None
    return "question_template:" + pattern.sub("{subject}", prompt)


def pair_reserved(supports, neighbours, expected_ids, *, dataset):
    supports = sorted(supports, key=lambda r: r["item_id"])
    neighbours = sorted(neighbours, key=lambda r: r["item_id"])
    if len(expected_ids) != len(supports) or len(set(expected_ids)) != len(expected_ids):
        raise ValueError("near-miss planned support-slot inventory differs")
    all_rows = supports + neighbours
    if len({r["item_id"] for r in all_rows}) != len(all_rows):
        raise ValueError("near-miss support/neighbour roles reuse an item")
    if any(r["dataset"] != dataset for r in all_rows):
        raise ValueError("near-miss reserved dataset differs")
    rows, missing, used = [], [], set()
    for identity, own in zip(expected_ids, supports, strict=True):
        family = near_key(own)
        subject = normalize_answer(own["subject"])
        other = next((r for r in neighbours if r["item_id"] not in used and family
                      and near_key(r) == family and subject
                      and normalize_answer(r["subject"]) not in ("", subject)), None)
        if other is None:
            missing.append(dict(item_id=identity, edit_item_id=own["item_id"],
                                reason="no_compatible_reserved_neighbour"))
            continue
        used.add(other["item_id"])
        rows.append(dict(item_id=identity, dataset=dataset, edit_item_id=own["item_id"],
                         neighbour_item_id=other["item_id"], edit_prompt=own["prompt"],
                         edit_answer=own["answer"], neighbour_prompt=other["prompt"],
                         neighbour_answer=other["answer"], type=family.split(":", 1)[0]+"_other_subject",
                         family=CONTRACT["family"], family_key=family))
    return dict(expected_ids=list(expected_ids), rows=rows, missing=missing, family_contract=dict(CONTRACT))


def validate_section(section, supports, neighbours, expected_ids, *, dataset):
    expected = pair_reserved(supports, neighbours, expected_ids, dataset=dataset)
    if section != expected:
        raise ValueError("DEC-061 near-miss family/source/pairing/missing inventory differs")
    return expected
