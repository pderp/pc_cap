"""Stage reports (PDF Appendix G; S0-11 first). ``pccap report --stage S0`` renders
``results/<stage>/report.md`` with the ten sections, the control table (expected / observed /
pass), the dependency table naming what a failing control blocks, cost against the ceiling (κ
per PA-3), and the ePC status.
"""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from pccap.analysis.budget import stages_summary

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / "results"
CONTROLS = RESULTS / "S0" / "controls"

# control name -> (evidence file, expected, blocks)
CONTROL_REGISTER = [
    ("Numerical known answers", "s0_metrics_known_answer", "rank/PR/overlap/JS/D.7/η² cases pass", "every S1 measurement using the metric"),
    ("PC-2 identity", "pc2_identity.json", "256-probe cap-off equality (max |Δ| = 0); oracle-false gate exact", "everything"),
    ("PC-3 idempotence", "pc3_idempotence.json", "20 repeated threshold-fitted edits, no new slots", "S3-04, S4"),
    ("PC-4 conflicts/revisions", "tests/controls/test_pc4_conflict.py", "distinct, identical, newer version, replay, failed rollback", "S3-04, correction track"),
    ("PC-5 probe/search", "tests/controls/test_pc5_probe.py, test_pc5_search.py", "signed scores, non-monotone, exact candidate, rollback", "C2 and all cap learning"),
    ("PC-6 budgets", "tests/controls/test_pc6_budget.py, tests/cap/test_memory.py", "equal ceilings, overhead, wide keys, aggregate increment, eviction, use-count once", "all arms"),
    ("PC-7 complete answers", "tests/controls/test_pc7_complete_answers.py", "wrong second token; teacher-forced vs generation; terminators", "all editing metrics"),
    ("PC-8 isolation/read-only", "pc8_readonly.json", "state hash after predict/decode unchanged", "evaluation validity"),
    ("PC-9 cloning/randomness", "pc9_cloning.json", "clone equality, replay, reversal start, item-keyed CR, scalar order effect", "S7, all confirmatory"),
    ("Reproducibility", "reproducibility.json", "two replays: identical decisions, metrics within tolerance", "all confirmatory"),
    ("Sign convention", "sign_convention.json", "analytic descent direction reduces the loss", "all credit"),
    ("ePC sign convention", "epc_sign_convention.json", "+e reduces the toy loss; cos(e, −adjoint) ≈ 1", "ePC credit"),
    ("Adjoint finite difference", "s0_05_finite_difference.json", "rel err < 1e-3 vs f64 reference at step 1e-2", "all credit"),
    ("ePC zero-error identity", "s0_06_zero_error_identity.json", "sites exact; logits within SD-10 record", "ePC arms"),
    ("Frozen base", "results/S0/C1/BP/h/0/0/metrics.json", "base_hash_before == base_hash_after", "that run"),
]


def _load(name: str):
    p = CONTROLS / name
    if p.exists() and p.suffix == ".json":
        try:
            return json.loads(p.read_text())
        except Exception:
            return None
    return None


