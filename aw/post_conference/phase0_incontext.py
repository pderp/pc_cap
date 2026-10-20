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
from aw.post_conference.common import EXT_DATA
from aw.post_conference.phase0_locality import stop_tokens
import re
import unicodedata


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t).casefold()).strip()


def prefix_match(generated, aliases) -> float:
    """1.0 if the normalised generation starts with a normalised alias at a word boundary (or equals it)."""
    if not isinstance(generated, str):
        return float("nan")
    g = _norm(generated)
    for a in aliases:
        a = _norm(str(a))
        if a and g.startswith(a) and (len(g) == len(a) or not g[len(a)].isalnum()):
            return 1.0
    return 0.0

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
                rows.append(dict(dataset=ds, arm=r["arm"], probe_id=r["probe_id"], family=r["family"], item_id=r.get("item_id"), target=tgt, nll_token=t["nll_token"], exact=g.get("exact", {}).get(tgt), generated=g.get("text"),
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
    atomic_parquet(DATA / "incontext.parquet", ic)
    gens = pd.read_parquet(EXT_DATA / "data" / "generations.parquet")
    gens = gens[(gens.horizon == HORIZON) | (gens.model == "frozen")]

    # cap seed means on the same probes for the comparison table
    caps = s[(s.model.isin(READERS)) & (s.status == "ok")][["dataset", "model", "probe_id", "family", "target", "nll_token", "exact"]].copy()
    caps = caps.merge(gens[["dataset", "model", "probe_id", "text"]], on=["dataset", "model", "probe_id"], how="left")
    caps["exact_prefix"] = [prefix_match(g, aliases.get((d, pid, t), [])) if isinstance(g, str) else np.nan for g, d, pid, t in zip(caps.text, caps.dataset, caps.probe_id, caps.target)]
    caps["rule"] = caps.model.str.split("_").str[0]
    caps["exact"] = caps.exact.astype(float)
    cm = caps.groupby(["dataset", "rule", "probe_id", "family", "target"]).agg(nll_token=("nll_token", "mean"), exact=("exact", "mean"), exact_prefix=("exact_prefix", "mean")).reset_index()
    fzg = gens[gens.model == "frozen"][["dataset", "probe_id", "text"]].drop_duplicates(["dataset", "probe_id"])
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
            rows.append(dict(dataset=ds, family=fam, target=tgt, arm="frozen", n=len(base_rows), mean_nll=base_rows.nll_token.mean(), cvar95=base_rows.nll_token.nlargest(k).mean(), exact=base_rows.exact.astype(float).mean(),
                             exact_prefix=np.nanmean([prefix_match(g, aliases.get((ds, pid, tgt), [])) if isinstance(g, str) else np.nan for g, pid in zip(bg.text, bg.probe_id)]), frac_worse_1nat=0.0, frac_severe=0.0, frac_better_1nat=0.0, retrieved_own_rate=np.nan))
            for arm in ("oracle", "knn", "lex"):
                x = ic[(ic.dataset == ds) & (ic.family == fam) & (ic.target == tgt) & (ic.arm == arm)]
                if not len(x):
                    continue
                rows.append(dict(dataset=ds, family=fam, target=tgt, arm=f"in-context {arm}", n=len(x), mean_nll=x.nll_token.mean(), cvar95=x.nll_token.nlargest(k).mean(), exact=x.exact.astype(float).mean(), exact_prefix=x.exact_prefix.astype(float).mean(),
                                 frac_worse_1nat=(x.D > 1).mean(), frac_severe=(x.D > SEVERE).mean(), frac_better_1nat=(x.D < -1).mean(), retrieved_own_rate=(x.retrieved_is_own.astype(float).mean() if x.retrieved_is_own.notna().any() else np.nan)))
            for rule, lab in (("bp", "BP-CAP seed mean"), ("epc", "PC-CAP seed mean")):
                x = cm[(cm.dataset == ds) & (cm.family == fam) & (cm.target == tgt) & (cm.rule == rule)]
                if not len(x):
                    continue
                rows.append(dict(dataset=ds, family=fam, target=tgt, arm=lab, n=len(x), mean_nll=x.nll_token.mean(), cvar95=x.nll_token.nlargest(k).mean(), exact=x.exact.mean(), exact_prefix=x.exact_prefix.mean(), frac_worse_1nat=(x.D > 1).mean(), frac_severe=(x.D > SEVERE).mean(), frac_better_1nat=(x.D < -1).mean(), retrieved_own_rate=np.nan))
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
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--datasets", default=",".join(DATASETS))
    a = ap.parse_args(argv)
    if a.execute:
        m = execute(a.datasets.split(","), a.limit)
        print(json.dumps({k: v.get("status") for k, v in m["cells"].items()}))
    if a.assemble:
        print(assemble())


if __name__ == "__main__":
    main()
