"""Phase 0, item 1: are the BP and PC readers on the same gate frontier? (saved scores + forward-only replay)

The registered gate fires when the reader's null mass is below 0.5 and the rare-token veto passes. Lowering the
threshold needs no GPU: a probe that stops firing scores exactly as the frozen model (abstained read = base logits).
Raising it needs the loss the cap *would* have produced on the probes it abstained from: this module replays those
probes with the null threshold removed (rare-token veto kept, because it is independent of the threshold), on the
restored 300-edit memory of each reader. One replay per reader/dataset gives every threshold in [0, 1].

A second replay forces the item's own record on paraphrases whose own record was not the applied record (the
review's oracle diagnostic: item identity picks the record, nothing about the answer enters prediction).

    python -m aw.post_conference.phase0_frontier --execute        # GPU, exclusive lease, ~1 h
    python -m aw.post_conference.phase0_frontier --assemble       # CPU: replay.parquet, frontier.csv, oracle_rescue.csv
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd

from aw.extremes.probes import build_probes
from aw.post_conference.common import CACHE, DATA, DATASETS, HORIZON, NULL_THRESHOLD, READERS, SEVERE, TABLES, Status, atomic_csv, atomic_json, atomic_parquet, ensure_dirs, frozen_losses, label, log_line, own_record_id, read_json, rule_of, scores, sha

REPLAY_FAMILIES = ("paraphrase", "near_miss_neighbour", "unseen", "locality_item", "composition")
TAUS = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
VALIDATE_N = 12


def _forced_select(cap, mode: str):
    """Wrap the reader's selection: 'force' ignores the null threshold (rare veto kept); 'oracle' applies the record of
    cap._oracle_item regardless of the gate."""
    from pccap.revision_v1.learner import Selection

    orig = cap._select

    def select(prompt):
        sel = orig(prompt)
        if mode == "force":
            if not sel.hard_null or not sel.record_ids or sel.null_mass < NULL_THRESHOLD:
                return sel  # fired already, nothing retrieved, or stopped by the rare-token veto (threshold-independent)
            i = int(np.argmax(sel.weights))
            rid = sel.record_ids[i]
            # The learner evaluates the rare-token gate only after the null gate passes (Capex review §2.2): apply it here,
            # so a relaxed threshold never accepts a query the registered rare-token veto would have stopped.
            rec0 = cap.store.get(rid)
            if cap.cfg.rare_overlap_min and (rec0.source_ids is None or cap._rare_overlap(prompt, rec0.source_ids) < cap.cfg.rare_overlap_min):
                sel.rare_veto_after_null = True
                return sel
        else:
            rid = own_record_id(cap.store, None, cap._oracle_item)
            if rid is None:
                return sel
            if not sel.hard_null and sel.record_ids and sel.record_ids[int(np.argmax(sel.weights))] == rid:
                return sel  # already applied the own record
        rec = cap.store.get(rid)
        w = np.zeros(1, np.float32) + 1.0
        return Selection(sel.prompt_len, [rid], w, sel.null_mass, np.asarray(rec.code, np.float32), False, prompt_pass=sel.prompt_pass, best_score=sel.best_score, pending_cost=sel.pending_cost, delta=rec.delta)

    cap._select = select
    return orig


def plan(sel_table: pd.DataFrame, s: pd.DataFrame) -> dict:
    """Which probes each replay needs, from the saved selection fields."""
    out = {}
    for model in READERS:
        for ds in DATASETS:
            t = sel_table[(sel_table.model == model) & (sel_table.dataset == ds) & (sel_table.family.isin(REPLAY_FAMILIES))]
            force = t[(t.veto == "null_threshold")].probe_id.tolist()
            para = t[(t.family == "paraphrase")]
            # every paraphrase whose *applied* record is not the own record: fired on a wrong record, or abstained (any gate)
            oracle = para[~((para.veto == "fired") & para.own_is_top.astype(bool))].probe_id.tolist()
            fired = t[(t.veto == "fired") & (t.family == "paraphrase")].probe_id.tolist()
            rng = np.random.default_rng(20261020)
            validate = list(rng.choice(fired, size=min(VALIDATE_N, len(fired)), replace=False)) if fired else []
            out[(model, ds)] = dict(force=force, oracle=oracle, validate=validate)
    return out


def execute(models=READERS, datasets=DATASETS, limit: int | None = None, oracle_only: bool = False) -> dict:
    import pccap  # noqa: F401  # isort: skip

    from aw.extremes import models as M
    from aw.extremes.score import score_probe, selection_view
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    ensure_dirs()
    s = scores(HORIZON)
    sel_table = pd.read_parquet(DATA / "selection_table.parquet")
    todo = plan(sel_table, s)
    out = CACHE / "replay"
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else dict(cells={}, started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    t_all = time.monotonic()
    with gpu_lease("phase0 frontier replay (forward-only)", stage="post_conference", projected_seconds=7200, exclusive=True) as lease:
        others = lease.other_cuda_processes()
        if blocking_cuda_processes(others):
            raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
        for ds in datasets:
            probes, _ = build_probes(ds)
            probes = [p for p in probes if p["family"] != "locality_item" or p["locality_index"] < 3]
            by_id = {p["probe_id"]: p for p in probes}
            parent = None
            for model in models:
                key = f"{model}/{ds}"
                if manifest["cells"].get(key, {}).get("status") == "complete" and not oracle_only:
                    continue
                rule, seed = model.split("_reader_s")
                adapter, cap, tok, identity = M.load_reader(rule, int(seed), ds, parent)
                record = M.snapshot_record(rule, int(seed), ds, HORIZON)
                state_sha = M.restore_memory(adapter, cap, record)
                capture, view = M.WriteCapture(cap.base), selection_view(cap)
                saved = s[(s.model == model) & (s.dataset == ds)].set_index(["probe_id", "target"])
                cell = manifest["cells"].get(key) if oracle_only else None
                cell = cell or dict(status="running", identity=dict(memory_state_sha256=state_sha, snapshot=record["path"], reader_sha256=record["reader_sha256"]), n=dict(), seconds=dict())
                lines = {"validate": [], "force": [], "oracle": []}
                t0 = time.monotonic()
                # 1) validation: untouched selection must reproduce the saved losses
                with capture:
                    for pid in ([] if oracle_only else todo[(model, ds)]["validate"]):
                        rec = score_probe(adapter, tok, by_id[pid], capture, view)
                        for tgt, tr in rec["targets"].items():
                            if tr.get("status") == "ok":
                                ref = saved.loc[(pid, tgt), "nll_token"]
                                tr["saved_nll_token"] = float(ref)
                                tr["abs_diff"] = abs(float(ref) - tr["nll_token"])
                        lines["validate"].append(json.dumps(rec, ensure_ascii=False))
                diffs = [tr["abs_diff"] for l in lines["validate"] for tr in json.loads(l)["targets"].values() if "abs_diff" in tr]
                if not oracle_only:
                    cell["validation"] = dict(n=len(diffs), max_abs_diff=max(diffs) if diffs else None)
                    if diffs and max(diffs) > 1e-4:
                        raise RuntimeError(f"{key}: replay does not reproduce the saved record (max |diff| {max(diffs):.3g})")
                    cell["seconds"]["validate"] = time.monotonic() - t0
                # 2) forced fire on every probe stopped by the null threshold; 3) oracle own record
                for mode in (("oracle",) if oracle_only else ("force", "oracle")):
                    t1 = time.monotonic()
                    pids = todo[(model, ds)][mode]
                    if limit:
                        pids = pids[:limit]
                    orig = _forced_select(cap, mode)
                    try:
                        with capture:
                            for pid in pids:
                                cap._oracle_item = by_id[pid].get("item_id")
                                rec = score_probe(adapter, tok, by_id[pid], capture, view)
                                rec["mode"] = mode
                                sel_now = cap.selection_for(np.asarray(tok.encode(by_id[pid]["prompt"]), np.int32))
                                rec["rare_veto_after_null"] = bool(getattr(sel_now, "rare_veto_after_null", False))
                                lines[mode].append(json.dumps(rec, ensure_ascii=False))
                    finally:
                        cap._select = orig
                        cap.reset_queries()
                    cell["n"][mode] = len(pids)
                    cell["seconds"][mode] = time.monotonic() - t1
                    log_line("frontier", f"{key} {mode} n={len(pids)} {time.monotonic() - t1:.0f}s")
                if cap.state_hash() != state_sha:
                    raise RuntimeError("replay changed the memory state")
                d = out / model / ds
                d.mkdir(parents=True, exist_ok=True)
                for mode, ls in lines.items():
                    if oracle_only and mode != "oracle":
                        continue
                    (d / f"{mode}.jsonl").write_text("\n".join(ls) + ("\n" if ls else ""))
                    cell[f"{mode}_sha256"] = sha(d / f"{mode}.jsonl")
                cell.update(status="complete", elapsed=cell.get("elapsed", 0.0) + time.monotonic() - t0, oracle_definition="every paraphrase whose applied record was not the own record (wrong record fired, or abstained by any gate)")
                manifest["cells"][key] = cell
                atomic_json(manifest_path, manifest)
                del adapter, cap, capture
    manifest.update(elapsed_total=time.monotonic() - t_all, other_cuda_processes=others)
    atomic_json(manifest_path, manifest)
    return manifest


def _rows(path, model, ds, mode):
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text().splitlines():
        r = json.loads(line)
        g = r.get("generation") or {}
        sel = r.get("selection") or {}
        for tgt, t in r["targets"].items():
            if t.get("status") != "ok":
                continue
            rows.append(dict(model=model, dataset=ds, mode=mode, probe_id=r["probe_id"], family=r["family"], item_id=r.get("item_id"), target=tgt, nll_token=t["nll_token"], exact=g.get("exact", {}).get(tgt),
                             generated=g.get("text"), replay_fired=not sel.get("hard_null", True), replay_record=(sel.get("record_ids") or [None])[0], rare_veto_after_null=bool(r.get("rare_veto_after_null", False)),
                             saved_nll_token=t.get("saved_nll_token"), abs_diff=t.get("abs_diff")))
    return rows


def assemble() -> dict:
    ensure_dirs()
    out = CACHE / "replay"
    manifest = read_json(out / "manifest.json")
    rows = []
    for key, cell in manifest["cells"].items():
        model, ds = key.split("/")
        for mode in ("validate", "force", "oracle"):
            rows.extend(_rows(out / model / ds / f"{mode}.jsonl", model, ds, mode))
    rep = pd.DataFrame(rows)
    atomic_parquet(DATA / "replay.parquet", rep)
    val = rep[rep["mode"] == "validate"].groupby(["model", "dataset"]).agg(n=("probe_id", "nunique"), max_abs_diff=("abs_diff", "max")).reset_index()
    atomic_csv(TABLES / "replay_validation.csv", val)

    s = scores(HORIZON)
    fz = frozen_losses(s)
    sel = pd.read_parquet(DATA / "selection_table.parquet")
    base = s[(s.model.isin(READERS)) & (s.family.isin(REPLAY_FAMILIES)) & (s.status == "ok")].merge(fz, on=["dataset", "probe_id", "target"], how="left")
    base = base.merge(sel[["model", "dataset", "probe_id", "veto", "own_is_top", "own_in_candidates"]], on=["model", "dataset", "probe_id"], how="left")
    force = rep[rep["mode"] == "force"][["model", "dataset", "probe_id", "target", "nll_token", "exact", "rare_veto_after_null"]].rename(columns={"nll_token": "L_force", "exact": "X_force"})
    base = base.merge(force, on=["model", "dataset", "probe_id", "target"], how="left")
    base["fired"] = base.fired.astype(bool)
    base["rare_veto_after_null"] = base.rare_veto_after_null.fillna(False).astype(bool)
    # loss/success if the gate fires (saved when it did, replayed when it did not), and if it abstains (frozen)
    base["L_fire"] = np.where(base.fired, base.nll_token, base.L_force)
    base["X_fire"] = np.where(base.fired, base.exact, base.X_force)
    base["L_abstain"] = base.L_frozen
    base["X_abstain"] = base.X_frozen
    # rare-vetoed (before or after the null gate) or candidate-less probes never fire at any threshold
    base["can_fire"] = base.veto.isin(["fired", "null_threshold"]) & ~base.rare_veto_after_null
    # selection risk (wrong record accepted) separately from answer risk (Capex review §2): own record is the applied one?
    base["applied_own"] = base.own_is_top.astype(bool)
    atomic_parquet(DATA / "frontier_cases.parquet", base)

    rows = []
    for (model, ds), x in base.groupby(["model", "dataset"]):
        for tau in TAUS:
            fire = x.can_fire & (x.null_mass < tau)
            L = np.where(fire, x.L_fire, x.L_abstain).astype(float)
            X = np.where(fire, x.X_fire, x.X_abstain)
            D = L - x.L_frozen.values
            row = dict(model=model, rule=rule_of(model), label=label(model), dataset=ds, tau=tau)
            for fam, tgt in (("paraphrase", "new"), ("near_miss_neighbour", "true"), ("unseen", "new"), ("locality_item", "true"), ("composition", "new")):
                m = ((x.family == fam) & (x.target == tgt)).values
                if not m.any():
                    continue
                ok = ~np.isnan(L[m])
                n = int(m.sum())
                Lm, Xm, Dm, fm = L[m][ok], X[m][ok], D[m][ok], fire.values[m][ok]
                Xm = pd.Series(Xm).astype(float).values
                k = max(1, int(np.ceil(0.05 * len(Lm))))
                if fam == "paraphrase":
                    sel_err = (fire.values[m][ok] & ~x.applied_own.values[m][ok])
                    row.update(paraphrase_wrong_record_rate=float(sel_err.mean()) if len(sel_err) else np.nan, paraphrase_fail_given_fired=float(1 - np.nanmean(Xm[fm])) if fm.any() else np.nan,
                               paraphrase_fail_given_fired_own=float(1 - np.nanmean(Xm[fm & x.applied_own.values[m][ok]])) if (fm & x.applied_own.values[m][ok]).any() else np.nan)
                row.update({f"{fam}_n": n, f"{fam}_scored": int(ok.sum()), f"{fam}_fire_rate": float(fm.mean()) if len(fm) else np.nan, f"{fam}_mean_nll": float(Lm.mean()) if len(Lm) else np.nan,
                            f"{fam}_cvar95": float(np.sort(Lm)[-k:].mean()) if len(Lm) else np.nan, f"{fam}_exact": float(np.nanmean(Xm)) if len(Xm) else np.nan,
                            f"{fam}_frac_worse_1nat": float((Dm > 1).mean()) if len(Dm) else np.nan, f"{fam}_frac_severe": float((Dm > SEVERE).mean()) if len(Dm) else np.nan, f"{fam}_mean_D": float(Dm.mean()) if len(Dm) else np.nan,
                            f"{fam}_frac_better_1nat": float((Dm < -1).mean()) if len(Dm) else np.nan})
            rows.append(row)
    fr = pd.DataFrame(rows)
    atomic_csv(TABLES / "frontier.csv", fr)

    # oracle rescue on paraphrases: failures at the registered gate vs with the own record forced
    orc = rep[rep["mode"] == "oracle"][["model", "dataset", "probe_id", "target", "nll_token", "exact"]].rename(columns={"nll_token": "L_oracle", "exact": "X_oracle"})
    para = base[(base.family == "paraphrase") & (base.target == "new")].merge(orc, on=["model", "dataset", "probe_id", "target"], how="left")
    para["L_oracle"] = np.where(para.own_is_top & para.fired, para.nll_token, para.L_oracle)
    para["X_oracle"] = np.where(para.own_is_top & para.fired, para.exact, para.X_oracle)
    rows = []
    for (model, ds), x in para.groupby(["model", "dataset"]):
        fail = x[~x.exact.astype(bool)]
        resc = fail[fail.X_oracle.astype(float) == 1.0]
        rows.append(dict(model=model, rule=rule_of(model), label=label(model), dataset=ds, n=len(x), success_registered=x.exact.astype(bool).mean(), success_oracle=x.X_oracle.astype(float).mean(),
                         mean_nll_registered=x.nll_token.mean(), mean_nll_oracle=x.L_oracle.mean(), cvar95_registered=x.nll_token.nlargest(max(1, int(np.ceil(0.05 * len(x))))).mean(), cvar95_oracle=x.L_oracle.nlargest(max(1, int(np.ceil(0.05 * len(x))))).mean(),
                         n_failures=len(fail), rescued_by_oracle=len(resc), rescue_rate=(len(resc) / len(fail) if len(fail) else np.nan),
                         failures_abstained=int((~fail.fired).sum()), rescued_among_abstained=int((resc.fired == False).sum()),  # noqa: E712
                         failures_fired_wrong=int((fail.fired & ~fail.own_is_top).sum()), rescued_among_fired_wrong=int((resc.fired & ~resc.own_is_top).sum()),
                         failures_fired_own=int((fail.fired & fail.own_is_top).sum()), not_rescuable_payload=int((fail.fired & fail.own_is_top).sum())))
    atomic_csv(TABLES / "oracle_rescue.csv", pd.DataFrame(rows))
    atomic_parquet(DATA / "oracle_cases.parquet", para)
    st = Status()
    for name in ("frontier", "oracle_rescue", "replay_validation"):
        st.artifact(f"tables/{name}", TABLES / f"{name}.csv")
    st.artifact("data/replay", DATA / "replay.parquet")
    st.stage("frontier", "complete", cells=len(manifest["cells"]), validation_max_abs_diff=float(val.max_abs_diff.max()) if len(val) else None)
    return dict(replay_rows=len(rep), frontier_rows=len(fr))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--assemble", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--oracle-only", action="store_true", help="re-run only the oracle replay on completed cells (keeps validate/force files)")
    ap.add_argument("--models", default=",".join(READERS))
    ap.add_argument("--datasets", default=",".join(DATASETS))
    a = ap.parse_args(argv)
    if a.execute:
        m = execute(a.models.split(","), a.datasets.split(","), a.limit, oracle_only=a.oracle_only)
        print(json.dumps({k: v.get("status") for k, v in m["cells"].items()}, indent=1))
    if a.assemble:
        print(assemble())


if __name__ == "__main__":
    main()
