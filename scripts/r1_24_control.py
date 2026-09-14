"""R1-24 CPU recipe/manifest preparation; --gpu explicitly launches the leased control.

Default preparation never imports JAX. All output paths are exclusive-create.
The original REG driver is deliberately not invoked: it resumes/prunes its own
50M-token run. This control has a separate budget, estimator and output tree.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
DEFAULT_MANIFEST = ROOT / "manifests/revision_v1/r1_24_control.json"
DEFAULT_PILOT = ROOT / "results/R1/pilot/cf_pool3k_pairnull_400/summary.json"
CALIBRATION = ROOT / "manifests/archive/frozen-confirmatory-v2-84126123-superseded-for-grammar-20260913.json"
OWT_SHA = "ae5b795aadcd3ef8990826c1ef37661b53b216e962e3bec8510a8758fecf540d"
OWT_TOKENS = 52_500_000
TRAIN_END = 50_001_920


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def write_new(path, value):
    path = Path(path)
    if not path.resolve().is_relative_to(ROOT):
        raise ValueError("logs/manifests must be inside pc_cap")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")


def integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(name + " must be an integer >= " + str(minimum))
    return value


def read_budgets(paths):
    rows, seen_paths, seen_tags = [], set(), set()
    for path in paths:
        p = Path(path).resolve()
        s = json.loads(p.read_text())
        tag = s["args"]["tag"]
        if p in seen_paths or tag in seen_tags:
            raise ValueError("duplicate pilot path or run tag")
        seen_paths.add(p)
        seen_tags.add(tag)
        steps = integer(s["args"]["steps"], "training steps", 1)
        if s["args"].get("eval_theta"):
            raise ValueError("evaluation-only pilot cannot define a training budget")
        ledger = s["ledger"]
        learning = integer(ledger["learning"]["tokens"], "learning tokens", 1)
        query = integer(ledger["query"]["tokens"], "query tokens")
        total = integer(ledger["total"]["tokens"], "total tokens")
        if learning + query != total:
            raise ValueError("ledger phase totals do not reconcile")
        rows.append({"path": str(p), "sha256": sha(p), "tag": tag, "steps": steps,
            "reported_learning_tokens": learning, "query_tokens_excluded": query,
            "estimator": s.get("estimator", s["args"].get("estimator")),
            "theta_path": s["theta_path"], "theta_selection": s.get("best_dev")})
    if not rows:
        raise ValueError("select at least one complete training pilot")
    return rows


def match_budget(pass_tokens, seq_len=128):
    integer(pass_tokens, "pass tokens", 2)
    integer(seq_len, "sequence length", 1)
    source_tokens, unspent = divmod(pass_tokens, 2)
    if source_tokens > TRAIN_END:
        raise ValueError("budget would enter the REG fidelity tail; no wrapping allowed")
    full_steps, tail = divmod(source_tokens, seq_len)
    return {"requested_forward_pass_tokens": pass_tokens, "source_tokens": source_tokens,
        "teacher_forward_tokens": source_tokens, "student_forward_tokens": source_tokens,
        "charged_forward_pass_tokens": 2 * source_tokens, "unspent_odd_pass_token": unspent,
        "seq_len": seq_len, "full_steps": full_steps, "tail_sequence_tokens": tail,
        "optimizer_steps": full_steps + bool(tail), "student_reverse_passes": full_steps + bool(tail),
        "reverse_token_positions_separately_reported": source_tokens,
        "unit": "input tokens on full teacher/student forward passes; reverse sweeps reported separately"}


def validate_manifest(m):
    if m.get("schema_version") != 1 or m.get("task") != "R1-24":
        raise ValueError("unsupported control manifest")
    b = m["budget"]
    if b["arithmetic"] != match_budget(b["matched_tokens"], m["recipe"]["seq_len"]):
        raise ValueError("budget arithmetic mismatch")
    if b["reported_learning_tokens"] != sum(integer(x["reported_learning_tokens"], "pilot tokens", 1) for x in b["pilots"]):
        raise ValueError("pilot sum mismatch")
    if not b["exact_training_passes_verified"] and b["matched_tokens"] != b["reported_learning_tokens"]:
        raise ValueError("unverified budget must equal the recorded ledger sum")
    if m["teacher"]["sha256"] != m["student_start"]["sha256"] or m["teacher"]["path"] != m["student_start"]["path"]:
        raise ValueError("this version is literal same-checkpoint self-distillation")
    if m["recipe"]["weight_decay"] != 0 or m["recipe"]["optimizer_reset"] is not True:
        raise ValueError("self-distillation requires zero decay and fresh optimizer state")
    ev = m["evaluation"]
    if ev["datasets"] != ["zsre", "counterfact"] or ev["edits_per_stream"] != 100:
        raise ValueError("control requires both fixed 100-edit development streams")
    if ev["drift_scored_positions"] != ev["drift_windows"] * (ev["drift_window"] - 1):
        raise ValueError("drift position arithmetic mismatch")
    if m["data"]["train_end_exclusive"] != TRAIN_END:
        raise ValueError("held-out token boundary changed")
    return m


def verify_sources(m):
    for p, expected in m["sources_sha256"].items():
        if sha(p) != expected:
            raise ValueError("source changed; prepare a new manifest version: " + p)


def prepare(paths, reconciliation=None):
    pilots = read_budgets(paths)
    source_hashes = {}
    def bind(p, expected=None):
        p = Path(p).resolve()
        h = sha(p)
        if expected is not None and h != expected:
            raise ValueError("pinned input hash mismatch: " + str(p))
        source_hashes[str(p)] = h
        return {"path": str(p), "sha256": h}
    reference_path = ROOT / "manifests/reference.json"
    reference = json.loads(reference_path.read_text())
    bind(reference_path)
    bind(ROOT / "manifests/assets.json")
    bind(ROOT / "manifests/frozen.json")
    bind(CALIBRATION)
    bind(ROOT / "docs/decisions.md")
    frozen = json.loads((ROOT / "manifests/frozen.json").read_text())
    for name in ("config.json", "tokenizer.json", "merges.txt", "vocab.json"):
        x = reference["inputs"][name]
        bind(x["path"], x["sha256"])
    x = reference["inputs"]["model.safetensors"]
    teacher = bind(x["path"], x["sha256"])
    theta = bind(pilots[-1]["theta_path"])
    for p in pilots:
        bind(p["path"], p["sha256"])
    for ds in ("zsre", "counterfact"):
        bind(ROOT / f"manifests/dev/{ds}_dev.json")
    bind(ROOT / "manifests/dev/s0_sample.json")
    bind(ROOT / "manifests/dev/lm_sets.json")
    drift = json.loads((ROOT / "manifests/dev/lm_sets.json").read_text())["files"]["drift_tokens"]
    bind(drift["path"], drift["sha256"])
    shard = bind(ASSETS / "data/raw/openwebtext/openwebtext.bin", OWT_SHA)
    if Path(shard["path"]).stat().st_size != 2 * OWT_TOKENS:
        raise ValueError("unexpected OWT uint16 shard length")
    # Bind source implementations. Future repairs require a new manifest; do not
    # silently switch algorithms between preparation and execution.
    for p in sorted((ROOT / "src/pccap").rglob("*.py")):
        bind(p)
    for name in ("r1_24_control.py", "r1_24_runtime.py"):
        bind(ROOT / "scripts" / name)
    reported = sum(p["reported_learning_tokens"] for p in pilots)
    matched, verified, rec_identity = reported, False, None
    if reconciliation:
        rec_identity = bind(reconciliation)
        rec = json.loads(Path(reconciliation).read_text())
        expected = {p["path"]: p["sha256"] for p in pilots}
        if rec.get("pilot_sources_sha256") != expected or rec.get("status") != "verified" or not rec.get("basis"):
            raise ValueError("reconciliation must identify exactly these pilots and document verified pass counting")
        matched = integer(rec["training_forward_pass_tokens"], "reconciled forward tokens", 2)
        verified = True
    m = {"schema_version": 1, "task": "R1-24", "status": "cpu_prepared_gpu_not_run",
        "v0_closeout_commit": "cb04d5e", "teacher": teacher, "student_start": dict(teacher),
        "start_interpretation": "v0 BP GPT-2 checkpoint, matching the frozen BP base used by current revision pilots; not regenerated SE-A",
        "recipe": {"estimator": "exact_bp_kl_base_continuation", "objective": "mean T^2 KL(teacher || student) over all input positions",
            "seq_len": 128, "batch_size": 1, "temperature": 2.0, "optimizer": "Adam", "weight_lr": 1e-6,
            "betas": [0.9, 0.999], "eps": 1e-8, "weight_decay": 0.0, "optimizer_reset": True, "dropout": False,
            "seed": 1729, "reuse": "distill.recipe optimizer constants; distill.data.load_shard; distill.train.batched_logits; GPT2 NPZ format",
            "difference_from_REG": "BP updates, token-mean loss, seq128/batch1, no ePC relaxation/homotopy, exact partial final batch"},
        "data": {**shard, "dtype": "uint16-le", "tokens": OWT_TOKENS, "train_start": 0,
            "train_end_exclusive": TRAIN_END, "wrap": False, "heldout_start": TRAIN_END},
        "budget": {"pilots": pilots, "reported_learning_tokens": reported, "matched_tokens": matched,
            "exact_training_passes_verified": verified, "reconciliation": rec_identity,
            "source_scope": "explicit selected training pilots only; no automatic glob sum; post-best-checkpoint work still charged",
            "limitations": ["BP direct outer-gradient GPT-2 calls are absent from the ledger.",
                "Learning phase includes featurization and some development scoring.",
                "ePC token totals do not multiply every relaxation pass.",
                "Without reconciliation this is a reported-ledger diagnostic, not a compute-matched control."],
            "arithmetic": match_budget(matched)},
        "evaluation": {"datasets": ["zsre", "counterfact"], "edits_per_stream": 100, "selection_seed": 21,
            "update_seed": 1, "exclude_s0": True, "locality_prompts": 50, "cap_seed": 0,
            "base_conditions": ["original", "continued"], "caps": ["v0_stable_C1", "revision"],
            "theta": theta, "theta_policy": "fixed selected pilot theta on both bases; no retuning/retraining in this control",
            "reader": {"pairwise_null": True}, "fast_steps": 0, "delta_steps": 5, "delta_lr": 0.1,
            "null_threshold": 0.5, "min_score": None, "calibration": str(CALIBRATION),
            "locality_reference": "original base for all four cells (common reference)",
            "drift": drift, "drift_window": 128, "drift_windows": 128, "drift_scored_positions": 16256,
            "drift_scope": "same fixed-prefix method as drift_supplement, declared development subset, not full validation split",
            "query_boundary": "reset each independent query; teacher-forced prefixes explicitly select original prompt before prediction",
            "fidelity_windows": 64, "fidelity_window": 128, "fidelity_kl_temperature": 1.0,
            "margins": {"ret_gs": 0.05, "es": -0.02, "ls": -0.01, "kl_nats": 0.001, "nll_increase": 0.01}},
        "stopping": {"training_wall_seconds": 1800, "total_wall_seconds": 7200,
            "checks": "before every optimizer/evaluation unit; one in-flight kernel may overshoot; nonfinite update rejected",
            "thresholds": "held-out KL > .001 or NLL increase > .01 labels fidelity failure; no threshold-based hyperparameter search",
            "historical_allowances_not_new_allocation": frozen.get("stage_allowance_seconds", frozen.get("budget", {})),
            "allocation_note": "proposed finite ceilings only; orchestrator schedules GPU execution and accounts its development allowance"},
        "self_distillation_caveat": "same deterministic checkpoint, zero optimizer moments and zero decay imply zero KL and gradient in exact arithmetic; this is a numerical negative control, not informative extra-learning treatment",
        "sources_sha256": source_hashes, "gpu_seconds": 0, "training_executed": False}
    return validate_manifest(m)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--pilot-summary", type=Path, action="append")
    ap.add_argument("--budget-reconciliation", type=Path)
    ap.add_argument("--gpu", action="store_true")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--allow-reported-ledger-budget", action="store_true",
        help="explicitly label GPU output diagnostic when pilot pass counting is unreconciled")
    args = ap.parse_args(argv)
    if args.gpu:
        if args.pilot_summary or args.budget_reconciliation:
            ap.error("GPU mode reads the frozen manifest; prepare a new manifest to change inputs")
        if not args.run_id or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id):
            ap.error("GPU mode requires a new simple --run-id")
        m = validate_manifest(json.loads(args.manifest.read_text()))
        if not m["budget"]["exact_training_passes_verified"] and not args.allow_reported_ledger_budget:
            raise ValueError("pilot pass accounting is unreconciled; provide a new reconciled manifest or explicitly request the reported-ledger diagnostic")
        verify_sources(m)
        from r1_24_runtime import execute
        return execute(m, args.manifest.resolve(), args.run_id)
    if args.manifest.exists():
        raise FileExistsError("preparation never overwrites an existing manifest")
    m = prepare(args.pilot_summary or [DEFAULT_PILOT], args.budget_reconciliation)
    write_new(args.manifest, m)
    print(json.dumps({"manifest": str(args.manifest), "budget": m["budget"]["arithmetic"],
        "exact_training_passes_verified": m["budget"]["exact_training_passes_verified"], "gpu_seconds": 0}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
