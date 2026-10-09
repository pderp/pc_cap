"""Probe construction: every prompt/target pair the three models are scored on, with stable identifiers.

Observation units are explicit in ``family``:
  edit / paraphrase / locality_item          one row per (item, prompt)  -- the 300 stream items of realization 0, order 100
  locality / near_miss_neighbour / near_miss_edit / revision / revision_paraphrase / unseen
                                             one row per endpoint row   -- the sealed endpoint bundles (50 / 100 / 50 / 100)
  composition                                one row per (case, question) -- MQuAKE multi-hop cases (80 cases x 3 questions)
Targets are kept per row under ``targets``: ``new`` (requested/taught answer), ``true`` (original fact), ``v1``/``v2``
(revision versions), ``old``/``new`` for composition. Raw and normalised answers are separate fields.
"""

from __future__ import annotations

import ast
import hashlib
import json

from aw.extremes.models import payload as load_payload
from pccap.metrics.editing import normalize_answer


def _lst(v):
    if v is None:
        return []
    if isinstance(v, str):
        try:
            v = ast.literal_eval(v)
        except Exception:
            return [v]
    return list(v)


def _str_target(v):
    if isinstance(v, dict):
        return v.get("str")
    if isinstance(v, str) and v.startswith("{"):
        try:
            return ast.literal_eval(v).get("str")
        except Exception:
            return v
    return v


def _target(text, aliases=None, qid=None):
    if text is None:
        return None
    aliases = [a for a in (aliases or []) if isinstance(a, str) and a.strip()]
    if not aliases:
        aliases = [text]
    return dict(text=text, normalized=normalize_answer(text), aliases=aliases, normalized_aliases=sorted({normalize_answer(a) for a in aliases}), qid=qid)


def probe_id(dataset, family, *parts):
    key = "|".join([dataset, family, *map(str, parts)])
    return hashlib.sha256(key.encode()).hexdigest()[:20]


def build_probes(dataset: str, n_items: int = 300) -> tuple[list[dict], dict]:
    pay, binding = load_payload(dataset)
    items = pay["items"][:n_items]
    pool = {r["item_id"]: r for r in pay.get("pool_rows", [])}
    rows: list[dict] = []

    def add(family, parts, prompt, targets, item_id=None, **meta):
        if not isinstance(prompt, str) or not prompt.strip():
            return
        rows.append(dict(probe_id=probe_id(dataset, family, *parts), dataset=dataset, family=family, item_id=item_id, prompt=prompt,
                         targets={k: v for k, v in targets.items() if v is not None}, **meta))

    for index, it in enumerate(items):
        iid = it["item_id"]
        new = _target(it["answer"], _lst(it.get("aliases")))
        true = None
        if dataset == "counterfact":
            true = _target(it.get("target_true"))
        elif dataset == "mquake":
            tt = it.get("target_true")
            true = _target(_str_target(tt), qid=(tt.get("id") if isinstance(tt, dict) else None))
        meta = dict(stream_index=index + 1, subject=it.get("subject"), relation_id=it.get("relation_id"), fact_id=it.get("fact_id"),
                    source_case_id=it.get("source_case_id"), answer_tokens=int(it["answer_tokens"]) if it.get("answer_tokens") is not None else None)
        add("edit", [iid], it["prompt"], dict(new=new, true=true), iid, **meta)
        for j, p in enumerate(_lst(it.get("paraphrases"))):
            add("paraphrase", [iid, j], p, dict(new=new, true=true), iid, paraphrase_index=j, **meta)
        if dataset == "mquake":
            for j, loc in enumerate(_lst(it.get("locality"))):
                add("locality_item", [iid, j], loc["prompt"], dict(true=_target(loc["answer"], loc.get("aliases"))), iid, locality_index=j, locality_item_id=loc.get("item_id"), relation_id=loc.get("relation_id"), stream_index=index + 1)
        else:
            lp, la = _lst(it.get("locality_prompts")), _lst(it.get("locality_answers"))
            for j, p in enumerate(lp):
                ans = la[j] if j < len(la) else None
                add("locality_item", [iid, j], p, dict(true=_target(ans)), iid, locality_index=j, stream_index=index + 1)
    ep = pay["endpoints"]
    for r in ep["locality"]["rows"]:
        src = pool.get(r.get("source_outside_item_id"))
        add("locality", [r["item_id"]], r["prompt"], dict(true=_target(src["answer"], _lst(src.get("aliases"))) if src else None), r["item_id"], source_outside_item_id=r.get("source_outside_item_id"))
    for r in ep["near_miss"]["rows"]:
        add("near_miss_neighbour", [r["item_id"]], r["neighbour_prompt"], dict(true=_target(r.get("neighbour_answer"))), r["item_id"], family_key=r.get("family_key"), neighbour_item_id=r.get("neighbour_item_id"), edit_item_id=r.get("edit_item_id"), near_type=r.get("type"))
        add("near_miss_edit", [r["item_id"]], r["edit_prompt"], dict(new=_target(r.get("edit_answer"))), r["item_id"], family_key=r.get("family_key"), edit_item_id=r.get("edit_item_id"))
    for r in ep["revision"]["rows"]:
        v = r["versions"]
        tv = {f"v{x['version']}": _target(x["answer"], x.get("aliases")) for x in v}
        add("revision", [r["item_id"]], r["prompt"], tv, r["item_id"], subject=r.get("subject"), fact_id=r.get("fact_id"))
        for j, p in enumerate(_lst(r.get("paraphrases"))):
            add("revision_paraphrase", [r["item_id"], j], p, tv, r["item_id"], paraphrase_index=j, fact_id=r.get("fact_id"))
    for r in ep["unseen"]["rows"]:
        add("unseen", [r["item_id"]], r["prompt"], dict(new=_target(r["answer"], _lst(r.get("aliases")))), r["item_id"], subject=r.get("subject"), relation_id=r.get("relation_id"))
    if dataset == "mquake" and ep.get("composition", {}).get("rows"):
        stream_ids = {it["item_id"] for it in items}
        for c in ep["composition"]["rows"]:
            orig = c.get("orig", {})
            hops = len(orig.get("triples", [])) or None
            deps = [d.get("item_id") for d in c.get("dependencies", [])]
            for q_index, q in enumerate(c["questions"]):
                add("composition", [c["composition_id"], q_index], q,
                    dict(old=_target(c.get("answer"), c.get("answer_aliases")), new=_target(c.get("new_answer"), c.get("new_answer_aliases"))),
                    c["composition_id"], question_index=q_index, hop_count=hops, n_edits=len(deps), dependency_ids=deps,
                    dependencies_in_stream=sum(d in stream_ids for d in deps), case_id=c.get("case_id"))
    ids = [r["probe_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate probe id")
    summary = dict(dataset=dataset, n_items=len(items), n_probes=len(rows), by_family={}, payload=binding)
    for r in rows:
        summary["by_family"][r["family"]] = summary["by_family"].get(r["family"], 0) + 1
    return rows, summary


if __name__ == "__main__":  # quick inventory
    for ds in ("zsre", "counterfact", "mquake"):
        rows, s = build_probes(ds)
        print(json.dumps({k: v for k, v in s.items() if k != "payload"}))
