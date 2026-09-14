"""R1-20c: versioned synthetic namespaces, disjoint in IDs AND prompt tokens.

Reuses the v1 private-rule task but transports it to reserved context and surface
tokens in the GPT-2 vocabulary. The 64-token v0 grammar model is incompatible.
No final examples are emitted by importing or freezing this specification.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, replace

from pccap.revision_v1 import episodes as old


@dataclass(frozen=True)
class Namespace:
    version: str = "grammar-private-scope-v2"
    entity_start: int = 64
    surface_start: int = 96
    marker: int = 102
    rule_seed: int = 2701
    fixture_only: bool = False

    def entities(self, split):
        start, end = {"train": (0, 16), "dev": (16, 24), "test": (24, 32)}[split]
        return tuple(range(self.entity_start + start, self.entity_start + end))

    def families(self, split):
        return tuple(self.surface_start + i for i in old.FAMILY_SPLITS[split])

    def seed_range(self, split):
        return {"train": (0, 499_999), "dev": (500_000, 999_999), "test": (1_000_000, 1_099_999)}[split]

    def identity(self):
        return old.digest(asdict(self))


DEFAULT = Namespace()


def validate_namespace(spec, *, exposed_entity_ids=(), exposed_namespace_tokens=(), vocab_size=50257):
    """Pre-emission check over the entire reservation, before sampling any episode."""
    if not spec.version or spec.version == "grammar-private-scope-v1":
        raise ValueError("a distinct namespace version is required")
    entities = [t for s in old.SPLITS for t in spec.entities(s)]
    surfaces = [t for s in old.SPLITS for t in spec.families(s)]
    tokens = entities + surfaces + [spec.marker]
    if len(tokens) != len(set(tokens)) or min(tokens) < 64 or max(tokens) >= vocab_size:
        raise ValueError("namespace tokens must be unique, outside legacy 0..63, and inside vocabulary")
    ids = {f"{spec.version}:entity-{t}" for t in entities}
    if ids & set(exposed_entity_ids) or set(tokens) & set(exposed_namespace_tokens):
        raise ValueError("namespace overlaps a prior entity/token reservation or exposure")
    return {"identity": spec.identity(), "entity_ids": sorted(ids), "namespace_tokens": sorted(tokens)}


def reservation(spec=DEFAULT):
    checked = validate_namespace(spec)
    return {"schema_version": 1, "namespace": asdict(spec), "namespace_sha256": spec.identity(),
        "partitions": {s: {"entity_tokens": list(spec.entities(s)), "surface_tokens": list(spec.families(s)),
            "episode_seed_range_inclusive": list(spec.seed_range(s)),
            "scope_ids": [f"{spec.version}:entity-{c}:value-{v}" for c in spec.entities(s) for v in range(9)]}
            for s in old.SPLITS},
        "namespace_tokens": checked["namespace_tokens"], "minimum_vocab_size": max(checked["namespace_tokens"]) + 1,
        "legacy_namespace_tokens": list(range(64)),
        "semantics": "v1 private-rule/composition task; namespace-specific rule seed; new physical entity and family tokens",
        "template_overlap": "underlying class transitions and composition opcode shared; surface markers and entities disjoint",
        "paraphrase_gate": "at least two distinct new-fact queries, none equal to support; reject whole episode",
        "final_generation_ready": True, "ready_scope": "implementation and immutable reservation only",
        "final_emission_authorized": False, "final_examples_emitted": 0,
        "required_runtime_permission": "matching lead-issued receipt, checked before generating a reserved test episode",
        "compatibility": "GPT-2 vocabulary; NOT the old 64-token grammar checkpoint or old synthetic oracle"}


def _mapping(spec, split, seed):
    legacy = old.CONTEXT_SPLITS[split]
    entities = spec.entities(split)
    group = seed % (len(entities) // len(legacy))
    return dict(zip(legacy, entities[group * len(legacy):(group + 1) * len(legacy)]))


def generate_episode(seed, split="train", history_size=4, *, spec=DEFAULT, revision=False,
                     composition=True, exposed_entity_ids=(), exposed_namespace_tokens=(), lead_receipt=None):
    validate_namespace(spec, exposed_entity_ids=exposed_entity_ids, exposed_namespace_tokens=exposed_namespace_tokens)
    lo, hi = spec.seed_range(split)
    if not lo <= seed <= hi:
        raise ValueError("episode seed outside its reserved split range")
    if split == "test" and not spec.fixture_only:
        if not isinstance(lead_receipt, dict) or lead_receipt.get("approved_by") != "lead" or lead_receipt.get("namespace_sha256") != spec.identity() or lead_receipt.get("allow_final_emission") is not True:
            raise PermissionError("reserved final emission requires the lead's matching authorization receipt")
    mapping = _mapping(spec, split, seed)
    rule_seed = spec.rule_seed + min(mapping.values())
    ep = old.synthetic_episode(seed, split, history_size, revision=revision, composition=composition, rule_seed=rule_seed)
    eid = "r1-syn-v2-" + old.digest((spec.identity(), ep.episode_id))[:24]

    def entity(c):
        return f"{spec.version}:entity-{mapping[c]}"

    def fact(s):
        match = re.fullmatch(r"grammar-private:c(\d+):v(\d+)", s)
        if match is None:
            raise ValueError("unknown inherited fact syntax")
        return entity(int(match[1])) + ":value-" + match[2]

    def family_id(f):
        if f == "composition-opcode-1":
            return spec.version + ":composition-shared-opcode-1"
        i = int(f.removeprefix("initial-class-"))
        return f"{spec.version}:surface-{spec.surface_start+i}"

    def prefix(ids, f):
        family = spec.surface_start + (old.FAMILY_SPLITS[split][1] if f == "composition-opcode-1" else int(f.removeprefix("initial-class-")))
        return (spec.marker, family) + tuple(mapping[t-2] if t in old.CONTEXT_TOKENS else t for t in ids)

    record_map = {}
    def support(s):
        ff = fact(s.fact_id)
        rid = ff + f":revision-{s.revision}"
        record_map[s.record_id] = rid
        return replace(s, record_id=rid, fact_id=ff, entity_id=entity(int(s.entity_id.removeprefix("context-"))),
                       family_id=family_id(s.family_id), prompt_ids=prefix(s.prompt_ids, s.family_id))

    history = tuple(support(s) for s in ep.inputs.support_history)
    new = tuple(support(s) for s in ep.inputs.new_support)
    queries, labels = [], []
    qmap = {q.query_id: q for q in ep.inputs.queries}
    for i, lab in enumerate(ep.query_labels):
        q = qmap[lab.query_id]
        qid = old.digest((eid, i))[:24]
        queries.append(replace(q, query_id=qid, prompt_ids=prefix(q.prompt_ids, lab.family_id)))
        labels.append(replace(lab, query_id=qid, entity_ids=tuple(entity(int(c.removeprefix("context-"))) for c in lab.entity_ids),
            family_id=family_id(lab.family_id), supporting_record_ids=tuple(record_map[r] for r in lab.supporting_record_ids)))
    out = replace(ep, episode_id=eid, domain=spec.version, inputs=old.EpisodeInputs(history, new, tuple(queries)),
        query_labels=tuple(labels), provenance=(("namespace_sha256", spec.identity()), ("namespace", json.dumps(asdict(spec), sort_keys=True)),
            ("context_map", json.dumps(mapping, sort_keys=True)), ("rule_seed", str(rule_seed)),
            ("fixture_only", str(spec.fixture_only).lower()), ("final_emission_authorized", str(split == "test" and lead_receipt is not None).lower())))
    old.validate_episode(out)
    for lab in out.query_labels:
        q = next(q for q in out.inputs.queries if q.query_id == lab.query_id)
        if semantic_oracle(q, history + new, out.provenance) != lab.target_ids:
            raise ValueError("transported namespace changed private-rule semantics")
    return out


def semantic_oracle(query, supports, provenance):
    """Test/evaluator oracle. Uses supplied support and public namespace metadata, no query labels."""
    prov = dict(provenance)
    spec = Namespace(**json.loads(prov["namespace"]))
    inverse = {int(v): int(k) for k, v in json.loads(prov["context_map"]).items()}
    def restore_ids(ids):
        if len(ids) < 3 or ids[0] != spec.marker or not spec.surface_start <= ids[1] < spec.surface_start + 6:
            raise ValueError("invalid namespace/surface prefix")
        return tuple(inverse[t] + 2 if t in inverse else t for t in ids[2:])
    restored = []
    for s in supports:
        m = re.fullmatch(re.escape(spec.version) + r":entity-(\d+):value-(\d+)", s.fact_id)
        if m is None or int(m[1]) not in inverse:
            raise ValueError("support belongs to a different namespace")
        restored.append(replace(s, fact_id=f"grammar-private:c{inverse[int(m[1])]}:v{m[2]}", prompt_ids=restore_ids(s.prompt_ids)))
    return old.synthetic_oracle(replace(query, prompt_ids=restore_ids(query.prompt_ids)), tuple(restored), int(prov["rule_seed"]))
