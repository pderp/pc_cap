"""R1-D2: ordered CounterFact remainder candidates and local fresh-source inventory.

Reads public metadata sidecars only, never historical realization payloads.
Reconstructs old reservation identities from the recorded sampling recipe and
verifies all 15 public order digests; performs no new confirmation draw or seal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    ).hexdigest()


def norm(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def old_reservations(ids, metadata, per=1000):
    if len(set(ids)) != len(ids) or len(ids) < 3 * per or len(metadata) != 3:
        raise ValueError("invalid historical source identity inventory")
    seed = int(hashlib.sha256(b"counterfact-partition").hexdigest()[:8], 16)
    partition = np.random.default_rng(seed).permutation(len(ids))
    reserved, checks = set(), []
    for r in range(3):
        sidecar = metadata[r]
        if sidecar["n_items"] != per or sidecar["subjects"] != per:
            raise ValueError("historical reservation size mismatch")
        chosen = [
            ids[int(i)]
            for i in np.random.default_rng(r).permutation(partition[r * per : (r + 1) * per])
        ]
        if reserved.intersection(chosen):
            raise ValueError("historical reservation overlap")
        reserved.update(chosen)
        for order_seed in range(100, 105):
            order = [chosen[int(i)] for i in np.random.default_rng(order_seed).permutation(per)]
            value = hashlib.sha256(json.dumps(order).encode()).hexdigest()[:16]
            if value != sidecar["orders"][str(order_seed)]:
                raise ValueError("historical order metadata mismatch")
            checks.append(
                {
                    "realization": r,
                    "order_seed": order_seed,
                    "order_digest": value,
                    "verified": True,
                }
            )
    return reserved, checks


def filter_remainder(rows, reserved, prior, current, training):
    by_subject = {r["normalized_subject"]: r for r in current["exclusions"]}
    if len(by_subject) != len(current["exclusions"]):
        raise ValueError("duplicate v3 subject identity")
    old_exposed = {
        r["normalized_subject"]
        for r in prior["exclusions"]
        if any(not reason.startswith("old_eligible:") for reason in r["reasons"])
    }
    all_reasons = defaultdict(set)
    for row in current["exclusions"]:
        all_reasons[row["canonical_subject_key"]].update(row["reasons"])
    counts = Counter(eligible=len(rows), insufficient_paraphrases_removed=0)
    historical = []
    for index, row in enumerate(rows):
        if row["item_id"] in reserved:
            counts["historical_reservations_removed"] += 1
        elif norm(row["subject"]) in old_exposed:
            counts["v1_other_exposures_removed"] += 1
        elif len(row.get("paraphrases", [])) < 2:
            counts["insufficient_paraphrases_removed"] += 1
        else:
            historical.append((index, row))
    counts["historical_remainder_before_training"] = len(historical)
    drawn = np.random.default_rng(training["seed"]).permutation(len(historical))[
        : len(training["items"])
    ]
    reconstructed_training = [historical[int(i)][1]["item_id"] for i in sorted(drawn)]
    if reconstructed_training != [r["item_id"] for r in training["items"]]:
        raise ValueError("DEC-037 training identity no longer matches historical recipe")
    train_ids = {r["item_id"] for r in training["items"]}
    train_subjects = {norm(r["subject"]) for r in training["items"]}
    accepted, decisions = [], []
    reason_families = Counter()
    for index, row in historical:
        s = norm(row["subject"])
        if row["item_id"] in train_ids or s in train_subjects:
            counts["dec037_training_removed"] += 1
            continue
        counts["nominal_remainder_after_dec037"] += 1
        if s not in by_subject:
            raise ValueError("old eligible subject missing from v3")
        canonical = by_subject[s]["canonical_subject_key"]
        reasons = sorted(all_reasons[canonical] - {"old_eligible:counterfact"})
        if reasons:
            counts["additional_v3_exposures_removed"] += 1
            reason_families.update({r.split(":", 1)[0] for r in reasons})
            decisions.append(
                {
                    "eligible_source_index": index,
                    "item_id": row["item_id"],
                    "canonical_subject_key": canonical,
                    "reasons": reasons,
                    "source_record_sha256": digest(row),
                }
            )
        else:
            accepted.append((index, row, canonical))
    counts["conditional_remainder_candidates"] = len(accepted)
    counts["strict_v3_candidates_without_exception"] = sum(
        norm(row["subject"]) not in by_subject for row in rows if row["item_id"] not in reserved
    )
    if len({r["item_id"] for _, r, _ in accepted}) != len(accepted):
        raise ValueError("duplicate candidate item")
    if len({canonical for _, _, canonical in accepted}) != len(accepted):
        raise ValueError("duplicate canonical candidate subject")
    if any(
        r["item_id"] in reserved or norm(r["subject"]) in train_subjects for _, r, _ in accepted
    ):
        raise ValueError("reserved/training identity survived")
    return accepted, decisions, dict(counts), dict(reason_families)


def prepare(output, resource_dir):
    if output.exists() or resource_dir.exists():
        raise ValueError("new manifest and new resource directory required")
    if not output.resolve().is_relative_to(ROOT) or not resource_dir.resolve().is_relative_to(
        ASSETS
    ):
        raise ValueError("manifest belongs in repo and data resources in assets")
    sources = {}

    def bind(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        value = sha(path)
        if expected and value != expected:
            raise ValueError("source hash mismatch: " + str(path))
        sources[str(path)] = value
        return path

    pools = json.loads(bind("manifests/dev/pools.json").read_text())
    source = pools["counterfact"]
    eligible_path = bind(source["confirm_pool_path"], source["confirm_pool_sha256"])
    rows = [json.loads(line) for line in eligible_path.read_text().splitlines()]
    prior = json.loads(bind("manifests/revision_v1/exclusions.json").read_text())
    register_path = bind("manifests/revision_v1/exclusions_v3.json")
    current = json.loads(register_path.read_text())
    training = json.loads(bind("manifests/revision_v1/train_pool_counterfact_v1.json").read_text())
    metadata = []
    for r in range(3):
        # Public aggregate/order-digest metadata; no realization payload is opened.
        path = bind(ROOT / "manifests" / "confirm" / f"counterfact_r{r}.meta.json")
        metadata.append(json.loads(path.read_text()))
    for rel in (
        "scripts/sample_confirm.py",
        "scripts/r1_d2_train_pool.py",
        "scripts/r1_d2_candidates.py",
    ):
        bind(rel)
    reserved, checks = old_reservations([r["item_id"] for r in rows], metadata)
    candidates, excluded, counts, families = filter_remainder(
        rows, reserved, prior, current, training
    )
    data = json.loads(bind("manifests/datasets.json").read_text())
    raw = bind(
        ASSETS / "data/raw/counterfact/counterfact.json",
        data["counterfact"]["files"]["data/raw/counterfact/counterfact.json"],
    )
    raw_inventory = sorted(
        str(p.relative_to(ASSETS / "data/raw"))
        for p in (ASSETS / "data/raw").rglob("*")
        if p.is_file()
    )
    cf_files = [p for p in raw_inventory if "counterfact" in p.casefold()]
    if cf_files != ["counterfact/counterfact.json"]:
        raise ValueError("additional local CounterFact sources need review before emission")
    resource_dir.mkdir(parents=True)
    payload = resource_dir / "counterfact_remainder_candidates.jsonl"
    details = resource_dir / "v3_additional_exclusions.jsonl"
    inventory = []
    with payload.open("x") as f:
        for rank, (index, row, canonical) in enumerate(candidates):
            record = {**row, "eligible_source_index": index, "source_record_sha256": digest(row)}
            f.write(
                json.dumps(record, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
            )
            item = {
                "candidate_rank": rank,
                "eligible_source_index": index,
                "item_id": row["item_id"],
                "fact_id": row["fact_id"],
                "normalized_subject": norm(row["subject"]),
                "canonical_subject_key": canonical,
                "source_record_sha256": digest(row),
                "prepared_record_sha256": digest(record),
                "prompt_sha256": hashlib.sha256(row["prompt"].encode()).hexdigest(),
                "conditional_candidate": True,
                "confirmatory_admitted": False,
            }
            item["candidate_sha256"] = digest(item)
            inventory.append(item)
    with details.open("x") as f:
        for row in excluded:
            f.write(
                json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
            )
    result = {
        "schema_version": 1,
        "task": "R1-D2",
        "name": "counterfact_fresh_candidates_v1",
        "status": "two_readings_prepared_for_lead_decision_not_a_draw",
        "sources_sha256": sources,
        "counts": counts,
        "historical_reservation_verification": {
            "method": "reproduce identity-only historical DATA-02 recipe; verify all 15 public order digests",
            "reserved_item_count": len(reserved),
            "checks": checks,
            "historical_payloads_opened": 0,
            "historical_manifests_recreated": False,
            "new_random_sampling_performed": False,
        },
        "option_a": {
            "status": "conditional_on_explicit_reason_specific_old_pool_exception",
            "requested_exception": "waive only old_eligible:counterfact; retain all other reasons including old_eligible:zsre",
            "register": str(register_path),
            "register_sha256": sources[str(register_path)],
            "strict_v3_without_exception_count": counts["strict_v3_candidates_without_exception"],
            "nominal_remainder_after_dec037": counts["nominal_remainder_after_dec037"],
            "additional_v3_removed": counts["additional_v3_exposures_removed"],
            "additional_exposure_reason_families_nonexclusive": families,
            "candidate_count": len(inventory),
            "ordered_by": "ascending eligible-source line index; no fresh permutation",
            "candidates": inventory,
            "candidates_sha256": digest(inventory),
            "payload": {"path": str(payload), "sha256": sha(payload), "records": len(inventory)},
            "additional_exclusions": {
                "path": str(details),
                "sha256": sha(details),
                "records": len(excluded),
            },
            "e2_status": "historical original-base eligible source; no new teacher run",
            "context_status": "v3 primary/canonical reasons enforced; expanded training-text context/alias review still required",
        },
        "option_b": {
            "status": "unavailable_no_additional_local_counterfact_source",
            "candidate_count": 0,
            "candidates": [],
            "local_raw_inventory": raw_inventory,
            "counterfact_files_found": cf_files,
            "known_original_source_path": str(raw),
            "known_original_source_sha256": sources[str(raw)],
            "interpretation": "the existing raw archive is the same source used in v0, not an independent fresh-source option; this says nothing about sources available elsewhere",
        },
        "selected_option": None,
        "draws_emitted": 0,
        "final_sealing_ready": False,
        "teacher_executed": False,
        "tokenization_executed": False,
        "gpu_seconds": 0,
        "sealed_payloads_opened": 0,
        "next_gates": [
            "lead chooses a reason-specific remainder exception or supplies a reviewed fresh source",
            "review canonical/context overlap against all exposed training texts and applicable reference teacher policy",
            "reserve disjoint final edit streams plus unseen-prompt/challenge inventories before any run",
            "independent final draw/sealing only after lead and freeze gates; never use this list for reader development",
        ],
    }
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed during preparation: " + path)
    with output.open("x") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "sha256": sha(output),
                "counts": counts,
                "v3_reason_families": families,
                "fresh_source": result["option_b"]["status"],
            },
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--assets-output", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.output.resolve(), args.assets_output.resolve())


if __name__ == "__main__":
    main()
