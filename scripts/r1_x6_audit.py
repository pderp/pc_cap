"""R1-X6 CPU audit: pinned reference identities, repaired ledger and scale-risk reproduction."""

from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import subprocess
import time
from pathlib import Path

# Import determinism setup before JAX or helpers that import it.
# isort: off
import pccap  # noqa: F401
import numpy as np
from scripts.r1_13_stream_eval import load_theta
from scripts.r1_46_response_audit import run as repair_recheck
from scripts.r1_53_scale_profile import profile_memory

import jax
import jax.numpy as jnp
from pccap.harness.ledger import Ledger
from pccap.revision_v1.controller import ControllerConfig, init_controller
from pccap.revision_v1.episodes import synthetic_episode
from pccap.revision_v1.observations import ObservationEncoder
from pccap.revision_v1.reader import (
    ReaderConfig,
    applicability,
    init_reader,
    params_hash,
    query_embedding,
    record_key,
)
from pccap.revision_v1.train import LossConfig, featurize
from pccap.revision_v1.train_fast import FastTrainer, pack_episode
from tests.revision_v1.tiny_base import CFG, TinyBase
# isort: on

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def functions_for(rc):
    v_key = jax.jit(jax.vmap(lambda p, l, s: record_key(p, rc, l, s), in_axes=(None, 0, 0)))
    j_query = jax.jit(lambda p, l, s: query_embedding(p, rc, l, s))
    j_app = jax.jit(lambda p, q, keys, mask, lex: applicability(p, rc, q, keys, mask, lex))
    return v_key, j_query, j_app


def ledger_control():
    base = TinyBase()
    rc = ReaderConfig(d=CFG.d, width=8, hidden=8, d_code=6, top_k=2)
    cc = ControllerConfig(d=CFG.d, width=8, d_code=6, hidden=8, A=0.3, bank_scales=(1.0, 1.0, 1.0))
    features = featurize(base, ObservationEncoder(base, taps=rc.taps), synthetic_episode(7), rc)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = {"reader": init_reader(k1, rc), "controller": init_controller(k2, cc)}
    packed = pack_episode(features, CFG.vocab, rc)
    prefixes = sum(g["ids"].shape[0] for g in packed.groups)
    tokens = sum(int(np.asarray(g["n"]).sum()) for g in packed.groups)
    ledger = Ledger()
    trainer = FastTrainer(rc, cc, base.params, base.cfg, LossConfig(), ledger=ledger)
    gradients, metrics = trainer.episode_grads(theta, features)
    total = ledger.totals()["learning"]
    assert total["full_forwards"] == total["reverses"] == prefixes
    assert total["tokens"] == tokens
    assert all(np.all(np.isfinite(np.asarray(x))) for x in jax.tree_util.tree_leaves(gradients))
    return {
        "expected_prefix_forwards": prefixes,
        "expected_prefix_reverses": prefixes,
        "expected_forward_tokens": tokens,
        "ledger": total,
        "metrics": {k: float(v) for k, v in metrics.items()},
        "finite_gradients": True,
        "scope": "actual differentiated tiny-base episode; logical prefix accounting, not accelerator-time certification",
    }


