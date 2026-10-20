"""Phase 0, item 5: why multi-hop composition scores zero (CPU part + forward-only GPU part).

Facts established from the payload: 78 of the 80 MQuAKE composition cases have exactly one dependency in the 300-edit
stream (one taught fact); the other hop is an unedited fact the frozen base must supply itself. So "chaining between
two memory records" is not the question. The question is which link breaks:

  (a) does the reader retrieve the dependency record on the multi-hop wording, and does the gate let it fire?   [CPU]
  (b) when it fires, does applying the taught delta change the composed answer at all?                            [CPU]
  (c) does frozen GPT-2 small know the second hop when the new first-hop entity is given explicitly?               [GPU]
  (d) can frozen GPT-2 small compose when the taught fact is placed in its context (in-context ceiling)?          [GPU]

CPU: python -m aw.post_conference.phase0_composition
GPU: python -m aw.post_conference.phase0_composition --execute   (frozen base only, forward-only)
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd

from aw.extremes.probes import build_probes, load_payload
from aw.post_conference.common import ASSETS, CACHE, DATA, HORIZON, READERS, TABLES, Status, atomic_csv, atomic_json, atomic_parquet, ensure_dirs, frozen_losses, label, log_line, read_json, rule_of, scores

RAW = ASSETS / "data/raw/mquake/MQuAKE-CF.json"


def cases() -> list[dict]:
    pay, _ = load_payload("mquake")
    items = {it["item_id"]: it for it in pay["items"][:300]}
    out = []
    for c in pay["endpoints"]["composition"]["rows"]:
        deps = [d for d in c["dependencies"]]
        out.append(dict(composition_id=c["composition_id"], case_id=c.get("case_id"), questions=c["questions"], answer=c.get("answer"), answer_aliases=c.get("answer_aliases") or [], new_answer=c.get("new_answer"),
                        new_answer_aliases=c.get("new_answer_aliases") or [], hops=len(c.get("orig", {}).get("triples", [])), n_deps=len(deps), deps=deps, dep_items=[items.get(d["item_id"]) for d in deps],
                        new_triples_labeled=c.get("orig", {}).get("new_triples_labeled"), triples_labeled=c.get("orig", {}).get("triples_labeled")))
    return out


def match_raw(case: dict, raw_by_id: dict) -> dict | None:
    """The raw MQuAKE-CF case whose requested rewrite matches the dependency (subject + target_new)."""
    r = raw_by_id.get(case["case_id"])
    dep = case["deps"][0] if case["deps"] else None
    if r is None or dep is None:
        return None
    rw = r.get("requested_rewrite", [])
    ok = any(str(x.get("subject", "")).lower() == str(dep.get("subject_key", "")).lower() and str(x.get("target_new", {}).get("str", "")) == str(dep.get("required_target_new", {}).get("str", "")) for x in rw)
    return r if ok else None


def cpu() -> dict:
    ensure_dirs()
    s = scores(HORIZON)
    sel = pd.read_parquet(DATA / "selection_table.parquet")
    fz = frozen_losses(s)
    cs = {c["composition_id"]: c for c in cases()}
    comp = s[(s.dataset == "mquake") & (s.family == "composition") & (s.model.isin(READERS)) & (s.status == "ok")].merge(fz, on=["dataset", "probe_id", "target"], how="left")
    comp = comp.merge(sel[["model", "dataset", "probe_id", "record_ids", "weights", "top_record", "veto", "n_candidates"]], on=["model", "dataset", "probe_id"], how="left")

    def dep_hit(row):
        deps = [d["item_id"] for d in cs[row.item_id]["deps"]]
        rids = json.loads(row.record_ids) if isinstance(row.record_ids, str) else []
        return any((":" + d + ":") in rid for rid in rids for d in deps)

    def dep_top(row):
        deps = [d["item_id"] for d in cs[row.item_id]["deps"]]
        return any((":" + d + ":") in str(row.top_record) for d in deps)

    comp["dependency_retrieved"] = comp.apply(dep_hit, axis=1)
    comp["dependency_is_top"] = comp.apply(dep_top, axis=1)
    comp["fired"] = comp.fired.astype(bool)
    comp["D"] = comp.nll_token - comp.L_frozen
    rows = []
    for (model, target), x in comp.groupby(["model", "target"]):
        f = x[x.fired]
        rows.append(dict(model=model, rule=rule_of(model), label=label(model), target=target, n_questions=len(x), dependency_retrieved_rate=x.dependency_retrieved.mean(), dependency_top_rate=x.dependency_is_top.mean(), fired_rate=x.fired.mean(),
                         fired_on_dependency=int((f.dependency_is_top).sum()), fired_on_other=int((~f.dependency_is_top).sum()), abstain_threshold=int((x.veto == "null_threshold").sum()), abstain_rare_veto=int((x.veto == "rare_token_veto").sum()),
                         exact_rate=x.exact.astype(bool).mean(), exact_fired=(f.exact.astype(bool).mean() if len(f) else np.nan), mean_nll=x.nll_token.mean(), mean_nll_frozen=x.L_frozen.mean(),
                         mean_D_fired=(f.D.mean() if len(f) else np.nan), frac_changed_when_fired=((f.D.abs() > 1e-3).mean() if len(f) else np.nan), frac_improved_gt1_when_fired=((f.D < -1).mean() if len(f) else np.nan)))
    t = pd.DataFrame(rows)
    atomic_csv(TABLES / "composition_retrieval.csv", t)
    atomic_csv(TABLES / "composition_questions.csv", comp[["model", "target", "probe_id", "item_id", "question_index", "hop_count", "fired", "veto", "null_mass", "dependency_retrieved", "dependency_is_top", "top_record", "nll_token", "L_frozen", "D", "exact"]])
    st = Status()
    st.artifact("tables/composition_retrieval", TABLES / "composition_retrieval.csv")
    st.artifact("tables/composition_questions", TABLES / "composition_questions.csv")
    st.stage("composition_cpu", "complete")
    return dict(rows=len(t))


# ------------------------------------------------------------------------------------------------------ GPU part
def gpu_probes() -> list[dict]:
    """Frozen-base probes: hop-2 single-hop questions (cloze + question form) with the new entity, and the multi-hop
    questions with the taught fact in context."""
    raw_by_id = {r["case_id"]: r for r in json.loads(RAW.read_bytes())}
    out = []
    for c in cases():
        r = match_raw(c, raw_by_id)
        dep = c["dep_items"][0] if c["dep_items"] and c["dep_items"][0] else None
        fact = None
        if dep:
            sep = "" if dep["prompt"][-1].isspace() else " "
            fact = f"{dep['prompt']}{sep}{dep['answer']}\n"
        for qi, q in enumerate(c["questions"]):
            base = dict(composition_id=c["composition_id"], case_id=c["case_id"], question_index=qi, hops=c["hops"], raw_matched=r is not None)
            if fact:
                out.append(dict(base, kind="multihop_in_context", prompt=fact + q, targets=dict(new=dict(text=c["new_answer"], aliases=[c["new_answer"]] + list(c["new_answer_aliases"])), old=dict(text=c["answer"], aliases=[c["answer"]] + list(c["answer_aliases"])))))
        if r is not None:
            nsh = r.get("new_single_hops", [])
            # the edited hop is the one whose answer equals the dependency's target_new; later hops use the new entity chain
            for hi, h in enumerate(nsh):
                edited = str(h.get("answer")) == str(c["deps"][0].get("required_target_new", {}).get("str"))
                base = dict(composition_id=c["composition_id"], case_id=c["case_id"], question_index=hi, hops=c["hops"], raw_matched=True, hop_index=hi, hop_is_edited=edited)
                tgt = dict(new=dict(text=h["answer"], aliases=[h["answer"]] + list(h.get("answer_alias", []))))
                out.append(dict(base, kind="single_hop_cloze", prompt=h["cloze"], targets=tgt))
                out.append(dict(base, kind="single_hop_question", prompt=h["question"], targets=tgt))
    return out


def execute(limit: int | None = None) -> dict:
    import pccap  # noqa: F401  # isort: skip

    from aw.extremes import models as M
    from aw.extremes.score import score_probe
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    ensure_dirs()
    probes = gpu_probes()
    if limit:
        probes = probes[:limit]
    out = CACHE / "composition"
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    with gpu_lease("phase0 composition (frozen, forward-only)", stage="post_conference", projected_seconds=1800, exclusive=True) as lease:
        others = lease.other_cuda_processes()
        if blocking_cuda_processes(others):
            raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
        model, parent, tok, binding = M.load_frozen("mquake")
        lines = []
        for i, p in enumerate(probes):
            pr = dict(p, probe_id=f"comp:{p['kind']}:{p['composition_id']}:{p['question_index']}", family="composition", item_id=p["composition_id"])
            rec = score_probe(model, tok, pr, None, None)
            rec.update(kind=p["kind"], composition_id=p["composition_id"], case_id=p["case_id"], question_index=p["question_index"], hops=p["hops"], hop_index=p.get("hop_index"), hop_is_edited=p.get("hop_is_edited"), prompt=p["prompt"])
            lines.append(json.dumps(rec, ensure_ascii=False))
            if (i + 1) % 100 == 0:
                log_line("composition", f"{i + 1}/{len(probes)} {time.monotonic() - t0:.0f}s")
        digest = (out / "frozen.jsonl").write_text("\n".join(lines) + "\n")
    manifest = dict(n_probes=len(probes), base_sha256=model.checksum(), recipe=binding, elapsed_process_seconds=time.monotonic() - t0, other_cuda_processes=others)
    atomic_json(out / "manifest.json", manifest)
    return manifest


def assemble_gpu() -> dict:
    out = CACHE / "composition"
    rows = []
    for line in (out / "frozen.jsonl").read_text().splitlines():
        r = json.loads(line)
        g = r.get("generation") or {}
        for key, t in r["targets"].items():
            if t.get("status") != "ok":
                continue
            rows.append(dict(kind=r["kind"], composition_id=r["composition_id"], case_id=r["case_id"], question_index=r["question_index"], hops=r["hops"], hop_index=r.get("hop_index"), hop_is_edited=r.get("hop_is_edited"), prompt=r["prompt"], target=key,
                             target_text=t["text"], nll_token=t["nll_token"], exact=g.get("exact", {}).get(key), generated=g.get("text")))
    f = pd.DataFrame(rows)
    atomic_parquet(DATA / "composition_frozen.parquet", f)
    summ = []
    for (kind, target), x in f.groupby(["kind", "target"]):
        summ.append(dict(kind=kind, target=target, n=len(x), exact=x.exact.astype(float).mean(), mean_nll=x.nll_token.mean(), median_nll=x.nll_token.median(), n_cases=x.composition_id.nunique()))
    # unedited hops only (hop-2 knowledge of the frozen base), edited hop separately
    for kind in ("single_hop_cloze", "single_hop_question"):
        for edited in (False, True):
            x = f[(f.kind == kind) & (f.hop_is_edited == edited)]
            if len(x):
                summ.append(dict(kind=kind + (" (edited hop)" if edited else " (unedited hop)"), target="new", n=len(x), exact=x.exact.astype(float).mean(), mean_nll=x.nll_token.mean(), median_nll=x.nll_token.median(), n_cases=x.composition_id.nunique()))
    # cases where frozen knows every unedited hop: upper bound on composition reachable by fixing hop 1
    un = f[(f.kind == "single_hop_cloze") & (f.hop_is_edited == False)]  # noqa: E712
    per_case = un.groupby("composition_id").exact.apply(lambda v: bool(np.all(v.astype(bool)))) if len(un) else pd.Series(dtype=bool)
    ic = f[(f.kind == "multihop_in_context") & (f.target == "new")]
    summ.append(dict(kind="cases whose unedited hops frozen GPT-2 answers exactly (cloze)", target="new", n=int(per_case.sum()) if len(per_case) else 0, exact=np.nan, mean_nll=np.nan, median_nll=np.nan, n_cases=int(len(per_case))))
    if len(ic):
        any_case = ic.groupby("composition_id").exact.apply(lambda v: bool(np.any(v.astype(bool))))
        all_case = ic.groupby("composition_id").exact.apply(lambda v: bool(np.all(v.astype(bool))))
        summ.append(dict(kind="multihop_in_context: any question correct (case level)", target="new", n=int(any_case.sum()), exact=any_case.mean(), mean_nll=np.nan, median_nll=np.nan, n_cases=int(len(any_case))))
        summ.append(dict(kind="multihop_in_context: all three correct (case level)", target="new", n=int(all_case.sum()), exact=all_case.mean(), mean_nll=np.nan, median_nll=np.nan, n_cases=int(len(all_case))))
    t = pd.DataFrame(summ)
    atomic_csv(TABLES / "composition_frozen_ceiling.csv", t)
    st = Status()
    st.artifact("tables/composition_frozen_ceiling", TABLES / "composition_frozen_ceiling.csv")
    st.artifact("data/composition_frozen", DATA / "composition_frozen.parquet")
    st.stage("composition_gpu", "complete", manifest=read_json(CACHE / "composition" / "manifest.json"))
    return dict(rows=len(f))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="run the forward-only frozen-base probes on the GPU")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args(argv)
    if a.execute:
        print(json.dumps(execute(a.limit), indent=1, default=str))
    if a.assemble:
        print(assemble_gpu())
    if not (a.execute or a.assemble):
        print(cpu())


if __name__ == "__main__":
    main()
