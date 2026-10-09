"""GPU scoring of probes for one model state: greedy generation (original convention) + teacher-forced target losses.

    python -m aw.extremes.score --model frozen --dataset zsre --execute
    python -m aw.extremes.score --model bp_reader_s0 --dataset counterfact --horizon 300 --execute

Per probe and per target the record holds: generated text (greedy, max 32, stop at newline/EOS), exact match against the
supplied aliases (project normalisation), per-token NLL of the target tokens under teacher forcing with the cap's writes
applied at every prediction position (E.2 semantics, same code path as the record's diagnostic), totals with and without
the newline terminator, the reader's selection at the prompt (record ids, null mass, hard null, best score) and the write
norms actually applied (absolute, relative to the pre-write residual) at every scored position.

Chunks of 100 probes are written atomically (JSONL) under assets/extremes_analysis/<run>/checkpoints/scores/... with a
chunk manifest; a restart verifies completed chunks by hash and scores only the missing ones.
"""

from __future__ import annotations

import pccap  # noqa: F401  # isort: skip

import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np

from aw.extremes import models as M
from aw.extremes.common import DATA, OUT, RUN_ID, Status, atomic_json, atomic_write_bytes, git_head, log_line, now, read_json, sha, sha_bytes
from aw.extremes.probes import build_probes
from pccap.data.decode import greedy_decode, score_generation
from pccap.data.tokenize import tokenize_pair

CHUNK = 100
GENERATE_FAMILIES = {"edit", "paraphrase", "locality", "near_miss_neighbour", "near_miss_edit", "revision", "revision_paraphrase", "unseen", "composition"}


def scores_dir(model: str, dataset: str, horizon: int | None) -> Path:
    return DATA / "checkpoints" / "scores" / model / dataset / (f"h{horizon}" if horizon else "h0")


def _logits(model, ids):
    fr = model.predict(np.asarray(ids, np.int32))
    row = np.asarray(fr.logits, np.float64)
    row = row[-1] if row.ndim == 2 else row
    if not np.all(np.isfinite(row)):
        raise FloatingPointError("nonfinite logits")
    return row


def teacher_forced(model, prompt_ids, answer_ids):
    """Per-token −log p(y_t | x, y_<t); one prediction per gold prefix (cap writes act at each position)."""
    ids = np.asarray(prompt_ids, np.int32).reshape(-1)
    out = []
    for y in np.asarray(answer_ids, np.int32).reshape(-1):
        row = _logits(model, ids)
        m = row.max()
        out.append(float(m + np.log(np.exp(row - m).sum()) - row[int(y)]))
        ids = np.concatenate([ids, np.int32([y])])
    return out


def norms(capture: M.WriteCapture, start: int):
    """Write norms per site for the predictions recorded since ``start``."""
    rows = []
    for W, sites in zip(capture.writes[start:], capture.sites[start:]):
        abs_ = [float(np.linalg.norm(W[m - 1])) for m in (1, 2, 3)]
        h = [float(np.linalg.norm(sites[m])) if m in sites else None for m in (1, 2, 3)]
        rows.append(dict(abs=abs_, h=h, rel=[a / (hh + 1e-12) if hh is not None else None for a, hh in zip(abs_, h)], energy=float((W * W).sum())))
    return rows


def score_probe(model, tok, probe, capture, cap_selection):
    model.reset_queries()
    pids = np.asarray(tok.encode(probe["prompt"]), np.int32)
    rec = dict(probe_id=probe["probe_id"], family=probe["family"], item_id=probe.get("item_id"), prompt_tokens=int(len(pids)), status="ok")
    if len(pids) == 0:
        rec.update(status="empty_prompt")
        return rec
    n0 = len(capture.writes) if capture else 0
    if probe["family"] in GENERATE_FAMILIES:
        dec = greedy_decode(lambda ids: _logits(model, ids), pids, tok, max_new=32, state_hash=model.state_hash)
        rec["generation"] = dict(text=dec.text, stopped_by=dec.stopped_by, truncated=bool(dec.truncated), steps=int(dec.steps), logprob_sum=float(sum(dec.logprobs)),
                                 exact={k: bool(score_generation(dec, t["aliases"])["value"]) for k, t in probe["targets"].items()})
        if capture:
            rec["generation"]["write_norms"] = norms(capture, n0)
    rec["targets"] = {}
    for key, t in probe["targets"].items():
        pair = tokenize_pair(tok, probe["prompt"], t["text"])
        if pair.excluded:
            rec["targets"][key] = dict(status="excluded:" + pair.reason)
            continue
        model.reset_queries()
        n1 = len(capture.writes) if capture else 0
        per_token = teacher_forced(model, pair.prompt_ids, pair.answer_ids)
        tr = dict(status="ok", text=t["text"], answer_ids=[int(x) for x in pair.answer_ids], n_tokens=len(per_token), per_token_nll=per_token,
                  nll_total=float(sum(per_token)), nll_total_no_terminator=float(sum(per_token[:-1])), nll_token=float(np.mean(per_token)),
                  nll_token_no_terminator=float(np.mean(per_token[:-1])) if len(per_token) > 1 else None)
        if capture:
            tr["write_norms"] = norms(capture, n1)
        rec["targets"][key] = tr
    if cap_selection is not None:
        sel = cap_selection(pids)
        rec["selection"] = sel
    return rec


