"""MQuAKE comparator profile recipes bound to development calibration v3.

Build/inspect never instantiate a base. --execute is reserved for the owner.
The profiling population is explicitly exposed development/training data.
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np
from scripts import r1_64c_comparator_recipes as comparator
from scripts import r1_68c_dev_cell as driver
from scripts.r1_64_dev_payload import payload_from_documents
from scripts.r1_64b_comparator_recipes import metadata_identity, ref
from scripts.r1_64b_comparator_recipes import verify as checked
from scripts.r1_73b_calibration_v3 import EXACT_NOTE

from pccap.contracts import Budget
from pccap.revision_v1.analysis import digest
from pccap.revision_v1.checkpoint_identity import checkpoint_tree

ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = comparator.previous.CONDITIONS


def make_payload():
    bindings = {}

    def read(path):
        path = (ROOT / Path(path)).resolve()
        bindings[str(path)] = driver.sha(path)
        return json.loads(path.read_text())

    dev = read("manifests/dev/mquake_dev_v3b.json")
    train = read("manifests/revision_v1/train_pool_mquake_v3.json")
    challenges = read("manifests/dev/challenges.json")
    inventory = read("manifests/revision_v1/mquake_items_v1.json")
    composition = inventory["artifacts"]["composition"]
    path = checked(composition)
    bindings[str(path)] = composition["sha256"]
    cases = [json.loads(line) for line in path.read_text().splitlines()]
    drift = ROOT.parent / "assets/data/prepared/lm/drift_tokens.npy"
    bindings[str(drift)] = driver.sha(drift)
    payload = payload_from_documents(
        "mquake", dev, train, challenges, cases, np.load(drift, allow_pickle=False), 300
    )
    payload["development_summary"].update(
        population_purpose="300-attempt comparator cost/behavior development profile; NOT the DEC-056 historical outside-occupancy diagnostic",
        locality_note="first 50 v3b unrelated prompts, from the already exposed training pool; some are also profile edits",
        training_pool_note="100 v3b development edits plus 200 selected-reader training-pool fillers; outside 100 also comes from this training pool. No reader-training independence or fresh-confirmation claim.",
    )
    for name, h in bindings.items():
        if driver.sha(name) != h:
            raise ValueError("payload source changed")
    return payload, bindings


def verify_calibration(path):
    cal = json.loads(Path(path).read_text())
    if (
        cal.get("task") != "R1-73b"
        or cal.get("scope") != "development"
        or cal.get("development_admitted") is not True
        or cal.get("confirmation_admitted") is not False
        or cal.get("launch_authorized") is not False
        or cal.get("exact_key_note") != EXACT_NOTE
    ):
        raise ValueError("admitted development calibration v3 required")
    if digest({k: v for k, v in cal.items() if k != "content_sha256"}) != cal.get("content_sha256"):
        raise ValueError("calibration content hash mismatch")
    if cal["calibration"]["BP"]["radii"]["mquake"] != {"1": 0.0, "2": 0.0, "3": 0.0}:
        raise ValueError("exact-key fallback required")
    for name, h in cal["bindings_sha256"].items():
        checked({"path": name, "sha256": h})
    return cal


def build(source, calibration_path, payload_binding, source_bindings):
    source = Path(source).resolve()
    m = json.loads(source.read_text())
    comparator.verify(m)
    condition = m["cell"]["condition"]
    if m["cell"]["dataset"] not in ("zsre", "counterfact") or (
        not condition.startswith("R1_") and m.get("r1_64d", {}).get("task") != "R1-64d"
    ):
        raise ValueError("current R1-64d comparator template required")
    if m["code_sha256"] != driver.code_identity():
        raise ValueError("template driver mismatch")
    cal = verify_calibration(calibration_path)
    payload = json.loads(checked(payload_binding).read_text())
    if len(payload["items"]) != 300 or any(r["dataset"] != "mquake" for r in payload["items"]):
        raise ValueError("complete 300-edit MQuAKE development profile required")
    m = copy.deepcopy(m)
    spec = m["construction"]
    spec["calibration"] = {
        "bank_scales": cal["b_m"],
        "radii": cal["calibration"]["BP"]["radii"]["mquake"],
    }
    identity = m["adapter_identity"]
    if identity["locality_base_sha256"] != cal["base_tensor_sha256"]:
        raise ValueError("calibration/base identity differs")
    params = checkpoint_tree(checked(spec["weights"])) if "weights" in spec else None
    stop = (
        json.loads(checked(spec["stop_tokens"]).read_text())["tokens"]
        if "stop_tokens" in spec
        else []
    )
    config = json.loads((Path(spec["base"]["path"]) / "config.json").read_text())
    m["adapter_identity"] = metadata_identity(
        condition,
        d=config["n_embd"],
        base_hash=identity["base_sha256"],
        original_hash=identity["locality_base_sha256"],
        calibration=spec["calibration"],
        seed=spec["seed"],
        stop_tokens=stop,
        params=params,
        budget=Budget(**spec["budget"]),
    )
    m["cell"].update(dataset="mquake", realization="development_calibration_v3", order="source")
    m.update(
        payload=payload_binding,
        source_bindings_sha256=source_bindings,
        checkpoints=[100, 300],
        integrity_driver_bindings=driver.driver_bindings(),
        code_sha256=driver.code_identity(),
        drift_implementation="profile_default" if condition.startswith("R1_") else "v0_batched_v1",
    )
    m["r1_73b"] = {
        "task": "R1-73b",
        "bindings": {
            "source_recipe": ref(source),
            "producer": ref(__file__),
            "calibration": ref(calibration_path),
            "calibration_auditor": ref(ROOT / "scripts/r1_73b_calibration_v3.py"),
            "U08_addendum": ref(ROOT / "docs/R1_stage4_U08_mquake_calibration_v3.md"),
        },
        "entry_point": "python -m scripts.r1_73b_comparator_recipes run",
        "exact_key_note": EXACT_NOTE,
        "applies_to_this_condition": not condition.startswith("R1_"),
        "reader_note": "RevisionCap conditions retain their own gates; radius 0 applies only to the six v0-style families.",
        "continued_base_transfer": cal["continued_base_transfer"],
        "population": payload["development_summary"],
        "historical_template_note": "R1-64b/c/d metadata is source-template provenance; R1-73b defines the current dataset, payload and calibration.",
        "state_hash": "measured by owner execution; not predicted",
        "launch_authorized": False,
    }
    verify(m)
    driver.validate_development_payload(m, payload)
    return m


def verify(m):
    comparator.verify(m)
    detail = m.get("r1_73b", {})
    if detail.get("task") != "R1-73b" or detail.get("exact_key_note") != EXACT_NOTE:
        raise ValueError("MQuAKE calibration recipe required")
    for b in detail["bindings"].values():
        checked(b)
    if detail["bindings"]["producer"] != ref(__file__):
        raise ValueError("recipe producer changed")
    cal = verify_calibration(checked(detail["bindings"]["calibration"]))
    expected = {"bank_scales": cal["b_m"], "radii": cal["calibration"]["BP"]["radii"]["mquake"]}
    if m["construction"]["calibration"] != expected or m["cell"]["dataset"] != "mquake":
        raise ValueError("dataset calibration mismatch")
    if m["code_sha256"] != driver.code_identity():
        raise ValueError("driver identity changed")
    condition = m["cell"]["condition"]
    wanted = "profile_default" if condition.startswith("R1_") else "v0_batched_v1"
    if m.get("drift_implementation") != wanted:
        raise ValueError("wrong MQuAKE drift dispatch")
    if m["checkpoints"] != [100, 300]:
        raise ValueError("registered profile cadence changed")
    return m


def inspect(path, expected):
    m, p = driver.load_development_cell(path, expected)
    verify(m)
    return {
        "recipe": ref(path),
        "cell": m["cell"],
        "items": len(p["items"]),
        "checkpoints": m["checkpoints"],
        "code_sha256": m["code_sha256"],
        "adapter_identity": m["adapter_identity"],
        "integrity_profile": m["integrity_profile"],
        "drift_implementation": m["drift_implementation"],
        "calibration": m["r1_73b"]["bindings"]["calibration"],
        "radii": m["construction"]["calibration"]["radii"],
        "exact_key_note": EXACT_NOTE,
        "payload": m["payload"],
        "population": p["development_summary"],
        "continued_checkpoint": m["construction"].get("continued_weights"),
        "reader_checkpoint": m["construction"].get("weights"),
        "state_sha256": None,
        "expected_result_directory": str(driver.OUTPUT_ROOT / driver.cell_name(m, expected)),
        "model_constructed": False,
        "admission": m["admission"],
    }


def build_all(output_dir, resource_dir, calibration_path):
    output_dir, resource_dir = Path(output_dir).resolve(), Path(resource_dir).resolve()
    if (
        output_dir.exists()
        or resource_dir.exists()
        or not output_dir.is_relative_to(ROOT / "docs/tasks")
        or not resource_dir.is_relative_to(driver.PAYLOAD_ROOT)
    ):
        raise FileExistsError(
            "new task recipe directory and new unsealed assets payload directory required"
        )
    verify_calibration(calibration_path)
    payload, bindings = make_payload()
    resource_dir.mkdir(parents=True, exist_ok=False)
    payload_binding = driver.write_json(resource_dir / "payload.json", payload)
    manifests = [
        build(
            ROOT / f"docs/tasks/R1-64d/R1-64d-zsre-{c}.recipe.json",
            calibration_path,
            payload_binding,
            bindings,
        )
        for c in CONDITIONS
    ]
    output_dir.mkdir(parents=True, exist_ok=False)
    inspections = []
    for m in manifests:
        path = output_dir / f"R1-73b-mquake-{m['cell']['condition']}.recipe.json"
        binding = driver.write_json(path, m)
        inspections.append(inspect(path, binding["sha256"]))
    with (output_dir / "inspection-receipts.json").open("x") as f:
        json.dump(inspections, f, indent=2, sort_keys=True)
        f.write("\n")
    lines = [
        "# R1-73b MQuAKE development comparator run list",
        "",
        EXACT_NOTE,
        "",
        "Owner GPU execution only; acquire the lease and retain every failure cost.",
        "300 attempts: 100 v3b development plus 200 exposed training fillers. This is not the DEC-056 unseen-population diagnostic.",
        "Near-miss/revision shortfalls are explicit; zero-row phases cannot price the final inventories.",
        "",
        "| Order | Condition | Integrity | Drift |",
        "|---:|---|---|---|",
    ]
    for i, r in enumerate(inspections, 1):
        lines.append(
            f"| {i} | {r['cell']['condition']} | {r['integrity_profile']} | {r['drift_implementation']} |"
        )
    for r in inspections:
        command = f"../venv/bin/python -m scripts.r1_73b_comparator_recipes run --manifest {r['recipe']['path']} --manifest-sha256 {r['recipe']['sha256']}"
        lines.extend(
            [
                "",
                f"{r['cell']['condition']} — inspect; append `--execute` only for owner execution:",
                "",
                "```bash",
                command,
                "```",
            ]
        )
    with (output_dir / "ordered-runlist.md").open("x") as f:
        f.write("\n".join(lines) + "\n")
    return inspections


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    b = sub.add_parser("build")
    b.add_argument("--output-dir", type=Path, required=True)
    b.add_argument("--resources", type=Path, required=True)
    b.add_argument("--calibration", type=Path, required=True)
    r = sub.add_parser("run")
    r.add_argument("--manifest", type=Path, required=True)
    r.add_argument("--manifest-sha256", required=True)
    r.add_argument("--execute", action="store_true")
    r.add_argument("--resume", action="store_true")
    args = p.parse_args(argv)
    if args.command == "build":
        report = build_all(args.output_dir, args.resources, args.calibration)
        print(json.dumps({"recipes": len(report), "model_constructed": False}))
        return 0
    if args.resume and not args.execute:
        p.error("resume requires execute")
    receipt = inspect(args.manifest, args.manifest_sha256)
    if not args.execute:
        print(json.dumps(receipt, indent=2))
        return 0
    m, _ = driver.load_development_cell(args.manifest, args.manifest_sha256)
    verify(m)
    adapter, tok = comparator.construct(m)
    result = driver.run_development_cell(
        args.manifest,
        args.manifest_sha256,
        adapter,
        tok,
        output_root=driver.OUTPUT_ROOT,
        resource_root=driver.RESOURCE_ROOT,
        resume=args.resume,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
