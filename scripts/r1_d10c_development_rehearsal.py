"""Exercise endpoint construction on already exposed development rows, CPU only.

Uses fixed small role groups in source order, never the candidate register or
confirmation RNG. No payload resources, approvals or reservations are published.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import r1_d9_receipt_core as core
from scripts.r1_d9_receipts import planned_compositions, read_resource, ref
from scripts.r1_d10a_review import ASSETS, ROOT, write_new
from scripts.r1_d10a_review_core import Entities, digest
from scripts.r1_d10c_endpoints import construct, role_plan

from pccap.data.tokenize import GPT2Tokenizer

COUNTS = {"edits": 2, "outside": 1, "near_miss_support": 1, "near_miss_neighbour": 1, "revision": 1}


def run(catalog_binding, report):
    entities, used, plans, bindings = Entities({}), set(), [], []
    base_recipe = ROOT / "docs/tasks/R1-68c-zsre-v5-full.recipe.json"
    base = json.loads(base_recipe.read_text())["construction"]["base"]
    tok = GPT2Tokenizer(snapshot=Path(base["path"]))
    cfg = json.loads((Path(base["path"]) / "config.json").read_text())
    bindings += [ref(base_recipe), ref(tok.path), ref(Path(base["path"]) / "config.json")]
    reservation = {"mode": "unsealed_fact_reservations", "allocations": [], "orders": {}}
    for ds in core.DATASETS:
        path = ROOT / f"manifests/dev/{ds}_dev{'_v3b' if ds == 'mquake' else ''}.json"
        bindings.append(ref(path))
        source = json.loads(path.read_text())["items"]
        chosen = []
        for original in source:
            entity, _ = entities.identity(original["subject"])
            if entity in used:
                continue
            row = dict(original)
            row["source_record_sha256"] = digest(original)
            row["rehearsal_provenance"] = (
                "hash of development source row; no new raw-source certification"
            )
            old = row.get("target_true", row.get("alt"))
            if isinstance(old, dict):
                old = old.get("str")
            plan = role_plan(row, old, tok, {"max_context": cfg["n_positions"]})
            if set(plan["roles"]) != set(COUNTS):
                continue
            used.add(entity)
            chosen.append((row, entity))
            plans.append(plan)
            if len(chosen) == 12:
                break
        if len(chosen) != 12:
            raise ValueError("development role rehearsal capacity shortfall: " + ds)
        offset = 0
        for real in range(2):
            for role, n in COUNTS.items():
                selected = chosen[offset : offset + n]
                offset += n
                metadata = [
                    {
                        "item_id": row["item_id"],
                        "fact_id": row["fact_id"],
                        "canonical_subject": " ".join(row["subject"].casefold().split()),
                        "entity_id": entity,
                        "payload_sha256": digest(row),
                        "source_record_sha256": row["source_record_sha256"],
                    }
                    for row, entity in selected
                ]
                reservation["allocations"].append(
                    {
                        "dataset": ds,
                        "realization": real,
                        "role": role,
                        "items": metadata,
                        "records": [r for r, _ in selected],
                    }
                )
                if role == "edits":
                    ids = [r["item_id"] for r, _ in selected]
                    for order in range(100, 105):
                        reservation["orders"][f"{ds}:{real}:{order}"] = (
                            ids if order % 2 == 0 else list(reversed(ids))
                        )
    catalog = read_resource(catalog_binding)
    reservation["planned_compositions"] = planned_compositions(reservation, catalog)
    cells = [
        {"condition": condition, "dataset": ds, "realization": real, "order": order}
        for condition in ("R1_learned_ff", "matched_update")
        for ds in core.DATASETS
        for real in range(2)
        for order in range(100, 105)
    ]
    # These same already-exposed drift tokens are read from a bound development payload.
    dev_binding = json.loads(base_recipe.read_text())["payload"]
    dev = read_resource(dev_binding)
    window = dev["endpoints"]["drift"]["windows"][0]
    drift = {"windows": [window], "expected_positions": len(window) - 1}
    payloads, population, result = construct(
        reservation,
        cells,
        catalog,
        {"rows": plans},
        drift,
        counts=COUNTS,
        realizations=2,
        locality_count=1,
        checkpoints=(1, 2),
    )
    result.update(
        task="R1-D10c",
        status="development-only CPU construction rehearsal",
        actual_draw=False,
        actual_seal=False,
        rng_calls=0,
        gpu_seconds=0,
        tested_coordinates=len(payloads),
        independent_coordinates=len(population["cells"]),
        role_counts_per_realization=COUNTS,
        source_rows=36,
        evidence_bindings=[
            *bindings,
            dev_binding,
            catalog_binding,
            ref(__file__),
            ref(ROOT / "scripts/r1_d10c_endpoints.py"),
        ],
        limitations=[
            "Small counts, two fixed edit permutations and already exposed development rows; not the production sampling protocol.",
            "Endpoint data construction and validation only; no adapter, model or behavioural results.",
        ],
    )
    write_new(report, result)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in {"identities", "evidence_bindings"}},
            indent=2,
        )
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--catalog", type=Path, required=True)
    ap.add_argument("--catalog-sha256", required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    if not args.catalog.resolve().is_relative_to(
        ASSETS
    ) or not args.report.resolve().is_relative_to(ROOT / "logs"):
        ap.error("bound assets catalog and repository report required")
    run({"path": str(args.catalog.resolve()), "sha256": args.catalog_sha256}, args.report)


if __name__ == "__main__":
    main()
