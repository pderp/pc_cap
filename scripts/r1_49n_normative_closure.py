"""D.4 incorporates D.3 and its immutable normative predecessors."""

from pathlib import Path

from scripts import r1_49m_normative_closure as prior
from scripts.r1_49j_normative_closure import sha

ROOT = prior.ROOT
PROTOCOL = "docs/R1_stage4_protocol_v5_2_D_4.md"


def closure(root=ROOT):
    root = Path(root).resolve()
    target = "[D.3](R1_stage4_protocol_v5_2_D_3.md)"
    text = (root / PROTOCOL).read_text()
    if text.count(target) != 1 or "incorporates" not in text:
        raise ValueError("D.4 must explicitly incorporate D.3 once")
    value = prior.closure(root)
    return dict(
        schema_version=1,
        root_document=PROTOCOL,
        graph={**value["graph"], PROTOCOL: [prior.PROTOCOL]},
        bindings_sha256={**value["bindings_sha256"], str(root / PROTOCOL): sha(root / PROTOCOL)},
        precedence="D.4 and later adopted decisions govern superseded provisions; DEC-066 prospective MQuAKE reduction; DEC-064 cap policy unchanged",
    )


def verify(candidate, root=ROOT):
    expected = closure(root)
    if candidate.get("normative_closure") != expected:
        raise ValueError("D.4 normative closure differs or is absent")
    for path, value in expected["bindings_sha256"].items():
        if candidate["bindings_sha256"].get(path) != value:
            raise ValueError("D.4 normative file missing or changed: " + path)
    return dict(normative_files=len(expected["bindings_sha256"]), normative_closure_verified=True)
