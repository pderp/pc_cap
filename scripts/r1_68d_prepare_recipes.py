"""Prepare R1-68d recipes for the exact reviewed R1-74 installed-source successor.

New metadata only. Source remains untouched. These recipes intentionally refuse
execution until the expected installed tree is present; no permission is implied.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import r1_68c_dev_cell as driver
from scripts.r1_68c_rebind_recipe import rebind

from pccap.revision_v1.analysis import digest

ROOT = driver.ROOT


def expected_code():
    planned = json.loads((ROOT / "logs/r1_round17/R1-74-patch-identity.json").read_text())
    target = ROOT / planned["source"]
    preview = ROOT / "docs/tasks/R1-74-stage4_assays.preview.py"
    if driver.sha(target) not in (planned["before_sha256"], planned["after_sha256"]):
        raise ValueError("scoring source changed outside reviewed patch")
    if driver.sha(preview) != planned["after_sha256"]:
        raise ValueError("scoring preview changed")
    paths = sorted([*(ROOT / "src/pccap").rglob("*.py"), ROOT / "scripts/r1_61_cell_driver.py"])
    core = {
        str(p.relative_to(ROOT)): planned["after_sha256"] if p == target else driver.sha(p)
        for p in paths
    }
    expected = digest(
        {
            "core": digest(core),
            "integrity_driver": driver.driver_bindings(),
            "development_scripts": {
                n: driver.sha(ROOT / n)
                for n in (
                    "scripts/r1_64_dev_payload.py",
                    "scripts/r1_64_dev_cell.py",
                    "scripts/r1_64_materialize_base.py",
                )
            },
        }
    )
    return expected, planned


def prepare(profile):
    source = ROOT / "docs/tasks/R1-68b-zsre-v5-full.recipe.json"
    value = rebind(source, driver.sha(source), profile=profile)
    expected, planned = expected_code()
    value["code_sha256"] = expected
    value["integrity_rebind"].update(
        task="R1-68d",
        identity_policy="full immutable rehash at attempt start/resume/checkpoint/completion; cheap in-memory phase checks",
        expected_scoring_source=planned["source"],
        expected_scoring_sha256=planned["after_sha256"],
        preparation_method="bind exact reviewed successor source without applying it; production loader must verify the installed identity",
        permission_granted_by_this_recipe=False,
    )
    driver.profile_config(value)
    return value


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-directory", type=Path, default=ROOT / "docs/tasks")
    ap.add_argument("--report", type=Path, required=True)
    a = ap.parse_args(argv)
    directory = a.output_directory.resolve()
    paths = [
        directory / f"R1-68d-zsre-v5-{profile}.recipe.json" for profile in ("full", "incremental")
    ]
    if (
        directory != ROOT / "docs/tasks"
        or any(p.exists() for p in paths)
        or a.report.exists()
        or not a.report.resolve().is_relative_to(ROOT / "logs")
    ):
        ap.error("new standard recipe/report paths required")
    recipes = [prepare(profile) for profile in ("full", "incremental")]
    expected, planned = expected_code()
    if any(m["code_sha256"] != expected for m in recipes):
        raise ValueError("code changed during preparation")
    receipts = [driver.write_json(p, m) for p, m in zip(paths, recipes, strict=True)]
    report = {
        "task": "R1-68d",
        "recipes": receipts,
        "expected_installed_code_sha256": expected,
        "installed_code_matches_now": driver.code_identity() == expected,
        "scoring_patch_applied_by_this_tool": False,
        "model_constructed": False,
        "gpu_seconds": 0,
        "approval_required_for_existing_scoring_file": True,
        "expected_scoring_sha256": planned["after_sha256"],
        "next_step": "after user permission and inactive owner profiles, apply exact R1-74 patch; run unmocked development loader and scoring tests",
    }
    with a.report.open("x") as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
