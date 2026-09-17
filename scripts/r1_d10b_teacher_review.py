"""Final-base E.2 teacher/token review. Default is a CPU metadata dry run.

The orchestrator uses --execute after the active GPU chain finishes. One lease
covers initialization and every dataset. Completed chunks resume by exact input,
producer, base and tokenizer identity. No draw, seal or lead approval is emitted.
"""

from __future__ import annotations

import argparse
import copy
import fcntl
import json
import math
import os
import time
from pathlib import Path

import numpy as np
from scripts.r1_d9_receipts import read_resource, ref, sha, source_rows
from scripts.r1_d10a_review import ASSETS, ROOT, write_new
from scripts.r1_d10a_review_core import DATASETS, digest, token_review

from pccap.metrics.editing import normalize_answer

RULE = "E.2: normalize(cap-off greedy text) not in normalize(canonical answer plus aliases); max_new=32; newline/EOS stop; truncation recorded separately"


def memory_guard(min_gib, meminfo=Path("/proc/meminfo")):
    values = {
        line.split(":", 1)[0]: int(line.split()[1]) for line in meminfo.read_text().splitlines()
    }
    available = values["MemAvailable"] * 1024
    if not math.isfinite(min_gib) or min_gib <= 0:
        raise ValueError("positive finite MemAvailable guard required")
    if available < min_gib * 2**30:
        raise MemoryError(f"MemAvailable {available / 2**30:.2f} GiB below {min_gib:g} GiB")
    return available


def verify_bindings(bindings):
    for binding in bindings:
        path = Path(binding["path"]).resolve()
        if not path.is_relative_to(ROOT.parent) or any(
            x in {"confirm", "stage4_sealed_payloads"} for x in path.parts
        ):
            raise PermissionError("only explicitly bound unsealed project inputs allowed")
        if sha(path) != binding["sha256"]:
            raise ValueError("review input changed: " + str(path))


def eligible_rows(evidence, rows):
    by_id = {(ds, r["item_id"]): r for ds in DATASETS for r in rows[ds]}
    dispositions = evidence["dispositions"]
    keys = [(d["dataset"], d["item_id"]) for d in dispositions]
    if len(keys) != len(set(keys)) or set(keys) != set(by_id):
        raise ValueError("exhaustive unique disposition/source coverage required")
    groups = {ds: [] for ds in DATASETS}
    for disp in dispositions:
        row = by_id[disp["dataset"], disp["item_id"]]
        if digest(row) != disp["payload_sha256"]:
            raise ValueError("disposition/source content differs")
        if disp["preteacher_eligible"]:
            if not all(disp[k] is True for k in ("alias_clear", "context_clear", "exposure_clear")):
                raise ValueError("preteacher eligibility lacks completed review")
            groups[disp["dataset"]].append(row)
    return groups


def evaluate(rows, base, tokenizer, limits, *, batch_size, decode):
    """Answer-free model inputs; the answer is used only after decode for scoring."""
    checks = [token_review(row, tokenizer, limits) for row in rows]
    selected = [i for i, c in enumerate(checks) if c["pass"]]
    outputs = (
        decode(
            base,
            [np.asarray(rows[i]["prompt_ids"], np.int32) for i in selected],
            tokenizer,
            max_new=32,
            batch_size=batch_size,
            phase="query",
        )
        if selected
        else []
    )
    if len(outputs) != len(selected):
        raise ValueError("teacher output coverage differs")
    decoded = dict(zip(selected, outputs, strict=True))
    result = []
    for i, (row, check) in enumerate(zip(rows, checks, strict=True)):
        dec = decoded.get(i)
        aliases = sorted({normalize_answer(a) for a in [row["answer"], *row.get("aliases", [])]})
        result.append(
            {
                "dataset": row["dataset"],
                "item_id": row["item_id"],
                "payload_sha256": digest(row),
                "tokens_pass": check["pass"],
                "token_check": check,
                "normalized_answers": aliases,
                "teacher_pass": normalize_answer(dec.text) not in aliases if dec else None,
                "generation": dec.text if dec else None,
                "new_ids": list(map(int, dec.new_ids)) if dec else None,
                "stopped_by": dec.stopped_by if dec else None,
                "truncated": bool(dec.truncated) if dec else None,
                "steps": int(dec.steps) if dec else 0,
            }
        )
    return result


