from __future__ import annotations

import copy

import numpy as np
import pytest
from scripts.r1_d10a_review import audit_query_reason
from scripts.r1_d10a_review_core import DATASETS, Entities, Matcher, digest, review, token_review


def test_historical_query_role_names_and_mixed_role_exclusions():
    assert (
        audit_query_reason(["mquake"], ["development_unrelated"])
        == "mquake_development_locality_query_subject"
    )
    assert (
        audit_query_reason(["mquake"], ["locality", "near_miss_reserved"])
        == "mquake_unverified_near_miss_query_subject"
    )
    assert audit_query_reason(["mquake"], ["locality", "primary"]) == "historical_query_reservation"
    assert audit_query_reason(["mquake", "zsre"], ["locality"]) == "historical_query_reservation"


class Tokenizer:
    def encode(self, text):
        return np.asarray([ord(c) for c in text], dtype=np.int32)

    def decode(self, ids):
        return "".join(chr(int(i)) for i in ids)


def fixture(names=None):
    tok = Tokenizer()
    sources, register = {}, {"schema_version": 6, "candidates": {}}
    for ds in DATASETS:
        sources[ds], register["candidates"][ds] = [], []
        for i, name in enumerate((names or {}).get(ds, [ds + str(i) for i in range(5)])):
            row = {
                "item_id": ds + str(i),
                "fact_id": ds + str(i),
                "dataset": ds,
                "subject": name,
                "prompt": name + "?",
                "answer": "new",
                "aliases": ["new"],
                "paraphrases": [name + " again?"],
                "source_record_sha256": "s" * 64,
            }
            row.update(
                prompt_ids=tok.encode(row["prompt"]).tolist(),
                answer_ids=tok.encode(" new\n").tolist(),
            )
            sources[ds].append(row)
            register["candidates"][ds].append(
                {
                    "item_id": row["item_id"],
                    "canonical_subject": name,
                    "payload_sha256": digest(row),
                    "source_record_sha256": row["source_record_sha256"],
                }
            )
    return (
        register,
        sources,
        {"verified_alias_pairs": {}, "events": []},
        tok,
        {"vocabulary": 65536, "max_context": 512},
    )


def test_exhaustive_dispositions_bounded_order_and_pending_teacher():
    e, checks = review(*fixture(), target=2)
    assert len(e["dispositions"]) == len(checks) == 15
    for ds in DATASETS:
        rows = [d for d in e["dispositions"] if d["dataset"] == ds]
        assert [d["preteacher_eligible"] for d in rows] == [True, True, False, False, False]
        assert rows[-1]["reasons"] == ["not_reviewed_bounded_policy"]
    assert not e["teacher_token_review_complete"]
    assert not e["role_compatibility_complete"]
    assert all(d["decision"] == "exclude" and d["teacher_pass"] is None for d in e["dispositions"])


def test_alias_transitivity_punctuation_unicode_and_word_boundaries():
    ids = Entities({"A. Name": "Ａ Name", "A Name": "Alias"})
    assert ids.identity("A-Name") == ids.identity("alias")
    matcher = Matcher(["Ann", "A Name", "Alias"], ids)
    assert ids.identity("Ann")[0] not in matcher.matches("Annual report")
    assert ids.identity("A Name")[0] in matcher.matches("Someone saw A—Name today.")


def test_global_cross_dataset_alias_and_duplicate_representatives():
    f = fixture({"zsre": ["A. Name", "A-Name", "third"], "counterfact": ["Alias", "other"]})
    f[2]["verified_alias_pairs"] = {"A Name": "Alias"}
    e, _ = review(*f, target=2)
    assert e["counts"]["zsre"]["preteacher_items"] == 3
    assert e["counts"]["zsre"]["preteacher_subjects"] == 2
    assert "cross_dataset_entity_collision" in e["dispositions"][3]["reasons"]


