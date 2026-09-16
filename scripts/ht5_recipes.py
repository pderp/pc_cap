"""HT-5 hash-bound development recipe family; no model construction or selection."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path

from scripts.ht5_probe_assays import CADENCE

from pccap.revision_v1.stage4_cell import ROOT, read_binding, sha

MODE = "stage4_development_cell"
BANNER = "development, not confirmatory"
PANEL = ROOT / "manifests/revision_v1/ht_development_panel_v1.json"
SOURCES = {
    "zsre": "zsre_dev.json",
    "counterfact": "counterfact_dev.json",
    "mquake": "mquake_dev_v3b.json",
}


def binding(path):
    path = Path(path).resolve()
    return {"path": str(path), "sha256": sha(path)}


def panel_data(reference):
    if Path(reference["path"]).resolve() != PANEL:
        raise ValueError("only the reviewed HT-2 development panel is accepted")
    panel = read_binding(reference)
    if panel.get("checkpoints", CADENCE) != CADENCE:
        raise ValueError("panel cadence changed")
    if panel["seed"] != 303 or len(panel["cells"]) != 6:
        raise ValueError("reviewed six-cell panel required")
    inventories = {}
    for ds, filename in SOURCES.items():
        spec = panel["datasets"][ds]
        source = (ROOT / spec["source"]["path"]).resolve()
        if source != ROOT / "manifests/dev" / filename:
            raise PermissionError("only the permitted development manifests may be read")
        doc = read_binding({**spec["source"], "path": str(source)})
        rows = {r["item_id"]: r for r in doc["items"]}
        if len(rows) != len(doc["items"]):
            raise ValueError("duplicate source IDs")
        orders = spec["ordered_item_ids"]
        a, b = orders["shuffled"], orders["clustered"]
        if (
            len(a) != 100
            or len(set(a)) != 100
            or set(a) != set(b)
            or len(b) != 100
            or a[:20] != b[:20]
            or a[60:] != b[60:]
            or spec["fixed_old_fact_probe_ids"] != a[:20]
        ):
            raise ValueError("paired fixed population/order mismatch")
        inventories[ds] = rows
    return panel, inventories


def validate(manifest, payload):
    if manifest.get("mode") != MODE or manifest.get("schema_version") != 1:
        raise ValueError("development recipe required")
    if manifest.get("recipe_family") != "ht_stress_panel_v1":
        raise ValueError("HT-5 recipe family required")
    if "reservations" in manifest or "protocol" in manifest:
        raise PermissionError("sealed inputs forbidden")
    if any(v is not False for v in manifest.get("admission", {}).values()):
        raise PermissionError("development refuses confirmation admission flags")
    fixture = manifest.get("test_fixture", False)
    if type(fixture) is not bool:
        raise ValueError("fixture must be boolean")
    if fixture and manifest["adapter_identity"]["base_sha256"] != "tiny":
        raise ValueError("fixtures require TinyBase")
    items = payload["items"]
    if (
        len(items) != 100
        or manifest["checkpoints"] != CADENCE
        or type(manifest["max_new"]) is not int
        or not 1 <= manifest["max_new"] <= 32
    ):
        raise ValueError("100 edits and 20/60/70/80/100 cadence required")
    if not fixture and manifest["max_new"] != 32:
        raise ValueError("real development generation uses max_new=32")
    for key in ("item_id", "fact_id", "subject"):
        values = [
            " ".join(str(r[key]).casefold().split()) if key == "subject" else r[key] for r in items
        ]
        if len(set(values)) != 100 or any(not v for v in values):
            raise ValueError("unique nonempty IDs/facts/normalized subjects required")
    if any(not r.get("paraphrases") or r["dataset"] != manifest["cell"]["dataset"] for r in items):
        raise ValueError("fixed paraphrases and dataset required")
    if payload.get("mode") != MODE or payload.get("banner") != BANNER:
        raise ValueError("unsealed development stamp required")
    if payload["fixed_old_fact_probe_ids"] != [r["item_id"] for r in items[:20]]:
        raise ValueError("old facts must be the fixed first twenty")
    if manifest["cell"]["order"] not in ("shuffled", "clustered"):
        raise ValueError("unknown stress schedule")
    cell = manifest["cell"]
    if (
        set(cell) != {"condition", "dataset", "realization", "order"}
        or any(not re.fullmatch(r"[A-Za-z0-9_-]+", str(v)) for v in cell.values())
        or cell["dataset"] not in SOURCES
        or cell["condition"] not in ("R1_learned_ff", "R1_learned_ff_v2")
    ):
        raise ValueError("invalid stress cell axes")
    if not fixture:
        panel, inventories = panel_data(manifest["ht_panel"])
        ds, schedule = manifest["cell"]["dataset"], manifest["cell"]["order"]
        spec = panel["datasets"][ds]
        if items != [inventories[ds][i] for i in spec["ordered_item_ids"][schedule]]:
            raise ValueError("stress payload differs from exact bound development rows")
        if payload["fixed_old_fact_probe_ids"] != spec["fixed_old_fact_probe_ids"]:
            raise ValueError("probe inventory differs from contract")
        primary = manifest["reader_provenance"]["primary"]
        path = Path(primary["path"]).resolve()
        if not path.is_relative_to(ROOT / "manifests/revision_v1") or not path.name.startswith(
            "primary_selection_"
        ):
            raise ValueError("selected-primary manifest binding required")
        read_binding(primary)
        if manifest["construction_primary"] != primary:
            raise ValueError("construction provenance differs from selected primary")
    return payload


def build(owner_recipe, owner_sha, output_dir, payload_dir):
    """Owner supplies the selected-primary construction receipt; all writes exclusive."""
    from scripts import ht5_dev_cell as driver

    owner_path = Path(owner_recipe).resolve()
    if not owner_path.is_relative_to(ROOT) or "confirm" in owner_path.parts:
        raise PermissionError("owner recipe must be an unsealed repo document")
    owner = read_binding({"path": str(owner_path), "sha256": owner_sha})
    primary = owner["reader_provenance"]["primary"]
    if owner["construction_primary"] != primary:
        raise ValueError("owner must bind construction explicitly to selected primary")
    panel_ref = binding(PANEL)
    panel, inventories = panel_data(panel_ref)
    out, assets = Path(output_dir).resolve(), Path(payload_dir).resolve()
    if not out.is_relative_to(ROOT / "docs/tasks") or not assets.is_relative_to(
        driver.PAYLOAD_ROOT
    ):
        raise ValueError("recipes in docs/tasks; payloads in development assets")
    if out.exists() or assets.exists():
        raise FileExistsError("choose new directories; recipes never overwrite")
    plans = []
    for cell in panel["cells"]:
        ds, order = cell["dataset"], cell["schedule"]
        spec = panel["datasets"][ds]
        payload = {
            "mode": MODE,
            "banner": BANNER,
            "items": [inventories[ds][i] for i in spec["ordered_item_ids"][order]],
            "fixed_old_fact_probe_ids": spec["fixed_old_fact_probe_ids"],
        }
        manifest = {
            k: copy.deepcopy(owner[k])
            for k in (
                "construction",
                "adapter_identity",
                "tokenizer_sha256",
                "reader_provenance",
                "construction_primary",
            )
        }
        manifest.update(
            schema_version=1,
            mode=MODE,
            banner=BANNER,
            recipe_family="ht_stress_panel_v1",
            ht_panel=panel_ref,
            owner_recipe={"path": str(owner_path), "sha256": owner_sha},
            cell={
                "condition": owner["cell"]["condition"],
                "dataset": ds,
                "order": order,
                "realization": "ht-dev-s303",
            },
            checkpoints=CADENCE,
            max_new=32,
            admission={},
            integrity_profile="incremental",
            integrity_batch_edits=16,
            integrity_driver_bindings=driver.driver_bindings(),
            code_sha256=driver.code_identity(),
            execution_authorized=False,
            source_bindings_sha256={
                str(PANEL): panel_ref["sha256"],
                str((ROOT / spec["source"]["path"]).resolve()): spec["source"]["sha256"],
            },
        )
        validate(manifest, payload)
        plans.append((cell["cell_id"], manifest, payload))
    out.mkdir(parents=True)
    assets.mkdir(parents=True)
    recipes = []
    for name, manifest, payload in plans:
        manifest["payload"] = driver.write_json(assets / f"{name}.json", payload)
        ref = driver.write_json(out / f"{name}.json", manifest)
        driver.load_development_cell(ref["path"], ref["sha256"])
        recipes.append(ref)
    bundle = {
        "schema_version": 1,
        "mode": MODE,
        "banner": BANNER,
        "task": "HT-5",
        "ht_panel": panel_ref,
        "reader_provenance": {"primary": primary},
        "recipes": recipes,
        "budget_seconds": 14400,
        "experimental_completion_deadline": "2026-10-09",
        "launch_authorized": False,
        "gpu_seconds": 0,
    }
    return driver.write_json(out / "bundle.json", bundle)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--owner-recipe", type=Path)
    ap.add_argument("--owner-sha256")
    ap.add_argument("--output-dir", type=Path)
    ap.add_argument("--payload-dir", type=Path)
    args = ap.parse_args()
    if args.owner_recipe is None:
        panel, _ = panel_data(binding(PANEL))
        print(
            json.dumps(
                {
                    "cells": len(panel["cells"]),
                    "source_bindings_verified": 3,
                    "model_constructed": False,
                    "selected_primary_read": False,
                }
            )
        )
        return
    if not all((args.owner_sha256, args.output_dir, args.payload_dir)):
        ap.error("building requires owner hash and two new output directories")
    print(
        json.dumps(build(args.owner_recipe, args.owner_sha256, args.output_dir, args.payload_dir))
    )


if __name__ == "__main__":
    main()
