"""Rebuild the development recipe chain after the R1-77d installed-tree patch.

Historical manifests stay immutable. Rebind before invoking verifiers that
correctly require the current driver; never relax their identity checks.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

from scripts import r1_64c_comparator_recipes as comparator
from scripts import r1_68c_dev_cell as driver
from scripts import r1_73b_comparator_recipes as mquake
from scripts import r1_73d_locality_recipes as locality
from scripts.r1_64b_comparator_recipes import ref
from scripts.r1_68c_rebind_recipe import rebind

ROOT = driver.ROOT


def rebind_current(path):
    """Preserve every experimental field, including dispatch and batch sizes."""
    path = Path(path).resolve()
    original = json.loads(path.read_text())
    result = rebind(
        path,
        driver.sha(path),
        profile=original["integrity_profile"],
        batch_edits=original["integrity_batch_edits"],
    )
    allowed = {"code_sha256", "integrity_driver_bindings", "integrity_rebind"}
    if {k: v for k, v in result.items() if k not in allowed} != {
        k: v for k, v in original.items() if k not in allowed
    }:
        raise ValueError("rebinding changed an experimental setting")
    return result


def write_recipe(path, manifest, inspect=None):
    if path.exists():
        raise FileExistsError(path)
    binding = driver.write_json(path, manifest)
    driver.load_development_cell(path, binding["sha256"])
    if inspect:
        return inspect(path, binding["sha256"])
    return dict(recipe=binding, cell=manifest["cell"], model_constructed=False)


def build_all():
    output = ROOT / "docs/tasks/R1-64e"
    parents = ROOT / "docs/tasks/R1-73b-post77d"
    corrected = ROOT / "docs/tasks/R1-73d-post77d"
    for directory in (output, parents, corrected):
        if directory.exists() and any(directory.iterdir()):
            raise FileExistsError(f"nonempty output directory: {directory}")
        directory.mkdir(parents=True, exist_ok=True)
    records = []
    for dataset in ("zsre", "counterfact"):
        for condition in comparator.previous.CONDITIONS:
            source = ROOT / f"docs/tasks/R1-64d/R1-64d-{dataset}-{condition}.recipe.json"
            value = rebind_current(source)
            comparator.verify(value)
            path = output / f"R1-64e-{dataset}-{condition}.recipe.json"
            records.append(write_recipe(path, value, comparator.inspect))
    primary_source = ROOT / "docs/tasks/R1-68e-zsre-v5-incremental.recipe.json"
    primary = write_recipe(
        output / "R1-64e-zsre-primary-v5.recipe.json", rebind_current(primary_source)
    )
    # Rebuild intermediate calibration recipes from current zsRE templates.
    # Keeping these stages explicit avoids treating historical code as current.
    inspections = []
    for condition in comparator.previous.CONDITIONS:
        old_path = ROOT / f"docs/tasks/R1-73b/R1-73b-mquake-{condition}.recipe.json"
        old = json.loads(old_path.read_text())
        parent = mquake.build(
            output / f"R1-64e-zsre-{condition}.recipe.json",
            ROOT / "manifests/revision_v1/calibration_v3.json",
            old["payload"],
            old["source_bindings_sha256"],
        )
        parent_path = parents / f"R1-73b-mquake-{condition}.recipe.json"
        write_recipe(parent_path, parent, mquake.inspect)
        old_corrected_path = ROOT / f"docs/tasks/R1-73d/R1-73d-mquake-{condition}.recipe.json"
        old_corrected = json.loads(old_corrected_path.read_text())
        payload = driver.read_binding(old_corrected["payload"])
        value = copy.deepcopy(parent)
        value["payload"] = old_corrected["payload"]
        value["r1_73b"]["population"] = payload["development_summary"]
        value["r1_73d"] = copy.deepcopy(old_corrected["r1_73d"])
        value["r1_73d"]["bindings"]["source_recipe"] = ref(parent_path)
        locality.verify(value, payload)
        # No new population, selection, adapter, or runtime setting is admitted.
        provenance = {"code_sha256", "integrity_driver_bindings", "integrity_rebind",
                      "r1_73b", "r1_73d"}
        if {k: v for k, v in value.items() if k not in provenance} != {
            k: v for k, v in old_corrected.items() if k not in provenance
        }:
            raise ValueError("post-patch MQuAKE recipe changed scientific settings")
        path = corrected / f"R1-73d-mquake-{condition}.recipe.json"
        inspections.append(write_recipe(path, value, locality.inspect))
    for directory, rows, module in (
        (output, [*records, primary], "scripts.r1_64c_comparator_recipes"),
        (corrected, inspections, "scripts.r1_73d_locality_recipes"),
    ):
        locality.metadata_json(directory / "inspection-receipts.json", rows)
        lines = ["# Post-R1-77d development recipes", "",
                 "CPU inspection below. Owner-only execution adds `--execute` with the lease.",
                 "New attempt identities; do not resume historical attempts.", ""]
        for row in rows:
            binding = row["recipe"]
            entry = "scripts.r1_68c_dev_cell" if row is primary else module
            subcommand = "" if row is primary else " run"
            lines += [f"{row['cell']['dataset']} / {row['cell']['condition']}", "", "```bash",
                      f"../venv/bin/python -m {entry}{subcommand} --manifest {binding['path']} --manifest-sha256 {binding['sha256']}",
                      "```", ""]
        (directory / "ordered-runlist.md").write_text("\n".join(lines))
    report = dict(
        task="R1-64e", producer=ref(__file__),
        installed_driver_code_sha256=driver.code_identity(),
        integrity_driver_bindings=driver.driver_bindings(),
        old_driver_code_sha256=json.loads(primary_source.read_text())["code_sha256"],
        comparator_recipes=records, primary=primary, mquake_recipes=inspections,
        builder_bindings=[ref(ROOT / f"scripts/{name}.py") for name in (
            "r1_64c_comparator_recipes", "r1_73b_comparator_recipes", "r1_73d_locality_recipes",
            "r1_68c_rebind_recipe")],
        payloads_changed=False, model_constructed=False, gpu_seconds=0,
        note="Rebind before current-identity verification. Existing builders and strict run guards remain intact; use this entry point to rebuild their complete dependency chain.",
    )
    locality.metadata_json(ROOT / "logs/r1_round25/r1-64e-build.json", report)
    return report


if __name__ == "__main__":
    result = build_all()
    print(json.dumps({k: result[k] for k in (
        "task", "installed_driver_code_sha256", "old_driver_code_sha256", "model_constructed")}, indent=2))
