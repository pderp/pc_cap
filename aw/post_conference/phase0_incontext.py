"""Phase 0, item 3: the equal-information baseline — frozen GPT-2 small with the taught fact in its context.

Three retrieval arms, all forward-only on the frozen base, scored on the same 300-edit probes as the caps:

  oracle  the probe's own taught fact is prepended (item families; the dependency fact for MQuAKE composition).
          Collateral families get no context under the oracle (an oracle knows they are unrelated), i.e. frozen.
  knn     top-1 taught fact by cosine between frozen residual keys (LN0 features at blocks 4/8/12, last prompt
          position, the cap's own key feature) of the probe and of the 300 taught prompts; always prepended.
  lex     top-1 taught fact by IDF-weighted non-stop token overlap with the taught prompt; always prepended.

Each knn/lex probe also records its retrieval score and whether the retrieved item is its own item, so a retrieval
threshold can be swept on CPU exactly like the cap's null threshold (frontier module).

    python -m aw.post_conference.phase0_incontext --execute      # GPU, exclusive lease, ~40 min
    python -m aw.post_conference.phase0_incontext --assemble     # CPU: incontext.parquet, incontext_summary.csv
"""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter

import numpy as np
import pandas as pd

from aw.extremes.probes import build_probes
from aw.post_conference.common import CACHE, DATA, DATASETS, HORIZON, READERS, SEVERE, TABLES, Status, atomic_csv, atomic_json, atomic_parquet, ensure_dirs, frozen_losses, label, log_line, read_json, scores, sha
from aw.post_conference.common import EXT_DATA, prefix_match
from aw.post_conference.phase0_locality import stop_tokens

FAMILIES = ("edit", "paraphrase", "locality_item", "near_miss_neighbour", "unseen", "composition")
ITEM = ("edit", "paraphrase")


def fact_text(item: dict) -> str:
    sep = "" if item["prompt"][-1].isspace() else " "
    return f"{item['prompt']}{sep}{item['answer']}\n"


class Retriever:
    def __init__(self, base, tok, items: list[dict], stop: set[int]):
        from pccap.cap.features import z

        self.items = items
        self.tok = tok
        self.stop = stop
        self.base = base
        self.z = z
        self.keys = np.stack([self.key(it["prompt"]) for it in items])  # [n, 3d]
        self.keys /= np.linalg.norm(self.keys, axis=1, keepdims=True) + 1e-8
        self.toks = [set(tok.encode(it["prompt"])) - stop for it in items]
        df = Counter(t for ts in self.toks for t in ts)
        n = len(items)
        self.idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}

    def key(self, prompt: str) -> np.ndarray:
        ids = np.asarray(self.tok.encode(prompt), np.int32)
        fr = self.base.forward(ids, (), retain_sites=True, phase="query", last_only=True)
        parts = []
        for site in sorted(fr.sites, key=lambda s: s.bank):
            h = np.asarray(fr.sites[site], np.float32)
            h = h.reshape(-1, h.shape[-1])[-1]
            parts.append(self.z(h))
        return np.concatenate(parts)

    def knn(self, prompt: str) -> tuple[int, float]:
        q = self.key(prompt)
        q /= np.linalg.norm(q) + 1e-8
        c = self.keys @ q
        i = int(np.argmax(c))
        return i, float(c[i])

    def lex(self, prompt: str) -> tuple[int, float]:
        q = set(self.tok.encode(prompt)) - self.stop
        best, score = -1, -1.0
        for i, ts in enumerate(self.toks):
            sc = sum(self.idf.get(t, 0.0) for t in q & ts)
            if sc > score:
                best, score = i, sc
        return best, float(score)


