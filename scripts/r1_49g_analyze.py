"""Analyze R1-75 receipt-bound reports under DEC-057/058/059; no model/payload reads."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts import r1_75_analysis_stage4_v1 as old
from scripts.r1_49g_inference import FAMILY, primary_contrasts
from scripts.r1_49g_secondary import cell_benchmarks, macro_benchmarks
from scripts.r1_d9e_near_family import CONTRACT as NEAR_CONTRACT

ROOT = Path(__file__).resolve().parents[1]


def near_family_summary(section, expected):
    summary, bounded, terminated = old.preservation_section(section, expected, "neighbour_query")
    return dict(
        family_contract=dict(NEAR_CONTRACT), bounded=bounded, terminated=terminated,
        diagnostics=summary, planned=len(expected), evaluated=bounded["scored"],
        missing=len(expected)-bounded["scored"], preserved=bounded["numerator"],
        observed_case_rate=bounded["evaluated_value"], full_inventory_rate=bounded["value"],
        interpretation="different-subject exact relation/template specificity; not semantic nearest neighbours",
        denominator_policy="planned slots retained; full rate unavailable with any missing case; no acquisition filter",
    )


def _read_verified(path, sources):
    path = Path(path).resolve()
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != sources.get(str(path)):
        raise ValueError("R1-75 report source changed or was not verified")
    return json.loads(raw)


def analyze(matrix):
    report = old.analyze(matrix)
    loaded = {c["cell_id"]: c for c in report["cells"]}
    report["historical_pointwise_contrasts"] = report.pop("contrasts")
    admitted_family = matrix.get("multiplicity") == FAMILY
    report["contrasts"] = primary_contrasts(matrix, loaded) if admitted_family else []
    report["primary_family"] = (
        FAMILY if admitted_family else {"status": "unavailable_nonregistered_matrix"}
    )
    cells, near_cells = [], []
    family = matrix.get("near_miss_family_contract")
    if family is not None and family != NEAR_CONTRACT:
        raise ValueError("unrecognized near-miss family contract")
    for declared in old.all_cells(matrix):
        observed = loaded[declared["cell_id"]]
        reports = {}
        directory = Path(declared["result_dir"]).resolve() if declared.get("result_dir") else None
        for name in report["sources_sha256"]:
            path = Path(name)
            if directory is None or not path.is_relative_to(directory):
                continue
            if (
                path.name.startswith("checkpoint-")
                and path.name.endswith(".json")
                and not path.name.endswith(".receipt.json")
            ):
                raw = _read_verified(path, report["sources_sha256"])
                n = raw.get("checkpoint")
                if str(n) not in observed.get("checkpoints", {}):
                    continue
                if n in reports:
                    raise ValueError("duplicate verified checkpoint report")
                reports[n] = raw
        cells.append(cell_benchmarks(declared, observed, reports))
        if family is not None:
            final = declared["checkpoints"][-1]
            expected = (declared.get("population") or {}).get("endpoints", {}).get("near_miss")
            if expected is None:
                near_cells.append(dict(cell_id=declared["cell_id"], status="unavailable",
                                       reason="independent near-miss population not bound"))
            else:
                section = reports.get(final, {}).get("endpoints", {}).get("near_miss")
                near_cells.append(dict(cell_id=declared["cell_id"], checkpoint=final,
                                       **near_family_summary(section, expected)))
    report["near_miss_family"] = dict(
        status="adopted_DEC061" if family is not None else "legacy_or_not_declared",
        contract=family, cells=near_cells,
    )
    report["secondary_benchmarks"] = {
        "decision": "DEC-059",
        "cells": cells,
        "macros": macro_benchmarks(matrix, cells),
        "resource_status": "No final September20 resource/ceiling receipt adapter is bound; ratios stay unavailable in file-based analysis.",
        "role": "secondary descriptive; no simultaneous significance guarantee",
    }
    report["analysis_revision"] = (
        "R1-49h_DEC057_DEC058_DEC059_DEC060"
        if matrix.get("option") == "D"
        else "R1-49g_DEC057_DEC058_DEC059"
    )
    report["dataset_layouts"] = matrix.get("dataset_layouts")
    if family is not None:
        report["analysis_revision"] = "R1-49i_DEC057_DEC058_DEC059_DEC060_DEC061"
    report["limits"] = [x for x in report["limits"] if "U12 multiplicity" not in x]
    report["limits"] += [
        FAMILY["coverage"],
        "Accepted thresholds do not confer population, execution or final scientific admission.",
        "Semantic revision is latest-answer success AND old-retired AND new-active; old acquisition is not an additional filter.",
        "Per-cell occupancy equivalence has no independent realization-cluster interval; only complete three-realization macros can report that interval.",
        "Option D leaves all MQuAKE 1000-edit primary comparisons unavailable in the unchanged 63-interval family. Actual 300-record rates are descriptive, without a transferred 1000-record threshold.",
    ]
    for name in report["sources_sha256"]:
        _read_verified(name, report["sources_sha256"])
    return report


def markdown(report):
    lines = [
        "# R1-49g — DEC-057/058/059 analysis",
        "",
        f"Scope: {report['scope']}. GPU/model calls: zero.",
        "",
        "The 63 intervals use nominal Bonferroni allocation of 0.05 and three realization clusters; exact familywise coverage is not claimed.",
        "",
        "| Dataset | Contrast | Classification | RET-GS realization estimates | Adjusted RET-GS interval |",
        "|---|---|---|---|---|",
    ]
    for r in report["contrasts"]:
        gs = r["metrics"]["RET-GS"]
        lines.append(
            f"| {r['dataset']} | {r['contrast']['id']} | {r['classification']} | {gs['realization_estimates']} | {gs['adjusted_interval']} |"
        )
    lines += [
        "",
        "Both adjusted and unadjusted intervals and all three realization estimates for every metric are in JSON.",
        "",
        "| Cell | Benchmark | Value | Pass | Availability |",
        "|---|---|---:|---|---|",
    ]
    for cell in report["secondary_benchmarks"]["cells"]:
        for name, v in cell["benchmarks"].items():
            lines.append(
                f"| {cell['cell_id']} | {name} | {v['value']} | {v['passes']} | {v['status']} |"
            )
    lines += [
        "",
        "Actual terminal occupancy (secondary descriptive; no threshold or pass decision):",
        "",
        "| Cell | Required actual records | Fires / planned | Rate | Wilson 95% | Paired change from actual 100 | Availability |",
        "|---|---:|---|---|---|---|---|",
    ]
    for cell in report["secondary_benchmarks"]["cells"]:
        v = cell["actual_occupancy_descriptive"]
        lines.append(
            f"| {cell['cell_id']} | {v['required_actual_occupancy']} | {v['fires']} / {v['planned']} | {v['value']} | {v['wilson95']} | {v['change_from_actual_100']} | {v['status']} |"
        )
    lines += [
        "",
        "| Dataset | Condition | Macro benchmark | Value | Pass | Failed cells |",
        "|---|---|---|---:|---|---|",
    ]
    for r in report["secondary_benchmarks"]["macros"]:
        lines.append(
            f"| {r['dataset']} | {r['condition']} | {r['metric']} | {r['value']} | {r['passes']} | {', '.join(r['failed_cells']) or 'none observed'} |"
        )
    near = report.get("near_miss_family", {})
    if near.get("cells"):
        lines += ["", "DEC-061 NM-template-v1 at the final planned checkpoint:", "",
                  "| Cell | Preserved / evaluated / planned | Full inventory rate | Missing |",
                  "|---|---|---|---|"]
        for r in near["cells"]:
            lines.append(f"| {r['cell_id']} | {r.get('preserved')} / {r.get('evaluated')} / {r.get('planned')} | {r.get('full_inventory_rate')} | {r.get('missing')} |")
        lines += ["", "Bounded equality compares each neighbour with its actual cap-off baseline. Missing planned slots remain missing; support-edit acquisition does not filter the denominator. This measures exact relation/template specificity, not semantic nearest-neighbour robustness."]
    lines += [
        "",
        "Resource ceilings remain unadmitted. Macro unavailability and missing cell results cannot be read as passes.",
        "",
        *report["limits"],
        "",
    ]
    return "\n".join(lines)


def run(matrix_path, output_prefix):
    matrix_path, prefix = Path(matrix_path).resolve(), Path(output_prefix).resolve()
    if not any(
        matrix_path.is_relative_to(ROOT / p) for p in ("docs/tasks", "manifests/revision_v1")
    ):
        raise PermissionError("declared repository analysis matrix required")
    outputs = [Path(str(prefix) + suffix) for suffix in (".json", ".md")]
    if any(p.exists() or not p.is_relative_to(ROOT / "logs") for p in outputs):
        raise FileExistsError("new output paths under logs required")
    raw = matrix_path.read_bytes()
    report = analyze(json.loads(raw))
    report["matrix_file"] = {"path": str(matrix_path), "sha256": hashlib.sha256(raw).hexdigest()}
    names = [
        "scripts/r1_49g_analyze.py",
        "scripts/r1_d9e_near_family.py",
        "scripts/r1_49g_inference.py",
        "scripts/r1_49g_secondary.py",
        "scripts/r1_75_analysis_stage4_v1.py",
        "src/pccap/revision_v1/analysis.py",
        "scripts/r1_74_rescore.py",
        "scripts/ht_audit_existing.py",
    ]
    report["analysis_source_sha256"] = {
        name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in names
    }
    if matrix_path.read_bytes() != raw:
        raise ValueError("matrix changed during analysis")
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    rendered = markdown(report)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    with outputs[0].open("x") as f:
        f.write(encoded)
    with outputs[1].open("x") as f:
        f.write(rendered)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args(argv)
    value = run(args.matrix, args.output_prefix)
    print(
        json.dumps(
            {
                "cells": len(value["cells"]),
                "primary_comparisons": len(value["contrasts"]),
                "gpu_seconds": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
