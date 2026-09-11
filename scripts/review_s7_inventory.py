#!/usr/bin/env python3
"""Lane X: subject-only inventory audit and two synthetic S7 metric counterexamples."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

os.environ.update(CUDA_VISIBLE_DEVICES="", JAX_PLATFORMS="cpu")
sys.dont_write_bytecode = True

import pccap  # noqa: E402

# isort: split
import numpy as np  # noqa: E402
from tests.cap.mock_base import make_item  # noqa: E402

from pccap.analysis import s7_01  # noqa: E402
from pccap.contracts import Budget  # noqa: E402
from pccap.metrics.editing import normalize_answer as norm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "logs/p4_s7_review"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pool_subject_projection(path):
    """Decode only each subject JSON string; do not deserialize any item payload."""
    pattern = re.compile(r'"subject"\s*:\s*("(?:\\.|[^"\\])*")')
    subjects = set()
    digest = hashlib.sha256()
    n = 0
    with path.open("rb") as f:
        for line in f:
            digest.update(line)
            if not line.strip():
                continue
            matches = list(pattern.finditer(line.decode()))
            assert len(matches) == 1, "subject-only projection is ambiguous"
            subjects.add(norm(json.loads(matches[0].group(1))))
            n += 1
    return subjects, {"rows": n, "unique_subjects": len(subjects), "source_sha256": digest.hexdigest(), "subject_set_sha256": hashlib.sha256(json.dumps(sorted(subjects)).encode()).hexdigest()}


class TinyState:
    def __init__(self, bias=0.0):
        self.bias = bias

    def clone(self):
        return TinyState(self.bias)


class ParaphraseOnlyLearner:
    """Updates affect only prefix 3 (i's paraphrase), never its prefix 1."""
    def __init__(self):
        self.state = TinyState()

    def import_state(self, state):
        self.state = state.clone()

    def state_hash(self):
        return repr(self.state.bias)

    def predict(self, ids):
        bias = self.state.bias if int(ids[0]) == 3 else 0.0
        return SimpleNamespace(logits=np.tile([bias, 0.0], (len(ids), 1)))

    def update_item(self, item):
        self.state.bias = 4.0 if item.item_id == "i" else -4.0
        return SimpleNamespace(code="accepted", rounds_used=1)


class BoundarySpy:
    decode_key_positions = True

    def __init__(self):
        self.calls = []

    def last_logits_batch(self, seqs, phase="query", key_positions=None):
        self.calls.append({"lengths": [len(s) for s in seqs], "key_positions": key_positions})
        return np.tile([2.0, 0.0], (len(seqs), 1))


def main():
    OUT.mkdir(exist_ok=True)
    inventory = ROOT / "manifests/dev/s7_pairs.json"
    selected = ROOT / "manifests/dev/s7_pairs_e2.json"
    watched = [inventory, selected, Path(s7_01.__file__), ROOT / "docs/pc_cap_month_plan_readable.pdf"]
    before = {str(p.relative_to(ROOT)): sha(p) for p in watched}
    man, e2 = json.loads(inventory.read_text()), json.loads(selected.read_text())
    pair_hash = hashlib.sha256(json.dumps(man["pairs"], sort_keys=True).encode()).hexdigest()
    assert pair_hash == man["sha256_pairs"] == e2["inventory_sha256_pairs"]
    pools = json.loads((ROOT / "manifests/dev/pools.json").read_text())
    forbidden, pool_evidence, dev_subjects = set(), {}, {}
    pool_sets = {}
    for ds in ("zsre", "counterfact"):
        subjects, info = pool_subject_projection(Path(pccap.ASSETS_ROOT) / "data/prepared/editing" / (ds + "_eligible.jsonl"))
        assert info["source_sha256"] == pools[ds]["confirm_pool_sha256"]
        forbidden.update(subjects)
        pool_sets[ds] = subjects
        pool_evidence[ds] = info
        dev = json.loads((ROOT / "manifests/dev" / (ds + "_dev.json")).read_text())
        dev_subjects[ds] = {norm(r["subject"]) for r in dev["items"]}
        forbidden.update(dev_subjects[ds])
    s0 = {norm(r["subject"]) for r in json.loads((ROOT / "manifests/dev/s0_sample.json").read_text())["items"]}
    forbidden.update(s0)
    report = {"inventory_sha256_pairs": pair_hash, "pool_subject_projection": pool_evidence, "sealed_realization_files_opened": 0, "datasets": {}, "source_before": before}
    for ds in ("zsre", "counterfact"):
        pairs = man["pairs"][ds]
        members = [p[m] for p in pairs for m in ("a", "b")]
        subjects = {norm(m["subject"]) for m in members}
        violations = []
        for p in pairs:
            a, b = p["a"], p["b"]
            same_subject = norm(a["subject"]) == norm(b["subject"])
            relation = "template" if ds == "zsre" else "relation_id"
            same_relation = a[relation] == b[relation]
            ok = norm(a["answer"]) != norm(b["answer"])
            ok &= (same_subject and not same_relation) if p["stratum"] == "shared" else ((not same_subject and same_relation) if p["stratum"] == "near_neighbour" else (not same_subject and not same_relation))
            if not ok:
                violations.append(p["pair_id"])
        report["datasets"][ds] = {
            "pairs": len(pairs), "members": len(members), "unique_item_ids": len({m["item_id"] for m in members}),
            "unique_subjects": len(subjects), "overlap_with_sealed_source_subjects": len(subjects & pool_sets[ds]),
            "overlap_with_all_reserved_subjects": len(subjects & forbidden),
            "outside_counterfact_development_subjects": len(subjects - dev_subjects["counterfact"]) if ds == "counterfact" else None,
            "syntactic_stratum_violations": violations,
            "minimum_paraphrases": min(len(m.get("paraphrases", [])) for m in members),
            "minimum_locality_controls": min(len(m.get("locality_prompts", [])) for m in members),
        }
        assert not violations
        assert len({m["item_id"] for m in members}) == len(members)
        if ds == "zsre":
            assert not subjects & forbidden
        else:
            assert not subjects & pool_sets["counterfact"]
            assert not subjects - dev_subjects["counterfact"]
    selection_checks = {}
    for ds, pairs in man["pairs"].items():
        for st in s7_01.STRATA:
            eligible = []
            for pair in pairs:
                if pair["stratum"] != st:
                    continue
                if ds == "grammar":
                    ok = True
                elif s7_01.NEEDS_FILTER[(ds, st)]:
                    ok = all(e2["evidence"][ds][pair[m]["item_id"]]["passes"] for m in ("a", "b"))
                else:
                    ok = all(not e2["evidence"][ds][pair[m]["item_id"]]["excluded"] for m in ("a", "b"))
                if ok:
                    eligible.append(pair["pair_id"])
            expected = eligible[:s7_01.TARGET[st]]
            assert expected == e2["selection"][ds][st]
            selection_checks[ds + "/" + st] = {"selected": len(expected), "target": s7_01.TARGET[st], "first_eligible_order_matches": True}
    report["selection_checks"] = selection_checks
    grammar = [p[m] for p in man["pairs"]["grammar"] for m in ("a", "b")]
    seeds = [r["grammar"]["seed"] for r in grammar]
    assert min(seeds) >= 900_000 and len(seeds) == len(set(seeds))
    syntactic = []
    for pair in man["pairs"]["grammar"]:
        a, b = pair["a"]["grammar"], pair["b"]["grammar"]
        if pair["stratum"] == "shared":
            ok = a["kind"] == b["kind"] == "shared_1" and a["context"] != b["context"]
        elif pair["stratum"] == "private":
            ok = a["kind"] == b["kind"] == "private" and a["context"] != b["context"]
        else:
            ok = a["kind"] == b["kind"] == "private" and a["context"] == b["context"]
        if not ok:
            syntactic.append(pair["pair_id"])
    # Published P4 sampled private kinds with this exact (seed, context) schedule.
    overlap_p4 = [r["item_id"] for r in grammar if r["grammar"]["kind"] == "private" and 1_000_000 <= r["grammar"]["seed"] < 1_008_192 and r["grammar"]["context"] == (r["grammar"]["seed"]-1_000_000) % 8]
    report["grammar"] = {"members": len(grammar), "min_seed": min(seeds), "max_seed": max(seeds), "disjoint_from_DATA06_train_eval_heldout": min(seeds) > 746_000, "syntactic_stratum_violations": syntactic, "exact_schedule_overlap_with_published_P4": overlap_p4}
    assert not syntactic

    i, j = make_item("i", prompt=(1,), answer=(0,)), make_item("j", prompt=(2,), answer=(0,))
    q_i = [i.prompt_ids, np.array([3], np.int32)]
    Q = {"Q_i": q_i, "Q_j": [j.prompt_ids], "controls": [np.array([4], np.int32)]}
    result = s7_01.reversal(ParaphraseOnlyLearner, TinyState(), i, j, Q, None, Budget())
    direct = ParaphraseOnlyLearner()
    direct.update_item(i)
    mid = [s7_01.item_loss(direct, replace(i, prompt_ids=q)) for q in q_i]
    direct.update_item(j)
    end = [s7_01.item_loss(direct, replace(i, prompt_ids=q)) for q in q_i]
    expected = float(np.mean(np.array(end) - mid))
    report["damage_counterexample"] = {"reported_I_ij": result["I_ij"], "mean_over_declared_Q_i": expected, "per_prefix_loss_after_i": mid, "per_prefix_loss_after_ij": end, "n_Q": result["n_Q"], "D_ij": result["D_ij"]["value"], "demonstrated_mismatch": abs(result["I_ij"]-expected) > 1e-12}
    spy = BoundarySpy()
    two_token = make_item("boundary", prompt=(1, 2), answer=(0, 0))
    s7_01.item_loss(spy, two_token)
    s7_01.item_exact(spy, two_token)
    report["grace_boundary_control"] = {"calls": spy.calls, "expected_original_prompt_key_position": 1, "all_calls_omit_boundaries": all(c["key_positions"] is None for c in spy.calls)}
    report["source_after"] = {str(p.relative_to(ROOT)): sha(p) for p in watched}
    assert before == report["source_after"], "S7 source/inventory changed during audit"
    with (OUT / "s7_audit.json").open("x") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