def execute(datasets=DATASETS, limit: int | None = None) -> dict:
    import pccap  # noqa: F401  # isort: skip

    from aw.extremes import models as M
    from aw.extremes.score import score_probe
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    ensure_dirs()
    out = CACHE / "incontext"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else dict(cells={})
    stop = stop_tokens()
    t_all = time.monotonic()
    with gpu_lease("phase0 in-context baseline (frozen, forward-only)", stage="post_conference", projected_seconds=5400, exclusive=True) as lease:
        others = lease.other_cuda_processes()
        if blocking_cuda_processes(others):
            raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
        for ds in datasets:
            if manifest["cells"].get(ds, {}).get("status") == "complete":
                continue
            model, parent, tok, binding = M.load_frozen(ds)
            probes, _ = build_probes(ds)
            probes = [p for p in probes if p["family"] in FAMILIES and (p["family"] != "locality_item" or p["locality_index"] < 3)]
            if limit:
                probes = probes[:limit]
            items = [p for p in probes if p["family"] == "edit"]
            by_item = {it["item_id"]: it for it in items}
            facts = [dict(item_id=it["item_id"], prompt=it["prompt"], answer=it["targets"]["new"]["text"]) for it in items]
            ret = Retriever(model.base, tok, facts, stop)
            deps = {}
            if ds == "mquake":
                from aw.post_conference.phase0_composition import cases

                deps = {c["composition_id"]: (c["dep_items"][0]["item_id"] if c["dep_items"] and c["dep_items"][0] else None) for c in cases()}
            t0 = time.monotonic()
            lines = []
            for i, p in enumerate(probes):
                arms = []
                own = p.get("item_id") if p["family"] in ITEM else (deps.get(p["item_id"]) if p["family"] == "composition" else None)
                if own is not None and own in by_item:
                    arms.append(("oracle", by_item[own]["item_id"], float("nan"), fact_text(dict(prompt=by_item[own]["prompt"], answer=by_item[own]["targets"]["new"]["text"]))))
                ki, ks = ret.knn(p["prompt"])
                arms.append(("knn", facts[ki]["item_id"], ks, fact_text(facts[ki])))
                li, lsc = ret.lex(p["prompt"])
                if li >= 0:
                    arms.append(("lex", facts[li]["item_id"], lsc, fact_text(facts[li])))
                for arm, rid, score, ctx in arms:
                    pr = dict(p, prompt=ctx + p["prompt"])
                    rec = score_probe(model, tok, pr, None, None)
                    rec.update(arm=arm, retrieved_item=rid, retrieval_score=score, retrieved_is_own=(rid == own) if own is not None else None, context=ctx, prompt=p["prompt"], stream_index=p.get("stream_index"))
                    lines.append(json.dumps(rec, ensure_ascii=False))
                if (i + 1) % 200 == 0:
                    log_line("incontext", f"{ds} {i + 1}/{len(probes)} {time.monotonic() - t0:.0f}s")
            path = out / f"{ds}.jsonl"
            path.write_text("\n".join(lines) + "\n")
            manifest["cells"][ds] = dict(status="complete", n_probes=len(probes), n_rows=len(lines), sha256=sha(path), base_sha256=model.checksum(), recipe=binding, elapsed=time.monotonic() - t0)
            atomic_json(manifest_path, manifest)
            del model, parent, ret
    manifest.update(elapsed_total=time.monotonic() - t_all, other_cuda_processes=others)
    atomic_json(manifest_path, manifest)
    return manifest