def validate_chunk(chunk, contract_sha, ds, number, rows):
    if chunk.get("rows_sha256") != digest(chunk["rows"]):
        raise ValueError("resume chunk content digest differs")
    if (
        chunk.get("contract_sha256") != contract_sha
        or chunk.get("dataset") != ds
        or chunk.get("number") != number
        or chunk.get("source_rows_sha256") != digest(rows)
    ):
        raise ValueError("resume chunk identity differs")
    expected = [(r["item_id"], digest(r)) for r in rows]
    got = [(r["item_id"], r["payload_sha256"]) for r in chunk["rows"]]
    if got != expected or any(r["dataset"] != ds for r in chunk["rows"]):
        raise ValueError("resume row inventory differs")
    for r, source in zip(chunk["rows"], rows, strict=True):
        aliases = sorted(
            {normalize_answer(a) for a in [source["answer"], *source.get("aliases", [])]}
        )
        if r["normalized_answers"] != aliases or r["tokens_pass"] != r["token_check"]["pass"]:
            raise ValueError("resume source aliases/token check differs")
        if type(r.get("tokens_pass")) is not bool:
            raise ValueError("resume token result unresolved")
        if r["tokens_pass"]:
            if type(r.get("teacher_pass")) is not bool or not isinstance(r.get("generation"), str):
                raise ValueError("resume teacher result unresolved")
            if r["teacher_pass"] != (
                normalize_answer(r["generation"]) not in r["normalized_answers"]
            ):
                raise ValueError("resume teacher scoring differs")
    return chunk["rows"]


def merge(evidence, reviewed, teacher_bindings):
    result = copy.deepcopy(evidence)
    wanted = {
        (d["dataset"], d["item_id"]) for d in result["dispositions"] if d["preteacher_eligible"]
    }
    keyed = {(r["dataset"], r["item_id"]): r for r in reviewed}
    if len(keyed) != len(reviewed) or set(keyed) != wanted:
        raise ValueError("complete teacher review required before merged output")
    for disp in result["dispositions"]:
        if not disp["preteacher_eligible"]:
            continue
        r = keyed[disp["dataset"], disp["item_id"]]
        if r["payload_sha256"] != disp["payload_sha256"]:
            raise ValueError("teacher/source hash differs")
        disp.update(
            teacher_pass=r["teacher_pass"],
            tokens_pass=r["tokens_pass"],
            base_tensor_sha256=result["base_tensor_sha256"],
            tokenizer_sha256=result["tokenizer_sha256"],
        )
        reasons = []
        if not r["tokens_pass"]:
            reasons.append("final_tokens_failed")
        if r["teacher_pass"] is not True:
            reasons.append("final_teacher_correct_or_unavailable")
        disp["teacher_token_eligible"] = not reasons
        # Endpoint role review is a distinct input, never fabricated by this producer.
        disp["decision"] = "exclude"
        disp["reasons"] = reasons or ["pending_endpoint_role_review"]
    result.update(
        teacher_token_review_complete=True,
        role_compatibility_complete=False,
        mode="unsealed_teacher_reviewed_evidence",
        teacher_rule=RULE,
        teacher_counts={
            ds: {
                "reviewed_items": sum(r["dataset"] == ds for r in reviewed),
                "eligible_subjects": len(
                    {
                        d["entity_id"]
                        for d in result["dispositions"]
                        if d["dataset"] == ds and d.get("teacher_token_eligible")
                    }
                ),
            }
            for ds in DATASETS
        },
    )
    result["evidence_bindings"] += teacher_bindings
    return result


