"""Reproduce the four saved concurrency/solo attempt ratios and final states."""

import json

from scripts.r1_d9_receipts import ref
from scripts.r1_d10a_review import ROOT, write_new


def completed(recipe_path):
    recipe = ref(ROOT / recipe_path)
    matches = []
    for path in sorted((ROOT / "results/R1/stage4_dev_cells").glob("*/attempt-*/result.json")):
        value = json.loads(path.read_text())
        if value.get("manifest_sha256") == recipe["sha256"] and value.get("status") == "complete":
            if value.get("completed_checkpoint") != 300:
                raise ValueError("unexpected completed cadence")
            receipt_path = path.parent / "checkpoint-300.receipt.json"
            receipt = json.loads(receipt_path.read_text())
            if receipt["receipt_sha256"] != value["last_receipt_sha256"] or receipt["manifest_sha256"] != recipe["sha256"]:
                raise ValueError("last receipt identity mismatch")
            if ref(receipt["report"]["path"]) != receipt["report"]:
                raise ValueError("checkpoint report changed")
            matches.append(dict(recipe=recipe, result=ref(path), receipt=ref(receipt_path),
                                checkpoint=receipt["report"], seconds=value["attempt_wall_seconds"],
                                state_sha256=receipt["state_sha256"]))
    if len(matches) != 1:
        raise ValueError("exactly one completed measurement required")
    return matches[0]


def main():
    rows = []
    for condition in ("R1_nonlearned", "R1_learned_ff_v2", "v0_stable", "matched_update"):
        learned = condition.startswith("R1_")
        solo = f"docs/tasks/R1-64c-zsre-{condition}.recipe.json" if learned else f"docs/tasks/R1-64d/R1-64d-zsre-{condition}.recipe.json"
        concurrent = f"docs/tasks/R1-64d/R1-64d-zsre-{condition}.recipe.json" if learned else f"docs/tasks/R1-64d-probe2/R1-64d-probe2-zsre-{condition}.recipe.json"
        a, b = completed(solo), completed(concurrent)
        ratio = b["seconds"] / a["seconds"]
        rows.append(dict(condition=condition, solo=a, concurrent=b,
                         attempt_slowdown=ratio, within_1_10=ratio <= 1.10,
                         identical_final_state=a["state_sha256"] == b["state_sha256"]))
    write_new(ROOT / "logs/r1_round25/r1-x15-concurrency.json", dict(
        task="R1-X15", rows=rows, producer=ref(__file__),
        notes=ref(ROOT / "docs/R1_stage2_notes.md"),
        scope="300-attempt development cells; excludes initialization and process envelope; no GPU rerun",
        limitation="Historical learned pair spans driver versions; four saved ratios do not prove a universal slowdown bound or elapsed pair speedup."))
    print(json.dumps([{k: r[k] for k in ("condition", "attempt_slowdown", "within_1_10", "identical_final_state")} for r in rows], indent=2))


if __name__ == "__main__":
    main()
