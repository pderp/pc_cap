"""Current operator candidate inventories exact current bytes and cannot grant launch authority."""

import copy
import json

import pytest
from scripts import r1_63g_freeze_candidate as candidate


@pytest.fixture(scope="module")
def value():
    return json.loads((candidate.ROOT / "manifests/revision_v1/freeze_candidate_v11.json").read_text())


def test_current_candidate_and_three_unsigned_requests(value):
    report = candidate.verify(value)
    assert report["bindings"] >= 700
    assert report["teacher_roles_complete"] and report["context_adjudication_admitted"]
    assert not report["frozen"] and not report["launch_authorized"]
    assert len(report["open_gates"]) == 17
    spec = candidate.d9.read_metadata(value["d9_inputs"])
    for stage in ("clearance", "draw", "seal"):
        form = candidate.d9.read_metadata(spec["receipts"][stage + "_authorization"])
        assert form["inspection_only_request_sha256"] == value["d9_request_sha256"][stage]
        assert form["request_sha256"] is None
        assert form["lead_approved"] is False
    assert spec["freeze_candidate"] == {"path": None, "sha256": None}


@pytest.mark.parametrize("fault", ["authority", "request", "tree", "binding"])
def test_candidate_tamper_refused(value, fault):
    bad = copy.deepcopy(value)
    if fault == "authority":
        bad["launch_authorized"] = True
    elif fault == "request":
        bad["d9_request_sha256"]["clearance"] = "0" * 64
    elif fault == "tree":
        bad["src_pccap_tree_sha256"] = "0" * 64
    else:
        first = next(iter(bad["bindings_sha256"]))
        bad["bindings_sha256"][first] = "0" * 64
    with pytest.raises(ValueError):
        candidate.verify(bad)