def atomic_new(path, value):
    """Publish only complete chunks; an interrupted temporary file is never resumed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".partial-{os.getpid()}-{time.time_ns()}")
    with temporary.open("x") as handle:
        json.dump(value, handle, sort_keys=True, ensure_ascii=False, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    # A hard link publishes atomically and refuses an existing final destination.
    os.link(temporary, path)
    temporary.unlink()
    return ref(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evidence", type=Path, required=True)
    ap.add_argument("--evidence-sha256", required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--log-dir", type=Path, required=True)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--allow-under-capacity-exploration", action="store_true")
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--chunk-size", type=int, default=256)
    ap.add_argument("--min-available-gib", type=float, default=8.0)
    args = ap.parse_args()
    if min(args.batch_size, args.chunk_size) < 1:
        ap.error("positive batch/chunk size required")
    if not args.output.resolve().is_relative_to(
        ASSETS
    ) or not args.log_dir.resolve().is_relative_to(ROOT / "logs"):
        ap.error("resources under assets and progress receipts under repository logs required")
    evidence_binding = {"path": str(args.evidence.resolve()), "sha256": args.evidence_sha256}
    evidence = read_resource(evidence_binding)
    verify_bindings([evidence["register"], *evidence["evidence_bindings"]])
    register = json.loads(Path(evidence["register"]["path"]).read_text())
    groups = eligible_rows(evidence, source_rows(register))
    base_spec = evidence["base"]
    base_bindings = [
        {"path": str(Path(base_spec["path"]) / n), "sha256": h}
        for n, h in base_spec["files"].items()
    ]
    verify_bindings(base_bindings)
    producer = [
        ref(__file__),
        ref(ROOT / "scripts/r1_d10a_review_core.py"),
        ref(ROOT / "src/pccap/data/decode.py"),
        ref(ROOT / "src/pccap/data/tokenize.py"),
        ref(ROOT / "src/pccap/bases/bp.py"),
        ref(ROOT / "src/pccap/bases/gpt2_jax.py"),
    ]
    contract = {
        "evidence": evidence_binding,
        "producer": producer,
        "rule": RULE,
        "base_tensor_sha256": evidence["base_tensor_sha256"],
        "tokenizer_sha256": evidence["tokenizer_sha256"],
        "batch_size": args.batch_size,
        "chunk_size": args.chunk_size,
        "datasets": {ds: [r["item_id"] for r in groups[ds]] for ds in DATASETS},
    }
    contract_sha = digest(contract)
    n = sum(map(len, groups.values()))
    short = {
        ds: c["preteacher_subjects"]
        for ds, c in evidence["counts"].items()
        if c["preteacher_subjects"] < 4050
    }
    historical = json.loads((ROOT / "manifests/revision_v1/mquake_pool_v1.json").read_text())
    per_row = historical["teacher_seconds"] / historical["counts"]["candidates"]
    status = {
        "mode": "dry_run",
        "contract_sha256": contract_sha,
        "rows": {ds: len(rows) for ds, rows in groups.items()},
        "max_generated_tokens": n * 32,
        "historical_decode_seconds_per_row": per_row,
        "linear_estimate_seconds": n * per_row,
        "planning_seconds_2x_to_5x": [n * per_row * 2, n * per_row * 5],
        "estimate_limit": "historical MQ measured throughput only; final prompt lengths, JIT and chunk shapes may differ; no new GPU measurement",
        "capacity_shortfall": short,
        "execution_requires": "explicit --execute, one GPU lease, MemAvailable guard",
        "final_clearance": "still requires independent endpoint-role review and all dataset capacities",
    }
    print(json.dumps(status, indent=2), flush=True)
    if not args.execute:
        return
    if short and not args.allow_under_capacity_exploration:
        raise ValueError(
            "preteacher capacity already insufficient; abort before GPU. Explicit exploratory override cannot authorize a draw."
        )
    args.log_dir.mkdir(parents=True, exist_ok=True)
    attempt = args.log_dir / f"attempt-{time.time_ns()}"
    attempt.mkdir()
    # Lock the run directory as well as the GPU; resumptions cannot publish racing chunks.
    args.output.mkdir(parents=True, exist_ok=True)
    with (args.output / ".run.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        contract_path = args.output / "contract.json"
        if contract_path.exists():
            if json.loads(contract_path.read_text()) != contract:
                raise ValueError("resume contract differs; use a new resource version")
        else:
            atomic_new(contract_path, contract)
        from pccap.harness.lease import gpu_lease

        start = time.monotonic()
        try:
            with gpu_lease(
                "R1-D10b:teacher", stage="R1", projected_seconds=n * per_row * 5, exclusive=True
            ) as lease:
                memory_guard(args.min_available_gib)
                import jax

                from pccap.bases.bp import BPBase
                from pccap.data.decode import greedy_decode_batch
                from pccap.data.tokenize import GPT2Tokenizer
                from pccap.harness.ledger import Ledger

                if jax.default_backend() != "gpu":
                    raise RuntimeError("owner execution requires JAX CUDA; dry run is CPU-only")
                base = BPBase(snapshot=Path(base_spec["path"]), ledger=Ledger())
                if base.checksum() != evidence["base_tensor_sha256"]:
                    raise ValueError("loaded base tensor identity differs")
                tok = GPT2Tokenizer(snapshot=Path(base_spec["path"]))
                if tok.file_sha256() != evidence["tokenizer_sha256"]:
                    raise ValueError("loaded tokenizer identity differs")
                reviewed, bindings = (
                    [],
                    [evidence_binding, ref(contract_path), *producer, *base_bindings],
                )
                for ds in DATASETS:
                    for number, offset in enumerate(range(0, len(groups[ds]), args.chunk_size)):
                        rows = groups[ds][offset : offset + args.chunk_size]
                        path = args.output / ds / f"chunk-{number:05d}.json"
                        chunk_start = time.monotonic()
                        available = memory_guard(args.min_available_gib)
                        resumed = path.exists()
                        if resumed:
                            chunk = json.loads(path.read_text())
                        else:
                            # Bound memory again before each internal batch, not only each chunk.
                            def guarded_decode(*pos, **kwargs):
                                memory_guard(args.min_available_gib)
                                return greedy_decode_batch(*pos, **kwargs)

                            out = []
                            for batch in range(0, len(rows), args.batch_size):
                                out.extend(
                                    evaluate(
                                        rows[batch : batch + args.batch_size],
                                        base,
                                        tok,
                                        evidence["model_limits"],
                                        batch_size=args.batch_size,
                                        decode=guarded_decode,
                                    )
                                )
                            chunk = {
                                "contract_sha256": contract_sha,
                                "dataset": ds,
                                "number": number,
                                "source_rows_sha256": digest(rows),
                                "rows": out,
                                "rows_sha256": digest(out),
                                "wall_seconds": time.monotonic() - chunk_start,
                            }
                            atomic_new(path, chunk)
                        reviewed.extend(validate_chunk(chunk, contract_sha, ds, number, rows))
                        bindings.append(ref(path))
                        progress = {
                            "dataset": ds,
                            "chunk_number": number,
                            "resumed": resumed,
                            "reviewed_total": len(reviewed),
                            "mem_available_bytes": available,
                            "wall_seconds": time.monotonic() - start,
                            "chunk": ref(path),
                        }
                        write_new(attempt / f"{ds}-{number:05d}.json", progress)
                        print(json.dumps(progress), flush=True)
                if base.checksum() != evidence["base_tensor_sha256"]:
                    raise ValueError("base tensor identity changed during review")
                verify_bindings([*evidence["evidence_bindings"], *bindings])
                merged = merge(evidence, reviewed, bindings)
                result = args.output / "teacher_evidence.json"
                if result.exists():
                    if json.loads(result.read_text()) != merged:
                        raise ValueError("completed evidence differs from verified resume")
                else:
                    atomic_new(result, merged)
            write_new(
                attempt / "complete.json",
                {
                    "task": "R1-D10b",
                    "evidence": ref(result),
                    "lease": lease.report,
                    "wall_seconds": time.monotonic() - start,
                    "status": "teacher evidence complete; role/lead clearance still pending",
                },
            )
        except BaseException as error:
            write_new(
                attempt / "failure.json",
                {
                    "task": "R1-D10b",
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "wall_seconds": time.monotonic() - start,
                    "completed_chunks_retained": True,
                },
            )
            raise


if __name__ == "__main__":
    main()
