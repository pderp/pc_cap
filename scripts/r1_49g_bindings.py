"""Additive DEC-057/058/059 analysis-matrix binding; preserves every execution gate."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

from scripts.r1_49g_inference import FAMILY, validate_family
from scripts.r1_49g_secondary import THRESHOLDS

ROOT = Path(__file__).resolve().parents[1]


def binding(path):
    path = (ROOT / Path(path)).resolve()
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build():
    source = ROOT / "manifests/revision_v1/run_matrix_v5.json"
    value = copy.deepcopy(json.loads(source.read_text()))
    for path, expected in value["sources_sha256"].items():
        if binding(path)["sha256"] != expected:
            raise ValueError("parent matrix binding changed: " + path)
    if len(value["cells"]) != 360 or len(value["extension"]["cells"]) != 45:
        raise ValueError("matrix scope changed")
    value.update(
        name="run_matrix_v5_1",
        task="R1-49g",
        status="confirmation_draft_accepted_analysis_rules",
        schema_version=6,
    )
    value["historical_matrix_v5"] = binding(source)
    value["protocol"] = binding("docs/R1_stage4_protocol_draft_v5_1.md")
    value["multiplicity"] = copy.deepcopy(FAMILY)
    value["classifier"] = {
        "decision": "DEC-058",
        "priority": ["unavailable", "negative", "positive", "qualified", "inconclusive"],
        "implementation": binding("scripts/r1_49g_inference.py"),
    }
    value["secondary_benchmarks"] = {
        "decision": "DEC-059",
        "thresholds": THRESHOLDS,
        "role": "secondary_descriptive",
        "implementation": binding("scripts/r1_49g_secondary.py"),
        "resource_ceilings_admitted": False,
    }
    value["analysis_entrypoint"] = binding("scripts/r1_49g_analyze.py")
    value["analysis_binding_producer"] = binding(__file__)
    value["open_lead_items"] = [
        x
        for x in value["open_lead_items"]
        if x
        not in (
            "Q4 kappa",
            "Q5 stress",
            "U12 multiplicity",
            "U14 secondary thresholds",
            "Q10 MQuAKE occupancy",
        )
    ]
    value["accepted_decisions"] = {}
    lines = (ROOT / "docs/decisions.md").read_text().splitlines()
    for decision in ("DEC-054", "DEC-055", "DEC-056", "DEC-057", "DEC-058", "DEC-059"):
        matches = [line for line in lines if line.startswith("| " + decision + " |")]
        if len(matches) != 1:
            raise ValueError("unique accepted decision row required")
        row = matches[0]
        value["accepted_decisions"][decision] = {
            "row": row,
            "sha256": hashlib.sha256(row.encode()).hexdigest(),
        }
    for b in (
        value["historical_matrix_v5"],
        value["protocol"],
        value["classifier"]["implementation"],
        value["secondary_benchmarks"]["implementation"],
        value["analysis_entrypoint"],
        value["analysis_binding_producer"],
    ):
        value["sources_sha256"][b["path"]] = b["sha256"]
    value["analysis_admission_note"] = (
        "Accepted analysis decisions do not authorize draw, seal, launch, costs or scientific admission. R1-68e hook, R1-64d recipes and sealed donor reconciliation remain separate."
    )
    validate_family(value)
    if any(
        value[k] is not False
        for k in ("confirmation_protocol_frozen", "draw_authorized", "launch_allowed")
    ):
        raise ValueError("analysis rebinding cannot grant execution authority")
    if any(
        c["admitted"] is not False or c["launch_allowed"] is not False
        for c in [*value["cells"], *value["extension"]["cells"]]
    ):
        raise ValueError("draft cells must remain unadmitted")
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "manifests/revision_v1"):
        raise FileExistsError("new manifest path required")
    value = build()
    with output.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "matrix": str(output),
                "core_cells": 360,
                "extension_cells": 45,
                "family_intervals": 63,
                "launch_allowed": False,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
