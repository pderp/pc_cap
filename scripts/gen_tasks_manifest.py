"""Generate manifests/tasks.json from the task graph of docs/updated_plan2.md (+ ongoing.md additions).

Run once at ENV-03; afterwards the orchestrator edits rows in place. Re-running preserves
status/agent/commit/evidence fields of existing rows.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "manifests" / "tasks.json"

# id, title, stage, role, deps, gpu, review
TASKS = [
    ("ENV-01", "Python environment (JAX venv) verified and completed", "ENV", "INTEGRATOR", [], "short", False),
    ("ENV-02", "Shared-workload benchmark and kappa", "ENV", "INTEGRATOR", ["ENV-01", "DATA-00"], "lease", False),
    ("ENV-03", "Package scaffold, contracts v0, Makefile, docs skeleton", "ENV", "INTEGRATOR", ["ENV-01"], "none", True),
    ("ENV-04", "Sibling reference recorder (read-only sibling, DEC-003)", "ENV", "INTEGRATOR", ["ENV-03"], "none", False),
    ("DATA-00", "Fetch and hash public assets into assets/", "DATA", "DATA", ["ENV-01"], "none", False),
    ("REF-01", "Reference oracle fixtures from HF PyTorch (CPU env under assets/)", "DATA", "DATA", ["DATA-00"], "none", False),
    ("S0-01", "Asset inventory and lead queue (T1)", "S0", "INTEGRATOR+BASE", ["ENV-04", "DATA-00"], "none", False),
    ("S0-03", "Schemas, outcome codes, CLI skeleton, ledger, records", "S0", "INTEGRATOR", ["ENV-03"], "none", True),
    ("S0-04", "BP base wrapper (GPT-2 small in JAX)", "S0", "BASE", ["ENV-01", "ENV-03", "DATA-00"], "short", True),
    ("S0-05", "Hidden-site adjoints and forced interventions", "S0", "BASE", ["S0-04"], "short", True),
    ("S0-06", "ePC base wrapper on FabricPC and declared energy (BP weights first)", "S0", "BASE", ["S0-04", "ENV-04"], "short", True),
    ("S0-07", "Metric library with known-answer tests", "S0", "METRICS", ["ENV-03"], "none", True),
    ("S0-07b", "HVP small-matrix controls (optional)", "S0", "METRICS", ["S0-07"], "none", False),
    ("S0-08", "Snapshot, clone, strict resume, resource-stop rollback", "S0", "INTEGRATOR", ["S0-03", "CAP-02"], "none", True),
    ("S0-09", "Development reservation, tokenization helper, reference decoder", "S0", "DATA", ["DATA-00", "S0-03"], "short", True),
    ("CAP-01", "Key features and deterministic retrieval", "S0", "MEMORY", ["ENV-03"], "none", False),
    ("CAP-02", "Slot metadata, use-count semantics, byte layout", "S0", "MEMORY", ["CAP-01"], "none", False),
    ("CAP-03", "Byte ceiling and capacity", "S0", "MEMORY", ["CAP-02"], "none", False),
    ("CAP-04", "Transactions, conflicts, eviction, revisions", "S0", "MEMORY", ["CAP-03", "S0-08"], "none", True),
    ("CAP-05", "Routers", "S0", "MEMORY+BASE", ["CAP-04", "S0-05"], "short", True),
    ("CAP-06", "Transactional candidate search and budget", "S0", "MEMORY", ["CAP-05"], "short", True),
    ("CAP-07", "Complete-edit learning loop", "S0", "MEMORY+DATA", ["CAP-06", "S0-09"], "short", True),
    ("S0-10", "Minimal cap integration smoke and the four pre-run invariants", "S0", "MEMORY", ["CAP-07", "S0-08", "S0-04"], "short", True),
    ("S0-11", "S0 stage report and CP-C", "S0", "INTEGRATOR", ["S0-10", "S0-06", "S0-07", "S0-09"], "none", True),
    ("REG-00", "JAX distillation driver for ePC regeneration (PA-1 enabler)", "REG", "BASE", ["DATA-00"], "short", False),
    ("REG-01", "Cost pilot (100 steps)", "REG", "BASE", ["ENV-04", "S0-01", "REG-00", "S0-06"], "lease", False),
    ("REG-02", "Full regeneration (<= 10 GPU-h)", "REG", "BASE", ["REG-01"], "lease", False),
    ("REG-03", "Load and preflight", "REG", "BASE", ["REG-02", "S0-06"], "short", True),
    ("GRAM-01", "Grammar generator per E.1", "GRAM", "DATA", ["ENV-03"], "none", True),
    ("GRAM-02", "Train the six-layer replacement grammar base", "GRAM", "DATA+BASE", ["GRAM-01"], "lease", False),
    ("DATA-07", "Causal tracing pairs on the grammar", "GRAM", "DATA+METRICS", ["GRAM-02"], "short", False),
    ("DATA-01", "Editing pools", "DATA", "DATA", ["S0-09"], "lease", True),
    ("DATA-02", "Realizations, orders, sealed confirmation manifests", "DATA", "DATA", ["DATA-01", "DATA-08"], "none", True),
    ("DATA-03", "MODULAR-CONTROL fixture", "DATA", "DATA+MEMORY", ["ENV-03", "CAP-05"], "none", True),
    ("DATA-04", "LM, probe and property sets with inventory", "DATA", "DATA+METRICS", ["DATA-00"], "none", False),
    ("DATA-06", "Grammar task streams", "DATA", "DATA", ["GRAM-02"], "none", False),
    ("DATA-08", "Challenge sets", "DATA", "DATA+BASELINES", ["DATA-01"], "short", False),
    ("ANA-01", "Frozen paired analysis code on synthetic tables (D.11)", "S4", "METRICS", ["ENV-03"], "none", True),
    ("S1-01", "P1 fidelity", "S1", "METRICS+BASE", ["REG-03", "DATA-04", "S0-11"], "lease", True),
    ("S1-02", "P2 geometry", "S1", "METRICS", ["S0-07", "DATA-04", "S0-04"], "short", False),
    ("S1-03", "P3 localization and coverage", "S1", "METRICS+BASE", ["S0-05", "S0-06", "DATA-04"], "short", False),
    ("S1-04", "P4 separability", "S1", "METRICS", ["DATA-04", "GRAM-02"], "short", False),
    ("S1-05", "P5 write locality", "S1", "BASE+METRICS", ["S0-10", "S2-01", "DATA-01"], "lease", False),
    ("S1-06", "P6 finite settling and informativeness", "S1", "BASE+METRICS", ["S0-06"], "lease", False),
    ("S1-07", "S1 report and D1 input", "S1", "INTEGRATOR+METRICS", ["S1-01", "S1-02", "S1-03", "S1-04", "S1-05", "S1-06"], "none", True),
    ("S2-01", "Residual scales and radius calibration", "S2", "BASE+MEMORY", ["S0-10", "DATA-01"], "lease", True),
    ("S2-02", "Aggregate step screening", "S2", "MEMORY+METRICS", ["S2-01"], "lease", True),
    ("S2-03", "LoRA baselines B1 (and B0)", "S2", "BASELINES", ["S0-09", "S0-04"], "short", True),
    ("S2-04", "Replay baseline B3", "S2", "BASELINES", ["S2-03", "S0-08"], "short", False),
    ("S2-05a", "GRACE reference environment and smoke (PA-6)", "S2", "BASELINES", ["DATA-00"], "none", False),
    ("S2-05b", "GRACE reference parity cases", "S2", "BASELINES", ["S2-05a", "S0-09"], "none", False),
    ("S2-05", "GRACE baseline B4 adapter with parity (PC-10)", "S2", "BASELINES", ["S2-05b", "S0-04"], "short", True),
    ("S2-06", "Throughput profile", "S2", "INTEGRATOR", ["S2-01", "S2-02", "S2-03", "S2-04", "S2-05"], "lease", True),
    ("S2-07", "Full cost projection and D1 memo", "S2", "INTEGRATOR+METRICS", ["S2-06", "S1-07", "ENV-02"], "none", True),
    ("CAP-08", "Read variants R-h0, R-g, R-e (optional)", "S2", "BASE+MEMORY", ["S0-10", "S0-06"], "short", True),
    ("CAP-09", "Optional difficulty weight", "S2", "MEMORY", ["CAP-07"], "none", False),
    ("S3-01", "Full control suite and development run matrix", "S3", "INTEGRATOR", ["S0-11", "DATA-03", "CAP-07", "S2-05", "DATA-06"], "short", True),
    ("S3-02", "Constructed fixture runs", "S3", "MEMORY+DATA", ["S3-01"], "short", False),
    ("S3-03", "Learned grammar runs and tracing", "S3", "DATA+METRICS", ["S3-01", "DATA-07"], "lease", False),
    ("S3-04", "Short editing checks", "S3", "BASELINES+MEMORY", ["S3-01"], "lease", False),
    ("S3-05", "CR distribution and re-profile", "S3", "METRICS+INTEGRATOR", ["S3-02", "S3-03", "S3-04"], "lease", True),
    ("S3-06", "D2 memo", "S3", "INTEGRATOR", ["S3-05", "S1-07"], "none", True),
    ("S4-01", "Frozen manifest", "S4", "INTEGRATOR", ["S3-06", "DATA-02", "DATA-08", "S2-07", "ANA-01"], "none", True),
    ("S4-02", "Scope selection", "S4", "INTEGRATOR", ["S4-01"], "none", True),
    ("S4-03", "Confirmatory run schedule", "S4", "run owner", ["S4-02"], "none", False),
    ("S4-04", "Confirmatory run execution", "S4", "run owner", ["S4-03"], "lease", False),
    ("S4-05", "Resource views", "S4", "METRICS", ["S4-04"], "none", False),
    ("S4-06", "Frozen paired analysis and D3 audit", "S4", "METRICS+INTEGRATOR", ["S4-05"], "none", True),
    ("S5-01", "Eligibility and arm definition", "S5", "BASE+INTEGRATOR", ["S4-01", "S1-07", "REG-03"], "none", False),
    ("S5-02", "Substrate execution", "S5", "run owner", ["S5-01"], "lease", False),
    ("S5-03", "Optional substrate repeats and read variants", "S5", "run owner", ["S5-02", "CAP-08"], "lease", False),
    ("S5-04", "S5 report", "S5", "METRICS", ["S5-02"], "none", False),
    ("S6-01", "Deficit statement and authorization", "S6", "BASE", ["S3-06"], "none", True),
    ("S6-02", "Regularizer implementation", "S6", "BASE", ["S6-01"], "short", False),
    ("S6-03", "Differentiable error features (create_graph path) with FD test", "S6", "BASE", ["S6-02"], "short", True),
    ("S6-04", "Matched continuation pair EPC-CONT / EPC-REG", "S6", "BASE", ["S6-03"], "lease", False),
    ("S6-05", "P1-P6 on both arms", "S6", "METRICS", ["S6-04"], "lease", False),
    ("S7-01", "Cloned-state reversals", "S7", "METRICS", ["S4-04"], "lease", False),
    ("S7-02", "Damage matrix", "S7", "METRICS", ["S7-01"], "lease", False),
    ("S7-03", "Order variation from permutations", "S7", "METRICS", ["S4-04"], "none", False),
    ("S7-04", "Optional HVP diagnostics", "S7", "METRICS", ["S7-03", "S0-07b"], "lease", False),
    ("S8-01", "Core completion and reproduction audit", "S8", "INTEGRATOR+METRICS", ["S4-06"], "lease", True),
    ("S8-02", "Fixed exploratory ablations", "S8", "run owner", ["S8-01"], "lease", False),
    ("S8-03", "Integrated report", "S8", "INTEGRATOR", ["S8-01", "S5-04", "S7-03"], "none", True),
    ("S8-04", "Handoff package and T4", "S8", "INTEGRATOR", ["S8-03"], "none", True),
]


def main() -> int:
    existing: dict[str, dict] = {}
    if OUT.exists():
        for row in json.loads(OUT.read_text())["tasks"]:
            existing[row["id"]] = row
    ids = {t[0] for t in TASKS}
    rows = []
    for tid, title, stage, role, deps, gpu, review in TASKS:
        for d in deps:
            if d not in ids:
                print(f"unknown dependency {d} for {tid}", file=sys.stderr)
                return 1
        prev = existing.get(tid, {})
        rows.append(
            {
                "id": tid,
                "title": title,
                "stage": stage,
                "role": role,
                "deps": deps,
                "gpu": gpu,
                "review": review,
                "status": prev.get("status", "pending"),
                "agent": prev.get("agent"),
                "worktree": prev.get("worktree"),
                "started": prev.get("started"),
                "finished": prev.get("finished"),
                "commit": prev.get("commit"),
                "evidence": prev.get("evidence", []),
                "gpu_seconds": prev.get("gpu_seconds", 0.0),
                "wall_seconds": prev.get("wall_seconds", 0.0),
                "note": prev.get("note", ""),
            }
        )
    OUT.write_text(json.dumps({"version": 1, "tasks": rows}, indent=1) + "\n")
    print(f"wrote {OUT} ({len(rows)} tasks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