@pytest.mark.parametrize(
    "reason,clear",
    [
        ("mquake_training_locality_query_subject", True),
        ("mquake_development_unrelated_query_subject", True),
        ("reserved_near_miss_candidate", False),
        ("mquake_unknown_query_subject", False),
        ("mquake_training_reserved_subject", False),
    ],
)
def test_only_exact_mquake_waivers(reason, clear):
    f = fixture({"mquake": ["Entity"]})
    f[2]["events"] = [
        {"source": "fixture", "reason": reason, "subject": "Entity", "text": "Entity?"}
    ]
    e, checks = review(*f)
    assert e["dispositions"][-1]["preteacher_eligible"] is clear
    assert bool(checks[-1]["waived_event_indices"]) is clear


def test_counterfact_old_eligible_exception_does_not_waive_actual_training():
    f = fixture({"counterfact": ["Entity"]})
    f[2]["events"] = [{"source": "old", "reason": "old_eligible:counterfact", "subject": "Entity"}]
    assert review(*f)[0]["counts"]["counterfact"]["preteacher_subjects"] == 1
    f[2]["events"].append({"source": "new", "reason": "training", "subject": "Entity"})
    assert review(*f)[0]["counts"]["counterfact"]["preteacher_subjects"] == 0


def test_true_query_waiver_does_not_release_other_entities_in_context():
    f = fixture({"mquake": ["Main Entity", "Incidental Entity"]})
    f[2]["events"] = [
        {
            "source": "fixture",
            "reason": "mquake_training_locality_query_subject",
            "text": "Main Entity worked near Incidental Entity.",
            "waiver_subjects": ["Main Entity"],
        }
    ]
    e, _ = review(*f)
    assert e["dispositions"][-2]["preteacher_eligible"]
    assert not e["dispositions"][-1]["preteacher_eligible"]


def test_context_mention_of_other_subject_is_not_a_direct_subject_alias():
    f = fixture({"mquake": ["Main Entity", "Incidental Entity"]})
    f[2]["events"] = [
        {
            "source": "fixture",
            "reason": "training",
            "subject": "Main Entity",
            "text": "Main Entity worked near Incidental Entity.",
        }
    ]
    e, _ = review(*f)
    assert not e["dispositions"][-2]["alias_clear"]
    assert e["dispositions"][-1]["alias_clear"]
    assert not e["dispositions"][-1]["context_clear"]


def test_answer_aliases_are_not_subject_aliases_and_context_matches_count():
    f = fixture({"zsre": ["Entity"]})
    f[2]["events"] = [{"source": "fixture", "reason": "training", "subject": "new"}]
    assert review(*f)[0]["dispositions"][0]["preteacher_eligible"]
    f[2]["events"].append(
        {"source": "ordinary_text", "reason": "text_training", "text": "An Entity lived here."}
    )
    d = review(*f)[0]["dispositions"][0]
    assert d["alias_clear"] and not d["exposure_clear"] and not d["context_clear"]


@pytest.mark.parametrize("fault", ["hash", "missing", "duplicate"])
def test_input_identity_failure(fault):
    f = fixture()
    if fault == "hash":
        f[1]["zsre"][0]["answer"] = "changed"
    elif fault == "missing":
        f[1]["zsre"].pop()
    else:
        f[1]["zsre"].append(copy.deepcopy(f[1]["zsre"][0]))
    with pytest.raises(ValueError, match="source"):
        review(*f)


@pytest.mark.parametrize("fault", ["paraphrase", "context", "ids", "answer"])
def test_full_token_and_paraphrase_validation(fault):
    _, sources, _, tok, limits = fixture()
    row = sources["zsre"][0]
    if fault == "paraphrase":
        row["paraphrases"] = []
    elif fault == "context":
        row["paraphrases"] = ["x" * 500]
    elif fault == "ids":
        row["prompt_ids"] = [0]
    else:
        row["answer"] = "x" * 40
    assert not token_review(row, tok, limits)["pass"]
