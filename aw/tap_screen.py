"""CPU-only layer audit and small probes of existing development feature banks.

L1 is a diagnostic of fixed residual similarities, not an editing experiment.
The reader's historical held-out suffix alone is used; a new connected-component
subject/template split holds out probe evaluation families. No cache is built.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import pickle
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

import pccap  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
READ_SETS = {"123": (1, 2, 3), "23": (2, 3), "3": (3,), "2": (2,), "lexical": ()}


def sha(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def binding(path):
    return dict(path=str(Path(path).resolve()), sha256=sha(path))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n")


def stable(value):
    return int(hashlib.sha256(("AW-L1-v1:" + value).encode()).hexdigest()[:16], 16)


def group_split(rows):
    """Union subjects AND template families, then hash whole components."""
    from scripts.r1_d9e_near_family import near_key

    from pccap.metrics.editing import normalize_answer

    parent = list(range(len(rows)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    keys = {}
    metadata = []
    for i, row in enumerate(rows):
        subject = normalize_answer(row["subject"])
        family = near_key(row)
        if not subject or not family:
            raise ValueError("probe requires explicit subject and template family")
        metadata.append((subject, family))
        for key in [("subject", subject), ("family", family)]:
            if key in keys:
                parent[find(i)] = find(keys[key])
            else:
                keys[key] = i
    groups = {}
    for i, row in enumerate(rows):
        groups.setdefault(find(i), []).append(row["item_id"])
    labels = {
        i: ("test" if stable("|".join(sorted(groups[find(i)]))) % 10 < 3 else "train")
        for i in range(len(rows))
    }
    for pos in (0, 1):
        a = {metadata[i][pos] for i in labels if labels[i] == "train"}
        b = {metadata[i][pos] for i in labels if labels[i] == "test"}
        if a & b:
            raise AssertionError("subject/template leakage")
    return labels, dict(
        components=len(groups),
        train=sum(v == "train" for v in labels.values()),
        test=sum(v == "test" for v in labels.values()),
        subject_overlap=0,
        family_overlap=0,
    )


def normalized(last, span):
    parts = []
    for value in (last, span):
        part = np.asarray(value, np.float64)
        part = part - part.mean(axis=-1, keepdims=True)
        parts.append(part / np.sqrt(np.mean(part * part, axis=-1, keepdims=True) + 1e-5))
    x = np.concatenate(parts, axis=-1)
    return x / np.maximum(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12)


def make_episode(items):
    """Fixed half-memory; positives = paraphrases, nulls = locality/outside questions."""
    ordered = sorted(items, key=lambda item: stable(item.item_id))
    n = len(ordered) // 2
    if n < 2:
        raise ValueError("split too small for paired probe")
    memory = ordered[:n]
    queries = []
    prompts = {tuple(np.asarray(r.prompt_ids).tolist()) for r in memory}
    positive_inputs = set(prompts)
    for it in memory:
        for _, _, prefixes in it.paraphrases:
            p = prefixes[0]
            positive_inputs.add(tuple(np.asarray(p.ids)[: p.n].tolist()))
    for k, it in enumerate(memory):
        for j, (last, span, prefixes) in enumerate(it.paraphrases):
            p = prefixes[0]
            ids = np.asarray(p.ids)[: p.n]
            if tuple(ids.tolist()) in prompts:
                continue
            queries.append(
                dict(
                    id=f"{it.item_id}:para:{j}",
                    kind="paraphrase",
                    target=k,
                    last=last,
                    span=span,
                    ids=ids,
                )
            )
        for j, (last, span, p) in enumerate(it.locality):
            ids = np.asarray(p.ids)[: p.n]
            if tuple(ids.tolist()) in positive_inputs:
                continue
            queries.append(
                dict(
                    id=f"{it.item_id}:locality:{j}",
                    kind="locality",
                    target=-1,
                    last=last,
                    span=span,
                    ids=ids,
                )
            )
    for it in ordered[n:]:
        if tuple(np.asarray(it.prompt_ids).tolist()) not in positive_inputs:
            queries.append(
                dict(
                    id=f"{it.item_id}:outside",
                    kind="outside",
                    target=-1,
                    last=it.key_last,
                    span=it.key_span,
                    ids=it.prompt_ids,
                )
            )
        for j, (last, span, prefixes) in enumerate(it.paraphrases):
            p = prefixes[0]
            ids = np.asarray(p.ids)[: p.n]
            if tuple(ids.tolist()) not in positive_inputs:
                queries.append(
                    dict(
                        id=f"{it.item_id}:outside_para:{j}",
                        kind="outside_paraphrase",
                        target=-1,
                        last=last,
                        span=span,
                        ids=ids,
                    )
                )
    return memory, queries


def pair_features(memory, queries, stop_tokens):
    from pccap.revision_v1.reader import lex_feature

    keys = np.stack([normalized(r.key_last, r.key_span) for r in memory])
    result = []
    for q in queries:
        cos = np.einsum("kd,nkd->nk", normalized(q["last"], q["span"]), keys)
        lex = np.array([lex_feature(q["ids"], r.prompt_ids, stop_tokens) for r in memory])
        result.append(np.column_stack([cos, lex]))
    return np.stack(result)


def fit_probe(x, y, ridge=0.01):
    """Balanced logistic ridge, fixed 40 Newton steps; training statistics only."""
    mean = x.mean(0)
    scale = np.maximum(x.std(0), 1e-6)
    design = np.column_stack([np.ones(len(x)), (x - mean) / scale])
    y = np.asarray(y, float)
    if not (0 < y.sum() < len(y)):
        raise ValueError("both training classes required")
    weights = np.where(y > 0, 0.5 / y.sum(), 0.5 / (len(y) - y.sum()))
    penalty = np.eye(design.shape[1]) * ridge
    penalty[0, 0] = 0
    beta = np.zeros(design.shape[1])
    for _ in range(40):
        logits = np.clip(design @ beta, -35, 35)
        prob = 1 / (1 + np.exp(-logits))
        grad = design.T @ (weights * (prob - y)) + penalty @ beta
        hess = (
            (design.T * (weights * prob * (1 - prob))) @ design
            + penalty
            + np.eye(len(beta)) * 1e-10
        )
        change = np.linalg.solve(hess, grad)
        beta -= change
        if np.max(np.abs(change)) < 1e-9:
            break
    return dict(mean=mean, scale=scale, beta=beta)


def probe_scores(model, x):
    shape = x.shape[:-1]
    flat = x.reshape(-1, x.shape[-1])
    d = np.column_stack([np.ones(len(flat)), (flat - model["mean"]) / model["scale"]])
    return (d @ model["beta"]).reshape(shape)


def summarize_predictions(queries, scores):
    rows = []
    for q, s in zip(queries, scores, strict=True):
        best = int(np.argmax(s))
        fire = bool(s[best] >= 0)
        rows.append(
            dict(
                query_id=q["id"],
                kind=q["kind"],
                target=q["target"],
                best=best,
                fires=fire,
                forced_correct=q["target"] >= 0 and best == q["target"],
                retrieved=q["target"] >= 0 and best == q["target"] and fire,
                false_fire=q["target"] < 0 and fire,
                max_logit=float(s[best]),
            )
        )
    positive = [r for r in rows if r["target"] >= 0]
    null = [r for r in rows if r["target"] < 0]

    def mean(xs, key):
        return float(np.mean([r[key] for r in xs])) if xs else None

    summary = dict(
        positive_queries=len(positive),
        null_queries=len(null),
        forced_retrieval=mean(positive, "forced_correct"),
        gated_retrieval=mean(positive, "retrieved"),
        false_fire=mean(null, "false_fire"),
        null_by_role={},
    )
    for kind in sorted({r["kind"] for r in null}):
        subset = [r for r in null if r["kind"] == kind]
        summary["null_by_role"][kind] = dict(n=len(subset), false_fire=mean(subset, "false_fire"))
    # Pairwise query-level AUROC includes ties at one half; a diagnostic only.
    if positive and null:
        p = np.array([r["max_logit"] for r in positive])[:, None]
        n = np.array([r["max_logit"] for r in null])[None, :]
        summary["retrieval_vs_null_auc"] = float(np.mean((p > n) + 0.5 * (p == n)))
    return summary, rows


def screen():
    from scripts.r1_d9e_near_family import near_key

    from pccap.revision_v1.stream_train import bank_identity, verify_bank

    output = ROOT / "results/additional_work/L1"
    provenance = json.loads(
        (ROOT / "results/R1/pilot/r1_50_stream_sel6_text_s2/summary.json").read_text()
    )
    stop = json.loads((ROOT / "manifests/revision_v1/stop_tokens_v1.json").read_text())["tokens"]
    report = dict(
        task="AW-L1",
        producer=binding(__file__),
        gpu_seconds=0,
        model_calls=0,
        cache_builds=0,
        interpretation="development-only similarity probe; not editing quality or a layer selection rule",
        probe=dict(
            model="balanced logistic ridge",
            ridge=0.01,
            newton_steps=40,
            threshold_logit=0,
            features="per-tap cosine of independently layer-normalized last/span concatenation, plus fixed lexical overlap",
            secondary_diagnostic="tap-only probes added after initial lexical control matched all combined arms; exploratory, no selection",
            fold="connected subject/template components; fixed hash 70/30; held-out bank suffix only",
            memory="hash-ordered first half within each probe fold",
        ),
        datasets={},
    )
    for ds in ("zsre", "counterfact"):
        pool = ROOT / f"manifests/revision_v1/train_pool_{ds}_v1.json"
        bank_path = ASSETS / f"runs/pc_cap/R1/banks/train_pool_{ds}_v1_1000.pkl"
        bank_binding = binding(bank_path)
        with bank_path.open("rb") as handle:
            bank = pickle.load(handle)
        rows = json.loads(pool.read_text())["items"][:1000]
        source = next(b for b in provenance["banks"] if b["pool"] == str(pool.relative_to(ROOT)))
        verify_bank(bank, source["identity"])
        verify_bank(
            bank,
            bank_identity(
                rows, source["identity"]["base_checksum"], 1, (1, 2, 3), 2, 2, np.float16
            ),
        )
        if bank.content_hash() != source["sha256"]:
            raise ValueError("bank ordered tokens differ")
        if sha(bank_path) != bank_binding["sha256"]:
            raise ValueError("bank changed during read")
        # Historical dev suffix = last 100. Missing explicit family is excluded,
        # with IDs retained, never assigned a supposedly unique family silently.
        selected = [
            (it, row)
            for it, row in zip(bank.items[-100:], rows[-100:], strict=True)
            if near_key(row)
        ]
        omitted = [row["item_id"] for row in rows[-100:] if not near_key(row)]
        items = [it for it, _ in selected]
        devrows = [r for _, r in selected]
        if any(it.item_id != r["item_id"] for it, r in selected):
            raise ValueError("bank source row order changed")
        labels, split = group_split(devrows)
        norm = {}
        for field in ("key_last", "key_span"):
            a = np.stack([getattr(it, field) for it in items]).astype(float)
            norm[field] = {
                str(m): dict(
                    mean_norm=float(np.linalg.norm(a[:, m - 1], axis=-1).mean()),
                    norm_sd=float(np.linalg.norm(a[:, m - 1], axis=-1).std()),
                    mean_coordinate_variance=float(a[:, m - 1].var(axis=0).mean()),
                )
                for m in (1, 2, 3)
            }
        trainmem, trainq = make_episode([it for i, it in enumerate(items) if labels[i] == "train"])
        testmem, testq = make_episode([it for i, it in enumerate(items) if labels[i] == "test"])
        tx = pair_features(trainmem, trainq, stop)
        ex = pair_features(testmem, testq, stop)
        y = np.zeros(tx.shape[:2])
        for i, q in enumerate(trainq):
            if q["target"] >= 0:
                y[i, q["target"]] = 1
        models = {}
        summaries = {}
        details = {}
        arms = {name: [t - 1 for t in taps] + [3] for name, taps in READ_SETS.items()}
        arms.update(
            {name + "-no-lex": [t - 1 for t in taps] for name, taps in READ_SETS.items() if taps}
        )
        for name, columns in arms.items():
            model = fit_probe(tx[:, :, columns].reshape(-1, len(columns)), y.reshape(-1))
            summaries[name], details[name] = summarize_predictions(
                testq, probe_scores(model, ex[:, :, columns])
            )
            models[name] = {k: v.tolist() for k, v in model.items()}
        paired = {}
        for name in arms:
            if name == "123":
                continue
            pairs = list(zip(details["123"], details[name], strict=True))
            paired[name] = dict(
                retrieval_only_full=sum(a["retrieved"] and not b["retrieved"] for a, b in pairs),
                retrieval_only_arm=sum(b["retrieved"] and not a["retrieved"] for a, b in pairs),
                false_fire_only_full=sum(a["false_fire"] and not b["false_fire"] for a, b in pairs),
                false_fire_only_arm=sum(b["false_fire"] and not a["false_fire"] for a, b in pairs),
            )
        dataset = dict(
            bank=bank_binding,
            pool=binding(pool),
            bank_identity=bank.identity,
            split=split,
            excluded_missing_family=omitted,
            norms=norm,
            metrics=summaries,
            paired_against_123=paired,
            train_memory=len(trainmem),
            test_memory=len(testmem),
            train_queries=len(trainq),
            test_queries=len(testq),
        )
        save(
            output / f"{ds}-predictions.json",
            dict(
                models=models,
                arms=details,
                split_ids={
                    fold: [items[i].item_id for i in labels if labels[i] == fold]
                    for fold in ("train", "test")
                },
            ),
        )
        report["datasets"][ds] = dataset
        del bank, items, selected, trainmem, testmem, trainq, testq
        gc.collect()
    save(output / "screen.json", report)
    print(json.dumps({ds: v["metrics"] for ds, v in report["datasets"].items()}, indent=2))


def identity_audit():
    import jax
    from scripts.r1_61_cell_driver import construct_owner_adapter

    from aw.interface import InterfaceCap
    from pccap.harness.ledger import Ledger
    from pccap.harness.snapshot import restore

    recipe_path = ROOT / "docs/tasks/R1-post63l-active/R1-64e/R1-64e-zsre-primary-v5.recipe.json"
    recipe = json.loads(recipe_path.read_text())
    path = (
        ASSETS
        / "runs/pc_cap/R1/stage4_dev_cells/R1_learned_ff-zsre-development_full_endpoints_R164f-seed64028-c84c64b1149e74b70edb/attempt-0000/checkpoint-300.snapshot"
    )
    metadata = json.loads(path.with_suffix(".snapshot.json").read_text())
    if sha(path) != metadata["snapshot_sha256"]:
        raise ValueError("checkpoint bytes changed")
    state = restore(path.read_bytes(), expected_hash=metadata["state_sha256"])
    adapter, _ = construct_owner_adapter(recipe)
    if adapter.identity() != recipe["adapter_identity"]:
        raise ValueError("constructor identity differs")
    parent = adapter.learner
    cap = InterfaceCap(parent.base, parent.cfg, Ledger(), params=parent.params)
    parent.import_state(state)
    cap.import_state(state)
    payload_path = Path(recipe["payload"]["path"])
    if sha(payload_path) != recipe["payload"]["sha256"]:
        raise ValueError("development payload changed")
    payload = json.loads(payload_path.read_text())
    results = []
    start = time.monotonic()
    # Two prefixes for each of the first 32 development facts: prompt, then its
    # first taught token. Same query caches and exact returned-cost comparison.
    for row in payload["items"][:32]:
        p = np.asarray(row["prompt_ids"], np.int32)
        answer = np.asarray(row["answer_ids"], np.int32)
        for t, ids in enumerate((p, np.concatenate([p, answer[:1]]))):
            a = parent.predict(ids)
            b = cap.predict(ids)
            costs_a = asdict(a.cost)
            costs_b = asdict(b.cost)
            # Measured elapsed seconds differ between two real CPU executions.
            for key in ("accel_seconds", "wall_seconds"):
                costs_a.pop(key, None)
                costs_b.pop(key, None)
            equal = bool(np.array_equal(a.logits, b.logits))
            if not equal or costs_a != costs_b:
                raise AssertionError("all-site reconstruction differs")
            results.append(
                dict(
                    item_id=row["item_id"],
                    prefix=t,
                    exact_logits=equal,
                    max_abs_logit_difference=float(np.max(np.abs(a.logits - b.logits))),
                    cost_counts_equal=True,
                )
            )
        parent.reset_queries()
        cap.reset_queries()
        if len(results) % 16 == 0:
            print(f"L0 verified {len(results)}/64 prefixes", flush=True)
            jax.clear_caches()
    if parent.cost_counters != cap.cost_counters:
        raise AssertionError("cost counters differ")
    report = dict(
        task="AW-L0",
        producer=binding(__file__),
        implementation={
            name: binding(ROOT / name)
            for name in (
                "aw/interface.py",
                "src/pccap/revision_v1/learner.py",
                "src/pccap/revision_v1/adapt.py",
                "src/pccap/revision_v1/reader.py",
                "src/pccap/revision_v1/observations.py",
                "src/pccap/bases/gpt2_jax.py",
            )
        },
        recipe=binding(recipe_path),
        snapshot=binding(path),
        snapshot_metadata=binding(path.with_suffix(".snapshot.json")),
        payload=recipe["payload"],
        reader_checkpoint=recipe["construction"]["weights"],
        adapter_identity=adapter.identity(),
        semantic_config=json.loads(cap.semantic_config()),
        tap_blocks_zero_based=cap.blocks,
        tap_blocks_one_based={k: v + 1 for k, v in cap.blocks.items()},
        tap_convention="post-block residual, pre-write; bank 3 before ln_f; no normalization in ObservationEncoder",
        reader_normalization="layer-normalize last and span separately (eps 1e-5), concatenate, project per tap, sum projections, GELU, query/key MLP; L2 normalization for cosine scoring (eps 1e-8)",
        source_doc_discrepancy="observations.py docstring says entering; executable run_blocks records after block",
        single_site=cap.cfg.single_site,
        prediction_checks=results,
        exact_prefixes=len(results),
        cost_counters=cap.cost_counters,
        interface_accounting=cap.interface_accounting(),
        execution_device=str(jax.devices()),
        gpu_seconds=0,
        wall_seconds=time.monotonic() - start,
        checkpoint_state_unchanged=parent.state_hash() == cap.state_hash() == state.content_hash(),
    )
    save(ROOT / "results/additional_work/L0/identity.json", report)
    print(
        json.dumps(
            dict(
                exact_prefixes=len(results),
                cost_counters=cap.cost_counters,
                device=str(jax.devices()),
            )
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["screen", "identity"])
    args = parser.parse_args()
    (screen if args.command == "screen" else identity_audit)()


if __name__ == "__main__":
    main()
