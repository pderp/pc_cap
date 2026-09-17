"""Outcome-free Q16 allocation proposal; independent remains the live default.

Family mode keeps the exact independent edit/outside/revision backbone, releases
its provisional near roles, and samples disjoint same-family pair units. It may
use several pairs from a family; 100 is a case count, not a distinct-family quota.
"""

from __future__ import annotations

import copy
from collections import Counter, defaultdict

import numpy as np
from scripts import r1_d9_receipt_core as core
from scripts.r1_d9e_near_family import near_key, pair_reserved

from pccap.metrics.editing import normalize_answer

SUPPORT, NEIGHBOUR = "near_miss_support", "near_miss_neighbour"
CONTRACT = {
    "version": 1,
    "decision_required": "DEC-062",
    "family": "DEC-061_NM-template-v1",
    "namespace": "R1-D9-family-pairs-v1",
    "backbone": "exact_independent_edit_outside_revision_allocations_all_realizations",
    "pool": "cleared_representatives_after_removing_all_backbone_subjects",
    "pair_units": "within_family_role_exclusive_first_then_dual_role_pairs; source_permuted; distinct_subjects; no_reuse",
    "selection": "uniform_permutation_of_disjoint_pair_units; multiple_pairs_per_family_allowed",
    "shortfall": "reserve_remaining_role_eligible_subjects_without_replacement; missing_pair_slots_keep_planned_denominator",
    "endpoint_pairing": "DEC061_lexical_repairing_within_reserved_roles; pair_units_select_membership_not_endpoint_slot_order",
    "constraints": "original_Hall_capacity_and_global_subject_fact_item_disjointness; no_outcomes_no_seed_retry",
}


def admitted_mode(rng, cfg, decision=None):
    mode = rng.get("near_allocation", "independent")
    core.require(mode in ("independent", "family_coordinated"), "unknown near allocation mode")
    core.require(
        cfg.get("near_allocation", "independent") == mode, "RNG/config near allocation differs"
    )
    if mode == "family_coordinated":
        core.require(
            rng.get("near_allocation_contract") == CONTRACT, "family allocation contract not bound"
        )
        core.require(
            isinstance(decision, dict)
            and decision.get("decision") == "DEC-062"
            and decision.get("near_allocation") == mode
            and decision.get("lead_approved") is True
            and decision.get("status") == "closed"
            and decision.get("allocation_contract") == CONTRACT,
            "family allocation requires explicit DEC-062 lead admission",
        )
    return mode


def stream(seed, register_sha256, dataset, realization, phase):
    coordinates = dict(
        namespace=CONTRACT["namespace"],
        seed=seed,
        register_sha256=register_sha256,
        dataset=dataset,
        realization=realization,
        phase=phase,
    )
    derived = int(core.content_digest(coordinates)[:32], 16)
    rng = np.random.Generator(np.random.PCG64(derived))
    return rng, dict(
        coordinates=coordinates,
        derived_seed=derived,
        initial_state=copy.deepcopy(rng.bit_generator.state),
    )


def ordered(rows):
    return sorted(rows, key=lambda r: (r["_entity"], r["item_id"]))


def units(rows, rng):
    """Disjoint units; exclusive-role rows first avoid consuming their only partner."""
    families = defaultdict(list)
    for row in ordered(rows):
        key = near_key(row)
        if key:
            families[key].append(row)
    result = []
    for family, members in sorted(families.items()):
        shuffled = [members[int(i)] for i in rng.permutation(len(members))]
        support_only = [
            r for r in shuffled if SUPPORT in r["_roles"] and NEIGHBOUR not in r["_roles"]
        ]
        neighbour_only = [
            r for r in shuffled if NEIGHBOUR in r["_roles"] and SUPPORT not in r["_roles"]
        ]
        both = [r for r in shuffled if SUPPORT in r["_roles"] and NEIGHBOUR in r["_roles"]]
        # Exclusive-exclusive, then exclusive-dual, then dual-dual. No outcome fields inspected.
        used = set()
        for supports, neighbours in (
            (support_only, neighbour_only),
            (support_only, both),
            (both, neighbour_only),
            (both, both),
        ):
            for own in supports:
                if own["item_id"] in used:
                    continue
                subject = normalize_answer(own["subject"])
                other = next(
                    (
                        r
                        for r in neighbours
                        if r["item_id"] not in used
                        and r["item_id"] != own["item_id"]
                        and subject
                        and normalize_answer(r["subject"]) not in ("", subject)
                    ),
                    None,
                )
                if other is not None:
                    used.update((own["item_id"], other["item_id"]))
                    result.append((family, own, other))
    return result


def allocate(rows_by_dataset, *, seed, register_sha256, mode="independent", **kwargs):
    baseline = core.allocate(rows_by_dataset, seed=seed, register_sha256=register_sha256, **kwargs)
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
    for dataset in core.DATASETS:
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


def reservation_document(allocation, register):
    result = core.reservation_document(allocation, register)
    for key in (
        "near_allocation",
        "near_allocation_contract",
        "independent_backbone_sha256",
        "near_pair_receipts",
    ):
        if key in allocation:
            result[key] = allocation[key]
    return result


def audit(reservation):
    if reservation.get("near_allocation", "independent") == "independent":
        return
    core.require(
        reservation.get("near_allocation") == "family_coordinated"
        and reservation.get("near_allocation_contract") == CONTRACT,
        "unknown family reservation contract",
    )
    groups = {(g["dataset"], g["realization"], g["role"]): g for g in reservation["allocations"]}
    expected = {f"{ds}:{real}" for ds, real, role in groups if role == SUPPORT}
    core.require(
        set(reservation.get("near_pair_receipts", {})) == expected,
        "complete near pair RNG receipt inventory required",
    )
    for key, receipt in reservation["near_pair_receipts"].items():
        ds, realization = key.split(":")
        roles = {
            role: groups[ds, int(realization), role]["records"] for role in (SUPPORT, NEIGHBOUR)
        }
        indexed = {role: {r["item_id"]: r for r in rows} for role, rows in roles.items()}
        taken = {SUPPORT: [], NEIGHBOUR: []}
        for pair in receipt["selected_pair_units"]:
            a, b = indexed[SUPPORT][pair["support"]], indexed[NEIGHBOUR][pair["neighbour"]]
            core.require(
                near_key(a) == near_key(b) == pair["family"]
                and pair["family"]
                and normalize_answer(a["subject"]) != normalize_answer(b["subject"]),
                "pair unit family/source differs",
            )
            taken[SUPPORT].append(a["item_id"])
            taken[NEIGHBOUR].append(b["item_id"])
        for role in roles:
            ids = taken[role] + receipt["unmatched_role_fillers"][role]
            core.require(
                len(ids) == len(set(ids)) and set(ids) == set(indexed[role]),
                "pair/filler role inventory differs",
            )
        section = pair_reserved(
            roles[SUPPORT],
            roles[NEIGHBOUR],
            [f"{key}:near:{i}" for i in range(receipt["planned"])],
            dataset=ds,
        )
        core.require(
            receipt["matched"] == len(section["rows"]) and receipt["missing"] == section["missing"],
            "near shortfall receipt differs",
        )
        _, expected_stream = stream(
            reservation["seed"],
            reservation["register"]["sha256"],
            ds,
            int(realization),
            "pair_units_and_shortfall_roles",
        )
        core.require(
            all(receipt.get(k) == v for k, v in expected_stream.items()),
            "near RNG stream identity differs",
        )
