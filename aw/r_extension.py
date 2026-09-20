"""DEC-073 fresh-realization preparation; CPU only, no execution authority.

The allocation, family allocation, reservation audit, endpoint constructor and
seal validator below are explicit adaptations of the frozen R1 builders. Only
the dataset/realization layout seam changes: zsRE/CounterFact, realization 3.
Keeping these adaptations here leaves the running primary source tree locked.
The imported clearance, RNG quotas, pairing, locality and payload validators
remain authoritative. No treatment results guide subject or endpoint selection.
"""

from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from pathlib import Path

import pccap  # noqa: F401 -- establish project JAX settings before imports

# isort: split

import numpy as np
from scripts import r1_d9_receipt_core as core
from scripts import r1_d9f_allocation as family
from scripts.r1_58_draw_streams import quotas
from scripts.r1_63o_locality import select as select_locality
from scripts.r1_75_analysis_stage4_v1 import coordinate_id
from scripts.r1_77b_sealed_backend import planned_population
from scripts.r1_d9_receipts import (
    clearance_value,
    paired_orders,
    planned_compositions,
    read_resource,
    ref,
    sha,
    source_rows,
)
from scripts.r1_d9e_near_family import near_key, pair_reserved
from scripts.r1_d9e_near_family import validate_section as validate_near_family
from scripts.r1_d10a_review_core import digest
from scripts.r1_d10b_teacher_review import verify_bindings
from scripts.r1_locality_contract import validate_locality

from pccap.revision_v1.endpoints_composition import dependency_ids
from pccap.revision_v1.stage4_cell import content_digest, validate_payload

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
DATASETS = ("zsre", "counterfact")
CONDITIONS = ("R1_learned_ff", "R1_nonlearned", "v0_stable")
ROLES = core.ROLES
RNG_RULE = dict(
    core.RNG_RULE, traversal="dataset declared order, explicit realization 3, role declared order"
)
require, feasible = core.require, core.feasible
SUPPORT, NEIGHBOUR, CONTRACT = family.SUPPORT, family.NEIGHBOUR, family.CONTRACT
stream, ordered, units = family.stream, family.ordered, family.units


def resolve_layout(layout, *, counts=ROLES, realizations=1, checkpoints=(100, 300, 1000)):
    require(
        layout is not None and set(layout) == set(DATASETS), "explicit AW-R dataset layout required"
    )
    for entry in layout.values():
        require(entry["realizations"] == [3], "AW-R is realization 3 only")
        require(set(entry["roles_per_realization"]) == set(ROLES), "declared roles required")
        require(
            all(type(n) is int and n > 0 for n in entry["roles_per_realization"].values()),
            "positive role counts required",
        )
        require(entry["checkpoints"] == list(checkpoints), "checkpoint layout differs")
    # Restore registered traversal after reading a sorted-key JSON manifest.
    return {
        ds: {
            **layout[ds],
            "roles_per_realization": {
                role: layout[ds]["roles_per_realization"][role] for role in ROLES
            },
        }
        for ds in DATASETS
    }


