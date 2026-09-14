"""R1-58: count-only dry run and lead-gated fresh-reservation recipe.

Dry runs never shuffle, select, reserve, seal or emit candidate identities.
Near-miss supports and neighbours are separate fact reserves; their semantic
pairing and revision-case construction remain independent admission gates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scripts.r1_d1f_freeze_register import digest, lines, norm, sha, verify

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
WRAPPER = ROOT / "manifests/revision_v1/exclusions_frozen_v3.json"
WRAPPER_SHA = "d3549f43327ec80f497cfd71df82494c7c0bded02c8e6f5c2c333800b2489805"
ROLES = ("edits", "outside", "near_miss_support", "near_miss_neighbour", "revision")
DEFAULT_COUNTS = dict(zip(ROLES, (1000, 100, 100, 100, 50), strict=True))
STRATA = ("1-2", "3-4", "5-8", "9+")


def stratum(row):
    n = len(row["answer_ids"])
    if n < 1:
        raise ValueError("nonempty tokenized answer required")
    return "1-2" if n <= 2 else "3-4" if n <= 4 else "5-8" if n <= 8 else "9+"


def canonical(row, aliases):
    key = norm(row["subject"])
    return aliases.get(key, key)


def allowed(row, reasons, aliases, source):
    why = reasons.get(canonical(row, aliases), set())
    if row["dataset"] == "counterfact" and source == "exception":
        return not why or why == {"old_eligible:counterfact"}
    return not why


def candidates(source):
    if source not in ("strict", "exception"):
        raise ValueError("named CounterFact source required")
    wrapper = verify(WRAPPER, WRAPPER_SHA)
    reg = json.loads(Path(wrapper["register"]["path"]).read_text())
    aliases = wrapper["policy"]["verified_alias_pairs"]
    reasons = defaultdict(set)
    for r in reg["exclusions"]:
        reasons[r["canonical_subject_key"]].update(r["reasons"])
    zs = wrapper["zsre"]
    overlay = lines(zs["prior_clear_v3_index"]["path"])
    lookup = {
        r["source_record_index"]: r
        for r in lines(zs["historical_review_resources"]["clear_candidates"]["path"])
    }
    zs_rows = []
    for meta in overlay:
        row = lookup[meta["source_record_index"]]
        if (
            digest(row) != meta["mapped_item_sha256"]
            or row["source_record_sha256"] != meta["source_record_sha256"]
        ):
            raise ValueError("zsRE overlay/payload hash mismatch")
        zs_rows.append(row)
    cf_rows = []
    if source == "exception":
        cf = json.loads(Path(wrapper["counterfact"]["review_manifest"]["path"]).read_text())
        metadata = {r["item_id"]: r for r in cf["option_a"]["candidates"]}
        cf_rows = lines(wrapper["counterfact"]["conditional_old_remainder"]["path"])
        for row in cf_rows:
            meta = metadata[row["item_id"]]
            if (
                digest(row) != meta["prepared_record_sha256"]
                or row["source_record_sha256"] != meta["source_record_sha256"]
            ):
                raise ValueError("CounterFact reviewed payload mismatch")
    result, removed, globally_seen = {}, {}, set()
    for ds, rows in (("zsre", zs_rows), ("counterfact", cf_rows)):
        result[ds], removed[ds] = [], Counter()
        for row in rows:
            key = canonical(row, aliases)
            if row["dataset"] != ds:
                raise ValueError("candidate dataset mismatch")
            if not allowed(row, reasons, aliases, source):
                raise ValueError("register exclusion reached candidate inventory")
            if key in globally_seen:
                removed[ds]["canonical_duplicate"] += 1
                continue
            globally_seen.add(key)
            result[ds].append(
                {
                    **row,
                    "_canonical_subject": key,
                    "_payload_sha256": digest(row),
                    "_stratum": stratum(row),
                }
            )
    return result, {
        "wrapper_path": str(WRAPPER),
        "wrapper_sha256": WRAPPER_SHA,
        "source_reading": source,
        "removed": {k: dict(v) for k, v in removed.items()},
        "bindings_sha256": wrapper["bindings_sha256"],
        "candidate_admission": "not E2/context/fresh-exposure certified",
    }


def quotas(available, wanted):
    if not isinstance(wanted, int) or isinstance(wanted, bool) or wanted < 0:
        raise ValueError("nonnegative integer role counts required")
    total = sum(available.values())
    take = min(wanted, total)
    if not total:
        return {s: 0 for s in sorted(available)}
    q = {s: take * available[s] // total for s in sorted(available)}
    extra = take - sum(q.values())
    order = sorted(available, key=lambda s: (-(take * available[s] % total), s))
    for s in order[:extra]:
        q[s] += 1
    if any(q[s] > available[s] for s in q):
        raise ValueError("quota exceeds stratum capacity")
    return q


def capacity(rows_by_dataset, counts=None, realizations=3):
    counts = dict(DEFAULT_COUNTS if counts is None else counts)
    if (
        set(counts) != set(ROLES)
        or not isinstance(realizations, int)
        or isinstance(realizations, bool)
        or realizations < 1
    ):
        raise ValueError("fixed role set and positive realization count required")
    for n in counts.values():
        quotas({}, n)
    records, shortfalls = [], []
    for ds, rows in rows_by_dataset.items():
        remaining = Counter(r["_stratum"] for r in rows)
        available = len(rows)
        for r in range(realizations):
            for role in ROLES:
                q = quotas(remaining, counts[role])
                allocated = sum(q.values())
                records.append(
                    {
                        "dataset": ds,
                        "realization": r,
                        "role": role,
                        "requested": counts[role],
                        "capacity": allocated,
                        "shortfall": counts[role] - allocated,
                        "strata": q,
                    }
                )
                remaining.subtract(q)
        shortfalls.append(
            {
                "dataset": ds,
                "available_candidates": available,
                "requested_total": realizations * sum(counts.values()),
                "shortfall": max(0, realizations * sum(counts.values()) - available),
            }
        )
    return {
        "roles": records,
        "datasets": shortfalls,
        "complete_capacity": all(x["shortfall"] == 0 for x in shortfalls),
        "counts": counts,
        "realizations": realizations,
        "stratification": "proportional answer-token-length quotas; bins include terminal tokens; largest remainder with lexical tie-break",
        "allocation_order": list(ROLES),
        "replacement": False,
        "shortfall_rule": "report capacity only; actual draw aborts globally before any selection or write",
        "note": "capacity quotas do not select candidate IDs; neither eligibility nor near-miss/revision semantics is certified",
    }


def allocate_records(rows_by_dataset, *, seed, counts=None, realizations=3):
    """Pure allocation primitive for synthetic tests or a separately admitted lead run."""
    if not isinstance(seed, int) or isinstance(seed, bool) or seed < 0:
        raise ValueError("nonnegative integer RNG seed required")
    plan = capacity(rows_by_dataset, counts, realizations)
    if not plan["complete_capacity"]:
        raise ValueError("global shortfall: no partial draw")
    streams, rngs = {}, {}
    subjects = [r["_canonical_subject"] for rows in rows_by_dataset.values() for r in rows]
    if len(subjects) != len(set(subjects)):
        raise ValueError("canonical subjects must be unique across source populations")
    for ds, rows in rows_by_dataset.items():
        streams[ds] = {}
        for s in sorted({r["_stratum"] for r in rows}):
            derived = int.from_bytes(
                hashlib.sha256(f"R1-58:{seed}:{ds}:{s}".encode()).digest()[:16], "big"
            )
            rng = np.random.Generator(np.random.PCG64(derived))
            group = sorted(
                (r for r in rows if r["_stratum"] == s),
                key=lambda r: (r["_canonical_subject"], r["item_id"]),
            )
            streams[ds][s] = [group[i] for i in rng.permutation(len(group))]
            rngs[f"{ds}:{s}"] = {"algorithm": "PCG64", "derived_seed": derived}
    chosen, offsets = [], defaultdict(int)
    for entry in plan["roles"]:
        ds, picked = entry["dataset"], []
        for s, n in entry["strata"].items():
            start = offsets[(ds, s)]
            picked.extend(streams[ds].get(s, [])[start : start + n])
            offsets[(ds, s)] += n
        chosen.append({**entry, "records": picked})
    return {
        "plan": plan,
        "allocations": chosen,
        "seed": seed,
        "rng_substreams": rngs,
        "numpy_version": np.__version__,
        "order_within_role": "stratum lexical order then seeded source permutation",
    }


def require_lead(is_lead, admission, binding, source):
    if not is_lead:
        raise PermissionError("real draws, payload writes and seals require --i-am-the-lead")
    if admission is None or admission.get("wrapper_sha256") != binding["wrapper_sha256"]:
        raise PermissionError("hash-bound independent eligibility/lead receipt required")
    required = (
        "lead_approved",
        "source_approved",
        "context_alias_review_complete",
        "teacher_eligibility_complete",
        "post_register_exposure_review_complete",
        "sampling_recipe_approved",
    )
    if any(admission.get(k) is not True for k in required):
        raise PermissionError("unresolved draw admission gates")
    if admission.get("counterfact_source") != source:
        raise PermissionError("source receipt does not match requested reading")


def admitted_rows(rows, admission):
    approved = admission["eligible_record_sha256"]
    result = {}
    for ds, records in rows.items():
        expected = approved.get(ds, {})
        known = {r["item_id"]: r for r in records}
        if any(i not in known for i in expected):
            raise ValueError("admission references an unknown candidate")
        result[ds] = []
        for row in records:
            if row["item_id"] in expected:
                if row["_payload_sha256"] != expected[row["item_id"]]:
                    raise ValueError("eligibility receipt payload identity mismatch")
                result[ds].append(row)
    return result


def write_lead_draw(
    allocation, binding, admission, *, manifest_path, payload_dir=None, seal=False, is_lead=False
):
    require_lead(is_lead, admission, binding, binding["source_reading"])
    manifest_path = Path(manifest_path).resolve()
    if manifest_path.exists() or not manifest_path.is_relative_to(ROOT / "manifests"):
        raise ValueError("new repository manifest required")
    if payload_dir is not None:
        payload_dir = Path(payload_dir).resolve()
        if payload_dir.exists() or not payload_dir.is_relative_to(ASSETS):
            raise ValueError("new assets payload directory required")
    if seal and (payload_dir is None or admission.get("reservation_schema_verified") is not True):
        raise PermissionError(
            "seal requires payloads and an independent reservation-schema validation receipt"
        )
    # This seals fact reservations, not constructed challenge cases or the scientific protocol.
    manifest = {
        "schema_version": 1,
        "mode": "unsealed_fact_reservations",
        "task": "R1-58",
        "binding": binding,
        "admission_sha256": digest(admission),
        "recipe_sha256": sha(__file__),
        "seed": allocation["seed"],
        "rng_substreams": allocation["rng_substreams"],
        "numpy_version": allocation["numpy_version"],
        "plan": allocation["plan"],
        "challenge_cases_constructed": False,
        "confirmation_launch_authorized": False,
        "allocations": [],
    }
    if payload_dir:
        payload_dir.mkdir(parents=True, exist_ok=False)
    for group in allocation["allocations"]:
        rows = group["records"]
        record = {k: v for k, v in group.items() if k != "records"}
        record["items"] = [
            {
                "item_id": r["item_id"],
                "fact_id": r["fact_id"],
                "canonical_subject": r["_canonical_subject"],
                "payload_sha256": r["_payload_sha256"],
                "source_record_sha256": r["source_record_sha256"],
            }
            for r in rows
        ]
        if payload_dir:
            p = payload_dir / f"{group['dataset']}-r{group['realization']}-{group['role']}.jsonl"
            with p.open("x") as f:
                for row in rows:
                    f.write(
                        json.dumps(
                            {k: v for k, v in row.items() if not k.startswith("_")}, sort_keys=True
                        )
                        + "\n"
                    )
            record["payload"] = {"path": str(p), "sha256": sha(p), "records": len(rows)}
        manifest["allocations"].append(record)
    if seal:
        manifest["mode"] = "content_sealed_fact_reservations"
        manifest["seal_scope"] = (
            "hash-bound reserved facts only; final challenge construction, loader admission and lead protocol freeze remain required"
        )
    with manifest_path.open("x") as f:
        f.write(json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--counterfact-source", required=True, choices=("strict", "exception"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report", type=Path)
    ap.add_argument("--seed", type=int, default=158)
    ap.add_argument("--realizations", type=int, default=3)
    ap.add_argument("--near-miss", type=int, default=100)
    ap.add_argument("--revision", type=int, default=50)
    ap.add_argument("--i-am-the-lead", action="store_true")
    ap.add_argument("--admission", type=Path)
    ap.add_argument("--output-manifest", type=Path)
    ap.add_argument("--payload-dir", type=Path)
    ap.add_argument("--seal", action="store_true")
    args = ap.parse_args()
    if args.seed < 0:
        ap.error("seed must be nonnegative")
    if args.dry_run:
        if (
            args.i_am_the_lead
            or args.admission
            or args.output_manifest
            or args.payload_dir
            or args.seal
        ):
            ap.error("dry run cannot request lead execution, admission, manifest, payload or seal")
        if (
            args.report is None
            or args.report.exists()
            or not args.report.resolve().is_relative_to(ROOT / "logs")
        ):
            ap.error("dry run writes only a new count report under logs")
    elif not args.i_am_the_lead:
        ap.error("no actual draw/payload/seal without --i-am-the-lead")
    rows, binding = candidates(args.counterfact_source)
    counts = {
        **DEFAULT_COUNTS,
        "near_miss_support": args.near_miss,
        "near_miss_neighbour": args.near_miss,
        "revision": args.revision,
    }
    if args.dry_run:
        result = {
            "task": "R1-58",
            "mode": "count_only_dry_run",
            "binding": binding,
            "seed_proposal_not_used": args.seed,
            **capacity(rows, counts, args.realizations),
            "draws_emitted": 0,
            "candidate_ids_emitted": 0,
            "rng_used": False,
            "payloads_written": 0,
            "seals_written": 0,
            "gpu_seconds": 0,
            "final_eligible_counts": None,
        }
        with args.report.open("x") as f:
            f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
        print(
            json.dumps(
                {
                    "mode": result["mode"],
                    "source": args.counterfact_source,
                    "datasets": result["datasets"],
                    "draws_emitted": 0,
                    "rng_used": False,
                },
                indent=2,
            )
        )
        return
    admission = json.loads(args.admission.read_text()) if args.admission else None
    require_lead(args.i_am_the_lead, admission, binding, args.counterfact_source)
    if args.output_manifest is None:
        ap.error("lead execution requires a new output manifest")
    if (
        admission.get("counts") != counts
        or admission.get("realizations") != args.realizations
        or admission.get("seed") != args.seed
    ):
        ap.error("recipe parameters differ from independent approval receipt")
    eligible = admitted_rows(rows, admission)
    allocation = allocate_records(
        eligible, seed=args.seed, counts=counts, realizations=args.realizations
    )
    write_lead_draw(
        allocation,
        binding,
        admission,
        manifest_path=args.output_manifest,
        payload_dir=args.payload_dir,
        seal=args.seal,
        is_lead=args.i_am_the_lead,
    )


if __name__ == "__main__":
    main()
