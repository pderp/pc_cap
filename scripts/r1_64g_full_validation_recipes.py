"""Inspect the DEC-063 recipe plan; build new identities only after owner patch application."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_64e_rebind_recipes as rebinder
from scripts import r1_68c_dev_cell as driver
from scripts import r1_68f_full_validation as full
from scripts.r1_d10a_review import write_new

ROOT = driver.ROOT


def sources():
    return sorted((ROOT / "docs/tasks/R1-64f").glob("*.recipe.json"))


def plan():
    spec = full.make_spec()
    full.validate_spec(dict(full_validation=spec))
    rows = []
    for path in sources():
        original = json.loads(path.read_text())
        data = driver.read_binding(original["payload"])
        proposed = {**original, "full_validation": spec}
        full.validate_sample(proposed, data["endpoints"]["drift"])
        if (
            len(data["items"]) != 300
            or original["checkpoints"] != [100, 300]
            or len(data["endpoints"]["near_miss"]["expected_ids"]) != 100
            or len(data["endpoints"]["revision"]["expected_ids"]) != 50
        ):
            raise ValueError("R1-64f endpoint inventory/cadence changed")
        rows.append(
            dict(
                source=full.ref(path),
                cell=original["cell"],
                payload=original["payload"],
                checkpoints=[100, 300],
                edits=300,
                near_miss=100,
                revision=50,
                full_validation=spec,
                model_constructed=False,
            )
        )
    keys = {(r["cell"]["dataset"], r["cell"]["condition"]) for r in rows}
    if (
        keys != {(ds, c) for ds in ("zsre", "mquake") for c in ("R1_learned_ff", "v0_stable")}
        or len(rows) != 4
    ):
        raise ValueError("exactly the four declared development measurements are required")
    return dict(
        task="R1-64g",
        status="prepared_waiting_for_installed_R1-68f",
        recipes=rows,
        gpu_seconds=0,
        model_constructed=False,
        canonical_frozen_manifest_written=False,
    )


def require_installed():
    if "scripts/r1_68f_full_validation.py" not in driver.DRIVER_FILES:
        raise RuntimeError("R1-68f driver patch has not been installed by the orchestrator")
    record = json.loads((ROOT / "logs/r1_round30/r1-68f-patch.json").read_text())
    identities = {
        **record["proposed_files_sha256"],
        **record["new_implementation_files_sha256"],
    }
    successor = json.loads((ROOT / "logs/r1_round31/r1-63l-backend-patch.json").read_text())
    target = successor["target"]
    if identities.get(target) != successor["original_sha256"]:
        raise ValueError("R1-63l is not a reviewed successor of the R1-68f backend")
    identities[target] = successor["proposed_sha256"]
    for name, expected in identities.items():
        if driver.sha(ROOT / name) != expected:
            raise ValueError("installed driver/backend differs from reviewed R1-68f bytes")


def build(output):
    require_installed()
    proposed = plan()
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "docs/tasks") or output.exists():
        raise ValueError("R1-64g requires a new output directory under docs/tasks")
    output.mkdir(parents=True)
    inspections = []
    for row in proposed["recipes"]:
        source = Path(row["source"]["path"])
        manifest = rebinder.rebind_current(source)
        manifest["full_validation"] = row["full_validation"]
        # Preserve population, adapter weights and all current timing settings.
        path = output / source.name.replace("R1-64f-", "R1-64g-")
        binding = driver.write_json(path, manifest)
        loaded, data = driver.load_development_cell(path, binding["sha256"])
        full.validate_sample(loaded, data["endpoints"]["drift"])
        inspections.append(
            dict(
                recipe=binding,
                cell=manifest["cell"],
                items=len(data["items"]),
                full_validation=manifest["full_validation"],
                model_constructed=False,
            )
        )
    write_new(output / "inspection-receipts.json", inspections)
    lines = [
        "# R1-64g — full-validation cost measurements",
        "",
        "Four new development identities. Keep the R1-64f payloads, weights and challenge sets.",
        "Sample at 100 and 300 edits; full validation only at 300. Never resume an older identity.",
        "Inspect on CPU below. The orchestrator adds --execute under the GPU lease.",
        "Wrap each execution in /usr/bin/time -v with a separate .time log; retain the memory monitor.",
        "Read full_validation:300 outer phase wall and NPZ-bound endpoint metadata for cost v4.",
        "",
    ]
    for r in inspections:
        b = r["recipe"]
        lines += [
            f"{r['cell']['dataset']} / {r['cell']['condition']}",
            "",
            "```bash",
            f"../venv/bin/python -m scripts.r1_68c_dev_cell --manifest {b['path']} --manifest-sha256 {b['sha256']}",
            "```",
            "",
        ]
    with (output / "ordered-runlist.md").open("x") as stream:
        stream.write("\n".join(lines))
    return dict(
        task="R1-64g",
        status="inspected_ready_for_owner_execution",
        inspections=inspections,
        driver_code_sha256=driver.code_identity(),
        gpu_seconds=0,
        model_constructed=False,
    )


def rebind_active(output):
    """Reuse R1-64e's strict rebinder in a new namespace; preserve historical directories."""
    require_installed()
    output = Path(output).resolve()
    if not output.is_relative_to(ROOT / "docs/tasks") or output.exists():
        raise ValueError("active recipe rebinding requires a new docs/tasks directory")
    output.mkdir(parents=True)
    rows = []
    for source_dir in ("R1-64e", "R1-64f"):
        directory = output / source_dir
        directory.mkdir()
        for source in sorted((ROOT / "docs/tasks" / source_dir).glob("*.recipe.json")):
            manifest = rebinder.rebind_current(source)
            path = directory / source.name
            inspector = (
                rebinder.comparator.inspect
                if "r1_64c" in manifest and "r1_64f" not in manifest
                else None
            )
            rows.append(rebinder.write_recipe(path, manifest, inspector))
    parents = output / "R1-73b-post68f"
    corrected = output / "R1-73d-post68f"
    parents.mkdir()
    corrected.mkdir()
    for source in sorted((ROOT / "docs/tasks/R1-73d-post77d").glob("*.recipe.json")):
        old = json.loads(source.read_text())
        old_parent = driver.read_binding(old["r1_73d"]["bindings"]["source_recipe"])
        condition = old["cell"]["condition"]
        parent = rebinder.mquake.build(
            output / f"R1-64e/R1-64e-zsre-{condition}.recipe.json",
            ROOT / "manifests/revision_v1/calibration_v3.json",
            old_parent["payload"],
            old_parent["source_bindings_sha256"],
        )
        parent_path = parents / f"R1-73b-mquake-{condition}.recipe.json"
        rebinder.write_recipe(parent_path, parent, rebinder.mquake.inspect)
        value = copy.deepcopy(parent)
        payload = driver.read_binding(old["payload"])
        value["payload"] = old["payload"]
        value["r1_73b"]["population"] = payload["development_summary"]
        value["r1_73d"] = copy.deepcopy(old["r1_73d"])
        value["r1_73d"]["bindings"]["source_recipe"] = full.ref(parent_path)
        ignored = {
            "code_sha256",
            "integrity_driver_bindings",
            "integrity_rebind",
            "r1_73b",
            "r1_73d",
        }
        if {k: v for k, v in value.items() if k not in ignored} != {
            k: v for k, v in old.items() if k not in ignored
        }:
            raise ValueError("corrected MQuAKE rebuild changed experimental settings")
        rows.append(
            rebinder.write_recipe(corrected / source.name, value, rebinder.locality.inspect)
        )
    write_new(output / "inspection-receipts.json", rows)
    return dict(
        task="R1-64g",
        rebound_active_recipes=len(rows),
        rebuilt_parent_recipes=8,
        recipes=rows,
        note="Historical measurements remain bound to historical recipes; rebinding is not a rerun or DEC-063 enablement.",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path)
    parser.add_argument("--build", type=Path)
    parser.add_argument("--rebind-active", type=Path)
    args = parser.parse_args()
    if sum(x is not None for x in (args.plan, args.build, args.rebind_active)) != 1:
        parser.error("choose exactly one action")
    if args.plan:
        value = write_new(args.plan, plan())
    elif args.build:
        value = build(args.build)
    else:
        value = rebind_active(args.rebind_active)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