def allocate(rows_by_dataset, *, seed, register_sha256, counts=ROLES, realizations=3, layout=None):
    require(type(seed) is int and seed >= 0, "explicit nonnegative integer seed required")
    require(type(realizations) is int and realizations > 0, "positive realization count required")
    require(
        set(rows_by_dataset) == set(DATASETS) and tuple(counts) == tuple(ROLES),
        "declared datasets/role order required",
    )
    require(all(type(v) is int and v > 0 for v in counts.values()), "positive role counts required")
    require(
        len(register_sha256) == 64 and all(c in "0123456789abcdef" for c in register_sha256),
        "register hash required",
    )
    all_rows = [r for ds in DATASETS for r in rows_by_dataset[ds]]
    for field in ("_entity", "item_id", "fact_id"):
        require(
            len({r[field] for r in all_rows}) == len(all_rows),
            "globally unique " + field + " required",
        )
    explicit_layout = layout is not None
    layout = resolve_layout(layout, counts=counts, realizations=realizations)
    allocations, streams = [], {}
    for ds in DATASETS:
        counts = layout[ds]["roles_per_realization"]
        realizations = len(layout[ds]["realizations"])
        remaining = list(rows_by_dataset[ds])
        demands = {role: n * realizations for role, n in counts.items()}
        feasible(remaining, demands)
        for realization in layout[ds]["realizations"]:
            for role, wanted in counts.items():
                eligible = [r for r in remaining if role in r["_roles"]]
                need = quotas(Counter(r["_stratum"] for r in eligible), wanted)
                picked = []
                for s, n in sorted(need.items()):
                    coordinates = {
                        "namespace": RNG_RULE["namespace"],
                        "seed": seed,
                        "register_sha256": register_sha256,
                        "dataset": ds,
                        "realization": realization,
                        "role": role,
                        "stratum": s,
                    }
                    derived = int(content_digest(coordinates)[:32], 16)
                    rng = np.random.Generator(np.random.PCG64(derived))
                    group = sorted(
                        (r for r in eligible if r["_stratum"] == s),
                        key=lambda r: (r["_entity"], r["item_id"]),
                    )
                    initial = copy.deepcopy(rng.bit_generator.state)
                    picked.extend(group[int(i)] for i in rng.permutation(len(group))[:n])
                    streams[f"{ds}:{realization}:{role}:{s}"] = {
                        "coordinates": coordinates,
                        "derived_seed": derived,
                        "initial_state": initial,
                        "final_state": rng.bit_generator.state,
                    }
                require(len(picked) == wanted, "role shortfall; abort entire draw")
                ids = {r["item_id"] for r in picked}
                remaining = [r for r in remaining if r["item_id"] not in ids]
                demands[role] -= wanted
                feasible(remaining, demands)
                allocations.append(
                    {
                        "dataset": ds,
                        "realization": realization,
                        "role": role,
                        "strata": dict(need),
                        "records": picked,
                    }
                )
    return {
        **(
            {"dataset_layouts": layout, "layout_sha256": content_digest(layout)}
            if explicit_layout
            else {}
        ),
        "schema_version": 2 if explicit_layout else 1,
        "register_sha256": register_sha256,
        "seed": seed,
        "rng_rule": RNG_RULE,
        "numpy_version": np.__version__,
        "rng_substreams": streams,
        "allocations": allocations,
    }


def audit_reservations(reservations, *, counts=ROLES, realizations=3, layout=None):
    layout = resolve_layout(
        layout if layout is not None else reservations.get("dataset_layouts"),
        counts=counts,
        realizations=realizations,
    )
    if "dataset_layouts" in reservations:
        require(
            reservations["dataset_layouts"] == layout
            and reservations.get("layout_sha256") == content_digest(layout),
            "reservation layout differs",
        )
    else:
        require(False, "versioned reservation layout required")
    groups = reservations["allocations"]
    expected = {
        (ds, r, role)
        for ds in DATASETS
        for r in layout[ds]["realizations"]
        for role in layout[ds]["roles_per_realization"]
    }
    require(
        len(groups) == len(expected)
        and {(g["dataset"], g["realization"], g["role"]) for g in groups} == expected,
        "complete unique allocation coordinates required",
    )
    seen = {k: set() for k in ("item_id", "fact_id", "entity_id", "canonical_subject")}
    for g in groups:
        counts = layout[g["dataset"]]["roles_per_realization"]
        require(
            len(g["items"]) == counts[g["role"]] and len(g["records"]) == counts[g["role"]],
            "wrong role count",
        )
        for meta, row in zip(g["items"], g["records"], strict=True):
            require(
                row["dataset"] == g["dataset"]
                and all(row[k] == meta[k] for k in ("item_id", "fact_id", "source_record_sha256"))
                and content_digest(row) == meta["payload_sha256"],
                "reservation content differs",
            )
            for field, values in seen.items():
                require(meta[field] not in values, "cross-role/realization duplicate " + field)
                values.add(meta[field])
    return {(g["dataset"], str(g["realization"]), g["role"]): g for g in groups}


