"""D.3 complete-family policy and real receipt/vector integration; zero model calls."""

import copy
import json
from uuid import uuid4

import numpy as np
import pytest
from scripts import r1_49g_analyze as reporting
from scripts import r1_49g_inference as inference
from scripts import r1_49m_fidelity_policy as policy
from scripts import r1_49m_normative_closure as norm
from scripts import r1_49m_protocol_matrix as producer
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_68f_full_validation as execution
from scripts import r1_75_analysis_stage4_v1 as analysis

from tests.revision_v1.test_r1_49h_analysis import reduced
from tests.revision_v1.test_r1_63l_vector_analysis import evidence

ASSETS = analysis.ROOT.parent / "assets/runs/pc_cap/R1/rehearsal_fixtures/round33"


@pytest.fixture
def scratch():
    root = ASSETS / uuid4().hex
    root.mkdir(parents=True)
    return root


def test_d3_definitions_and_normative_closure_preserve_scientific_family():
    m = producer.document()
    parent = producer.d9.read_metadata(m["historical_matrix"])
    assert len(m["cells"]) == 360 and len(m["extension"]["cells"]) == 45
    assert len(norm.closure()["bindings_sha256"]) == 8
    for key in (
        "classifier",
        "multiplicity",
        "contrasts",
        "axes",
        "dataset_layouts",
        "budget",
        "full_validation",
    ):
        assert m[key] == parent[key]
    for c, old in zip(analysis.all_cells(m), analysis.all_cells(parent), strict=True):
        assert c["cap_fidelity_policy"] == policy.POLICY
        assert c["expected_definition_sha256"] != old["expected_definition_sha256"]
        assert c["previous_D2_definition_sha256"] == old["expected_definition_sha256"]
        assert not c["admitted"] and not c["launch_allowed"]
        omitted = {
            "cap_fidelity_policy",
            "expected_definition_sha256",
            "previous_D2_definition_sha256",
        }
        assert {k: v for k, v in c.items() if k not in omitted} == {
            k: v for k, v in old.items() if k not in omitted
        }
    analysis.validate_matrix(m)


@pytest.mark.parametrize(
    "fault",
    ["root_missing", "cell_missing", "extension_missing", "changed_limit", "unknown_option"],
)
def test_d3_policy_cannot_downgrade_or_change_threshold(fault):
    m = producer.document()
    if fault == "root_missing":
        del m["cap_fidelity_policy"]
    elif fault == "cell_missing":
        del m["cells"][0]["cap_fidelity_policy"]
    elif fault == "extension_missing":
        del m["extension"]["cells"][0]["cap_fidelity_policy"]
    elif fault == "changed_limit":
        m["cells"][0]["cap_fidelity_policy"]["mean_kl_ceiling_nats"] = 0.01
    else:
        m["cap_fidelity_policy"]["option"] = 2
    with pytest.raises(ValueError, match="DEC-064"):
        analysis.validate_matrix(m)


def test_all_cap_failures_leave_primary_intervals_and_labels_unchanged():
    m, loaded = reduced()
    baseline = inference.primary_contrasts(m, loaded)
    m["cap_fidelity_policy"] = copy.deepcopy(policy.POLICY)
    m["full_validation"] = full.production_contract()
    for cell in m["cells"]:
        cell["cap_fidelity_policy"] = copy.deepcopy(policy.POLICY)
        cell["full_validation"] = m["full_validation"]
        cell["population"]["full_validation"] = m["full_validation"]
        obs = loaded[cell["cell_id"]]
        obs.update(
            primary_metrics_complete=True,
            endpoint_complete=True,
            full_validation_fidelity_passes=False,
        )
        obs["scientific_admission"] = policy.scientific_admission(cell, obs, "confirmatory")
    results = inference.primary_contrasts(m, loaded)
    assert results == baseline
    assert sum(r["interval_count"] for r in results) == 63
    assert sum(r["classification"] == "positive" for r in results) == 14
    assert sum(r["classification"] == "unavailable" for r in results) == 7
    # An unadmitted base/recipe retains its upstream veto, independent of cap fidelity.
    cell = next(
        c for c in m["cells"] if c["dataset"] == "zsre" and c["condition"] == "R1_learned_ff"
    )
    cell["admitted"] = False
    obs = loaded[cell["cell_id"]]
    obs["scientific_admission"] = policy.scientific_admission(cell, obs, "confirmatory")
    assert not obs["scientific_admission"]
    after = inference.primary_contrasts(m, loaded)
    assert sum(r["classification"] == "unavailable" for r in after) == 14
    assert [r["metrics"] for r in after] == [r["metrics"] for r in baseline]


