"""AW-B4 read-only reconstruction; final report refuses unfinished evaluation."""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import json
import math
from pathlib import Path

import numpy as np

from aw import aw_b_calibrate as driver
from aw.pc_complete_report import read
from aw.pc_historical import ROOT, Sources, sha
from aw.pc_v0_report import table
from aw.pc_v1_run import metrics

CALIBRATION = ROOT / "results/additional_work/AW-B/calibration-20260929"
EVALUATION = ROOT / "results/additional_work/AW-B/evaluation-20260929"
OUTPUT = ROOT / "logs/additional_work/AW-B/report-20260929"
DOCUMENT = ROOT / "docs/additional_work/AW-B_report.md"
METRICS = ("ES", "RET-ES", "RET-GS", "LS", "near_miss", "revision")


def ready(folder):
    folder = Path(folder)
    if not (folder / "report.json").exists() or not (folder / "cost.json").exists():
        return False
    report = json.loads((folder / "report.json").read_bytes())
    cost = json.loads((folder / "cost.json").read_bytes())
    return report.get("status") == "complete" and cost.get("status") == "complete"


def bound(config):
    kind, value = config
    return (
        2 * value
        if kind == "clip"
        else -math.log(value)
        if kind == "mixture"
        else 0
        if kind == "capoff"
        else None
    )


def validate(folder, expected_command, evidence):
    folder = Path(folder)
    if not ready(folder):
        raise ValueError("completed " + expected_command + " report and cost receipt required")
    report = read(folder / "report.json", evidence)
    cost = read(folder / "cost.json", evidence)
    if report["command"] != expected_command:
        raise ValueError("wrong AW-B population mode")
    evidence.check(report["sources_sha256"])
    if cost["completed_memories"] != len(report["inputs"]) or set(report["cells"]) != set(
        report["inputs"]
    ):
        raise ValueError("incomplete memory inventory")
    expected = (
        driver.development_inputs()
        if expected_command == "calibrate"
        else driver.evaluation_inputs()
    )
    if report["inputs"] != expected:
        raise ValueError("AW-B memory/input identities differ")
    windows, selection = driver.selection("v5")
    if report["selection"] != selection or selection["positions"] != 245237:
        raise ValueError("full validation population differs")
    configs = [tuple(c) for c in report["configs"]]
    keys = {driver.scoring.config_key(c): c for c in configs}
    if len(keys) != len(configs) or any(c not in driver.CONFIGS for c in configs):
        raise ValueError("unregistered or duplicate settings")
    verified = []
    for name, spec in report["inputs"].items():
        for k in ("recipe", "payload", "checkpoint", "metadata", "snapshot"):
            evidence.resolve(spec[k]["path"], spec[k]["sha256"])
        payload = read(spec["payload"]["path"], evidence)
        ids = [it["item_id"] for it in payload["items"][:300]]
        endpoints = {k: payload["endpoints"][k] for k in ("locality", "near_miss", "revision")}
        row = report["cells"][name]
        saved = read(folder / name / "report.json", evidence)
        if (
            row != saved
            or row["memory_sha256"] != spec["state_sha256"]
            or row["base_sha256"] != spec["base_sha256"]
            or row["reader_sha256"] != spec["reader_sha256"]
        ):
            raise ValueError("per-memory report/immutable identities differ")
        if set(row["harm"]) != set(keys) or set(row["efficacy"]) != set(keys):
            raise ValueError("missing or extra setting")
        original_reference = None
        for key, config in keys.items():
            harm = row["harm"][key]
            evidence.resolve(harm["vectors"]["path"], harm["vectors"]["sha256"])
            with np.load(harm["vectors"]["path"], allow_pickle=False) as f:
                values = f["values"]
            if (
                values.shape != (1931, 127, 5)
                or not np.isfinite(values).all()
                or driver.summarize(values) != harm["summary"]
            ):
                raise ValueError("harm vectors/statistics do not reproduce")
            if (
                harm["selection"] != selection
                or harm["telemetry"]["logical_positions"] != selection["positions"]
            ):
                raise ValueError("position or gate telemetry coverage differs")
            if (
                harm["telemetry"]["hard_null"] + harm["telemetry"]["selected"]
                != selection["positions"]
            ):
                raise ValueError("gate telemetry does not partition positions")
            if harm["changed_fraction"] != float((values[:, :, 3] > 1e-9).mean()):
                raise ValueError("changed-distribution fraction does not reproduce")
            if original_reference is None:
                original_reference = values[:, :, 1:3].copy()
            if not np.array_equal(values[:, :, 1:3], original_reference):
                raise ValueError("wrapper settings do not share base reference")
            ceiling = bound(config)
            if (
                ceiling is not None
                and float(np.max(values[:, :, 0] - values[:, :, 1])) > ceiling + 1e-10
            ):
                raise ValueError("fixed-prefix loss ceiling violated")
            cp = read(folder / name / "efficacy" / (key.replace(":", "-") + ".json"), evidence)
            if (
                metrics(cp, ids, endpoints) != cp["metrics"]
                or cp["metrics"] != row["efficacy"][key]["metrics"]
                or cp.get("memory_unchanged") is not True
            ):
                raise ValueError("efficacy does not reproduce from installed scoring")
            verified.append(
                dict(
                    memory=name,
                    config=key,
                    positions=selection["positions"],
                    loss_bound=ceiling,
                    maximum=harm["summary"]["original"]["loss"]["maximum_signed"],
                )
            )
    return report, cost, verified


