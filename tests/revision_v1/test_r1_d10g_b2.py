"""Adopted contexts, later exposure, and decoding-free teacher certification."""

import copy
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts.r1_d10a_review_core import digest, review
from scripts.r1_d10b_teacher_review import RULE, certify_rows, eligible_rows, evaluate
from scripts.r1_d10e_adjudication import adjudicate
from scripts.r1_d10g_promote import promote

from tests.revision_v1.test_r1_d10a_review import fixture
from tests.revision_v1.test_r1_d10e_adjudication import fixture as context_fixture


def test_later_subject_exposure_revokes_proposed_release():
    old, inputs, checks = context_fixture(
        [dict(source="text", reason="development_drift_text", text="Alex Example")]
    )
    old["counts"] = {d: {} for d in ("zsre", "counterfact", "mquake")}
    candidate, _, _ = adjudicate(old, inputs, checks)
    later = [dict(source="new", reason="development_payload_reserved", subject="Alex Example")]
    result, losses = promote(candidate, {"decision": "ADOPTED"}, later, {})
    assert not result["dispositions"][0]["preteacher_eligible"] and len(losses) == 1
    assert candidate["proposed_dispositions"][0]["preteacher_eligible"]
    result, _ = promote(
        candidate,
        {"decision": "ADOPTED"},
        [dict(source="new", reason="development_drift_text", text="Alex Example")],
        {},
    )
    assert result["dispositions"][0]["preteacher_eligible"]
    with pytest.raises(ValueError, match="adoption"):
        promote(candidate, {"decision": "pending"}, [], {})


def completed():
    f = fixture()
    e, _ = review(*f, target=2)
    e.update(base_tensor_sha256="base", tokenizer_sha256="tokenizer", evidence_bindings=[])
    groups = eligible_rows(e, f[1])
    contract = dict(
        rule=RULE,
        base_tensor_sha256="base",
        tokenizer_sha256="tokenizer",
        chunk_size=2,
        datasets={d: [r["item_id"] for r in rows] for d, rows in groups.items()},
    )
    chunks = {}
    for ds, rows in groups.items():
        values = evaluate(
            rows,
            object(),
            f[3],
            f[4],
            batch_size=2,
            decode=lambda base, prompts, tok, **kw: [
                SimpleNamespace(
                    text="different", new_ids=[2], stopped_by="newline", truncated=False, steps=1
                )
                for _ in prompts
            ],
        )
        chunks[ds, 0] = dict(
            contract_sha256=digest(contract),
            dataset=ds,
            number=0,
            source_rows_sha256=digest(rows),
            rows=values,
            rows_sha256=digest(values),
        )
    return e, f[1], contract, chunks, f[3]


def test_certification_reuses_every_receipt_and_never_decodes():
    args = completed()
    reviewed = certify_rows(*args)
    assert len(reviewed) == 6 and all(r["teacher_pass"] for r in reviewed)


@pytest.mark.parametrize(
    "fault", ["missing", "extra", "score", "source", "base", "token", "contract"]
)
def test_bad_completed_receipts_refuse(fault):
    e, s, c, ch, t = completed()
    if fault == "missing":
        ch.pop(("zsre", 0))
    if fault == "extra":
        ch["zsre", 1] = copy.deepcopy(ch["zsre", 0])
    if fault == "score":
        ch["zsre", 0]["rows"][0]["teacher_pass"] = False
        ch["zsre", 0]["rows_sha256"] = digest(ch["zsre", 0]["rows"])
    if fault == "source":
        s["zsre"][0]["answer"] = "changed"
    if fault == "base":
        e["base_tensor_sha256"] = "wrong"
    if fault == "token":
        ch["zsre", 0]["rows"][0]["token_check"]["prompt_lengths"] = [999]
        ch["zsre", 0]["rows_sha256"] = digest(ch["zsre", 0]["rows"])
    if fault == "contract":
        c["chunk_size"] = 1
    with pytest.raises((ValueError, KeyError)):
        certify_rows(e, s, c, ch, t)


@pytest.mark.parametrize("fault", [None, "completion", "coverage"])
def test_certify_run_writes_only_verified_evidence(monkeypatch, fault):
    from scripts import r1_d10b_teacher_review as teacher
    from scripts.r1_d9_layouts import production

    from pccap.data import tokenize

    repo = Path(__file__).resolve().parents[2]
    key = uuid.uuid4().hex
    logs = repo / "logs/r1_round24/certification_tests" / key
    resources = repo.parent / "assets/runs/pc_cap/R1/test_scratch/r1_round24" / key
    logs.mkdir(parents=True)
    resources.mkdir(parents=True)
    evidence, sources, contract, chunks, tok = completed()
    evidence.update(
        register=teacher.atomic_new(resources / "register.json", fixture()[0]),
        base={"path": str(resources)},
        dataset_layouts=production("D"),
    )
    original = teacher.atomic_new(resources / "original.json", evidence)
    contract.update(evidence=original, producer=[teacher.ref(teacher.__file__)])
    binding = teacher.atomic_new(resources / "run/contract.json", contract)
    chunk_refs = []
    for (ds, number), chunk in chunks.items():
        chunk["contract_sha256"] = digest(contract)
        chunk_refs.append(
            teacher.atomic_new(resources / f"run/{ds}/chunk-{number:05d}.json", chunk)
        )
    finished = teacher.merge(
        evidence, [r for c in chunks.values() for r in c["rows"]], [original, binding, *chunk_refs]
    )
    finished_ref = teacher.atomic_new(resources / "run/teacher_evidence.json", finished)
    completion = teacher.atomic_new(
        logs / "completion.json",
        dict(
            task="R1-D10b",
            status="teacher evidence complete",
            lease="synthetic-test-lease",
            evidence=original if fault == "completion" else finished_ref,
        ),
    )
    if fault == "coverage":
        evidence["dispositions"][2]["preteacher_eligible"] = True
    current = teacher.atomic_new(resources / "current.json", evidence)
    matrix = teacher.ref(repo / "manifests/revision_v1/run_matrix_v5_2_option_D.json")
    tok.file_sha256 = lambda: "tokenizer"
    monkeypatch.setattr(tokenize, "GPT2Tokenizer", lambda **kw: tok)
    monkeypatch.setattr(teacher, "source_rows", lambda register: sources)
    monkeypatch.setattr(teacher, "evaluate", lambda *a, **k: pytest.fail("must never decode"))
    output, report = resources / "certified.json", logs / "certification.json"
    if fault:
        with pytest.raises(ValueError, match="completion|not decoded"):
            teacher.certify_run(current, resources / "run", completion, output, report, matrix)
        assert not output.exists() and not report.exists()
    else:
        result = teacher.certify_run(current, resources / "run", completion, output, report, matrix)
        saved = json.loads(output.read_text())
        assert saved["teacher_token_review_complete"] and not saved["role_compatibility_complete"]
        assert result["model_calls"] == result["gpu_seconds"] == 0
        assert result["final_capacity_shortfall"]["mquake"] == {"available": 2, "required": 1950}
        assert not result["draw_authorized"]