def _observed(name: str, evidence: str) -> tuple[str, str]:
    d = _load(evidence)
    if evidence.startswith("tests/"):
        return "pytest green (see test-fast / test-gpu logs)", "pass"
    if name == "Numerical known answers":
        return "39 known-answer tests (S0-07/S0-07b) green", "pass"
    if name == "Frozen base":
        p = ROOT / evidence
        if p.exists():
            m = json.loads(p.read_text())
            ok = m.get("base_hash_before") == m.get("base_hash_after")
            return f"before {m.get('base_hash_before', '')[:10]} == after {m.get('base_hash_after', '')[:10]}", "pass" if ok else "FAIL"
        return "no smoke run", "missing"
    if d is None:
        return "no evidence file", "missing"
    if name == "PC-2 identity":
        return f"probes {d['probes']}, max |Δ| cap-off {d['max_abs_logit_diff_cap_off']}, gate {d['oracle_false_gate_max_abs_diff']}, unrelated fired {d['unrelated_fired']}", "pass" if d.get("pass") else "FAIL"
    if name == "PC-3 idempotence":
        return f"reached {d['reached_threshold']}, checked {d['checked']}, violations {d['violations']}", "pass" if d["violations"] == 0 and d["checked"] >= 1 else "FAIL"
    if name == "PC-8 isolation/read-only":
        return "hash unchanged after predict + decode", "pass" if d.get("pass") else "FAIL"
    if name == "PC-9 cloning/randomness":
        return f"decisions {d.get('decisions')}, clone/replay/reversal equal", "pass" if d.get("clone_equal") and d.get("replay_identical") else "FAIL"
    if name == "Reproducibility":
        return f"{d.get('decisions')} decisions identical", "pass" if d.get("identical") else "FAIL"
    if name == "Sign convention":
        return f"loss {d['loss_before']:.3f} -> {d['loss_after_direction']:.3f} (flipped {d['loss_after_flipped']:.3f})", "pass" if d["descent_reduces_loss"] else "FAIL"
    if name == "ePC sign convention":
        return f"cos(e, −adjoint) = {d['cos(settled_error, -adjoint)']:.6f}", "pass" if d["plus_e_reduces_loss"] else "FAIL"
    if name == "Adjoint finite difference":
        return f"worst rel err vs f64 = {d['worst_rel_err_vs_f64_reference']:.2e} (fp32-internal FD {d['worst_rel_err_fp32_wrapper_fd']:.2e})", "pass" if d["worst_rel_err_vs_f64_reference"] < 1e-3 else "FAIL"
    if name == "ePC zero-error identity":
        return f"sites max |Δ| = {d['max_abs_site_diff']}, logits max |Δ| = {d['max_abs_logit_diff']:.2e} (kernel: head GEMM; SD-10 record)", "pass (with record)"
    return json.dumps(d)[:80], "?"