def validate_seal(
    reservations,
    cells,
    payloads,
    independent_population,
    *,
    counts=ROLES,
    realizations=3,
    checkpoints=(100, 300, 1000),
    locality_count=50,
    layout=None,
    full_validation=None,
):
    """Validate constructed cells against the fixed draw and independent inventory."""
    if full_validation is not None:
        from scripts.r1_63l_full_validation_contract import validate

        validate(full_validation)
        require(
            independent_population.get("full_validation") == full_validation,
            "DEC-063 independent population root differs",
        )
    explicit_layout = layout
    layout = resolve_layout(
        layout, counts=counts, realizations=realizations, checkpoints=checkpoints
    )
    roles = audit_reservations(
        reservations, counts=counts, realizations=realizations, layout=explicit_layout
    )
    coords = [coordinate_id(c) for c in cells]
    require(
        len(coords) == len(set(coords))
        and set(coords) == set(payloads) == set(independent_population["cells"]),
        "exact matrix/payload/population inventory required",
    )
    require(
        {(c["dataset"], str(c["realization"])) for c in cells}
        == {(d, str(r)) for d in DATASETS for r in layout[d]["realizations"]},
        "all dataset/realization groups required",
    )
    identities, shared, endpoint_by_realization = {}, {}, {}
    for cell, cid in zip(cells, coords, strict=True):
        data = payloads[cid]
        ds, realization = cell["dataset"], str(cell["realization"])
        counts = layout[ds]["roles_per_realization"]
        checkpoints = layout[ds]["checkpoints"]
        group = {role: roles[ds, realization, role] for role in counts}
        ids = [r["item_id"] for r in data["items"]]
        expected_edits = {r["item_id"]: r for r in group["edits"]["items"]}
        require(
            len(ids) == counts["edits"] and set(ids) == set(expected_edits),
            "edit membership changed",
        )
        require(
            all(
                content_digest(r) == expected_edits[r["item_id"]]["payload_sha256"]
                and r.get("paraphrases")
                for r in data["items"]
            ),
            "edit content/paraphrases changed",
        )
        validate_payload(
            {"cell": cell, "mode": "synthetic", "checkpoints": list(checkpoints), "max_new": 32},
            data,
        )
        ep = data["endpoints"]
        validate_locality(data["items"], ep["locality"]["rows"])
        require(
            set(ep["unseen"]["expected_ids"]) == {r["item_id"] for r in group["outside"]["items"]},
            "outside reservation differs",
        )
        for kind, n in [
            ("locality", locality_count),
            ("unseen", counts["outside"]),
            ("near_miss", counts["near_miss_support"]),
            ("revision", counts["revision"]),
        ]:
            require(len(ep[kind]["expected_ids"]) == n, "planned denominator differs: " + kind)
        # Every reserved role's source content remains available even if an assay row is unavailable.
        pool = {r["item_id"]: r for r in data["pool_rows"]}
        require(
            set(pool) == {m["item_id"] for g in group.values() for m in g["items"]},
            "pool must equal the complete reserved role inventory",
        )
        for g in group.values():
            for meta in g["items"]:
                require(
                    meta["item_id"] in pool
                    and content_digest(pool[meta["item_id"]]) == meta["payload_sha256"],
                    "pool differs from reserved role content",
                )
        if explicit_layout is not None or "family_contract" in ep["near_miss"]:
            validate_near_family(
                ep["near_miss"],
                group["near_miss_support"]["records"],
                group["near_miss_neighbour"]["records"],
                [f"{ds}:{realization}:near:{i}" for i in range(counts["near_miss_support"])],
                dataset=ds,
            )
        for case in ep["near_miss"]["rows"]:
            require(case.get("dataset") == ds, "near-miss endpoint dataset differs")
            support = {r["item_id"]: r for r in group["near_miss_support"]["records"]}
            neighbours = {r["item_id"]: r for r in group["near_miss_neighbour"]["records"]}
            require(
                case.get("edit_item_id") in support and case.get("neighbour_item_id") in neighbours,
                "near-miss role binding missing",
            )
            own, other = support[case["edit_item_id"]], neighbours[case["neighbour_item_id"]]
            require(
                case["edit_prompt"] == own["prompt"]
                and case["edit_answer"] == own["answer"]
                and case["neighbour_prompt"] == other["prompt"],
                "near-miss source content changed",
            )
        require(
            len({r["edit_item_id"] for r in ep["near_miss"]["rows"]})
            == len(ep["near_miss"]["rows"])
            and len({r["neighbour_item_id"] for r in ep["near_miss"]["rows"]})
            == len(ep["near_miss"]["rows"]),
            "near-miss role reused",
        )
        require(
            len({r.get("fact_id") for r in ep["revision"]["rows"]}) == len(ep["revision"]["rows"]),
            "revision role reused",
        )
        for case in ep["revision"]["rows"]:
            require(case.get("dataset") == ds, "revision endpoint dataset differs")
            revision = {r["fact_id"]: r for r in group["revision"]["records"]}
            require(case.get("fact_id") in revision, "revision role binding missing")
            require(
                case.get("prompt") == revision[case["fact_id"]]["prompt"],
                "revision prompt differs from reserved fact",
            )
        for case in ep["composition"]["rows"]:
            require(set(dependency_ids(case)) <= set(ids), "composition outside edit realization")
        expected_population = planned_population(data)
        if full_validation is not None:
            from scripts.r1_63l_full_validation_contract import sample

            sample(full_validation, ep["drift"])
            expected_population["full_validation"] = full_validation
        require(
            expected_population == independent_population["cells"][cid],
            "independent analysis population differs",
        )
        identity = {
            "endpoint_bundle_sha256": content_digest(ep),
            "ordered_item_ids_sha256": digest(ids),
            "payload_content_sha256": content_digest(data),
        }
        shared_key = (ds, realization, str(cell["order"]))
        require(
            shared_key not in shared or shared[shared_key] == identity,
            "condition-specific payload for a shared realization/order",
        )
        endpoint_key = (ds, realization)
        require(
            endpoint_key not in endpoint_by_realization
            or endpoint_by_realization[endpoint_key] == identity["endpoint_bundle_sha256"],
            "endpoint population changed across paired orders",
        )
        endpoint_by_realization[endpoint_key] = identity["endpoint_bundle_sha256"]
        shared[shared_key] = identity
        identities[cid] = identity
    return identities