def selection(calibration, evidence):
    selected = read(CALIBRATION / "selection.json", evidence)
    evidence.resolve(
        selected["calibration_report"]["path"], selected["calibration_report"]["sha256"]
    )
    if selected["calibration_report"]["sha256"] != sha(CALIBRATION / "report.json"):
        raise ValueError("selection refers to different calibration")
    reproduced = driver.select(calibration["cells"], "minimum")
    if any(selected[k] != v for k, v in reproduced.items()):
        raise ValueError("mechanical selection does not reproduce")
    return selected


def calibration_text(cal, chosen, cost):
    text = "## Calibration: all sixteen settings\n\nExposed development memories, 300 edits per dataset. Selection precedes evaluation. All means and tails below use the full 245,237-position fixed-prefix inventory. ES is a saved-memory re-query, equal to RET-ES, not immediate acquisition. RET-GS is the installed item-level paraphrase score and can include fractional item credit.\n\n"
    rows = []
    eligible = {r["key"]: r["eligible"] for r in chosen["candidates"]}
    for ds, row in cal["cells"].items():
        for kind, parameter in cal["configs"]:
            key = driver.scoring.config_key((kind, parameter))
            h = row["harm"][key]["summary"]["original"]
            m = row["efficacy"][key]["metrics"]
            rows.append(
                [
                    ds,
                    key,
                    *[m[k]["value"] for k in METRICS],
                    h["kl"]["mean_signed"],
                    h["loss"]["mean_signed"],
                    h["loss"]["es99_positive"],
                    h["loss"]["maximum_signed"],
                    eligible.get(key, "reference"),
                ]
            )
    text += table(
        [
            "Dataset",
            "Setting",
            *METRICS,
            "Mean KL",
            "Mean ΔNLL",
            "ES99+",
            "Max ΔNLL",
            "Eligible on both datasets",
        ],
        rows,
    )
    text += "\n\nEligibility requires RET-ES and RET-GS within ±0.02 of v5 on **both** datasets, without decreasing LS or near-miss preservation. Rank eligible arms by the **smaller** dataset reduction in maximum harm, then the **smaller** ES99 reduction; complete ties retain the declared setting order. At most one bound and one shrink/gate comparator may advance.\n\n"
    text += table(
        [
            "Setting",
            "Category",
            "Eligible",
            "Worst-dataset max reduction",
            "Worst-dataset ES99 reduction",
            "zsRE efficacy changes",
            "CounterFact efficacy changes",
        ],
        [
            [
                r["key"],
                r["category"],
                r["eligible"],
                r["rank_maximum"],
                r["rank_es99"],
                r["efficacy_changes"]["zsre"],
                r["efficacy_changes"]["counterfact"],
            ]
            for r in chosen["candidates"]
        ],
    )
    text += "\n\nThe selected bound is **mixture ρ = exp(−1)**, with 1−ρ ≈ 0.6321 multiplying the cap distribution. No shrink/gate comparator is eligible, so evaluation contains three arms rather than filling the missing slot with an ineligible comparator.\n\n"
    text += "Every clip setting fails retention eligibility. Its symmetric log-ratio restriction limits increases as well as decreases relative to the base; after normalization, no token can gain more than 2b nats relative to that base. This is consistent with suppressing strong edited-answer corrections, although aggregate scores alone do not isolate every decoding cause. Mixture instead preserves a base-probability floor while permitting large increases for tokens the base considers unlikely. It does **not** generally guarantee unchanged greedy answers: the measured CounterFact RET-GS falls from 0.753333 to 0.745000 (−0.8333 percentage points), inside the registered tolerance. zsRE scores are unchanged.\n\n"
    text += "The calibration mixture brings zsRE mean KL below 0.001, but CounterFact remains above that line. No κ or coupled-free-energy objective is used here. Without an eligible shrink/gate comparator, this experiment cannot establish superiority to an efficacy-matched weakening control.\n\n"
    text += f"Calibration cost: {cost['elapsed_process_seconds']:.3f} process seconds ({cost['elapsed_process_seconds'] / 3600:.3f} h), including construction, wrapper scoring, efficacy and temporary endpoint teaching. Thirteen numerical settings share one pass; the three gates use separate passes. No repeated per-setting pass times are summed as extra work.\n\n"
    return text


