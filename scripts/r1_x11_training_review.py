"""R1-X11: metadata-only episode rehearsal and stored-result recount; no base."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

import numpy as np

from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.revision_v1 import stream_train as current
from pccap.revision_v1.train import PrefixFeat

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_bank():
    tok = GPT2Tokenizer()
    items, groups, bindings, datasets = [], [], {}, {}
    zero = np.zeros(1, np.float32)

    def prefix(ids, target=-1):
        ids = np.asarray(ids, np.int32)
        return PrefixFeat(
            ids=ids, n=len(ids), target=target, last=zero, span=zero, capoff_logits=None
        )

    for ds, version in (("counterfact", 1), ("zsre", 1), ("mquake", 3)):
        p = ROOT / f"manifests/revision_v1/train_pool_{ds}_v{version}.json"
        bindings[str(p.relative_to(ROOT))] = sha(p)
        rows = json.loads(p.read_text())["items"][:1000]
        off = len(items)
        for row in rows:
            prompt, answer = (
                np.asarray(row["prompt_ids"], np.int32),
                np.asarray(row["answer_ids"], np.int32),
            )
            paras = []
            for text in row.get("paraphrases", [])[:2]:
                pair = tokenize_pair(tok, text, row["answer"])
                paras.append((zero, zero, [prefix(pair.prompt_ids, int(pair.answer_ids[0]))]))
            loc = [
                (zero, zero, prefix(tok.encode(text)))
                for text in row.get("locality_prompts", [])[:2]
            ]
            items.append(
                current.ItemFeatures(
                    row["item_id"],
                    row.get("fact_id", row["item_id"]),
                    zero,
                    zero,
                    zero,
                    zero,
                    prompt,
                    answer,
                    [prefix(prompt, int(answer[0]))],
                    paras,
                    loc,
                    row.get("subject", ""),
                )
            )
            datasets[row["item_id"]] = ds
        groups.append(list(range(off, off + len(rows) - 100)))
    return current.FeatureBank(items, "mixed"), groups, bindings, datasets, tok.file_sha256()


def rehearse(builder, bank, groups, datasets, *, seed=0, prob=None, steps=300):
    rng = np.random.default_rng(seed)
    collisions, locals_, roles = Counter(), Counter(), Counter()
    fractions = []
    for _ in range(steps):
        kwargs = (
            {} if prob is None else {"out_paraphrase_nulls": True, "out_paraphrase_null_prob": prob}
        )
        batch = [
            builder.stream_episode_mixed(
                groups, bank, rng, n_memory=64, n_query_records=8, n_out=8, **kwargs
            )
            for _ in range(2)
        ]
        for ep in batch:
            # Exact post-batch RNG consumption of add_text_nulls with 512*3 prefixes.
            rng.choice(1536, size=8, replace=False)
            mem = {tuple(s.prompt_ids) for s in ep.supports}
            rec = sum(q.target_record >= 0 for q in ep.queries)
            null = len(ep.queries) - rec + 8
            outpara = sum(q.query_id.startswith("outpara:") for q in ep.queries)
            fractions.append(
                {
                    "record_count": rec,
                    "null_count": null,
                    "outpara_count": outpara,
                    "null_query_weight": 0.5 / null,
                    "outpara_L2_mass": 0.5 * outpara / null,
                }
            )
            roles["text"] += 8
            for q in ep.queries:
                role = q.query_id.split(":", 1)[0]
                roles[role] += 1
                if role == "loc":
                    ds = datasets[q.query_id.split(":", 1)[1]]
                    locals_[ds] += 1
                    collisions[ds] += int(tuple(q.query_ids) in mem)
    return {
        "seed": seed,
        "episodes": steps * 2,
        "groups": [len(g) for g in groups],
        "locality": {
            ds: {
                "collisions": collisions[ds],
                "queries": locals_[ds],
                "rate": collisions[ds] / locals_[ds] if locals_[ds] else None,
            }
            for ds in ("counterfact", "zsre", "mquake")
        },
        "all_locality": {
            "collisions": sum(collisions.values()),
            "queries": sum(locals_.values()),
            "rate": sum(collisions.values()) / sum(locals_.values()),
        },
        "roles": dict(roles),
        "episode_mean": {k: float(np.mean([f[k] for f in fractions])) for k in fractions[0]},
        "balanced_L2_record_mass": 0.5,
        "balanced_L2_null_mass": 0.5,
    }


def recount():
    bindings = {}

    def read(rel):
        p = ROOT / rel
        raw = p.read_bytes()
        bindings[rel] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    candidates = {}
    population = []
    for name in ("tri4_text_s0", "tri4_text_s2", "tri5_text_s0"):
        training = read(f"results/R1/pilot/r1_50_stream_{name}/summary.json")
        entry = {
            "training_args": training["args"],
            "best_step_zero_based": training["best_step"],
            "theta_params_hash": training["theta_hash"],
            "streams": {},
        }
        for ds, suffix in (("zsre", ""), ("counterfact", "@counterfact"), ("mquake", "@mquake")):
            tag = f"{name}_rare1_null0.5{suffix}"
            run = read(f"results/R1/stream_eval_{tag}.json")
            p = ROOT / f"results/R1/streams_revision/{tag}/items.jsonl"
            bindings[str(p.relative_to(ROOT))] = sha(p)
            rows = [json.loads(x) for x in p.read_text().splitlines()]
            assert len(rows) == 100 and len({r["item_id"] for r in rows}) == 100
            cp = read(f"results/R1/streams_revision/{tag}/checkpoints.json")
            entry["streams"][ds] = {
                "summary": run["stream_metrics"],
                "n": len(rows),
                "ordered_item_ids": [r["item_id"] for r in rows],
                "args": run["args"],
                "checkpoint_tail": cp[-1],
            }
            assert run["theta_hash"] == training["theta_hash"]
        short = name.replace("_text", "")
        report = read(f"results/R1/endpoints/{short}_rare1_n100_unseen_zsre/report.json")
        summary = read(f"results/R1/endpoints/{short}_rare1_n100_unseen_zsre/summary.json")
        rows = report["rows"]
        assert len(rows) == 100 and report["memory_records"] == report["edited_items"] == 100
        assert all(r["status"] == "ok" and isinstance(r["false_fire"], bool) for r in rows)
        fires = sum(r["false_fire"] for r in rows)
        entry["unseen"] = {
            "n": len(rows),
            "fires": fires,
            "false_fire_rate": fires / len(rows),
            "answer_changes": sum(r["answer_changed"] for r in rows),
            "both_terminated": sum(r["both_answers_terminated"] for r in rows),
            "outside_source": summary["outside_source"],
            "source_sha256": report["source_sha256"],
            "requested_item_ids_sha256": report["requested_item_ids_sha256"],
            "edited_item_ids": summary["edited_item_ids"],
            "outside_item_ids": summary["outside_item_ids"],
        }
        entry["mean_RET_GS"] = (
            sum(entry["streams"][ds]["summary"]["ret_gs_end"] for ds in entry["streams"]) / 3
        )
        entry["eligible_on_observed_metrics_only"] = fires <= 10 and all(
            s["summary"]["ls_complete_answer_end"] >= 0.98 for s in entry["streams"].values()
        )
        population.append(
            (summary["edited_item_ids"], summary["outside_item_ids"], report["source_sha256"])
        )
        candidates[name] = entry
    assert all(x == population[0] for x in population)
    for ds in ("zsre", "counterfact", "mquake"):
        assert len({tuple(c["streams"][ds]["ordered_item_ids"]) for c in candidates.values()}) == 1
    oldtags = sorted((ROOT / "results/R1").glob("stream_eval_tri2*"))
    inventory = {
        "tri4_seed1_complete": (
            ROOT / "results/R1/pilot/r1_50_stream_tri4_text_s1/summary.json"
        ).exists(),
        "tri6_seed0_complete": (
            ROOT / "results/R1/pilot/r1_50_stream_tri6_text_s0/summary.json"
        ).exists(),
        "historical_tri2_stream_paths": [str(p.relative_to(ROOT)) for p in oldtags],
    }
    return candidates, bindings, inventory


def build():
    bank, groups, bindings, datasets, toksha = metadata_bank()
    historical = ROOT / "logs/r1_round12/source_snapshot/src/pccap/revision_v1/stream_train.py"
    spec = importlib.util.spec_from_file_location("pccap.revision_v1.r1_x11_historical", historical)
    import sys

    old = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = old
    spec.loader.exec_module(old)
    bindings[str(historical.relative_to(ROOT))] = sha(historical)
    for rel in (
        "src/pccap/revision_v1/stream_train.py",
        "src/pccap/revision_v1/train.py",
        "src/pccap/revision_v1/train_fast.py",
        "scripts/r1_50_stream_train.py",
    ):
        bindings[rel] = sha(ROOT / rel)
    trials = {}
    for seed in (0, 2):
        trials[f"historical_seed{seed}"] = rehearse(old, bank, groups, datasets, seed=seed)
    for name, prob in (("fixed", None), ("question_full", 1.0), ("question_35pct", 0.35)):
        trials[name] = rehearse(current, bank, groups, datasets, prob=prob)
    candidates, resultbindings, inventory = recount()
    bindings.update(resultbindings)
    return {
        "schema_version": 1,
        "task": "R1-X11",
        "mode": "CPU metadata rehearsal and stored result recount",
        "gpu_executions": 0,
        "base_executions": 0,
        "confirmatory": False,
        "bindings": bindings,
        "tokenizer_sha256": toksha,
        "rehearsal_scope": "Actual ordered first-1000 pools, last 100 held out per pool; metadata features only; first two paraphrases/localities; 300 batches of two 64-record episodes, 8 query records, 8 outside, then 8 of 1536 text null RNG draws. Historical code snapshot, not an execution trace of historical training. Dummy numeric features never enter a loss/model.",
        "homogeneous_heuristic": 63 / 499,
        "rehearsals": trials,
        "candidates": candidates,
        "paired_recent_stream_ids": True,
        "paired_recent_unseen_ids": True,
        "inventory": inventory,
        "final_primary_selected": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("report must be in pc_cap")
    if args.output.exists():
        raise FileExistsError(args.output)
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, allow_nan=False)
    print(
        json.dumps(
            {
                "rehearsals": result["rehearsals"],
                "candidates": {
                    k: {
                        "mean_RET_GS": v["mean_RET_GS"],
                        "unseen": {j: v["unseen"][j] for j in ("n", "fires", "both_terminated")},
                    }
                    for k, v in result["candidates"].items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
