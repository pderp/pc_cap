"""Round-26 published drafts cannot silently become launch or semantic approval."""
import copy
import json
from pathlib import Path

import pytest
from scripts.r1_58c_draw_seal_preflight import check_receipt
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_63h_refresh import external_dependencies
from scripts.r1_d9_receipts import contract
from scripts.r1_d9e_near_family import CONTRACT

ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / name).read_text())


def test_preview_identity_and_unsigned_request_previews():
    candidate = read("manifests/revision_v1/freeze_candidate_v13.json")
    verify(candidate)
    spec = read(candidate["d9_inputs"]["path"])
    assert spec["near_miss_family_contract"] == CONTRACT
    for stage in ("clearance", "draw", "seal"):
        auth = read(spec["receipts"][stage + "_authorization"]["path"])
        assert auth["request_sha256"] is None and auth["lead_approved"] is False
        assert auth["inspection_only_request_sha256"] == contract(spec, stage)
    assert not candidate["launch_authorized"] and candidate["cost_admission_receipt"] is None


def test_family_omission_and_unreviewed_protocol_cannot_pass():
    spec = read("docs/tasks/R1-D9-inputs-v8.json")
    receipt = read(spec["receipts"]["protocol_admission"]["path"])
    receipt.update(status="closed", lead_approved=True)
    with pytest.raises(ValueError, match="not signed"):
        check_receipt("protocol_admission", receipt, spec)
    receipt["near_family_reviewed"] = True
    check_receipt("protocol_admission", receipt, spec)
    for mutation in [lambda r: r.pop("near_miss_family_contract"),
                     lambda r: r["near_miss_family_contract"].update(family="substitute")]:
        bad = copy.deepcopy(receipt)
        mutation(bad)
        with pytest.raises(ValueError, match="contract differs"):
            check_receipt("protocol_admission", bad, spec)


def test_final_refresh_requires_eight_completed_profiles_and_plan(tmp_path):
    plan = tmp_path / "plan.md"
    profiles = [dict(condition=str(i), status="complete") for i in range(8)]
    assert external_dependencies(profiles, plan) == ["execution_plan_v2"]
    plan.write_text("synthetic plan")
    profiles[4]["status"] = "pending"
    assert external_dependencies(profiles, plan) == ["chain_Q:4"]
    with pytest.raises(ValueError, match="eight"):
        external_dependencies(profiles[:7], plan)
