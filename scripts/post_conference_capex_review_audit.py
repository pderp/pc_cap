"""CPU-only evidence checks for Capex's 20 October post-conference review.

Reads saved results; does not import JAX, run models, or modify historical data.
Run from any directory:
    python3 scripts/post_conference_capex_review_audit.py --output <new-file.json>
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT.parent / "assets/extremes_analysis/ext-20261009/checkpoints/scores"
RECIPE = ROOT / "docs/tasks/R1-final-cell-recipes/43925e53c31860219a85ef90.json"
MODELS = [f"{rule}_reader_s{seed}" for rule in ("bp", "epc") for seed in range(3)]


def normalized(text):
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def audit():
    sources = {}

    def read(path, expected=None):
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if expected is not None and digest != expected:
            raise ValueError(f"source hash mismatch: {path}")
        sources[str(path.relative_to(ROOT.parent))] = digest
        return data

    def saved(model, dataset, horizon):
        directory = SCORES / model / dataset / horizon
        manifest = json.loads(read(directory / "chunks.json"))
        if manifest["status"] != "complete":
            raise ValueError(f"incomplete scores: {directory}")
        rows = []
        for name, info in sorted(manifest["chunks"].items()):
            chunk = [
                json.loads(line)
                for line in read(directory / f"{name}.jsonl", info["sha256"]).splitlines()
            ]
            if len(chunk) != info["n"]:
                raise ValueError("chunk row count mismatch")
            rows.extend(chunk)
        if len(rows) != manifest["n_probes"]:
            raise ValueError("probe count mismatch")
        probes = json.loads(read(directory / "probes.json"))
        mapping = {p["probe_id"]: p for p in probes}
        if len(mapping) != len(probes) or {r["probe_id"] for r in rows} != set(mapping):
            raise ValueError("probe identity mismatch")
        return rows, mapping

    recipe = json.loads(read(RECIPE))
    payload = json.loads(read(Path(recipe["payload"]["path"]), recipe["payload"]["sha256"]))
    items = payload["items"][:300]
    if len(items) != 300:
        raise ValueError("expected the 300-edit population")
    by_id = {item["item_id"]: item for item in items}
    by_prompt = {item["prompt"]: item for item in items}
    structure = Counter()
    for item in items:
        for neighbour in item["locality"][:3]:
            structure["rows"] += 1
            structure["same_subject_as_parent"] += (
                normalized(item["subject_key"]) == normalized(neighbour["subject_key"])
            )
            structure["same_relation_as_parent"] += item["relation_id"] == neighbour["relation_id"]
            structure["locality_id_is_taught"] += neighbour["item_id"] in by_id
            structure["locality_prompt_is_taught"] += neighbour["prompt"] in by_prompt

    frozen, probes = saved("frozen", "mquake", "h0")
    frozen = {r["probe_id"]: r for r in frozen if r["family"] == "locality_item"}
    locality = {key: probes[key] for key in frozen}
    overlap = {}
    for key, probe in locality.items():
        if probe["prompt"] not in by_prompt:
            continue
        taught = by_prompt[probe["prompt"]]
        old_aliases = {normalized(a) for a in probe["targets"]["true"]["aliases"]}
        new_aliases = {normalized(a) for a in taught["aliases"]}
        overlap[key] = {
            "probe_id": key,
            "parent_item_id": probe["item_id"],
            "taught_item_id": taught["item_id"],
            "prompt": probe["prompt"],
            "locality_old_answer": probe["targets"]["true"]["text"],
            "taught_new_answer": taught["answer"],
            "answer_aliases_disjoint": old_aliases.isdisjoint(new_aliases),
        }

    selection_rows, locality_rows = [], []
    for dataset in ("zsre", "counterfact", "mquake"):
        for model in MODELS:
            rows, _ = saved(model, dataset, "h300")
            counts = Counter()
            groups = defaultdict(Counter)
            for row in rows:
                sel = row.get("selection") or {}
                if row["family"] in ("edit", "paraphrase"):
                    ids, weights = sel["record_ids"], sel["weights"]
                    if len(ids) != len(weights):
                        raise ValueError("candidate/weight shape mismatch")
                    own_marker = ":" + str(row["item_id"]) + ":"
                    in_candidates = any(own_marker in rid for rid in ids)
                    selected = (
                        ids[max(range(len(ids)), key=lambda i: weights[i])]
                        if ids and sum(weights) > 0 else None
                    )
                    top_is_own = selected is not None and own_marker in selected
                    counts["edit_and_paraphrase_rows"] += 1
                    counts["own_in_candidates"] += in_candidates
                    counts["top_candidate_is_own"] += top_is_own
                    counts["own_in_candidates_but_top_is_not_own"] += in_candidates and not top_is_own
                    counts["top_is_own_but_gate_abstained"] += top_is_own and sel["hard_null"]
                if dataset != "mquake" or row["family"] != "locality_item":
                    continue
                key = row["probe_id"]
                if key not in frozen:
                    raise ValueError("unpaired locality row")
                on, off = row["targets"]["true"], frozen[key]["targets"]["true"]
                if on["status"] != "ok" or off["status"] != "ok" or on["answer_ids"] != off["answer_ids"]:
                    raise ValueError("incomparable locality losses")
                deterioration = on["nll_token"] - off["nll_token"]
                group = "taught_prompt_overlap" if key in overlap else "nonoverlap"
                groups[group]["rows"] += 1
                groups[group]["fired"] += not sel["hard_null"]
                groups[group]["deterioration_gt_0p001"] += deterioration > 0.001
                groups[group]["deterioration_gt_2"] += deterioration > 2
            selection_rows.append(dict(dataset=dataset, model=model, **counts))
            if dataset == "mquake":
                if sum(g["rows"] for g in groups.values()) != len(frozen):
                    raise ValueError("locality partition incomplete")
                locality_rows.append(dict(model=model, groups=dict(groups)))

    harm_path = ROOT / "results/extremes_analysis/ext-20261009/tables/cap_value/harm_unrelated_text.csv"
    harm = defaultdict(list)
    for row in csv.DictReader(read(harm_path).decode().splitlines()):
        if row["model"] != "frozen":
            harm[(row["dataset"], row["rule"])].append(float(row["es99_positive"]))
    harm_summary = []
    for (dataset, rule), values in sorted(harm.items()):
        if len(values) != 3:
            raise ValueError("expected three harm seeds")
        harm_summary.append(dict(dataset=dataset, rule=rule, mean=sum(values) / 3, seed_values=values))

    history_fields = {}
    for model in MODELS:
        rule, seed = model.split("_reader_s")
        path = ROOT / f"results/extremes_analysis/ext-20261009/mquake_eval/eval-{rule}-s{seed}-mquake/stream/items.jsonl"
        rows = [json.loads(line) for line in read(path).splitlines()]
        if len(rows) != 300:
            raise ValueError("expected 300 saved acquisition records")
        history_fields[model] = dict(Counter(key for row in rows for key in row["outcome"]))

    read(Path(__file__).resolve())
    return {
        "date": "2026-10-20",
        "scope": "saved-artifact review; no model calls; historical results unchanged",
        "severe_event": "cap minus frozen mean target-token NLL > 2 nats (including terminator)",
        "mquake_locality_structure": dict(structure),
        "mquake_locality_unique_prompts": len({p["prompt"] for p in locality.values()}),
        "mquake_overlap_rows": len(overlap),
        "mquake_overlap_unique_prompts": len({p["prompt"] for p in overlap.values()}),
        "mquake_overlap_examples": list(overlap.values()),
        "mquake_locality_partition": locality_rows,
        "candidate_presence_vs_top_selection": selection_rows,
        "ordinary_text_es99_positive": harm_summary,
        "saved_mquake_acquisition_outcome_fields": history_fields,
        "source_sha256": sources,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as out:
        json.dump(result, out, indent=2, allow_nan=False)
        out.write("\n")
    print(f"Saved review evidence: {args.output}")


if __name__ == "__main__":
    main()