def evaluation_text(evaluation, cost):
    text = "## Exposed sealed-stream evaluation\n\nRealization 0, five paired orders, two datasets, restored original 300-edit memories. These are already-exposed populations. No result here enters parameter selection. All per-order values and differences remain visible; positions and orders are not independent realizations.\n\n"
    rows = []
    differences = []
    for name, row in evaluation["cells"].items():
        baseline = row["harm"]["v5"]["summary"]["original"]
        bm = row["efficacy"]["v5"]["metrics"]
        for key, h in row["harm"].items():
            s = h["summary"]["original"]
            m = row["efficacy"][key]["metrics"]
            rows.append(
                [
                    name,
                    key,
                    *[m[k]["value"] for k in METRICS],
                    s["kl"]["mean_signed"],
                    s["loss"]["mean_signed"],
                    s["loss"]["es99_positive"],
                    s["loss"]["maximum_signed"],
                ]
            )
            differences.append(
                [
                    name,
                    key,
                    *[
                        None
                        if m[k]["value"] is None or bm[k]["value"] is None
                        else m[k]["value"] - bm[k]["value"]
                        for k in METRICS
                    ],
                    s["kl"]["mean_signed"] - baseline["kl"]["mean_signed"],
                    *[
                        s["loss"][k] - baseline["loss"][k]
                        for k in ("mean_signed", "es99_positive", "maximum_signed")
                    ],
                ]
            )
    text += table(
        ["Memory", "Setting", *METRICS, "Mean KL", "Mean ΔNLL", "ES99+", "Max ΔNLL"], rows
    )
    text += "\n\nPaired differences, setting minus v5 (loss lower is better):\n\n" + table(
        [
            "Memory",
            "Setting",
            *["Δ" + k for k in METRICS],
            "Δmean KL",
            "Δmean NLL",
            "ΔES99+",
            "Δmaximum",
        ],
        differences,
    )
    success = driver.evaluation_success(evaluation["cells"])
    text += "\n\nPredeclared usefulness requires smaller maximum and ES99+, with both retention scores within ±0.02, in every dataset/order. This is a conjunction across the declared cells, not an aggregate-average claim.\n\n"
    text += table(
        ["Setting", "Every coordinate passes"], list(success["all_coordinates_by_config"].items())
    )
    text += f"\n\nEvaluation process time: {cost['elapsed_process_seconds']:.3f} seconds ({cost['elapsed_process_seconds'] / 3600:.3f} h), separate from calibration.\n\n"
    return text