def execute_matched(models=READERS, datasets=DATASETS, limit: int | None = None) -> dict:
    """Matched comparator (Capex §6): for every probe on which a reader fired, place the record it applied (its taught
    fact) in frozen GPT-2's context; abstentions keep the frozen answer by construction. Per-probe wall time recorded."""
    import pccap  # noqa: F401  # isort: skip

    from aw.extremes import models as M
    from aw.extremes.score import score_probe
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    ensure_dirs()
    out = CACHE / "incontext_matched"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else dict(cells={})
    sel = pd.read_parquet(DATA / "selection_table.parquet")
    t_all = time.monotonic()
    with gpu_lease("phase0 matched in-context comparator (frozen, forward-only)", stage="post_conference", projected_seconds=3600, exclusive=True) as lease:
        others = lease.other_cuda_processes()
        if blocking_cuda_processes(others):
            raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
        for ds in datasets:
            model, parent, tok, binding = M.load_frozen(ds)
            probes, _ = build_probes(ds)
            probes = [p for p in probes if p["family"] in FAMILIES and (p["family"] != "locality_item" or p["locality_index"] < 3)]
            by_id = {p["probe_id"]: p for p in probes}
            items = {p["item_id"]: dict(item_id=p["item_id"], prompt=p["prompt"], answer=p["targets"]["new"]["text"]) for p in probes if p["family"] == "edit"}
            for reader in models:
                key = f"{reader}/{ds}"
                if manifest["cells"].get(key, {}).get("status") == "complete":
                    continue
                fired = sel[(sel.model == reader) & (sel.dataset == ds) & (~sel.hard_null.astype(bool)) & (sel.family != "composition")]
                if limit:
                    fired = fired.head(limit)
                t0 = time.monotonic()
                lines = []
                for r in fired.itertuples(index=False):
                    p = by_id.get(r.probe_id)
                    rid = str(r.top_record)
                    item = next((it for iid, it in items.items() if (":" + iid + ":") in rid), None)
                    if p is None or item is None:
                        continue
                    ctx = fact_text(item)
                    t1 = time.monotonic()
                    rec = score_probe(model, tok, dict(p, prompt=ctx + p["prompt"]), None, None)
                    rec.update(arm="matched", reader=reader, retrieved_item=item["item_id"], retrieved_is_own=(item["item_id"] == p.get("item_id")), context=ctx, prompt=p["prompt"], wall_seconds=time.monotonic() - t1, context_tokens=len(tok.encode(ctx)))
                    lines.append(json.dumps(rec, ensure_ascii=False))
                d = out / reader
                d.mkdir(parents=True, exist_ok=True)
                (d / f"{ds}.jsonl").write_text("\n".join(lines) + ("\n" if lines else ""))
                manifest["cells"][key] = dict(status="complete", n_rows=len(lines), sha256=sha(d / f"{ds}.jsonl"), elapsed=time.monotonic() - t0)
                atomic_json(manifest_path, manifest)
                log_line("incontext", f"matched {key} n={len(lines)} {time.monotonic() - t0:.0f}s")
            del model, parent
    manifest.update(elapsed_total=time.monotonic() - t_all, other_cuda_processes=others, base_sha256=binding.get("sha256") if isinstance(binding, dict) else None)
    atomic_json(manifest_path, manifest)
    return manifest


