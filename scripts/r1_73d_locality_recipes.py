"""Rebuild MQuAKE development locality and eight recipes; default run only inspects."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_73b_comparator_recipes as previous
from scripts.r1_64b_comparator_recipes import ref
from scripts.r1_64b_comparator_recipes import verify as checked
from scripts.r1_locality_contract import select_unrelated, validate_locality

ROOT, driver = previous.ROOT, previous.driver
NOTE = "First 50 distinct v3b unrelated source prompts excluding every prompt/paraphrase in the full 300-edit stream; exposed development/training data, not fresh confirmation."


def metadata_json(path, value):
    with Path(path).open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    return ref(path)


def corrected_payload(original, unrelated):
    payload = copy.deepcopy(original)
    rows, audit = select_unrelated(payload["items"], unrelated)
    assert [r["item_id"] for r in rows] == payload["endpoints"]["locality"]["expected_ids"]
    payload["endpoints"]["locality"]["rows"] = rows
    payload["development_summary"]["locality_note"] = NOTE
    verify_payload_change(original, payload, unrelated)
    return payload, audit


def verify_payload_change(original, payload, unrelated):
    rows, _ = select_unrelated(original["items"], unrelated)
    expected = copy.deepcopy(original)
    expected["endpoints"]["locality"]["rows"] = rows
    expected["development_summary"]["locality_note"] = NOTE
    if expected != payload:
        raise ValueError(
            "only the deterministic locality rows and their explanatory note may change"
        )
    validate_locality(payload["items"], payload["endpoints"]["locality"]["rows"])


def verify(m, payload):
    previous.verify(m)
    detail = m.get("r1_73d", {})
    if detail.get("task") != "R1-73d" or detail.get("launch_authorized") is not False:
        raise ValueError("versioned R1-73d development provenance required")
    for b in detail["bindings"].values():
        checked(b)
    if detail["bindings"]["producer"] != ref(__file__):
        raise ValueError("locality producer changed")
    parent = json.loads(checked(detail["bindings"]["source_recipe"]).read_text())
    original = json.loads(checked(parent["payload"]).read_text())
    dev = json.loads(checked(detail["bindings"]["unrelated_source"]).read_text())
    _, expected_audit = select_unrelated(original["items"], dev["unrelated_prompts"])
    if detail["selection_audit"] != expected_audit:
        raise ValueError("locality selection audit differs")
    verify_payload_change(original, payload, dev["unrelated_prompts"])
    expected = copy.deepcopy(parent)
    expected.update(payload=m["payload"], r1_73d=detail)
    expected["r1_73b"]["population"] = payload["development_summary"]
    if expected != m:
        raise ValueError(
            "recipe differs beyond locality/provenance; all experiment settings must stay identical"
        )
    if (
        m["code_sha256"] != driver.code_identity()
        or m["integrity_driver_bindings"] != driver.driver_bindings()
    ):
        raise ValueError("current installed driver identity required")
    driver.validate_development_payload(m, payload)


def inspect(path, expected):
    m, payload = driver.load_development_cell(path, expected)
    verify(m, payload)
    receipt = previous.inspect(path, expected)
    receipt.update(
        task="R1-73d",
        locality_overlap_count=0,
        source_recipe=m["r1_73d"]["bindings"]["source_recipe"],
        locality_audit=m["r1_73d"]["selection_audit"],
    )
    return receipt


def build_all(output, resources):
    output, resources = Path(output).resolve(), Path(resources).resolve()
    if (
        output.exists()
        or resources.exists()
        or not output.is_relative_to(ROOT / "docs/tasks")
        or not resources.is_relative_to(driver.PAYLOAD_ROOT)
    ):
        raise ValueError("new repository recipe and assets payload directories required")
    parents = [
        ROOT / f"docs/tasks/R1-73b/R1-73b-mquake-{c}.recipe.json" for c in previous.CONDITIONS
    ]
    manifests = [json.loads(p.read_text()) for p in parents]
    if len({json.dumps(m["payload"], sort_keys=True) for m in manifests}) != 1:
        raise ValueError("shared predecessor payload required")
    original = json.loads(checked(manifests[0]["payload"]).read_text())
    source = ROOT / "manifests/dev/mquake_dev_v3b.json"
    dev = json.loads(source.read_text())
    if manifests[0]["source_bindings_sha256"].get(str(source)) != ref(source)["sha256"]:
        raise ValueError("original unrelated source binding differs")
    payload, audit = corrected_payload(original, dev["unrelated_prompts"])
    resources.mkdir(parents=True)
    binding = driver.write_json(resources / "payload.json", payload)
    output.mkdir(parents=True)
    receipts = []
    for path, m in zip(parents, manifests, strict=True):
        previous.verify(m)
        m["payload"] = binding
        m["r1_73b"]["population"] = payload["development_summary"]
        m["r1_73d"] = dict(
            task="R1-73d",
            launch_authorized=False,
            selection_audit=audit,
            historical_results="Chain M locality0/50 is invalid as locality; retain historical cost/other results with their original identities.",
            bindings=dict(
                source_recipe=ref(path),
                producer=ref(__file__),
                unrelated_source=ref(source),
                locality_guard=ref(ROOT / "scripts/r1_locality_contract.py"),
            ),
        )
        verify(m, payload)
        target = output / f"R1-73d-mquake-{m['cell']['condition']}.recipe.json"
        r = driver.write_json(target, m)
        receipts.append(inspect(target, r["sha256"]))
    metadata_json(output / "inspection-receipts.json", receipts)
    lines = [
        "# R1-73d — corrected MQuAKE development run list",
        "",
        NOTE,
        "",
        "Inspect on CPU first. Owner GPU execution adds `--execute` at the scheduled boundary, with the usual lease. These are new attempt identities; do not resume old Chain M results.",
        "",
    ]
    for receipt in receipts:
        b = receipt["recipe"]
        lines += [
            f"{receipt['cell']['condition']}:",
            "",
            "```bash",
            f"../venv/bin/python -m scripts.r1_73d_locality_recipes run --manifest {b['path']} --manifest-sha256 {b['sha256']}",
            "```",
            "",
        ]
    (output / "ordered-runlist.md").write_text("\n".join(lines))
    forbidden = {p for r in original["items"] for p in [r["prompt"], *r["paraphrases"]]}
    report = dict(
        task="R1-73d",
        payload=binding,
        source_payload=json.loads(parents[0].read_text())["payload"],
        before_overlap_count=sum(
            r["prompt"] in forbidden for r in original["endpoints"]["locality"]["rows"]
        ),
        after_overlap_count=0,
        selection=audit,
        inspections=ref(output / "inspection-receipts.json"),
        unchanged=[
            "all300 edit rows/order",
            "pool rows",
            "outside100",
            "near/revision/composition",
            "drift",
            "weights/base/calibration",
            "cadence",
            "integrity/drift dispatch",
        ],
        gpu_seconds=0,
        model_calls=0,
    )
    metadata_json(ROOT / "logs/r1_round24/r1-73d-build.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--output", type=Path, required=True)
    build.add_argument("--resources", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("--manifest", type=Path, required=True)
    run.add_argument("--manifest-sha256", required=True)
    run.add_argument("--execute", action="store_true")
    run.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.command == "build":
        print(json.dumps(build_all(args.output, args.resources), indent=2))
        return
    if args.resume and not args.execute:
        parser.error("resume requires execute")
    receipt = inspect(args.manifest, args.manifest_sha256)
    if not args.execute:
        print(json.dumps(receipt, indent=2))
        return
    m, payload = driver.load_development_cell(args.manifest, args.manifest_sha256)
    verify(m, payload)
    adapter, tok = previous.comparator.construct(m)
    print(
        json.dumps(
            driver.run_development_cell(
                args.manifest,
                args.manifest_sha256,
                adapter,
                tok,
                output_root=driver.OUTPUT_ROOT,
                resource_root=driver.RESOURCE_ROOT,
                resume=args.resume,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
