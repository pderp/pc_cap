"""S4-01: assemble the frozen manifest (plan §6.10 S4-01; PDF Op. rule 4).

``python -m pccap.harness.freeze --draft`` writes ``manifests/frozen.draft.json`` from the development
evidence on disk (S2-01/02 numerics, S3-05 CR distribution, DATA-02 sealed manifests, D1 scope,
DEC-009 policy text, SD-1…18, hashes of code/env/PDF/base) and validates it against
``pccap.harness.schema.MANIFEST_FROZEN``; fields whose inputs do not exist yet are filled with
``null`` plus a ``pending`` note and listed. ``--final`` writes ``manifests/frozen.json`` — the CP-E
act that unlocks confirmation access (§4.5 rule 4) — and is the lead's decision: it refuses unless
``--i-am-the-lead`` is also given.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path

import jsonschema

from pccap.cap.memory import b_cap, bank_ceilings, capacity, slot_bytes
from pccap.harness.schema import MANIFEST_FROZEN

ROOT = Path(__file__).resolve().parents[3]
R = ROOT / "results"
M = ROOT / "manifests"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_sha(root: Path, pattern: str = "*.py") -> str:
    h = hashlib.sha256()
    for p in sorted(root.rglob(pattern)):
        if "__pycache__" in p.parts:
            continue
        h.update(p.relative_to(root).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def git(*args) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True, timeout=20).strip()
    except Exception as e:  # pragma: no cover
        return f"unavailable ({e})"


def load(p: Path, default=None):
    return json.loads(p.read_text()) if p.exists() else default


def spec_defects() -> list[dict]:
    rows = []
    for line in (ROOT / "docs" / "spec_defects.md").read_text().splitlines():
        m = re.match(r"^\| (SD-\d+) \| (.*?) \| (.*?) \| (.*?) \|$", line)
        if m:
            rows.append({"id": m.group(1), "issue": m.group(2), "resolution": m.group(3), "status": m.group(4)})
    return rows


def decision_text(dec_id: str) -> str:
    for line in (ROOT / "docs" / "decisions.md").read_text().splitlines():
        if line.startswith(f"| {dec_id} |"):
            return line.split("|")[3].strip()
    return ""


def build(draft: bool = True) -> tuple[dict, list[str]]:
    pending: list[str] = []
    snap = ROOT / ".." / "assets" / "models" / "gpt2"
    snap = Path("/home/derp/cap/assets/models/gpt2")
    datasets = load(M / "datasets.json", {})
    screening = load(R / "S2" / "A_screening.json", {})
    cr = load(M / "cr_distribution.json")
    proj = load(R / "S2" / "projection.json", {})
    kappa = load(R / "ENV" / "kappa.json", {"kappa": 1.0, "kappa_band": [0.5, 2.0], "status": "provisional"})
    sums = M / "confirm" / "SHA256SUMS"
    dataset_ids: dict = {"zsre": {}, "counterfact": {}, "grammar": None}
    if sums.exists():
        for line in sums.read_text().splitlines():
            h, name = line.split()
            dataset_ids[name.split("_")[0]][name] = h
    else:
        pending.append("dataset_ids (DATA-02 SHA256SUMS missing)")
    if dataset_ids["grammar"] is None:
        pending.append("dataset_ids.grammar (GRAM-02 / DATA-06)")
    if cr is None:
        pending.append("cr_distribution (S3-05)")
    d = 768
    caps = {}
    for arm in ("C0", "C1", "C2", "CR"):
        caps[arm] = {str(m): capacity(B, d, d) for m, B in bank_ceilings(arm, d).items()}
    epc_final = Path("/home/derp/cap/assets/models/epc/epc-50m/checkpoints")
    epc_ck = None
    if (epc_final / "latest").exists():
        latest = epc_final / (epc_final / "latest").read_text().strip()
        if latest.name.startswith("final"):
            epc_ck = {"path": str(latest / "params.npz"), "sha256": sha(latest / "params.npz"), "provenance": "REG-02 (JAX re-implementation, DEC-014/015; REG-00 float32 fix)"}
    if epc_ck is None:
        pending.append("base_checkpoints.epc (REG-02/03; S5 only)")
    lr_screen = {}
    for tag, lr in (("baselines", 1e-4), ("lr3e-5", 3e-5), ("lr3e-4", 3e-4)):
        t = load(R / "S2" / f"throughput_{tag}.json")
        if t:
            lr_screen[str(lr)] = {ds: {k: t["runs"][f"B1/{ds}"]["metrics"][k] for k in ("es_immediate", "ret_gs_end", "ls_complete_answer_end", "lm_drift_perplexity_ratio")}
                                  for ds in ("zsre", "counterfact") if f"B1/{ds}" in t["runs"]}
    chosen_lr = choose_lr(lr_screen) if len(lr_screen) == 3 else None
    if chosen_lr is None:
        pending.append("lora.lr (development screen {3e-5, 1e-4, 3e-4} incomplete)")
    sel = proj.get("selected") or {}
    man = {
        "name": "frozen-confirmatory-v1" + ("-draft" if draft else ""), "mode": "confirm", "stage": "S4", "seed": 0,
        "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) if not draft else None, "draft": draft,
        "code_commit": {"git_head": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain")), "src_tree_sha256": tree_sha(ROOT / "src" / "pccap"),
                        "note": "the lead commits; src_tree_sha256 identifies the uncommitted working tree"},
        "env_lock_sha": sha(ROOT / "requirements.lock") if (ROOT / "requirements.lock").exists() else None,
        "pdf_sha": sha(ROOT / "docs" / "pc_cap_month_plan_readable.pdf"),
        "base_checkpoints": {"bp": {"snapshot": snap.name, "safetensors_sha256": datasets.get("gpt2", {}).get("files", {}).get("models/gpt2/model.safetensors")}, "epc": epc_ck},
        "tokenizer_rev": {"snapshot_revision": "607a30d7", "tokenizer_json_sha256": datasets.get("gpt2", {}).get("files", {}).get("models/gpt2/tokenizer.json")},
        "bank_sites": {"1": 3, "2": 7, "3": 11},
        "radii": {"bank": screening.get("radii_per_dataset"), "read": "h", "rule": "SD-17: per dataset, shared across arms; CounterFact exact keys (0.0)"},
        "b_m": screening.get("b_m"), "A": screening.get("chosen_A", 0.3), "epsilon": 0.01, "R": 5, "tau_edit": 0.1,
        "byte_ceiling": b_cap(d), "slot_bytes": slot_bytes(d, d), "slot_capacities": caps,
        "cr_distribution": {"zsre": cr["per_dataset"]["zsre"]["distribution"], "counterfact": cr["per_dataset"]["counterfact"]["distribution"],
                            "grammar": None, "labels": {k: v["label"] for k, v in cr["per_dataset"].items()}, "rule": cr["rule"]} if cr else None,
        "dataset_ids": dataset_ids, "confirm_dir": (M / "confirm").relative_to(ROOT).as_posix(), "realizations": [0, 1, 2], "order_seeds": [100, 101, 102, 103, 104],
        "cap_seed": "1000*realization + 10*(order_seed-100)", "router_seed": "1000*realization + 10*(order_seed-100) + 1",
        "replay_seed": "1000*realization + 10*(order_seed-100) + 2",
        "stream_lengths": {"zsre": sel.get("zsre"), "counterfact": sel.get("counterfact"), "grammar_train_count": sel.get("grammar"),
                           "c0_initial": 300, "source": "S2-07 projection (S4-02 confirms the scope before any confirmatory access)"},
        "arms": ["C0", "C1", "C2", "CR", "B0", "B1", "B3", "B4"],
        "arm_availability": {"B4": "unavailable until S2-05 (GRACE, PA-6)", "grammar": "unavailable until GRAM-02 (PA-2)"},
        "contrasts": [["C2", "C1"], ["C2", "CR"], ["C2", "C0"], ["C2", "B3"], ["C2", "B4"]],
        "required_contrasts": [["C2", "C1"], ["C2", "CR"]],
        "primary_endpoint": "RET-GS", "margins": {"ret_gs": 0.02, "es": -0.02, "ls": -0.01},
        "interval": {"method": "paired-cluster-bootstrap", "draws": 10000, "level": 0.975},
        "checkpoints": [100, 300, 1000, 3000],
        "challenge_policy": {"sets": ["near_neighbour", "composition", "temporal_correction"], "manifest": "manifests/dev/challenges.json",
                             "manifest_sha256": sha(M / "dev" / "challenges.json") if (M / "dev" / "challenges.json").exists() else None,
                             "rule": "challenge sets are disjoint from development and confirmation streams and are evaluated and reported separately; they never enter the primary endpoint; the correction track alone enables RevisionEvent slot retirement (SD-4)"},
        "resource_rules": {"headroom": 0.25, "kappa": kappa["kappa"], "kappa_band": kappa["kappa_band"], "kappa_status": kappa["status"],
                           "stop_boundary": "a run stops at an item boundary when its ledger exceeds the allowance; the incomplete item is rolled back (ItemGuard) and its cost kept; status resource_stop with the exact completed prefix; no imputation"},
        "analysis_code_commit": {"git_head": git("rev-parse", "HEAD"), "analysis_tree_sha256": tree_sha(ROOT / "src" / "pccap" / "analysis")},
        "negative_case_interpretation": decision_text("DEC-009"),
        "classification_policy": decision_text("DEC-009"),
        "spec_defect_resolutions": spec_defects(),
        "lora": {"rank": 8, "steps": 10, "lr": chosen_lr, "screen": lr_screen, "rule": "DEC-017: highest mean development RET-GS (primary endpoint) over both datasets; ties -> the prescribed 1e-4; ES/LS/drift reported, not optimized"},
        "b3_policy": "growing_capacity_algorithm_r_not_uniform_all_history (DEC-016)",
        "substrate_arms": load(M / "dev" / "s5_arms.json", {}).get("arms"),
        "substrate_contrasts": [["SE-A", "SB"], ["SE-E", "SE-A"]],
        "exploratory_ablations": {"list_frozen_at": "S4-01 (plan §6.14 S8-02)", "design": "3 realizations × 2 orders, labelled exploratory, dropped before any core pair",
                                  "items": ["R-h0 vs R-h", "half B_cap", "double B_cap", "difficulty weight (CAP-09)", "R-e vs R-g (only if CAP-08 is built)"]},
        "decisions": [f"DEC-{i:03d}" for i in range(0, 17)],
        "pending": pending,
    }
    return man, pending


def choose_lr(screen: dict) -> float | None:
    """DEC-017: the learning rate with the highest mean development RET-GS (the primary endpoint) over
    the two datasets; ties → the prescribed 1e-4. ES/LS/drift are reported alongside, not optimized."""
    rows = []
    for lr, per in screen.items():
        rg = sum(v["ret_gs_end"] for v in per.values()) / len(per)
        rows.append((float(lr), rg))
    rows.sort(key=lambda r: (-round(r[1], 6), abs(r[0] - 1e-4)))
    return rows[0][0] if rows else 1e-4


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true", default=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--i-am-the-lead", action="store_true")
    args = ap.parse_args(argv)
    if args.final and not args.i_am_the_lead:
        raise SystemExit("writing manifests/frozen.json is the lead's CP-E act: pass --final --i-am-the-lead")
    man, pending = build(draft=not args.final)
    errors = sorted(jsonschema.Draft202012Validator(MANIFEST_FROZEN).iter_errors(man), key=lambda e: list(e.path))
    out = M / ("frozen.json" if args.final else "frozen.draft.json")
    out.write_text(json.dumps(man, indent=1, default=float) + "\n")
    print("wrote", out)
    print("schema errors:", [f"{'/'.join(map(str, e.path))}: {e.message[:80]}" for e in errors] or "none")
    print("pending inputs:", pending or "none")
    return 1 if (errors and args.final) else 0


if __name__ == "__main__":
    raise SystemExit(main())