def guarantee_text():
    return """## What the one-nat guarantee says

For the same fixed prefix h and target token y, let p₀ be the unchanged base distribution and p₁ the cap distribution. The selected mixture is q = ρp₀ + (1−ρ)p₁ with ρ = exp(−1). Since q(y|h) ≥ ρp₀(y|h),

    ΔNLL(y|h) = log[p₀(y|h) / q(y|h)] ≤ −log ρ = 1 nat.

This is a per-token likelihood-ratio bound relative to the specified base, at the same prefix. It is **not** a one-nat bound on total sequence loss, generated-text loss on different prefixes, semantic harm, or greedy-answer preservation. Along a shared teacher-forced sequence of N prefixes, the bounds sum to at most N nats, not one. The mixture also implies KL(p₀ || q) ≤ 1 nat, which is much weaker than the unchanged 0.001 mean-KL benchmark. No bound is asserted relative to another independently trained base.

Survival curves use P(ΔNLL > x), including zero and beneficial positions in the denominator. The one-nat ceiling is shown explicitly. Apparent concentration or a truncated observed tail does not prove a heavy-tail family. This query-time intervention tests a way of limiting extreme prediction loss in the active-inference testbed; it introduces neither PC acquisition nor autonomous policy inference.

"""


def build(*, final=False, output=OUTPUT, document=DOCUMENT):
    if final and not ready(EVALUATION):
        raise ValueError("evaluation still running; final AW-B report must wait")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    evidence = Sources()
    cal, cc, checks = validate(CALIBRATION, "calibrate", evidence)
    chosen = selection(cal, evidence)
    if cal["configs"] != [list(c) for c in driver.CONFIGS]:
        raise ValueError("all sixteen calibration settings required")
    if chosen["final_configs"] != [["v5", None], ["capoff", None], ["mixture", math.exp(-1)]]:
        raise ValueError(
            "selected setting differs; update explanatory narrative before publication"
        )
    result = dict(
        schema="aw-b-report-v1",
        status="complete" if final else "calibration_verified_evaluation_pending",
        calibration=cal,
        selection=chosen,
        calibration_cost=cc,
        verified_settings=checks,
    )
    text = (
        "# Bounded correction: calibration and exposed-stream evaluation\n\n"
        if final
        else "# AW-B calibration review — evaluation pending\n\nThis is development evidence only. The running evaluation has not been analyzed or used for selection.\n\n"
    )
    text += calibration_text(cal, chosen, cc)
    if final:
        ev, ec, more = validate(EVALUATION, "evaluate", evidence)
        if ev["configs"] != chosen["final_configs"]:
            raise ValueError("evaluation arms differ from selected arms")
        success = driver.evaluation_success(ev["cells"])
        if ev.get("success") != success:
            raise ValueError("evaluation success does not reproduce")
        result.update(
            evaluation=ev, evaluation_cost=ec, success=success, verified_settings=checks + more
        )
        text += evaluation_text(ev, ec)
    text += guarantee_text()
    evidence.bindings[str(Path(__file__).resolve())] = sha(__file__)
    result["sources_sha256"] = evidence.bindings
    evidence.verify_unchanged()
    name = "report" if final else "calibration-review"
    (output / (name + ".json")).write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    target = Path(document) if final else output / "calibration-review.md"
    target.write_text(text)
    (output / (name + "-publication.json")).write_text(
        json.dumps(dict(path=str(target), sha256=sha(target)), indent=2) + "\n"
    )
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--final", action="store_true")
    p.add_argument("--output", default=str(OUTPUT))
    p.add_argument("--document", default=str(DOCUMENT))
    a = p.parse_args()
    r = build(final=a.final, output=a.output, document=a.document)
    print(json.dumps(dict(status=r["status"], settings_verified=len(r["verified_settings"]))))