def selection_view(cap):
    def view(pids):
        s = cap.selection_for(np.asarray(pids, np.int32))
        return dict(hard_null=bool(s.hard_null), null_mass=float(s.null_mass), best_score=None if s.best_score is None else float(s.best_score),
                    record_ids=list(s.record_ids), weights=[float(w) for w in np.asarray(s.weights).reshape(-1)] if s.weights is not None else [],
                    has_delta=s.delta is not None, prompt_len=int(s.prompt_len))
    return view


def run(model_id: str, dataset: str, horizon: int | None, *, max_locality_per_item: int = 3, limit: int | None = None):
    from aw.pc_v0 import blocking_cuda_processes
    from pccap.harness.lease import gpu_lease

    out = scores_dir(model_id, dataset, horizon)
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "chunks.json"
    manifest = read_json(manifest_path) if manifest_path.exists() else dict(run_id=RUN_ID, model=model_id, dataset=dataset, horizon=horizon, chunks={}, status="running")
    probes, summary = build_probes(dataset)
    if max_locality_per_item is not None:
        probes = [p for p in probes if p["family"] != "locality_item" or p["locality_index"] < max_locality_per_item]
    if limit:
        probes = probes[:limit]
    probe_blob = json.dumps([p["probe_id"] for p in probes]).encode()
    manifest.update(n_probes=len(probes), probe_ids_sha256=sha_bytes(probe_blob), probe_summary={k: v for k, v in summary.items() if k != "payload"}, payload=summary["payload"],
                    max_locality_per_item=max_locality_per_item, code_sha=git_head(), started=manifest.get("started") or now())
    atomic_json(manifest_path, manifest)
    atomic_write_bytes(out / "probes.json", json.dumps(probes, ensure_ascii=False).encode())
    t0 = time.monotonic()
    with gpu_lease(f"{RUN_ID} score {model_id} {dataset} h{horizon}", stage="extremes", projected_seconds=3600, exclusive=True) as lease:
        others = lease.other_cuda_processes()
        if blocking_cuda_processes(others):
            raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
        if model_id == "frozen":
            model, parent, tok, binding = M.load_frozen(dataset)
            capture, cap_sel = None, None
            identity = dict(base_sha256=model.checksum(), recipe=binding)
        else:
            spec = {k: v for k, v in zip(("rule", "seed"), model_id.replace("_reader_s", " ").split())}
            rule, seed = spec["rule"], int(spec["seed"])
            adapter, cap, tok, identity = M.load_reader(rule, seed, dataset)
            record = M.snapshot_record(rule, seed, dataset, horizon)
            identity["snapshot"] = record
            identity["memory_state_sha256"] = M.restore_memory(adapter, cap, record)
            identity["base_sha256"] = cap.base.checksum(recompute=True)
            model = adapter
            capture, cap_sel = M.WriteCapture(cap.base), selection_view(cap)
        manifest["identity"] = identity
        atomic_json(manifest_path, manifest)
        state0 = model.state_hash()
        for start in range(0, len(probes), CHUNK):
            key = f"chunk-{start // CHUNK:04d}"
            path = out / (key + ".jsonl")
            done = manifest["chunks"].get(key)
            if done and path.exists() and sha(path) == done["sha256"]:
                continue
            batch = probes[start : start + CHUNK]
            t1 = time.monotonic()
            lines = []
            if capture:
                with capture:
                    for p in batch:
                        lines.append(json.dumps(score_probe(model, tok, p, capture, cap_sel), ensure_ascii=False))
            else:
                for p in batch:
                    lines.append(json.dumps(score_probe(model, tok, p, None, None), ensure_ascii=False))
            if model.state_hash() != state0:
                raise RuntimeError("scoring changed the memory state")
            digest = atomic_write_bytes(path, ("\n".join(lines) + "\n").encode())
            manifest["chunks"][key] = dict(sha256=digest, n=len(batch), first=start, seconds=time.monotonic() - t1, written=now())
            atomic_json(manifest_path, manifest)
            log_line("score", f"{model_id} {dataset} h{horizon} {key} n={len(batch)} {time.monotonic() - t1:.1f}s")
        manifest.update(status="complete", finished=now(), elapsed_process_seconds=time.monotonic() - t0, peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
                        final_state_sha256=model.state_hash(), other_cuda_processes=others)
        atomic_json(manifest_path, manifest)
    Status().artifact(f"scores/{model_id}/{dataset}/h{horizon}", manifest_path, model=model_id, dataset=dataset, horizon=horizon, n_probes=len(probes))
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(M_MODELS()))
    ap.add_argument("--dataset", required=True, choices=["zsre", "counterfact", "mquake"])
    ap.add_argument("--horizon", type=int, default=None, help="memory checkpoint (100 or 300) for reader models")
    ap.add_argument("--max-locality-per-item", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args(argv)
    if not a.execute:
        raise SystemExit("GPU scoring requires --execute")
    if a.model != "frozen" and a.horizon not in (100, 300):
        raise SystemExit("reader models need --horizon 100 or 300")
    if a.model == "frozen":
        a.horizon = None
    m = run(a.model, a.dataset, a.horizon, max_locality_per_item=a.max_locality_per_item, limit=a.limit)
    print(json.dumps(dict(status=m["status"], n_probes=m["n_probes"], seconds=m.get("elapsed_process_seconds"))))


def M_MODELS():
    return ["frozen"] + [f"{r}_reader_s{s}" for r in ("bp", "epc") for s in (0, 1, 2)]


if __name__ == "__main__":
    main()
