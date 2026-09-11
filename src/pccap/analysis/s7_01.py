"""S7-01/02: cloned-state pair reversals and the damage matrix (plan §6.13 S7-01/02; PDF S7, D.9).

At an immutable checkpoint state ``s`` (a committed S4/S5 learner checkpoint, or any exported state on
CPU) clone the complete state and run ``U_j(U_i(s))`` and ``U_i(U_j(s))`` under the item-update protocol
(``pccap.cap.learn.update_item``; the router's randomness is keyed on the item digest, so only the order
changes). Report

* ``D_ij = |Q|⁻¹ Σ_{x∈Q} JS(p(x; s_ij), p(x; s_ji))`` with Q = both edits' fixed evaluation prefixes
  (prompt and paraphrases) and unrelated controls (their locality prompts); natural logs, JS ∈ [0, log 2];
* per-item accuracy changes (teacher-forced NLL and exact-match on the greedy answer, before/after in
  each order), update counts (rounds), allocations and evictions (from the decision records);
* the damage matrix ``I_ij = E_{x∈Q_i}[L_x(U_j(U_i(s))) − L_x(U_i(s))]`` in both orders, with strata.

The pair inventory (``manifests/dev/s7_pairs.json``, ``--build``) is fixed before any result: 100 pairs
per checkpoint dataset, stratified shared / private / near-neighbour, drawn from data independent of
every S4 stream (zsRE MEND *train* records whose subjects are in no pool; the CounterFact development
pool and the raw records that share a reserved development subject; fresh grammar seeds). Editing pairs
are over-sampled 3× in a fixed order because the E.2 teacher filter (edit only what the teacher does not
already answer) needs the GPU: the rule is "the first n pairs per stratum, in manifest order, whose four
members pass the E.2 filter". Strata short of their target are reported short, never back-filled from
another stratum or from sealed confirmation pools.

    python -m pccap.analysis.s7_01 --build            # write the inventory (CPU)
    python -m pccap.analysis.s7_01 --checkpoint PATH --dataset zsre --arm C2   # GPU, later (S7-01/02 run)
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import time
from pathlib import Path

import numpy as np

from pccap.contracts import Budget, EditItem, metric
from pccap.metrics.divergence import js
from pccap.metrics.editing import normalize_answer

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "manifests" / "dev" / "s7_pairs.json"
STRATA = ("shared", "private", "near_neighbour")
TARGET = {"shared": 34, "private": 33, "near_neighbour": 33}  # 100 pairs per checkpoint dataset
OVERSAMPLE = 3
# strata whose members still need the E.2 teacher filter on the GPU are over-sampled OVERSAMPLE×; CounterFact development
# items were teacher-selected by DATA-01 and grammar items need no filter (the base knows no task mechanism by construction)
NEEDS_FILTER = {("zsre", "shared"): True, ("zsre", "private"): True, ("zsre", "near_neighbour"): True,
                ("counterfact", "shared"): True, ("counterfact", "private"): False, ("counterfact", "near_neighbour"): False,
                ("grammar", "shared"): False, ("grammar", "private"): False, ("grammar", "near_neighbour"): False}
SEED = 71
GRAMMAR_SEED_BASE = 900_000  # disjoint from DATA-06 train/eval/held-out seed blocks
GRAMMAR_STRIDE = 20_000


# ----------------------------------------------------------------------------- inventory
def _digest_hex(item_id: str, prompt: str, answer: str) -> str:
    return hashlib.sha256(f"{item_id}|{prompt}|{answer}".encode()).hexdigest()[:32]


def _pool_subjects() -> set[str]:
    """Every subject in a development pool, the S0 sample or a sealed confirmation source pool."""
    from pccap import ASSETS_ROOT

    subs: set[str] = set()
    for ds in ("zsre", "counterfact"):
        p = Path(ASSETS_ROOT) / "data" / "prepared" / "editing" / f"{ds}_eligible.jsonl"
        for line in p.read_text().splitlines():
            if line.strip():
                subs.add(normalize_answer(json.loads(line)["subject"]))
        for it in json.loads((ROOT / "manifests" / "dev" / f"{ds}_dev.json").read_text())["items"]:
            subs.add(normalize_answer(it["subject"]))
    for it in json.loads((ROOT / "manifests" / "dev" / "s0_sample.json").read_text())["items"]:
        subs.add(normalize_answer(it["subject"]))
    return subs


def _zsre_train_records(pool: set[str]) -> list[dict]:
    from pccap.data.splits import load_zsre

    out, seen = [], set()
    for i, r in enumerate(load_zsre("train")):
        subj = normalize_answer(r.get("subject", ""))
        answers = [a for a in r.get("answers", []) if a and a.strip()]
        if not subj or subj in pool or not answers or r["subject"] not in r["src"] or not r.get("rephrase"):
            continue
        key = (subj, r["src"])
        if key in seen:
            continue
        seen.add(key)
        it = {"item_id": f"zsre-train-{i}", "dataset": "zsre", "prompt": r["src"], "answer": answers[0],
              "aliases": sorted({normalize_answer(a) for a in answers}), "paraphrases": [r["rephrase"]],
              "locality_prompts": [r["loc"]] if r.get("loc") else [], "locality_answers": [r["loc_ans"]] if r.get("loc_ans") else [],
              "subject": r["subject"], "fact_id": f"zsre-train-{i}", "template": r["src"].replace(r["subject"], "{}"),
              "source": "zsre_mend_train.json (independent of every pool: subject in no development, S0 or sealed pool)"}
        it["digest"] = _digest_hex(it["item_id"], it["prompt"], it["answer"])
        out.append(it)
    return out


def _counterfact_records(pool_eligible: set[str]) -> tuple[list[dict], list[dict]]:
    """Development-pool items and the raw records sharing a reserved development subject (not in the sealed pool)."""
    from pccap.data.splits import counterfact_item, load_counterfact

    dev = json.loads((ROOT / "manifests" / "dev" / "counterfact_dev.json").read_text())["items"]
    dev_subj = {normalize_answer(it["subject"]) for it in dev}
    dev_ids = {it["item_id"] for it in dev}
    sibs = []
    for r in load_counterfact():
        s = normalize_answer(r["requested_rewrite"]["subject"])
        if s in dev_subj and s not in pool_eligible and f"cf-{r['case_id']}" not in dev_ids:
            it = counterfact_item(r)
            it["digest"] = _digest_hex(it["item_id"], it["prompt"], it["answer"])
            it["source"] = "counterfact.json raw record sharing a reserved development subject (excluded from the sealed pool by DATA-01)"
            sibs.append(it)
    for it in dev:
        it.setdefault("source", "counterfact development pool (manifests/dev/counterfact_dev.json)")
    return dev, sibs


def _slim(it: dict) -> dict:
    keep = ("item_id", "dataset", "prompt", "answer", "aliases", "paraphrases", "locality_prompts", "locality_answers", "subject",
            "fact_id", "relation_id", "template", "digest", "source", "grammar")
    return {k: it[k] for k in keep if k in it}


def _pair(pid: str, stratum: str, dataset: str, a: dict, b: dict, rank: int, note: str) -> dict:
    return {"pair_id": pid, "stratum": stratum, "dataset": dataset, "rank": rank, "a": _slim(a), "b": _slim(b), "relation": note}


def build_zsre_pairs(rng: np.random.Generator, recs: list[dict]) -> list[dict]:
    by_subj: dict[str, list[dict]] = collections.defaultdict(list)
    by_tmpl: dict[str, list[dict]] = collections.defaultdict(list)
    for r in recs:
        by_subj[normalize_answer(r["subject"])].append(r)
        by_tmpl[r["template"]].append(r)
    pairs, used = [], set()

    def fresh(*items):
        return all(it["item_id"] not in used for it in items)

    def take(*items):
        used.update(it["item_id"] for it in items)

    def distinct(a, b):  # no semantic contradiction, no duplicate fact
        return normalize_answer(a["answer"]) != normalize_answer(b["answer"]) and a["template"] != b["template"]

    n = OVERSAMPLE * TARGET["shared"]
    subjects = sorted(s for s, v in by_subj.items() if len(v) >= 2)
    for s in rng.permutation(subjects):
        if len(pairs) >= n:
            break
        v = by_subj[s]
        cand = [(a, b) for i, a in enumerate(v) for b in v[i + 1:] if distinct(a, b)]
        if cand and fresh(*cand[0]):
            a, b = cand[int(rng.integers(len(cand)))]
            take(a, b)
            pairs.append(_pair(f"z-sh-{len(pairs)}", "shared", "zsre", a, b, len(pairs), "same subject, different relation (question template) and answer"))
    k0 = len(pairs)
    n = OVERSAMPLE * TARGET["near_neighbour"]
    templates = sorted(t for t, v in by_tmpl.items() if len(v) >= 2)
    for t in rng.permutation(templates):
        if len(pairs) - k0 >= n:
            break
        v = [r for r in by_tmpl[t] if r["item_id"] not in used]
        if len(v) < 2:
            continue
        a, b = (v[i] for i in rng.choice(len(v), 2, replace=False))
        if normalize_answer(a["subject"]) != normalize_answer(b["subject"]) and normalize_answer(a["answer"]) != normalize_answer(b["answer"]):
            take(a, b)
            pairs.append(_pair(f"z-nn-{len(pairs) - k0}", "near_neighbour", "zsre", a, b, len(pairs) - k0, "same relation (question template), different subject and answer"))
    k0 = len(pairs)
    n = OVERSAMPLE * TARGET["private"]
    order = rng.permutation(len(recs))
    i = 0
    while len(pairs) - k0 < n and i + 1 < len(order):
        a, b = recs[order[i]], recs[order[i + 1]]
        i += 2
        if fresh(a, b) and normalize_answer(a["subject"]) != normalize_answer(b["subject"]) and distinct(a, b):
            take(a, b)
            pairs.append(_pair(f"z-pr-{len(pairs) - k0}", "private", "zsre", a, b, len(pairs) - k0, "different subject, relation and answer (unrelated)"))
    return pairs


def build_counterfact_pairs(rng: np.random.Generator, dev: list[dict], sibs: list[dict]) -> list[dict]:
    pairs, used = [], set()
    by_subj = {normalize_answer(it["subject"]): it for it in dev}
    for s in rng.permutation(sorted({normalize_answer(x["subject"]) for x in sibs})):
        d = by_subj[s]
        cands = [x for x in sibs if normalize_answer(x["subject"]) == s and x.get("relation_id") != d.get("relation_id")
                 and normalize_answer(x["answer"]) != normalize_answer(d["answer"])]
        if cands and d["item_id"] not in used:
            x = cands[int(rng.integers(len(cands)))]
            used.update({d["item_id"], x["item_id"]})
            pairs.append(_pair(f"c-sh-{len(pairs)}", "shared", "counterfact", d, x, len(pairs), "same reserved subject, different relation id and target"))
    k0 = len(pairs)
    by_rel: dict[str, list[dict]] = collections.defaultdict(list)
    for it in dev:
        by_rel[it.get("relation_id")].append(it)
    n = TARGET["near_neighbour"]
    rels = sorted(r for r, v in by_rel.items() if len(v) >= 2)
    tries = 0
    while len(pairs) - k0 < n and tries < 10_000:
        tries += 1
        r = rels[int(rng.integers(len(rels)))]
        v = [x for x in by_rel[r] if x["item_id"] not in used]
        if len(v) < 2:
            continue
        a, b = (v[i] for i in rng.choice(len(v), 2, replace=False))
        if normalize_answer(a["answer"]) != normalize_answer(b["answer"]):
            used.update({a["item_id"], b["item_id"]})
            pairs.append(_pair(f"c-nn-{len(pairs) - k0}", "near_neighbour", "counterfact", a, b, len(pairs) - k0, "same relation id, different subject and target"))
    k0 = len(pairs)
    n = TARGET["private"]
    order = rng.permutation(len(dev))
    i = 0
    while len(pairs) - k0 < n and i + 1 < len(order):
        a, b = dev[order[i]], dev[order[i + 1]]
        i += 2
        if a["item_id"] in used or b["item_id"] in used:
            continue
        if a.get("relation_id") != b.get("relation_id") and normalize_answer(a["answer"]) != normalize_answer(b["answer"]):
            used.update({a["item_id"], b["item_id"]})
            pairs.append(_pair(f"c-pr-{len(pairs) - k0}", "private", "counterfact", a, b, len(pairs) - k0, "different subject, relation id and target (unrelated)"))
    return pairs


def build_grammar_pairs(rng: np.random.Generator) -> list[dict]:
    """Grammar pairs are (context, kind, seed) triples; items are regenerated at run time (no teacher filter:
    the base was trained with every mechanism switch off, so no task mechanism is known by construction)."""
    from pccap.fixtures.grammar_generator import CONTEXTS

    pairs = []
    counter = collections.Counter()

    def rec(ctx: int, kind: str) -> dict:
        i = counter[(ctx, kind)]
        counter[(ctx, kind)] += 1
        seed = GRAMMAR_SEED_BASE + GRAMMAR_STRIDE * ctx + (0 if kind == "private" else 10_000) + i
        return {"item_id": f"g7-{ctx}-{kind}-{seed}", "dataset": "grammar", "grammar": {"context": ctx, "kind": kind, "seed": seed}}

    for k in range(TARGET["shared"]):
        c1, c2 = rng.choice(CONTEXTS, 2, replace=False)
        pairs.append(_pair(f"g-sh-{k}", "shared", "grammar", rec(int(c1), "shared_1"), rec(int(c2), "shared_1"), k, "shared mechanism shared_1 fired in two different contexts"))
    for k in range(TARGET["private"]):
        c1, c2 = rng.choice(CONTEXTS, 2, replace=False)
        pairs.append(_pair(f"g-pr-{k}", "private", "grammar", rec(int(c1), "private"), rec(int(c2), "private"), k, "private mechanisms of two different contexts (independent by construction)"))
    for k in range(TARGET["near_neighbour"]):
        c = int(rng.integers(CONTEXTS))
        pairs.append(_pair(f"g-nn-{k}", "near_neighbour", "grammar", rec(c, "private"), rec(c, "private"), k, "same context's private mechanism, different sequences (same key region)"))
    return pairs


def build_inventory(seed: int = SEED) -> dict:
    from pccap import ASSETS_ROOT
    from pccap.data.splits import _sha

    rng = np.random.default_rng(seed)
    pool = _pool_subjects()
    elig_cf = set()
    for line in (Path(ASSETS_ROOT) / "data" / "prepared" / "editing" / "counterfact_eligible.jsonl").read_text().splitlines():
        if line.strip():
            elig_cf.add(normalize_answer(json.loads(line)["subject"]))
    z = build_zsre_pairs(rng, _zsre_train_records(pool))
    dev, sibs = _counterfact_records(elig_cf)
    c = build_counterfact_pairs(rng, dev, sibs)
    gpairs = build_grammar_pairs(rng)
    pairs = {"zsre": z, "counterfact": c, "grammar": gpairs}
    counts = {ds: {st: sum(1 for p in v if p["stratum"] == st) for st in STRATA} for ds, v in pairs.items()}
    raw = Path(ASSETS_ROOT) / "data" / "raw"
    man = {
        "name": "s7_pairs", "stage": "S7", "seed": seed, "written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "targets_per_stratum": TARGET, "oversample": OVERSAMPLE,
        "rule": ("Per checkpoint dataset and stratum, the pairs used are the first `targets_per_stratum` pairs in manifest order whose members "
                 "all pass the E.2 teacher filter (tokenization eligibility and the teacher's complete greedy answer outside the aliases), "
                 "evaluated once on the frozen BP base before any S7 result; a stratum that runs short is reported short. Semantic "
                 "contradictions (same subject and relation) and duplicate facts are excluded by construction."),
        "strata": {"shared": "two edits about the same subject with different relations (mechanism plausibly shared through the subject's key region)",
                   "private": "unrelated edits: different subject, relation and answer",
                   "near_neighbour": "same relation (zsRE question template / CounterFact relation id), different subject"},
        "independence": {"zsre": "MEND train split; subjects in no development, S0 or sealed pool",
                         "counterfact": "development pool items plus raw records sharing a reserved development subject; no sealed-pool item",
                         "grammar": f"seed block {GRAMMAR_SEED_BASE}+ (disjoint from DATA-06 train/eval/held-out blocks)"},
        "sources": {"zsre_mend_train.json": _sha(raw / "zsre" / "zsre_mend_train.json"), "counterfact.json": _sha(raw / "counterfact" / "counterfact.json"),
                    "counterfact_dev.json": _sha(ROOT / "manifests" / "dev" / "counterfact_dev.json")},
        "needs_teacher_filter": {f"{ds}/{st}": v for (ds, st), v in NEEDS_FILTER.items()},
        "expected": {ds: {st: TARGET[st] * (OVERSAMPLE if NEEDS_FILTER[(ds, st)] else 1) for st in STRATA} for ds in counts},
        "counts": counts, "shortfalls": {ds: {st: max(0, TARGET[st] * (OVERSAMPLE if NEEDS_FILTER[(ds, st)] else 1) - counts[ds][st]) for st in STRATA} for ds in counts},
        "pairs": pairs,
    }
    man["sha256_pairs"] = hashlib.sha256(json.dumps(pairs, sort_keys=True).encode()).hexdigest()
    return man


def materialize(rec: dict, tok=None, grammar=None) -> EditItem:
    """EditItem for one inventory record (GPT-2 tokenization for the editing datasets; regenerated grammar sequence)."""
    if rec["dataset"] == "grammar":
        from pccap.data.grammar_streams import _item
        from pccap.fixtures.grammar_generator import Grammar, Switches

        gsp = rec["grammar"]
        g = grammar or Grammar()
        toks, p, label = g.sequence(gsp["context"], Switches.task(gsp["context"]), gsp["seed"], gsp["kind"])
        return _item(toks, p, label, rec["item_id"], gsp["context"])
    from pccap.data.tokenize import tokenize_pair

    te = tokenize_pair(tok, rec["prompt"], rec["answer"])
    if te.excluded:
        raise ValueError(f"{rec['item_id']} excluded: {te.reason}")
    return EditItem(item_id=rec["item_id"], digest=bytes.fromhex(rec["digest"]), prompt=rec["prompt"], answer=rec["answer"], aliases=rec["aliases"],
                    paraphrases=rec.get("paraphrases", []), locality_prompts=rec.get("locality_prompts", []), prompt_ids=te.prompt_ids,
                    answer_ids=te.answer_ids, dataset=rec["dataset"], fact_id=rec.get("fact_id"))


# ----------------------------------------------------------------------------- protocol
def evaluation_set(item_i: EditItem, item_j: EditItem, tok=None, controls: list[np.ndarray] | None = None) -> dict[str, list[np.ndarray]]:
    """Q per D.9: the two edits' prefixes (prompt and paraphrases) and unrelated controls (their locality prompts, or
    ``controls``); ``Q_i`` (item i's own prefixes) is what the damage matrix averages over."""
    enc = (lambda s: np.asarray(tok.encode(s), np.int32)) if tok is not None else None

    def own(it: EditItem) -> list[np.ndarray]:
        return [np.asarray(it.prompt_ids, np.int32)] + ([enc(p) for p in it.paraphrases] if enc else [])

    ctrl = list(controls) if controls is not None else ([enc(p) for it in (item_i, item_j) for p in it.locality_prompts] if enc else [])
    return {"Q_i": own(item_i), "Q_j": own(item_j), "controls": ctrl}


def _last_logits(learner, seqs: list[np.ndarray]) -> np.ndarray:
    base = getattr(learner, "base", None)
    if hasattr(learner, "edited_forward_batch") and hasattr(base, "forward_batch"):
        return np.asarray(learner.edited_forward_batch(seqs, phase="query")[0])
    if hasattr(learner, "last_logits_batch"):
        return np.asarray(learner.last_logits_batch(seqs, phase="query"))
    rows = []
    for x in seqs:
        lg = np.asarray(learner.predict(x).logits)
        rows.append(lg[-1] if lg.ndim == 2 else lg)
    return np.stack(rows)


def _softmax(rows: np.ndarray) -> np.ndarray:
    r = np.asarray(rows, np.float64)
    r = r - r.max(-1, keepdims=True)
    e = np.exp(r)
    return e / e.sum(-1, keepdims=True)


def distributions(learner, Q: list[np.ndarray]) -> np.ndarray:
    """Next-token distributions at the last position of every prefix in Q ([|Q|, V]); read-only (PC-8)."""
    before = learner.state_hash()
    out = np.concatenate([_softmax(_last_logits(learner, Q[k: k + 64])) for k in range(0, len(Q), 64)]) if Q else np.zeros((0, 1))
    if learner.state_hash() != before:
        raise RuntimeError("evaluation mutated learner state (PC-8)")
    return out


def item_loss(learner, it: EditItem) -> float:
    """Teacher-forced NLL of the item's answer (sum over answer tokens) — L_x with x = the item's prompt."""
    ids = np.asarray(it.prompt_ids, np.int32)
    prefixes, targets = [], []
    for y in np.asarray(it.answer_ids, np.int32):
        prefixes.append(ids)
        targets.append(int(y))
        ids = np.concatenate([ids, np.int32([y])])
    L = _last_logits(learner, prefixes).astype(np.float64)
    m = L.max(-1)
    return float((m + np.log(np.exp(L - m[:, None]).sum(-1)) - L[np.arange(len(targets)), targets]).sum())


def item_exact(learner, it: EditItem) -> float:
    """Greedy answer (max_new = |answer_ids|) equals the answer tokens exactly — 1.0 / 0.0."""
    ids = np.asarray(it.prompt_ids, np.int32)
    for y in np.asarray(it.answer_ids, np.int32):
        nxt = int(np.argmax(_last_logits(learner, [ids])[0]))
        if nxt != int(y):
            return 0.0
        ids = np.concatenate([ids, np.int32([nxt])])
    return 1.0


def _apply(learner, it: EditItem, router, budget: Budget, seed: int) -> dict:
    """One protocol update with the decision records folded into counts."""
    recs: list = []
    if hasattr(learner, "banks"):
        from pccap.cap.learn import update_item

        out = update_item(learner, it, router, budget, on_decision=recs.append, seed=seed)
    else:
        out = learner.update_item(it)
    codes = [c for r in recs for c in r.codes]
    return {"code": out.code, "rounds": int(out.rounds_used), "decisions": len(recs),
            "allocations": sum(1 for r in recs for pb in r.per_bank.values() if pb.get("allocated")),
            "evictions": sum(1 for r in recs for pb in r.per_bank.values() if pb.get("evicted")),
            "codes": dict(collections.Counter(codes))}


def reversal(make_learner, state, item_i: EditItem, item_j: EditItem, Q: dict[str, list[np.ndarray]], router, budget: Budget, seed: int = 0) -> dict:
    """Clone ``state`` twice, run i→j and j→i, return D_ij with its operands, per-item accuracy/loss changes in both
    orders, update counts, allocations, evictions, and the damage entries I_ij (learn i, then j: change in L_i) and I_ji."""
    Q_all = Q["Q_i"] + Q["Q_j"] + Q["controls"]
    orders = {}
    for tag, first, second in (("ij", item_i, item_j), ("ji", item_j, item_i)):
        learner = make_learner()
        learner.import_state(state.clone())
        loss0 = {"i": item_loss(learner, item_i), "j": item_loss(learner, item_j)}
        acc0 = {"i": item_exact(learner, item_i), "j": item_exact(learner, item_j)}
        u1 = _apply(learner, first, router, budget, seed)
        loss_mid = {"i": item_loss(learner, item_i), "j": item_loss(learner, item_j)}
        u2 = _apply(learner, second, router, budget, seed)
        loss1 = {"i": item_loss(learner, item_i), "j": item_loss(learner, item_j)}
        acc1 = {"i": item_exact(learner, item_i), "j": item_exact(learner, item_j)}
        orders[tag] = {"dist": distributions(learner, Q_all), "loss_start": loss0, "loss_after_first": loss_mid, "loss_end": loss1,
                       "acc_start": acc0, "acc_end": acc1, "updates": {"first": u1, "second": u2}, "state_hash": learner.state_hash()}
    d = js(orders["ij"]["dist"], orders["ji"]["dist"]) if Q_all else metric(None, units="nats", n=0, status="undefined")
    per_pos = d["strata"]["per_position"] if Q_all else []
    ni, nj = len(Q["Q_i"]), len(Q["Q_j"])
    return {
        "D_ij": d, "D_parts": {"Q_i": float(np.mean(per_pos[:ni])) if ni else None, "Q_j": float(np.mean(per_pos[ni:ni + nj])) if nj else None,
                               "controls": float(np.mean(per_pos[ni + nj:])) if len(per_pos) > ni + nj else None},
        "I_ij": orders["ij"]["loss_end"]["i"] - orders["ij"]["loss_after_first"]["i"],  # learn i, then j: harm to i
        "I_ji": orders["ji"]["loss_end"]["j"] - orders["ji"]["loss_after_first"]["j"],  # learn j, then i: harm to j
        "accuracy": {t: {"i": (o["acc_start"]["i"], o["acc_end"]["i"]), "j": (o["acc_start"]["j"], o["acc_end"]["j"])} for t, o in orders.items()},
        "loss": {t: {"start": o["loss_start"], "after_first": o["loss_after_first"], "end": o["loss_end"]} for t, o in orders.items()},
        "updates": {t: o["updates"] for t, o in orders.items()},
        "state_hash": {t: o["state_hash"] for t, o in orders.items()}, "same_endpoint": orders["ij"]["state_hash"] == orders["ji"]["state_hash"],
        "n_Q": {"Q_i": ni, "Q_j": nj, "controls": len(Q["controls"])},
    }


def damage_matrix(results: list[dict]) -> dict:
    """Aggregate I_ij / I_ji and D_ij per stratum and over all pairs (both orders, with operands)."""
    out = {}
    for st in list(STRATA) + ["all"]:
        rs = [r for r in results if st == "all" or r["stratum"] == st]
        if not rs:
            out[st] = {"n": 0, "status": "undefined"}
            continue
        I = np.asarray([[r["I_ij"], r["I_ji"]] for r in rs], np.float64)
        D = np.asarray([r["D_ij"]["value"] for r in rs if r["D_ij"]["value"] is not None], np.float64)
        out[st] = {"n": len(rs), "I_ij_mean": float(I[:, 0].mean()), "I_ji_mean": float(I[:, 1].mean()), "I_both_orders_mean": float(I.mean()),
                   "I_positive_fraction": float((I > 0).mean()), "D_ij_mean": float(D.mean()) if len(D) else None, "D_ij_max": float(D.max()) if len(D) else None,
                   "same_endpoint_fraction": float(np.mean([r["same_endpoint"] for r in rs])),
                   "updates_mean_rounds": float(np.mean([r["updates"][t][k]["rounds"] for r in rs for t in ("ij", "ji") for k in ("first", "second")])),
                   "allocations_total": int(sum(r["updates"][t][k]["allocations"] for r in rs for t in ("ij", "ji") for k in ("first", "second"))),
                   "evictions_total": int(sum(r["updates"][t][k]["evictions"] for r in rs for t in ("ij", "ji") for k in ("first", "second")))}
    return out


def run_pairs(make_learner, state, pairs: list[tuple[str, str, EditItem, EditItem, dict]], router, budget: Budget, seed: int = 0) -> dict:
    """pairs: (pair_id, stratum, item_i, item_j, Q). Returns the per-pair results and the damage matrix."""
    rows = []
    for pid, st, a, b, Q in pairs:
        r = reversal(make_learner, state, a, b, Q, router, budget, seed)
        r.update(pair_id=pid, stratum=st)
        rows.append(r)
    return {"pairs": rows, "damage_matrix": damage_matrix(rows), "n": len(rows)}


# ----------------------------------------------------------------------------- CLI
def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true", help="write manifests/dev/s7_pairs.json")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--checkpoint", default=None, help="GPU run on a committed learner checkpoint (S7-01/02; needs the frozen manifest)")
    args = ap.parse_args(argv)
    if args.build:
        man = build_inventory(args.seed)
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(json.dumps(man, indent=1))
        print(json.dumps({"counts": man["counts"], "shortfalls": man["shortfalls"], "sha256_pairs": man["sha256_pairs"]}, indent=1))
        return 0
    if args.checkpoint:
        raise SystemExit("the checkpoint run is wired after S4-04 commits checkpoints (needs the frozen arm, the GPU lease and the E.2 filter pass)")
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
