"""Reproduce the Round-21 cumulative, unsealed preteacher review on CPU.

Example: JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= python -m scripts.r1_d10a_review
Outputs are new files; this tool never draws, seals, loads model tensors or signs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scripts.r1_d9_receipts import ROOT, ref, sha, source_rows
from scripts.r1_d10a_review_core import presented_texts, review

from pccap.data.tokenize import GPT2Tokenizer

ASSETS = ROOT.parent / "assets"
ROUND21 = "2a8b237"


def audit_query_reason(datasets, roles):
    roles = set(roles)
    if datasets == ["mquake"] and roles:
        if roles <= {"locality", "development_unrelated"}:
            return "mquake_development_locality_query_subject"
        if roles <= {"locality", "development_unrelated", "near_miss_reserved"}:
            return "mquake_unverified_near_miss_query_subject"
    return "historical_query_reservation"


class Snapshot:
    def __init__(self, commit):
        self.commit = subprocess.check_output(
            ["git", "rev-parse", commit + "^{commit}"], cwd=ROOT, text=True
        ).strip()
        tree = subprocess.check_output(["git", "ls-tree", "-rz", self.commit], cwd=ROOT)
        self.files = {}
        for entry in tree.split(b"\0"):
            if entry:
                header, name = entry.split(b"\t", 1)
                self.files[name.decode()] = header.split()[2].decode()
        self.bindings = {}

    def read(self, name):
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if not path.is_relative_to(ROOT.parent) or any(
            p in {"confirm", "stage4_sealed_payloads"} for p in path.parts
        ):
            raise PermissionError("unsealed project input required")
        data = path.read_bytes()
        if path.is_relative_to(ROOT):
            rel = str(path.relative_to(ROOT))
            git_hash = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if git_hash != self.files.get(rel):
                raise ValueError("input is not the committed snapshot: " + rel)
        self.bindings[str(path)] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    def resource(self, binding):
        if sha(binding["path"]) != binding["sha256"]:
            raise ValueError("resource binding changed: " + binding["path"])
        value = self.read(binding["path"])
        if self.bindings[str(Path(binding["path"]).resolve())] != binding["sha256"]:
            raise ValueError("resource changed during read")
        return value

    def verify(self):
        for path, expected in self.bindings.items():
            if sha(path) != expected:
                raise ValueError("review input changed during work: " + path)


def collect(snapshot, register, tokenizer):
    """Reserve all declared training/dev rows, without filtering by model outcomes."""
    events, seen, inventory = [], set(), []
    mq_path = ASSETS / "data/prepared/revision_v1/r1_d4_v1/items.jsonl"
    if sha(mq_path) != register["bindings_sha256"][str(mq_path)]:
        raise ValueError("prepared MQ prompt/subject map changed")
    mq_prompts = defaultdict(set)
    with mq_path.open() as handle:
        for line in handle:
            row = json.loads(line)
            mq_prompts[row["prompt"]].add(row["subject"])
    snapshot.bindings[str(mq_path)] = register["bindings_sha256"][str(mq_path)]

    def event(source, reason, *, subject=None, text=None):
        if not subject and not text:
            return
        key = (source, reason, subject, text)
        if key not in seen:
            seen.add(key)
            events.append(
                {
                    "source": source,
                    "reason": reason,
                    **({"subject": subject} if subject else {}),
                    **({"text": text} if text else {}),
                    **(
                        {
                            "waiver_subjects": sorted(
                                mq_prompts.get(text, set()) | ({subject} if subject else set())
                            )
                        }
                        if reason
                        in {
                            "mquake_training_locality_query_subject",
                            "mquake_development_locality_query_subject",
                            "mquake_development_unrelated_query_subject",
                        }
                        else {}
                    ),
                }
            )

    def primary(row, source, reason):
        event(source, reason, subject=row.get("subject") or row.get("subject_key"))
        for text in presented_texts(row):
            event(source, reason, text=text)

    def queries(row, source, reason):
        for text in row.get("locality_prompts", []):
            event(source, reason, text=text)
        for loc in row.get("locality", []) or []:
            event(source, reason, subject=loc.get("subject_key"), text=loc.get("prompt"))
        # Near-miss support is not covered by the true-fact locality exception.
        for near in row.get("near_miss_candidates", []) or []:
            primary(near, source, "reserved_near_miss_candidate")

    old = snapshot.read("manifests/revision_v1/exclusions_v3.json")
    aliases = old["verified_alias_pairs"]
    for row in old["exclusions"]:
        for reason in row["reasons"]:
            event(
                "manifests/revision_v1/exclusions_v3.json",
                reason,
                subject=row["canonical_subject_key"],
            )
    for ds, rows in register["removals"].items():
        for row in rows:
            for reason in row["reasons"]:
                event("register_v6_removals:" + ds, reason, subject=row["canonical_subject"])
    # Full historical versions include all of the 700-row MQ historical remainder.
    pool_names = sorted(
        p
        for p in snapshot.files
        if (p.startswith("manifests/revision_v1/train_pool") and p.endswith(".json"))
        or (
            p.startswith("manifests/dev/")
            and Path(p).name.startswith(("zsre_dev", "counterfact_dev", "mquake_dev"))
            and p.endswith(".json")
        )
    )
    for name in pool_names:
        doc = snapshot.read(name)
        ds = doc.get("dataset") or next(
            ds for ds in ("zsre", "counterfact", "mquake") if ds in name
        )
        kind = "training" if "train_pool" in name else "development"
        local_reason = f"{ds}_{kind}_locality_query_subject"
        inventory.append({"path": name, "kind": kind, "dataset": ds, "rows": len(doc["items"])})
        for row in doc["items"]:
            source = name + "#" + row["item_id"]
            primary(row, source, f"{ds}_{kind}_reserved_subject")
            queries(row, source, local_reason)
        for text in doc.get("unrelated_prompts", []):
            event(name, f"{ds}_development_unrelated_query_subject", text=text)
    reserved_name = "manifests/dev/reserved_subjects.json"
    reserved = snapshot.read(reserved_name)
    for subject in reserved["subjects"]:
        event(reserved_name, "historical_s0_reserved", subject=subject)
    for prompt in reserved["prompts"]:
        event(reserved_name, "historical_s0_reserved", text=prompt)
    audit_name = "logs/r1_round11/exposure_audit.part2_queries.json"
    audit = snapshot.read(audit_name)
    for query in audit["queries"]:
        # Preserve the unresolved near-miss policy separately from primary exposure.
        reason = audit_query_reason(query["reservation_datasets"], query["roles"])
        source = audit_name + "#" + query["query_sha256"]
        for text in query["texts"]:
            event(source, reason, text=text)
        for mapped in query["mapped_subjects"]:
            event(source, reason, subject=mapped["subject"])
    pop_name = "docs/tasks/R1-76b-mquake-historical-v3.population.spec.json"
    spec = snapshot.read(pop_name)
    pop = snapshot.resource(spec["population"])
    for role in ("edits", "outside"):
        for row in pop[role]:
            primary(row, pop_name + "#" + role + ":" + row["item_id"], "R1-76b_reserved_subject")
    payloads = set()
    for name in sorted(snapshot.files):
        if not (name.startswith("docs/tasks/") and name.endswith(".recipe.json")):
            continue
        recipe = snapshot.read(name)
        if recipe.get("mode") != "stage4_development_cell":
            continue
        binding = recipe["payload"]
        key = (binding["path"], binding["sha256"])
        if key in payloads:
            continue
        payloads.add(key)
        payload = snapshot.resource(binding)
        inventory.append(
            {
                "path": binding["path"],
                "kind": "committed_development_payload",
                "recipe": name,
                "rows": len(payload.get("items", [])),
            }
        )
        for role in ("items", "pool_rows"):
            for row in payload.get(role, []):
                primary(row, binding["path"] + "#" + row["item_id"], "development_payload_reserved")
        for kind, endpoint in payload.get("endpoints", {}).items():
            reason = (
                "mquake_development_locality_query_subject"
                if recipe["cell"]["dataset"] == "mquake" and kind == "locality"
                else "development_endpoint:" + kind
            )
            for row in endpoint.get("rows", []):
                primary(row, binding["path"] + "#" + kind, reason)
            for win in endpoint.get("windows", []):
                ids = win if isinstance(win, list) else win.get("ids", win.get("token_ids", []))
                if ids:
                    event(
                        binding["path"] + "#drift",
                        "development_drift_text",
                        text=tokenizer.decode(ids),
                    )
    # Exact sampled 96-token prefixes cover all 16/48/96-token training prefixes.
    samplings = set()
    for name in sorted(snapshot.files):
        if not (name.startswith("results/R1/pilot/") and name.endswith("/summary.json")):
            continue
        doc = snapshot.read(name)
        args = doc.get("args", {})
        if args.get("text_nulls", 0) > 0:
            if "seed" not in args or "text_windows" not in args:
                raise ValueError("ordinary-text sampling identity incomplete: " + name)
            samplings.add((int(args["seed"]) + 7, int(args["text_windows"])))
    if samplings:
        shard_path = ASSETS / "data/raw/openwebtext/openwebtext.bin"
        snapshot.bindings[str(shard_path)] = sha(shard_path)
        shard = np.memmap(shard_path, dtype="<u2", mode="r")
        if len(shard) < 50_001_920:
            raise ValueError("training shard too short")
        for seed, windows in sorted(samplings):
            starts = np.random.default_rng(seed).integers(0, 50_001_920 - 128, size=windows)
            for start in starts:
                event(
                    f"{shard_path}#text:{int(start)}:96",
                    "ordinary_text_training_prefix",
                    text=tokenizer.decode(shard[int(start) : int(start) + 96]),
                )
        inventory.append(
            {
                "path": str(shard_path),
                "kind": "ordinary_text_training",
                "samplings": sorted(samplings),
                "prefix_lengths_covered": [16, 48, 96],
            }
        )
    return {
        "schema_version": 1,
        "commit": snapshot.commit,
        "verified_alias_pairs": aliases,
        "inventory": inventory,
        "events": events,
        "scope": "all committed training versions, dev slices/reservations, round11 query audit, historical MQ pools, R1-76b, committed development payloads, declared ordinary-text banks",
        "not_model_exposure": [
            "full preparation catalogs (including challenges.json)",
            "base pretraining corpus",
            "unused candidate teacher-pool preparation",
        ],
        "history_policy": "all declared reservations retained even without execution evidence; no outcome-based releases",
    }


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as handle:
        json.dump(
            value,
            handle,
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        )
        handle.write("\n")
    return ref(path)


def run(commit, output, report):
    start = time.monotonic()
    if not output.resolve().is_relative_to(ASSETS) or not report.resolve().is_relative_to(
        ROOT / "logs"
    ):
        raise ValueError("resource under assets and report under repository logs required")
    names = ["inputs.json", "row_checks.json", "evidence.json"]
    if any((output / name).exists() for name in names) or report.exists():
        raise FileExistsError("choose new versioned output paths")
    snapshot = Snapshot(commit)
    register_path = ROOT / "manifests/revision_v1/exclusions_frozen_v6.json"
    register = snapshot.read(register_path)
    base_recipe = snapshot.read("docs/tasks/R1-68c-zsre-v5-full.recipe.json")
    base = base_recipe["construction"]["base"]
    for name, expected in base["files"].items():
        path = Path(base["path"]) / name
        if sha(path) != expected:
            raise ValueError("final base file differs: " + str(path))
        snapshot.bindings[str(path)] = expected
    cfg = snapshot.read(Path(base["path"]) / "config.json")
    limits = {"vocabulary": cfg["vocab_size"], "max_context": cfg["n_positions"]}
    tok = GPT2Tokenizer(snapshot=Path(base["path"]))
    sources = source_rows(register)
    inputs = collect(snapshot, register, tok)
    print(
        json.dumps(
            {
                "phase": "inputs_collected",
                "events": len(inputs["events"]),
                "bindings": len(snapshot.bindings),
            }
        ),
        flush=True,
    )
    evidence, details = review(register, sources, inputs, tok, limits)
    inputs["source_bindings"] = [
        {"path": p, "sha256": h} for p, h in sorted(snapshot.bindings.items())
    ]
    # Bind all prepared source inputs, immutable register ancestry and producer code.
    bindings = {**register["bindings_sha256"], **snapshot.bindings}
    for path in [
        __file__,
        ROOT / "scripts/r1_d10a_review_core.py",
        ROOT / "scripts/r1_d9_receipts.py",
        ROOT / "src/pccap/data/tokenize.py",
        ROOT / "scripts/r1_50_stream_train.py",
        ROOT / "src/pccap/revision_v1/stream_train.py",
    ]:
        bindings[str(Path(path).resolve())] = sha(path)
    snapshot.verify()
    input_ref = write_new(output / "inputs.json", inputs)
    details_ref = write_new(output / "row_checks.json", details)
    evidence.update(
        register=ref(register_path),
        exposure_as_of_commit=snapshot.commit,
        base_tensor_sha256=base_recipe["adapter_identity"]["base_sha256"],
        tokenizer_sha256=tok.file_sha256(),
        base=base,
        evidence_bindings=[{"path": p, "sha256": h} for p, h in sorted(bindings.items())]
        + [input_ref, details_ref],
    )
    result_ref = write_new(output / "evidence.json", evidence)
    summary = {k: v for k, v in evidence.items() if k not in {"dispositions", "evidence_bindings"}}
    summary.update(
        task="R1-D10a",
        evidence=result_ref,
        inputs=input_ref,
        row_checks=details_ref,
        event_count=len(inputs["events"]),
        input_file_count=len(bindings),
        gpu_seconds=0,
        model_calls=0,
        wall_seconds=time.monotonic() - start,
        status="preteacher review only; final clearance not admitted",
    )
    write_new(report, summary)
    print(
        json.dumps(
            {
                "counts": evidence["counts"],
                "evidence": result_ref,
                "wall_seconds": summary["wall_seconds"],
            },
            indent=2,
        )
    )
    return summary


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--commit", default=ROUND21)
    ap.add_argument("--output", type=Path, default=ASSETS / "runs/pc_cap/R1/r1_d10a/round22_v1")
    ap.add_argument("--report", type=Path, default=ROOT / "logs/r1_round22/r1-d10a-review.json")
    args = ap.parse_args()
    run(args.commit, args.output, args.report)


if __name__ == "__main__":
    main()
