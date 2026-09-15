"""R1-X9: CPU evidence audit; reconstruction is conditional, never a data release."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import pickle
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from pccap.data.tokenize import GPT2Tokenizer, tokenize_pair
from pccap.revision_v1.stage4_cell import ROOT, sha, write_json
from pccap.revision_v1.stream_train import FeatureBank, stream_episode, stream_episode_mixed


def key(ids):
    return hashlib.sha256(np.asarray(ids, np.int32).tobytes()).hexdigest()


def norm(s):
    return " ".join(s.casefold().split())


def lean_bank(bank):
    """Keep exact cached query IDs and sampling cardinalities, discard feature/logit arrays."""
    out = []
    for it in bank.items:

        def prefix(p):
            return SimpleNamespace(ids=np.asarray(p.ids[: p.n], np.int32).copy(), n=p.n)

        out.append(
            SimpleNamespace(
                item_id=it.item_id,
                fact_id=it.fact_id,
                subject=it.subject,
                prompt_ids=it.prompt_ids.copy(),
                answer_ids=it.answer_ids.copy(),
                key_last=None,
                key_span=None,
                code_last=None,
                code_span=None,
                own=[prefix(it.own[0])],
                paraphrases=[(None, None, [prefix(x[2][0])]) for x in it.paraphrases],
                locality=[(None, None, prefix(x[2])) for x in it.locality],
            )
        )
    return FeatureBank(out, bank.dataset, identity=getattr(bank, "identity", {}))


def replay(bank, sizes, args, steps):
    """Use installed episode functions themselves; match batch-before-text RNG ordering."""
    offsets = np.cumsum([0, *sizes]).tolist()
    train = [list(range(a, b - args["held_out"])) for a, b in zip(offsets, offsets[1:])]
    dev = [list(range(b - args["held_out"], b)) for b in offsets[1:]]
    if any(not x for x in train + dev):
        raise ValueError("invalid per-pool holdout")
    seen = defaultdict(set)

    def capture(ep, phase):
        for q in ep.queries:
            seen[(phase, q.role)].add(key(q.query_ids))

    def episode(groups, rng, development=False, i=0):
        kw = dict(
            n_memory=min(args["n_memory"], sum(map(len, groups)))
            if development
            else args["n_memory"],
            n_query_records=args["n_query_records"],
            n_out=min(args["n_out"], 8) if development else args["n_out"],
            episode_id=f"dev-{i}" if development else "",
        )
        return (
            stream_episode_mixed(groups, bank, rng, **kw)
            if len(groups) > 1
            else stream_episode(bank, rng, pool_indices=groups[0], **kw)
        )

    def consume_text(rng):
        n = args.get("text_nulls", 0)
        if n > 0:
            total = args.get("text_windows", 512) * 3
            rng.choice(total, size=min(n, total), replace=False)

    drng = np.random.default_rng(args["seed"] + 1000)
    deps = [episode(dev, drng, True, i) for i in range(6)]
    for ep in deps:
        consume_text(drng)
        capture(ep, "heldout_reader")
    rng = np.random.default_rng(args["seed"])
    for _ in range(steps):
        batch = [episode(train, rng) for _ in range(args["batch"])]
        for ep in batch:
            consume_text(rng)
            capture(ep, "training_reader")
    return seen


def build():
    bindings = {}

    def read(p):
        p = Path(p).resolve()
        bindings[str(p)] = sha(p)
        return json.loads(p.read_text())

    def lines(p):
        p = Path(p).resolve()
        bindings[str(p)] = sha(p)
        return [json.loads(s) for s in p.read_text().splitlines() if s.strip()]

    paths = [
        ROOT / f"manifests/revision_v1/train_pool_{ds}_v1.json"
        for ds in ("zsre", "counterfact", "mquake")
    ]
    paths += [ROOT / "manifests/revision_v1/train_pool_mquake_v2.json"]
    paths += [ROOT / f"manifests/dev/{ds}_dev.json" for ds in ("zsre", "counterfact", "mquake")]
    docs = {str(p): read(p) for p in paths}
    tok = GPT2Tokenizer()
    # Exact original-prompt mapping only. No substring/entity guesses.
    prompt_subjects = defaultdict(set)
    known_rows = {}
    sources = [ROOT / "manifests/revision_v1/mquake_pool_v1.json"]
    allrows = [r for d in docs.values() for r in d["items"]] + read(sources[0])["items"]
    for ds in ("zsre", "counterfact"):
        p = ROOT.parent / f"assets/data/prepared/editing/{ds}_eligible.jsonl"
        if p.exists():
            allrows += lines(p)
    for r in allrows:
        ds = r["dataset"]
        known_rows[(ds, r["item_id"])] = r
        prompt_subjects[norm(r["prompt"])].add((ds, norm(r.get("subject", ""))))
    reservations = defaultdict(
        lambda: {
            "texts": set(),
            "owners": set(),
            "roles": set(),
            "sources": set(),
            "subjects": set(),
        }
    )

    def reserve(ds, text, role, owner, path, subjects=()):
        q = key(tok.encode(text))
        z = reservations[q]
        z["texts"].add(text)
        z["owners"].add(ds)
        z["roles"].add(role)
        z["sources"].add(path)
        z["subjects"].update(subjects or prompt_subjects.get(norm(text), set()))
        return q

    for path, d in docs.items():
        ds = d["dataset"]
        for r in d["items"]:
            reserve(ds, r["prompt"], "primary", r["item_id"], path, [(ds, norm(r["subject"]))])
            for text in r.get("paraphrases", []):
                reserve(ds, text, "paraphrase", r["item_id"], path, [(ds, norm(r["subject"]))])
            for text in r.get("locality_prompts", []):
                reserve(ds, text, "locality", r["item_id"], path)
            for n in r.get("near_miss_candidates", []):
                reserve(
                    ds,
                    n["prompt"],
                    "near_miss_reserved",
                    r["item_id"],
                    path,
                    [(ds, norm(n["subject_key"]))],
                )
        for text in d.get("unrelated_prompts", []):
            reserve(ds, text, "development_unrelated", "", path)
    banks = {}
    bank_evidence = []
    gaps = []
    evidence = defaultdict(set)
    for p in sorted((ROOT.parent / "assets/runs/pc_cap/R1/banks").glob("train_pool_*_1000.pkl")):
        if p.stem not in {
            "train_pool_counterfact_v1_1000",
            "train_pool_zsre_v1_1000",
            "train_pool_mquake_v1_1000",
            "train_pool_mquake_v2_1000",
        }:
            continue
        print("Reading cached bank", p.name, flush=True)
        bindings[str(p)] = sha(p)
        with p.open("rb") as handle:
            original = pickle.load(handle)
        content = original.content_hash()
        b = lean_bank(original)
        del original
        gc.collect()
        pool = str(ROOT / ("manifests/revision_v1/" + p.stem.removesuffix("_1000") + ".json"))
        rows = docs[pool]["items"][:1000]
        if [x.item_id for x in b.items] != [r["item_id"] for r in rows]:
            raise ValueError("bank membership differs: " + str(p))
        for it, row in zip(b.items, rows):
            if not np.array_equal(it.prompt_ids, row["prompt_ids"]) or not np.array_equal(
                it.answer_ids, row["answer_ids"]
            ):
                raise ValueError("cached support mismatch")
            pairs = [(key(it.prompt_ids), row["prompt"])]
            if len(it.paraphrases) != len(row["paraphrases"][:2]) or len(it.locality) != len(
                row["locality_prompts"][:2]
            ):
                raise ValueError("bank query count differs")
            for cached, text in zip(it.paraphrases, row["paraphrases"][:2]):
                ids = tokenize_pair(tok, text, row["answer"]).prompt_ids
                if key(cached[2][0].ids) != key(ids):
                    raise ValueError("cached paraphrase differs")
                pairs.append((key(ids), text))
            for cached, text in zip(it.locality, row["locality_prompts"][:2]):
                if key(cached[2].ids) != key(tok.encode(text)):
                    raise ValueError("cached locality differs")
                pairs.append((key(cached[2].ids), text))
            for q, _ in pairs:
                evidence[q].add(("bank_base_observation", str(p)))
        banks[pool] = (b, content)
        bank_evidence.append(
            {
                "path": str(p),
                "sha256": bindings[str(p)],
                "pool": pool,
                "items": len(b.items),
                "identity": b.identity,
                "queries_verified": True,
            }
        )
    sessions = []
    for p in sorted((ROOT / "results/R1/pilot").glob("r1_50*/summary.json")):
        d = read(p)
        a = d["args"]
        pools = [str((ROOT / x).resolve()) for x in a["pool"].split(",") if x]
        metric = p.parent / "metrics.jsonl"
        metrics = lines(metric) if metric.exists() else []
        complete = [m.get("step") for m in metrics] == list(range(a["steps"]))
        if not complete or not d.get("banks") or any(x not in banks for x in pools):
            gaps.append(
                {
                    "path": str(p),
                    "reason": "missing full metrics, bank receipt, or cached bank; no exact execution claim",
                }
            )
            continue
        verified = True
        for receipt, pool in zip(d["banks"], pools):
            b, content = banks[pool]
            if receipt["sha256"] != content or receipt.get("identity") != b.identity:
                verified = False
        if len(d["banks"]) != len(pools) or not verified:
            gaps.append({"path": str(p), "reason": "cached bank differs from session binding"})
            continue
        selected = [banks[x][0] for x in pools]
        combined = FeatureBank([it for b in selected for it in b.items], "mixed")
        seen = replay(combined, [len(b.items) for b in selected], a, a["steps"])
        for (phase, role), qs in seen.items():
            for q in qs:
                evidence[q].add((phase + ":" + role, str(p)))
        sessions.append(
            {
                "path": str(p),
                "sha256": bindings[str(p)],
                "steps": a["steps"],
                "seed": a["seed"],
                "pools": pools,
                "unique_queries_by_role": {"/".join(k): len(v) for k, v in seen.items()},
                "status": "RNG reconstruction from matching bank and completed metrics; historical sampler version not recorded",
            }
        )
    streams = []
    for p in sorted((ROOT / "results/R1/streams_revision").glob("*/items.jsonl")):
        rows = lines(p)
        found = 0
        for tr in rows:
            r = known_rows.get((tr.get("dataset"), tr.get("item_id")))
            if r is None:
                continue
            found += 1
            evidence[key(tok.encode(r["prompt"]))].add(("development_item_trace", str(p)))
            if tr.get("gs_n") == len(r.get("paraphrases", [])):
                for q in r.get("paraphrases", []):
                    evidence[key(tok.encode(q))].add(
                        ("development_paraphrase_reconstructed", str(p))
                    )
        summary = ROOT / f"results/R1/stream_eval_{p.parent.name}.json"
        if summary.exists():
            sm = read(summary)
            ds = sm.get("dataset", sm.get("args", {}).get("dataset", "zsre"))
            dev = docs.get(str(ROOT / f"manifests/dev/{ds}_dev.json"))
            if dev:
                for q in dev.get("unrelated_prompts", [])[:200]:
                    evidence[key(tok.encode(q))].add(
                        ("development_unrelated_schedule_inferred", str(summary))
                    )
        else:
            gaps.append(
                {
                    "path": str(p),
                    "reason": "no stream_eval summary; unrelated query identities absent in trace",
                }
            )
        streams.append(
            {
                "path": str(p),
                "items": len(rows),
                "mapped": found,
                "summary_present": summary.exists(),
            }
        )
    subject_queries = defaultdict(set)
    query_rows = []
    for q, r in sorted(reservations.items()):
        for pair in r["subjects"]:
            subject_queries[pair].add(q)
        query_rows.append(
            {
                "query_sha256": q,
                "texts": sorted(r["texts"]),
                "reservation_datasets": sorted(r["owners"]),
                "roles": sorted(r["roles"]),
                "reservation_sources": sorted(r["sources"]),
                "mapped_subjects": [
                    {"dataset": ds, "subject": s} for ds, s in sorted(r["subjects"])
                ],
                "execution_evidence": [{"kind": k, "path": p} for k, p in sorted(evidence[q])],
                "status": "evidence_found"
                if evidence[q]
                else "reservation_only_in_audited_evidence",
            }
        )
    subjects = []
    for (ds, s), qs in sorted(subject_queries.items()):
        kinds = {kind for q in qs for kind, _ in evidence[q]}
        subjects.append(
            {
                "dataset": ds,
                "subject": s,
                "query_sha256": sorted(qs),
                "evidence_kinds": sorted(kinds),
                "potentially_releasable_under_audited_scope": not kinds,
                "release_certified": False,
                "reason": "no matched evidence; incomplete history and context mapping prevent certified release"
                if not kinds
                else "execution or bank observation evidence found",
            }
        )
    historical = read(ROOT / "manifests/revision_v1/exclusions_frozen_v4_supplement_v2.json")
    historical_subjects = {
        r["canonical_subject"]: r["reasons"] for r in historical["additional_exclusions"]
    }
    # Enumerate supplement subjects too, including those with no current exact-prompt mapping.
    supplement_candidates = []
    bysubject = defaultdict(set)
    for (_ds, s), qs in subject_queries.items():
        bysubject[s].update(kind for q in qs for kind, _ in evidence[q])
    for s, reasons in sorted(historical_subjects.items()):
        if not bysubject[s]:
            supplement_candidates.append(
                {
                    "subject": s,
                    "current_reasons": reasons,
                    "evidence_kinds": [],
                    "status": "candidate for lead review only; absence is not proof of no execution",
                }
            )
    for name in (
        "scripts/r1_50_stream_train.py",
        "src/pccap/revision_v1/stream_train.py",
        "scripts/r1_13_stream_eval.py",
        "src/pccap/harness/runs.py",
        __file__,
    ):
        p = (ROOT / name).resolve()
        bindings[str(p)] = sha(p)
    return {
        "task": "R1-X9",
        "status": "conditional trace audit, no release",
        "released_subjects": 0,
        "gpu_seconds": 0,
        "bindings_sha256": bindings,
        "banks": bank_evidence,
        "sessions": sessions,
        "streams": streams,
        "gaps": gaps,
        "queries": query_rows,
        "subjects": subjects,
        "supplement_subjects_without_matched_evidence": supplement_candidates,
        "counts": {
            ds: {
                "reserved_mapped_subjects": sum(r["dataset"] == ds for r in subjects),
                "with_execution_or_bank_evidence": sum(
                    r["dataset"] == ds and bool(r["evidence_kinds"]) for r in subjects
                ),
                "potential_release_review_only": sum(
                    r["dataset"] == ds and not r["evidence_kinds"] for r in subjects
                ),
                "certified_release": 0,
            }
            for ds in ("zsre", "counterfact", "mquake")
        },
        "limits": [
            "Current RNG functions are bound; historical sessions did not pin sampler source, so reconstruction is conditional.",
            "All cached features were observed by the frozen base. Episode selection is the narrower reader-training exposure.",
            "Legacy training jobs without bank receipts, interrupted jobs and non-stream assays require further reconciliation.",
            "Development item/paraphrase traces identify executed supports; unrelated IDs are inferred from current script plus completion summary, not saved per-query traces.",
            "Exact-prompt mapping misses incidental entities, aliases and ordinary text. Unknown mappings are retained, not declared safe.",
            "Teacher-only eligibility and reservations do not by themselves establish reader execution.",
            "No subject is released and no cumulative supplement is modified.",
        ],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args(argv)
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT / "logs"):
        raise ValueError("new repository log required")
    result = build()
    write_json(a.output, result)
    print(
        json.dumps(
            {
                "counts": result["counts"],
                "sessions": len(result["sessions"]),
                "gaps": len(result["gaps"]),
                "supplement_review_candidates": len(
                    result["supplement_subjects_without_matched_evidence"]
                ),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
