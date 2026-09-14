"""CPU source-mapping and refusal tests; no teacher or model execution."""

import copy

import numpy as np
import pytest
from scripts import r1_d4_prepare_mquake as prep


class Tokenizer:
    def encode(self, text):
        return np.asarray([ord(c) for c in text], dtype=np.int32)

    def decode(self, ids):
        return "".join(chr(int(c)) for c in ids)


def case(i, subject=None, target="new", relation="P1"):
    subject = subject or f"S{i}"
    rewrite = {
        "subject": subject,
        "relation_id": relation,
        "prompt": "{} works at",
        "question": f"Who employs {subject}?",
        "target_new": {"str": target, "id": "Q" + target},
        "target_true": {"str": "old", "id": "Qold"},
    }
    return {
        "case_id": i,
        "requested_rewrite": [rewrite],
        "questions": [f"composition {i} {j}" for j in range(3)],
        "answer": "old",
        "new_answer": target,
        "answer_alias": ["Old"],
        "new_answer_alias": [target],
        "single_hops": [
            {
                "question": rewrite["question"],
                "cloze": f"{subject} works at",
                "answer": "old",
                "answer_alias": [],
            }
        ],
        "new_single_hops": [
            {
                "question": rewrite["question"],
                "cloze": f"{subject} works at",
                "answer": target,
                "answer_alias": [target + " alias"],
            }
        ],
        "orig": {
            "triples": [["QS", relation, "Qold"]],
            "new_triples": [["QS", relation, "Q" + target]],
            "triples_labeled": [[subject, relation, "old"]],
            "new_triples_labeled": [[subject, relation, target]],
            "edit_triples": [["QS", relation, "Q" + target]],
        },
    }


def test_first_case_wins_and_conflicting_composition_retained():
    rows = [case(2, "S1", "alt"), case(1, "S1")]
    result = prep.prepare(rows, set(), Tokenizer())
    assert len(result["items"]) == 1
    assert result["items"][0]["answer"] == "new"
    assert result["items"][0]["aliases"] == ["new", "new alias"]
    assert result["summary"]["target_new_conflicting_occurrences"] == 1
    assert result["composition"][1]["unavailable_reasons"] == ["conflicts_with_first_case_target"]
    assert result["composition"][1]["questions"] == rows[0]["questions"]


def test_subject_normalization_exclusion_counts_subjects_and_rewrites():
    rows = [case(1, "  Ａ  B "), case(2, "a b", relation="P2"), case(3)]
    result = prep.prepare(rows, {"a b"}, Tokenizer())
    assert result["summary"]["excluded_subjects"] == 1
    assert result["summary"]["excluded_unique_rewrites"] == 2
    assert len(result["items"]) == 1
    assert result["composition"][0]["dependencies"][0]["status"] == "excluded_subject"


def test_locality_two_near_two_other_subjects_and_relation():
    result = prep.prepare([case(i) for i in range(1, 7)], set(), Tokenizer())
    for row in result["items"]:
        local, near = row["locality"], row["near_miss_candidates"]
        assert len(local) == len(near) == 2
        assert len({x["subject_key"] for x in local + near}) == 4
        assert all(x["subject_key"] != row["subject_key"] for x in local + near)
        assert all(
            x["relation_id"] == row["relation_id"] and x["answer"] == "old" for x in local + near
        )
        assert row["locality_prompts"] == [x["prompt"] for x in local]


def test_short_neighbour_pool_is_explicit():
    result = prep.prepare([case(1), case(2)], set(), Tokenizer())
    assert result["summary"]["locality_coverage_histogram"] == {1: 2}
    assert result["summary"]["near_miss_coverage_histogram"] == {0: 2}


def test_source_variants_merge_with_exact_triple_anchor():
    a, b = case(1), case(2, "S1")
    b["new_single_hops"][0]["question"] = "Second question for S1?"
    b["new_single_hops"].append(
        {
            "question": "Wrong entity?",
            "cloze": "S99 works at",
            "answer": "new",
            "answer_alias": ["BAD"],
        }
    )
    result = prep.prepare([a, b], set(), Tokenizer())
    row = result["items"][0]
    assert row["paraphrases"] == ["Who employs S1?", "Second question for S1?"]
    assert "BAD" not in row["aliases"]


def test_deterministic_reordered_input_and_dependency_hashes():
    rows = [case(i) for i in range(1, 7)]
    a = prep.prepare(rows, set(), Tokenizer(), {"s1", "s99"})
    b = prep.prepare(list(reversed(rows)), set(), Tokenizer(), {"s1", "s99"})
    assert a == b
    assert a["summary"]["zsre_v3_fresh_candidate_subject_overlap"] == 1
    assert a["items"][0]["source_record_sha256"] == prep.digest(rows[0]["requested_rewrite"][0])
    assert a["items"][0]["composition_question_count_source"] == 3


def test_token_ineligible_retained_and_composition_unavailable():
    result = prep.prepare([case(1, target="x" * 40)], set(), Tokenizer())
    assert result["summary"]["token_ineligible"] == 1
    assert result["items"][0]["token_status"] == "token_ineligible"
    assert result["composition"][0]["unavailable_reasons"] == ["token_ineligible"]


def test_composition_preserves_direct_source_and_orig():
    a, b = case(1), case(2)
    a["requested_rewrite"] += copy.deepcopy(b["requested_rewrite"])
    result = prep.prepare([a], set(), Tokenizer())
    comp = result["composition"][0]
    assert len(comp["dependencies"]) == 2
    assert comp["verified_source"] == "MQuAKE"
    assert comp["orig"] == a["orig"]
    assert comp["questions"] == a["questions"]
    assert comp["final_eligible"] is None


def test_different_entity_id_is_target_conflict():
    a, b = case(1), case(2, "S1")
    b["requested_rewrite"][0]["target_new"]["id"] = "different"
    result = prep.prepare([a, b], set(), Tokenizer())
    assert result["summary"]["target_new_conflicting_occurrences"] == 1


@pytest.mark.parametrize("bad", ["duplicate_case", "bad_template", "empty_subject"])
def test_malformed_input_refused(bad):
    a = case(1)
    rows = [a]
    if bad == "duplicate_case":
        rows.append(copy.deepcopy(a))
    elif bad == "bad_template":
        a["requested_rewrite"][0]["prompt"] = "{} with {}"
    else:
        a["requested_rewrite"][0]["subject"] = " "
    with pytest.raises(ValueError):
        prep.prepare(rows, set(), Tokenizer())


def test_output_refuses_existing_before_any_write(tmp_path):
    resource = tmp_path / "existing"
    resource.mkdir()
    with pytest.raises(FileExistsError):
        prep.write_outputs({}, {}, resource, tmp_path / "manifest", tmp_path / "report")
    assert list(resource.iterdir()) == []


def test_output_scope_refused_before_any_write(tmp_path):
    with pytest.raises(ValueError, match="resources under assets"):
        prep.write_outputs({}, {}, tmp_path / "new", tmp_path / "manifest", tmp_path / "report")
    assert not (tmp_path / "new").exists()


def test_primary_subject_key_deduplicates_but_relations_remain_separate():
    result = prep.prepare(
        [case(1, "Ａ"), case(2, "a"), case(3, "a", relation="P2")], set(), Tokenizer()
    )
    assert len(result["items"]) == 2
    assert result["summary"]["subjects"] == 1
    assert len({r["item_id"] for r in result["items"]}) == 2
