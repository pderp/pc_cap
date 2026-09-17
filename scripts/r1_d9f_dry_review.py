"""One declared diagnostic seed, two proposed modes; never an authorized draw."""

from __future__ import annotations

import json

from scripts import r1_d9_receipt_core as core
from scripts import r1_d9_receipts as d9
from scripts import r1_d9f_allocation as allocation
from scripts.r1_d9e_near_family import pair_reserved
from scripts.r1_d10a_review import ROOT, write_new
from scripts.r1_d10b_teacher_review import verify_bindings

SEED = 20260917  # diagnostic only, declared before inspecting either mode


def run():
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v4.json"))
    binding = spec["d9"]["clearance"]["evidence"]
    evidence = d9.read_resource(binding)
    verify_bindings(evidence["evidence_bindings"])
    register = d9.read_metadata(spec["register"])
    pool, counts = core.review_candidates(
        register, d9.source_rows(register), evidence, layout=spec["dataset_layouts"]
    )
    reports, backbone = {}, None
    for mode in ("independent", "family_coordinated"):
        result = allocation.allocate(
            pool,
            seed=SEED,
            register_sha256=spec["register"]["sha256"],
            layout=spec["dataset_layouts"],
            mode=mode,
        )
        reservation = allocation.reservation_document(result, spec["register"])
        core.audit_reservations(reservation, layout=spec["dataset_layouts"])
        allocation.audit(reservation)
        nonnear = [
            g
            for g in result["allocations"]
            if g["role"] not in (allocation.SUPPORT, allocation.NEIGHBOUR)
        ]
        if backbone is None:
            backbone = nonnear
        elif backbone != nonnear:
            raise ValueError("non-near roles changed across modes")
        cells = []
        groups = {
            (g["dataset"], g["realization"], g["role"]): g["records"] for g in result["allocations"]
        }
        for dataset in core.DATASETS:
            for real in spec["dataset_layouts"][dataset]["realizations"]:
                section = pair_reserved(
                    groups[dataset, real, allocation.SUPPORT],
                    groups[dataset, real, allocation.NEIGHBOUR],
                    [f"{dataset}:{real}:near:{i}" for i in range(100)],
                    dataset=dataset,
                )
                cells.append(
                    dict(
                        dataset=dataset,
                        realization=real,
                        planned=100,
                        matched=len(section["rows"]),
                        missing=len(section["missing"]),
                    )
                )
        # Deliberately omit executable unsealed_fact_reservations mode and publication bindings.
        resource = dict(
            diagnostic_only=True,
            authorizes_nothing=True,
            seed=SEED,
            mode=mode,
            selected_ids=[
                dict(
                    dataset=g["dataset"],
                    realization=g["realization"],
                    role=g["role"],
                    items=[r["item_id"] for r in g["records"]],
                )
                for g in result["allocations"]
            ],
            baseline_streams=result["rng_substreams"],
            pair_streams=result.get("near_pair_receipts"),
            allocator=d9.ref(allocation.__file__),
            evidence=binding,
        )
        ref = write_new(
            ROOT.parent / f"assets/runs/pc_cap/R1/r1_d9f/round27/diagnostic-{mode}.json", resource
        )
        reports[mode] = dict(
            cells=cells, resource=ref, nonnear_identity=core.content_digest(nonnear)
        )
    report = dict(
        task="R1-D9f",
        seed=SEED,
        seed_is_not_lead_master_seed=True,
        selection="single predeclared diagnostic seed; no search or redraw",
        interpretation="One simulated allocation, not an availability probability or final draw. Multiple pairs per family allowed; planned100 is cases.",
        counts=counts,
        modes=reports,
        contract=allocation.CONTRACT,
        inputs=d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v4.json"),
        evidence=binding,
        producer=d9.ref(__file__),
        actual_draws=0,
        signatures=0,
        seals=0,
        gpu_seconds=0,
        family_mode_activated=False,
        lead_decision_pending="DEC-062",
    )
    write_new(ROOT / "logs/r1_round27/r1-d9f-real-pool.json", report)
    print(json.dumps({k: v["cells"] for k, v in reports.items()}, indent=2))


if __name__ == "__main__":
    run()
