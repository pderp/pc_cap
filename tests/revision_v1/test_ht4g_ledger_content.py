"""Publication refusals, lineage preservation and ledger-bound deck checks."""

import copy
import json

import pytest
from scripts import ht4g_ledger_content as ledger
from scripts import ht10b_deck_v2 as deck


@pytest.fixture(scope="module")
def content():
    return json.loads(ledger.CONTENT.read_text())


def test_complete_content_has_only_signed_cost_pending(content):
    ledger.verify_sources(content)
    assert len(content["rows"]) == 40
    assert content["pending"] == ["signed_cost_receipt"]
    assert all(p["status"] == "complete" for p in content["profiles"])
    rows = {r["id"]: r for r in content["rows"]}
    assert rows["COST-matrix"]["status"] == "superseded"
    assert rows["DEC060-scale"]["status"] == "superseded"
    assert len(rows["HT6-full-validation"]["numeric_rows"]) == 8
    assert {r["reference"] for r in rows["HT6-full-validation"]["numeric_rows"]} == {
        "original",
        "capoff",
    }
    assert len(content["historical_binding_updates"]) == 4
    assert all(
        r["old"]["sha256"] != r["current"]["sha256"] for r in content["historical_binding_updates"]
    )
    assert content["superseded_binding_changes"][0]["claims"] == ["COST-matrix"]


def test_unsigned_real_cost_template_cannot_publish():
    target = ledger.ROOT / "logs/r1_round40/talk_evidence_v6.json"
    before = target.read_bytes() if target.exists() else None
    with pytest.raises((ValueError, PermissionError)):
        ledger.publish(ledger.CONTENT, ledger.ROOT / "docs/tasks/R1-cost-admission-receipt-v4.json")
    after = target.read_bytes() if target.exists() else None
    assert after == before


def test_source_drift_refuses_without_rebinding(content):
    value = copy.deepcopy(content)
    key = next(iter(value["sources_sha256"]))
    value["sources_sha256"][key] = "0" * 64
    with pytest.raises(ValueError, match="source changed"):
        ledger.verify_sources(value)


@pytest.mark.parametrize("damage", ["duplicate", "superseded", "numeric_rows", "extra_pending"])
def test_incomplete_or_ambiguous_content_refused(content, damage):
    value = copy.deepcopy(content)
    if damage == "duplicate":
        value["rows"].append(value["rows"][0])
    elif damage == "superseded":
        next(r for r in value["rows"] if r["id"] == "COST-matrix")["status"] = "current"
    elif damage == "numeric_rows":
        next(r for r in value["rows"] if r["id"] == "HT6-full-validation")["numeric_rows"].pop()
    else:
        value["pending"].append("missing_measurement")
    with pytest.raises(ValueError):
        ledger.verify_sources(value)


def test_v2_sources_notes_and_each_slide_bound_to_current_rows(content):
    slides, _, lineage = deck.prepare()
    assert len(slides) == 12
    assert "zsRE unseen" in slides[2]["points"][3]
    assert "1,931 complete" in slides[4]["speaker_notes"]
    assert "meets the retention floor" in slides[7]["points"][4]
    assert "Each tested dataset" in slides[8]["points"][0]
    assert slides[6]["foot"] == slides[7]["foot"] == deck.rendering.DEC054
    assert "NO CONFIRMATORY RESULTS" in slides[9]["label"]
    assert "NOT MEASURED PROGRESS" in slides[10]["label"]
    assert lineage["signature_status"] == "pending_signed_cost_receipt"
    rows = {r["id"]: r for r in content["rows"]}
    for slide in slides:
        assert slide["ledger"] == ledger.ref(ledger.CONTENT)
        assert slide["ledger_rows"]
        for link in slide["ledger_rows"]:
            assert rows[link["id"]]["status"] != "superseded"
            assert content["rows"][int(link["pointer"].split("/")[-1])]["id"] == link["id"]
