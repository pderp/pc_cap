"""Pure R1-D9 clearance, independent allocation and content-seal validators.

No model, filesystem access, approval creation or random draw at import time.
Production counts are fixed by the CLI; small counts are only an API test seam.
"""

from __future__ import annotations

import copy
from collections import Counter
from itertools import combinations

import numpy as np
from scripts.r1_58_draw_streams import quotas, stratum
from scripts.r1_58c_draw_seal_preflight import DATASETS, ROLES
from scripts.r1_75_analysis_stage4_v1 import coordinate_id
from scripts.r1_77b_sealed_backend import planned_population
from scripts.r1_d9_layouts import resolve as resolve_layout
from scripts.r1_d9e_near_family import validate_section as validate_near_family
from scripts.r1_locality_contract import validate_locality

from pccap.revision_v1.analysis import digest
from pccap.revision_v1.endpoints_composition import dependency_ids
from pccap.revision_v1.stage4_cell import content_digest, validate_payload

POLICY = "DEC-048-option-C;DEC-042-CounterFact;zsRE-priority"
RNG_RULE = {
    "algorithm": "numpy.PCG64",
    "namespace": "R1-D9-v1",
    "derivation": "SHA256(canonical compact JSON of namespace,seed,register_sha256,dataset,realization,role,stratum); first16 bytes big-endian",
    "source_order": "entity_id,item_id lexical within each stratum",
    "quota": "largest remainder of remaining role-eligible strata; lexical ties",
    "traversal": "dataset declared order, realization 0..2, role declared order",
    "within_role": "lexical strata then substream permutation",
    "failure": "abort whole draw on shortfall; no outcome-based replacement or seed retry",
    "representative": "first eligible row in register order per reviewed global entity",
}
REVIEW_FLAGS = (
    "alias_review_complete",
    "context_review_complete",
    "teacher_token_review_complete",
    "role_compatibility_complete",
    "cross_dataset_disjoint",
    "cumulative_exposure_current",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def feasible(rows, demands):
    """Hall's capacity condition for role eligibility; subjects are indivisible."""
    roles = tuple(k for k, n in demands.items() if n)
    for n in range(1, len(roles) + 1):
        for subset in combinations(roles, n):
            capacity = sum(bool(set(subset) & set(r["_roles"])) for r in rows)
            require(
                capacity >= sum(demands[r] for r in subset),
                "joint role capacity shortfall: " + ",".join(subset),
            )


def review_candidates(
    register, rows_by_dataset, evidence, *, counts=ROLES, realizations=3, layout=None
):
    """Validate exhaustive owner-reviewed dispositions, not infer semantic clearance."""
    require(register.get("schema_version") == 6, "register v6 required")
    require(evidence.get("policy") == POLICY, "exact exclusion policy required")
    require(all(evidence.get(k) is True for k in REVIEW_FLAGS), "incomplete joint review")
    require(
        evidence.get("tokenizer_sha256") and evidence.get("base_tensor_sha256"),
        "final tokenizer/base review identity required",
    )
    require(set(rows_by_dataset) == set(DATASETS), "all three source populations required")
    limits = evidence["model_limits"]
    require(
        type(limits.get("vocabulary")) is int
        and limits["vocabulary"] > 0
        and type(limits.get("max_context")) is int
        and limits["max_context"] >= 32,
        "bound model token/context limits required",
    )
    reviewed = evidence["dispositions"]
    expected_keys = {(ds, m["item_id"]) for ds in DATASETS for m in register["candidates"][ds]}
    keyed = {(r["dataset"], r["item_id"]): r for r in reviewed}
    require(
        len(keyed) == len(reviewed) and set(keyed) == expected_keys,
        "exact candidate disposition coverage required",
    )
    layout = resolve_layout(layout, counts=counts, realizations=realizations)
    eligible, counts_out, used_entities, used_facts = {}, {}, set(), set()
    for ds in DATASETS:
        counts = layout[ds]["roles_per_realization"]
        realizations = len(layout[ds]["realizations"])
        source = {r["item_id"]: r for r in rows_by_dataset[ds]}
        require(
            len(source) == len(rows_by_dataset[ds])
            and set(source) == {m["item_id"] for m in register["candidates"][ds]},
            "complete unique candidate source rows required",
        )
        rows, rejected, seen = [], Counter(), set()
        for meta in register["candidates"][ds]:
            row = source[meta["item_id"]]
            disp = keyed[ds, meta["item_id"]]
            require(
                row["dataset"] == ds
                and content_digest(row) == meta["payload_sha256"]
                and row["source_record_sha256"] == meta["source_record_sha256"],
                "prepared candidate content changed",
            )
            require(
                disp.get("payload_sha256") == meta["payload_sha256"]
                and disp.get("canonical_subject") == meta["canonical_subject"],
                "review/source identity differs",
            )
            require(
                isinstance(disp.get("entity_id"), str) and bool(disp["entity_id"]),
                "reviewed global entity required",
            )
            require(disp.get("decision") in ("eligible", "exclude"), "unresolved disposition")
            if disp["decision"] == "exclude":
                require(bool(disp.get("reasons")), "excluded candidate needs reasons")
                rejected["excluded"] += 1
                continue
            require(
                disp.get("reasons") == []
                and all(
                    disp.get(k) is True
                    for k in (
                        "alias_clear",
                        "context_clear",
                        "exposure_clear",
                        "teacher_pass",
                        "tokens_pass",
                    )
                ),
                "eligible row has unresolved clearance",
            )
            require(
                disp.get("base_tensor_sha256") == evidence["base_tensor_sha256"]
                and disp.get("tokenizer_sha256") == evidence["tokenizer_sha256"],
                "row teacher/token review identity differs",
            )
            require(
                isinstance(disp.get("roles"), list)
                and len(disp["roles"]) == len(set(disp["roles"]))
                and set(disp["roles"]) <= set(counts)
                and bool(disp["roles"]),
                "explicit compatible roles required",
            )
            require(
                1 <= len(row.get("answer_ids", [])) <= 32
                and row.get("prompt_ids")
                and row.get("paraphrases"),
                "tokenized answer/support/paraphrases required",
            )
            require(
                all(
                    type(t) is int and 0 <= t < limits["vocabulary"]
                    for t in row["prompt_ids"] + row["answer_ids"]
                )
                and len(row["prompt_ids"]) + max(32, len(row["answer_ids"]))
                <= limits["max_context"],
                "token/context limit violation",
            )
            require(disp["entity_id"] not in used_entities, "cross-dataset entity collision")
            if disp["entity_id"] in seen:
                rejected["later_entity_representative"] += 1
                continue
            require(row["fact_id"] not in used_facts, "duplicate fact across representatives")
            seen.add(disp["entity_id"])
            used_facts.add(row["fact_id"])
            rows.append(
                {
                    **copy.deepcopy(row),
                    "_entity": disp["entity_id"],
                    "_canonical_subject": meta["canonical_subject"],
                    "_roles": disp["roles"],
                    "_stratum": stratum(row),
                }
            )
        feasible(rows, {r: n * realizations for r, n in counts.items()})
        used_entities.update(seen)
        eligible[ds] = rows
        counts_out[ds] = {
            "reviewed_items": len(source),
            "usable_subjects": len(rows),
            "rejections": dict(rejected),
            "role_eligible": {r: sum(r in x["_roles"] for x in rows) for r in counts},
        }
    return eligible, counts_out


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
        for realization in range(realizations):
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


def reservation_document(allocation, register_binding):
    require(
        allocation["register_sha256"] == register_binding["sha256"],
        "allocation seed/register binding differs",
    )
    result = {
        "schema_version": 1,
        "mode": "unsealed_fact_reservations",
        "task": "R1-D9",
        "register": register_binding,
        "seed": allocation["seed"],
        "rng_rule": allocation["rng_rule"],
        "numpy_version": allocation["numpy_version"],
        "rng_substreams": allocation["rng_substreams"],
        "allocations": [],
        "confirmation_launch_authorized": False,
    }
    if "dataset_layouts" in allocation:
        result.update(
            schema_version=2,
            dataset_layouts=allocation["dataset_layouts"],
            layout_sha256=allocation["layout_sha256"],
        )
    for group in allocation["allocations"]:
        rows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in group["records"]]
        metadata = [
            {
                "item_id": r["item_id"],
                "fact_id": r["fact_id"],
                "canonical_subject": original["_canonical_subject"],
                "entity_id": original["_entity"],
                "payload_sha256": content_digest(r),
                "source_record_sha256": r["source_record_sha256"],
            }
            for r, original in zip(rows, group["records"], strict=True)
        ]
        result["allocations"].append(
            {k: v for k, v in group.items() if k != "records"}
            | {"items": metadata, "records": rows}
        )
    return result


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
    elif layout != resolve_layout(None, counts=counts, realizations=realizations):
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
