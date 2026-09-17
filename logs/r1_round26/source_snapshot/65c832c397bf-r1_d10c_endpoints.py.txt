"""CPU-only role plans, composition catalog and unsealed endpoint construction.

No RNG, models, draw, seal or approval creation. The constructor defaults to a
dry run; the owner can publish new unsealed resources after the actual draw.
Missing compatible endpoint rows keep their planned denominators.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from scripts import r1_d9_receipt_core as core
from scripts.r1_d9_receipts import planned_compositions, read_resource, ref, sha, source_rows
from scripts.r1_d10a_review import ASSETS, ROOT, write_new
from scripts.r1_d10a_review_core import digest
from scripts.r1_d10b_teacher_review import verify_bindings
from scripts.r1_locality_contract import validate_locality

from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.metrics.editing import normalize_answer
from pccap.revision_v1.endpoints_composition import dependency_ids, structural_reason


def near_key(row):
    if row["dataset"] in ("counterfact", "mquake"):
        return "relation:" + row["relation_id"] if row.get("relation_id") else None
    subject, prompt = normalize_answer(row["subject"]), normalize_answer(row["prompt"])
    if not subject:
        return None
    pattern = re.compile(r"(?<!\w)" + re.escape(subject) + r"(?!\w)")
    if len(pattern.findall(prompt)) != 1:
        return None
    return "question_template:" + pattern.sub("{subject}", prompt)


def role_plan(row, old_answer, tokenizer, limits):
    roles = ["edits", "outside"]
    key = near_key(row)
    if key:
        roles += ["near_miss_support", "near_miss_neighbour"]
    versions, reason = None, "no_bound_distinct_prior_answer"
    new_aliases = sorted({normalize_answer(a) for a in [row["answer"], *row.get("aliases", [])]})
    if (
        isinstance(old_answer, str)
        and normalize_answer(old_answer)
        and normalize_answer(old_answer) not in new_aliases
    ):
        pair = tokenize_pair(tokenizer, row["prompt"], old_answer)
        if not pair.excluded and len(pair.prompt_ids) + 32 <= limits["max_context"]:
            versions = [
                {"version": 1, "answer": old_answer, "aliases": [normalize_answer(old_answer)]},
                {"version": 2, "answer": row["answer"], "aliases": new_aliases},
            ]
            roles.append("revision")
            reason = None
    return {
        "dataset": row["dataset"],
        "item_id": row["item_id"],
        "payload_sha256": digest(row),
        "roles": roles,
        "near_key": key,
        "revision_versions": versions,
        "revision_unavailable_reason": reason,
    }


def catalog_from_rows(rows):
    if len({r["composition_id"] for r in rows}) != len(rows):
        raise ValueError("duplicate composition source IDs")
    for row in rows:
        dependency_ids(row)
        if row.get("verified_source") != "MQuAKE" or not row.get("source_case_sha256"):
            raise ValueError("direct source provenance required")
    # Keep unavailable/conflicting cases in the predetermined inventory. Membership
    # does not imply semantic availability; the installed assay records that status.
    return {"zsre": [], "counterfact": [], "mquake": copy.deepcopy(rows)}


def build_roles(evidence, sources, raw_zsre, tokenizer):
    selected = {
        (d["dataset"], d["item_id"]): d
        for d in evidence["dispositions"]
        if d["preteacher_eligible"]
    }
    plans = []
    for ds in core.DATASETS:
        for row in sources[ds]:
            disp = selected.get((ds, row["item_id"]))
            if disp is None:
                continue
            if digest(row) != disp["payload_sha256"]:
                raise ValueError("role/source identity differs")
            if ds == "zsre":
                raw = raw_zsre[row["source_record_index"]]
                if digest(raw) != row["source_record_sha256"]:
                    raise ValueError("zsRE source-record identity differs")
                old = raw.get("alt")
            else:
                old = row.get("target_true")
                if isinstance(old, dict):
                    old = old.get("str")
            plan = role_plan(row, old, tokenizer, evidence["model_limits"])
            plan["prior_answer_source"] = (
                "zsRE raw alt (staged prior version)" if ds == "zsre" else "source target_true"
            )
            plans.append(plan)
    return {
        "schema_version": 1,
        "mode": "unsealed_endpoint_role_plan",
        "rows": plans,
        "policy": {
            "near": "same relation for CF/MQ; exactly matching subject-masked question template for zsRE, different globally reserved subjects",
            "pairing": "lexical support item order; first unused neighbour with equal near_key; no substitutions across roles",
            "revision": "two bound source versions, v2 equals reserved answer; no fabricated alternative",
            "missing": "preserve full planned denominator and record unavailable reason",
            "zsre_caveat": "same-template/different-subject family; differs from historical same-subject/other-relation development challenges and requires explicit endpoint admission",
            "role_capacity": "individual roles only; joint allocation and postdraw pair availability checked separately",
        },
    }


def merge_roles(teacher, plan, plan_binding):
    result = copy.deepcopy(teacher)
    if teacher.get("teacher_token_review_complete") is not True:
        raise ValueError("complete final teacher review required")
    keyed = {(r["dataset"], r["item_id"]): r for r in plan["rows"]}
    expected = {
        (d["dataset"], d["item_id"]) for d in teacher["dispositions"] if d["preteacher_eligible"]
    }
    if len(keyed) != len(plan["rows"]) or set(keyed) != expected:
        raise ValueError("exact preteacher role-plan coverage required")
    for disp in result["dispositions"]:
        if not disp["preteacher_eligible"]:
            continue
        r = keyed[disp["dataset"], disp["item_id"]]
        if r["payload_sha256"] != disp["payload_sha256"] or not r["roles"]:
            raise ValueError("role/source identity or compatibility missing")
        disp["roles"] = r["roles"]
        if disp.get("teacher_token_eligible"):
            disp.update(decision="eligible", reasons=[])
    result.update(role_compatibility_complete=True, mode="unsealed_joint_review_evidence")
    result["evidence_bindings"] += [plan_binding, *plan.get("evidence_bindings", [])]
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
):
    if reservations.get("mode") != "unsealed_fact_reservations":
        raise ValueError("unsealed reservations required")
    original_counts = counts
    explicit_layout = layout
    resolved = core.resolve_layout(
        layout, counts=counts, realizations=realizations, checkpoints=checkpoints
    )
    groups = core.audit_reservations(
        reservations, counts=counts, realizations=realizations, layout=layout
    )
    planned = planned_compositions(reservations, catalog)
    if reservations.get("planned_compositions") != planned:
        raise ValueError("composition inventory differs from draw")
    keyed = {(r["dataset"], r["item_id"]): r for r in plan["rows"]}
    if len(keyed) != len(plan["rows"]):
        raise ValueError("duplicate role plan")
    payloads, inventory, group_cache, payload_cache = {}, {"cells": {}}, {}, {}
    missing = []
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
            near, used = [], set()
            supports = sorted(roles["near_miss_support"], key=lambda r: r["item_id"])
            neighbours = sorted(roles["near_miss_neighbour"], key=lambda r: r["item_id"])
            near_ids = [f"{gkey}:near:{i}" for i in range(counts["near_miss_support"])]
            for i, row in enumerate(supports):
                k = keyed[ds, row["item_id"]]["near_key"]
                neighbour = next(
                    (
                        n
                        for n in neighbours
                        if n["item_id"] not in used
                        and k is not None
                        and keyed[ds, n["item_id"]]["near_key"] == k
                    ),
                    None,
                )
                if neighbour is None:
                    missing.append(
                        {
                            "group": gkey,
                            "item_id": near_ids[i],
                            "reason": "no_compatible_reserved_neighbour",
                        }
                    )
                    continue
                used.add(neighbour["item_id"])
                near.append(
                    {
                        "item_id": near_ids[i],
                        "dataset": ds,
                        "edit_item_id": row["item_id"],
                        "neighbour_item_id": neighbour["item_id"],
                        "edit_prompt": row["prompt"],
                        "edit_answer": row["answer"],
                        "neighbour_prompt": neighbour["prompt"],
                        "neighbour_answer": neighbour["answer"],
                        "type": k.split(":", 1)[0] + "_other_subject",
                    }
                )
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
            loc, seen = [], set()
            for row in sorted(roles["outside"], key=lambda r: r["item_id"]):
                for prompt in row.get("locality_prompts", []):
                    if prompt not in seen and len(loc) < locality_count:
                        seen.add(prompt)
                        loc.append(
                            {
                                "item_id": f"{gkey}:locality:{len(loc)}",
                                "prompt": prompt,
                                "source_outside_item_id": row["item_id"],
                            }
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
                "near_miss": {"expected_ids": near_ids, "rows": near},
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
    identities = core.validate_seal(
        reservations,
        cells,
        payloads,
        inventory,
        counts=original_counts,
        realizations=realizations,
        checkpoints=checkpoints,
        locality_count=locality_count,
        layout=explicit_layout,
    )
    return (
        payloads,
        inventory,
        {
            "identities": identities,
            "missing": missing,
            "unique_payloads": len(payload_cache),
            "draws": 0,
            "seals": 0,
            "model_calls": 0,
        },
    )


def prepare(evidence_binding, output, report):
    evidence = read_resource(evidence_binding)
    verify_bindings([evidence["register"], *evidence["evidence_bindings"]])
    register = json.loads(Path(evidence["register"]["path"]).read_text())
    source = source_rows(register)
    raw_path = ASSETS / "data/raw/zsre/zsre_mend_train.json"
    ancestor_path = ROOT / "manifests/revision_v1/exclusions_v2.json"
    if sha(ancestor_path) != register["bindings_sha256"][str(ancestor_path)]:
        raise ValueError("raw-source ancestor binding changed")
    ancestor = json.loads(ancestor_path.read_text())
    if sha(raw_path) != ancestor["sources_sha256"][str(raw_path)]:
        raise ValueError("bound zsRE raw source changed")
    raw = json.loads(raw_path.read_text())
    tok = GPT2Tokenizer(snapshot=Path(evidence["base"]["path"]))
    plan = build_roles(evidence, source, raw, tok)
    manifest_path = ROOT / "manifests/revision_v1/mquake_items_v1.json"
    if sha(manifest_path) != register["bindings_sha256"][str(manifest_path)]:
        raise ValueError("composition inventory manifest differs from register")
    manifest = json.loads(manifest_path.read_text())
    binding = manifest["artifacts"]["composition"]
    verify_bindings([binding])
    cases = [json.loads(line) for line in Path(binding["path"]).read_text().splitlines()]
    catalog = catalog_from_rows(cases)
    plan["evidence_bindings"] = [
        ref(ancestor_path),
        evidence_binding,
        ref(raw_path),
        ref(__file__),
        ref(manifest_path),
        binding,
    ]
    plan_ref = write_new(output / "role_plan.json", plan)
    catalog_ref = write_new(output / "composition_catalog.json", catalog)
    summary = {
        "task": "R1-D10c",
        "role_plan": plan_ref,
        "composition_catalog": catalog_ref,
        "composition_cases": len(cases),
        "composition_structural_status": dict(
            Counter(structural_reason(c) or "structurally_available" for c in cases)
        ),
        "roles": {
            ds: dict(
                Counter(role for p in plan["rows"] if p["dataset"] == ds for role in p["roles"])
            )
            for ds in core.DATASETS
        },
        "policy": plan["policy"],
        "status": "prepared unsealed inputs; actual draw/teacher results and endpoint admission pending",
        "gpu_seconds": 0,
        "draws": 0,
        "seals": 0,
    }
    write_new(report, summary)
    print(json.dumps(summary, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--evidence", type=Path, required=True)
    prep.add_argument("--evidence-sha256", required=True)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--report", type=Path, required=True)
    con = sub.add_parser("construct")
    con.add_argument(
        "--spec",
        type=Path,
        required=True,
        help="bound draw_receipt, matrix, catalog, role_plan, drift, output and report paths",
    )
    con.add_argument(
        "--dry-run", action="store_true", help="default; construct/validate in memory only"
    )
    con.add_argument(
        "--write", action="store_true", help="owner publishes new unsealed resources, never a seal"
    )
    merger = sub.add_parser("merge-review")
    merger.add_argument("--teacher", type=Path, required=True)
    merger.add_argument("--teacher-sha256", required=True)
    merger.add_argument("--role-plan", type=Path, required=True)
    merger.add_argument("--role-plan-sha256", required=True)
    merger.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.command == "merge-review":
        if not args.output.resolve().is_relative_to(ASSETS):
            ap.error("new unsealed assets resource required")
        teacher_ref = {"path": str(args.teacher.resolve()), "sha256": args.teacher_sha256}
        role_ref = {"path": str(args.role_plan.resolve()), "sha256": args.role_plan_sha256}
        teacher, plan = read_resource(teacher_ref), read_resource(role_ref)
        verify_bindings(teacher["evidence_bindings"] + plan["evidence_bindings"])
        merged = merge_roles(teacher, plan, role_ref)
        merged["evidence_bindings"] += [teacher_ref, ref(__file__)]
        print(json.dumps(write_new(args.output, merged)))
        return
    if args.command == "prepare":
        if not args.output.resolve().is_relative_to(
            ASSETS
        ) or not args.report.resolve().is_relative_to(ROOT / "logs"):
            ap.error("resources under assets and report under repository logs required")
        prepare(
            {"path": str(args.evidence.resolve()), "sha256": args.evidence_sha256},
            args.output,
            args.report,
        )
        return
    if args.write and args.dry_run:
        ap.error("choose dry-run or write")
    spec = json.loads(args.spec.read_text())
    verify_bindings([spec["draw_receipt"], spec["matrix"]])
    draw = json.loads(Path(spec["draw_receipt"]["path"]).read_text())
    reservations = read_resource(draw["reservations"])
    matrix = json.loads(Path(spec["matrix"]["path"]).read_text())
    cells = [
        {k: c[k] for k in ("condition", "dataset", "realization", "order")} for c in matrix["cells"]
    ]
    if spec.get("extension_admitted") is True:
        cells += [
            {k: c[k] for k in ("condition", "dataset", "realization", "order")}
            for c in matrix["extension"]["cells"]
        ]
    elif spec.get("extension_admitted") is not False:
        raise ValueError("explicit extension_admitted true/false required")
    catalog, plan = read_resource(spec["catalog"]), read_resource(spec["role_plan"])
    verify_bindings(plan["evidence_bindings"] + [spec["drift"]])
    drift_tokens = np.load(spec["drift"]["path"], allow_pickle=False).reshape(-1)
    if len(drift_tokens) < 128 * 128:
        raise ValueError("128 drift windows required")
    drift = {
        "windows": drift_tokens[: 128 * 128].reshape(128, 128).astype(int).tolist(),
        "expected_positions": 128 * 127,
    }
    from scripts.r1_d9_layouts import from_matrix

    layout = from_matrix(matrix)
    payloads, population, report = construct(
        reservations,
        cells,
        catalog,
        plan,
        drift,
        layout=layout if "dataset_layouts" in matrix else None,
    )
    report.update(
        draw_receipt=spec["draw_receipt"],
        reservations=draw["reservations"],
        status="dry construction verified; no seal or approval",
    )
    if args.write:
        output, report_path = Path(spec["output"]), Path(spec["report"])
        if not output.resolve().is_relative_to(ASSETS) or not report_path.resolve().is_relative_to(
            ROOT / "logs"
        ):
            raise ValueError("new assets resources and repository report required")
        bindings, by_hash = {}, {}
        for cid, payload in payloads.items():
            h = digest(payload)
            if h not in by_hash:
                by_hash[h] = write_new(output / "payloads" / (h + ".json"), payload)
            bindings[cid] = by_hash[h]
        report["bundle"] = write_new(output / "bundle.json", {"payloads": bindings})
        report["independent_population"] = write_new(
            output / "independent_population.json", population
        )
        write_new(report_path, report)
    print(json.dumps({k: v for k, v in report.items() if k != "identities"}, indent=2))


if __name__ == "__main__":
    main()
