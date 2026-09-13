"""R1-00: reconstruct the historical reference without model execution or GPU access.

Outputs are exclusive-create. The caller must identify whether the snapshot is the
lead's v0 close-out; the script never promotes a moving checkout to that status.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = "frozen-confirmatory-v2-84126123"
REFERENCE = {
    "C1": ("0.998467", "0.523667", "0.139467", "272.793"),
    "SE-A": ("0.998533", "0.522067", "0.137467", "267.558"),
    "SE-E": ("0.662333", "0.366133", "0.156333", "816.588"),
}
METRICS = ("es_immediate", "ret_es_end", "ret_gs_end")


def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def git(*args: str, root: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def reconstruct(root: Path = ROOT) -> dict:
    """Check the complete paired grid, phase ledgers and saved item acquisition."""
    runs, means, identities = {}, {}, {}
    for arm, expected in REFERENCE.items():
        stage = "S4" if arm == "C1" else "S5"
        files = sorted((root / "results" / stage / EXPERIMENT / "zsre" / arm).rglob("metrics.json"))
        require(len(files) == 15, f"{arm}: expected 15 complete runs, got {len(files)}")
        rows = []
        for p in files:
            names = [p, p.with_name("config.json"), p.with_name("cost.json"), p.with_name("items.jsonl")]
            before = {str(n.relative_to(root)): sha(n) for n in names}
            m, c, cost = [json.loads(n.read_text()) for n in names[:3]]
            items = [json.loads(line) for line in names[3].read_text().splitlines() if line.strip()]
            r, o = int(c["realization"]), int(c["perm"])
            require(m["status"] == c["status"] == "complete", f"incomplete {p}")
            require(m["items_completed"] == m["items_planned"] == len(items) == 1000, f"item count {p}")
            require(c["experiment_id"] == EXPERIMENT and c["arm"] == arm and c["dataset"] == "zsre", f"identity {p}")
            require(m["base_hash_before"] == m["base_hash_after"] == c["base_hash_before"] == c["base_hash_after"], f"base changed {p}")
            for phase in ("learning", "query", "total"):
                require(cost[phase] == m["ledger_totals"][phase] == c["ledger_totals"][phase], f"ledger mismatch {phase} {p}")
            require(len({i["item_id"] for i in items}) == 1000, f"duplicate items {p}")
            require([i["index"] for i in items] == list(range(1000)), f"item order {p}")
            values = {k: float(m["metrics"][k]["value"]) for k in METRICS}
            for k in METRICS:
                require(m["metrics"][k]["status"] == "ok" and m["metrics"][k]["n"] == 1000, f"denominator {k} {p}")
                require(m["metrics"][k] == c["metrics"][k], f"config metric mismatch {p}")
            require(abs(statistics.mean(i["es"] for i in items) - values[METRICS[0]]) < 1e-12, f"acquisition mismatch {p}")
            key = (r, o)
            pairing = (c["manifest_sha256"], tuple(i["item_id"] for i in items))
            require(key not in identities or identities[key] == pairing, f"unpaired items/order {p}")
            identities[key] = pairing
            require(before == {str(n.relative_to(root)): sha(n) for n in names}, f"input changed while reading {p}")
            rows.append({"realization": r, "order": o, "order_seed": 100 + o,
                         "named_seeds": {"seed_cap_init": 1000*r + 10*o, "seed_router": 1000*r + 10*o + 1,
                                         "seed_replay": 1000*r + 10*o + 2},
                         "seed_provenance": "v2 DATA-02 seed convention; C1 metrics also record named seeds",
                         **values, "learning_seconds": float(cost["learning"]["accel_seconds"]),
                         "total_seconds": float(cost["total"]["accel_seconds"]),
                         "n_items": 1000, "input_sha256": before,
                         "historical_determinism": c["determinism"],
                         "historical_source_sha256": c["src_tree_sha256"],
                         "historical_code_commit": c["code_commit"],
                         "dataset_sha256": c["manifest_sha256"],
                         "base_parameter_digest": m["base_hash_before"]})
        require({(r["realization"], r["order"]) for r in rows} == {(r, o) for r in range(3) for o in range(5)}, f"{arm}: grid mismatch")
        rows.sort(key=lambda r: (r["realization"], r["order"]))
        keys = (*METRICS, "learning_seconds", "total_seconds")
        mean = {k: statistics.mean(r[k] for r in rows) for k in keys}
        display = tuple(f"{mean[k]:.6f}" for k in METRICS) + (f"{mean['learning_seconds']:.3f}",)
        require(display == expected, f"{arm}: guide mismatch {display} != {expected}")
        means[arm] = {**mean, "guide_display": display, "matches_guide": True,
                      "per_realization": {str(r): {k: statistics.mean(x[k] for x in rows if x["realization"] == r) for k in keys} for r in range(3)}}
        runs[arm] = rows
    return {"experiment_id": EXPERIMENT, "runs": runs, "means": means, "all_reference_checks_pass": True,
            "uncertainty": "15 orders per arm, grouped into 3 realizations; no new interval or independent n=15 claim",
            "retention_method": "saved endpoint metrics; acquisition additionally recounted from 45,000 per-item records"}


def seed_fields(value, prefix: str = "") -> dict:
    out = {}
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{prefix}.{k}" if prefix else k
            if "seed" in k.lower():
                out[p] = v
            else:
                out.update(seed_fields(v, p))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--closeout-commit", help="Optional exact lead-approved v0 close-out SHA; must equal HEAD")
    a = ap.parse_args()
    out = a.output.resolve()
    require(out.is_relative_to(ROOT) and not out.exists(), "output must be a new file inside pc_cap")
    started = time.monotonic()
    head = git("rev-parse", "HEAD").decode().strip()
    if a.closeout_commit:
        require(head == git("rev-parse", a.closeout_commit).decode().strip(), "close-out commit is not HEAD")
    diff = git("diff", "--binary", "HEAD")
    status = git("status", "--porcelain=v1", "-uall").decode()
    reference = reconstruct()
    assets = json.loads((ROOT / "manifests/assets.json").read_text())
    datasets = json.loads((ROOT / "manifests/datasets.json").read_text())
    asset_root = Path(os.environ.get("PCCAP_ASSETS", "/home/derp/cap/assets"))
    checked = {}

    def check(path: Path, expected: str | None) -> None:
        actual = sha(path) if path.is_file() else None
        checked[str(path)] = {"available": actual is not None, "expected_sha256": expected,
                              "actual_sha256": actual, "matches": actual == expected and actual is not None}

    for group in datasets.values():
        for name, expected in group.get("files", {}).items():
            check(asset_root / name, expected)
    for name in ("bp_teacher", "epc_checkpoint", "grammar_replacement"):
        row = assets["assets"][name]
        check(Path(row["path"]), row["sha256"])
    require(all(r["matches"] for r in checked.values()), "required asset missing or changed; no substitution allowed")
    manifest_paths = [ROOT / "manifests/assets.json", ROOT / "manifests/datasets.json",
                      ROOT / "manifests/frozen.json", ROOT / "requirements.lock"]
    manifest_paths += sorted((ROOT / "manifests/dev").glob("*.json"))
    manifest_paths += sorted((ROOT / "manifests/grammar").glob("*.json"))
    versions = {name: importlib.metadata.version(name) for name in ("jax", "jaxlib", "fabricpc", "numpy", "tokenizers")}
    # Do not probe CUDA: the active production queue owns the GPU.
    os.environ["JAX_PLATFORMS"] = "cpu"
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    import pccap

    determinism = pccap.determinism_report()
    snapshot = {"commit": head, "tracked_dirty_diff_sha256": hashlib.sha256(diff).hexdigest(),
                "tracked_dirty_diff": diff.decode(), "status_at_start": status,
                "untracked_files_included_in_diff": False,
                "status_at_end": git("status", "--porcelain=v1", "-uall").decode(),
                "commit_at_end": git("rev-parse", "HEAD").decode().strip()}
    snapshot["commit_and_tracked_diff_stable"] = snapshot["commit_at_end"] == head and git("diff", "--binary", "HEAD") == diff
    result = {"task": "R1-00", "written_utc": datetime.now(timezone.utc).isoformat(),
              "baseline_status": "lead_identified_closeout" if a.closeout_commit else "pre_closeout_snapshot_not_final_revision_freeze",
              "snapshot": snapshot, "python": {"executable": sys.executable, "version": platform.python_version()},
              "package_versions": versions, "audit_runtime": determinism,
              "historical_dtype": "float32 model parameters (bp._digest/gpt2_jax.to_device); x64 disabled in saved configs",
              "fabricpc": {"path": str(ROOT.parent / "FabricPC"),
                           "commit": git("rev-parse", "HEAD", root=ROOT.parent / "FabricPC").decode().strip(),
                           "dirty_diff_sha256": hashlib.sha256(git("diff", "--binary", "HEAD", root=ROOT.parent / "FabricPC")).hexdigest()},
              "assets": checked, "manifest_sha256": {str(p.relative_to(ROOT)): sha(p) for p in manifest_paths},
              "manifest_seed_fields": {str(p.relative_to(ROOT)): seed_fields(json.loads(p.read_text())) for p in manifest_paths if p.suffix == ".json"},
              "reference": reference, "gpu_seconds": 0, "wall_seconds": time.monotonic()-started,
              "limitations": ["No training or prediction rerun; retention is reconstructed from saved metrics.",
                              "New revision dataset selection and all model-training gates remain separate tasks.",
                              "Moving checkout status is disclosed; only --closeout-commit identifies the lead's final baseline."]}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps({"output": str(out), "reference_pass": True, "assets_verified": len(checked), "means": reference["means"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
