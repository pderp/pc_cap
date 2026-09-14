"""R1-24b: CPU-only LM-continuation recipe; no training or launch entry point."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRAIN_END = 50_001_920


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def integer(value, name, minimum=0):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def lm_budget(pass_tokens, seq_len=128, train_end=TRAIN_END):
    """One student forward per input; each logit predicts the next shard token.

    Inputs [s:s+n], targets [s+1:s+n+1]. This scores every consecutive next
    token, including the last logit in a chunk, without crossing the train tail.
    """
    integer(pass_tokens, "pass_tokens", 1)
    integer(seq_len, "seq_len", 1)
    integer(train_end, "train_end", 2)
    if pass_tokens + 1 > train_end:
        raise ValueError("final next-token label would enter the held-out tail")
    full, tail = divmod(pass_tokens, seq_len)
    steps = full + int(tail > 0)
    return {"requested_forward_pass_tokens": pass_tokens, "charged_forward_pass_tokens": pass_tokens,
            "student_forward_tokens": pass_tokens, "teacher_forward_tokens": 0,
            "student_reverse_token_positions": pass_tokens, "scored_next_token_targets": pass_tokens,
            "unique_source_tokens_read": pass_tokens + 1, "seq_len": seq_len,
            "full_steps": full, "tail_sequence_tokens": tail, "optimizer_steps": steps,
            "student_reverse_passes": steps, "input_start": 0, "input_end_exclusive": pass_tokens,
            "target_start": 1, "target_end_exclusive": pass_tokens + 1,
            "unit": "valid student forward input-token positions; reverse work and lookahead reads separate"}


def batches(pass_tokens, seq_len=128, train_end=TRAIN_END):
    b = lm_budget(pass_tokens, seq_len, train_end)
    for start in range(0, b["student_forward_tokens"], seq_len):
        end = min(start + seq_len, pass_tokens)
        yield {"input_start": start, "input_end": end, "target_start": start + 1,
               "target_end": end + 1, "valid_positions": end - start}


def read_pilot(path):
    obj = json.loads(Path(path).read_text())
    args, ledger = obj["args"], obj["ledger"]
    integer(args["steps"], "training steps", 1)
    if args.get("eval_theta"):
        raise ValueError("evaluation-only summary cannot define the training budget")
    learning = integer(ledger["learning"]["tokens"], "learning tokens", 1)
    query = integer(ledger["query"]["tokens"], "query tokens")
    if learning + query != ledger["total"]["tokens"]:
        raise ValueError("pilot token ledger does not reconcile")
    return {"path": str(Path(path).resolve()), "sha256": sha(path), "tag": args.get("tag", Path(path).parent.name),
            "steps": args["steps"], "reported_learning_tokens": learning, "query_tokens_excluded": query}


def validate(m):
    if m["task"] != "R1-24b" or m["launch_allowed"] or m["training_executed"]:
        raise ValueError("only an unlaunched R1-24b dry recipe is supported")
    b = m["budget"]
    if b["arithmetic"] != lm_budget(b["matched_tokens"], m["recipe"]["seq_len"], m["data"]["train_end_exclusive"]):
        raise ValueError("LM token arithmetic mismatch")
    if b["matched_tokens"] != sum(p["reported_learning_tokens"] for p in b["pilots"]):
        raise ValueError("selected pilot ledger sum mismatch")
    if m["recipe"]["teacher_forward_required"] or m["recipe"]["objective"] != "mean next-token cross-entropy over valid consecutive positions":
        raise ValueError("recipe must specify hard next-token targets, not teacher distillation")
    if m["recipe"]["optimizer"] != "Adam" or not m["recipe"]["optimizer_reset"]:
        raise ValueError("fresh Adam is the declared continuation optimizer")
    if m["evaluation_sha256"] != hashlib.sha256(json.dumps(m["evaluation"], sort_keys=True).encode()).hexdigest():
        raise ValueError("evaluation block identity mismatch")
    return m


def prepare(companion):
    companion = Path(companion).resolve()
    literal = json.loads(companion.read_text())
    if literal.get("task") != "R1-24" or literal["budget"]["exact_training_passes_verified"]:
        raise ValueError("this draft expects the existing unreconciled literal control; reconcile both together in a new version")
    pilots = [read_pilot(p["path"]) for p in literal["budget"]["pilots"]]
    if len({p["path"] for p in pilots}) != len(pilots) or len({p["tag"] for p in pilots}) != len(pilots):
        raise ValueError("duplicate selected pilot")
    for p, old in zip(pilots, literal["budget"]["pilots"]):
        if p["sha256"] != old["sha256"]:
            raise ValueError("selected pilot changed since literal recipe")
    reported = sum(p["reported_learning_tokens"] for p in pilots)
    if reported != literal["budget"]["matched_tokens"]:
        raise ValueError("companion token budget mismatch")
    sources = {str(companion): sha(companion)}
    def bind(path, expected=None):
        path = Path(path).resolve()
        h = sha(path)
        if expected is not None and h != expected:
            raise ValueError("pinned resource changed: " + str(path))
        sources[str(path)] = h
    data, evaluation = copy.deepcopy(literal["data"]), copy.deepcopy(literal["evaluation"])
    for info in (data, literal["student_start"], evaluation["theta"], evaluation["drift"]):
        bind(info["path"], info["sha256"])
    for p in pilots:
        bind(p["path"], p["sha256"])
    for rel in ("src/pccap/distill/recipe.py", "src/pccap/distill/data.py", "src/pccap/distill/train.py",
                "src/pccap/data/decode.py", "src/pccap/harness/runs.py", "scripts/r1_24_runtime.py",
                "scripts/r1_24_lm_recipe.py", "manifests/reference.json", "manifests/dev/lm_sets.json",
                "manifests/dev/zsre_dev.json", "manifests/dev/counterfact_dev.json", "manifests/dev/s0_sample.json"):
        bind(ROOT / rel)
    bind(evaluation["calibration"])
    recipe = copy.deepcopy(literal["recipe"])
    recipe.pop("temperature", None)
    recipe.update(estimator="exact_bp_next_token_base_continuation",
                  objective="mean next-token cross-entropy over valid consecutive positions",
                  teacher_forward_required=False, targets="OpenWebText tokens[s+1:s+n+1] for inputs tokens[s:s+n]",
                  loss_mask="all n valid logits including last; padded bucket rows excluded",
                  reset_context="causal context resets at each 128-token chunk; no gap in scored target indices",
                  reuse="distill.recipe Adam constants, distill.data.load_shard, distill.train.batched_logits; new execution adapter required",
                  difference_from_REG="ordinary BP language-model continuation, seq128/batch1, no teacher or PC relaxation, exact tail length")
    m = {"schema_version": 1, "task": "R1-24b", "name": "r1_24_control_lm", "status": "dry_recipe_pending_lead_decision_and_runtime",
         "companion": {"path": str(companion), "sha256": sources[str(companion)]},
         "student_start": copy.deepcopy(literal["student_start"]), "recipe": recipe, "data": data,
         "budget": {"pilots": pilots, "reported_learning_tokens": reported, "matched_tokens": reported,
                    "arithmetic": lm_budget(reported, recipe["seq_len"], data["train_end_exclusive"]),
                    "matching_basis": "same selected pilot learning forward-input-token ledger as literal control; NOT exact compute matching",
                    "exact_training_passes_verified": False, "query_phase_excluded": True,
                    "limitations": copy.deepcopy(literal["budget"]["limitations"]),
                    "literal_companion_arithmetic": copy.deepcopy(literal["budget"]["arithmetic"]),
                    "comparison": "LM uses one forward and one reverse per source position; KD uses teacher+student forwards and a student reverse. Equal forward-token counts do not match reverse work, source exposure or accelerator seconds.",
                    "source_exposure_matched_alternative": {"status": "not_selected", "lm_input_tokens": literal["budget"]["arithmetic"]["source_tokens"],
                        "note": "would halve the present LM forward budget; needs a joint revised decision/recipe, not a silent switch"}},
         "evaluation": evaluation, "evaluation_sha256": hashlib.sha256(json.dumps(evaluation, sort_keys=True).encode()).hexdigest(),
         "evaluation_policy": "byte-for-byte JSON-value equivalent to the literal companion; same theta, streams, original-base locality reference and development fidelity probes",
         "stopping": copy.deepcopy(literal["stopping"]),
         "launch_allowed": False, "training_executed": False, "gpu_seconds": 0,
         "required_before_execution": ["lead chooses informative LM control", "new runtime implements hard-target CE; existing KD runner must refuse this task id",
             "refresh both recipes against the exact execution source version and select common evaluation theta if policy changes",
             "reconcile pilot pass tokens and profile forward/reverse cost for any matched-compute claim", "lease and owner GPU scheduling"],
         "legacy_source_binding_caveat": "companion's old broad source registry may be stale after repairs; copied evaluation/resource values are verified here, old implementation hashes are not silently adopted",
         "sources_sha256": sources}
    for p,h in sources.items():
        if sha(p) != h:
            raise RuntimeError("source changed during recipe preparation: " + p)
    return validate(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--companion", type=Path, default=ROOT / "manifests/revision_v1/r1_24_control_v2.json")
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository manifest required")
    m = prepare(a.companion)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x") as f:
        json.dump(m, f, indent=2, sort_keys=True, allow_nan=False)
        f.write("\n")
    print(json.dumps({"output": str(a.output), "budget": m["budget"]["arithmetic"], "launch_allowed": False}, indent=2))


if __name__ == "__main__":
    main()