def run():
    started = time.monotonic()
    sources = {}

    def bind(path, expected=None):
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        digest = sha(path)
        if expected and digest != expected:
            raise ValueError("source hash mismatch: " + str(path))
        sources[str(path)] = digest
        return path

    primary_path = bind("manifests/revision_v1/primary_condition_v1.json")
    primary = json.loads(primary_path.read_text())
    for ref in primary["weights"].values():
        bind(ref["path"], ref["sha256"])
    stop_path = bind(primary["stop_tokens"]["path"], primary["stop_tokens"]["sha256"])
    for name, digest in primary["pools"].items():
        bind("manifests/revision_v1/" + name + ".json", digest)
    for rel in (
        "scripts/r1_x6_audit.py",
        "scripts/r1_53_scale_profile.py",
        "scripts/r1_13_stream_eval.py",
        "scripts/r1_50_stream_train.py",
        "scripts/r1_52_operating_point.py",
        "src/pccap/revision_v1/reader.py",
        "src/pccap/revision_v1/memory.py",
        "src/pccap/revision_v1/learner.py",
        "src/pccap/revision_v1/stream_train.py",
        "src/pccap/revision_v1/train_fast.py",
        "docs/decisions.md",
        "manifests/revision_v1/r1_24_budget_reconciliation_v1.json",
    ):
        bind(rel)
    saved = json.loads(bind("results/R1/scale_profile_r1_50_stream_mixed.json").read_text())
    additional = {}
    for path in sorted((ROOT / "results/R1").glob("scale_profile_*.json")):
        if path.name == "scale_profile_r1_50_stream_mixed.json":
            continue
        additional[path.name] = json.loads(bind(path).read_text())
    stop = tuple(json.loads(stop_path.read_text())["tokens"])
    rc = ReaderConfig(lexical=True, stop_tokens=stop, top_k=4)
    k1, k2 = jax.random.split(jax.random.PRNGKey(0))
    theta = load_theta(
        Path(primary["weights"]["seed0"]["path"]),
        {"reader": init_reader(k1, rc), "controller": init_controller(k2, ControllerConfig())},
    )
    v_key, j_query, j_app = functions_for(rc)
    rng = np.random.default_rng(0)
    profiles, population, differences = {}, {}, []
    for dataset in ("counterfact", "zsre"):
        path = bind(
            ROOT.parent / "assets/runs/pc_cap/R1/banks" / f"train_pool_{dataset}_v1_1000.pkl"
        )
        bank = pickle.loads(path.read_bytes())
        items = bank.items
        keys = np.asarray(
            v_key(
                theta["reader"],
                jnp.asarray(np.stack([it.key_last for it in items])),
                jnp.asarray(np.stack([it.key_span for it in items])),
            )
        )
        profiles[dataset], population[dataset] = {}, {}
        for size in (64, 100, 300, 1000):
            perm = rng.permutation(len(items))
            mem = perm[:size]
            queries = rng.permutation(mem)[:200]
            outs = perm[size : size + 200]
            measured = profile_memory(
                items, keys, mem, queries, outs, rc, theta, stop, j_query, j_app, 0.5
            )
            profiles[dataset][str(size)] = measured
            population[dataset][str(size)] = {
                "memory_n": len(mem),
                "own_queries_n": len(queries),
                "paraphrase_queries_n": sum(bool(items[int(i)].paraphrases) for i in queries),
                "locality_queries_n": sum(bool(items[int(i)].locality) for i in queries),
                "outside_queries_n": len(outs),
                "memory_item_ids": [items[int(i)].item_id for i in mem],
                "queried_item_ids": [items[int(i)].item_id for i in queries],
                "outside_item_ids": [items[int(i)].item_id for i in outs],
            }
            for metric, value in measured.items():
                original = saved["profile"][dataset][str(size)][metric]
                difference = None if value is None or original is None else abs(value - original)
                if (value is None) != (original is None) or (
                    difference is not None and difference > 1e-5
                ):
                    differences.append(
                        {
                            "dataset": dataset,
                            "memory": size,
                            "metric": metric,
                            "saved": original,
                            "cpu": value,
                            "absolute_difference": difference,
                        }
                    )
            print(
                json.dumps(
                    {
                        "dataset": dataset,
                        "memory": size,
                        "para_fires_own": measured["para_top1_fires"],
                        "para_in_topk": measured["para_in_topk"],
                        "outside_hard_null": measured["out_hard_null_rate"],
                        "outside_n": len(outs),
                    }
                ),
                flush=True,
            )
        del bank, items, keys
    cf, zs = profiles["counterfact"], profiles["zsre"]
    risks = {
        "counterfact_selection_scale_loss_reproduced": cf["1000"]["para_top1_fires"]
        < cf["100"]["para_top1_fires"],
        "zsre_outside_rejection_scale_loss_reproduced": zs["300"]["out_hard_null_rate"]
        < zs["100"]["out_hard_null_rate"],
        "counterfact_1000_fires_own": cf["1000"]["para_top1_fires"],
        "counterfact_1000_candidate_recall": cf["1000"]["para_in_topk"],
        "zsre_outside_hard_null_at_100": zs["100"]["out_hard_null_rate"],
        "zsre_outside_hard_null_at_300": zs["300"]["out_hard_null_rate"],
        "outside_at_1000_is_unavailable_not_perfect": zs["1000"]["out_hard_null_rate"] is None,
    }
    assert all(
        risks[k]
        for k in (
            "counterfact_selection_scale_loss_reproduced",
            "zsre_outside_rejection_scale_loss_reproduced",
            "outside_at_1000_is_unavailable_not_perfect",
        )
    )
    repairs = repair_recheck()
    sources.update(repairs["sources_sha256"])
    ledger = ledger_control()
    budget_path = ROOT / "manifests/revision_v1/r1_24_budget_reconciliation_v1.json"
    budget = json.loads(budget_path.read_text())
    for path, expected in budget["pilot_sources_sha256"].items():
        summary = json.loads(bind(path, expected).read_text())
    banks = summary["banks"]
    bank_tokens = sum(b["construction_cost"]["tokens"] for b in banks)
    outer_tokens = summary["ledger"]["learning"]["tokens"]
    budget_check = {
        "bank_tokens": bank_tokens,
        "outer_tokens": outer_tokens,
        "forward_pass_tokens": bank_tokens + outer_tokens,
        "reconciliation_forward_tokens": budget["training_forward_pass_tokens"],
        "matches": bank_tokens + outer_tokens == budget["training_forward_pass_tokens"],
        "ledger_run_theta_hash": summary["theta_hash"],
        "reference_theta_hash": params_hash(theta),
        "same_checkpoint": summary["theta_hash"] == params_hash(theta),
        "scope": "rerun accounting, not retroactive original-run costs; forward/reverse token conventions separate",
    }
    assert budget_check["matches"]
    for path, expected in sources.items():
        if sha(path) != expected:
            raise RuntimeError("source changed during audit: " + path)
    return {
        "task": "R1-X6",
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "sources_sha256": sources,
        "reference_hash_bindings_verified": True,
        "reader_config": {**rc.__dict__, "stop_tokens": "bound by manifest SHA-256"},
        "reference_theta_hash": params_hash(theta),
        "profile": profiles,
        "population": population,
        "saved_profile_differences_gt_1e_minus5": differences,
        "risks": risks,
        "other_saved_profiles_reviewed": additional,
        "repair_recheck": repairs,
        "tiny_ledger_control": ledger,
        "budget_reconciliation": budget_check,
        "jax_platforms": sorted({d.platform for d in jax.devices()}),
        "gpu_seconds": 0,
        "real_base_queries": 0,
        "wall_seconds": time.monotonic() - started,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or not args.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    result = run()
    with args.output.open("x") as f:
        f.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "risks": result["risks"],
                "ledger": result["budget_reconciliation"],
                "wall_seconds": result["wall_seconds"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
