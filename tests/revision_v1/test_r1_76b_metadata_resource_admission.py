"""Bound asset metadata admission; real files stay read-only, patched loader runs in memory."""

import pccap  # noqa: F401 # isort: skip
import hashlib
import json
import types
from pathlib import Path

import pytest

from pccap.bases.gpt2_jax import DEFAULT_SNAPSHOT
from pccap.revision_v1.analysis import digest
from tests.revision_v1.test_r1_round19_preflight import patched_source

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "scripts/r1_76_unseen_common.py"
SPEC = ROOT / "docs/tasks/R1-76b-mquake-historical-v2.population.spec.json"


@pytest.fixture
def fixture(monkeypatch):
    source = patched_source(
        "scripts/r1_76_unseen_common.py",
        "docs/tasks/R1-76b-metadata-resource-allowlist.patch",
        "allowed_metadata_resources = set()",
    )
    loader = types.ModuleType("proposed_metadata_loader")
    loader.__file__ = str(TARGET)
    exec(compile(source, str(TARGET), "exec"), loader.__dict__)
    original_sha = loader.sha
    raw_spec = json.loads(SPEC.read_text())
    resource = Path(raw_spec["population"]["path"]).resolve()
    population = json.loads(resource.read_text())
    virtual = {}
    bad_hashes = set()
    original_read = Path.read_bytes

    def read(path):
        return virtual[path.resolve()] if path.resolve() in virtual else original_read(path)

    def sha(path):
        path = Path(path).resolve()
        if path in bad_hashes:
            return "0" * 64
        if path == TARGET:
            return hashlib.sha256(source.encode()).hexdigest()
        if path in virtual:
            return hashlib.sha256(virtual[path]).hexdigest()
        return original_sha(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    monkeypatch.setattr(loader, "sha", sha)

    def install():
        virtual[resource] = json.dumps(population, sort_keys=True).encode()
        raw_spec["population"]["sha256"] = sha(resource)
        raw_spec["population_identity"] = digest(population)
        raw_spec["runner_bindings"]["scripts/r1_76_unseen_common.py"] = sha(TARGET)
        virtual[SPEC] = json.dumps(raw_spec, sort_keys=True).encode()

    install()
    return loader, population, install, bad_hashes


def test_real_population_accepts_only_bound_metadata_resources(fixture):
    loader, population, install, bad_hashes = fixture
    p, s = loader.load_spec(SPEC)
    assert p == population and p["checkpoints"] == [100, 300]
    assert len(p["edits"]) == 300 and len(p["outside"]) == 100
    assert len([x for x in p["sources_sha256"] if not Path(x).is_relative_to(ROOT)]) == 3
    assert s["population_identity"] == digest(p)


@pytest.mark.parametrize(
    "path",
    [
        ROOT.parent / "assets/data/prepared/revision_v1/r1_d4_v1/items.jsonl",
        DEFAULT_SNAPSHOT / "tokenizer.json",
        DEFAULT_SNAPSHOT / "config.json",
    ],
)
def test_metadata_hash_mismatch_is_still_rejected(fixture, path):
    loader, population, install, bad_hashes = fixture
    bad_hashes.add(path.resolve())
    with pytest.raises(ValueError, match="source changed"):
        loader.load_spec(SPEC)


@pytest.mark.parametrize(
    "path",
    [
        ROOT.parent / "assets/runs/pc_cap/R1/stage4_sealed_payloads/forbidden-fixture.json",
        ROOT.parent / "assets/data/prepared/revision_v1/unapproved/forbidden-fixture.json",
        ROOT / "manifests/confirm/forbidden-fixture.json",
    ],
)
def test_unapproved_or_sealed_sources_are_not_read(fixture, path):
    loader, population, install, bad_hashes = fixture
    population["sources_sha256"][str(path)] = "0" * 64
    install()
    with pytest.raises(PermissionError, match="metadata source"):
        loader.load_spec(SPEC)