@pytest.mark.parametrize(
    "kl,loss,kl_label,nll_label",
    [
        (0.001, 0.01, "pass", "pass"),
        (0.001000001, 0.01, "fail", "pass"),
        (0.001, 0.010000001, "pass", "fail"),
        (0.1, 0.1, "fail", "fail"),
        (0, -0.1, "pass", "pass"),
    ],
)
def test_both_benchmark_labels_at_thresholds(kl, loss, kl_label, nll_label):
    summary = dict(
        complete=True,
        references={
            "original": dict(kl=dict(mean_signed=kl), loss=dict(mean_signed=loss)),
            "capoff": dict(kl=dict(mean_signed=0), loss=dict(mean_signed=0)),
        },
    )
    b = policy.benchmark(summary)
    assert b["references"]["original"]["mean_kl_label"] == kl_label
    assert b["references"]["original"]["mean_nll_label"] == nll_label
    assert b["references"]["capoff"]["mean_kl_label"] == "pass"
    assert b["references"]["capoff"]["mean_nll_label"] == "pass"
    assert not b["admission_veto"]


def receipt_cell(monkeypatch, root):
    monkeypatch.setattr(full, "ROOT", root)
    monkeypatch.setattr(analysis, "ROOT", root)
    source = root / "tokens.npy"
    np.save(source, np.array([2, 3, 4, 2, 3, 4, 2], np.int32))
    inventory = root / "lm_sets.json"
    inventory.write_text(
        json.dumps(dict(files=dict(drift_tokens={**full.ref(source), "shape": [7]})))
    )
    spec = execution.make_spec(inventory=inventory, fixture=True, window_tokens=3)
    monkeypatch.setattr(full, "production_contract", lambda: copy.deepcopy(spec))
    section, report, vector, _ = evidence(spec)
    coords = dict(condition="R1_learned_ff", dataset="zsre", realization=0, order=100)
    ids = [f"edit-{i}" for i in range(300)]
    rows = [dict(item_id=i, status="ok", paraphrase_n=1, es=1.0, gs=1.0) for i in ids]
    generation = dict(generated="same", truncated=False)
    report.update(
        mode="stage4_sealed_cell",
        history=rows,
        retention=dict(rows=rows),
        locality=dict(
            rows=[dict(item_id="loc", status="ok", reference=generation, query=generation)]
        ),
    )
    report["endpoints"]["full_validation"] = section
    cell = dict(
        coords,
        cell_id=analysis.coordinate_id(coords),
        block_number=1,
        within_block_order=1,
        checkpoints=[300],
        admitted=True,
        result_dir=str(vector.parent.parent),
        manifest_sha256="a" * 64,
        cap_fidelity_policy=copy.deepcopy(policy.POLICY),
        full_validation=spec,
        population=dict(
            item_ids=ids,
            paraphrase_counts=[1] * 300,
            endpoints=dict(locality=["loc"], unseen=[], near_miss=[], revision=[]),
            drift=dict(expected_positions=2),
            full_validation=spec,
        ),
    )
    metadata = dict(
        cell=coords,
        manifest_sha256="a" * 64,
        checkpoints=[300],
        mode="stage4_sealed_cell",
        adapter_identity=dict(base_sha256="tiny", locality_base_sha256="tiny"),
    )
    (vector.parent.parent / "cell.json").write_text(json.dumps(metadata))
    return cell, report, vector


