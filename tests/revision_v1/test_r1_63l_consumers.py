"""DEC-063 production consumers: independent contracts, seal/population and real CPU cadences."""

import copy
import json
import uuid
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scripts import r1_49g_analyze as analysis
from scripts import r1_63l_full_validation_contract as contract
from scripts import r1_68f_full_validation as execution
from scripts import r1_75_analysis_stage4_v1 as old_analysis
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_layouts as layouts
from scripts import r1_d9_receipt_core as core
from scripts.r1_58c_draw_seal_preflight import check_receipt
from scripts.r1_d10c_endpoints import construct

from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.r1_63l_patch_support import install
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_r1_58e_rehearsal import TerminatingTinyBase, stages  # noqa: F401
from tests.revision_v1.test_r1_77b_sealed_backend import REPO, make, new_json  # noqa: F401
from tests.revision_v1.test_r1_d10c_endpoints import COUNTS, setup
from tests.revision_v1.test_stage4_cell import CAL


@pytest.fixture
def tiny_contract(monkeypatch):
    root = REPO.parent / "assets/test_scratch/r1_round31" / uuid.uuid4().hex
    root.mkdir(parents=True)
    source = root / "tokens.npy"
    np.save(source, np.array([2, 3, 4, 2, 3, 4, 2], np.int32))
    inventory = root / "lm_sets.json"
    inventory.write_text(
        json.dumps(dict(files=dict(drift_tokens={**contract.ref(source), "shape": [7]})))
    )
    spec = execution.make_spec(inventory=inventory, fixture=True, window_tokens=3)
    monkeypatch.setattr(contract, "production_contract", lambda: copy.deepcopy(spec))
    # Synthetic sealed fixtures intentionally omit the forbidden test_fixture flag.
    # Restrict the execution population exception to TinyBase in this process.
    validate = execution.validate_spec
    monkeypatch.setattr(execution, "validate_spec", lambda m: validate({**m, "test_fixture": True}))
    return spec


def test_real_contract_matches_execution_and_refuses_omission_or_tamper():
    spec = contract.production_contract()
    assert spec == execution.make_spec()
    assert contract.validate(spec) == spec
    for bad in (
        None,
        {},
        {**spec, "expected_positions": 16256},
        {**spec, "trailing_tokens_dropped": 0},
    ):
        with pytest.raises(ValueError, match="DEC-063"):
            contract.validate(bad)


def test_constructor_and_seal_retain_full_population_and_reject_downgrade(tiny_contract):
    reservation, cells, catalog, plan, drift = setup()
    payloads, population, _ = construct(
        reservation,
        cells,
        catalog,
        plan,
        drift,
        counts=COUNTS,
        realizations=2,
        locality_count=1,
        checkpoints=(1, 2),
        full_validation=tiny_contract,
    )
    assert population["full_validation"] == tiny_contract
    assert all(p["full_validation"] == tiny_contract for p in population["cells"].values())
    bad = copy.deepcopy(population)
    del bad["cells"][next(iter(bad["cells"]))]["full_validation"]
    with pytest.raises(ValueError, match="independent analysis population"):
        core.validate_seal(
            reservation,
            cells,
            payloads,
            bad,
            counts=COUNTS,
            realizations=2,
            locality_count=1,
            checkpoints=(1, 2),
            full_validation=tiny_contract,
        )
    bad = copy.deepcopy(drift)
    bad["windows"][0][0] += 1
    with pytest.raises(ValueError, match="bound full-validation prefix"):
        construct(
            reservation,
            cells,
            catalog,
            plan,
            bad,
            counts=COUNTS,
            realizations=2,
            locality_count=1,
            checkpoints=(1, 2),
            full_validation=tiny_contract,
        )


def test_receipt_omission_and_unreviewed_protocol_refuse(tiny_contract):
    spec = dict(full_validation=tiny_contract)
    with pytest.raises(ValueError, match="contract differs"):
        check_receipt("protocol_admission", {}, spec)
    with pytest.raises(ValueError, match="not signed"):
        check_receipt("protocol_admission", dict(full_validation=tiny_contract), spec)


