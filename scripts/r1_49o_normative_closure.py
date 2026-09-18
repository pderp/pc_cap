"""D.5 normative closure, preserving immutable D.4 ancestry."""

from pathlib import Path

from scripts import r1_49n_normative_closure as prior
from scripts.r1_49j_normative_closure import sha

ROOT = prior.ROOT
PROTOCOL = "docs/R1_stage4_protocol_v5_2_D_5.md"


def closure(root=ROOT):
    root = Path(root).resolve()
    text = (root / PROTOCOL).read_text()
    if text.count("[D.4](R1_stage4_protocol_v5_2_D_4.md)") != 1 or "incorporates" not in text:
        raise ValueError("D.5 must explicitly incorporate D.4 once")
    value = prior.closure(root)
    return dict(
        schema_version=1,
        root_document=PROTOCOL,
        graph={**value["graph"], PROTOCOL: [prior.PROTOCOL]},
        bindings_sha256={**value["bindings_sha256"], str(root / PROTOCOL): sha(root / PROTOCOL)},
        precedence="D.5: DEC-068 triplet-first and DEC-069 preliminary summaries; D.4/DEC-066 scope and DEC-064 policy retained",
    )


def verify(candidate, root=ROOT):
    expected = closure(root)
    if candidate.get("normative_closure") != expected:
        raise ValueError("D.5 normative closure differs or is absent")
    for path, value in expected["bindings_sha256"].items():
        if candidate["bindings_sha256"].get(path) != value:
            raise ValueError("D.5 normative file missing or changed: " + path)
    return dict(normative_files=len(expected["bindings_sha256"]), normative_closure_verified=True)
