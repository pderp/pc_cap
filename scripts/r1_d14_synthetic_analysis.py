"""Isolated, explicitly synthetic D.4 report rehearsal; no models or real outcomes.

Keep 330 cell coordinates, 100/300/1000 versus 100/300 cadence, endpoint counts,
receipt chains and all analysis logic. Substitute only the four-position validation
population in this process using the established DEC-063 fixture technique.
"""

from __future__ import annotations

import argparse
import copy
import json
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scripts import ht8_fidelity_watch as watch
from scripts import r1_49g_analyze as analysis
from scripts import r1_63l_full_validation_contract as full
from scripts import r1_68f_full_validation as execution
from scripts.ht_audit_existing import statistics

ROOT = analysis.ROOT


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, sort_keys=True, separators=(",", ":"), allow_nan=False)
        f.write("\n")
    return full.ref(path)


def prepare(name):
    if not name or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for c in name):
        raise ValueError("simple unique rehearsal name required")
    outputs = ROOT / "docs/tasks/R1-D14-rehearsal" / name
    results = ROOT / "results/R1/r1_d14_synthetic" / name
    resources = ROOT.parent / "assets/test_scratch/r1_round39" / name
    if any(p.exists() for p in (outputs, results, resources)):
        raise FileExistsError("new rehearsal roots required")
    resources.mkdir(parents=True)
    source = resources / "tokens.npy"
    np.save(source, np.array([2, 3, 4, 2, 3, 4, 2], np.int32))
    inventory = ROOT / "logs/r1_round39" / (name + "-synthetic-token-inventory.json")
    put(inventory, dict(files=dict(drift_tokens={**full.ref(source), "shape": [7]})))
    contract = execution.make_spec(inventory=inventory, fixture=True, window_tokens=3)
    original = ROOT / "manifests/revision_v1/run_matrix_v5_2_D_4.json"
    matrix = json.loads(original.read_text())
    matrix.update(
        synthetic_name="SYNTHETIC D14 D4 report rehearsal " + name,
        scope="confirmatory",
        synthetic=True,
        research_results=False,
        source_declaration=full.ref(original),
        full_validation=contract,
        fidelity_watch=watch.binding(),
        synthetic_limit="330 synthetic cell reports; four full-validation positions, two sampled positions; no model execution, source population claim, or real admission",
    )
    events = []
    trace = dict(generated="synthetic answer", truncated=False)
    cells = analysis.old.all_cells(matrix)
    for cell in cells:
        ds, realization, condition = cell["dataset"], cell["realization"], cell["condition"]
        final = max(cell["checkpoints"])
        prefix = f"SYNTHETIC:{ds}:r{realization}"
        pop = dict(
            item_ids=[f"{prefix}:edit:{i}" for i in range(final)],
            paraphrase_counts=[1] * final,
            endpoints={
                k: [f"{prefix}:{k}:{i}" for i in range(n)]
                for k, n in (
                    ("locality", 50),
                    ("unseen", 100),
                    ("near_miss", 100),
                    ("revision", 50),
                )
            },
            drift=dict(expected_positions=2, source_sha256="synthetic-drift-prefix"),
            full_validation=contract,
        )
        cell.update(
            admitted=True,
            launch_allowed=False,
            population=pop,
            full_validation=contract,
            manifest_sha256=full.digest(dict(synthetic=True, cell_id=cell["cell_id"], name=name)),
            result_dir=str(results / cell["cell_id"]),
        )
        coords = {k: cell[k] for k in analysis.old.COORDS}
        adapter = dict(base_sha256="synthetic-base", locality_base_sha256="synthetic-original")
        mode, directory = "stage4_sealed_cell", Path(cell["result_dir"])
        put(
            directory / "cell.json",
            dict(
                synthetic=True,
                mode=mode,
                cell=coords,
                manifest_sha256=cell["manifest_sha256"],
                checkpoints=cell["checkpoints"],
                adapter_identity=adapter,
            ),
        )
        previous = None
        for n in cell["checkpoints"]:
            attempt = directory / "attempt-0000"
            gs = (0.85 if condition == "R1_learned_ff" else 0.70) + realization * 0.01
            history = [
                dict(item_id=i, status="ok", es=True, paraphrase_n=1) for i in pop["item_ids"][:n]
            ]
            retained = [dict(r, gs=gs) for r in history]
            report = dict(
                synthetic=True,
                mode=mode,
                checkpoint=n,
                state_sha256=full.digest(dict(cell=coords, checkpoint=n)),
                history=history,
                retention=dict(rows=retained),
                locality=dict(
                    rows=[
                        dict(item_id=i, status="ok", reference=trace, query=trace)
                        for i in pop["endpoints"]["locality"]
                    ]
                ),
                unseen=dict(
                    rows=[
                        dict(
                            item_id=i,
                            status="ok",
                            false_fire=j < 5 + realization,
                            firing_status="ok",
                            answer_changed=j < 2,
                        )
                        for j, i in enumerate(pop["endpoints"]["unseen"])
                    ]
                ),
                observation=dict(active_records_status="ok", active_records=n),
                endpoints={},
            )
            values = np.full((2, 2, 5), 2.0)
            values[:, :, 3:] = (
                0.0002 if condition != "R1_learned_ff" else 0.002 + realization * 0.0005
            )
            values[:, :, 0] += np.array(
                [[0.001, -0.001], [0.0, 0.02 if condition == "R1_learned_ff" else 0.0]]
            )
            report["endpoints"]["drift"] = dict(
                source_sha256=pop["drift"]["source_sha256"],
                rows=[
                    dict(
                        item_id=f"w0:p{i + 1}", cap=float(values[0, i, 0]), capoff=2.0, original=2.0
                    )
                    for i in range(2)
                ],
            )
            if n == final:
                report["endpoints"]["near_miss"] = dict(
                    rows=[
                        dict(item_id=i, status="ok", reference=trace, neighbour_query=trace)
                        for i in pop["endpoints"]["near_miss"]
                    ]
                )
                report["endpoints"]["revision"] = dict(
                    rows=[
                        dict(
                            item_id=i,
                            status="ok",
                            latest_answer_success=True,
                            revision_success=True,
                            old_record_retired=True,
                            new_record_active=True,
                            query_n=1,
                            old_answer_reappearance_n=0,
                            after_revision_queries=[dict(old_answer_reappeared=False)],
                        )
                        for i in pop["endpoints"]["revision"]
                    ]
                )
                attempt.mkdir(parents=True, exist_ok=True)
                vectors = attempt / f"full-validation-{n}.npz"
                np.savez_compressed(vectors, values=values)
                locations = ["w0:p1", "w0:p2", "w1:p1", "w1:p2"]
                stats = {
                    k: statistics(v.ravel().tolist(), locations)
                    for k, v in (
                        ("loss_delta_capoff", values[:, :, 0] - values[:, :, 1]),
                        ("loss_delta_original", values[:, :, 0] - values[:, :, 2]),
                        ("kl_capoff_to_cap", values[:, :, 3]),
                        ("kl_original_to_cap", values[:, :, 4]),
                    )
                }
                report["endpoints"]["full_validation"] = dict(
                    status="complete",
                    policy=full.POLICY,
                    checkpoint=n,
                    state_sha256=report["state_sha256"],
                    manifest_sha256=cell["manifest_sha256"],
                    contract_sha256=full.digest(contract),
                    source=contract["source"],
                    source_inventory=contract["source_inventory"],
                    coverage={
                        k: contract[k]
                        for k in (
                            "source_tokens",
                            "window_tokens",
                            "complete_windows",
                            "expected_positions",
                            "trailing_tokens_dropped",
                            "windows_int64le_sha256",
                        )
                    },
                    scored_positions=4,
                    reference_base_sha256=dict(
                        own_capoff=adapter["base_sha256"],
                        original_base=adapter["locality_base_sha256"],
                    ),
                    vectors={
                        **full.ref(vectors),
                        "fields": full.FIELDS,
                        "shape": [2, 2, 5],
                        "dtype": "float64",
                    },
                    statistics=stats,
                )
                identity = dict(mode=mode, recipe_sha256=cell["manifest_sha256"], cell=coords)
                observation = dict(
                    identity=identity,
                    cell_id=full.digest(identity),
                    cell=coords,
                    scope="confirmatory",
                    synthetic=True,
                    recipe=dict(
                        path="synthetic-no-executable-recipe", sha256=cell["manifest_sha256"]
                    ),
                    references={
                        r: dict(kl=stats["kl_" + r + "_to_cap"], loss=stats["loss_delta_" + r])
                        for r in ("original", "capoff")
                    },
                )
                events.append(
                    dict(
                        policy=watch.POLICY,
                        observation=observation,
                        observation_sha256=full.digest(observation),
                        recorded_utc=datetime.now(UTC).isoformat(),
                    )
                )
            report_binding = put(attempt / f"checkpoint-{n}.json", report)
            receipt = dict(
                mode=mode,
                checkpoint=n,
                previous_receipt_sha256=previous,
                manifest_sha256=cell["manifest_sha256"],
                state_sha256=report["state_sha256"],
                report=report_binding,
            )
            receipt["receipt_sha256"] = full.digest(receipt)
            put(attempt / f"checkpoint-{n}.receipt.json", receipt)
            previous = receipt["receipt_sha256"]
        put(
            attempt / "result.json",
            dict(
                synthetic=True,
                mode=mode,
                cell=coords,
                manifest_sha256=cell["manifest_sha256"],
                status="complete",
                completed_checkpoint=final,
                last_receipt_sha256=previous,
                attempt_wall_seconds=1.0,
            ),
        )
    matrix_binding = put(outputs / "matrix.json", matrix)
    journal = ROOT / "logs/r1_round39" / (name + "-synthetic-watch.jsonl")
    with journal.open("x") as f:
        for e in events:
            f.write(watch.encoded(e))
    return dict(
        matrix=matrix_binding,
        watch=full.ref(journal),
        contract=contract,
        synthetic=True,
        results=str(results),
        source_declaration=full.ref(original),
    )


def run(name):
    fixture = prepare(name)
    prefix = ROOT / "logs/r1_round39" / name / "analysis"
    # Only the validation population changes; all installed receipt, vector,
    # classifier, denominator and bootstrap code executes unchanged.
    with patch.object(full, "production_contract", lambda: copy.deepcopy(fixture["contract"])):
        report = analysis.run(fixture["matrix"]["path"], prefix)
    if len(report["cells"]) != 330 or len(report["contrasts"]) != 21:
        raise ValueError("D4 cell/contrast inventory differs")
    if report["incomplete_cells"]:
        raise ValueError(
            "synthetic reports failed actual analysis: " + str(report["incomplete_cells"][:2])
        )
    fixture.update(
        analysis=full.ref(Path(str(prefix) + ".json")),
        cells=330,
        metrics=63,
        complete_blocks=report["complete_blocks"],
        research_results=False,
        validation_positions=4,
        producer=full.ref(__file__),
    )
    put(ROOT / "logs/r1_round39" / name / "rehearsal.json", fixture)
    return fixture


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    print(json.dumps(run(parser.parse_args().name), indent=2))
