"""Build HT-2's development-only six-cell contract; never execute models."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 303
SOURCES = {
    "zsre": "zsre_dev.json",
    "counterfact": "counterfact_dev.json",
    "mquake": "mquake_dev_v3b.json",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def key(ds, role, item):
    return hashlib.sha256(f"HT-2:{SEED}:{ds}:{role}:{item['item_id']}".encode()).hexdigest()


def family(row):
    if row.get("relation_id"):
        return "relation:" + row["relation_id"]
    prompt = " ".join(row["prompt"].casefold().split())
    subject = " ".join(row["subject"].casefold().split())
    if not subject or subject not in prompt:
        return None
    return "exact_subject_masked_template:" + prompt.replace(subject, "<subject>")


def build():
    datasets = {}
    cells = []
    for ds, name in SOURCES.items():
        path = ROOT / "manifests/dev" / name
        doc = json.loads(path.read_text())
        rows = doc["items"]
        if len({r["item_id"] for r in rows}) != len(rows):
            raise ValueError("duplicate development IDs")
        # Keep one row per normalized subject before computing family eligibility.
        seen = set()
        unique = []
        for r in sorted(rows, key=lambda r: key(ds, "dedup", r)):
            subject = " ".join(r["subject"].casefold().split())
            if subject not in seen:
                seen.add(subject)
                unique.append(r)
        groups = defaultdict(list)
        for r in unique:
            if family(r):
                groups[family(r)].append(r)
        eligible = {
            f: rs
            for f, rs in groups.items()
            if 4 <= len(rs) <= 20 and len(unique) - len(rs) >= 100 - len(rs)
        }
        if not eligible:
            raise ValueError("no predeclared eligible family; no fallback after outcomes")
        ranked = sorted(
            eligible,
            key=lambda f: (
                -sum(len(r["answer_ids"]) - 1 for r in eligible[f]) / len(eligible[f]),
                f,
            ),
        )
        selected = ranked[0]
        difficult = sorted(eligible[selected], key=lambda r: key(ds, "difficult", r))
        other = sorted(
            [r for r in unique if family(r) != selected], key=lambda r: key(ds, "other", r)
        )
        warm = other[:20]
        middle_other = other[20 : 60 - len(difficult)]
        later = other[60 - len(difficult) : 100 - len(difficult)]
        block = middle_other + difficult
        shuffled = sorted(block, key=lambda r: key(ds, "shuffle", r))

        def ids(rs):
            return [r["item_id"] for r in rs]

        ordered = {"clustered": ids(warm + block + later), "shuffled": ids(warm + shuffled + later)}
        if any(len(v) != 100 or len(set(v)) != 100 for v in ordered.values()) or set(
            ordered["clustered"]
        ) != set(ordered["shuffled"]):
            raise ValueError("paired 100-item inventory required")
        datasets[ds] = {
            "source": {"path": str(path.relative_to(ROOT)), "sha256": sha(path)},
            "family": selected,
            "family_size": len(difficult),
            "family_mean_answer_tokens_excluding_terminal": sum(
                len(r["answer_ids"]) - 1 for r in difficult
            )
            / len(difficult),
            "difficult_item_ids": ids(difficult),
            "fixed_old_fact_probe_ids": ids(warm),
            "ordered_item_ids": ordered,
            "family_ranking": [
                {
                    "family": f,
                    "n": len(eligible[f]),
                    "mean_answer_tokens_excluding_terminal": sum(
                        len(r["answer_ids"]) - 1 for r in eligible[f]
                    )
                    / len(eligible[f]),
                }
                for f in ranked
            ],
        }
        for schedule in ("shuffled", "clustered"):
            cells.append(
                {
                    "cell_id": f"HT2-{ds}-{schedule}-s{SEED}",
                    "dataset": ds,
                    "schedule": schedule,
                    "attempted_edits": 100,
                    "seed": SEED,
                    "reader_slot": "selected_primary",
                    "measurement_points": [20, 60, 70, 80, 100],
                }
            )
    return {
        "schema_version": 1,
        "task": "HT-2",
        "status": "contract_only_no_execution",
        "banner": "development, not confirmatory",
        "selected_primary": {"path": None, "sha256": None, "weights": None},
        "execution_authorized": False,
        "confirmation_populations_used": False,
        "seed": SEED,
        "cells": cells,
        "datasets": datasets,
        "difficulty_definition": "metadata proxy only: rank eligible exact relation/template families by mean answer-token length (terminal excluded), lexical tie-break. Between 4 and 20 distinct subjects; enough non-family rows for 100 total. No reader or original-base scores used.",
        "ordering_definition": "SHA256 ordering HT-2:303:dataset:role:item_id; common 20 warm-up edits, same 40 treatment edits, same 40 later edits. Cluster all difficult items at end of treatment; shuffle same 40 treatment facts. Both arms measure at treatment end (60), not at a varying last-difficult-item time.",
        "old_fact_measurement": {
            "n": 20,
            "policy": "all first-20 taught answers and existing paraphrases; include failures to acquire in denominators",
            "reference": "paired pre-treatment state at edit 20; original-base values separately labelled",
            "outcomes": [
                "target NLL change from edit20 for fixed target tokens",
                "exact-match retention",
                "paraphrase retention",
            ],
            "recovery": "first measured t in {60,70,80,100} with mean positive target-NLL degradation <=0.01 nat/token and exact-match count >= edit20 count, sustained at all subsequent measured times",
            "censoring": "if absent, right-censor >40 later updates; report interval (previous measured lag, first recovered lag], point 0 allowed; missing or failed probes are failed assays, never recovered",
            "training_on_probes": False,
            "update_on_probe_queries": False,
        },
        "budget": {
            "gpu_seconds_ceiling_total": 14400,
            "hard_model_experiment_stop": "2026-10-09T23:59:59-04:00",
            "scheduling": "owner approval of block order; after initial confirmatory blocks are secure and before realization2 if lead accepts",
            "accounting": "charge setup, model work, probes, retries and failed work; no new cell if remaining measured budget is inadequate",
        },
        "driver_recipe_form": {
            "mode": "stage4_development_cell",
            "banner": "development, not confirmatory",
            "integrity_profile": "incremental",
            "integrity_batch_edits": 16,
            "cell": {
                "condition": "R1_learned_ff",
                "dataset": "<one dataset>",
                "realization": "ht-dev-s303",
                "order": "<shuffled|clustered>",
            },
            "checkpoints": [20, 60, 70, 80, 100],
            "payload": {
                "path": "<new file under assets/runs/pc_cap/R1/stage4_dev_payloads>",
                "sha256": None,
            },
            "reader_provenance": {"primary": {"path": None, "sha256": None}},
            "adapter_identity": None,
            "code_sha256": None,
            "tokenizer_sha256": None,
            "admission": {
                "protocol_frozen": False,
                "lead_approved": False,
                "condition_admitted": False,
                "launch_authorized": False,
            },
            "warning": "template, NOT currently executable: existing development validator uses 100/300/1000 cadence; owner needs a separately tested stress driver with fixed-probe NLL and arbitrary development cadence, plus source/reader/base hashes",
        },
        "gates": [
            "selected primary bound after common-population selection",
            "review and bind metadata-only family choices before panel outcomes",
            "stress driver CPU end-to-end tests and query-purity tests",
            "reader/base/tokenizer/code/payload hash bindings",
            "lead pilot scheduling go-ahead, GPU lease, memory guard and measured cost budget",
        ],
        "sources_sha256": {
            n: sha(ROOT / n)
            for n in (
                "docs/heavy_tail_counter_review.md",
                "docs/heavy_tail_suggested_slight_pivot.md",
                "scripts/ht_build_development_panel.py",
            )
        },
        "gpu_seconds": 0,
    }


def main():
    path = ROOT / "manifests/revision_v1/ht_development_panel_v1.json"
    value = build()
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(
        json.dumps(
            {
                ds: {"family": v["family"], "n": v["family_size"]}
                for ds, v in value["datasets"].items()
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
