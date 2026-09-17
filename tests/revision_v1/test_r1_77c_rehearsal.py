"""R1-77c dispatch and reduced-size synthetic admission-to-analysis rehearsal."""

from __future__ import annotations

import copy
import functools

import pytest
from scripts import r1_49g_analyze as final_analysis
from scripts import r1_77_queue as queue
from scripts import r1_77b_sealed_backend as backend
from scripts import r1_d9_receipt_core as d9

from tests.revision_v1.test_r1_77b_sealed_backend import (
    REPO,
    make,  # noqa: F401 -- pytest shared fixture
    new_json,
    observed,
)
from tests.revision_v1.test_r1_d9_receipts import COUNTS, fixture, seal_fixture, validate
from tests.revision_v1.test_stage4_cell import TinyTok


@pytest.mark.parametrize("implementation", [None, "profile_default", "v0_batched_v1"])
def test_sealed_v0_dispatch_requires_explicit_recipe_opt_in(make, monkeypatch, implementation):  # noqa: F811
    f = make(profile="full", condition="v0_stable", drift_implementation=implementation)
    calls = []
    original = backend.donor.run_drift_assay

    def traced(assays, definition, manifest, profile):
        calls.append((manifest.get("drift_implementation"), profile))
        return original(assays, definition, manifest, profile)

    monkeypatch.setattr(backend.donor, "run_drift_assay", traced)
    result = f["execute"]()
    assert result["status"] == "complete"
    assert calls == [(implementation, "full")]
    report, _ = observed(f, result)
    assert report["artifact_complete"]


def test_batch_choice_is_part_of_frozen_recipe_contract(make):  # noqa: F811
    f = make(profile="full", condition="v0_stable")
    changed = copy.deepcopy(f["m"])
    changed["drift_implementation"] = "v0_batched_v1"
    assert backend.contract_digest(changed) != backend.contract_digest(f["m"])
    binding = new_json(f["root"] / "docs/tasks/altered-drift-recipe.json", changed)
    with pytest.raises(ValueError, match="contract inventory"):
        backend.inspect_manifest(binding["path"], binding["sha256"], code_root=REPO)


def test_reduced_clearance_draw_seal_freeze_queue_execution_analysis(make, monkeypatch):  # noqa: F811
    # Synthetic source rows have their own reviewed metadata and token IDs.
    # Small counts enter only pure APIs; production CLI counts remain unchanged.
    register, rows, evidence = fixture()
    tok = TinyTok()
    for ds, values in rows.items():
        for n, row in enumerate(values):
            row["prompt"] = f"p{n % 4}?"
            row["paraphrases"] = [f"p{n % 4} again?"]
            row["prompt_ids"] = tok.encode(row["prompt"]).tolist()
            row["answer_ids"] = tok.encode(" new\n").tolist()
            h = d9.content_digest(row)
            register["candidates"][ds][n]["payload_sha256"] = h
            next(d for d in evidence["dispositions"] if d["item_id"] == row["item_id"])[
                "payload_sha256"
            ] = h
    reviewed, counts = d9.review_candidates(register, rows, evidence, counts=COUNTS, realizations=2)
    reservations, cells, payloads, population = seal_fixture(reviewed)
    identities = validate(reservations, cells, payloads, population)
    # The model fixture's tokenizer must reproduce the reviewed support IDs.
    # Its normal priming order differs, so retain this exact reviewed tokenizer.
    cell = cells[0]
    cid = d9.coordinate_id(cell)
    data = payloads[cid]
    sealed = copy.deepcopy(reservations)
    sealed["mode"] = "content_sealed_fact_reservations"
    f = make(
        data_override=data,
        reservations_override=sealed,
        realization=cell["realization"],
        order=cell["order"],
    )
    original_factory = f["factory"]

    def factory(m):
        cap, _ = original_factory(m)
        # Prime every queried string before execution, preserving support IDs.
        for r in data["pool_rows"]:
            tok.encode(r["prompt"])
            for p in r["paraphrases"]:
                tok.encode(p)
        tok.encode("loc?")
        tok.file_sha256 = lambda: "a" * 64
        return cap, tok

    directory = backend.OUTPUT_ROOT / backend.cell_name(f["m"], f["binding"]["sha256"])
    m = f["m"]
    declared = {
        **m["cell"],
        "cell_id": d9.coordinate_id(m["cell"]),
        "block_number": 1,
        "within_block_order": 1,
        "result_dir": str(directory),
        "manifest_sha256": f["binding"]["sha256"],
        "checkpoints": m["checkpoints"],
        "admitted": True,
        "population": backend.planned_population(data),
        "adapter_identity": m["adapter_identity"],
        "code_sha256": m["code_sha256"],
        "payload_sha256": m["payload"]["sha256"],
    }
    matrix = {
        "schema_version": 1,
        "name": "R1-77c synthetic reduced rehearsal",
        "scope": "confirmatory",
        "cells": [declared],
        "contrasts": [],
        "axes": {"datasets": [cell["dataset"]]},
    }
    monkeypatch.setattr(queue, "ROOT", backend.ROOT)
    monkeypatch.setattr(
        backend, "inspect_manifest", functools.partial(backend.inspect_manifest, code_root=REPO)
    )
    binding = {
        "recipes": {declared["cell_id"]: {**f["binding"], "backend": backend.backend_binding()}}
    }
    queue.recipe_for(declared, binding)
    dry = queue.inventory(matrix)
    assert len(dry["incomplete_cells"]) == 1
    assert not directory.exists()
    result = backend.execute(
        f["binding"]["path"], f["binding"]["sha256"], code_root=REPO, factory=factory
    )
    assert result["status"] == "complete"
    analyzed = final_analysis.analyze(matrix)
    assert analyzed["cells"][0]["artifact_complete"]
    assert analyzed["analysis_revision"] == "R1-49g_DEC057_DEC058_DEC059"
    assert analyzed["primary_family"]["status"] == "unavailable_nonregistered_matrix"
    # Publish a compact, replayable receipt in this test's isolated log root.
    new_json(
        f["root"] / "docs/tasks/d9-synthetic-stage-evidence.json",
        {
            "synthetic": True,
            "clearance_counts": counts,
            "reservation_hash": d9.content_digest(reservations),
            "seal_identities": identities,
            "production_admission": False,
        },
    )
    new_json(f["root"] / "docs/tasks/rehearsal-queue-dry.json", dry)
    new_json(f["root"] / "docs/tasks/rehearsal-analysis.json", analyzed)
    new_json(
        REPO / "logs/r1_round21" / ("rehearsal-" + f["root"].name + ".json"),
        {
            "synthetic": True,
            "fixture_root": str(f["root"]),
            "resources": str(f["resources"]),
            "stages": [
                "clearance validation",
                "independent role/realization draw",
                "paired orders",
                "seal validation",
                "synthetic freeze candidate",
                "synthetic freeze",
                "queue dry-run",
                "sealed TinyBase execution",
                "R1-49g analysis",
            ],
            "full_cli_authorization_rehearsal": False,
            "note": "Reduced-size pure producer APIs plus actual sealed admission/execution; production CLI authorization/writer refusal and receipt schemas have separate tests. No real scientific admission.",
        },
    )
