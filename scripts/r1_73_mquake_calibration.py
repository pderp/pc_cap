"""R1-73: inspectable MQuAKE v3b calibration specification; owner execution is opt-in."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scripts.r1_64b_comparator_recipes import ROOT, ref, verify

from pccap.cap.calibrate import calibrate_radii, keys_for
from pccap.revision_v1.analysis import digest

DEV = ROOT / "manifests/dev/mquake_dev_v3b.json"
TRAIN = ROOT / "manifests/revision_v1/train_pool_mquake_v3.json"
SOURCE_RECIPE = ROOT / "docs/tasks/R1-68c-zsre-v5-full.recipe.json"


def populations(dev, train):
    items = dev["items"]
    if len(items) != 100 or len(train["items"]) != 500:
        raise ValueError("v3b100 edits and v3 training500 outside prompts required")
    outside = dev["unrelated_prompts"]
    if outside != [r["prompt"] for r in train["items"]]:
        raise ValueError("outside prompts must exactly match the already-exposed v3 training pool")

    def norm(x):
        return " ".join(x.casefold().split())

    subjects = [{norm(r["subject"]) for r in rows} for rows in (items, train["items"])]
    if subjects[0] & subjects[1] or len({r["item_id"] for r in items}) != 100:
        raise ValueError("duplicate edits or edit/outside subject overlap")
    prompts = [r["prompt"] for r in items]
    if set(prompts) & set(outside):
        raise ValueError("edit/outside prompt collision")
    para, owner = [], []
    for i, row in enumerate(items):
        if not row["paraphrases"]:
            raise ValueError("paraphrases required")
        for p in row["paraphrases"]:
            para.append(p)
            owner.append(i)
    return prompts, para, np.asarray(owner, np.int64), outside


def spec():
    dev, train = json.loads(DEV.read_text()), json.loads(TRAIN.read_text())
    prompts, para, owner, outside = populations(dev, train)
    source = json.loads(SOURCE_RECIPE.read_text())
    base = source["construction"]["base"]
    for name, h in base["files"].items():
        verify({"path": str(Path(base["path"]) / name), "sha256": h})
    return {
        "schema_version": 1,
        "task": "R1-73",
        "mode": "development_calibration_spec",
        "status": "unexecuted",
        "dataset": "mquake",
        "read": "h",
        "base": base,
        "bindings": {
            "development": ref(DEV),
            "outside_source": ref(TRAIN),
            "source_recipe": ref(SOURCE_RECIPE),
            "v0_method": ref(ROOT / "src/pccap/cap/calibrate.py"),
            "feature": ref(ROOT / "src/pccap/cap/features.py"),
            "producer": ref(__file__),
            "metadata_dependency": ref(ROOT / "scripts/r1_64b_comparator_recipes.py"),
        },
        "bank_scales": source["construction"]["calibration"]["bank_scales"],
        "bank_scales_policy": "carry forward historical BP pooled b_m; no recalibration or silent pooled change",
        "population": {
            "edit_ids": [r["item_id"] for r in dev["items"]],
            "outside_ids": [r["item_id"] for r in train["items"]],
            "edit_count": len(prompts),
            "paraphrase_count": len(para),
            "outside_count": len(outside),
            "ordered_prompt_sha256": digest(
                {"edit": prompts, "paraphrase": para, "owner": owner.tolist(), "outside": outside}
            ),
            "source_order": "all100 dev items; all paraphrases per item; all500 outside prompts in v3 train order",
            "limits": "already exposed development data; disjoint normalized subjects, not certified alias equivalence or fresh evaluation",
        },
        "method": {
            "banks": [1, 2, 3],
            "site": "last prompt position at g.BANK_BLOCK; cap disabled; feature z(h)",
            "distance": "Euclidean normalized edit/paraphrase keys; outside distance to nearest of ALL100 edit keys",
            "grid_quantiles": [i / 20 for i in range(1, 21)],
            "false_fire_max": 0.01,
            "coverage": "paraphrase to its own edit key within radius",
            "selection": "largest positive grid radius with empirical outside false-fire <=1%, tie by coverage",
            "fallback": "zero radius if no positive candidate; report actual zero-radius false fire separately",
            "stream_note": "v0 static cap-disabled development-key displacement assay; no edits, optimized writes, or between-step key-motion calibration",
            "reference": "reuse pccap.cap.calibrate.calibrate_radii unchanged",
        },
        "admission_required": [
            "matching source/base/tokenizer/code/feature and array hashes before and after execution",
            "complete finite three-bank keys, all100/100/500 rows; no dropped probes or outcome-selected subset",
            "all candidate radii, coverage and false-fire denominators; explicit exact-key fallback and its measured false-fire",
            "original BP radii shared across v0 arms only after owner policy binding; continued-base transfer remains explicit",
            "versioned calibration_v3 with unchanged zsRE/CounterFact entries, historical b_m, new mquake radii and this receipt",
            "bind U08 cadence and U03/U11/U16 identities/profile; no post-draw retuning",
        ],
        "radii": None,
        "calibration_admitted": False,
        "launch_authorized": False,
        "model_calls": 0,
        "gpu_seconds": 0,
    }


def from_keys(edit, para, owner, outside):
    if set(edit) != {1, 2, 3} or set(para) != {1, 2, 3} or set(outside) != {1, 2, 3}:
        raise ValueError("all three banks required")
    owner = np.asarray(owner)
    if owner.ndim != 1 or owner.dtype.kind not in "iu" or not len(owner):
        raise ValueError("integer paraphrase ownership required")
    shapes = None
    for k in (1, 2, 3):
        arrays = [np.asarray(x[k]) for x in (edit, para, outside)]
        if any(a.ndim != 2 or not len(a) or not np.all(np.isfinite(a)) for a in arrays):
            raise ValueError("nonempty finite key matrices required")
        E, P, U = arrays
        if (
            E.shape[1] != P.shape[1]
            or E.shape[1] != U.shape[1]
            or len(P) != len(owner)
            or owner.min() < 0
            or owner.max() >= len(E)
        ):
            raise ValueError("key dimensions/ownership mismatch")
        current = (len(E), len(P), len(U))
        if shapes is not None and current != shapes:
            raise ValueError("bank population mismatch")
        shapes = current
    result = calibrate_radii(edit, para, owner, outside, false_fire_max=0.01)
    for k in (1, 2, 3):
        E, P, U = edit[k], para[k], outside[k]
        near = np.sqrt(((U[:, None, :] - E[None, :, :]) ** 2).sum(-1)).min(axis=1)
        distances = np.linalg.norm(P - E[owner], axis=1)
        r = result[str(k)]["radius"]
        count = int(np.count_nonzero(near <= r))
        result[str(k)].update(
            selected_false_fire_count=count,
            selected_false_fire_denominator=len(U),
            selected_false_fire_rate=count / len(U),
            selected_meets_empirical_bound=count / len(U) <= 0.01,
            selected_coverage_count=int(np.count_nonzero(distances <= r)),
            selected_coverage_denominator=len(P),
            exact_key_fallback=r == 0.0,
        )
    return result


def execute(document, output, resources):
    """Owner-only run, never called for specification or CPU tests."""
    from scripts.r1_61_cell_driver import _snapshot

    from pccap.bases.bp import BPBase
    from pccap.data.tokenize import GPT2Tokenizer
    from pccap.harness.lease import gpu_lease

    for binding in document["bindings"].values():
        verify(binding)
    if document["bindings"]["producer"] != ref(__file__) or document != spec():
        raise ValueError("specification/code drift")
    output, resources = output.resolve(), resources.resolve()
    if output.exists() or not output.is_relative_to(ROOT / "results/R1"):
        raise ValueError("new result directory under pc_cap/results/R1 required")
    if resources.exists() or not resources.is_relative_to(ROOT.parent / "assets/runs/pc_cap/R1"):
        raise ValueError("new calibration resource directory under assets required")
    path = _snapshot(document["base"])
    dev, train = json.loads(DEV.read_text()), json.loads(TRAIN.read_text())
    prompts, paras, owner, outside = populations(dev, train)
    with gpu_lease("R1-73", stage="R1", projected_seconds=1800) as lease:
        tok = GPT2Tokenizer(snapshot=path)
        base = BPBase(snapshot=path)
        before = base.checksum(recompute=True)
        edit = keys_for(base, tok, prompts)
        para = keys_for(base, tok, paras)
        unrel = keys_for(base, tok, outside)
        result = from_keys(edit, para, owner, unrel)
        if base.checksum(recompute=True) != before:
            raise ValueError("base changed during calibration")
        ledger = base.ledger.totals()
    for binding in document["bindings"].values():
        verify(binding)
    _snapshot(document["base"])
    resources.mkdir(parents=True, exist_ok=False)
    arrays = resources / "keys.npz"
    with arrays.open("xb") as stream:
        np.savez(
            stream,
            owner=owner,
            **{
                f"{label}_{k}": v[k]
                for label, v in (("edit", edit), ("paraphrase", para), ("outside", unrel))
                for k in (1, 2, 3)
            },
        )
    report = {
        "task": "R1-73",
        "mode": "development_calibration_result",
        "status": "measured_not_admitted",
        "specification": document,
        "base_tensor_sha256": before,
        "arrays": ref(arrays),
        "per_dataset": {"mquake": result},
        "bank_scales": document["bank_scales"],
        "radii": {"mquake": {k: r["radius"] for k, r in result.items()}},
        "empirical_all_banks_pass": all(
            r["selected_meets_empirical_bound"] for r in result.values()
        ),
        "lease": lease.report,
        "ledger": ledger,
        "calibration_admitted": False,
        "launch_authorized": False,
        "limits": [
            "1% is an in-sample selection criterion, not a population upper bound.",
            "With500 outside prompts, at most5 hits pass; exact-key fallback can itself fail.",
            "No continuation-base recalibration or final population clearance implied.",
        ],
    }
    output.mkdir(parents=True, exist_ok=False)
    with (output / "calibration_candidate.json").open("x") as f:
        json.dump(report, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-spec", type=Path)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--spec", type=Path)
    ap.add_argument("--spec-sha256")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--resources", type=Path)
    a = ap.parse_args()
    if a.execute:
        if a.write_spec or not all((a.spec, a.spec_sha256, a.output, a.resources)):
            ap.error("execution requires existing bound spec, new output and resource directories")
        document = json.loads(verify({"path": str(a.spec), "sha256": a.spec_sha256}).read_text())
        result = execute(document, a.output, a.resources)
        print(json.dumps(result["radii"]))
    else:
        document = spec()
        if a.write_spec:
            if a.write_spec.exists() or not a.write_spec.resolve().is_relative_to(
                ROOT / "docs/tasks"
            ):
                ap.error("new spec under docs/tasks required")
            with a.write_spec.open("x") as f:
                json.dump(document, f, indent=2, sort_keys=True, allow_nan=False)
                f.write("\n")
        print(json.dumps(document, indent=2))


if __name__ == "__main__":
    main()