def family_allocate(rows_by_dataset, *, seed, register_sha256, mode="independent", **kwargs):
    baseline = allocate(rows_by_dataset, seed=seed, register_sha256=register_sha256, **kwargs)
    if mode == "independent":
        return baseline  # exact legacy identity, including ordering and RNG receipts
    core.require(mode == "family_coordinated", "unknown near allocation mode")
    result = copy.deepcopy(baseline)
    result.update(
        near_allocation=mode,
        near_allocation_contract=CONTRACT,
        independent_backbone_sha256=core.content_digest(baseline),
        near_pair_receipts={},
    )
    selected = {(g["dataset"], g["realization"], g["role"]): g for g in result["allocations"]}
    for dataset in DATASETS:
        groups = [g for g in baseline["allocations"] if g["dataset"] == dataset]
        taken = {
            r["item_id"]
            for g in groups
            if g["role"] not in (SUPPORT, NEIGHBOUR)
            for r in g["records"]
        }
        remaining = [r for r in rows_by_dataset[dataset] if r["item_id"] not in taken]
        demands = {
            role: sum(len(g["records"]) for g in groups if g["role"] == role)
            for role in (SUPPORT, NEIGHBOUR)
        }
        core.feasible(remaining, demands)
        for realization in sorted({g["realization"] for g in groups}):
            targets = {
                role: len(selected[dataset, realization, role]["records"]) for role in demands
            }
            core.require(
                targets[SUPPORT] == targets[NEIGHBOUR], "equal planned near roles required"
            )
            rng, receipt = stream(
                seed, register_sha256, dataset, realization, "pair_units_and_shortfall_roles"
            )
            receipt["input_pool_sha256"] = core.content_digest(ordered(remaining))
            candidates = units(remaining, rng)
            picked_units = [
                candidates[int(i)] for i in rng.permutation(len(candidates))[: targets[SUPPORT]]
            ]
            picked = {
                SUPPORT: [p[1] for p in picked_units],
                NEIGHBOUR: [p[2] for p in picked_units],
            }
            used = {r["item_id"] for group in picked.values() for r in group}
            remaining = [r for r in remaining if r["item_id"] not in used]
            for role in demands:
                demands[role] -= len(picked[role])
            core.feasible(remaining, demands)
            filler_ids = {}
            for role in demands:
                want = targets[role] - len(picked[role])
                available = ordered(r for r in remaining if role in r["_roles"])
                fillers = (
                    [available[int(i)] for i in rng.permutation(len(available))[:want]]
                    if want
                    else []
                )
                core.require(len(fillers) == want, "near role capacity shortfall; whole draw fails")
                filler_ids[role] = [r["item_id"] for r in fillers]
                used = set(filler_ids[role])
                picked[role].extend(fillers)
                remaining = [r for r in remaining if r["item_id"] not in used]
                demands[role] -= want
                core.feasible(remaining, demands)
                selected[dataset, realization, role].update(
                    records=picked[role], strata=dict(Counter(r["_stratum"] for r in picked[role]))
                )
            section = pair_reserved(
                picked[SUPPORT],
                picked[NEIGHBOUR],
                [f"{dataset}:{realization}:near:{i}" for i in range(targets[SUPPORT])],
                dataset=dataset,
            )
            receipt.update(
                final_state=copy.deepcopy(rng.bit_generator.state),
                candidate_pair_units=len(candidates),
                selected_pair_units=[
                    dict(family=k, support=a["item_id"], neighbour=b["item_id"])
                    for k, a, b in picked_units
                ],
                unmatched_role_fillers=filler_ids,
                planned=targets[SUPPORT],
                matched=len(section["rows"]),
                missing=section["missing"],
                source_family_count=len({p[0] for p in candidates}),
            )
            result["near_pair_receipts"][f"{dataset}:{realization}"] = receipt
    result["allocations"] = [
        selected[g["dataset"], g["realization"], g["role"]] for g in baseline["allocations"]
    ]
    return result


