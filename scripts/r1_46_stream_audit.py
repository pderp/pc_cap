"""R1-46 read-only stream-builder review evidence; synthetic CPU cases and local bank metadata."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pickle
from collections import Counter
from pathlib import Path

import numpy as np

import pccap  # noqa: F401
from pccap.revision_v1.reader import ReaderConfig
from pccap.revision_v1.stream_train import (
    FeatureBank,
    ItemFeatures,
    merge_banks,
    stream_episode,
    stream_episode_mixed,
)
from pccap.revision_v1.train import PrefixFeat
from pccap.revision_v1.train_fast import pack_episode

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def fixture_bank(n=20, prefix="a"):
    items = []
    for i in range(n):
        last = np.full((3, 2), i, np.float32)
        span = last + 0.1
        ids = np.int32([1, 2, i + 3])
        para = np.int32([2, 1, i + 3])
        loc = np.int32([40, 41, i + 3])

        def pf(tokens, target, kl=False, last=last, span=span):
            return PrefixFeat(
                ids=tokens,
                n=len(tokens),
                target=target,
                last=last.copy(),
                span=span.copy(),
                capoff_logits=np.zeros(256, np.float16) if kl else None,
            )

        items.append(
            ItemFeatures(
                item_id=f"{prefix}{i}",
                fact_id=f"{prefix}fact{i}",
                key_last=last,
                key_span=span,
                code_last=last + 1,
                code_span=span + 1,
                prompt_ids=ids,
                answer_ids=np.int32([99, 198]),
                own=[pf(ids, 99), pf(np.concatenate([ids, np.int32([99])]), 198)],
                paraphrases=[
                    (
                        last + 0.2,
                        span + 0.2,
                        [pf(para, 99), pf(np.concatenate([para, np.int32([99])]), 198)],
                    )
                ],
                locality=[(last + 0.3, span + 0.3, pf(loc, -1, True))],
                subject=f"{prefix}subject{i}",
            )
        )
    return FeatureBank(items=items, dataset=prefix)


def controls():
    bank = fixture_bank()
    ep = stream_episode(bank, np.random.default_rng(0), n_memory=8, n_query_records=3, n_out=2)
    roles = Counter(q.role for q in ep.queries)
    assert roles == {"own_prompt": 3, "new_paraphrase": 3, "unrelated": 3, "unrelated_no_kl": 2}
    mem = {s.record_id for s in ep.supports}
    assert all(
        q.query_id.split(":", 1)[1] not in mem for q in ep.queries if q.role == "unrelated_no_kl"
    )
    rc = ReaderConfig(d=2, width=4, hidden=4, d_code=2, lexical=True)
    packed = pack_episode(ep, 256, rc)
    edited = copy.deepcopy(ep)
    for q in edited.queries:
        q.target_record = 0
        for pf in q.prefixes:
            pf.target = 123
    relabelled = pack_episode(edited, 256, rc)
    invariant = ("sup_last", "sup_span", "code_last", "code_span", "q_last", "q_span", "lex")
    assert all(np.array_equal(getattr(packed, k), getattr(relabelled, k)) for k in invariant)
    assert not np.array_equal(packed.q_target, relabelled.q_target)
    assert all(np.array_equal(a["ids"], b["ids"]) for a, b in zip(packed.groups, relabelled.groups))
    shortage = stream_episode(
        bank, np.random.default_rng(0), n_memory=20, n_query_records=3, n_out=8
    )
    zero_out = sum(q.role == "unrelated_no_kl" for q in shortage.queries)
    assert zero_out == 0
    repeated = stream_episode(
        bank,
        np.random.default_rng(0),
        n_memory=4,
        n_query_records=1,
        n_out=0,
        pool_indices=[0, 0, 0, 0],
    )
    duplicate_supports = [s.record_id for s in repeated.supports]
    assert len(set(duplicate_supports)) == 1
    merged = merge_banks([fixture_bank(4), fixture_bank(4)])
    assert len(merged.items) == 8 and len(merged.by_id()) == 4
    two = merge_banks([fixture_bank(100, "a"), fixture_bank(100, "b")])
    rounded = stream_episode_mixed(
        [list(range(100)), list(range(100, 200))],
        two,
        np.random.default_rng(0),
        n_memory=5,
        n_query_records=1,
        n_out=0,
    )
    assert len(rounded.supports) == 4
    missing_domains = []
    for seed in range(512):
        e = stream_episode_mixed(
            [list(range(100)), list(range(100, 200))],
            two,
            np.random.default_rng(seed),
            n_memory=64,
            n_query_records=8,
            n_out=8,
        )
        domains = {q.query_id.split(":", 1)[1][0] for q in e.queries if q.role == "own_prompt"}
        if len(domains) < 2:
            missing_domains.append(seed)
    alias_bank = fixture_bank()
    for item in alias_bank.items:
        item.fact_id = "same_fact"
    alias_ep = stream_episode(
        alias_bank, np.random.default_rng(0), n_memory=8, n_query_records=3, n_out=2
    )
    assert any(q.role == "unrelated_no_kl" for q in alias_ep.queries)
    # Invalid per-pool split arithmetic copied from the driver; negative indices are valid Python indexing.
    n_b, held_out = 4, 6
    dev_indices = list(range(n_b - held_out, n_b))
    assert dev_indices[0] < 0
    return {
        "label_reassignment": {
            "reader_inputs_unchanged": list(invariant),
            "reader_token_prefixes_unchanged": True,
            "training_targets_changed": True,
            "scope": "actual stream_episode + pack_episode on controlled features; no claim of end-to-end base feature recomputation",
        },
        "normal_populations": dict(roles),
        "binary_class_weights": {
            "record_count": 6,
            "null_count": 5,
            "record_total_weight": 0.5,
            "null_total_weight": 0.5,
            "null_role_weights": {"locality": 0.5 * 3 / 5, "out_of_memory": 0.5 * 2 / 5},
            "formula_source": "train_fast._make_fns.retrieval",
        },
        "undersized_pool": {"requested_out": 8, "actual_out": zero_out, "refused": False},
        "duplicate_pool_indices": {"support_ids": duplicate_supports, "refused": False},
        "duplicate_merged_ids": {
            "items": len(merged.items),
            "by_id_entries": len(merged.by_id()),
            "refused": False,
        },
        "mixed_rounding": {
            "requested_memory": 5,
            "actual_memory": len(rounded.supports),
            "equal_pools": True,
            "refused": False,
        },
        "mixed_query_domain_coverage": {
            "episodes": 512,
            "own_prompt_queries_per_episode": 8,
            "episodes_missing_a_domain": len(missing_domains),
            "example_seeds": missing_domains[:10],
        },
        "out_of_memory_fact_identity": {
            "out_queries_labelled_null": 2,
            "same_fact_id_in_memory": True,
            "refused": False,
        },
        "invalid_heldout_split": {
            "pool_items": n_b,
            "heldout": held_out,
            "dev_indices": dev_indices,
            "negative_indices_admitted_by_current_slice_formula": True,
        },
    }


def audit_banks(sources):
    reports = {}
    for ds in ("counterfact", "zsre"):
        pool = ROOT / f"manifests/revision_v1/train_pool_{ds}_v1.json"
        path = ROOT.parent / f"assets/runs/pc_cap/R1/banks/train_pool_{ds}_v1_1000.pkl"
        if not pool.exists() or not path.exists():
            reports[ds] = {"status": "not_available"}
            continue
        sources[str(pool)] = sha(pool)
        sources[str(path)] = sha(path)
        rows = json.loads(pool.read_text())["items"]
        bank = pickle.loads(path.read_bytes())
        lookup = {r["item_id"]: r for r in rows}
        missing = [it.item_id for it in bank.items if it.item_id not in lookup]
        report = {
            "status": "inspected",
            "pool_items": len(rows),
            "bank_items": len(bank.items),
            "bank_fields": sorted(vars(bank)),
            "same_ordered_first_1000_ids": [it.item_id for it in bank.items]
            == [r["item_id"] for r in rows[:1000]],
            "missing_pool_ids": missing,
            "answer_array_mismatches": sum(
                list(it.answer_ids) != lookup[it.item_id]["answer_ids"]
                for it in bank.items
                if it.item_id in lookup
            ),
            "prompt_array_mismatches": sum(
                list(it.prompt_ids) != lookup[it.item_id]["prompt_ids"]
                for it in bank.items
                if it.item_id in lookup
            ),
            "bank_answer_length_histogram": dict(Counter(len(it.answer_ids) for it in bank.items)),
            "pool_answer_length_histogram": dict(Counter(len(r["answer_ids"]) for r in rows)),
            "train_subjects": sorted({it.subject for it in bank.items[:-100]}),
            "dev_subjects": sorted({it.subject for it in bank.items[-100:]}),
            "internal_train_dev_subject_overlap": sorted(
                {it.subject for it in bank.items[:-100]} & {it.subject for it in bank.items[-100:]}
            ),
            "serialized_cost": bank.cost.as_dict(),
            "cache_has_source_or_encoder_binding": False,
        }
        reports[ds] = report
    if all(
        ds in reports and reports[ds]["status"] == "inspected" for ds in ("counterfact", "zsre")
    ):
        reports["cross_domain_primary_subject_overlap"] = sorted(
            (
                set(reports["counterfact"]["train_subjects"])
                | set(reports["counterfact"]["dev_subjects"])
            )
            & (set(reports["zsre"]["train_subjects"]) | set(reports["zsre"]["dev_subjects"]))
        )
    return reports


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    paths = [
        ROOT / rel
        for rel in (
            "src/pccap/revision_v1/stream_train.py",
            "src/pccap/revision_v1/train.py",
            "src/pccap/revision_v1/train_fast.py",
            "src/pccap/revision_v1/reader.py",
            "src/pccap/revision_v1/learner.py",
            "src/pccap/revision_v1/memory.py",
            "scripts/r1_50_stream_train.py",
            "scripts/r1_52_operating_point.py",
            "scripts/r1_13_stream_eval.py",
            "src/pccap/data/tokenize.py",
        )
    ]
    paths.append(Path(__file__).resolve())
    sources = {str(p): sha(p) for p in paths}
    result = {
        "task": "R1-46",
        "controls": controls(),
        "banks": audit_banks(sources),
        "sources_sha256": sources,
        "gpu_seconds": 0,
        "real_base_queries": 0,
        "code_edits": False,
    }
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("review source changed: " + path)
    with args.output.open("x") as f:
        json.dump(result, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps(result["controls"], indent=2))


if __name__ == "__main__":
    main()
