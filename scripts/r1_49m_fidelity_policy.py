"""DEC-064 option 1: cap benchmarks do not veto primary comparisons.

An absent policy retains explicit historical D.2 replay behavior. A D.3 matrix
must bind this policy at root and in every cell; a partial binding is invalid.
"""

from __future__ import annotations

import math

from scripts import ht7_concentration as ht7

POLICY = {
    "version": 1,
    "decision": "DEC-064",
    "option": 1,
    "cap_role": "labelled_secondary_benchmark_without_admission_veto",
    "mean_kl_ceiling_nats": 0.001,
    "mean_signed_nll_increase_ceiling_nats": 0.01,
    "references": ["capoff", "original"],
    "equality_passes": True,
    "continued_base_gate": "DEC-047 unchanged; cap disabled",
    "incomplete_or_invalid_evidence": "unavailable; no fabricated pass",
    "concentration": ht7.CONTRACT,
}


def validate(policy):
    if policy != POLICY:
        raise ValueError("unrecognized or missing DEC-064 cap fidelity policy")
    return policy


def validate_matrix(matrix, cells):
    policy = matrix.get("cap_fidelity_policy")
    d3 = matrix.get("policy_revision") == "DEC064_D3"
    if policy is not None or d3 or any("cap_fidelity_policy" in c for c in cells):
        validate(policy)
        if matrix.get("full_validation") is None:
            raise ValueError("DEC-064 requires the full-validation measurement contract")
        for cell in cells:
            validate(cell.get("cap_fidelity_policy"))


def scientific_admission(cell, observed, scope):
    policy = cell.get("cap_fidelity_policy")
    if policy is not None:
        validate(policy)
    required = (cell.get("population") or {}).get("full_validation") is not None
    if policy is not None and not required:
        return False
    return bool(
        scope == "confirmatory"
        and cell.get("admitted") is True
        and observed["primary_metrics_complete"]
        and (
            not required
            or (
                observed["endpoint_complete"]
                and (policy is not None or observed["full_validation_fidelity_passes"])
            )
        )
    )


def benchmark(summary):
    if not summary.get("complete"):
        return dict(status="unavailable", passes=None, references={}, admission_veto=False)
    refs = {}
    for name in POLICY["references"]:
        ref = summary["references"][name]
        kl, loss = ref["kl"]["mean_signed"], ref["loss"]["mean_signed"]
        if not math.isfinite(kl) or not math.isfinite(loss) or kl < 0:
            raise ValueError("finite means and nonnegative KL required")
        refs[name] = dict(
            mean_kl_nats=kl,
            mean_signed_nll_increase_nats=loss,
            mean_kl_label="pass" if kl <= 0.001 else "fail",
            mean_nll_label="pass" if loss <= 0.01 else "fail",
        )
    return dict(
        status="complete",
        policy=POLICY,
        references=refs,
        passes=all(r["mean_kl_label"] == r["mean_nll_label"] == "pass" for r in refs.values()),
        admission_veto=False,
    )


def report_lines(cells):
    lines = [
        "",
        "DEC-064 cap fidelity: secondary benchmarks; failure does not veto primary comparisons.",
        "",
        "| Cell | Reference | Mean KL | KL ≤.001 | Mean signed NLL increase | NLL ≤.01 | Availability |",
        "|---|---|---:|---|---:|---|---|",
    ]
    for cell in cells:
        b = cell.get("cap_fidelity_benchmark", {})
        if not b.get("references"):
            lines.append(
                f"| {cell['cell_id']} | both | — | unavailable | — | unavailable | {b.get('status', cell['status'])} |"
            )
        for name, ref in b.get("references", {}).items():
            lines.append(
                f"| {cell['cell_id']} | {name} | {ref['mean_kl_nats']:.8g} | {ref['mean_kl_label']} | {ref['mean_signed_nll_increase_nats']:.8g} | {ref['mean_nll_label']} | {b['status']} |"
            )
    for cell in cells:
        for cp in cell.get("checkpoints", {}).values():
            concentration = cp.get("secondary", {}).get("full_validation", {}).get("concentration")
            if concentration:
                lines += ["", f"Cell {cell['cell_id']}", *ht7.report_lines(concentration)]
    return lines
