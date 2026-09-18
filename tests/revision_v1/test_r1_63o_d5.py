"""Scientific invariants and execution boundary regressions for D.5."""

import json
import math
import sys
from pathlib import Path

import pytest
from scripts import r1_49g_analyze as analysis
from scripts import r1_49g_inference as inference
from scripts import r1_49o_protocol_matrix as matrix_producer
from scripts import r1_49o_sensitivity as sensitivity
from scripts import r1_58g_operator as operator
from scripts import r1_d9_receipts as d9
from scripts import r1_d10c_endpoints as endpoints

ROOT = matrix_producer.ROOT


def test_d5_only_reorders_coordinates_and_changes_interpretation():
    prior = json.loads((ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json").read_text())
    current = matrix_producer.document()

    def by_id(m):
        return {c["cell_id"]: c for c in m["cells"] + m["extension"]["cells"]}

    before, after = by_id(prior), by_id(current)
    assert before.keys() == after.keys()
    ignored = {
        "block_number",
        "within_block_order",
        "expected_definition_sha256",
        "previous_D4_definition_sha256",
    }
    for cid in before:
        assert {k: v for k, v in before[cid].items() if k not in ignored} == {
            k: v for k, v in after[cid].items() if k not in ignored
        }
    assert current["queue"]["block_sizes"] == [45, 45, 45, 90, 60, 45]
    assert current["queue"]["block_labels"][:3] == [f"primary/random/stable r{i}" for i in range(3)]
    assert len([c for c in current["cells"] if c["block_number"] <= 3]) == 135
    assert all(
        c["condition"] in ("R1_learned_ff", "R1_nonlearned", "v0_stable")
        for c in current["cells"]
        if c["block_number"] <= 3
    )
    for key in (
        "multiplicity",
        "dataset_layouts",
        "full_validation",
        "cap_fidelity_policy",
        "prospective_scope",
        "budget",
    ):
        assert current[key] == prior[key]
    assert current["classifier"]["implementation"] == d9.ref(inference.__file__)


def test_registered_numbers_and_categories_unchanged_t_not_classifier_input():
    grid = [[0.1, 0.12, 0.08, 0.11, 0.09], [0.2] * 5, [0.3] * 5]
    old = inference.cluster_intervals(grid)
    new = inference.cluster_intervals(grid, preliminary=True)
    assert {k: v for k, v in new.items() if k != "preliminary"} == old
    t = new["preliminary"]["t_sensitivity"]
    half = 4.302652729696142 * 0.1 / math.sqrt(3)
    assert t["lower"] == pytest.approx(0.2 - half)
    assert t["upper"] == pytest.approx(0.2 + half)
    assert t["degrees_of_freedom"] == 2 and not t["family_adjusted"]
    row = new["preliminary"]["order_dispersion"][0]
    assert row["minimum"] == 0.08 and row["maximum"] == 0.12 and row["observed_orders"] == 5
    assert row["sample_sd"] == pytest.approx(math.sqrt(0.001 / 4))
    metrics = {
        "RET-GS": new,
        "ES": inference.cluster_intervals([[0] * 5] * 3),
        "LS": inference.cluster_intervals([[0] * 5] * 3),
    }
    label = inference.classify(metrics, admitted=True)
    new["preliminary"]["t_sensitivity"].update(lower=-100, upper=100)
    assert inference.classify(metrics, admitted=True) == label == "positive"


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), True])
def test_missing_order_not_imputed_and_invalid_population_disables_t(bad):
    grid = [[1] * 5 for _ in range(3)]
    grid[1][2] = bad
    display = sensitivity.display(grid)
    assert display["t_sensitivity"]["status"] == "unavailable"
    assert display["order_dispersion"][1]["mean"] is None
    assert display["order_dispersion"][1]["observed_orders"] == 4
    assert (
        sensitivity.display([[1] * 5] * 3, population_valid=False)["t_sensitivity"]["lower"] is None
    )
    assert sensitivity.display([[1] * 5] * 3)["t_sensitivity"]["zero_variance_caveat"]


def test_d5_analysis_preserves_unavailable_63_family_and_displays_every_contrast():
    result = analysis.analyze(matrix_producer.document())
    assert result["analysis_revision"] == "R1-49o_DEC068_DEC069_D5"
    assert result["primary_family"] == inference.FAMILY
    assert sum(c["interval_count"] for c in result["contrasts"]) == 63
    for c in result["contrasts"] + result["historical_pointwise_contrasts"]:
        for metric in c["metrics"].values():
            assert len(metric["preliminary"]["order_dispersion"]) == 3
            assert metric["preliminary"]["t_sensitivity"]["status"] == "unavailable"
    assert all(
        c["classification"] == "unavailable"
        for c in result["contrasts"]
        if c["dataset"] == "mquake"
    )
    text = analysis.markdown(result)
    assert text.index("RET-GS realization estimates") < text.index("Preliminary classification")


