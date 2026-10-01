"""Option R supplemental consumer: CPU plan; explicit Tuesday approval to run.

The installed sealed execution engine is reused in a private function namespace.
Only admission, output namespace, deadline and supplemental labels differ. The
original recipes, primary freeze, acquisition, endpoints and scorer are unchanged.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import inspect
import json
import math
import os
import subprocess
import sys
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from pathlib import Path

from scripts import ht8_fidelity_watch as watch
from scripts import r1_77_queue as queue
from scripts import r1_77b_sealed_backend as native
from scripts.r1_68b_integrity_runtime import durable_json
from scripts.r1_75_analysis_stage4_v1 import coordinate_id
from scripts.r1_77f_scheduler import failure_class, lease_probe

from aw.pc_historical import bind
from aw.pc_v0 import CUTOFF, blocking_cuda_processes
from pccap.revision_v1 import stage4_cell as core

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "manifests/additional_work/run_matrix_R_v1.json"
PREPARATION = ROOT / "logs/additional_work/R/preparation-v1.json"
OUTPUT = ROOT / "results/additional_work/R"
RESOURCES = ROOT.parent / "assets/runs/pc_cap/R1/additional_work/R/execution"
RECEIPTS = ROOT / "logs/additional_work/R/queue"
MODE = "additional_work_R_cell"
BANNER = "supplemental Option R, realization 3; excluded from primary inference"
RETAINED = (
    "adapter_identity",
    "construction",
    "calibration",
    "checkpoints",
    "code_sha256",
    "full_validation",
    "full_validation_implementation",
    "integrity_batch_edits",
    "integrity_driver_bindings",
    "integrity_profile",
    "max_new",
    "tokenizer_sha256",
)


def ref(path):
    return dict(path=str(Path(path).resolve()), sha256=native.sha(path))


def checked(binding):
    path = Path(binding["path"]).resolve()
    if native.sha(path) != binding["sha256"]:
        raise ValueError("bound input changed: " + str(path))
    return json.loads(path.read_bytes())


def deadline_check(now=None):
    if (time.time() if now is None else now) >= CUTOFF:
        raise TimeoutError("October 9, 17:00 EDT experimental cutoff reached")


def sources():
    paths = [
        Path(__file__),
        Path(native.__file__),
        Path(watch.__file__),
        ROOT / "aw/pc_historical.py",
        ROOT / "aw/pc_v0.py",
        ROOT / "requirements.lock",
    ]
    paths += sorted((ROOT / "scripts").glob("*.py"))
    paths += sorted((ROOT / "src/pccap").rglob("*.py"))
    return {str(p): native.sha(p) for p in paths}


def matrix():
    prepared = json.loads(PREPARATION.read_bytes())
    m = checked(prepared["matrix"])
    if (
        Path(prepared["matrix"]["path"]).resolve() != MATRIX
        or m["mode"] != "additional_work_R_content_sealed"
    ):
        raise ValueError("AW-R0 prepared matrix required")
    for key in ("population", "reservations", "producer", "parent_freeze"):
        binding = m[key]
        if key != "producer":
            checked(binding)
        elif native.sha(binding["path"]) != binding["sha256"]:
            raise ValueError("allocation producer changed")
    coords = {(c["condition"], c["dataset"], c["realization"], c["order"]) for c in m["cells"]}
    expected = {
        (c, d, 3, o)
        for c in ("R1_learned_ff", "R1_nonlearned", "v0_stable")
        for d in ("zsre", "counterfact")
        for o in range(100, 105)
    }
    if len(m["cells"]) != 30 or coords != expected or m["primary_inference_inclusion"] is not False:
        raise ValueError("exact supplemental 30-cell design required")
    return m


def recipe(cell, m, *, payload=False):
    r = checked(cell["recipe"])
    coord = {k: cell[k] for k in ("condition", "dataset", "realization", "order")}
    if (
        r["mode"] != MODE
        or r["cell"] != coord
        or coordinate_id(coord) != cell["cell_id"]
        or r["checkpoints"] != [100, 300, 1000]
        or r["payload"] != cell["payload"]
        or r["population"] != checked(m["population"])["cells"][cell["cell_id"]]
        or r["reservations"] != m["reservations"]
        or r["parent_freeze"] != m["parent_freeze"]
        or r["producer"] != m["producer"]
        or r["ceilings"] != cell["ceilings"]
        or r["admission"].get("content_sealed") is not True
        or r["result_dir"] != str(OUTPUT / cell["cell_id"])
    ):
        raise ValueError("supplemental recipe/matrix/population identity differs")
    parent = native.inspect_manifest(r["parent_recipe"]["path"], r["parent_recipe"]["sha256"])
    if any(r[k] != parent[k] for k in RETAINED):
        raise ValueError("supplemental science differs from frozen parent")
    if parent["cell"] != dict(coord, realization=0) or parent["freeze"] != r["parent_freeze"]:
        raise ValueError("wrong parent coordinate/freeze")
    cap = cell["ceilings"]
    if cap["factor"] != 1.7 or not math.isclose(
        cap["wall_seconds"], 1.7 * cap["mean_process_seconds"], rel_tol=1e-12
    ):
        raise ValueError("cell ceiling must apply factor 1.7 exactly once")
    data = None
    if payload:
        data = checked(r["payload"])
        supplemental_validator()(r, data)
        native.full_contract.sample(r["full_validation"], data["endpoints"]["drift"])
        population = dict(native.planned_population(data), full_validation=r["full_validation"])
        if (
            population != r["population"]
            or core.content_digest(data) != r["admission"]["payload_content_sha256"]
        ):
            raise ValueError("supplemental payload differs from independent population")
    return r, data


def supplemental_validator():
    """Use the installed membership/order/content checks with the AW-R seal label."""
    source = inspect.getsource(core.validate_payload)
    old = '"content_sealed_fact_reservations"'
    if source.count(old) != 1:
        raise ValueError("reservation admission seam changed")
    namespace = dict(core.validate_payload.__globals__)
    exec(
        compile(
            source.replace(old, '"aw_r_content_sealed_reservations"'),
            "<AW-R reservation validator>",
            "exec",
        ),
        namespace,
    )
    return namespace["validate_payload"]


def load(path, expected_sha256, *, code_root=None, allow_sealed=False):
    if allow_sealed is not True or (code_root is not None and Path(code_root).resolve() != ROOT):
        raise PermissionError("explicit supplemental execution on installed tree required")
    m = matrix()
    matches = [
        c
        for c in m["cells"]
        if c["recipe"] == dict(path=str(Path(path).resolve()), sha256=expected_sha256)
    ]
    if len(matches) != 1:
        raise ValueError("recipe is not one of the 30 prepared supplemental cells")
    r, payload = recipe(matches[0], m, payload=True)
    # The frozen engine records these metadata fields but never uses them to
    # admit a cell. Parent freeze is provenance only; it does not authorize R.
    r = dict(
        r,
        backend=dict(module="aw.r_run", **ref(__file__)),
        freeze=r["parent_freeze"],
        admission_scope="supplemental; separate operator approval, not primary freeze",
    )
    return r, payload


def engine(loader=load, *, output_root=OUTPUT):
    writer = bind(native.write_json, MODE=MODE, BANNER=BANNER)
    execute = bind(
        native._run_sealed_cell,
        load_sealed_cell=loader,
        OUTPUT_ROOT=output_root,
        cell_name=lambda m, h: coordinate_id(m["cell"]),
        write_json=writer,
        deadline_check=deadline_check,
        BANNER=BANNER,
    )

    def run(path, expected_sha256, adapter, tokenizer, **kwargs):
        manifest, _ = loader(
            path,
            expected_sha256,
            code_root=kwargs.get("code_root"),
            allow_sealed=kwargs.get("allow_sealed", False),
        )
        directory = Path(kwargs["output_root"]) / coordinate_id(manifest["cell"])
        if any(
            json.loads(p.read_bytes()).get("status") == "complete"
            for p in directory.glob("attempt-*/result.json")
        ):
            raise ValueError("supplemental cell already complete")
        return execute(path, expected_sha256, adapter, tokenizer, **kwargs)

    return run


def watch_inspector():
    # Two explicit label/admission changes; all receipt, vector and scoring
    # checks remain the installed function's exact code. No global mutation.
    source = inspect.getsource(watch.inspect)
    before = '("stage4_development_cell", "stage4_sealed_cell")'
    after = '("stage4_development_cell", "stage4_sealed_cell", "additional_work_R_cell")'
    scope = 'scope="development" if mode == "stage4_development_cell" else "confirmatory",'
    if source.count(before) != 1 or source.count(scope) != 1:
        raise ValueError("fidelity-watch extension seam changed; review required")
    source = source.replace(before, after).replace(
        scope,
        'scope="supplemental" if mode == "additional_work_R_cell" else ("development" if mode == "stage4_development_cell" else "confirmatory"),',
    )
    namespace = dict(watch.inspect.__globals__)
    exec(compile(source, "<AW-R supplemental fidelity watch>", "exec"), namespace)
    return namespace["inspect"]


def observe(cell):
    directory = OUTPUT / cell["cell_id"]
    endings = [
        p
        for p in directory.glob("attempt-*/result.json")
        if json.loads(p.read_bytes()).get("status") == "complete"
    ]
    if len(endings) != 1:
        raise ValueError("exactly one completed supplemental result required")
    return watch_inspector()(cell["recipe"], endings[0])


def schedule(cells, field):
    workers = [0.0, 0.0]
    rows = []
    for cell in cells:
        slot = min(range(2), key=lambda i: workers[i])
        start = workers[slot]
        workers[slot] += cell["ceilings"][field]
        rows.append(
            dict(
                cell_id=cell["cell_id"],
                worker=slot,
                start_hours=start / 3600,
                finish_hours=workers[slot] / 3600,
            )
        )
    return dict(wall_hours=max(workers) / 3600, rows=rows)


def plan(*, validate_payloads=False):
    m = matrix()
    for c in m["cells"]:
        recipe(c, m, payload=validate_payloads)
    return dict(
        mode=MODE,
        matrix=ref(MATRIX),
        cells=30,
        workers=2,
        memory_floor_mib=6144,
        projected_process_hours=sum(c["ceilings"]["mean_process_seconds"] for c in m["cells"])
        / 3600,
        summed_cell_ceiling_hours=sum(c["ceilings"]["wall_seconds"] for c in m["cells"]) / 3600,
        projected_schedule=schedule(m["cells"], "mean_process_seconds"),
        ceiling_schedule=schedule(m["cells"], "wall_seconds"),
        portfolio_wall_hours=30,
        cutoff="2026-10-09 17:00 America/New_York",
        cutoff_epoch=CUTOFF,
        cost_note="Two-worker overlap is a schedule estimate, not measured speedup. The original 30-wall-hour portfolio allowance is not increased. Ceilings are applied once per cell across both attempts.",
        retry="at most one clean-checkpoint cell retry; host failure, torn journal or unknown cost stops admission",
        primary_inference_inclusion=False,
        payloads_validated=validate_payloads,
        launch_authorized=False,
        run_requires="Tuesday lead decision supplied with --approved-decision PATH",
        sources_sha256=sources(),
        model_calls=0,
    )


def approve(path):
    """Record an existing lead decision, never manufacture one in this consumer."""
    p = Path(path).resolve()
    if not p.is_relative_to(ROOT / "docs") or not p.is_file() or not p.read_text().strip():
        raise ValueError("existing lead decision document under docs required")
    return ref(p)


def attempt_files(directory):
    return {
        str(p.resolve()): native.sha(p)
        for p in sorted(Path(directory).glob("attempt-*/**/*"))
        if p.is_file()
    }


def status(cell, matrix_hash, *, reconciled=True):
    c = dict(cell, result_dir=str(OUTPUT / cell["cell_id"]))
    cost = queue.charged_cost(c, queue.cell_cost(c["result_dir"]), RECEIPTS, matrix_hash)
    starts = [p for p in RECEIPTS.glob("*/" + cell["cell_id"] + "/*/start.json")]
    attempts = len(starts)
    complete = any(
        json.loads(p.read_bytes()).get("status") == "complete"
        for p in Path(c["result_dir"]).glob("attempt-*/result.json")
    )
    terminal = None
    path = OUTPUT / cell["cell_id"] / "reconciliation.json"
    if reconciled and path.exists():
        rec = json.loads(path.read_bytes())
        if (
            rec["matrix_sha256"] != matrix_hash
            or rec["cell_id"] != cell["cell_id"]
            or rec["recipe"] != cell["recipe"]
            or rec["status"] != "incomplete_by_ceiling"
            or rec["retry_budget_seconds"] != 0
            or rec["charged_process_wall_seconds"] != cost["known_attempt_wall_seconds"]
            or rec["process_receipts"] != cost["process_receipts"]
            or rec["unknown_attempts_closed"] != cost["unknown_attempts"]
            or rec["attempt_files"] != attempt_files(c["result_dir"])
            or cost["known_attempt_wall_seconds"] < cell["ceilings"]["wall_seconds"]
            or complete
        ):
            raise ValueError("reconciliation no longer matches cell evidence")
        cost["reconciled_unknown_attempts"] = cost["unknown_attempts"]
        cost["unknown_attempts"] = []
        terminal = rec["status"]
    return dict(cost=cost, dispatches=attempts, complete=complete, terminal=terminal)


def reconcile(cell_id, *, execute=False):
    """Close accounting only. Preserve the torn journal and all scientific artifacts."""
    session_cost()  # Refuse reconciliation while an Option R segment is open.
    m = matrix()
    cell = next((c for c in m["cells"] if c["cell_id"] == cell_id), None)
    if cell is None:
        raise ValueError("cell is not in the Option R matrix")
    current = status(cell, native.sha(MATRIX))
    target = OUTPUT / cell_id / "reconciliation.json"
    if current["terminal"]:
        return json.loads(target.read_bytes())
    st = status(cell, native.sha(MATRIX), reconciled=False)
    cost = st["cost"]
    if st["complete"] or cost["known_attempt_wall_seconds"] < cell["ceilings"]["wall_seconds"]:
        raise ValueError("reconciliation requires an incomplete cell with exhausted ceiling")
    covered = set()
    for binding in cost["process_receipts"]:
        finish = checked(binding)
        covered.update(finish["new_attempts"])
        # A completed subprocess envelope is required even if the driver was killed.
        session = Path(binding["path"]).parents[2]
        if not (session / "session-finish.json").exists():
            raise ValueError("owning session must be stopped before reconciliation")
    if not cost["process_receipts"] or not set(cost["unknown_attempts"]).issubset(covered):
        raise ValueError("unknown attempt not covered by a closed process envelope")
    rec = dict(
        schema="aw-r-accounting-reconciliation-v1",
        status="incomplete_by_ceiling",
        cell_id=cell_id,
        matrix_sha256=native.sha(MATRIX),
        recipe=cell["recipe"],
        charged_process_wall_seconds=cost["known_attempt_wall_seconds"],
        process_receipts=cost["process_receipts"],
        unknown_attempts_closed=cost["unknown_attempts"],
        attempt_files=attempt_files(OUTPUT / cell_id),
        retry_budget_seconds=0,
        additional_charge_seconds=0,
        primary_inference_inclusion=False,
        scientific_completion=False,
        note="Accounting closure only. Torn phases and checkpoint evidence remain untouched; no successful phase or final endpoint is synthesized.",
    )
    if execute:
        durable_json(target, rec)
        status(cell, native.sha(MATRIX))
    return rec


def session_cost():
    """Count closed execution segments once; never charge idle time between resumes."""
    total = 0.0
    for start in sorted(RECEIPTS.glob("*/session-start.json")):
        for p in [start, *sorted(start.parent.glob("resumes/*/session-start.json"))]:
            end = p.with_name("session-finish.json")
            if not end.exists():
                raise ValueError("unfinished queue session needs owner reconciliation")
            value = json.loads(p.read_bytes())
            if value["matrix"] != ref(MATRIX):
                raise ValueError("session matrix differs")
            seconds = json.loads(end.read_bytes())["elapsed_wall_seconds"]
            if isinstance(seconds, bool) or not math.isfinite(seconds) or seconds < 0:
                raise ValueError("invalid session wall cost")
            total += seconds
    return total


def resume_inventory(*, defer_classes=()):
    m = matrix()
    available = {c["condition"] + ":" + c["dataset"] for c in m["cells"]}
    if not set(defer_classes).issubset(available):
        raise ValueError("unknown condition:dataset deferral")
    groups = dict(completed=[], incomplete=[], deferred=[], pending=[])
    process_seconds = 0.0
    for c in m["cells"]:
        st = status(c, native.sha(MATRIX))
        process_seconds += st["cost"]["known_attempt_wall_seconds"]
        if st["cost"]["unknown_attempts"]:
            raise ValueError("unknown/torn attempt cost; reconcile before resuming")
        group = (
            "completed"
            if st["complete"]
            else "incomplete"
            if st["terminal"]
            else "deferred"
            if c["condition"] + ":" + c["dataset"] in defer_classes
            else "pending"
        )
        groups[group].append(c["cell_id"])
    return dict(
        groups,
        process_seconds=process_seconds,
        prior_wall_seconds=session_cost(),
        defer_classes=sorted(set(defer_classes)),
        model_calls=0,
    )


def retry_allowed(state, directory):
    if state.get("terminal"):
        raise RuntimeError("terminal incomplete cell has no retry budget")
    if state["cost"]["unknown_attempts"]:
        raise ValueError("unknown/torn attempt cost; reconcile before resuming")
    if state["dispatches"] >= 2:
        raise RuntimeError("one-retry limit exhausted")
    if state["dispatches"] and not list(
        Path(directory).glob("attempt-*/checkpoint-*.receipt.json")
    ):
        raise ValueError("retry requires an existing certified checkpoint")


def dispatch(cell, manifest, session, decision, lease, expected_sources, remaining_wall):
    st = status(cell, native.sha(MATRIX))
    retry_allowed(st, OUTPUT / cell["cell_id"])
    remaining = min(
        cell["ceilings"]["wall_seconds"] - st["cost"]["known_attempt_wall_seconds"],
        remaining_wall,
        CUTOFF - time.time(),
    )
    if remaining <= 0:
        raise TimeoutError("cell/portfolio/deadline allowance exhausted")
    if sources() != expected_sources:
        raise ValueError("supplemental runner sources changed before dispatch")
    queue.verify_resume(dict(cell, result_dir=str(OUTPUT / cell["cell_id"])), manifest)
    target = session / cell["cell_id"] / f"dispatch-{st['dispatches']:02d}"
    target.mkdir(parents=True, exist_ok=False)
    before = set((OUTPUT / cell["cell_id"]).glob("attempt-*"))
    start = dict(
        schema_version=1,
        mode=MODE,
        matrix_sha256=native.sha(MATRIX),
        cell_id=cell["cell_id"],
        recipe=cell["recipe"],
        decision=decision,
        runner_sources=expected_sources,
        lease=lease,
        resume=bool(before),
        started_epoch=time.time(),
        allowance_seconds=remaining,
        retry_policy="AW-R-one-clean-checkpoint-retry",
        cost_scope="whole child-process envelope, including failed work",
    )
    durable_json(target / "start.json", start)
    cmd = [
        sys.executable,
        "-m",
        "aw.r_run",
        "cell",
        "--cell-id",
        cell["cell_id"],
        "--parent-pid",
        str(os.getpid()),
        "--receipt",
        str(target / "start.json"),
        "--execute",
    ]
    code, error = None, None
    begun = time.monotonic()
    try:
        with (target / "process.log").open("xb") as stream:
            code = subprocess.run(
                cmd,
                cwd=ROOT,
                stdout=stream,
                stderr=subprocess.STDOUT,
                timeout=remaining,
                check=False,
            ).returncode
    except BaseException as exc:
        error = repr(exc)
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
    finally:
        new = sorted(str(p) for p in set((OUTPUT / cell["cell_id"]).glob("attempt-*")) - before)
        durable_json(
            target / "finish.json",
            dict(
                start,
                start_sha256=native.sha(target / "start.json"),
                charged_process_wall_seconds=time.monotonic() - begun,
                new_attempts=new,
                returncode=code,
                error=error,
                failure_class=None
                if code == 0 and error is None
                else failure_class(code, error, new, target / "process.log"),
            ),
        )
    return json.loads((target / "finish.json").read_bytes())


def child(cell_id, parent_pid, receipt):
    deadline_check()
    held = lease_probe(ROOT)
    if held is None or held["pid"] != parent_pid or os.getppid() != parent_pid:
        raise PermissionError("live owning queue GPU lease required")
    start = json.loads(Path(receipt).read_bytes())
    if (
        start["cell_id"] != cell_id
        or start["lease"] != held
        or start["matrix_sha256"] != native.sha(MATRIX)
        or start["runner_sources"] != sources()
    ):
        raise ValueError("child receipt/lease/source binding differs")
    checked(start["decision"]) if str(start["decision"]["path"]).endswith(".json") else None
    if native.sha(start["decision"]["path"]) != start["decision"]["sha256"]:
        raise ValueError("lead decision changed")
    m = matrix()
    c = next(c for c in m["cells"] if c["cell_id"] == cell_id)
    r, _ = load(c["recipe"]["path"], c["recipe"]["sha256"], allow_sealed=True)
    import jax

    if not any(d.platform == "gpu" for d in jax.devices()):
        raise RuntimeError("GPU execution requires CUDA-enabled JAX")
    adapter, tokenizer = native.construct_owner_adapter(r)
    return engine()(
        c["recipe"]["path"],
        c["recipe"]["sha256"],
        adapter,
        tokenizer,
        output_root=OUTPUT,
        resource_root=RESOURCES,
        allow_sealed=True,
        resume=start["resume"],
    )


def run(decision_path, *, wall_hours=30, resume=None, defer_classes=()):
    from pccap.harness.lease import gpu_lease

    if not math.isfinite(wall_hours) or not 0 < wall_hours <= 30:
        raise ValueError("portfolio wall allowance must be positive and at most 30 hours")
    decision = approve(decision_path)
    m = matrix()
    expected_sources = sources()
    inventory = resume_inventory(defer_classes=defer_classes)
    prior = inventory["prior_wall_seconds"]
    allowance = min(wall_hours * 3600 - prior, CUTOFF - time.time())
    if allowance <= 0:
        raise TimeoutError("portfolio wall budget exhausted")
    if resume is None:
        if list(RECEIPTS.glob("*/session-start.json")):
            raise ValueError("existing portfolio requires --resume SESSION")
        session = RECEIPTS / time.strftime("%Y%m%dT%H%M%S")
        segment = session
    else:
        session = Path(resume).resolve()
        if session.parent != RECEIPTS.resolve():
            raise ValueError("resume requires an existing Option R session")
        original = json.loads((session / "session-start.json").read_bytes())
        if original["matrix"] != ref(MATRIX) or original["decision"] != decision:
            raise ValueError("resume matrix or approved decision differs")
        number = len(list(session.glob("resumes/*/session-start.json"))) + 1
        segment = session / "resumes" / f"{number:04d}"
    segment.mkdir(parents=True, exist_ok=False)
    durable_json(
        segment / "session-start.json",
        dict(
            matrix=ref(MATRIX),
            decision=decision,
            allowance_seconds=allowance,
            workers=2,
            memory_floor_mib=6144,
            sources=expected_sources,
            inventory=inventory,
            parent_session=str(session),
            prior_wall_seconds=prior,
            idle_gaps_charged=False,
        ),
    )
    begun = time.monotonic()
    result = dict(
        status="failed",
        completed=[],
        observations=[],
        incomplete=inventory["incomplete"],
        deferred=inventory["deferred"],
    )
    pending = [
        c for c in m["cells"] if c["cell_id"] not in result["incomplete"] + result["deferred"]
    ]
    active = {}
    stop = None
    try:
        with (
            gpu_lease(
                "AW-R-1", stage="additional_work", projected_seconds=allowance, exclusive=True
            ) as lease,
            ThreadPoolExecutor(max_workers=2) as workers,
        ):
            others = lease.other_cuda_processes()
            if any("error" in p for p in others) or blocking_cuda_processes(others):
                raise RuntimeError("released project GPU required")
            held = lease_probe(ROOT)
            if held is None or held["pid"] != os.getpid():
                raise RuntimeError("queue lease is not held")
            while pending or active:
                remaining = allowance - (time.monotonic() - begun)
                if remaining <= 0:
                    stop = stop or "portfolio allowance exhausted"
                while pending and len(active) < 2 and stop is None:
                    c = pending[0]
                    st = status(c, native.sha(MATRIX))
                    if st["complete"]:
                        result["observations"].append(observe(c))
                        result["completed"].append(c["cell_id"])
                        pending.pop(0)
                        continue
                    retry_allowed(st, OUTPUT / c["cell_id"])
                    # Reserve both prospective peaks; this is intentionally conservative.
                    peaks = (
                        sum(x["ceilings"]["peak_host_mib"] for x in active.values())
                        + c["ceilings"]["peak_host_mib"]
                    )
                    if queue.memory_available_mib() < 6144 + peaks:
                        if not active:
                            stop = "insufficient host memory; no model launched"
                        break
                    r, _ = recipe(c, m)
                    active[
                        workers.submit(
                            dispatch, c, r, session, decision, held, expected_sources, remaining
                        )
                    ] = c
                    pending.pop(0)
                if not active:
                    break
                done, _ = wait(active, timeout=5, return_when=FIRST_COMPLETED)
                for future in done:
                    c = active.pop(future)
                    try:
                        receipt = future.result()
                        if receipt["failure_class"] is None:
                            result["observations"].append(observe(c))
                            result["completed"].append(c["cell_id"])
                            watch.update(
                                result["observations"],
                                output=OUTPUT / "fidelity_watch",
                                document=ROOT / "docs/additional_work/R_fidelity_watch.md",
                            )
                        elif receipt["failure_class"] == "host":
                            stop = "host failure; admission halted"
                        else:
                            retry_allowed(status(c, native.sha(MATRIX)), OUTPUT / c["cell_id"])
                            pending.insert(0, c)
                    except Exception as exc:
                        stop = repr(exc)
                if stop is not None:
                    pending = []  # Running children finish within already recorded ceilings.
            if sources() != expected_sources:
                stop = "runner sources changed during execution"
            result.update(
                status=(
                    "complete"
                    if len(result["completed"]) == 30
                    else "finished_with_incomplete_cells"
                )
                if stop is None and not pending
                else "stopped",
                reason=stop,
            )
    finally:
        result["elapsed_wall_seconds"] = time.monotonic() - begun
        result["process_seconds"] = sum(
            status(c, native.sha(MATRIX))["cost"]["known_attempt_wall_seconds"] for c in m["cells"]
        )
        durable_json(segment / "session-finish.json", result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("plan", "run", "cell", "reconcile", "status"))
    p.add_argument("--validate-payloads", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--approved-decision")
    p.add_argument("--wall-hours", type=float, default=30)
    p.add_argument("--cell-id")
    p.add_argument("--parent-pid", type=int)
    p.add_argument("--receipt")
    p.add_argument("--resume", metavar="SESSION")
    p.add_argument("--defer-class", action="append", default=[], metavar="CONDITION:DATASET")
    a = p.parse_args()
    if a.command == "plan":
        result = plan(validate_payloads=a.validate_payloads)
    elif a.command == "reconcile":
        if not a.cell_id:
            p.error("--cell-id required")
        result = reconcile(a.cell_id, execute=a.execute)
        result = {k: v for k, v in result.items() if k != "attempt_files"}
    elif a.command == "status":
        result = resume_inventory(defer_classes=a.defer_class)
    elif a.command == "run":
        if not a.execute or not a.approved_decision:
            p.error("--execute and --approved-decision required after Tuesday choice")
        result = run(
            a.approved_decision,
            wall_hours=a.wall_hours,
            resume=a.resume,
            defer_classes=a.defer_class,
        )
    else:
        if not a.execute or not all((a.cell_id, a.parent_pid, a.receipt)):
            p.error("cell is dispatched by the owning queue only")
        result = child(a.cell_id, a.parent_pid, a.receipt)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