@pytest.mark.parametrize("dataset", ["mquake", "zsre"])
def test_actual_300_1000_cadences_full_and_sampled(
    make,  # noqa: F811
    stages,  # noqa: F811
    tiny_contract,
    monkeypatch,
    dataset,  # noqa: F811
):
    install(monkeypatch)
    monkeypatch.setattr(contract, "ROOT", backend.ROOT.path)
    template = next(
        c
        for c in stages["matrix"]["cells"]
        if c["dataset"] == dataset
        and c["condition"] == "R1_learned_ff"
        and c["realization"] == 0
        and c["order"] == 100
    )
    cid = template["cell_id"]
    data = stages["payloads"][cid]
    # Exercise the actual seal validator over all 360 populations, with only the
    # model/source fixture substituted; no production draw/seal is performed.
    populations = copy.deepcopy(stages["population"])
    populations["full_validation"] = tiny_contract
    for p in populations["cells"].values():
        p["full_validation"] = tiny_contract
    core.validate_seal(
        stages["sealed"],
        [{k: c[k] for k in old_analysis.COORDS} for c in stages["matrix"]["cells"]],
        stages["payloads"],
        populations,
        layout=layouts.production("D"),
        full_validation=tiny_contract,
    )
    matrix_doc = copy.deepcopy(stages["matrix"])
    matrix_doc.update(full_validation=tiny_contract, endpoint_contract_version=1)
    matrix_binding = new_json(backend.ROOT / "docs/tasks/DEC063-matrix.json", matrix_doc)

    def enable(m, frozen, payload):
        m.update(
            checkpoints=template["checkpoints"],
            population_contract_version=2,
            matrix=matrix_binding,
            integrity_batch_edits=100,
            full_validation=tiny_contract,
            full_validation_implementation=contract.ref(contract.__file__),
        )
        protocol = dict(
            schema_version=2,
            mode="stage4_final_protocol",
            lead_approved=True,
            open_gates=[],
            population_decision="DEC-060-option-D",
            dataset_layouts=layouts.production("D"),
            layout_sha256=layouts.digest(layouts.production("D")),
            matrix=matrix_binding,
            extension_admitted=False,
            max_new=32,
            locality_score="bounded_text_equality_DEC053",
            experiment_deadline="2026-10-09",
            full_validation=tiny_contract,
            full_validation_implementation=m["full_validation_implementation"],
        )
        m["protocol"] = new_json(backend.ROOT / "docs/tasks/DEC063-protocol.json", protocol)
        m["population"] = new_json(
            stages["resources"] / ("full-pop-" + dataset + ".json"), populations
        )
        frozen.update(
            protocol=m["protocol"],
            population=m["population"],
            full_validation=tiny_contract,
            full_validation_implementation=m["full_validation_implementation"],
        )
        frozen["bindings_sha256"][m["full_validation_implementation"]["path"]] = m[
            "full_validation_implementation"
        ]["sha256"]

    f = make(
        data_override=data,
        reservations_override=stages["sealed"],
        realization=0,
        order=100,
        change=enable,
    )

    def factory(m):
        cfg = _cfg()
        cfg.fast = replace(cfg.fast, steps=0, delta_steps=0)
        return build_adapter(
            "R1_learned_ff",
            TerminatingTinyBase(),
            Ledger(),
            calibration=CAL,
            synthetic=True,
            revision_config=cfg,
        ), stages["tokenizer"]

    result = backend.execute(
        f["binding"]["path"], f["binding"]["sha256"], code_root=REPO, factory=factory
    )
    assert result["status"] == "complete"
    phases = result["phase_timer_summary"]
    assert phases["drift"]["count"] == len(template["checkpoints"])
    assert phases["full_validation"]["count"] == 1
    declared = dict(
        template,
        full_validation=tiny_contract,
        population=populations["cells"][cid],
        admitted=True,
        result_dir=result["run_dir"],
        manifest_sha256=f["binding"]["sha256"],
        adapter_identity=f["m"]["adapter_identity"],
        code_sha256=f["m"]["code_sha256"],
        payload_sha256=f["m"]["payload"]["sha256"],
    )
    matrix_doc.update(scope="confirmatory", extension={"cells": []})
    matrix_doc["cells"] = [
        declared
        if c["cell_id"] == cid
        else dict(
            c,
            result_dir=None,
            admitted=False,
            full_validation=tiny_contract,
            population=populations["cells"][c["cell_id"]],
        )
        for c in matrix_doc["cells"]
    ]
    report = analysis.analyze(matrix_doc)
    observed = next(c for c in report["cells"] if c["cell_id"] == cid)
    assert observed["artifact_complete"], observed
    assert observed["full_validation_complete"]
    for cp in observed["checkpoints"].values():
        assert cp["secondary"]["sampled_drift"]["status"] == "complete"
    final = observed["checkpoints"][str(template["checkpoints"][-1])]["secondary"][
        "full_validation"
    ]
    assert final["planned"] == final["scored"] == 4
    assert final["overlap_gate"] == "independently_verified"
    assert "ES99_positive" in final["references"]["original"]["loss"]
    assert any(p.endswith(".npz") for p in report["sources_sha256"])
    assert "full validation" in analysis.markdown(report)
    assert "128-window sample (descriptive)" in analysis.markdown(report)
    vector = Path(final["vectors"]["path"])
    saved = vector.read_bytes()
    vector.write_bytes(b"corrupt")
    invalid = next(c for c in analysis.analyze(matrix_doc)["cells"] if c["cell_id"] == cid)
    assert invalid["status"] == "invalid_cell" and not invalid["scientific_admission"]
    vector.write_bytes(saved)
    new_json(
        REPO / f"logs/r1_round31/rehearsal-{dataset}-{uuid.uuid4().hex}.json",
        dict(
            synthetic=True,
            gpu_seconds=0,
            production_admission=False,
            checkpoints=template["checkpoints"],
            full_validation=final,
            sample_phases=phases["drift"]["count"],
            full_phases=1,
            producer_stages=stages["record"],
            result=result,
        ),
    )
