"""R1-X0: subject-only DATA-R1/S7 accounting and development paraphrase counts.

Does not open sealed realization payloads, select a fresh test, or run a teacher.
The conservative candidate count excludes the entire old eligible pools.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"


def normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def project_subjects(path: Path) -> tuple[list[str], str]:
    """Extract only subject string fields, leaving prompts and answers opaque."""
    raw = path.read_bytes()
    pattern = rb'"subject"\s*:\s*("(?:\\.|[^"\\])*")'
    return [normalize(json.loads(m.group(1))) for m in re.finditer(pattern, raw)], hashlib.sha256(raw).hexdigest()


def audit() -> dict:
    sources = {}

    def load(relative):
        p = ROOT / relative
        sources[relative] = sha(p)
        return json.loads(p.read_text())

    assets = load("manifests/datasets.json")
    pools = load("manifests/dev/pools.json")
    s7 = load("manifests/dev/s7_pairs.json")
    chosen = load("manifests/dev/s7_pairs_e2.json")
    dev, reserved, paraphrases = set(), set(), {}
    for dataset in ("zsre", "counterfact"):
        d = load(f"manifests/dev/{dataset}_dev.json")
        dev.update(normalize(r["subject"]) for r in d["items"])
        counts = Counter()
        for row in d["items"]:
            unique = {normalize(p) for p in row.get("paraphrases", []) if p.strip()} - {normalize(row["prompt"])}
            counts[len(unique)] += 1
        paraphrases[dataset] = {"items": len(d["items"]), "unique_unseen_paraphrases_histogram": dict(sorted(counts.items())),
                                "items_with_at_least_two": sum(n for k, n in counts.items() if k >= 2)}
        p = ASSETS / f"data/prepared/editing/{dataset}_eligible.jsonl"
        subjects, actual = project_subjects(p)
        if actual != pools[dataset]["confirm_pool_sha256"]:
            raise ValueError(f"source pool identity mismatch: {p}")
        sources[str(p)] = actual
        reserved.update(subjects)
    s0 = load("manifests/dev/s0_sample.json")
    dev.update(normalize(r["subject"]) for r in s0["items"])
    all_s7, selected_s7 = set(), set()
    s7_rows = {}
    for dataset in ("zsre", "counterfact"):
        selection = {p for ids in chosen["selection"][dataset].values() for p in ids}
        all_members = [p[k] for p in s7["pairs"][dataset] for k in ("a", "b")]
        selected_members = [p[k] for p in s7["pairs"][dataset] if p["pair_id"] in selection for k in ("a", "b")]
        candidate_subjects = {normalize(r["subject"]) for r in all_members}
        selected_subjects = {normalize(r["subject"]) for r in selected_members}
        all_s7.update(candidate_subjects)
        selected_s7.update(selected_subjects)
        s7_rows[dataset] = {"candidate_pairs": len(s7["pairs"][dataset]), "selected_pairs": len(selection),
                            "candidate_unique_subjects": len(candidate_subjects), "selected_unique_subjects": len(selected_subjects),
                            "unselected_candidate_subjects": len(candidate_subjects-selected_subjects),
                            "candidate_subjects_sha256": hashlib.sha256(json.dumps(sorted(candidate_subjects)).encode()).hexdigest()}
    raw_path = ASSETS / "data/raw/zsre/zsre_mend_train.json"
    raw, actual = project_subjects(raw_path)
    expected = assets["zsre"]["files"]["data/raw/zsre/zsre_mend_train.json"]
    if actual != expected:
        raise ValueError("MEND train identity mismatch")
    sources[str(raw_path)] = actual
    before_s7 = set(raw) - dev - reserved - {""}
    fresh = before_s7 - all_s7
    return {"task": "R1-X0", "sources_sha256": sources, "development_paraphrases": paraphrases,
            "s7": s7_rows, "mend_train": {"raw_subject_fields": len(raw), "unique_subjects": len(set(raw)),
                "empty_subject_fields": raw.count(""), "v0_dev_subjects_union": len(dev),
                "all_v0_eligible_pool_subjects_union": len(reserved),
                "unique_subjects_outside_dev_and_all_old_pools": len(before_s7),
                "additional_excluded_s7_inventory_subjects": len(before_s7 & all_s7),
                "additional_excluded_selected_s7_subjects": len(before_s7 & selected_s7),
                "conservative_unique_subject_candidates": len(fresh),
                "conservative_candidate_subject_set_sha256": hashlib.sha256(json.dumps(sorted(fresh)).encode()).hexdigest(),
                "candidate_record_count": sum(s in fresh for s in raw)},
            "eligibility_status": "subject candidates only; not tokenization/E.2-filtered and not reserved for confirmation",
            "policy": "Conservative review excludes all exposed S7 inventory candidates, including unselected candidates; lead must freeze the exact exclusion inventory.",
            "unresolved": ["Subject strings are not canonical entity IDs; aliases and neighborhood/query entities require explicit handling.",
                           "Challenge-set subjects and any newly exposed development subjects must join the exclusion register.",
                           "Do not count raw records as unique eligible facts or as three independent realizations.",
                           "Do not use this audit's subject counts as teacher-filtered confirmation capacity."],
            "sealed_realization_payloads_opened": 0, "gpu_seconds": 0}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    output = a.output.resolve()
    if not output.is_relative_to(ROOT) or output.exists():
        raise ValueError("output must be a new file inside pc_cap")
    result = audit()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({k: v for k, v in result.items() if k != "sources_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
