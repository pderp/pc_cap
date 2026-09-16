"""HT-3b independent CPU mathematical checks and exact pilot proposal. No training."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

# isort: off
import pccap  # noqa: F401 -- initialize determinism before JAX
import jax
import jax.numpy as jnp
import numpy as np
# isort: on

from pccap.revision_v1.train import LossConfig, coupled_divergence, coupled_surprisal

ROOT = Path(__file__).resolve().parents[1]


def checks():
    rng = np.random.default_rng(303)
    divergences, stationary = [], []
    for kappa in (0.2, 0.5):
        for _ in range(64):
            lp = jax.nn.log_softmax(jnp.asarray(rng.normal(0, 3, 64), jnp.float32))
            lq = jax.nn.log_softmax(jnp.asarray(rng.normal(0, 3, 64), jnp.float32))
            value = float(coupled_divergence(lp, lq, kappa))
            assert np.isfinite(value) and value >= -1e-6
            divergences.append(value)
            match, grad = jax.value_and_grad(
                lambda logits, lp=lp, kappa=kappa: coupled_divergence(
                    lp, jax.nn.log_softmax(logits), kappa
                )
            )(lp)
            assert abs(float(match)) < 1e-6
            norm = float(jnp.linalg.norm(grad))
            assert norm < 2e-6
            stationary.append(norm)
    lp = jax.nn.log_softmax(jnp.linspace(-2, 2, 64))
    lq = jax.nn.log_softmax(jnp.linspace(2, -2, 64))
    exact = float(coupled_divergence(lp, lq, 0))
    small = float(coupled_divergence(lp, lq, 1e-10))
    assert np.isclose(exact, small, atol=2e-6, rtol=2e-6)
    s = jnp.asarray([0.0, 1e-4, 2.0, 100.0])
    np.testing.assert_allclose(coupled_surprisal(s, 1e-10), s, atol=2e-6, rtol=2e-6)
    invalid = [{"kappa": x} for x in (-0.1, float("nan"), float("inf"), -float("inf"))]
    invalid += [
        {"clip_surprisal": x} for x in (0.0, -0.1, float("nan"), float("inf"), -float("inf"))
    ]
    invalid += [{"kappa": 0.5, "clip_surprisal": 2.0}, {"fast_steps": 1}]
    for kwargs in invalid:
        try:
            LossConfig(**kwargs)
        except (ValueError, NotImplementedError):
            pass
        else:
            raise AssertionError(f"invalid configuration accepted: {kwargs}")
    # This is an exposed numerical limit, not a reason to redefine the objective.
    extreme = float(
        coupled_divergence(
            jnp.log(jnp.asarray([0.5, 0.5])), jax.nn.log_softmax(jnp.asarray([0.0, -1000.0])), 0.5
        )
    )
    assert not np.isfinite(extreme)
    return {
        "random_distribution_pairs": 128,
        "min_divergence": min(divergences),
        "max_stationary_logit_gradient_norm": max(stationary),
        "small_kappa": 1e-10,
        "kl_limit": exact,
        "small_kappa_divergence": small,
        "invalid_configs_refused": len(invalid),
        "extreme_float32_preservation": "overflow reproduced; positive infinity",
        "status": "mathematical repair passes; runtime finite-value safeguard remains a launch gate",
    }


def proposal(report):
    files = (
        "src/pccap/revision_v1/train.py",
        "src/pccap/revision_v1/train_fast.py",
        "tests/revision_v1/test_ht_kappa_actual.py",
        "scripts/ht3b_objective_review.py",
    )
    return {
        "schema_version": 2,
        "task": "HT-3b",
        "status": "objective_review_passes_pending_Q4",
        "gpu_seconds": 0,
        "training_runs_executed": 0,
        "launch_authorized": False,
        "supersedes": "manifests/revision_v1/kappa_pilot_v1.json",
        "sources_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files},
        "objective": {
            "answer": "-expm1(-kappa * surprisal) / kappa; ordinary surprisal at kappa=0",
            "preservation": "D_k(p||q) = sum p * expm1(kappa*(log(p)-log(q))) / kappa",
            "zero_limit": "KL(p||q)",
            "proof": "For normalized positive p,q, D=sum q*f(p/q), f(t)=(t^(1+k)-t)/k; f(1)=0, f''(t)=(1+k)t^(k-1)>0. Jensen gives D>=0; equality and stationary q-logits at q=p.",
            "reference": "episode-fixed reference; coupled_divergence does not itself detach its first argument",
            "small_kappa": "expm1 avoids subtraction cancellation",
            "finite_precision": "not uniformly bounded; float32 expm1 overflows near kappa*log(p/q)>88.7",
            "mapping": "Nelson-Umarov ln_Q(x)=(x^Q-1)/Q; ln_Q(1/p)=-ln_{-Q}(p); implemented -ln_kappa(p) maps to Q=-kappa",
            "citation": {
                "arxiv": "https://arxiv.org/abs/0912.0748v1",
                "doi": "10.1016/j.physa.2010.01.044",
            },
            "interpretation": "bounded answer surprisal with convex preservation f-divergence; not a proof that the entire objective equals a published coupled entropy/free energy",
            "boundary": "rejection CE formula is unchanged but shared parameters may change its predictions; kappa does not repair the rejection boundary",
        },
        "review": report,
        "actual_trainer_validation": {
            "command": "PYTHONDONTWRITEBYTECODE=1 JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= ../venv/bin/python -m pytest -q -p no:cacheprovider tests/revision_v1/test_ht_kappa_actual.py tests/revision_v1/test_kappa_loss.py",
            "result": "10 passed in 13.59s",
            "coverage": "actual fast objective plus TinyBase slow/fast gradients at zero and kappa=.5",
        },
        "arms": [
            {"id": "ordinary", "kappa": 0.0, "clip_surprisal": None, "seeds": [0, 1, 2]},
            {
                "id": "kappa02",
                "kappa": 0.2,
                "clip_surprisal": None,
                "seeds": [0, 1, 2],
                "answer_ceiling": 5.0,
            },
            {
                "id": "kappa05",
                "kappa": 0.5,
                "clip_surprisal": None,
                "seeds": [0, 1, 2],
                "answer_ceiling": 2.0,
            },
            {
                "id": "clip2",
                "kappa": 0.0,
                "clip_surprisal": 2.0,
                "seeds": [0, 1, 2],
                "answer_ceiling": 2.0,
            },
        ],
        "training_count": 12,
        "design": "9 ordinary/coupled + 3 clipped; shared chosen architecture/training schedule and development evaluation population",
        "comparator_interpretation": "clip2 ceiling-matches kappa05 only. kappa02 is a secondary unmatched dose. Ceiling-matching both requires clip5 and 15 total trainings, a separate scope/budget amendment.",
        "aggregation_proposal_requires_Q4_acceptance": {
            "datasets": ["zsre", "counterfact", "mquake"],
            "seeds": [0, 1, 2],
            "retention": "For each arm compute RET-GS at the predeclared final pilot checkpoint per dataset/seed; equal-weight mean of 9 values. Each coupled candidate must be >= ordinary macro mean minus .02.",
            "unseen": "For each dataset, arithmetic mean false-fire rate across the same 3 seeds must not exceed ordinary's dataset mean; report every seed as well.",
            "tail_population": "Same frozen ordinary-text windows/positions for all arms and seeds; positive per-token NLL increase relative to original base. Compare only complete identically keyed populations; any missing/nonfinite cell makes the gate unavailable.",
            "tail_metrics": [
                "empirical ES95 of positive harm (fractional boundary weights)",
                "maximum positive harm",
            ],
            "seed_spread_rule": "For each metric average the 3 datasets within each seed. Compare each coupled arm's 3-seed mean with ordinary's; require abs(mean difference) > max(range of coupled seed macros, range of ordinary seed macros). Print the signed difference. This is exploratory separation, not a significance test.",
            "direction": "An increase may meet separation but cannot be described as improved robustness; reduction is required for an improvement claim.",
            "clip_role": "Report kappa05 vs clip2 descriptively on identical metrics. No ceiling-matched claim for kappa02.",
            "missingness": "Never drop seeds/datasets or select checkpoint by observed tail performance.",
            "inferential_scope": "development pilot, no confirmatory p-values or causal heavy-tail claim",
        },
        "budget_seconds": 10800,
        "experimental_completion_deadline": "2026-10-09",
        "blockers_cleared": [
            "negative preservation counterexample",
            "nonstationarity at equality",
            "small-kappa cancellation",
            "nonfinite config acceptance",
            "missing positive-kappa reference/fast parity",
        ],
        "launch_gates_open": [
            "lead Q4 acceptance including arms/aggregation",
            "selected primary and all training/evaluation bindings",
            "finite loss/gradient/parameter abort guard with charged failure receipts (overflow probe demonstrates why)",
            "GPU lease, memory guard and measured 3h aggregate budget including failures",
        ],
        "selected_primary": None,
    }


def main():
    report = checks()
    manifest = proposal(report)
    for path, value in (
        (ROOT / "logs/heavy_tail/HT-3b-objective-review.json", report),
        (ROOT / "manifests/revision_v1/kappa_pilot_v2.json", manifest),
    ):
        with path.open("x") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
