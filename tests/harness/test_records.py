"""S0-03: outcome codes are a closed string enum, distinct from NaN, documented."""

import json
import math
import re
from pathlib import Path

import pytest

from pccap.harness import records

ROOT = Path(__file__).resolve().parents[2]


def test_codes_are_strings_not_numbers():
    for c in records.OutcomeCode:
        assert isinstance(c.value, str)
        assert not isinstance(c.value, float)
    assert not records.is_code(float("nan"))
    assert not records.is_code(math.nan)
    assert records.is_code("undefined")


def test_outcome_codes_doc_matches_enum():
    doc = (ROOT / "docs" / "outcome_codes.md").read_text()
    documented = set(re.findall(r"^\| `([a-z_]+)` \|", doc, flags=re.M))
    assert documented == set(records.ALL_CODES), documented ^ set(records.ALL_CODES)


def test_decision_record_rejects_nan_and_unknown_codes(tmp_path):
    ok = dict(item_digest="0" * 32, prefix_index=0, round=0, candidate_banks=[1, 2, 3],
              signed_scores={"1": 0.1}, chosen_route=[1], accepted_increment={"1": 0.05},
              loss_before=2.0, loss_after=1.5, codes=["accepted"], cost={})
    rec = records.DecisionRecord(**ok)
    records.append_jsonl(tmp_path / "decisions.jsonl", rec)
    back = records.read_jsonl(tmp_path / "decisions.jsonl")[0]
    from pccap.harness import schema

    schema.validate("decision", back)
    with pytest.raises(ValueError):
        records.DecisionRecord(**{**ok, "loss_after": float("nan")})
    with pytest.raises(ValueError):
        records.DecisionRecord(**{**ok, "codes": ["oops"]})


def test_error_json(tmp_path):
    p = records.write_error_json(tmp_path, ValueError("boom"), "item-1", "tb")
    d = json.loads(p.read_text())
    assert d["status"] == "correctness_failure" and d["item_id"] == "item-1"
