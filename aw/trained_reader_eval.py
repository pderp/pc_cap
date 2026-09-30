"""Native endpoint evaluation and full harm for newly trained supplemental readers."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import dataclasses
import json
import resource
import time
from pathlib import Path

import jax
import numpy as np

from aw.interface import ALL, InterfaceCap, InterfaceConfig
from aw.interface_readout import InterfacePositionBatchReader
from aw.pc_harm_readout import read_arm, selection, window_hash
from aw.pc_reader_train import (
    ASSETS,
    OUTPUT,
    ROOT,
    binding,
    device_memory,
    initial_theta,
    load_theta,
    memory_guard,
    recipe,
    remaining_allowance,
)
from aw.pc_v0 import blocking_cuda_processes, dump, sha, wall_limit
from aw.pc_v1_run import bound_recipe, checked, metrics
from pccap.harness.snapshot import restore, save
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints import EndpointResourceFailure
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.revision_v1.stage4_assays import CellAssays


def sources():
    from aw.pc_reader_train import source_hashes

    result = source_hashes()
    for name in (
        "aw/trained_reader_eval.py",
        "aw/interface_readout.py",
        "aw/pc_harm_readout.py",
        "aw/pc_v1_run.py",
        "scripts/r1_61_cell_driver.py",
        "scripts/r1_68c_batched_drift.py",
        "scripts/r1_68f_full_validation.py",
        "aw/scoring.py",
    ):
        result[str(ROOT / name)] = sha(ROOT / name)
    return result


def save_snapshot(cap, path):
    state = cap.export_state()
    record = dict(
        path=str(path),
        sha256=save(state, path),
        state_sha256=state.content_hash(),
        reader_sha256=params_hash(cap.params),
        base_sha256=cap.base.checksum(recompute=True),
        interface=dataclasses.asdict(cap.interface),
        acquisition="adjoint",
    )
    if (
        restore(Path(path).read_bytes(), expected_hash=state.content_hash()).content_hash()
        != cap.state_hash()
    ):
        raise ValueError("snapshot does not roundtrip")
    return record


def run_stream(
    adapter, tok, payload, checkpoints, out, resources, config, *, max_new=32, guard=memory_guard
):
    """Shared real/tiny engine; installed R1 semantics, fresh acquisition, strict restoration."""
    if out.exists() or resources.exists():
        raise FileExistsError("new stream and resource directories required")
    items = [as_edit(r, tok) for r in payload["items"]]
    if not checkpoints or sorted(set(checkpoints)) != checkpoints or checkpoints[-1] != len(items):
        raise ValueError("checkpoints must cover complete selected stream")
    if len({it.item_id for it in items}) != len(items):
        raise ValueError("duplicate stream item")
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    cap, assays = adapter.learner, CellAssays(adapter, tok, max_new=max_new)
    endpoints = payload["endpoints"]
    base_hash, reader_hash = cap.base.checksum(recompute=True), params_hash(cap.params)
    completed, history = [], []
    finish = dict(
        status="failed",
        items_completed=0,
        items_planned=len(items),
        checkpoints_completed=completed,
    )
    dump(
        out / "config.json",
        dict(
            config,
            item_ids=[it.item_id for it in items],
            endpoints_sha256=digest(endpoints),
            base_sha256=base_hash,
            reader_sha256=reader_hash,
            interface=dataclasses.asdict(cap.interface),
            semantic_config=json.loads(cap.semantic_config()),
            acquisition="adjoint",
        ),
    )
    started = time.monotonic()

    def phase(label, fn, teaching=False):
        guard()
        state, t0 = cap.state_hash(), time.monotonic()
        assays.events.clear()
        status = "failed"
        try:
            value = fn()
            if not teaching and cap.state_hash() != state:
                raise RuntimeError("endpoint changed the stream memory")
            status = "complete"
            return value
        finally:
            adapter.reset_queries()
            with (out / "phases.jsonl").open("a") as f:
                f.write(
                    json.dumps(
                        dict(
                            phase=label,
                            status=status,
                            elapsed_process_seconds=time.monotonic() - t0,
                            state_before=state,
                            state_after=cap.state_hash(),
                            returned_events=assays.events,
                        ),
                        allow_nan=False,
                    )
                    + "\n"
                )

    try:
        if cap.store.records:
            raise ValueError("fresh reader memory required")
        for n, it in enumerate(items, 1):
            update = phase(f"edit:{n}", lambda it=it: adapter.update_item(it), teaching=True)
            if update.code == "resource_stop" or any(
                str(s).startswith("resource_failure:") for s in update.codes
            ):
                raise EndpointResourceFailure(";".join(update.codes))
            immediate = phase(f"immediate:{n}", lambda it=it: assays.item(it))
            history.append(
                dict(
                    immediate,
                    outcome=dict(
                        code=update.code,
                        codes=list(update.codes),
                        returned_cost=update.cost.as_dict(),
                    ),
                )
            )
            finish["items_completed"] = n
            with (out / "items.jsonl").open("a") as f:
                f.write(json.dumps(history[-1], allow_nan=False) + "\n")
            if n not in checkpoints:
                continue
            cp = dict(checkpoint=n, history=list(history), endpoints={})
            cp["retention"] = phase(f"retention:{n}", lambda n=n: assays.retention(items[:n]))
            cp["locality"] = phase(f"locality:{n}", lambda: assays.locality(endpoints["locality"]))
            for kind in ("near_miss", "revision"):
                cp["endpoints"][kind] = phase(
                    f"{kind}:{n}",
                    lambda kind=kind, n=n: assays.challenges(kind, endpoints[kind], items[:n]),
                )
                if any(
                    r.get("status") == "resource_failure" for r in cp["endpoints"][kind]["rows"]
                ):
                    raise EndpointResourceFailure(kind)
            if "unseen" in endpoints:
                cp["unseen"] = phase(
                    f"unseen:{n}",
                    lambda n=n: assays.unseen(
                        endpoints["unseen"],
                        payload["pool_rows"],
                        items[:n],
                        f"supplemental-{n}",
                        digest(payload["pool_rows"]),
                    ),
                )
            cp["metrics"] = metrics(cp, [it.item_id for it in items[:n]], endpoints)
            if (
                cap.base.checksum(recompute=True) != base_hash
                or params_hash(cap.params) != reader_hash
            ):
                raise ValueError("base or trained reader changed during acquisition")
            cp["snapshot"] = save_snapshot(cap, resources / f"checkpoint-{n}.snapshot")
            cp["interface_accounting"] = cap.interface_accounting()
            dump(out / f"checkpoint-{n}.json", cp)
            completed.append(n)
        finish["status"] = "complete"
    except BaseException as exc:
        finish["error"] = repr(exc)
        raise
    finally:
        finish.update(
            elapsed_process_seconds=time.monotonic() - started,
            ledger=adapter.ledger.totals(),
            state_sha256=cap.state_hash(),
            base_sha256=cap.base.checksum(recompute=True),
            reader_sha256=params_hash(cap.params),
        )
        dump(out / "finish.json", finish)
    return finish


def execute_evaluation(args, *, write_sites=ALL, output_root=OUTPUT):
    if not args.execute:
        raise ValueError("GPU evaluation requires --execute")
    if not args.training or not args.output:
        raise ValueError("training directory and new output required")
    tr_path = Path(args.training).resolve()
    tr = json.loads((tr_path / "report.json").read_bytes())
    cost = json.loads((tr_path / "cost.json").read_bytes())
    if (
        tr.get("status") != "complete"
        or cost.get("status") != "complete"
        or tr["recipe"] != recipe()
    ):
        raise ValueError("complete training/profile with the declared recipe required")
    if not args.development and tr["profile_only"]:
        raise ValueError("profile reader cannot enter exposed evaluation")
    if output_root == OUTPUT and tr["read_taps"] != list(ALL):
        raise ValueError("PC-15 uses the full-read interface")
    if output_root == ROOT / "results/additional_work/AW-L" and tr["rule"] != "bp":
        raise ValueError("AW-L's approved training rule is BP")
    for name, h in tr["sources_sha256"].items():
        if sha(name) != h:
            raise ValueError("training source changed: " + name)
    if not args.development:
        if not args.evaluation_profile:
            raise ValueError("matching development evaluation profile required")
        ep = Path(args.evaluation_profile)
        pr = json.loads((ep / "report.json").read_bytes())
        pc = json.loads((ep / "cost.json").read_bytes())
        if (
            pr["status"] != "complete"
            or pc["status"] != "complete"
            or not pr["development"]
            or pr["dataset"] != args.dataset
            or pr["rule"] != tr["rule"]
            or pr["read_taps"] != tr["read_taps"]
            or pr["write_sites"] != list(write_sites)
            or pr["sources_sha256"] != sources()
        ):
            raise ValueError("matching complete evaluation profile required")
    out = Path(args.output).resolve()
    if not out.is_relative_to(output_root) or out == output_root or out.exists():
        raise ValueError("new output below " + str(output_root) + " required")
    resources = ASSETS / "runs" / out.relative_to(ROOT / "results")
    if resources.exists():
        raise FileExistsError(resources)
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    start = time.monotonic()
    receipt = dict(
        status="failed", scope="construction + acquisition/endpoints + harm; components are subsets"
    )
    try:
        from scripts.r1_61_cell_driver import construct_owner_adapter

        from pccap.harness.lease import gpu_lease

        allowance = remaining_allowance(output_root, args.wall_seconds)
        with (
            gpu_lease(
                "trained-reader-evaluation",
                stage="additional_work",
                projected_seconds=allowance,
                exclusive=True,
            ) as lease,
            wall_limit(allowance),
        ):
            others = lease.other_cuda_processes()
            if (
                any("error" in r for r in others)
                or blocking_cuda_processes(others)
                or not any(d.platform == "gpu" for d in jax.devices())
            ):
                raise RuntimeError("owner needs a released CUDA device")
            memory_guard()
            native, native_binding = bound_recipe(args.dataset)
            parent, tok = construct_owner_adapter(native)
            if parent.identity() != native["adapter_identity"]:
                raise ValueError("original constructor identity differs")
            cfg = dataclasses.replace(
                parent.learner.cfg,
                reader=dataclasses.replace(parent.learner.cfg.reader, taps=tuple(tr["read_taps"])),
            )
            template = initial_theta(tr["seed"], cfg.reader, cfg.controller)
            theta = load_theta(tr["reader"], template)
            cap = InterfaceCap(
                parent.base,
                cfg,
                parent.ledger,
                params=theta,
                interface=InterfaceConfig(tuple(tr["read_taps"]), write_sites),
            )
            if cap.base.checksum(recompute=True) != tr["base_sha256"]:
                raise ValueError("training/evaluation bases differ")
            adapter = CellAdapter(cap, "R1_learned_ff", budget=parent.budget)
            pop, pop_binding = bound_recipe(args.dataset, development=args.development)
            payload = checked(pop["payload"])
            n = 10 if args.development else 300
            if len(payload["items"]) < n:
                raise ValueError("insufficient planned stream")
            payload = dict(payload, items=payload["items"][:n])
            if not args.development:
                for kind, expected in (
                    ("locality", 50),
                    ("near_miss", 100),
                    ("revision", 50),
                    ("unseen", 100),
                ):
                    endpoint = payload["endpoints"][kind]
                    ids = endpoint["expected_ids"]
                    if (
                        len(ids) != expected
                        or len(set(ids)) != expected
                        or [r["item_id"] for r in endpoint["rows"]] != ids
                    ):
                        raise ValueError("evaluation endpoint coverage/order differs: " + kind)
            context = dict(
                training=binding(tr_path / "report.json"),
                dataset=args.dataset,
                rule=tr["rule"],
                seed=tr["seed"],
                development=args.development,
                population="development profile"
                if args.development
                else "post hoc/exposed realization0 order100, 300 edits",
                source_recipe=native_binding,
                payload_recipe=pop_binding,
                payload=pop["payload"],
                sources_sha256=sources(),
            )
            stream = run_stream(
                adapter,
                tok,
                payload,
                [n] if args.development else [100, 300],
                out / "stream",
                resources / "stream",
                context,
            )
            windows, meta = selection("v5")
            if args.development:
                windows = windows[:8]
                meta = dict(
                    meta,
                    positions=windows.size - len(windows),
                    windows_sha256=window_hash(windows),
                    profile_subset="first eight fixed validation windows; no scientific effect estimate",
                )
            reader = InterfacePositionBatchReader(
                adapter,
                batch_size=args.batch_size,
                guard=memory_guard,
                treatment=dict(
                    reader_rule=tr["rule"],
                    seed=tr["seed"],
                    read_taps=tr["read_taps"],
                    write_sites=list(write_sites),
                    acquisition="adjoint",
                ),
            )
            harm = read_arm(reader, windows, meta, out / "harm")
            with np.load(harm["vectors"]["path"], allow_pickle=False) as f:
                changed = float((f["values"][:, :, 3] > 1e-9).mean())
            report = dict(
                context,
                status="complete",
                read_taps=tr["read_taps"],
                write_sites=list(write_sites),
                stream=stream,
                harm=harm,
                changed_distribution_fraction=changed,
                gate_telemetry=reader.telemetry,
                interface_accounting=cap.interface_accounting(),
                device_memory=device_memory(),
            )
            if sources() != context["sources_sha256"]:
                raise ValueError("evaluation sources changed during execution")
            dump(out / "report.json", report)
            receipt["status"] = "complete"
    except BaseException as exc:
        receipt["error"] = repr(exc)
        raise
    finally:
        receipt.update(
            elapsed_process_seconds=time.monotonic() - start,
            peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        )
        dump(out / "cost.json", receipt)
    return report
