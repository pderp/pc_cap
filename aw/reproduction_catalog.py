"""Collect exact input hashes and measured cost receipts for a staged refresh."""

from __future__ import annotations

import json
from pathlib import Path

from aw.refresh_reports import ROOT, save, sha


def build(out, state):
    out = Path(out)
    audit_path = out / "audit/X25/audit.json"
    artifacts, inputs = [], {}
    if audit_path.exists():
        audit = json.loads(audit_path.read_text())
        for group in audit["reports"]:
            paths = []
            for binding in group["bindings"]:
                path = binding.get("historical_archive", binding["path"])
                expected = binding["expected"]
                if path in inputs and inputs[path] != expected:
                    raise ValueError(f"conflicting source identities: {path}")
                inputs[path] = expected
                paths.append(path)
            artifacts.append(
                dict(
                    name=group["name"],
                    report=group["source"],
                    sha256=group["source_sha256"],
                    inputs=sorted(set(paths)),
                    verification=group["status"],
                )
            )
    # The supplemental audit also covers the deck. Add the antecedent tail,
    # pilot and assembly calculations that the deck cites through documents.
    from aw.supplemental_audit import Audit

    auditor = Audit()
    for label, relative in (
        ("HT-15", "ht15/cell_tails.json"),
        ("Stage-4 assembly", "stage4/assembly.json"),
        ("kappa independent review", "kappa/report.json"),
        ("PC credit settings", "pc-settings/report.json"),
    ):
        path = out / relative
        if not path.exists():
            continue
        group = auditor.report(label, path)
        if group["status"] != "PASS":
            raise ValueError(f"catalog source discrepancy: {label}")
        paths = []
        for binding in group["bindings"]:
            name = binding.get("historical_archive", binding["path"])
            inputs[name] = binding["expected"]
            paths.append(name)
        artifacts.append(
            dict(
                name=label,
                report=str(path),
                sha256=sha(path),
                inputs=sorted(set(paths)),
                verification="PASS",
            )
        )
    costs = []

    def cost(
        path, field="elapsed_process_seconds", scope="enclosing process; do not add its children"
    ):
        path = Path(path)
        if not path.exists():
            costs.append(
                dict(path=str(path), field=field, seconds=None, status="unavailable", scope=scope)
            )
            return
        d = json.loads(path.read_text())
        costs.append(
            dict(
                path=str(path),
                sha256=sha(path),
                field=field,
                seconds=d.get(field),
                status=d.get("status", "complete" if d.get("complete") else "see receipt"),
                scope=scope,
            )
        )
        inputs[str(path)] = sha(path)

    for family, runs in {
        "PC-v0": (
            "dev-profile-20260927",
            "replication-60-20260927",
            "control-k1-20260928",
            "control-k32-20260928",
            "random-control/run-20260929",
            "matched-control/run-20260929",
        ),
        "PC-v1": (
            "profile-20260927",
            "replication-4-20260927",
            "replication-4-k32-20260929",
            "replication-4-lr0.05-20260929",
            "replication-4-lr0.2-20260929",
        ),
    }.items():
        for run in runs:
            cost(
                ROOT / "results/additional_work" / family / run / "summary.json",
                scope="driver elapsed process seconds; includes its serial child cells",
            )
        for path in sorted(
            (ROOT / "results/additional_work" / family / "harm").glob("*/cost.json")
        ):
            cost(
                path,
                scope="whole harm invocation; includes per-arm readouts; failed final-table receipts retained",
            )
    for run in ("calibration-20260929", "evaluation-20260929"):
        cost(ROOT / "results/additional_work/AW-B" / run / "cost.json")
    for family in ("PC-reader", "AW-L"):
        base = ROOT / "results/additional_work" / family
        for folder in sorted(base.glob("*")):
            if folder.is_dir() and folder.name.startswith(("train-", "eval-", "profile-")):
                cost(
                    folder / "cost.json",
                    scope=f"{family} top-level process; stream/harm are included; PC-reader full-read controls reused by AW-L are charged once",
                )
    for arm in ("ordinary", "kappa02", "kappa05", "clip2"):
        for seed in range(3):
            tag = f"r1_50_stream_sel6_text_s{seed}" if arm == "ordinary" else f"ht3_{arm}_s{seed}"
            cost(
                ROOT / "results/R1/pilot" / tag / "summary.json",
                "total_wall_s",
                scope="legacy pilot training including bank construction; excludes later averaging/evaluation; ordinary family reused",
            )
    option = out / "option-r/report.json"
    if option.exists():
        cost(
            option,
            "charged_process_seconds",
            "Option R child process charges, including ceiling stop; not elapsed session time",
        )
        cost(
            option,
            "completed_segment_wall_seconds",
            "Option R closed session elapsed time; excludes idle gaps; not added to child charges",
        )
    tail = out / "ht17/report.json"
    if tail.exists():
        cost(tail, "wall_seconds", "CPU fitting only; also included in the ht17 orchestration step")
    for name in (
        "requirements.lock",
        "manifests/assets.json",
        "manifests/datasets.json",
        "manifests/revision_v1/kappa_pilot_v3.json",
        "manifests/additional_work/run_matrix_R_v1.json",
    ):
        inputs[str(ROOT / name)] = sha(ROOT / name)
    record = dict(
        schema="supplemental-reproduction-catalog-v1",
        artifacts=artifacts,
        inputs_sha256=inputs,
        costs=costs,
        cpu_commands=state["steps"],
        qualification="Each enclosing receipt is a distinct cost view. Do not sum this catalog: driver/child, session/process and shared-control costs overlap. Unknown is not zero. CPU commands never rerun GPU experiments.",
    )
    save(out / "catalog.json", record)
    return record
