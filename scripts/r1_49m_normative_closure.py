"""D.3 incorporates the immutable D.2 closure and supersedes cap veto language."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from scripts import r1_49k_normative_closure as prior
from scripts.r1_49j_normative_closure import sha

ROOT = prior.ROOT
PROTOCOL = "docs/R1_stage4_protocol_v5_2_D_3.md"


def closure(root=ROOT):
    root = Path(root).resolve()
    targets = []
    for paragraph in (root / PROTOCOL).read_text().split("\n\n"):
        if "incorporat" not in paragraph.lower():
            continue
        for target in re.findall(r"\]\(([^)]+)\)", paragraph):
            target = unquote(target.split("#")[0])
            if not target or "://" in target:
                continue
            resolved = ((root / PROTOCOL).parent / target).resolve()
            if resolved != root / prior.PROTOCOL:
                raise ValueError("undeclared D.3 incorporated target: " + target)
            targets.append(resolved)
    if targets != [root / prior.PROTOCOL]:
        raise ValueError("D.3 must explicitly incorporate D.2 once")
    value = prior.closure(root)
    return dict(
        schema_version=1,
        root_document=PROTOCOL,
        graph={**value["graph"], PROTOCOL: [prior.PROTOCOL]},
        bindings_sha256={**value["bindings_sha256"], str(root / PROTOCOL): sha(root / PROTOCOL)},
        precedence="D.3 and later adopted decisions govern superseded provisions; DEC-064 cap benchmark has no admission veto",
    )


def verify(candidate, root=ROOT):
    expected = closure(root)
    if candidate.get("normative_closure") != expected:
        raise ValueError("D.3 normative closure differs or is absent")
    for path, value in expected["bindings_sha256"].items():
        if candidate["bindings_sha256"].get(path) != value:
            raise ValueError("D.3 normative file missing or changed: " + path)
    return dict(normative_files=len(expected["bindings_sha256"]), normative_closure_verified=True)
