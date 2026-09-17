"""Full option-D producer receipts and one sealed CPU TinyBase per actual cadence."""

from __future__ import annotations

import copy
import functools
import json
import uuid
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from scripts import r1_49g_analyze as analysis
from scripts import r1_58c_draw_seal_preflight as preflight
from scripts import r1_77_queue as queue
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_layouts as layouts
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9_receipts as producer
from scripts.r1_d10c_endpoints import construct

from pccap.harness.ledger import Ledger
from pccap.revision_v1.stage4_adapters import build_adapter
from tests.revision_v1.r1_77d_patch_support import install
from tests.revision_v1.test_learner_cpu import _cfg
from tests.revision_v1.test_r1_77b_sealed_backend import (
    REPO,
    FixtureRoot,
    make,  # noqa: F401
    new_json,
)
from tests.revision_v1.test_stage4_cell import CAL, TinyTok
from tests.revision_v1.tiny_base import TinyBase


@pytest.fixture(scope="module")
def stages():
    root = REPO / "logs/r1_round24/rehearsal" / uuid.uuid4().hex
    resources = REPO.parent / "assets/runs/pc_cap/R1/test_scratch/r1_round24" / root.name
    layout = layouts.production("D")
    tok = TinyTok()
    tok.file_sha256 = lambda: "a" * 64
    prompt_ids = tok.encode("p?").tolist()
    answer_ids = tok.encode(" new\n").tolist()
    tok.encode("para?")
    tok.encode(" old\n")
    for i in range(50):
        tok.encode(f"loc{i}?")
    sources = {}
    candidates = {}
    dispositions = []
    plan = {"rows": []}
    for ds in layouts.DATASETS:
        rows = []
        candidates[ds] = []
        for i in range(layout[ds]["demand_subjects"] + 10):
            iid = f"{ds}:{i}"
            row = dict(
                dataset=ds,
                item_id=iid,
                fact_id=iid,
                subject=iid,
                prompt="p?",
                answer="new",
                aliases=["new"],
                paraphrases=["para?"],
                prompt_ids=prompt_ids,
                answer_ids=answer_ids,
                source_record_sha256=layouts.digest([ds, i]),
                locality_prompts=[f"loc{j}?" for j in range(50)],
            )
            rows.append(row)
            meta = dict(
                item_id=iid,
                canonical_subject=iid,
                payload_sha256=layouts.digest(row),
                source_record_sha256=row["source_record_sha256"],
            )
            candidates[ds].append(meta)
            dispositions.append(
                dict(
                    meta,
                    dataset=ds,
                    entity_id=iid,
                    decision="eligible",
                    reasons=[],
                    roles=list(layouts.ROLES),
                    alias_clear=True,
                    context_clear=True,
                    exposure_clear=True,
                    teacher_pass=True,
                    tokens_pass=True,
                    base_tensor_sha256="tiny",
                    tokenizer_sha256="a" * 64,
                )
            )
            plan["rows"].append(
                dict(
                    dataset=ds,
                    item_id=iid,
                    payload_sha256=meta["payload_sha256"],
                    roles=list(layouts.ROLES),
                    near_key="relation:synthetic",
                    revision_versions=[
                        {"version": 1, "answer": "old", "aliases": ["old"]},
                        {"version": 2, "answer": "new", "aliases": ["new"]},
                    ],
                )
            )
        sources[ds] = rows
    source_binding = new_json(resources / "sources.json", sources)
    register = dict(
        schema_version=6,
        candidates=candidates,
        counts={d: {"candidate_subjects": len(sources[d])} for d in layouts.DATASETS},
        synthetic=True,
    )
    register_binding = new_json(root / "docs/tasks/register.json", register)
    evidence = dict(
        policy=core.POLICY,
        register=register_binding,
        base_tensor_sha256="tiny",
        tokenizer_sha256="a" * 64,
        model_limits={"vocabulary": 64, "max_context": 128},
        dispositions=dispositions,
        dataset_layouts=layout,
        evidence_bindings=[source_binding],
        **dict.fromkeys(core.REVIEW_FLAGS, True),
    )
    eb = new_json(resources / "evidence.json", evidence)
    matrix = json.loads((REPO / "manifests/revision_v1/run_matrix_v5_2_option_D.json").read_text())
    mb = new_json(root / "docs/tasks/matrix.json", matrix)
    pb = new_json(root / "docs/tasks/protocol.json", {"synthetic": True, "dataset_layouts": layout})
    catalog = {d: [] for d in layouts.DATASETS}
    cb = new_json(resources / "catalog.json", catalog)
    spec = dict(
        schema_version=3,
        register=register_binding,
        matrix=mb,
        protocol=pb,
        dataset_layouts=layout,
        layout_sha256=layouts.digest(layout),
        receipts={},
        d9={
            s: dict(
                receipt_output=str(root / f"docs/tasks/{s}.receipt.json"),
                resource_output=str(resources / s),
            )
            for s in ("clearance", "draw", "seal")
        },
    )
    spec["d9"]["clearance"]["evidence"] = eb
    spec["d9"]["draw"].update(master_seed=17, composition_catalog=cb)
    common = dict(
        status="closed",
        lead_approved=True,
        synthetic=True,
        register=register_binding,
        contract_version=2,
        dataset_layouts=layout,
        layout_sha256=layouts.digest(layout),
        matrix=mb,
        protocol=pb,
    )
    for name, extra in [
        ("protocol_admission", dict(extension_admitted=False)),
        (
            "rng_admission",
            dict(
                master_seed=17,
                rng_rule=core.RNG_RULE,
                numpy_version=np.__version__,
                paired_order_rule="R1-D9-order-v1; orders100..104; same order for every condition",
                composition_rule="all bound catalog cases with every dependency in the realization edit set",
            ),
        ),
    ]:
        spec["receipts"][name] = new_json(root / f"docs/tasks/{name}.json", {**common, **extra})
    dependencies = producer.implementation_bindings()
    (root / "scripts").mkdir(parents=True)
    (root / "scripts/r1_d9_receipt_core.py").write_bytes(
        (REPO / "scripts/r1_d9_receipt_core.py").read_bytes()
    )
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(producer, "ROOT", FixtureRoot(root))
        mp.setattr(preflight, "ROOT", root)
        mp.setattr(producer, "implementation_bindings", lambda: dependencies)

        def verify_register(value):
            assert value == register  # the only source-loader seam; exact synthetic inventory

        mp.setattr(producer, "verify_register", verify_register)
        mp.setattr(producer, "source_rows", lambda value: copy.deepcopy(sources))

        def authorize(stage):
            auth = {
                **common,
                "operation": stage,
                "request_sha256": producer.contract(spec, stage),
                "cumulative_exposure_current": True,
            }
            spec["receipts"][stage + "_authorization"] = new_json(
                root / f"docs/tasks/{stage}.authorization.json", auth
            )
            return producer.execute(spec, stage)

        spec["receipts"]["joint_clearance"] = authorize("clearance")["receipt"]
        spec["receipts"]["draw_receipt"] = authorize("draw")["receipt"]
        draw = json.loads(Path(spec["receipts"]["draw_receipt"]["path"]).read_text())
        reservations = producer.read_resource(draw["reservations"])
        cells = [{k: c[k] for k in producer.COORDS} for c in matrix["cells"]]
        payloads, population, endpoints = construct(
            reservations,
            cells,
            catalog,
            plan,
            {"windows": [[2, 3, 4]], "expected_positions": 2},
            layout=layout,
        )
        unique = {}
        payload_bindings = {}
        for cid, payload in payloads.items():
            h = layouts.digest(payload)
            if h not in unique:
                unique[h] = new_json(resources / "constructed" / f"{h}.json", payload)
            payload_bindings[cid] = unique[h]
        bundle = new_json(resources / "bundle.json", {"payloads": payload_bindings})
        pop = new_json(resources / "population.json", population)
        spec["d9"]["seal"].update(bundle=bundle, independent_population=pop)
        spec["receipts"]["endpoint_construction"] = new_json(
            root / "docs/tasks/endpoints.receipt.json",
            {
                **common,
                "datasets": list(layouts.DATASETS),
                "draw_receipt": spec["receipts"]["draw_receipt"],
                "reservations": draw["reservations"],
                "bundle": bundle,
                "independent_population": pop,
                "all_roles_disjoint": True,
                "composition_dependencies_closed": True,
            },
        )
        spec["receipts"]["seal_receipt"] = authorize("seal")["receipt"]
        sealed_receipt = json.loads(Path(spec["receipts"]["seal_receipt"]["path"]).read_text())
        sealed = producer.read_resource(sealed_receipt["reservations"])
        # A stale request from before the population layout must be rejected.
        tampered = copy.deepcopy(spec)
        tampered["dataset_layouts"] = layouts.production()
        tampered["layout_sha256"] = layouts.digest(tampered["dataset_layouts"])
        with pytest.raises(ValueError):
            producer.admitted_receipts(tampered, "seal")
    record = new_json(
        root / "summary.json",
        dict(
            synthetic=True,
            layout=layout,
            stages=["clearance", "draw", "endpoint construction", "seal"],
            receipts=spec["receipts"],
            endpoint_missing=endpoints["missing"],
            source_loader_injected=True,
            public_producer_execution_and_authorization_checks=True,
            production_admission=False,
        ),
    )
    return dict(
        root=root,
        resources=resources,
        record=record,
        matrix=matrix,
        matrix_binding=mb,
        payloads=payloads,
        population=population,
        sealed=sealed,
        tokenizer=tok,
    )


