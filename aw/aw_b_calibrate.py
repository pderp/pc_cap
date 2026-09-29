"""AW-B3: bounded-correction calibration and selected, exposed evaluation.

No installed source or active PC runner is modified. `plan` qualifies existing
development memories without running a model. GPU commands require --execute,
an exclusive lease, a new output directory and the October 9 deadline. Numerical
wrappers share one fixed-prefix pass; each gate setting gets a separate pass.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import dataclasses
import json
import math
import time
from pathlib import Path

import numpy as np
from scripts import r1_68f_full_validation as fv
from scripts.r1_68c_batched_drift import PositionBatchReader

from aw import scoring
from aw.pc_harm_readout import selection, summarize, window_hash
from aw.pc_v0 import CUTOFF, blocking_cuda_processes, dump, sha, wall_limit
from aw.pc_v0_report import table
from aw.pc_v1_run import metrics
from aw.wrapper import BoundedCap
from pccap.harness.snapshot import restore
from pccap.revision_v1.endpoints_composition import as_edit
from pccap.revision_v1.learner import RevisionCap
from pccap.revision_v1.reader import params_hash
from pccap.revision_v1.stage4_adapters import CellAdapter
from pccap.revision_v1.stage4_assays import CellAssays

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(pccap.ASSETS_ROOT)
OUTPUT = ROOT / "results/additional_work/AW-B"
SPEC = ROOT / "docs/additional_work/AW-B.md"
DATASETS = ("zsre", "counterfact")
NUMERICAL = (
    [("v5", None), ("capoff", None)]
    + [
        (kind, value)
        for b in (0.5, 1, 2, 4)
        for kind, value in (("clip", b), ("mixture", math.exp(-2 * b)))
    ]
    + [("shrink", a) for a in (0.25, 0.5, 0.75)]
)
GATES = [("gate", t) for t in (0.4, 0.3, 0.2)]
CONFIGS = NUMERICAL + GATES
DEVELOPMENT = {
    "zsre": (
        "docs/tasks/R1-64g-post63l/R1-64g-zsre-R1_learned_ff.recipe.json",
        "R1_learned_ff-zsre-development_full_endpoints_R164f-seed64028-c84c64b1149e74b70edb",
    ),
    "counterfact": (
        "docs/tasks/R1-64-counterfact-v5.recipe.json",
        "R1_learned_ff-counterfact-development-source-bc285b69b70dff8514a4",
    ),
}


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def checked(b):
    path = Path(b["path"])
    if sha(path) != b["sha256"]:
        raise ValueError("bound input changed: " + str(path))
    return json.loads(path.read_bytes())


def sources():
    files = [
        Path(__file__),
        SPEC,
        ROOT / "aw/wrapper.py",
        ROOT / "aw/bounded.py",
        ROOT / "aw/scoring.py",
        ROOT / "aw/pc_harm_readout.py",
        ROOT / "aw/pc_v0.py",
        ROOT / "aw/pc_v1_run.py",
        ROOT / "requirements.lock",
        ROOT / "scripts/r1_61_cell_driver.py",
        ROOT / "scripts/r1_68c_batched_drift.py",
        ROOT / "scripts/r1_68f_full_validation.py",
        ROOT / "scripts/r1_49g_secondary.py",
    ]
    files += sorted((ROOT / "src/pccap").rglob("*.py"))
    return {str(p): sha(p) for p in files}


def qualify(recipe_path, result_dir, snapshot_path, *, population):
    rb = binding(recipe_path)
    recipe = checked(rb)
    payload = checked(recipe["payload"])
    cpb, mb, sb = (
        binding(p)
        for p in (
            Path(result_dir) / "checkpoint-300.json",
            Path(str(snapshot_path) + ".json"),
            snapshot_path,
        )
    )
    cp, meta = checked(cpb), checked(mb)
    if meta["snapshot_sha256"] != sb["sha256"] or meta["state_sha256"] != cp["state_sha256"]:
        raise ValueError("development/evaluation snapshot and checkpoint bindings differ")
    state = restore(Path(sb["path"]).read_bytes(), expected_hash=meta["state_sha256"])
    if cp["checkpoint"] != 300 or [x["item_id"] for x in cp["history"]] != [
        x["item_id"] for x in payload["items"][:300]
    ]:
        raise ValueError("checkpoint is not the declared first 300 development/evaluation edits")
    semantics = json.loads(state.scalars["config"])
    identity = recipe["adapter_identity"]
    if (
        identity["condition"] != "R1_learned_ff"
        or identity["params_sha256"] != state.scalars["params_hash"]
        or semantics["base"] != identity["base_sha256"]
        or semantics.get("null_threshold") != 0.5
        or "pc_acquisition" in semantics
    ):
        raise ValueError("qualified original selected-v5 memory required")
    return dict(
        recipe=rb,
        payload=recipe["payload"],
        checkpoint=cpb,
        metadata=mb,
        snapshot=sb,
        state_sha256=meta["state_sha256"],
        population=population,
        cell=recipe["cell"],
        base_sha256=identity["base_sha256"],
        reader_sha256=identity["params_sha256"],
        memory_origin="existing registered-acquisition 300-edit snapshot; no new training",
    )


def development_inputs():
    result = {}
    for ds, (recipe, name) in DEVELOPMENT.items():
        result[ds] = qualify(
            ROOT / recipe,
            ROOT / "results/R1/stage4_dev_cells" / name / "attempt-0000",
            ASSETS
            / "runs/pc_cap/R1/stage4_dev_cells"
            / name
            / "attempt-0000/checkpoint-300.snapshot",
            population="exposed development: "
            + ("r1_64f_round28/zsre full endpoints" if ds == "zsre" else "r16_counterfact_v5"),
        )
    return result


def evaluation_inputs():
    from scripts.r1_77b_sealed_backend import cell_name

    result = {}
    for path in sorted((ROOT / "docs/tasks/R1-final-cell-recipes").glob("*.json")):
        recipe = json.loads(path.read_bytes())
        c = recipe["cell"]
        if (
            c["condition"] != "R1_learned_ff"
            or c["dataset"] not in DATASETS
            or c["realization"] != 0
        ):
            continue
        name = cell_name(recipe, sha(path))
        run = ROOT / "results/R1/stage4_sealed_cells" / name
        candidates = list(run.glob("attempt-*/checkpoint-300.json"))
        if len(candidates) != 1:
            raise ValueError("unique original checkpoint-300 attempt required: " + name)
        attempt = candidates[0].parent.name
        spec = qualify(
            path,
            candidates[0].parent,
            ASSETS
            / "runs/pc_cap/R1/stage4_sealed_cells"
            / name
            / attempt
            / "checkpoint-300.snapshot",
            population="post hoc / exposed sealed R1 realization 0, first 300 edits",
        )
        result[f"{c['dataset']}-o{c['order']}"] = spec
    if {(v["cell"]["dataset"], v["cell"]["order"]) for v in result.values()} != {
        (ds, order) for ds in DATASETS for order in range(100, 105)
    } or len(result) != 10:
        raise ValueError("ten exposed evaluation memories required")
    return result


def reconstruct(spec):
    from scripts.r1_61_cell_driver import construct_owner_adapter

    recipe = checked(spec["recipe"])
    adapter, tokenizer = construct_owner_adapter(recipe)
    if adapter.identity() != recipe["adapter_identity"]:
        raise ValueError("registered constructor identity differs")
    if sha(spec["snapshot"]["path"]) != spec["snapshot"]["sha256"]:
        raise ValueError("snapshot bytes changed")
    adapter.import_state(
        restore(Path(spec["snapshot"]["path"]).read_bytes(), expected_hash=spec["state_sha256"])
    )
    if adapter.state_hash() != spec["state_sha256"]:
        raise ValueError("restored memory differs")
    payload = checked(spec["payload"])
    items = [as_edit(row, tokenizer) for row in payload["items"][:300]]
    endpoints = {k: payload["endpoints"][k] for k in ("locality", "near_miss", "revision")}
    return adapter.learner, tokenizer, items, endpoints


def view(cap, config, *, generation):
    kind, parameter = config
    if config not in CONFIGS:
        raise ValueError("unregistered AW-B setting")
    cfg = dataclasses.replace(cap.cfg, null_threshold=parameter) if kind == "gate" else cap.cfg
    wrapper = None if kind in ("v5", "gate") else ("mixture", 1.0) if kind == "capoff" else config
    new = (
        BoundedCap(cap.base, cfg, cap.ledger, params=cap.params, wrapper=wrapper)
        if generation
        else RevisionCap(cap.base, cfg, cap.ledger, params=cap.params)
    )
    state = cap.export_state().clone()
    if kind == "gate":
        expected = json.loads(state.scalars["config"])
        expected["null_threshold"] = parameter
        if expected != json.loads(new.semantic_config()):
            raise ValueError("gate view would change additional semantics")
        state.scalars["config"] = new.semantic_config()
    new.import_state(state)
    if new.store.export().content_hash() != cap.store.export().content_hash():
        raise ValueError("query-time view changed stored records")
    return new


def fixed_prefix(cap, windows, metadata, configs, output, resources, *, batch_size=16):
    """One native batch pass for numerical configs, one per requested gate."""
    output, resources = Path(output), Path(resources)
    output.mkdir(parents=True, exist_ok=False)
    resources.mkdir(parents=True, exist_ok=False)
    if metadata["windows_sha256"] != window_hash(windows):
        raise ValueError("position selection hash differs")
    groups = [([c for c in configs if c[0] != "gate"], ("v5", None))]
    groups += [([c], c) for c in configs if c[0] == "gate"]
    results = {}
    original_state, original_base, original_reader = (
        cap.state_hash(),
        cap.base.checksum(recompute=True),
        params_hash(cap.params),
    )
    for configurations, source_config in groups:
        if not configurations:
            continue
        reader_cap = view(cap, source_config, generation=False)
        reader = PositionBatchReader(
            CellAdapter(reader_cap, "R1_learned_ff"), batch_size=batch_size
        )
        numeric = [("v5", None)] if source_config[0] == "gate" else configurations
        accumulator = scoring.Accumulator(numeric)
        telemetry = dict(logical_positions=0, hard_null=0, selected=0, corrected_positions=0)
        events = {}
        start = time.monotonic()
        before = reader_cap.state_hash()
        for chunk in fv.chunks(windows, batch_size):
            try:
                on = reader.last_logits_batch([r[2] for r in chunk])
                off = reader.last_capoff
                accumulator.add(on, off, off, np.asarray([r[3] for r in chunk]))
                for event in reader.events:
                    for decision in event.get("selections", []):
                        telemetry["logical_positions"] += 1
                        telemetry["hard_null"] += int(decision["hard_null"])
                        telemetry["selected"] += int(not decision["hard_null"])
                    telemetry["corrected_positions"] += event.get("logical_corrected_prefixes", 0)
            finally:
                fv.aggregate_events(reader.events, events)
                reader.events.clear()
        if (
            telemetry["logical_positions"] != metadata["positions"]
            or reader_cap.state_hash() != before
        ):
            raise ValueError("incomplete coverage or changed query memory")
        summaries = accumulator.summary()
        for key, values in accumulator.vectors().items():
            label = scoring.config_key(source_config) if source_config[0] == "gate" else key
            if values.shape != (metadata["positions"], 5) or not np.isfinite(values).all():
                raise ValueError("incomplete or nonfinite full-vocabulary metrics")
            shaped = values.reshape(len(windows), windows.shape[1] - 1, 5)
            path = resources / (label.replace(":", "-") + ".npz")
            with path.open("xb") as f:
                np.savez_compressed(f, values=shaped)
            results[label] = dict(
                summary=summarize(shaped),
                changed_fraction=summaries[key]["changed_fraction"],
                telemetry=dict(telemetry),
                vectors=binding(path),
                selection=metadata,
                pass_key=scoring.config_key(source_config),
                pass_process_seconds=time.monotonic() - start,
                returned_events=events,
                cost_note="shared pass charged once, not once per numerical configuration",
            )
            dump(output / (label.replace(":", "-") + ".json"), results[label])
        if (
            cap.state_hash() != original_state
            or cap.base.checksum(recompute=True) != original_base
            or params_hash(cap.params) != original_reader
        ):
            raise RuntimeError("fixed-prefix assay changed immutable inputs")
    return results


def efficacy(cap, tokenizer, items, endpoints, configs, output, *, max_new=32):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    original = cap.state_hash()
    base_identity, reader_identity = cap.base.checksum(recompute=True), params_hash(cap.params)
    rows = {}
    for config in configs:
        active = view(cap, config, generation=True)
        adapter = CellAdapter(active, "R1_learned_ff", locality_base=cap.base)
        assay = CellAssays(adapter, tokenizer, max_new=max_new)
        state = active.state_hash()
        start = time.monotonic()
        retained = assay.retention(items)
        cp = dict(
            history=retained["rows"],
            retention=retained,
            locality=assay.locality(endpoints["locality"]),
            endpoints={},
        )
        for kind in ("near_miss", "revision"):
            cp["endpoints"][kind] = assay.challenges(kind, endpoints[kind], items)
            if any(r["status"] == "resource_failure" for r in cp["endpoints"][kind]["rows"]):
                raise RuntimeError("endpoint resource failure: " + kind)
        cp["metrics"] = metrics(cp, [it.item_id for it in items], endpoints)
        cp["ES_scope"] = (
            "re-query at saved 300-edit memory, identical to RET-ES; not immediate acquisition ES"
        )
        cp["acquisition_scope"] = (
            "no new stream training; installed near-miss/revision temporary teaching is restored and charged"
        )
        cp["elapsed_process_seconds"] = time.monotonic() - start
        cp["wrapper_counters"] = dict(active.wrapper_counters)
        if (
            active.state_hash() != state
            or cap.state_hash() != original
            or cap.base.checksum(recompute=True) != base_identity
            or params_hash(cap.params) != reader_identity
        ):
            raise RuntimeError("efficacy assay changed saved memory")
        cp["memory_unchanged"] = True
        key = scoring.config_key(config)
        dump(output / (key.replace(":", "-") + ".json"), cp)
        rows[key] = dict(
            metrics=cp["metrics"], elapsed_process_seconds=cp["elapsed_process_seconds"]
        )
    return rows


def select(calibration, ranking):
    """Explicit cross-dataset ranking; pending approval is not a default choice."""
    if ranking != "minimum":
        raise ValueError("an approved cross-dataset selection ranking is required")
    aggregate = min
    if set(calibration) != set(DATASETS):
        raise ValueError("both calibration datasets required")
    rows = []
    for config in CONFIGS:
        kind, _ = config
        if kind in ("v5", "capoff"):
            continue
        key = scoring.config_key(config)
        eligible, changes, reductions, tails = True, {}, [], []
        for ds in DATASETS:
            r = calibration[ds]
            a, b = r["efficacy"]["v5"]["metrics"], r["efficacy"][key]["metrics"]
            diffs = {}
            for metric in ("RET-ES", "RET-GS", "LS", "near_miss"):
                left, right = a[metric]["value"], b[metric]["value"]
                diffs[metric] = None if left is None or right is None else right - left
                eligible &= diffs[metric] is not None and (
                    abs(diffs[metric]) <= 0.02 + 1e-12
                    if metric in ("RET-ES", "RET-GS")
                    else diffs[metric] >= -1e-12
                )
            changes[ds] = diffs
            original, candidate = (r["harm"][k]["summary"]["original"]["loss"] for k in ("v5", key))
            reductions.append(original["maximum_signed"] - candidate["maximum_signed"])
            tails.append(original["es99_positive"] - candidate["es99_positive"])
        rows.append(
            dict(
                config=list(config),
                key=key,
                category="bound" if kind in ("clip", "mixture") else "comparator",
                eligible=bool(eligible),
                efficacy_changes=changes,
                maximum_reductions=dict(zip(DATASETS, reductions)),
                es99_reductions=dict(zip(DATASETS, tails)),
                rank_maximum=aggregate(reductions),
                rank_es99=aggregate(tails),
            )
        )
    chosen = {}
    for category in ("bound", "comparator"):
        eligible = [r for r in rows if r["category"] == category and r["eligible"]]
        # Complete numerical ties retain the predeclared CONFIGS order; no outcome-based extra criterion.
        chosen[category] = (
            max(eligible, key=lambda r: (r["rank_maximum"], r["rank_es99"])) if eligible else None
        )
    arms = [["v5", None], ["capoff", None]] + [
        r["config"] for r in chosen.values() if r is not None
    ]
    return dict(
        schema="aw-b-selection-v1",
        ranking=ranking,
        candidates=rows,
        chosen=chosen,
        final_configs=arms,
        no_eligible_policy="omit missing category; do not invent a qualifying arm",
        tie_policy="maximum reduction, ES99 reduction, then predeclared configuration order",
        selection_population="development only; never evaluation",
    )


def evaluation_success(cells):
    """Per-coordinate success; no pooling hides a failing dataset/order."""
    rows = []
    for name, cell in cells.items():
        baseline = cell["harm"]["v5"]["summary"]["original"]["loss"]
        for key, harm in cell["harm"].items():
            loss = harm["summary"]["original"]["loss"]
            differences = {}
            for metric in ("RET-ES", "RET-GS", "LS", "near_miss", "revision"):
                a, b = (cell["efficacy"][k]["metrics"][metric]["value"] for k in ("v5", key))
                differences[metric] = None if a is None or b is None else b - a
            retention = all(
                differences[m] is not None and abs(differences[m]) <= 0.02 + 1e-12
                for m in ("RET-ES", "RET-GS")
            )
            rows.append(
                dict(
                    cell=name,
                    config=key,
                    efficacy_changes=differences,
                    maximum_reduction=baseline["maximum_signed"] - loss["maximum_signed"],
                    es99_reduction=baseline["es99_positive"] - loss["es99_positive"],
                    retention_within_two_points=retention,
                    success=bool(
                        retention
                        and loss["maximum_signed"] < baseline["maximum_signed"]
                        and loss["es99_positive"] < baseline["es99_positive"]
                    ),
                )
            )
    return dict(
        per_coordinate=rows,
        all_coordinates_by_config={
            k: all(r["success"] for r in rows if r["config"] == k)
            for k in sorted({r["config"] for r in rows})
        },
        scope="descriptive exposed evaluation; lower maximum and ES99+, retention within two points on every coordinate",
    )


def render(report):
    text = "# AW-B bounded-correction " + report["command"] + "\n\n"
    text += (
        "Post hoc / exposed populations. Full validation: 245,237 target positions, 1,931 windows. "
    )
    text += "Fixed-prefix loss/KL use original = cap-off; positions are not independent experimental replicates. "
    text += "The benchmark lines remain mean KL 0.001 and mean ΔNLL 0.01.\n\n"
    data = []
    for cell, row in report["cells"].items():
        for config, h in row["harm"].items():
            s = h["summary"]["original"]
            data.append(
                [
                    cell,
                    config,
                    s["kl"]["mean_signed"],
                    s["loss"]["mean_signed"],
                    s["loss"]["es99_positive"],
                    s["loss"]["maximum_signed"],
                    s["loss"]["maximum_location"],
                    h["changed_fraction"],
                    *[
                        row["efficacy"][config]["metrics"][m]["value"]
                        for m in ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")
                    ],
                ]
            )
    text += table(
        [
            "Cell",
            "Setting",
            "Mean KL",
            "Mean ΔNLL",
            "ES99+",
            "Max ΔNLL",
            "Location",
            "Changed fraction",
            "ES re-query",
            "RET-ES",
            "RET-GS",
            "LS",
            "Near miss",
            "Revision",
        ],
        data,
    )
    if report["command"] == "evaluate":
        text += "\n\nSuccess requires lower maximum and ES99+, and retention within two percentage points, on every dataset/order.\n\n"
        text += table(
            ["Setting", "All coordinates succeed"],
            list(evaluation_success(report["cells"])["all_coordinates_by_config"].items()),
        )
    return text


def run(
    command, output, *, selection_file=None, ranking="minimum", batch_size=16, wall_seconds=None
):
    import jax

    from pccap.harness.lease import gpu_lease

    ceiling = 28800 if command == "calibrate" else 57600
    allowance = min(ceiling if wall_seconds is None else wall_seconds, CUTOFF - time.time())
    if allowance <= 0 or allowance > ceiling or not 1 <= batch_size <= 32:
        raise ValueError("invalid allowance/batch size or experimental cutoff reached")
    out = Path(output).resolve()
    if not out.is_relative_to(OUTPUT) or out == OUTPUT:
        raise ValueError("new output must be below " + str(OUTPUT))
    resources = ASSETS / "runs" / out.relative_to(ROOT / "results")
    if out.exists() or resources.exists():
        raise FileExistsError("new result and vector directories required")
    if command == "calibrate":
        inputs, configs = development_inputs(), CONFIGS
    else:
        sb = binding(selection_file)
        selected = checked(sb)
        if (
            selected.get("schema") != "aw-b-selection-v1"
            or selected.get("selection_population") != "development only; never evaluation"
        ):
            raise ValueError("completed calibration selection required")
        parent = checked(selected["calibration_report"])
        reproduced = select(parent["cells"], selected["ranking"])
        if any(selected[k] != reproduced[k] for k in reproduced):
            raise ValueError("selection does not reproduce from calibration")
        for path, h in parent["sources_sha256"].items():
            if sha(path) != h:
                raise ValueError("calibration source changed: " + path)
        inputs, configs = evaluation_inputs(), [tuple(c) for c in selected["final_configs"]]
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    begun = time.monotonic()
    report = dict(
        command=command,
        cells={},
        inputs=inputs,
        sources_sha256=sources(),
        configs=configs,
        base_reader="selected BP-trained v5; no PC reader-training claim",
        status="running",
    )
    cost = dict(
        status="failed",
        ceiling_seconds=ceiling,
        charged_scope="lease wait, construction, wrapper scoring, assays including temporary teaching, failures and serialization; preliminary read-only input qualification excluded",
    )
    try:
        with (
            gpu_lease(
                "AW-B3", stage="additional_work", projected_seconds=allowance, exclusive=True
            ) as lease,
            wall_limit(allowance),
        ):
            others = lease.other_cuda_processes()
            if (
                any("error" in r for r in others)
                or blocking_cuda_processes(others)
                or not any(d.platform == "gpu" for d in jax.devices())
            ):
                raise RuntimeError("released project CUDA device required")
            windows, metadata = selection("v5")
            report["selection"] = metadata
            for name, spec in inputs.items():
                start = time.monotonic()
                cap, tok, items, endpoints = reconstruct(spec)
                cell_out = out / name
                cell_out.mkdir()
                harm = fixed_prefix(
                    cap,
                    windows,
                    metadata,
                    configs,
                    cell_out / "harm",
                    resources / name,
                    batch_size=batch_size,
                )
                scores = efficacy(cap, tok, items, endpoints, configs, cell_out / "efficacy")
                row = dict(
                    harm=harm,
                    efficacy=scores,
                    elapsed_process_seconds=time.monotonic() - start,
                    ledger=cap.ledger.totals(),
                    memory_sha256=cap.state_hash(),
                    base_sha256=cap.base.checksum(recompute=True),
                    reader_sha256=params_hash(cap.params),
                )
                dump(cell_out / "report.json", row)
                report["cells"][name] = row
                del cap
            if sources() != report["sources_sha256"] or selection("v5")[1] != metadata:
                raise ValueError("source or validation inventory changed during assay")
            report["status"] = cost["status"] = "complete"
            if command == "evaluate":
                report["success"] = evaluation_success(report["cells"])
            dump(out / "report.json", report)
            (out / "table.md").write_text(render(report))
            if command == "calibrate":
                if ranking is None:
                    dump(
                        out / "selection-pending.json",
                        dict(
                            reason="cross-dataset ranking awaiting scientific approval",
                            calibration_report=binding(out / "report.json"),
                        ),
                    )
                else:
                    chosen = select(report["cells"], ranking)
                    chosen["calibration_report"] = binding(out / "report.json")
                    dump(out / "selection.json", chosen)
    except BaseException as exc:
        cost["status"] = "failed"
        cost["error"] = repr(exc)
        raise
    finally:
        cost.update(
            elapsed_process_seconds=time.monotonic() - begun,
            completed_memories=len(report["cells"]),
        )
        dump(out / "cost.json", cost)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("plan", "calibrate", "evaluate", "select"))
    p.add_argument("--execute", action="store_true")
    p.add_argument("--output")
    p.add_argument("--selection")
    p.add_argument("--report")
    p.add_argument("--ranking", choices=("minimum",), default="minimum")
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--wall-seconds", type=float)
    a = p.parse_args()
    if a.command == "plan":
        print(
            json.dumps(
                dict(
                    inputs=development_inputs(),
                    configs=CONFIGS,
                    calibration_ceiling_seconds=28800,
                    evaluation_ceiling_seconds=57600,
                    model_execution=False,
                    selection_ranking="minimum: charlie approved 2026-09-28",
                ),
                indent=2,
            )
        )
    elif a.command == "select":
        if not a.report or not a.output or not a.ranking:
            p.error("--report, --output and approved --ranking required")
        rb = binding(a.report)
        r = checked(rb)
        if r.get("command") != "calibrate" or r.get("status") != "complete":
            p.error("completed calibration required")
        chosen = select(r["cells"], a.ranking)
        chosen["calibration_report"] = rb
        dump(Path(a.output), chosen)
    else:
        if not a.execute or not a.output or (a.command == "evaluate" and not a.selection):
            p.error("--execute/new --output required; evaluate also requires --selection")
        if a.wall_seconds is not None and (
            not math.isfinite(a.wall_seconds) or a.wall_seconds <= 0
        ):
            p.error("positive finite wall allowance required")
        run(
            a.command,
            a.output,
            selection_file=a.selection,
            ranking=a.ranking,
            batch_size=a.batch_size,
            wall_seconds=a.wall_seconds,
        )


if __name__ == "__main__":
    main()
