"""R1-64c: rebind historical comparator recipes to the installed R1-68d driver.

Metadata commands never construct a model. Real-base execution is owner-only and
requires --execute; this module does not grant a GPU lease or admission.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_64b_comparator_recipes as previous
from scripts import r1_68c_dev_cell as driver
from scripts.r1_68c_rebind_recipe import rebind

ROOT = driver.ROOT


def profile_for(condition):
    if condition not in previous.CONDITIONS:
        raise ValueError("one of the eight declared comparators required")
    return "incremental" if condition.startswith("R1_") else "full"


def verify(manifest):
    condition = manifest["cell"]["condition"]
    profile = profile_for(condition)
    if manifest["integrity_profile"] != profile:
        raise ValueError("wrong comparator integrity profile")
    if (
        profile == "incremental"
        and manifest["adapter_identity"]["class"] != "pccap.revision_v1.learner.RevisionCap"
    ):
        raise ValueError("incremental profile requires exact RevisionCap")
    # R1-64b's verifier additionally insists on full for every condition. Verify
    # its historical bindings in a copy, then enforce the narrower audited
    # R1-68d condition/class rule above for our opt-in incremental recipes.
    historical = copy.deepcopy(manifest)
    historical["integrity_profile"] = "full"
    previous.verify_recipe_bindings(historical)
    for binding in manifest["r1_64c"]["bindings"].values():
        previous.verify(binding)
    driver.profile_config(manifest)
    return profile


def build(source):
    source = Path(source).resolve()
    old = json.loads(source.read_text())
    previous.verify_recipe_bindings(old)
    condition = old["cell"]["condition"]
    profile = profile_for(condition)
    manifest = rebind(source, driver.sha(source), profile=profile)
    manifest["r1_64c"] = {
        "task": "R1-64c",
        "bindings": {"source_recipe": previous.ref(source), "producer": previous.ref(__file__)},
        "entry_point": "python -m scripts.r1_64c_comparator_recipes run",
        "profile_reason": (
            "Exact RevisionCap: audited IndexedAdapter supports this class."
            if profile == "incremental"
            else "Cap/StableCap/MatchedUpdateCap are outside IndexedAdapter's exact RevisionCap type contract; full integrity required."
        ),
        "checkpoint_policy": "same bound weights and payload as R1-64b; states at 100/300 measured by execution, never predicted",
        "launch_authorized": False,
    }
    verify(manifest)
    return manifest


def inspect(path, expected):
    manifest, payload = driver.load_development_cell(path, expected)
    profile = verify(manifest)
    spec = manifest["construction"]
    return {
        "recipe": {"path": str(Path(path).resolve()), "sha256": expected},
        "cell": manifest["cell"],
        "profile": profile,
        "profile_reason": manifest["r1_64c"]["profile_reason"],
        "code_sha256": manifest["code_sha256"],
        "adapter_identity": manifest["adapter_identity"],
        "payload": manifest["payload"],
        "items": len(payload["items"]),
        "checkpoints": manifest["checkpoints"],
        "reader_checkpoint": spec.get("weights"),
        "continued_checkpoint": spec.get("continued_weights"),
        "base_snapshot": spec["base"],
        "original_base_snapshot": spec.get("original_base"),
        "expected_result_directory": str(driver.OUTPUT_ROOT / driver.cell_name(manifest, expected)),
        "expected_checkpoint_receipt_pattern": "attempt-*/checkpoint-{100,300}.receipt.json",
        "expected_state_sha256": None,
        "state_hash_note": "Observed during execution; recipe/adapter/reader/base/payload identities are bound now.",
        "model_constructed": False,
        "admission": manifest["admission"],
    }


def construct(manifest):
    verify(manifest)
    if profile_for(manifest["cell"]["condition"]) == "full":
        # This retains R1-64b's NPZ continued-base construction for both S1 arms.
        return previous.construct(manifest)
    from scripts.r1_61_cell_driver import construct_owner_adapter

    return construct_owner_adapter(manifest)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--source", type=Path, required=True)
    b.add_argument("--output", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--manifest-sha256", required=True)
    r.add_argument("--execute", action="store_true")
    r.add_argument("--resume", action="store_true")
    args = p.parse_args(argv)
    if args.command == "build":
        out = args.output.resolve()
        if out.exists() or not out.is_relative_to(ROOT / "docs/tasks"):
            p.error("new recipe under docs/tasks required")
        manifest = build(args.source)
        binding = driver.write_json(out, manifest)
        print(json.dumps(inspect(out, binding["sha256"]), indent=2))
        return 0
    if args.resume and not args.execute:
        p.error("--resume requires --execute")
    receipt = inspect(args.manifest, args.manifest_sha256)
    if not args.execute:
        print(json.dumps(receipt, indent=2))
        return 0
    manifest, _ = driver.load_development_cell(args.manifest, args.manifest_sha256)
    adapter, tokenizer = construct(manifest)
    result = driver.run_development_cell(
        args.manifest,
        args.manifest_sha256,
        adapter,
        tokenizer,
        output_root=driver.OUTPUT_ROOT,
        resource_root=driver.RESOURCE_ROOT,
        resume=args.resume,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
