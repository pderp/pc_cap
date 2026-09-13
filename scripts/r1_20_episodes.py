"""R1-20 episode implementation, staged outside the active v0 source hash.

Intended destination after the owner releases the v0 queue:
``src/pccap/revision_v1/episodes.py``. No v0 module is modified. These local,
immutable records are an adapter boundary for the Stage 1 contracts owner.

Synthetic semantics extend Grammar's private rule at (context, class-3 value),
not an entire context switch. Support supplies a revised class-4 answer for that
scope. Other scopes retain the base grammar. Composition opcode BOS (1) requests
two private-rule applications; class-4 output index becomes class-3 input index
for the second hop. This is a new synthetic task, not a v0 grammar result.

All generated splits here are DEVELOPMENT fixtures, including ``test``. A fresh
confirmation generator/version and subject reservation are separate owner acts.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from pccap.fixtures.grammar_generator import (
    BOS,
    CLASS_SIZE,
    CONTENT_BASE,
    CONTEXT_TOKENS,
    Grammar,
    Switches,
    class_of,
    class_tokens,
)

Split = Literal["train", "dev", "test"]
SPLITS = ("train", "dev", "test")
CONTEXT_SPLITS = {"train": (0, 1, 2, 3), "dev": (4, 5), "test": (6, 7)}
FAMILY_SPLITS = {"train": (0, 1), "dev": (2, 3), "test": (4, 5)}
TOKEN_IDS = tuple[int, ...]


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(re.findall(r"\w+", text.casefold()))


@dataclass(frozen=True)
class SupportExample:
    record_id: str
    fact_id: str
    revision: int
    entity_id: str
    family_id: str
    prompt_ids: TOKEN_IDS = ()
    answer_ids: TOKEN_IDS = ()
    prompt: str = ""
    answer: str = ""
    # Only supplied support belongs here. No query targets or oracle links.


@dataclass(frozen=True)
class PredictionQuery:
    query_id: str
    prompt_ids: TOKEN_IDS = ()
    prompt: str = ""


@dataclass(frozen=True)
class QueryLabel:
    query_id: str
    role: str
    entity_ids: tuple[str, ...]
    family_id: str
    target_ids: TOKEN_IDS = ()
    target: str | None = None
    target_source: str = "synthetic_rule"
    supporting_record_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class EpisodeInputs:
    """Support contains teaching labels; queries contain no scoring metadata."""

    support_history: tuple[SupportExample, ...]
    new_support: tuple[SupportExample, ...]
    queries: tuple[PredictionQuery, ...]

    def input_digest(self) -> str:
        return digest(asdict(self))

    def adaptation_batches(self) -> tuple[tuple[SupportExample, ...], ...]:
        """Consumer starts from empty memory and adapts on support alone."""
        return tuple((s,) for s in self.support_history) + (self.new_support,)


@dataclass(frozen=True)
class LabeledEpisode:
    """Only outer-training/evaluation code receives this label-bearing record."""

    episode_id: str
    split_id: Split
    generator_seed: int
    partition_seed: int
    domain: str
    inputs: EpisodeInputs
    query_labels: tuple[QueryLabel, ...]
    provenance: tuple[tuple[str, str], ...]

    def prediction_inputs(self) -> tuple[PredictionQuery, ...]:
        return self.inputs.queries


def _split(split: str) -> None:
    if split not in SPLITS:
        raise ValueError(f"unknown split {split!r}")


def _fact(context: int, value: int) -> str:
    return f"grammar-private:c{context}:v{value}"


def _base(g: Grammar, context: int, value: int) -> int:
    return class_tokens(4)[int(g.perm_p[context, 0, value])]


def _prefix(g: Grammar, context: int, value: int, seed: int, family: int,
            forbidden: set[TOKEN_IDS]) -> TOKEN_IDS:
    """Bounded rejection, with explicit failure instead of missing paraphrases."""
    for attempt in range(1024):
        tokens, position, _ = g.sequence(context, Switches.base(), seed + attempt,
                                         "private", {"class3": class_tokens(3)[value]})
        prefix = tuple(int(x) for x in tokens[:position])
        if class_of(prefix[1]) != family or prefix in forbidden:
            continue
        content = [x for x in prefix if x >= CONTENT_BASE]
        if content[-1] != class_tokens(3)[value]:
            continue
        expected, kind = g.rule_target(tokens[:position], context, Switches.base())
        if kind != "private" or expected != _base(g, context, value):
            raise ValueError("grammar scope reconstruction failed")
        forbidden.add(prefix)
        return prefix
    raise ValueError("paraphrase family exhausted; episode rejected in full")


def synthetic_episode(seed: int, split: Split = "train", history_size: int = 4,
                      *, revision: bool = False, composition: bool = True,
                      rule_seed: int = 7) -> LabeledEpisode:
    """Two to eight supports, one new edit, two paraphrases and scope controls.

    Entity partition is the *actual context token*; families are disjoint actual
    initial content classes. Labels never affect prefix generation. Prefixes are
    sampled under the base rule, so a new answer is not planted in its question.
    """
    _split(split)
    if not 2 <= history_size <= 8 or seed < 0:
        raise ValueError("history_size must be 2..8 and seed nonnegative")
    g, rng = Grammar(rule_seed), random.Random(seed)
    contexts = CONTEXT_SPLITS[split]
    support_family, query_family = FAMILY_SPLITS[split]
    context = rng.choice(contexts)
    other = rng.choice([c for c in contexts if c != context])
    value = rng.randrange(CLASS_SIZE)
    original = _base(g, context, value)
    new_answer = class_tokens(4)[(original - class_tokens(4)[0] + (2 if revision else 1)) % CLASS_SIZE]
    second_value = new_answer - class_tokens(4)[0]
    second_scope = (other, second_value)
    excluded_answers = {_base(g, other, second_value),
                        _base(g, other, original - class_tokens(4)[0])}
    second_answer = rng.choice([t for t in class_tokens(4) if t not in excluded_answers])
    scopes = [(c, v) for c in contexts for v in range(CLASS_SIZE)]
    near = (context, (value + 1) % CLASS_SIZE)
    unrelated = (other, (second_value + 1) % CLASS_SIZE)
    reserved = {(context, value), second_scope, near, unrelated,
                (other, original - class_tokens(4)[0])}
    free = [s for s in scopes if s not in reserved]
    rng.shuffle(free)
    history_scopes = [second_scope] + ([(context, value)] if revision else [])
    history_scopes += free[:history_size-len(history_scopes)]
    forbidden: set[TOKEN_IDS] = set()
    episode_id = "r1-syn-" + digest((rule_seed, split, seed, history_size, revision, composition))[:24]

    def support(scope, answer, rev, index):
        c, v = scope
        prompt = _prefix(g, c, v, 6_000_000 + seed*100_000 + index*2048,
                         support_family, forbidden)
        fact = _fact(c, v)
        return SupportExample(f"{fact}:revision-{rev}", fact, rev, f"context-{c}",
                              f"initial-class-{support_family}", prompt, (answer,))

    history = []
    for i, scope in enumerate(history_scopes):
        c, v = scope
        answer = second_answer if scope == second_scope else class_tokens(4)[(_base(g, c, v)-class_tokens(4)[0]+1) % CLASS_SIZE]
        history.append(support(scope, answer, 1, i))
    new = support((context, value), new_answer, 2 if revision else 1, 10)
    queries, labels = [], []

    def query(scope, role, target, records=()):
        c, v = scope
        qi = len(queries)
        qid = digest((episode_id, "query", qi))[:24]
        prefix = _prefix(g, c, v, 6_000_000 + seed*100_000 + (20+qi)*2048,
                         query_family, forbidden)
        queries.append(PredictionQuery(qid, prefix))
        labels.append(QueryLabel(qid, role, (f"context-{c}",),
                                 f"initial-class-{query_family}", (target,),
                                 supporting_record_ids=tuple(records)))

    for _ in range(2):
        query((context, value), "new_paraphrase", new_answer, (new.record_id,))
    query(second_scope, "old_fact", second_answer, (history[0].record_id,))
    query(near, "near_miss", _base(g, *near))
    query(unrelated, "unrelated", _base(g, *unrelated))
    if composition:
        qid = digest((episode_id, "query", len(queries)))[:24]
        prefix = (BOS, CONTEXT_TOKENS[context], class_tokens(3)[value], BOS, CONTEXT_TOKENS[other])
        queries.append(PredictionQuery(qid, prefix))
        labels.append(QueryLabel(qid, "composition", (f"context-{context}", f"context-{other}"),
                                 "composition-opcode-1", (second_answer,),
                                 supporting_record_ids=(new.record_id, history[0].record_id)))
    out = LabeledEpisode(episode_id, split, seed, 0, "grammar-private-scope-v1",
                         EpisodeInputs(tuple(history), (new,), tuple(queries)), tuple(labels),
                         (("rule_seed", str(rule_seed)), ("partition", "contexts and initial classes fixed before sampling"),
                          ("composition_template_overlap", "shared fixed opcode across development splits; explicitly controlled"),
                          ("fresh_confirmation", "false; development fixture only")))
    validate_episode(out)
    return out


def synthetic_oracle(query: PredictionQuery, supports: tuple[SupportExample, ...],
                     rule_seed: int = 7) -> TOKEN_IDS:
    """Fixture semantic oracle for tests only. Accepts support, never query labels."""
    g = Grammar(rule_seed)
    state = {}
    for s in supports:
        state[s.fact_id] = s.answer_ids[0]

    def answer(c, v):
        return state.get(_fact(c, v), _base(g, c, v))

    p = query.prompt_ids
    if p and p[0] == BOS:
        if len(p) != 5 or p[3] != BOS:
            raise ValueError("bad composition syntax")
        c1, c2, v = p[1]-2, p[4]-2, p[2]-class_tokens(3)[0]
        first = answer(c1, v)
        return (answer(c2, first-class_tokens(4)[0]),)
    content = [x for x in p if x >= CONTENT_BASE]
    return (answer(p[0]-2, content[-1]-class_tokens(3)[0]),)


def validate_episode(e: LabeledEpisode) -> None:
    _split(e.split_id)
    if not 2 <= len(e.inputs.support_history) <= 8 or len(e.inputs.new_support) != 1:
        raise ValueError("support cardinality")
    queries = e.prediction_inputs()
    qids = [q.query_id for q in queries]
    if len(set(qids)) != len(qids) or set(qids) != {x.query_id for x in e.query_labels} or len(queries) != len(e.query_labels):
        raise ValueError("query/label alignment")
    if sum(x.role == "new_paraphrase" for x in e.query_labels) < 2:
        raise ValueError("two unseen paraphrases required")
    if not {"old_fact", "near_miss", "unrelated"} <= {x.role for x in e.query_labels}:
        raise ValueError("missing scope/retention query")
    supports = e.inputs.support_history + e.inputs.new_support
    record_ids = {s.record_id for s in supports}
    if len(record_ids) != len(supports):
        raise ValueError("duplicate support record")
    seen = set()
    support_prompts = {(s.prompt_ids, s.prompt) for s in supports}
    for q in queries:
        key = (q.prompt_ids, q.prompt)
        if key in seen or key in support_prompts:
            raise ValueError("query duplicate or reused support prompt")
        seen.add(key)
    for label in e.query_labels:
        if not set(label.supporting_record_ids) <= record_ids:
            raise ValueError("label refers to absent support")
    if e.domain == "grammar-private-scope-v1":
        by_id = {q.query_id: q for q in queries}
        for label in e.query_labels:
            if synthetic_oracle(by_id[label.query_id], supports, int(dict(e.provenance)["rule_seed"])) != label.target_ids:
                raise ValueError("synthetic target differs from explicit scope semantics")


def paraphrase_family(row: dict, prompt: str) -> str:
    """Conservative relation family for CF; subject-masked surface template for zsRE.

    These are operational IDs, not a claim of semantic equivalence. CF groups
    all phrasings of a relation together rather than splitting by context filler.
    """
    if row.get("relation_id"):
        return "cf-relation:" + str(row["relation_id"])
    subject = normalize(row["subject"])
    template = normalize(prompt).replace(subject, "{entity}") if subject else normalize(prompt)
    return "surface:" + digest(template)


def partition_dev_records(rows: list[dict], seed: int = 91) -> dict[str, Split]:
    """Connected components of fact/entity/family before episode generation.

    Pass both development pools together to enforce cross-dataset entity joins.
    This uses no labels and no metrics. Components, not individual rows, receive
    a deterministic 70/15/15 hash assignment; sizes may be unbalanced.
    """
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    row_keys = {}
    for row in rows:
        rid = str(row["item_id"])
        if rid in row_keys:
            raise ValueError("duplicate source item id")
        keys = ["entity:"+normalize(row["subject"]), "fact:"+str(row["fact_id"])]
        keys += ["family:"+paraphrase_family(row, p) for p in [row["prompt"], *row.get("paraphrases", [])]]
        keys += ["prompt:"+normalize(p) for p in [row["prompt"], *row.get("paraphrases", [])]]
        row_keys[rid] = keys
        for key in keys:
            a, b = find(keys[0]), find(key)
            parent[max(a, b)] = min(a, b)
    groups = {}
    for rid, keys in row_keys.items():
        groups.setdefault(find(keys[0]), []).append(rid)
    assignment = {}
    for members in groups.values():
        bucket = int(digest((seed, sorted(members)))[:16], 16) % 100
        split = "train" if bucket < 70 else "dev" if bucket < 85 else "test"
        assignment.update({rid: split for rid in members})
    return assignment


def load_development(root: Path) -> tuple[list[dict], dict[str, str]]:
    """Only the two named development pools are loadable through this API."""
    rows, sources = [], {}
    for dataset in ("zsre", "counterfact"):
        path = root / "manifests" / "dev" / f"{dataset}_dev.json"
        raw = path.read_bytes()
        doc = json.loads(raw)
        if doc.get("mode") != "dev" or doc.get("dataset") != dataset:
            raise ValueError("not a declared development pool")
        rows.extend(doc["items"])
        sources[str(path)] = hashlib.sha256(raw).hexdigest()
    return rows, sources


def usable_paraphrases(row: dict) -> tuple[str, ...]:
    out, seen = [], {normalize(row["prompt"])}
    for prompt in row.get("paraphrases", []):
        key = normalize(prompt)
        if key and key not in seen:
            seen.add(key)
            out.append(prompt)
    return tuple(out)


def natural_episode(rows: list[dict], seed: int, split: Split = "train", history_size: int = 4,
                    *, dataset: str = "counterfact", partition_seed: int = 91) -> LabeledEpisode:
    """Development-only text adapter; no invented paraphrases or locality labels.

    Scope controls require cap-disabled teacher predictions supplied separately
    by the evaluator/outer trainer. Gold edited answers must not stand in for the
    teacher on unrelated prompts. Natural-language composition is unsupported
    until a checked relation graph is supplied.
    """
    _split(split)
    if not 2 <= history_size <= 8 or seed < 0:
        raise ValueError("history_size must be 2..8 and seed nonnegative")
    assignment = partition_dev_records(rows, partition_seed)
    pool = [r for r in rows if r["dataset"] == dataset and assignment[r["item_id"]] == split]
    eligible = [r for r in pool if len(usable_paraphrases(r)) >= 2 and r.get("locality_prompts")]
    if len(eligible) < history_size+2:
        raise ValueError(f"{dataset}/{split}: need {history_size+2} records with >=2 distinct paraphrases and a scope prompt; got {len(eligible)}")
    rng = random.Random(seed)
    rng.shuffle(eligible)
    # Skip episodes whose neighborhood prompt duplicates a supervised fact; no relabeling.
    for offset in range(len(eligible)):
        group = (eligible[offset:]+eligible[:offset])[:history_size+2]
        old, new, unrelated = group[:history_size], group[history_size], group[-1]
        if len({normalize(r["subject"]) for r in group}) != len(group):
            continue
        if paraphrase_family(new, new["prompt"]) == paraphrase_family(unrelated, unrelated["prompt"]):
            continue
        used = {normalize(r["prompt"]) for r in [*old, new]}
        paras = usable_paraphrases(new)[:2]
        old_query = usable_paraphrases(old[0])[0]
        near = next((p for p in new["locality_prompts"] if normalize(p) not in used and normalize(p) not in {normalize(x) for x in (*paras, old_query, unrelated["prompt"])}), None)
        if near is not None:
            break
    else:
        raise ValueError("no unambiguous distinct scope-control layout in this split")
    eid = "r1-natural-"+digest((dataset, split, seed, partition_seed, [r["item_id"] for r in group]))[:24]

    def support(row):
        return SupportExample(str(row["fact_id"])+":revision-1", str(row["fact_id"]), 1,
                              normalize(row["subject"]), paraphrase_family(row, row["prompt"]),
                              prompt=row["prompt"], answer=row["answer"])

    history = tuple(support(r) for r in old)
    new_support = support(new)
    queries, labels = [], []
    specifications = [(p, "new_paraphrase", new, new["answer"], (new_support.record_id,)) for p in paras]
    specifications += [(old_query, "old_fact", old[0], old[0]["answer"], (history[0].record_id,)),
                       (near, "near_miss", new, None, ()),
                       (unrelated["prompt"], "unrelated", unrelated, None, ())]
    for i, (prompt, role, row, target, records) in enumerate(specifications):
        qid = digest((eid, "query", i))[:24]
        queries.append(PredictionQuery(qid, prompt=prompt))
        entities = ("unresolved-neighborhood:" + digest(prompt),) if role == "near_miss" else (normalize(row["subject"]),)
        labels.append(QueryLabel(qid, role, entities, paraphrase_family(row, prompt),
                                 target=target, target_source="development_supplied_edit" if target is not None else "teacher_prediction_required",
                                 supporting_record_ids=records))
    out = LabeledEpisode(eid, split, seed, partition_seed, "natural-development-v1",
                         EpisodeInputs(history, (new_support,), tuple(queries)), tuple(labels),
                         (("source_items", json.dumps([r["item_id"] for r in group])),
                          ("composition", "unsupported: no verified two-hop relation graph"),
                          ("scope_entities", "source subject IDs are provenance, not resolved entities of neighborhood text; DATA-R1 needs an expanded exclusion audit"),
                          ("family_policy", "CF whole relation; zsRE subject-masked surface template; connected components across pools"),
                          ("tokenization", "deferred to GPT2Tokenizer/tokenize_pair adapter; text kept verbatim"),
                          ("fresh_confirmation", "false; all inputs drawn from v0 development pools")))
    validate_episode(out)
    return out