def test_endpoint_cli_supplies_identity_used_by_operator(tmp_path, monkeypatch, capsys):
    spec = dict(
        draw_receipt={"path": str(tmp_path / "draw.json")},
        matrix={"path": str(tmp_path / "matrix.json")},
        catalog={},
        role_plan={},
        drift={"path": "unused"},
        extension_admitted=False,
    )
    (tmp_path / "spec.json").write_text(json.dumps(spec))
    (tmp_path / "draw.json").write_text(json.dumps(dict(reservations={})))
    (tmp_path / "matrix.json").write_text(json.dumps(dict(cells=[], full_validation=None)))
    monkeypatch.setattr(endpoints, "verify_bindings", lambda _: None)
    monkeypatch.setattr(endpoints, "read_resource", lambda _: {"evidence_bindings": []})
    import numpy as np

    monkeypatch.setattr(endpoints.np, "load", lambda *a, **k: np.zeros(128 * 128, dtype=np.int32))
    from scripts import r1_d9_layouts

    monkeypatch.setattr(r1_d9_layouts, "from_matrix", lambda _: {})
    monkeypatch.setattr(
        endpoints, "construct", lambda *a, **k: ({}, {}, dict(identities={"cell": "identity"}))
    )
    monkeypatch.setattr(
        sys, "argv", ["endpoints", "construct", "--spec", str(tmp_path / "spec.json"), "--dry-run"]
    )
    endpoints.main()
    output = json.loads(capsys.readouterr().out)
    assert d9.core.content_digest(output["identities"]) == d9.core.content_digest(
        {"cell": "identity"}
    )


@pytest.mark.parametrize(
    "extra",
    [
        [],
        [dict(gate="exhaustive_clearance_review", reason="changed evidence")],
        [
            dict(
                gate="owner_receipts",
                reason="clearance_authorization: open or unapproved receipt; protocol missing",
            )
        ],
    ],
)
def test_operator_preserves_every_other_nested_blocker(tmp_path, monkeypatch, extra):
    from uuid import uuid4

    session = ROOT / "logs/r1_63o/tests" / uuid4().hex
    spec = json.loads((ROOT / "docs/tasks/R1-D9-inputs-v10.json").read_text())
    monkeypatch.setattr(
        operator,
        "journal_read",
        lambda _: [dict(status="complete", step=s, inputs={}) for s in operator.STEPS[:2]],
    )
    monkeypatch.setattr(operator.d9, "read_metadata", lambda b: spec)
    monkeypatch.setattr(operator, "verify_candidate", lambda _: None)
    monkeypatch.setattr(operator, "check_fields", lambda *a: None)
    monkeypatch.setattr(operator, "fields_for", lambda *a: {})
    monkeypatch.setattr(
        operator.d9,
        "prepare",
        lambda *a: (
            dict(
                request_sha256="test",
                blocked=[
                    dict(
                        gate="owner_receipts",
                        reason="clearance_authorization: open or unapproved receipt",
                    )
                ]
                + extra,
            ),
            {},
        ),
    )
    monkeypatch.setattr(operator, "journal_append", lambda *a: None)
    out = operator.run(
        "clearance",
        inputs=ROOT / "docs/tasks/R1-D9-inputs-v10.json",
        candidate=ROOT / "manifests/revision_v1/freeze_candidate_v14.json",
        session=session,
    )
    assert len(out["blocked"]) == len(extra)
    if extra:
        assert extra[0]["reason"] in out["blocked"][0]