def assemble() -> dict:
    ensure_dirs()
    out = CACHE / "incontext"
    manifest = read_json(out / "manifest.json")
    rows = []
    for ds, cell in manifest["cells"].items():
        for line in (out / f"{ds}.jsonl").read_text().splitlines():
            r = json.loads(line)
            g = r.get("generation") or {}
            for tgt, t in r["targets"].items():
                if t.get("status") != "ok":
                    continue
                rows.append(dict(dataset=ds, arm=r["arm"], probe_id=r["probe_id"], family=r["family"], item_id=r.get("item_id"), prompt_tokens=r["prompt_tokens"], target=tgt, nll_token=t["nll_token"], nll_noterm=t.get("nll_token_no_terminator"), exact=g.get("exact", {}).get(tgt), generated=g.get("text"),
                                 retrieved_item=r["retrieved_item"], retrieval_score=r["retrieval_score"], retrieved_is_own=r["retrieved_is_own"], stream_index=r.get("stream_index")))
    ic = pd.DataFrame(rows)
    s = scores(HORIZON)
    fz = frozen_losses(s)
    ic = ic.merge(fz, on=["dataset", "probe_id", "target"], how="left")
    ic["D"] = ic.nll_token - ic.L_frozen
    # prefix exact match: the strict metric stops the generation at a newline, which a one-shot context often suppresses
    # (the model continues with another question); credit a generation that *starts* with an alias, for every arm alike.
    aliases = {}
    for ds in DATASETS:
        for p in build_probes(ds)[0]:
            for tgt, t in p["targets"].items():
                aliases[(ds, p["probe_id"], tgt)] = list(t.get("aliases") or [t["text"]])
    ic["exact_prefix"] = [prefix_match(g, aliases.get((d, pid, t), [])) for g, d, pid, t in zip(ic.generated, ic.dataset, ic.probe_id, ic.target)]
    ptok = s[s.model == "frozen"][["dataset", "probe_id", "prompt_tokens"]].drop_duplicates(["dataset", "probe_id"]).rename(columns={"prompt_tokens": "probe_tokens"})
    ic = ic.merge(ptok, on=["dataset", "probe_id"], how="left")
    ic["context_tokens"] = ic.prompt_tokens - ic.probe_tokens
    atomic_parquet(DATA / "incontext.parquet", ic)
    # matched comparator rows (one per reader): fired probes carry the in-context result, abstained ones the frozen result
    mrows = []
    mout = CACHE / "incontext_matched"
    if (mout / "manifest.json").exists():
        for key in read_json(mout / "manifest.json")["cells"]:
            reader, ds = key.split("/")
            path = mout / reader / f"{ds}.jsonl"
            for line in path.read_text().splitlines():
                r = json.loads(line)
                g = r.get("generation") or {}
                for tgt, t in r["targets"].items():
                    if t.get("status") != "ok":
                        continue
                    mrows.append(dict(dataset=ds, reader=reader, rule=reader.split("_")[0], probe_id=r["probe_id"], family=r["family"], target=tgt, nll_token=t["nll_token"], nll_noterm=t.get("nll_token_no_terminator"), exact=g.get("exact", {}).get(tgt), generated=g.get("text"),
                                      retrieved_is_own=r["retrieved_is_own"], wall_seconds=r["wall_seconds"], context_tokens=r["context_tokens"]))
    matched = pd.DataFrame(mrows)
    if len(matched):
        matched["exact_prefix"] = [prefix_match(g, aliases.get((d, pid, t), [])) for g, d, pid, t in zip(matched.generated, matched.dataset, matched.probe_id, matched.target)]
        matched = matched.merge(fz, on=["dataset", "probe_id", "target"], how="left")
        matched["D"] = matched.nll_token - matched.L_frozen
        atomic_parquet(DATA / "incontext_matched.parquet", matched)
    gens = pd.read_parquet(EXT_DATA / "data" / "generations.parquet")
    gens = gens[(gens.horizon == HORIZON) | (gens.model == "frozen")]

    # cap seed means on the same probes for the comparison table
    caps = s[(s.model.isin(READERS)) & (s.status == "ok")][["dataset", "model", "probe_id", "family", "target", "nll_token", "nll_token_no_terminator", "exact"]].copy().rename(columns={"nll_token_no_terminator": "nll_noterm"})
    caps = caps.merge(gens[["dataset", "model", "probe_id", "text"]], on=["dataset", "model", "probe_id"], how="left")
    caps["exact_prefix"] = [prefix_match(g, aliases.get((d, pid, t), [])) if isinstance(g, str) else np.nan for g, d, pid, t in zip(caps.text, caps.dataset, caps.probe_id, caps.target)]
    caps["rule"] = caps.model.str.split("_").str[0]
    caps["exact"] = caps.exact.astype(float)
    cm = caps.groupby(["dataset", "rule", "probe_id", "family", "target"]).agg(nll_token=("nll_token", "mean"), nll_noterm=("nll_noterm", "mean"), exact=("exact", "mean"), exact_prefix=("exact_prefix", "mean")).reset_index()
    fzg = gens[gens.model == "frozen"][["dataset", "probe_id", "text"]].drop_duplicates(["dataset", "probe_id"])
    sel_fired = pd.read_parquet(DATA / "selection_table.parquet")
    sel_fired = sel_fired[~sel_fired.hard_null.astype(bool)]
    cm = cm.merge(fz, on=["dataset", "probe_id", "target"], how="left")
    cm["D"] = cm.nll_token - cm.L_frozen
    rows = []
    for fam, tgt in (("edit", "new"), ("paraphrase", "new"), ("locality_item", "true"), ("near_miss_neighbour", "true"), ("unseen", "new"), ("composition", "new")):
        for ds in DATASETS:
            f = fz[(fz.dataset == ds)]
            base_rows = s[(s.model == "frozen") & (s.dataset == ds) & (s.family == fam) & (s.target == tgt) & (s.status == "ok")]
            if not len(base_rows):
                continue
            k = max(1, int(np.ceil(0.05 * len(base_rows))))
            bg = base_rows.merge(fzg, on=["dataset", "probe_id"], how="left")
            rows.append(dict(dataset=ds, family=fam, target=tgt, arm="frozen", n=len(base_rows), context_tokens=0.0, mean_nll=base_rows.nll_token.mean(), mean_nll_noterm=base_rows.nll_token_no_terminator.mean(), cvar95=base_rows.nll_token.nlargest(k).mean(), exact=base_rows.exact.astype(float).mean(),
                             exact_prefix=np.nanmean([prefix_match(g, aliases.get((ds, pid, tgt), [])) if isinstance(g, str) else np.nan for g, pid in zip(bg.text, bg.probe_id)]), frac_worse_1nat=0.0, frac_severe=0.0, frac_better_1nat=0.0, retrieved_own_rate=np.nan))
            for arm in ("oracle", "knn", "lex"):
                x = ic[(ic.dataset == ds) & (ic.family == fam) & (ic.target == tgt) & (ic.arm == arm)]
                if not len(x):
                    continue
                rows.append(dict(dataset=ds, family=fam, target=tgt, arm=f"in-context {arm}", n=len(x), context_tokens=x.context_tokens.mean(), mean_nll=x.nll_token.mean(), mean_nll_noterm=x.nll_noterm.mean(), cvar95=x.nll_token.nlargest(k).mean(), exact=x.exact.astype(float).mean(), exact_prefix=x.exact_prefix.astype(float).mean(),
                                 frac_worse_1nat=(x.D > 1).mean(), frac_severe=(x.D > SEVERE).mean(), frac_better_1nat=(x.D < -1).mean(), retrieved_own_rate=(x.retrieved_is_own.astype(float).mean() if x.retrieved_is_own.notna().any() else np.nan)))
            # matched comparator: per reader, fired probes from the in-context run, abstained probes = frozen; then seed mean
            if len(matched):
                for rule, lab in (("bp", "matched in-context (BP-CAP's records) seed mean"), ("epc", "matched in-context (PC-CAP's records) seed mean")):
                    per = []
                    for reader in [m for m in READERS if m.startswith(rule)]:
                        fired_sel = sel_fired[(sel_fired.model == reader) & (sel_fired.dataset == ds)]
                        all_probes = base_rows[["probe_id", "nll_token", "nll_token_no_terminator", "exact"]].copy()
                        mm = matched[(matched.reader == reader) & (matched.dataset == ds) & (matched.family == fam) & (matched.target == tgt)].set_index("probe_id")
                        all_probes["L"] = [mm.nll_token.get(pid, l) for pid, l in zip(all_probes.probe_id, all_probes.nll_token)]
                        all_probes["Ln"] = [mm.nll_noterm.get(pid, l) for pid, l in zip(all_probes.probe_id, all_probes.nll_token_no_terminator)]
                        all_probes["X"] = [mm.exact_prefix.get(pid, float(bool(e))) for pid, e in zip(all_probes.probe_id, all_probes.exact)]
                        all_probes["ctx"] = [mm.context_tokens.get(pid, 0.0) for pid in all_probes.probe_id]
                        all_probes["fired"] = all_probes.probe_id.isin(mm.index)
                        per.append(all_probes)
                    if not per:
                        continue
                    pm = pd.concat(per).groupby("probe_id").agg(L=("L", "mean"), Ln=("Ln", "mean"), X=("X", "mean"), ctx=("ctx", "mean"), fired=("fired", "mean"), L0=("nll_token", "first")).reset_index()
                    Dm = pm.L - pm.L0
                    rows.append(dict(dataset=ds, family=fam, target=tgt, arm=lab, n=len(pm), context_tokens=pm.ctx.mean(), mean_nll=pm.L.mean(), mean_nll_noterm=pm.Ln.mean(), cvar95=pm.L.nlargest(k).mean(), exact=np.nan, exact_prefix=pm.X.mean(),
                                     frac_worse_1nat=(Dm > 1).mean(), frac_severe=(Dm > SEVERE).mean(), frac_better_1nat=(Dm < -1).mean(), retrieved_own_rate=np.nan, fire_rate=pm.fired.mean(),
                                     wall_seconds_per_fired_query=matched[(matched.rule == rule) & (matched.dataset == ds) & (matched.family == fam)].wall_seconds.mean()))
            for rule, lab in (("bp", "BP-CAP seed mean"), ("epc", "PC-CAP seed mean")):
                x = cm[(cm.dataset == ds) & (cm.family == fam) & (cm.target == tgt) & (cm.rule == rule)]
                if not len(x):
                    continue
                rows.append(dict(dataset=ds, family=fam, target=tgt, arm=lab, n=len(x), context_tokens=0.0, mean_nll=x.nll_token.mean(), mean_nll_noterm=x.nll_noterm.mean(), cvar95=x.nll_token.nlargest(k).mean(), exact=x.exact.mean(), exact_prefix=x.exact_prefix.mean(), frac_worse_1nat=(x.D > 1).mean(), frac_severe=(x.D > SEVERE).mean(), frac_better_1nat=(x.D < -1).mean(), retrieved_own_rate=np.nan))
    summ = pd.DataFrame(rows)
    atomic_csv(TABLES / "incontext_summary.csv", summ)

    # retrieval-threshold frontier for knn / lex: prepend only when the retrieval score is at least theta
    rows = []
    for arm, grid in (("knn", np.round(np.linspace(0.0, 1.0, 21), 3)), ("lex", [0, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10])):
        for ds in DATASETS:
            x = ic[(ic.dataset == ds) & (ic.arm == arm)]
            if not len(x):
                continue
            for th in grid:
                use = x.retrieval_score >= th
                L = np.where(use, x.nll_token, x.L_frozen)
                X = np.where(use, x.exact_prefix.astype(float), x.X_frozen.astype(float))  # prefix match (see above); frozen strict and prefix coincide on these probes
                D = L - x.L_frozen.values
                row = dict(dataset=ds, arm=arm, theta=float(th))
                for fam, tgt in (("paraphrase", "new"), ("near_miss_neighbour", "true"), ("unseen", "new"), ("locality_item", "true"), ("composition", "new")):
                    m = ((x.family == fam) & (x.target == tgt)).values
                    if not m.any():
                        continue
                    k = max(1, int(np.ceil(0.05 * m.sum())))
                    row.update({f"{fam}_fire_rate": float(use.values[m].mean()), f"{fam}_mean_nll": float(L[m].mean()), f"{fam}_cvar95": float(np.sort(L[m])[-k:].mean()), f"{fam}_exact": float(np.nanmean(X[m])), f"{fam}_frac_worse_1nat": float((D[m] > 1).mean()), f"{fam}_frac_severe": float((D[m] > SEVERE).mean())})
                rows.append(row)
    atomic_csv(TABLES / "incontext_frontier.csv", pd.DataFrame(rows))
    st = Status()
    for name in ("incontext_summary", "incontext_frontier"):
        st.artifact(f"tables/{name}", TABLES / f"{name}.csv")
    st.artifact("data/incontext", DATA / "incontext.parquet")
    st.stage("incontext", "complete", cells=list(manifest["cells"]))
    return dict(rows=len(ic))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--matched", action="store_true", help="run the matched comparator (cap-applied record in context) on the GPU")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--datasets", default=",".join(DATASETS))
    a = ap.parse_args(argv)
    if a.execute:
        m = execute(a.datasets.split(","), a.limit)
        print(json.dumps({k: v.get("status") for k, v in m["cells"].items()}))
    if a.matched:
        m = execute_matched(datasets=a.datasets.split(","), limit=a.limit)
        print(json.dumps({k: v.get("status") for k, v in m["cells"].items()}))
    if a.assemble:
        print(assemble())


if __name__ == "__main__":
    main()
