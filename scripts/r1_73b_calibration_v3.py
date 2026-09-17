"""R1-73b: verify saved MQuAKE keys and build additive development calibration v3."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import numpy as np
from scripts import r1_73_mquake_calibration as original
from scripts.r1_64b_comparator_recipes import ref, verify

from pccap.revision_v1.analysis import digest

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "results/R1/calibration_mquake_v3/calibration_candidate.json"
SPEC = ROOT / "docs/tasks/R1-73-mquake-calibration.spec.json"
PARENT = (
    ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
)
EXACT_NOTE = (
    "MQuAKE v0-style conditions use the declared radius-zero exact-key (exact-prompt) fallback on all three banks; "
    "no paraphrase radius was admitted. Exact-prompt presentation is not a guarantee of acquisition or retention; RET-GS still scores every planned paraphrase."
)


def audit_arrays(arrays, counts, dimension):
    wanted = {
        "owner",
        *(f"{role}_{bank}" for role in ("edit", "paraphrase", "outside") for bank in (1, 2, 3)),
    }
    if set(arrays) != wanted:
        raise ValueError("exact key-array inventory required")
    owner = np.asarray(arrays["owner"])
    if (
        owner.dtype.kind not in "iu"
        or owner.shape != (counts["paraphrase"],)
        or np.any(owner < 0)
        or np.any(owner >= counts["edit"])
    ):
        raise ValueError("complete valid paraphrase ownership required")
    result = {}
    for bank in (1, 2, 3):
        E, P, U = (
            np.asarray(arrays[f"{role}_{bank}"]) for role in ("edit", "paraphrase", "outside")
        )
        for role, value in zip(("edit", "paraphrase", "outside"), (E, P, U)):
            if (
                value.shape != (counts[role], dimension)
                or value.dtype != np.float32
                or not np.isfinite(value).all()
            ):
                raise ValueError("complete finite float32 key matrices required")
        dp = np.linalg.norm(P - E[owner], axis=1)
        # Same float32 distance reduction, with bounded temporary host memory.
        du = np.concatenate(
            [
                np.sqrt(((chunk[:, None, :] - E[None, :, :]) ** 2).sum(-1)).min(axis=1)
                for chunk in np.array_split(U, max(1, (len(U) + 31) // 32))
            ]
        )
        grid = np.unique(np.quantile(np.concatenate([dp, du]), np.linspace(0, 1, 21)[1:]))
        candidates = [
            {
                "radius": float(r),
                "false_fire": float((du <= r).mean()),
                "coverage": float((dp <= r).mean()),
                "admissible": bool((du <= r).mean() <= 0.01),
            }
            for r in grid
        ]
        eligible = [c for c in candidates if c["radius"] > 0 and c["admissible"]]
        radius = (
            max(eligible, key=lambda c: (c["radius"], c["coverage"]))["radius"] if eligible else 0.0
        )
        result[str(bank)] = {
            "radius": radius,
            "candidates": candidates,
            "n_edits": len(E),
            "n_para": len(P),
            "n_unrel": len(U),
            "selected_coverage_count": int((dp <= radius).sum()),
            "selected_coverage_denominator": len(P),
            "selected_false_fire_count": int((du <= radius).sum()),
            "selected_false_fire_denominator": len(U),
            "selected_false_fire_rate": float((du <= radius).mean()),
            "selected_meets_empirical_bound": bool((du <= radius).mean() <= 0.01),
            "exact_key_fallback": radius == 0.0,
            "d_para_quantiles": np.quantile(dp, [0.05, 0.5, 0.95]).tolist(),
            "d_unrel_quantiles": np.quantile(du, [0.05, 0.5, 0.95]).tolist(),
        }
    return result


def validate_candidate(
    candidate, specification, arrays, *, dimension, expected_owner, expected_base_hash
):
    if (
        candidate.get("mode") != "development_calibration_result"
        or candidate.get("status") != "measured_not_admitted"
        or candidate.get("specification") != specification
        or candidate.get("launch_authorized") is not False
        or candidate.get("calibration_admitted") is not False
    ):
        raise ValueError("exact unadmitted measured source receipt required")
    if (
        candidate["base_tensor_sha256"] != expected_base_hash
        or candidate["bank_scales"] != specification["bank_scales"]
    ):
        raise ValueError("base/scales identity mismatch")
    counts = {
        k: specification["population"][k + "_count"] for k in ("edit", "paraphrase", "outside")
    }
    if counts != {"edit": 100, "paraphrase": 100, "outside": 500}:
        raise ValueError("registered 100/100/500 population required")
    if not np.array_equal(arrays["owner"], expected_owner):
        raise ValueError("paraphrase order/ownership changed")
    measured = audit_arrays(arrays, counts, dimension)
    if set(candidate["per_dataset"]) != {"mquake"} or set(candidate["per_dataset"]["mquake"]) != {
        "1",
        "2",
        "3",
    }:
        raise ValueError("complete three-bank receipt required")
    for bank, row in measured.items():
        saved = candidate["per_dataset"]["mquake"][bank]
        if any(saved.get(k) != v for k, v in row.items()):
            raise ValueError(
                "saved calibration differs from independent array reproduction: bank" + bank
            )
        if not row["exact_key_fallback"] or not row["selected_meets_empirical_bound"]:
            raise ValueError("this v3 admission is specifically the measured exact-key fallback")
    radii = {"mquake": {k: r["radius"] for k, r in measured.items()}}
    if candidate["radii"] != radii or candidate.get("empirical_all_banks_pass") is not True:
        raise ValueError("radius/all-bank admission mismatch")
    return measured


def build():
    spec = json.loads(SPEC.read_text())
    candidate = json.loads(CANDIDATE.read_text())
    parent = json.loads(PARENT.read_text())
    bindings = {}

    def bind(path, expected=None):
        b = ref(path)
        if expected is not None and b["sha256"] != expected:
            raise ValueError("binding changed: " + str(path))
        if b["path"] in bindings and bindings[b["path"]] != b["sha256"]:
            raise ValueError("input changed during audit")
        bindings[b["path"]] = b["sha256"]
        return b

    for b in spec["bindings"].values():
        bind(b["path"], b["sha256"])
    for name, h in spec["base"]["files"].items():
        bind(Path(spec["base"]["path"]) / name, h)
    bind(candidate["arrays"]["path"], candidate["arrays"]["sha256"])
    if spec != original.spec():
        raise ValueError("specification/source order differs from bound producer")
    dev = json.loads(verify(spec["bindings"]["development"]).read_text())
    train = json.loads(verify(spec["bindings"]["outside_source"]).read_text())
    _, _, owner, _ = original.populations(dev, train)
    source = json.loads(verify(spec["bindings"]["source_recipe"]).read_text())
    cfg = json.loads((Path(spec["base"]["path"]) / "config.json").read_text())
    with np.load(candidate["arrays"]["path"], allow_pickle=False) as z:
        arrays = {k: z[k] for k in z.files}
    measured = validate_candidate(
        candidate,
        spec,
        arrays,
        dimension=cfg["n_embd"],
        expected_owner=owner,
        expected_base_hash=source["adapter_identity"]["base_sha256"],
    )
    if (
        parent["b_m"] != spec["bank_scales"]
        or parent["calibration"]["BP"]["b_m"] != spec["bank_scales"]
    ):
        raise ValueError("historical scales differ")
    calibration = copy.deepcopy(parent["calibration"])
    calibration["BP"]["radii"]["mquake"] = {k: r["radius"] for k, r in measured.items()}
    report = {
        "schema_version": 3,
        "task": "R1-73b",
        "name": "calibration_v3",
        "scope": "development",
        "status": "owner_admitted_development_exact_key_fallback",
        "calibration": calibration,
        "b_m": copy.deepcopy(parent["b_m"]),
        "parent": bind(PARENT),
        "specification": bind(SPEC),
        "measured_receipt": bind(CANDIDATE),
        "arrays": candidate["arrays"],
        "producer": bind(__file__),
        "audit": measured,
        "base_tensor_sha256": candidate["base_tensor_sha256"],
        "historical_entries_unchanged": ["BP.zsre", "BP.counterfact", "EPC", "GRAM"],
        "development_admitted": True,
        "confirmation_admitted": False,
        "launch_authorized": False,
        "owner_authority": "ongoing.md round21 R1-73b; lead_queue.md entry55 (2026-09-17): orchestrator admits development calibration v3",
        "exact_key_note": EXACT_NOTE,
        "continued_base_transfer": "Use original-BP zero radii and historical b_m for S1 development profiling; no continued-base calibration measurement is asserted. Final U03 admission remains required.",
        "limits": [
            "An empirical 0/500 outside rate is not a population guarantee.",
            "Calibration data are already exposed development/training data.",
            "This is original-BP cap-disabled static key separation, not learned-reader gate calibration.",
            "No new clearance, final protocol, cost or launch admission is implied.",
        ],
        "bindings_sha256": bindings,
        "model_calls": 0,
        "gpu_seconds": 0,
    }
    report["content_sha256"] = digest({k: v for k, v in report.items() if k != "content_sha256"})
    for name, h in bindings.items():
        bind(name, h)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    output = args.output.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "manifests/revision_v1"):
        raise FileExistsError("new calibration manifest required")
    value = build()
    with output.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "radii": value["calibration"]["BP"]["radii"]["mquake"],
                "model_calls": 0,
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
