"""ENV-03: the tree matches updated_plan2.md §5 and the confirm-manifest firewall holds."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "pccap"

EXPECTED = [
    "__init__.py", "contracts.py", "vendor_hdpc.py", "cli.py",
    "bases/bp.py", "bases/epc.py", "bases/checksum.py", "bases/hooks.py",
    "transport/transport.py",
    "cap/features.py", "cap/bank.py", "cap/transaction.py", "cap/cap.py", "cap/learn.py", "cap/memory.py",
    "routers/last.py", "routers/full.py", "routers/measured.py", "routers/random_.py", "routers/supplied.py",
    "baselines/lora.py", "baselines/replay.py", "baselines/grace_adapter.py", "baselines/b0.py",
    "data/fetch.py", "data/streams.py", "data/tokenize.py", "data/decode.py", "data/splits.py",
    "data/confirm.py", "data/lm_sets.py",
    "fixtures/modular_control.py", "fixtures/grammar_model.py", "fixtures/grammar_generator.py",
    "fixtures/tracing.py",
    "metrics/rank.py", "metrics/participation.py", "metrics/overlap.py", "metrics/divergence.py",
    "metrics/editing.py", "metrics/cl_matrix.py", "metrics/order.py", "metrics/hvp.py",
    "harness/ledger.py", "harness/records.py", "harness/snapshot.py", "harness/runner.py",
    "harness/lease.py", "harness/status.py", "harness/schema.py",
    "analysis/paired.py", "analysis/bootstrap.py", "analysis/frontier.py", "analysis/budget.py",
    "analysis/report.py",
]


@pytest.mark.parametrize("rel", EXPECTED)
def test_module_exists(rel):
    assert (SRC / rel).exists(), rel


def test_contracts_import():
    import pccap.contracts as c

    assert c.SiteId(1, 3, 0).block == 3
    m = c.metric(None, units="nats", status="undefined")
    assert m["value"] is None and m["status"] == "undefined"
    with pytest.raises(ValueError):
        c.metric(float("nan"), units="x")


def test_confirm_manifest_firewall():
    """Only data/confirm.py may mention the confirmation manifests (plan §4.5 rule 4)."""
    offenders = []
    for p in SRC.rglob("*.py"):
        if p.relative_to(SRC).as_posix() == "data/confirm.py":
            continue
        if "manifests/confirm" in p.read_text():
            offenders.append(p.relative_to(SRC).as_posix())
    assert offenders == [], offenders


def test_docs_and_manifests_exist():
    for rel in ["docs/pdf_text/plan.txt", "docs/spec_defects.md", "docs/decisions.md",
                "docs/lead_queue.md", "docs/environment.md", "manifests/tasks.json"]:
        assert (ROOT / rel).exists(), rel


def test_determinism_settings_applied():
    import jax

    import pccap  # noqa: F401

    assert jax.config.jax_default_matmul_precision == "highest"
    assert jax.config.jax_enable_x64 is False
