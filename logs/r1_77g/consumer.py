"""Explicit post-freeze queue-policy consumer; inspection is the default.

This NEW file is outside the locked scripts/src inventory. Original scheduler,
cell recipes, backend, matrix, frozen contract and receipt root remain unchanged.
Actual resume requires a new exact signed form and a globally reconciled D11
snapshot. This module is prepared for review; its existence grants no authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
# isort: off
import pccap  # noqa: E402,F401 -- before JAX-dependent imports
from scripts import r1_58g_operator as op  # noqa: E402
from scripts import r1_77_queue as queue  # noqa: E402
from scripts import r1_77f_scheduler as scheduler  # noqa: E402
from scripts import r1_d12_reprice as reprice  # noqa: E402
# isort: on

FORMAT = "R1-77g-ceiling-amendment-v2"
STEP = "R1-77g-resume"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_ref(binding):
    path = Path(binding["path"]).resolve()
    require(path.is_relative_to(ROOT) and "confirm" not in path.parts,
            "amendment inputs must be repository metadata")
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == binding["sha256"],
            "amendment input hash differs: " + binding["path"])
    return json.loads(raw)


def ref(path):
    return dict(path=str(Path(path).resolve()), sha256=queue.sha(path))


def load_policy(path):
    binding = ref(path)
    proposal = read_ref(binding)
    require(proposal.get("format") == FORMAT and proposal.get("status") == "unsigned_proposal",
            "explicit version-2 amendment proposal required")
    require("recipes" not in proposal, "legacy queue must not silently accept the amendment")
    base = read_ref(proposal["base_bindings"])
    matrix = read_ref(proposal["matrix"])
    require(base["matrix_sha256"] == proposal["matrix"]["sha256"] == proposal["matrix_sha256"], "matrix differs")
    require(base["freeze"] == proposal["freeze"] == matrix["freeze"], "freeze differs")
    require(base["cost_admission"] == proposal["cost_admission"] == matrix["cost_admission"], "base cost admission differs")
    require(matrix["queue_ceiling_contract"] == scheduler.CEILING_DEFINITION, "frozen base ceiling contract differs")
    cells = queue.analysis.all_cells(matrix)
    require(len(cells) == 330 and set(base["recipes"]) == {c["cell_id"] for c in cells}, "full 330-cell inventory required")
    require(all(c.get("full_validation") == matrix["full_validation"] for c in cells), "all affected cells must bear the frozen full-validation contract")
    policy = proposal["ceiling_amendment"]
    require(policy["workers_1_factor"] == 1.0 and policy["workers_2_factor"] == 1.7
            and policy["previous_workers_2_factor"] == 1.15, "unreviewed factor")
    require(policy["application"] == "replace_two_worker_factor_once_on_frozen_solo_whole_cell_ceiling",
            "phase-only or double-counted factor refused")
    require(set(policy["affected_cell_ids"]) == {c["cell_id"] for c in cells}
            and len(policy["affected_cell_ids"]) == len(cells), "amendment must cover exactly the declared cells")
    require(proposal["shared_process_hours"] == matrix["shared_process_hours"] == 750,
            "shared budget cannot change through this amendment")
    require(proposal["consumer"] == ref(__file__), "reviewed consumer implementation differs")
    for binding_ in proposal["implementation_bindings"].values():
        read_ref(binding_) if binding_["path"].endswith(".json") else require(
            ref(binding_["path"]) == binding_, "base implementation differs")
    evidence = read_ref(proposal["evidence"])
    require(evidence["status"] == "verified_block1_cost_evidence", "verified block-1 evidence required")
    for name, sha in evidence["source_bindings_sha256"].items():
        require(queue.sha(name) == sha, "cost evidence changed: " + name)
    return binding, proposal, base, matrix


def project(inventory, matrix, workers):
    """Replace only remaining-ceiling forecasting; preserve every actual charge."""
    factor = {1:1.0, 2:1.7}[workers]
    cells = {c["cell_id"]:c for c in queue.analysis.all_cells(matrix)}
    remaining = [cells[r["cell_id"]]["ceilings"]["wall_seconds"] * factor
                 for r in inventory["queue"]
                 if not r["observed"]["artifact_complete"] and not r["retry"]["exhausted"]]
    cost = dict(inventory["cost"])
    total = None if cost["unknown_attempts"] else cost["known_attempt_hours"] + math.fsum(remaining)/3600
    cost.update(projected_total_hours=total,
                projected_within_ceiling=None if total is None or cost["ceiling_hours"] is None else total <= cost["ceiling_hours"],
                remaining_cell_ceiling_multiplier=factor,
                ceiling_amendment=FORMAT,
                basis=cost["basis"] + " R1-77g replaces the remaining two-worker ceiling factor once; actual historical envelopes are unchanged.")
    return dict(inventory, cost=cost)


def namespace(base_namespace, binding, base_bindings, *, authorization=None, guard=lambda:None):
    """Use the scheduler's existing namespace interface, without module mutation."""
    original = dict(base_namespace)
    amended = dict(original, __file__=__file__)
    def read(path):
        if Path(path).resolve() == Path(binding["path"]).resolve():
            require(original["sha"](path) == binding["sha256"], "amendment bytes changed")
            return base_bindings
        return original["read"](path)
    def factor(workers):
        original["worker_factor"](workers)
        return {1:1.0, 2:1.7}[workers]
    def inventory(matrix, **kwargs):
        return project(original["inventory"](matrix, **kwargs), matrix, kwargs["workers"])
    def validate_watch(matrix):
        guard()
        return original["validate_watch"](matrix)
    def write(path, value):
        row = dict(value, ceiling_amendment=binding, resume_authorization=authorization,
                   base_queue_producer=ref(queue.__file__))
        return original["durable_json"](path, row)
    amended.update(read=read, worker_factor=factor, inventory=inventory,
                   validate_watch=validate_watch, durable_json=write)
    return amended


