"""Independent numerical/scope and unsigned-state review of candidate v14."""

from __future__ import annotations

import copy
import json
import math
from decimal import Decimal
from pathlib import Path

from scripts import r1_49g_analyze as analysis
from scripts import r1_49m_fidelity_policy as fidelity
from scripts import r1_58h_cost_contract as costs
from scripts import r1_d9_receipts as d9
from scripts.r1_63g_freeze_candidate import verify
from scripts.r1_d10a_review import ROOT, write_new


def require(value, reason):
    if not value:
        raise ValueError(reason)


def refusal(function, value):
    try:
        function(value)
    except (ValueError, PermissionError, KeyError) as error:
        return str(error)
    raise ValueError("negative control incorrectly accepted")


def current_rehearsals():
    found = {}
    paths = [
        *(ROOT / "logs/r1_round29").glob("assembler-rehearsal-*.json"),
        *(ROOT / "logs/r1_round36").glob("assembler-extension-*.json"),
    ]
    for path in sorted(paths, key=lambda p: p.stat().st_mtime):
        result = d9.read_metadata(d9.ref(path))
        # Older retained log entries may outlive their temporary staged package.
        # They cannot establish a current proof; both current inventories are
        # still required below, with every surviving binding checked exactly.
        if not Path(result["bundle"]["path"]).exists():
            continue
        doc = d9.read_metadata(result["bundle"])
        freeze_ref = next(
            a["source"]
            for a in doc["artifacts"]
            if a["destination"].endswith("/frozen_stage4.json")
        )
        freeze = d9.read_metadata(freeze_ref)
        assembler = str(ROOT / "scripts/r1_63j_production_bundle.py")
        if freeze["bindings_sha256"].get(assembler) != d9.sha(assembler):
            continue
        cost = d9.read_metadata(freeze["cost_admission"])
        if cost.get("receipt_revision") != 4:
            continue
        matrix_ref = next(
            a["source"] for a in doc["artifacts"] if a["destination"] == doc["matrix"]["path"]
        )
        matrix = d9.read_metadata(matrix_ref)
        if matrix.get("policy_revision") != "DEC066_D4":
            continue
        # Old successful proofs are excluded if any frozen source changed later.
        if any(d9.sha(p) != h for p, h in freeze["bindings_sha256"].items()):
            continue
        for artifact in doc["artifacts"]:
            require(
                d9.ref(artifact["source"]["path"]) == artifact["source"], "staged artifact changed"
            )
            require(
                not Path(artifact["destination"]).exists(), "synthetic final destination published"
            )
        proof = result["verification"]
        require(
            proof["workers"] == 2 and proof["fidelity_watch_verified"],
            "two-worker/watch rehearsal missing",
        )
        require(
            proof["queue_backend_validation"] == "passed" and not result["published"],
            "whole-package proof incomplete",
        )
        recipes = [
            d9.read_metadata(a["source"])
            for a in doc["artifacts"]
            if "/recipes/" in a["source"]["path"]
        ]
        require(
            all(r["full_validation"] == matrix["full_validation"] for r in recipes),
            "extension/core full contract differs",
        )
        found[len(recipes)] = dict(
            proof=d9.ref(path),
            bundle=result["bundle"],
            recipes=len(recipes),
            artifacts=len(doc["artifacts"]),
            synthetic=True,
            workers=2,
            fidelity_watch_verified=True,
            frozen_source_bindings_verified=len(freeze["bindings_sha256"]),
        )
    require(set(found) == {285, 330}, "current typed-v4 D.4 core and extension rehearsals required")
    return found