def save_report(cell, report, vector):
    path = vector.parent / "checkpoint-300.json"
    path.write_text(json.dumps(report))
    rec = dict(
        checkpoint=300,
        report=full.ref(path),
        manifest_sha256=cell["manifest_sha256"],
        state_sha256=report["state_sha256"],
        mode="stage4_sealed_cell",
        previous_receipt_sha256=None,
    )
    rec["receipt_sha256"] = analysis.digest(rec)
    path.with_name("checkpoint-300.receipt.json").write_text(json.dumps(rec))
    path.with_name("result.json").write_text(
        json.dumps(
            dict(
                cell={k: cell[k] for k in analysis.COORDS},
                manifest_sha256=cell["manifest_sha256"],
                status="complete",
                completed_checkpoint=300,
                last_receipt_sha256=rec["receipt_sha256"],
            )
        )
    )


@pytest.mark.parametrize(
    "fault,admitted",
    [
        (None, True),
        ("missing_full", False),
        ("missing_primary", False),
        ("upstream_unadmitted", False),
        ("development", False),
        ("legacy", False),
    ],
)
def test_actual_receipts_vectors_and_analysis_policy(monkeypatch, scratch, fault, admitted):
    cell, report, vector = receipt_cell(monkeypatch, scratch)
    if fault == "missing_full":
        del report["endpoints"]["full_validation"]
    elif fault == "missing_primary":
        report["retention"]["rows"] = []
    elif fault == "upstream_unadmitted":
        cell["admitted"] = False
    elif fault == "legacy":
        del cell["cap_fidelity_policy"]
    save_report(cell, report, vector)
    files = analysis.Files()
    out = analysis.load_cell(
        cell, files, "development" if fault == "development" else "confirmatory"
    )
    files.verify()
    assert out["scientific_admission"] is admitted
    if fault is None:
        assert out["full_validation_complete"] and not out["full_validation_fidelity_passes"]
        assert out["cap_fidelity_benchmark"]["references"]["original"]["mean_nll_label"] == "fail"
        assert (
            out["checkpoints"]["300"]["secondary"]["full_validation"]["concentration"]["positions"]
            == 4
        )
        text = "\n".join(policy.report_lines([out]))
        assert "capoff" in text and "original" in text and "fail" in text and "HT-7" in text


def test_corrupt_vectors_remain_invalid_after_veto_removed(monkeypatch, scratch):
    cell, report, vector = receipt_cell(monkeypatch, scratch)
    save_report(cell, report, vector)
    vector.write_bytes(vector.read_bytes() + b"corrupt")
    m = dict(
        name="synthetic",
        scope="confirmatory",
        cells=[cell],
        contrasts=[],
        axes=dict(datasets=[], orders=[]),
        full_validation=cell["full_validation"],
        cap_fidelity_policy=policy.POLICY,
    )
    out = reporting.analyze(m)
    assert out["cells"][0]["status"] == "invalid_cell"
    assert not out["cells"][0]["scientific_admission"]
    assert "hash changed" in out["cells"][0]["reason"]


def test_normative_graph_rejects_mutation_or_undeclared_parent(scratch):
    for path in norm.closure()["bindings_sha256"]:
        source = producer.ROOT / path
        dest = scratch / source.relative_to(producer.ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(source.read_bytes())
    closed = norm.closure(scratch)
    candidate = dict(
        normative_closure=closed, bindings_sha256=copy.deepcopy(closed["bindings_sha256"])
    )
    assert norm.verify(candidate, scratch)["normative_files"] == 8
    d3 = scratch / norm.PROTOCOL
    d3.write_text(d3.read_text() + "\nchanged\n")
    with pytest.raises(ValueError, match="closure differs"):
        norm.verify(candidate, scratch)
    d3.write_text(d3.read_text() + "\n\nWe incorporate [other](other.md).\n")
    with pytest.raises(ValueError, match="undeclared D.3"):
        norm.closure(scratch)