def construct(
    reservations,
    cells,
    catalog,
    plan,
    drift,
    *,
    counts=core.ROLES,
    realizations=3,
    locality_count=50,
    checkpoints=(100, 300, 1000),
    layout=None,
    full_validation=None,
    exclude_locality_overlaps=False,
):
    if reservations.get("mode") != "unsealed_fact_reservations":
        raise ValueError("unsealed reservations required")
    original_counts = counts
    explicit_layout = layout
    resolved = resolve_layout(
        layout, counts=counts, realizations=realizations, checkpoints=checkpoints
    )
    groups = audit_reservations(
        reservations, counts=counts, realizations=realizations, layout=layout
    )
    planned = planned_compositions(reservations, catalog)
    if reservations.get("planned_compositions") != planned:
        raise ValueError("composition inventory differs from draw")
    keyed = {(r["dataset"], r["item_id"]): r for r in plan["rows"]}
    if len(keyed) != len(plan["rows"]):
        raise ValueError("duplicate role plan")
    payloads, inventory, group_cache, payload_cache = {}, {"cells": {}}, {}, {}
    if full_validation is not None:
        from scripts.r1_63l_full_validation_contract import sample

        sample(full_validation, drift)
        inventory["full_validation"] = full_validation
    missing = []
    locality_selection = []
    for cell in cells:
        ds, real = cell["dataset"], str(cell["realization"])
        counts = resolved[ds]["roles_per_realization"]
        gkey = ds + ":" + real
        if gkey not in group_cache:
            roles = {role: groups[ds, real, role]["records"] for role in counts}
            for role, rows in roles.items():
                for row in rows:
                    p = keyed[ds, row["item_id"]]
                    if p["payload_sha256"] != digest(row) or role not in p["roles"]:
                        raise ValueError("drawn source is not compatible with reserved role")
            for role in ("near_miss_support", "near_miss_neighbour"):
                for row in roles[role]:
                    if keyed[ds, row["item_id"]]["near_key"] != near_key(row):
                        raise ValueError("near-family role plan differs from source")
            near_ids = [f"{gkey}:near:{i}" for i in range(counts["near_miss_support"])]
            near = pair_reserved(
                roles["near_miss_support"], roles["near_miss_neighbour"], near_ids, dataset=ds
            )
            missing.extend(dict(group=gkey, **row) for row in near["missing"])
            revisions = []
            revision_ids = [f"{gkey}:revision:{i}" for i in range(counts["revision"])]
            for i, row in enumerate(sorted(roles["revision"], key=lambda r: r["item_id"])):
                versions = keyed[ds, row["item_id"]]["revision_versions"]
                if not versions:
                    missing.append(
                        {
                            "group": gkey,
                            "item_id": revision_ids[i],
                            "reason": "no_bound_revision_versions",
                        }
                    )
                    continue
                revisions.append(
                    {
                        "item_id": revision_ids[i],
                        "dataset": ds,
                        "fact_id": row["fact_id"],
                        "subject": row["subject"],
                        "prompt": row["prompt"],
                        "paraphrases": row["paraphrases"],
                        "versions": versions,
                    }
                )
            if exclude_locality_overlaps:
                loc, locality_review = select_locality(
                    roles["edits"], roles["outside"], group=gkey, count=locality_count
                )
                locality_selection.append(locality_review)
            else:
                # Historical D.1 construction fails on a selected collision.
                loc, seen = [], set()
                for row in sorted(roles["outside"], key=lambda r: r["item_id"]):
                    for prompt in row.get("locality_prompts", []):
                        if prompt not in seen and len(loc) < locality_count:
                            seen.add(prompt)
                            loc.append(
                                dict(
                                    item_id=f"{gkey}:locality:{len(loc)}",
                                    prompt=prompt,
                                    source_outside_item_id=row["item_id"],
                                )
                            )
                validate_locality(roles["edits"], loc)
            for i in range(len(loc), locality_count):
                missing.append(
                    {
                        "group": gkey,
                        "item_id": f"{gkey}:locality:{i}",
                        "reason": "locality_source_shortfall",
                    }
                )
            ep = {
                "locality": {
                    "expected_ids": [f"{gkey}:locality:{i}" for i in range(locality_count)],
                    "rows": loc,
                },
                "unseen": {
                    "expected_ids": [r["item_id"] for r in roles["outside"]],
                    "rows": roles["outside"],
                },
                "near_miss": near,
                "revision": {"expected_ids": revision_ids, "rows": revisions},
                "composition": {
                    "expected_ids": [c["composition_id"] for c in planned[gkey]],
                    "rows": planned[gkey],
                },
                "drift": copy.deepcopy(drift),
            }
            pool = [r for role in counts for r in roles[role]]
            group_cache[gkey] = (ep, pool, {r["item_id"]: r for r in roles["edits"]})
        order_key = gkey + ":" + str(cell["order"])
        if order_key not in payload_cache:
            ep, pool, edits = group_cache[gkey]
            order = reservations["orders"][order_key]
            if len(order) != len(edits) or set(order) != set(edits):
                raise ValueError("draw order inventory differs")
            payload_cache[order_key] = {
                "items": [edits[i] for i in order],
                "pool_rows": pool,
                "endpoints": ep,
            }
        cid = core.coordinate_id(cell)
        payloads[cid] = payload_cache[order_key]
        inventory["cells"][cid] = core.planned_population(payloads[cid])
        if full_validation is not None:
            inventory["cells"][cid]["full_validation"] = full_validation
    identities = validate_seal(
        reservations,
        cells,
        payloads,
        inventory,
        counts=original_counts,
        realizations=realizations,
        checkpoints=checkpoints,
        locality_count=locality_count,
        layout=explicit_layout,
        full_validation=full_validation,
    )
    return (
        payloads,
        inventory,
        {
            "identities": identities,
            "missing": missing,
            "locality_selection": locality_selection,
            "unique_payloads": len(payload_cache),
            "draws": 0,
            "seals": 0,
            "model_calls": 0,
        },
    )


