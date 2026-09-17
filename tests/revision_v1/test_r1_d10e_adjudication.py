"""Context proposals cannot erase edit exposure or alter operative evidence."""

import copy

import pytest
from scripts.r1_d10a_review_core import Entities
from scripts.r1_d10e_adjudication import adjudicate, waive


def fixture(events, *, reason=None, dataset="mquake"):
    entity = Entities({}).identity("Alex Example")[0]
    d = dict(
        dataset=dataset,
        item_id="item",
        canonical_subject="Alex Example",
        entity_id=entity,
        payload_sha256="payload",
        preteacher_eligible=False,
        decision="exclude",
        roles=[],
        reasons=reason or ["exposed_context_name_match"],
        teacher_pass=None,
        tokens_pass=None,
    )
    e = dict(dispositions=[d], teacher_token_review_complete=False)
    inputs = dict(verified_alias_pairs={}, events=events)
    checks = [
        dict(
            dataset=dataset,
            item_id="item",
            entity_key="alex example",
            blocking_event_indices=list(range(len(events))),
            token_context_check={"pass": True},
        )
    ]
    return e, inputs, checks


def test_ordinary_only_proposal_preserves_original_dispositions():
    args = fixture(
        [dict(reason="ordinary_text_training_prefix", source="text#1", text="Alex Example")]
    )
    original = copy.deepcopy(args)
    candidate, sheet, counts = adjudicate(*args)
    assert args == original
    assert candidate["dispositions"] == args[0]["dispositions"]
    assert candidate["proposed_dispositions"][0]["preteacher_eligible"]
    assert candidate["proposed_dispositions"][0]["decision"] == "exclude"
    assert counts["mquake"]["restored_subjects"] == 1
    assert sheet["rows"][0]["events"][0]["source_event"] == args[1]["events"][0]
    assert not candidate["context_adjudication_admitted"]


@pytest.mark.parametrize(
    "reason",
    [
        "development_payload_reserved",
        "mquake_training_reserved_subject",
        "reserved_near_miss_candidate",
        "development_endpoint:locality",
        "historical_query_reservation",
        "unknown",
    ],
)
def test_query_context_remains_blocked_even_with_ordinary_mention(reason):
    args = fixture(
        [
            dict(reason="development_drift_text", source="drift#1", text="Alex Example"),
            dict(reason=reason, source="otherdataset#query", text="Alex Example"),
        ]
    )
    c, sheet, counts = adjudicate(*args)
    assert not c["proposed_dispositions"][0]["preteacher_eligible"]
    assert counts["mquake"]["restored_subjects"] == 0
    assert len(sheet["rows"][0]["remaining_event_indices"]) == 1


def test_direct_subject_and_subject_annotated_text_cannot_be_waived():
    event = dict(
        reason="ordinary_text_training_prefix",
        source="unknown",
        subject="Alex Example",
        text="Alex Example",
    )
    assert not waive(event)
    c, sheet, _ = adjudicate(
        *fixture([event], reason=["exposed_subject_alias", "exposed_context_name_match"])
    )
    assert not sheet["rows"]
    assert not c["proposed_dispositions"][0]["preteacher_eligible"]


def test_cross_dataset_release_cannot_displace_existing_eligible_subject():
    e, inputs, checks = fixture(
        [dict(reason="development_drift_text", source="drift#1", text="Alex Example")],
        dataset="zsre",
    )
    other = copy.deepcopy(e["dispositions"][0])
    other.update(
        dataset="counterfact",
        preteacher_eligible=True,
        reasons=["pending_final_teacher_token_and_role_review"],
    )
    e["dispositions"].append(other)
    checks.append(
        dict(
            dataset="counterfact",
            item_id="item",
            entity_key="alex example",
            blocking_event_indices=[],
            token_context_check={"pass": True},
        )
    )
    c, sheet, _ = adjudicate(e, inputs, checks)
    assert not c["proposed_dispositions"][0]["preteacher_eligible"]
    assert c["proposed_dispositions"][1]["preteacher_eligible"]
    assert sheet["rows"][0]["cross_dataset_collision"]


def test_bad_coverage_or_index_refuses():
    e, i, c = fixture([dict(reason="development_drift_text", source="drift", text="Alex Example")])
    with pytest.raises(ValueError):
        adjudicate(e, i, [])
    c[0]["blocking_event_indices"] = [-1]
    with pytest.raises(ValueError):
        adjudicate(e, i, c)
