"""R1-D1f: bind the DEC-041 register and candidate inventories without a draw."""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from scripts.r1_d1e_exclusions_v3 import digest, fold

ROOT = Path(__file__).resolve().parents[1]
REGISTER_SHA = "e214de7d048c6b104fc62c75757eed01f12b47fb330eaeeb58c1a2bec8fbbd4a"
POLICY_SHA = "481e04c3eba70ea2f85aada9c0599c4f44031ea6cd7c75cf6c03cadec2c369a8"
ZSRE_SHA = "840f77494b7d747b92eadea88ecee2f6a12e59947a0ea8cc1dc0c51b92db78d7"
CF_SHA = "0d1ac13607ea5d2a3082dece3de01cc6a1943957b3ceb355382d5636cbccfe44"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def norm(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def lines(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f]


def validate_document(m, *, check_sources=True):
    if m["register"]["sha256"] != REGISTER_SHA or m["policy"]["sha256"] != POLICY_SHA:
        raise ValueError("DEC-041 register/policy identity changed; requires a new version")
    if m["acceptance"]["decision"] != "DEC-041":
        raise ValueError("register acceptance missing")
    row = m["acceptance"]["decision_row"]
    if hashlib.sha256(row.encode()).hexdigest() != m["acceptance"]["decision_row_sha256"]:
        raise ValueError("accepted decision text changed")
    if not m["register_policy_frozen"] or m["confirmation_protocol_frozen"] or m["draw_authorized"]:
        raise ValueError("register freeze is not a confirmation freeze or draw permission")
    if m["counterfact"]["selected_reading"] is not None:
        raise ValueError("CounterFact source exception needs a separate decision/version")
    if m["zsre"]["prior_clear_v3_index"]["records"] != 52498:
        raise ValueError("stale pre-reservation zsRE count")
    if m["counterfact"]["strict_v3_old_pool_count"] != 0:
        raise ValueError("strict v3 forbids old CounterFact pool")
    if m["counterfact"]["conditional_old_remainder"]["records"] != 12246:
        raise ValueError("conditional remainder count changed")
    if m["counts"]["zsre_reservation_subjects"] != 6000:
        raise ValueError("all 6000 reserved subjects must remain excluded")
    if m["draws_emitted"] != 0 or m["sealed_payloads_opened"] != 0:
        raise ValueError("metadata-only artifact required")
    if check_sources:
        for path, expected in m["bindings_sha256"].items():
            if sha(path) != expected:
                raise ValueError("bound input changed: " + path)
    return m


def verify(path, expected_sha256):
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
        raise ValueError("caller must pin the wrapper SHA-256")
    if sha(path) != expected_sha256:
        raise ValueError("wrapper identity mismatch")
    return validate_document(json.loads(Path(path).read_text()))


def build():
    bindings = {}

    def bind(path, expected=None):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT / p
        actual = sha(p)
        if expected and actual != expected:
            raise ValueError("input identity mismatch: " + str(p))
        bindings[str(p)] = actual
        return p

    def read(path, expected=None):
        return json.loads(bind(path, expected).read_text())

    def resource(ref):
        p = bind(ref["path"], ref["sha256"])
        return {**ref, "path": str(p)}

    reg_path = "manifests/revision_v1/exclusions_v3.json"
    policy_path = "manifests/revision_v1/exclusions_v2.json"
    zs_path = "manifests/revision_v1/zsre_fresh_candidates_v1.json"
    cf_path = "manifests/revision_v1/counterfact_fresh_candidates_v1.json"
    reg = read(reg_path, REGISTER_SHA)
    policy = read(policy_path, POLICY_SHA)
    zs = read(zs_path, ZSRE_SHA)
    cf = read(cf_path, CF_SHA)
    reservation = read(reg["reservation"]["manifest"], reg["reservation"]["sha256"])
    training = read("manifests/revision_v1/train_pool_zsre_v1.json")
    expected, reserved = fold(policy, reservation)
    if reg["exclusions"] != expected:
        raise ValueError("v3 is not the accepted policy plus the full training reservation")
    blocked = {r["normalized_subject"] for r in reg["exclusions"]}
    canonical = {r["canonical_subject_key"] for r in reg["exclusions"]}
    if not {norm(r["subject"]) for r in training["items"]} <= reserved:
        raise ValueError("accepted training subject is not reserved")
    raw_ref = resource(reg["candidates"])
    clear_ref = resource(reg["clear_candidate_subject_survivors"])
    raw = lines(raw_ref["path"])
    survivors = lines(clear_ref["path"])
    if len(raw) != 143753 or len({r["normalized_subject"] for r in raw}) != 81857:
        raise ValueError("raw candidate counts changed")
    if any(r["normalized_subject"] in blocked for r in raw):
        raise ValueError("excluded raw candidate")
    if len(survivors) != 52498 or any(r["review_flags"] for r in survivors):
        raise ValueError("prior-clear overlay invalid")
    zs_resources = {k: resource(v) for k, v in zs["artifacts"].items()}
    clear_payload = lines(zs_resources["clear_candidates"]["path"])
    payload_by_index = {r["source_record_index"]: r for r in clear_payload}
    original_by_index = {r["source_record_index"]: r for r in zs["records"]}
    if len(payload_by_index) != len(clear_payload) or len(clear_payload) != 58498:
        raise ValueError("prior clear payload count/uniqueness changed")
    survivor_indices = [r["source_record_index"] for r in survivors]
    if survivor_indices != sorted(set(survivor_indices)):
        raise ValueError("survivor source order changed")
    for r in survivors:
        i = r["source_record_index"]
        if r != original_by_index[i]:
            raise ValueError("survivor differs from reviewed representative")
        payload = payload_by_index[i]
        if digest(payload) != r["mapped_item_sha256"]:
            raise ValueError("mapped candidate hash mismatch")
        if (
            payload["source_record_sha256"] != r["source_record_sha256"]
            or norm(payload["subject"]) in blocked
        ):
            raise ValueError("excluded or mismatched survivor payload")
    cf_a, cf_b = cf["option_a"], cf["option_b"]
    if cf_a["register_sha256"] != REGISTER_SHA or cf["selected_option"] is not None:
        raise ValueError("CounterFact candidate policy or selection changed")
    cf_payload = resource(cf_a["payload"])
    cf_excluded = resource(cf_a["additional_exclusions"])
    records = cf_a["candidates"]
    if digest(records) != cf_a["candidates_sha256"] or len(records) != 12246:
        raise ValueError("CounterFact candidate list identity changed")
    reasons = defaultdict(set)
    for r in reg["exclusions"]:
        reasons[r["canonical_subject_key"]].update(r["reasons"])
    for r in records:
        if reasons[r["canonical_subject_key"]] != {"old_eligible:counterfact"}:
            raise ValueError("CounterFact exception would waive another exposure")
        if digest({k: v for k, v in r.items() if k != "candidate_sha256"}) != r["candidate_sha256"]:
            raise ValueError("CounterFact record hash mismatch")
    if cf_b["candidate_count"] != 0:
        raise ValueError("new CounterFact source needs a new inventory")
    decisions = (ROOT / "docs/decisions.md").read_text()
    accepted_row = next(line for line in decisions.splitlines() if line.startswith("| DEC-041 |"))
    decision_sha = hashlib.sha256(accepted_row.encode()).hexdigest()
    m = {
        "schema_version": 1,
        "name": "exclusions_frozen_v3",
        "task": "R1-D1f",
        "status": "accepted_register_binding_only_candidates_not_admitted",
        "register_policy_frozen": True,
        "confirmation_protocol_frozen": False,
        "draw_authorized": False,
        "draws_emitted": 0,
        "sealed_payloads_opened": 0,
        "gpu_seconds": 0,
        "acceptance": {
            "decision": "DEC-041",
            "decision_row": accepted_row,
            "decision_row_sha256": decision_sha,
            "decision_file_at_creation": "docs/decisions.md",
            "decision_file_sha256_at_creation": sha(ROOT / "docs/decisions.md"),
            "scope": "v2 conservative policy and current v3 register only; CounterFact exception separate",
        },
        "register": {
            "path": str(ROOT / reg_path),
            "sha256": REGISTER_SHA,
            "version": reg["version"],
        },
        "policy": {
            "path": str(ROOT / policy_path),
            "sha256": POLICY_SHA,
            "version": policy["version"],
            "normalization": reg["normalization"],
            "canonicalization": reg["canonicalization"],
            "verified_alias_pairs": reg["verified_alias_pairs"],
            "unknown_global_underexclusion_count": None,
        },
        "counts": {
            "excluded_source_subject_keys": len(blocked),
            "excluded_canonical_keys": len(canonical),
            "zsre_reservation_subjects": len(reserved),
            "accepted_zsre_training_items": len(training["items"]),
            "raw_mend_v3": len(raw),
            "unique_primary_subjects_v3": len({r["normalized_subject"] for r in raw}),
            "prior_clear_v2": len(clear_payload),
            "prior_clear_v3_direct_survivors": len(survivors),
            "source_reason_counts_nonexclusive": dict(
                sorted(
                    Counter(reason for r in reg["exclusions"] for reason in r["reasons"]).items()
                )
            ),
        },
        "zsre": {
            "historical_review_manifest": {"path": str(ROOT / zs_path), "sha256": ZSRE_SHA},
            "historical_review_resources": zs_resources,
            "v3_raw_subject_inventory": raw_ref,
            "prior_clear_v3_index": clear_ref,
            "selection_view": "join prior_clear_v3_index to historical clear_candidates on source_record_index; verify source/mapped hashes; preserve index order",
            "do_not_sample_historical_58498_directly": True,
            "reviewed_context_clear_v3": None,
            "fresh_teacher_eligible_count": None,
            "final_draw_ready": False,
        },
        "counterfact": {
            "review_manifest": {"path": str(ROOT / cf_path), "sha256": CF_SHA},
            "selected_reading": None,
            "strict_v3_old_pool_count": 0,
            "conditional_old_remainder": {
                **cf_payload,
                "candidate_list_sha256": cf_a["candidates_sha256"],
                "required_separate_decision": "reason-specific waiver of old_eligible:counterfact only",
                "nominal_before_other_v3_reasons": 13141,
                "other_v3_removed": 895,
                "additional_exclusion_decisions": cf_excluded,
                "admitted": False,
            },
            "distinct_local_source": {
                "status": cf_b["status"],
                "records": 0,
                "inventory": cf_b["local_raw_inventory"],
                "admitted": False,
            },
            "fresh_teacher_or_context_readiness": "not certified by this binding",
        },
        "bindings_sha256": bindings,
        "consumer_contract": [
            "pin this wrapper file SHA-256 externally before using any child",
            "verify every binding and the exact register/policy/count semantics",
            "use the v3 index overlay, not the historical zsRE clear list directly",
            "obtain separate CounterFact source decision; no exception is authorized here",
            "complete context/entity/alias and teacher eligibility, reserve disjoint endpoints, then separate lead draw/seal/freeze",
            "attest no later exposure since this register; later exposures require v4 and a new binding; never silently reuse v3",
            "ordinary-text training may expose new entities; assess/register it before a fresh draw",
        ],
    }
    return validate_document(m)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository manifest required")
    m = build()
    with args.output.open("x") as f:
        f.write(json.dumps(m, sort_keys=True, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "sha256": sha(args.output),
                "counts": {
                    k: v for k, v in m["counts"].items() if k != "source_reason_counts_nonexclusive"
                },
                "bindings": len(m["bindings_sha256"]),
                "draw_authorized": m["draw_authorized"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
