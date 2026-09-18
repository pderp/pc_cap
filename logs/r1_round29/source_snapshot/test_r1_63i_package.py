"""Current package binds repaired semantics without concealing unmeasured work."""

import copy
import json

import pytest
from scripts import r1_58g_operator as operator
from scripts import r1_d9_receipts as d9
from scripts.r1_49j_normative_closure import PROTOCOL
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT


def current():
    c = json.loads((ROOT / "manifests/revision_v1/freeze_candidate_v12.json").read_text())
    return c, d9.read_metadata(c["d9_inputs"])


def test_protocol_matrix_cost_and_closure_agree():
    c, s = current()
    assert c["protocol"] == s["protocol"] == d9.ref(ROOT / PROTOCOL)
    assert d9.read_metadata(s["matrix"])["protocol"] == s["protocol"]
    cost = operator.cost_source(s)
    assert cost["matrix"] == s["matrix"] and cost["protocol"] == s["protocol"]
    assert cost["shared_process_hours"] == 750
    assert s["family_pair_unit_policy_reviewed"]
    assert len(c["normative_closure"]["bindings_sha256"]) == 6
    assert not c["signatures_only"] and c["non_signature_blockers"]
    assert not c["launch_authorized"]


def test_real_candidate_verifier_enforces_normative_closure():
    c, _ = current()
    bad = copy.deepcopy(c)
    del bad["normative_closure"]
    with pytest.raises(ValueError, match="normative closure"):
        verify(bad)
    key = str(ROOT / "docs/R1_stage4_protocol_draft_v5_1.md")
    del c["bindings_sha256"][key]
    with pytest.raises(ValueError, match="normative file"):
        verify(c)


def test_operator_defaults_to_typed_costs_and_refuses_pending_evidence():
    _, s = current()
    fields = operator.fields_for("cost-admit", s)
    assert fields["shared_process_hours"] == 750 and len(fields["cells"]) == 27
    fields["full_endpoint_cost_basis_reviewed"] = True
    with pytest.raises(ValueError, match="cost evidence pending"):
        operator.check_fields("cost-admit", fields, s)