def check_cutover(binding, proposal, matrix):
    snap = read_ref(binding)
    require(snap.get("task") == "R1-D11" and snap["report_sha256"] == reprice.digest(
        {k:v for k,v in snap.items() if k != "report_sha256"}), "D11 snapshot digest differs")
    require(snap["identity"]["matrix"] == proposal["matrix"] and
            snap["identity"]["receipt_root"] == proposal["receipt_root"] and
            snap["identity"]["workers"] == 2 and snap["identity"]["ceiling_hours"] == 750,
            "cutover accounting identity differs")
    require(snap["boundary_ready"] and not snap["issues"] and not snap["inventory"]["cost"]["unknown_attempts"],
            "globally reconciled idle boundary required; a completed earlier block alone is insufficient")
    require(not snap["cost_ledger"]["uncovered_driver_seconds"] and
            not snap["watch"]["missing_completed_cells"], "cost or watch gaps block cutover")
    reprice.verify_snapshot(dict(d11=snap, inputs=dict(matrix=proposal["matrix"], cutover=binding)))
    return snap


def request(binding, proposal, cutover, stop_after):
    return dict(version=1, step=STEP, bindings=binding, predecessor=proposal["base_bindings"],
                matrix=proposal["matrix"], freeze=proposal["freeze"], cost_admission=proposal["cost_admission"],
                consumer=ref(__file__), implementations=proposal["implementation_bindings"],
                cutover_report=cutover, receipt_root=proposal["receipt_root"], workers=2,
                workers_2_factor=1.7, ceiling_hours=750, min_memory_mib=6144.0,
                stop_after=stop_after, experiment_deadline="2026-10-09")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("inspect", "request", "run"))
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--cutover-report", type=Path)
    parser.add_argument("--stop-after", type=int, choices=range(1,7))
    parser.add_argument("--form", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    binding, proposal, base, matrix = load_policy(args.bindings)
    if args.mode == "inspect":
        require(not args.execute, "inspection cannot execute")
        print(json.dumps(dict(status="unsigned_proposal", affected_cells=330, workers_2_factor=1.7,
                              live_queue_changed=False, launch_authorized=False)))
        return 0
    require(args.cutover_report is not None and args.output is not None, "cutover report and new output directory required")
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / "logs") and not output.exists(), "new output directory under logs required")
    cutover = ref(args.cutover_report)
    check_cutover(cutover, proposal, matrix)
    req = request(binding, proposal, cutover, args.stop_after)
    digest = op.d9.core.content_digest(req)
    if args.mode == "request":
        require(not args.execute, "request preparation cannot execute")
        output.mkdir(parents=True, exist_ok=False)
        op.new_json(output / "request.json", req)
        op.new_json(output / "unsigned-form.json", dict(step=STEP, request_sha256=digest,
                    lead_approved=False, lead_signature=dict(name=None,date=None)))
        print(json.dumps(dict(status="unsigned_request", request_sha256=digest, launch_authorized=False)))
        return 0
    require(args.execute and args.form is not None, "run requires --execute and a new exact signed form")
    form_ref = ref(args.form)
    op.validate_signature(read_ref(form_ref), req)
    # Native queue still enforces the matrix lock, externally held live GPU lease,
    # checkpoint integrity, retries, failure charges, host floors and deadline.
    queue.verify_sealed_matrix(matrix, base)
    require(scheduler.lease_probe(ROOT) is not None, "externally held live GPU lease required")
    check_cutover(cutover, proposal, matrix)
    output.mkdir(parents=True, exist_ok=False)
    authorization = op.new_json(output / "resume-authorization.json", dict(request=req, form=form_ref,
                               request_sha256=digest, predecessor=proposal["base_bindings"], status="authorized"))
    fixed = [binding, proposal["base_bindings"], proposal["evidence"], proposal["consumer"], form_ref,
             *proposal["implementation_bindings"].values()]
    def guard():
        for b in fixed:
            require(ref(b["path"]) == b, "amendment dependency changed during execution")
    ns = namespace(vars(queue), binding, base, authorization=authorization, guard=guard)
    try:
        result = scheduler.run_workers(ns, proposal["matrix"]["path"], binding["path"],
                    receipt_root=proposal["receipt_root"], stop_after=args.stop_after,
                    min_memory_mib=6144.0, ceiling_hours=750, executor=queue.launch,
                    memory_reader=queue.memory_available_mib, workers=2)
    except BaseException as error:
        op.new_json(output / "interrupted.json", dict(authorization=authorization, error=repr(error),
                    outcome="owner reconciliation required; no completed operator step asserted"))
        raise
    op.new_json(output / "result.json", dict(authorization=authorization, queue_result=result))
    print(json.dumps(result))
    return 0 if result["status"] == "selected_blocks_complete" else 2


if __name__ == "__main__":
    raise SystemExit(main())
