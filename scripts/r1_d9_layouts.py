"""Pure versioned population contracts; no imports from execution producers."""

from __future__ import annotations

import hashlib
import json

DATASETS = ("zsre", "counterfact", "mquake")
ROLES = dict(edits=1000, outside=100, near_miss_support=100, near_miss_neighbour=100, revision=50)


def digest(value):
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        ).encode()
    ).hexdigest()


def entry(counts, realizations, checkpoints):
    return dict(
        realizations=list(realizations),
        roles_per_realization=dict(counts),
        checkpoints=list(checkpoints),
        demand_per_realization=sum(counts.values()),
        demand_subjects=sum(counts.values()) * len(realizations),
        demand_by_role={k: n * len(realizations) for k, n in counts.items()},
    )


def production(option="legacy"):
    if option not in ("legacy", "D"):
        raise ValueError("only legacy or DEC-060 option D is admitted")
    return {
        ds: entry(
            {**ROLES, "edits": 300 if ds == "mquake" and option == "D" else 1000},
            range(3),
            [100, 300] if ds == "mquake" and option == "D" else [100, 300, 1000],
        )
        for ds in DATASETS
    }


def resolve(layout=None, *, counts=ROLES, realizations=3, checkpoints=None):
    """API allows small synthetic counts; public producers call admitted()."""
    if layout is None:
        if type(realizations) is not int or realizations < 1:
            raise ValueError("positive realization count required")
        layout = {
            ds: entry(counts, range(realizations), checkpoints or [counts["edits"]])
            for ds in DATASETS
        }
    if not isinstance(layout, dict) or set(layout) != set(DATASETS):
        raise ValueError("all three dataset layouts required")
    result = {}
    for ds in DATASETS:
        x = layout[ds]
        roles = x["roles_per_realization"]
        reals = x["realizations"]
        cps = x["checkpoints"]
        if set(roles) != set(ROLES) or any(type(n) is not int or n < 1 for n in roles.values()):
            raise ValueError("exact roles and positive integer counts required")
        if (
            not isinstance(reals, list)
            or not reals
            or any(type(r) is not int for r in reals)
            or reals != list(range(len(reals)))
        ):
            raise ValueError("contiguous realization inventory required")
        if (
            not isinstance(cps, list)
            or not cps
            or any(type(c) is not int or c < 1 for c in cps)
            or cps != sorted(set(cps))
            or cps[-1] != roles["edits"]
        ):
            raise ValueError("cadence must end at exact edit demand")
        result[ds] = entry({r: roles[r] for r in ROLES}, reals, cps)
        if digest(result[ds]) != digest(x):
            raise ValueError("layout demand fields differ from roles/realizations")
    return result


def admitted(layout):
    layout = resolve(layout)
    if layout not in (production(), production("D")):
        raise ValueError("population differs from legacy/DEC-060 admitted structure")
    return layout


def from_spec(spec):
    if "dataset_layouts" not in spec:
        if spec.get("schema_version", 2) >= 3:
            raise ValueError("v3 inputs need an explicit dataset layout")
        return production()
    layout = admitted(spec["dataset_layouts"])
    if spec.get("layout_sha256") != digest(layout):
        raise ValueError("layout hash differs")
    if spec.get("schema_version") != 3:
        raise ValueError("explicit per-dataset layouts require v3 stage inputs")
    return layout


def from_matrix(matrix):
    if matrix.get("name") == "run_matrix_v5_1":
        if "dataset_layouts" in matrix and digest(matrix["dataset_layouts"]) != digest(
            production()
        ):
            raise ValueError("legacy matrix layout changed")
        return production()
    if matrix.get("name") != "run_matrix_v5_2_option_D" or matrix.get("option") != "D":
        raise ValueError("registered v5.1 or DEC-060 option-D matrix required")
    layout = admitted(matrix["dataset_layouts"])
    if layout != production("D") or matrix.get("layout_sha256") != digest(layout):
        raise ValueError("option-D matrix demand/cadence differs")
    return layout