def load_bound(binding):
    path = Path(binding["path"])
    require(sha(path) == binding["sha256"], "binding changed: " + str(path))
    result = json.loads(path.read_text())
    require(sha(path) == binding["sha256"], "resource changed during read")
    return result


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    # Idempotent only for identical bytes, never replace a published population.
    if path.exists():
        require(path.read_text() == data, "refusing to replace published artifact: " + str(path))
    else:
        with path.open("x") as handle:
            handle.write(data)
    return ref(path)


def exclude_reserved(candidates, previous):
    fields = {
        "item_id": "item_id",
        "fact_id": "fact_id",
        "_entity": "entity_id",
        "_canonical_subject": "canonical_subject",
    }
    used = {
        key: {r[value] for g in previous["allocations"] for r in g["items"]}
        for key, value in fields.items()
    }
    return {
        ds: [r for r in candidates[ds] if all(r[k] not in used[k] for k in fields)]
        for ds in DATASETS
    }


def prepare():
    spec_path = ROOT / "docs/tasks/R1-D9-inputs-v11.json"
    spec = json.loads(spec_path.read_text())
    freeze_binding = ref(ROOT / "manifests/revision_v1/frozen_stage4.json")
    freeze = load_bound(freeze_binding)
    previous = read_resource(freeze["reservations"])
    register = load_bound(spec["register"])
    evidence = read_resource(spec["d9"]["clearance"]["evidence"])
    clearance = clearance_value(spec, register, evidence, source_rows(register))
    candidates = exclude_reserved(clearance["candidates"], previous)
    layout = {
        ds: dict(realizations=[3], roles_per_realization=dict(ROLES), checkpoints=[100, 300, 1000])
        for ds in DATASETS
    }
    for rows in candidates.values():
        feasible(rows, ROLES)
    allocation = family_allocate(
        candidates,
        seed=previous["seed"],
        register_sha256=spec["register"]["sha256"],
        mode="family_coordinated",
        layout=layout,
    )
    reservations = family.reservation_document(allocation, spec["register"])
    reservations.update(paired_orders(reservations))
    inputs_binding = (
        spec["d9"]["seal"]["construction_inputs"]
        if "construction_inputs" in spec["d9"].get("seal", {})
        else spec["construction_inputs"]
    )
    inputs = load_bound(inputs_binding)
    catalog, plan = read_resource(inputs["catalog"]), read_resource(inputs["role_plan"])
    verify_bindings(plan["evidence_bindings"] + [inputs["drift"]])
    reservations["planned_compositions"] = planned_compositions(reservations, catalog)
    family.audit(reservations)
    audit_reservations(reservations, layout=layout)
    # Explicit global overlap proof, in addition to the pre-allocation removal.
    selected = {
        ds: [r for g in allocation["allocations"] if g["dataset"] == ds for r in g["records"]]
        for ds in DATASETS
    }
    require(exclude_reserved(selected, previous) == selected, "prior reservation overlap")
    drift_tokens = np.load(inputs["drift"]["path"], allow_pickle=False).reshape(-1)
    drift = dict(
        windows=drift_tokens[: 128 * 128].reshape(128, 128).astype(int).tolist(),
        expected_positions=128 * 127,
    )
    cells = [
        dict(condition=c, dataset=ds, realization=3, order=o)
        for ds in DATASETS
        for o in range(100, 105)
        for c in CONDITIONS
    ]
    payloads, population, validation = construct(
        reservations,
        cells,
        catalog,
        plan,
        drift,
        layout=layout,
        full_validation=freeze["full_validation"],
        exclude_locality_overlaps=True,
    )
    require(not validation["missing"], "endpoint shortfall: draw aborted, no seed retry")
    output = ASSETS / "runs/pc_cap/R1/additional_work/R/v1"
    reservations.update(
        mode="aw_r_content_sealed_reservations",
        task="AW-R0",
        parent_reservations=freeze["reservations"],
        preparation_authority="DEC-073 allocation A; ongoing round 43",
        confirmation_launch_authorized=False,
        seal_scope="content only; separate supplemental execution admission required",
    )
    reserved_binding = write_new(output / "reservations.json", reservations)
    population_binding = write_new(output / "analysis-population.json", population)
    # Freeze a fully audited completed block, rather than changing the cost sample
    # as the live queue finishes additional cells during preparation.
    timing_binding = ref(ROOT / "logs/r1_77g/block1-evidence.json")
    timing = load_bound(timing_binding)
    times = {}
    for row in timing["rows"]:
        if row["dataset"] not in DATASETS or row["condition"] not in CONDITIONS:
            continue
        finish = load_bound(row["finish"])
        value = finish["charged_process_wall_seconds"]
        require(
            math.isfinite(value) and value > 0 and value == row["charged_process_seconds"],
            "invalid measured process cost",
        )
        times.setdefault((row["condition"], row["dataset"]), []).append(value)
    require(
        len(times) == 6 and all(len(v) == 5 for v in times.values()),
        "30 finished cost donors required",
    )
    matrix = dict(
        schema_version=1,
        mode="additional_work_R_content_sealed",
        decision="DEC-073",
        block_number=6,
        launch_authorized=False,
        primary_inference_inclusion=False,
        recipe_consumer="supplemental consumer still required; frozen primary backend rejects this mode",
        dataset_layouts=layout,
        reservations=reserved_binding,
        population=population_binding,
        parent_freeze=freeze_binding,
        producer=ref(__file__),
        receipt_root=str(ROOT / "logs/additional_work/R"),
        full_validation=freeze["full_validation"],
        cells=[],
    )
    original = json.loads((ROOT / "manifests/revision_v1/run_matrix_final.json").read_text())
    old_cells = {
        (c["condition"], c["dataset"], c["order"]): c
        for c in original["cells"]
        if c["realization"] == 0
    }
    payload_bindings = {}
    for index, cell in enumerate(cells):
        cid = coordinate_id(cell)
        payload_binding = write_new(
            output / "payloads" / f"{content_digest(payloads[cid])}.json", payloads[cid]
        )
        payload_bindings[cid] = payload_binding
        old = old_cells[cell["condition"], cell["dataset"], cell["order"]]
        parent_binding = ref(ROOT / "docs/tasks/R1-final-cell-recipes" / f"{old['cell_id']}.json")
        require(parent_binding["sha256"] == old["manifest_sha256"], "primary recipe changed")
        parent = load_bound(parent_binding)
        means = times[cell["condition"], cell["dataset"]]
        mean = math.fsum(means) / len(means)
        ceilings = dict(
            parent["ceilings"],
            wall_seconds=1.7 * mean,
            mean_process_seconds=mean,
            factor=1.7,
            donors=len(means),
            measurement=timing_binding,
            factor_application="once; no inherited concurrency multiplier",
        )
        retained = [
            "adapter_identity",
            "construction",
            "calibration",
            "checkpoints",
            "code_sha256",
            "full_validation",
            "full_validation_implementation",
            "integrity_batch_edits",
            "integrity_driver_bindings",
            "integrity_profile",
            "max_new",
            "tokenizer_sha256",
        ]
        recipe = {k: copy.deepcopy(parent[k]) for k in retained}
        recipe.update(
            schema_version=1,
            mode="additional_work_R_cell",
            cell=cell,
            block_number=6,
            parent_recipe=parent_binding,
            parent_freeze=freeze_binding,
            producer=ref(__file__),
            admission=dict(
                launch_authorized=False,
                content_sealed=True,
                decision="DEC-073",
                **validation["identities"][cid],
            ),
            payload=payload_binding,
            population=population["cells"][cid],
            reservations=reserved_binding,
            ceilings=ceilings,
            receipt_root=str(ROOT / "logs/additional_work/R" / cid),
            result_dir=str(ROOT / "results/additional_work/R" / cid),
        )
        recipe_binding = write_new(ROOT / "docs/tasks/AW-R-cell-recipes" / f"{cid}.json", recipe)
        matrix["cells"].append(
            dict(
                cell,
                cell_id=cid,
                block_number=6,
                within_block_order=index + 1,
                recipe=recipe_binding,
                payload=payload_binding,
                ceilings=ceilings,
                attempted_edits=1000,
                launch_allowed=False,
            )
        )
    matrix_binding = write_new(ROOT / "manifests/additional_work/run_matrix_R_v1.json", matrix)
    report = dict(
        task="AW-R0",
        status="content_sealed_not_launched",
        decision="DEC-073",
        matrix=matrix_binding,
        reservations=reserved_binding,
        population=population_binding,
        input_spec=ref(spec_path),
        evidence=spec["d9"]["clearance"]["evidence"],
        role_plan=inputs["role_plan"],
        original_reservations=freeze["reservations"],
        producer=ref(__file__),
        gpu_seconds=0,
        model_calls=0,
        seed_retries=0,
        validation=validation,
        cost_evidence=timing_binding,
        projected_process_hours=math.fsum(
            c["ceilings"]["mean_process_seconds"] for c in matrix["cells"]
        )
        / 3600,
        total_cell_ceiling_hours=math.fsum(c["ceilings"]["wall_seconds"] for c in matrix["cells"])
        / 3600,
        portfolio_R_budget_hours=30,
        datasets={},
    )
    for ds in DATASETS:
        pairs = allocation["near_pair_receipts"][f"{ds}:3"]
        report["datasets"][ds] = dict(
            feasible=True,
            certified=len(clearance["candidates"][ds]),
            remaining_before=len(candidates[ds]),
            allocated=sum(ROLES.values()),
            remaining_after=len(candidates[ds]) - sum(ROLES.values()),
            roles=ROLES,
            role_eligible_before={r: sum(r in x["_roles"] for x in candidates[ds]) for r in ROLES},
            pair_units_after_backbone=pairs["candidate_pair_units"],
            near_pairs=pairs["matched"],
            available_pair_families=pairs["source_family_count"],
            selected_pair_families=len({p["family"] for p in pairs["selected_pair_units"]}),
            prior_reservation_intersections=0,
        )
    report["budget_warning"] = report["projected_process_hours"] > 30
    report_binding = write_new(ROOT / "logs/additional_work/R/preparation-v1.json", report)
    print(
        json.dumps(
            dict(
                report=report_binding,
                datasets=report["datasets"],
                projected_process_hours=report["projected_process_hours"],
                total_cell_ceiling_hours=report["total_cell_ceiling_hours"],
            ),
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prepare", action="store_true", required=True)
    parser.parse_args()
    prepare()


if __name__ == "__main__":
    main()