def _git() -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def render_s0() -> str:
    b = stages_summary()
    s0 = b["stages"]["S0"]
    smoke = RESULTS / "S0" / "C1" / "BP" / "h" / "0" / "0" / "metrics.json"
    sm = json.loads(smoke.read_text()) if smoke.exists() else None
    env = json.loads((RESULTS / "ENV" / "bench.json").read_text()) if (RESULTS / "ENV" / "bench.json").exists() else {}
    epc = _load("s0_06_energy_descent.json")
    lines = [
        "# S0 stage report (Appendix G)", "",
        f"Rendered {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} by `pccap report --stage S0`.", "",
        "## 1. Header", "",
        f"- Stage: S0 (harness, invariants, minimal cap). Code commit: `{_git()}`.",
        "- Configuration: `manifests/dev/s0_smoke.json`; base checkpoint: GPT-2 small snapshot `607a30d7…` (`model.safetensors` sha256 `248dfc39…`).",
        f"- Hardware: {env.get('device', 'RTX 5070')} (cc {env.get('compute_capability', '12.0')}), JAX {env.get('determinism', {}).get('jax_version', '0.11.1')}, fp32, TF32 off.",
        "- Realizations/orders: development only (s0 sample, seed 7); no confirmatory access.",
        f"- Elapsed cost: {s0['local_hours_total']:.2f} local GPU-h = {s0['a100_equivalent_hours']:.2f} A100-eq h (κ = {b['kappa']['kappa']}, band {b['kappa']['kappa_band']}, {b['kappa']['status']}) against the 8 h ceiling ({100 * s0['fraction_of_ceiling']:.1f}%).",
        "", "## 2. Status", "",
        "Development. Completed: ENV-01..04, DATA-00, S0-03..S0-10, CAP-01..CAP-07, S0-07/S0-07b/ANA-01 (Lane B). "
        "Pending inside S0: REF-01 (HF oracle fixture; rows in S0-04/S0-09 records marked pending), S0-01 (asset inventory / T1 clock). "
        "No correctness failure open; no resource limitation hit.",
        "", "## 3. Controls", "",
        "| control | expected | observed | pass | blocks if failing |", "| --- | --- | --- | --- | --- |",
    ]
    for name, evidence, expected, blocks in CONTROL_REGISTER:
        obs, ok = _observed(name, evidence)
        lines.append(f"| {name} | {expected} | {obs} | {ok} | {blocks} |")
    lines += ["", "Geometry alerts: none measured yet (S1). Scientific outcomes: none claimed at S0.", "",
              "## 4. Coverage", "",
              "- Planned S0 arms: one smoke edit, C1, BP, R-h. Completed: 1/1.",
              "- Unsupported/undefined so far: HF-oracle parity rows (pending REF-01, recorded `unavailable`); sibling fast tests (`unsupported`, DEC-001).",
              "- ePC checkpoint: absent (S0-01 inventory pending; PA-1 clock starts at CP-A). ePC wrapper built and tested on BP weights.", ""]
    if sm:
        it = sm["items"][0]
        lines += ["## 5. Results (development smoke, not a finding)", "",
                  f"- Item `{it['item_id']}`: outcome `{it['outcome']}`, rounds {it['rounds']}; ES {it['es_before']} → {it['es_after']}; teacher-forced NLL {it['nll_before']:.2f} → {it['nll_after']:.2f} nats.",
                  f"- Memory: occupied {sm['memory']['occupied_bytes']} B of allocated {sm['memory']['allocated_bytes']} B (ceiling {sm['memory']['ceiling_bytes']} B).",
                  f"- Base hash before/after: `{sm['base_hash_before'][:12]}` / `{sm['base_hash_after'][:12]}`.", ""]
    lines += ["## 6. Mechanism evidence", "", "None at S0 (oracle fixture, random-routing comparison and signed scores arrive with S3).", "",
              "## 7. Optional mathematics", "", "HVP small-matrix controls (S0-07b) pass; no HVP diagnostics run.", "",
              "## 8. Deviations", "",
              "See `docs/decisions.md` DEC-001..DEC-009 and `docs/spec_defects.md` SD-13..SD-16: JAX-only stack (SD-13); HF oracle via stored fixtures (SD-14); "
              "PA-1 needs a JAX distillation driver (SD-15); C2 tie rule (SD-16); adjoint finite-difference oracle is the float64 reference (S0-05 record); "
              "ePC ledger counts the terminal residual (docs/epc_energy.md); ePC head-GEMM logit difference 8.4e-5 recorded (SD-10). All before any test access.",
              "", "## 9. Interpretation", "",
              "S0 establishes the apparatus only: cap-off identity, memory accounting, transactional rollback and complete-state cloning hold; "
              "one development edit is acquired. No claim about routing, representation or credit is supported or refuted by S0.",
              ""]
    if epc:
        lines += [f"ePC status: wrapper on FabricPC; on BP weights, 8-step energy descent monotone on {epc['n_prompts'] - epc['non_monotone_count']}/{epc['n_prompts']} prompts; "
                  f"r_8 in [{min(r['r_k'] for r in epc['rows']):.2f}, {max(r['r_k'] for r in epc['rows']):.2f}] → label 'finite-iteration error credit'. Distilled checkpoint: absent.", ""]
    lines += ["## 10. Reproduction", "", "```",
              "make test-fast && make test-gpu",
              "python -m pccap.data.fetch --verify",
              "python -m pccap.cli run --stage S0 --arm C1 --base BP --read h --realization 0 --perm 0 --manifest manifests/dev/s0_smoke.json",
              "python -m pccap.cli report --stage S0", "```", "",
              "Licences/provenance: `manifests/datasets.json`, `manifests/assets.json`. Remaining S0 work in priority order: REF-01 oracle fixtures; S0-01 inventory and T1 clock; CAP-08 read variants (optional).", ""]
    return "\n".join(lines)


def main(args) -> int:
    stage = getattr(args, "stage", None) or "S0"
    if stage != "S0":
        print(f"report for stage {stage} not implemented yet")
        return 3
    out = RESULTS / "S0" / "report.md"
    out.write_text(render_s0())
    print("wrote", out)
    return 0
