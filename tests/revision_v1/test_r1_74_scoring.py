"""R1-74 proposed patch: actual TinyBase and controlled endpoint generations."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

import pytest
from scripts.r1_74_rescore import preservation_flags, preservation_summary, rescore

from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import CellAdapter, build_adapter
from tests.revision_v1.test_endpoints import Cap, Tokenizer
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_stage4_cell import CAL, TinyTok
from tests.revision_v1.tiny_base import TinyBase

PREVIEW = Path(__file__).resolve().parents[2] / "docs/tasks/R1-74-stage4_assays.preview.py"


def proposed():
    spec = importlib.util.spec_from_file_location("r174_scoring_preview", PREVIEW)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("same", [True, False])
@pytest.mark.parametrize("left,right", [(False, False), (True, False), (False, True), (True, True)])
def test_both_conventions_and_side_flags(same, left, right):
    args = (
        {"generated": "Text", "truncated": left},
        {"generated": "Text" if same else "text", "truncated": right},
    )
    result = preservation_flags(*args)
    assert result == proposed().preservation_flags(*args)
    assert result["preserved"] is same
    assert result["preserved_terminated"] is (same and not (left or right))
    assert result["truncated_pair"] is (left or right)
    assert result["reference_truncated"] is left and result["query_truncated"] is right


def test_actual_tiny_locality_preserves_identical_truncated_text():
    module = proposed()
    adapter = build_adapter(
        "R1_learned_ff",
        TinyBase(),
        Ledger(),
        calibration=CAL,
        revision_config=_cfg(),
        synthetic=True,
    )
    tok = TinyTok()
    tok.encode("outside")
    before = adapter.state_hash()
    report = module.CellAssays(adapter, tok, max_new=2).locality(
        {"rows": [{"item_id": "a", "prompt": "outside"}], "expected_ids": ["a"]}
    )
    assert adapter.state_hash() == before
    assert report["summary"]["preserved_n"] == 1
    assert report["summary"]["preserved_terminated_n"] == 0
    assert report["rows"][0]["truncated_pair"] is True


@pytest.mark.parametrize("max_new,terminated", [(1, False), (4, True)])
def test_near_miss_both_conventions_with_actual_endpoint_pipeline(max_new, terminated):
    module = proposed()
    tok = Tokenizer()
    cap = Cap(tok, {"neighbour?": "old"})
    adapter = CellAdapter(cap, "R1_learned_ff")
    row = {
        "item_id": "n",
        "dataset": "counterfact",
        "edit_item_id": "new-fact",
        "edit_prompt": "edit?",
        "edit_answer": "edited",
        "neighbour_prompt": "neighbour?",
        "neighbour_answer": "old",
    }
    before = adapter.state_hash()
    result = module.CellAssays(adapter, tok, max_new=max_new).challenges(
        "near_miss", {"rows": [row], "expected_ids": ["n"]}, []
    )
    assert adapter.state_hash() == before
    assert result["rows"][0]["status"] == "ok"
    assert result["summary"]["preserved_n"] == 1
    assert result["summary"]["preserved_terminated_n"] == int(terminated)


def test_missing_endpoint_is_not_zero_failure_or_perfect_preservation():
    module = proposed()
    result = module.preservation_summary([], ["a", "b"])
    assert result == preservation_summary([], ["a", "b"])
    assert result["preserved_fraction"] is None and result["unavailable_n"] == 2
    assert all(v is None for v in preservation_flags(None, None, status="unavailable").values())
    with pytest.raises(ValueError):
        preservation_flags({"generated": "x"}, {"generated": "x", "truncated": False})
    with pytest.raises(ValueError):
        preservation_summary([], ["a", "a"])


def test_unavailable_near_miss_still_carries_null_flags():
    module = proposed()
    with patch.object(
        module.EndpointEvaluator, "near_miss", return_value={"status": "unavailable"}
    ):
        evaluator = object.__new__(module._Challenges)
        row = evaluator.near_miss({})
    assert set(preservation_flags(None, None, status="unavailable")) <= row.keys()
    assert row["preserved"] is None


def test_rescoring_does_not_mutate_the_input():
    data = {
        "locality": {
            "rows": [
                {
                    "item_id": "a",
                    "status": "ok",
                    "preserved": False,
                    "reference": {"generated": "same", "truncated": True},
                    "query": {"generated": "same", "truncated": True},
                }
            ],
            "expected_ids": ["a"],
        }
    }
    result = rescore(data)
    assert data["locality"]["rows"][0]["preserved"] is False
    assert result["locality"]["rows"][0]["preserved"] is True
    assert result["locality"]["rows"][0]["stored_preserved"] is False