def run():
    cr = d9.ref(ROOT / "manifests/revision_v1/freeze_candidate_v14.json")
    candidate = d9.read_metadata(cr)
    verified = verify(candidate)
    spec = d9.read_metadata(candidate["d9_inputs"])
    cost = d9.read_metadata(candidate["cost_admission_source_unsigned"])
    matrix = d9.read_metadata(candidate["matrix"])
    require(
        candidate["matrix"] == spec["matrix"] == cost["matrix"], "current matrix binding differs"
    )
    require(
        candidate["protocol"] == spec["protocol"] == cost["protocol"] == matrix["protocol"],
        "D.4 protocol binding differs",
    )
    d9.check_matrix_layout(matrix)
    costs.validate(cost)
    prices = d9.read_metadata(cost["bindings"]["cell_ceilings"])["cells"]
    component_checks = []
    for c in cost["cells"]:
        key = c["condition"] + ":" + c["dataset"]
        e = d9.read_metadata(c["measurement"])
        q = e["cost_components"]
        summed = math.fsum(
            q[k]
            for k in (
                "inherited_nonvalidation_seconds",
                "sampled_all_checkpoints_seconds",
                "endpoints_all_checkpoints_seconds",
                "startup_validation_seconds_estimate",
                "full_outer_seconds",
            )
        )
        require(
            math.isclose(summed, q["component_solo_seconds"], abs_tol=1e-8),
            "independent component sum differs",
        )
        require(
            q["endpoint_checkpoint_count"] == 1
            and q["endpoints_all_checkpoints_seconds"] == q["endpoint_seconds_per_checkpoint"],
            "endpoint cadence overcount",
        )
        require(
            q["solo_seconds"]
            == max(q["component_solo_seconds"], q["measured_whole_process_floor_seconds"]),
            "whole-process floor differs",
        )
        require(
            c["wall_seconds"] == 1.5 * q["solo_seconds"] == prices[key]["ceiling_seconds"],
            "single solo margin differs",
        )
        require(
            q["two_worker_ceiling_seconds"] == 1.15 * c["wall_seconds"],
            "single concurrency adjustment differs",
        )
        component_checks.append(
            dict(key=key, endpoint_kind=e["endpoint_cost_kind"], full_kind=q["full_cost_kind"])
        )
    independently_summed = {}
    for name, cells in [
        ("core", matrix["cells"]),
        ("extension", matrix["extension"]["cells"]),
        ("combined", matrix["cells"] + matrix["extension"]["cells"]),
    ]:
        seconds = sum(
            Decimal(str(prices[c["condition"] + ":" + c["dataset"]]["solo_seconds"])) for c in cells
        )
        hours = float(seconds / Decimal(3600) * Decimal("1.15"))
        require(
            math.isclose(hours, cost["projection"][name]["two_worker_process_hours"], abs_tol=1e-9),
            "independent matrix-weighted projection differs",
        )
        independently_summed[name] = hours
    inference = analysis.analyze(matrix)
    require(
        inference["primary_family"]["family_size"] == 63 and len(inference["contrasts"]) == 21,
        "primary family shrank",
    )
    mq = [r for r in inference["contrasts"] if r["dataset"] == "mquake"]
    require(
        len(mq) == 7 and all(r["classification"] == "unavailable" for r in mq),
        "MQuAKE1000 improperly inferred",
    )
    bad = copy.deepcopy(matrix)
    bad["cells"].pop()
    probes = {"extra_omitted_cell": refusal(d9.check_matrix_layout, bad)}
    bad = copy.deepcopy(cost)
    bad["cells"][0]["wall_seconds"] *= 1.15
    probes["double_concurrency"] = refusal(costs.validate, bad)
    bad = copy.deepcopy(cost)
    bad["receipt_revision"] = 5
    probes["unknown_cost_revision"] = refusal(costs.validate, bad)
    bad = copy.deepcopy(matrix)
    bad["cap_fidelity_policy"]["mean_kl_ceiling_nats"] = 0.01
    probes["changed_fidelity_policy"] = refusal(
        lambda m: fidelity.validate_matrix(m, m["cells"] + m["extension"]["cells"]), bad
    )
    require(
        cost["lead_approved"] is False and not cost["lead_signature"]["name"],
        "cost receipt acquired signature",
    )
    require(
        not (ROOT / "manifests/revision_v1/frozen_stage4.json").exists(),
        "canonical freeze was written",
    )
    for b in spec["receipts"].values():
        if b.get("path"):
            require(d9.read_metadata(b)["lead_approved"] is False, "real receipt gained approval")
    report = dict(
        task="X19",
        verdict="ENGINEERING_AND_COST_REVIEW_PASS_UNSIGNED_POSTSIGNATURE_WORK_REMAINS",
        candidate=cr,
        candidate_verification=verified,
        producer=d9.ref(__file__),
        core_cells=285,
        extension_cells=45,
        prospectively_omitted_cells=75,
        cost_rows=27,
        cost_component_checks=component_checks,
        decimal_recomputed_process_hours=independently_summed,
        projection=cost["projection"],
        primary_intervals=63,
        unavailable_mquake1000_intervals=21,
        typed_v4_whole_package_rehearsals=current_rehearsals(),
        negative_controls=probes,
        unsigned_rehearsal=d9.ref(ROOT / "logs/r1_round36/unsigned-rehearsal-final.json"),
        remaining=candidate["non_signature_blockers"],
        lead_signatures_supplied=False,
        HT4f="waiting for actual signed cost v4",
        gpu_seconds=0,
        model_calls=0,
    )
    return write_new(ROOT / "logs/r1_round36/X19-review.json", report)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