class TerminatingTinyBase(TinyBase):
    """Real tiny JAX forwards with a deterministic EOS head for bounded CPU cost."""

    def forward(self, *args, **kwargs):
        result = super().forward(*args, **kwargs)
        logits = np.full_like(np.asarray(result.logits), -5.0)
        logits[..., 63] = 5.0
        return replace(result, logits=logits)


@pytest.mark.parametrize("dataset", ["mquake", "zsre"])
def test_full_actual_cadence_sealed_tinybase(make, monkeypatch, stages, dataset):  # noqa: F811
    patch_mode = install(monkeypatch)
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

    def change(m, frozen, payload):
        m["checkpoints"] = template["checkpoints"]
        m["population_contract_version"] = 2
        m["matrix"] = stages["matrix_binding"]
        m["integrity_batch_edits"] = 100
        m["protocol"] = new_json(
            stages["root"] / f"docs/tasks/final-protocol-{dataset}.json",
            dict(
                schema_version=2,
                mode="stage4_final_protocol",
                lead_approved=True,
                open_gates=[],
                population_decision="DEC-060-option-D",
                dataset_layouts=layouts.production("D"),
                layout_sha256=layouts.digest(layouts.production("D")),
                matrix=stages["matrix_binding"],
                extension_admitted=False,
                max_new=32,
                locality_score="bounded_text_equality_DEC053",
                experiment_deadline="2026-10-09",
            ),
        )
        frozen["protocol"] = m["protocol"]

    # Fixture metadata roots are isolated; its protocol guard accepts its own
    # root only, so copy the final protocol binding into that root below.
    def local_change(m, frozen, payload):
        change(m, frozen, payload)
        doc = json.loads(Path(m["protocol"]["path"]).read_text())
        m["protocol"] = new_json(backend.ROOT / "docs/tasks/versioned-protocol.json", doc)
        frozen["protocol"] = m["protocol"]

    f = make(
        data_override=data,
        reservations_override=stages["sealed"],
        realization=0,
        order=100,
        change=local_change,
    )
    tok = stages["tokenizer"]

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
        ), tok

    directory = backend.OUTPUT_ROOT / backend.cell_name(f["m"], f["binding"]["sha256"])
    m = f["m"]
    declared = {
        **template,
        "result_dir": str(directory),
        "manifest_sha256": f["binding"]["sha256"],
        "admitted": True,
        "population": backend.planned_population(data),
        "adapter_identity": m["adapter_identity"],
        "code_sha256": m["code_sha256"],
        "payload_sha256": m["payload"]["sha256"],
    }
    matrix = copy.deepcopy(stages["matrix"])
    matrix["scope"] = "confirmatory"
    matrix["cells"] = [declared if c["cell_id"] == cid else c for c in matrix["cells"]]
    monkeypatch.setattr(queue, "ROOT", backend.ROOT)
    monkeypatch.setattr(
        backend, "inspect_manifest", functools.partial(backend.inspect_manifest, code_root=REPO)
    )
    queue.recipe_for(
        declared, {"recipes": {cid: {**f["binding"], "backend": backend.backend_binding()}}}
    )
    dry = queue.inventory(matrix)
    assert len(dry["incomplete_cells"]) == 405
    result = backend.execute(
        f["binding"]["path"], f["binding"]["sha256"], code_root=REPO, factory=factory
    )
    assert result["status"] == "complete"
    report = analysis.analyze(matrix)
    observed = next(c for c in report["cells"] if c["cell_id"] == cid)
    assert observed["artifact_complete"] and set(observed["checkpoints"]) == set(
        map(str, template["checkpoints"])
    )
    assert all(
        c["classification"] == "unavailable"
        for c in report["contrasts"]
        if c["dataset"] == "mquake"
    )
    outcome = new_json(f["root"] / f"docs/tasks/round24-analysis-{dataset}.json", report)
    new_json(
        REPO / "logs/r1_round24" / f"rehearsal-{dataset}-{f['root'].name}.json",
        dict(
            synthetic=True,
            dataset=dataset,
            checkpoints=template["checkpoints"],
            attempted_edits=len(data["items"]),
            producer_stages=stages["record"],
            fixture_root=str(f["root"]),
            analysis=outcome,
            driver_result=result["status"],
            queue_dry_incomplete=len(dry["incomplete_cells"]),
            model="JAX TinyBase with EOS test head",
            installed_patch_applied=patch_mode == "installed",
            patch_in_memory=patch_mode == "memory",
            production_admission=False,
            gpu_seconds=0,
        ),
    )
