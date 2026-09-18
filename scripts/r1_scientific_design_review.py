"""CPU review of the current experiment, using saved results and synthetic inference probes.

No model execution, new scientific outcomes, policy edits or signing operations.
The coverage example is a mathematical counterexample under a stated symmetric
sampling model, not an estimate of this project's actual sampling distribution.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scripts import r1_49g_inference as inference

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def inference_probe():
    indices = np.random.default_rng(0).integers(0, 3, size=(10000, 3))
    extreme_counts = [int(np.all(indices == i, axis=1).sum()) for i in range(3)]
    examples = []
    for means in ((-.02, .03, .12), (.01, .06, .11), (-.15, -.07, -.01), (0., 0., 0.)):
        result = inference.cluster_intervals([[v] * 5 for v in means])
        expected = [min(result["realization_estimates"]), max(result["realization_estimates"])]
        for field in ("unadjusted_interval", "adjusted_interval"):
            np.testing.assert_allclose(
                [result[field]["lower"], result[field]["upper"]], expected, rtol=0, atol=1e-15
            )
        examples.append(dict(realization_means=means, result=result))
    exact_indices = np.asarray(list(itertools.product(range(3), repeat=3)))
    values = np.asarray([0., 1., 3.])
    exact_means = values[exact_indices].mean(axis=1)
    # This is the exact sampling probability under independent continuous,
    # symmetric cluster estimates centered on zero: all positive or all negative.
    exact_coverage = 1 - 2 * .5 ** 3
    null = np.random.default_rng(20260918).normal(0., .10, size=(200000, 3))
    contains_zero = (null.min(axis=1) <= 0) & (null.max(axis=1) >= 0)
    # ES/LS differences set to zero: both preservation inequalities pass. The
    # remaining DEC-058 positive rule is min(G)>0 and mean(G)>=.05.
    positive = (null.min(axis=1) > 0) & (null.mean(axis=1) >= .05)
    return dict(
        method=inference.FAMILY,
        bootstrap_ordered_index_sequences=27,
        bootstrap_count_vectors=10,
        exact_distinct_means_in_example=len(np.unique(exact_means)),
        probability_at_each_unique_extreme=1 / 27,
        installed_seed0_extreme_counts=extreme_counts,
        installed_draw_count=len(indices),
        adjusted_lower_tail_probability=(1 - inference.ADJUSTED_CONFIDENCE) / 2,
        pointwise_lower_tail_probability=(1 - .975) / 2,
        examples=examples,
        symmetric_independent_three_cluster_model=dict(
            true_effect=0,
            analytic_interval_coverage=exact_coverage,
            one_sided_exclusion_probability=.5 ** 3,
            minimum_standard_two_sided_exact_signflip_p=2 / 8,
            signflip_qualification="Only under exchangeable paired signs; no test substituted for DEC-057.",
        ),
        synthetic_monte_carlo=dict(
            purpose="Illustrate failure of nominal coverage, not predict actual experiment error rates.",
            seed=20260918, trials=len(null), cluster_standard_deviation=.10,
            interval_coverage=float(contains_zero.mean()),
            dec058_positive_fraction_when_ES_LS_zero=float(positive.mean()),
        ),
        interpretation="For the installed seed/draws, both displayed intervals are the observed realization range. Increasing draws does not repair three-cluster support.",
    )


def build():
    sources = {}

    def read(relative):
        path = (ROOT / relative).resolve()
        raw = path.read_bytes()
        sources[str(path)] = hashlib.sha256(raw).hexdigest()
        return json.loads(raw)

    inventory = read("logs/r1_round35/chain-s-inventory.json")
    measurements = []
    for name, cell in inventory["cells"].items():
        summary = cell["full_sample_results"]
        binding = summary["vectors"]
        path = Path(binding["path"])
        if sha(path) != binding["sha256"]:
            raise ValueError("saved development vector changed")
        sources[str(path)] = binding["sha256"]
        with np.load(path, allow_pickle=False) as archive:
            values = archive["values"].reshape(-1, 5)
        if len(values) != 245237 or not np.isfinite(values).all():
            raise ValueError("incomplete or nonfinite full-validation data")
        loss = values[:, 0] - values[:, 2]
        kl = values[:, 4]
        positive = np.maximum(loss, 0)
        q = .01 * len(values)
        ordered = np.sort(positive)[::-1]
        tail = float((ordered[:int(q)].sum() + (q - int(q)) * ordered[int(q)]) / q)
        observed = dict(
            mean_KL=float(kl.mean()), mean_signed_NLL=float(loss.mean()),
            ES99_positive_NLL=tail, max_positive_NLL=float(positive.max()),
            positive_NLL_positions=int((loss > 0).sum()), NLL_above_1=int((loss > 1).sum()),
            positions=len(values), KL_pass=bool(kl.mean() <= .001), NLL_pass=bool(loss.mean() <= .01),
        )
        saved = summary["references"]["original"]
        np.testing.assert_allclose(
            [observed["mean_KL"], observed["mean_signed_NLL"], tail, observed["max_positive_NLL"]],
            [saved["kl"]["mean_signed"], saved["loss"]["mean_signed"], saved["loss"]["ES99_positive"], saved["loss"]["maximum_positive"]],
            rtol=0, atol=1e-12,
        )
        if observed["NLL_above_1"] != saved["loss"]["exceedances_nats"]["1.0"]["count"]:
            raise ValueError("independent exceedance recount differs")
        measurements.append(dict(cell=name, reference="original", **observed))

    cost = read("docs/tasks/R1-cost-admission-receipt-v4.json")
    pilot = read("logs/r1_round22/ht3e-independent-review-v2.json")
    teacher = read("logs/r1_round25/r1-x15-independent.json")
    matrix = read("manifests/revision_v1/run_matrix_v5_2_D_4.json")
    roles = dict(core=len(matrix["cells"]), extension=len(matrix["extension"]["cells"]),
                 omitted=len(matrix["prospectively_omitted_cells"]), nominal_primary_intervals=63,
                 unavailable_MQuAKE_primary_intervals=21)
    arm_means = {}
    for arm in ("ordinary", "kappa02", "kappa05", "clip2"):
        rows = [r for r in pilot["pilot"]["rows"] if r["arm"] == arm]
        if len(rows) != 9:
            raise ValueError("nine dataset/seed rows required per arm")
        arm_means[arm] = dict(RET_GS=float(np.mean([r["ret_gs"] for r in rows])),
                              ES95=float(np.mean([r["es95"] for r in rows])))
    for name in (
        "docs/updated_plan9.md", "docs/decisions.md", "docs/R1_stage4_protocol_draft_v5_1.md",
        "docs/R1_stage4_protocol_v5_2_D_3.md", "docs/R1_stage4_protocol_v5_2_D_4.md",
        "docs/R1_U03_interpretation_memo.md", "docs/R1_execution_plan_v3.md",
        "docs/R1_stage2_report.md", "docs/R1_stage2_notes.md", "docs/R1_diagnosis.md",
        "docs/report.md", "docs/heavy_tail_counter_review.md", "docs/tasks/R1-X21-edit-requests.md",
        "docs/R1_stage4_U08_mquake_calibration_v3.md", "docs/tasks/R1-73b.md",
        "src/pccap/revision_v1/stage4_adapters.py", "scripts/r1_49g_inference.py",
        "docs/talk_claim_ledger_v6.md", "docs/presentation/talk_outline_v1.md",
        "docs/pc_cap_month_plan_readable.pdf", "docs/more_input/pc_cap_coding_agent_guide (1).pdf",
        "scripts/r1_scientific_design_review.py",
    ):
        sources[str(ROOT / name)] = sha(ROOT / name)
    for path, expected in sources.items():
        if sha(path) != expected:
            raise ValueError("review source changed during read: " + path)
    return dict(
        scope="scientific design review; saved development data plus labelled synthetic mathematical probes",
        no_new_experiments=True, GPU_seconds=0, signing_operations=0,
        inference=inference_probe(), full_validation_recount=measurements,
        pilot_arm_means=arm_means, pilot_comparisons=pilot["pilot"]["comparisons"],
        teacher_baseline=teacher["teacher_baseline"], scope_counts=roles,
        cost_projection=cost["projection"], source_bindings_sha256=sources,
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    path = args.output.resolve()
    if not path.is_relative_to(ROOT / "logs"):
        raise ValueError("review outputs belong in repository logs")
    value = build()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(output=str(path), sources=len(value["source_bindings_sha256"]),
                          mathematical_coverage=value["inference"]["symmetric_independent_three_cluster_model"]["analytic_interval_coverage"])))


if __name__ == "__main__":
    main()
