"""Pure three-dataset count reconciliation and refusal tests."""

import sys

import pytest
from scripts import r1_58_three_dataset_dry_run as three


def row(name, subject, relation="P1"):
    return {
        "item_id": name,
        "subject_key": subject,
        "answer_ids": [1, 198],
        "token_status": "candidate",
        "relation_id": relation,
    }


def test_cross_dataset_subjects_and_extra_relations_not_double_counted():
    merged, removed = three.merge_subjects(
        {"zsre": [{"_canonical_subject": "a", "_stratum": "1-2"}], "counterfact": []},
        [row("x", "a"), row("y", "b"), row("z", "b", "P2"), row("w", "c")],
    )
    assert len(merged["mquake"]) == 2
    assert removed == {"cross_dataset_subject_overlap": 1, "within_mquake_extra_relation": 1}
    assert {r["_canonical_subject"] for r in merged["mquake"]} == {"b", "c"}


def test_token_ineligible_not_counted():
    r = row("x", "a")
    r["token_status"] = "token_ineligible"
    merged, removed = three.merge_subjects({"zsre": [], "counterfact": []}, [r])
    assert merged["mquake"] == []
    assert removed == {"token_ineligible": 1}


@pytest.mark.parametrize("extra", [[], ["--i-am-the-lead"], ["--seal"]])
def test_no_real_draw_interface(monkeypatch, tmp_path, extra):
    args = [
        "three",
        "--counterfact-source",
        "exception",
        "--report",
        str(tmp_path / "report"),
        *extra,
    ]
    monkeypatch.setattr(sys, "argv", args)
    with pytest.raises(SystemExit):
        three.main()
    assert not (tmp_path / "report").exists()