@pytest.mark.parametrize("extension", [False, True])
def test_d5_whole_package_native_assembly(tmp_path, monkeypatch, extension):
    from types import SimpleNamespace

    from scripts import r1_63j_production_bundle as bundle
    from scripts.r1_49o_normative_closure import closure
    from scripts.r1_d10a_review import write_new

    from tests.revision_v1.r1_63l_patch_support import install
    from tests.revision_v1.test_r1_63j_production_bundle import assembly_inputs

    matrix = matrix_producer.document()
    original_read = Path.read_text
    old_path = ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json"

    def read_text(path, *a, **k):
        if path == old_path:
            return json.dumps(matrix)
        return original_read(path, *a, **k)

    # Substitute only the declaration, before the existing synthetic receipt
    # producers run; signatures/payloads remain explicitly synthetic fixtures.
    with monkeypatch.context() as m:
        m.setattr(Path, "read_text", read_text)
        root, spec, templates = assembly_inputs.__wrapped__(SimpleNamespace(param=extension))
    install(monkeypatch)
    result = bundle.assemble(spec, templates, root / "d5-staged", normative=closure())
    assert result["verification"]["cells"] == (330 if extension else 285)
    assert not result["published"] and not result["verification"]["model_constructed"]
    doc = d9.read_metadata(result["bundle"])
    matrix_artifact = next(
        a for a in doc["artifacts"] if a["destination"].endswith("/run_matrix_final.json")
    )
    final = d9.read_metadata(matrix_artifact["source"])
    assert final["policy_revision"] == "DEC068_DEC069_D5"
    assert final["queue"]["block_sizes"] == [45, 45, 45, 90, 60, 45]
    assert len([c for c in final["cells"] if c["block_number"] <= 3]) == 135
    write_new(
        ROOT / f"logs/r1_63o/d5-assembly-{root.name}.json",
        dict(result, synthetic=True, extension=extension),
    )


def test_locality_deterministic_complete_stream_exclusion_and_fixed_shortfall():
    from scripts.r1_63o_locality import select

    edits = [dict(prompt="edit now", paraphrases=["future para"]), dict(prompt="future edit")]
    outside = [
        dict(item_id="z", locality_prompts=["future para", "later"]),
        dict(item_id="a", locality_prompts=["edit now", "kept", "future edit", "kept", "second"]),
    ]
    rows, review = select(edits, outside, group="test:0", count=2)
    assert [r["prompt"] for r in rows] == ["kept", "second"]
    assert [r["item_id"] for r in rows] == ["test:0:locality:0", "test:0:locality:1"]
    assert review["excluded_overlap_count"] == 3 and review["eligible_unique"] == 3
    assert select(edits, list(reversed(outside)), group="test:0", count=2) == (rows, review)
    rows, review = select(edits, outside, group="test:0", count=50)
    assert len(rows) == 3 and review["planned"] == 50 and review["shortfall"] == 47
    with pytest.raises(ValueError, match="nonempty"):
        select(edits, [dict(item_id="a", locality_prompts=[""])], group="test:0")


def test_final_v15_seven_step_synthetic_operator_chain_and_assembly_mapping(monkeypatch):
    from tests.revision_v1 import test_r1_63n_assembly_inputs as fixture

    if not (ROOT / "manifests/revision_v1/freeze_candidate_v15.json").exists():
        pytest.skip("canonical v15 emitted after source validation")
    old_read = Path.read_text
    substitutions = {
        ROOT / "docs/tasks/R1-D9-inputs-v9.json": ROOT / "docs/tasks/R1-D9-inputs-v11.json",
        ROOT / "manifests/revision_v1/freeze_candidate_v14.json": ROOT
        / "manifests/revision_v1/freeze_candidate_v15.json",
    }

    def read_text(path, *a, **k):
        return old_read(substitutions.get(path, path), *a, **k)

    with monkeypatch.context() as m:
        m.setattr(Path, "read_text", read_text)
        f = fixture.signed_session.__wrapped__()
    state = fixture.verified(f, monkeypatch)
    assert state["spec"]["matrix"]["path"].endswith("run_matrix_v5_2_D_5.json")
    assert state["spec"]["cost_admission_source_unsigned"]["path"].endswith("receipt-v5.json")
    monkeypatch.setattr(fixture.build, "ROOT", f["root"])
    result = fixture.build.emit(state, f["root"] / "docs/tasks/d5-derived")
    assert result["gates"] == 18 and not result["signed"] and not result["frozen"]
    assert not fixture.build.assembly.inspect(d9.read_metadata(result["inputs"]))["blocked"]


def test_final_live_audit_detects_changed_active_implementation(monkeypatch):
    from scripts import r1_63o_live_audit as live

    candidate = ROOT / "manifests/revision_v1/freeze_candidate_v15.json"
    if not candidate.exists():
        pytest.skip("canonical v15 emitted after source validation")
    inputs = ROOT / "docs/tasks/R1-D9-inputs-v11.json"
    clean = live.audit(inputs, candidate)
    assert not clean["active_binding_errors"]
    target = str(ROOT / "scripts/r1_63o_locality.py")
    original = live.graph.sha
    monkeypatch.setattr(live.graph, "sha", lambda p: "0" * 64 if str(p) == target else original(p))
    changed = live.audit(inputs, candidate)
    assert any(e["binding"]["path"] == target for e in changed["active_binding_errors"])
