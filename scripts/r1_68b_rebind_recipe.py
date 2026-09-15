"""Make a new, source-bound development recipe for the opt-in R1-68b driver.

This never constructs a model, draws/seals a population, or edits the source recipe.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_68b_dev_cell as driver


def rebind(source_path, source_sha256, *, profile="incremental", batch_edits=16):
    source_path = Path(source_path).resolve()
    if "confirm" in source_path.parts:
        raise PermissionError("sealed source recipe refused")
    original = driver.read_binding({"path": str(source_path), "sha256": source_sha256})
    if (
        original.get("mode") != driver.MODE
        or "reservations" in original
        or "protocol" in original
        or any(value is not False for value in original.get("admission", {}).values())
    ):
        raise PermissionError("unsealed development recipe required")
    manifest = copy.deepcopy(original)
    manifest.update(
        integrity_profile=profile,
        integrity_batch_edits=batch_edits,
        integrity_driver_bindings=driver.driver_bindings(),
        code_sha256=driver.code_identity(),
        integrity_rebind={
            "source_recipe": {"path": str(source_path), "sha256": source_sha256},
            "source_code_sha256": original["code_sha256"],
            "purpose": "development-only timing/behavioral comparison; same population and reader",
            "model_executed": False,
        },
    )
    driver.profile_config(manifest)
    payload_path = Path(manifest["payload"]["path"]).resolve()
    if not payload_path.is_relative_to(driver.PAYLOAD_ROOT):
        raise PermissionError("payload outside unsealed development resources")
    for name, expected in manifest.get("source_bindings_sha256", {}).items():
        path = Path(name).resolve()
        allowed = (
            path.is_relative_to(driver.ROOT / "manifests/dev")
            or path.is_relative_to(driver.ROOT / "manifests/revision_v1")
            or path.is_relative_to(driver.ROOT.parent / "assets/data/prepared")
        )
        if not allowed or "confirm" in path.parts or driver.sha(path) != expected:
            raise ValueError("development source path/hash mismatch")
    payload = driver.read_binding(manifest["payload"])
    driver.validate_development_payload(manifest, payload)
    if driver.code_identity() != manifest["code_sha256"]:
        raise ValueError("installed code changed during recipe construction")
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--profile", choices=("full", "incremental"), default="incremental")
    parser.add_argument("--batch-edits", type=int, default=16)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(driver.ROOT / "docs/tasks"):
        parser.error("only a new recipe file under docs/tasks may be written")
    manifest = rebind(
        args.source, args.source_sha256, profile=args.profile, batch_edits=args.batch_edits
    )
    binding = driver.write_json(output, manifest)
    driver.load_development_cell(output, binding["sha256"])
    print(json.dumps(binding, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
