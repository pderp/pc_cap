"""CPU projection from completed training/evaluation profiles, with explicit components."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aw.pc_reader_train import binding, recipe, validate_profile
from aw.trained_reader_eval import sources


def evaluation_components(directory):
    path = Path(directory)
    r, c = (json.loads((path / name).read_bytes()) for name in ("report.json", "cost.json"))
    if (
        r["status"] != "complete"
        or c["status"] != "complete"
        or not r["development"]
        or r["sources_sha256"] != sources()
    ):
        raise ValueError("matching complete development evaluation required")
    phases = [json.loads(s) for s in (path / "stream/phases.jsonl").read_text().splitlines()]
    if any(p["status"] != "complete" for p in phases) or r["stream"]["items_planned"] != 10:
        raise ValueError("ten-item successful profile phases required")
    sums = {}
    for p in phases:
        kind = p["phase"].split(":")[0]
        sums[kind] = sums.get(kind, 0) + p["elapsed_process_seconds"]
    hc = json.loads((path / "harm/cost.json").read_bytes())
    fixed = sum(v for k, v in sums.items() if k not in ("edit", "immediate", "retention"))
    parts = dict(
        acquisition_and_immediate_300=30 * (sums.get("edit", 0) + sums.get("immediate", 0)),
        retention_at_100_and_300=40 * sums.get("retention", 0),
        fixed_endpoints_twice=2 * fixed,
        full_harm=hc["elapsed_process_seconds"] * 245237 / hc["positions_completed"],
        construction_and_other=max(
            0, c["elapsed_process_seconds"] - sum(sums.values()) - hc["elapsed_process_seconds"]
        ),
    )
    return r, dict(
        components=parts,
        projected_seconds=sum(parts.values()),
        source=binding(path / "report.json"),
    )


def project(study, training, evaluation):
    expected_train = (
        {("bp", (1, 2, 3)), ("epc", (1, 2, 3))}
        if study == "pc"
        else {("bp", (1, 2, 3)), ("bp", (2, 3))}
    )
    tp, ep = {}, {}
    for path in training:
        r = json.loads((Path(path) / "report.json").read_bytes())
        validate_profile(path, r["rule"], tuple(r["read_taps"]), recipe())
        key = (r["rule"], tuple(r["read_taps"]))
        if key in tp:
            raise ValueError("duplicate training profile coordinate")
        c = json.loads((Path(path) / "cost.json").read_bytes())
        # Ten updates retain compilation costs; do not market a steady-state speed claim.
        tp[key] = dict(
            source=binding(Path(path) / "report.json"),
            projected_seconds=r["projected_update_seconds_300"]
            + max(0, c["elapsed_process_seconds"] - sum(r["update_seconds"])),
        )
    for path in evaluation:
        r, value = evaluation_components(path)
        key = (r["rule"], tuple(r["read_taps"]), tuple(r["write_sites"]), r["dataset"])
        if key in ep:
            raise ValueError("duplicate evaluation profile coordinate")
        ep[key] = value
    expected_eval = {
        (rule, taps, sites, ds)
        for rule, taps in expected_train
        for sites in ((1, 2, 3),)
        if study == "pc"
        for ds in ("zsre", "counterfact")
    }
    if study == "upper":
        expected_eval = {
            (rule, taps, sites, ds)
            for rule, taps in expected_train
            for sites in ((1, 2, 3), (3,))
            for ds in ("zsre", "counterfact")
        }
    if set(tp) != expected_train or set(ep) != expected_eval:
        raise ValueError("complete declared training/read/write/dataset profile coverage required")
    hours = (
        3
        * (
            sum(v["projected_seconds"] for v in tp.values())
            + sum(v["projected_seconds"] for v in ep.values())
        )
        / 3600
    )
    return dict(
        study=study,
        model_calls=0,
        gpu_seconds=0,
        projected_process_hours=hours,
        training_profiles={str(k): v for k, v in tp.items()},
        evaluation_profiles={str(k): v for k, v in ep.items()},
        upper_ceiling_hours=48 if study == "upper" else None,
        fits_upper_ceiling_before_retry_reserve=hours <= 48 if study == "upper" else None,
        limitations="Extrapolation from seed0, 10 edits and eight validation windows; occupancy, variable prefix shapes, cache clearing and retries may increase cost. No automatic dispatch or arm reduction. Shared full-read BP training is charged once when combining the two portfolios.",
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--study", choices=("pc", "upper"), required=True)
    p.add_argument("--training-profile", action="append", required=True)
    p.add_argument("--evaluation-profile", action="append", required=True)
    p.add_argument("--output", required=True)
    a = p.parse_args()
    result = project(a.study, a.training_profile, a.evaluation_profile)
    Path(a.output).write_text(json.dumps(result, indent=2) + "\n")
