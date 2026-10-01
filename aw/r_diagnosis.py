"""CPU forensic comparison of Option R's stopped cell with its measured donors."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import json
from collections import defaultdict
from pathlib import Path

from aw import r_run as r


def timings(attempt):
    groups = defaultdict(lambda: dict(count=0, seconds=0.0))
    endpoints = []
    for path in sorted(attempt.glob("phase-timings/*.json")):
        d = json.loads(path.read_bytes())
        kind = d["phase"].split(":")[0]
        groups[kind]["count"] += 1
        groups[kind]["seconds"] += d["total_phase_seconds"]
        if kind not in ("edit", "immediate"):
            endpoints.append(dict(phase=d["phase"], seconds=d["total_phase_seconds"]))
    return dict(groups=groups, endpoints=endpoints)


def build():
    m = r.matrix()
    cell = next(c for c in m["cells"] if c["cell_id"] == "61eb6d08de6f1b0b9a28d03b")
    recipe = r.checked(cell["recipe"])
    parent = r.checked(recipe["parent_recipe"])
    measurement = r.checked(cell["ceilings"]["measurement"])
    donors = []
    for row in measurement["rows"]:
        if (row["condition"], row["dataset"]) != (cell["condition"], cell["dataset"]):
            continue
        r.checked(row["result"])
        donors.append(
            dict(
                order=row["order"],
                process_seconds=row["charged_process_seconds"],
                timings=timings(Path(row["result"]["path"]).parent),
            )
        )
    session = r.RECEIPTS / "20260929T174143"
    finish = json.loads((session / cell["cell_id"] / "dispatch-00/finish.json").read_bytes())
    start, stop = (
        finish["started_epoch"],
        finish["started_epoch"] + finish["charged_process_wall_seconds"],
    )
    overlap = []
    for path in session.glob("*/dispatch-*/finish.json"):
        d = json.loads(path.read_bytes())
        if d["cell_id"] == cell["cell_id"]:
            continue
        seconds = max(
            0,
            min(stop, d["started_epoch"] + d["charged_process_wall_seconds"])
            - max(start, d["started_epoch"]),
        )
        overlap.append(dict(cell_id=d["cell_id"], overlap_process_seconds=seconds))
    result = dict(
        cell=cell,
        recipe_drift={k: recipe.get(k) for k in ("drift_implementation", "drift_batch_size")},
        parent_drift={k: parent.get(k) for k in ("drift_implementation", "drift_batch_size")},
        timing=timings(r.OUTPUT / cell["cell_id"] / "attempt-0000"),
        donors=donors,
        overlap=overlap,
        model_calls=0,
        sources=[
            r.ref(__file__),
            cell["recipe"],
            recipe["parent_recipe"],
            cell["ceilings"]["measurement"],
        ],
    )
    (r.ROOT / "logs/additional_work/R/r2-diagnosis.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    build()
